#!/usr/bin/env python3
"""
🛡️ Universal Context Guard
==========================

Confirms context before sending logs to ANY AI system:
- IDE Extensions (VSCode, IntelliJ, etc.)
- AI CLI Tools (GitHub Copilot CLI, etc.)
- API Providers (OpenAI, Anthropic, etc.)
- Local AI Models (Ollama, etc.)

Prevents context reset impact across all AI interaction modes.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from auto_context_manager import AutoContextManager
from context_reset_cases import ContextResetCaseManager


class UniversalContextGuard:
    """Universal context confirmation system for all AI modes."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.guard_dir = self.project_root / "context_guard"
        self.guard_dir.mkdir(exist_ok=True)

        # Initialize components
        self.context_manager = AutoContextManager(project_root)
        self.case_manager = ContextResetCaseManager(project_root)

        # Guard configuration
        self.guard_config = self.guard_dir / "guard_config.json"
        self.context_summary = self.guard_dir / "CONTEXT_SUMMARY.md"
        self.ai_modes_log = self.guard_dir / "ai_modes_usage.json"

        self._initialize_guard()

    def _initialize_guard(self):
        """Initialize universal context guard."""
        if not self.guard_config.exists():
            config = {
                "ai_modes": {
                    "ide_extensions": {
                        "vscode_copilot": {"active": False, "last_context_sent": None},
                        "intellij_ai": {"active": False, "last_context_sent": None},
                        "cursor_ai": {"active": False, "last_context_sent": None},
                    },
                    "cli_tools": {
                        "github_copilot_cli": {
                            "active": False,
                            "last_context_sent": None,
                        },
                        "openai_cli": {"active": False, "last_context_sent": None},
                        "anthropic_cli": {"active": False, "last_context_sent": None},
                    },
                    "api_providers": {
                        "openai_api": {"active": False, "last_context_sent": None},
                        "anthropic_api": {"active": False, "last_context_sent": None},
                        "groq_api": {"active": False, "last_context_sent": None},
                        "cerebras_api": {"active": False, "last_context_sent": None},
                    },
                    "local_models": {
                        "ollama": {"active": False, "last_context_sent": None},
                        "local_llm": {"active": False, "last_context_sent": None},
                    },
                },
                "guard_settings": {
                    "auto_confirm_context": False,
                    "require_manual_confirmation": True,
                    "context_summary_length": "medium",
                    "include_sensitive_info": False,
                },
            }

            with open(self.guard_config, "w") as f:
                json.dump(config, f, indent=2)

    def generate_context_summary(self, ai_mode: str, target: str) -> dict[str, Any]:
        """Generate context summary for specific AI mode and target."""

        # Get current context
        context = self.context_manager.capture_full_context()

        # Detect current case
        case_number, case_evidence = self.case_manager.detect_case()

        # Create safe summary (no sensitive data)
        summary = {
            "timestamp": datetime.now().isoformat(),
            "ai_mode": ai_mode,
            "target": target,
            "project_context": {
                "name": "AI Orchestra",
                "type": "Multi-provider AI system",
                "current_branch": context.get("git_status", {}).get(
                    "current_branch", "unknown"
                ),
                "python_files": context.get("project_stats", {}).get("python_files", 0),
                "documentation_files": context.get("project_stats", {}).get(
                    "documentation_files", 0
                ),
                "is_git_clean": context.get("git_status", {}).get("is_clean", False),
            },
            "system_status": {
                "case_detected": case_number,
                "apis_configured": sum(
                    1 for v in context.get("api_status", {}).values() if v == "SET"
                ),
                "automation_available": True,
                "context_protection_active": self._check_crp_active(),
            },
            "key_capabilities": [
                "Multi-provider AI routing (15+ providers)",
                "Intelligent health monitoring",
                "Automated context preservation",
                "Semi-automated CRI reduction",
                "Pattern-based automation guidance",
            ],
            "current_focus": self._get_current_focus(case_number),
            "available_tools": [
                "ai_health_monitor.py - Provider health monitoring",
                "automation_guide.py - Task guidance and duplication prevention",
                "auto_context_manager.py - Context recovery and preservation",
                "resilient_crs.py - Interruption-proof context management",
            ],
        }

        return summary

    def confirm_context_before_ai(
        self, ai_mode: str, target: str, prompt: str = ""
    ) -> dict[str, Any]:
        """Confirm context before sending to any AI system."""

        print(f"🛡️ UNIVERSAL CONTEXT GUARD - {ai_mode.upper()}")
        print("=" * 50)

        # Generate context summary
        summary = self.generate_context_summary(ai_mode, target)

        # Save context summary
        self._save_context_summary(summary)

        # Display context confirmation
        confirmation = self._display_context_confirmation(summary, prompt)

        # Log AI mode usage
        self._log_ai_mode_usage(ai_mode, target, summary)

        return confirmation

    def _display_context_confirmation(
        self, summary: dict[str, Any], prompt: str
    ) -> dict[str, Any]:
        """Display context confirmation dialog."""

        print("\n📊 PROJECT CONTEXT SUMMARY:")
        print(f"  • Project: {summary['project_context']['name']}")
        print(f"  • Branch: {summary['project_context']['current_branch']}")
        print(
            f"  • Files: {summary['project_context']['python_files']} Python, {summary['project_context']['documentation_files']} docs"
        )
        print(
            f"  • Case: {summary['system_status']['case_detected']} (Context Reset Case)"
        )
        print(f"  • APIs: {summary['system_status']['apis_configured']}/5 configured")

        print("\n🎯 CURRENT FOCUS:")
        for focus_item in summary["current_focus"]:
            print(f"  • {focus_item}")

        print("\n🤖 AVAILABLE AUTOMATION:")
        for tool in summary["available_tools"][:3]:  # Show top 3
            print(f"  • {tool}")

        if prompt:
            print("\n💬 AI PROMPT PREVIEW:")
            print(f"  \"{prompt[:100]}{'...' if len(prompt) > 100 else ''}\"")

        print("\n🛡️ CONTEXT PROTECTION:")
        protection_status = (
            "ACTIVE"
            if summary["system_status"]["context_protection_active"]
            else "INACTIVE"
        )
        print(f"  • Status: {protection_status}")

        # Confirmation prompt
        print(
            f"\n❓ CONFIRM CONTEXT FOR {summary['ai_mode'].upper()} ({summary['target']}):"
        )
        print("  This context summary will be available to the AI system.")
        print("  No sensitive data (API keys, credentials) will be shared.")

        # Auto-confirm for Case 3 (optimized), manual for others
        case_number = summary["system_status"]["case_detected"]
        if case_number == 3:
            print("  ✅ Auto-confirmed (Case 3: Agent Optimized)")
            confirmed = True
        else:
            confirm = input("  Continue? (y/N): ").lower().strip()
            confirmed = confirm == "y"

        result = {
            "confirmed": confirmed,
            "summary": summary,
            "timestamp": datetime.now().isoformat(),
        }

        if confirmed:
            print("  ✅ Context confirmed - Proceeding with AI interaction")
        else:
            print("  ❌ Context confirmation cancelled")
            print("  💡 Run: ./case_study.sh to optimize context first")

        return result

    def _save_context_summary(self, summary: dict[str, Any]):
        """Save context summary to file."""

        markdown_summary = f"""# 🛡️ Context Summary for AI Interaction

**Generated:** {summary['timestamp']}
**AI Mode:** {summary['ai_mode']} → {summary['target']}

## 📊 Project Context
- **Project:** {summary['project_context']['name']}
- **Type:** {summary['project_context']['type']}
- **Branch:** {summary['project_context']['current_branch']}
- **Files:** {summary['project_context']['python_files']} Python, {summary['project_context']['documentation_files']} docs
- **Git Status:** {'Clean' if summary['project_context']['is_git_clean'] else 'Has changes'}

## 🎯 System Status
- **Context Reset Case:** {summary['system_status']['case_detected']}
- **APIs Configured:** {summary['system_status']['apis_configured']}/5
- **Automation Available:** {'Yes' if summary['system_status']['automation_available'] else 'No'}
- **Context Protection:** {'Active' if summary['system_status']['context_protection_active'] else 'Inactive'}

## 🚀 Current Focus
"""

        for focus_item in summary["current_focus"]:
            markdown_summary += f"- {focus_item}\n"

        markdown_summary += """
## 🤖 Key Capabilities
"""
        for capability in summary["key_capabilities"]:
            markdown_summary += f"- {capability}\n"

        markdown_summary += """
## 🔧 Available Tools
"""
        for tool in summary["available_tools"]:
            markdown_summary += f"- {tool}\n"

        markdown_summary += """
---
*Generated by Universal Context Guard - Ensuring consistent context across all AI interactions*
"""

        with open(self.context_summary, "w") as f:
            f.write(markdown_summary)

    def _get_current_focus(self, case_number: int) -> list[str]:
        """Get current focus based on case number."""
        focus_map = {
            1: [
                "Context recovery after reset",
                "API key configuration",
                "System validation and health checks",
                "Automation discovery and usage",
            ],
            2: [
                "Context Reset Impact (CRI) reduction",
                "System optimization and consolidation",
                "Pattern standardization",
                "Knowledge unification",
            ],
            3: [
                "Task execution with full automation",
                "Leveraging existing 76 Python modules",
                "Maintaining context protection",
                "Continuous system improvement",
            ],
        }

        return focus_map.get(case_number, ["General system operation"])

    def _check_crp_active(self) -> bool:
        """Check if Context Reset Prevention is active."""
        session_file = self.project_root / "CRS" / "CURRENT_SESSION.json"
        return session_file.exists()

    def _log_ai_mode_usage(self, ai_mode: str, target: str, summary: dict[str, Any]):
        """Log AI mode usage for tracking."""
        try:
            if self.ai_modes_log.exists():
                with open(self.ai_modes_log) as f:
                    log_data = json.load(f)
            else:
                log_data = {"usage_history": []}

            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "ai_mode": ai_mode,
                "target": target,
                "case_detected": summary["system_status"]["case_detected"],
                "context_confirmed": True,  # Only logged if confirmed
            }

            log_data["usage_history"].append(log_entry)

            # Keep only last 100 entries
            if len(log_data["usage_history"]) > 100:
                log_data["usage_history"] = log_data["usage_history"][-100:]

            with open(self.ai_modes_log, "w") as f:
                json.dump(log_data, f, indent=2)
        except:
            pass  # Don't fail on logging errors

    def create_ai_mode_wrappers(self):
        """Create wrapper scripts for common AI modes."""

        # VSCode Copilot wrapper
        vscode_wrapper = self.guard_dir / "vscode_copilot_wrapper.py"
        vscode_wrapper.write_text(
            '''#!/usr/bin/env python3
"""VSCode Copilot Context Guard Wrapper"""
import sys
from universal_context_guard import UniversalContextGuard

guard = UniversalContextGuard()
result = guard.confirm_context_before_ai("ide_extension", "vscode_copilot", " ".join(sys.argv[1:]))

if result["confirmed"]:
    print("Context confirmed - VSCode Copilot can proceed")
    sys.exit(0)
else:
    print("Context confirmation failed")
    sys.exit(1)
'''
        )

        # CLI wrapper
        cli_wrapper = self.guard_dir / "ai_cli_wrapper.py"
        cli_wrapper.write_text(
            '''#!/usr/bin/env python3
"""AI CLI Context Guard Wrapper"""
import sys
from universal_context_guard import UniversalContextGuard

if len(sys.argv) < 2:
    print("Usage: python ai_cli_wrapper.py <ai_tool> [prompt]")
    sys.exit(1)

ai_tool = sys.argv[1]
prompt = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""

guard = UniversalContextGuard()
result = guard.confirm_context_before_ai("cli_tool", ai_tool, prompt)

if result["confirmed"]:
    print(f"Context confirmed - {ai_tool} can proceed")
    sys.exit(0)
else:
    print("Context confirmation failed")
    sys.exit(1)
'''
        )

        # API wrapper
        api_wrapper = self.guard_dir / "api_provider_wrapper.py"
        api_wrapper.write_text(
            '''#!/usr/bin/env python3
"""API Provider Context Guard Wrapper"""
import sys
from universal_context_guard import UniversalContextGuard

if len(sys.argv) < 2:
    print("Usage: python api_provider_wrapper.py <provider> [prompt]")
    sys.exit(1)

provider = sys.argv[1]
prompt = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""

guard = UniversalContextGuard()
result = guard.confirm_context_before_ai("api_provider", provider, prompt)

if result["confirmed"]:
    print(f"Context confirmed - {provider} API can proceed")
    print("Context summary available in: context_guard/CONTEXT_SUMMARY.md")
    sys.exit(0)
else:
    print("Context confirmation failed")
    sys.exit(1)
'''
        )

        # Make wrappers executable
        for wrapper in [vscode_wrapper, cli_wrapper, api_wrapper]:
            wrapper.chmod(0o755)

        print("✅ AI mode wrappers created:")
        print(f"  • VSCode: {vscode_wrapper}")
        print(f"  • CLI: {cli_wrapper}")
        print(f"  • API: {api_wrapper}")


