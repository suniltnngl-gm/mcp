"""
Centralized Configuration Management.

This module handles loading and providing application configuration,
including securely loading secrets using SecretManager.
"""

import logging
import os
from pathlib import Path
from typing import Any, Optional

from src.core.secret_manager import SecretManager

logger = logging.getLogger(__name__)


class Config:
    """
    Centralized configuration object for the application.
    Loads settings from environment variables and securely handles secrets.
    """

    _instance: Optional["Config"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, vault_path: Path | None = None, encryption_key: bytes | None = None):
        if not hasattr(self, "_initialized"):
            self.secret_manager = SecretManager(
                vault_path=vault_path, encryption_key=encryption_key
            )
            self._settings: dict[str, Any] = {}
            self._load_config()
            self._initialized = True

    def _load_config(self):
        """Load configuration from environment variables, securely handling secrets."""
        logger.info("Loading application configuration...")

        # General Application Settings
        self._settings["DEVFLOW_ENV"] = os.getenv("DEVFLOW_ENV", "development")
        self._settings["DEVFLOW_LOG_LEVEL"] = os.getenv("DEVFLOW_LOG_LEVEL", "INFO")
        self._settings["DEVFLOW_DATA_DIR"] = Path(os.getenv("DEVFLOW_DATA_DIR", "./data"))

        # AI Provider API Keys (Securely loaded)
        self._settings["OPENAI_API_KEY"] = self.secret_manager.get_secret("OPENAI_API_KEY")
        self._settings["ANTHROPIC_API_KEY"] = self.secret_manager.get_secret("ANTHROPIC_API_KEY")
        self._settings["GOOGLE_API_KEY"] = self.secret_manager.get_secret("GOOGLE_API_KEY")

        # Security Settings
        self._settings["ENABLE_ENCRYPTION"] = (
            os.getenv("ENABLE_ENCRYPTION", "true").lower() == "true"
        )
        # The SECRET_KEY itself is used by SecretManager for encryption,
        # so it's handled during SecretManager initialization.
        # We don't store it directly in _settings unless needed for other purposes.

        # Knowledge Base Settings
        self._settings["KB_STORAGE_PATH"] = Path(
            os.getenv("KB_STORAGE_PATH", "./data/knowledge-base")
        )
        self._settings["KB_AUTO_BACKUP"] = os.getenv("KB_AUTO_BACKUP", "true").lower() == "true"
        self._settings["KB_BACKUP_INTERVAL"] = int(os.getenv("KB_BACKUP_INTERVAL", "3600"))

        # Feature Flags
        self._settings["ENABLE_AI_FEATURES"] = (
            os.getenv("ENABLE_AI_FEATURES", "false").lower() == "true"
        )
        self._settings["ENABLE_LEARNING"] = os.getenv("ENABLE_LEARNING", "false").lower() == "true"
        self._settings["ENABLE_PREDICTIONS"] = (
            os.getenv("ENABLE_PREDICTIONS", "false").lower() == "true"
        )

        # Performance Settings
        self._settings["MAX_WORKERS"] = int(os.getenv("MAX_WORKERS", "4"))
        self._settings["CACHE_SIZE"] = int(os.getenv("CACHE_SIZE", "1000"))
        self._settings["TIMEOUT"] = int(os.getenv("TIMEOUT", "30"))

        # Development Settings
        self._settings["DEBUG"] = os.getenv("DEBUG", "false").lower() == "true"
        self._settings["VERBOSE"] = os.getenv("VERBOSE", "false").lower() == "true"

        logger.info("Configuration loaded successfully.")

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration setting."""
        return self._settings.get(key, default)

    def __getattr__(self, name: str) -> Any:
        """Allow accessing settings as attributes (e.g., config.DEVFLOW_ENV)."""
        if name in self._settings:
            return self._settings[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


# Initialize a global config instance
config = Config()

# Configure logging based on loaded config
log_level_str = config.get("DEVFLOW_LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_str, logging.INFO)
logging.basicConfig(level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

if __name__ == "__main__":
    # Example usage:
    # To run this example, you would typically set environment variables
    # or have a vault.json with encrypted secrets.
    # For testing, you might temporarily set os.environ values.

    # Example of setting a secret via SecretManager (would be done externally)
    # manager = SecretManager()
    # manager.store_secret("OPENAI_API_KEY", "sk-test-openai-key")

    # Re-initialize config to pick up changes if run after setting secrets
    # config = Config()

    print(f"DevFlow Environment: {config.DEVFLOW_ENV}")
    print(f"Log Level: {config.DEVFLOW_LOG_LEVEL}")
    print(f"Data Directory: {config.DEVFLOW_DATA_DIR}")
    print(f"Enable AI Features: {config.ENABLE_AI_FEATURES}")
    print(f"OpenAI API Key (masked by SecretManager): {config.OPENAI_API_KEY}")
    print(f"Is Debug Mode: {config.DEBUG}")
