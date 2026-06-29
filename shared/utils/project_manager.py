#!/usr/bin/env python3
"""Project Manager: Manage user projects"""

import sqlite3
from pathlib import Path
from datetime import datetime
import subprocess
import json

DB_PATH = Path("/media/sunil-kr/workspace/workspace-system/workspace_knowledge.db")
PROJECTS_ROOT = Path("/media/sunil-kr/workspace/user-projects")


def init_project_tables():
    """Initialize project tracking tables"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        """CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        path TEXT NOT NULL,
        status TEXT DEFAULT 'active',
        description TEXT,
        created_at TEXT,
        updated_at TEXT
    )"""
    )

    c.execute(
        """CREATE TABLE IF NOT EXISTS project_stats (
        id INTEGER PRIMARY KEY,
        project_id INTEGER,
        files_count INTEGER,
        lines_count INTEGER,
        py_files INTEGER,
        has_git BOOLEAN,
        has_tests BOOLEAN,
        last_commit TEXT,
        measured_at TEXT,
        FOREIGN KEY (project_id) REFERENCES projects(id)
    )"""
    )

    conn.commit()
    conn.close()


def register_project(name, path, description=None):
    """Register a project"""
    init_project_tables()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    now = datetime.now().isoformat()
    path_str = str(Path(path).resolve())

    try:
        c.execute(
            """INSERT INTO projects (name, path, description, created_at, updated_at)
                     VALUES (?, ?, ?, ?, ?)""",
            (name, path_str, description, now, now),
        )
        conn.commit()
        project_id = c.lastrowid
        conn.close()
        return project_id
    except sqlite3.IntegrityError:
        conn.close()
        return None


def list_projects(status=None):
    """List all projects"""
    init_project_tables()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if status:
        c.execute("SELECT * FROM projects WHERE status = ? ORDER BY name", (status,))
    else:
        c.execute("SELECT * FROM projects ORDER BY name")

    projects = c.fetchall()
    conn.close()
    return projects


def get_project(name):
    """Get project by name"""
    init_project_tables()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT * FROM projects WHERE name = ?", (name,))
    project = c.fetchone()
    conn.close()
    return project


def analyze_project(project_path):
    """Analyze project structure and stats"""
    path = Path(project_path)
    if not path.exists():
        return None

    stats = {
        "path": str(path),
        "exists": True,
        "files_count": 0,
        "lines_count": 0,
        "py_files": 0,
        "has_git": (path / ".git").exists(),
        "has_tests": (path / "tests").exists() or (path / "test").exists(),
        "has_venv": (path / ".venv").exists() or (path / "venv").exists(),
        "has_requirements": (path / "requirements.txt").exists(),
        "has_readme": (path / "README.md").exists(),
        "last_commit": None,
    }

    # Count files
    try:
        py_files = list(path.rglob("*.py"))
        stats["py_files"] = len(py_files)
        stats["files_count"] = len(list(path.rglob("*")))

        # Count lines in Python files
        total_lines = 0
        for py_file in py_files:
            try:
                with open(py_file) as f:
                    total_lines += len(f.readlines())
            except Exception:
                pass
        stats["lines_count"] = total_lines
    except Exception:
        pass

    # Get last commit
    if stats["has_git"]:
        try:
            result = subprocess.run(
                ["git", "-C", str(path), "log", "-1", "--format=%ci"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                stats["last_commit"] = result.stdout.strip()
        except Exception:
            pass

    return stats


def save_project_stats(project_id, stats):
    """Save project statistics"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    now = datetime.now().isoformat()

    c.execute(
        """INSERT INTO project_stats 
               (project_id, files_count, lines_count, py_files, has_git, has_tests, last_commit, measured_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            project_id,
            stats["files_count"],
            stats["lines_count"],
            stats["py_files"],
            stats["has_git"],
            stats["has_tests"],
            stats.get("last_commit"),
            now,
        ),
    )

    conn.commit()
    conn.close()


def update_project_status(name, status):
    """Update project status"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    now = datetime.now().isoformat()
    c.execute(
        "UPDATE projects SET status = ?, updated_at = ? WHERE name = ?",
        (status, now, name),
    )

    conn.commit()
    conn.close()


def scan_projects_directory():
    """Scan projects directory and register found projects"""
    discovered = []

    # Scan current projects
    current_dir = PROJECTS_ROOT / "current"
    if current_dir.exists():
        for item in current_dir.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                discovered.append({"name": item.name, "path": str(item), "status": "active"})

    # Scan archived projects
    archive_dir = PROJECTS_ROOT / "archive"
    if archive_dir.exists():
        for item in archive_dir.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                discovered.append(
                    {
                        "name": f"{item.name}-archive",
                        "path": str(item),
                        "status": "archived",
                    }
                )

    return discovered


def project_summary():
    """Get project summary"""
    projects = list_projects()
    active = [p for p in projects if p[3] == "active"]
    archived = [p for p in projects if p[3] == "archived"]

    return {
        "total": len(projects),
        "active": len(active),
        "archived": len(archived),
        "projects": projects,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: project_manager.py <command> [args]")
        print("\nCommands:")
        print("  scan              - Scan and discover projects")
        print("  list [status]     - List projects")
        print("  register <name> <path> [desc] - Register project")
        print("  analyze <name>    - Analyze project")
        print("  status <name> <status> - Update status")
        print("  summary           - Show summary")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "scan":
        discovered = scan_projects_directory()
        print(f"Found {len(discovered)} projects:")
        for proj in discovered:
            print(f"  - {proj['name']} ({proj['status']})")
            print(f"    {proj['path']}")

    elif cmd == "list":
        status = sys.argv[2] if len(sys.argv) > 2 else None
        projects = list_projects(status)
        for p in projects:
            print(f"[{p[3]}] {p[1]}")
            print(f"  Path: {p[2]}")
            if p[4]:
                print(f"  Desc: {p[4]}")

    elif cmd == "register" and len(sys.argv) >= 4:
        name = sys.argv[2]
        path = sys.argv[3]
        desc = sys.argv[4] if len(sys.argv) > 4 else None
        project_id = register_project(name, path, desc)
        if project_id:
            print(f"✓ Registered project '{name}' (ID: {project_id})")
        else:
            print(f"✗ Project '{name}' already exists")

    elif cmd == "analyze" and len(sys.argv) >= 3:
        name = sys.argv[2]
        project = get_project(name)
        if project:
            stats = analyze_project(project[2])
            if stats:
                print(f"\n📊 Project: {name}")
                print(f"Path: {stats['path']}")
                print(f"Files: {stats['files_count']}")
                print(f"Python files: {stats['py_files']}")
                print(f"Lines of code: {stats['lines_count']:,}")
                print(f"Git: {'✓' if stats['has_git'] else '✗'}")
                print(f"Tests: {'✓' if stats['has_tests'] else '✗'}")
                print(f"Venv: {'✓' if stats['has_venv'] else '✗'}")
                print(f"Requirements: {'✓' if stats['has_requirements'] else '✗'}")
                if stats["last_commit"]:
                    print(f"Last commit: {stats['last_commit']}")

                save_project_stats(project[0], stats)
                print("\n✓ Stats saved")
        else:
            print(f"✗ Project '{name}' not found")

    elif cmd == "status" and len(sys.argv) >= 4:
        name = sys.argv[2]
        status = sys.argv[3]
        update_project_status(name, status)
        print(f"✓ Updated '{name}' status to '{status}'")

    elif cmd == "summary":
        summary = project_summary()
        print("\n📊 Projects Summary")
        print(f"Total: {summary['total']}")
        print(f"Active: {summary['active']}")
        print(f"Archived: {summary['archived']}")
