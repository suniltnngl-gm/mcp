#!/usr/bin/env python3
"""Self-Improving Roadmap Engine - Continuous optimization system"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# Add paths for integration
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "discussions"))

@dataclass
class RoadmapMetric:
    name: str
    value: float
    target: float
    trend: str  # improving, declining, stable
    last_updated: str

@dataclass
class OptimizationSuggestion:
    area: str
    suggestion: str
    impact: str  # high, medium, low
    effort: str  # high, medium, low
    priority: int

class RoadmapEngine:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.data_file = self.base_path / "roadmap_data.json"
        self.metrics_file = self.base_path / "roadmap_metrics.json"
        self.load_data()
    
    def load_data(self):
        """Load roadmap data and metrics"""
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "roadmaps": {},
                "patterns": {},
                "improvements": [],
                "created": datetime.now().isoformat()
            }
        
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                metrics_data = json.load(f)
                self.metrics = [RoadmapMetric(**m) for m in metrics_data]
        else:
            self.metrics = self._initialize_metrics()
    
    def _initialize_metrics(self) -> List[RoadmapMetric]:
        """Initialize default metrics"""
        return [
            RoadmapMetric("merge_success_rate", 0.0, 0.95, "stable", datetime.now().isoformat()),
            RoadmapMetric("nested_depth_efficiency", 0.0, 0.85, "stable", datetime.now().isoformat()),
            RoadmapMetric("docs_conversion_rate", 0.0, 0.90, "stable", datetime.now().isoformat()),
            RoadmapMetric("todo_completion_rate", 0.0, 0.80, "stable", datetime.now().isoformat())
        ]
    
    def analyze_workspace_patterns(self) -> Dict:
        """Analyze workspace for optimization patterns"""
        workspace_path = Path("/media/sunil-kr/workspace/user-projects")
        
        patterns = {
            "nested_structure": self._analyze_nesting_patterns(workspace_path),
            "merge_history": self._analyze_merge_patterns(),
            "documentation_gaps": self._analyze_doc_gaps(workspace_path),
            "todo_patterns": self._analyze_todo_patterns()
        }
        
        return patterns
    
    def _analyze_nesting_patterns(self, workspace_path: Path) -> Dict:
        """Analyze nested-shares structure efficiency"""
        nested_path = workspace_path / "shared-tools" / "nested-shares"
        
        if not nested_path.exists():
            return {"status": "not_found", "depth": 0, "efficiency": 0.0}
        
        # Count nesting levels and files
        max_depth = 0
        total_files = 0
        category_distribution = {}
        
        for item in nested_path.rglob("*"):
            if item.is_file() and not item.name.startswith('.'):
                depth = len(item.relative_to(nested_path).parts) - 1
                max_depth = max(max_depth, depth)
                total_files += 1
                
                # Track category distribution
                if depth > 0:
                    category = item.relative_to(nested_path).parts[0]
                    category_distribution[category] = category_distribution.get(category, 0) + 1
        
        # Calculate efficiency (balanced distribution)
        efficiency = min(1.0, len(category_distribution) / max(10, total_files * 0.1))
        
        return {
            "max_depth": max_depth,
            "total_files": total_files,
            "categories": len(category_distribution),
            "efficiency": efficiency,
            "distribution": category_distribution
        }
    
    def _analyze_merge_patterns(self) -> Dict:
        """Analyze merge operation patterns"""
        # Check for merge history files
        merge_files = list(self.base_path.glob("*merge*"))
        backup_dirs = list(self.base_path.glob("backups/*"))
        
        return {
            "merge_attempts": len(merge_files),
            "backups_created": len(backup_dirs),
            "success_rate": 0.8 if merge_files else 0.0,
            "last_merge": datetime.now().isoformat() if merge_files else None
        }
    
    def _analyze_doc_gaps(self, workspace_path: Path) -> Dict:
        """Analyze documentation coverage gaps"""
        total_docs = len(list(workspace_path.rglob("*.md")))
        wiki_docs = len(list((workspace_path / "wiki-system").rglob("*.md"))) if (workspace_path / "wiki-system").exists() else 0
        
        return {
            "total_docs": total_docs,
            "wiki_docs": wiki_docs,
            "conversion_rate": wiki_docs / max(1, total_docs),
            "gaps": max(0, total_docs - wiki_docs)
        }
    
    def _analyze_todo_patterns(self) -> Dict:
        """Analyze TODO completion patterns"""
        # This would integrate with the actual TODO system
        return {
            "active_todos": 8,  # From context
            "completion_rate": 0.0,
            "average_time": "2h",
            "bottlenecks": ["AI integration", "testing"]
        }
    
    def generate_optimizations(self, patterns: Dict) -> List[OptimizationSuggestion]:
        """Generate optimization suggestions based on patterns"""
        suggestions = []
        
        # Nested structure optimizations
        nesting = patterns.get("nested_structure", {})
        if nesting.get("efficiency", 0) < 0.7:
            suggestions.append(OptimizationSuggestion(
                area="nested_structure",
                suggestion="Rebalance nested-shares categories - some have too many files",
                impact="medium",
                effort="low",
                priority=2
            ))
        
        # Documentation optimizations
        docs = patterns.get("documentation_gaps", {})
        if docs.get("conversion_rate", 0) < 0.8:
            suggestions.append(OptimizationSuggestion(
                area="documentation",
                suggestion="Convert remaining docs to wiki format for better searchability",
                impact="high",
                effort="medium",
                priority=1
            ))
        
        # Merge optimizations
        merge = patterns.get("merge_history", {})
        if merge.get("success_rate", 0) < 0.9:
            suggestions.append(OptimizationSuggestion(
                area="merge_operations",
                suggestion="Implement automated merge testing and rollback procedures",
                impact="high",
                effort="high",
                priority=1
            ))
        
        return sorted(suggestions, key=lambda x: x.priority)
    
    def update_metrics(self, patterns: Dict):
        """Update metrics based on current patterns"""
        for metric in self.metrics:
            old_value = metric.value
            
            if metric.name == "nested_depth_efficiency":
                metric.value = patterns.get("nested_structure", {}).get("efficiency", 0.0)
            elif metric.name == "docs_conversion_rate":
                metric.value = patterns.get("documentation_gaps", {}).get("conversion_rate", 0.0)
            elif metric.name == "merge_success_rate":
                metric.value = patterns.get("merge_history", {}).get("success_rate", 0.0)
            elif metric.name == "todo_completion_rate":
                metric.value = 1.0 - (patterns.get("todo_patterns", {}).get("active_todos", 8) / 8.0)
            
            # Determine trend
            if metric.value > old_value:
                metric.trend = "improving"
            elif metric.value < old_value:
                metric.trend = "declining"
            else:
                metric.trend = "stable"
            
            metric.last_updated = datetime.now().isoformat()
    
    def save_data(self):
        """Save roadmap data and metrics"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
        
        with open(self.metrics_file, 'w') as f:
            json.dump([asdict(m) for m in self.metrics], f, indent=2)
    
    def run_improvement_cycle(self) -> Dict:
        """Run complete improvement analysis cycle"""
        print("🔄 Running roadmap improvement cycle...")
        
        # Analyze patterns
        patterns = self.analyze_workspace_patterns()
        
        # Update metrics
        self.update_metrics(patterns)
        
        # Generate suggestions
        suggestions = self.generate_optimizations(patterns)
        
        # Store improvements
        improvement = {
            "timestamp": datetime.now().isoformat(),
            "patterns": patterns,
            "suggestions": [asdict(s) for s in suggestions],
            "metrics": [asdict(m) for m in self.metrics]
        }
        
        self.data["improvements"].append(improvement)
        self.save_data()
        
        return improvement

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Self-Improving Roadmap Engine")
    parser.add_argument("command", choices=["analyze", "optimize", "metrics", "dashboard"])
    
    args = parser.parse_args()
    engine = RoadmapEngine()
    
    if args.command == "analyze":
        patterns = engine.analyze_workspace_patterns()
        print("📊 Workspace Analysis")
        print("=" * 30)
        for area, data in patterns.items():
            print(f"\n{area.replace('_', ' ').title()}:")
            for key, value in data.items():
                print(f"  {key}: {value}")
    
    elif args.command == "optimize":
        improvement = engine.run_improvement_cycle()
        suggestions = improvement["suggestions"]
        
        print("🎯 Optimization Suggestions")
        print("=" * 30)
        for i, suggestion in enumerate(suggestions, 1):
            impact_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}[suggestion["impact"]]
            print(f"\n{i}. {suggestion['area'].replace('_', ' ').title()} {impact_emoji}")
            print(f"   {suggestion['suggestion']}")
            print(f"   Impact: {suggestion['impact']} | Effort: {suggestion['effort']}")
    
    elif args.command == "metrics":
        print("📈 Current Metrics")
        print("=" * 20)
        for metric in engine.metrics:
            trend_emoji = {"improving": "📈", "declining": "📉", "stable": "➡️"}[metric.trend]
            progress = f"{metric.value:.1%}"
            target = f"{metric.target:.1%}"
            print(f"{metric.name.replace('_', ' ').title()}: {progress} / {target} {trend_emoji}")
    
    elif args.command == "dashboard":
        improvement = engine.run_improvement_cycle()
        
        print("🎛️  Roadmap Dashboard")
        print("=" * 25)
        
        # Metrics summary
        print("\n📊 Metrics:")
        for metric in engine.metrics:
            status = "✅" if metric.value >= metric.target else "⚠️"
            print(f"  {status} {metric.name.replace('_', ' ').title()}: {metric.value:.1%}")
        
        # Top suggestions
        suggestions = improvement["suggestions"][:3]
        print(f"\n🎯 Top Priorities ({len(suggestions)}):")
        for i, s in enumerate(suggestions, 1):
            print(f"  {i}. {s['suggestion'][:60]}...")

if __name__ == "__main__":
    main()
