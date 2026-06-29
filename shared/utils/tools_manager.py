#!/usr/bin/env python3
"""Tools Manager: Register, discover, and manage tools with self-improvement"""
import sqlite3
import json
import subprocess
from datetime import datetime
from pathlib import Path

DB_PATH = Path("/media/sunil-kr/workspace/workspace-system/workspace_knowledge.db")


def init_db():
    """Initialize tools tables"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Tools registry
    c.execute(
        """CREATE TABLE IF NOT EXISTS tools (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        type TEXT NOT NULL,
        description TEXT,
        command TEXT NOT NULL,
        category TEXT,
        version TEXT,
        status TEXT DEFAULT 'active',
        usage_count INTEGER DEFAULT 0,
        success_count INTEGER DEFAULT 0,
        failure_count INTEGER DEFAULT 0,
        avg_runtime REAL DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )"""
    )

    # Tool executions (audit log)
    c.execute(
        """CREATE TABLE IF NOT EXISTS tool_executions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tool_id INTEGER NOT NULL,
        user TEXT,
        args TEXT,
        result TEXT,
        status TEXT,
        runtime REAL,
        error TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (tool_id) REFERENCES tools(id)
    )"""
    )

    # Tool improvements
    c.execute(
        """CREATE TABLE IF NOT EXISTS tool_improvements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tool_id INTEGER,
        type TEXT NOT NULL,
        description TEXT NOT NULL,
        impact TEXT,
        status TEXT DEFAULT 'proposed',
        implemented_at TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (tool_id) REFERENCES tools(id)
    )"""
    )

    # Health checks
    c.execute(
        """CREATE TABLE IF NOT EXISTS health_checks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        component TEXT NOT NULL,
        status TEXT NOT NULL,
        message TEXT,
        details TEXT,
        created_at TEXT NOT NULL
    )"""
    )

    conn.commit()
    conn.close()


# === TOOL REGISTRY ===
def register_tool(name, type, command, description="", category="general", version="1.0"):
    """Register a tool"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()

    try:
        c.execute(
            """INSERT INTO tools (name, type, description, command, category, version, created_at, updated_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, type, description, command, category, version, now, now),
        )
        conn.commit()
        tool_id = c.lastrowid
    except sqlite3.IntegrityError:
        tool_id = None
    finally:
        conn.close()
    return tool_id


def list_tools(category=None, status="active"):
    """List tools"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if category:
        c.execute(
            "SELECT * FROM tools WHERE category=? AND status=? ORDER BY name",
            (category, status),
        )
    else:
        c.execute("SELECT * FROM tools WHERE status=? ORDER BY category, name", (status,))

    results = c.fetchall()
    conn.close()
    return results


def get_tool(name):
    """Get tool by name"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM tools WHERE name=?", (name,))
    result = c.fetchone()
    conn.close()
    return result


def update_tool_stats(tool_id, success, runtime):
    """Update tool statistics"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        "SELECT usage_count, success_count, failure_count, avg_runtime FROM tools WHERE id=?",
        (tool_id,),
    )
    stats = c.fetchone()

    usage = stats[0] + 1
    success_count = stats[1] + (1 if success else 0)
    failure_count = stats[2] + (0 if success else 1)
    avg_runtime = (stats[3] * stats[0] + runtime) / usage

    c.execute(
        """UPDATE tools SET usage_count=?, success_count=?, failure_count=?, avg_runtime=?, updated_at=?
                 WHERE id=?""",
        (
            usage,
            success_count,
            failure_count,
            avg_runtime,
            datetime.now().isoformat(),
            tool_id,
        ),
    )

    conn.commit()
    conn.close()


