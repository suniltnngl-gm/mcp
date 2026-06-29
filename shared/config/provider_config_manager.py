"""
🔧 Provider Configuration Manager
=================================

Centralized configuration system for managing all AI provider settings,
API keys, preferences, and optimization parameters.
"""

import logging
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import toml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
logger = logging.getLogger(__name__)


@dataclass
class ProviderConfig:
    """Configuration for a single AI provider."""

    name: str
    enabled: bool = True
    primary_api_key: str | None = None
    backup_api_keys: list[str] = None
    default_model: str = "default"
    max_tokens: int = 2000
    temperature: float = 0.7
    rate_limit_rpm: int | None = None
    priority: int = 50
    cost_tier: str = "medium"
    custom_settings: dict[str, Any] = None

    def __post_init__(self):
        if self.backup_api_keys is None:
            self.backup_api_keys = []
        if self.custom_settings is None:
            self.custom_settings = {}


@dataclass
class GlobalConfig:
    """Global configuration for the AI Orchestra system."""

    daily_budget_limit: float = 5.0
    preferred_cost_tier: str = "free"
    fallback_strategy: str = "intelligent"
    auto_failover: bool = True
    health_check_interval: int = 300  # seconds
    enable_metrics_collection: bool = True
    log_level: str = "INFO"
    max_concurrent_requests: int = 5
    request_timeout: int = 60

    # Provider preferences (0-100 scale)
    provider_preferences: dict[str, int] = None

    def __post_init__(self):
        if self.provider_preferences is None:
            self.provider_preferences = {
                "groq": 110,  # Ultra-fast, free
                "cerebras": 108,  # Ultra-fast, free
                "sambanova": 105,  # Fast, free, good limits
                "ollama": 100,  # Local, completely free
                "fireworks": 95,  # Fast, cheap
                "hyperbolic": 90,  # Fast, cheap
                "together": 85,  # Reliable, cheap
                "deepseek": 80,  # Very affordable
                "ai21": 75,  # Free tier
                "cohere": 70,  # Free tier
                "gemini": 65,  # Google, competitive
                "mistral": 60,  # Good performance
                "openrouter": 55,  # Multiple models
                "perplexity": 50,  # Limited but good for research
                "anthropic": 45,  # High quality, expensive
                "openai": 40,  # Excellent but expensive
                "huggingchat": 25,  # Often unreliable
                "replicate": 20,  # Pay-per-use, cold starts
                "mock": 10,  # Testing only
            }


