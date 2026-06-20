"""Gap detectors — find missing docs, missing tests, missing configs, stale tracking."""

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from review_cycle.models import ScanFinding


HOME = Path.home()
BASE = HOME / "Public"
ACTIVE_REPOS: Dict[str, Path] = {
    "Workspace": BASE / "Workspace",
    "project": BASE / "project",
    "repositories": BASE / "repositories",
    ".opencode": BASE / ".opencode",
    "coding-agent": BASE / "coding-agent",
    "next-steps": BASE / "next-steps",
    "shared-tools": BASE / "shared-tools",
    "firebase-app": BASE / "Workspace" / "firebase-app",
}


def scan_docs_gaps() -> List[ScanFinding]:
    """Find Python modules and scripts that lack KB entries or READMEs."""
    findings = []
    kb_md = BASE / ".opencode" / "KB.md"
    if not kb_md.exists():
        return findings
    kb_text = kb_md.read_text(encoding="utf-8").lower()
    seen_modules: Set[str] = set()
    for name, path in ACTIVE_REPOS.items():
        if not path.exists():
            continue
        py_files = list(path.rglob("*.py")) + list(path.rglob("*.sh"))
        for f in py_files:
            rel = f.relative_to(path)
            if any(p in rel.parts for p in (".git", "node_modules", "__pycache__", ".venv")):
                continue
            stem = f.stem.lower()
            if stem in seen_modules:
                continue
            seen_modules.add(stem)
            if stem not in kb_text and stem not in ("__init__", "__main__", "conftest", "setup"):
                if f.stat().st_size < 200:
                    continue
                findings.append(
                    ScanFinding(
                        repo=name,
                        category="missing_kb_entry",
                        severity="info",
                        summary=f"No KB entry for '{stem}'",
                        detail=f"File: {rel} ({f.stat().st_size}b) — no matching KB.md entry found",
                        file_path=str(f),
                        suggested_action=f"Add KB entry: `{stem}` with description and tags",
                        score=0.2,
                    )
                )
    return findings


def scan_env_gaps() -> List[ScanFinding]:
    """Find .env files without .env.example, node_modules without gitignore."""
    findings = []
    for name, path in ACTIVE_REPOS.items():
        if not path.exists():
            continue
        env_file = path / ".env"
        env_example = path / ".env.example"
        if env_file.exists() and not env_example.exists():
            findings.append(
                ScanFinding(
                    repo=name,
                    category="missing_env_example",
                    severity="info",
                    summary=".env exists but no .env.example",
                    detail=f"Add .env.example with placeholder values (keys redacted)",
                    file_path=str(env_file),
                    suggested_action="Generate .env.example from .env keys",
                    score=0.3,
                )
            )
        gitignore = path / ".gitignore"
        nm_dir = path / "node_modules"
        if nm_dir.exists() and gitignore.exists():
            gi_text = gitignore.read_text(encoding="utf-8")
            if "node_modules" not in gi_text:
                findings.append(
                    ScanFinding(
                        repo=name,
                        category="missing_gitignore_entry",
                        severity="warning",
                        summary="node_modules/ exists but not in .gitignore",
                        detail="Add 'node_modules/' to .gitignore",
                        file_path=str(gitignore),
                        suggested_action="Append 'node_modules/' to .gitignore",
                        score=0.5,
                    )
                )
    return findings


def scan_tracking_gaps() -> List[ScanFinding]:
    """Find stale or inconsistent tracking entries."""
    findings = []
    plan_md = BASE / "project" / "PLAN.md"
    dashboard = BASE / ".opencode" / "DASHBOARD.md"
    cross = BASE / ".opencode" / "CROSS_PROJECT.md"
    for doc_path, doc_name in [(plan_md, "PLAN.md"), (dashboard, "DASHBOARD.md"), (cross, "CROSS_PROJECT.md")]:
        if not doc_path.exists():
            continue
        text = doc_path.read_text(encoding="utf-8")
        pending_count = len(re.findall(r"⏳\s*(?:Pending|Not started|in_progress)", text))
        done_count = len(re.findall(r"✅\s*(?:Completed|Done)", text))
        if pending_count > 0 and done_count > pending_count * 3:
            findings.append(
                ScanFinding(
                    repo=".opencode" if doc_name != "PLAN.md" else "project",
                    category="tracking_stale",
                    severity="info",
                    summary=f"{doc_name}: {pending_count} pending, {done_count} done",
                    detail=f"Most tasks completed ({done_count}/{done_count + pending_count}), review pending items",
                    file_path=str(doc_path),
                    suggested_action=f"Review pending items in {doc_name}",
                    score=0.2,
                )
            )
    return findings


def scan_orphaned_files() -> List[ScanFinding]:
    """Find files >1KB tracked in git that appear unreferenced (by other files)."""
    findings = []
    orphans_per_repo = 0
    for name, path in ACTIVE_REPOS.items():
        if not (path / ".git").exists() or orphans_per_repo >= 5:
            continue
        try:
            result = subprocess.run(
                ["git", "ls-files", "*.py"],
                cwd=path, capture_output=True, text=True, timeout=30,
            )
            py_files = [f for f in result.stdout.splitlines() if f.strip()]
            for pyf in py_files:
                if orphans_per_repo >= 5:
                    break
                full = path / pyf
                if not full.exists() or full.stat().st_size < 1024:
                    continue
                stem = Path(pyf).stem
                if stem in ("__init__", "__main__", "conftest", "setup", "manage"):
                    continue
                grep_result = subprocess.run(
                    ["git", "grep", "-l", stem, "--", "*.py"],
                    cwd=path, capture_output=True, text=True, timeout=15,
                )
                refs = [l for l in grep_result.stdout.splitlines() if l.strip() and l != pyf]
                if not refs:
                    findings.append(
                        ScanFinding(
                            repo=name,
                            category="orphaned_file",
                            severity="info",
                            summary=f"Potentially orphaned: {pyf[:50]}",
                            detail=f"Not imported by any other .py file",
                            file_path=str(full),
                            suggested_action="Verify file is still needed",
                            score=0.2,
                        )
                    )
                    orphans_per_repo += 1
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
    return findings


def scan_test_gaps() -> List[ScanFinding]:
    """Find Python modules without corresponding test files."""
    findings = []
    for name, path in ACTIVE_REPOS.items():
        if not path.exists():
            continue
        test_dirs = list(path.rglob("tests")) + [path / "tests"]
        test_files = set()
        for td in test_dirs:
            if td.exists():
                for tf in td.rglob("test_*.py"):
                    test_files.add(tf.stem.replace("test_", ""))
        src_files = list(path.rglob("*.py"))
        for f in src_files:
            rel = f.relative_to(path)
            if any(p in rel.parts for p in (".git", "node_modules", "__pycache__", ".venv", "tests")):
                continue
            stem = f.stem
            if stem in ("__init__", "__main__", "conftest", "setup"):
                continue
            if stem not in test_files and f.stat().st_size > 500:
                findings.append(
                    ScanFinding(
                        repo=name,
                        category="missing_tests",
                        severity="info",
                        summary=f"No tests for '{stem}'",
                        detail=f"File: {rel} ({f.stat().st_size}b)",
                        file_path=str(f),
                        suggested_action=f"Create test_{stem}.py with unit tests",
                        score=0.2,
                    )
                )
    return findings
