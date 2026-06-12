from google import generativeai as genai
from llm_wrapper.core.config import settings
from llm_wrapper.core.base import BaseLLMClient, LLMResponse
from typing import Dict, Any, List, AsyncGenerator


class ProviderSDKClient(BaseLLMClient):
    """Professional provider tier using the Google GenAI SDK."""

    def __init__(self):
        # Ensure GOOGLE_API_KEY is in your .env
        if not settings.google_api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found in settings. Please set it in .env or environment variables."
            )
        genai.configure(api_key=settings.google_api_key)
        print("ProviderSDKClient initialized.")

    async def generate(
        self, prompt: str, parameters: Dict[str, Any] = None, context: List[Dict] = None
    ) -> LLMResponse:
        try:
            model_name = settings.provider_model_name
            model = genai.GenerativeModel(model_name)

            # TODO: Map ModelParameters to genai.GenerationConfig
            # TODO: Handle context (e.g., chat history) for genai

            response = await model.generate_content_async(
                contents=prompt,
                # generation_config=genai.types.GenerationConfig(**parameters) # This would require mapping
            )

            generated_text = ""
            if response.candidates:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, "text"):
                        generated_text += part.text

            return LLMResponse(
                content=generated_text.strip(),
                model=model_name,  # Use the actual model name from settings
                raw_response=str(response),
            )
        except Exception as e:
            # TODO: Define specific error types for better handling
            return LLMResponse(
                content=f"Error: {str(e)}", model=settings.provider_model_name
            )

    async def stream(
        self, prompt: str, parameters: Dict[str, Any] = None, context: List[Dict] = None
    ) -> AsyncGenerator[str, None]:
        model_name = settings.provider_model_name
        model = genai.GenerativeModel(model_name)

        # TODO: Implement full streaming logic
        responses = await model.generate_content_async(contents=prompt, stream=True)

        async for chunk in responses:
            if chunk.candidates:
                for part in chunk.candidates[0].content.parts:
                    if hasattr(part, "text"):
                        yield part.text

    async def list_models(self) -> List[str]:
        # TODO: Implement listing models using genai.list_models()
        return [settings.provider_model_name]  # Placeholder
