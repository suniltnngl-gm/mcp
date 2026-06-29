#!/usr/bin/env python3
"""Roadmap Dashboard - Visual progress tracking and metrics"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class RoadmapDashboard:
    def __init__(self):
        self.base_path = Path(__file__).parent
    
    def generate_dashboard(self) -> str:
        """Generate complete dashboard view"""
        from roadmap_engine import RoadmapEngine
        from nested_optimizer import NestedOptimizer
        from feedback_loop import FeedbackLoop
        
        # Collect data
        roadmap = RoadmapEngine()
        optimizer = NestedOptimizer()
        feedback = FeedbackLoop()
        
        patterns = roadmap.analyze_workspace_patterns()
        structure = optimizer.analyze_structure()
        health = feedback.get_system_health()
        
        # Generate dashboard
        dashboard = self._create_header()
        dashboard += self._create_metrics_section(patterns, structure, health)
        dashboard += self._create_progress_section()
        dashboard += self._create_priorities_section(patterns, structure)
        dashboard += self._create_recommendations_section(optimizer, patterns)
        
        return dashboard
    
    def _create_header(self) -> str:
        """Create dashboard header"""
        return f"""
🎛️  SELF-IMPROVING ROADMAP DASHBOARD
{'=' * 45}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
    
    def _create_metrics_section(self, patterns: Dict, structure: Dict, health: Dict) -> str:
        """Create metrics overview section"""
        section = "📊 SYSTEM METRICS\n"
        section += "-" * 20 + "\n"
        
        # Health overview
        health_emoji = {"excellent": "🟢", "good": "🟡", "needs_attention": "🟠", "critical": "🔴"}
        trend_emoji = {"improving": "📈", "stable": "➡️", "declining": "📉"}
        
        section += f"Overall Health: {health['health_score']:.1%} {health_emoji.get(health['status'], '⚪')}\n"
        section += f"Trend: {health['trend'].title()} {trend_emoji.get(health['trend'], '➡️')}\n\n"
        
        # Individual metrics
        metrics = [
            ("Nested Efficiency", structure["optimization_score"], 0.85),
            ("Merge Success", patterns.get("merge_history", {}).get("success_rate", 0.0), 0.95),
            ("Docs Conversion", patterns.get("documentation_gaps", {}).get("conversion_rate", 0.0), 0.90),
            ("TODO Completion", 1.0 - (patterns.get("todo_patterns", {}).get("active_todos", 8) / 8.0), 0.80)
        ]
        
        for name, current, target in metrics:
            status = "✅" if current >= target else "⚠️" if current >= target * 0.7 else "❌"
            progress_bar = self._create_progress_bar(current, target)
            section += f"{status} {name}: {progress_bar} {current:.1%}/{target:.1%}\n"
        
        return section + "\n"
    
    def _create_progress_bar(self, current: float, target: float, width: int = 20) -> str:
        """Create ASCII progress bar"""
        progress = min(1.0, current / target)
        filled = int(progress * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"
    
    def _create_progress_section(self) -> str:
        """Create TODO progress section"""
        section = "📋 TODO PROGRESS\n"
        section += "-" * 15 + "\n"
        
        # This would integrate with actual TODO system
        # For now, showing static progress from context
        completed = 5
        total = 8
        progress = completed / total
        
        section += f"Roadmap Tasks: {completed}/{total} ({progress:.1%})\n"
        section += f"Progress: {self._create_progress_bar(progress, 1.0)}\n"
        
        # Recent completions
        recent_tasks = [
            "✅ Roadmap engine with self-improvement",
            "✅ Progress tracking integration", 
            "✅ Nested-shares optimizer",
            "✅ Merge/split pattern analyzer",
            "✅ Docs-to-wiki converter"
        ]
        
        section += "\nRecent Completions:\n"
        for task in recent_tasks:
            section += f"  {task}\n"
        
        return section + "\n"
    
    def _create_priorities_section(self, patterns: Dict, structure: Dict) -> str:
        """Create current priorities section"""
        section = "🎯 CURRENT PRIORITIES\n"
        section += "-" * 20 + "\n"
        
        priorities = []
        
        # Check critical issues
        imbalance = structure["file_distribution"]["imbalance_ratio"]
        if imbalance > 0.9:
            priorities.append(("🔴 CRITICAL", f"Rebalance categories ({imbalance:.1%} imbalance)"))
        
        merge_rate = patterns.get("merge_history", {}).get("success_rate", 0.0)
        if merge_rate < 0.9:
            priorities.append(("🟡 HIGH", f"Improve merge success ({merge_rate:.1%} rate)"))
        
        doc_rate = patterns.get("documentation_gaps", {}).get("conversion_rate", 0.0)
        if doc_rate < 0.5:
            priorities.append(("🟡 MEDIUM", f"Convert docs to wiki ({doc_rate:.1%} done)"))
        
        # Show top 5 priorities
        for i, (level, desc) in enumerate(priorities[:5], 1):
            section += f"{i}. {level}: {desc}\n"
        
        return section + "\n"
    
    def _create_recommendations_section(self, optimizer, patterns: Dict) -> str:
        """Create recommendations section"""
        section = "💡 RECOMMENDATIONS\n"
        section += "-" * 18 + "\n"
        
        # Get optimization suggestions
        structure = optimizer.analyze_structure()
        optimizations = optimizer.generate_optimizations(structure)
        
        # Show top 3 recommendations
        for i, opt in enumerate(optimizations[:3], 1):
            impact_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}[opt["priority"]]
            section += f"{i}. {impact_emoji} {opt['description']}\n"
            section += f"   Action: {opt['action']}\n"
            section += f"   Impact: {opt['impact']}\n\n"
        
        return section
    
    def save_dashboard(self, content: str) -> Path:
        """Save dashboard to file"""
        dashboard_file = self.base_path / f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        
        with open(dashboard_file, 'w') as f:
            f.write(content)
        
        return dashboard_file
    
    def create_summary_report(self) -> Dict:
        """Create summary report for integration"""
        from roadmap_engine import RoadmapEngine
        from nested_optimizer import NestedOptimizer
        from feedback_loop import FeedbackLoop
        
        roadmap = RoadmapEngine()
        optimizer = NestedOptimizer()
        feedback = FeedbackLoop()
        
        patterns = roadmap.analyze_workspace_patterns()
        structure = optimizer.analyze_structure()
        health = feedback.get_system_health()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "health_score": health["health_score"],
            "status": health["status"],
            "metrics": {
                "nested_efficiency": structure["optimization_score"],
                "imbalance_ratio": structure["file_distribution"]["imbalance_ratio"],
                "total_files": structure["file_distribution"]["total_files"],
                "categories": len(structure["categories"])
            },
            "critical_issues": [
                issue for issue in [
                    "severe_imbalance" if structure["file_distribution"]["imbalance_ratio"] > 0.9 else None,
                    "low_efficiency" if structure["optimization_score"] < 0.5 else None,
                    "doc_backlog" if patterns.get("documentation_gaps", {}).get("conversion_rate", 0) < 0.5 else None
                ] if issue
            ],
            "next_actions": [
                "Rebalance AI category (1585 files)",
                "Complete remaining TODO tasks (3/8)",
                "Convert documentation to wiki format"
            ]
        }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Roadmap dashboard")
    parser.add_argument("command", choices=["show", "save", "summary"])
    
    args = parser.parse_args()
    dashboard = RoadmapDashboard()
    
    if args.command == "show":
        content = dashboard.generate_dashboard()
        print(content)
    
    elif args.command == "save":
        content = dashboard.generate_dashboard()
        file_path = dashboard.save_dashboard(content)
        print(f"📊 Dashboard saved to: {file_path}")
        print(content)
    
    elif args.command == "summary":
        summary = dashboard.create_summary_report()
        
        print("📋 Summary Report")
        print("=" * 16)
        print(f"Health: {summary['health_score']:.1%} ({summary['status']})")
        print(f"Files: {summary['metrics']['total_files']} across {summary['metrics']['categories']} categories")
        print(f"Efficiency: {summary['metrics']['nested_efficiency']:.1%}")
        print(f"Imbalance: {summary['metrics']['imbalance_ratio']:.1%}")
        
        if summary['critical_issues']:
            print(f"\n🚨 Critical Issues:")
            for issue in summary['critical_issues']:
                print(f"  • {issue.replace('_', ' ').title()}")
        
        print(f"\n🎯 Next Actions:")
        for action in summary['next_actions']:
            print(f"  • {action}")

if __name__ == "__main__":
    main()
