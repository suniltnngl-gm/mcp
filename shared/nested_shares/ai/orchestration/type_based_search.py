#!/usr/bin/env python3
"""Type-Based Search System - Enhanced search with file type filters and category navigation"""

from shared_tools.utils.config_utils import get_workspace_path
import os
import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

class TypeBasedSearch:
    def __init__(self):
        self.workspace_path = get_workspace_path() / "shared-tools" / "nested-shares"
        self.file_types = {
            'python': ['.py'],
            'shell': ['.sh'],
            'javascript': ['.js', '.ts'],
            'config': ['.json', '.yaml', '.yml', '.toml', '.ini'],
            'docs': ['.md', '.txt', '.rst'],
            'data': ['.csv', '.jsonl', '.xml']
        }
        self.categories = self._scan_categories()
    
    def _scan_categories(self) -> Dict[str, Dict]:
        """Scan and categorize all files by type and location"""
        categories = {}
        
        for cat_dir in self.workspace_path.iterdir():
            if not cat_dir.is_dir() or cat_dir.name.startswith('.'):
                continue
                
            cat_info = {
                'files': defaultdict(list),
                'subcategories': {},
                'total_files': 0
            }
            
            # Scan files and subcategories
            for item in cat_dir.rglob("*"):
                if item.is_file():
                    file_type = self._get_file_type(item)
                    rel_path = item.relative_to(self.workspace_path)
                    cat_info['files'][file_type].append(str(rel_path))
                    cat_info['total_files'] += 1
                elif item.is_dir() and item != cat_dir:
                    subcat_name = item.relative_to(cat_dir).parts[0]
                    if subcat_name not in cat_info['subcategories']:
                        cat_info['subcategories'][subcat_name] = 0
                    cat_info['subcategories'][subcat_name] += len([f for f in item.rglob("*") if f.is_file()])
            
            categories[cat_dir.name] = cat_info
        
        return categories
    
    def _get_file_type(self, file_path: Path) -> str:
        """Determine file type from extension"""
        suffix = file_path.suffix.lower()
        for type_name, extensions in self.file_types.items():
            if suffix in extensions:
                return type_name
        return 'other'
    
    def search_by_type(self, file_type: str, category: str = None) -> Dict:
        """Search files by type, optionally filtered by category"""
        results = {'matches': [], 'summary': {}}
        
        categories_to_search = [category] if category else self.categories.keys()
        
        for cat_name in categories_to_search:
            if cat_name in self.categories:
                files = self.categories[cat_name]['files'].get(file_type, [])
                results['matches'].extend(files)
                if files:
                    results['summary'][cat_name] = len(files)
        
        return results
    
    def search_by_category(self, category: str, subcategory: str = None) -> Dict:
        """Search within specific category/subcategory"""
        if category not in self.categories:
            return {'error': f'Category {category} not found'}
        
        cat_info = self.categories[category]
        
        if subcategory:
            # Filter by subcategory
            matches = []
            for file_type, files in cat_info['files'].items():
                for file_path in files:
                    if f"{category}/{subcategory}" in file_path:
                        matches.append(file_path)
            return {'matches': matches, 'subcategory': subcategory}
        
        return {
            'files_by_type': dict(cat_info['files']),
            'subcategories': cat_info['subcategories'],
            'total_files': cat_info['total_files']
        }
    
    def mixed_content_preview(self, category: str) -> Dict:
        """Preview mixed content in a category"""
        if category not in self.categories:
            return {'error': f'Category {category} not found'}
        
        cat_info = self.categories[category]
        preview = {
            'category': category,
            'file_types': {},
            'diversity_score': 0,
            'recommendations': []
        }
        
        # Analyze file type distribution
        total_files = cat_info['total_files']
        for file_type, files in cat_info['files'].items():
            count = len(files)
            if count > 0:
                preview['file_types'][file_type] = {
                    'count': count,
                    'percentage': round((count / total_files) * 100, 1),
                    'sample_files': files[:3]
                }
        
        # Calculate diversity score (higher = more mixed)
        type_count = len([t for t, f in cat_info['files'].items() if f])
        preview['diversity_score'] = type_count
        
        # Generate recommendations
        if type_count > 3:
            preview['recommendations'].append('Consider splitting by file type')
        if total_files > 50:
            preview['recommendations'].append('Large category - consider subcategorization')
        
        return preview
    
    def generate_navigation_menu(self) -> Dict:
        """Generate navigation menu for categories and types"""
        menu = {
            'categories': {},
            'file_types': defaultdict(int),
            'quick_stats': {}
        }
        
        total_files = 0
        for cat_name, cat_info in self.categories.items():
            menu['categories'][cat_name] = {
                'files': cat_info['total_files'],
                'subcategories': list(cat_info['subcategories'].keys()),
                'top_types': sorted(
                    [(t, len(f)) for t, f in cat_info['files'].items() if f],
                    key=lambda x: x[1], reverse=True
                )[:3]
            }
            
            # Aggregate file types
            for file_type, files in cat_info['files'].items():
                menu['file_types'][file_type] += len(files)
            
            total_files += cat_info['total_files']
        
        menu['quick_stats'] = {
            'total_files': total_files,
            'total_categories': len(self.categories),
            'total_file_types': len(menu['file_types'])
        }
        
        return menu

