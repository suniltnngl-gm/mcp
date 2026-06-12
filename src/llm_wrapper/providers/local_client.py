import subprocess
from llm_wrapper.core.base import BaseLLMClient, LLMResponse
from typing import Dict, Any, List, AsyncGenerator


class LocalCLIClient(BaseLLMClient):
    """Simulates a local LLM by calling the Gemini CLI."""

    async def generate(
        self, prompt: str, parameters: Dict[str, Any] = None, context: List[Dict] = None
    ) -> LLMResponse:
        try:
            # Executes: gemini -p "prompt"
            # TODO: Incorporate parameters and context into the CLI command if supported by `gemini -p`
            # For now, only prompt is passed.
            result = subprocess.run(
                ["gemini", "-p", prompt], capture_output=True, text=True, check=True
            )
            return LLMResponse(
                content=result.stdout.strip(),
                model="gemini-2.5-flash",  # As clarified by user
                raw_response={"stdout": result.stdout, "stderr": result.stderr},
            )
        except subprocess.CalledProcessError as e:
            # TODO: Define specific error types for better handling
            return LLMResponse(
                content=f"CLI Error: {e.stderr}",
                model="gemini-2.5-flash",
                raw_response=str(e),
            )
        except Exception as e:
            return LLMResponse(
                content=f"Unexpected error: {str(e)}", model="gemini-2.5-flash"
            )

    async def stream(
        self, prompt: str, parameters: Dict[str, Any] = None, context: List[Dict] = None
    ) -> AsyncGenerator[str, None]:
        # The `gemini -p` command does not inherently support streaming in a simple subprocess.run fashion.
        # This would require more advanced subprocess management (e.g., Popen, reading stdout line by line).
        # For now, we will generate the full response and yield it as a single chunk.
        response = await self.generate(prompt, parameters, context)
        yield response.content

    async def list_models(self) -> List[str]:
        # The local CLI typically only "uses" one configured model or an implicit default.
        return ["gemini-2.5-flash"]
