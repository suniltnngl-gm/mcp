#!/usr/bin/env python3
"""
Lean Versioning Dashboard - Monitor version tracking and improvement history
Integrates with lean versioning system for insights and learning
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class LeanVersioningDashboard:
    def __init__(self, workspace_root: str = None):
        self.workspace_root = Path(workspace_root or os.getcwd())
        self.registry_path = self.workspace_root / ".kiro" / "lean_versions.json"
    
    def load_registry(self) -> Dict:
        """Load version registry"""
        if not self.registry_path.exists():
            return {"versions": {}, "sessions": {}}
        return json.loads(self.registry_path.read_text())
    
    def get_stats(self) -> Dict:
        """Get version statistics"""
        registry = self.load_registry()
        versions = registry.get("versions", {})
        sessions = registry.get("sessions", {})
        
        total_versions = len(versions)
        active_sessions = len([s for s in sessions.values() if s.get("active", False)])
        
        # Count improvements by type
        improvements = {}
        for version in versions.values():
            imp_type = version.get("improvement_type", "unknown")
            improvements[imp_type] = improvements.get(imp_type, 0) + 1
        
        return {
            "total_versions": total_versions,
            "active_sessions": active_sessions,
            "improvement_types": improvements,
            "last_activity": max([v.get("timestamp", "") for v in versions.values()], default="")
        }
    
    def get_recent_activity(self, limit: int = 10) -> List[Dict]:
        """Get recent version activity"""
        registry = self.load_registry()
        versions = list(registry.get("versions", {}).values())
        
        # Sort by timestamp
        versions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return versions[:limit]
    
    def get_learning_insights(self) -> List[str]:
        """Extract learning insights from version history"""
        registry = self.load_registry()
        versions = registry.get("versions", {})
        
        insights = []
        
        # Success patterns
        success_types = {}
        for version in versions.values():
            if version.get("success", False):
                imp_type = version.get("improvement_type", "unknown")
                success_types[imp_type] = success_types.get(imp_type, 0) + 1
        
        if success_types:
            best_type = max(success_types, key=success_types.get)
            insights.append(f"Most successful improvement type: {best_type} ({success_types[best_type]} successes)")
        
        # Error patterns
        errors = [v for v in versions.values() if v.get("errors")]
        if errors:
            insights.append(f"Found {len(errors)} versions with errors - review for patterns")
        
        return insights
    
    def display_dashboard(self):
        """Display dashboard in terminal"""
        stats = self.get_stats()
        recent = self.get_recent_activity(5)
        insights = self.get_learning_insights()
        
        print("=== Lean Versioning Dashboard ===\n")
        
        print("📊 Statistics:")
        print(f"  Total Versions: {stats['total_versions']}")
        print(f"  Active Sessions: {stats['active_sessions']}")
        print(f"  Last Activity: {stats['last_activity']}")
        
        if stats['improvement_types']:
            print("\n🔧 Improvement Types:")
            for imp_type, count in stats['improvement_types'].items():
                print(f"  {imp_type}: {count}")
        
        if recent:
            print("\n📈 Recent Activity:")
            for version in recent:
                timestamp = version.get("timestamp", "")[:19]  # Remove microseconds
                imp_type = version.get("improvement_type", "unknown")
                success = "✅" if version.get("success") else "⏳"
                print(f"  {success} {timestamp} - {imp_type}")
        
        if insights:
            print("\n💡 Learning Insights:")
            for insight in insights:
                print(f"  • {insight}")
        
        print()

def main():
    """CLI interface for dashboard"""
    import sys
    
    dashboard = LeanVersioningDashboard()
    
    if len(sys.argv) > 1 and sys.argv[1] == "json":
        # JSON output for automation
        stats = dashboard.get_stats()
        recent = dashboard.get_recent_activity()
        insights = dashboard.get_learning_insights()
        
        output = {
            "stats": stats,
            "recent_activity": recent,
            "insights": insights
        }
        print(json.dumps(output, indent=2))
    else:
        # Human-readable dashboard
        dashboard.display_dashboard()

if __name__ == "__main__":
    main()
