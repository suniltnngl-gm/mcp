#!/usr/bin/env python3
"""Quick Search - Optimized search interface with all improvements"""

import time
from functools import lru_cache
from typing import Dict, List
from semantic_search import SemanticSearch
from type_based_search import TypeBasedSearch

class QuickSearch:
    def __init__(self):
        self.semantic_search = SemanticSearch()
        self.type_search = TypeBasedSearch()
        self.cache_stats = {'hits': 0, 'misses': 0}
    
    @lru_cache(maxsize=50)
    def quick_semantic_search(self, query: str) -> str:
        """Quick semantic search with formatted output"""
        results = self.semantic_search.semantic_search(query, max_results=5)
        
        if not results:
            return f"No results found for '{query}'"
        
        output = [f"🔍 '{query}' - {len(results)} results:"]
        for i, result in enumerate(results, 1):
            output.append(f"{i}. {result.file_path} ({result.relevance_score:.2f})")
        
        return '\n'.join(output)
    
    @lru_cache(maxsize=30)
    def quick_type_search(self, file_type: str) -> str:
        """Quick type search with formatted output"""
        results = self.type_search.search_by_type(file_type)
        
        output = [f"📄 {file_type} files - {len(results['matches'])} found:"]
        for file_path in results['matches'][:10]:
            output.append(f"  • {file_path}")
        
        if len(results['matches']) > 10:
            output.append(f"  ... and {len(results['matches']) - 10} more")
        
        return '\n'.join(output)
    
    @lru_cache(maxsize=20)
    def quick_category_overview(self, category: str) -> str:
        """Quick category overview"""
        results = self.type_search.search_by_category(category)
        
        if 'error' in results:
            return f"❌ {results['error']}"
        
        output = [f"📁 {category} - {results['total_files']} files:"]
        
        if results.get('subcategories'):
            output.append("  Subcategories:")
            for subcat, count in results['subcategories'].items():
                output.append(f"    • {subcat}: {count} files")
        
        if results.get('files_by_type'):
            output.append("  File types:")
            for ftype, files in results['files_by_type'].items():
                if files:
                    output.append(f"    • {ftype}: {len(files)} files")
        
        return '\n'.join(output)
    
    def smart_search(self, query: str) -> str:
        """Smart search that determines best search method"""
        query_lower = query.lower()
        
        # Check if it's a file type query
        file_types = ['python', 'py', 'shell', 'sh', 'javascript', 'js', 'docs', 'md', 'config', 'json']
        for ftype in file_types:
            if ftype in query_lower:
                actual_type = {'py': 'python', 'sh': 'shell', 'js': 'javascript', 'md': 'docs', 'json': 'config'}.get(ftype, ftype)
                return self.quick_type_search(actual_type)
        
        # Check if it's a category query
        categories = ['ai', 'workflow', 'refactor', 'core', 'docs', 'discussions', 'alternatives', 'utilities']
        for category in categories:
            if category in query_lower:
                return self.quick_category_overview(category)
        
        # Default to semantic search
        return self.quick_semantic_search(query)
    
    def get_navigation_menu(self) -> str:
        """Get quick navigation menu"""
        menu = self.type_search.generate_navigation_menu()
        
        output = ["🔍 Quick Navigation Menu"]
        output.append("=" * 25)
        output.append(f"📊 {menu['quick_stats']['total_files']} files, {menu['quick_stats']['total_categories']} categories")
        output.append("")
        
        output.append("📁 Categories:")
        for cat, info in menu['categories'].items():
            output.append(f"  • {cat}: {info['files']} files")
        
        output.append("\n📄 File Types:")
        for ftype, count in sorted(menu['file_types'].items(), key=lambda x: x[1], reverse=True):
            output.append(f"  • {ftype}: {count} files")
        
        return '\n'.join(output)
    
    def benchmark_performance(self) -> str:
        """Quick performance benchmark"""
        test_queries = ['python', 'automation', 'ai category']
        
        results = []
        total_time = 0
        
        for query in test_queries:
            start_time = time.time()
            self.smart_search(query)
            query_time = time.time() - start_time
            total_time += query_time
            results.append(f"  • '{query}': {query_time:.3f}s")
        
        output = ["⚡ Performance Benchmark"]
        output.append("=" * 25)
        output.extend(results)
        output.append(f"\nTotal time: {total_time:.3f}s")
        output.append(f"Average: {total_time/len(test_queries):.3f}s per query")
        
        return '\n'.join(output)

def main():
    import sys
    
    search = QuickSearch()
    
    if len(sys.argv) < 2:
        print("🚀 Quick Search - Optimized search interface")
        print("=" * 45)
        print("Usage: python3 quick_search.py <command>")
        print("")
        print("Commands:")
        print("  search <query>  - Smart search (auto-detects type)")
        print("  menu           - Show navigation menu")
        print("  benchmark      - Performance benchmark")
        print("  help           - Show this help")
        print("")
        print("Examples:")
        print("  python3 quick_search.py search python")
        print("  python3 quick_search.py search ai category")
        print("  python3 quick_search.py search automation tools")
        return
    
    command = sys.argv[1]
    
    if command == 'search' and len(sys.argv) >= 3:
        query = ' '.join(sys.argv[2:])
        result = search.smart_search(query)
        print(result)
    
    elif command == 'menu':
        menu = search.get_navigation_menu()
        print(menu)
    
    elif command == 'benchmark':
        benchmark = search.benchmark_performance()
        print(benchmark)
    
    elif command == 'help':
        print("🚀 Quick Search Help")
        print("=" * 20)
        print("Smart search automatically detects:")
        print("  • File types: python, shell, javascript, docs, config")
        print("  • Categories: ai, workflow, refactor, core, docs, etc.")
        print("  • General queries: uses semantic search")
        print("")
        print("Quick commands:")
        print("  qs search python     # Find Python files")
        print("  qs search ai         # Browse ai category")
        print("  qs menu             # Navigation menu")
        print("  qs benchmark        # Performance test")
    
    else:
        # Default to smart search for any other input
        query = ' '.join(sys.argv[1:])
        result = search.smart_search(query)
        print(result)

if __name__ == "__main__":
    main()
