from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


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

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


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
    baseline: Optional[str] = None

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
            f"| Metric | Value |",
            "|--------|-------|",
            f"| Total findings | {self.summary.total_findings if self.summary else 0} |",
            f"| Blockers | {self.summary.blockers if self.summary else 0} |",
            f"| Critical | {self.summary.critical if self.summary else 0} |",
            f"| Warnings | {self.summary.warnings if self.summary else 0} |",
            f"| Infos | {self.summary.infos if self.summary else 0} |",
            f"| Health score | {self.summary.score if self.summary else 100:.1f} |",
            "",
            "## Findings",
            "",
        ]
        for i, f in enumerate(self.findings, 1):
            lines.extend(
                [
                    f"### {i}. [{f.severity.upper()}] {f.repo} — {f.summary}",
                    "",
                    f"- **Category:** {f.category}",
                    f"- **Detail:** {f.detail}",
                    f"- **Suggested action:** {f.suggested_action}",
                    f"- **Score:** {f.score:.2f}",
                    f"- **File:** {f.file_path or 'N/A'}",
                    "",
                ]
            )
        return "\n".join(lines) + "\n"
