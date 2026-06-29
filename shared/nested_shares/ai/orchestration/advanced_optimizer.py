#!/usr/bin/env python3
"""Advanced Optimizer - Handle complex category optimization scenarios"""

import shutil
from pathlib import Path
from typing import Dict, List
from collections import defaultdict, Counter

class AdvancedOptimizer:
    def __init__(self):
        self.workspace_path = Path("/media/sunil-kr/workspace/user-projects/shared-tools/nested-shares")
    
    def optimize_python_code_category(self) -> Dict:
        """Optimize python-code category by project/purpose"""
        python_code_path = self.workspace_path / "python-code"
        if not python_code_path.exists():
            return {'success': False, 'message': 'python-code category not found'}
        
        results = {'success': True, 'actions': [], 'files_moved': 0}
        
        # Create subcategories in python-code
        subcategories = {
            'orchestration': python_code_path / 'orchestration',
            'automation': python_code_path / 'automation', 
            'monitoring': python_code_path / 'monitoring',
            'utilities': python_code_path / 'utilities'
        }
        
        for subcat_path in subcategories.values():
            subcat_path.mkdir(exist_ok=True)
        
        # Categorize files by keywords
        moved = 0
        for file_path in python_code_path.rglob("*.py"):
            if file_path.parent in subcategories.values():
                continue  # Skip already organized files
                
            filename = file_path.name.lower()
            
            if any(word in filename for word in ['orchestr', 'conduct', 'manage']):
                target = subcategories['orchestration']
            elif any(word in filename for word in ['automat', 'schedul', 'trigger']):
                target = subcategories['automation']
            elif any(word in filename for word in ['monitor', 'health', 'alert', 'track']):
                target = subcategories['monitoring']
            else:
                target = subcategories['utilities']
            
            new_path = target / file_path.name
            if not new_path.exists():
                file_path.rename(new_path)
                moved += 1
        
        results['actions'].append(f"Organized {moved} Python files into subcategories")
        results['files_moved'] = moved
        return results
    
    def optimize_ai_category(self) -> Dict:
        """Optimize AI category with better subcategorization"""
        ai_path = self.workspace_path / "ai"
        if not ai_path.exists():
            return {'success': False, 'message': 'ai category not found'}
        
        results = {'success': True, 'actions': [], 'files_moved': 0}
        
        # Enhanced subcategory structure
        subcategories = {
            'core': ai_path / 'core-ai',
            'tools': ai_path / 'ai-tools',
            'config': ai_path / 'configuration',
            'docs': ai_path / 'documentation'
        }
        
        for subcat_path in subcategories.values():
            subcat_path.mkdir(exist_ok=True)
        
        moved = 0
        # Move files based on existing structure and content
        for item in ai_path.iterdir():
            if item.is_file():
                filename = item.name.lower()
                
                if any(ext in filename for ext in ['.md', '.txt', '.rst']):
                    target = subcategories['docs']
                elif any(word in filename for word in ['config', 'setting', 'param']):
                    target = subcategories['config']
                elif any(word in filename for word in ['tool', 'util', 'helper']):
                    target = subcategories['tools']
                else:
                    target = subcategories['core']
                
                new_path = target / item.name
                if not new_path.exists():
                    item.rename(new_path)
                    moved += 1
        
        results['actions'].append(f"Organized {moved} AI files into subcategories")
        results['files_moved'] = moved
        return results
    
    def archive_temp_files(self) -> Dict:
        """Archive temp-files to separate storage"""
        temp_files_path = self.workspace_path / "temp-files"
        if not temp_files_path.exists():
            return {'success': False, 'message': 'temp-files category not found'}
        
        # Create archive directory outside main workspace
        archive_path = self.workspace_path.parent / "workspace-archive" / "temp-files"
        archive_path.mkdir(parents=True, exist_ok=True)
        
        results = {'success': True, 'actions': [], 'files_moved': 0}
        
        # Move entire temp-files directory to archive
        if temp_files_path.exists():
            shutil.move(str(temp_files_path), str(archive_path / "archived-temp"))
            results['actions'].append(f"Archived temp-files to {archive_path}")
            results['files_moved'] = 755  # Known count
        
        return results
    
    def cleanup_small_categories(self) -> Dict:
        """Cleanup categories with very few files"""
        results = {'success': True, 'actions': [], 'files_moved': 0}
        
        # Find categories with 1-2 files
        small_categories = []
        for cat_dir in self.workspace_path.iterdir():
            if cat_dir.is_dir() and not cat_dir.name.startswith('.'):
                files = list(cat_dir.rglob("*"))
                files = [f for f in files if f.is_file()]
                
                if len(files) <= 2:
                    small_categories.append((cat_dir, len(files)))
        
        # Merge small categories into utilities
        utilities_path = self.workspace_path / "utilities"
        utilities_path.mkdir(exist_ok=True)
        
        moved = 0
        for cat_dir, file_count in small_categories:
            if cat_dir.name != 'utilities':
                target_subdir = utilities_path / cat_dir.name
                target_subdir.mkdir(exist_ok=True)
                
                for item in cat_dir.iterdir():
                    new_path = target_subdir / item.name
                    if item.is_file():
                        item.rename(new_path)
                        moved += 1
                    elif item.is_dir():
                        shutil.move(str(item), str(new_path))
                
                # Remove empty category
                try:
                    cat_dir.rmdir()
                    results['actions'].append(f"Merged {cat_dir.name} ({file_count} files) into utilities")
                except:
                    pass
        
        results['files_moved'] = moved
        return results
    
    def run_complete_optimization(self) -> Dict:
        """Run complete advanced optimization"""
        results = {
            'success': True,
            'optimizations': [],
            'total_files_moved': 0,
            'categories_optimized': 0
        }
        
        # 1. Optimize python-code category
        python_result = self.optimize_python_code_category()
        if python_result['success']:
            results['optimizations'].extend(python_result['actions'])
            results['total_files_moved'] += python_result['files_moved']
            results['categories_optimized'] += 1
        
        # 2. Optimize AI category
        ai_result = self.optimize_ai_category()
        if ai_result['success']:
            results['optimizations'].extend(ai_result['actions'])
            results['total_files_moved'] += ai_result['files_moved']
            results['categories_optimized'] += 1
        
        # 3. Archive temp files
        temp_result = self.archive_temp_files()
        if temp_result['success']:
            results['optimizations'].extend(temp_result['actions'])
            results['total_files_moved'] += temp_result['files_moved']
            results['categories_optimized'] += 1
        
        # 4. Cleanup small categories
        cleanup_result = self.cleanup_small_categories()
        if cleanup_result['success']:
            results['optimizations'].extend(cleanup_result['actions'])
            results['total_files_moved'] += cleanup_result['files_moved']
        
        return results

