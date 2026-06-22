"""Approval gate — determines whether a fix needs human review via PR.

Simple fixes (env example, gitignore entry, test stubs) commit directly.
Complex fixes (task status changes, tracking doc patches) go through
a branch + PR workflow.
"""

import subprocess
from pathlib import Path
from typing import Optional

from review_cycle.models import ScanFinding

HOME = Path.home()

FIXES_NEEDING_APPROVAL = {
    "task_stale",
    "tracking_outdated",
}


def needs_approval(category: str) -> bool:
    return category in FIXES_NEEDING_APPROVAL


def create_pr(
    finding: ScanFinding,
    branch_name: str,
    commit_message: str,
    repo_path: Optional[str] = None,
) -> dict:
    repo = repo_path or str(HOME / "Public" / finding.repo)
    result = {"success": False, "pr_url": "", "error": ""}

    try:
        subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=repo, capture_output=True, text=True, check=True,
        )
    except subprocess.CalledProcessError as e:
        result["error"] = f"Branch creation failed: {e.stderr[:200]}"
        return result

    try:
        subprocess.run(
            ["git", "add", "-A"],
            cwd=repo, capture_output=True, text=True, check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=repo, capture_output=True, text=True, check=True,
        )
    except subprocess.CalledProcessError as e:
        result["error"] = f"Commit failed: {e.stderr[:200]}"
        return result

    try:
        push = subprocess.run(
            ["git", "push", "origin", branch_name],
            cwd=repo, capture_output=True, text=True, check=True,
        )
    except subprocess.CalledProcessError as e:
        result["error"] = f"Push failed: {e.stderr[:200]}"
        return result

    try:
        gh = subprocess.run(
            ["gh", "pr", "create",
             "--title", commit_message,
             "--body", f"Auto-fix: {finding.summary}\n\n{finding.detail}",
             "--fill"],
            cwd=repo, capture_output=True, text=True, check=True,
        )
        result["pr_url"] = gh.stdout.strip()
        result["success"] = True
    except subprocess.CalledProcessError as e:
        result["error"] = f"PR creation failed: {e.stderr[:200]}"
        result["success"] = True

    return result
