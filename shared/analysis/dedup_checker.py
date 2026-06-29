#!/usr/bin/env python3
"""Deduplication Checker: Find similar items across all tables"""
import sqlite3
from difflib import SequenceMatcher
from pathlib import Path

DB_PATH = Path("/media/sunil-kr/workspace/workspace-system/workspace_knowledge.db")


def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_duplicates(title, threshold=0.8):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    sources = [
        ("ideas", "SELECT id, title FROM ideas"),
        ("proposals", "SELECT id, title FROM proposals"),
        ("todos", "SELECT id, title FROM todos"),
        ("wiki", "SELECT id, title FROM wiki"),
        ("knowledge", "SELECT id, title FROM knowledge"),
    ]

    duplicates = []
    for source, query in sources:
        try:
            c.execute(query)
            for row in c.fetchall():
                score = similarity(title, row[1])
                if score >= threshold:
                    duplicates.append((source, row[0], row[1], score))
        except:
            continue

    conn.close()
    return sorted(duplicates, key=lambda x: x[3], reverse=True)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: dedup_checker.py <title> [threshold]")
        print("  threshold: 0.0-1.0 (default: 0.8)")
        sys.exit(1)

    title = " ".join(
        sys.argv[1:-1]
        if len(sys.argv) > 2 and sys.argv[-1].replace(".", "").isdigit()
        else sys.argv[1:]
    )
    threshold = (
        float(sys.argv[-1])
        if len(sys.argv) > 2 and sys.argv[-1].replace(".", "").isdigit()
        else 0.8
    )

    dupes = find_duplicates(title, threshold)

    if dupes:
        print(f"⚠️  Found {len(dupes)} similar items (>={threshold:.0%}):")
        for source, id, text, score in dupes:
            print(f"  {score:.0%} - {source}#{id}: {text[:60]}")
        sys.exit(1)
    else:
        print("✓ No duplicates found")
        sys.exit(0)
