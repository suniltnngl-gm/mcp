#!/usr/bin/env python3
"""Intelligent code review with knowledge base learning - FIXED VERSION"""
import os
import sys
import json
import subprocess
import re
from pathlib import Path
from datetime import datetime


class IntelligentCodeReview:
    def __init__(self):
        self.kb_dir = Path("config/knowledge_base")  # Fixed path
        self.review_patterns_file = self.kb_dir / "review_patterns.json"
        self.code_issues_file = self.kb_dir / "code_issues.json"

        # Learn from this fix
        self._learn_from_fix(
            "path_traversal", "Use config/knowledge_base instead of knowledge_base"
        )

    def review_file(self, file_path):
        """Review single file with learning - FIXED"""
        issues = []

        # Validate and sanitize file path - FIX for path traversal
        if not self._is_safe_path(file_path):
            self._learn_from_fix(
                "path_validation", f"Rejected unsafe path: {file_path}"
            )
            return []

        # Case-insensitive file extension check - FIX for case handling
        file_lower = file_path.lower()
        if file_lower.endswith(".sh"):
            issues.extend(self._review_shell_script(file_path))
        elif file_lower.endswith(".py"):
            issues.extend(self._review_python_file(file_path))

        # Learn from review patterns
        self._learn_review_patterns(file_path, issues)

        return issues

    def _is_safe_path(self, file_path):
        """Validate file path to prevent traversal attacks - NEW"""
        try:
            # Resolve path and check if it's within allowed directories
            resolved = Path(file_path).resolve()
            allowed_dirs = [Path.cwd(), Path.cwd() / "scripts", Path.cwd() / "core"]

            return any(
                str(resolved).startswith(str(allowed_dir))
                for allowed_dir in allowed_dirs
            )
        except Exception:
            return False

    def _review_shell_script(self, file_path):
        """Review shell script with pattern matching - FIXED"""
        issues = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")
        except (IOError, OSError, UnicodeDecodeError) as e:
            self._learn_from_fix("file_read_error", f"Failed to read {file_path}: {e}")
            return []

        # Check common shell issues - FIXED indexing
        for i, line in enumerate(lines, 1):
            # Missing quotes around variables
            if re.search(r'\$\w+(?!\s*["\'])', line) and not line.strip().startswith(
                "#"
            ):
                issues.append(
                    {
                        "line": i,
                        "type": "shell_quoting",
                        "message": "Variable should be quoted to prevent word splitting",
                        "severity": "medium",
                        "suggestion": 'Use "$variable" instead of $variable',
                    }
                )

            # Missing error handling
            if (
                "rm " in line
                and "rm -f" not in line
                and not any(x in line for x in ["||", "&&", "if"])
            ):
                issues.append(
                    {
                        "line": i,
                        "type": "error_handling",
                        "message": "Potentially dangerous rm command without error handling",
                        "severity": "high",
                        "suggestion": "Add error handling or use rm -f",
                    }
                )

        return issues

    def _review_python_file(self, file_path):
        """Review Python file with pattern matching - FIXED"""
        issues = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")
        except (IOError, OSError, UnicodeDecodeError) as e:
            self._learn_from_fix("file_read_error", f"Failed to read {file_path}: {e}")
            return []

        # Check common Python issues - FIXED indexing
        for i, line in enumerate(lines, 1):
            # Bare except clauses
            if re.match(r"\s*except\s*:", line):
                issues.append(
                    {
                        "line": i,
                        "type": "exception_handling",
                        "message": "Bare except clause catches all exceptions",
                        "severity": "medium",
                        "suggestion": "Specify exception type: except SpecificException:",
                    }
                )

            # Missing docstrings for functions - FIXED indexing
            if line.strip().startswith("def ") and i < len(lines):
                next_line = (
                    lines[i].strip() if i < len(lines) else ""
                )  # Fixed: use i instead of i+1
                if not next_line.startswith('"""') and not next_line.startswith("'''"):
                    issues.append(
                        {
                            "line": i,
                            "type": "documentation",
                            "message": "Function missing docstring",
                            "severity": "low",
                            "suggestion": "Add docstring to document function purpose",
                        }
                    )

        return issues

    def _learn_review_patterns(self, file_path, issues):
        """Learn from review patterns for future improvements - FIXED"""
        patterns = self._load_json(self.review_patterns_file)

        file_type = Path(file_path).suffix
        if file_type not in patterns:
            patterns[file_type] = {}

        for issue in issues:
            issue_type = issue["type"]
            if issue_type not in patterns[file_type]:
                patterns[file_type][issue_type] = {
                    "count": 0,
                    "examples": [],
                    "solutions": [],
                }

            patterns[file_type][issue_type]["count"] += 1

            # Store example if not duplicate - FIX for performance
            example_key = f"{file_path}:{issue['line']}"
            existing_examples = [
                ex.get("key") for ex in patterns[file_type][issue_type]["examples"]
            ]

            if (
                example_key not in existing_examples
                and len(patterns[file_type][issue_type]["examples"]) < 5
            ):
                patterns[file_type][issue_type]["examples"].append(
                    {
                        "key": example_key,
                        "file": file_path,
                        "line": issue["line"],
                        "message": issue["message"],
                    }
                )

        self._save_json(self.review_patterns_file, patterns)

    def get_review_insights(self):
        """Get insights from accumulated review data"""
        patterns = self._load_json(self.review_patterns_file)
        insights = []

        for file_type, issues in patterns.items():
            for issue_type, data in issues.items():
                if data["count"] > 3:  # Frequent issue
                    insights.append(
                        {
                            "type": issue_type,
                            "file_type": file_type,
                            "frequency": data["count"],
                            "recommendation": f"Consider creating automated check for {issue_type}",
                        }
                    )

        return insights

    def _load_json(self, file_path):
        """Load JSON file safely - FIXED"""
        if file_path.exists():
            try:
                with open(file_path, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError, OSError):
                self._learn_from_fix("json_load_error", f"Failed to load {file_path}")
                return {}
        return {}

    def _save_json(self, file_path, data):
        """Save JSON file safely"""
        file_path.parent.mkdir(exist_ok=True)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except (IOError, OSError) as e:
            self._learn_from_fix("json_save_error", f"Failed to save {file_path}: {e}")

    def _learn_from_fix(self, fix_type, description):
        """Learn from fixes applied - NEW"""
        fixes_file = self.kb_dir / "applied_fixes.json"
        fixes = self._load_json(fixes_file) if fixes_file.exists() else {}

        if fix_type not in fixes:
            fixes[fix_type] = []

        fixes[fix_type].append(
            {
                "description": description,
                "timestamp": datetime.now().isoformat(),
                "file": "intelligent_code_review.py",
            }
        )

        self._save_json(fixes_file, fixes)


