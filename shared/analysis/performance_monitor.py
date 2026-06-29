import subprocess
from pathlib import Path

from rich.console import Console

from scripts.config_manager import is_path_ignored

console = Console()


class PerformanceMonitor:
    """Monitors project performance."""

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

    def performance_monitoring(self) -> dict:
        """Monitor project performance metrics."""
        console.print("📈 Monitoring performance...")

        metrics = {}

        # 1. Project size metrics
        console.print("  📊 Calculating project size...")
        python_files = list(self.project_root.rglob("*.py"))
        python_files = [f for f in python_files if not is_path_ignored(f)]

        total_lines = 0
        for py_file in python_files:
            try:
                total_lines += len(py_file.read_text().splitlines())
            except:
                continue

        metrics["project_size"] = {
            "python_files": len(python_files),
            "total_lines": total_lines,
            "avg_lines_per_file": (
                total_lines // len(python_files) if python_files else 0
            ),
        }

        # 2. Git metrics
        console.print("  📈 Analyzing git metrics...")
        git_metrics = {}

        # Recent commits
        success, commits_output, _ = self.run_command(
            ["git", "log", "--oneline", "--since=7.days.ago"]
        )

        if success:
            recent_commits = (
                len(commits_output.strip().split("\n")) if commits_output.strip() else 0
            )
            git_metrics["recent_commits"] = recent_commits

        # Repository size
        success, size_output, _ = self.run_command(["git", "count-objects", "-vH"])

        if success:
            git_metrics["repo_info"] = size_output

        metrics["git"] = git_metrics

        # 3. Test coverage estimation
        console.print("  🧪 Estimating test coverage...")
        test_files = list(self.project_root.rglob("test_*.py"))
        test_files.extend(self.project_root.rglob("*_test.py"))

        metrics["testing"] = {
            "test_files": len(test_files),
            "test_coverage_ratio": (
                len(test_files) / len(python_files) if python_files else 0
            ),
        }

        return metrics
