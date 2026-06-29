#!/usr/bin/env python3
"""Smart Workflow: Ideas → Proposals (Review) → Todos (Discussion) with flaw detection"""
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("/media/sunil-kr/workspace/workspace-system/workspace_knowledge.db")


class FlawDetector:
    """Detect flaws in proposals before conversion"""

    @staticmethod
    def check_proposal(title, description):
        """Check for common flaws"""
        flaws = []
        warnings = []

        # Check title
        if len(title) < 10:
            flaws.append("Title too short (< 10 chars)")
        if len(title) > 200:
            warnings.append("Title very long (> 200 chars)")

        # Check description
        if not description or len(description) < 20:
            flaws.append("Description missing or too short")

        # Check for vague language
        vague_words = ["maybe", "perhaps", "might", "could", "possibly"]
        if any(word in title.lower() for word in vague_words):
            warnings.append("Title contains vague language")

        # Check for missing context
        if "reality" not in description.lower() and "source" not in description.lower():
            warnings.append("Missing reality score or source context")

        # Check for duplicate indicators
        if "duplicate" in title.lower() or "duplicate" in description.lower():
            flaws.append("Marked as duplicate")

        # Check for test/mock indicators
        test_words = ["test", "mock", "demo", "example", "sample"]
        if any(word in title.lower() for word in test_words):
            warnings.append("Contains test/mock/demo indicators")

        return flaws, warnings


class WorkflowGate:
    """Enforce workflow gates - no bypassing"""

    @staticmethod
    def can_create_proposal_from_idea(idea_id):
        """Check if idea can become proposal"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Check idea exists and has good reality
        c.execute("SELECT reality_score, category FROM ideas WHERE id=?", (idea_id,))
        result = c.fetchone()

        if not result:
            return False, "Idea not found"

        reality, category = result

        if reality < 50:
            return False, f"Reality score too low ({reality}% < 50%)"

        # Check if already converted
        c.execute("SELECT id FROM proposals WHERE description LIKE ?", (f"%Idea #{idea_id}%",))
        if c.fetchone():
            return False, "Already converted to proposal"

        conn.close()
        return True, "OK"

    @staticmethod
    def can_convert_proposal_to_todo(proposal_id):
        """Check if proposal can become todo"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Check proposal exists
        c.execute(
            "SELECT status, title, description FROM proposals WHERE id=?",
            (proposal_id,),
        )
        result = c.fetchone()

        if not result:
            return False, "Proposal not found", []

        status, title, description = result

        # GATE 1: Must be reviewed
        if status not in ["approved", "validated"]:
            return (
                False,
                f"Proposal not approved (status: {status}). Review required!",
                [],
            )

        # GATE 2: Must have discussion
        c.execute("SELECT COUNT(*) FROM discussions WHERE title LIKE ?", (f"%{title[:30]}%",))
        discussion_count = c.fetchone()[0]

        if discussion_count == 0:
            return False, "No discussion found. Discussion required!", []

        # GATE 3: Check for flaws
        flaws, warnings = FlawDetector.check_proposal(title, description)

        if flaws:
            return False, f"Flaws detected: {', '.join(flaws)}", warnings

        # Check if already converted
        c.execute(
            "SELECT id FROM todos WHERE description LIKE ?",
            (f"%Proposal #{proposal_id}%",),
        )
        if c.fetchone():
            return False, "Already converted to todo", warnings

        conn.close()
        return True, "OK", warnings

    @staticmethod
    def require_review(proposal_id):
        """Mark proposal as requiring review"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE proposals SET status='needs_review' WHERE id=?", (proposal_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def require_discussion(proposal_id, title):
        """Create discussion if missing"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Check if discussion exists
        c.execute("SELECT id FROM discussions WHERE title LIKE ?", (f"%{title[:30]}%",))
        if c.fetchone():
            return False, "Discussion already exists"

        # Create discussion
        now = datetime.now().isoformat()
        disc_title = f"Discussion: {title[:60]}"
        c.execute(
            """INSERT INTO discussions (title, created_by, created_at, updated_at)
            VALUES (?, 1, ?, ?)""",
            (disc_title, now, now),
        )

        conn.commit()
        conn.close()
        return True, "Discussion created"


def create_proposal_from_idea(idea_id, force=False):
    """Create proposal from idea with gate checks"""

    # GATE CHECK
    if not force:
        can_create, reason = WorkflowGate.can_create_proposal_from_idea(idea_id)
        if not can_create:
            return False, reason, None

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Get idea details
    c.execute(
        "SELECT title, description, category, reality_score FROM ideas WHERE id=?",
        (idea_id,),
    )
    result = c.fetchone()

    if not result:
        conn.close()
        return False, "Idea not found", None

    title, desc, category, reality = result

    # Determine impact and effort
    if reality >= 95:
        impact, effort = "high", "low"
    elif reality >= 85:
        impact, effort = "medium", "medium"
    else:
        impact, effort = "low", "high"

    # Create proposal
    proposal_title = f"{category.title()}: {title[:60]}"
    proposal_desc = f"Reality: {reality}%\nSource: Idea #{idea_id}\n\n{desc or 'Auto-generated from extracted ideas'}"
    now = datetime.now().isoformat()

    # Check for flaws
    flaws, warnings = FlawDetector.check_proposal(proposal_title, proposal_desc)

    if flaws and not force:
        conn.close()
        return False, f"Flaws detected: {', '.join(flaws)}", warnings

    c.execute(
        """INSERT INTO proposals 
        (title, description, impact, effort, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, 'needs_review', ?, ?)""",
        (proposal_title, proposal_desc, impact, effort, now, now),
    )

    proposal_id = c.lastrowid

    # Auto-create discussion
    WorkflowGate.require_discussion(proposal_id, proposal_title)

    conn.commit()
    conn.close()

    return True, f"Proposal #{proposal_id} created (needs review)", warnings


