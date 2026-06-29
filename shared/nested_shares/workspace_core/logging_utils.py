"""Core logging utilities - extracted from 106 shared-tools."""

import logging
from pathlib import Path


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Setup logger with consistent format.
    
    Used by 106 tools in shared-tools.
    Extracted to avoid duplication.
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def log_error(logger: logging.Logger, message: str, exception: Exception = None):
    """Log error with optional exception."""
    if exception:
        logger.error(f"{message}: {exception}")
    else:
        logger.error(message)


def log_success(logger: logging.Logger, message: str):
    """Log success message."""
    logger.info(f"✓ {message}")


def log_warning(logger: logging.Logger, message: str):
    """Log warning message."""
    logger.warning(f"⚠️  {message}")
