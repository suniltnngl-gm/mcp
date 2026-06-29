#!/usr/bin/env python3
"""
AI Orchestra - Error Monitoring Script

This script periodically runs the reality checker and alerts the user to new error patterns.
"""

import json
import time
from pathlib import Path

from reality_checker import RealityChecker


class ErrorMonitor:
    """Monitors for new error patterns and alerts the user."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.reality_checker = RealityChecker(str(project_root))
        self.error_learning_path = (
            self.project_root / "reality_checks" / "error_learning.json"
        )
        self.known_errors = self._load_known_errors()

    def _load_known_errors(self):
        """Loads known error patterns from the error_learning.json file."""
        if self.error_learning_path.exists():
            with open(self.error_learning_path) as f:
                return json.load(f).get("learned_errors", {})
        return {}

    def _save_known_errors(self):
        """Saves known error patterns to the error_learning.json file."""
        with open(self.error_learning_path, "w") as f:
            json.dump({"learned_errors": self.known_errors}, f, indent=2)

    def monitor_for_errors(self, interval: int = 60):
        """Periodically runs the reality checker and alerts on new errors."""
        print(f"Monitoring for new error patterns every {interval} seconds...")
        try:
            while True:
                print("\nRunning reality check...")
                # Run reality check on all python files
                python_files = list(self.project_root.glob("**/*.py"))
                python_files = [str(f) for f in python_files if ".venv" not in str(f)]

                report = self.reality_checker.perform_reality_check(
                    "monitoring", python_files
                )

                new_errors_found = False
                for validation in report.metadata_validations:
                    if (
                        not validation.is_valid
                        and validation.validation_type not in self.known_errors
                    ):
                        print(
                            f"🚨 New Error Found: {validation.issues[0]} (Type: {validation.validation_type})"
                        )
                        self.known_errors[validation.validation_type] = {
                            "error": validation.issues[0],
                            "cause": f"Failed validation rule: {validation.validation_type}",
                            "prevention": f"Run reality checker for {validation.validation_type}",
                            "validation": f"python reality_checker.py --validate {validation.item_id}",
                        }
                        new_errors_found = True

                if new_errors_found:
                    self._save_known_errors()
                    print("Updated error knowledge base with new patterns.")
                else:
                    print("No new error patterns found.")

                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nError monitoring stopped.")


def main():
    """Main function to run the error monitor."""
    import argparse

    parser = argparse.ArgumentParser(description="Monitor for new error patterns.")
    parser.add_argument(
        "--interval", type=int, default=60, help="Monitoring interval in seconds."
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    monitor = ErrorMonitor(project_root)
    monitor.monitor_for_errors(args.interval)


if __name__ == "__main__":
    main()
