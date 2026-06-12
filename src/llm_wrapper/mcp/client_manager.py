import asyncio
from contextlib import AsyncExitStack
from typing import Dict, List, Any, Optional

# Import actual mcp types and client session
from mcp.types import Tool, CallToolResult
from mcp import StdioServerParameters

from src.llm_wrapper.mcp.interfaces import MCPClient  # Import our ABC
from src.llm_wrapper.mcp.config import McpConfig, LocalServerConfig, RemoteServerConfig
from src.llm_wrapper.mcp.stdio_client import (
    StdioMCPClient,
)  # Import the real StdioMCPClient
from src.llm_wrapper.mcp.resilience import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    retry_with_backoff,
)  # Import resilience components

# Timeout configuration
DEFAULT_TOOL_CALL_TIMEOUT = 30  # seconds


class PlaceholderRemoteClient(MCPClient):
    """
    A placeholder for a remote MCP client implementation.
    In a real scenario, this would interact with a remote MCP server via HTTP/RPC.
    """

    def __init__(self, config: RemoteServerConfig):
        self._config = config
        print(f"PlaceholderRemoteClient initialized for URL: {config.url}")

    async def list_tools(self) -> List[Tool]:
        """Returns dummy tools for testing."""
        tool2 = Tool(
            name="remote_tool_2",
            description="A dummy remote tool 2",
            inputSchema={
                "type": "object",
                "properties": {"param2": {"type": "integer"}},
            },
        )
        return [tool2]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Simulates calling a remote tool."""
        print(f"PlaceholderRemoteClient: Calling tool '{name}' with args {arguments}")
        result = CallToolResult(
            content=f"Result from remote_tool_2: {arguments.get('param2', 0) * 2}"
        )
        return result


class MultiClientManager(MCPClient):
    """
    Manages multiple MCP clients, routing tool calls and aggregating tools.
    Implements the MCPClient interface to provide a unified entry point to MCP servers.
    """

    _clients: Dict[str, MCPClient]
    _config: McpConfig
    _exit_stack: AsyncExitStack
    _circuit_breakers: Dict[
        str, CircuitBreaker
    ]  # New: Circuit Breakers for each client

    def __init__(self, config: McpConfig):
        self._clients = {}
        self._config = config
        self._exit_stack = AsyncExitStack()
        self._circuit_breakers = {}  # Initialize circuit breakers
        self._initialize_clients()

    def _initialize_clients(self):
        """Initializes clients and their respective circuit breakers based on the provided McpConfig."""
        for server_name, server_def in self._config.mcpServers.items():
            try:
                # Normalize client_config access for dicts and Pydantic models
                if isinstance(server_def.config, dict):
                    client_cfg = server_def.config.get("client_config", {})
                else:
                    client_cfg = getattr(server_def.config, "client_config", {}) or {}

                # Initialize Circuit Breaker for this client
                self._circuit_breakers[server_name] = CircuitBreaker(
                    failure_threshold=client_cfg.get("cb_failure_threshold", 3),
                    reset_timeout=client_cfg.get("cb_reset_timeout", 30),
                    service_name=server_name,
                )

                if server_def.type == "local":
                    if not isinstance(server_def.config, LocalServerConfig):
                        raise TypeError(
                            "Local server config must be LocalServerConfig type."
                        )

                    # Convert list-style command into command+args for StdioServerParameters
                    cmd = server_def.config.command
                    if isinstance(cmd, list):
                        cmd_exe = cmd[0]
                        cmd_args = cmd[1:]
                    else:
                        cmd_exe = cmd
                        cmd_args = server_def.config.args or []

                    server_params = StdioServerParameters(
                        command=cmd_exe,
                        args=cmd_args,
                        env=server_def.config.env,
                    )
                    self._clients[server_name] = StdioMCPClient(server_params)
                    print(f"Initialized StdioMCPClient for {server_name}")
                elif server_def.type == "remote":
                    if not isinstance(server_def.config, RemoteServerConfig):
                        raise TypeError(
                            "Remote server config must be RemoteServerConfig type."
                        )

                    self._clients[server_name] = PlaceholderRemoteClient(
                        server_def.config
                    )
                    print(f"Initialized PlaceholderRemoteClient for {server_name}")
                else:
                    print(
                        f"Warning: Unknown server type '{server_def.type}' for server '{server_name}'. Skipping."
                    )
            except Exception as e:
                print(f"Error initializing client for server '{server_name}': {e}")
                try:
                    import traceback

                    traceback.print_exc()
                except Exception:
                    pass
                try:
                    print(f"server_def.config type: {type(server_def.config)}")
                    print(f"server_def.config repr: {repr(server_def.config)}")
                except Exception:
                    pass

    async def __aenter__(self):
        """Connects all managed clients."""
        for client_name, client in self._clients.items():
            if isinstance(client, StdioMCPClient):
                # Use the connect async context manager for StdioMCPClient
                await self._exit_stack.enter_async_context(client.connect())
            # For other client types (e.g., PlaceholderRemoteClient),
            # if they need a connect, it would be called here.
            # Currently, PlaceholderRemoteClient doesn't have a connect method.
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Disconnects all managed clients."""
        await self._exit_stack.aclose()  # This will properly exit all contexts entered
        # Explicitly call disconnect for any clients not managed by AsyncExitStack
        for client_name, client in self._clients.items():
            if not isinstance(client, StdioMCPClient):
                if hasattr(client, "disconnect") and callable(client.disconnect):
                    await client.disconnect()

        # Force close any open circuits for managed clients
        for cb in self._circuit_breakers.values():
            await cb.record_success()  # Force close any open circuits

        self._clients.clear()  # Clear clients on exit

    async def list_tools(self) -> List[Tool]:
        """
        Aggregates and returns all tools from all managed MCP clients.
        Applies circuit breaker logic.
        """
        all_tools: List[Tool] = []
        tasks = []
        for client_name, client in self._clients.items():
            cb = self._circuit_breakers.get(client_name)
            if cb and cb.state == "OPEN":
                print(f"[{client_name} Circuit Breaker]: OPEN. Skipping tool listing.")
                continue

            # For StdioMCPClient, check if session is active before trying to list tools
            if isinstance(client, StdioMCPClient) and client._session is None:
                print(
                    f"Warning: StdioMCPClient for '{client_name}' is not connected, skipping tool listing."
                )
                continue

            # Wrap list_tools call with circuit breaker and timeout
            async def _list_tools_with_cb_and_timeout(
                cl: MCPClient, cb_instance: Optional[CircuitBreaker], timeout_val: float
            ):
                try:
                    # Apply circuit breaker
                    if cb_instance:
                        tools_from_client = await cb_instance(
                            lambda: asyncio.wait_for(cl.list_tools(), timeout_val)
                        )
                    else:
                        tools_from_client = await asyncio.wait_for(
                            cl.list_tools(), timeout_val
                        )
                    return tools_from_client
                except CircuitBreakerOpenError as e:
                    print(f"List tools blocked by Circuit Breaker: {e}")
                    return e  # Return exception to be caught by gather
                except asyncio.TimeoutError:
                    print(f"Timeout while listing tools from '{client_name}'.")
                    if cb_instance:
                        await cb_instance.record_failure()
                    return asyncio.TimeoutError(
                        f"Timeout while listing tools from '{client_name}'."
                    )
                except Exception as e:
                    print(f"Error listing tools from client '{client_name}': {e}")
                    if cb_instance:
                        await cb_instance.record_failure()
                    return e

            tasks.append(
                _list_tools_with_cb_and_timeout(client, cb, DEFAULT_TOOL_CALL_TIMEOUT)
            )

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for client_tools in results:
            if isinstance(client_tools, Exception):
                print(f"Error or exception during list_tools: {client_tools}")
                continue
            all_tools.extend(client_tools)
        return all_tools

    async def call_tool(
        self, name: str, arguments: Dict[str, Any], server_name: Optional[str] = None
    ) -> CallToolResult:
        """
        Routes a tool call to a specific or default MCP client.
        Applies circuit breaker, retries, and timeout logic.
        """
        target_server_name = server_name
        if target_server_name is None:
            if self._config.default_server:
                target_server_name = self._config.default_server
            else:
                raise ValueError(
                    "No target server specified and no default server configured."
                )

        client = self._clients.get(target_server_name)
        if not client:
            raise ValueError(f"No client found for server: {target_server_name}")

        cb = self._circuit_breakers.get(target_server_name)

        async def _perform_call():
            """Internal function to perform the actual tool call with timeout."""
            return await asyncio.wait_for(
                client.call_tool(name, arguments), DEFAULT_TOOL_CALL_TIMEOUT
            )

        try:
            # Apply Circuit Breaker
            if cb:
                # If provider client, also apply retries
                if isinstance(
                    client, PlaceholderRemoteClient
                ):  # Check for placeholder remote, will be real ProviderLLMClient
                    tool_result = await cb(
                        lambda: retry_with_backoff(
                            _perform_call,
                            max_retries=3,
                            catch_exceptions=(
                                asyncio.TimeoutError,
                                ConnectionError,
                                IOError,
                            ),
                        )
                    )
                else:  # Local clients
                    tool_result = await cb(_perform_call)
            else:  # No circuit breaker configured
                tool_result = await _perform_call()

            return tool_result

        except CircuitBreakerOpenError as e:
            print(
                f"Tool call to '{target_server_name}.{name}' blocked by Circuit Breaker: {e}"
            )
            return CallToolResult(
                content=f"Tool call failed: Service temporarily unavailable ({e})",
                success=False,
            )
        except asyncio.TimeoutError:
            print(f"Timeout while calling tool '{target_server_name}.{name}'.")
            if cb:
                await cb.record_failure()  # Record failure for CB if timeout
            return CallToolResult(
                content=f"Tool call failed: Timeout after {DEFAULT_TOOL_CALL_TIMEOUT}s.",
                success=False,
            )
        except Exception as e:
            print(f"Error calling tool '{target_server_name}.{name}': {e}")
            if cb:
                await cb.record_failure()  # Record failure for CB
            return CallToolResult(content=f"Tool call failed: {e}", success=False)


