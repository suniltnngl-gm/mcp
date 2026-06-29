#!/usr/bin/env python3
"""Review Tools: Code review, proposal review, discussion support"""
import sqlite3
import json
import re
from datetime import datetime
from pathlib import Path

DB_PATH = Path("/media/sunil-kr/workspace/workspace-system/workspace_knowledge.db")


def init_db():
    """Initialize review tables"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Code reviews
    c.execute(
        """CREATE TABLE IF NOT EXISTS code_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT NOT NULL,
        reviewer TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        score INTEGER,
        findings TEXT,
        suggestions TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )"""
    )

    # Review comments
    c.execute(
        """CREATE TABLE IF NOT EXISTS review_comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        review_id INTEGER NOT NULL,
        review_type TEXT NOT NULL,
        line_number INTEGER,
        severity TEXT,
        category TEXT,
        message TEXT NOT NULL,
        suggestion TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (review_id) REFERENCES code_reviews(id)
    )"""
    )

    # Review templates
    c.execute(
        """CREATE TABLE IF NOT EXISTS review_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        type TEXT NOT NULL,
        checklist TEXT NOT NULL,
        created_at TEXT NOT NULL
    )"""
    )

    conn.commit()
    conn.close()


# === CODE REVIEW ===
def start_code_review(file_path, reviewer):
    """Start code review"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()

    c.execute(
        """INSERT INTO code_reviews (file_path, reviewer, created_at, updated_at)
                 VALUES (?, ?, ?, ?)""",
        (file_path, reviewer, now, now),
    )

    conn.commit()
    review_id = c.lastrowid
    conn.close()
    return review_id


def add_review_comment(
    review_id,
    review_type,
    message,
    line_number=None,
    severity="info",
    category="general",
    suggestion=None,
):
    """Add review comment"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()

    c.execute(
        """INSERT INTO review_comments 
                 (review_id, review_type, line_number, severity, category, message, suggestion, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            review_id,
            review_type,
            line_number,
            severity,
            category,
            message,
            suggestion,
            now,
        ),
    )

    conn.commit()
    conn.close()


def complete_review(review_id, status, score=None):
    """Complete review"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()

    # Get all comments
    c.execute("SELECT * FROM review_comments WHERE review_id=?", (review_id,))
    comments = c.fetchall()

    findings = {
        "critical": sum(1 for c in comments if c[4] == "critical"),
        "warning": sum(1 for c in comments if c[4] == "warning"),
        "info": sum(1 for c in comments if c[4] == "info"),
    }

    c.execute(
        """UPDATE code_reviews SET status=?, score=?, findings=?, updated_at=?
                 WHERE id=?""",
        (status, score, json.dumps(findings), now, review_id),
    )

    conn.commit()
    conn.close()


def get_review(review_id):
    """Get review with comments"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT * FROM code_reviews WHERE id=?", (review_id,))
    review = c.fetchone()

    c.execute(
        "SELECT * FROM review_comments WHERE review_id=? ORDER BY line_number, created_at",
        (review_id,),
    )
    comments = c.fetchall()

    conn.close()
    return review, comments


# === AUTO REVIEW ===
def auto_review_code(file_path):
    """Auto-review code file"""
    try:
        with open(file_path, "r") as f:
            content = f.read()
            lines = content.split("\n")
    except:
        return None

    review_id = start_code_review(file_path, "auto-reviewer")
    issues = []

    # Check 1: Long lines
    for i, line in enumerate(lines, 1):
        if len(line) > 120:
            add_review_comment(
                review_id,
                "code",
                f"Line too long ({len(line)} chars)",
                i,
                "warning",
                "style",
                "Consider breaking into multiple lines",
            )
            issues.append("long_line")

    # Check 2: TODO comments
    for i, line in enumerate(lines, 1):
        if "TODO" in line or "FIXME" in line:
            add_review_comment(review_id, "code", "Unresolved TODO/FIXME", i, "info", "maintenance")
            issues.append("todo")

    # Check 3: No docstrings (Python)
    if file_path.endswith(".py"):
        if not re.search(r'""".*?"""', content, re.DOTALL):
            add_review_comment(
                review_id,
                "code",
                "Missing module docstring",
                1,
                "warning",
                "documentation",
                "Add module-level docstring",
            )
            issues.append("no_docstring")

    # Check 4: Hardcoded credentials
    patterns = [r'password\s*=\s*["\']', r'api_key\s*=\s*["\']', r'secret\s*=\s*["\']']
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            line_num = content[: match.start()].count("\n") + 1
            add_review_comment(
                review_id,
                "code",
                "Possible hardcoded credential",
                line_num,
                "critical",
                "security",
                "Use environment variables or config files",
            )
            issues.append("hardcoded_cred")

    # Calculate score
    critical = sum(1 for i in issues if i == "hardcoded_cred")
    warnings = sum(1 for i in issues if i in ["long_line", "no_docstring"])
    score = max(0, 100 - (critical * 30) - (warnings * 5))

    status = "approved" if score >= 80 else "needs_changes" if score >= 60 else "rejected"
    complete_review(review_id, status, score)

    return review_id


