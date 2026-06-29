#!/usr/bin/env python3
"""API Key Manager - Secure key management for AI providers"""

import os
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass

@dataclass
class ProviderConfig:
    """Configuration for AI provider"""
    api_key: str
    base_url: str
    timeout: int = 30
    max_retries: int = 3

class APIKeyManager:
    """Secure API key management"""
    
    def __init__(self, env_file: str = ".env"):
        self.env_file = Path(env_file)
        self.providers = self._load_provider_configs()
    
    def _load_provider_configs(self) -> Dict[str, ProviderConfig]:
        """Load provider configurations from environment"""
        # Load .env file if exists
        if self.env_file.exists():
            self._load_env_file()
        
        return {
            "openrouter-free": ProviderConfig(
                api_key=os.getenv("OPENROUTER_API_KEY", ""),
                base_url="https://openrouter.ai/api/v1"
            ),
            "claude-sonnet": ProviderConfig(
                api_key=os.getenv("ANTHROPIC_API_KEY", ""),
                base_url="https://api.anthropic.com"
            ),
            "gpt-4": ProviderConfig(
                api_key=os.getenv("OPENAI_API_KEY", ""),
                base_url="https://api.openai.com/v1"
            ),
            "gemini-flash": ProviderConfig(
                api_key=os.getenv("GOOGLE_API_KEY", ""),
                base_url="https://generativelanguage.googleapis.com"
            )
        }
    
    def _load_env_file(self):
        """Load environment variables from .env file"""
        with open(self.env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value
    
    def get_provider_config(self, provider: str) -> Optional[ProviderConfig]:
        """Get configuration for specific provider"""
        return self.providers.get(provider)
    
    def is_provider_configured(self, provider: str) -> bool:
        """Check if provider is properly configured"""
        config = self.get_provider_config(provider)
        return config is not None and bool(config.api_key)
    
    def get_configured_providers(self) -> List[str]:
        """Get list of properly configured providers"""
        return [
            provider for provider in self.providers
            if self.is_provider_configured(provider)
        ]

# Global instance
api_key_manager = APIKeyManager()
