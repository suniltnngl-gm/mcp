#!/usr/bin/env python3
"""Self-Improvement Feedback Loop - System analyzes its own performance"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
from dataclasses import dataclass, asdict

@dataclass
class PerformanceMetric:
    name: str
    current_value: float
    target_value: float
    trend: str
    improvement_rate: float
    last_action: str

class FeedbackLoop:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.feedback_file = self.base_path / "feedback_history.json"
        self.load_history()
    
    def load_history(self):
        """Load feedback history"""
        if self.feedback_file.exists():
            with open(self.feedback_file, 'r') as f:
                self.history = json.load(f)
        else:
            self.history = {"cycles": [], "improvements": [], "created": datetime.now().isoformat()}
    
    def analyze_system_performance(self) -> Dict:
        """Analyze current system performance"""
        from roadmap_engine import RoadmapEngine
        from nested_optimizer import NestedOptimizer
        
        # Get current metrics
        roadmap = RoadmapEngine()
        optimizer = NestedOptimizer()
        
        patterns = roadmap.analyze_workspace_patterns()
        structure = optimizer.analyze_structure()
        
        performance = {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "nested_efficiency": structure["optimization_score"],
                "merge_success_rate": patterns.get("merge_history", {}).get("success_rate", 0.0),
                "docs_conversion": patterns.get("documentation_gaps", {}).get("conversion_rate", 0.0),
                "todo_completion": 1.0 - (patterns.get("todo_patterns", {}).get("active_todos", 8) / 8.0)
            },
            "bottlenecks": self._identify_bottlenecks(patterns, structure),
            "improvement_opportunities": self._find_opportunities(patterns, structure)
        }
        
        return performance
    
    def _identify_bottlenecks(self, patterns: Dict, structure: Dict) -> List[str]:
        """Identify system bottlenecks"""
        bottlenecks = []
        
        # Check nested structure imbalance
        imbalance = structure["file_distribution"]["imbalance_ratio"]
        if imbalance > 0.8:
            bottlenecks.append(f"severe_category_imbalance_{imbalance:.1%}")
        
        # Check merge success rate
        merge_rate = patterns.get("merge_history", {}).get("success_rate", 0.0)
        if merge_rate < 0.9:
            bottlenecks.append(f"low_merge_success_{merge_rate:.1%}")
        
        # Check documentation gaps
        doc_rate = patterns.get("documentation_gaps", {}).get("conversion_rate", 0.0)
        if doc_rate < 0.5:
            bottlenecks.append(f"documentation_backlog_{doc_rate:.1%}")
        
        return bottlenecks
    
    def _find_opportunities(self, patterns: Dict, structure: Dict) -> List[Dict]:
        """Find improvement opportunities"""
        opportunities = []
        
        # AI category split opportunity
        ai_files = structure["categories"].get("ai", {}).get("total_files", 0)
        if ai_files > 1000:
            opportunities.append({
                "type": "category_split",
                "target": "ai_category",
                "impact": "high",
                "effort": "medium",
                "description": f"Split AI category ({ai_files} files) into specialized subcategories"
            })
        
        # Automation opportunity
        manual_tasks = patterns.get("todo_patterns", {}).get("active_todos", 0)
        if manual_tasks > 5:
            opportunities.append({
                "type": "automation",
                "target": "todo_workflow",
                "impact": "medium",
                "effort": "low",
                "description": "Automate repetitive TODO management tasks"
            })
        
        return opportunities
    
    def generate_roadmap_updates(self, performance: Dict) -> List[Dict]:
        """Generate roadmap updates based on performance"""
        updates = []
        
        # Check if current roadmap is effective
        bottlenecks = performance["bottlenecks"]
        
        if any("imbalance" in b for b in bottlenecks):
            updates.append({
                "action": "prioritize_rebalancing",
                "reason": "Critical imbalance detected",
                "new_priority": 1,
                "estimated_impact": 0.4
            })
        
        if any("merge_success" in b for b in bottlenecks):
            updates.append({
                "action": "enhance_merge_testing",
                "reason": "Low merge success rate",
                "new_priority": 2,
                "estimated_impact": 0.2
            })
        
        # Add new tasks based on opportunities
        for opp in performance["improvement_opportunities"]:
            if opp["impact"] == "high":
                updates.append({
                    "action": "add_task",
                    "task": opp["description"],
                    "priority": 1 if opp["impact"] == "high" else 3,
                    "estimated_impact": 0.3 if opp["impact"] == "high" else 0.1
                })
        
        return updates
    
    def calculate_improvement_rate(self, metric_name: str, current_value: float) -> float:
        """Calculate improvement rate for a metric"""
        if not self.history["cycles"]:
            return 0.0
        
        # Find previous values
        previous_cycles = [c for c in self.history["cycles"] if metric_name in c.get("metrics", {})]
        
        if len(previous_cycles) < 2:
            return 0.0
        
        # Calculate rate from last two cycles
        prev_value = previous_cycles[-1]["metrics"][metric_name]
        older_value = previous_cycles[-2]["metrics"][metric_name]
        
        if older_value == 0:
            return 0.0
        
        return (current_value - prev_value) / abs(older_value)
    
    def run_feedback_cycle(self) -> Dict:
        """Run complete feedback cycle"""
        print("🔄 Running self-improvement feedback cycle...")
        
        # Analyze current performance
        performance = self.analyze_system_performance()
        
        # Generate roadmap updates
        updates = self.generate_roadmap_updates(performance)
        
        # Calculate improvement rates
        improvement_rates = {}
        for metric_name, value in performance["metrics"].items():
            improvement_rates[metric_name] = self.calculate_improvement_rate(metric_name, value)
        
        # Create feedback cycle record
        cycle = {
            "timestamp": datetime.now().isoformat(),
            "performance": performance,
            "updates": updates,
            "improvement_rates": improvement_rates,
            "cycle_number": len(self.history["cycles"]) + 1
        }
        
        # Store cycle
        self.history["cycles"].append(cycle)
        self.save_history()
        
        return cycle
    
    def get_system_health(self) -> Dict:
        """Get overall system health score"""
        if not self.history["cycles"]:
            return {"health_score": 0.5, "status": "initializing"}
        
        latest = self.history["cycles"][-1]
        metrics = latest["performance"]["metrics"]
        
        # Calculate weighted health score
        weights = {
            "nested_efficiency": 0.3,
            "merge_success_rate": 0.25,
            "docs_conversion": 0.25,
            "todo_completion": 0.2
        }
        
        health_score = sum(metrics.get(metric, 0) * weight for metric, weight in weights.items())
        
        # Determine status
        if health_score >= 0.8:
            status = "excellent"
        elif health_score >= 0.6:
            status = "good"
        elif health_score >= 0.4:
            status = "needs_attention"
        else:
            status = "critical"
        
        return {
            "health_score": health_score,
            "status": status,
            "bottlenecks": len(latest["performance"]["bottlenecks"]),
            "opportunities": len(latest["performance"]["improvement_opportunities"]),
            "trend": self._calculate_trend()
        }
    
    def _calculate_trend(self) -> str:
        """Calculate overall improvement trend"""
        if len(self.history["cycles"]) < 2:
            return "stable"
        
        current = self.history["cycles"][-1]["performance"]["metrics"]
        previous = self.history["cycles"][-2]["performance"]["metrics"]
        
        improvements = 0
        total_metrics = 0
        
        for metric in current:
            if metric in previous:
                total_metrics += 1
                if current[metric] > previous[metric]:
                    improvements += 1
        
        if total_metrics == 0:
            return "stable"
        
        improvement_ratio = improvements / total_metrics
        
        if improvement_ratio >= 0.6:
            return "improving"
        elif improvement_ratio <= 0.4:
            return "declining"
        else:
            return "stable"
    
    def save_history(self):
        """Save feedback history"""
        with open(self.feedback_file, 'w') as f:
            json.dump(self.history, f, indent=2)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Self-improvement feedback loop")
    parser.add_argument("command", choices=["run", "health", "history"])
    
    args = parser.parse_args()
    feedback = FeedbackLoop()
    
    if args.command == "run":
        cycle = feedback.run_feedback_cycle()
        
        print("🎯 Feedback Cycle Complete")
        print("=" * 25)
        print(f"Cycle: #{cycle['cycle_number']}")
        print(f"Bottlenecks: {len(cycle['performance']['bottlenecks'])}")
        print(f"Opportunities: {len(cycle['performance']['improvement_opportunities'])}")
        print(f"Updates Generated: {len(cycle['updates'])}")
        
        if cycle['updates']:
            print(f"\n📋 Recommended Updates:")
            for update in cycle['updates'][:3]:
                print(f"  • {update['action']}: {update['reason']}")
    
    elif args.command == "health":
        health = feedback.get_system_health()
        
        print("🏥 System Health Report")
        print("=" * 22)
        print(f"Health Score: {health['health_score']:.1%}")
        print(f"Status: {health['status'].title()}")
        print(f"Trend: {health['trend'].title()}")
        print(f"Active Bottlenecks: {health['bottlenecks']}")
        print(f"Opportunities: {health['opportunities']}")
    
    elif args.command == "history":
        cycles = feedback.history.get("cycles", [])
        
        print(f"📈 Feedback History ({len(cycles)} cycles)")
        print("=" * 30)
        
        for cycle in cycles[-5:]:  # Show last 5 cycles
            print(f"\nCycle #{cycle['cycle_number']} - {cycle['timestamp'][:10]}")
            metrics = cycle['performance']['metrics']
            for name, value in metrics.items():
                print(f"  {name}: {value:.1%}")

if __name__ == "__main__":
    main()
