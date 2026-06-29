#!/usr/bin/env python3
"""Automation Manager: Self-review, study, conclude, and report"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path("/media/sunil-kr/workspace/workspace-system/workspace_knowledge.db")

# Import all systems for analysis
try:
    from maintenance_system import get_complexity_score, get_utilization_summary
    from quality_gate import run_assessment, get_alerts
    from prevention_system import get_prevention_stats, proactive_check
    from tools_manager import list_tools, get_tool_stats
    from workspace_manager import todo_list, progress_list
    from proposal_system import list_proposals
    from session_manager import list_sessions
except ImportError:
    pass


def init_db():
    """Initialize automation tables"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Automated reports
    c.execute(
        """CREATE TABLE IF NOT EXISTS automated_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_type TEXT NOT NULL,
        period TEXT NOT NULL,
        data TEXT NOT NULL,
        summary TEXT,
        recommendations TEXT,
        created_at TEXT NOT NULL
    )"""
    )

    # Automated tasks
    c.execute(
        """CREATE TABLE IF NOT EXISTS automated_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_type TEXT NOT NULL,
        schedule TEXT NOT NULL,
        last_run TEXT,
        next_run TEXT,
        enabled INTEGER DEFAULT 1,
        created_at TEXT NOT NULL
    )"""
    )

    conn.commit()
    conn.close()


# === AUTOMATED REVIEW ===
def auto_review():
    """Automatically review system state"""
    review = {
        "timestamp": datetime.now().isoformat(),
        "metrics": {},
        "status": {},
        "issues": [],
        "achievements": [],
    }

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Complexity
    try:
        complexity = get_complexity_score()
        review["metrics"]["complexity"] = complexity["score"]
        review["status"]["complexity"] = complexity["level"]

        if complexity["level"] == "low":
            review["achievements"].append(f"Maintained low complexity: {complexity['score']}")
        elif complexity["level"] == "high":
            review["issues"].append(f"High complexity detected: {complexity['score']}")
    except:
        pass

    # Quality
    try:
        assessment = run_assessment("system", "workspace")
        review["metrics"]["quality_score"] = assessment["score"]
        review["metrics"]["quality_grade"] = assessment["grade"]

        if assessment["grade"] in ["A", "B"]:
            review["achievements"].append(f"High quality maintained: {assessment['grade']}")
        else:
            review["issues"].append(f"Quality needs improvement: {assessment['grade']}")
    except:
        pass

    # Tools
    try:
        tools = list_tools()
        active_tools = [t for t in tools if t[7] == "active"]
        total_usage = sum(t[8] for t in active_tools)
        total_success = sum(t[9] for t in active_tools)
        success_rate = (total_success / total_usage * 100) if total_usage > 0 else 0

        review["metrics"]["tools_active"] = len(active_tools)
        review["metrics"]["tool_success_rate"] = round(success_rate, 1)

        if success_rate >= 90:
            review["achievements"].append(f"High tool success rate: {success_rate:.1f}%")
        elif success_rate < 70:
            review["issues"].append(f"Low tool success rate: {success_rate:.1f}%")
    except:
        pass

    # Todos
    try:
        todos = todo_list()
        urgent = sum(1 for t in todos if t[4] == "urgent")
        completed = sum(1 for t in todos if t[3] == "done")

        review["metrics"]["todos_total"] = len(todos)
        review["metrics"]["todos_urgent"] = urgent
        review["metrics"]["todos_completed"] = completed

        if urgent > 5:
            review["issues"].append(f"High urgent todo count: {urgent}")
    except:
        pass

    # Alerts
    try:
        alerts = get_alerts()
        review["metrics"]["alerts_unresolved"] = len(alerts)

        if len(alerts) > 0:
            review["issues"].append(f"{len(alerts)} unresolved alerts")
    except:
        pass

    # Prevention
    try:
        prev_stats = get_prevention_stats()
        review["metrics"]["prevention_total"] = prev_stats["total_prevented"]
        review["metrics"]["prevention_recent"] = prev_stats["recent_prevented"]

        if prev_stats["recent_prevented"] > 0:
            review["achievements"].append(
                f"Prevented {prev_stats['recent_prevented']} issues this week"
            )
    except:
        pass

    conn.close()
    return review


