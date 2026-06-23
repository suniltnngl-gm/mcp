"""Release manager — tag, changelog, GitHub release."""

import subprocess
from datetime import datetime, timezone
from pathlib import Path

from review_cycle.github_automation.issue_creator import REPO_MAP


def _get_latest_tag(repo_path: Path) -> str:
    r = subprocess.run(
        ["git", "tag", "--sort=-creatordate", "--list"],
        cwd=repo_path, capture_output=True, text=True, timeout=10,
    )
    tags = [t.strip() for t in r.stdout.strip().splitlines() if t.strip()]
    return tags[0] if tags else ""


def _generate_changelog(repo_path: Path, since_tag: str) -> str:
    if since_tag:
        r = subprocess.run(
            ["git", "log", f"{since_tag}..HEAD", "--oneline"],
            cwd=repo_path, capture_output=True, text=True, timeout=10,
        )
    else:
        r = subprocess.run(
            ["git", "log", "--oneline", "-20"],
            cwd=repo_path, capture_output=True, text=True, timeout=10,
        )
    commits = r.stdout.strip().splitlines()
    if not commits:
        return "No changes since last release."
    lines = ["## Changelog", ""]
    for c in commits:
        lines.append(f"- {c}")
    lines.append("")
    return "\n".join(lines)


def create_release(repo: str, bump: str = "patch", dry_run: bool = False) -> dict:
    gh_repo = REPO_MAP.get(repo, repo)
    repo_path = Path.home() / "Public" / repo
    if not repo_path.exists():
        return {"error": f"repo path not found: {repo_path}"}

    latest = _get_latest_tag(repo_path)

    if latest:
        parts = latest.lstrip("v").split(".")
        if len(parts) == 3:
            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
            if bump == "major":
                major += 1; minor = 0; patch = 0
            elif bump == "minor":
                minor += 1; patch = 0
            else:
                patch += 1
            new_tag = f"v{major}.{minor}.{patch}"
        else:
            new_tag = f"v{datetime.now(timezone.utc).strftime('%Y%m%d')}"
    else:
        new_tag = "v0.1.0"

    changelog = _generate_changelog(repo_path, latest)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    body = f"## Release {new_tag}\n\n**Date:** {today}\n\n{changelog}"

    if dry_run:
        return {"repo": gh_repo, "tag": new_tag, "dry_run": True, "changelog": changelog}

    r_tag = subprocess.run(
        ["git", "tag", "-a", new_tag, "-m", f"Release {new_tag}"],
        cwd=repo_path, capture_output=True, text=True, timeout=10,
    )
    if r_tag.returncode != 0:
        return {"error": f"tag failed: {r_tag.stderr.strip()}"}

    r_push = subprocess.run(
        ["git", "push", "origin", new_tag],
        cwd=repo_path, capture_output=True, text=True, timeout=30,
    )
    if r_push.returncode != 0:
        return {"error": f"push failed: {r_push.stderr.strip()}"}

    r_release = subprocess.run(
        ["gh", "release", "create", new_tag, "--title", f"Release {new_tag}",
         "--notes", body, "--repo", f"suniltnngl-gm/{gh_repo}"],
        capture_output=True, text=True, timeout=30,
    )
    if r_release.returncode != 0:
        return {"error": f"release failed: {r_release.stderr.strip()}"}

    return {
        "repo": gh_repo,
        "tag": new_tag,
        "release_url": r_release.stdout.strip(),
        "success": True,
    }
