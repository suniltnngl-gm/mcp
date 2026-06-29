import shutil
from datetime import datetime, timedelta
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from scripts.config_manager import is_path_ignored

console = Console()


class MaintenanceMonitor:
    """Monitors and performs project maintenance."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logs_dir = project_root / "logs"

    def automated_maintenance(self) -> dict:
        """Run automated maintenance tasks."""
        console.print(Panel.fit("🔧 Automated Maintenance", style="bold blue"))

        maintenance_results = {}

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:

            total_tasks = 5
            task = progress.add_task("Running maintenance...", total=total_tasks)

            # 1. Clean up temporary files
            progress.update(task, description="Cleaning temporary files...")
            cleanup_success = self._cleanup_temp_files()
            maintenance_results["cleanup"] = {"success": cleanup_success}
            progress.advance(task)

            # 2. Update .gitignore if needed
            progress.update(task, description="Checking .gitignore...")
            gitignore_updated = self._ensure_gitignore_complete()
            maintenance_results["gitignore"] = {"updated": gitignore_updated}
            progress.advance(task)

            # 3. Log rotation
            progress.update(task, description="Rotating logs...")
            logs_rotated = self._rotate_logs()
            maintenance_results["logs"] = {"rotated": logs_rotated}
            progress.advance(task)

            # 4. Database maintenance
            progress.update(task, description="Database maintenance...")
            db_status = self._maintain_database()
            maintenance_results["database"] = db_status
            progress.advance(task)

            # 5. Generate summary
            progress.update(task, description="Generating summary...")
            summary = self._generate_maintenance_summary(maintenance_results)
            maintenance_results["summary"] = summary
            progress.advance(task)

        return maintenance_results

    def _cleanup_temp_files(self) -> bool:
        """Clean up temporary files based on .aiignore patterns."""
        try:
            # Use patterns that should be cleaned up (based on .aiignore)
            cleanup_patterns = [
                "**/__pycache__",
                "**/*.pyc",
                "**/*.pyo",
                "**/.pytest_cache",
                "**/tmp_*",
                "**/*.tmp",
                "**/*.log",  # Clean old logs
            ]

            cleaned_count = 0
            for pattern in cleanup_patterns:
                for path in self.project_root.glob(pattern):
                    # Double-check with .aiignore - only clean if it would be ignored
                    if is_path_ignored(path):
                        try:
                            if path.is_file():
                                path.unlink()
                                cleaned_count += 1
                            elif path.is_dir():
                                shutil.rmtree(path)
                                cleaned_count += 1
                        except Exception:
                            # Skip files we can't delete
                            continue

            console.print(f"  ✅ Cleaned {cleaned_count} temporary files/directories")
            return True

        except Exception as e:
            console.print(f"  ❌ Cleanup failed: {e}")
            return False

    def _ensure_gitignore_complete(self) -> bool:
        """Ensure .gitignore is consistent with .aiignore patterns."""
        gitignore_file = self.project_root / ".gitignore"
        aiignore_file = self.project_root / ".aiignore"

        # Critical entries that MUST be in .gitignore for security
        critical_entries = [".env", "*.key", "*.pem"]

        if not gitignore_file.exists():
            if aiignore_file.exists():
                # Copy .aiignore patterns to .gitignore as a starting point
                aiignore_content = aiignore_file.read_text()
                gitignore_file.write_text(
                    f"# Generated from .aiignore\\n{aiignore_content}"
                )
                console.print("  ✅ Created .gitignore from .aiignore patterns")
            else:
                # Fallback: create basic .gitignore
                basic_patterns = [".env", "__pycache__/", "*.pyc", ".venv/"]
                gitignore_file.write_text("\\n".join(basic_patterns) + "\\n")
                console.print("  ✅ Created basic .gitignore")
            return True

        current_content = gitignore_file.read_text()

        # Ensure critical entries are present
        missing_critical = [
            entry for entry in critical_entries if entry not in current_content
        ]

        if missing_critical:
            with gitignore_file.open("a") as f:
                f.write("\\n# Critical entries added by maintenance\\n")
                for entry in missing_critical:
                    f.write(f"{entry}\\n")

            console.print(
                f"  ✅ Added {len(missing_critical)} critical entries to .gitignore"
            )
            return True

        console.print("  ✅ .gitignore appears complete")
        return False

    def _rotate_logs(self) -> int:
        """Rotate old log files."""
        if not self.logs_dir.exists():
            return 0

        rotated_count = 0
        cutoff_date = datetime.now() - timedelta(days=7)

        for log_file in self.logs_dir.glob("*.log"):
            if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff_date:
                # Compress and move old logs
                archive_name = (
                    f"{log_file.stem}_{datetime.now().strftime('%Y%m%d')}.log.old"
                )
                archive_path = self.logs_dir / archive_name
                log_file.rename(archive_path)
                rotated_count += 1

        if rotated_count > 0:
            console.print(f"  ✅ Rotated {rotated_count} old log files")
        else:
            console.print("  ✅ No log files need rotation")

        return rotated_count

    def _maintain_database(self) -> dict:
        """Perform database maintenance."""
        db_file = self.project_root / "ai_orchestra.db"

        if not db_file.exists():
            return {"exists": False, "size": 0, "maintenance_needed": False}

        # Get database size
        db_size = db_file.stat().st_size

        # Simple maintenance check
        maintenance_needed = db_size > 10 * 1024 * 1024  # 10MB threshold

        if maintenance_needed:
            console.print("  ⚠️ Database is large - consider cleanup")
        else:
            console.print("  ✅ Database size is acceptable")

        return {
            "exists": True,
            "size": db_size,
            "size_mb": db_size / (1024 * 1024),
            "maintenance_needed": maintenance_needed,
        }

    def _generate_maintenance_summary(self, results: dict) -> dict:
        """Generate maintenance summary."""
        total_tasks = len(results) - 1  # Exclude summary itself
        successful_tasks = sum(
            1
            for task in results.values()
            if isinstance(task, dict) and task.get("success", True)
        )

        return {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "success_rate": successful_tasks / total_tasks if total_tasks > 0 else 1.0,
            "timestamp": datetime.now().isoformat(),
        }
