import asyncio
from contextlib import asynccontextmanager
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import actual mcp types and client session
from mcp.client.stdio import stdio_client
from mcp.types import Tool, CallToolResult
from mcp import ClientSession, StdioServerParameters

# Import our abstract base class
from src.llm_wrapper.mcp.interfaces import MCPClient


class StdioMCPClient(MCPClient):
    """
    An MCPClient implementation for connecting to a local MCP server via stdio.
    This client manages the lifecycle of the subprocess and the MCP session.
    """

    def __init__(self, server_params: StdioServerParameters):
        self.server_params = server_params
        # Backwards compatibility: older code expects command line as a list
        cmd = getattr(self.server_params, "command", None)
        args = getattr(self.server_params, "args", None) or []
        if isinstance(cmd, (list, tuple)):
            self._command_line = list(cmd) + list(args)
        elif cmd is None:
            self._command_line = list(args)
        else:
            self._command_line = [str(cmd)] + list(args)

        self._session: Optional[ClientSession] = None
        self._process: Optional[asyncio.subprocess.Process] = None

    @asynccontextmanager
    async def connect(self):
        """
        Establishes a connection to the stdio server and yields the client session.
        This should be used as an async context manager.
        """
        if self._session:
            raise RuntimeError("StdioMCPClient is already connected.")

        # Build a printable command line from available fields for compatibility
        cmd = getattr(self.server_params, "command", None)
        args = getattr(self.server_params, "args", None) or []
        if isinstance(cmd, (list, tuple)):
            command_line = list(cmd) + list(args)
        elif cmd is None:
            command_line = list(args)
        else:
            command_line = [str(cmd)] + list(args)

        print(f"Starting stdio client with command: {' '.join(command_line)}")

        try:
            # stdio_client is an async context manager that returns read/write streams
            async with stdio_client(self.server_params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    self._session = session
                    print("Stdio client connected.")
                    yield self

            # Ensure session is cleaned up after exiting the context
            self._session = None
            print("Stdio client disconnected gracefully.")
        except Exception as e:
            print(f"Error connecting StdioMCPClient: {e}")
            if self._session:
                await self.disconnect()
            raise  # Re-raise the exception

    async def list_tools(self) -> List[Tool]:
        """
        Lists all available tools from the connected stdio server.
        Requires an active session.
        """
        if not self._session:
            raise RuntimeError("StdioMCPClient is not connected. Call connect() first.")

        response = await self._session.list_tools()
        return response.tools

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """
        Executes a specific tool on the connected stdio server.
        Requires an active session.
        """
        if not self._session:
            raise RuntimeError("StdioMCPClient is not connected. Call connect() first.")

        return await self._session.call_tool(name, arguments)

    async def disconnect(self):
        """
        Explicitly disconnects the client session.
        This method is primarily for explicit control if not using the 'connect'
        async context manager, or for error cleanup.
        """
        if self._session:
            try:
                await self._session.__aexit__(None, None, None)
                print("Stdio client session disconnected.")
            except Exception as e:
                print(f"Error disconnecting StdioMCPClient session: {e}")
            finally:
                self._session = None


# --- Test Utilities (for development and demonstration) ---
async def create_dummy_mcp_server_script(path: Path):
    """Creates a dummy MCP server Python script for testing."""
    dummy_server_content = """
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, CallToolResult
from pydantic import BaseModel

class MyToolInput(BaseModel):
    message: str

async def my_tool_function(input: MyToolInput) -> CallToolResult:
    print(f"Dummy server received message for my_tool: {input.message}", flush=True)
    return CallToolResult(content=f"Server says: '{input.message}'")

class EchoToolInput(BaseModel):
    text: str

async def echo_tool_function(input: EchoToolInput) -> CallToolResult:
    print(f"Dummy server echoing for echo_tool: {input.text}", flush=True)
    return CallToolResult(content=input.text)

my_server = FastMCP(
    name="my_test_server",
    tools=[
        Tool(name="my_tool", description="A test tool", inputSchema=MyToolInput.model_json_schema()),
        Tool(name="echo_tool", description="Echoes text", inputSchema=EchoToolInput.model_json_schema())

    async def test_stdio_client():
        print("--- Testing StdioMCPClient ---")
        dummy_server_path = Path("my_mcp_server.py")
        await create_dummy_mcp_server_script(dummy_server_path)

        server_params = StdioServerParameters(
            command=["python", str(dummy_server_path)],
            args=[],
        )
        client = StdioMCPClient(server_params)

        try:
            async with client.connect() as connected_client:
                print("\nListing tools:")
                tools = await connected_client.list_tools()
                for tool in tools:
                    print(f"- {tool.name}: {tool.description}")

                print("\nCalling 'my_tool':")
                result = await connected_client.call_tool(
                    "my_tool", {"message": "Hello from client!"}
                )
                print(f"Result for my_tool: {result.content}")

                print("\nCalling 'echo_tool':")
                echo_result = await connected_client.call_tool(
                    "echo_tool", {"text": "This is an echo test."}
                )
                print(f"Result for echo_tool: {echo_result.content}")

        except Exception as e:
            print(f"An error occurred during client interaction: {e}")
        finally:
            await cleanup_dummy_mcp_server_script(dummy_server_path)

    asyncio.run(test_stdio_client())
