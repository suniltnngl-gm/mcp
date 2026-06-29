#!/usr/bin/env python3
"""Systematic Improvement Dashboard - Unified view of all tracking systems"""

from shared_tools.utils.config_utils import get_workspace_path
import json
from pathlib import Path
from datetime import datetime
from shared_tools.nested_shares.workspace_core.error_registry_integration import ErrorRegistryIntegration

class ImprovementDashboard:
    def __init__(self):
        self.workspace_path = get_workspace_path()
        self.framework_path = Path(__file__).parent
        
    def generate_unified_dashboard(self) -> dict:
        """Generate unified dashboard showing all systematic improvements"""
        
        print("📊 GENERATING SYSTEMATIC IMPROVEMENT DASHBOARD")
        print("Unifying: inventory + roadmap + todos + progress + errors + versions\n")
        
        # Collect data from all tracking systems
        inventory_status = self._get_inventory_status()
        roadmap_status = self._get_roadmap_status()
        todo_status = self._get_todo_status()
        progress_status = self._get_progress_status()
        error_status = self._get_error_status()
        version_status = self._get_version_status()
        
        # Calculate overall health score
        health_score = self._calculate_overall_health(
            inventory_status, roadmap_status, todo_status, 
            progress_status, error_status, version_status
        )
        
        # Generate improvement recommendations
        recommendations = self._generate_recommendations(
            inventory_status, roadmap_status, todo_status
        )
        
        dashboard = {
            "generated_at": datetime.now().isoformat(),
            "framework_version": "1.0.0",
            "overall_health_score": health_score,
            "components": {
                "system_inventory": inventory_status,
                "improvement_roadmap": roadmap_status,
                "todo_registry": todo_status,
                "progress_tracking": progress_status,
                "error_registry": error_status,
                "file_versions": version_status
            },
            "recommendations": recommendations,
            "next_actions": self._get_next_actions()
        }
        
        # Save dashboard
        dashboard_file = self.framework_path / "improvement_dashboard.json"
        dashboard_file.write_text(json.dumps(dashboard, indent=2))
        
        return dashboard
    
    def _get_inventory_status(self) -> dict:
        """Get system inventory status"""
        
        inventory_file = self.framework_path / "unified_system_inventory.json"
        
        if inventory_file.exists():
            try:
                inventory = json.loads(inventory_file.read_text())
                return {
                    "status": "active",
                    "total_systems": inventory.get("metadata", {}).get("total_systems", 0),
                    "improvement_opportunities": inventory.get("metadata", {}).get("improvement_opportunities", 0),
                    "last_updated": inventory.get("metadata", {}).get("last_updated", "unknown"),
                    "health": "good" if inventory.get("metadata", {}).get("total_systems", 0) > 100 else "needs_attention"
                }
            except:
                pass
        
        return {
            "status": "needs_initialization",
            "total_systems": 0,
            "improvement_opportunities": 0,
            "health": "critical"
        }
    
    def _get_roadmap_status(self) -> dict:
        """Get improvement roadmap status"""
        
        roadmap_file = self.framework_path / "improvement_roadmap.json"
        
        if roadmap_file.exists():
            try:
                roadmap = json.loads(roadmap_file.read_text())
                phases = roadmap.get("phases", {})
                
                completed_phases = sum(1 for p in phases.values() if p.get("status") == "completed")
                total_phases = len(phases)
                
                return {
                    "status": "active",
                    "total_phases": total_phases,
                    "completed_phases": completed_phases,
                    "completion_rate": (completed_phases / total_phases * 100) if total_phases > 0 else 0,
                    "current_phase": self._get_current_phase(phases),
                    "health": "good" if completed_phases > 0 else "needs_attention"
                }
            except:
                pass
        
        return {
            "status": "needs_initialization",
            "total_phases": 0,
            "completed_phases": 0,
            "completion_rate": 0,
            "health": "critical"
        }
    
    def _get_current_phase(self, phases: dict) -> str:
        """Get current active phase"""
        
        for phase_id, phase in phases.items():
            if phase.get("status") == "in_progress":
                return phase.get("title", phase_id)
        
        return "No active phase"
    
    def _get_todo_status(self) -> dict:
        """Get todo registry status"""
        
        todo_file = self.framework_path / "improvement_todos.json"
        
        if todo_file.exists():
            try:
                todos = json.loads(todo_file.read_text())
                
                total_todos = len(todos.get("todos", []))
                completed_todos = len(todos.get("completed", []))
                
                return {
                    "status": "active",
                    "total_todos": total_todos,
                    "completed_todos": completed_todos,
                    "completion_rate": (completed_todos / (total_todos + completed_todos) * 100) if (total_todos + completed_todos) > 0 else 0,
                    "pending_todos": total_todos,
                    "health": "good" if total_todos < 20 else "needs_attention"
                }
            except:
                pass
        
        return {
            "status": "needs_initialization",
            "total_todos": 0,
            "completed_todos": 0,
            "completion_rate": 0,
            "health": "critical"
        }
    
    def _get_progress_status(self) -> dict:
        """Get progress tracking status"""
        
        progress_file = self.framework_path / "progress_metrics.json"
        
        if progress_file.exists():
            try:
                progress = json.loads(progress_file.read_text())
                metrics = progress.get("metrics", {})
                
                # Calculate average progress
                total_progress = 0
                metric_count = 0
                
                for metric_name, metric_data in metrics.items():
                    current = metric_data.get("current_value", 0)
                    target = metric_data.get("target_value", 100)
                    
                    if metric_name == "system_redundancy":
                        # For redundancy, lower is better
                        progress_pct = max(0, (target - current) / target * 100)
                    else:
                        # For others, higher is better
                        progress_pct = min(100, current / target * 100)
                    
                    total_progress += progress_pct
                    metric_count += 1
                
                avg_progress = total_progress / metric_count if metric_count > 0 else 0
                
                return {
                    "status": "active",
                    "metrics_tracked": metric_count,
                    "average_progress": avg_progress,
                    "health_score": metrics.get("system_health_score", {}).get("current_value", 0),
                    "health": "good" if avg_progress > 60 else "needs_attention"
                }
            except:
                pass
        
        return {
            "status": "needs_initialization",
            "metrics_tracked": 0,
            "average_progress": 0,
            "health": "critical"
        }
    
    def _get_error_status(self) -> dict:
        """Get error registry status"""
        
        # Use ErrorRegistryIntegration to load the unified error registry
        error_integration = ErrorRegistryIntegration(workspace_root=self.workspace_path)
        error_registry = error_integration.load_error_registry()
        
        # Extract relevant information
        total_errors = len(error_registry.get("errors", {}))
        patterns_found = len(error_registry.get("patterns", {}))
        prevention_rules = len(error_registry.get("prevention_rules", []))
        critical_learnings_count = len(error_registry.get("critical_learnings", {}))
        
        # Calculate a simple health based on rules and critical learnings
        health = "good" if prevention_rules > 0 and critical_learnings_count > 0 else "needs_attention"
        if total_errors > 50 and prevention_rules < 5: # Example: many errors, few rules
            health = "critical"

        return {
            "status": "active",
            "total_errors_recorded": total_errors,
            "patterns_found": patterns_found,
            "prevention_rules_generated": prevention_rules,
            "critical_learnings_integrated": critical_learnings_count,
            "health": health
        }
    
    def _get_version_status(self) -> dict:
        """Get file version registry status"""
        
        version_file = self.framework_path / "file_version_registry.json"
        
        if version_file.exists():
            try:
                versions = json.loads(version_file.read_text())
                
                files_tracked = len(versions.get("files", {}))
                total_changes = versions.get("change_tracking", {}).get("total_changes", 0)
                
                return {
                    "status": "active",
                    "files_tracked": files_tracked,
                    "total_changes": total_changes,
                    "last_scan": versions.get("change_tracking", {}).get("last_scan", "unknown"),
                    "health": "good" if files_tracked > 0 else "needs_attention"
                }
            except:
                pass
        
        return {
            "status": "needs_initialization",
            "files_tracked": 0,
            "total_changes": 0,
            "health": "critical"
        }
    
    def _calculate_overall_health(self, *component_statuses) -> float:
        """Calculate overall system health score"""
        
        health_scores = []
        
        for status in component_statuses:
            if status.get("health") == "good":
                health_scores.append(85)
            elif status.get("health") == "needs_attention":
                health_scores.append(60)
            else:  # critical
                health_scores.append(30)
        
        return sum(health_scores) / len(health_scores) if health_scores else 0
    
    def _generate_recommendations(self, inventory_status: dict, roadmap_status: dict, todo_status: dict) -> list:
        """Generate improvement recommendations"""
        
        recommendations = []
        
        # Inventory recommendations
        if inventory_status.get("improvement_opportunities", 0) > 20:
            recommendations.append(f"High consolidation potential: {inventory_status['improvement_opportunities']} systems need consolidation")
        
        # Roadmap recommendations
        if roadmap_status.get("completion_rate", 0) < 50:
            recommendations.append("Roadmap progress is behind - focus on completing current phase")
        
        # Todo recommendations
        if todo_status.get("pending_todos", 0) > 15:
            recommendations.append(f"Todo backlog is high: {todo_status['pending_todos']} pending items need attention")
        
        # General recommendations
        if not recommendations:
            recommendations.append("System health is good - continue systematic improvement cycle")
        
        return recommendations
    
    def _get_next_actions(self) -> list:
        """Get recommended next actions"""
        
        return [
            "Execute systematic update cycle to refresh all tracking data",
            "Review high-priority improvement opportunities",
            "Advance current roadmap phase based on progress",
            "Address pending todos with high impact potential",
            "Update error registry with latest API learnings",
            "Monitor system health metrics for trends"
        ]

