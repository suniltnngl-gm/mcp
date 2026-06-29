#!/usr/bin/env python3

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

# Add devflow-intelligence src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from intelligence.pattern_recognition import PatternRecognizer


def run_gadd_and_learn(gadd_path: Path, files_to_add: list[str]):
    """
    Runs gadd with --json-output, captures its findings, and feeds them to PatternRecognizer.
    """
    # Determine the Git repository root from the first file_to_add
    if files_to_add:
        first_file_path = Path(files_to_add[0])
        current_dir = Path.cwd()
        abs_first_file_path = (current_dir / first_file_path).resolve()

        git_repo_root = None
        for parent in abs_first_file_path.parents:
            if (parent / ".git").is_dir():
                git_repo_root = parent
                break

        if not git_repo_root:
            print(f"Error: Could not find Git repository for {first_file_path}")
            return

        # Adjust files_to_add to be relative to the git_repo_root
        relative_files_to_add = []
        for f in files_to_add:
            abs_file_path = (Path.cwd() / f).resolve()  # Get absolute path of the file
            relative_files_to_add.append(str(abs_file_path.relative_to(git_repo_root)))
    else:
        git_repo_root = Path.cwd()  # Default to current directory if no files specified
        relative_files_to_add = []

    command = [str(gadd_path), "--json-output"] + relative_files_to_add

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,  # Don't raise exception for non-zero exit code
            cwd=git_repo_root,  # Execute gadd in the Git repository root
        )

        if result.returncode != 0 and result.stdout.strip() == "[]":
            # gadd exited with error but no issues found (e.g., not in git repo, or other gadd error)
            print(f"Error running gadd: {result.stderr}")
            return

        findings_json = result.stdout.strip()

        if not findings_json:
            print("gadd returned no output.")
            return

        findings_raw = json.loads(findings_json)

        # Format findings for PatternRecognizer
        formatted_findings: list[dict[str, Any]] = []
        for finding in findings_raw:
            formatted_findings.append(
                {
                    "file": finding.get("file", "unknown"),
                    "severity": "medium",  # Default severity for gadd issues
                    "category": finding.get("issue_type", "gadd_issue"),
                    "issue": finding.get("description", "Gadd detected an issue."),
                    "suggestion": f"Review '{finding.get('file', 'unknown')}' for '{finding.get('issue_type', 'gadd_issue')}'",
                }
            )

        recognizer = PatternRecognizer()
        recognizer.learn_from_findings(
            formatted_findings, success=False
        )  # Assume findings indicate a problem
        print(
            f"Successfully learned from {len(formatted_findings)} gadd findings via PatternRecognizer."
        )

        # After learning, try to identify and store higher-level patterns
        recognizer.identify_and_store_patterns()

    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON from gadd output: {e}")
        print(f"gadd stdout: {result.stdout}")
        print(f"gadd stderr: {result.stderr}")
    except FileNotFoundError:
        print(f"Error: gadd script not found at {gadd_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    gadd_script_path = Path(__file__).parent.parent / "shared-tools" / "git" / "gadd"

    # Pass files to add from command line arguments, excluding the script name itself
    files_to_add = sys.argv[1:]

    if not files_to_add:
        print("Usage: gadd_wrapper.py [files_to_add...]")
        print("Example: gadd_wrapper.py .")
        sys.exit(1)

    run_gadd_and_learn(gadd_script_path, files_to_add)
