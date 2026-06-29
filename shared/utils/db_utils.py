#!/usr/bin/env python3
"""Database Utilities: Centralized DB access and connection management"""
import sqlite3
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path("/media/sunil-kr/workspace/workspace-system/workspace_knowledge.db")


@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def execute(query, params=None):
    """Execute query and return results"""
    with get_db() as conn:
        c = conn.cursor()
        if params:
            c.execute(query, params)
        else:
            c.execute(query)
        return c.fetchall()


def execute_one(query, params=None):
    """Execute query and return single result"""
    results = execute(query, params)
    return results[0] if results else None


def insert(query, params):
    """Insert and return last row id"""
    with get_db() as conn:
        c = conn.cursor()
        c.execute(query, params)
        return c.lastrowid
