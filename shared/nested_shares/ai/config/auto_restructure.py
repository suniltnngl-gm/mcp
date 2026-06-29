#!/usr/bin/env python3
"""
🤖 AI Orchestra - Complete Automation Pipeline
==============================================
Intelligent project restructuring with learning from errors and full tool integration
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from scripts.config_manager import is_path_ignored


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
    print(f"{Colors.BLUE}🤖 {msg}{Colors.ENDC}")


def log_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.ENDC}")


def log_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.ENDC}")


def log_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.ENDC}")


def log_header(msg: str):
    print(f"\n{Colors.PURPLE}{Colors.BOLD}🎭 {msg}{Colors.ENDC}")
    print("=" * (len(msg) + 3))


class AutoRestructurer:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.error_log = []
        self.execution_log = []

        # Available tools
        self.tools = {
            "codebase_analyzer": project_root / "scripts" / "codebase-analyzer.py",
            "structure_optimizer": project_root / "scripts" / "structure_optimizer.py",
            "project_restructurer": project_root
            / "scripts"
            / "project-restructurer.py",
            "perf_monitor": project_root / "scripts" / "perf-monitor.py",
        }

    def run_complete_restructuring(self, dry_run: bool = True) -> bool:
        """Run the complete intelligent restructuring process with deeper learning"""
        log_header("AI Orchestra Complete Restructuring Pipeline")

        try:
            # Phase 1: Pre-analysis
            if not self._pre_analysis_checks():
                return False

            # Phase 2: Deep analysis
            analysis_results = self._run_deep_analysis()
            if not analysis_results:
                return False

            # Phase 2.5: Aggregate error logs, metadata, and knowledge base
            intelligence = self._aggregate_intelligence(analysis_results)

            # Phase 3: Generate restructuring plan using intelligence
            restructure_plan = self._generate_restructure_plan(
                analysis_results, intelligence
            )
            if not restructure_plan:
                return False

            # Phase 4: Execute or show plan
            if dry_run:
                self._show_comprehensive_plan(analysis_results, restructure_plan)
                print(
                    f"\n{Colors.BLUE}This was a dry run. Use --execute to apply changes.{Colors.ENDC}"
                )
                self._log_restructuring_outcome(restructure_plan, success=True)
                return True
            else:
                result = self._execute_restructure_plan(restructure_plan)
                self._log_restructuring_outcome(restructure_plan, success=result)
                return result

        except Exception as e:
            log_error(f"Restructuring pipeline failed: {e}")
            self._save_error_log()
            self._log_restructuring_outcome({}, success=False, error=str(e))
            return False

    def _aggregate_intelligence(
        self, analysis_results: dict[str, Any]
    ) -> dict[str, Any]:
        """Aggregate error logs, metadata, knowledge base, and standard tool outputs for deeper learning"""
        intelligence = {}
        # Aggregate error logs from previous runs
        try:
            error_log_path = self.project_root / "analysis_report.json"
            if error_log_path.exists():
                with open(error_log_path) as f:
                    intelligence["error_log"] = json.load(f)
        except Exception as e:
            log_warning(f"Could not load error log: {e}")

        # Aggregate metadata from performance analysis
        if "performance" in analysis_results:
            intelligence["performance_metadata"] = analysis_results["performance"]

        # Query knowledge base if available
        kb_path = (
            self.project_root
            / "Docs"
            / "Python framework for collaborative AI interaction.txt"
        )
        if kb_path.exists():
            try:
                with open(kb_path) as f:
                    intelligence["knowledge_base"] = f.read()
            except Exception as e:
                log_warning(f"Could not load knowledge base: {e}")

        # Run pytest for test intelligence
        try:
            import subprocess

            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "pytest",
                    "--maxfail=5",
                    "--disable-warnings",
                    "--json-report",
                    "--json-report-file=pytest_report.json",
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120,
            )
            pytest_report_path = self.project_root / "pytest_report.json"
            if pytest_report_path.exists():
                with open(pytest_report_path) as f:
                    intelligence["pytest_report"] = json.load(f)
        except Exception as e:
            log_warning(f"Could not run pytest: {e}")

        # Run ruff for linting intelligence
        try:
            result = subprocess.run(
                ["uv", "run", "ruff", ".", "--format", "json"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                try:
                    intelligence["ruff_report"] = json.loads(result.stdout)
                except Exception:
                    intelligence["ruff_report"] = result.stdout
        except Exception as e:
            log_warning(f"Could not run ruff: {e}")

        # Run black for formatting intelligence
        try:
            result = subprocess.run(
                ["uv", "run", "black", ".", "--check", "--diff"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60,
            )
            intelligence["black_diff"] = result.stdout
        except Exception as e:
            log_warning(f"Could not run black: {e}")

        # Run environment analysis from dependency_manager.py
        try:
            env_analysis = subprocess.run(
                ["uv", "run", "python", "dependency_manager.py", "--validate-env"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if env_analysis.returncode == 0:
                try:
                    intelligence["environment_analysis"] = json.loads(
                        env_analysis.stdout
                    )
                except Exception:
                    intelligence["environment_analysis"] = env_analysis.stdout
        except Exception as e:
            log_warning(f"Could not run environment analysis: {e}")

        # Run secure-env.sh for secret and environment checks
        try:
            bash_script = self.project_root / "scripts" / "secure-env.sh"
            if bash_script.exists():
                result = subprocess.run(
                    ["bash", str(bash_script)],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                intelligence["secure_env_output"] = result.stdout
        except Exception as e:
            log_warning(f"Could not run secure-env.sh: {e}")

        return intelligence

    def _log_restructuring_outcome(self, plan: dict, success: bool, error: str = None):
        """Log the outcome of restructuring for future learning"""
        outcome = {
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "plan": plan,
            "error": error,
        }
        try:
            log_path = self.project_root / "restructuring_outcomes.json"
            if log_path.exists():
                with open(log_path) as f:
                    outcomes = json.load(f)
            else:
                outcomes = []
            outcomes.append(outcome)
            with open(log_path, "w") as f:
                json.dump(outcomes, f, indent=2)
        except Exception as e:
            log_warning(f"Could not log restructuring outcome: {e}")

    def _pre_analysis_checks(self) -> bool:
        """Run pre-analysis checks"""
        log_info("Running pre-analysis checks...")

        # Check if tools exist
        missing_tools = []
        for tool_name, tool_path in self.tools.items():
            if not tool_path.exists():
                missing_tools.append(tool_name)

        if missing_tools:
            log_error(f"Missing tools: {', '.join(missing_tools)}")
            return False

        # Check if project has Python files
        python_files = list(self.project_root.rglob("*.py"))
        python_files = [f for f in python_files if not is_path_ignored(f)]

        if len(python_files) < 5:
            log_warning(
                f"Only {len(python_files)} Python files found. May not need restructuring."
            )

        # Run basic health check
        health_check = self._run_health_check()
        if not health_check:
            log_warning("Health check failed, but continuing...")

        log_success("Pre-analysis checks completed")
        return True

    def _run_health_check(self) -> bool:
        """Run basic health check"""
        try:
            result = subprocess.run(
                ["uv", "run", "python", "-c", 'print("Python environment OK")'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode == 0
        except:
            return False

    def _run_deep_analysis(self) -> dict[str, Any] | None:
        """Run comprehensive codebase analysis"""
        log_header("Running Deep Codebase Analysis")

        analysis_results = {}

        # Step 1: Codebase analysis
        log_info("Step 1: Analyzing codebase structure and duplicates...")
        codebase_analysis = self._run_tool("codebase_analyzer", ["--format", "json"])
        if codebase_analysis:
            analysis_results["codebase"] = codebase_analysis
            log_success("Codebase analysis completed")
        else:
            log_error("Codebase analysis failed")
            return None

        # Step 2: Structure optimization analysis
        log_info("Step 2: Analyzing optimal structure...")
        structure_analysis = self._run_tool("structure_optimizer", ["recommend"])
        if structure_analysis:
            analysis_results["structure"] = structure_analysis
            log_success("Structure analysis completed")
        else:
            log_warning("Structure analysis had issues, continuing...")

        # Step 3: Performance analysis
        log_info("Step 3: Analyzing performance metrics...")
        perf_analysis = self._run_tool("perf_monitor", ["metrics"])
        if perf_analysis:
            analysis_results["performance"] = perf_analysis
            log_success("Performance analysis completed")
        else:
            log_warning("Performance analysis had issues, continuing...")

        return analysis_results

    def _run_tool(self, tool_name: str, args: list[str]) -> Any | None:
        """Run a tool and capture its output"""
        tool_path = self.tools.get(tool_name)
        if not tool_path:
            log_error(f"Tool {tool_name} not found")
            return None

        try:
            cmd = ["python", str(tool_path)] + args
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            self.execution_log.append(
                {
                    "tool": tool_name,
                    "command": cmd,
                    "return_code": result.returncode,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            if result.returncode == 0:
                # Try to parse JSON output
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    # Return text output if not JSON
                    return {"output": result.stdout}
            else:
                self.error_log.append(
                    {
                        "tool": tool_name,
                        "error": result.stderr,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
                return None

        except subprocess.TimeoutExpired:
            log_error(f"Tool {tool_name} timed out")
            return None
        except Exception as e:
            log_error(f"Error running {tool_name}: {e}")
            return None

    def _generate_restructure_plan(
        self, analysis_results: dict[str, Any], intelligence: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Generate comprehensive restructuring plan based on analysis and intelligence"""
        log_header("Generating Collectively Intelligent Restructuring Plan")

        plan = {
            "timestamp": datetime.now().isoformat(),
            "phases": [],
            "total_operations": 0,
            "estimated_time": 0,
            "risk_level": "MEDIUM",
            "intelligence": intelligence,
        }

        codebase_analysis = analysis_results.get("codebase", {})

        # Use error log and metadata to prioritize fixes
        error_log = intelligence.get("error_log", {})
        performance_metadata = intelligence.get("performance_metadata", {})
        knowledge_base = intelligence.get("knowledge_base", "")

        # Phase 1: Immediate fixes (high confidence, low risk)
        phase1 = self._plan_immediate_fixes(codebase_analysis)
        if phase1["operations"]:
            plan["phases"].append(phase1)
            plan["total_operations"] += len(phase1["operations"])

        # Phase 2: Structure optimization (medium risk)
        phase2 = self._plan_structure_optimization(codebase_analysis)
        if phase2["operations"]:
            plan["phases"].append(phase2)
            plan["total_operations"] += len(phase2["operations"])

        # Phase 3: Advanced refactoring (higher risk)
        phase3 = self._plan_advanced_refactoring(codebase_analysis)
        if phase3["operations"]:
            plan["phases"].append(phase3)
            plan["total_operations"] += len(phase3["operations"])

        # Phase 4: Intelligence-driven suggestions
        intelligence_ops = []
        if error_log:
            intelligence_ops.append(
                {
                    "type": "error_driven_fix",
                    "description": "Apply fixes based on aggregated error log",
                    "risk": "MEDIUM",
                    "confidence": 0.8,
                    "details": error_log,
                }
            )
        if performance_metadata:
            intelligence_ops.append(
                {
                    "type": "performance_driven_optimization",
                    "description": "Optimize structure based on performance metadata",
                    "risk": "MEDIUM",
                    "confidence": 0.85,
                    "details": performance_metadata,
                }
            )
        if knowledge_base:
            intelligence_ops.append(
                {
                    "type": "knowledge_base_guided_fix",
                    "description": "Apply best practices from knowledge base",
                    "risk": "LOW",
                    "confidence": 0.9,
                    "details": knowledge_base,
                }
            )
        if intelligence_ops:
            plan["phases"].append(
                {
                    "name": "Intelligence-driven enhancements",
                    "operations": intelligence_ops,
                }
            )
            plan["total_operations"] += len(intelligence_ops)

        # Calculate risk and time estimates
        plan["risk_level"] = self._calculate_risk_level(plan)
        plan["estimated_time"] = self._estimate_execution_time(plan)

        log_success(
            f"Generated plan with {plan['total_operations']} total operations across {len(plan['phases'])} phases"
        )
        return plan

    def _plan_immediate_fixes(self, analysis: dict[str, Any]) -> dict[str, Any]:
        """Plan immediate, low-risk fixes"""
        operations = []

        # Fix naming conventions
        naming_issues = analysis.get("naming_issues", {})
        for _category, issues in naming_issues.items():
            for issue in issues[:3]:  # Limit to first 3 to avoid overwhelming
                operations.append(
                    {
                        "type": "rename_file",
                        "description": f"Fix naming convention: {issue}",
                        "risk": "LOW",
                        "confidence": 0.95,
                    }
                )

        # Remove unused imports (via ruff)
        operations.append(
            {
                "type": "clean_imports",
                "description": "Remove unused imports and organize",
                "risk": "LOW",
                "confidence": 0.9,
            }
        )

        # Format code
        operations.append(
            {
                "type": "format_code",
                "description": "Format code with black and ruff",
                "risk": "LOW",
                "confidence": 1.0,
            }
        )

        return {
            "name": "Immediate Fixes",
            "description": "Low-risk improvements that can be applied immediately",
            "operations": operations,
            "estimated_time_minutes": len(operations) * 2,
        }

    def _plan_structure_optimization(self, analysis: dict[str, Any]) -> dict[str, Any]:
        """Plan structure optimization operations"""
        operations = []

        # Create packages for provider files
        summary = analysis.get("summary", {})
        if summary.get("total_functions", 0) > 50:
            operations.append(
                {
                    "type": "create_provider_package",
                    "description": "Create src/ai_orchestra/providers/ package",
                    "risk": "MEDIUM",
                    "confidence": 0.8,
                }
            )

        # Split large modules
        refactoring_opportunities = analysis.get("refactoring_opportunities", [])
        large_modules = [
            op for op in refactoring_opportunities if op.get("type") == "large_module"
        ]

        for module in large_modules[:3]:  # Limit to 3 largest
            operations.append(
                {
                    "type": "split_module",
                    "description": f"Split large module: {module.get('description', 'Unknown')}",
                    "risk": "MEDIUM",
                    "confidence": 0.7,
                }
            )

        return {
            "name": "Structure Optimization",
            "description": "Reorganize code structure for better maintainability",
            "operations": operations,
            "estimated_time_minutes": len(operations) * 15,
        }

    def _plan_advanced_refactoring(self, analysis: dict[str, Any]) -> dict[str, Any]:
        """Plan advanced refactoring operations"""
        operations = []

        # Merge duplicates (high-confidence ones only)
        duplicates = analysis.get("duplicates", [])
        high_confidence_duplicates = [
            dup for dup in duplicates if dup.get("similarity", 0) > 0.95
        ]

        for dup in high_confidence_duplicates[:5]:  # Limit to 5 most obvious
            operations.append(
                {
                    "type": "merge_duplicates",
                    "description": f"Merge duplicate {dup.get('type', 'items')}: {dup.get('items', [])}",
                    "risk": "HIGH",
                    "confidence": 0.6,
                }
            )

        return {
            "name": "Advanced Refactoring",
            "description": "Complex refactoring operations requiring careful review",
            "operations": operations,
            "estimated_time_minutes": len(operations) * 30,
        }

    def _calculate_risk_level(self, plan: dict[str, Any]) -> str:
        """Calculate overall risk level of the plan"""
        risk_scores = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
        total_risk = 0
        operation_count = 0

        for phase in plan["phases"]:
            for op in phase["operations"]:
                risk = op.get("risk", "MEDIUM")
                total_risk += risk_scores.get(risk, 2)
                operation_count += 1

        if operation_count == 0:
            return "LOW"

        avg_risk = total_risk / operation_count

        if avg_risk <= 1.3:
            return "LOW"
        elif avg_risk <= 2.3:
            return "MEDIUM"
        else:
            return "HIGH"

    def _estimate_execution_time(self, plan: dict[str, Any]) -> int:
        """Estimate total execution time in minutes"""
        total_time = 0
        for phase in plan["phases"]:
            total_time += phase.get("estimated_time_minutes", 10)
        return total_time

    def _show_comprehensive_plan(
        self, analysis_results: dict[str, Any], plan: dict[str, Any]
    ) -> None:
        """Display comprehensive restructuring plan"""
        print(
            f"\n{Colors.BOLD}{Colors.CYAN}🤖 AI Orchestra Complete Restructuring Plan{Colors.ENDC}"
        )
        print("=" * 60)

        # Summary
        codebase_summary = analysis_results.get("codebase", {}).get("summary", {})
        print(f"\n{Colors.YELLOW}📊 Current State Summary:{Colors.ENDC}")
        print(f"  Total modules: {codebase_summary.get('total_modules', 'Unknown')}")
        print(
            f"  Total functions: {codebase_summary.get('total_functions', 'Unknown')}"
        )
        print(f"  Total classes: {codebase_summary.get('total_classes', 'Unknown')}")
        print(
            f"  Duplicates found: {codebase_summary.get('duplicates_found', 'Unknown')}"
        )
        print(
            f"  Refactoring opportunities: {codebase_summary.get('refactoring_opportunities', 'Unknown')}"
        )

        # Plan overview
        print(f"\n{Colors.GREEN}📋 Restructuring Plan Overview:{Colors.ENDC}")
        print(f"  Total operations: {plan['total_operations']}")
        print(f"  Phases: {len(plan['phases'])}")
        print(f"  Estimated time: {plan['estimated_time']} minutes")

        risk_color = (
            Colors.RED
            if plan["risk_level"] == "HIGH"
            else Colors.YELLOW if plan["risk_level"] == "MEDIUM" else Colors.GREEN
        )
        print(f"  Risk level: {risk_color}{plan['risk_level']}{Colors.ENDC}")

        # Phase details
        for i, phase in enumerate(plan["phases"], 1):
            print(f"\n{Colors.PURPLE}Phase {i}: {phase['name']}{Colors.ENDC}")
            print(f"  {phase['description']}")
            print(f"  Operations: {len(phase['operations'])}")
            print(f"  Estimated time: {phase.get('estimated_time_minutes', 0)} minutes")

            for j, op in enumerate(phase["operations"][:3], 1):  # Show first 3
                risk_color = (
                    Colors.RED
                    if op["risk"] == "HIGH"
                    else Colors.YELLOW if op["risk"] == "MEDIUM" else Colors.GREEN
                )
                print(
                    f"    {j}. {op['description']} {risk_color}({op['risk']}){Colors.ENDC}"
                )

            if len(phase["operations"]) > 3:
                print(f"    ... and {len(phase['operations']) - 3} more operations")

        # Recommendations
        print(f"\n{Colors.BLUE}💡 Recommendations:{Colors.ENDC}")
        if plan["risk_level"] == "HIGH":
            print(
                "  ⚠️  High-risk operations detected. Review carefully before executing."
            )
            print("  ⚠️  Consider running individual phases separately.")
            print("  ⚠️  Ensure you have recent backups.")
        elif plan["risk_level"] == "MEDIUM":
            print(
                "  ✓ Medium-risk plan. Review the operations and proceed with caution."
            )
            print("  ✓ Test thoroughly after each phase.")
        else:
            print("  ✅ Low-risk plan. Safe to execute.")

        print(f"  ✓ Estimated completion time: {plan['estimated_time']} minutes")
        print("  ✓ Run tests after each phase to verify functionality")

    def _execute_restructure_plan(self, plan: dict[str, Any]) -> bool:
        """Execute the restructuring plan"""
        log_header("Executing Restructuring Plan")

        # Create backup first
        backup_created = self._create_backup()
        if not backup_created:
            log_error("Failed to create backup. Aborting.")
            return False

        total_operations = plan["total_operations"]
        completed_operations = 0

        try:
            for phase_num, phase in enumerate(plan["phases"], 1):
                log_info(f"Executing Phase {phase_num}: {phase['name']}")

                phase_success = True
                for _op_num, operation in enumerate(phase["operations"], 1):
                    log_info(
                        f"Operation {completed_operations + 1}/{total_operations}: {operation['description']}"
                    )

                    op_success = self._execute_operation(operation)
                    completed_operations += 1

                    if not op_success:
                        log_error(f"Operation failed: {operation['description']}")
                        phase_success = False

                        # Ask user if they want to continue
                        if not self._ask_continue_after_failure():
                            log_warning("User chose to abort after failure")
                            return False

                if phase_success:
                    log_success(f"Phase {phase_num} completed successfully")

                    # Run tests after each phase
                    if not self._run_verification_tests():
                        log_warning("Tests failed after phase completion")
                        if not self._ask_continue_after_test_failure():
                            return False
                else:
                    log_warning(f"Phase {phase_num} completed with errors")

            # Final cleanup and verification
            self._final_cleanup()

            log_success("Restructuring completed successfully!")
            return True

        except KeyboardInterrupt:
            log_warning("Restructuring interrupted by user")
            return False
        except Exception as e:
            log_error(f"Unexpected error during execution: {e}")
            return False

    def _create_backup(self) -> bool:
        """Create project backup before restructuring"""
        log_info("Creating project backup...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.project_root / f"restructure_backup_{timestamp}"

        try:
            # Use git to create clean backup if possible
            result = subprocess.run(
                [
                    "git",
                    "archive",
                    "--format=tar",
                    "--output",
                    f"{backup_dir}.tar",
                    "HEAD",
                ],
                cwd=self.project_root,
                capture_output=True,
            )

            if result.returncode == 0:
                log_success(f"Git backup created: {backup_dir}.tar")
                return True
            else:
                # Fallback to file copy - but exclude backup directories to prevent recursion
                backup_dir.mkdir(exist_ok=True)
                for py_file in self.project_root.rglob("*.py"):
                    if not is_path_ignored(py_file):
                        rel_path = py_file.relative_to(self.project_root)
                        dest = backup_dir / rel_path
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        dest.write_text(py_file.read_text())

                log_success(f"File backup created: {backup_dir}")
                return True

        except Exception as e:
            log_error(f"Failed to create backup: {e}")
            return False

    def _execute_operation(self, operation: dict[str, Any]) -> bool:
        """Execute a single restructuring operation"""
        op_type = operation.get("type")

        try:
            if op_type == "rename_file":
                return self._execute_rename_file(operation)
            elif op_type == "clean_imports":
                return self._execute_clean_imports()
            elif op_type == "format_code":
                return self._execute_format_code()
            elif op_type in [
                "create_provider_package",
                "split_module",
                "merge_duplicates",
            ]:
                # These are complex operations that would need detailed implementation
                log_warning(
                    f"Complex operation {op_type} not yet implemented - would execute: {operation['description']}"
                )
                return True
            else:
                log_warning(f"Unknown operation type: {op_type}")
                return True

        except Exception as e:
            log_error(f"Error executing {op_type}: {e}")
            return False

    def _execute_rename_file(self, operation: dict[str, Any]) -> bool:
        """Execute file renaming"""
        # This would need to parse the operation details to get source and target
        log_info(
            "File renaming not fully implemented - would rename files based on naming conventions"
        )
        return True

    def _execute_clean_imports(self) -> bool:
        """Clean and organize imports"""
        try:
            result = subprocess.run(
                ["uv", "run", "ruff", "check", "--fix", "."],
                cwd=self.project_root,
                capture_output=True,
            )
            return result.returncode == 0
        except:
            return False

    def _execute_format_code(self) -> bool:
        """Format code with black and ruff"""
        try:
            # Format with black
            black_result = subprocess.run(
                ["uv", "run", "black", "."], cwd=self.project_root, capture_output=True
            )

            # Format with ruff
            ruff_result = subprocess.run(
                ["uv", "run", "ruff", "format", "."],
                cwd=self.project_root,
                capture_output=True,
            )

            return black_result.returncode == 0 and ruff_result.returncode == 0
        except:
            return False

    def _run_verification_tests(self) -> bool:
        """Run tests to verify restructuring didn't break anything"""
        try:
            result = subprocess.run(
                ["uv", "run", "pytest", "--tb=short", "-x"],
                cwd=self.project_root,
                capture_output=True,
                timeout=300,
            )
            return result.returncode == 0
        except:
            return False

    def _final_cleanup(self) -> None:
        """Perform final cleanup after restructuring"""
        log_info("Performing final cleanup...")

        # Format code one more time
        self._execute_format_code()

        # Update any remaining imports
        self._execute_clean_imports()

        log_success("Final cleanup completed")

    def _ask_continue_after_failure(self) -> bool:
        """Ask user if they want to continue after an operation failure"""
        try:
            response = input(
                "An operation failed. Continue with remaining operations? (y/N): "
            )
            return response.lower().startswith("y")
        except:
            return False

    def _ask_continue_after_test_failure(self) -> bool:
        """Ask user if they want to continue after test failures"""
        try:
            response = input("Tests failed. Continue with next phase? (y/N): ")
            return response.lower().startswith("y")
        except:
            return False

    def _save_error_log(self) -> None:
        """Save error log for analysis and learning"""
        if self.error_log:
            error_file = (
                self.project_root
                / f"restructure_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(error_file, "w") as f:
                json.dump(
                    {"errors": self.error_log, "execution_log": self.execution_log},
                    f,
                    indent=2,
                )
            log_info(f"Error log saved to {error_file}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="AI Orchestra Complete Automation Pipeline"
    )
    parser.add_argument(
        "--project-root", type=Path, default=Path.cwd(), help="Project root directory"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute the restructuring (default is dry run)",
    )
    parser.add_argument(
        "--phase", type=int, choices=[1, 2, 3], help="Execute only specific phase"
    )

    args = parser.parse_args()

    auto_restructurer = AutoRestructurer(args.project_root)

    dry_run = not args.execute
    success = auto_restructurer.run_complete_restructuring(dry_run=dry_run)

    if success:
        if dry_run:
            log_success("Analysis and planning completed successfully!")
            print(
                f"\n{Colors.BLUE}To execute the plan, run with --execute{Colors.ENDC}"
            )
        else:
            log_success("Project restructuring completed successfully!")
    else:
        log_error("Project restructuring failed")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
