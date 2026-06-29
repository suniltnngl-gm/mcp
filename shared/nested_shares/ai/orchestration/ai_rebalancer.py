#!/usr/bin/env python3
"""AI Category Rebalancer - Fix critical imbalance (1585 files → balanced structure)"""

import shutil
from pathlib import Path
from collections import defaultdict
from typing import Dict, List

class AIRebalancer:
    def __init__(self):
        self.ai_path = Path("/media/sunil-kr/workspace/user-projects/shared-tools/nested-shares/ai")
        self.backup_path = Path(__file__).parent / "rebalance_backup"
        
    def analyze_ai_structure(self) -> Dict:
        """Analyze current AI category structure"""
        structure = {
            "total_files": 0,
            "subdirs": {},
            "file_types": defaultdict(int),
            "suggested_categories": []
        }
        
        if not self.ai_path.exists():
            return structure
        
        # Analyze current structure
        for item in self.ai_path.rglob("*"):
            if item.is_file() and not item.name.startswith('.'):
                structure["total_files"] += 1
                structure["file_types"][item.suffix] += 1
                
                # Track subdirectories
                rel_path = item.relative_to(self.ai_path)
                if len(rel_path.parts) > 1:
                    subdir = rel_path.parts[0]
                    if subdir not in structure["subdirs"]:
                        structure["subdirs"][subdir] = 0
                    structure["subdirs"][subdir] += 1
        
        # Suggest new categories based on existing structure
        structure["suggested_categories"] = self._suggest_categories(structure["subdirs"])
        
        return structure
    
    def _suggest_categories(self, subdirs: Dict) -> List[Dict]:
        """Suggest new category structure"""
        suggestions = []
        
        # Find large subdirectories that should become top-level categories
        for subdir, count in subdirs.items():
            if count > 50:  # Threshold for new category
                suggestions.append({
                    "name": subdir,
                    "files": count,
                    "action": "promote_to_category",
                    "priority": "high" if count > 200 else "medium"
                })
        
        # Suggest grouping small subdirs
        small_dirs = {k: v for k, v in subdirs.items() if v <= 50}
        if len(small_dirs) > 5:
            suggestions.append({
                "name": "ai_utilities",
                "files": sum(small_dirs.values()),
                "action": "group_small_dirs",
                "priority": "medium",
                "includes": list(small_dirs.keys())
            })
        
        return suggestions
    
    def create_rebalance_plan(self) -> Dict:
        """Create detailed rebalancing plan"""
        structure = self.analyze_ai_structure()
        
        plan = {
            "current_files": structure["total_files"],
            "target_categories": [],
            "moves": [],
            "estimated_reduction": 0
        }
        
        # Process suggestions
        for suggestion in structure["suggested_categories"]:
            if suggestion["action"] == "promote_to_category":
                plan["target_categories"].append({
                    "name": suggestion["name"],
                    "source": f"ai/{suggestion['name']}",
                    "files": suggestion["files"]
                })
                plan["moves"].append({
                    "action": "move_directory",
                    "source": f"ai/{suggestion['name']}",
                    "target": suggestion["name"],
                    "files": suggestion["files"]
                })
                plan["estimated_reduction"] += suggestion["files"]
        
        # Calculate remaining files in AI category
        plan["remaining_ai_files"] = structure["total_files"] - plan["estimated_reduction"]
        
        return plan
    
    def execute_rebalance(self, plan: Dict, dry_run: bool = True) -> Dict:
        """Execute rebalancing plan"""
        results = {
            "moves_completed": 0,
            "files_moved": 0,
            "errors": [],
            "dry_run": dry_run
        }
        
        if not dry_run:
            # Create backup
            self._create_backup()
        
        # Execute moves
        for move in plan["moves"]:
            try:
                source_path = self.ai_path.parent / move["source"]
                target_path = self.ai_path.parent / move["target"]
                
                if dry_run:
                    print(f"DRY RUN: Would move {source_path} → {target_path}")
                    results["moves_completed"] += 1
                    results["files_moved"] += move["files"]
                else:
                    if source_path.exists():
                        shutil.move(str(source_path), str(target_path))
                        results["moves_completed"] += 1
                        results["files_moved"] += move["files"]
                        print(f"✅ Moved {move['files']} files: {move['source']} → {move['target']}")
                    else:
                        results["errors"].append(f"Source not found: {source_path}")
                        
            except Exception as e:
                results["errors"].append(f"Move failed {move['source']}: {e}")
        
        return results
    
    def _create_backup(self):
        """Create backup before rebalancing"""
        if self.backup_path.exists():
            shutil.rmtree(self.backup_path)
        
        self.backup_path.mkdir(parents=True)
        shutil.copytree(self.ai_path, self.backup_path / "ai_backup")
        print(f"📁 Backup created: {self.backup_path}")
    
    def verify_rebalance(self) -> Dict:
        """Verify rebalancing results"""
        from nested_optimizer import NestedOptimizer
        
        optimizer = NestedOptimizer()
        new_structure = optimizer.analyze_structure()
        
        verification = {
            "new_optimization_score": new_structure["optimization_score"],
            "new_imbalance_ratio": new_structure["file_distribution"]["imbalance_ratio"],
            "categories_count": len(new_structure["categories"]),
            "ai_files_remaining": new_structure["categories"].get("ai", {}).get("total_files", 0),
            "improvement": "significant" if new_structure["optimization_score"] > 0.5 else "moderate"
        }
        
        return verification

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="AI category rebalancer")
    parser.add_argument("command", choices=["analyze", "plan", "execute", "verify"])
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    
    args = parser.parse_args()
    rebalancer = AIRebalancer()
    
    if args.command == "analyze":
        structure = rebalancer.analyze_ai_structure()
        
        print("🔍 AI Category Analysis")
        print("=" * 25)
        print(f"Total Files: {structure['total_files']}")
        print(f"Subdirectories: {len(structure['subdirs'])}")
        
        print(f"\n📊 Largest Subdirectories:")
        sorted_dirs = sorted(structure["subdirs"].items(), key=lambda x: x[1], reverse=True)
        for name, count in sorted_dirs[:10]:
            print(f"  {name}: {count} files")
        
        print(f"\n💡 Suggested Categories ({len(structure['suggested_categories'])}):")
        for suggestion in structure["suggested_categories"]:
            print(f"  • {suggestion['name']}: {suggestion['files']} files ({suggestion['priority']} priority)")
    
    elif args.command == "plan":
        plan = rebalancer.create_rebalance_plan()
        
        print("📋 Rebalancing Plan")
        print("=" * 18)
        print(f"Current AI Files: {plan['current_files']}")
        print(f"Files to Move: {plan['estimated_reduction']}")
        print(f"Remaining in AI: {plan['remaining_ai_files']}")
        print(f"New Categories: {len(plan['target_categories'])}")
        
        print(f"\n🎯 Planned Moves:")
        for move in plan["moves"]:
            print(f"  • {move['source']} → {move['target']} ({move['files']} files)")
    
    elif args.command == "execute":
        plan = rebalancer.create_rebalance_plan()
        results = rebalancer.execute_rebalance(plan, dry_run=args.dry_run)
        
        mode = "DRY RUN" if args.dry_run else "EXECUTION"
        print(f"🔄 Rebalancing {mode} Complete")
        print("=" * 30)
        print(f"Moves Completed: {results['moves_completed']}")
        print(f"Files Moved: {results['files_moved']}")
        
        if results["errors"]:
            print(f"\n❌ Errors ({len(results['errors'])}):")
            for error in results["errors"]:
                print(f"  • {error}")
        
        if not args.dry_run:
            print(f"\n✅ Rebalancing complete! Run 'verify' to check results.")
    
    elif args.command == "verify":
        verification = rebalancer.verify_rebalance()
        
        print("✅ Rebalancing Verification")
        print("=" * 25)
        print(f"New Optimization Score: {verification['new_optimization_score']:.1%}")
        print(f"New Imbalance Ratio: {verification['new_imbalance_ratio']:.1%}")
        print(f"Total Categories: {verification['categories_count']}")
        print(f"AI Files Remaining: {verification['ai_files_remaining']}")
        print(f"Improvement Level: {verification['improvement'].title()}")

if __name__ == "__main__":
    main()
