#!/usr/bin/env python3

import json
import subprocess
import os
import sys  # Added import for sys
from pathlib import Path
import logging  # Added this line


class AutomatedCorrection:
    def __init__(self):
        self.kb_dir = Path(__file__).parent.parent / "knowledge_base"
        self.solutions_file = self.kb_dir / "solutions.json"
        self.solutions = self._load_solutions()

    def _load_solutions(self):
        """Load solutions from knowledge base"""
        if not self.solutions_file.exists():
            return {}
        try:
            with open(self.solutions_file, "r") as f:
                return json.load(f)
        except json.decoder.JSONDecodeError as e:
            logging.error(
                f"Malformed JSON in {self.solutions_file}: {e}", exc_info=True
            )
            return {}
        except Exception as e:
            logging.error(
                f"An unexpected error occurred while loading {self.solutions_file}: {e}",
                exc_info=True,
            )
            return {}

    def detect_and_fix(self, error_type, context, error_message=""):
        """Main correction workflow: detect issue and apply fix"""

        # Find matching solution
        solution = self._find_solution(error_type, context, error_message)
        if not solution:
            return {"fixed": False, "reason": "No solution found"}

        # Apply correction
        result = self._apply_correction(solution, context)

        # Validate fix
        if result["applied"]:
            validation = self._validate_fix(error_type, context)
            result["validated"] = validation

            # Update solution effectiveness
            self._update_effectiveness(solution["id"], validation)

        return result

    def _find_solution(self, error_type, context, error_message):
        """Find best matching solution from knowledge base"""

        for solution_id, solution in self.solutions.items():
            # Match by error type
            if solution.get("error_type") == error_type:
                # Check context relevance
                if self._context_matches(solution.get("context", ""), context):
                    return {"id": solution_id, **solution}

        return None

    def _context_matches(self, solution_context, current_context):
        """Check if solution context matches current situation"""
        if not solution_context:
            return True

        # Check if solution_context is a substring of current_context (case-insensitive)
        return solution_context.lower() in current_context.lower()

    def _apply_correction(self, solution, context):
        """Apply the correction solution"""

        fix_command = solution.get("fix_command", "")
        if not fix_command:
            return {"applied": False, "reason": "No fix command"}

        try:
            # Replace context variables in command
            fix_command = fix_command.replace("{context}", context)

            # Execute fix
            result = subprocess.run(
                fix_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                check=True,  # Raise CalledProcessError for non-zero exit codes
            )

            return {
                "applied": True,  # If check=True, then applied is True on success
                "command": fix_command,
                "output": result.stdout,
                "error": result.stderr,
            }

        except subprocess.CalledProcessError as e:
            logging.error(
                f"Fix command failed: {e.cmd}\nStdout: {e.stdout}\nStderr: {e.stderr}",
                exc_info=True,
            )
            return {"applied": False, "reason": f"Fix command failed: {e.stderr}"}
        except subprocess.TimeoutExpired as e:
            logging.error(
                f"Fix command timed out: {e.cmd}\nStdout: {e.stdout}\nStderr: {e.stderr}",
                exc_info=True,
            )
            return {"applied": False, "reason": "Fix command timed out"}
        except Exception as e:
            logging.error(
                f"An unexpected error occurred during fix application: {e}",
                exc_info=True,
            )
            return {"applied": False, "reason": f"Unexpected error: {e}"}

    def _validate_fix(self, error_type, context):
        """Validate that the fix resolved the issue"""

        # Run basic validation based on error type
        validation_commands = {
            "missing_file": f"test -f {context}",
            "permissions": f"test -r {context}",
            "missing_directory": f"test -d {context}",
            "command_not_found": f"command -v {context.split()[0]} >/dev/null",
        }

        cmd = validation_commands.get(error_type, "true")

        try:
            subprocess.run(
                cmd, shell=True, capture_output=True, check=True
            )  # Added check=True
            return True  # If check=True, then True on success
        except subprocess.CalledProcessError as e:
            logging.warning(
                f"Validation command failed for {error_type}: {e.cmd}\nStdout: {e.stdout}\nStderr: {e.stderr}",
                exc_info=True,
            )
            return False
        except Exception as e:
            logging.error(
                f"An unexpected error occurred during validation for {error_type}: {e}",
                exc_info=True,
            )
            return False

    def _update_effectiveness(self, solution_id, success):
        """Update solution effectiveness tracking"""

        if solution_id not in self.solutions:
            logging.warning(
                f"Attempted to update effectiveness for unknown solution_id: {solution_id}"
            )
            return

        solution = self.solutions[solution_id]

        # Initialize tracking if not exists
        if "effectiveness" not in solution:
            solution["effectiveness"] = {"successes": 0, "failures": 0}

        # Update counters
        if success:
            solution["effectiveness"]["successes"] += 1
        else:
            solution["effectiveness"]["failures"] += 1

        # Save updated solutions
        try:
            with open(self.kb_dir / "solutions.json", "w") as f:
                json.dump(self.solutions, f, indent=2)
        except Exception as e:
            logging.error(
                f"Failed to save updated solutions to {self.kb_dir / 'solutions.json'}: {e}",
                exc_info=True,
            )


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Automated correction system")
    parser.add_argument("--error-type", required=True, help="Type of error to fix")
    parser.add_argument("--context", required=True, help="Error context")
    parser.add_argument("--error-message", default="", help="Error message")

    args = parser.parse_args()

    try:  # Added try block
        corrector = AutomatedCorrection()
        result = corrector.detect_and_fix(
            args.error_type, args.context, args.error_message
        )

        if result.get("applied", False) and result.get("validated", False):
            print(f"✅ Issue automatically corrected: {args.error_type}")
            return 0
        else:
            print(f"❌ Could not auto-correct: {result.get('reason', 'Unknown')}")
            return 1
    except Exception as e:  # Added except block
        logging.critical(
            f"An unhandled error occurred in automated_correction.py: {e}",
            exc_info=True,
        )
        print(
            f"❌ An unhandled error occurred: {e}", file=sys.stderr
        )  # Added print to stderr
        return 1  # Return non-zero exit code for error


if __name__ == "__main__":
    exit(main())
