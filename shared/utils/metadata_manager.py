#!/usr/bin/env python3
"""Metadata manager for knowledge base enrichment and reality checks"""

import json
import os
from datetime import datetime
from pathlib import Path


class MetadataManager:
    def __init__(self):
        self.kb_dir = Path("knowledge_base")
        self.metadata_file = self.kb_dir / "metadata.json"

    def enrich_error_metadata(self, error_id, context_data):
        """Enrich error with contextual metadata"""
        metadata = self._load_metadata()

        if "errors" not in metadata:
            metadata["errors"] = {}

        metadata["errors"][error_id] = {
            "context": {
                "system_state": context_data.get("system_state", {}),
                "environment": context_data.get("environment", {}),
                "preconditions": context_data.get("preconditions", []),
                "user_intent": context_data.get("user_intent", ""),
                "execution_path": context_data.get("execution_path", []),
            },
            "reality_check": {
                "verified": False,
                "confidence": 0.5,
                "validation_attempts": 0,
                "false_positives": 0,
                "context_mismatches": [],
            },
            "learning_metadata": {
                "complexity": "medium",
                "frequency_pattern": "sporadic",
                "impact_level": "medium",
                "resolution_time": None,
                "similar_cases": [],
            },
        }

        self._save_metadata(metadata)

    def validate_solution_reality(self, error_id, solution_id, validation_result):
        """Validate solution effectiveness with reality checks"""
        metadata = self._load_metadata()

        if "solutions" not in metadata:
            metadata["solutions"] = {}

        if solution_id not in metadata["solutions"]:
            metadata["solutions"][solution_id] = {
                "reality_checks": [],
                "context_dependencies": [],
                "failure_modes": [],
                "success_conditions": [],
            }

        # Add reality check result
        reality_check = {
            "timestamp": datetime.now().isoformat(),
            "error_id": error_id,
            "success": validation_result.get("success", False),
            "context": validation_result.get("context", {}),
            "side_effects": validation_result.get("side_effects", []),
            "environment_factors": validation_result.get("environment", {}),
        }

        metadata["solutions"][solution_id]["reality_checks"].append(reality_check)

        # Update confidence based on reality checks
        success_rate = self._calculate_success_rate(
            metadata["solutions"][solution_id]["reality_checks"]
        )
        metadata["solutions"][solution_id]["confidence"] = success_rate

        self._save_metadata(metadata)
        return success_rate

    def detect_misunderstandings(self):
        """Detect potential misunderstandings in knowledge base"""
        metadata = self._load_metadata()
        misunderstandings = []

        # Check for low-confidence solutions
        for solution_id, solution_meta in metadata.get("solutions", {}).items():
            if solution_meta.get("confidence", 1.0) < 0.6:
                misunderstandings.append(
                    {
                        "type": "low_confidence_solution",
                        "solution_id": solution_id,
                        "confidence": solution_meta.get("confidence", 0),
                        "issue": "Solution has low success rate in reality checks",
                    }
                )

        # Check for context mismatches
        for error_id, error_meta in metadata.get("errors", {}).items():
            context_mismatches = error_meta.get("reality_check", {}).get(
                "context_mismatches", []
            )
            if len(context_mismatches) > 2:
                misunderstandings.append(
                    {
                        "type": "context_mismatch",
                        "error_id": error_id,
                        "mismatches": len(context_mismatches),
                        "issue": "Error context frequently misunderstood",
                    }
                )

        return misunderstandings

    def generate_reality_check_plan(self):
        """Generate plan for systematic reality checks"""
        errors = self._load_json("errors.json")
        solutions = self._load_json("solutions.json")

        plan = {
            "validation_targets": [],
            "context_verification": [],
            "misunderstanding_prevention": [],
        }

        # Identify high-frequency errors for validation
        for error_id, error_data in errors.items():
            if error_data.get("frequency", 0) > 2:
                plan["validation_targets"].append(
                    {
                        "error_id": error_id,
                        "category": error_data.get("category", "unknown"),
                        "priority": "high",
                        "validation_method": "controlled_reproduction",
                    }
                )

        # Identify solutions needing context verification
        for error_id, solution_list in solutions.items():
            for i, solution in enumerate(solution_list):
                if (
                    solution.get("usage_count", 0) > 0
                    and solution.get("effectiveness", 1.0) == 1.0
                ):
                    plan["context_verification"].append(
                        {
                            "solution_id": f"{error_id}_{i}",
                            "error_id": error_id,
                            "priority": "medium",
                            "verification_method": "environment_testing",
                        }
                    )

        return plan

    def _calculate_success_rate(self, reality_checks):
        """Calculate success rate from reality checks"""
        if not reality_checks:
            return 0.5  # Default uncertainty

        successes = sum(1 for check in reality_checks if check.get("success", False))
        return successes / len(reality_checks)

    def _load_metadata(self):
        """Load metadata safely"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file) as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_metadata(self, metadata):
        """Save metadata safely"""
        self.kb_dir.mkdir(exist_ok=True)
        with open(self.metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

    def _load_json(self, filename):
        """Load JSON file safely"""
        file_path = self.kb_dir / filename
        if file_path.exists():
            try:
                with open(file_path) as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}


def main():
    manager = MetadataManager()

    if len(os.sys.argv) > 1:
        action = os.sys.argv[1]

        if action == "detect":
            misunderstandings = manager.detect_misunderstandings()
            print("🔍 Detected Misunderstandings:")
            for issue in misunderstandings:
                print(f"  • {issue['type']}: {issue['issue']}")

        elif action == "plan":
            plan = manager.generate_reality_check_plan()
            print("📋 Reality Check Plan:")
            print(f"  • Validation targets: {len(plan['validation_targets'])}")
            print(f"  • Context verifications: {len(plan['context_verification'])}")


if __name__ == "__main__":
    main()
