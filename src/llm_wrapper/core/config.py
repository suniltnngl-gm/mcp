from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings for the LLM wrapper, loaded from environment variables (.env file).
    """

    # Provider Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None  # Added Google API Key

    # Local Provider Config
    ollama_base_url: str = "http://localhost:11434"
    default_local_model: str = "llama3"

    # Remote Provider Config
    provider_model_name: str = "gemini-2.5-flash"  # Updated default provider model name

    # MCP Settings
    mcp_server_timeout: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton instance of settings
settings = Settings()
