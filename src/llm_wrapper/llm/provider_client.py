# src/llm_wrapper/llm/provider_client.py

import asyncio
import json
import os
from typing import AsyncGenerator, Dict, List, Any, Optional

from openai import AsyncOpenAI  # Assuming openai-python library is installed
from mcp.types import Tool  # Use actual mcp types


class ProviderLLMClient:
    """
    A client for interacting with a provider LLM (OpenAI-compatible), supporting streaming,
    tool formatting, and basic token tracking.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: str = "gpt-4o",
    ):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = (
            base_url  # e.g., "https://api.openai.com/v1" or "http://localhost:1234/v1"
        )
        self.model_name = model_name

        if not self.api_key and not self.base_url:
            print(
                "Warning: OpenAI API key not provided and base_url not set. Will attempt connection without key."
            )
            print(
                "Set OPENAI_API_KEY environment variable or pass api_key to ProviderLLMClient."
            )

        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

    async def _format_tools_for_openai(self, tools: List[Tool]) -> List[Dict[str, Any]]:
        """
        Converts MCP Tool objects into OpenAI-compatible function calling format.
        """
        openai_tools = []
        for tool in tools:
            # OpenAI expects 'type' to be 'function'
            openai_tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema,  # Assuming inputSchema is already a dict (JSON Schema)
                    },
                }
            )
        return openai_tools

    async def generate_stream(
        self, prompt: str, tools: Optional[List[Tool]] = None, **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generates a streaming response from the provider LLM.
        """
        messages = [
            {"role": "user", "content": prompt},
        ]

        openai_tools = await self._format_tools_for_openai(tools) if tools else []

        try:
            stream = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=openai_tools if openai_tools else None,
                tool_choice="auto"
                if openai_tools
                else None,  # Allow model to choose tool if available
                stream=True,
                **kwargs,
            )

            async for chunk in stream:
                yield chunk.model_dump()  # Convert Pydantic model to dict
        except Exception as e:
            print(f"Error during provider LLM streaming generation: {e}")
            yield {"error": f"Provider LLM API Error: {e}"}

    async def generate(
        self, prompt: str, tools: Optional[List[Tool]] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Generates a complete response from the provider LLM, with token tracking
        and tool call parsing.
        """
        messages = [
            {"role": "user", "content": prompt},
        ]

        openai_tools = await self._format_tools_for_openai(tools) if tools else []

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=openai_tools if openai_tools else None,
                tool_choice="auto" if openai_tools else None,
                **kwargs,
            )

            response_dict = response.model_dump()  # Convert Pydantic model to dict

            # Basic Token Tracking
            input_tokens = response.usage.prompt_tokens if response.usage else 0
            output_tokens = response.usage.completion_tokens if response.usage else 0
            total_tokens = response.usage.total_tokens if response.usage else 0

            response_dict["token_usage"] = {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
            }

            # Check for tool calls
            tool_calls = response.choices[0].message.tool_calls
            if tool_calls:
                # Assuming single tool call for simplicity in this initial implementation
                first_tool_call = tool_calls[0].function
                return {
                    "tool_call": {
                        "name": first_tool_call.name,
                        "arguments": json.loads(first_tool_call.arguments),
                    },
                    "token_usage": response_dict["token_usage"],
                }

            return {
                "response": response.choices[0].message.content,
                "token_usage": response_dict["token_usage"],
            }

        except Exception as e:
            print(f"Error during provider LLM generation: {e}")
            return {"error": f"Provider LLM API Error: {e}"}


if __name__ == "__main__":

    async def main():
        print("--- Testing ProviderLLMClient (OpenAI-compatible) ---")

        # NOTE: For this test to work, you need:
        # 1. An OpenAI API key set as an environment variable (OPENAI_API_KEY)
        #    or passed directly to the client.
        # 2. Optionally, a local OpenAI-compatible server running (e.g., LM Studio, Ollama + openai-compatible server)
        #    If using a local server, set base_url.

        # Example with an actual OpenAI endpoint (requires API key)
        # client = ProviderLLMClient(model_name="gpt-4o")

        # Example with a local OpenAI-compatible endpoint (e.g., LM Studio default)
        client = ProviderLLMClient(
            base_url="http://localhost:1234/v1",
            model_name="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
        )
        print(f"Using model: {client.model_name}, Base URL: {client.base_url}")

        # Dummy tool for demonstration
        dummy_tool = Tool(
            name="get_current_weather",
            description="Get the current weather in a given location",
            input_schema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        )

        print("\nGenerating non-streaming response with tool call simulation:")
        try:
            response_with_tool = await client.generate(
                "What's the weather like in Boston?",
                tools=[dummy_tool],
                # Ensure model supports tool calling for best results
            )
            print(f"Response with tool: {json.dumps(response_with_tool, indent=2)}")
        except Exception as e:
            print(f"Error during tool call generation: {e}")

        print("\nGenerating streaming response (no tool):")
        full_stream_response = ""
        try:
            async for chunk in client.generate_stream(
                "Tell me a short poem about technology."
            ):
                if (
                    chunk.get("choices")
                    and chunk["choices"][0].delta
                    and chunk["choices"][0].delta.content
                ):
                    print(chunk["choices"][0].delta.content, end="", flush=True)
                    full_stream_response += chunk["choices"][0].delta.content
                elif chunk.get("error"):
                    print(f"\nStream Error: {chunk['error']}")
                    break
            print("\n")
        except Exception as e:
            print(f"Error during streaming generation: {e}")

        print("\nGenerating non-streaming response (no tool):")
        try:
            response_no_tool = await client.generate("Hello, who are you?")
            print(f"Response: {json.dumps(response_no_tool, indent=2)}")
        except Exception as e:
            print(f"Error during non-streaming generation: {e}")

    asyncio.run(main())
