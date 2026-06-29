import subprocess
from pathlib import Path

from rich.console import Console

console = Console()


class DevWorkflow:
    """Automates AI Orchestra development workflows."""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def run_command_with_output(
        self, cmd: list[str], description: str
    ) -> tuple[bool, str, str]:
        """Run command and capture output."""
        try:
            result = subprocess.run(
                cmd, cwd=self.project_root, capture_output=True, text=True, timeout=300
            )

            success = result.returncode == 0
            return success, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
