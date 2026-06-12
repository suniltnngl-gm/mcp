import abc
from typing import List, Dict, Any

# Import actual mcp types
from mcp.types import Tool, CallToolResult


class MCPServer(abc.ABC):
    """
    Abstract Base Class for an MCP Server.
    Concrete implementations should provide methods for listing available tools
    and executing specific tools.
    """

    @abc.abstractmethod
    async def list_tools(self) -> List[Tool]:
        """
        Lists all available tools provided by this server.

        Returns:
            A list of Tool objects, each describing an available tool.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def call_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> CallToolResult:
        """
        Executes a specific tool on this server.

        Args:
            tool_name: The name of the tool to execute.
            arguments: A dictionary of arguments to pass to the tool.

        Returns:
            A CallToolResult object containing the result of the tool execution.
        """
        raise NotImplementedError


class MCPClient(abc.ABC):
    """
    Abstract Base Class for an MCP Client.
    Concrete implementations should provide methods for interacting with an
    MCP Server, including fetching available tools and calling them.
    """

    @abc.abstractmethod
    async def list_tools(self) -> List[Tool]:
        """
        Fetches available tools from the connected MCP server(s).

        Returns:
            A list of Tool objects, each describing an available tool.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """
        Executes a tool on the connected MCP server.

        Args:
            name: The name of the tool to execute.
            arguments: A dictionary of arguments to pass to the tool.

        Returns:
            A CallToolResult object containing the result of the tool execution.
        """
        raise NotImplementedError
