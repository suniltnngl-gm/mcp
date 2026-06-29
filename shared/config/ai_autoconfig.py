#!/usr/bin/env python3
"""
🧙 AI Orchestra - Smart Auto-Configuration
=========================================

Intelligent detection, validation, and optimization of:
- API keys with multi-key pattern support
- Provider priority with smart auto-configuration
- Reality checking for actual API key validity
- Git/GitHub integration status
- Comprehensive configuration recommendations
"""

import contextlib
import os
import re
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

# Check if we have rich for fancy output
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from ai_orchestra.providers import get_provider_class

    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


class KeyInfo:
    """Information about a detected API key."""

    def __init__(self, name: str, value: str, provider: str, index: int | None = None):
        self.name = name
        self.value = value
        self.provider = provider
        self.index = index
        self.valid: bool | None = None
        self.error: str | None = None
        self.verified_at: float | None = None

    def mask(self) -> str:
        """Return a masked version of the key for display."""
        if not self.value:
            return "(empty)"

        if len(self.value) <= 8:
            return "****"

        return f"{self.value[:4]}...{self.value[-4:]}"

    def __repr__(self) -> str:
        return f"KeyInfo({self.name}, {self.mask()}, {self.provider}, {self.index})"


class GitStatus:
    """Git repository status information."""

    def __init__(self):
        self.has_git = False
        self.has_gh = False
        self.has_uncommitted_changes = False
        self.has_env_in_gitignore = False
        self.branch = ""
        self.gh_authenticated = False
        self.gh_token_set = bool(os.getenv("GH_TOKEN"))
        self.git_configured = False
        self.git_author_name = os.getenv("GIT_AUTHOR_NAME", "")
        self.git_author_email = os.getenv("GIT_AUTHOR_EMAIL", "")

    def check_status(self):
        """Check git and GitHub CLI status."""
        # Check for git
        self.has_git = shutil.which("git") is not None
        if not self.has_git:
            return

        try:
            # Check if we're in a git repo
            subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                check=True,
                capture_output=True,
            )

            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                check=True,
                capture_output=True,
            )
            self.branch = result.stdout.decode().strip()

            # Check for uncommitted changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                check=True,
                capture_output=True,
            )
            self.has_uncommitted_changes = bool(result.stdout.decode().strip())

            # Check if .env is in .gitignore
            gitignore_path = Path(".gitignore")
            if gitignore_path.exists():
                with open(gitignore_path) as f:
                    content = f.read()
                    self.has_env_in_gitignore = ".env" in content.splitlines()

            # Check if git user is configured
            try:
                name_result = subprocess.run(
                    ["git", "config", "user.name"],
                    check=True,
                    capture_output=True,
                )
                email_result = subprocess.run(
                    ["git", "config", "user.email"],
                    check=True,
                    capture_output=True,
                )
                self.git_configured = bool(
                    name_result.stdout.decode().strip()
                    and email_result.stdout.decode().strip()
                )
            except subprocess.CalledProcessError:
                self.git_configured = False

            # Check for GitHub CLI
            self.has_gh = shutil.which("gh") is not None
            if self.has_gh:
                try:
                    # Check if gh is authenticated
                    result = subprocess.run(
                        ["gh", "auth", "status"],
                        capture_output=True,
                    )
                    self.gh_authenticated = result.returncode == 0
                except Exception:
                    self.gh_authenticated = False

        except subprocess.CalledProcessError:
            # Not in a git repo
            self.has_git = False


