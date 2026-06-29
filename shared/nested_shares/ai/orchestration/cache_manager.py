#!/usr/bin/env python3
"""Cache Manager - Intelligent caching for AI responses"""

import json
import hashlib
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional, Dict

class IntelligentCache:
    """Multi-tier caching system for AI responses"""
    
    def __init__(self, cache_dir: str = "cache", default_ttl: int = 3600):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.default_ttl = default_ttl
        self.memory_cache = {}  # L1 cache (fastest)
        self.max_memory_items = 1000
    
    def _generate_cache_key(self, provider: str, prompt: str, params: Dict = None) -> str:
        """Generate unique cache key for request"""
        content = f"{provider}:{prompt}:{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cache_file(self, cache_key: str) -> Path:
        """Get cache file path for key"""
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, provider: str, prompt: str, params: Dict = None) -> Optional[Dict]:
        """Get cached response if available and valid"""
        cache_key = self._generate_cache_key(provider, prompt, params)
        
        # Check L1 cache (memory)
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            if entry["expires_at"] > time.time():
                return entry["data"]
            else:
                del self.memory_cache[cache_key]
        
        # Check L2 cache (file)
        cache_file = self._get_cache_file(cache_key)
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    entry = json.load(f)
                
                if entry["expires_at"] > time.time():
                    # Promote to L1 cache
                    self._add_to_memory_cache(cache_key, entry)
                    return entry["data"]
                else:
                    # Expired, remove file
                    cache_file.unlink()
            except (json.JSONDecodeError, KeyError):
                # Corrupted cache file, remove it
                cache_file.unlink()
        
        return None
    
    def set(self, provider: str, prompt: str, response: Dict, 
            params: Dict = None, ttl: int = None) -> bool:
        """Cache response with TTL"""
        cache_key = self._generate_cache_key(provider, prompt, params)
        ttl = ttl or self.default_ttl
        expires_at = time.time() + ttl
        
        entry = {
            "data": response,
            "created_at": time.time(),
            "expires_at": expires_at,
            "provider": provider,
            "ttl": ttl
        }
        
        # Store in L1 cache (memory)
        self._add_to_memory_cache(cache_key, entry)
        
        # Store in L2 cache (file)
        cache_file = self._get_cache_file(cache_key)
        try:
            with open(cache_file, 'w') as f:
                json.dump(entry, f)
            return True
        except Exception as e:
            print(f"Cache write error: {e}")
            return False
    
    def _add_to_memory_cache(self, cache_key: str, entry: Dict):
        """Add entry to memory cache with size limit"""
        # Remove oldest entries if at limit
        if len(self.memory_cache) >= self.max_memory_items:
            oldest_key = min(self.memory_cache.keys(), 
                           key=lambda k: self.memory_cache[k]["created_at"])
            del self.memory_cache[oldest_key]
        
        self.memory_cache[cache_key] = entry
    
    def clear_expired(self) -> int:
        """Clear expired cache entries"""
        current_time = time.time()
        removed_count = 0
        
        # Clear memory cache
        expired_keys = [
            key for key, entry in self.memory_cache.items()
            if entry["expires_at"] <= current_time
        ]
        for key in expired_keys:
            del self.memory_cache[key]
            removed_count += 1
        
        # Clear file cache
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file) as f:
                    entry = json.load(f)
                
                if entry["expires_at"] <= current_time:
                    cache_file.unlink()
                    removed_count += 1
            except (json.JSONDecodeError, KeyError):
                # Corrupted file, remove it
                cache_file.unlink()
                removed_count += 1
        
        return removed_count
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        file_count = len(list(self.cache_dir.glob("*.json")))
        memory_count = len(self.memory_cache)
        
        return {
            "memory_cache_size": memory_count,
            "file_cache_size": file_count,
            "total_cached_items": memory_count + file_count,
            "cache_directory": str(self.cache_dir),
            "memory_limit": self.max_memory_items
        }

# Global cache instance
intelligent_cache = IntelligentCache()