def main():
    import sys
    
    search = TypeBasedSearch()
    
    if len(sys.argv) < 2:
        print("Usage: python3 type_based_search.py <command> [args]")
        print("Commands:")
        print("  menu                    - Show navigation menu")
        print("  type <type> [category]  - Search by file type")
        print("  category <cat> [subcat] - Search by category")
        print("  preview <category>      - Mixed content preview")
        return
    
    command = sys.argv[1]
    
    if command == 'menu':
        menu = search.generate_navigation_menu()
        print("🔍 Type-Based Search Navigation")
        print("=" * 35)
        print(f"📊 Quick Stats: {menu['quick_stats']['total_files']} files, {menu['quick_stats']['total_categories']} categories")
        print()
        
        print("📁 Categories:")
        for cat, info in menu['categories'].items():
            print(f"  • {cat}: {info['files']} files")
            if info['subcategories']:
                print(f"    └─ Subcategories: {', '.join(info['subcategories'])}")
        
        print("\n📄 File Types:")
        for ftype, count in sorted(menu['file_types'].items(), key=lambda x: x[1], reverse=True):
            print(f"  • {ftype}: {count} files")
    
    elif command == 'type' and len(sys.argv) >= 3:
        file_type = sys.argv[2]
        category = sys.argv[3] if len(sys.argv) > 3 else None
        
        results = search.search_by_type(file_type, category)
        print(f"🔍 {file_type.title()} Files" + (f" in {category}" if category else ""))
        print("=" * 30)
        
        if 'summary' in results:
            for cat, count in results['summary'].items():
                print(f"📁 {cat}: {count} files")
        
        print(f"\n📄 Files ({len(results['matches'])}):")
        for file_path in results['matches'][:10]:
            print(f"  • {file_path}")
        
        if len(results['matches']) > 10:
            print(f"  ... and {len(results['matches']) - 10} more")
    
    elif command == 'category' and len(sys.argv) >= 3:
        category = sys.argv[2]
        subcategory = sys.argv[3] if len(sys.argv) > 3 else None
        
        results = search.search_by_category(category, subcategory)
        
        if 'error' in results:
            print(f"❌ {results['error']}")
            return
        
        if subcategory:
            print(f"🔍 {category}/{subcategory}")
            print("=" * 30)
            print(f"📄 Files ({len(results['matches'])}):")
            for file_path in results['matches']:
                print(f"  • {file_path}")
        else:
            print(f"📁 {category} Overview")
            print("=" * 30)
            print(f"📊 Total files: {results['total_files']}")
            
            if results['subcategories']:
                print("\n📂 Subcategories:")
                for subcat, count in results['subcategories'].items():
                    print(f"  • {subcat}: {count} files")
            
            print("\n📄 Files by type:")
            for ftype, files in results['files_by_type'].items():
                if files:
                    print(f"  • {ftype}: {len(files)} files")
    
    elif command == 'preview' and len(sys.argv) >= 3:
        category = sys.argv[2]
        preview = search.mixed_content_preview(category)
        
        if 'error' in preview:
            print(f"❌ {preview['error']}")
            return
        
        print(f"🔍 Mixed Content Preview: {category}")
        print("=" * 40)
        print(f"🎯 Diversity Score: {preview['diversity_score']}/10")
        
        print("\n📊 File Type Distribution:")
        for ftype, info in preview['file_types'].items():
            print(f"  • {ftype}: {info['count']} files ({info['percentage']}%)")
            if info['sample_files']:
                print(f"    └─ Sample: {', '.join(info['sample_files'])}")
        
        if preview['recommendations']:
            print("\n💡 Recommendations:")
            for rec in preview['recommendations']:
                print(f"  • {rec}")

if __name__ == "__main__":
    main()
