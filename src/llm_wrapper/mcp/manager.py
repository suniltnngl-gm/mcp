import asyncio
from contextlib import AsyncExitStack
from typing import Dict, List
from mcp.types import Tool
from llm_wrapper.mcp.client import LocalMCPClient
import logging

logger = logging.getLogger(__name__)


class MCPManager:
    """Manages multiple MCP server connections and aggregates their tools."""

    def __init__(self):
        # Maps server name -> LocalMCPClient instance
        self.clients: Dict[str, LocalMCPClient] = {}
        self.exit_stack = AsyncExitStack()
        self._is_initialized = False
        logger.info("MCPManager initialized.")

    async def register_server(self, name: str, command: str, args: List[str]):
        """Adds a server configuration to the manager."""
        if name in self.clients:
            logger.warning(f"Server '{name}' is already registered. Skipping.")
            return

        client = LocalMCPClient(command=command, args=args)
        self.clients[name] = client
        logger.info(f"Registered MCP server: {name} with command '{command} {args}'.")

    async def initialize_all(self):
        """Connects to all registered servers."""
        if self._is_initialized:
            logger.info("MCPManager already initialized.")
            return

        connect_tasks = []
        for name, client in self.clients.items():
            logger.info(f"Attempting to connect to MCP server: {name}...")
            connect_tasks.append(client.connect())

        await asyncio.gather(*connect_tasks)
        self._is_initialized = True
        logger.info("All registered MCP servers initialized.")

    async def get_all_tools(self) -> Dict[str, List[Tool]]:
        """
        Retrieves tools from all connected servers.
        Returns: { "server_name": [Tool, Tool, ...] }
        """
        all_tools = {}
        for name, client in self.clients.items():
            try:
                tools = await client.list_tools()
                all_tools[name] = tools
                logger.debug(f"Fetched {len(tools)} tools from server: {name}.")
            except Exception as e:
                logger.error(f"Failed to fetch tools from server '{name}': {e}")
                all_tools[name] = []  # Ensure it's always a list, even on error
        return all_tools

    async def call_server_tool(
        self, server_name: str, tool_name: str, arguments: dict
    ) -> CallToolResult:
        """Routes a tool call to the specific server."""
        client = self.clients.get(server_name)
        if not client:
            raise ValueError(f"Server '{server_name}' not found or not initialized.")

        logger.info(
            f"Calling tool '{tool_name}' on server '{server_name}' with args: {arguments}"
        )
        return await client.call_tool(tool_name, arguments)

    async def shutdown(self):
        """Gracefully disconnects all servers."""
        if not self._is_initialized:
            logger.info("MCPManager not initialized, no servers to shut down.")
            return

        logger.info("Shutting down all MCP servers.")
        shutdown_tasks = [client.disconnect() for client in self.clients.values()]
        await asyncio.gather(*shutdown_tasks)
        await self.exit_stack.aclose()  # Ensure exit stack is closed
        self._is_initialized = False
        logger.info("All MCP servers shut down.")