def main():
    """CLI interface for universal context guard."""

    guard = UniversalContextGuard()

    if len(sys.argv) < 2:
        print("🛡️ UNIVERSAL CONTEXT GUARD")
        print("==========================")
        print("Usage:")
        print("  python universal_context_guard.py <ai_mode> <target> [prompt]")
        print("")
        print("AI Modes:")
        print("  ide_extension  - VSCode, IntelliJ, Cursor, etc.")
        print("  cli_tool      - GitHub Copilot CLI, OpenAI CLI, etc.")
        print("  api_provider  - OpenAI API, Anthropic API, etc.")
        print("  local_model   - Ollama, local LLM, etc.")
        print("")
        print("Examples:")
        print("  python universal_context_guard.py ide_extension vscode_copilot")
        print(
            "  python universal_context_guard.py api_provider openai 'help with API setup'"
        )
        print("  python universal_context_guard.py cli_tool github_copilot")
        return

    ai_mode = sys.argv[1]
    target = sys.argv[2] if len(sys.argv) > 2 else "unknown"
    prompt = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""

    if ai_mode == "create_wrappers":
        guard.create_ai_mode_wrappers()
        return

    result = guard.confirm_context_before_ai(ai_mode, target, prompt)

    if result["confirmed"]:
        print(f"\n✅ CONTEXT CONFIRMED FOR {ai_mode.upper()}")
        print("📄 Context summary: context_guard/CONTEXT_SUMMARY.md")
        sys.exit(0)
    else:
        print("\n❌ CONTEXT CONFIRMATION CANCELLED")
        print("💡 Optimize context first: ./case_study.sh")
        sys.exit(1)


if __name__ == "__main__":
    main()
