#!/usr/bin/env python3
"""
📊 AI Orchestra - Dependency Checker
===================================

Checks for outdated dependencies using uv.
"""

import argparse
import json
import subprocess
from pathlib import Path

from logging_config import setup_logging

# Setup logger
logger = setup_logging(__name__)


def check_dependencies(project_root: Path) -> dict:
    """Checks for outdated dependencies and returns a summary."""
    logger.info("📊 Checking for outdated dependencies...")
    results = {"outdated_packages": [], "error": None}

    try:
        process = subprocess.run(
            ["uv", "pip", "list", "--outdated"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True,
        )

        # The output of `uv pip list --outdated` is a table.
        # We can parse this to get the package names and versions.
        lines = process.stdout.strip().splitlines()
        if len(lines) > 2:  # Header and separator lines
            for line in lines[2:]:
                parts = line.split()
                if len(parts) >= 4:
                    results["outdated_packages"].append(
                        {
                            "package": parts[0],
                            "current_version": parts[1],
                            "latest_version": parts[3],
                        }
                    )

        if results["outdated_packages"]:
            logger.warning(
                f"Found {len(results['outdated_packages'])} outdated packages."
            )
        else:
            logger.info("✅ All dependencies are up-to-date.")

    except FileNotFoundError:
        results["error"] = "uv is not installed or not in PATH."
        logger.error(results["error"])
    except subprocess.CalledProcessError as e:
        # A non-zero exit code from `uv pip list --outdated` can sometimes just mean no packages are installed
        if "no installed packages" in e.stdout.lower():
            logger.info("✅ No packages installed, so none are outdated.")
        else:
            results["error"] = e.stderr or e.stdout
            logger.error(f"Error checking dependencies: {results['error']}")
    except Exception as e:
        results["error"] = str(e)
        logger.exception(f"An unexpected error occurred: {e}")

    return results


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Dependency Checker")
    parser.add_argument(
        "--context-in", type=str, help="Path to the input context file."
    )
    parser.parse_args()

    project_root = Path(__file__).parent.parent
    results = check_dependencies(project_root)

    # Output the results as a JSON object for the orchestrator
    output_context = {"dependency_check_results": results}
    print(json.dumps(output_context))

    # Exit with a non-zero code if there are outdated packages or an error occurred
    if results["outdated_packages"] or results["error"]:
        exit(1)


if __name__ == "__main__":
    main()
