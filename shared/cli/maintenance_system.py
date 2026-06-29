#!/usr/bin/env python3
"""Maintenance System: Scheduled tasks, capability tracking, complexity management"""
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

DB_PATH = Path("/media/sunil-kr/workspace/workspace-system/workspace_knowledge.db")


def init_db():
    """Initialize maintenance tables"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Maintenance tasks
    c.execute(
        """CREATE TABLE IF NOT EXISTS maintenance_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        schedule TEXT NOT NULL,
        command TEXT NOT NULL,
        priority TEXT DEFAULT 'normal',
        enabled INTEGER DEFAULT 1,
        last_run TEXT,
        next_run TEXT,
        run_count INTEGER DEFAULT 0,
        avg_duration REAL DEFAULT 0,
        created_at TEXT NOT NULL
    )"""
    )

    # Task executions
    c.execute(
        """CREATE TABLE IF NOT EXISTS task_executions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        status TEXT NOT NULL,
        duration REAL,
        output TEXT,
        error TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (task_id) REFERENCES maintenance_tasks(id)
    )"""
    )

    # System capabilities
    c.execute(
        """CREATE TABLE IF NOT EXISTS capabilities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        type TEXT NOT NULL,
        status TEXT DEFAULT 'available',
        complexity INTEGER DEFAULT 1,
        dependencies TEXT,
        usage_count INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )"""
    )

    # Complexity metrics
    c.execute(
        """CREATE TABLE IF NOT EXISTS complexity_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        component TEXT NOT NULL,
        metric_type TEXT NOT NULL,
        value INTEGER NOT NULL,
        threshold INTEGER,
        created_at TEXT NOT NULL
    )"""
    )

    # Utilization tracking
    c.execute(
        """CREATE TABLE IF NOT EXISTS utilization (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resource TEXT NOT NULL,
        used REAL NOT NULL,
        total REAL NOT NULL,
        percent REAL NOT NULL,
        created_at TEXT NOT NULL
    )"""
    )

    conn.commit()
    conn.close()


# === MAINTENANCE TASKS ===
def add_task(name, schedule, command, description="", priority="normal"):
    """Add maintenance task"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()

    # Calculate next run
    next_run = calculate_next_run(schedule)

    try:
        c.execute(
            """INSERT INTO maintenance_tasks 
                     (name, description, schedule, command, priority, next_run, created_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (name, description, schedule, command, priority, next_run, now),
        )
        conn.commit()
        task_id = c.lastrowid
    except sqlite3.IntegrityError:
        task_id = None
    finally:
        conn.close()
    return task_id


def calculate_next_run(schedule):
    """Calculate next run time from schedule"""
    now = datetime.now()

    if schedule == "hourly":
        next_run = now + timedelta(hours=1)
    elif schedule == "daily":
        next_run = now + timedelta(days=1)
    elif schedule == "weekly":
        next_run = now + timedelta(weeks=1)
    elif schedule.startswith("every_"):
        # e.g., "every_5_minutes"
        parts = schedule.split("_")
        if len(parts) == 3:
            interval = int(parts[1])
            unit = parts[2]
            if unit == "minutes":
                next_run = now + timedelta(minutes=interval)
            elif unit == "hours":
                next_run = now + timedelta(hours=interval)
            else:
                next_run = now + timedelta(days=1)
        else:
            next_run = now + timedelta(days=1)
    else:
        next_run = now + timedelta(days=1)

    return next_run.isoformat()


def run_due_tasks():
    """Run tasks that are due"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()

    c.execute(
        """SELECT * FROM maintenance_tasks 
                 WHERE enabled=1 AND next_run <= ?
                 ORDER BY priority DESC""",
        (now,),
    )
    tasks = c.fetchall()

    results = []

    for task in tasks:
        task_id = task[0]
        name = task[1]
        command = task[4]
        schedule = task[3]

        # Execute task
        start = datetime.now()
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=300
            )
            status = "success" if result.returncode == 0 else "failed"
            output = result.stdout[:1000]
            error = result.stderr[:1000] if result.returncode != 0 else None
        except subprocess.TimeoutExpired:
            status = "timeout"
            output = ""
            error = "Task timed out after 5 minutes"
        except Exception as e:
            status = "error"
            output = ""
            error = str(e)

        duration = (datetime.now() - start).total_seconds()

        # Log execution
        c.execute(
            """INSERT INTO task_executions (task_id, status, duration, output, error, created_at)
                     VALUES (?, ?, ?, ?, ?, ?)""",
            (task_id, status, duration, output, error, datetime.now().isoformat()),
        )

        # Update task
        next_run = calculate_next_run(schedule)
        run_count = task[9] + 1
        avg_duration = (task[10] * task[9] + duration) / run_count

        c.execute(
            """UPDATE maintenance_tasks 
                     SET last_run=?, next_run=?, run_count=?, avg_duration=?
                     WHERE id=?""",
            (datetime.now().isoformat(), next_run, run_count, avg_duration, task_id),
        )

        conn.commit()

        results.append({"task": name, "status": status, "duration": duration})

    conn.close()
    return results


