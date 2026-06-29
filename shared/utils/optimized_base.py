"""
🚀 AI Orchestra - Optimized Provider Base
=========================================

High-performance base class for AI providers with:
- Lazy loading of dependencies
- Connection pooling
- Response caching
- Optimized error handling
"""

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union
from weakref import WeakValueDictionary

from ai_orchestra.utils.shared import console, get_env_var, get_logger

logger = get_logger(__name__)

@dataclass
class ProviderConfig:
    """Optimized provider configuration with defaults."""
    name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: float = 30.0
    max_retries: int = 3
    cache_responses: bool = True
    pool_connections: int = 10
    pool_maxsize: int = 10

class OptimizedProviderBase(ABC):
    """
    Optimized base class for AI providers with performance enhancements.
    """
    
    # Class-level cache for shared resources
    _client_cache: WeakValueDictionary = WeakValueDictionary()
    _response_cache: Dict[str, Any] = {}
    _cache_timestamps: Dict[str, float] = {}
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.logger = get_logger(f"{__name__}.{config.name}")
        self._client = None
        self._initialized = False
        
    @property
    def client(self):
        """Lazy-loaded client with caching."""
        if self._client is None:
            cache_key = f"{self.config.name}_{id(self.config)}"
            if cache_key in self._client_cache:
                self._client = self._client_cache[cache_key]
            else:
                self._client = self._create_client()
                self._client_cache[cache_key] = self._client
        return self._client
    
    @abstractmethod
    def _create_client(self):
        """Create the actual client instance."""
        pass
    
    @lru_cache(maxsize=128)
    def get_models(self) -> List[str]:
        """Get available models with caching."""
        return self._fetch_models()
    
    @abstractmethod
    def _fetch_models(self) -> List[str]:
        """Fetch models from the provider."""
        pass
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response with caching and optimization."""
        if self.config.cache_responses:
            cache_key = self._get_cache_key(prompt, kwargs)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                return cached_response
        
        try:
            response = self._generate_impl(prompt, **kwargs)
            
            if self.config.cache_responses:
                self._cache_response(cache_key, response)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            raise
    
    @abstractmethod
    def _generate_impl(self, prompt: str, **kwargs) -> str:
        """Actual generation implementation."""
        pass
    
    def _get_cache_key(self, prompt: str, kwargs: Dict) -> str:
        """Generate cache key for request."""
        import hashlib
        key_data = f"{prompt}_{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Get cached response if valid."""
        if cache_key in self._response_cache:
            timestamp = self._cache_timestamps.get(cache_key, 0)
            if time.time() - timestamp < 3600:  # 1 hour cache
                return self._response_cache[cache_key]
            else:
                # Clean expired cache
                self._response_cache.pop(cache_key, None)
                self._cache_timestamps.pop(cache_key, None)
        return None
    
    def _cache_response(self, cache_key: str, response: str):
        """Cache response with timestamp."""
        self._response_cache[cache_key] = response
        self._cache_timestamps[cache_key] = time.time()
        
        # Limit cache size
        if len(self._response_cache) > 1000:
            self._cleanup_cache()
    
    def _cleanup_cache(self):
        """Clean up old cache entries."""
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self._cache_timestamps.items()
            if current_time - timestamp > 3600
        ]
        
        for key in expired_keys:
            self._response_cache.pop(key, None)
            self._cache_timestamps.pop(key, None)
    
    async def generate_async(self, prompt: str, **kwargs) -> str:
        """Async generation with proper concurrency handling."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate, prompt, **kwargs)
    
    def health_check(self) -> Dict[str, Any]:
        """Optimized health check."""
        try:
            start_time = time.time()
            models = self.get_models()  # Uses cached result
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "models_available": len(models),
                "cache_size": len(self._response_cache)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "cache_size": len(self._response_cache)
            }
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, '_client') and self._client:
            try:
                if hasattr(self._client, 'close'):
                    self._client.close()
            except Exception:
                pass  # Ignore cleanup errors
