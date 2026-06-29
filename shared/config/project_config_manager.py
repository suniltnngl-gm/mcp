#!/usr/bin/env python3
"""
⚙️ AI Orchestra - Configuration Manager
======================================

Provides centralized access to project configurations, like ignore patterns.
"""

import fnmatch
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
_ignore_patterns = []


def _load_ignore_patterns():
    """Loads ignore patterns from the .aiignore file."""
    global _ignore_patterns
    if _ignore_patterns:
        return

    ignore_file = PROJECT_ROOT / ".aiignore"
    if ignore_file.exists():
        with open(ignore_file) as f:
            _ignore_patterns = [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]


def is_path_ignored(path: Path) -> bool:
    """
    Checks if a given path should be ignored based on the central .aiignore file.

    Args:
        path (Path): The path to check.

    Returns:
        bool: True if the path should be ignored, False otherwise.
    """
    _load_ignore_patterns()

    # Convert to absolute path and get relative to project root
    if not path.is_absolute():
        path = PROJECT_ROOT / path

    try:
        relative_path_str = str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        # Path is not under PROJECT_ROOT, assume not ignored
        return False

    for pattern in _ignore_patterns:
        if fnmatch.fnmatch(relative_path_str, pattern) or fnmatch.fnmatch(
            path.name, pattern
        ):
            return True
        # Also check if any part of the path is a directory that should be ignored
        if pattern.endswith("/"):
            if any(p == pattern[:-1] for p in relative_path_str.split("/")):
                return True

    return False


if __name__ == "__main__":
    # Example usage:
    paths_to_check = [
        PROJECT_ROOT / "backups" / "test.zip",
        PROJECT_ROOT / "scripts" / "quality.py",
        PROJECT_ROOT / "logs" / "automation.log",
        PROJECT_ROOT / "__pycache__" / "some_cache.pyc",
        PROJECT_ROOT / ".venv" / "lib" / "python3.12" / "site-packages" / "rich",
        PROJECT_ROOT / "README.md",
    ]

    print("Checking example paths:")
    for p in paths_to_check:
        if is_path_ignored(p):
            print(f"  - IGNORED:  {p}")
        else:
            print(f"  - INCLUDED: {p}")
