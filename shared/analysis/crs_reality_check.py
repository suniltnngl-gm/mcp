"""
✅ AI Orchestra - CRS Reality Check
===================================

Validates that the core CRS (Context, Reality, and Status) files are present and up-to-date.
"""

import argparse
import datetime
import json
from pathlib import Path

from logging_config import setup_logging

# Setup logger
logger = setup_logging(__name__)


class CRSRealityChecker:
    """Checks the status of CRS files."""

    def __init__(self, project_root: Path, context: dict):
        self.project_root = project_root
        self.crs_files = [
            "CRS/SESSION_NOTES.md",
            "CRS/STATUS_AND_NEXT_STEPS.md",
            "CRS/TODO.md",
        ]
        self.context = context

    def run_check(self) -> dict:
        """Runs the CRS reality check and returns a results dictionary."""
        logger.info("Running CRS reality check...")
        results = {"files_checked": [], "all_ok": True}

        for file_name in self.crs_files:
            file_path = self.project_root / file_name
            file_status = {
                "file_name": file_name,
                "exists": False,
                "updated_today": False,
                "error": None,
            }
            if not file_path.exists():
                logger.error(f"❌ Missing CRS file: {file_name}")
                results["all_ok"] = False
            else:
                file_status["exists"] = True
                try:
                    with open(file_path) as f:
                        content = f.read()
                    if str(datetime.date.today()) not in content:
                        logger.warning(f"⚠️ CRS file not updated today: {file_name}")
                        results["all_ok"] = False
                    else:
                        logger.info(f"✅ CRS file up-to-date: {file_name}")
                        file_status["updated_today"] = True
                except Exception as e:
                    logger.error(f"Could not read file {file_name}: {e}")
                    results["all_ok"] = False
                    file_status["error"] = str(e)
            results["files_checked"].append(file_status)

        if results["all_ok"]:
            logger.info("✅ All CRS files are present and up-to-date.")
        else:
            logger.warning("CRS reality check failed. See warnings/errors above.")

        return results


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="CRS Reality Check")
    parser.add_argument(
        "--context-in", type=str, help="Path to the input context file."
    )
    args = parser.parse_args()

    context = {}
    if args.context_in:
        try:
            with open(args.context_in) as f:
                context = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Could not load context from {args.context_in}: {e}")

    project_root = Path(__file__).parent.parent
    checker = CRSRealityChecker(project_root, context)
    results = checker.run_check()

    # Output the results as a JSON object for the orchestrator
    output_context = {
        "crs_reality_check_passed": results["all_ok"],
        "crs_files_status": results["files_checked"],
    }
    print(json.dumps(output_context))

    if not results["all_ok"]:
        exit(1)


if __name__ == "__main__":
    main()
