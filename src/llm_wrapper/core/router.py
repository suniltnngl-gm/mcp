import re
import logging
from typing import Tuple, Any
from llm_wrapper.core.base import BaseLLMClient, LLMResponse
from llm_wrapper.providers.local_client import LocalCLIClient
from llm_wrapper.providers.remote_client import ProviderSDKClient

logger = logging.getLogger(__name__)


class RequestRouter:
    """Traffic controller for LLM requests with fallback capabilities."""

    def __init__(
        self, local_client: LocalCLIClient, provider_client: ProviderSDKClient
    ):
        # Clients are instantiated once and passed to the router
        self.local_client = local_client
        self.provider_client = provider_client
        logger.info(
            "RequestRouter initialized with provided LocalCLIClient and ProviderSDKClient instances."
        )

    async def generate_with_fallback(
        self, prompt: str, parameters: Dict[str, Any] = None, context: List[Dict] = None
    ) -> LLMResponse:
        """
        Attempts execution on the preferred route.
        If local fails, automatically escalates to provider.
        """
        # 1. Determine the preferred route
        target_client, clean_prompt = self.determine_route(prompt)

        # 2. Try preferred route
        try:
            response = await target_client.generate(clean_prompt, parameters, context)

            # Even if code runs, check for internal CLI errors (e.g. command not found)
            # This check is specific to LocalCLIClient returning an error message in content
            if target_client == self.local_client and "CLI Error:" in response.content:
                raise RuntimeError(
                    f"Local CLI execution reported an error: {response.content}"
                )

            return response

        except Exception as e:
            # 3. Fallback Logic
            if target_client == self.local_client:
                logger.warning(
                    f"Local client failed. Falling back to Provider SDK. Error: {e}"
                )

                # Tag the prompt so the provider knows it's a fallback (optional)
                fallback_prompt = f"[Local Fallback] {clean_prompt}"
                try:
                    return await self.provider_client.generate(
                        fallback_prompt, parameters, context
                    )
                except Exception as provider_e:
                    logger.error(
                        f"Critical failure: Both Local and Provider routes failed. Provider error: {provider_e}"
                    )
                    raise provider_e  # Re-raise if provider also fails

            # If provider itself fails (or was the initial target and failed), we raise the error up
            logger.error(f"Critical failure: Initial provider route failed. {e}")
            raise e

    def determine_route(self, prompt: str) -> Tuple[BaseLLMClient, str]:
        """
        Decides which client to use based on prompt analysis.
        Returns: (Client instance, clean_prompt)
        """
        # 1. Check for Explicit Tags
        if "@local" in prompt.lower():
            logger.info("Explicit @local tag found. Routing to LocalCLIClient.")
            return self.local_client, prompt.replace("@local", "").strip()

        if "@cloud" in prompt.lower() or "@provider" in prompt.lower():
            logger.info(
                "Explicit @cloud/@provider tag found. Routing to ProviderSDKClient."
            )
            return self.provider_client, prompt.replace("@cloud", "").replace(
                "@provider", ""
            ).strip()

        # 2. Rule-Based Complexity/Privacy Check
        if self._is_high_complexity(prompt):
            logger.info(
                "Prompt detected as high complexity. Routing to ProviderSDKClient."
            )
            return self.provider_client, prompt

        # Default to local for simple tasks to save cost/latency
        logger.info(
            "Prompt detected as low complexity/default. Routing to LocalCLIClient."
        )
        return self.local_client, prompt

    def _is_high_complexity(self, prompt: str) -> bool:
        """Heuristic to detect tasks requiring the 'Provider' tier."""
        # Keywords suggesting coding, complex logic, or math
        complex_patterns = [
            r"\b(write a function|debug|refactor|python|javascript)\b",
            r"\b(solve|calculate|theorem|complex)\b",
            r"\b(analyze|summarize this 50 page)\b",
            r"\b(generate code|implement solution)\b",
        ]

        # If prompt is long (> 200 chars, reduced from 500 for more aggressive provider routing on verbosity)
        if len(prompt) > 200:
            logger.debug(
                f"Prompt length ({len(prompt)}) > 200. Considered high complexity."
            )
            return True

        # Check against complex patterns
        is_complex = any(
            re.search(pattern, prompt, re.IGNORECASE) for pattern in complex_patterns
        )
        if is_complex:
            logger.debug("Prompt matched complex pattern. Considered high complexity.")
        return is_complex
