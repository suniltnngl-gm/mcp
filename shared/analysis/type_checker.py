import json
import subprocess
from pathlib import Path

from logging_config import setup_logging

logger = setup_logging(__name__)


class TypeChecker:
    """Handles MyPy type checking."""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def run_mypy_check(self) -> tuple[bool, str, list[dict]]:
        """Run MyPy type checking."""
        logger.info("🔍 Running MyPy type checking...")

        try:
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "mypy",
                    ".",
                    "--ignore-missing-imports",
                    "--json-report",
                    "/tmp/mypy-report",
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            issues = []
            try:
                # Try to parse JSON report
                with open("/tmp/mypy-report/index.json") as f:
                    mypy_data = json.load(f)
                    issues = mypy_data.get("files", {})
            except (FileNotFoundError, json.JSONDecodeError):
                # Fallback to parsing stdout
                if result.stdout:
                    issues = [{"file": "stdout", "message": result.stdout}]

            success = result.returncode == 0
            message = (
                "Type checking passed" if success else "Type checking found issues"
            )

            return success, message, issues

        except Exception as e:
            return False, str(e), []
