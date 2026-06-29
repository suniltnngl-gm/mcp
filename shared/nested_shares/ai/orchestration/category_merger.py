#!/usr/bin/env python3
"""Category Merger - Consolidate placeholder and small categories"""

import shutil
from pathlib import Path
from typing import Dict, List

class CategoryMerger:
    def __init__(self):
        self.workspace_path = Path("/media/sunil-kr/workspace/user-projects/shared-tools/nested-shares")
        self.placeholder_categories = ["git", "db", "config", "web", "data", "system"]
    
    def analyze_merge_opportunities(self) -> Dict:
        """Analyze categories for merge opportunities"""
        opportunities = {
            "placeholder_consolidation": [],
            "small_category_merges": [],
            "semantic_merges": []
        }
        
        # Analyze placeholder categories
        for cat_name in self.placeholder_categories:
            cat_path = self.workspace_path / cat_name
            if cat_path.exists():
                files = list(cat_path.rglob("*"))
                files = [f for f in files if f.is_file()]
                
                opportunities["placeholder_consolidation"].append({
                    "category": cat_name,
                    "files": len(files),
                    "target": "utilities",
                    "subcategory": cat_name
                })
        
        # Find small categories (< 5 files)
        for cat_dir in self.workspace_path.iterdir():
            if cat_dir.is_dir() and cat_dir.name not in self.placeholder_categories:
                files = list(cat_dir.rglob("*"))
                files = [f for f in files if f.is_file()]
                
                if len(files) < 5 and len(files) > 0:
                    opportunities["small_category_merges"].append({
                        "category": cat_dir.name,
                        "files": len(files),
                        "suggested_target": self._suggest_merge_target(cat_dir.name)
                    })
        
        return opportunities
    
    def _suggest_merge_target(self, category_name: str) -> str:
        """Suggest merge target based on semantic similarity"""
        semantic_map = {
            "testing": "core",
            "ignore": "utilities", 
            "tasks": "workflow",
            "core": "utilities"
        }
        
        return semantic_map.get(category_name, "utilities")
    
    def execute_placeholder_consolidation(self, dry_run: bool = True) -> Dict:
        """Consolidate placeholder categories into utilities"""
        results = {
            "created_utilities": False,
            "moved_categories": [],
            "errors": [],
            "dry_run": dry_run
        }
        
        utilities_path = self.workspace_path / "utilities"
        
        # Create utilities directory
        if not dry_run:
            utilities_path.mkdir(exist_ok=True)
            results["created_utilities"] = True
        elif dry_run:
            print(f"DRY RUN: Would create utilities directory")
        
        # Move each placeholder category
        for cat_name in self.placeholder_categories:
            cat_path = self.workspace_path / cat_name
            
            if cat_path.exists():
                target_subdir = utilities_path / cat_name
                
                try:
                    if dry_run:
                        files = list(cat_path.rglob("*"))
                        file_count = len([f for f in files if f.is_file()])
                        print(f"DRY RUN: Would move {cat_name} ({file_count} files) → utilities/{cat_name}")
                        results["moved_categories"].append(cat_name)
                    else:
                        shutil.move(str(cat_path), str(target_subdir))
                        results["moved_categories"].append(cat_name)
                        print(f"✅ Moved {cat_name} → utilities/{cat_name}")
                        
                except Exception as e:
                    results["errors"].append(f"Failed to move {cat_name}: {e}")
        
        return results
    
    def execute_small_category_merges(self, dry_run: bool = True) -> Dict:
        """Merge small categories into appropriate targets"""
        opportunities = self.analyze_merge_opportunities()
        
        results = {
            "merges_executed": [],
            "errors": [],
            "dry_run": dry_run
        }
        
        for merge_op in opportunities["small_category_merges"]:
            source_cat = merge_op["category"]
            target_cat = merge_op["suggested_target"]
            
            source_path = self.workspace_path / source_cat
            target_path = self.workspace_path / target_cat
            
            if not source_path.exists():
                continue
            
            try:
                if dry_run:
                    print(f"DRY RUN: Would merge {source_cat} ({merge_op['files']} files) → {target_cat}")
                    results["merges_executed"].append(f"{source_cat} → {target_cat}")
                else:
                    # Create target if it doesn't exist
                    target_path.mkdir(exist_ok=True)
                    
                    # Move files to target with subdirectory
                    target_subdir = target_path / source_cat
                    shutil.move(str(source_path), str(target_subdir))
                    
                    results["merges_executed"].append(f"{source_cat} → {target_cat}")
                    print(f"✅ Merged {source_cat} → {target_cat}/{source_cat}")
                    
            except Exception as e:
                results["errors"].append(f"Failed to merge {source_cat}: {e}")
        
        return results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Category merger")
    parser.add_argument("command", choices=["analyze", "consolidate", "merge"])
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    
    args = parser.parse_args()
    merger = CategoryMerger()
    
    if args.command == "analyze":
        opportunities = merger.analyze_merge_opportunities()
        
        print("🔗 Merge Opportunities Analysis")
        print("=" * 30)
        
        print(f"\n📦 Placeholder Consolidation ({len(opportunities['placeholder_consolidation'])}):")
        for item in opportunities["placeholder_consolidation"]:
            print(f"  • {item['category']}: {item['files']} files → utilities/{item['subcategory']}")
        
        print(f"\n🔄 Small Category Merges ({len(opportunities['small_category_merges'])}):")
        for item in opportunities["small_category_merges"]:
            print(f"  • {item['category']}: {item['files']} files → {item['suggested_target']}")
    
    elif args.command == "consolidate":
        results = merger.execute_placeholder_consolidation(dry_run=args.dry_run)
        
        mode = "DRY RUN" if args.dry_run else "EXECUTION"
        print(f"📦 Placeholder Consolidation {mode}")
        print("=" * 35)
        
        if results["created_utilities"]:
            print("✅ Created utilities directory")
        
        print(f"Categories moved: {len(results['moved_categories'])}")
        for cat in results["moved_categories"]:
            print(f"  ✅ {cat}")
        
        if results["errors"]:
            print(f"\nErrors: {len(results['errors'])}")
            for error in results["errors"]:
                print(f"  ❌ {error}")
    
    elif args.command == "merge":
        results = merger.execute_small_category_merges(dry_run=args.dry_run)
        
        mode = "DRY RUN" if args.dry_run else "EXECUTION"
        print(f"🔄 Small Category Merges {mode}")
        print("=" * 30)
        
        print(f"Merges executed: {len(results['merges_executed'])}")
        for merge in results["merges_executed"]:
            print(f"  ✅ {merge}")
        
        if results["errors"]:
            print(f"\nErrors: {len(results['errors'])}")
            for error in results["errors"]:
                print(f"  ❌ {error}")

if __name__ == "__main__":
    main()
