"""Auto pipeline — detect gaps, fix trivial ones, rebuild KB, report."""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from autofix.fixers import get_fixer, list_fixable_categories
from autofix.gaps import (
    scan_docs_gaps,
    scan_env_gaps,
    scan_orphaned_files,
    scan_test_gaps,
    scan_tracking_gaps,
)
from brain import LessonCache
from review_cycle.main import run_review, _persist_report
from review_cycle.models import ReviewReport, ReviewSummary, ScanFinding


HOME = Path.home()


def run_auto_pipeline(
    apply: bool = False,
    scanners: Optional[List[str]] = None,
    skip_kb_rebuild: bool = False,
) -> ReviewReport:
    findings: List[ScanFinding] = []
    gap_scanners = {
        "docs": scan_docs_gaps,
        "env": scan_env_gaps,
        "tracking": scan_tracking_gaps,
        "orphans": scan_orphaned_files,
        "tests_gaps": scan_test_gaps,
    }
    active_gaps = scanners or list(gap_scanners.keys())
    report = run_review(scanners=active_gaps)
    findings.extend(report.findings)
    for name in active_gaps:
        if name in gap_scanners:
            try:
                findings.extend(gap_scanners[name]())
            except Exception as e:
                findings.append(
                    ScanFinding(
                        repo="auto",
                        category="gap_scanner_error",
                        severity="warning",
                        summary=f"Gap scanner '{name}' failed",
                        detail=str(e)[:500],
                        score=0.5,
                    )
                )

    lesson_cache = LessonCache()
    filtered = []
    suppressed = 0
    for f in findings:
        should_suppress, lid = lesson_cache.should_suppress(f.category, f.summary)
        if should_suppress and lid:
            lesson_cache.record_suppressed(lid)
            suppressed += 1
            continue
        filtered.append(f)
    lesson_cache.save()
    if suppressed:
        print(f"  🧠 Brain suppressed {suppressed} known findings")
    findings = filtered

    final_report = ReviewReport(findings=findings)
    _persist_report(final_report)
    if apply:
        auto_fixable = [
            f for f in findings if f.category in list_fixable_categories()
        ]
        for finding in auto_fixable:
            fixer = get_fixer(finding.category)
            if fixer:
                try:
                    result = fixer(finding)
                    if result.applied:
                        status = "✅" if not result.requires_approval else "🔄"
                        print(f"  {status} Fixed [{finding.category}] {finding.summary}")
                        print(f"     {result.message}")
                    else:
                        print(f"  ⏭️  Skipped [{finding.category}] {finding.summary} — {result.message}")
                except Exception as e:
                    print(f"  ❌ Fix failed [{finding.category}] {finding.summary}: {e}")
    if not skip_kb_rebuild:
        _rebuild_kb()
    if os.environ.get("OLLAMA_API_KEY"):
        _ai_enhance(final_report)
    return final_report


def _ai_enhance(report: ReviewReport) -> None:
    try:
        from ai_assist.suggest import suggest_priority
        from ai_assist.summarize import summarize_report
        reviews_dir = Path.home() / ".opencode" / "reviews"
        priority = suggest_priority(report.findings)
        summary = summarize_report(report.findings, report.summary)
        print(f"\n  🤖 AI Priority: {priority[:200]}")
        print(f"  🤖 AI Summary: {summary[:200]}")
        enh_path = reviews_dir / f"ai_{report.timestamp[:10]}.md"
        enh_path.write_text(
            f"# AI Enhancement — {report.timestamp[:10]}\n\n"
            f"## Summary\n{summary}\n\n"
            f"## Priority\n{priority}\n"
        )
    except Exception as e:
        print(f"  ⚠️  AI enhancement skipped: {e}")
    try:
        from brain import overnight_sync
        result = overnight_sync()
        print(f"  🧠 Brain overnight sync: {result['context_entries']} context entries")
    except Exception as e:
        print(f"  ⚠️  Brain sync skipped: {e}")


def _rebuild_kb() -> None:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "autokb", "scan"],
            cwd=str(HOME / "Public" / "project"),
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0:
            print(f"  📚 KB index rebuilt")
        else:
            print(f"  ⚠️  KB rebuild: {result.stderr[:200]}")
    except Exception as e:
        print(f"  ⚠️  KB rebuild failed: {e}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Auto pipeline — detect gaps, fix, rebuild KB")
    parser.add_argument("command", nargs="?", default="run",
                        choices=["run", "plan", "status", "fixable"],
                        help="run (detect+fix), plan (detect only), status, fixable")
    parser.add_argument("--apply", action="store_true", help="Apply auto-fixes")
    parser.add_argument("--scanners", nargs="*",
                        help="Scanners to run (default: all)")
    parser.add_argument("--skip-kb", action="store_true", help="Skip KB rebuild")
    args = parser.parse_args()

    if args.command == "fixable":
        print("Auto-fixable categories:")
        for cat in list_fixable_categories():
            print(f"  - {cat}")
        return

    if args.command == "status":
        reviews_dir = HOME / ".opencode" / "reviews"
        latest = reviews_dir / "latest.json"
        if latest.exists():
            data = json.loads(latest.read_text(encoding="utf-8"))
            s = data.get("summary", {})
            print(f"Last review: {data.get('timestamp', '?')[:10]}")
            print(f"  Score: {s.get('score', '?')}/100 ({s.get('trend', '?')})")
            print(f"  Findings: {s.get('total_findings', 0)} "
                  f"({s.get('blockers', 0)} blockers, "
                  f"{s.get('critical', 0)} critical, "
                  f"{s.get('warnings', 0)} warnings)")
        else:
            print("No review data yet. Run 'auto run' first.")
        return

    if args.command == "plan":
        print("=== Auto Pipeline Plan ===")
        print()
        report = run_auto_pipeline(apply=False, scanners=args.scanners, skip_kb_rebuild=True)
        s = report.summary
        print(f"\nFindings: {s.total_findings}")
        print(f"  Blockers: {s.blockers}  Critical: {s.critical}  Warnings: {s.warnings}  Infos: {s.infos}")
        auto_fixable = [f for f in report.findings if f.category in list_fixable_categories()]
        if auto_fixable:
            print(f"\nAuto-fixable ({len(auto_fixable)}):")
            for f in auto_fixable:
                print(f"  ✅ {f.summary}")
        needs_review = [f for f in report.findings if f.category not in list_fixable_categories()]
        if needs_review:
            print(f"\nNeeds manual review ({len(needs_review)}):")
            for f in needs_review:
                print(f"  🔍 [{f.severity}] {f.repo}: {f.summary}")
        print(f"\nRun with --apply to auto-fix trivial gaps")
        return

    print("=== Auto Pipeline ===")
    report = run_auto_pipeline(apply=args.apply, scanners=args.scanners, skip_kb_rebuild=args.skip_kb)
    s = report.summary
    print(f"\n✅ Pipeline complete — Score: {s.score:.1f}/100")
    print(f"   {s.total_findings} findings: {s.blockers}b/{s.critical}c/{s.warnings}w/{s.infos}i")


if __name__ == "__main__":
    main()
