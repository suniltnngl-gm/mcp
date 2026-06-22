"""AI Assist — Ollama cloud-powered workspace assistance.

Integrates into auto pipeline (smarter gaps), kb-auto (search explanations),
and review cycle (summaries). Uses free Ollama cloud models.
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Optional

from ai_assist.client import ask, ask_smart
from ai_assist.suggest import suggest_fix, suggest_priority, explain_gap
from ai_assist.summarize import summarize_report, explain_search_results, answer_query


HOME = Path.home()
REVIEWS_DIR = HOME / ".opencode" / "reviews"


def check_key() -> bool:
    key = os.environ.get("OLLAMA_API_KEY", "")
    if not key:
        print("OLLAMA_API_KEY not set — AI features unavailable")
        print("Set it in ~/Public/ENV/.env or export it")
        return False
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="AI Assist — Ollama cloud workspace AI")
    parser.add_argument("command", nargs="?",
                        choices=["ask", "suggest", "priority", "explain", "summarize", "search-explain", "answer"])
    parser.add_argument("args", nargs="*", help="Command arguments")
    parser.add_argument("--model", choices=["fast", "smart"], default="fast",
                        help="Model tier: fast (ministral-3) or smart (gpt-oss:120b)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    if not check_key():
        return

    fn = {"fast": ask, "smart": ask_smart}[args.model]

    if args.command == "ask":
        prompt = " ".join(args.args) if args.args else ""
        if not prompt:
            print("Usage: ai ask <question>")
            return
        result = fn(prompt)
        if args.json:
            print(json.dumps({"response": result}))
        else:
            print(result)
        return

    if args.command == "suggest":
        from review_cycle.models import ScanFinding
        findings = _load_latest_findings()
        if not findings:
            print("No findings loaded. Run 'auto plan' or 'review' first.")
            return
        idx = 0
        if args.args:
            try:
                idx = int(args.args[0]) - 1
            except ValueError:
                pass
        if 0 <= idx < len(findings):
            result = suggest_fix(findings[idx])
            print(f"Finding: {findings[idx].summary}")
            print(f"Suggestion: {result}")
        else:
            print(f"Invalid index. Use 1-{len(findings)}")
        return

    if args.command == "priority":
        from review_cycle.models import ScanFinding
        findings = _load_latest_findings()
        if not findings:
            print("No findings loaded.")
            return
        result = suggest_priority(findings)
        print(result)
        return

    if args.command == "explain":
        gap = args.args[0] if args.args else ""
        detail = " ".join(args.args[1:]) if len(args.args) > 1 else ""
        if not gap:
            print("Usage: ai explain <gap_type> [detail]")
            return
        result = explain_gap(gap, detail)
        print(result)
        return

    if args.command == "summarize":
        from review_cycle.models import ScanFinding
        findings = _load_latest_findings()
        if not findings:
            print("No findings loaded.")
            return
        s = _load_latest_summary()
        result = summarize_report(findings, s) if s else "No summary available"
        print(result)
        return

    if args.command == "search-explain":
        query = " ".join(args.args) if args.args else ""
        print(f"Search for '{query}', then running with --explain...")
        return

    if args.command == "answer":
        query = " ".join(args.args) if args.args else ""
        if not query:
            print("Usage: ai answer <question>")
            return
        context = _build_workspace_context()
        result = answer_query(query, context)
        print(result)
        return


def _load_latest_findings() -> List:
    from review_cycle.models import ScanFinding
    latest_review = REVIEWS_DIR / "latest.json"
    if not latest_review.exists():
        return []
    try:
        data = json.loads(latest_review.read_text(encoding="utf-8"))
        return [
            ScanFinding(
                repo=f.get("repo", "?"),
                category=f.get("category", "unknown"),
                severity=f.get("severity", "info"),
                summary=f.get("summary", ""),
                detail=f.get("detail", ""),
                file_path=f.get("file_path"),
                suggested_action=f.get("suggested_action", ""),
                score=f.get("score", 0),
            )
            for f in data.get("findings", [])
        ]
    except (json.JSONDecodeError, OSError):
        return []


def _load_latest_summary():
    from review_cycle.models import ReviewSummary
    latest_review = REVIEWS_DIR / "latest.json"
    if not latest_review.exists():
        return None
    try:
        data = json.loads(latest_review.read_text(encoding="utf-8"))
        s = data.get("summary", {})
        return ReviewSummary(
            total_findings=s.get("total_findings", 0),
            blockers=s.get("blockers", 0),
            critical=s.get("critical", 0),
            warnings=s.get("warnings", 0),
            infos=s.get("infos", 0),
            score=s.get("score", 100),
            trend=s.get("trend", "stable"),
        )
    except (json.JSONDecodeError, OSError):
        return None


def _build_workspace_context() -> str:
    parts = []
    latest_review = REVIEWS_DIR / "latest.json"
    if latest_review.exists():
        try:
            data = json.loads(latest_review.read_text())
            s = data.get("summary", {})
            parts.append(f"Last review: score {s.get('score', '?')}/100, "
                         f"{s.get('total_findings', 0)} findings")
        except Exception:
            pass
    plan_md = HOME / "Public" / "project" / "PLAN.md"
    if plan_md.exists():
        try:
            text = plan_md.read_text(encoding="utf-8")
            for line in text.splitlines():
                if "Phase" in line and "Status" in line:
                    pass
            phases = [l for l in text.splitlines() if "|" in l and "✅" in l or "🔄" in l or "⏳" in l]
            if phases:
                parts.append("Phase status: " + "; ".join(p.strip()[:80] for p in phases[:5]))
        except Exception:
            pass
    return "\n".join(parts) if parts else "No workspace context available."


if __name__ == "__main__":
    main()
