#!/usr/bin/env python3
"""Smart Reorganizer - Intelligent post-split category organization"""

import shutil
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

class SmartReorganizer:
    def __init__(self):
        self.workspace_path = Path("/media/sunil-kr/workspace/user-projects/shared-tools/nested-shares")
        
    def reorganize_split_results(self) -> Dict:
        """Intelligently reorganize split results into proper structure"""
        results = {
            'reorganized': [],
            'created_categories': [],
            'moved_files': 0
        }
        
        # Handle code-files category - split by language
        code_files_path = self.workspace_path / "code-files"
        if code_files_path.exists():
            results.update(self._reorganize_code_files(code_files_path))
        
        # Handle other category - split by type
        other_path = self.workspace_path / "other"
        if other_path.exists():
            results.update(self._reorganize_other_files(other_path))
        
        # Handle ai-content - merge back to ai with subcategories
        ai_content_path = self.workspace_path / "ai-content"
        if ai_content_path.exists():
            results.update(self._reorganize_ai_content(ai_content_path))
        
        return results
    
    def _reorganize_code_files(self, code_files_path: Path) -> Dict:
        """Reorganize code-files by programming language"""
        results = {'reorganized': [], 'moved_files': 0}
        
        # Create language-specific directories
        languages = {
            '.py': 'python-code',
            '.js': 'javascript-code', 
            '.sh': 'shell-scripts',
            '.md': 'documentation',
            '.json': 'config-files'
        }
        
        file_counts = defaultdict(int)
        
        # Count files by extension
        for file_path in code_files_path.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                file_counts[ext] += 1
        
        # Create categories for significant file types (>20 files)
        for ext, count in file_counts.items():
            if count > 20 and ext in languages:
                target_dir = self.workspace_path / languages[ext]
                target_dir.mkdir(exist_ok=True)
                
                # Move files
                moved = 0
                for file_path in code_files_path.rglob(f"*{ext}"):
                    if file_path.is_file():
                        rel_path = file_path.relative_to(code_files_path)
                        new_path = target_dir / rel_path
                        new_path.parent.mkdir(parents=True, exist_ok=True)
                        file_path.rename(new_path)
                        moved += 1
                
                results['reorganized'].append(f"Created {languages[ext]} with {moved} files")
                results['moved_files'] += moved
        
        # Remove empty code-files directory
        try:
            if not any(code_files_path.iterdir()):
                code_files_path.rmdir()
        except:
            pass
        
        return results
    
    def _reorganize_other_files(self, other_path: Path) -> Dict:
        """Reorganize other files into meaningful categories"""
        results = {'reorganized': [], 'moved_files': 0}
        
        # Create temp-files category for temporary/cache files
        temp_patterns = ['.venv', '__pycache__', '.cache', '.git', 'node_modules']
        temp_dir = self.workspace_path / "temp-files"
        temp_dir.mkdir(exist_ok=True)
        
        moved_temp = 0
        for pattern in temp_patterns:
            for item in other_path.rglob(f"*{pattern}*"):
                if item.exists():
                    rel_path = item.relative_to(other_path)
                    new_path = temp_dir / rel_path
                    new_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    if item.is_file():
                        item.rename(new_path)
                        moved_temp += 1
                    elif item.is_dir():
                        shutil.move(str(item), str(new_path))
                        moved_temp += len(list(new_path.rglob("*")))
        
        if moved_temp > 0:
            results['reorganized'].append(f"Created temp-files with {moved_temp} items")
            results['moved_files'] += moved_temp
        
        # Move remaining files to mixed-content
        remaining_files = list(other_path.rglob("*"))
        remaining_files = [f for f in remaining_files if f.is_file()]
        
        if remaining_files:
            mixed_dir = self.workspace_path / "mixed-content"
            mixed_dir.mkdir(exist_ok=True)
            
            moved_mixed = 0
            for file_path in remaining_files:
                rel_path = file_path.relative_to(other_path)
                new_path = mixed_dir / rel_path
                new_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.rename(new_path)
                moved_mixed += 1
            
            results['reorganized'].append(f"Created mixed-content with {moved_mixed} files")
            results['moved_files'] += moved_mixed
        
        # Remove empty other directory
        try:
            if not any(other_path.iterdir()):
                other_path.rmdir()
        except:
            pass
        
        return results
    
    def _reorganize_ai_content(self, ai_content_path: Path) -> Dict:
        """Merge ai-content back to ai with proper subcategorization"""
        results = {'reorganized': [], 'moved_files': 0}
        
        ai_dir = self.workspace_path / "ai"
        if not ai_dir.exists():
            ai_dir.mkdir()
        
        # Create ai-content subdirectory in ai
        ai_content_subdir = ai_dir / "content"
        ai_content_subdir.mkdir(exist_ok=True)
        
        moved = 0
        for item in ai_content_path.iterdir():
            new_path = ai_content_subdir / item.name
            if item.is_file():
                item.rename(new_path)
                moved += 1
            elif item.is_dir():
                shutil.move(str(item), str(new_path))
                moved += len(list(new_path.rglob("*")))
        
        results['reorganized'].append(f"Merged ai-content to ai/content with {moved} items")
        results['moved_files'] += moved
        
        # Remove empty ai-content directory
        try:
            ai_content_path.rmdir()
        except:
            pass
        
        return results
    
    def cleanup_empty_directories(self) -> int:
        """Remove empty directories after reorganization"""
        removed = 0
        
        for item in self.workspace_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                try:
                    # Check if directory is empty
                    if not any(item.iterdir()):
                        item.rmdir()
                        removed += 1
                except:
                    pass
        
        return removed

def main():
    import sys
    
    reorganizer = SmartReorganizer()
    
    if len(sys.argv) < 2:
        print("Usage: python3 smart_reorganizer.py <command>")
        print("Commands:")
        print("  reorganize  - Reorganize split results intelligently")
        print("  cleanup     - Remove empty directories")
        return
    
    command = sys.argv[1]
    
    if command == 'reorganize':
        results = reorganizer.reorganize_split_results()
        
        print("🔄 Smart Reorganization")
        print("=" * 25)
        
        if results['reorganized']:
            print("✅ Reorganization Results:")
            for result in results['reorganized']:
                print(f"  • {result}")
            print(f"\nTotal files moved: {results['moved_files']}")
        else:
            print("No reorganization needed")
        
        # Cleanup empty directories
        removed = reorganizer.cleanup_empty_directories()
        if removed > 0:
            print(f"\n🧹 Cleaned up {removed} empty directories")
    
    elif command == 'cleanup':
        removed = reorganizer.cleanup_empty_directories()
        print(f"🧹 Removed {removed} empty directories")

if __name__ == "__main__":
    main()
