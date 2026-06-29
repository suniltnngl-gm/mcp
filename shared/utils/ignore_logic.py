"""Smart ignore logic for file operations."""

IGNORE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    "*.pyo",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "node_modules",
    ".venv",
    "venv",
    ".git",
    "*.egg-info",
    ".coverage",
    ".DS_Store",
]

def should_ignore(path: str) -> bool:
    """Check if path should be ignored."""
    import fnmatch
    from pathlib import Path
    
    p = Path(path)
    for pattern in IGNORE_PATTERNS:
        if fnmatch.fnmatch(p.name, pattern):
            return True
        if any(fnmatch.fnmatch(part, pattern) for part in p.parts):
            return True
    return False
