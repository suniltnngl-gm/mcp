from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class LLMResponse(BaseModel):
    """
    Standardized response schema for all LLM providers (local and remote).
    """

    content: str = Field(..., description="The generated text content from the LLM.")
    model: str = Field(
        ..., description="The identifier of the model that generated the response."
    )
    usage: Optional[Dict[str, Any]] = Field(
        None, description="Usage statistics, e.g., token counts."
    )
    raw_response: Optional[Any] = Field(
        None,
        description="The raw response object from the underlying LLM API for debugging.",
    )


class BaseLLMClient(ABC):
    """
    Unified abstract interface for all LLM providers (local and remote).
    This ensures that different LLM implementations adhere to a common contract.
    """

    @abstractmethod
    async def generate(
        self, prompt: str, parameters: Dict[str, Any] = None, context: List[Dict] = None
    ) -> LLMResponse:
        """
        Sends a request to the LLM and returns a standardized response.

        Args:
            prompt (str): The input prompt string for the LLM.
            parameters (Dict[str, Any]): Inference parameters (e.g., temperature, max_tokens).
            context (List[Dict]): Additional contextual information like chat history.

        Returns:
            LLMResponse: A standardized response object.
        """
        pass

    @abstractmethod
    async def stream(
        self, prompt: str, parameters: Dict[str, Any] = None, context: List[Dict] = None
    ):
        """
        Streams the LLM response tokens.

        Args:
            prompt (str): The input prompt string for the LLM.
            parameters (Dict[str, Any]): Inference parameters (e.g., temperature, max_tokens).
            context (List[Dict]): Additional contextual information like chat history.

        Yields:
            str: Chunks of generated text.
        """
        pass

    @abstractmethod
    async def list_models(self) -> List[str]:
        """
        Lists available models for this client.

        Returns:
            List[str]: A list of model identifiers.
        """
        pass
