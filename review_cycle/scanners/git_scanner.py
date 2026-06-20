import subprocess
from pathlib import Path
from typing import List

from review_cycle.models import ScanFinding


HOME = Path.home()
BASE = HOME / "Public"

ACTIVE_REPOS = {
    "Workspace": BASE / "Workspace",
    "project": BASE / "project",
    "repositories": BASE / "repositories",
    ".opencode": BASE / ".opencode",
    "coding-agent": BASE / "coding-agent",
    "next-steps": BASE / "next-steps",
    "shared-tools": BASE / "shared-tools",
    "firebase-app": BASE / "Workspace" / "firebase-app",
}


class GitScanner:
    def scan(self) -> List[ScanFinding]:
        findings = []
        for name, path in ACTIVE_REPOS.items():
            if not (path / ".git").exists():
                findings.append(
                    ScanFinding(
                        repo=name,
                        category="git_missing",
                        severity="warning",
                        summary=f"Not a git repository",
                        detail=f"{path} has no .git directory",
                        file_path=str(path),
                        suggested_action="Initialize with git init or clone",
                        score=0.5,
                    )
                )
                continue
            findings.extend(self._check_repo(name, path))
        return findings

    def _check_repo(self, name: str, path: Path) -> List[ScanFinding]:
        findings = []
        try:
            status = subprocess.run(
                ["git", "status", "--short"],
                cwd=path, capture_output=True, text=True, timeout=30,
            )
            dirty_lines = [l for l in status.stdout.splitlines() if l.strip()]
            if dirty_lines:
                mcount = sum(1 for l in dirty_lines if l.startswith(" M") or l.startswith("M "))
                acount = sum(1 for l in dirty_lines if l.startswith("??"))
                findings.append(
                    ScanFinding(
                        repo=name,
                        category="git_dirty",
                        severity="warning" if len(dirty_lines) <= 3 else "critical",
                        summary=f"{len(dirty_lines)} uncommitted file(s)",
                        detail=f"Modified: {mcount}, Untracked: {acount}\n{chr(10).join(dirty_lines[:10])}",
                        file_path=str(path),
                        suggested_action="Review and commit changes",
                        score=min(0.9, len(dirty_lines) * 0.1),
                    )
                )
            ahead = subprocess.run(
                ["git", "rev-list", "--count", "@{u}..HEAD", "--"],
                cwd=path, capture_output=True, text=True, timeout=15,
            )
            behind = subprocess.run(
                ["git", "rev-list", "--count", "HEAD..@{u}", "--"],
                cwd=path, capture_output=True, text=True, timeout=15,
            )
            ahead_count = int(ahead.stdout.strip() or 0)
            behind_count = int(behind.stdout.strip() or 0)
            if ahead_count > 0:
                findings.append(
                    ScanFinding(
                        repo=name,
                        category="git_unpushed",
                        severity="info",
                        summary=f"{ahead_count} commit(s) ahead of remote",
                        detail=f"Run git push to sync {ahead_count} local commits",
                        file_path=str(path),
                        suggested_action="git push",
                        score=0.3,
                    )
                )
            if behind_count > 0:
                findings.append(
                    ScanFinding(
                        repo=name,
                        category="git_behind",
                        severity="warning",
                        summary=f"{behind_count} commit(s) behind remote",
                        detail=f"Run git pull to sync with remote changes",
                        file_path=str(path),
                        suggested_action="git pull",
                        score=0.6,
                    )
                )
        except subprocess.TimeoutExpired:
            findings.append(
                ScanFinding(
                    repo=name,
                    category="git_timeout",
                    severity="warning",
                    summary="Git operation timed out",
                    detail=f"Could not check git state within 30s",
                    file_path=str(path),
                    suggested_action="Check repo manually",
                    score=0.4,
                )
            )
        except FileNotFoundError:
            findings.append(
                ScanFinding(
                    repo=name,
                    category="git_not_installed",
                    severity="blocker",
                    summary="Git not found",
                    detail="The git command is not installed or not in PATH",
                    suggested_action="Install git",
                    score=1.0,
                )
            )
        return findings
