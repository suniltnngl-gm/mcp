import subprocess
from datetime import datetime
from pathlib import Path

from rich.console import Console

console = Console()


class DependencyMonitor:
    """Monitors project dependencies."""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def run_command(self, cmd: list[str], timeout: int = 60) -> tuple[bool, str, str]:
        """Run command with timeout."""
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)

    def check_dependencies(self) -> dict:
        """Check dependency status and updates."""
        console.print("📦 Checking dependencies...")

        # Get current dependency tree
        success, tree_output, error = self.run_command(["uv", "tree"])

        # Get lock file info
        lock_file = self.project_root / "uv.lock"
        lock_exists = lock_file.exists()
        lock_age = None

        if lock_exists:
            lock_mtime = lock_file.stat().st_mtime
            lock_age = datetime.now() - datetime.fromtimestamp(lock_mtime)

        # Check for outdated packages (simplified check)
        outdated_info = (
            "Manual check required - uv doesn't have built-in outdated command"
        )

        return {
            "tree_available": success,
            "tree_output": (
                tree_output[:500] + "..." if len(tree_output) > 500 else tree_output
            ),
            "lock_exists": lock_exists,
            "lock_age_days": lock_age.days if lock_age else None,
            "outdated_info": outdated_info,
            "error": error,
        }

    def dependency_update_check(self) -> dict:
        """Check for dependency updates and security advisories."""
        console.print("🔄 Checking for dependency updates...")

        update_info = {}

        # Read current dependencies from pyproject.toml
        pyproject_file = self.project_root / "pyproject.toml"
        if pyproject_file.exists():
            try:
                content = pyproject_file.read_text()

                # Simple parsing for dependencies (would need proper TOML parser in production)
                dependencies = []
                in_dependencies = False
                for line in content.split("\n"):
                    if "dependencies = [" in line:
                        in_dependencies = True
                    elif in_dependencies and "]" in line:
                        in_dependencies = False
                    elif in_dependencies and '"' in line:
                        # Extract package name
                        package = line.split('"')[1].split(">=")[0].split("==")[0]
                        dependencies.append(package)

                update_info["current_dependencies"] = dependencies
                update_info["dependency_count"] = len(dependencies)

            except Exception as e:
                update_info["parse_error"] = str(e)

        # Check lock file age
        lock_file = self.project_root / "uv.lock"
        if lock_file.exists():
            lock_age = datetime.now() - datetime.fromtimestamp(
                lock_file.stat().st_mtime
            )
            update_info["lock_age_days"] = lock_age.days
            update_info["lock_needs_update"] = lock_age.days > 7

        return update_info
