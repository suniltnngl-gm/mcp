#!/usr/bin/env python3
"""Custom Rule Engine for Code Reviews

This module provides a simple, regex-based rule engine to enforce
project-specific coding standards.
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class CustomFinding:
    """Represents a finding from a custom rule"""

    file: str
    line: int
    rule_name: str
    severity: str
    message: str
    suggestion: str


@dataclass
class CustomRule:
    """User-defined review rule"""

    name: str
    pattern: str
    severity: str
    message: str
    suggestion: str
    file_types: List[str] = field(default_factory=list)


class CustomRuleEngine:
    """Execute custom regex-based rules"""

    def __init__(self, rules_file: Path):
        """Initialize the rule engine

        Args:
            rules_file: Path to the JSON file containing custom rules
        """
        self.rules = self._load_rules(rules_file)

    def _load_rules(self, rules_file: Path) -> List[CustomRule]:
        """Load rules from a JSON config file"""
        if not rules_file.exists():
            print(f"Warning: Rules file not found: {rules_file}")
            return []

        try:
            data = json.loads(rules_file.read_text())
            return [CustomRule(**rule) for rule in data.get("rules", [])]
        except json.JSONDecodeError as e:
            print(f"Error: Failed to decode rules file {rules_file}: {e}")
            return []
        except Exception as e:
            print(f"Error: Failed to load rules from {rules_file}: {e}")
            return []

    def review_file(self, filepath: Path) -> List[CustomFinding]:
        """Apply all custom rules to a single file

        Args:
            filepath: Path to the file to review

        Returns:
            List of findings for the file
        """
        findings = []
        
        try:
            content = filepath.read_text()
        except Exception as e:
            print(f"Warning: Could not read file {filepath}: {e}")
            return []

        for rule in self.rules:
            # Check if rule applies to this file type
            if not self._is_applicable(filepath, rule.file_types):
                continue

            # Apply regex pattern
            try:
                for i, line in enumerate(content.split('\n'), 1):
                    if re.search(rule.pattern, line):
                        findings.append(
                            CustomFinding(
                                file=str(filepath),
                                line=i,
                                rule_name=rule.name,
                                severity=rule.severity,
                                message=rule.message,
                                suggestion=rule.suggestion,
                            )
                        )
            except re.error as e:
                print(f"Warning: Invalid regex for rule '{rule.name}': {e}")

        return findings

    def review_directory(
        self, root_dir: Path, patterns: Optional[List[str]] = None
    ) -> List[CustomFinding]:
        """Review all applicable files in a directory

        Args:
            root_dir: The root directory to scan
            patterns: Glob patterns to select files (e.g., ["*.py"])

        Returns:
            List of all findings in the directory
        """
        all_findings = []
        
        if patterns is None:
            # Default to all file types defined in rules
            patterns = list(set(ft for rule in self.rules for ft in rule.file_types))
            if not patterns:
                return [] # No rules to apply

        # Get all unique file extensions from rules
        rule_extensions = {ext.lstrip('.') for r in self.rules for ext in r.file_types}

        for ext in rule_extensions:
            for filepath in root_dir.rglob(f"**/*.{ext}"):
                if self._is_excluded(filepath):
                    continue
                
                file_findings = self.review_file(filepath)
                all_findings.extend(file_findings)

        return all_findings

    def print_summary(self, findings: List[CustomFinding]):
        """Print a summary of custom rule findings"""
        if not findings:
            print("\n✅ No custom rule violations found.")
            return

        print(f"\n--- Custom Rule Violations ({len(findings)}) ---")
        
        # Group by severity
        by_severity = {}
        for f in findings:
            by_severity.setdefault(f.severity, []).append(f)

        for severity in ["critical", "high", "medium", "low", "info"]:
            if severity in by_severity:
                print(f"\n[{severity.upper()}] Violations:")
                for f in by_severity[severity]:
                    print(f"  - {f.file}:{f.line} ({f.rule_name}): {f.message}")

    def _is_applicable(self, filepath: Path, file_types: List[str]) -> bool:
        """Check if a rule is applicable to a given file type"""
        return any(filepath.match(ft) for ft in file_types)

    def _is_excluded(self, filepath: Path) -> bool:
        """Check if a file should be excluded from review"""
        excluded_dirs = [".git", ".venv", "__pycache__", "node_modules"]
        return any(part in filepath.parts for part in excluded_dirs)


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python custom_rules.py /path/to/project [--rules /path/to/rules.json]")
        sys.exit(1)

    project_dir = Path(sys.argv[1])
    rules_path = project_dir / "custom_review_rules.json"

    # Allow overriding rules file path
    if "--rules" in sys.argv:
        try:
            rules_path = Path(sys.argv[sys.argv.index("--rules") + 1])
        except IndexError:
            print("Error: --rules flag requires a path argument")
            sys.exit(1)

    if not rules_path.exists():
        print(f"Error: Rules file not found at {rules_path}")
        # Create an example file
        example_rules = {
            "rules": [
                {
                    "name": "no-print-statements",
                    "pattern": "^\\s*print\\(",
                    "severity": "low",
                    "message": "Avoid print statements in production code",
                    "suggestion": "Use the logging module instead.",
                    "file_types": ["*.py"]
                },
                {
                    "name": "no-todo-without-ticket",
                    "pattern": "TODO(?!.*#\\d+)",
                    "severity": "medium",
                    "message": "TODO comment found without a ticket reference.",
                    "suggestion": "Add a ticket number, e.g., TODO #123: your comment",
                    "file_types": ["*.py", "*.js"]
                }
            ]
        }
        rules_path.write_text(json.dumps(example_rules, indent=2))
        print(f"Created an example rules file at: {rules_path}")
        sys.exit(1)

    # Initialize and run the engine
    engine = CustomRuleEngine(rules_path)
    findings = engine.review_directory(project_dir)
    engine.print_summary(findings)

    if findings:
        sys.exit(1)