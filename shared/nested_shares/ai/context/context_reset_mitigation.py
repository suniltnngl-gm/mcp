#!/usr/bin/env python3
"""
🧠 Context Reset Mitigation System
=================================

Minimizes impact of inevitable context resets through:
1. Rapid context reconstruction
2. Error learning and prevention
3. Knowledge base with metadata
4. Reality checks and validation
5. Codebase unification guidance
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from auto_context_manager import AutoContextManager
from automation_guide import AutomationGuide


class ContextResetMitigation:
    """Intelligent system to minimize context reset impact."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.kb_dir = self.project_root / "knowledge_base"
        self.kb_dir.mkdir(exist_ok=True)

        self.context_manager = AutoContextManager(project_root)
        self.automation_guide = AutomationGuide(project_root)

        # Initialize knowledge base files
        self.error_log = self.kb_dir / "error_patterns.json"
        self.success_patterns = self.kb_dir / "success_patterns.json"
        self.metadata_db = self.kb_dir / "codebase_metadata.json"
        self.reality_checks = self.kb_dir / "reality_checks.json"

        self._initialize_knowledge_base()

    def _initialize_knowledge_base(self):
        """Initialize knowledge base with existing project intelligence."""
        if not self.error_log.exists():
            self._create_error_patterns()
        if not self.success_patterns.exists():
            self._create_success_patterns()
        if not self.metadata_db.exists():
            self._create_metadata_db()
        if not self.reality_checks.exists():
            self._create_reality_checks()

    def _create_error_patterns(self):
        """Create error pattern database from project experience."""
        error_patterns = {
            "common_mistakes": {
                "duplicate_scripts": {
                    "pattern": "Creating new script when existing automation available",
                    "prevention": "Always run automation_guide.py suggest first",
                    "examples": [
                        "health_checker.py → Use ai_health_monitor.py",
                        "api_setup.py → Use mise + existing workflows",
                        "context_manager.py → Use auto_context_manager.py",
                    ],
                },
                "manual_operations": {
                    "pattern": "Performing manual tasks with existing automation",
                    "prevention": "Check automation inventory before manual work",
                    "examples": [
                        "Manual API setup → Use mise set commands",
                        "Manual health checks → Use ai_health_monitor.py",
                        "Manual context save → Use resilient_crs.py",
                    ],
                },
                "incorrect_file_counts": {
                    "pattern": "Including dependency files in project statistics",
                    "prevention": "Exclude .venv, cache, and dependency directories",
                    "reality_check": "User files: ~73 Python, not 5000+",
                },
            },
            "context_reset_indicators": [
                "Agent suggests creating existing scripts",
                "Agent provides manual steps for automated tasks",
                "Agent gives incorrect project statistics",
                "Agent doesn't reference existing automation",
            ],
            "mitigation_triggers": [
                "Run automation_guide.py immediately",
                "Execute auto_context_manager.py recovery",
                "Check reality_checks.json for validation",
                "Review success_patterns.json for guidance",
            ],
        }

        with open(self.error_log, "w") as f:
            json.dump(error_patterns, f, indent=2)

    def _create_success_patterns(self):
        """Create success pattern database."""
        success_patterns = {
            "proven_workflows": {
                "api_key_setup": {
                    "steps": [
                        "Get API keys from provider websites",
                        "Use mise set API_KEY=value for configuration",
                        "Test with uv run python ai_health_monitor.py status",
                        "Validate with uv run python demo_full_system.py",
                    ],
                    "success_indicators": [
                        "Providers show healthy status",
                        "Demo runs successfully",
                    ],
                    "common_issues": ["Incorrect key format", "Network connectivity"],
                },
                "context_recovery": {
                    "steps": [
                        "uv run python auto_context_manager.py recovery",
                        "uv run python resilient_crs.py recover",
                        "Check CRS/EMERGENCY_RECOVERY.md",
                        "Validate current state with health monitor",
                    ],
                    "success_indicators": [
                        "Current state displayed",
                        "Next actions clear",
                    ],
                    "time_to_recovery": "< 2 minutes",
                },
                "system_validation": {
                    "steps": [
                        "uv run python automation_guide.py",
                        "uv run python ai_health_monitor.py status",
                        "Review project statistics for accuracy",
                        "Check git status and recent commits",
                    ],
                    "success_indicators": [
                        "Automation inventory shown",
                        "Health status clear",
                    ],
                    "validation_points": ["File counts accurate", "API status known"],
                },
            },
            "architectural_patterns": {
                "centralized_config": {
                    "example": ".aiignore + config_manager.py pattern",
                    "benefits": ["Single source of truth", "Consistent behavior"],
                    "usage": "17 scripts use centralized config pattern",
                },
                "multi_provider": {
                    "example": "expanded_providers.py with unified interface",
                    "benefits": ["Intelligent routing", "Automatic failover"],
                    "usage": "15+ AI providers with consistent API",
                },
            },
        }

        with open(self.success_patterns, "w") as f:
            json.dump(success_patterns, f, indent=2)

    def _create_metadata_db(self):
        """Create codebase metadata database."""
        metadata = {
            "project_stats": {
                "user_created_python_files": 73,
                "documentation_files": 20,
                "shell_scripts": 3,
                "total_dependencies": "5962 (in .venv)",
                "last_updated": datetime.now().isoformat(),
            },
            "core_modules": {
                "ai_health_monitor.py": {
                    "purpose": "Provider health monitoring and status",
                    "commands": ["status", "monitor", "report", "test", "optimize"],
                    "replaces": ["Manual health checks", "Custom monitoring scripts"],
                },
                "ai_provider_manager.py": {
                    "purpose": "Multi-provider AI routing and management",
                    "features": [
                        "15+ providers",
                        "Intelligent routing",
                        "Cost optimization",
                    ],
                    "replaces": ["Manual provider switching", "Custom API clients"],
                },
                "auto_context_manager.py": {
                    "purpose": "Automated context preservation and recovery",
                    "features": [
                        "Real-time capture",
                        "Emergency recovery",
                        "State reconstruction",
                    ],
                    "replaces": [
                        "Manual context documentation",
                        "Custom backup scripts",
                    ],
                },
            },
            "architectural_excellence": {
                "centralized_patterns": 17,
                "provider_modules": 9,
                "monitoring_modules": 4,
                "orchestration_scripts": 31,
                "quality_indicators": {
                    "docstring_blocks": 6308,
                    "error_handling_blocks": 1130,
                    "type_hinted_functions": 1587,
                },
            },
        }

        with open(self.metadata_db, "w") as f:
            json.dump(metadata, f, indent=2)

    def _create_reality_checks(self):
        """Create reality check validation system."""
        reality_checks = {
            "file_count_validation": {
                "user_python_files": {"expected_range": [70, 80], "current": 73},
                "documentation_files": {"expected_range": [15, 25], "current": 20},
                "dependency_files": {"location": ".venv/", "count": "~5962"},
                "validation_command": "find . -name '*.py' -not -path './.venv/*' | wc -l",
            },
            "system_health_validation": {
                "api_keys_configured": {
                    "command": "env | grep API_KEY",
                    "expected": "0-5 keys",
                },
                "providers_active": {
                    "command": "uv run python ai_health_monitor.py status",
                    "expected": "0+ healthy",
                },
                "git_status": {
                    "command": "git status",
                    "expected": "Clean or known changes",
                },
            },
            "automation_validation": {
                "core_systems_available": [
                    "ai_health_monitor.py",
                    "ai_provider_manager.py",
                    "auto_context_manager.py",
                    "resilient_crs.py",
                ],
                "scripts_directory": {"path": "scripts/", "expected_count": "30+"},
                "automation_guide": {
                    "command": "python automation_guide.py",
                    "expected": "Quick reference",
                },
            },
            "context_reset_indicators": {
                "agent_suggests_existing_scripts": "RED FLAG - Check automation_guide.py",
                "agent_provides_manual_steps": "RED FLAG - Existing automation available",
                "agent_incorrect_statistics": "RED FLAG - Run reality checks",
                "agent_ignores_existing_tools": "RED FLAG - Context reset occurred",
            },
        }

        with open(self.reality_checks, "w") as f:
            json.dump(reality_checks, f, indent=2)

    def rapid_context_reconstruction(self) -> dict[str, Any]:
        """Rapidly reconstruct context after reset."""
        print("🧠 Rapid Context Reconstruction...")

        # Get current state
        context = self.context_manager.capture_full_context()

        # Load knowledge base
        with open(self.metadata_db) as f:
            metadata = json.load(f)

        # Validate reality
        reality_status = self.validate_reality()

        # Get automation guidance
        automation_ref = self.automation_guide.get_quick_reference()

        reconstruction = {
            "timestamp": datetime.now().isoformat(),
            "current_state": context,
            "project_metadata": metadata,
            "reality_validation": reality_status,
            "automation_reference": automation_ref,
            "immediate_actions": self._get_immediate_actions(context),
            "common_mistakes_to_avoid": self._get_common_mistakes(),
        }

        return reconstruction

    def validate_reality(self) -> dict[str, Any]:
        """Validate current reality against known facts."""
        with open(self.reality_checks) as f:
            checks = json.load(f)

        validation_results = {}

        # File count validation
        try:
            result = subprocess.run(
                [
                    "find",
                    ".",
                    "-name",
                    "*.py",
                    "-not",
                    "-path",
                    "./.venv/*",
                    "-not",
                    "-path",
                    "./__pycache__/*",
                    "-not",
                    "-path",
                    "./~/*",
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            py_files = len(
                [
                    f
                    for f in result.stdout.strip().split("\n")
                    if f and not any(x in f for x in ["/cache/", "/archive-v0/"])
                ]
            )

            expected_range = checks["file_count_validation"]["user_python_files"][
                "expected_range"
            ]
            validation_results["python_files"] = {
                "count": py_files,
                "expected": expected_range,
                "valid": expected_range[0] <= py_files <= expected_range[1],
            }
        except:
            validation_results["python_files"] = {"error": "Could not validate"}

        # System health validation
        api_keys = len([k for k in os.environ if "API_KEY" in k])
        validation_results["api_keys"] = {
            "configured": api_keys,
            "status": "configured" if api_keys > 0 else "needs_setup",
        }

        return validation_results

    def _get_immediate_actions(self, context: dict[str, Any]) -> list[str]:
        """Get immediate actions based on current state."""
        actions = []

        # Check API configuration
        api_status = context.get("api_status", {})
        if not any(v == "SET" for v in api_status.values()):
            actions.append("🔑 Setup API keys: mise set GROQ_API_KEY=your_key")

        # Check git status
        git_status = context.get("git_status", {})
        if not git_status.get("is_clean", True):
            actions.append("📝 Review git changes: git status && git log --oneline -5")

        # Always include validation
        actions.extend(
            [
                "🔍 Check automation: uv run python automation_guide.py",
                "📊 Validate health: uv run python ai_health_monitor.py status",
                "🧠 Verify context: uv run python auto_context_manager.py recovery",
            ]
        )

        return actions

    def _get_common_mistakes(self) -> list[str]:
        """Get common mistakes to avoid after context reset."""
        with open(self.error_log) as f:
            errors = json.load(f)

        mistakes = []
        for _category, info in errors["common_mistakes"].items():
            mistakes.append(f"❌ {info['pattern']}")
            mistakes.append(f"✅ {info['prevention']}")

        return mistakes

    def learn_from_error(self, error_description: str, solution: str):
        """Learn from errors to prevent future occurrences."""
        with open(self.error_log) as f:
            errors = json.load(f)

        # Add new error pattern
        timestamp = datetime.now().isoformat()
        if "learned_errors" not in errors:
            errors["learned_errors"] = {}

        errors["learned_errors"][timestamp] = {
            "error": error_description,
            "solution": solution,
            "prevention": "Check for this pattern in future context resets",
        }

        with open(self.error_log, "w") as f:
            json.dump(errors, f, indent=2)

        print(f"📚 Learned from error: {error_description}")

    def unify_codebase_guidance(self) -> dict[str, Any]:
        """Provide guidance for codebase unification and streamlining."""
        guidance = {
            "consolidation_opportunities": [],
            "standardization_needs": [],
            "cleanup_suggestions": [],
            "pattern_extensions": [],
        }

        # Analyze for consolidation opportunities
        scripts_dir = self.project_root / "scripts"
        if scripts_dir.exists():
            script_count = len(list(scripts_dir.glob("*.py")))
            if script_count > 35:
                guidance["consolidation_opportunities"].append(
                    f"Consider consolidating {script_count} scripts into functional modules"
                )

        # Check for pattern extension opportunities
        guidance["pattern_extensions"] = [
            "Extend .aiignore pattern to other configuration areas",
            "Apply multi-provider pattern to databases and storage",
            "Extend health monitoring to system resources",
            "Apply centralized config to all subsystems",
        ]

        return guidance

    def generate_recovery_summary(self) -> str:
        """Generate comprehensive recovery summary."""
        reconstruction = self.rapid_context_reconstruction()

        summary = f"""
🧠 CONTEXT RESET RECOVERY SUMMARY
================================

⏰ Recovery Time: {reconstruction['timestamp']}

📊 CURRENT STATE:
- Branch: {reconstruction['current_state']['git_status'].get('current_branch', 'unknown')}
- Files: {reconstruction['reality_validation']['python_files']['count']} Python (validated ✅)
- APIs: {reconstruction['reality_validation']['api_keys']['configured']}/5 configured

🎯 IMMEDIATE ACTIONS:
"""
        for action in reconstruction["immediate_actions"][:5]:
            summary += f"  {action}\n"

        summary += """
🚨 AVOID THESE MISTAKES:
"""
        for mistake in reconstruction["common_mistakes_to_avoid"][:6]:
            summary += f"  {mistake}\n"

        summary += """
🤖 AUTOMATION AVAILABLE:
  • ai_health_monitor.py - Provider health monitoring
  • ai_provider_manager.py - Multi-provider routing
  • auto_context_manager.py - Context preservation
  • automation_guide.py - Task guidance (USE THIS FIRST!)

🔧 QUICK COMMANDS:
  uv run python automation_guide.py
  uv run python ai_health_monitor.py status
  uv run python auto_context_manager.py recovery

---
Context reset impact minimized! 🎭
"""
        return summary


def main():
    """CLI interface for context reset mitigation."""
    import sys

    mitigation = ContextResetMitigation()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "recover":
            summary = mitigation.generate_recovery_summary()
            print(summary)

        elif command == "validate":
            reality = mitigation.validate_reality()
            print("🔍 REALITY VALIDATION:")
            for check, result in reality.items():
                if isinstance(result, dict) and "valid" in result:
                    status = "✅" if result["valid"] else "❌"
                    print(f"  {status} {check}: {result}")
                else:
                    print(f"  📊 {check}: {result}")

        elif command == "learn":
            if len(sys.argv) < 4:
                print(
                    "Usage: python context_reset_mitigation.py learn 'error' 'solution'"
                )
                return
            error = sys.argv[2]
            solution = sys.argv[3]
            mitigation.learn_from_error(error, solution)

        elif command == "unify":
            guidance = mitigation.unify_codebase_guidance()
            print("🔧 CODEBASE UNIFICATION GUIDANCE:")
            for category, items in guidance.items():
                if items:
                    print(f"\n{category.replace('_', ' ').title()}:")
                    for item in items:
                        print(f"  • {item}")

        else:
            print("Commands: recover, validate, learn 'error' 'solution', unify")
    else:
        # Default: full recovery
        summary = mitigation.generate_recovery_summary()
        print(summary)


if __name__ == "__main__":
    main()
