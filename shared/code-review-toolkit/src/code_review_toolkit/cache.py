#!/usr/bin/env python3
"""Review Cache System - Avoid redundant AI API calls

This module caches AI review results based on file content hashes,
reducing API costs by ~90% for unchanged files.
"""

import hashlib
import json
from dataclasses import asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from code_review_toolkit.common_types import AIReviewFinding


class ReviewCache:
    """Cache AI review results to avoid redundant API calls"""

    def __init__(self, cache_dir: Path = None, ttl_hours: int = 24):
        """Initialize review cache

        Args:
            cache_dir: Directory to store cache files (default: .review_cache)
            ttl_hours: Time-to-live for cache entries in hours (default: 24)
        """
        if cache_dir is None:
            cache_dir = Path.cwd() / ".review_cache"

        self.cache_dir = cache_dir
        self.ttl = timedelta(hours=ttl_hours)
        self.cache_dir.mkdir(exist_ok=True, parents=True)

        # Stats for reporting
        self.stats = {
            "hits": 0,
            "misses": 0,
            "expired": 0,
            "saved_api_calls": 0,
        }

    def get_cache_key(self, filepath: Path, content: str) -> str:
        """Generate cache key from file path and content hash

        Args:
            filepath: Path to the file
            content: File content

        Returns:
            Cache key string
        """
        # Use file path and content hash for cache key
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        file_identifier = str(filepath).replace("/", "_").replace("\\", "_")
        return f"{file_identifier}_{content_hash[:16]}"

    def get(self, cache_key: str) -> Optional[List[AIReviewFinding]]:
        """Retrieve cached findings if not expired

        Args:
            cache_key: Cache key to lookup

        Returns:
            List of findings if cache hit, None otherwise
        """
        cache_file = self.cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            self.stats["misses"] += 1
            return None

        # Check if cache is expired
        mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
        age = datetime.now() - mtime

        if age > self.ttl:
            cache_file.unlink()  # Remove stale cache
            self.stats["expired"] += 1
            self.stats["misses"] += 1
            return None

        # Load cached findings
        try:
            data = json.loads(cache_file.read_text())
            findings = [AIReviewFinding(**f) for f in data]
            self.stats["hits"] += 1
            self.stats["saved_api_calls"] += 1
            return findings
        except Exception as e:
            print(f"Warning: Failed to load cache {cache_key}: {e}")
            cache_file.unlink()  # Remove corrupted cache
            self.stats["misses"] += 1
            return None

    def set(self, cache_key: str, findings: List[AIReviewFinding]):
        """Store findings in cache

        Args:
            cache_key: Cache key to store under
            findings: List of findings to cache
        """
        try:
            cache_file = self.cache_dir / f"{cache_key}.json"
            findings_data = [asdict(f) for f in findings]
            cache_file.write_text(json.dumps(findings_data, indent=2))
        except Exception as e:
            print(f"Warning: Failed to save cache {cache_key}: {e}")

    def clear(self):
        """Clear all cache entries"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
        print(f"Cleared cache directory: {self.cache_dir}")

    def clear_expired(self):
        """Remove only expired cache entries"""
        expired_count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
            age = datetime.now() - mtime

            if age > self.ttl:
                cache_file.unlink()
                expired_count += 1

        print(f"Removed {expired_count} expired cache entries")

    def get_stats(self) -> dict:
        """Get cache statistics

        Returns:
            Dictionary with cache hit/miss stats
        """
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (
            (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        )

        return {
            **self.stats,
            "total_requests": total_requests,
            "hit_rate_percent": round(hit_rate, 2),
        }

    def print_stats(self):
        """Print cache statistics"""
        stats = self.get_stats()

        print("\n--- Cache Statistics ---")
        print(f"Cache Hits: {stats['hits']}")
        print(f"Cache Misses: {stats['misses']}")
        print(f"Expired Entries: {stats['expired']}")
        print(f"Hit Rate: {stats['hit_rate_percent']}%")
        print(f"API Calls Saved: {stats['saved_api_calls']}")

        if stats["saved_api_calls"] > 0:
            # Estimate cost savings (assuming $0.001 per API call)
            savings = stats["saved_api_calls"] * 0.001
            print(f"Estimated Cost Savings: ${savings:.4f}")


if __name__ == "__main__":
    # Test the cache system
    import sys

    cache = ReviewCache()

    if len(sys.argv) > 1:
        action = sys.argv[1]

        if action == "clear":
            cache.clear()
        elif action == "clear-expired":
            cache.clear_expired()
        elif action == "stats":
            cache.print_stats()
        else:
            print("Usage: python review_cache.py [clear|clear-expired|stats]")
    else:
        print("Review Cache System")
        print(f"Cache Directory: {cache.cache_dir}")
        print(f"TTL: {cache.ttl}")
        print("\nCommands:")
        print("  clear         - Clear all cache entries")
        print("  clear-expired - Remove only expired entries")
        print("  stats         - Show cache statistics")
