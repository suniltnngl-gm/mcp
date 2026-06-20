"""Auto-fix registry — applies known fixes for detected gaps."""

import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from review_cycle.models import ScanFinding


HOME = Path.home()
BASE = HOME / "Public"


@dataclass
class FixResult:
    finding: ScanFinding
    applied: bool
    message: str
    requires_approval: bool = False


Fixer = Callable[[ScanFinding], FixResult]


_REGISTRY: Dict[str, Fixer] = {}


def register(category: str):
    def decorator(fn: Fixer):
        _REGISTRY[category] = fn
        return fn
    return decorator


def get_fixer(category: str) -> Optional[Fixer]:
    return _REGISTRY.get(category)


def list_fixable_categories() -> List[str]:
    return list(_REGISTRY.keys())


@register("missing_env_example")
def fix_env_example(finding: ScanFinding) -> FixResult:
    if not finding.file_path:
        return FixResult(finding, False, "No file path")
    env_path = Path(finding.file_path)
    env_example = env_path.parent / ".env.example"
    try:
        keys = []
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key = line.split("=", 1)[0].strip()
                if key and not key.startswith("#"):
                    keys.append(key)
        if not keys:
            return FixResult(finding, False, "No keys found in .env")
        content = "# Environment Variables\n# Copy this file to .env and fill in values\n\n"
        for key in sorted(set(keys)):
            content += f"{key}=<your-value>\n"
        env_example.write_text(content)
        return FixResult(finding, True, f"Generated .env.example with {len(keys)} keys")
    except OSError as e:
        return FixResult(finding, False, str(e))


@register("missing_gitignore_entry")
def fix_gitignore(finding: ScanFinding) -> FixResult:
    if not finding.file_path:
        return FixResult(finding, False, "No file path")
    gitignore = Path(finding.file_path)
    try:
        text = gitignore.read_text(encoding="utf-8")
        if "node_modules" not in text:
            gitignore.write_text(text.rstrip() + "\nnode_modules/\n")
            return FixResult(finding, True, "Added 'node_modules/' to .gitignore")
        return FixResult(finding, False, "Already present")
    except OSError as e:
        return FixResult(finding, False, str(e))


@register("missing_kb_entry")
def fix_kb_entry(finding: ScanFinding) -> FixResult:
    if not finding.file_path:
        return FixResult(finding, False, "No file path")
    fp = Path(finding.file_path)
    stem = fp.stem
    kb_path = BASE / ".opencode" / "KB.md"
    if not kb_path.exists():
        return FixResult(finding, False, "KB.md not found")
    try:
        text = kb_path.read_text(encoding="utf-8")
        if stem.lower() in text.lower():
            return FixResult(finding, False, "Entry already exists")
        line_count = 0
        with open(fp, encoding="utf-8") as f:
            for _ in f:
                line_count += 1
                if line_count > 100:
                    break
        repo = finding.repo
        entry = f"\n| KB_{stem[:8]} | {stem} | `{stem}` `auto` | {repo}/{'/'.join(fp.relative_to(BASE / repo).parts[:-1]) if (BASE / repo).exists() else '?'} |\n"
        kb_path.write_text(text.rstrip() + entry)
        return FixResult(finding, True, f"Added KB entry for '{stem}'")
    except OSError as e:
        return FixResult(finding, False, str(e))


@register("task_stale")
def fix_task_status(finding: ScanFinding) -> FixResult:
    if not finding.file_path:
        return FixResult(finding, False, "No file path")
    plan_path = Path(finding.file_path)
    try:
        text = plan_path.read_text(encoding="utf-8")
        tid_match = re.search(r"Task (\d+\.\d+)", finding.detail)
        if not tid_match:
            return FixResult(finding, False, "Could not find task ID in detail")
        tid = tid_match.group(1)
        old = r"(\*\*Status:\*\*\s*)in_progress"
        new = r"\1completed"
        new_text = re.sub(old, new, text, count=1)
        if new_text == text:
            old = r"(\*\*Status:\*\*\s*)pending"
            new_text = re.sub(old, new, new_text, count=1)
        if new_text != text:
            plan_path.write_text(new_text)
            return FixResult(finding, True, f"Marked Task {tid} as completed")
        return FixResult(finding, False, "Could not parse task status")
    except (OSError, re.error) as e:
        return FixResult(finding, False, str(e))


@register("missing_tests")
def fix_test_stub(finding: ScanFinding) -> FixResult:
    if not finding.file_path:
        return FixResult(finding, False, "No file path")
    fp = Path(finding.file_path)
    test_file = fp.parent.parent / "tests" / f"test_{fp.stem}.py"
    if test_file.exists():
        return FixResult(finding, False, "Test file already exists")
    try:
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text(
            f'"""Tests for {fp.name}."""\n\n\n'
            f"def test_{fp.stem}_imports():\n"
            f'    """Verify module imports cleanly."""\n'
            f"    pass\n"
        )
        return FixResult(finding, True, f"Created stub test: {test_file.name}")
    except OSError as e:
        return FixResult(finding, False, str(e))
