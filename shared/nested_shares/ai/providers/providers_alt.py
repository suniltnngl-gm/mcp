#!/usr/bin/env python3
"""API Provider Abstraction Layer"""

import json
import logging
import os

import requests

from agent.config import get_gemini_api_key, get_openai_api_key

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class APIProvider:
    def generate(self, prompt: str) -> str:
        """Generate text based on prompt"""
        return f"# Local template: {prompt}"

    def _fallback(self, prompt: str) -> str:
        """Fallback to local template"""
        return f"# Fallback template: {prompt}"


class GeminiProvider(APIProvider):
    def generate(self, prompt: str) -> str:
        api_key = get_gemini_api_key()
        if not api_key:
            return self._fallback(prompt)

        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.0-pro:generateContent?key={api_key}",
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=10,
            )
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except requests.exceptions.RequestException as e:
            logging.exception(f"Gemini API request failed: {e}")
        except (json.JSONDecodeError, KeyError) as e:
            logging.exception(f"Gemini API response parsing failed: {e}")
        except Exception as e:
            logging.exception(f"An unexpected error occurred with Gemini API: {e}")
        return self._fallback(prompt)


class OpenAIProvider(APIProvider):
    def generate(self, prompt: str) -> str:
        api_key = get_openai_api_key()
        if not api_key:
            return self._fallback(prompt)

        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=10,
            )
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            logging.exception(f"OpenAI API request failed: {e}")
        except (json.JSONDecodeError, KeyError) as e:
            logging.exception(f"OpenAI API response parsing failed: {e}")
        except Exception as e:
            logging.exception(f"An unexpected error occurred with OpenAI API: {e}")
        return self._fallback(prompt)


class ProviderManager:
    def __init__(self):
        self.providers = {
            "gemini": GeminiProvider(),
            "openai": OpenAIProvider(),
            "local": APIProvider(),  # Default fallback
        }
        self.current_provider = "local"

    def set_provider(self, provider_name: str):
        if provider_name in self.providers:
            self.current_provider = provider_name
        else:
            print(f"Warning: Provider {provider_name} not found. Using local fallback.")

    def generate(self, prompt: str, language: str = "python") -> str:
        return self.providers[self.current_provider].generate(prompt)

    def execute(self, code: str, language: str = "python") -> dict:
        # Placeholder for execution logic, not directly handled by API providers
        return {"stdout": "", "stderr": "", "returncode": 0}


if __name__ == "__main__":
    manager = ProviderManager()

    # Test Gemini
    os.environ["GEMINI_API_KEY"] = "YOUR_GEMINI_KEY"  # Replace with actual key
    manager.set_provider("gemini")
    print("Gemini response:", manager.generate("Hello world in python"))

    # Test OpenAI
    os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_KEY"  # Replace with actual key
    manager.set_provider("openai")
    print("OpenAI response:", manager.generate("Hello world in javascript"))

    # Test local fallback
    del os.environ["GEMINI_API_KEY"]
    del os.environ["OPENAI_API_KEY"]
    manager.set_provider("local")
    print("Local response:", manager.generate("Hello world"))