class ProviderConfigManager:
    """Manages configuration for all AI providers with persistent storage."""

    def __init__(self, config_dir: Path | None = None):
        self.config_dir = config_dir or Path.home() / ".config" / "ai-orchestra"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.config_file = self.config_dir / "providers.toml"
        self.global_config_file = self.config_dir / "global.toml"
        self.secrets_file = self.config_dir / "secrets.env"

        # Load configurations
        self.providers: dict[str, ProviderConfig] = {}
        self.global_config = GlobalConfig()

        self._load_configurations()
        self._load_environment_keys()

    def _load_configurations(self):
        """Load provider and global configurations from files."""
        # Load provider configurations
        if self.config_file.exists():
            try:
                data = toml.load(self.config_file)
                for provider_name, config_data in data.get("providers", {}).items():
                    self.providers[provider_name] = ProviderConfig(
                        name=provider_name, **config_data
                    )
                console.print(
                    f"✅ Loaded configuration for {len(self.providers)} providers"
                )
            except Exception as e:
                logger.error(f"Failed to load provider config: {e}")

        # Load global configuration
        if self.global_config_file.exists():
            try:
                data = toml.load(self.global_config_file)
                config_dict = data.get("global", {})

                # Update global config with loaded values
                for key, value in config_dict.items():
                    if hasattr(self.global_config, key):
                        setattr(self.global_config, key, value)

                console.print("✅ Loaded global configuration")
            except Exception as e:
                logger.error(f"Failed to load global config: {e}")

    def _load_environment_keys(self):
        """Load API keys from environment variables and update provider configs."""
        env_prefixes = {
            "openai": "OPENAI",
            "anthropic": "ANTHROPIC",
            "mistral": "MISTRAL",
            "gemini": "GEMINI",
            "groq": "GROQ",
            "together": "TOGETHER",
            "cohere": "COHERE",
            "perplexity": "PERPLEXITY",
            "deepseek": "DEEPSEEK",
            "ollama": "OLLAMA",  # No keys needed
            "replicate": "REPLICATE",
            "openrouter": "OPENROUTER",
            "ai21": "AI21",
            "fireworks": "FIREWORKS",
            "cerebras": "CEREBRAS",
            "sambanova": "SAMBANOVA",
            "hyperbolic": "HYPERBOLIC",
            "huggingchat": "HUGGINGFACE",  # Special case
        }

        for provider_name, env_prefix in env_prefixes.items():
            if provider_name not in self.providers:
                self.providers[provider_name] = ProviderConfig(name=provider_name)

            provider_config = self.providers[provider_name]

            # Special handling for HuggingChat
            if provider_name == "huggingchat":
                email = os.getenv("HUGGINGFACE_EMAIL")
                password = os.getenv("HUGGINGFACE_PASSWORD")
                if email and password:
                    provider_config.custom_settings = {
                        "email": email,
                        "password": password,
                    }
                    provider_config.enabled = True
                continue

            # Standard API key loading
            primary_key = os.getenv(f"{env_prefix}_API_KEY")
            if primary_key:
                provider_config.primary_api_key = primary_key
                provider_config.enabled = True

            # Load backup keys
            backup_keys = []
            for i in range(1, 10):
                key = os.getenv(f"{env_prefix}_API_KEY_{i}")
                if key:
                    backup_keys.append(key)

            for suffix in ["BACKUP", "SECONDARY", "TERTIARY", "ALT", "SPARE"]:
                key = os.getenv(f"{env_prefix}_API_KEY_{suffix}")
                if key:
                    backup_keys.append(key)

            if backup_keys:
                provider_config.backup_api_keys = backup_keys

    def save_configurations(self):
        """Save current configurations to files."""
        try:
            # Save provider configurations (without sensitive data)
            provider_data = {"providers": {}}
            for name, config in self.providers.items():
                config_dict = asdict(config)
                # Remove sensitive data for persistent storage
                config_dict.pop("primary_api_key", None)
                config_dict.pop("backup_api_keys", None)
                if "password" in config_dict.get("custom_settings", {}):
                    config_dict["custom_settings"] = {
                        k: v
                        for k, v in config_dict["custom_settings"].items()
                        if k not in ["password", "email"]
                    }
                provider_data["providers"][name] = config_dict

            with open(self.config_file, "w") as f:
                toml.dump(provider_data, f)

            # Save global configuration
            global_data = {"global": asdict(self.global_config)}
            with open(self.global_config_file, "w") as f:
                toml.dump(global_data, f)

            console.print("✅ Configurations saved successfully")

        except Exception as e:
            logger.error(f"Failed to save configurations: {e}")

    def get_provider_config(self, provider_name: str) -> ProviderConfig | None:
        """Get configuration for a specific provider."""
        return self.providers.get(provider_name)

    def update_provider_config(self, provider_name: str, **updates):
        """Update configuration for a specific provider."""
        if provider_name not in self.providers:
            self.providers[provider_name] = ProviderConfig(name=provider_name)

        config = self.providers[provider_name]
        for key, value in updates.items():
            if hasattr(config, key):
                setattr(config, key, value)

        self.save_configurations()

    def enable_provider(self, provider_name: str):
        """Enable a specific provider."""
        self.update_provider_config(provider_name, enabled=True)

    def disable_provider(self, provider_name: str):
        """Disable a specific provider."""
        self.update_provider_config(provider_name, enabled=False)

    def get_enabled_providers(self) -> list[str]:
        """Get list of enabled provider names."""
        return [name for name, config in self.providers.items() if config.enabled]

    def get_free_providers(self) -> list[str]:
        """Get list of free tier providers."""
        free_providers = []
        for name, config in self.providers.items():
            if config.enabled and config.cost_tier in ["free"]:
                free_providers.append(name)
        return free_providers

    def get_providers_by_cost_tier(self, cost_tier: str) -> list[str]:
        """Get providers filtered by cost tier."""
        return [
            name
            for name, config in self.providers.items()
            if config.enabled and config.cost_tier == cost_tier
        ]

    def set_daily_budget(self, amount: float):
        """Set daily budget limit."""
        self.global_config.daily_budget_limit = amount
        self.save_configurations()

    def set_provider_priority(self, provider_name: str, priority: int):
        """Set priority for a provider (0-100, higher = more preferred)."""
        self.update_provider_config(provider_name, priority=priority)
        self.global_config.provider_preferences[provider_name] = priority
        self.save_configurations()

    def get_api_keys_for_provider(self, provider_name: str) -> list[str]:
        """Get all API keys for a provider (primary + backups)."""
        config = self.get_provider_config(provider_name)
        if not config:
            return []

        keys = []
        if config.primary_api_key:
            keys.append(config.primary_api_key)
        if config.backup_api_keys:
            keys.extend(config.backup_api_keys)

        return keys

    def display_configuration_status(self):
        """Display comprehensive configuration status."""
        table = Table(title="🔧 Provider Configuration Status")

        table.add_column("Provider", style="cyan", no_wrap=True)
        table.add_column("Status", justify="center")
        table.add_column("Keys", justify="center")
        table.add_column("Cost Tier", justify="center")
        table.add_column("Priority", justify="right")
        table.add_column("Default Model", style="yellow")

        for name, config in self.providers.items():
            status = "✅ Enabled" if config.enabled else "❌ Disabled"
            key_count = len(self.get_api_keys_for_provider(name))
            keys_display = f"{key_count} keys" if key_count > 0 else "No keys"

            # Special handling for providers that don't need API keys
            if name in ["ollama", "mock"]:
                keys_display = "N/A"
            elif name == "huggingchat":
                has_creds = bool(
                    config.custom_settings.get("email")
                    and config.custom_settings.get("password")
                )
                keys_display = "✅ Creds" if has_creds else "❌ No creds"

            table.add_row(
                config.name,
                status,
                keys_display,
                config.cost_tier.title(),
                str(config.priority),
                config.default_model,
            )

        console.print(table)

        # Display global settings
        console.print(
            Panel(
                f"""
**Global Configuration:**
💰 Daily Budget Limit: ${self.global_config.daily_budget_limit:.2f}
🎯 Preferred Cost Tier: {self.global_config.preferred_cost_tier.title()}
🔄 Auto Failover: {'Enabled' if self.global_config.auto_failover else 'Disabled'}
📊 Metrics Collection: {'Enabled' if self.global_config.enable_metrics_collection else 'Disabled'}
⏱️ Health Check Interval: {self.global_config.health_check_interval}s
🚀 Max Concurrent Requests: {self.global_config.max_concurrent_requests}
""",
                title="Global Settings",
                style="blue",
            )
        )

    def generate_setup_script(self) -> str:
        """Generate a bash script to set up all environment variables."""
        script_lines = [
            "#!/bin/bash",
            "# AI Orchestra Provider Setup Script",
            "# Generated automatically - customize as needed",
            "",
            "# ===========================================",
            "# 🌟 FREE TIER PROVIDERS (Recommended First)",
            "# ===========================================",
            "",
            "# Groq - Ultra-fast inference (14,400 tokens/day free)",
            "# Get key from: https://console.groq.com/",
            '# export GROQ_API_KEY="your-groq-key-here"',
            '# export GROQ_API_KEY_1="your-backup-groq-key"',
            "",
            "# Cerebras - Ultra-fast inference (30 requests/hour free)",
            "# Get key from: https://cloud.cerebras.ai/",
            '# export CEREBRAS_API_KEY="your-cerebras-key"',
            "",
            "# SambaNova - Enterprise AI (1,000 requests/day free)",
            "# Get key from: https://cloud.sambanova.ai/",
            '# export SAMBANOVA_API_KEY="your-sambanova-key"',
            "",
            "# AI21 Labs - Jurassic models (10,000 tokens/month free)",
            "# Get key from: https://studio.ai21.com/",
            '# export AI21_API_KEY="your-ai21-key"',
            "",
            "# Cohere - Enterprise AI (100 requests/month free)",
            "# Get key from: https://dashboard.cohere.ai/",
            '# export COHERE_API_KEY="your-cohere-key"',
            "",
            "# Perplexity - Search-enhanced AI (5 requests/day free)",
            "# Get key from: https://www.perplexity.ai/settings/api",
            '# export PERPLEXITY_API_KEY="your-perplexity-key"',
            "",
            "# HuggingChat - Completely free (requires account)",
            "# Create account at: https://huggingface.co/chat/",
            '# export HUGGINGFACE_EMAIL="your-email@example.com"',
            '# export HUGGINGFACE_PASSWORD="your-password"',
            "",
            "# Ollama - Local models (completely free, no API key needed)",
            "# Install from: https://ollama.ai/",
            "# Run: ollama pull llama3",
            "",
            "# ====================================",
            "# 💰 LOW-COST PROVIDERS (Very Cheap)",
            "# ====================================",
            "",
            "# Together AI - Open source models ($0.0008/1K tokens)",
            "# Get key from: https://api.together.xyz/",
            '# export TOGETHER_API_KEY="your-together-key"',
            '# export TOGETHER_API_KEY_1="your-backup-key"',
            "",
            "# DeepSeek - Very affordable ($0.0014/1K tokens)",
            "# Get key from: https://platform.deepseek.com/",
            '# export DEEPSEEK_API_KEY="your-deepseek-key"',
            "",
            "# Fireworks AI - Fast inference ($0.0009/1K tokens)",
            "# Get key from: https://fireworks.ai/",
            '# export FIREWORKS_API_KEY="your-fireworks-key"',
            "",
            "# Hyperbolic - Fast inference ($0.0015/1K tokens)",
            "# Get key from: https://app.hyperbolic.xyz/",
            '# export HYPERBOLIC_API_KEY="your-hyperbolic-key"',
            "",
            "# ====================================",
            "# 💎 PREMIUM PROVIDERS (High Quality)",
            "# ====================================",
            "",
            "# Google Gemini - Competitive pricing",
            "# Get key from: https://makersuite.google.com/app/apikey",
            '# export GEMINI_API_KEY="your-gemini-key"',
            "",
            "# Mistral AI - European AI leader",
            "# Get key from: https://console.mistral.ai/",
            '# export MISTRAL_API_KEY="your-mistral-key"',
            '# export MISTRAL_API_KEY_BACKUP="your-backup-key"',
            "",
            "# OpenRouter - Access to multiple models",
            "# Get key from: https://openrouter.ai/keys",
            '# export OPENROUTER_API_KEY="your-openrouter-key"',
            "",
            "# Anthropic Claude - Excellent for analysis",
            "# Get key from: https://console.anthropic.com/",
            '# export ANTHROPIC_API_KEY="your-anthropic-key"',
            "",
            "# OpenAI - Industry standard (most expensive)",
            "# Get key from: https://platform.openai.com/api-keys",
            '# export OPENAI_API_KEY="your-openai-key"',
            "",
            "# ====================================",
            "# 🚀 ACTIVATION",
            "# ====================================",
            "",
            'echo "AI Orchestra Provider Setup Complete!"',
            'echo "Restart your terminal or run: source ~/.bashrc"',
            'echo "Test with: python orchestra_cli.py status"',
        ]

        return "\n".join(script_lines)

    def create_setup_script(self):
        """Create a setup script file."""
        script_content = self.generate_setup_script()
        script_path = self.config_dir / "setup_providers.sh"

        with open(script_path, "w") as f:
            f.write(script_content)

        os.chmod(script_path, 0o755)  # Make executable

        console.print(f"✅ Setup script created: {script_path}")
        console.print(f"Run: bash {script_path}")

    def validate_configurations(self) -> dict[str, Any]:
        """Validate all provider configurations and return status."""
        validation_results = {
            "valid_providers": [],
            "invalid_providers": [],
            "missing_keys": [],
            "recommendations": [],
        }

        for name, config in self.providers.items():
            if not config.enabled:
                continue

            # Check if provider has necessary credentials
            has_credentials = False

            if name == "ollama":
                # Check if Ollama is running locally
                try:
                    import requests

                    response = requests.get(
                        "http://localhost:11434/api/tags", timeout=2
                    )
                    has_credentials = response.status_code == 200
                except:
                    has_credentials = False
            elif name == "huggingchat":
                has_credentials = bool(
                    config.custom_settings.get("email")
                    and config.custom_settings.get("password")
                )
            elif name == "mock":
                has_credentials = True
            else:
                has_credentials = bool(config.primary_api_key)

            if has_credentials:
                validation_results["valid_providers"].append(name)
            else:
                validation_results["invalid_providers"].append(name)
                validation_results["missing_keys"].append(name)

        # Generate recommendations
        if not validation_results["valid_providers"]:
            validation_results["recommendations"].append(
                "No valid providers configured. Start with free providers like Groq or Ollama."
            )

        if len(validation_results["valid_providers"]) < 3:
            validation_results["recommendations"].append(
                "Consider adding more providers for better redundancy and rate limit avoidance."
            )

        return validation_results

    def display_validation_report(self):
        """Display a comprehensive validation report."""
        results = self.validate_configurations()

        console.print(
            Panel.fit("🔍 Configuration Validation Report", style="bold cyan")
        )

        # Valid providers
        if results["valid_providers"]:
            console.print(
                f"\n✅ **{len(results['valid_providers'])} Valid Providers:**"
            )
            for provider in results["valid_providers"]:
                self.providers[provider]
                key_count = len(self.get_api_keys_for_provider(provider))
                if provider == "ollama":
                    console.print(f"  • {provider} (local)")
                elif provider == "mock":
                    console.print(f"  • {provider} (testing)")
                else:
                    console.print(f"  • {provider} ({key_count} keys)")

        # Invalid providers
        if results["invalid_providers"]:
            console.print(
                f"\n❌ **{len(results['invalid_providers'])} Invalid Providers:**"
            )
            for provider in results["invalid_providers"]:
                console.print(f"  • {provider} (missing credentials)")

        # Recommendations
        if results["recommendations"]:
            console.print("\n💡 **Recommendations:**")
            for rec in results["recommendations"]:
                console.print(f"  • {rec}")

        # Quick start suggestion
        if not results["valid_providers"] or len(results["valid_providers"]) < 2:
            console.print(
                Panel(
                    """
🚀 **Quick Start - Get Free AI Access:**

1. **Groq (Fastest, Free)**: https://console.groq.com/
2. **Ollama (Local, Free)**: https://ollama.ai/
3. **Cerebras (Fast, Free)**: https://cloud.cerebras.ai/
4. **SambaNova (Free)**: https://cloud.sambanova.ai/

Run the setup script to get started:
```bash
python provider_config_manager.py setup
```
""",
                    style="green",
                )
            )

    def auto_configure_defaults(self):
        """Auto-configure default settings for all known providers."""
        default_configs = {
            "groq": ProviderConfig(
                name="groq",
                enabled=False,
                default_model="llama-3.1-8b-instant",
                max_tokens=4096,
                temperature=0.7,
                priority=110,
                cost_tier="free",
            ),
            "cerebras": ProviderConfig(
                name="cerebras",
                enabled=False,
                default_model="llama3.1-8b",
                max_tokens=8192,
                temperature=0.7,
                priority=108,
                cost_tier="free",
            ),
            "sambanova": ProviderConfig(
                name="sambanova",
                enabled=False,
                default_model="Meta-Llama-3.1-8B-Instruct",
                max_tokens=16384,
                temperature=0.7,
                priority=105,
                cost_tier="free",
            ),
            "ollama": ProviderConfig(
                name="ollama",
                enabled=True,
                default_model="llama3",
                max_tokens=8192,
                temperature=0.7,
                priority=100,
                cost_tier="free",
            ),
            "fireworks": ProviderConfig(
                name="fireworks",
                enabled=False,
                default_model="accounts/fireworks/models/llama-v3p1-70b-instruct",
                max_tokens=16384,
                temperature=0.7,
                priority=95,
                cost_tier="low",
            ),
            "ai21": ProviderConfig(
                name="ai21",
                enabled=False,
                default_model="j2-mid",
                max_tokens=8192,
                temperature=0.7,
                priority=75,
                cost_tier="free",
            ),
            "mock": ProviderConfig(
                name="mock",
                enabled=True,
                default_model="mock-model",
                max_tokens=2000,
                temperature=0.7,
                priority=10,
                cost_tier="free",
            ),
        }

        for name, default_config in default_configs.items():
            if name not in self.providers:
                self.providers[name] = default_config
            else:
                # Update only missing fields
                existing = self.providers[name]
                for field, value in asdict(default_config).items():
                    if not getattr(existing, field, None):
                        setattr(existing, field, value)

        self.save_configurations()
        console.print("✅ Default configurations applied")


def create_config_manager() -> ProviderConfigManager:
    """Factory function to create the configuration manager."""
    return ProviderConfigManager()


if __name__ == "__main__":
    import sys

    manager = create_config_manager()

    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        # Setup mode
        console.print("🔧 Setting up AI Orchestra Provider Configuration...")
        manager.auto_configure_defaults()
        manager.create_setup_script()
        manager.display_validation_report()
    else:
        # Status mode
        manager.display_configuration_status()
        manager.display_validation_report()
