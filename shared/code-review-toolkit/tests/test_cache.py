"""Tests for caching system"""
import pytest
from pathlib import Path
from code_review_toolkit.cache import ReviewCache


def test_cache_initialization():
    """Test cache can be initialized"""
    cache = ReviewCache()
    assert cache is not None
    assert cache.cache_dir.exists()


def test_cache_key_generation():
    """Test cache key generation"""
    cache = ReviewCache()
    filepath = Path("test.py")
    content = "print('hello')"
    
    key1 = cache.get_cache_key(filepath, content)
    key2 = cache.get_cache_key(filepath, content)
    
    assert key1 == key2  # Same content = same key


def test_cache_key_changes_with_content():
    """Test cache key changes when content changes"""
    cache = ReviewCache()
    filepath = Path("test.py")
    
    key1 = cache.get_cache_key(filepath, "print('hello')")
    key2 = cache.get_cache_key(filepath, "print('world')")
    
    assert key1 != key2  # Different content = different key
