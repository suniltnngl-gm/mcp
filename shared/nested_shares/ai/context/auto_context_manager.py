#!/usr/bin/env python3
"""
🧠 Automated Context Manager - Enhanced CRS System
================================================

Automatically captures and preserves project context to prevent information loss
during context resets. Goes beyond manual CRS updates.
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


class AutoContextManager:
    """Automated context preservation system."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.context_dir = self.project_root / "CRS"
        self.context_dir.mkdir(exist_ok=True)

    def capture_full_context(self) -> dict[str, Any]:
        """Capture comprehensive project context automatically."""
        context = {
            "timestamp": datetime.now().isoformat(),
            "git_status": self._get_git_status(),
            "recent_changes": self._get_recent_changes(),
            "project_stats": self._get_project_stats(),
            "environment": self._get_environment_info(),
            "dependencies": self._get_dependency_status(),
            "active_branches": self._get_branch_info(),
            "recent_commits": self._get_recent_commits(),
            "file_changes": self._get_file_changes(),
            "api_status": self._get_api_status(),
            "next_actions": self._extract_next_actions(),
        }
        return context

    def _get_git_status(self) -> dict[str, Any]:
        """Get current git status."""
        try:
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            branch = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            return {
                "current_branch": branch.stdout.strip(),
                "uncommitted_files": (
                    status.stdout.strip().split("\n") if status.stdout.strip() else []
                ),
                "is_clean": len(status.stdout.strip()) == 0,
            }
        except:
            return {"error": "Git not available"}

    def _get_recent_changes(self) -> list[str]:
        """Get recent file modifications."""
        try:
            # Files modified in last 24 hours
            result = subprocess.run(
                [
                    "find",
                    ".",
                    "-name",
                    "*.py",
                    "-o",
                    "-name",
                    "*.md",
                    "-o",
                    "-name",
                    "*.sh",
                    "-mtime",
                    "-1",
                    "-not",
                    "-path",
                    "./.venv/*",
                    "-not",
                    "-path",
                    "./.git/*",
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            return result.stdout.strip().split("\n") if result.stdout.strip() else []
        except:
            return []

    def _get_project_stats(self) -> dict[str, int]:
        """Get current project statistics."""
        try:
            # Count user-created Python files only (exclude .venv, cache, dependencies)
            py_files = subprocess.run(
                [
                    "find",
                    ".",
                    "-name",
                    "*.py",
                    "-not",
                    "-path",
                    "./.venv/*",
                    "-not",
                    "-path",
                    "./__pycache__/*",
                    "-not",
                    "-path",
                    "./~/*",
                    "-not",
                    "-path",
                    "./.git/*",
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            # Filter out dependency files in cache directories
            py_lines = (
                py_files.stdout.strip().split("\n") if py_files.stdout.strip() else []
            )
            user_py_files = [
                f
                for f in py_lines
                if not any(
                    x in f for x in ["/cache/", "/archive-v0/", "setuptools", "pip-"]
                )
            ]

            md_files = subprocess.run(
                ["find", ".", "-maxdepth", "1", "-name", "*.md"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            return {
                "python_files": len(user_py_files),
                "documentation_files": (
                    len(md_files.stdout.strip().split("\n"))
                    if md_files.stdout.strip()
                    else 0
                ),
                "total_size_mb": self._get_directory_size(),
            }
        except:
            return {"error": "Could not get stats"}

    def _get_directory_size(self) -> float:
        """Get directory size in MB."""
        try:
            result = subprocess.run(
                ["du", "-sm", "."],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            return float(result.stdout.split()[0])
        except:
            return 0.0

    def _get_environment_info(self) -> dict[str, str]:
        """Get environment information."""
        return {
            "python_version": subprocess.run(
                ["python3", "--version"], capture_output=True, text=True
            ).stdout.strip(),
            "uv_version": (
                subprocess.run(
                    ["uv", "--version"], capture_output=True, text=True
                ).stdout.strip()
                if self._command_exists("uv")
                else "Not installed"
            ),
            "mise_version": (
                subprocess.run(
                    ["mise", "--version"], capture_output=True, text=True
                ).stdout.strip()
                if self._command_exists("mise")
                else "Not installed"
            ),
        }

    def _command_exists(self, command: str) -> bool:
        """Check if command exists."""
        return subprocess.run(["which", command], capture_output=True).returncode == 0

    def _get_dependency_status(self) -> dict[str, bool]:
        """Check key dependencies."""
        deps = ["rich", "openai", "anthropic", "psutil"]
        status = {}
        for dep in deps:
            try:
                subprocess.run(
                    ["python3", "-c", f"import {dep}"],
                    check=True,
                    capture_output=True,
                    cwd=self.project_root,
                )
                status[dep] = True
            except:
                status[dep] = False
        return status

    def _get_branch_info(self) -> list[str]:
        """Get all branches."""
        try:
            result = subprocess.run(
                ["git", "branch", "-a"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            return [line.strip() for line in result.stdout.split("\n") if line.strip()]
        except:
            return []

    def _get_recent_commits(self) -> list[str]:
        """Get recent commits."""
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-10"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            return result.stdout.strip().split("\n") if result.stdout.strip() else []
        except:
            return []

    def _get_file_changes(self) -> dict[str, list[str]]:
        """Get file changes by category."""
        try:
            # New files
            new_files = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            # Modified files
            modified = subprocess.run(
                ["git", "diff", "--name-only"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            return {
                "new_files": (
                    new_files.stdout.strip().split("\n")
                    if new_files.stdout.strip()
                    else []
                ),
                "modified_files": (
                    modified.stdout.strip().split("\n")
                    if modified.stdout.strip()
                    else []
                ),
            }
        except:
            return {"new_files": [], "modified_files": []}

    def _get_api_status(self) -> dict[str, str]:
        """Check API key status."""
        api_keys = [
            "GROQ_API_KEY",
            "CEREBRAS_API_KEY",
            "AI21_API_KEY",
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
        ]
        status = {}
        for key in api_keys:
            status[key] = "SET" if os.getenv(key) else "NOT_SET"
        return status

    def _extract_next_actions(self) -> list[str]:
        """Extract next actions from TODO and status files."""
        actions = []

        # Check TODO.md
        todo_file = self.context_dir / "TODO.md"
        if todo_file.exists():
            content = todo_file.read_text()
            # Extract unchecked items
            for line in content.split("\n"):
                if "- [ ]" in line:
                    actions.append(line.strip())

        return actions[:10]  # Top 10 actions

    def save_context(self) -> str:
        """Save current context to file."""
        context = self.capture_full_context()

        # Save as JSON for programmatic access
        json_file = (
            self.context_dir
            / f"auto_context_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(json_file, "w") as f:
            json.dump(context, f, indent=2)

        # Save as markdown for human reading
        md_file = self.context_dir / "LATEST_CONTEXT.md"
        self._save_as_markdown(context, md_file)

        return str(json_file)

    def _save_as_markdown(self, context: dict[str, Any], file_path: Path):
        """Save context as readable markdown."""
        md_content = f"""# 🧠 Auto-Generated Context Snapshot

**Generated:** {context['timestamp']}

## 🎯 Current Status

### Git Status
- **Branch:** {context['git_status'].get('current_branch', 'unknown')}
- **Clean:** {'✅' if context['git_status'].get('is_clean', False) else '❌'}
- **Uncommitted Files:** {len(context['git_status'].get('uncommitted_files', []))}

### Project Stats
- **Python Files:** {context['project_stats'].get('python_files', 0)}
- **Documentation:** {context['project_stats'].get('documentation_files', 0)}
- **Size:** {context['project_stats'].get('total_size_mb', 0)}MB

### Environment
- **Python:** {context['environment'].get('python_version', 'unknown')}
- **UV:** {context['environment'].get('uv_version', 'unknown')}
- **Mise:** {context['environment'].get('mise_version', 'unknown')}

## 🔑 API Keys Status
"""
        for key, status in context["api_status"].items():
            md_content += f"- **{key}:** {'✅' if status == 'SET' else '❌'}\n"

        md_content += """
## 📝 Recent Changes
"""
        for file in context["recent_changes"][:10]:
            md_content += f"- {file}\n"

        md_content += """
## 🚀 Next Actions
"""
        for action in context["next_actions"]:
            md_content += f"{action}\n"

        md_content += """
## 📊 Recent Commits
"""
        for commit in context["recent_commits"][:5]:
            md_content += f"- {commit}\n"

        file_path.write_text(md_content)

    def get_recovery_info(self) -> str:
        """Get quick recovery information."""
        context = self.capture_full_context()

        recovery_info = f"""
🧠 QUICK RECOVERY INFO:

📍 Current State:
- Branch: {context['git_status'].get('current_branch')}
- Files: {context['project_stats'].get('python_files')} Python, {context['project_stats'].get('documentation_files')} docs
- APIs: {sum(1 for v in context['api_status'].values() if v == 'SET')}/{len(context['api_status'])} configured

🎯 Immediate Actions:
{chr(10).join(context['next_actions'][:3])}

🔧 Quick Start:
1. uv run python ai_health_monitor.py status
2. uv run python demo_full_system.py
3. Check CRS/LATEST_CONTEXT.md for details
"""
        return recovery_info


def main():
    """CLI interface for auto context manager."""
    import sys

    manager = AutoContextManager()

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "save":
            file_path = manager.save_context()
            print(f"✅ Context saved to: {file_path}")
        elif command == "recovery":
            print(manager.get_recovery_info())
        else:
            print("Usage: python auto_context_manager.py [save|recovery]")
    else:
        # Default: save context
        file_path = manager.save_context()
        print(f"✅ Context saved to: {file_path}")
        print("\n" + manager.get_recovery_info())


if __name__ == "__main__":
    main()