def main():
    """Generate and display systematic improvement dashboard"""
    
    dashboard = ImprovementDashboard()
    result = dashboard.generate_unified_dashboard()
    
    print("📊 SYSTEMATIC IMPROVEMENT DASHBOARD")
    print("=" * 50)
    
    print(f"\n🎯 OVERALL HEALTH SCORE: {result['overall_health_score']:.1f}/100")
    
    print(f"\n📋 COMPONENT STATUS:")
    for component, status in result["components"].items():
        health_icon = "✅" if status["health"] == "good" else "⚠️" if status["health"] == "needs_attention" else "❌"
        print(f"  {health_icon} {component}: {status['status']}")
    
    print(f"\n🎯 KEY METRICS:")
    inventory = result["components"]["system_inventory"]
    roadmap = result["components"]["improvement_roadmap"]
    todos = result["components"]["todo_registry"]
    errors_status = result["components"]["error_registry"] # New line

    print(f"  - Systems cataloged: {inventory.get('total_systems', 0)}")
    print(f"  - Improvement opportunities: {inventory.get('improvement_opportunities', 0)}")
    print(f"  - Roadmap completion: {roadmap.get('completion_rate', 0):.1f}%")
    print(f"  - Pending todos: {todos.get('pending_todos', 0)}")
    # New error metrics
    print(f"  - Total errors recorded: {errors_status.get('total_errors_recorded', 0)}")
    print(f"  - Error patterns found: {errors_status.get('patterns_found', 0)}")
    print(f"  - Prevention rules generated: {errors_status.get('prevention_rules_generated', 0)}")
    print(f"  - Critical learnings integrated: {errors_status.get('critical_learnings_integrated', 0)}")
    
    print(f"\n🚀 TOP RECOMMENDATIONS:")
    for i, rec in enumerate(result["recommendations"][:3], 1):
        print(f"  {i}. {rec}")
    
    print(f"\n📅 NEXT ACTIONS:")
    for i, action in enumerate(result["next_actions"][:3], 1):
        print(f"  {i}. {action}")
    
    print(f"\n✅ DASHBOARD GENERATED: improvement_dashboard.json")
    print(f"🔄 Run systematic update cycle for latest data")

if __name__ == "__main__":
    main()
