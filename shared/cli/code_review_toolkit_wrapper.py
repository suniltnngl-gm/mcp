#!/usr/bin/env python3

import sys
from pathlib import Path

# Add devflow-intelligence src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Add toolkit to path
# This should be handled by installing the toolkit as a package
# toolkit_path = Path("/media/sunil-kr/storage/workspace/tools/code-review-toolkit/src")
# sys.path.insert(0, str(toolkit_path))

from code_review_toolkit.ai_reviewer import AICodeReviewer
from code_review_toolkit.pattern_learner import PatternLearner


def run_code_review_and_learn(target_path: Path):
    """
    Runs AICodeReviewer on the target path, captures its findings, and feeds them to PatternRecognizer.
    """
    try:
        # 1. Instantiate PatternLearner
        pattern_learner = PatternLearner()

        # 2. Instantiate AICodeReviewer with the learner
        reviewer = AICodeReviewer(
            provider="gemini_api",
            repo_root=target_path,
            pattern_learner=pattern_learner
        )

        # 3. Run the review. The learning process is now handled within the reviewer.
        findings = reviewer.review_directory(
            target_dir=target_path,
            aspects=["security", "performance", "maintainability", "hardcoded_secrets"]
        )

        print(f"Review complete. Found {len(findings)} findings.")

    except Exception as e:
        print(f"An unexpected error occurred during code review: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: code_review_toolkit_wrapper.py <path_to_review>")
        print("Example: code_review_toolkit_wrapper.py /path/to/my/project")
        sys.exit(1)

    target_path = Path(sys.argv[1])
    if not target_path.is_dir():
        print(f"Error: {target_path} is not a valid directory.")
        sys.exit(1)

    run_code_review_and_learn(target_path)