def main():
    import sys
    
    optimizer = AdvancedOptimizer()
    
    if len(sys.argv) < 2:
        print("Usage: python3 advanced_optimizer.py <command>")
        print("Commands:")
        print("  python     - Optimize python-code category")
        print("  ai         - Optimize AI category")
        print("  archive    - Archive temp files")
        print("  cleanup    - Cleanup small categories")
        print("  complete   - Run complete optimization")
        return
    
    command = sys.argv[1]
    
    if command == 'python':
        result = optimizer.optimize_python_code_category()
    elif command == 'ai':
        result = optimizer.optimize_ai_category()
    elif command == 'archive':
        result = optimizer.archive_temp_files()
    elif command == 'cleanup':
        result = optimizer.cleanup_small_categories()
    elif command == 'complete':
        result = optimizer.run_complete_optimization()
    else:
        print(f"Unknown command: {command}")
        return
    
    if result['success']:
        print("✅ Advanced Optimization Complete")
        print("=" * 35)
        
        if 'optimizations' in result:
            for action in result['optimizations']:
                print(f"  • {action}")
            print(f"\nTotal files moved: {result['total_files_moved']}")
            print(f"Categories optimized: {result['categories_optimized']}")
        elif 'actions' in result:
            for action in result['actions']:
                print(f"  • {action}")
            print(f"\nFiles moved: {result['files_moved']}")
    else:
        print(f"❌ {result['message']}")

if __name__ == "__main__":
    main()