def analyze_staged_files():
    """Analyze only staged files for commit - MOVED before main"""
    try:
        # Get staged files - FIXED command injection
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            timeout=30,  # Add timeout
        )

        if result.returncode != 0:
            return []

        staged_files = [f.strip() for f in result.stdout.split("\n") if f.strip()]

        # Filter for code files
        code_extensions = [".py", ".sh", ".js", ".ts", ".json", ".yaml", ".yml"]
        code_files = [
            f
            for f in staged_files
            if any(f.lower().endswith(ext) for ext in code_extensions)
        ]  # Case insensitive

        return code_files

    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, OSError) as e:
        print(f"Error getting staged files: {e}")
        return []


def main():
    reviewer = IntelligentCodeReview()

    if len(sys.argv) > 1:  # FIXED: use sys.argv instead of os.sys.argv
        action = sys.argv[1]

        if action == "review" and len(sys.argv) > 2:
            file_path = sys.argv[2]
            issues = reviewer.review_file(file_path)

            print(f"Code review for {file_path}:")
            for issue in issues:
                print(
                    f"  Line {issue['line']}: [{issue['severity'].upper()}] {issue['message']}"
                )
                print(f"    Suggestion: {issue['suggestion']}")

        elif action == "insights":
            insights = reviewer.get_review_insights()
            print("Review insights:")
            for insight in insights:
                print(
                    f"  {insight['type']} in {insight['file_type']} files: {insight['frequency']} occurrences"
                )
                print(f"    {insight['recommendation']}")


if __name__ == "__main__":
    main()

# Handle staged analysis - MOVED after main function definition
if __name__ == "__main__" and "--staged" in sys.argv:
    reviewer = IntelligentCodeReview()
    staged_files = analyze_staged_files()
    if staged_files:
        print(f"[INTELLIGENCE] Analyzing {len(staged_files)} staged files...")
        issues_found = 0
        for file_path in staged_files:
            if os.path.exists(file_path):
                issues = reviewer.review_file(file_path)
                if issues:
                    issues_found += len(issues)
                    print(f"Issues in {file_path}:")
                    for issue in issues:
                        print(f"  Line {issue['line']}: {issue['message']}")
        if issues_found > 0:
            sys.exit(1)
    else:
        print("[INTELLIGENCE] No staged code files to analyze")
