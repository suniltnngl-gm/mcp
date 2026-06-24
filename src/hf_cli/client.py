import json
import os
import subprocess
from pathlib import Path

HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_CACHE = Path.home() / "Public" / "hf"
BASE = "https://huggingface.co/api"


def _headers() -> dict:
    h = {"User-Agent": "hf-cli/0.1"}
    if HF_TOKEN:
        h["Authorization"] = f"Bearer {HF_TOKEN}"
    return h


def _curl(url: str, params: dict | None = None) -> dict:
    url = f"{url}?" + "&".join(f"{k}={v}" for k, v in (params or {}).items()) if params else url
    r = subprocess.run(
        ["curl", "-s", url] + (["-H", f"Authorization: Bearer {HF_TOKEN}"] if HF_TOKEN else []),
        capture_output=True, text=True, timeout=30,
    )
    if r.returncode != 0:
        return {"error": f"curl failed: {r.stderr.strip()}"}
    return json.loads(r.stdout)


def search_models(query: str, limit: int = 10) -> list[dict]:
    data = _curl(f"{BASE}/models", {"search": query, "limit": limit})
    return data if isinstance(data, list) else data.get("models", data.get("items", []))


def search_datasets(query: str, limit: int = 10) -> list[dict]:
    data = _curl(f"{BASE}/datasets", {"search": query, "limit": limit})
    return data if isinstance(data, list) else data.get("datasets", data.get("items", []))


def list_files(repo: str, path: str = "", revision: str = "main") -> list[dict]:
    url = f"{BASE}/models/{repo}/tree/{revision}"
    if path:
        url += f"/{path}"
    data = _curl(url)
    return data if isinstance(data, list) else []


def repo_info(repo: str) -> dict | None:
    data = _curl(f"{BASE}/models/{repo}")
    if isinstance(data, dict) and "error" not in data:
        return data
    data = _curl(f"{BASE}/datasets/{repo}")
    if isinstance(data, dict) and "error" not in data:
        return data
    return None
