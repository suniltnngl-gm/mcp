#!/usr/bin/env python3
"""Approval Tool: Human reviews and approves AI suggestions"""
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("/media/sunil-kr/workspace/workspace-system/workspace_knowledge.db")


def get_pending_suggestions(limit=20):
    """Get AI suggestions pending human review"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """SELECT s.id, s.idea_id, i.title, s.suggestion_type, 
                        s.suggestion, s.confidence, s.reasoning
        FROM ai_suggestions s
        JOIN ideas i ON s.idea_id = i.id
        WHERE s.accepted IS NULL
        ORDER BY s.confidence DESC
        LIMIT ?""",
        (limit,),
    )
    suggestions = c.fetchall()
    conn.close()
    return suggestions


def approve_suggestion(suggestion_id, idea_id, decision, feedback=""):
    """Record human approval/rejection"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Update suggestion
    accepted = 1 if decision == "approve" else 0
    c.execute(
        """UPDATE ai_suggestions
        SET accepted = ?, human_feedback = ?
        WHERE id = ?""",
        (accepted, feedback, suggestion_id),
    )

    # Update collaboration mode
    c.execute(
        """UPDATE collaboration_modes
        SET reviewed_by = 'human', reviewed_at = ?, decision = ?
        WHERE idea_id = ?""",
        (datetime.now().isoformat(), decision, idea_id),
    )

    conn.commit()
    conn.close()


def interactive_review():
    """Interactive review of AI suggestions"""
    suggestions = get_pending_suggestions()

    if not suggestions:
        print("\n✓ No pending suggestions to review")
        return

    print(f"\n{'='*70}")
    print(f"AI SUGGESTIONS REVIEW ({len(suggestions)} pending)")
    print(f"{'='*70}\n")

    approved = 0
    rejected = 0

    for i, (
        sugg_id,
        idea_id,
        title,
        sugg_type,
        suggestion,
        confidence,
        reasoning,
    ) in enumerate(suggestions, 1):
        print(f"\n[{i}/{len(suggestions)}] Idea #{idea_id}")
        print(f"Title: {title[:60]}")
        print("\n🤖 AI Suggestion:")
        print(f"   Type: {sugg_type}")
        print(f"   Action: {suggestion}")
        print(f"   Confidence: {confidence:.0%}")
        print(f"   Reasoning: {reasoning}")

        print("\n👤 Your decision:")
        print("   [a] Approve")
        print("   [r] Reject")
        print("   [s] Skip (decide later)")
        print("   [q] Quit review")

        choice = input("\nChoice: ").lower().strip()

        if choice == "a":
            feedback = input("Feedback (optional): ").strip()
            approve_suggestion(sugg_id, idea_id, "approved", feedback)
            print("✓ Approved")
            approved += 1

        elif choice == "r":
            feedback = input("Reason for rejection: ").strip()
            approve_suggestion(sugg_id, idea_id, "rejected", feedback)
            print("✗ Rejected")
            rejected += 1

        elif choice == "s":
            print("⊙ Skipped")
            continue

        elif choice == "q":
            break

    print(f"\n{'='*70}")
    print("Review Summary:")
    print(f"  Approved: {approved}")
    print(f"  Rejected: {rejected}")
    print(f"  Remaining: {len(suggestions) - approved - rejected}")
    print(f"{'='*70}\n")


def batch_approve(confidence_threshold=0.90):
    """Batch approve high-confidence suggestions"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        """SELECT id, idea_id FROM ai_suggestions
        WHERE accepted IS NULL AND confidence >= ?""",
        (confidence_threshold,),
    )
    suggestions = c.fetchall()

    for sugg_id, idea_id in suggestions:
        approve_suggestion(
            sugg_id,
            idea_id,
            "approved",
            f"Auto-approved (confidence >= {confidence_threshold:.0%})",
        )

    conn.close()

    print(f"✓ Batch approved {len(suggestions)} high-confidence suggestions")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  approve_suggestions.py interactive       - Interactive review")
        print("  approve_suggestions.py batch [threshold] - Batch approve (default: 0.90)")
        print("  approve_suggestions.py list              - List pending")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "interactive":
        interactive_review()

    elif cmd == "batch":
        threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 0.90
        batch_approve(threshold)

    elif cmd == "list":
        suggestions = get_pending_suggestions()
        print(f"\nPending Suggestions ({len(suggestions)} total):\n")
        for (
            sugg_id,
            idea_id,
            title,
            sugg_type,
            suggestion,
            confidence,
            reasoning,
        ) in suggestions:
            print(f"  #{idea_id:5} [{confidence:.0%}] {sugg_type:15} - {title[:40]}")
