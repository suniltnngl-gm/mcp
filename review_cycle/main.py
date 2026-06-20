"""Review cycle orchestrator — runs all scanners and generates report."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from review_cycle.models import ReviewReport, ScanFinding
from review_cycle.scanners import GitScanner, TestRunner, TaskChecker


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
                        score=0.5,
                    )
                )
    report = ReviewReport(findings=findings)
    _persist_report(report)
    if output == "json":
        _write_json(report)
    elif output == "markdown":
        _write_markdown(report)
    return report


def _persist_report(report: ReviewReport) -> None:
    REVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    date_str = report.timestamp[:10]
    report_path = REVIEWS_DIR / f"{date_str}.json"
    data = {
        "timestamp": report.timestamp,
        "summary": {
            "total_findings": report.summary.total_findings if report.summary else 0,
            "blockers": report.summary.blockers if report.summary else 0,
            "critical": report.summary.critical if report.summary else 0,
            "warnings": report.summary.warnings if report.summary else 0,
            "infos": report.summary.infos if report.summary else 0,
            "score": report.summary.score if report.summary else 100.0,
            "trend": report.summary.trend if report.summary else "stable",
        },
        "findings": [
            {
                "repo": f.repo,
                "category": f.category,
                "severity": f.severity,
                "summary": f.summary,
                "detail": f.detail[:200],
                "suggested_action": f.suggested_action,
                "score": f.score,
            }
            for f in report.findings
        ],
    }
    report_path.write_text(json.dumps(data, indent=2))
    latest = REVIEWS_DIR / "latest.json"
    latest.write_text(json.dumps(data, indent=2))


def _write_json(report: ReviewReport) -> str:
    output_path = REVIEWS_DIR / f"review_{report.timestamp[:10]}.json"
    data = {
        "timestamp": report.timestamp,
        "findings": [
            {
                "repo": f.repo,
                "category": f.category,
                "severity": f.severity,
                "summary": f.summary,
                "detail": f.detail,
                "file_path": f.file_path,
                "suggested_action": f.suggested_action,
                "score": f.score,
            }
            for f in report.findings
        ],
        "summary": {
            "total_findings": report.summary.total_findings if report.summary else 0,
            "blockers": report.summary.blockers if report.summary else 0,
            "critical": report.summary.critical if report.summary else 0,
            "warnings": report.summary.warnings if report.summary else 0,
            "infos": report.summary.infos if report.summary else 0,
            "score": report.summary.score if report.summary else 100.0,
            "trend": report.summary.trend if report.summary else "stable",
        },
    }
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
    print(f"\nWorkspace health score: {s.score:.1f}/100 ({s.trend})")
    print(f"  {s.total_findings} findings: "
          f"{s.blockers} blockers, {s.critical} critical, "
          f"{s.warnings} warnings, {s.infos} infos")


if __name__ == "__main__":
    main()
