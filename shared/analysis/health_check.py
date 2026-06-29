import subprocess
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


class HealthChecker:
    """Handles AI Orchestra health checks."""

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

    def health_check_workflow(self) -> dict:
        """Complete health check workflow."""
        console.print(Panel.fit("🎭 AI Orchestra Health Check", style="bold green"))

        checks = {}

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
        ) as progress:

            total_checks = 6
            task = progress.add_task("Running health checks...", total=total_checks)

            # 1. Check Python environment
            progress.update(task, description="Checking Python environment...")
            success, stdout, stderr = self.run_command_with_output(
                ["uv", "run", "python", "--version"], "Python version check"
            )
            checks["python"] = {
                "success": success,
                "output": stdout.strip(),
                "error": stderr,
            }
            progress.advance(task)

            # 2. Check dependencies
            progress.update(task, description="Checking dependencies...")
            success, stdout, stderr = self.run_command_with_output(
                [
                    "uv",
                    "run",
                    "python",
                    "-c",
                    "import enhanced_orchestra; print('Core modules OK')",
                ],
                "Dependencies check",
            )
            checks["dependencies"] = {
                "success": success,
                "output": stdout.strip(),
                "error": stderr,
            }
            progress.advance(task)

            # 3. Check database
            progress.update(task, description="Checking database...")
            db_exists = (self.project_root / "ai_orchestra.db").exists()
            checks["database"] = {
                "success": True,
                "output": (
                    "Database exists"
                    if db_exists
                    else "Database will be created on first run"
                ),
                "error": "",
            }
            progress.advance(task)

            # 4. Check configuration
            progress.update(task, description="Checking configuration...")
            env_exists = (self.project_root / ".env").exists()
            checks["config"] = {
                "success": env_exists,
                "output": (
                    "Configuration file exists"
                    if env_exists
                    else "No .env configuration"
                ),
                "error": "Run setup to create .env file" if not env_exists else "",
            }
            progress.advance(task)

            # 5. Check Git status
            progress.update(task, description="Checking Git status...")
            success, stdout, stderr = self.run_command_with_output(
                ["git", "status", "--porcelain"], "Git status check"
            )
            git_clean = success and not stdout.strip()
            checks["git"] = {
                "success": True,
                "output": (
                    "Working directory clean"
                    if git_clean
                    else f"{len(stdout.splitlines())} files changed"
                ),
                "error": stderr,
            }
            progress.advance(task)

            # 6. Quick functionality test
            progress.update(task, description="Testing core functionality...")
            success, stdout, stderr = self.run_command_with_output(
                [
                    "uv",
                    "run",
                    "python",
                    "-c",
                    "from enhanced_orchestra import EnhancedAIOrchestra; o = EnhancedAIOrchestra(); print('Core functionality OK')",
                ],
                "Core functionality test",
            )
            checks["functionality"] = {
                "success": success,
                "output": stdout.strip(),
                "error": stderr,
            }
            progress.advance(task)

        return checks

    def display_health_results(self, checks: dict):
        """Display health check results."""
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Details", style="white")

        for check_name, result in checks.items():
            status = "✅ OK" if result["success"] else "❌ ISSUE"
            status_style = "green" if result["success"] else "red"

            details = result["output"] or result["error"] or "No details"

            table.add_row(
                check_name.title(),
                f"[{status_style}]{status}[/{status_style}]",
                details[:50] + "..." if len(details) > 50 else details,
            )

        console.print(table)

        # Overall status
        all_healthy = all(check["success"] for check in checks.values())
        if all_healthy:
            console.print(Panel("🎉 System is healthy and ready!", style="bold green"))
        else:
            console.print(
                Panel(
                    "⚠️ Some issues detected. Review above for details.",
                    style="bold yellow",
                )
            )
