#!/usr/bin/env python3
"""Cached Search - High-performance search with result caching"""

import time
from functools import lru_cache
from typing import Dict, List
from semantic_search import SemanticSearch, SearchResult
from type_based_search import TypeBasedSearch

class CachedSearch:
    def __init__(self):
        self.semantic_search = SemanticSearch()
        self.type_search = TypeBasedSearch()
        self._cache_stats = {'hits': 0, 'misses': 0}
    
    @lru_cache(maxsize=100)
    def _cached_semantic_search(self, query: str, max_results: int) -> tuple:
        """Cached semantic search (returns tuple for hashability)"""
        results = self.semantic_search.semantic_search(query, max_results)
        # Convert to tuple of tuples for caching
        return tuple((r.file_path, r.category, r.relevance_score, r.match_type, r.snippet) 
                    for r in results)
    
    @lru_cache(maxsize=50)
    def _cached_type_search(self, file_type: str, category: str = None) -> tuple:
        """Cached type-based search"""
        results = self.type_search.search_by_type(file_type, category)
        return tuple(results['matches']), tuple(results.get('summary', {}).items())
    
    @lru_cache(maxsize=30)
    def _cached_category_search(self, category: str, subcategory: str = None) -> dict:
        """Cached category search"""
        return self.type_search.search_by_category(category, subcategory)
    
    def semantic_search(self, query: str, max_results: int = 20) -> tuple:
        """High-performance semantic search with caching"""
        start_time = time.time()
        
        try:
            # Try cache first
            cached_results = self._cached_semantic_search(query, max_results)
            self._cache_stats['hits'] += 1
            
            # Convert back to SearchResult objects
            results = [SearchResult(
                file_path=r[0], category=r[1], relevance_score=r[2], 
                match_type=r[3], snippet=r[4]
            ) for r in cached_results]
            
        except Exception:
            # Cache miss or error, use direct search
            self._cache_stats['misses'] += 1
            results = self.semantic_search.semantic_search(query, max_results)
        
        search_time = time.time() - start_time
        return results, search_time
    
    def type_search(self, file_type: str, category: str = None) -> Dict:
        """High-performance type search with caching"""
        try:
            matches, summary = self._cached_type_search(file_type, category)
            self._cache_stats['hits'] += 1
            return {'matches': list(matches), 'summary': dict(summary)}
        except Exception:
            self._cache_stats['misses'] += 1
            return self.type_search.search_by_type(file_type, category)
    
    def category_search(self, category: str, subcategory: str = None) -> Dict:
        """High-performance category search with caching"""
        try:
            result = self._cached_category_search(category, subcategory)
            self._cache_stats['hits'] += 1
            return result
        except Exception:
            self._cache_stats['misses'] += 1
            return self.type_search.search_by_category(category, subcategory)
    
    def get_cache_stats(self) -> Dict:
        """Get cache performance statistics"""
        total = self._cache_stats['hits'] + self._cache_stats['misses']
        hit_rate = self._cache_stats['hits'] / max(total, 1)
        
        return {
            'cache_hits': self._cache_stats['hits'],
            'cache_misses': self._cache_stats['misses'],
            'hit_rate': hit_rate,
            'total_requests': total
        }
    
    def clear_cache(self):
        """Clear all caches"""
        self._cached_semantic_search.cache_clear()
        self._cached_type_search.cache_clear()
        self._cached_category_search.cache_clear()
        self._cache_stats = {'hits': 0, 'misses': 0}

def main():
    import sys
    
    cached_search = CachedSearch()
    
    if len(sys.argv) < 2:
        print("Usage: python3 cached_search.py <command> [args]")
        print("Commands:")
        print("  search <query>          - Cached semantic search")
        print("  type <type> [category]  - Cached type search")
        print("  category <cat> [subcat] - Cached category search")
        print("  stats                   - Show cache statistics")
        print("  benchmark               - Run performance benchmark")
        return
    
    command = sys.argv[1]
    
    if command == 'search' and len(sys.argv) >= 3:
        query = ' '.join(sys.argv[2:])
        results, search_time = cached_search.semantic_search(query)
        
        print(f"🔍 Cached Search: '{query}' ({search_time:.3f}s)")
        print("=" * 40)
        
        for i, result in enumerate(results[:5], 1):
            print(f"{i}. {result.file_path}")
            print(f"   📁 {result.category} | 🎯 {result.relevance_score:.2f}")
            print(f"   💬 {result.snippet[:80]}...")
            print()
    
    elif command == 'type' and len(sys.argv) >= 3:
        file_type = sys.argv[2]
        category = sys.argv[3] if len(sys.argv) > 3 else None
        
        results = cached_search.type_search(file_type, category)
        
        print(f"📄 Cached Type Search: {file_type}")
        if category:
            print(f"   Category: {category}")
        print("=" * 30)
        
        print(f"Found {len(results['matches'])} files")
        for file_path in results['matches'][:10]:
            print(f"  • {file_path}")
    
    elif command == 'category' and len(sys.argv) >= 3:
        category = sys.argv[2]
        subcategory = sys.argv[3] if len(sys.argv) > 3 else None
        
        results = cached_search.category_search(category, subcategory)
        
        print(f"📁 Cached Category Search: {category}")
        if subcategory:
            print(f"   Subcategory: {subcategory}")
        print("=" * 30)
        
        if 'total_files' in results:
            print(f"Total files: {results['total_files']}")
        elif 'matches' in results:
            print(f"Found {len(results['matches'])} files")
    
    elif command == 'stats':
        stats = cached_search.get_cache_stats()
        
        print("📊 Cache Statistics")
        print("=" * 20)
        print(f"Cache Hits: {stats['cache_hits']}")
        print(f"Cache Misses: {stats['cache_misses']}")
        print(f"Hit Rate: {stats['hit_rate']:.1%}")
        print(f"Total Requests: {stats['total_requests']}")
    
    elif command == 'benchmark':
        print("⚡ Performance Benchmark")
        print("=" * 25)
        
        # Test queries
        test_queries = ['python automation', 'category split', 'monitoring health']
        
        # Benchmark without cache
        cached_search.clear_cache()
        start_time = time.time()
        for query in test_queries:
            cached_search.semantic_search(query)
        cold_time = time.time() - start_time
        
        # Benchmark with cache (run same queries again)
        start_time = time.time()
        for query in test_queries:
            cached_search.semantic_search(query)
        warm_time = time.time() - start_time
        
        speedup = cold_time / max(warm_time, 0.001)
        
        print(f"Cold cache: {cold_time:.3f}s")
        print(f"Warm cache: {warm_time:.3f}s")
        print(f"Speedup: {speedup:.1f}x")
        
        stats = cached_search.get_cache_stats()
        print(f"Cache hit rate: {stats['hit_rate']:.1%}")

if __name__ == "__main__":
    main()
