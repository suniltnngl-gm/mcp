# src/llm_wrapper/llm/local_client.py

import asyncio
import json
import re
from pathlib import Path
from typing import AsyncGenerator, Dict, List, Any, Optional

import ollama  # Assuming ollama-python library is installed

from mcp.types import Tool  # Use actual mcp types

# Assuming a base LLMClient interface if one were to be created
# For now, we'll implement the necessary methods directly.


class LocalLLMClient:
    """
    A client for interacting with a local LLM via Ollama, supporting streaming
    and system prompt injection from file_registry.json.
    """

    def __init__(
        self, model_name: str = "llama2", base_url: str = "http://localhost:11434"
    ):
        self.model_name = model_name
        self.base_url = base_url
        self.client = ollama.AsyncClient(host=self.base_url)
        self.file_registry_path = Path(
            "file_registry.json"
        )  # Path to your file_registry.json

    async def _get_system_context_from_registry(self) -> str:
        """
        Reads file_registry.json and formats its content as a system prompt.
        """
        if not self.file_registry_path.is_file():
            return "No file registry available for context."

        try:
            content = self.file_registry_path.read_text()
            registry_data = json.loads(content)

            # Format the registry data into a readable system context
            system_context = "You have access to the following project file registry:\n"
            for item in registry_data:
                system_context += f"- Path: {item.get('path')}, Type: {item.get('type')}, Description: {item.get('description', 'No description')}\n"
            system_context += "\nUse this information to better understand the project structure and context."
            return system_context
        except json.JSONDecodeError:
            return "Error reading file_registry.json: Invalid JSON."
        except Exception as e:
            return f"Error loading file_registry.json: {e}"

    async def _format_tools_for_ollama_context(self, tools: List[Tool]) -> str:
        """
        Formats MCP Tool objects into a string that can be injected into the LLM's system context.
        Ollama currently doesn't have native tool calling, so tools are described in the prompt.
        The format is designed to encourage the LLM to output tool calls in a parsable way.
        """
        if not tools:
            return ""

        tool_descriptions = ["\n# Available Tools\n"]
        for tool in tools:
            tool_descriptions.append(f"## {tool.name}")
            tool_descriptions.append(f"Description: {tool.description}")
            if tool.inputSchema and isinstance(tool.inputSchema, dict):
                params_str = json.dumps(
                    tool.inputSchema.get("properties", {{}}), indent=2
                )
                tool_descriptions.append(
                    f"Parameters (JSON Schema properties): {params_str}"
                )

        tool_descriptions.append(
            "\nTo use a tool, respond ONLY with a JSON object like this:\n"
            "```json\n"
            "{\n"
            '  "tool_call": {\n'
            '    "name": "tool_name",\n'
            '    "arguments": { "arg1": "value1", "arg2": value2 }\n'
            "  }\n"
            "}\n"
            "```\n"
            "Do not include any other text before or after the JSON. The tool name must match one of the available tools exactly.\n"
        )
        return "\n".join(tool_descriptions)

    async def generate_stream(
        self, prompt: str, tools: Optional[List[Tool]] = None, **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generates a streaming response from the local Ollama model.
        """
        system_context = await self._get_system_context_from_registry()
        tool_context = await self._format_tools_for_ollama_context(tools)

        full_system_message = system_context
        if tool_context:
            full_system_message += "\n" + tool_context

        messages = [
            {"role": "system", "content": full_system_message},
            {"role": "user", "content": prompt},
        ]

        try:
            async for chunk in await self.client.chat(
                model=self.model_name, messages=messages, stream=True, **kwargs
            ):
                yield chunk
        except ollama.ResponseError as e:
            print(f"Ollama API Error: {e.status_code} - {e.error}")
            yield {"error": f"Ollama API Error: {e.status_code} - {e.error}"}
        except Exception as e:
            print(f"An unexpected error occurred during Ollama generation: {e}")
            yield {"error": f"An unexpected error occurred: {e}"}

    async def generate(
        self, prompt: str, tools: Optional[List[Tool]] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Generates a complete response from the local Ollama model.
        (Non-streaming version for simpler integration with current Orchestrator placeholder).
        This also attempts to parse a tool call if the LLM output is formatted as such.
        """
        full_response_content = ""
        async for chunk in self.generate_stream(prompt, tools, **kwargs):
            if "content" in chunk.get("message", {{}}):
                full_response_content += chunk["message"]["content"]
            elif "error" in chunk:
                return {"error": chunk["error"]}

        # Attempt to parse tool call from the response
        tool_call_match = re.search(
            r"```json\s*(\{[\s\S]*?\})\s*```", full_response_content
        )
        if tool_call_match:
            try:
                json_str = tool_call_match.group(1)
                parsed_json = json.loads(json_str)
                if (
                    "tool_call" in parsed_json
                    and "name" in parsed_json["tool_call"]
                    and "arguments" in parsed_json["tool_call"]
                ):
                    return parsed_json
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON for tool call: {e}")
            except Exception as e:
                print(f"Unexpected error during tool call parsing: {e}")

        return {"response": full_response_content}


if __name__ == "__main__":

    async def main():
        print("--- Testing LocalLLMClient (Ollama) ---")

        # Create a dummy file_registry.json for testing
        file_registry_path = Path("file_registry.json")
        if not file_registry_path.is_file():
            print(f"Creating dummy {file_registry_path} for testing.")
            dummy_registry_content = [
                {
                    "path": "src/main.py",
                    "type": "file",
                    "description": "Main application entry point.",
                },
                {
                    "path": "docs/README.md",
                    "type": "file",
                    "description": "Project documentation.",
                },
                {
                    "path": "src/llm_wrapper/mcp/",
                    "type": "directory",
                    "description": "MCP related modules.",
                },
            ]
            file_registry_path.write_text(json.dumps(dummy_registry_content, indent=2))

        client = LocalLLMClient(
            model_name="llama2"
        )  # Ensure 'llama2' model is available in Ollama

        print("\nAttempting to connect to Ollama (this might take a moment)...")
        try:
            # Check if Ollama server is running and model is available
            # Note: client.chat will raise ResponseError if server is not available
            # or model is not found. We can try a simple list_models check.
            models = await client.client.list_models()
            if not any(m["model"] == client.model_name for m in models["models"]):
                print(
                    f"Error: Ollama model '{client.model_name}' not found. Please pull it (e.g., `ollama pull {client.model_name}`)"
                )
                if file_registry_path.is_file():
                    file_registry_path.unlink()
                return
            print(
                f"Successfully connected to Ollama and found model '{client.model_name}'."
            )
        except ollama.ResponseError as e:
            print(f"Ollama server not reachable or other API error: {e}")
            print("Please ensure Ollama server is running (e.g., `ollama serve`)")
            if file_registry_path.is_file():
                file_registry_path.unlink()
            return
        except Exception as e:
            print(f"An unexpected error occurred during Ollama setup: {e}")
            if file_registry_path.is_file():
                file_registry_path.unlink()
            return

        print("\nGenerating non-streaming response with file registry context:")
        response = await client.generate(
            "Summarize the project based on the file registry. What are the key directories?"
        )
        print(f"Response: {response.get('response')}")
        if response.get("error"):
            print(f"Error: {response['error']}")

        print("\nGenerating non-streaming response with tool simulation:")
        # Dummy tool for demonstration
        dummy_tool = Tool(
            name="local_tool_1",
            description="A test tool to retrieve local data.",
            input_schema={
                "type": "object",
                "properties": {"query": {"type": "string"}},
            },
        )
        response_with_tool = await client.generate(
            'Please use local_tool_1 to get some data. {"tool_call":{"name":"local_tool_1","arguments":{"query":"important info"}}}',
            tools=[dummy_tool],
        )
        print(f"Response with tool: {response_with_tool}")
        # The prompt is crafted to force the tool call format for demonstration.
        # In a real scenario, the LLM would naturally generate this.

        print("\nGenerating streaming response:")
        print("Story starts:")
        async for chunk in client.generate_stream(
            "Tell me a short story about a brave knight and a wise dragon."
        ):
            if "content" in chunk.get("message", {{}}):
                print(chunk["message"]["content"], end="", flush=True)
            elif "error" in chunk:
                print(f"\nStream Error: {chunk['error']}")
        print("\nStory ends.\n")

        # Cleanup dummy file
        if file_registry_path.is_file():
            file_registry_path.unlink()
            print(f"Deleted dummy {file_registry_path}.")

    asyncio.run(main())