class AIAutoConfig:
    """Smart auto-configuration for AI Orchestra."""

    def __init__(self):
        self.provider_patterns = {
            "groq": [r"^GROQ_API_KEY(?:_(\d+))?$", r"^GROQ_KEY(?:_(\d+))?$"],
            "cerebras": [
                r"^CEREBRAS_API_KEY(?:_(\d+))?$",
                r"^CEREBRAS_KEY(?:_(\d+))?$",
            ],
            "ai21": [r"^AI21_API_KEY(?:_(\d+))?$", r"^AI21_KEY(?:_(\d+))?$"],
            "together": [
                r"^TOGETHER_API_KEY(?:_(\d+))?$",
                r"^TOGETHER_KEY(?:_(\d+))?$",
            ],
            "cohere": [r"^COHERE_API_KEY(?:_(\d+))?$", r"^COHERE_KEY(?:_(\d+))?$"],
            "fireworks": [
                r"^FIREWORKS_API_KEY(?:_(\d+))?$",
                r"^FIREWORKS_KEY(?:_(\d+))?$",
            ],
            "hyperbolic": [
                r"^HYPERBOLIC_API_KEY(?:_(\d+))?$",
                r"^HYPERBOLIC_KEY(?:_(\d+))?$",
            ],
            "openrouter": [
                r"^OPENROUTER_API_KEY(?:_(\d+))?$",
                r"^OPENROUTER_KEY(?:_(\d+))?$",
            ],
            "sambanova": [
                r"^SAMBANOVA_API_KEY(?:_(\d+))?$",
                r"^SAMBANOVA_KEY(?:_(\d+))?$",
            ],
            "openai": [r"^OPENAI_API_KEY(?:_(\d+))?$", r"^OPENAI_KEY(?:_(\d+))?$"],
            "anthropic": [
                r"^ANTHROPIC_API_KEY(?:_(\d+))?$",
                r"^ANTHROPIC_KEY(?:_(\d+))?$",
            ],
            "mistral": [r"^MISTRAL_API_KEY(?:_(\d+))?$", r"^MISTRAL_KEY(?:_(\d+))?$"],
            "perplexity": [
                r"^PERPLEXITY_API_KEY(?:_(\d+))?$",
                r"^PERPLEXITY_KEY(?:_(\d+))?$",
            ],
            "deepseek": [
                r"^DEEPSEEK_API_KEY(?:_(\d+))?$",
                r"^DEEPSEEK_KEY(?:_(\d+))?$",
            ],
            "replicate": [
                r"^REPLICATE_API_TOKEN(?:_(\d+))?$",
                r"^REPLICATE_KEY(?:_(\d+))?$",
            ],
        }

        self.provider_tiers = {
            "groq": "free",
            "cerebras": "free",
            "ai21": "free",
            "together": "free",
            "cohere": "free",
            "fireworks": "free",
            "hyperbolic": "free",
            "openrouter": "free",
            "sambanova": "free",
            "openai": "premium",
            "anthropic": "premium",
            "mistral": "premium",
            "perplexity": "low",
            "deepseek": "low",
            "replicate": "premium",
        }

        # Load provider config from ai_provider_manager if available
        self.providers_from_manager = self._load_provider_config()
        self.git_status = GitStatus()
        self.git_status.check_status()

    def _load_provider_config(self) -> dict:
        """Attempt to load provider config from ai_provider_manager."""
        try:
            from ai_provider_manager import SmartProviderRouter

            router = SmartProviderRouter()
            return router.metrics
        except ImportError:
            return {}
        except Exception:
            return {}

    def find_env_files(self) -> list[Path]:
        """Find .env files in the current directory."""
        return list(Path(".").glob(".env*"))

    def detect_api_keys(self) -> dict[str, list[KeyInfo]]:
        """Detect API keys from environment variables."""
        keys_by_provider = {}

        # Check all environment variables
        for name, value in os.environ.items():
            if not value:  # Skip empty values
                continue

            # Check if this matches any provider pattern
            for provider, patterns in self.provider_patterns.items():
                for pattern in patterns:
                    match = re.match(pattern, name)
                    if match:
                        # Extract index (if any)
                        index = None
                        if match.groups() and match.group(1):
                            with contextlib.suppress(ValueError):
                                index = int(match.group(1))
                        elif name.endswith("_2"):
                            index = 2
                        elif name.endswith("_3"):
                            index = 3

                        # Create key info
                        key_info = KeyInfo(name, value, provider, index)

                        # Add to provider list
                        if provider not in keys_by_provider:
                            keys_by_provider[provider] = []
                        keys_by_provider[provider].append(key_info)
                        break

        # Sort keys by index for each provider
        for provider in keys_by_provider:
            keys_by_provider[provider].sort(key=lambda k: k.index if k.index else 1)

        return keys_by_provider

    def validate_api_key(self, key_info: KeyInfo) -> bool:
        """Validate an API key by testing it (basic format check)."""
        provider_class = get_provider_class(key_info.provider)
        provider_instance = provider_class(key_info)
        return provider_instance.validate_key()

    def deep_validate_api_key(self, key_info: KeyInfo) -> bool:
        """Perform a more thorough validation by actually testing the API."""
        provider_class = get_provider_class(key_info.provider)
        provider_instance = provider_class(key_info)
        return provider_instance.deep_validate_key()

    def generate_smart_provider_priority(
        self, keys_by_provider: dict[str, list[KeyInfo]]
    ) -> str:
        """Generate smart provider priority based on available keys."""
        # Start with free providers
        priority = []

        # First add free providers with keys
        free_providers = [
            p for p in keys_by_provider if self.provider_tiers.get(p) == "free"
        ]
        priority.extend(sorted(free_providers, key=lambda p: -len(keys_by_provider[p])))

        # Then add low-cost providers with keys
        low_providers = [
            p for p in keys_by_provider if self.provider_tiers.get(p) == "low"
        ]
        priority.extend(sorted(low_providers, key=lambda p: -len(keys_by_provider[p])))

        # Finally add premium providers with keys
        premium_providers = [
            p for p in keys_by_provider if self.provider_tiers.get(p) == "premium"
        ]
        priority.extend(
            sorted(premium_providers, key=lambda p: -len(keys_by_provider[p]))
        )

        return ",".join(priority)

    def create_shell_exports(
        self, keys_by_provider: dict[str, list[KeyInfo]], provider_priority: str
    ) -> str:
        """Create shell export commands for detected keys."""
        exports = [
            "# Generated by AI Orchestra Autoconfig",
            f"# {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]

        # Add provider priority
        exports.append(f'export AI_PROVIDER_PRIORITY="{provider_priority}"')

        # Add strategy based on available providers
        free_providers = [
            p for p in keys_by_provider if self.provider_tiers.get(p) == "free"
        ]
        if free_providers:
            exports.append(
                'export AI_STRATEGY="cost_optimized"  # Using free providers first'
            )
        else:
            exports.append(
                'export AI_STRATEGY="balanced"  # Balancing available providers'
            )

        exports.append("")

        # Add key exports by tier
        exports.append("# Free tier providers")
        for provider in sorted(keys_by_provider.keys()):
            if self.provider_tiers.get(provider) != "free":
                continue

            exports.append(
                f"# {provider.title()} ({len(keys_by_provider[provider])} keys)"
            )
            for key_info in keys_by_provider[provider]:
                exports.append(f'export {key_info.name}="{key_info.value}"')
            exports.append("")

        exports.append("# Low-cost providers")
        for provider in sorted(keys_by_provider.keys()):
            if self.provider_tiers.get(provider) != "low":
                continue

            exports.append(
                f"# {provider.title()} ({len(keys_by_provider[provider])} keys)"
            )
            for key_info in keys_by_provider[provider]:
                exports.append(f'export {key_info.name}="{key_info.value}"')
            exports.append("")

        exports.append("# Premium providers")
        for provider in sorted(keys_by_provider.keys()):
            if self.provider_tiers.get(provider) != "premium":
                continue

            exports.append(
                f"# {provider.title()} ({len(keys_by_provider[provider])} keys)"
            )
            for key_info in keys_by_provider[provider]:
                exports.append(f'export {key_info.name}="{key_info.value}"')
            exports.append("")

        return "\n".join(exports)

    def create_env_file(
        self, keys_by_provider: dict[str, list[KeyInfo]], provider_priority: str
    ) -> str:
        """Create .env file content based on detected keys."""
        env_content = [
            "# AI Orchestra Configuration (.env)",
            f"# Generated by ai_autoconfig.py on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "# Only keys with actual values are uncommented",
            "",
            f'AI_PROVIDER_PRIORITY="{provider_priority}"',
            'AI_STRATEGY="cost_optimized"',
            'AI_DEBUG="false"',
            'AI_TIMEOUT="30"',
            "",
        ]

        # Add keys by tier
        env_content.append("# 🆓 Free Providers")
        env_content.append("# ===============")

        # Get all possible free providers
        free_providers = [
            p for p, tier in self.provider_tiers.items() if tier == "free"
        ]
        for provider in sorted(free_providers):
            keys = keys_by_provider.get(provider, [])

            env_content.append(f"# {provider.title()} configuration")
            # Add the standard key pattern for this provider
            base_key = f"{provider.upper()}_API_KEY"

            if provider in keys_by_provider:
                # Add actual keys that we found
                for key_info in keys:
                    env_content.append(f'{key_info.name}="{key_info.value}"')

                # Add placeholders for additional keys
                max_index = max([k.index or 1 for k in keys]) if keys else 0
                for i in range(
                    max_index + 1, max_index + 2
                ):  # Add one more than we found
                    suffix = f"_{i}" if i > 1 else ""
                    env_content.append(f'# {base_key}{suffix}=""')
            else:
                # Provider not configured, add commented placeholders
                env_content.append(f'# {base_key}=""')
                env_content.append(f'# {base_key}_2=""')

            env_content.append("")

        # Low-cost providers
        env_content.append("# 💸 Low-Cost Providers")
        env_content.append("# ===================")

        low_providers = [p for p, tier in self.provider_tiers.items() if tier == "low"]
        for provider in sorted(low_providers):
            keys = keys_by_provider.get(provider, [])

            env_content.append(f"# {provider.title()} configuration")
            base_key = f"{provider.upper()}_API_KEY"

            if provider in keys_by_provider:
                for key_info in keys:
                    env_content.append(f'{key_info.name}="{key_info.value}"')

                max_index = max([k.index or 1 for k in keys]) if keys else 0
                for i in range(max_index + 1, max_index + 2):
                    suffix = f"_{i}" if i > 1 else ""
                    env_content.append(f'# {base_key}{suffix}=""')
            else:
                env_content.append(f'# {base_key}=""')

            env_content.append("")

        # Premium providers
        env_content.append("# 💰 Premium Providers")
        env_content.append("# ==================")

        premium_providers = [
            p for p, tier in self.provider_tiers.items() if tier == "premium"
        ]
        for provider in sorted(premium_providers):
            keys = keys_by_provider.get(provider, [])

            env_content.append(f"# {provider.title()} configuration")
            base_key = f"{provider.upper()}_API_KEY"
            if provider == "replicate":
                base_key = "REPLICATE_API_TOKEN"

            if provider in keys_by_provider:
                for key_info in keys:
                    env_content.append(f'{key_info.name}="{key_info.value}"')

                max_index = max([k.index or 1 for k in keys]) if keys else 0
                for i in range(max_index + 1, max_index + 2):
                    suffix = f"_{i}" if i > 1 else ""
                    env_content.append(f'# {base_key}{suffix}=""')
            else:
                env_content.append(f'# {base_key}=""')

            env_content.append("")

        # Git configuration
        env_content.append("# 📦 Git/GitHub Configuration")
        env_content.append("# =========================")

        if self.git_status.git_author_name:
            env_content.append(f'GIT_AUTHOR_NAME="{self.git_status.git_author_name}"')
        else:
            env_content.append('# GIT_AUTHOR_NAME=""')

        if self.git_status.git_author_email:
            env_content.append(f'GIT_AUTHOR_EMAIL="{self.git_status.git_author_email}"')
        else:
            env_content.append('# GIT_AUTHOR_EMAIL=""')

        if self.git_status.gh_token_set:
            env_content.append(
                "# GH_TOKEN is set in environment (not added to .env for security)"
            )
        else:
            env_content.append('# GH_TOKEN=""  # GitHub CLI token for API access')

        return "\n".join(env_content)

    def print_key_summary(self, keys_by_provider: dict[str, list[KeyInfo]]):
        """Print a summary of detected keys."""
        total_keys = sum(len(keys) for keys in keys_by_provider.values())

        if RICH_AVAILABLE:
            # Create table with rich
            table = Table(show_header=True, header_style="bold blue")
            table.add_column("Provider", style="cyan")
            table.add_column("Tier", style="green")
            table.add_column("Keys", justify="right", style="magenta")
            table.add_column("Key Details", style="yellow")

            # Add rows
            for provider in sorted(keys_by_provider.keys()):
                keys = keys_by_provider[provider]
                tier = self.provider_tiers.get(provider, "unknown")
                tier_icon = "🆓" if tier == "free" else "💸" if tier == "low" else "💰"

                # Format key details
                key_details = []
                for key in keys:
                    key_details.append(f"{key.name}={key.mask()}")

                table.add_row(
                    f"{provider.title()}",
                    f"{tier_icon} {tier}",
                    str(len(keys)),
                    ", ".join(key_details),
                )

            # Print summary
            console.print(
                Panel.fit(
                    f"Detected {total_keys} API keys across {len(keys_by_provider)} providers",
                    style="bold cyan",
                )
            )
            console.print(table)

        else:
            # Plain text summary
            print(
                f"Detected {total_keys} API keys across {len(keys_by_provider)} providers:"
            )

            for provider in sorted(keys_by_provider.keys()):
                keys = keys_by_provider[provider]
                tier = self.provider_tiers.get(provider, "unknown")
                tier_label = (
                    "FREE"
                    if tier == "free"
                    else "LOW-COST" if tier == "low" else "PREMIUM"
                )

                print(f"  - {provider.title()} ({tier_label}): {len(keys)} keys")
                for key in keys:
                    print(f"    * {key.name}={key.mask()}")

    def print_git_status(self):
        """Print git and GitHub status information."""
        if RICH_AVAILABLE:
            git_panel = Panel(
                "\n".join(
                    [
                        f"Git Installed: {'✅' if self.git_status.has_git else '❌'}",
                        f"In Git Repository: {'✅' if self.git_status.has_git else '❌'}",
                        f"Current Branch: {self.git_status.branch or 'N/A'}",
                        f"Uncommitted Changes: {'⚠️ Yes' if self.git_status.has_uncommitted_changes else '✅ No'}",
                        f".env in .gitignore: {'✅ Yes' if self.git_status.has_env_in_gitignore else '⚠️ No'}",
                        f"Git User Configured: {'✅ Yes' if self.git_status.git_configured else '⚠️ No'}",
                        f"GitHub CLI: {'✅ Available' if self.git_status.has_gh else '❌ Not found'}",
                        f"GitHub Authenticated: {'✅ Yes' if self.git_status.gh_authenticated else '❌ No'}",
                        f"GH_TOKEN: {'✅ Set' if self.git_status.gh_token_set else '❌ Not set'}",
                    ]
                ),
                title="📦 Git and GitHub Status",
                style="cyan",
            )
            console.print(git_panel)
        else:
            print("\nGit and GitHub Status:")
            print(f"  - Git Installed: {'Yes' if self.git_status.has_git else 'No'}")
            print(
                f"  - In Git Repository: {'Yes' if self.git_status.has_git else 'No'}"
            )
            if self.git_status.has_git:
                print(f"  - Current Branch: {self.git_status.branch or 'N/A'}")
                print(
                    f"  - Uncommitted Changes: {'Yes' if self.git_status.has_uncommitted_changes else 'No'}"
                )
                print(
                    f"  - .env in .gitignore: {'Yes' if self.git_status.has_env_in_gitignore else 'No'}"
                )
                print(
                    f"  - Git User Configured: {'Yes' if self.git_status.git_configured else 'No'}"
                )
            print(
                f"  - GitHub CLI: {'Available' if self.git_status.has_gh else 'Not found'}"
            )
            if self.git_status.has_gh:
                print(
                    f"  - GitHub Authenticated: {'Yes' if self.git_status.gh_authenticated else 'No'}"
                )
            print(
                f"  - GH_TOKEN: {'Set' if self.git_status.gh_token_set else 'Not set'}"
            )

    def print_recommendations(self, keys_by_provider: dict[str, list[KeyInfo]]):
        """Print recommendations based on configuration."""
        recommendations = []

        # Check for missing free providers
        free_providers = {
            p for p, tier in self.provider_tiers.items() if tier == "free"
        }
        configured_free = {
            p for p in keys_by_provider if self.provider_tiers.get(p) == "free"
        }
        missing_free = free_providers - configured_free

        if missing_free:
            recommendations.append(
                f"Add keys for free providers: {', '.join(sorted(p.title() for p in missing_free))}"
            )

        # Check for single keys (recommend multiple)
        single_key_providers = [
            p for p in keys_by_provider if len(keys_by_provider[p]) == 1
        ]
        if single_key_providers:
            recommendations.append(
                f"Add additional keys for: {', '.join(sorted(p.title() for p in single_key_providers))}"
            )

        # Git recommendations
        if self.git_status.has_git:
            if not self.git_status.has_env_in_gitignore:
                recommendations.append(
                    "Add .env to .gitignore to prevent committing secrets"
                )

            if self.git_status.has_uncommitted_changes:
                recommendations.append(
                    "Commit or stash changes before making configuration changes"
                )

            if not self.git_status.git_configured:
                recommendations.append("Configure git user.name and user.email")

        # GitHub recommendations
        if self.git_status.has_gh and not self.git_status.gh_authenticated:
            recommendations.append("Run 'gh auth login' to authenticate GitHub CLI")

        # Environment recommendations
        if not keys_by_provider:
            recommendations.append("Configure at least one provider API key")
        else:
            if not any(self.provider_tiers.get(p) == "free" for p in keys_by_provider):
                recommendations.append(
                    "Consider adding free tier providers to reduce costs"
                )

        # Ensure proper .env file
        env_files = self.find_env_files()
        if not any(f.name == ".env" for f in env_files):
            recommendations.append("Create a .env file from the template")

        if RICH_AVAILABLE:
            if recommendations:
                rec_panel = Panel(
                    "\n".join([f"• {rec}" for rec in recommendations]),
                    title="💡 Recommendations",
                    style="green",
                )
                console.print(rec_panel)
            else:
                console.print(
                    Panel(
                        "✅ Configuration looks good!",
                        title="💡 Recommendations",
                        style="green",
                    )
                )
        else:
            print("\nRecommendations:")
            if recommendations:
                for rec in recommendations:
                    print(f"  • {rec}")
            else:
                print("  ✅ Configuration looks good!")

    def run_auto_config(
        self,
        validate_keys: bool = False,
        deep_validate: bool = False,
        generate_env: bool = False,
        generate_exports: bool = False,
    ):
        """Run the auto-configuration process."""
        if RICH_AVAILABLE:
            console.print(
                Panel.fit("🧙 AI Orchestra Smart Auto-Configuration", style="bold cyan")
            )
        else:
            print("=== 🧙 AI Orchestra Smart Auto-Configuration ===")

        # Detect API keys
        if RICH_AVAILABLE:
            with console.status("Detecting API keys..."):
                keys_by_provider = self.detect_api_keys()
        else:
            print("Detecting API keys...")
            keys_by_provider = self.detect_api_keys()

        # Validate keys if requested
        if validate_keys:
            if RICH_AVAILABLE:
                with console.status("Validating API keys..."):
                    for _provider, keys in keys_by_provider.items():
                        for key in keys:
                            if deep_validate:
                                self.deep_validate_api_key(key)
                            else:
                                self.validate_api_key(key)
            else:
                print("Validating API keys...")
                for _provider, keys in keys_by_provider.items():
                    for key in keys:
                        if deep_validate:
                            self.deep_validate_api_key(key)
                        else:
                            self.validate_api_key(key)

        # Generate provider priority
        provider_priority = self.generate_smart_provider_priority(keys_by_provider)

        # Print summary
        self.print_key_summary(keys_by_provider)

        if RICH_AVAILABLE:
            console.print(
                f"\n🎯 Recommended Provider Priority: [cyan]{provider_priority}[/cyan]"
            )
        else:
            print(f"\nRecommended Provider Priority: {provider_priority}")

        # Print git status
        self.print_git_status()

        # Print recommendations
        self.print_recommendations(keys_by_provider)

        # Generate .env file if requested
        if generate_env:
            env_content = self.create_env_file(keys_by_provider, provider_priority)
            env_path = Path(".env.generated")

            with open(env_path, "w") as f:
                f.write(env_content)

            if RICH_AVAILABLE:
                console.print(f"\n✅ Generated .env file: [cyan]{env_path}[/cyan]")
                console.print("   Copy this to .env to use these settings.")
            else:
                print(f"\nGenerated .env file: {env_path}")
                print("Copy this to .env to use these settings.")

        # Generate shell exports if requested
        if generate_exports:
            exports = self.create_shell_exports(keys_by_provider, provider_priority)
            exports_path = Path("exports.sh")

            with open(exports_path, "w") as f:
                f.write(exports)

            if RICH_AVAILABLE:
                console.print(
                    f"\n✅ Generated shell exports: [cyan]{exports_path}[/cyan]"
                )
                console.print("   Source this file to load the configuration:")
                console.print("   [green]source exports.sh[/green]")
            else:
                print(f"\nGenerated shell exports: {exports_path}")
                print("Source this file to load the configuration:")
                print("  source exports.sh")


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="🧙 AI Orchestra Smart Auto-Configuration"
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validate API keys (basic format check)"
    )
    parser.add_argument(
        "--deep-validate",
        action="store_true",
        help="Deep validate API keys (makes API calls)",
    )
    parser.add_argument("--env", action="store_true", help="Generate .env file")
    parser.add_argument("--exports", action="store_true", help="Generate shell exports")
    parser.add_argument("--all", action="store_true", help="Enable all options")

    args = parser.parse_args()

    # If --all, enable everything
    if args.all:
        args.validate = True
        args.env = True
        args.exports = True

    # Run auto-config
    auto_config = AIAutoConfig()
    auto_config.run_auto_config(
        validate_keys=args.validate or args.deep_validate,
        deep_validate=args.deep_validate,
        generate_env=args.env,
        generate_exports=args.exports,
    )


if __name__ == "__main__":
    main()
