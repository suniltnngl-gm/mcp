#!/usr/bin/env python3
"""Workspace Manager: Wiki, Todos, Progress Tracking"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path("/media/sunil-kr/workspace/workspace-system/workspace_knowledge.db")


def init_db():
    """Initialize all tables"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Knowledge base (existing)
    c.execute(
        """CREATE TABLE IF NOT EXISTS knowledge (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        tags TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )"""
    )

    # Wiki pages
    c.execute(
        """CREATE TABLE IF NOT EXISTS wiki (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        parent_id INTEGER,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (parent_id) REFERENCES wiki(id)
    )"""
    )

    # Todos
    c.execute(
        """CREATE TABLE IF NOT EXISTS todos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'todo',
        priority TEXT DEFAULT 'medium',
        project TEXT,
        tags TEXT,
        due_date TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        completed_at TEXT
    )"""
    )

    # Progress tracking
    c.execute(
        """CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project TEXT NOT NULL,
        milestone TEXT NOT NULL,
        status TEXT DEFAULT 'not_started',
        progress INTEGER DEFAULT 0,
        notes TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )"""
    )

    # FTS for wiki
    c.execute(
        """CREATE VIRTUAL TABLE IF NOT EXISTS wiki_fts USING fts5(
        title, content, content=wiki, content_rowid=id
    )"""
    )

    conn.commit()
    conn.close()


# === WIKI ===
def wiki_create(path, title, content, parent_id=None):
    """Create wiki page"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()
    try:
        c.execute(
            """INSERT INTO wiki (path, title, content, parent_id, created_at, updated_at)
                     VALUES (?, ?, ?, ?, ?, ?)""",
            (path, title, content, parent_id, now, now),
        )
        conn.commit()
        page_id = c.lastrowid
    except sqlite3.IntegrityError:
        page_id = None
    finally:
        conn.close()
    return page_id


def wiki_get(path):
    """Get wiki page"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM wiki WHERE path = ?", (path,))
    result = c.fetchone()
    conn.close()
    return result


def wiki_update(path, content):
    """Update wiki page"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute(
        "UPDATE wiki SET content = ?, updated_at = ? WHERE path = ?",
        (content, now, path),
    )
    conn.commit()
    conn.close()


def wiki_list(parent_id=None):
    """List wiki pages"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if parent_id is None:
        c.execute("SELECT id, path, title FROM wiki WHERE parent_id IS NULL ORDER BY title")
    else:
        c.execute(
            "SELECT id, path, title FROM wiki WHERE parent_id = ? ORDER BY title",
            (parent_id,),
        )
    results = c.fetchall()
    conn.close()
    return results


def wiki_search(query):
    """Search wiki"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """SELECT w.id, w.path, w.title, w.content
                 FROM wiki w
                 JOIN wiki_fts ON w.id = wiki_fts.rowid
                 WHERE wiki_fts MATCH ?""",
        (query,),
    )
    results = c.fetchall()
    conn.close()
    return results


# === TODOS ===
def todo_add(title, description="", priority="medium", project=None, tags=None, due_date=None):
    """Add todo"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()
    tags_str = json.dumps(tags) if tags else None
    c.execute(
        """INSERT INTO todos (title, description, status, priority, project, tags, due_date, created_at, updated_at)
                 VALUES (?, ?, 'todo', ?, ?, ?, ?, ?, ?)""",
        (title, description, priority, project, tags_str, due_date, now, now),
    )
    conn.commit()
    todo_id = c.lastrowid
    conn.close()
    return todo_id


def todo_update(todo_id, status=None, priority=None):
    """Update todo status/priority"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()
    completed = now if status == "done" else None

    if status and priority:
        c.execute(
            "UPDATE todos SET status=?, priority=?, updated_at=?, completed_at=? WHERE id=?",
            (status, priority, now, completed, todo_id),
        )
    elif status:
        c.execute(
            "UPDATE todos SET status=?, updated_at=?, completed_at=? WHERE id=?",
            (status, now, completed, todo_id),
        )
    elif priority:
        c.execute(
            "UPDATE todos SET priority=?, updated_at=? WHERE id=?",
            (priority, now, todo_id),
        )

    conn.commit()
    conn.close()


def todo_list(status=None, project=None):
    """List todos"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if status and project:
        c.execute(
            "SELECT * FROM todos WHERE status=? AND project=? ORDER BY priority, created_at",
            (status, project),
        )
    elif status:
        c.execute(
            "SELECT * FROM todos WHERE status=? ORDER BY priority, created_at",
            (status,),
        )
    elif project:
        c.execute("SELECT * FROM todos WHERE project=? ORDER BY status, priority", (project,))
    else:
        c.execute("SELECT * FROM todos ORDER BY status, priority, created_at")

    results = c.fetchall()
    conn.close()
    return results


