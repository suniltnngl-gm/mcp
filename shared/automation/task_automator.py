#!/usr/bin/env python3
"""Task Automator: Identify and automate manual tasks"""
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("/media/sunil-kr/workspace/workspace-system/workspace_knowledge.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS auto_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        command TEXT NOT NULL,
        schedule TEXT,
        frequency TEXT,
        last_run TEXT,
        run_count INTEGER DEFAULT 0,
        enabled INTEGER DEFAULT 1,
        created_at TEXT NOT NULL
    )"""
    )
    conn.commit()
    conn.close()


def add_task(name, description, command, schedule, frequency="daily"):
    """Add automated task"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """INSERT INTO auto_tasks 
        (name, description, command, schedule, frequency, created_at)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (name, description, command, schedule, frequency, datetime.now().isoformat()),
    )
    task_id = c.lastrowid
    conn.commit()
    conn.close()
    print(f"✓ Task #{task_id} added: {name}")
    return task_id


def list_tasks():
    """List all tasks"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """SELECT id, name, schedule, frequency, run_count, enabled 
        FROM auto_tasks ORDER BY enabled DESC, frequency"""
    )
    tasks = c.fetchall()
    conn.close()

    print(f"\n🤖 AUTOMATED TASKS ({len(tasks)} total)")
    print("-" * 80)
    for tid, name, schedule, freq, runs, enabled in tasks:
        status = "✓" if enabled else "✗"
        print(f"  {status} #{tid:2} {name:30} {freq:10} {schedule:15} ({runs} runs)")


def run_task(task_id):
    """Execute task"""
    import subprocess

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name, command FROM auto_tasks WHERE id = ?", (task_id,))
    row = c.fetchone()

    if not row:
        print(f"✗ Task #{task_id} not found")
        return False

    name, command = row
    print(f"Running: {name}")

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        success = result.returncode == 0

        c.execute(
            """UPDATE auto_tasks 
            SET last_run = ?, run_count = run_count + 1 
            WHERE id = ?""",
            (datetime.now().isoformat(), task_id),
        )
        conn.commit()

        if success:
            print("✓ Task completed")
        else:
            print(f"✗ Task failed: {result.stderr}")

        return success
    finally:
        conn.close()


def setup_default_tasks():
    """Setup recommended automated tasks"""
    tasks = [
        (
            "Daily Backup",
            "Backup database daily",
            "python3 backup_manager.py backup",
            "0 2 * * *",
            "daily",
        ),
        (
            "Hourly Health Check",
            "Monitor system health",
            "python3 health_monitor.py check",
            "0 * * * *",
            "hourly",
        ),
        (
            "Daily Report",
            "Generate daily report",
            "python3 automation_manager.py report daily",
            "0 9 * * *",
            "daily",
        ),
        (
            "Weekly Cleanup",
            "Clean old data",
            "python3 maintenance_system.py cleanup",
            "0 3 * * 0",
            "weekly",
        ),
        (
            "Quality Check",
            "Run quality gates",
            "python3 quality_gate.py check",
            "0 */6 * * *",
            "6-hourly",
        ),
    ]

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    for name, desc, cmd, sched, freq in tasks:
        c.execute("SELECT id FROM auto_tasks WHERE name = ?", (name,))
        if not c.fetchone():
            c.execute(
                """INSERT INTO auto_tasks 
                (name, description, command, schedule, frequency, created_at)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (name, desc, cmd, sched, freq, datetime.now().isoformat()),
            )
            print(f"✓ Added: {name}")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    import sys

    init_db()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  task_automator.py list           - List tasks")
        print("  task_automator.py setup          - Setup default tasks")
        print("  task_automator.py run <id>       - Run task")
        print("  task_automator.py add <name> <cmd> <schedule> - Add task")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "list":
        list_tasks()
    elif cmd == "setup":
        setup_default_tasks()
    elif cmd == "run" and len(sys.argv) > 2:
        run_task(int(sys.argv[2]))
    elif cmd == "add" and len(sys.argv) > 4:
        add_task(sys.argv[2], "", sys.argv[3], sys.argv[4])
    else:
        print("Invalid command")
