"""
⚙️ AI Orchestra - Optimized Configuration Manager
================================================

High-performance configuration management with:
- Lazy loading of configuration files
- Environment variable caching
- Validation and type conversion
- Hot reloading support
"""

import json
import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ai_orchestra.utils.shared import get_env_var, get_logger

logger = get_logger(__name__)

@dataclass
class OptimizedConfig:
    """Optimized configuration with lazy loading and caching."""
    
    # Provider settings
    default_provider: str = "openai"
    fallback_providers: List[str] = field(default_factory=lambda: ["anthropic", "groq"])
    
    # Performance settings
    max_concurrent_requests: int = 10
    request_timeout: float = 30.0
    cache_responses: bool = True
    cache_ttl: int = 3600
    
    # Rate limiting
    rate_limit_requests_per_minute: int = 60
    rate_limit_burst: int = 10
    
    # Retry settings
    max_retries: int = 3
    retry_delay: float = 1.0
    exponential_backoff: bool = True
    
    # Monitoring
    enable_health_monitoring: bool = True
    health_check_interval: int = 300
    enable_metrics: bool = True
    
    # Database
    database_url: Optional[str] = None
    database_pool_size: int = 5
    
    def __post_init__(self):
        """Load configuration from environment after initialization."""
        self._load_from_environment()
    
    def _load_from_environment(self):
        """Load configuration from environment variables with caching."""
        # Provider settings
        self.default_provider = get_env_var("AI_DEFAULT_PROVIDER", self.default_provider)
        
        fallback_str = get_env_var("AI_FALLBACK_PROVIDERS")
        if fallback_str:
            self.fallback_providers = [p.strip() for p in fallback_str.split(",")]
        
        # Performance settings
        self.max_concurrent_requests = int(get_env_var("AI_MAX_CONCURRENT", str(self.max_concurrent_requests)))
        self.request_timeout = float(get_env_var("AI_REQUEST_TIMEOUT", str(self.request_timeout)))
        self.cache_responses = get_env_var("AI_CACHE_RESPONSES", "true").lower() == "true"
        self.cache_ttl = int(get_env_var("AI_CACHE_TTL", str(self.cache_ttl)))
        
        # Rate limiting
        self.rate_limit_requests_per_minute = int(get_env_var("AI_RATE_LIMIT_RPM", str(self.rate_limit_requests_per_minute)))
        self.rate_limit_burst = int(get_env_var("AI_RATE_LIMIT_BURST", str(self.rate_limit_burst)))
        
        # Retry settings
        self.max_retries = int(get_env_var("AI_MAX_RETRIES", str(self.max_retries)))
        self.retry_delay = float(get_env_var("AI_RETRY_DELAY", str(self.retry_delay)))
        self.exponential_backoff = get_env_var("AI_EXPONENTIAL_BACKOFF", "true").lower() == "true"
        
        # Monitoring
        self.enable_health_monitoring = get_env_var("AI_ENABLE_HEALTH_MONITORING", "true").lower() == "true"
        self.health_check_interval = int(get_env_var("AI_HEALTH_CHECK_INTERVAL", str(self.health_check_interval)))
        self.enable_metrics = get_env_var("AI_ENABLE_METRICS", "true").lower() == "true"
        
        # Database
        self.database_url = get_env_var("DATABASE_URL", self.database_url)
        self.database_pool_size = int(get_env_var("DATABASE_POOL_SIZE", str(self.database_pool_size)))

class ConfigManager:
    """Singleton configuration manager with lazy loading."""
    
    _instance: Optional['ConfigManager'] = None
    _config: Optional[OptimizedConfig] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @property
    def config(self) -> OptimizedConfig:
        """Get configuration with lazy loading."""
        if self._config is None:
            self._config = self._load_config()
        return self._config
    
    def _load_config(self) -> OptimizedConfig:
        """Load configuration from various sources."""
        config = OptimizedConfig()
        
        # Try to load from config file if it exists
        config_file = Path("config/ai_orchestra.json")
        if config_file.exists():
            try:
                with open(config_file) as f:
                    file_config = json.load(f)
                    self._update_config_from_dict(config, file_config)
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")
        
        return config
    
    def _update_config_from_dict(self, config: OptimizedConfig, data: Dict[str, Any]):
        """Update configuration from dictionary."""
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
    
    @lru_cache(maxsize=128)
    def get_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """Get provider-specific configuration with caching."""
        base_config = {
            "timeout": self.config.request_timeout,
            "max_retries": self.config.max_retries,
            "cache_responses": self.config.cache_responses,
        }
        
        # Provider-specific overrides
        provider_configs = {
            "openai": {
                "api_key": get_env_var("OPENAI_API_KEY"),
                "base_url": get_env_var("OPENAI_BASE_URL"),
            },
            "anthropic": {
                "api_key": get_env_var("ANTHROPIC_API_KEY"),
                "base_url": get_env_var("ANTHROPIC_BASE_URL"),
            },
            "groq": {
                "api_key": get_env_var("GROQ_API_KEY"),
                "base_url": get_env_var("GROQ_BASE_URL"),
            },
        }
        
        if provider_name in provider_configs:
            base_config.update(provider_configs[provider_name])
        
        return base_config
    
    def reload_config(self):
        """Reload configuration from sources."""
        self._config = None
        # Clear caches
        self.get_provider_config.cache_clear()
        logger.info("Configuration reloaded")

# Global configuration instance
config_manager = ConfigManager()

def get_config() -> OptimizedConfig:
    """Get the global configuration instance."""
    return config_manager.config

def get_provider_config(provider_name: str) -> Dict[str, Any]:
    """Get provider-specific configuration."""
    return config_manager.get_provider_config(provider_name)