# === TOOL EXECUTION ===
def execute_tool(name, args=None, user=None):
    """Execute a tool"""
    tool = get_tool(name)
    if not tool:
        return {"success": False, "error": "Tool not found"}

    tool_id = tool[0]
    command = tool[4]

    # Build command
    if args:
        full_command = f"{command} {args}"
    else:
        full_command = command

    # Execute
    start = datetime.now()
    try:
        result = subprocess.run(
            full_command, shell=True, capture_output=True, text=True, timeout=30
        )
        success = result.returncode == 0
        output = result.stdout if success else result.stderr
        error = None if success else result.stderr
    except subprocess.TimeoutExpired:
        success = False
        output = ""
        error = "Timeout"
    except Exception as e:
        success = False
        output = ""
        error = str(e)

    runtime = (datetime.now() - start).total_seconds()

    # Log execution
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """INSERT INTO tool_executions (tool_id, user, args, result, status, runtime, error, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            tool_id,
            user,
            args,
            output[:1000],
            "success" if success else "failure",
            runtime,
            error,
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    conn.close()

    # Update stats
    update_tool_stats(tool_id, success, runtime)

    return {"success": success, "output": output, "error": error, "runtime": runtime}


def get_tool_stats(name):
    """Get tool statistics"""
    tool = get_tool(name)
    if not tool:
        return None

    return {
        "name": tool[1],
        "usage_count": tool[8],
        "success_count": tool[9],
        "failure_count": tool[10],
        "success_rate": round(tool[9] / tool[8] * 100, 1) if tool[8] > 0 else 0,
        "avg_runtime": round(tool[11], 3),
    }


# === SELF-IMPROVEMENT ===
def propose_improvement(tool_id, type, description, impact="medium"):
    """Propose tool improvement"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()

    c.execute(
        """INSERT INTO tool_improvements (tool_id, type, description, impact, created_at)
                 VALUES (?, ?, ?, ?, ?)""",
        (tool_id, type, description, impact, now),
    )

    conn.commit()
    improvement_id = c.lastrowid
    conn.close()
    return improvement_id


def list_improvements(status=None):
    """List improvements"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if status:
        c.execute(
            """SELECT i.*, t.name FROM tool_improvements i
                     LEFT JOIN tools t ON i.tool_id = t.id
                     WHERE i.status=? ORDER BY i.created_at DESC""",
            (status,),
        )
    else:
        c.execute(
            """SELECT i.*, t.name FROM tool_improvements i
                     LEFT JOIN tools t ON i.tool_id = t.id
                     ORDER BY i.status, i.created_at DESC"""
        )

    results = c.fetchall()
    conn.close()
    return results


def implement_improvement(improvement_id):
    """Mark improvement as implemented"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute(
        "UPDATE tool_improvements SET status=?, implemented_at=? WHERE id=?",
        ("implemented", now, improvement_id),
    )
    conn.commit()
    conn.close()


