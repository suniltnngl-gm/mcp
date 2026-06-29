import subprocess
from pathlib import Path

from logging_config import setup_logging
from scripts.backup import BackupManager

logger = setup_logging(__name__)


class Formatter:
    """Handles code formatting using Black."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backup_manager = BackupManager(project_root)

    def run_black_format(self) -> tuple[bool, str]:
        """Run black code formatter."""
        logger.info("🎉 Running Black formatter...")

        # First, find which files will be changed
        try:
            check_result = subprocess.run(
                ["uv", "run", "black", ".", "--check"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )
            files_to_reformat = []
            if check_result.returncode != 0:
                for line in check_result.stdout.splitlines():
                    if line.startswith("would reformat"):
                        files_to_reformat.append(
                            self.project_root / line.split(" ")[-1]
                        )

            if files_to_reformat:
                logger.info(f"{len(files_to_reformat)} files will be reformatted.")
                self.backup_manager.create_backup(
                    "pre_black_formatting", files_to_backup=files_to_reformat
                )

        except Exception as e:
            logger.warning(f"Could not check for files to reformat: {e}")

        # Now, run the formatter
        try:
            result = subprocess.run(
                ["uv", "run", "black", "."],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                return True, "Code formatting successful"
            else:
                return False, result.stderr or result.stdout

        except Exception as e:
            return False, str(e)
