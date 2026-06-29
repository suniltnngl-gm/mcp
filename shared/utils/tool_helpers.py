#!/usr/bin/env python3
"""Tool Helpers: Discussion support, admin tools, and utilities"""
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("/media/sunil-kr/workspace/workspace-system/workspace_knowledge.db")


def init_db():
    """Initialize helper tables"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Discussion threads for reviews
    c.execute(
        """CREATE TABLE IF NOT EXISTS review_discussions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        review_id INTEGER NOT NULL,
        review_type TEXT NOT NULL,
        user TEXT NOT NULL,
        message TEXT NOT NULL,
        parent_id INTEGER,
        resolved BOOLEAN DEFAULT 0,
        created_at TEXT NOT NULL,
        FOREIGN KEY (parent_id) REFERENCES review_discussions(id)
    )"""
    )

    # Tool admin logs
    c.execute(
        """CREATE TABLE IF NOT EXISTS tool_admin_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_user TEXT NOT NULL,
        action TEXT NOT NULL,
        target_type TEXT NOT NULL,
        target_id INTEGER,
        details TEXT,
        created_at TEXT NOT NULL
    )"""
    )

    conn.commit()
    conn.close()


# Discussion Support
def add_discussion(review_id, review_type, user, message, parent_id=None):
    """Add discussion comment to review"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """INSERT INTO review_discussions 
                 (review_id, review_type, user, message, parent_id, created_at)
                 VALUES (?, ?, ?, ?, ?, ?)""",
        (review_id, review_type, user, message, parent_id, datetime.now().isoformat()),
    )
    discussion_id = c.lastrowid
    conn.commit()
    conn.close()
    return discussion_id


def get_discussions(review_id, review_type):
    """Get all discussions for a review"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """SELECT id, user, message, parent_id, resolved, created_at
                 FROM review_discussions
                 WHERE review_id = ? AND review_type = ?
                 ORDER BY created_at""",
        (review_id, review_type),
    )
    discussions = [
        {
            "id": r[0],
            "user": r[1],
            "message": r[2],
            "parent_id": r[3],
            "resolved": bool(r[4]),
            "created_at": r[5],
        }
        for r in c.fetchall()
    ]
    conn.close()
    return discussions


def resolve_discussion(discussion_id):
    """Mark discussion as resolved"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE review_discussions SET resolved = 1 WHERE id = ?", (discussion_id,))
    conn.commit()
    conn.close()


# Tool Administration
def admin_disable_tool(admin_user, tool_id, reason):
    """Disable a tool (admin action)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE tools SET status = ? WHERE id = ?", ("disabled", tool_id))
    c.execute(
        """INSERT INTO tool_admin_logs 
                 (admin_user, action, target_type, target_id, details, created_at)
                 VALUES (?, ?, ?, ?, ?, ?)""",
        (
            admin_user,
            "disable_tool",
            "tool",
            tool_id,
            reason,
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def admin_enable_tool(admin_user, tool_id):
    """Enable a tool (admin action)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE tools SET status = ? WHERE id = ?", ("active", tool_id))
    c.execute(
        """INSERT INTO tool_admin_logs 
                 (admin_user, action, target_type, target_id, details, created_at)
                 VALUES (?, ?, ?, ?, ?, ?)""",
        (admin_user, "enable_tool", "tool", tool_id, None, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def admin_reset_tool_stats(admin_user, tool_id):
    """Reset tool statistics (admin action)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """UPDATE tools 
                 SET usage_count = 0, success_count = 0, failure_count = 0, avg_runtime = 0
                 WHERE id = ?""",
        (tool_id,),
    )
    c.execute(
        """INSERT INTO tool_admin_logs 
                 (admin_user, action, target_type, target_id, details, created_at)
                 VALUES (?, ?, ?, ?, ?, ?)""",
        (admin_user, "reset_stats", "tool", tool_id, None, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_admin_logs(limit=50):
    """Get recent admin actions"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """SELECT admin_user, action, target_type, target_id, details, created_at
                 FROM tool_admin_logs
                 ORDER BY created_at DESC
                 LIMIT ?""",
        (limit,),
    )
    logs = [
        {
            "admin": r[0],
            "action": r[1],
            "target_type": r[2],
            "target_id": r[3],
            "details": r[4],
            "created_at": r[5],
        }
        for r in c.fetchall()
    ]
    conn.close()
    return logs


# Utility Helpers
def get_tool_health_summary():
    """Get summary of all tool health"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""SELECT COUNT(*), status FROM tools GROUP BY status""")
    status_counts = dict(c.fetchall())
    c.execute(
        """SELECT AVG(CAST(success_count AS FLOAT) / NULLIF(usage_count, 0) * 100)
                 FROM tools WHERE usage_count > 0"""
    )
    avg_success = c.fetchone()[0] or 0
    conn.close()
    return {"status_counts": status_counts, "avg_success_rate": round(avg_success, 2)}


def get_review_summary():
    """Get summary of all reviews"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*), status FROM code_reviews GROUP BY status")
    review_counts = dict(c.fetchall())
    c.execute("SELECT AVG(score) FROM code_reviews WHERE score IS NOT NULL")
    avg_score = c.fetchone()[0] or 0
    conn.close()
    return {"review_counts": review_counts, "avg_score": round(avg_score, 2)}


def cleanup_old_executions(days=30):
    """Clean up old tool execution logs"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    cutoff = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    cutoff = cutoff.replace(day=cutoff.day - days)
    c.execute("DELETE FROM tool_executions WHERE created_at < ?", (cutoff.isoformat(),))
    deleted = c.rowcount
    conn.commit()
    conn.close()
    return deleted


if __name__ == "__main__":
    init_db()
    print("✓ Tool helpers initialized")
