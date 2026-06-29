#!/usr/bin/env python3
"""
AI Orchestra - Learning Workflow

This module provides a workflow for learning from errors in the codebase.
"""

import glob
import os
from pathlib import Path

from reality_checker import RealityChecker


class LearningWorkflow:
    """Workflow for learning from errors."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.reality_checker = RealityChecker(str(project_root))

    def learn_from_errors(self):
        """Run the reality checker on all Python files to learn from errors."""
        print("🧠 Starting the learning process...")

        python_files = glob.glob(
            os.path.join(self.project_root, "**/*.py"), recursive=True
        )

        # Filter out files in .venv
        python_files = [f for f in python_files if ".venv" not in f]

        report = self.reality_checker.perform_reality_check("learning", python_files)

        # Update codebase_metadata.json with new metrics
        codebase_metadata_path = (
            self.project_root / "knowledge_base" / "codebase_metadata.json"
        )
        if codebase_metadata_path.exists():
            with open(codebase_metadata_path, "r+") as f:
                metadata = json.load(f)
                metadata["code_metrics"] = report.code_metrics
                f.seek(0)
                json.dump(metadata, f, indent=2)

        print("✅ Learning process completed.")
