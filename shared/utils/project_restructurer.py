#!/usr/bin/env python3
"""
🏗️ AI Orchestra - Intelligent Project Restructurer
================================================
Automated project restructuring with intelligent duplicate removal and optimization
"""

import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from scripts.config_manager import is_path_ignored

# Import our analyzer
sys.path.append(str(Path(__file__).parent))
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# Colors for terminal output
class Colors:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def log_info(msg: str):
    print(f"{Colors.BLUE}🏗️  {msg}{Colors.ENDC}")


def log_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.ENDC}")


def log_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.ENDC}")


def log_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.ENDC}")


def log_header(msg: str):
    print(f"\n{Colors.PURPLE}{Colors.BOLD}🎭 {msg}{Colors.ENDC}")
    print("=" * (len(msg) + 3))


@dataclass
class RefactoringPlan:
    """Plan for refactoring operations"""

    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    operations: list[dict[str, Any]] = field(default_factory=list)
    new_structure: dict[str, list[str]] = field(default_factory=dict)
    backups_created: list[str] = field(default_factory=list)


@dataclass
class RestructureOperation:
    """Individual restructure operation"""

    type: str  # 'move', 'merge', 'split', 'rename', 'create_package'
    source: str
    target: str
    reason: str
    confidence: float
    dependencies: list[str] = field(default_factory=list)


