#!/usr/bin/env python3
"""Session Manager: Track context, conversations, and state between sessions"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path("/media/sunil-kr/workspace/workspace-system/workspace_knowledge.db")


def init_db():
    """Initialize session tables"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Sessions
    c.execute(
        """CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT NOT NULL,
        title TEXT,
        context TEXT,
        status TEXT DEFAULT 'active',
        started_at TEXT NOT NULL,
        ended_at TEXT
    )"""
    )

    # Session messages (conversation history)
    c.execute(
        """CREATE TABLE IF NOT EXISTS session_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        metadata TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (session_id) REFERENCES sessions(id)
    )"""
    )

    # Session state (key-value store per session)
    c.execute(
        """CREATE TABLE IF NOT EXISTS session_state (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        key TEXT NOT NULL,
        value TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (session_id) REFERENCES sessions(id),
        UNIQUE(session_id, key)
    )"""
    )

    # Session bookmarks (important moments)
    c.execute(
        """CREATE TABLE IF NOT EXISTS session_bookmarks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        message_id INTEGER,
        created_at TEXT NOT NULL,
        FOREIGN KEY (session_id) REFERENCES sessions(id),
        FOREIGN KEY (message_id) REFERENCES session_messages(id)
    )"""
    )

    conn.commit()
    conn.close()


# === SESSIONS ===
def start_session(user, title=None, context=None):
    """Start new session"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()

    if not title:
        title = f"Session {now[:10]}"

    context_json = json.dumps(context) if context else None

    c.execute(
        """INSERT INTO sessions (user, title, context, started_at)
                 VALUES (?, ?, ?, ?)""",
        (user, title, context_json, now),
    )

    conn.commit()
    session_id = c.lastrowid
    conn.close()
    return session_id


def end_session(session_id):
    """End session"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute(
        "UPDATE sessions SET status=?, ended_at=? WHERE id=?",
        ("ended", now, session_id),
    )
    conn.commit()
    conn.close()


def get_active_session(user):
    """Get user's active session"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT * FROM sessions WHERE user=? AND status=? ORDER BY started_at DESC LIMIT 1",
        (user, "active"),
    )
    result = c.fetchone()
    conn.close()
    return result


def list_sessions(user, limit=20):
    """List user sessions"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT * FROM sessions WHERE user=? ORDER BY started_at DESC LIMIT ?",
        (user, limit),
    )
    results = c.fetchall()
    conn.close()
    return results


def update_session_context(session_id, context):
    """Update session context"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    context_json = json.dumps(context)
    c.execute("UPDATE sessions SET context=? WHERE id=?", (context_json, session_id))
    conn.commit()
    conn.close()


# === MESSAGES ===
def add_message(session_id, role, content, metadata=None):
    """Add message to session"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()
    metadata_json = json.dumps(metadata) if metadata else None

    c.execute(
        """INSERT INTO session_messages (session_id, role, content, metadata, created_at)
                 VALUES (?, ?, ?, ?, ?)""",
        (session_id, role, content, metadata_json, now),
    )

    conn.commit()
    msg_id = c.lastrowid
    conn.close()
    return msg_id


def get_messages(session_id, limit=50):
    """Get session messages"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT * FROM session_messages WHERE session_id=? ORDER BY created_at DESC LIMIT ?",
        (session_id, limit),
    )
    results = c.fetchall()
    conn.close()
    return list(reversed(results))


def search_messages(user, query):
    """Search messages across sessions"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """SELECT sm.*, s.title FROM session_messages sm
                 JOIN sessions s ON sm.session_id = s.id
                 WHERE s.user=? AND sm.content LIKE ?
                 ORDER BY sm.created_at DESC LIMIT 50""",
        (user, f"%{query}%"),
    )
    results = c.fetchall()
    conn.close()
    return results


# === STATE ===
def set_state(session_id, key, value):
    """Set session state"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()
    value_json = json.dumps(value)

    c.execute(
        """INSERT OR REPLACE INTO session_state (session_id, key, value, updated_at)
                 VALUES (?, ?, ?, ?)""",
        (session_id, key, value_json, now),
    )

    conn.commit()
    conn.close()


def get_state(session_id, key):
    """Get session state"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT value FROM session_state WHERE session_id=? AND key=?",
        (session_id, key),
    )
    result = c.fetchone()
    conn.close()
    return json.loads(result[0]) if result else None


def get_all_state(session_id):
    """Get all session state"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT key, value FROM session_state WHERE session_id=?", (session_id,))
    results = c.fetchall()
    conn.close()
    return {k: json.loads(v) for k, v in results}


# === BOOKMARKS ===
def add_bookmark(session_id, title, description=None, message_id=None):
    """Bookmark important moment"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()

    c.execute(
        """INSERT INTO session_bookmarks (session_id, title, description, message_id, created_at)
                 VALUES (?, ?, ?, ?, ?)""",
        (session_id, title, description, message_id, now),
    )

    conn.commit()
    bookmark_id = c.lastrowid
    conn.close()
    return bookmark_id


def list_bookmarks(session_id):
    """List session bookmarks"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT * FROM session_bookmarks WHERE session_id=? ORDER BY created_at",
        (session_id,),
    )
    results = c.fetchall()
    conn.close()
    return results


