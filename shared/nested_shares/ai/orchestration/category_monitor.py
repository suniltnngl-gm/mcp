#!/usr/bin/env python3
"""Category Monitor - Continuous monitoring and self-improvement"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, asdict

@dataclass
class CategoryHealth:
    name: str
    file_count: int
    balance_score: float
    growth_rate: float
    last_optimized: str
    health_status: str  # healthy, warning, critical

class CategoryMonitor:
    def __init__(self):
        self.workspace_path = Path("/media/sunil-kr/workspace/user-projects/shared-tools/nested-shares")
        self.monitor_data_file = Path(__file__).parent / "category_monitor_data.json"
        self.load_historical_data()
    
    def load_historical_data(self):
        """Load historical monitoring data"""
        if self.monitor_data_file.exists():
            with open(self.monitor_data_file, 'r') as f:
                self.historical_data = json.load(f)
        else:
            self.historical_data = {"snapshots": [], "alerts": []}
    
    def take_snapshot(self) -> Dict:
        """Take current snapshot of category health"""
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "categories": {}
        }
        
        for cat_dir in self.workspace_path.iterdir():
            if cat_dir.is_dir() and not cat_dir.name.startswith('.'):
                health = self._assess_category_health(cat_dir)
                snapshot["categories"][cat_dir.name] = asdict(health)
        
        # Store snapshot
        self.historical_data["snapshots"].append(snapshot)
        
        # Keep only last 30 snapshots
        if len(self.historical_data["snapshots"]) > 30:
            self.historical_data["snapshots"] = self.historical_data["snapshots"][-30:]
        
        self.save_data()
        return snapshot
    
    def _assess_category_health(self, cat_path: Path) -> CategoryHealth:
        """Assess health of single category"""
        files = list(cat_path.rglob("*"))
        files = [f for f in files if f.is_file() and not f.name.startswith('.')]
        
        file_count = len(files)
        balance_score = self._calculate_balance_score(files, cat_path)
        growth_rate = self._calculate_growth_rate(cat_path.name, file_count)
        
        # Determine health status
        if file_count > 1000 or balance_score < 0.3:
            health_status = "critical"
        elif file_count > 500 or balance_score < 0.6:
            health_status = "warning"
        else:
            health_status = "healthy"
        
        return CategoryHealth(
            name=cat_path.name,
            file_count=file_count,
            balance_score=balance_score,
            growth_rate=growth_rate,
            last_optimized=self._get_last_optimization_date(cat_path.name),
            health_status=health_status
        )
    
    def _calculate_balance_score(self, files: List[Path], cat_path: Path) -> float:
        """Calculate balance score based on file distribution"""
        if not files:
            return 1.0
        
        # Analyze subdirectory distribution
        subdirs = {}
        for file_path in files:
            try:
                rel_path = file_path.relative_to(cat_path)
                if len(rel_path.parts) > 1:
                    subdir = rel_path.parts[0]
                    subdirs[subdir] = subdirs.get(subdir, 0) + 1
            except ValueError:
                continue
        
        if not subdirs:
            return 0.8  # Flat structure is okay for small categories
        
        # Calculate distribution balance
        file_counts = list(subdirs.values())
        avg_files = sum(file_counts) / len(file_counts)
        variance = sum((count - avg_files) ** 2 for count in file_counts) / len(file_counts)
        
        # Convert to 0-1 score (lower variance = higher score)
        balance_score = 1.0 / (1.0 + variance / max(1, avg_files))
        return min(1.0, balance_score)
    
    def _calculate_growth_rate(self, category_name: str, current_count: int) -> float:
        """Calculate growth rate compared to previous snapshots"""
        if len(self.historical_data["snapshots"]) < 2:
            return 0.0
        
        # Find previous count
        prev_snapshot = self.historical_data["snapshots"][-2]
        prev_count = prev_snapshot.get("categories", {}).get(category_name, {}).get("file_count", current_count)
        
        if prev_count == 0:
            return 0.0
        
        return (current_count - prev_count) / prev_count
    
    def _get_last_optimization_date(self, category_name: str) -> str:
        """Get last optimization date for category"""
        # Check for optimization markers in historical data
        for snapshot in reversed(self.historical_data["snapshots"]):
            if "optimizations" in snapshot:
                for opt in snapshot["optimizations"]:
                    if opt.get("category") == category_name:
                        return opt.get("timestamp", "unknown")
        
        return "never"
    
    def detect_issues(self, snapshot: Dict) -> List[Dict]:
        """Detect issues requiring attention"""
        issues = []
        
        for cat_name, cat_data in snapshot["categories"].items():
            health = CategoryHealth(**cat_data)
            
            # Critical size issues
            if health.file_count > 1000:
                issues.append({
                    "type": "oversized_category",
                    "category": cat_name,
                    "severity": "critical",
                    "description": f"Category has {health.file_count} files (>1000 threshold)",
                    "suggested_action": "Split category into smaller subcategories"
                })
            
            # Rapid growth issues
            if health.growth_rate > 0.5:
                issues.append({
                    "type": "rapid_growth",
                    "category": cat_name,
                    "severity": "warning",
                    "description": f"Category growing rapidly ({health.growth_rate:.1%} increase)",
                    "suggested_action": "Monitor and prepare for potential split"
                })
            
            # Balance issues
            if health.balance_score < 0.3:
                issues.append({
                    "type": "poor_balance",
                    "category": cat_name,
                    "severity": "warning",
                    "description": f"Poor file distribution (balance score: {health.balance_score:.1%})",
                    "suggested_action": "Reorganize subdirectory structure"
                })
        
        return issues
    
    def generate_optimization_suggestions(self, issues: List[Dict]) -> List[Dict]:
        """Generate optimization suggestions based on detected issues"""
        suggestions = []
        
        # Group issues by type
        issue_groups = {}
        for issue in issues:
            issue_type = issue["type"]
            if issue_type not in issue_groups:
                issue_groups[issue_type] = []
            issue_groups[issue_type].append(issue)
        
        # Generate suggestions
        if "oversized_category" in issue_groups:
            suggestions.append({
                "action": "execute_category_splits",
                "priority": "critical",
                "categories": [i["category"] for i in issue_groups["oversized_category"]],
                "estimated_time": "2-4 hours"
            })
        
        if "rapid_growth" in issue_groups:
            suggestions.append({
                "action": "setup_growth_monitoring",
                "priority": "medium",
                "categories": [i["category"] for i in issue_groups["rapid_growth"]],
                "estimated_time": "30 minutes"
            })
        
        if "poor_balance" in issue_groups:
            suggestions.append({
                "action": "rebalance_categories",
                "priority": "low",
                "categories": [i["category"] for i in issue_groups["poor_balance"]],
                "estimated_time": "1-2 hours"
            })
        
        return suggestions
    
    def save_data(self):
        """Save monitoring data"""
        with open(self.monitor_data_file, 'w') as f:
            json.dump(self.historical_data, f, indent=2)
    
    def run_monitoring_cycle(self) -> Dict:
        """Run complete monitoring cycle"""
        print("🔍 Running category monitoring cycle...")
        
        # Take snapshot
        snapshot = self.take_snapshot()
        
        # Detect issues
        issues = self.detect_issues(snapshot)
        
        # Generate suggestions
        suggestions = self.generate_optimization_suggestions(issues)
        
        # Store alerts for critical issues
        critical_issues = [i for i in issues if i["severity"] == "critical"]
        if critical_issues:
            alert = {
                "timestamp": datetime.now().isoformat(),
                "critical_issues": critical_issues,
                "suggestions": suggestions
            }
            self.historical_data["alerts"].append(alert)
            self.save_data()
        
        return {
            "snapshot": snapshot,
            "issues": issues,
            "suggestions": suggestions,
            "critical_count": len(critical_issues)
        }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Category monitor")
    parser.add_argument("command", choices=["snapshot", "monitor", "health", "issues"])
    
    args = parser.parse_args()
    monitor = CategoryMonitor()
    
    if args.command == "snapshot":
        snapshot = monitor.take_snapshot()
        
        print("📸 Category Snapshot")
        print("=" * 18)
        print(f"Timestamp: {snapshot['timestamp']}")
        print(f"Categories: {len(snapshot['categories'])}")
        
        for name, data in snapshot["categories"].items():
            health_emoji = {"healthy": "🟢", "warning": "🟡", "critical": "🔴"}[data["health_status"]]
            print(f"  {health_emoji} {name}: {data['file_count']} files, {data['balance_score']:.1%} balance")
    
    elif args.command == "monitor":
        result = monitor.run_monitoring_cycle()
        
        print("🔍 Monitoring Cycle Complete")
        print("=" * 25)
        print(f"Issues detected: {len(result['issues'])}")
        print(f"Critical issues: {result['critical_count']}")
        print(f"Suggestions: {len(result['suggestions'])}")
        
        if result["issues"]:
            print(f"\n⚠️  Issues Detected:")
            for issue in result["issues"][:3]:
                severity_emoji = {"critical": "🔴", "warning": "🟡", "info": "🔵"}[issue["severity"]]
                print(f"  {severity_emoji} {issue['category']}: {issue['description']}")
        
        if result["suggestions"]:
            print(f"\n💡 Suggestions:")
            for suggestion in result["suggestions"]:
                priority_emoji = {"critical": "🔴", "high": "🟡", "medium": "🟠", "low": "🟢"}[suggestion["priority"]]
                print(f"  {priority_emoji} {suggestion['action']}: {len(suggestion['categories'])} categories")

if __name__ == "__main__":
    main()