def convert_proposal_to_todo(proposal_id, force=False):
    """Convert proposal to todo with gate checks"""

    # GATE CHECK
    if not force:
        can_convert, reason, warnings = WorkflowGate.can_convert_proposal_to_todo(proposal_id)
        if not can_convert:
            return False, reason, warnings

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Get proposal details
    c.execute("SELECT title, description, impact FROM proposals WHERE id=?", (proposal_id,))
    result = c.fetchone()

    if not result:
        conn.close()
        return False, "Proposal not found", []

    title, desc, impact = result

    # Determine priority from impact
    priority_map = {"high": "high", "medium": "medium", "low": "low"}
    priority = priority_map.get(impact, "medium")

    # Create todo
    todo_title = title[:100]
    todo_desc = f"From Proposal #{proposal_id}\n\n{desc}"
    now = datetime.now().isoformat()

    c.execute(
        """INSERT INTO todos (title, description, status, priority, created_at, updated_at)
        VALUES (?, ?, 'todo', ?, ?, ?)""",
        (todo_title, todo_desc, priority, now, now),
    )

    todo_id = c.lastrowid

    # Update proposal status
    c.execute("UPDATE proposals SET status='converted' WHERE id=?", (proposal_id,))

    conn.commit()
    conn.close()

    return True, f"Todo #{todo_id} created from proposal", []


def review_proposal(proposal_id, decision, feedback=""):
    """Review proposal - approve or reject"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if decision == "approve":
        status = "approved"
        score = 100
    elif decision == "reject":
        status = "rejected"
        score = 0
    else:
        status = "needs_revision"
        score = 50

    c.execute("UPDATE proposals SET status=? WHERE id=?", (status, proposal_id))

    # Log review
    c.execute(
        """INSERT INTO reviews (proposal_id, reviewer, decision, score, comments, created_at)
        VALUES (?, 'system', ?, ?, ?, ?)""",
        (proposal_id, decision, score, feedback, datetime.now().isoformat()),
    )

    conn.commit()
    conn.close()

    return True, f"Proposal #{proposal_id} {status}"


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  smart_workflow.py idea-to-proposal <idea_id>")
        print("  smart_workflow.py proposal-to-todo <proposal_id>")
        print("  smart_workflow.py review <proposal_id> <approve|reject|revise>")
        print("  smart_workflow.py check-proposal <proposal_id>")
        print("  smart_workflow.py check-idea <idea_id>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "idea-to-proposal" and len(sys.argv) > 2:
        idea_id = int(sys.argv[2])
        success, message, warnings = create_proposal_from_idea(idea_id)

        if success:
            print(f"✓ {message}")
            if warnings:
                print(f"⚠️  Warnings: {', '.join(warnings)}")
        else:
            print(f"✗ {message}")
            if warnings:
                print(f"⚠️  Warnings: {', '.join(warnings)}")

    elif cmd == "proposal-to-todo" and len(sys.argv) > 2:
        proposal_id = int(sys.argv[2])
        success, message, warnings = convert_proposal_to_todo(proposal_id)

        if success:
            print(f"✓ {message}")
            if warnings:
                print(f"⚠️  Warnings: {', '.join(warnings)}")
        else:
            print(f"✗ BLOCKED: {message}")
            if warnings:
                print(f"⚠️  Warnings: {', '.join(warnings)}")
            print("\nRequired steps:")
            print("  1. Review proposal: smart_workflow.py review <id> approve")
            print("  2. Ensure discussion exists")
            print("  3. Fix any flaws")

    elif cmd == "review" and len(sys.argv) > 3:
        proposal_id = int(sys.argv[2])
        decision = sys.argv[3]
        feedback = " ".join(sys.argv[4:]) if len(sys.argv) > 4 else ""

        success, message = review_proposal(proposal_id, decision, feedback)
        print(f"✓ {message}")

    elif cmd == "check-proposal" and len(sys.argv) > 2:
        proposal_id = int(sys.argv[2])
        can_convert, reason, warnings = WorkflowGate.can_convert_proposal_to_todo(proposal_id)

        if can_convert:
            print(f"✓ Proposal #{proposal_id} ready to convert")
        else:
            print(f"✗ Proposal #{proposal_id} NOT ready: {reason}")

        if warnings:
            print(f"⚠️  Warnings: {', '.join(warnings)}")

    elif cmd == "check-idea" and len(sys.argv) > 2:
        idea_id = int(sys.argv[2])
        can_create, reason = WorkflowGate.can_create_proposal_from_idea(idea_id)

        if can_create:
            print(f"✓ Idea #{idea_id} ready to become proposal")
        else:
            print(f"✗ Idea #{idea_id} NOT ready: {reason}")
