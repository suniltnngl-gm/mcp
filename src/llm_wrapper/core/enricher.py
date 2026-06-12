import json
from typing import List, Dict, Any
from mcp.types import Tool
import logging

logger = logging.getLogger(__name__)


class ContextEnricher:
    """Translates MCP tools and resources into LLM-friendly formats."""

    def __init__(self):
        self.system_base = (
            "You are a helpful AI assistant with access to local tools through the "
            "Model Context Protocol (MCP). Use these tools to provide accurate, "
            "real-time information from the user's local environment."
        )
        logger.info("ContextEnricher initialized.")

    def enrich_for_sdk(self, tools: List[Tool]) -> List[Dict[str, Any]]:
        """
        Converts MCP tools to Gemini SDK Function Declarations.
        Gemini expects a specific dictionary format for tools.
        """
        declarations = []
        for tool in tools:
            # MCP 'inputSchema' is compatible with JSON Schema,
            # which Gemini's 'parameters' field accepts.
            declarations.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema.model_dump(
                        by_alias=True
                    ),  # Use model_dump to convert Pydantic to dict
                }
            )
        logger.debug(f"Enriched {len(tools)} tools for SDK.")
        return declarations

    def enrich_for_cli(self, tools_map: Dict[str, List[Tool]]) -> str:
        """
        Creates a text-based system prompt for the 'gemini -p' CLI.
        Since the CLI is a text-only interface, we must describe the tools manually.
        """
        prompt_parts = [self.system_base, "\nAVAILABLE TOOLS:"]

        for server_name, tools in tools_map.items():
            prompt_parts.append(f"\n[{server_name.upper()} SERVER]")
            for tool in tools:
                prompt_parts.append(f"- {tool.name}: {tool.description}")
                # Convert Pydantic model to dictionary for JSON serialization
                prompt_parts.append(
                    f"  Arguments: {json.dumps(tool.inputSchema.model_dump(by_alias=True).get('properties', {}))}"
                )

        prompt_parts.append(
            "\nWhen you need to use a tool, respond in this format: "
            "CALL_TOOL: server_name.tool_name(arg1=val1, ...)"
        )
        logger.debug("Enriched tools for CLI.")
        return "\n".join(prompt_parts)