# === SUMMARY ===
def get_session_summary(session_id):
    """Get session summary"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Session info
    c.execute("SELECT * FROM sessions WHERE id=?", (session_id,))
    session = c.fetchone()

    # Message count
    c.execute("SELECT COUNT(*) FROM session_messages WHERE session_id=?", (session_id,))
    msg_count = c.fetchone()[0]

    # Bookmarks
    c.execute("SELECT COUNT(*) FROM session_bookmarks WHERE session_id=?", (session_id,))
    bookmark_count = c.fetchone()[0]

    # State keys
    c.execute("SELECT COUNT(*) FROM session_state WHERE session_id=?", (session_id,))
    state_count = c.fetchone()[0]

    conn.close()

    return {
        "session": session,
        "messages": msg_count,
        "bookmarks": bookmark_count,
        "state_vars": state_count,
    }


def resume_session(user):
    """Resume last active session or create new one"""
    session = get_active_session(user)
    if session:
        return session[0], False  # session_id, is_new
    else:
        session_id = start_session(user)
        return session_id, True


if __name__ == "__main__":
    import sys

    init_db()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  Session:  python session_manager.py session <start|end|list|resume|summary> ...")
        print("  Message:  python session_manager.py msg <add|list|search> ...")
        print("  State:    python session_manager.py state <set|get|list> ...")
        print("  Bookmark: python session_manager.py bookmark <add|list> ...")
        sys.exit(1)

    module = sys.argv[1]
    cmd = sys.argv[2] if len(sys.argv) > 2 else None

    # === SESSION COMMANDS ===
    if module == "session":
        if cmd == "start" and len(sys.argv) >= 4:
            title = sys.argv[4] if len(sys.argv) > 4 else None
            session_id = start_session(sys.argv[3], title)
            print(f"Started session #{session_id}")

        elif cmd == "end" and len(sys.argv) >= 4:
            end_session(int(sys.argv[3]))
            print(f"Ended session #{sys.argv[3]}")

        elif cmd == "resume" and len(sys.argv) >= 4:
            session_id, is_new = resume_session(sys.argv[3])
            if is_new:
                print(f"Started new session #{session_id}")
            else:
                print(f"Resumed session #{session_id}")

        elif cmd == "list" and len(sys.argv) >= 4:
            sessions = list_sessions(sys.argv[3])
            print(f"\nSessions for {sys.argv[3]}:")
            for s in sessions:
                status = "🟢" if s[4] == "active" else "⚫"
                print(f"  {status} #{s[0]}: {s[2]} ({s[5][:10]})")

        elif cmd == "summary" and len(sys.argv) >= 4:
            summary = get_session_summary(int(sys.argv[3]))
            s = summary["session"]
            print(f"\nSession #{s[0]}: {s[2]}")
            print(f"User: {s[1]}")
            print(f"Status: {s[4]}")
            print(f"Started: {s[5]}")
            print(f"Messages: {summary['messages']}")
            print(f"Bookmarks: {summary['bookmarks']}")
            print(f"State vars: {summary['state_vars']}")

    # === MESSAGE COMMANDS ===
    elif module == "msg":
        if cmd == "add" and len(sys.argv) >= 6:
            msg_id = add_message(int(sys.argv[3]), sys.argv[4], sys.argv[5])
            print(f"Added message #{msg_id}")

        elif cmd == "list" and len(sys.argv) >= 4:
            messages = get_messages(int(sys.argv[3]))
            print(f"\nMessages ({len(messages)}):")
            for m in messages:
                print(f"  [{m[2]}] {m[3][:80]}")

        elif cmd == "search" and len(sys.argv) >= 5:
            results = search_messages(sys.argv[3], sys.argv[4])
            print(f"\nSearch results ({len(results)}):")
            for r in results:
                print(f"  Session: {r[6]}")
                print(f"  [{r[2]}] {r[3][:100]}\n")

    # === STATE COMMANDS ===
    elif module == "state":
        if cmd == "set" and len(sys.argv) >= 6:
            set_state(int(sys.argv[3]), sys.argv[4], sys.argv[5])
            print(f"Set {sys.argv[4]} = {sys.argv[5]}")

        elif cmd == "get" and len(sys.argv) >= 5:
            value = get_state(int(sys.argv[3]), sys.argv[4])
            print(f"{sys.argv[4]} = {value}")

        elif cmd == "list" and len(sys.argv) >= 4:
            state = get_all_state(int(sys.argv[3]))
            print("\nSession state:")
            for k, v in state.items():
                print(f"  {k} = {v}")

    # === BOOKMARK COMMANDS ===
    elif module == "bookmark":
        if cmd == "add" and len(sys.argv) >= 5:
            desc = sys.argv[5] if len(sys.argv) > 5 else None
            bookmark_id = add_bookmark(int(sys.argv[3]), sys.argv[4], desc)
            print(f"Added bookmark #{bookmark_id}")

        elif cmd == "list" and len(sys.argv) >= 4:
            bookmarks = list_bookmarks(int(sys.argv[3]))
            print("\nBookmarks:")
            for b in bookmarks:
                print(f"  📌 {b[2]}: {b[3] or 'No description'}")
