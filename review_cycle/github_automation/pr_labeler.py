"""Auto-label GitHub PRs by changed file paths."""

import subprocess

from review_cycle.github_automation.issue_creator import REPO_MAP

PATH_LABELS = {
    "auth": "area:auth",
    "firebase": "area:firebase",
    "mcp": "area:mcp",
    "agent": "area:agent",
    "review_cycle": "area:review-cycle",
    "autokb": "area:knowledge-base",
    "scanner": "area:scanner",
    "test": "area:tests",
    "docs": "area:docs",
    "docker": "area:deploy",
    "config": "area:config",
    "security": "area:security",
    "api": "area:api",
    "ui": "area:ui",
    "deploy": "area:deploy",
    "backup": "area:backup",
    "sync": "area:backup",
    "hf": "area:hf",
    "github": "area:github",
}

RISK_PATHS = {
    "auth": "needs:security-review",
    "security": "needs:security-review",
    "firebase": "needs:security-review",
    "mcp": "needs:arch-review",
    "deploy": "needs:ops-review",
}


def _gh_labels_for(repo: str) -> set[str]:
    r = subprocess.run(
        ["gh", "label", "list", "--repo", f"suniltnngl-gm/{repo}", "--json", "name"],
        capture_output=True, text=True, timeout=15,
    )
    if r.returncode != 0:
        return set()
    import json
    return {lbl["name"] for lbl in json.loads(r.stdout) if r.stdout.strip()}


def _ensure_labels(repo: str, needed: set[str]):
    existing = _gh_labels_for(repo)
    for lbl in needed:
        if lbl not in existing:
            color = "5319e7" if lbl.startswith("severity:") else \
                    "0e8a16" if lbl.startswith("area:") else \
                    "e99695" if lbl.startswith("needs:") else \
                    "bfdadc" if lbl.startswith("category:") else "ededed"
            subprocess.run(
                ["gh", "label", "create", lbl, "--color", color,
                 "--repo", f"suniltnngl-gm/{repo}"],
                capture_output=True, timeout=15,
            )


def label_pull_request(repo: str, pr_number: int, changed_files: list[str]) -> dict:
    gh_repo = REPO_MAP.get(repo, repo)
    area_labels = set()
    risk_labels = set()

    for fp in changed_files:
        fp_lower = fp.lower()
        for keyword, label in PATH_LABELS.items():
            if keyword in fp_lower:
                area_labels.add(label)
        for keyword, label in RISK_PATHS.items():
            if keyword in fp_lower:
                risk_labels.add(label)

    all_needed = area_labels | risk_labels
    if not all_needed:
        return {"pr": pr_number, "labels_added": []}

    _ensure_labels(gh_repo, all_needed)
    label_str = ",".join(all_needed)
    r = subprocess.run(
        ["gh", "pr", "edit", str(pr_number), "--add-label", label_str,
         "--repo", f"suniltnngl-gm/{gh_repo}"],
        capture_output=True, text=True, timeout=15,
    )
    if r.returncode != 0:
        return {"pr": pr_number, "error": r.stderr.strip()}
    return {"pr": pr_number, "labels_added": list(all_needed)}
