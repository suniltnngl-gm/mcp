import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from review_cycle.models import ReviewReport, ScanFinding
from review_cycle.scanners import GitScanner, TestRunner, TaskChecker
from review_cycle.engine import (
    compute_trend,
    diff_baseline,
    load_baseline,
    load_score_history,
    save_score_history,
    score_findings,
    compute_report_hash,
)

HOME = Path.home()
REVIEWS_DIR = HOME / ".opencode" / "reviews"


def run_review(
    scanners: Optional[List[str]] = None,
    output: str = "report",
) -> ReviewReport:
    findings: List[ScanFinding] = []
    scanner_map = {
        "git": GitScanner(),
        "tests": TestRunner(),
        "tasks": TaskChecker(),
    }
    active = scanners or list(scanner_map.keys())
    for name in active:
        if name in scanner_map:
            try:
                result = scanner_map[name].scan()
                findings.extend(result)
            except Exception as e:
                findings.append(
                    ScanFinding(
                        repo="review_cycle",
                        category="scanner_error",
                        severity="warning",
                        summary=f"Scanner '{name}' failed",
                        detail=str(e)[:500],
                        suggested_action="Check scanner implementation",
                    )
                )

    findings = score_findings(findings)
    baseline = load_baseline()
    new_findings, resolved_keys, _ = diff_baseline(
        ReviewReport(findings=findings), baseline
    )

    current_hash = compute_report_hash(ReviewReport(findings=findings))
    history = load_score_history()
    trend = compute_trend(history)

    report = ReviewReport(
        findings=findings,
        baseline_hash=current_hash,
        new_findings=new_findings,
        resolved_finding_ids=resolved_keys,
    )
    report.summary.trend = trend

    _persist_report(report)

    score_entry = {
        "date": report.timestamp[:13],
        "score": report.summary.score,
        "total_findings": report.summary.total_findings,
        "trend": trend,
    }
    save_score_history(score_entry)

    if output == "json":
        _write_json(report)
    elif output == "markdown":
        _write_markdown(report)
    return report


def _persist_report(report: ReviewReport) -> None:
    REVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    date_str = report.timestamp[:10]
    report_path = REVIEWS_DIR / f"{date_str}.json"
    data = report.to_json()
    report_path.write_text(json.dumps(data, indent=2))
    latest = REVIEWS_DIR / "latest.json"
    latest.write_text(json.dumps(data, indent=2))


def _write_json(report: ReviewReport) -> str:
    output_path = REVIEWS_DIR / f"review_{report.timestamp[:10]}.json"
    data = report.to_json()
    output_path.write_text(json.dumps(data, indent=2))
    print(f"Review report: {output_path}")
    return str(output_path)


def _write_markdown(report: ReviewReport) -> str:
    output_path = REVIEWS_DIR / f"review_{report.timestamp[:10]}.md"
    content = report.to_markdown()
    output_path.write_text(content)
    print(f"Review report: {output_path}")
    return str(output_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run automated review cycle")
    parser.add_argument(
        "--scanners", nargs="*",
        choices=["git", "tests", "tasks"],
        help="Scanners to run (default: all)",
    )
    parser.add_argument(
        "--output", choices=["report", "json", "markdown"],
        default="report",
        help="Output format (default: report — both persist + latest.json)",
    )
    args = parser.parse_args()
    report = run_review(scanners=args.scanners, output=args.output)
    s = report.summary
    trend_icon = {"improving": "↑", "declining": "↓", "stable": "→"}.get(s.trend, "→")
    new_count = len(report.new_findings)
    resolved_count = len(report.resolved_finding_ids)
    print(f"\nWorkspace health score: {s.score:.1f}/100 ({s.trend} {trend_icon})")
    print(f"  {s.total_findings} findings: "
          f"{s.blockers} blockers, {s.critical} critical, "
          f"{s.warnings} warnings, {s.infos} infos")
    if new_count:
        print(f"  {new_count} new, {resolved_count} resolved since last review")


if __name__ == "__main__":
    main()