# === AUTOMATED STUDY ===
def auto_study():
    """Study trends and patterns"""
    study = {
        "timestamp": datetime.now().isoformat(),
        "trends": {},
        "patterns": [],
        "insights": [],
    }

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Complexity trend
    c.execute(
        """SELECT value, created_at FROM complexity_metrics 
                 WHERE metric_type="total" 
                 ORDER BY created_at DESC LIMIT 10"""
    )
    complexity_history = c.fetchall()
    if len(complexity_history) >= 2:
        recent = complexity_history[0][0]
        older = complexity_history[-1][0]
        if recent < older:
            study["trends"]["complexity"] = "decreasing"
            study["insights"].append("Complexity is decreasing - good!")
        elif recent > older:
            study["trends"]["complexity"] = "increasing"
            study["insights"].append("Complexity is increasing - consider simplification")
        else:
            study["trends"]["complexity"] = "stable"

    # Quality trend
    c.execute(
        """SELECT score, created_at FROM assessments 
                 WHERE type="system" 
                 ORDER BY created_at DESC LIMIT 10"""
    )
    quality_history = c.fetchall()
    if len(quality_history) >= 2:
        recent_avg = sum(q[0] for q in quality_history[:3]) / 3
        older_avg = sum(q[0] for q in quality_history[-3:]) / 3
        if recent_avg > older_avg:
            study["trends"]["quality"] = "improving"
            study["insights"].append("Quality is improving - keep it up!")
        elif recent_avg < older_avg:
            study["trends"]["quality"] = "degrading"
            study["insights"].append("Quality is degrading - needs attention")
        else:
            study["trends"]["quality"] = "stable"

    # Tool usage patterns
    c.execute(
        """SELECT tool_id, COUNT(*) as usage 
                 FROM tool_executions 
                 WHERE created_at > datetime("now", "-7 days")
                 GROUP BY tool_id 
                 ORDER BY usage DESC LIMIT 5"""
    )
    top_tools = c.fetchall()
    if top_tools:
        study["patterns"].append(
            f"Most used tools: {len(top_tools)} tools account for majority of usage"
        )

    # Todo completion rate
    c.execute(
        """SELECT COUNT(*) FROM todos WHERE status="done" 
                 AND updated_at > datetime("now", "-7 days")"""
    )
    completed_week = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM todos WHERE status!="done"')
    pending = c.fetchone()[0]

    if completed_week > 0:
        study["patterns"].append(f"Completed {completed_week} todos this week")
        if pending > completed_week * 2:
            study["insights"].append("Todo backlog growing - prioritize completion")

    conn.close()
    return study


# === AUTOMATED CONCLUSION ===
def auto_conclude(review, study):
    """Draw conclusions and recommendations"""
    conclusion = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": "healthy",
        "key_findings": [],
        "recommendations": [],
        "action_items": [],
    }

    # Determine overall status
    issues_count = len(review.get("issues", []))
    quality_score = review["metrics"].get("quality_score", 100)

    if issues_count == 0 and quality_score >= 90:
        conclusion["overall_status"] = "excellent"
    elif issues_count <= 2 and quality_score >= 80:
        conclusion["overall_status"] = "healthy"
    elif issues_count <= 5 and quality_score >= 70:
        conclusion["overall_status"] = "needs_attention"
    else:
        conclusion["overall_status"] = "critical"

    # Key findings
    if review["achievements"]:
        conclusion["key_findings"].append(
            f"Achievements: {len(review['achievements'])} positive outcomes"
        )

    if review["issues"]:
        conclusion["key_findings"].append(f"Issues: {len(review['issues'])} items need attention")

    if study["trends"]:
        improving = sum(
            1 for t in study["trends"].values() if t == "improving" or t == "decreasing"
        )
        if improving > 0:
            conclusion["key_findings"].append(f"Positive trends: {improving} metrics improving")

    # Recommendations
    if review["metrics"].get("complexity", 0) > 100:
        conclusion["recommendations"].append("Reduce complexity through consolidation")
        conclusion["action_items"].append("Run: python3 maintenance_system.py complexity suggest")

    if review["metrics"].get("todos_urgent", 0) > 3:
        conclusion["recommendations"].append("Address urgent todos immediately")
        conclusion["action_items"].append("Run: ./ws todo | grep URGENT")

    if review["metrics"].get("alerts_unresolved", 0) > 0:
        conclusion["recommendations"].append("Resolve outstanding alerts")
        conclusion["action_items"].append("Run: python3 quality_gate.py alerts")

    if review["metrics"].get("tool_success_rate", 100) < 90:
        conclusion["recommendations"].append("Investigate and fix failing tools")
        conclusion["action_items"].append("Run: python3 tools_manager.py tool list")

    if study["trends"].get("quality") == "degrading":
        conclusion["recommendations"].append("Focus on quality improvement")
        conclusion["action_items"].append("Run: ./ws check")

    # If everything is good
    if not conclusion["recommendations"]:
        conclusion["recommendations"].append("Continue current practices")
        conclusion["action_items"].append("Run: ./ws maintain")

    return conclusion


