"""Auto-create GitHub Issues from review cycle findings with dedup."""

import json
import subprocess
from pathlib import Path

from review_cycle.models import ScanFinding

REPO_MAP = {
    "project": "mcp",
    "Workspace": "workspace",
    ".opencode": "opencode-config",
    "repositories": "dropbox-utils",
    "todo-automator": "todo-automator",
    "coding-agent": "coding-agent",
    "shared-tools": "shared-tools",
    "firebase-app": "firebase-app",
    "next-steps": "next-steps",
    "DevEnvSync": "DevEnvSync",
    "devflow-intelligence": "devflow-intelligence",
    "docs": "work",
    "artifacts": "work",
}

SEVERITY_LABELS = {
    "blocker": "severity:blocker",
    "critical": "severity:critical",
    "warning": "severity:warning",
    "info": "severity:info",
}

CATEGORY_LABELS = {
    "git_missing": "category:git",
    "git_uncommitted": "category:git",
    "git_diverged": "category:git",
    "test_failure": "category:testing",
    "task_stale": "category:tasks",
    "task_unblocked": "category:tasks",
    "tracking_outdated": "category:tasks",
    "doc_missing": "category:docs",
}

DEDUP_FILE = Path.home() / "Public" / ".opencode" / "issue_dedup.json"


def _load_dedup() -> dict:
    if DEDUP_FILE.exists():
        return json.loads(DEDUP_FILE.read_text())
    return {}


def _save_dedup(data: dict):
    DEDUP_FILE.parent.mkdir(parents=True, exist_ok=True)
    DEDUP_FILE.write_text(json.dumps(data, indent=2))


def _gh_issue_create(repo: str, title: str, body: str, labels: list[str]) -> dict:
    label_args = []
    for lbl in labels:
        label_args += ["--label", lbl]
    r = subprocess.run(
        ["gh", "issue", "create", "--repo", f"suniltnngl-gm/{repo}",
         "--title", title, "--body", body] + label_args,
        capture_output=True, text=True, timeout=30,
    )
    if r.returncode != 0:
        return {"error": r.stderr.strip()}
    return {"url": r.stdout.strip()}


def _issue_body(finding: ScanFinding) -> str:
    return f"""## {finding.summary}

**Severity:** {finding.severity}
**Category:** {finding.category}
**Repo:** {finding.repo}
**File:** {finding.file_path or 'N/A'}
**Score:** {finding.score:.2f}
**ID:** `{finding.finding_id}`

### Detail

{finding.detail}

### Suggested Action

{finding.suggested_action}

---
Auto-created by review_cycle issue_creator.
"""


def create_issues_from_findings(
    findings: list[ScanFinding],
    dry_run: bool = False,
    severity_min: str = "warning",
) -> list[dict]:
    severity_order = {"blocker": 0, "critical": 1, "warning": 2, "info": 3}
    min_order = severity_order.get(severity_min, 2)
    dedup = _load_dedup()
    results = []

    for f in findings:
        if severity_order.get(f.severity, 99) > min_order:
            continue

        gh_repo = REPO_MAP.get(f.repo)
        if not gh_repo:
            continue

        finding_id = f.finding_id
        if finding_id in dedup:
            continue

        title = f"[{f.severity.upper()}] {f.repo}: {f.summary[:80]}"
        body = _issue_body(f)
        labels = [SEVERITY_LABELS.get(f.severity, "severity:info")]
        if f.category in CATEGORY_LABELS:
            labels.append(CATEGORY_LABELS[f.category])

        if dry_run:
            results.append({
                "finding_id": finding_id,
                "repo": gh_repo,
                "title": title,
                "labels": labels,
                "dry_run": True,
            })
            continue

        result = _gh_issue_create(gh_repo, title, body, labels)
        if "error" in result:
            results.append({"finding_id": finding_id, "error": result["error"]})
        else:
            dedup[finding_id] = {"url": result["url"], "title": title}
            _save_dedup(dedup)
            results.append({"finding_id": finding_id, "url": result["url"], "success": True})

    return results
