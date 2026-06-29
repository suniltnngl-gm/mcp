#!/usr/bin/env python3
"""Searchable Knowledge Base Manager"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path("/media/sunil-kr/workspace/workspace-system/workspace_knowledge.db")


def init_db():
    """Initialize knowledge base database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Main knowledge table
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

    # Full-text search index
    c.execute(
        """CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(
        title, content, tags, content=knowledge, content_rowid=id
    )"""
    )

    # Triggers to keep FTS in sync
    c.execute(
        """CREATE TRIGGER IF NOT EXISTS knowledge_ai AFTER INSERT ON knowledge BEGIN
        INSERT INTO knowledge_fts(rowid, title, content, tags) 
        VALUES (new.id, new.title, new.content, new.tags);
    END"""
    )

    c.execute(
        """CREATE TRIGGER IF NOT EXISTS knowledge_ad AFTER DELETE ON knowledge BEGIN
        DELETE FROM knowledge_fts WHERE rowid = old.id;
    END"""
    )

    c.execute(
        """CREATE TRIGGER IF NOT EXISTS knowledge_au AFTER UPDATE ON knowledge BEGIN
        UPDATE knowledge_fts SET title=new.title, content=new.content, tags=new.tags 
        WHERE rowid=new.id;
    END"""
    )

    conn.commit()
    conn.close()


def add_entry(category, title, content, tags=None):
    """Add knowledge entry"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()
    tags_str = json.dumps(tags) if tags else None

    c.execute(
        """INSERT INTO knowledge (category, title, content, tags, created_at, updated_at)
                 VALUES (?, ?, ?, ?, ?, ?)""",
        (category, title, content, tags_str, now, now),
    )

    conn.commit()
    entry_id = c.lastrowid
    conn.close()
    return entry_id


def search(query):
    """Full-text search"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        """SELECT k.id, k.category, k.title, k.content, k.tags, k.created_at
                 FROM knowledge k
                 JOIN knowledge_fts ON k.id = knowledge_fts.rowid
                 WHERE knowledge_fts MATCH ?
                 ORDER BY rank""",
        (query,),
    )

    results = c.fetchall()
    conn.close()
    return results


def get_by_category(category):
    """Get all entries in category"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT * FROM knowledge WHERE category = ? ORDER BY updated_at DESC",
        (category,),
    )
    results = c.fetchall()
    conn.close()
    return results


def list_categories():
    """List all categories"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT DISTINCT category FROM knowledge ORDER BY category")
    results = [r[0] for r in c.fetchall()]
    conn.close()
    return results


if __name__ == "__main__":
    import sys

    init_db()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  Add: python kb_manager.py add <category> <title> <content> [tags]")
        print("  Search: python kb_manager.py search <query>")
        print("  List: python kb_manager.py list [category]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "add" and len(sys.argv) >= 5:
        tags = sys.argv[5].split(",") if len(sys.argv) > 5 else None
        entry_id = add_entry(sys.argv[2], sys.argv[3], sys.argv[4], tags)
        print(f"Added entry #{entry_id}")

    elif cmd == "search" and len(sys.argv) >= 3:
        results = search(sys.argv[2])
        for r in results:
            print(f"\n[{r[1]}] {r[2]}")
            print(f"  {r[3][:200]}...")

    elif cmd == "list":
        if len(sys.argv) >= 3:
            results = get_by_category(sys.argv[2])
            for r in results:
                print(f"{r[0]}: {r[2]}")
        else:
            cats = list_categories()
            print("Categories:", ", ".join(cats))
