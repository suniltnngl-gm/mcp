"""Core file operations - extracted from 97 shared-tools."""

from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def safe_read(path: Path | str, default: str = "") -> str:
    """Safely read file with error handling.
    
    Used by 97 tools in shared-tools.
    Extracted to avoid duplication.
    """
    try:
        return Path(path).read_text()
    except Exception as e:
        logger.error(f"Failed to read {path}: {e}")
        return default


def safe_write(path: Path | str, content: str) -> bool:
    """Safely write file with error handling.
    
    Used by 97 tools in shared-tools.
    Extracted to avoid duplication.
    """
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        return True
    except Exception as e:
        logger.error(f"Failed to write {path}: {e}")
        return False


def file_exists(path: Path | str) -> bool:
    """Check if file exists safely."""
    try:
        return Path(path).exists()
    except:
        return False


def ensure_dir(path: Path | str) -> bool:
    """Ensure directory exists."""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        return False