def list_tasks(enabled_only=True):
    """List maintenance tasks"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if enabled_only:
        c.execute("SELECT * FROM maintenance_tasks WHERE enabled=1 ORDER BY next_run")
    else:
        c.execute("SELECT * FROM maintenance_tasks ORDER BY next_run")

    results = c.fetchall()
    conn.close()
    return results


# === CAPABILITIES ===
def register_capability(name, type, complexity=1, dependencies=None):
    """Register system capability"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()
    deps_json = json.dumps(dependencies) if dependencies else None

    try:
        c.execute(
            """INSERT INTO capabilities (name, type, complexity, dependencies, created_at, updated_at)
                     VALUES (?, ?, ?, ?, ?, ?)""",
            (name, type, complexity, deps_json, now, now),
        )
        conn.commit()
        cap_id = c.lastrowid
    except sqlite3.IntegrityError:
        cap_id = None
    finally:
        conn.close()
    return cap_id


def use_capability(name):
    """Track capability usage"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        "UPDATE capabilities SET usage_count = usage_count + 1, updated_at=? WHERE name=?",
        (datetime.now().isoformat(), name),
    )
    conn.commit()
    conn.close()


def list_capabilities(type=None):
    """List capabilities"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if type:
        c.execute("SELECT * FROM capabilities WHERE type=? ORDER BY complexity", (type,))
    else:
        c.execute("SELECT * FROM capabilities ORDER BY type, complexity")

    results = c.fetchall()
    conn.close()
    return results


def get_capability_map():
    """Get capability dependency map"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name, dependencies FROM capabilities")
    results = c.fetchall()
    conn.close()

    cap_map = {}
    for name, deps_json in results:
        deps = json.loads(deps_json) if deps_json else []
        cap_map[name] = deps

    return cap_map


# === COMPLEXITY MANAGEMENT ===
def record_complexity(component, metric_type, value, threshold=None):
    """Record complexity metric"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        """INSERT INTO complexity_metrics (component, metric_type, value, threshold, created_at)
                 VALUES (?, ?, ?, ?, ?)""",
        (component, metric_type, value, threshold, datetime.now().isoformat()),
    )

    conn.commit()
    conn.close()


def get_complexity_score():
    """Calculate overall complexity score"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Count capabilities
    c.execute("SELECT COUNT(*), SUM(complexity) FROM capabilities")
    cap_count, total_complexity = c.fetchone()

    # Count dependencies
    c.execute("SELECT dependencies FROM capabilities WHERE dependencies IS NOT NULL")
    deps = c.fetchall()
    total_deps = sum(len(json.loads(d[0])) for d in deps if d[0])

    # Count tools
    c.execute('SELECT COUNT(*) FROM tools WHERE status="active"')
    tool_count = c.fetchone()[0]

    # Count active sessions
    c.execute('SELECT COUNT(*) FROM sessions WHERE status="active"')
    session_count = c.fetchone()[0]

    conn.close()

    # Calculate score (higher = more complex)
    score = (cap_count * 2) + total_complexity + (total_deps * 3) + tool_count + session_count

    return {
        "score": score,
        "capabilities": cap_count,
        "total_complexity": total_complexity,
        "dependencies": total_deps,
        "tools": tool_count,
        "active_sessions": session_count,
        "level": "low" if score < 50 else "medium" if score < 150 else "high",
    }


def suggest_simplification():
    """Suggest ways to reduce complexity"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    suggestions = []

    # Check for unused capabilities
    c.execute("SELECT name FROM capabilities WHERE usage_count = 0")
    unused = c.fetchall()
    if unused:
        suggestions.append(
            {
                "type": "remove_unused",
                "message": f"Remove {len(unused)} unused capabilities",
                "impact": "medium",
                "items": [u[0] for u in unused],
            }
        )

    # Check for failing tools
    c.execute(
        """SELECT name FROM tools 
                 WHERE usage_count > 0 AND (failure_count * 1.0 / usage_count) > 0.5"""
    )
    failing = c.fetchall()
    if failing:
        suggestions.append(
            {
                "type": "fix_or_remove",
                "message": f"Fix or remove {len(failing)} failing tools",
                "impact": "high",
                "items": [f[0] for f in failing],
            }
        )

    # Check for old sessions
    cutoff = (datetime.now() - timedelta(days=7)).isoformat()
    c.execute(
        'SELECT COUNT(*) FROM sessions WHERE status="active" AND started_at < ?',
        (cutoff,),
    )
    old_sessions = c.fetchone()[0]
    if old_sessions > 0:
        suggestions.append(
            {
                "type": "cleanup",
                "message": f"Clean up {old_sessions} old sessions",
                "impact": "low",
            }
        )

    conn.close()
    return suggestions


# === UTILIZATION ===
def record_utilization(resource, used, total):
    """Record resource utilization"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    percent = (used / total * 100) if total > 0 else 0

    c.execute(
        """INSERT INTO utilization (resource, used, total, percent, created_at)
                 VALUES (?, ?, ?, ?, ?)""",
        (resource, used, total, percent, datetime.now().isoformat()),
    )

    conn.commit()
    conn.close()


