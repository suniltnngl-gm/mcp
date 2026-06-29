#!/usr/bin/env python3
"""Git-Based Backup: Don't Reinvent the Wheel"""

import subprocess
from pathlib import Path
from datetime import datetime


def git_backup(project_path, reason="manual"):
    """Use Git's proven backup: commit + tag"""
    project_path = Path(project_path).resolve()

    if not (project_path / ".git").exists():
        print("✗ Not a git repository")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    tag_name = f"backup/{reason}/{timestamp}"

    print(f"📦 Creating git backup: {tag_name}")

    try:
        # Stash any uncommitted changes
        subprocess.run(
            [
                "git",
                "-C",
                str(project_path),
                "stash",
                "push",
                "-u",
                "-m",
                f"Backup: {reason}",
            ],
            check=True,
            capture_output=True,
        )

        # Create tag at current state
        subprocess.run(
            [
                "git",
                "-C",
                str(project_path),
                "tag",
                "-a",
                tag_name,
                "-m",
                f"Backup: {reason}",
            ],
            check=True,
            capture_output=True,
        )

        print(f"✓ Backup created: {tag_name}")
        print(f"  Recover with: git checkout {tag_name}")
        return tag_name

    except subprocess.CalledProcessError as e:
        print(f"✗ Backup failed: {e}")
        return None


def git_recover(tag_name, project_path):
    """Recover from git tag"""
    project_path = Path(project_path).resolve()

    print(f"🔄 Recovering from: {tag_name}")

    try:
        # Checkout tag
        subprocess.run(["git", "-C", str(project_path), "checkout", tag_name], check=True)
        print(f"✓ Recovered to: {tag_name}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"✗ Recovery failed: {e}")
        return False


def list_git_backups(project_path):
    """List git backup tags"""
    project_path = Path(project_path).resolve()

    try:
        result = subprocess.run(
            ["git", "-C", str(project_path), "tag", "-l", "backup/*"],
            capture_output=True,
            text=True,
            check=True,
        )

        tags = result.stdout.strip().split("\n")
        return [t for t in tags if t]

    except subprocess.CalledProcessError:
        return []


def cleanup_old_backups(project_path, keep_recent=5):
    """Remove old backup tags"""
    backups = list_git_backups(project_path)

    if len(backups) <= keep_recent:
        print(f"✓ Only {len(backups)} backups, nothing to clean")
        return 0

    to_remove = backups[:-keep_recent]
    removed = 0

    for tag in to_remove:
        try:
            subprocess.run(
                ["git", "-C", str(project_path), "tag", "-d", tag],
                check=True,
                capture_output=True,
            )
            removed += 1
            print(f"🗑️  Removed: {tag}")
        except subprocess.CalledProcessError:
            pass

    print(f"✓ Cleaned up {removed} old backups")
    return removed


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  git_backup.py backup <project_path> [reason]")
        print("  git_backup.py list <project_path>")
        print("  git_backup.py recover <project_path> <tag_name>")
        print("  git_backup.py cleanup <project_path> [keep_recent]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "backup" and len(sys.argv) >= 3:
        path = sys.argv[2]
        reason = sys.argv[3] if len(sys.argv) > 3 else "manual"
        git_backup(path, reason)

    elif cmd == "list" and len(sys.argv) >= 3:
        path = sys.argv[2]
        backups = list_git_backups(path)
        print(f"\n📦 Git Backups ({len(backups)}):")
        for tag in backups:
            print(f"  {tag}")

    elif cmd == "recover" and len(sys.argv) >= 4:
        path = sys.argv[2]
        tag = sys.argv[3]
        git_recover(tag, path)

    elif cmd == "cleanup" and len(sys.argv) >= 3:
        path = sys.argv[2]
        keep = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        cleanup_old_backups(path, keep)
