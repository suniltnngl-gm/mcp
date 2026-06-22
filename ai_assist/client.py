"""Fast Ollama cloud client for workspace AI assistance."""

import os
from pathlib import Path
from typing import Optional

import ollama
from dotenv import load_dotenv


ENV_FILE = Path.home() / "Public" / "ENV" / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)


CLOUD_HOST = "https://ollama.com"
FAST_MODEL = "ministral-3:8b"
SMART_MODEL = "gpt-oss:120b-cloud"


def get_client():
    api_key = os.environ.get("OLLAMA_API_KEY", "")
    return ollama.Client(
        host=CLOUD_HOST,
        headers={"Authorization": f"Bearer {api_key}"} if api_key else {},
    )


def ask(
    prompt: str,
    system: Optional[str] = None,
    model: str = FAST_MODEL,
    max_tokens: int = 512,
) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    try:
        client = get_client()
        resp = client.chat(model=model, messages=messages, options={"num_predict": max_tokens})
        return resp.message.content.strip()
    except Exception as e:
        return f"AI error: {e}"


def ask_smart(prompt: str, system: Optional[str] = None, **kwargs) -> str:
    kwargs.setdefault("max_tokens", 1024)
    return ask(prompt, system=system, model=SMART_MODEL, **kwargs)