if __name__ == "__main__":
    # Example usage for testing MultiClientManager
    from src.llm_wrapper.mcp.config import load_mcp_config
    from pathlib import Path
    from src.llm_wrapper.mcp.stdio_client import (
        create_dummy_mcp_server_script,
        cleanup_dummy_mcp_server_script,
    )

    async def main():
        print("--- Testing MultiClientManager with StdioMCPClient ---")
        dummy_server_path = Path("my_mcp_server.py")
        await create_dummy_mcp_server_script(
            dummy_server_path
        )  # Ensure dummy server is available

        # Create a dummy mcp.json for testing if it doesn't exist
        dummy_config_path = Path("mcp.json")
        if not dummy_config_path.is_file():
            print(
                f"Creating a dummy {dummy_config_path} for testing MultiClientManager."
            )
            dummy_content = {
                "mcpServers": {
                    "local_dev_server": {
                        "type": "local",
                        "config": {
                            "command": ["python", str(dummy_server_path)],
                            "args": ["--debug"],
                            "env": {"PYTHONUNBUFFERED": "1"},
                            "client_config": {"timeout": 60},
                        },
                    },
                    "remote_prod_server": {
                        "type": "remote",
                        "config": {
                            "url": "http://localhost:8081",
                            "api_key": "YOUR_REMOTE_API_KEY",
                        },
                    },
                },
                "default_server": "local_dev_server",
            }
            with open(dummy_config_path, "w", encoding="utf-8") as f:
                json.dump(dummy_content, f, indent=2)

        mcp_config = (
            load_mcp_config()
        )  # Assumes mcp.json is available from config.py test

        if mcp_config:
            async with MultiClientManager(
                mcp_config
            ) as manager:  # Use as async context manager
                print("\nListing all tools via manager:")
                all_tools = await manager.list_tools()
                for tool in all_tools:
                    print(f"- Tool Name: {tool.name}, Description: {tool.description}")

                print("\nCalling local_tool_1 via manager:")
                try:
                    local_result = await manager.call_tool(
                        name="my_tool",
                        arguments={"message": "Hello from MCM!"},
                        server_name="local_dev_server",
                    )
                    print(f"Local Tool Result: {local_result.content}")
                except ValueError as e:
                    print(f"Error calling local tool: {e}")

                print("\nCalling remote_tool_2 via manager:")
                try:
                    remote_result = await manager.call_tool(
                        name="remote_tool_2",
                        arguments={"param2": 10},
                        server_name="remote_prod_server",
                    )
                    print(f"Remote Tool Result: {remote_result.content}")
                except ValueError as e:
                    print(f"Error calling remote tool: {e}")

                print(
                    "\nCalling a tool without specifying server (should use default if configured):"
                )
                try:
                    # If local_dev_server is default and has local_tool_1
                    default_result = await manager.call_tool(
                        name="echo_tool", arguments={"text": "default_test_echo"}
                    )
                    print(f"Default Tool Result: {default_result.content}")
                except ValueError as e:
                    print(f"Error calling default tool: {e}")
        else:
            print("Failed to load MCP configuration, cannot test MultiClientManager.")

        # Clean up dummy config and server
        if dummy_config_path.is_file():
            dummy_config_path.unlink()
            print(f"Deleted {dummy_config_path}.")
        await cleanup_dummy_mcp_server_script(dummy_server_path)

    asyncio.run(main())
