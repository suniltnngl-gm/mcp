from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Tool, CallToolResult
from typing import List, Dict, Any


class LocalMCPClient:
    """Manages connection to a single MCP server."""

    def __init__(self, command: str, args: list[str]):
        self.server_params = StdioServerParameters(command=command, args=args, env=None)
        self.exit_stack = AsyncExitStack()
        self.session: ClientSession | None = None

    async def connect(self):
        """Initializes the stdio transport and session."""
        # This starts the server process (e.g., npx @modelcontextprotocol/server-filesystem)
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(self.server_params)
        )
        self.read_stream, self.write_stream = stdio_transport

        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.read_stream, self.write_stream)
        )

        # Must initialize as per protocol
        await self.session.initialize()
        print(f"Connected to MCP server: {self.server_params.command}")

    async def list_tools(self) -> List[Tool]:
        """Fetches available tools from the server."""
        if not self.session:
            raise RuntimeError("Session not initialized. Call connect() first.")

        response = await self.session.list_tools()
        return response.tools

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Executes a tool on the server."""
        if not self.session:
            raise RuntimeError("Session not initialized. Call connect() first.")
        return await self.session.call_tool(name, arguments)

    async def disconnect(self):
        """Gracefully shuts down the connection and server process."""
        await self.exit_stack.aclose()
