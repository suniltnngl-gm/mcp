#!/usr/bin/env python3
"""Schema Manager: Single source of truth for all database tables"""
import sqlite3
from pathlib import Path

DB_PATH = Path("/media/sunil-kr/workspace/workspace-system/workspace_knowledge.db")

TABLES = {
    # Knowledge & Wiki
    "knowledge": """CREATE TABLE IF NOT EXISTS knowledge (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        tags TEXT,
        created_at TEXT NOT NULL
    )""",
    "wiki": """CREATE TABLE IF NOT EXISTS wiki (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL UNIQUE,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT
    )""",
    # Tasks & Progress
    "todos": """CREATE TABLE IF NOT EXISTS todos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'todo',
        priority TEXT DEFAULT 'medium',
        created_at TEXT NOT NULL
    )""",
    "progress": """CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT NOT NULL,
        status TEXT NOT NULL,
        notes TEXT,
        created_at TEXT NOT NULL
    )""",
    # Proposals & Reviews
    "proposals": """CREATE TABLE IF NOT EXISTS proposals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TEXT NOT NULL
    )""",
    "reviews": """CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        proposal_id INTEGER,
        status TEXT NOT NULL,
        score REAL,
        feedback TEXT,
        created_at TEXT NOT NULL
    )""",
    # Collaboration
    "users": """CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        role TEXT DEFAULT 'contributor',
        created_at TEXT NOT NULL
    )""",
    "discussions": """CREATE TABLE IF NOT EXISTS discussions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        created_by INTEGER,
        created_at TEXT NOT NULL
    )""",
    # Tools & Execution
    "tools": """CREATE TABLE IF NOT EXISTS tools (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        path TEXT NOT NULL,
        discovered_at TEXT NOT NULL
    )""",
    "tool_executions": """CREATE TABLE IF NOT EXISTS tool_executions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tool_id INTEGER,
        status TEXT NOT NULL,
        runtime REAL,
        executed_at TEXT NOT NULL
    )""",
    # Quality & Prevention
    "quality_gates": """CREATE TABLE IF NOT EXISTS quality_gates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        rules TEXT NOT NULL,
        created_at TEXT NOT NULL
    )""",
    "prevention_rules": """CREATE TABLE IF NOT EXISTS prevention_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        condition TEXT NOT NULL,
        action TEXT NOT NULL,
        created_at TEXT NOT NULL
    )""",
    # Automation
    "automated_tasks": """CREATE TABLE IF NOT EXISTS automated_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        command TEXT NOT NULL,
        schedule TEXT,
        last_run TEXT,
        created_at TEXT NOT NULL
    )""",
    # Health & Monitoring
    "health_checks": """CREATE TABLE IF NOT EXISTS health_checks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        status TEXT NOT NULL,
        data TEXT,
        checked_at TEXT NOT NULL
    )""",
    # Optimizations
    "optimizations": """CREATE TABLE IF NOT EXISTS optimizations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        issue TEXT NOT NULL,
        current_state TEXT,
        proposed_state TEXT,
        priority TEXT,
        created_at TEXT NOT NULL
    )""",
}


def init_all():
    """Initialize all tables"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    for name, sql in TABLES.items():
        c.execute(sql)

    conn.commit()
    conn.close()
    print(f"✓ Initialized {len(TABLES)} tables")


if __name__ == "__main__":
    init_all()