# === PROPOSAL REVIEW ===
def review_proposal_quality(proposal_id):
    """Review proposal quality"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT * FROM proposals WHERE id=?", (proposal_id,))
    proposal = c.fetchone()
    conn.close()

    if not proposal:
        return None

    review_id = start_code_review(f"proposal:{proposal_id}", "auto-reviewer")
    score = 0

    # Check title
    if len(proposal[1]) < 10:
        add_review_comment(review_id, "proposal", "Title too short", None, "warning", "clarity")
    else:
        score += 20

    # Check description
    if len(proposal[2]) < 50:
        add_review_comment(
            review_id,
            "proposal",
            "Description too brief",
            None,
            "warning",
            "clarity",
            "Add more details about the proposal",
        )
    else:
        score += 30

    # Check rationale
    if not proposal[3] or len(proposal[3]) < 20:
        add_review_comment(
            review_id,
            "proposal",
            "Missing or weak rationale",
            None,
            "warning",
            "justification",
            "Explain why this is needed",
        )
    else:
        score += 30

    # Check impact/effort
    if proposal[4] and proposal[5]:
        score += 20

    status = "approved" if score >= 70 else "needs_changes"
    complete_review(review_id, status, score)

    return review_id, score


# === REVIEW TEMPLATES ===
def create_template(name, type, checklist):
    """Create review template"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()

    try:
        c.execute(
            "INSERT INTO review_templates (name, type, checklist, created_at) VALUES (?, ?, ?, ?)",
            (name, type, json.dumps(checklist), now),
        )
        conn.commit()
        template_id = c.lastrowid
    except sqlite3.IntegrityError:
        template_id = None
    finally:
        conn.close()
    return template_id


def get_template(name):
    """Get review template"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM review_templates WHERE name=?", (name,))
    result = c.fetchone()
    conn.close()
    return result


def list_templates(type=None):
    """List templates"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if type:
        c.execute("SELECT * FROM review_templates WHERE type=?", (type,))
    else:
        c.execute("SELECT * FROM review_templates")
    results = c.fetchall()
    conn.close()
    return results


if __name__ == "__main__":
    import sys

    init_db()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  Review:   python review_tools.py review <file_path>")
        print("  Proposal: python review_tools.py proposal <proposal_id>")
        print("  Show:     python review_tools.py show <review_id>")
        print("  Template: python review_tools.py template <create|list> ...")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "review" and len(sys.argv) >= 3:
        review_id = auto_review_code(sys.argv[2])
        if review_id:
            review, comments = get_review(review_id)
            print(f"\nReview #{review_id}: {review[1]}")
            print(f"Status: {review[3]}, Score: {review[4]}")
            print(f"\nFindings: {len(comments)}")
            for c in comments:
                severity_icon = "🔴" if c[4] == "critical" else "🟡" if c[4] == "warning" else "ℹ️"
                line_info = f"Line {c[3]}: " if c[3] else ""
                print(f"  {severity_icon} {line_info}{c[6]}")
                if c[7]:
                    print(f"     → {c[7]}")

    elif cmd == "proposal" and len(sys.argv) >= 3:
        result = review_proposal_quality(int(sys.argv[2]))
        if result:
            review_id, score = result
            review, comments = get_review(review_id)
            print(f"\nProposal Review: Score {score}/100")
            print(f"Status: {review[3]}\n")
            for c in comments:
                print(f"  • {c[6]}")
                if c[7]:
                    print(f"    → {c[7]}")

    elif cmd == "show" and len(sys.argv) >= 3:
        review, comments = get_review(int(sys.argv[2]))
        if review:
            print(f"\nReview #{review[0]}: {review[1]}")
            print(f"Reviewer: {review[2]}")
            print(f"Status: {review[3]}, Score: {review[4]}")
            print(f"\nComments ({len(comments)}):")
            for c in comments:
                print(f"  [{c[4]}] {c[6]}")

    elif cmd == "template":
        subcmd = sys.argv[2] if len(sys.argv) > 2 else None
        if subcmd == "create" and len(sys.argv) >= 5:
            checklist = json.loads(sys.argv[4])
            template_id = create_template(sys.argv[3], "code", checklist)
            print(f"Created template #{template_id}")
        elif subcmd == "list":
            templates = list_templates()
            for t in templates:
                print(f"{t[1]} ({t[2]})")
