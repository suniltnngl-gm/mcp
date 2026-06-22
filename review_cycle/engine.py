import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from review_cycle.models import ReviewReport, ScanFinding, ReviewSummary

HOME = Path.home()
REVIEWS_DIR = HOME / ".opencode" / "reviews"
SCORE_HISTORY_PATH = REVIEWS_DIR / "score_history.json"

SEVERITY_WEIGHTS = {
    "blocker": 1.0,
    "critical": 0.8,
    "warning": 0.5,
    "info": 0.2,
}

CATEGORY_WEIGHTS = {
    "dirty_repo": 0.9,
    "unpushed_commits": 0.8,
    "behind_remote": 0.7,
    "test_failure": 1.0,
    "task_outdated": 0.5,
    "scanner_error": 0.6,
    "default": 0.5,
}


def compute_finding_score(category: str, severity: str, age_hours: float = 0) -> float:
    severity_w = SEVERITY_WEIGHTS.get(severity, 0.5)
    category_w = CATEGORY_WEIGHTS.get(category, CATEGORY_WEIGHTS["default"])
    recency = max(0.5, 1.0 - (age_hours / 168))
    score = severity_w * category_w * recency
    return round(min(1.0, score), 4)


def score_findings(findings: List[ScanFinding]) -> List[ScanFinding]:
    now = datetime.now(timezone.utc)
    for f in findings:
        age = 0.0
        if f.timestamp:
            try:
                ts = datetime.fromisoformat(f.timestamp)
                age = (now - ts).total_seconds() / 3600
            except (ValueError, TypeError):
                pass
        f.score = compute_finding_score(f.category, f.severity, age)
    return findings


def compute_report_hash(report: ReviewReport) -> str:
    raw = json.dumps(
        [
            {"repo": f.repo, "category": f.category, "severity": f.severity, "summary": f.summary}
            for f in sorted(report.findings, key=lambda x: (x.repo, x.category, x.summary))
        ],
        sort_keys=True,
    )
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def load_baseline() -> Optional[ReviewReport]:
    latest_path = REVIEWS_DIR / "latest.json"
    if not latest_path.exists():
        return None
    try:
        data = json.loads(latest_path.read_text())
        findings = [
            ScanFinding(
                repo=f["repo"],
                category=f["category"],
                severity=f["severity"],
                summary=f["summary"],
                detail=f.get("detail", ""),
                suggested_action=f.get("suggested_action", ""),
                score=f.get("score", 0.0),
            )
            for f in data.get("findings", [])
        ]
        summary_data = data.get("summary", {})
        summary = ReviewSummary(
            total_findings=summary_data.get("total_findings", 0),
            blockers=summary_data.get("blockers", 0),
            critical=summary_data.get("critical", 0),
            warnings=summary_data.get("warnings", 0),
            infos=summary_data.get("infos", 0),
            score=summary_data.get("score", 100.0),
            trend=summary_data.get("trend", "stable"),
        )
        return ReviewReport(
            timestamp=data.get("timestamp", ""),
            findings=findings,
            summary=summary,
        )
    except (json.JSONDecodeError, KeyError):
        return None


def diff_baseline(
    current: ReviewReport, baseline: Optional[ReviewReport]
) -> Tuple[List[ScanFinding], List[str], List[str]]:
    new_findings: List[ScanFinding] = []
    resolved_keys: List[str] = []
    if baseline is None:
        return current.findings, [], []

    def finding_key(f: ScanFinding) -> str:
        return f"{f.repo}::{f.category}::{f.summary}"

    baseline_keys = {finding_key(f) for f in baseline.findings}
    current_keys = {finding_key(f) for f in current.findings}

    for f in current.findings:
        k = finding_key(f)
        if k not in baseline_keys:
            new_findings.append(f)

    for f in baseline.findings:
        k = finding_key(f)
        if k not in current_keys:
            resolved_keys.append(k)

    return new_findings, resolved_keys, list(current_keys)


def load_score_history() -> List[dict]:
    if not SCORE_HISTORY_PATH.exists():
        return []
    try:
        data = json.loads(SCORE_HISTORY_PATH.read_text())
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, ValueError):
        return []


def save_score_history(entry: dict) -> None:
    REVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    history = load_score_history()
    history.append(entry)
    if len(history) > 90:
        history = history[-90:]
    SCORE_HISTORY_PATH.write_text(json.dumps(history, indent=2))


def compute_trend(history: List[dict]) -> str:
    if len(history) < 2:
        return "stable"
    recent = history[-3:] if len(history) >= 3 else history
    scores = [h.get("score", 100.0) for h in recent]
    if len(scores) < 2:
        return "stable"
    slope = (scores[-1] - scores[0]) / max(1, len(scores) - 1)
    if slope > 3:
        return "improving"
    elif slope < -3:
        return "declining"
    return "stable"
