"""Health audit — standardized report merging review cycle, auto pipeline, and deliverable verification."""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from review_cycle.main import run_review
from review_cycle.models import ReviewReport, ScanFinding

HOME = Path.home()
BASE = HOME / "Public"
PROJECT = BASE / "project"
OPCODE = BASE / ".opencode"
AUTOKB_INDEX = HOME / ".opencode" / "autokb" / "index.json"

SEVERITY_ORDER = {"blocker": 0, "critical": 1, "warning": 2, "info": 3}

PHASE_DELIVERABLES: dict[int, list[dict]] = {
    0: [
        {"path": ".opencode/ENTRY.md", "label": "Session lifecycle"},
        {"path": ".opencode/guidelines.md", "label": "Session continuity"},
        {"path": ".opencode/DASHBOARD.md", "label": "Cross-project dashboard"},
        {"path": ".opencode/AGENT_LOG.md", "label": "Agent audit trail"},
        {"path": "workspace.sh", "label": "Unified CLI"},
        {"path": "ENV/.env", "label": "Centralized secrets"},
    ],
    1: [
        {"path": "project/.venv", "label": "Virtual environment", "check": "isdir"},
        {"path": "project/pyproject.toml", "label": "Project config"},
        {"path": "project/src/llm_wrapper", "label": "LLM wrapper package", "check": "isdir"},
    ],
    2: [
        {"path": "project/src/llm_wrapper/__init__.py", "label": "Wrapper module"},
    ],
    3: [
        {"path": "project/src/llm_wrapper/llm/local_client.py", "label": "Local LLM client"},
    ],
    4: [
        {"path": "project/src/llm_wrapper/providers/remote_client.py", "label": "Provider LLM client"},
    ],
    5: [
        {"path": "project/src/llm_wrapper/mcp/__init__.py", "label": "MCP framework"},
    ],
    6: [
        {"path": "project/src/llm_wrapper/mcp/doc_manager_server.py", "label": "Document management"},
    ],
    7: [
        {"path": "project/src/llm_wrapper/mcp/ollama_cloud_server.py", "label": "Ollama cloud MCP"},
        {"path": "project/src/llm_wrapper/mcp/osenv_server.py", "label": "osenv bridge MCP"},
    ],
    8: [
        {"path": "project/src/llm_wrapper/mcp/game_rules_server.py", "label": "Game rules MCP", "alt": "Project 8 games live in mcp/"},
    ],
    9: [
        {"path": "project/src/llm_wrapper/orchestrator.py", "label": "LLM orchestrator"},
        {"path": "project/src/llm_wrapper/mcp/cooperative_strategy.py", "label": "Cooperative strategies"},
    ],
    10: [
        {"path": "project/tests", "label": "Test suite", "check": "isdir"},
    ],
    11: [
        {"path": "project/workspace-automation", "label": "Workspace automation", "check": "isdir"},
    ],
    13: [
        {"path": "project/review_cycle/scanners", "label": "Review scanners", "check": "isdir"},
        {"path": "project/review_cycle/engine.py", "label": "Scoring engine"},
        {"path": "project/review_cycle/autofix/approval_gate.py", "label": "Approval gate"},
    ],
    14: [
        {"path": "project/autokb", "label": "Auto KB module", "check": "isdir"},
        {"path": str(HOME / ".opencode" / "autokb" / "index.json"), "label": "KB index"},
    ],
    15: [
        {"path": "project/review_cycle/autofix", "label": "Autofix pipeline", "check": "isdir"},
    ],
    16: [
        {"path": "devflow-intelligence", "label": "DevFlow Intelligence repo", "check": "isdir"},
    ],
    17: [
        {"path": "archive/consolidation", "label": "Consolidation repo (archived)", "check": "isdir"},
    ],
    18: [
        {"path": "project/todo-automator", "label": "Todo automator repo", "check": "isdir"},
    ],
    19: [
        {"path": "project/src/hf_cli/client.py", "label": "HF API client"},
        {"path": "project/src/hf_cli/download.py", "label": "HF download with resume"},
        {"path": "project/src/hf_cli/push.py", "label": "HF push"},
    ],
    20: [
        {"path": "project/review_cycle/github_automation/issue_creator.py", "label": "Auto issue creator"},
        {"path": "project/review_cycle/github_automation/pr_labeler.py", "label": "PR labeler"},
        {"path": "project/review_cycle/github_automation/release_manager.py", "label": "Release manager"},
    ],
}