# === PROGRESS ===
def progress_add(project, milestone, status="not_started", progress=0, notes=""):
    """Add progress milestone"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute(
        """INSERT INTO progress (project, milestone, status, progress, notes, created_at, updated_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (project, milestone, status, progress, notes, now, now),
    )
    conn.commit()
    prog_id = c.lastrowid
    conn.close()
    return prog_id


def progress_update(prog_id, status=None, progress=None, notes=None):
    """Update progress"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()

    updates = []
    params = []
    if status:
        updates.append("status=?")
        params.append(status)
    if progress is not None:
        updates.append("progress=?")
        params.append(progress)
    if notes:
        updates.append("notes=?")
        params.append(notes)

    if updates:
        updates.append("updated_at=?")
        params.append(now)
        params.append(prog_id)
        c.execute(f'UPDATE progress SET {", ".join(updates)} WHERE id=?', params)
        conn.commit()

    conn.close()


def progress_list(project=None):
    """List progress"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if project:
        c.execute(
            "SELECT * FROM progress WHERE project=? ORDER BY updated_at DESC",
            (project,),
        )
    else:
        c.execute("SELECT * FROM progress ORDER BY project, updated_at DESC")
    results = c.fetchall()
    conn.close()
    return results


if __name__ == "__main__":
    import sys

    init_db()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  Wiki:     python workspace_manager.py wiki <create|get|list|search> ...")
        print("  Todo:     python workspace_manager.py todo <add|list|update> ...")
        print("  Progress: python workspace_manager.py progress <add|list|update> ...")
        sys.exit(1)

    module = sys.argv[1]
    cmd = sys.argv[2] if len(sys.argv) > 2 else None

    # === WIKI COMMANDS ===
    if module == "wiki":
        if cmd == "create" and len(sys.argv) >= 5:
            page_id = wiki_create(sys.argv[3], sys.argv[4], sys.argv[5])
            print(f"Created wiki page #{page_id}: {sys.argv[3]}")

        elif cmd == "get" and len(sys.argv) >= 4:
            page = wiki_get(sys.argv[3])
            if page:
                print(f"\n{page[2]}\n{'='*len(page[2])}\n{page[3]}")
            else:
                print("Page not found")

        elif cmd == "list":
            pages = wiki_list()
            for p in pages:
                print(f"{p[1]}: {p[2]}")

        elif cmd == "search" and len(sys.argv) >= 4:
            results = wiki_search(sys.argv[3])
            for r in results:
                print(f"\n{r[1]}: {r[2]}")

    # === TODO COMMANDS ===
    elif module == "todo":
        if cmd == "add" and len(sys.argv) >= 4:
            project = sys.argv[5] if len(sys.argv) > 5 else None
            todo_id = todo_add(
                sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "", project=project
            )
            print(f"Added todo #{todo_id}")

        elif cmd == "list":
            status = sys.argv[3] if len(sys.argv) > 3 else None
            todos = todo_list(status=status)
            for t in todos:
                print(f"[{t[3]}] #{t[0]}: {t[1]} ({t[4]})")

        elif cmd == "update" and len(sys.argv) >= 5:
            todo_update(int(sys.argv[3]), status=sys.argv[4])
            print(f"Updated todo #{sys.argv[3]}")

    # === PROGRESS COMMANDS ===
    elif module == "progress":
        if cmd == "add" and len(sys.argv) >= 5:
            prog_id = progress_add(sys.argv[3], sys.argv[4])
            print(f"Added progress #{prog_id}")

        elif cmd == "list":
            project = sys.argv[3] if len(sys.argv) > 3 else None
            progs = progress_list(project=project)
            for p in progs:
                print(f"{p[1]}: {p[2]} - {p[3]} ({p[4]}%)")

        elif cmd == "update" and len(sys.argv) >= 5:
            progress_update(int(sys.argv[3]), progress=int(sys.argv[4]))
            print(f"Updated progress #{sys.argv[3]}")
