#!/usr/bin/env python3
"""
Wiki Manager - Search and view wiki entries from the database
"""
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path("workspace_knowledge.db")


def search_wiki(query):
    """Search wiki entries"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Search in title and content
    search_term = f"%{query}%"
    c.execute(
        """
        SELECT id, title, LENGTH(content) as content_len
        FROM wiki
        WHERE title LIKE ? OR content LIKE ?
        ORDER BY title
    """,
        (search_term, search_term),
    )

    results = c.fetchall()
    conn.close()

    return results


def get_wiki_entry(title):
    """Get full wiki entry by title"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        """
        SELECT id, title, content, created_at, updated_at
        FROM wiki
        WHERE title LIKE ?
    """,
        (f"%{title}%",),
    )

    result = c.fetchone()
    conn.close()

    return result


def list_all_wiki():
    """List all wiki entries"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        """
        SELECT id, title, LENGTH(content) as content_len
        FROM wiki
        ORDER BY title
    """
    )

    results = c.fetchall()
    conn.close()

    return results


def display_entry(entry):
    """Display a wiki entry"""
    if not entry:
        print("Entry not found")
        return

    id, title, content, created_at, updated_at = entry

    print(f"\n{'═' * 70}")
    print(f"📖 {title}")
    print(f"{'═' * 70}")
    print(f"ID: {id} | Created: {created_at} | Updated: {updated_at}")
    print(f"{'─' * 70}\n")
    print(content)
    print(f"\n{'═' * 70}\n")


def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print(
            """
📖 Wiki Manager
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Usage:
  python3 wiki_manager.py list              - List all entries
  python3 wiki_manager.py search <query>   - Search wiki
  python3 wiki_manager.py get <title>      - Get entry by title
  python3 wiki_manager.py stats            - Show wiki statistics

Examples:
  python3 wiki_manager.py list
  python3 wiki_manager.py search architecture
  python3 wiki_manager.py get "Quick Start"
  python3 wiki_manager.py stats
        """
        )
        return

    command = sys.argv[1].lower()

    if command == "list":
        entries = list_all_wiki()
        print(f"\n📖 Wiki Entries ({len(entries)} total)")
        print(f"{'─' * 70}")
        print(f"{'ID':3} {'Title':45} {'Size':10}")
        print(f"{'─' * 70}")
        for id, title, content_len in entries:
            print(f"{id:3} {title:45} {content_len:10}")
        print()

    elif command == "search":
        if len(sys.argv) < 3:
            print("Usage: python3 wiki_manager.py search <query>")
            return

        query = " ".join(sys.argv[2:])
        results = search_wiki(query)

        if results:
            print(f"\n🔍 Search Results for '{query}'")
            print(f"{'─' * 70}")
            print(f"{'ID':3} {'Title':45} {'Size':10}")
            print(f"{'─' * 70}")
            for id, title, content_len in results:
                print(f"{id:3} {title:45} {content_len:10}")
            print()
        else:
            print(f"No results found for '{query}'")

    elif command == "get":
        if len(sys.argv) < 3:
            print("Usage: python3 wiki_manager.py get <title>")
            return

        title = " ".join(sys.argv[2:])
        entry = get_wiki_entry(title)
        display_entry(entry)

    elif command == "stats":
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        c.execute("SELECT COUNT(*) FROM wiki")
        total_entries = c.fetchone()[0]

        c.execute("SELECT SUM(LENGTH(content)) FROM wiki")
        total_size = c.fetchone()[0] or 0

        c.execute(
            """
            SELECT 
                MIN(created_at) as oldest,
                MAX(updated_at) as newest
            FROM wiki
        """
        )
        oldest, newest = c.fetchone()

        conn.close()

        print(f"\n📊 Wiki Statistics")
        print(f"{'─' * 70}")
        print(f"  Total Entries: {total_entries}")
        print(f"  Total Size: {total_size / 1024:.1f} KB")
        print(f"  Average Entry: {total_size // total_entries:.0f} bytes")
        print(f"  Oldest Entry: {oldest}")
        print(f"  Newest Update: {newest}")
        print()

    else:
        print(f"Unknown command: {command}")
        print("Use 'python3 wiki_manager.py' for help")


if __name__ == "__main__":
    main()