@dataclass
class DeliverableCheck:
    phase: int
    phase_name: str
    path: str
    label: str
    status: str  # EXISTS, MISSING, MOVED
    size_kb: float = 0
    notes: str = ""

    def passed(self) -> bool:
        return self.status == "EXISTS"


@dataclass
class HealthIssue:
    phase: int
    severity: str
    summary: str
    detail: str
    suggestion: str = ""

    def sort_key(self):
        return (SEVERITY_ORDER.get(self.severity, 99), self.phase)


@dataclass
class HealthAudit:
    timestamp: str = ""
    review_score: float = 100.0
    review_trend: str = "stable"
    review_findings: list = field(default_factory=list)
    review_summary: dict = field(default_factory=dict)
    auto_summary: dict = field(default_factory=dict)
    deliverables: list[DeliverableCheck] = field(default_factory=list)
    issues: list[HealthIssue] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    kb_summary: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def phase_status_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for d in self.deliverables:
            s = d.status
            counts[s] = counts.get(s, 0) + 1
        return counts

    def phase_status(self, phase: int) -> str:
        phase_dels = [d for d in self.deliverables if d.phase == phase]
        if not phase_dels:
            return "—"
        totals = {"EXISTS": 0, "MISSING": 0, "MOVED": 0}
        for d in phase_dels:
            totals[d.status] = totals.get(d.status, 0) + 1
        total = len(phase_dels)
        if totals["EXISTS"] == total:
            return "✅"
        if totals["MISSING"] == 0:
            return "🟡"
        return "🔴"

    def to_markdown(self) -> str:
        lines = [
            f"# Health Audit — {self.timestamp[:10]}",
            "",
            "## Review Cycle",
            "",
            f"**Score:** {self.review_score:.1f}/100 ({self.review_trend})",
            f"**Findings:** {self.review_summary.get('total_findings', 0)} total — "
            f"{self.review_summary.get('blockers', 0)} blockers, "
            f"{self.review_summary.get('critical', 0)} critical, "
            f"{self.review_summary.get('warnings', 0)} warnings, "
            f"{self.review_summary.get('infos', 0)} infos",
            "",
        ]

        kb = self.kb_summary
        if kb:
            lines.extend([
                "## Knowledge Base",
                "",
                f"**KB:** {'✅ indexed' if kb.get('available') else '❌ not indexed'}",
            ])
            if kb.get("available"):
                lines.append(
                    f"{kb['files']} files, {kb['terms']} terms, {kb['size_kb']}KB — "
                    f"{'no repos' if not kb.get('repos') else ', '.join(kb['repos'])}"
                )
            lines.append("")

        lines.extend([
            "## Auto Pipeline",
            "",
        ])
        ap = self.auto_summary
        if ap:
            lines.append(f"**Findings:** {ap.get('total', 0)} ({ap.get('autofixable', 0)} auto-fixable, {ap.get('manual', 0)} need review)")
            if ap.get("categories"):
                for cat, count in sorted(ap["categories"].items()):
                    lines.append(f"- {cat}: {count}")
        else:
            lines.append("*Not run this cycle*")
        lines.append("")

        phase_stati: dict[int, str] = {}
        for d in self.deliverables:
            phase_stati.setdefault(d.phase, set()).add(d.status)

        lines.extend([
            "## Deliverables Audit",
            "",
            "| Phase | Status |",
            "|-------|--------|",
        ])
        seen = set()
        for d in sorted(self.deliverables, key=lambda x: (x.phase, x.path)):
            if d.phase not in seen:
                lines.append(f"| {d.phase} | {self.phase_status(d.phase)} |")
                seen.add(d.phase)
        lines.append("")

        sorted_issues = sorted(self.issues, key=lambda x: x.sort_key())
        if sorted_issues:
            lines.extend([
                "## Issues Found",
                "",
            ])
            for i, iss in enumerate(sorted_issues, 1):
                icon = {"blocker": "🔴", "critical": "🔶", "warning": "🟡", "info": "🟢"}.get(iss.severity, "⚪")
                lines.extend([
                    f"### {i}. {icon} [{iss.severity.upper()}] Phase {iss.phase} — {iss.summary}",
                    "",
                    f"{iss.detail}",
                    f"**Suggestion:** {iss.suggestion}",
                    "",
                ])

        if self.recommendations:
            lines.extend([
                "## Recommendations",
                "",
            ])
            for i, rec in enumerate(self.recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")

        lines.append("---\n*Generated by review_cycle.health_audit*\n")
        return "\n".join(lines)

    def to_json(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "review_score": self.review_score,
            "review_trend": self.review_trend,
            "review_summary": self.review_summary,
            "auto_summary": self.auto_summary,
            "kb_summary": self.kb_summary,
            "deliverables": [
                {"phase": d.phase, "phase_name": d.phase_name, "path": d.path,
                 "label": d.label, "status": d.status, "size_kb": d.size_kb, "notes": d.notes}
                for d in self.deliverables
            ],
            "issues": [
                {"phase": i.phase, "severity": i.severity, "summary": i.summary,
                 "detail": i.detail, "suggestion": i.suggestion}
                for i in sorted(self.issues, key=lambda x: x.sort_key())
            ],
            "recommendations": self.recommendations,
        }


def _check_deliverable(entry: dict) -> DeliverableCheck:
    phase = entry.get("phase", 0)
    phase_name = entry.get("phase_name", "")
    path_raw = entry["path"]
    label = entry["label"]
    check_type = entry.get("check", "isfile")
    alt = entry.get("alt", "")

    p = Path(path_raw) if path_raw.startswith("/") else BASE / path_raw

    exists = p.exists() if check_type == "isdir" else p.is_file()
    size_kb = 0
    if exists:
        try:
            size_kb = round(p.stat().st_size / 1024, 1)
        except OSError:
            size_kb = 0

    if exists:
        return DeliverableCheck(phase=phase, phase_name=phase_name, path=path_raw,
                                label=label, status="EXISTS", size_kb=size_kb, notes="")
    if alt:
        return DeliverableCheck(phase=phase, phase_name=phase_name, path=path_raw,
                                label=label, status="MOVED", size_kb=0, notes=alt)
    return DeliverableCheck(phase=phase, phase_name=phase_name, path=path_raw,
                            label=label, status="MISSING", size_kb=0, notes="")


def _scan_deliverables() -> list[DeliverableCheck]:
    phase_names = {
        0: "Genesis", 1: "Foundational Setup", 2: "Pre-LLM Wrapper",
        3: "Local LLM", 4: "Provider LLM", 5: "MCP Foundational",
        6: "Document Management", 7: "Distributed MCP", 8: "Game Integration",
        9: "Orchestration", 10: "Testing", 11: "Workflow Automation",
        13: "Review Cycle", 14: "Auto KB", 15: "Auto Fix",
        16: "DevFlow Intelligence", 17: "Code Review Consolidation",
        18: "Todo Monitor", 19: "HF Hub CLI", 20: "GitHub Automation",
    }
    results = []
    for phase, entries in sorted(PHASE_DELIVERABLES.items()):
        for e in entries:
            e["phase"] = phase
            e["phase_name"] = phase_names.get(phase, "")
            results.append(_check_deliverable(e))
    return results


def _get_kb_summary() -> dict:
    stats = {"available": False, "files": 0, "terms": 0, "size_kb": 0, "generated": None, "repos": []}
    if AUTOKB_INDEX.exists():
        try:
            data = json.loads(AUTOKB_INDEX.read_text())
            stats["available"] = True
            stats["files"] = data.get("entries_count", 0)
            stats["terms"] = data.get("terms_count", 0)
            stats["generated"] = data.get("generated", "?")[:19]
            stats["size_kb"] = round(AUTOKB_INDEX.stat().st_size / 1024, 1)
            stats["repos"] = data.get("repos", [])
        except Exception:
            pass
    return stats


def _get_auto_summary() -> dict:
    """Run gap scanners directly (no nested run_review) and summarize."""
    summary = {"total": 0, "autofixable": 0, "manual": 0, "categories": {}}
    try:
        from autofix.fixers import list_fixable_categories
        from autofix.gaps import scan_docs_gaps, scan_env_gaps, scan_orphaned_files, scan_test_gaps, scan_tracking_gaps
        from review_cycle.engine import score_findings
        gap_findings: list = []
        for scanner in [scan_docs_gaps, scan_env_gaps, scan_tracking_gaps, scan_orphaned_files, scan_test_gaps]:
            try:
                gap_findings.extend(scanner())
            except Exception:
                pass
        gap_findings = score_findings(gap_findings)
        fixable = set(list_fixable_categories())
        for f in gap_findings:
            summary["total"] += 1
            if f.category in fixable:
                summary["autofixable"] += 1
                cat = "test_stubs" if "test" in f.category else "kb_entries"
            else:
                summary["manual"] += 1
                cat = "orphans"
            summary["categories"][cat] = summary["categories"].get(cat, 0) + 1
    except Exception:
        pass
    return summary


def _build_issues(
    review_report: ReviewReport,
    deliverables: list[DeliverableCheck],
    kb: dict,
) -> list[HealthIssue]:
    issues: list[HealthIssue] = []

    for f in review_report.findings:
        issues.append(HealthIssue(
            phase=0,
            severity=f.severity,
            summary=f.summary,
            detail=f.detail[:300],
            suggestion=f.suggested_action,
        ))

    missing = [d for d in deliverables if d.status == "MISSING"]
    if missing:
        for d in missing:
            issues.append(HealthIssue(
                phase=d.phase, severity="warning",
                summary=f"Missing deliverable: {d.label}",
                detail=f"Expected at `{d.path}` — not found",
                suggestion=f"Create `{d.path}` or update PLAN.md if moved",
            ))

    moved = [d for d in deliverables if d.status == "MOVED"]
    if moved:
        for d in moved:
            issues.append(HealthIssue(
                phase=d.phase, severity="info",
                summary=f"Moved deliverable: {d.label}",
                detail=f"Expected at `{d.path}` — {d.notes}",
                suggestion="Update deliverable registry or PLAN.md to reflect current location",
            ))

    if not kb.get("available"):
        issues.append(HealthIssue(
            phase=14, severity="warning",
            summary="Knowledge base not indexed",
            detail="autokb index missing — search and code review will be slower",
            suggestion="Run `workspace.sh kb-auto scan` to rebuild",
        ))

    return issues


def _build_recommendations(issues: list[HealthIssue], deliverables: list[DeliverableCheck], kb: dict) -> list[str]:
    recs: list[str] = []

    blockers = [i for i in issues if i.severity == "blocker"]
    critical = [i for i in issues if i.severity == "critical"]
    warning = [i for i in issues if i.severity == "warning"]

    if blockers:
        recs.append(f"🔴 Resolve {len(blockers)} blocker(s): {blockers[0].summary}")
    if critical:
        recs.append(f"🔶 Fix {len(critical)} critical issue(s): {critical[0].summary}")
    if warning:
        recs.append(f"🟡 Address {len(warning)} warning(s) — highest priority: {warning[0].summary}")

    missing_count = len([d for d in deliverables if d.status == "MISSING"])
    if missing_count:
        recs.append(f"Create or document {missing_count} missing deliverable(s)")
    moved_count = len([d for d in deliverables if d.status == "MOVED"])
    if moved_count:
        recs.append(f"Update PLAN.md for {moved_count} relocated deliverable(s)")

    if not kb.get("available"):
        recs.append("Rebuild knowledge base with `workspace.sh kb-auto scan`")

    if not recs:
        recs.append("All systems nominal — no action needed")

    return recs


def run_health_audit(output: str = "report") -> HealthAudit:
    review_report = run_review(output="report")
    kb = _get_kb_summary()
    auto = _get_auto_summary()
    deliverables = _scan_deliverables()
    issues = _build_issues(review_report, deliverables, kb)
    recommendations = _build_recommendations(issues, deliverables, kb)

    rs = review_report.summary
    audit = HealthAudit(
        timestamp=datetime.now(timezone.utc).isoformat(),
        review_score=rs.score if rs else 100.0,
        review_trend=rs.trend if rs else "stable",
        review_findings=[
            {"finding_id": f.finding_id, "repo": f.repo, "category": f.category,
             "severity": f.severity, "summary": f.summary, "detail": f.detail[:200],
             "suggested_action": f.suggested_action, "score": f.score}
            for f in review_report.findings
        ],
        review_summary=review_report.to_json()["summary"],
        auto_summary=auto,
        deliverables=deliverables,
        issues=issues,
        recommendations=recommendations,
        kb_summary=kb,
    )

    _persist(audit)
    if output == "json":
        _write_json(audit)
    elif output == "markdown":
        _write_markdown(audit)
    else:
        _print_summary(audit)
    return audit


def _persist(audit: HealthAudit):
    audit_dir = HOME / ".opencode" / "audits"
    audit_dir.mkdir(parents=True, exist_ok=True)
    date_str = audit.timestamp[:10]
    (audit_dir / f"{date_str}.json").write_text(json.dumps(audit.to_json(), indent=2, default=str))
    (audit_dir / "latest.json").write_text(json.dumps(audit.to_json(), indent=2, default=str))
    (audit_dir / f"{date_str}.md").write_text(audit.to_markdown())


def _write_json(audit: HealthAudit):
    print(json.dumps(audit.to_json(), indent=2, default=str))


def _write_markdown(audit: HealthAudit):
    print(audit.to_markdown())


def _print_summary(audit: HealthAudit):
    pc = audit.phase_status_counts()
    total_dels = len(audit.deliverables)
    green = pc.get("EXISTS", 0)
    amber = pc.get("MOVED", 0)
    red = pc.get("MISSING", 0)
    icon = "🔴" if red else ("🟡" if amber else "✅")

    print(f"\n  ══ Health Audit — {audit.timestamp[:19]} ══\n")
    print(f"  📊 Review: {audit.review_score:.1f}/100 ({audit.review_trend}) — "
          f"{audit.review_summary.get('total_findings', 0)} findings")
    print(f"  🔧 Auto: {audit.auto_summary.get('total', 0)} gaps "
          f"({audit.auto_summary.get('autofixable', 0)} fixable, "
          f"{audit.auto_summary.get('manual', 0)} manual)")
    print(f"  {icon} Deliverables: {green}/{total_dels} pass"
          + (f", {amber} moved" if amber else "")
          + (f", {red} missing" if red else ""))
    print(f"  📚 KB: {'✅ indexed' if audit.kb_summary.get('available') else '❌ not indexed'}")

    issues = sorted(audit.issues, key=lambda x: x.sort_key())
    if issues:
        print(f"\n  Issues ({len(issues)}):")
        for iss in issues[:5]:
            icon = {"blocker": "🔴", "critical": "🔶", "warning": "🟡", "info": "🟢"}.get(iss.severity, "⚪")
            print(f"  {icon} [{iss.severity.upper()}] Phase {iss.phase}: {iss.summary}")
        if len(issues) > 5:
            print(f"     ... and {len(issues) - 5} more")

    if audit.recommendations:
        print(f"\n  Recommendations:")
        for r in audit.recommendations:
            print(f"  → {r}")

    print(f"\n  Full report: {HOME}/.opencode/audits/{audit.timestamp[:10]}.md")
    print()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run health audit")
    parser.add_argument("--output", choices=["report", "json", "markdown"], default="report")
    args = parser.parse_args()
    run_health_audit(output=args.output)


if __name__ == "__main__":
    main()
