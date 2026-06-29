#!/usr/bin/env python3

import json
import time
import os
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import sqlite3

DB_PATH = Path("/media/sunil-kr/workspace/workspace-system/workspace_knowledge.db")

class UnifiedMonitor:
    def __init__(self):
        self.kb_dir = Path(__file__).parent.parent / "knowledge_base"
        self.refresh_interval = 5
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS health_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT NOT NULL,
            data TEXT,
            checked_at TEXT NOT NULL
        )"""
        )
        conn.commit()
        conn.close()

        
    def load_data(self):
        """Load current system data"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "errors": self._load_errors(),
            "solutions": self._load_solutions(),
            "system_health": self._check_system_health(),
            "workflow_status": self._check_workflow_status()
        }
        return data
    
    def _load_errors(self):
        """Load error data from knowledge base"""
        try:
            with open(self.kb_dir / "errors.json") as f:
                errors = json.load(f)
                return {
                    "total": len(errors),
                    "by_type": self._count_by_type(errors),
                    "recent": self._get_recent_errors(errors)
                }
        except:
            return {"total": 0, "by_type": {}, "recent": []}
    
    def _load_solutions(self):
        """Load solution effectiveness data"""
        try:
            with open(self.kb_dir / "solutions.json") as f:
                solutions = json.load(f)
                total_successes = 0
                total_attempts = 0
                
                for solution in solutions.values():
                    eff = solution.get("effectiveness", {})
                    total_successes += eff.get("successes", 0)
                    total_attempts += eff.get("successes", 0) + eff.get("failures", 0)
                
                success_rate = (total_successes / total_attempts * 100) if total_attempts > 0 else 0
                
                return {
                    "total": len(solutions),
                    "success_rate": round(success_rate, 1),
                    "total_corrections": total_successes,
                    "total_attempts": total_attempts
                }
        except:
            return {"total": 0, "success_rate": 0, "total_corrections": 0, "total_attempts": 0}
    
    def get_health_history(self, hours=24):
        """Get health history"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        since = (datetime.now() - timedelta(hours=hours)).isoformat()
        c.execute(
            """SELECT status, checked_at FROM health_checks 
            WHERE checked_at > ? ORDER BY checked_at DESC""",
            (since,),
        )

        history = c.fetchall()
        conn.close()
        return history

    def _check_system_health(self):
        """Check overall system health"""
        platform_health = self._check_autonomous_platform_health()
        workspace_health = self._check_workspace_health()

        issues = platform_health["issues"] + workspace_health["issues"]
        status = "HEALTHY"
        if issues:
            status = "WARNING"
        if platform_health["status"] == "degraded" or workspace_health["status"] == "CRITICAL":
            status = "CRITICAL"

        return {
            "status": status,
            "issues": issues,
            "platform_health": platform_health,
            "workspace_health": workspace_health,
        }

    def _check_workspace_health(self):
        """Run health check and record"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Database size
        db_size = DB_PATH.stat().st_size

        # Active tools
        c.execute("SELECT COUNT(*) FROM tools")
        tools_active = c.fetchone()[0]

        # Quality grade
        c.execute("SELECT grade FROM assessments ORDER BY created_at DESC LIMIT 1")
        row = c.fetchone()
        quality_grade = row[0] if row else "N/A"

        # Unresolved alerts
        c.execute("SELECT COUNT(*) FROM degradation_alerts WHERE resolved = 0")
        alerts = c.fetchone()[0]

        # Determine status
        issues = []
        if db_size > 10 * 1024 * 1024:  # > 10MB
            issues.append("Database too large")
        if tools_active < 5:
            issues.append("Few tools active")
        if quality_grade in ["D", "F"]:
            issues.append("Low quality grade")
        if alerts > 5:
            issues.append("Many unresolved alerts")

        status = "CRITICAL" if len(issues) >= 3 else "WARNING" if issues else "HEALTHY"

        # Record check
        import json

        data = json.dumps(
            {
                "db_size": db_size,
                "tools_active": tools_active,
                "quality_grade": quality_grade,
                "alerts": alerts,
                "issues": issues,
            }
        )
        c.execute(
            """INSERT INTO health_checks (status, data, checked_at)
            VALUES (?, ?, ?)""",
            (status, data, datetime.now().isoformat()),
        )

        conn.commit()
        conn.close()

        return {
            "status": status,
            "db_size": db_size,
            "tools_active": tools_active,
            "quality_grade": quality_grade,
            "alerts": alerts,
            "issues": issues,
        }

    def _check_autonomous_platform_health(self):
        """Check overall system health"""
        health = {"status": "healthy", "issues": []}
        
        # Check key components
        components = [
            "scripts/automated_correction.py",
            "scripts/self_healing_wrapper.sh", 
            "scripts/validation_wrapper.sh",
            "knowledge_base/solutions.json"
        ]
        
        for component in components:
            if not Path(component).exists():
                health["issues"].append(f"Missing: {component}")
                health["status"] = "degraded"
        
        return health
    
    def _check_workflow_status(self):
        """Check workflow integration status"""
        enhanced_workflows = 0
        total_workflows = 7
        
        workflows = ["cli.sh", "health_check.sh", "advanced_testing.sh", 
                    "production_readiness.sh", "ai_workflow.sh", 
                    "custom_development.sh", "analytics_insights.sh"]
        
        for workflow in workflows:
            script_path = Path(f"scripts/{workflow}")
            if script_path.exists():
                try:
                    content = script_path.read_text()
                    if "validation_wrapper.sh" in content:
                        enhanced_workflows += 1
                except:
                    pass
        
        return {
            "enhanced": enhanced_workflows,
            "total": total_workflows,
            "coverage": round(enhanced_workflows / total_workflows * 100, 1)
        }
    
    def _count_by_type(self, errors):
        """Count errors by type"""
        counts = {}
        for error in errors.values():
            error_type = error.get("type", "unknown")
            counts[error_type] = counts.get(error_type, 0) + 1
        return counts
    
    def _get_recent_errors(self, errors, hours=24):
        """Get recent errors within specified hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = []
        
        for error in errors.values():
            try:
                error_time = datetime.fromisoformat(error.get("timestamp", ""))
                if error_time > cutoff:
                    recent.append(error)
            except:
                pass
        
        return recent[:5]  # Last 5 recent errors
    
    def display_dashboard(self):
        """Display real-time dashboard"""
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')
            
            data = self.load_data()
            
            print("🔍 UNIFIED MONITORING DASHBOARD")
            print("=" * 50)
            print(f"📅 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
            # System Health
            health = data["system_health"]
            status_icon = "🟢" if health["status"] == "HEALTHY" else "🟡" if health["status"] == "WARNING" else "🔴"
            print(f"{status_icon} OVERALL SYSTEM HEALTH: {health['status'].upper()}")
            if health["issues"]:
                for issue in health["issues"]:
                    print(f"  ⚠️  {issue}")
            print()

            # Workspace Health
            workspace_health = health['workspace_health']
            ws_status_icon = "🟢" if workspace_health["status"] == "HEALTHY" else "🟡" if workspace_health["status"] == "WARNING" else "🔴"
            print(f"{ws_status_icon} WORKSPACE HEALTH: {workspace_health['status'].upper()}")
            print(f"  Database:     {workspace_health['db_size'] / 1024:.1f} KB")
            print(f"  Tools Active: {workspace_health['tools_active']}")
            print(f"  Quality:      {workspace_health['quality_grade']}")
            print(f"  Alerts:       {workspace_health['alerts']}")
            print()

            # Autonomous Platform Health
            platform_health = health['platform_health']
            ph_status_icon = "🟢" if platform_health["status"] == "healthy" else "🟡"
            print(f"{ph_status_icon} AUTONOMOUS PLATFORM HEALTH: {platform_health['status'].upper()}")
            if platform_health["issues"]:
                for issue in platform_health["issues"]:
                    print(f"  ⚠️  {issue}")
            print()
            
            # Workflow Status
            workflow = data["workflow_status"]
            print(f"🔗 WORKFLOW INTEGRATION: {workflow['enhanced']}/{workflow['total']} ({workflow['coverage']}%%)")
            print()
            
            # Self-Healing Metrics
            solutions = data["solutions"]
            print(f"🤖 AUTONOMOUS CORRECTIONS:")
            print(f"  📊 Success Rate: {solutions['success_rate']}%")
            print(f"  ✅ Total Corrections: {solutions['total_corrections']}")
            print(f"  🎯 Available Solutions: {solutions['total']}")
            print()
            
            # Error Analytics
            errors = data["errors"]
            print(f"📈 ERROR ANALYTICS:")
            print(f"  📝 Total Errors Learned: {errors['total']}")
            
            if errors["by_type"]:
                print("  🏷️  Error Types:")
                for error_type, count in errors["by_type"].items():
                    print(f"     • {error_type}: {count}")
            
            if errors["recent"]:
                print(f"  🕐 Recent Activity ({len(errors['recent'])} in 24h):")
                for error in errors["recent"][:3]:
                    print(f"     • {error.get('type', 'unknown')}: {error.get('message', 'N/A')[:40]}...")
            print()
            
            # Real-time Activity
            print("🔄 REAL-TIME ACTIVITY:")
            print("  Monitoring autonomous operations...")
            print("  Press Ctrl+C to exit")
            
            time.sleep(self.refresh_interval)
    
    def generate_report(self):
        """Generate summary report"""
        data = self.load_data()
        
        report = f"""