# === HEALTH CHECKS ===
def run_health_check(component, check_func):
    """Run health check"""
    start = datetime.now()
    try:
        result = check_func()
        status = "healthy" if result.get("success") else "unhealthy"
        message = result.get("message", "")
        details = json.dumps(result.get("details", {}))
    except Exception as e:
        status = "error"
        message = str(e)
        details = "{}"

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """INSERT INTO health_checks (component, status, message, details, created_at)
                 VALUES (?, ?, ?, ?, ?)""",
        (component, status, message, details, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()

    return {"component": component, "status": status, "message": message}


def get_health_status():
    """Get overall health status"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Get latest check for each component
    c.execute(
        """SELECT component, status, message, created_at
                 FROM health_checks
                 WHERE id IN (
                     SELECT MAX(id) FROM health_checks GROUP BY component
                 )
                 ORDER BY component"""
    )

    results = c.fetchall()
    conn.close()

    healthy = sum(1 for r in results if r[1] == "healthy")
    total = len(results)

    return {
        "overall": ("healthy" if healthy == total else "degraded" if healthy > 0 else "unhealthy"),
        "components": results,
        "healthy_count": healthy,
        "total_count": total,
    }


# === AUTO-DISCOVERY ===
def discover_tools():
    """Auto-discover tools in workspace"""
    workspace = Path(__file__).parent
    discovered = []

    # Python scripts
    for py_file in workspace.glob("*.py"):
        if py_file.name not in ["tools_manager.py", "__init__.py"]:
            name = py_file.stem
            if not get_tool(name):
                tool_id = register_tool(
                    name=name,
                    type="python",
                    command=f"python3 {py_file}",
                    description=f"Auto-discovered: {name}",
                    category="auto-discovered",
                )
                if tool_id:
                    discovered.append(name)

    # Shell scripts
    for sh_file in workspace.glob("*.sh"):
        name = sh_file.stem
        if not get_tool(name):
            tool_id = register_tool(
                name=name,
                type="shell",
                command=f"bash {sh_file}",
                description=f"Auto-discovered: {name}",
                category="auto-discovered",
            )
            if tool_id:
                discovered.append(name)

    return discovered


if __name__ == "__main__":
    import sys

    init_db()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  Tool:    python tools_manager.py tool <register|list|stats|execute> ...")
        print("  Improve: python tools_manager.py improve <propose|list|implement> ...")
        print("  Health:  python tools_manager.py health <check|status> ...")
        print("  Discover: python tools_manager.py discover")
        sys.exit(1)

    module = sys.argv[1]
    cmd = sys.argv[2] if len(sys.argv) > 2 else None

    # === TOOL COMMANDS ===
    if module == "tool":
        if cmd == "register" and len(sys.argv) >= 6:
            tool_id = register_tool(
                sys.argv[3],
                sys.argv[4],
                sys.argv[5],
                sys.argv[6] if len(sys.argv) > 6 else "",
            )
            print(f"Registered tool #{tool_id}: {sys.argv[3]}")

        elif cmd == "list":
            category = sys.argv[3] if len(sys.argv) > 3 else None
            tools = list_tools(category)
            print(f"\nTools ({len(tools)}):")
            for t in tools:
                print(f"  [{t[5]}] {t[1]} ({t[2]}) - {t[8]} uses, {t[9]}/{t[10]} success/fail")

        elif cmd == "stats" and len(sys.argv) >= 4:
            stats = get_tool_stats(sys.argv[3])
            if stats:
                print(f"\n{stats['name']} Statistics:")
                print(f"  Usage: {stats['usage_count']}")
                print(f"  Success: {stats['success_count']} ({stats['success_rate']}%)")
                print(f"  Failures: {stats['failure_count']}")
                print(f"  Avg Runtime: {stats['avg_runtime']}s")

        elif cmd == "execute" and len(sys.argv) >= 4:
            args = sys.argv[4] if len(sys.argv) > 4 else None
            result = execute_tool(sys.argv[3], args)
            if result["success"]:
                print(f"✓ Success ({result['runtime']:.2f}s)")
                print(result["output"])
            else:
                print(f"✗ Failed ({result['runtime']:.2f}s)")
                print(result["error"])

    # === IMPROVEMENT COMMANDS ===
    elif module == "improve":
        if cmd == "propose" and len(sys.argv) >= 5:
            tool = get_tool(sys.argv[3])
            if tool:
                imp_id = propose_improvement(tool[0], sys.argv[4], sys.argv[5])
                print(f"Proposed improvement #{imp_id}")

        elif cmd == "list":
            status = sys.argv[3] if len(sys.argv) > 3 else None
            improvements = list_improvements(status)
            print(f"\nImprovements ({len(improvements)}):")
            for i in improvements:
                print(f"  [{i[5]}] #{i[0]}: {i[7] or 'System'} - {i[2]} ({i[3]})")

        elif cmd == "implement" and len(sys.argv) >= 4:
            implement_improvement(int(sys.argv[3]))
            print(f"Implemented improvement #{sys.argv[3]}")

    # === HEALTH COMMANDS ===
    elif module == "health":
        if cmd == "status":
            health = get_health_status()
            print(f"\nSystem Health: {health['overall'].upper()}")
            print(f"Components: {health['healthy_count']}/{health['total_count']} healthy\n")
            for c in health["components"]:
                status_icon = "✓" if c[1] == "healthy" else "✗"
                print(f"  {status_icon} {c[0]}: {c[1]} - {c[2]}")

    # === DISCOVERY ===
    elif module == "discover":
        discovered = discover_tools()
        print(f"Discovered {len(discovered)} tools:")
        for name in discovered:
            print(f"  + {name}")
