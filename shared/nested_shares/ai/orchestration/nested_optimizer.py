#!/usr/bin/env python3
"""Nested-Shares Optimizer - AI-powered deep nesting analysis"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

class NestedOptimizer:
    def __init__(self):
        self.nested_path = Path("/media/sunil-kr/workspace/user-projects/shared-tools/nested-shares")
        
    def analyze_structure(self) -> Dict:
        """Analyze current nested structure efficiency"""
        structure = {
            "categories": {},
            "depth_analysis": {},
            "file_distribution": {},
            "optimization_score": 0.0
        }
        
        if not self.nested_path.exists():
            return structure
        
        # Analyze each category
        for category_dir in self.nested_path.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith('.'):
                cat_analysis = self._analyze_category(category_dir)
                structure["categories"][category_dir.name] = cat_analysis
        
        # Calculate overall metrics
        structure["depth_analysis"] = self._calculate_depth_metrics(structure["categories"])
        structure["file_distribution"] = self._analyze_distribution(structure["categories"])
        structure["optimization_score"] = self._calculate_optimization_score(structure)
        
        return structure
    
    def _analyze_category(self, category_path: Path) -> Dict:
        """Analyze single category structure"""
        analysis = {
            "total_files": 0,
            "max_depth": 0,
            "subcategories": {},
            "file_types": defaultdict(int),
            "balance_score": 0.0
        }
        
        for item in category_path.rglob("*"):
            if item.is_file() and not item.name.startswith('.'):
                analysis["total_files"] += 1
                
                # Calculate depth
                depth = len(item.relative_to(category_path).parts) - 1
                analysis["max_depth"] = max(analysis["max_depth"], depth)
                
                # Track file types
                analysis["file_types"][item.suffix] += 1
                
                # Track subcategories
                if depth > 0:
                    subcat = item.relative_to(category_path).parts[0]
                    if subcat not in analysis["subcategories"]:
                        analysis["subcategories"][subcat] = 0
                    analysis["subcategories"][subcat] += 1
        
        # Calculate balance score
        if analysis["subcategories"]:
            file_counts = list(analysis["subcategories"].values())
            avg_files = sum(file_counts) / len(file_counts)
            variance = sum((x - avg_files) ** 2 for x in file_counts) / len(file_counts)
            analysis["balance_score"] = 1.0 / (1.0 + variance / max(1, avg_files))
        
        return analysis
    
    def _calculate_depth_metrics(self, categories: Dict) -> Dict:
        """Calculate depth-related metrics"""
        depths = [cat["max_depth"] for cat in categories.values()]
        return {
            "avg_depth": sum(depths) / max(1, len(depths)),
            "max_depth": max(depths) if depths else 0,
            "depth_variance": sum((d - sum(depths)/len(depths))**2 for d in depths) / max(1, len(depths))
        }
    
    def _analyze_distribution(self, categories: Dict) -> Dict:
        """Analyze file distribution across categories"""
        total_files = sum(cat["total_files"] for cat in categories.values())
        
        return {
            "total_files": total_files,
            "categories_count": len(categories),
            "avg_files_per_category": total_files / max(1, len(categories)),
            "largest_category": max(categories.items(), key=lambda x: x[1]["total_files"])[0] if categories else None,
            "imbalance_ratio": self._calculate_imbalance(categories)
        }
    
    def _calculate_imbalance(self, categories: Dict) -> float:
        """Calculate distribution imbalance ratio"""
        if not categories:
            return 0.0
        
        file_counts = [cat["total_files"] for cat in categories.values()]
        max_files = max(file_counts)
        min_files = min(file_counts)
        
        return (max_files - min_files) / max(1, max_files)
    
    def _calculate_optimization_score(self, structure: Dict) -> float:
        """Calculate overall optimization score (0-1)"""
        scores = []
        
        # Depth efficiency (prefer 2-3 levels)
        avg_depth = structure["depth_analysis"].get("avg_depth", 0)
        depth_score = 1.0 - abs(avg_depth - 2.5) / 5.0
        scores.append(max(0, depth_score))
        
        # Balance score
        balance_scores = [cat.get("balance_score", 0) for cat in structure["categories"].values()]
        avg_balance = sum(balance_scores) / max(1, len(balance_scores))
        scores.append(avg_balance)
        
        # Distribution score (lower imbalance is better)
        imbalance = structure["file_distribution"].get("imbalance_ratio", 1.0)
        distribution_score = 1.0 - imbalance
        scores.append(distribution_score)
        
        return sum(scores) / len(scores)
    
    def generate_optimizations(self, structure: Dict) -> List[Dict]:
        """Generate optimization recommendations"""
        optimizations = []
        
        # Check depth issues
        if structure["depth_analysis"]["avg_depth"] > 4:
            optimizations.append({
                "type": "reduce_depth",
                "priority": "high",
                "description": "Reduce nesting depth - some categories are too deep",
                "action": "Flatten overly nested structures",
                "impact": "Improves navigation and reduces complexity"
            })
        
        # Check imbalance
        imbalance = structure["file_distribution"]["imbalance_ratio"]
        if imbalance > 0.7:
            optimizations.append({
                "type": "rebalance_categories",
                "priority": "medium",
                "description": f"Rebalance categories - {imbalance:.1%} imbalance detected",
                "action": "Move files from large categories to smaller ones",
                "impact": "Better organization and easier discovery"
            })
        
        # Check category efficiency
        for cat_name, cat_data in structure["categories"].items():
            if cat_data["balance_score"] < 0.5:
                optimizations.append({
                    "type": "reorganize_category",
                    "priority": "low",
                    "description": f"Reorganize {cat_name} category - poor subcategory balance",
                    "action": f"Redistribute files in {cat_name} subcategories",
                    "impact": "Improved category organization"
                })
        
        return sorted(optimizations, key=lambda x: {"high": 3, "medium": 2, "low": 1}[x["priority"]], reverse=True)
    
    def suggest_restructure(self, structure: Dict) -> Dict:
        """Suggest optimal restructure plan"""
        plan = {
            "current_score": structure["optimization_score"],
            "target_score": 0.85,
            "moves": [],
            "new_categories": [],
            "estimated_improvement": 0.0
        }
        
        # Find overcrowded categories
        avg_files = structure["file_distribution"]["avg_files_per_category"]
        
        for cat_name, cat_data in structure["categories"].items():
            if cat_data["total_files"] > avg_files * 1.5:
                # Suggest splitting
                plan["moves"].append({
                    "action": "split_category",
                    "category": cat_name,
                    "reason": f"Too many files ({cat_data['total_files']} vs avg {avg_files:.0f})",
                    "suggestion": f"Split {cat_name} into 2-3 subcategories"
                })
        
        # Estimate improvement
        plan["estimated_improvement"] = min(0.85, structure["optimization_score"] + 0.2)
        
        return plan

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Nested-shares optimizer")
    parser.add_argument("command", choices=["analyze", "optimize", "restructure"])
    
    args = parser.parse_args()
    optimizer = NestedOptimizer()
    
    if args.command == "analyze":
        structure = optimizer.analyze_structure()
        
        print("🔍 Nested Structure Analysis")
        print("=" * 30)
        print(f"Optimization Score: {structure['optimization_score']:.1%}")
        print(f"Categories: {len(structure['categories'])}")
        print(f"Total Files: {structure['file_distribution']['total_files']}")
        print(f"Average Depth: {structure['depth_analysis']['avg_depth']:.1f}")
        print(f"Imbalance Ratio: {structure['file_distribution']['imbalance_ratio']:.1%}")
        
        print(f"\n📊 Category Breakdown:")
        for name, data in structure["categories"].items():
            print(f"  {name}: {data['total_files']} files, depth {data['max_depth']}, balance {data['balance_score']:.1%}")
    
    elif args.command == "optimize":
        structure = optimizer.analyze_structure()
        optimizations = optimizer.generate_optimizations(structure)
        
        print("🎯 Optimization Recommendations")
        print("=" * 35)
        
        for i, opt in enumerate(optimizations, 1):
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}[opt["priority"]]
            print(f"\n{i}. {opt['type'].replace('_', ' ').title()} {priority_emoji}")
            print(f"   {opt['description']}")
            print(f"   Action: {opt['action']}")
            print(f"   Impact: {opt['impact']}")
    
    elif args.command == "restructure":
        structure = optimizer.analyze_structure()
        plan = optimizer.suggest_restructure(structure)
        
        print("🏗️  Restructure Plan")
        print("=" * 20)
        print(f"Current Score: {plan['current_score']:.1%}")
        print(f"Target Score: {plan['target_score']:.1%}")
        print(f"Expected Improvement: +{plan['estimated_improvement'] - plan['current_score']:.1%}")
        
        print(f"\n📋 Recommended Moves:")
        for move in plan["moves"]:
            print(f"  • {move['action'].replace('_', ' ').title()}: {move['category']}")
            print(f"    Reason: {move['reason']}")
            print(f"    Suggestion: {move['suggestion']}")

if __name__ == "__main__":
    main()