# === GENERATE REPORT ===
def generate_report(period="daily"):
    """Generate comprehensive automated report"""
    print(f"\n{'='*70}")
    print(f"AUTOMATED SYSTEM REPORT - {period.upper()}")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")

    # Review
    print("📊 SYSTEM REVIEW")
    print("-" * 70)
    review = auto_review()

    print("\nMetrics:")
    for key, value in review["metrics"].items():
        print(f"  • {key.replace('_', ' ').title()}: {value}")

    if review["achievements"]:
        print("\n✅ Achievements:")
        for achievement in review["achievements"]:
            print(f"  • {achievement}")

    if review["issues"]:
        print("\n⚠️  Issues:")
        for issue in review["issues"]:
            print(f"  • {issue}")

    # Study
    print(f"\n{'='*70}")
    print("🔍 TREND ANALYSIS")
    print("-" * 70)
    study = auto_study()

    if study["trends"]:
        print("\nTrends:")
        for metric, trend in study["trends"].items():
            icon = (
                "📈"
                if trend in ["improving", "decreasing"]
                else "📉" if trend in ["degrading", "increasing"] else "➡️"
            )
            print(f"  {icon} {metric.title()}: {trend}")

    if study["patterns"]:
        print("\nPatterns:")
        for pattern in study["patterns"]:
            print(f"  • {pattern}")

    if study["insights"]:
        print("\nInsights:")
        for insight in study["insights"]:
            print(f"  💡 {insight}")

    # Conclusion
    print(f"\n{'='*70}")
    print("🎯 CONCLUSIONS & RECOMMENDATIONS")
    print("-" * 70)
    conclusion = auto_conclude(review, study)

    status_icons = {
        "excellent": "🟢",
        "healthy": "🟢",
        "needs_attention": "🟡",
        "critical": "🔴",
    }
    icon = status_icons.get(conclusion["overall_status"], "⚪")
    print(f"\nOverall Status: {icon} {conclusion['overall_status'].upper()}")

    if conclusion["key_findings"]:
        print("\nKey Findings:")
        for finding in conclusion["key_findings"]:
            print(f"  • {finding}")

    if conclusion["recommendations"]:
        print("\nRecommendations:")
        for i, rec in enumerate(conclusion["recommendations"], 1):
            print(f"  {i}. {rec}")

    if conclusion["action_items"]:
        print("\nAction Items:")
        for i, action in enumerate(conclusion["action_items"], 1):
            print(f"  {i}. {action}")

    print(f"\n{'='*70}\n")

    # Save report
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    report_data = {"review": review, "study": study, "conclusion": conclusion}

    summary = f"Status: {conclusion['overall_status']}, Issues: {len(review['issues'])}, Achievements: {len(review['achievements'])}"
    recommendations = json.dumps(conclusion["recommendations"])

    c.execute(
        """INSERT INTO automated_reports (report_type, period, data, summary, recommendations, created_at)
                 VALUES (?, ?, ?, ?, ?, ?)""",
        (
            "system_review",
            period,
            json.dumps(report_data),
            summary,
            recommendations,
            datetime.now().isoformat(),
        ),
    )

    conn.commit()
    conn.close()

    return report_data


# === TASK ADMINISTRATOR ===
def schedule_automated_tasks():
    """Schedule automated review tasks"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()

    tasks = [
        ("daily_review", "daily", "Generate daily system review"),
        ("weekly_study", "weekly", "Analyze weekly trends"),
        ("monthly_report", "monthly", "Comprehensive monthly report"),
    ]

    for task_type, schedule, description in tasks:
        try:
            c.execute(
                """INSERT INTO automated_tasks (task_type, schedule, next_run, created_at)
                        VALUES (?, ?, ?, ?)""",
                (task_type, schedule, now, now),
            )
        except:
            pass  # Already exists

    conn.commit()
    conn.close()


# === TOOL HELPERS ===
def quick_health_check():
    """Quick health check helper"""
    print("\n🏥 QUICK HEALTH CHECK")
    print("-" * 40)

    checks = []

    # Check 1: Database
    try:
        db_size = Path(DB_PATH).stat().st_size / 1024  # KB
        checks.append(("Database", "✓", f"{db_size:.1f} KB"))
    except:
        checks.append(("Database", "✗", "Not accessible"))

    # Check 2: Tools
    try:
        tools = list_tools()
        active = sum(1 for t in tools if t[7] == "active")
        checks.append(("Tools", "✓", f"{active} active"))
    except:
        checks.append(("Tools", "✗", "Error"))

    # Check 3: Quality
    try:
        assessment = run_assessment("system", "workspace")
        checks.append(("Quality", "✓", f"{assessment['grade']} grade"))
    except:
        checks.append(("Quality", "?", "Not assessed"))

    # Check 4: Prevention
    try:
        stats = get_prevention_stats()
        checks.append(("Prevention", "✓", f"{stats['active_rules']} rules"))
    except:
        checks.append(("Prevention", "?", "Not configured"))

    for name, status, detail in checks:
        print(f"  {status} {name:15} {detail}")

    print()


if __name__ == "__main__":
    import sys

    init_db()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  Report:   python automation_manager.py report [daily|weekly|monthly]")
        print("  Review:   python automation_manager.py review")
        print("  Study:    python automation_manager.py study")
        print("  Conclude: python automation_manager.py conclude")
        print("  Health:   python automation_manager.py health")
        print("  Schedule: python automation_manager.py schedule")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "report":
        period = sys.argv[2] if len(sys.argv) > 2 else "daily"
        generate_report(period)

    elif cmd == "review":
        review = auto_review()
        print(json.dumps(review, indent=2))

    elif cmd == "study":
        study = auto_study()
        print(json.dumps(study, indent=2))

    elif cmd == "conclude":
        review = auto_review()
        study = auto_study()
        conclusion = auto_conclude(review, study)
        print(json.dumps(conclusion, indent=2))

    elif cmd == "health":
        quick_health_check()

    elif cmd == "schedule":
        schedule_automated_tasks()
        print("✓ Automated tasks scheduled")
