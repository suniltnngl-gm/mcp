import hashlib
import json
import os
import subprocess
from pathlib import Path

CACHE_DIR = Path.home() / "Public" / "hf"
MANIFEST_FILE = CACHE_DIR / "manifest.json"
HF_TOKEN = os.getenv("HF_TOKEN", "")
BASE = "https://huggingface.co"


def _load_manifest() -> dict:
    if MANIFEST_FILE.exists():
        return json.loads(MANIFEST_FILE.read_text())
    return {}


def _save_manifest(m: dict):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_FILE.write_text(json.dumps(m, indent=2))


def _curl_dl(url: str, dest: Path, resume: bool = True):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["curl", "-L", "-o", str(dest)]
    if resume and dest.exists():
        cmd += ["-C", "-"]
    if HF_TOKEN:
        cmd += ["-H", f"Authorization: Bearer {HF_TOKEN}"]
    cmd.append(url)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode not in (0, 33):
        return {"error": f"download failed: {r.stderr.strip()}"}
    return {"path": str(dest), "size": dest.stat().st_size if dest.exists() else 0}


def download_model(repo: str, filename: str | None = None,
                   revision: str = "main", cache: bool = True) -> dict:
    dest_dir = CACHE_DIR / "models" / repo.replace("/", "--")
    manifest = _load_manifest() if cache else {}
    key = f"model:{repo}:{filename or 'full'}:{revision}"

    if cache and key in manifest:
        cached = Path(manifest[key]["path"])
        if cached.exists():
            manifest[key]["hits"] = manifest[key].get("hits", 0) + 1
            _save_manifest(manifest)
            return {"cached": True, "path": str(cached), "size": cached.stat().st_size}

    if filename:
        url = f"{BASE}/{repo}/resolve/{revision}/{filename}"
        dest = dest_dir / revision / filename
        result = _curl_dl(url, dest)
    else:
        url = f"{BASE}/{repo}/resolve/{revision}"
        dest = dest_dir / f"{revision}.tar.gz"
        result = _curl_dl(f"{url}/download", dest)

    if "error" not in result and cache:
        manifest[key] = {"path": result["path"], "size": result["size"], "revision": revision}
        _save_manifest(manifest)

    return result


def download_dataset(repo: str, filename: str | None = None,
                     revision: str = "main", cache: bool = True) -> dict:
    dest_dir = CACHE_DIR / "datasets" / repo.replace("/", "--")
    manifest = _load_manifest() if cache else {}
    key = f"dataset:{repo}:{filename or 'full'}:{revision}"

    if cache and key in manifest:
        cached = Path(manifest[key]["path"])
        if cached.exists():
            manifest[key]["hits"] = manifest[key].get("hits", 0) + 1
            _save_manifest(manifest)
            return {"cached": True, "path": str(cached), "size": cached.stat().st_size}

    if filename:
        url = f"{BASE}/datasets/{repo}/resolve/{revision}/{filename}"
        dest = dest_dir / revision / filename
        result = _curl_dl(url, dest)
    else:
        url = f"{BASE}/datasets/{repo}/resolve/{revision}"
        dest = dest_dir / f"{revision}.tar.gz"
        result = _curl_dl(f"{url}/download", dest)

    if "error" not in result and cache:
        manifest[key] = {"path": result["path"], "size": result["size"], "revision": revision}
        _save_manifest(manifest)

    return result


def cache_info() -> dict:
    manifest = _load_manifest()
    total_size = sum(e.get("size", 0) for e in manifest.values())
    return {"entries": len(manifest), "total_size_mb": round(total_size / (1024 * 1024), 1)}


def cache_clear(key: str | None = None):
    manifest = _load_manifest()
    if key:
        manifest.pop(key, None)
    else:
        manifest = {}
    _save_manifest(manifest)