def get_utilization_summary():
    """Get utilization summary"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Get latest for each resource
    c.execute(
        """SELECT resource, used, total, percent
                 FROM utilization
                 WHERE id IN (
                     SELECT MAX(id) FROM utilization GROUP BY resource
                 )"""
    )

    results = c.fetchall()
    conn.close()

    return [{"resource": r[0], "used": r[1], "total": r[2], "percent": r[3]} for r in results]


if __name__ == "__main__":
    import sys

    init_db()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  Task:       python maintenance_system.py task <add|list|run> ...")
        print("  Capability: python maintenance_system.py cap <register|list|map> ...")
        print("  Complexity: python maintenance_system.py complexity <score|suggest> ...")
        print("  Util:       python maintenance_system.py util <record|summary> ...")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "task":
        subcmd = sys.argv[2] if len(sys.argv) > 2 else None

        if subcmd == "add" and len(sys.argv) >= 6:
            desc = sys.argv[6] if len(sys.argv) > 6 else ""
            task_id = add_task(sys.argv[3], sys.argv[4], sys.argv[5], desc)
            print(f"Added task #{task_id}")

        elif subcmd == "list":
            tasks = list_tasks()
            print(f"\nMaintenance Tasks ({len(tasks)}):")
            for t in tasks:
                next_run = t[8][:16] if t[8] else "Not scheduled"
                print(f"  [{t[5]}] {t[1]} - {t[3]} (next: {next_run})")

        elif subcmd == "run":
            results = run_due_tasks()
            if results:
                print(f"\nRan {len(results)} tasks:")
                for r in results:
                    status_icon = "✓" if r["status"] == "success" else "✗"
                    print(f"  {status_icon} {r['task']} ({r['duration']:.2f}s)")
            else:
                print("No tasks due")

    elif cmd == "cap":
        subcmd = sys.argv[2] if len(sys.argv) > 2 else None

        if subcmd == "register" and len(sys.argv) >= 5:
            complexity = int(sys.argv[5]) if len(sys.argv) > 5 else 1
            cap_id = register_capability(sys.argv[3], sys.argv[4], complexity)
            print(f"Registered capability #{cap_id}")

        elif subcmd == "list":
            caps = list_capabilities()
            print(f"\nCapabilities ({len(caps)}):")
            for c in caps:
                print(f"  [{c[2]}] {c[1]} (complexity: {c[4]}, used: {c[7]}x)")

        elif subcmd == "map":
            cap_map = get_capability_map()
            print("\nCapability Dependencies:")
            for name, deps in cap_map.items():
                if deps:
                    print(f"  {name} → {', '.join(deps)}")

    elif cmd == "complexity":
        subcmd = sys.argv[2] if len(sys.argv) > 2 else None

        if subcmd == "score":
            score = get_complexity_score()
            print(f"\nComplexity Score: {score['score']} ({score['level'].upper()})")
            print(f"  Capabilities: {score['capabilities']}")
            print(f"  Total complexity: {score['total_complexity']}")
            print(f"  Dependencies: {score['dependencies']}")
            print(f"  Tools: {score['tools']}")
            print(f"  Active sessions: {score['active_sessions']}")

        elif subcmd == "suggest":
            suggestions = suggest_simplification()
            if suggestions:
                print(f"\nSimplification Suggestions ({len(suggestions)}):")
                for s in suggestions:
                    print(f"  [{s['impact']}] {s['message']}")
                    if "items" in s:
                        for item in s["items"][:3]:
                            print(f"    - {item}")
            else:
                print("No simplification needed")

    elif cmd == "util":
        subcmd = sys.argv[2] if len(sys.argv) > 2 else None

        if subcmd == "record" and len(sys.argv) >= 5:
            record_utilization(sys.argv[3], float(sys.argv[4]), float(sys.argv[5]))
            print(f"Recorded utilization for {sys.argv[3]}")

        elif subcmd == "summary":
            summary = get_utilization_summary()
            print("\nResource Utilization:")
            for u in summary:
                bar = "█" * int(u["percent"] / 5) + "░" * (20 - int(u["percent"] / 5))
                print(f"  {u['resource']:15} [{bar}] {u['percent']:.1f}%")
