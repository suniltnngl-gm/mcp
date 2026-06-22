from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


@dataclass
class ScanFinding:
    repo: str
    category: str
    severity: str
    summary: str
    detail: str
    file_path: Optional[str] = None
    suggested_action: str = ""
    score: float = 0.0
    timestamp: str = ""
    finding_id: str = ""

    def __post_init__(self):
        now = datetime.now(timezone.utc)
        if not self.timestamp:
            self.timestamp = now.isoformat()
        if not self.finding_id:
            import hashlib
            raw = f"{self.repo}::{self.category}::{self.summary}"
            self.finding_id = hashlib.sha256(raw.encode()).hexdigest()[:16]


@dataclass
class ReviewSummary:
    total_findings: int = 0
    blockers: int = 0
    critical: int = 0
    warnings: int = 0
    infos: int = 0
    score: float = 100.0
    trend: str = "stable"


@dataclass
class ReviewReport:
    timestamp: str = ""
    findings: list[ScanFinding] = field(default_factory=list)
    summary: Optional[ReviewSummary] = None
    baseline_hash: Optional[str] = None
    new_findings: list[ScanFinding] = field(default_factory=list)
    resolved_finding_ids: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if self.summary is None:
            self.summary = self._compute_summary()

    def _compute_summary(self) -> ReviewSummary:
        s = ReviewSummary(total_findings=len(self.findings))
        for f in self.findings:
            if f.severity == "blocker":
                s.blockers += 1
            elif f.severity == "critical":
                s.critical += 1
            elif f.severity == "warning":
                s.warnings += 1
            else:
                s.infos += 1
        s.score = max(
            0.0,
            min(
                100.0,
                100.0
                - s.blockers * 10
                - s.critical * 5
                - s.warnings * 2
                - s.infos * 0.5,
            ),
        )
        return s

    def to_markdown(self) -> str:
        lines = [
            f"# Review Report — {self.timestamp[:10]}",
            "",
            "## Summary",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Total findings | {self.summary.total_findings if self.summary else 0} |",
            f"| Blockers | {self.summary.blockers if self.summary else 0} |",
            f"| Critical | {self.summary.critical if self.summary else 0} |",
            f"| Warnings | {self.summary.warnings if self.summary else 0} |",
            f"| Infos | {self.summary.infos if self.summary else 0} |",
            f"| Health score | {self.summary.score if self.summary else 100:.1f} |",
            f"| Trend | {self.summary.trend if self.summary else 'stable'} |",
            "",
        ]
        if self.resolved_finding_ids:
            lines.extend([
                "## Resolved",
                "",
            ])
            for rid in self.resolved_finding_ids:
                lines.append(f"- `{rid}`")
            lines.append("")

        if self.new_findings:
            lines.extend([
                "## New Findings",
                "",
            ])
            for f in sorted(self.new_findings, key=lambda x: x.score, reverse=True):
                lines.extend([
                    f"- **{f.severity.upper()}** [{f.repo}] {f.summary} *(score: {f.score:.2f})*",
                    f"  - {f.detail[:200]}",
                    "",
                ])

        sorted_findings = sorted(self.findings, key=lambda x: x.score, reverse=True)
        lines.extend([
            "## All Findings",
            "",
        ])
        for i, f in enumerate(sorted_findings, 1):
            lines.extend([
                f"### {i}. [{f.severity.upper()}] {f.repo} — {f.summary}",
                "",
                f"- **Category:** {f.category}",
                f"- **Detail:** {f.detail}",
                f"- **Suggested action:** {f.suggested_action}",
                f"- **Score:** {f.score:.2f}",
                f"- **File:** {f.file_path or 'N/A'}",
                f"- **ID:** `{f.finding_id}`",
                "",
            ])
        return "\n".join(lines) + "\n"

    def to_json(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "baseline_hash": self.baseline_hash,
            "summary": {
                "total_findings": self.summary.total_findings if self.summary else 0,
                "blockers": self.summary.blockers if self.summary else 0,
                "critical": self.summary.critical if self.summary else 0,
                "warnings": self.summary.warnings if self.summary else 0,
                "infos": self.summary.infos if self.summary else 0,
                "score": self.summary.score if self.summary else 100.0,
                "trend": self.summary.trend if self.summary else "stable",
            },
            "findings": [
                {
                    "finding_id": f.finding_id,
                    "repo": f.repo,
                    "category": f.category,
                    "severity": f.severity,
                    "summary": f.summary,
                    "detail": f.detail[:200],
                    "suggested_action": f.suggested_action,
                    "score": f.score,
                }
                for f in self.findings
            ],
            "new_findings": [
                {
                    "finding_id": f.finding_id,
                    "repo": f.repo,
                    "summary": f.summary,
                    "severity": f.severity,
                    "score": f.score,
                }
                for f in self.new_findings
            ],
            "resolved_finding_ids": self.resolved_finding_ids,
        }