# Unified Monitoring Report
Generated: {data['timestamp']}

## Overall System Health: {data['system_health']['status'].upper()}
- Total Issues: {len(data['system_health']['issues'])}

### Workspace Health: {data['system_health']['workspace_health']['status']}
- Database Size: {data['system_health']['workspace_health']['db_size'] / 1024:.1f} KB
- Active Tools: {data['system_health']['workspace_health']['tools_active']}
- Quality Grade: {data['system_health']['workspace_health']['quality_grade']}
- Unresolved Alerts: {data['system_health']['workspace_health']['alerts']}

### Autonomous Platform Health: {data['system_health']['platform_health']['status']}
- Workflow Integration: {data['workflow_status']['coverage']}% ({data['workflow_status']['enhanced']}/{data['workflow_status']['total']})
- Available Solutions: {data['solutions']['total']}
- Success Rate: {data['solutions']['success_rate']}%

## Performance Metrics
- Total Corrections Applied: {data['solutions']['total_corrections']}
- Total Errors Learned: {data['errors']['total']}
- Recent Activity: {len(data['errors']['recent'])} errors in 24h

## Error Distribution
"""
        
        for error_type, count in data['errors']['by_type'].items():
            report += f"- {error_type}: {count}\n"
        
        return report

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified Monitoring Dashboard")
    parser.add_argument("--report", action="store_true", help="Generate text report instead of dashboard")
    parser.add_argument("--history", action="store_true", help="Display health history")
    parser.add_argument("--hours", type=int, default=24, help="Hours of history to display")
    
    args = parser.parse_args()
    
    monitor = UnifiedMonitor()
    
    if args.report:
        print(monitor.generate_report())
    elif args.history:
        history = monitor.get_health_history(args.hours)
        print(f"\n📊 HEALTH HISTORY (last {args.hours}h)")
        print("-" * 60)

        if not history:
            print("  No history available")
            return

        emoji = {"HEALTHY": "🟢", "WARNING": "🟡", "CRITICAL": "🔴"}
        for status, checked_at in history[:40]:
            dt = datetime.fromisoformat(checked_at)
            print(f"  {emoji.get(status, '❓')} {status:10} - {dt.strftime('%Y-%m-%d %H:%M')}")
    else:
        try:
            monitor.display_dashboard()
        except KeyboardInterrupt:
            print("\n\n👋 Dashboard stopped. System continues autonomous operation.")

if __name__ == "__main__":
    main()
