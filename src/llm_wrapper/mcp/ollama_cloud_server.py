"""MCP server that wraps the Ollama Cloud API for free models."""

import json
import os
from typing import Optional
from mcp.server.fastmcp import FastMCP
from mcp.types import CallToolResult, TextContent

_server = FastMCP("ollama-cloud", instructions="Ollama Cloud API — free model access")

FREE_MODELS = [
    "gpt-oss:120b-cloud",
    "gpt-oss:20b-cloud",
    "gemma3:12b",
    "ministral-3:8b",
    "rnj-1:8b",
]


def _get_client():
    from ollama import Client
    api_key = os.environ.get("OLLAMA_API_KEY")
    if not api_key:
        raise ValueError("OLLAMA_API_KEY not set in environment")
    return Client(
        host="https://ollama.com",
        headers={"Authorization": f"Bearer {api_key}"},
    )


@_server.tool(name="ollama_chat", description="Send a chat message to an Ollama cloud model")
async def ollama_chat(
    model: str = "gpt-oss:120b-cloud",
    messages: str = '[{"role":"user","content":"Hello"}]',
    stream: bool = False,
    max_tokens: Optional[int] = None,
) -> CallToolResult:
    try:
        client = _get_client()
        parsed_messages = json.loads(messages) if isinstance(messages, str) else messages
        kwargs = {
            "model": model,
            "messages": parsed_messages,
            "stream": stream,
        }
        if max_tokens:
            kwargs["options"] = {"num_predict": max_tokens}

        if stream:
            response_parts = []
            for part in client.chat(**kwargs):
                response_parts.append(part["message"]["content"])
            content = "".join(response_parts)
        else:
            response = client.chat(**kwargs)
            content = response.message.content

        return CallToolResult(
            content=[TextContent(type="text", text=content)],
            success=True,
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=str(e))],
            success=False,
        )


@_server.tool(name="ollama_list_models", description="List available free Ollama cloud models")
async def ollama_list_models() -> CallToolResult:
    return CallToolResult(
        content=[TextContent(type="text", text=json.dumps(FREE_MODELS, indent=2))],
        success=True,
    )


if __name__ == "__main__":
    _server.run(transport="stdio")
