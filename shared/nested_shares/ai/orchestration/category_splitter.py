#!/usr/bin/env python3
"""Category Splitter - Smart split operations for mixed categories"""

import shutil
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

class CategorySplitter:
    def __init__(self):
        self.workspace_path = Path("/media/sunil-kr/workspace/user-projects/shared-tools/nested-shares")
        self.discussions_path = self.workspace_path / "discussions"
    
    def analyze_discussions_split(self) -> Dict:
        """Analyze discussions category for optimal split strategy"""
        if not self.discussions_path.exists():
            return {"error": "Discussions directory not found"}
        
        files = list(self.discussions_path.rglob("*"))
        files = [f for f in files if f.is_file() and not f.name.startswith('.')]
        
        categorization = {
            "ai_content": [],
            "code_files": [],
            "docs_files": [],
            "config_files": [],
            "other": []
        }
        
        for file_path in files:
            category = self._categorize_file(file_path)
            categorization[category].append(file_path)
        
        return {
            "total_files": len(files),
            "categorization": {k: len(v) for k, v in categorization.items()},
            "file_lists": categorization,
            "split_plan": self._generate_split_plan(categorization)
        }
    
    def _categorize_file(self, file_path: Path) -> str:
        """Categorize file based on content and location"""
        name = file_path.name.lower()
        suffix = file_path.suffix.lower()
        path_str = str(file_path).lower()
        
        # AI content detection
        ai_indicators = ['ai', 'ml', 'model', 'neural', 'llm', 'gpt', 'claude', 'gemini']
        if any(indicator in path_str for indicator in ai_indicators):
            return "ai_content"
        
        # Code files
        code_extensions = ['.py', '.js', '.sh', '.ts', '.go', '.rs', '.java', '.cpp']
        if suffix in code_extensions:
            return "code_files"
        
        # Config files
        config_extensions = ['.json', '.yaml', '.yml', '.toml', '.ini', '.conf', '.env']
        if suffix in config_extensions or 'config' in name:
            return "config_files"
        
        # Documentation
        doc_extensions = ['.md', '.txt', '.rst', '.adoc']
        if suffix in doc_extensions or 'readme' in name or 'doc' in name:
            return "docs_files"
        
        return "other"
    
    def _generate_split_plan(self, categorization: Dict[str, List]) -> List[Dict]:
        """Generate optimal split plan"""
        plan = []
        
        # Only split categories with significant file counts
        for category, files in categorization.items():
            if len(files) > 50:  # Threshold for new category
                plan.append({
                    "source_category": "discussions",
                    "target_category": category.replace("_", "-"),
                    "file_count": len(files),
                    "action": "create_new_category"
                })
            elif len(files) > 10:
                plan.append({
                    "source_category": "discussions", 
                    "target_category": f"discussions-{category.replace('_', '-')}",
                    "file_count": len(files),
                    "action": "create_subcategory"
                })
        
        return plan
    
    def execute_split(self, dry_run: bool = True) -> Dict:
        """Execute the discussions category split"""
        analysis = self.analyze_discussions_split()
        
        if "error" in analysis:
            return analysis
        
        results = {
            "operations": [],
            "errors": [],
            "dry_run": dry_run
        }
        
        for plan_item in analysis["split_plan"]:
            try:
                target_path = self.workspace_path / plan_item["target_category"]
                
                if dry_run:
                    print(f"DRY RUN: Would create {target_path} with {plan_item['file_count']} files")
                    results["operations"].append(f"Create {plan_item['target_category']}")
                else:
                    target_path.mkdir(exist_ok=True)
                    
                    # Move files
                    category_key = plan_item["target_category"].replace("-", "_")
                    if "discussions" in category_key:
                        category_key = category_key.replace("discussions_", "")
                    
                    files_to_move = analysis["file_lists"].get(category_key, [])
                    
                    for file_path in files_to_move:
                        rel_path = file_path.relative_to(self.discussions_path)
                        new_path = target_path / rel_path
                        new_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(file_path), str(new_path))
                    
                    results["operations"].append(f"Created {plan_item['target_category']} with {len(files_to_move)} files")
                    
            except Exception as e:
                results["errors"].append(f"Failed to create {plan_item['target_category']}: {e}")
        
        return results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Category splitter")
    parser.add_argument("command", choices=["analyze", "split"])
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    
    args = parser.parse_args()
    splitter = CategorySplitter()
    
    if args.command == "analyze":
        analysis = splitter.analyze_discussions_split()
        
        if "error" in analysis:
            print(f"❌ {analysis['error']}")
            return
        
        print("📊 Discussions Category Analysis")
        print("=" * 30)
        print(f"Total Files: {analysis['total_files']}")
        
        print(f"\n📋 File Distribution:")
        for category, count in analysis["categorization"].items():
            percentage = (count / analysis['total_files']) * 100
            print(f"  {category.replace('_', ' ').title()}: {count} files ({percentage:.1f}%)")
        
        print(f"\n✂️  Split Plan ({len(analysis['split_plan'])} operations):")
        for plan in analysis["split_plan"]:
            print(f"  • {plan['source_category']} → {plan['target_category']}")
            print(f"    Files: {plan['file_count']} | Action: {plan['action']}")
    
    elif args.command == "split":
        results = splitter.execute_split(dry_run=args.dry_run)
        
        mode = "DRY RUN" if args.dry_run else "EXECUTION"
        print(f"✂️  Category Split {mode}")
        print("=" * 25)
        
        print(f"Operations: {len(results['operations'])}")
        for op in results["operations"]:
            print(f"  ✅ {op}")
        
        if results["errors"]:
            print(f"\nErrors: {len(results['errors'])}")
            for error in results["errors"]:
                print(f"  ❌ {error}")

if __name__ == "__main__":
    main()
