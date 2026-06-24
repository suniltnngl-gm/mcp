import os
import subprocess
from pathlib import Path

HF_TOKEN = os.getenv("HF_TOKEN", "")
BASE = "https://huggingface.co"


def _git_push(repo_type: str, repo_id: str, local_path: Path, message: str) -> dict:
    if not HF_TOKEN:
        return {"error": "HF_TOKEN not set"}
    auth_url = f"https://user:{HF_TOKEN}@huggingface.co/{repo_id}"
    try:
        r = subprocess.run(
            ["git", "clone", "--depth=1", auth_url, str(local_path / ".hf-clone")],
            capture_output=True, text=True, timeout=60,
        )
        if r.returncode != 0:
            return {"error": f"clone failed: {r.stderr.strip()}"}

        clone_dir = local_path / ".hf-clone"
        target = clone_dir / local_path.name
        if target.exists():
            subprocess.run(["cp", "-r", str(local_path) + "/*", str(clone_dir)],
                           capture_output=True, timeout=30)
        else:
            subprocess.run(["cp", "-r", str(local_path), str(clone_dir.parent)],
                           capture_output=True, timeout=30)

        subprocess.run(["git", "add", "-A"], cwd=clone_dir, capture_output=True, timeout=30)
        subprocess.run(["git", "commit", "-m", message], cwd=clone_dir,
                       capture_output=True, timeout=30)
        r2 = subprocess.run(["git", "push"], cwd=clone_dir,
                            capture_output=True, text=True, timeout=120)
        subprocess.run(["rm", "-rf", str(clone_dir)], capture_output=True, timeout=30)

        if r2.returncode != 0:
            return {"error": f"push failed: {r2.stderr.strip()}"}
        return {"success": True, "repo": repo_id, "message": message}
    except subprocess.TimeoutExpired:
        return {"error": "operation timed out"}
    except Exception as e:
        return {"error": str(e)}


def upload_file(repo_type: str, repo_id: str, local_path: Path,
                path_in_repo: str = "", message: str = "upload via hf-cli") -> dict:
    return _git_push(repo_type, repo_id, local_path, message)