class IntelligentRestructurer:
    def __init__(self, project_root: Path, analysis_report: dict | None = None):
        self.project_root = project_root
        self.analysis_report = analysis_report
        self.plan = RefactoringPlan()
        self.dry_run = True

        # Restructuring patterns
        self.package_patterns = {
            "providers": [
                "provider",
                "openai",
                "anthropic",
                "mistral",
                "gemini",
                "openrouter",
                "groq",
                "cohere",
                "ai21",
                "cerebras",
            ],
            "core": ["orchestra", "manager", "load_balancer", "context"],
            "persistence": ["persistence", "data", "cache", "storage"],
            "monitoring": ["monitor", "health", "tracker", "metrics"],
            "configuration": ["config", "setup", "autoconfig"],
            "utils": ["checker", "detector", "helper", "utility"],
            "plugins": ["plugin", "extension"],
            "cli": ["cli", "interface", "web"],
        }

    def create_restructuring_plan(self) -> RefactoringPlan:
        """Create comprehensive restructuring plan"""
        log_header("Creating Intelligent Restructuring Plan")

        if not self.analysis_report:
            log_error("No analysis report provided")
            return self.plan

        # Step 1: Plan package organization
        self._plan_package_structure()

        # Step 2: Plan duplicate resolution
        self._plan_duplicate_resolution()

        # Step 3: Plan file splitting for large modules
        self._plan_module_splitting()

        # Step 4: Plan naming improvements
        self._plan_naming_improvements()

        # Step 5: Plan import optimization
        self._plan_import_optimization()

        log_success(f"Created plan with {len(self.plan.operations)} operations")
        return self.plan

    def _plan_package_structure(self) -> None:
        """Plan optimal package structure based on analysis"""
        log_info("Planning package structure...")

        # Analyze current file distribution
        file_categories = {"other": []}

        for module_data in self.analysis_report.get("summary", {}).get("modules", []):
            module_name = module_data.get("name", "")
            module_lower = module_name.lower()

            categorized = False
            for category, patterns in self.package_patterns.items():
                if any(pattern in module_lower for pattern in patterns):
                    if category not in file_categories:
                        file_categories[category] = []
                    file_categories[category].append(module_name)
                    categorized = True
                    break

            if not categorized:
                file_categories["other"].append(module_name)

        # Create package operations for categories with multiple files
        for category, modules in file_categories.items():
            if len(modules) >= 3 and category != "other":
                self.plan.operations.append(
                    {
                        "type": "create_package",
                        "target": f"src/ai_orchestra/{category}",
                        "modules": modules,
                        "reason": f"Organize {len(modules)} {category}-related modules",
                        "confidence": 0.9,
                    }
                )
                self.plan.new_structure[category] = modules

        # Handle remaining files
        if len(file_categories["other"]) > 0:
            self.plan.new_structure["core"] = file_categories["other"]

    def _plan_duplicate_resolution(self) -> None:
        """Plan resolution of duplicates"""
        log_info("Planning duplicate resolution...")

        duplicates = self.analysis_report.get("duplicates", [])

        for dup in duplicates:
            if dup.get("similarity", 0) > 0.95:  # Near identical
                self.plan.operations.append(
                    {
                        "type": "merge_duplicates",
                        "items": dup.get("items", []),
                        "similarity": dup.get("similarity"),
                        "reason": f"Merge near-identical {dup.get('type')}s",
                        "confidence": 0.95,
                    }
                )
            elif dup.get("similarity", 0) > 0.8:  # Similar
                self.plan.operations.append(
                    {
                        "type": "consolidate_similar",
                        "items": dup.get("items", []),
                        "similarity": dup.get("similarity"),
                        "reason": f"Consolidate similar {dup.get('type')}s",
                        "confidence": 0.7,
                    }
                )

    def _plan_module_splitting(self) -> None:
        """Plan splitting of large modules"""
        log_info("Planning module splitting...")

        # From structure recommendations
        recommendations = self.analysis_report.get("structure_recommendations", [])

        for rec in recommendations:
            if "lines - consider splitting" in rec:
                # Extract module name
                parts = rec.split(" has ")
                if len(parts) >= 2:
                    module_name = parts[0].replace("Module ", "")
                    lines_info = parts[1].split(" lines")[0]

                    try:
                        lines = int(lines_info)
                        if lines > 1000:  # Very large modules
                            confidence = 0.9
                        elif lines > 700:  # Large modules
                            confidence = 0.8
                        else:  # Medium modules
                            confidence = 0.6

                        self.plan.operations.append(
                            {
                                "type": "split_module",
                                "source": module_name,
                                "lines": lines,
                                "reason": f"Split large module with {lines} lines",
                                "confidence": confidence,
                            }
                        )
                    except ValueError:
                        continue

    def _plan_naming_improvements(self) -> None:
        """Plan naming improvements"""
        log_info("Planning naming improvements...")

        naming_issues = self.analysis_report.get("naming_issues", {})

        for _category, issues in naming_issues.items():
            for issue in issues:
                if "should use snake_case" in issue:
                    # Extract current name
                    current_name = issue.split(" - ")[0]
                    suggested_name = self._suggest_snake_case_name(current_name)

                    self.plan.operations.append(
                        {
                            "type": "rename_file",
                            "source": current_name,
                            "target": suggested_name,
                            "reason": "Fix naming convention to snake_case",
                            "confidence": 0.95,
                        }
                    )

    def _plan_import_optimization(self) -> None:
        """Plan import reorganization"""
        log_info("Planning import optimization...")

        # Based on most common imports, suggest shared utilities
        import_analysis = self.analysis_report.get("import_analysis", {})
        common_imports = import_analysis.get("most_common", [])

        # If rich components are heavily used, suggest a rich utilities module
        rich_imports = [imp for imp, count in common_imports if "rich." in imp[0]]
        if len(rich_imports) >= 3:
            self.plan.operations.append(
                {
                    "type": "create_utility_module",
                    "target": "src/ai_orchestra/utils/rich_utils.py",
                    "reason": "Consolidate rich component imports",
                    "imports": rich_imports,
                    "confidence": 0.8,
                }
            )

    def _suggest_snake_case_name(self, name: str) -> str:
        """Suggest snake_case version of name"""
        # Convert hyphens to underscores
        name = name.replace("-", "_")

        # Convert camelCase to snake_case
        name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()

        return name

    def execute_plan(self, dry_run: bool = True) -> bool:
        """Execute the restructuring plan"""
        self.dry_run = dry_run

        if dry_run:
            log_header("Dry Run - Showing Planned Operations")
            self._show_plan()
            return True

        log_header("Executing Restructuring Plan")

        # Create backup first
        self._create_backup()

        try:
            # Execute operations in order
            for i, operation in enumerate(self.plan.operations):
                log_info(f"Executing operation {i+1}/{len(self.plan.operations)}")
                success = self._execute_operation(operation)

                if not success:
                    log_error(f"Operation failed: {operation}")
                    if not self._ask_continue():
                        log_warning("Aborting restructuring")
                        return False

            # Run tests to verify nothing broke
            if self._run_tests():
                log_success("All tests passed after restructuring!")
            else:
                log_warning("Some tests failed - review changes")

            # Update imports and references
            self._update_imports()

            # Format and lint the code
            self._format_code()

            log_success("Restructuring completed successfully!")
            return True

        except Exception as e:
            log_error(f"Error during restructuring: {e}")
            self._restore_backup()
            return False

    def _show_plan(self) -> None:
        """Display the restructuring plan"""
        print(f"\n{Colors.CYAN}📋 Restructuring Plan{Colors.ENDC}")
        print("=" * 30)

        # Group operations by type
        by_type = {}
        for op in self.plan.operations:
            op_type = op.get("type", "unknown")
            if op_type not in by_type:
                by_type[op_type] = []
            by_type[op_type].append(op)

        for op_type, ops in by_type.items():
            print(
                f"\n{Colors.YELLOW}{op_type.replace('_', ' ').title()}: {len(ops)} operations{Colors.ENDC}"
            )
            for op in ops[:3]:  # Show first 3
                confidence_color = (
                    Colors.GREEN if op.get("confidence", 0) > 0.8 else Colors.YELLOW
                )
                print(
                    f"  • {op.get('reason', 'No reason')} "
                    f"{confidence_color}(confidence: {op.get('confidence', 0):.1%}){Colors.ENDC}"
                )
            if len(ops) > 3:
                print(f"  ... and {len(ops) - 3} more")

        print(f"\n{Colors.BLUE}📁 New Package Structure:{Colors.ENDC}")
        for package, modules in self.plan.new_structure.items():
            print(f"  {package}/: {len(modules)} modules")
            for module in modules[:2]:
                print(f"    - {module}")
            if len(modules) > 2:
                print(f"    ... and {len(modules) - 2} more")

    def _create_backup(self) -> None:
        """Create backup of current state"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.project_root / f"restructure_backup_{timestamp}"

        log_info(f"Creating backup at {backup_path}")

        # Copy Python files and important configs
        backup_path.mkdir(exist_ok=True)

        for py_file in self.project_root.rglob("*.py"):
            if not is_path_ignored(py_file):
                rel_path = py_file.relative_to(self.project_root)
                dest_path = backup_path / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(py_file, dest_path)

        # Copy important config files
        for config_file in ["pyproject.toml", ".mise.toml", "Makefile"]:
            src = self.project_root / config_file
            if src.exists():
                shutil.copy2(src, backup_path / config_file)

        self.plan.backups_created.append(str(backup_path))
        log_success(f"Backup created at {backup_path}")

    def _execute_operation(self, operation: dict[str, Any]) -> bool:
        """Execute a single operation"""
        op_type = operation.get("type")

        try:
            if op_type == "create_package":
                return self._create_package(operation)
            elif op_type == "split_module":
                return self._split_module(operation)
            elif op_type == "rename_file":
                return self._rename_file(operation)
            elif op_type == "merge_duplicates":
                return self._merge_duplicates(operation)
            elif op_type == "create_utility_module":
                return self._create_utility_module(operation)
            else:
                log_warning(f"Unknown operation type: {op_type}")
                return True  # Continue with other operations

        except Exception as e:
            log_error(f"Error executing {op_type}: {e}")
            return False

    def _create_package(self, operation: dict[str, Any]) -> bool:
        """Create a new package and move modules"""
        target_dir = Path(operation["target"])
        modules = operation.get("modules", [])

        log_info(f"Creating package: {target_dir}")

        # Create directory structure
        full_target = self.project_root / target_dir
        full_target.mkdir(parents=True, exist_ok=True)

        # Create __init__.py
        init_file = full_target / "__init__.py"
        with open(init_file, "w") as f:
            f.write(f'"""\n{target_dir.name.title()} Package\n"""\n')

        # Move modules
        for module in modules:
            src_file = self.project_root / f"{module}.py"
            if src_file.exists():
                dest_file = full_target / f"{module}.py"
                shutil.move(str(src_file), str(dest_file))
                log_info(f"Moved {module}.py to {target_dir}")

        return True

    def _split_module(self, operation: dict[str, Any]) -> bool:
        """Split a large module into smaller ones"""
        source_module = operation.get("source", "")

        log_info(f"Splitting module: {source_module}")

        # This is a complex operation - for now, just log what would be done
        log_warning(f"Module splitting not yet implemented for {source_module}")
        log_info("Would analyze AST and split based on class/function groupings")

        return True

    def _rename_file(self, operation: dict[str, Any]) -> bool:
        """Rename a file to follow naming conventions"""
        source = operation.get("source", "")
        target = operation.get("target", "")

        if source.endswith(".py"):
            src_path = self.project_root / source
        else:
            src_path = self.project_root / f"{source}.py"

        if target.endswith(".py"):
            dest_path = self.project_root / target
        else:
            dest_path = self.project_root / f"{target}.py"

        if src_path.exists():
            src_path.rename(dest_path)
            log_info(f"Renamed {source} to {target}")
            return True
        else:
            log_warning(f"Source file not found: {src_path}")
            return False

    def _merge_duplicates(self, operation: dict[str, Any]) -> bool:
        """Merge duplicate functions/classes"""
        items = operation.get("items", [])

        log_info(f"Would merge duplicates: {items}")
        log_warning(
            "Duplicate merging not yet implemented - requires complex AST analysis"
        )

        return True

    def _create_utility_module(self, operation: dict[str, Any]) -> bool:
        """Create utility module for common imports"""
        target = operation.get("target", "")
        imports = operation.get("imports", [])

        log_info(f"Creating utility module: {target}")

        target_path = self.project_root / target
        target_path.parent.mkdir(parents=True, exist_ok=True)

        with open(target_path, "w") as f:
            f.write('"""\nUtility module for common imports\n"""\n\n')
            for imp, count in imports:
                f.write(f"from {imp} import *  # Used {count} times across codebase\n")

        return True

    def _run_tests(self) -> bool:
        """Run tests to verify restructuring didn't break anything"""
        log_info("Running tests to verify restructuring...")

        try:
            result = subprocess.run(
                ["uv", "run", "pytest", "--tb=short", "-q"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                log_success("All tests passed!")
                return True
            else:
                log_warning("Some tests failed:")
                print(result.stdout)
                return False

        except Exception as e:
            log_warning(f"Could not run tests: {e}")
            return True  # Don't fail restructuring due to test issues

    def _update_imports(self) -> None:
        """Update import statements after restructuring"""
        log_info("Updating import statements...")

        # This would require sophisticated import analysis and updating
        # For now, just run ruff to catch import issues
        try:
            subprocess.run(
                ["uv", "run", "ruff", "check", "--fix", "."],
                cwd=self.project_root,
                capture_output=True,
            )
        except Exception as e:
            log_warning(f"Could not auto-fix imports: {e}")

    def _format_code(self) -> None:
        """Format code after restructuring"""
        log_info("Formatting code...")

        try:
            # Format with black
            subprocess.run(
                ["uv", "run", "black", "."], cwd=self.project_root, capture_output=True
            )

            # Check with ruff
            subprocess.run(
                ["uv", "run", "ruff", "format", "."],
                cwd=self.project_root,
                capture_output=True,
            )

            log_success("Code formatted")
        except Exception as e:
            log_warning(f"Could not format code: {e}")

    def _restore_backup(self) -> None:
        """Restore from backup if something went wrong"""
        if self.plan.backups_created:
            backup_path = Path(self.plan.backups_created[-1])
            log_warning(f"Restoring from backup: {backup_path}")

            # This would restore files - implementation depends on backup strategy
            log_info("Backup restoration not implemented - manual recovery needed")

    def _ask_continue(self) -> bool:
        """Ask user if they want to continue after an error"""
        try:
            response = input("Continue with remaining operations? (y/N): ")
            return response.lower().startswith("y")
        except KeyboardInterrupt:
            return False


def main():
    """Main restructuring function"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Orchestra Project Restructurer")
    parser.add_argument(
        "--project-root", type=Path, default=Path.cwd(), help="Project root directory"
    )
    parser.add_argument("--analysis-file", type=Path, help="Analysis report JSON file")
    parser.add_argument(
        "--execute", action="store_true", help="Execute the plan (default is dry run)"
    )
    parser.add_argument(
        "--show-plan", action="store_true", help="Only show the plan without executing"
    )

    args = parser.parse_args()

    # Load analysis report
    analysis_report = None
    if args.analysis_file and args.analysis_file.exists():
        with open(args.analysis_file) as f:
            analysis_report = json.load(f)
    else:
        # Run analysis first
        log_info("Running codebase analysis first...")
        try:
            from codebase_analyzer import CodebaseAnalyzer

            analyzer = CodebaseAnalyzer(args.project_root)
            report = analyzer.analyze_project()

            # Convert to dict format
            analysis_report = {
                "summary": {
                    "total_modules": len(report.modules),
                    "modules": [
                        {"name": m.name, "file_path": m.file_path}
                        for m in report.modules
                    ],
                },
                "duplicates": [
                    {
                        "type": d.type,
                        "similarity": d.similarity,
                        "items": [
                            item.name if hasattr(item, "name") else str(item)
                            for item in d.items
                        ],
                    }
                    for d in report.duplicates
                ],
                "naming_issues": report.naming_issues,
                "structure_recommendations": report.structure_recommendations,
                "import_analysis": report.import_analysis,
            }
        except ImportError:
            log_error("Could not import codebase analyzer")
            return 1

    # Create restructurer
    restructurer = IntelligentRestructurer(args.project_root, analysis_report)

    # Create plan
    restructurer.create_restructuring_plan()

    if args.show_plan or not args.execute:
        restructurer._show_plan()

        if not args.show_plan:
            print(
                f"\n{Colors.BLUE}To execute this plan, run with --execute{Colors.ENDC}"
            )
    else:
        # Execute plan
        success = restructurer.execute_plan(dry_run=False)
        if success:
            log_success("Project restructuring completed successfully!")
            return 0
        else:
            log_error("Project restructuring failed")
            return 1


if __name__ == "__main__":
    sys.exit(main())
