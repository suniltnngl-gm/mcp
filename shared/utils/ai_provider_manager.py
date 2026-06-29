import json

#!/usr/bin/env python3
"""
🎭 AI Orchestra - Enhanced Provider Manager
==========================================

Advanced multi-provider AI system with load balancing, failover, and cost optimization.
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Import moved to avoid circular dependency - will import when needed

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Import base classes
from expanded_providers import (
    AI21Provider,
    CerebrasProvider,
    CohereProvider,
    DeepSeekProvider,
    EnhancedMistralProvider,
    FireworksProvider,
    GroqProvider,
    HyperbolicProvider,
    OpenRouterProvider,
    PerplexityProvider,
    TogetherProvider,
)
from ai_orchestra.llm_providers import BaseLLMProvider, LLMConfig

console = Console()
logger = logging.getLogger(__name__)


class ProviderTier(Enum):
    """Provider cost tiers for smart routing."""

    FREE = "free"
    LOW_COST = "low"
    PREMIUM = "premium"


class ProviderSpeed(Enum):
    """Provider speed categories."""

    ULTRA_FAST = "ultra_fast"
    VERY_FAST = "very_fast"
    FAST = "fast"
    MEDIUM = "medium"
    SLOW = "slow"


@dataclass
class ProviderMetrics:
    """Metrics for provider performance tracking."""

    name: str
    tier: ProviderTier
    speed: ProviderSpeed
    success_rate: float = 100.0
    avg_response_time: float = 0.0
    requests_today: int = 0
    rate_limited_until: float = 0.0
    last_used: float = 0.0
    total_requests: int = 0
    total_failures: int = 0
    historical_response_times: list[float] = field(default_factory=list)
    historical_error_counts: list[int] = field(default_factory=list)

    def to_dict(self):
        return {
            "name": self.name,
            "tier": self.tier.value,
            "speed": self.speed.value,
            "success_rate": self.success_rate,
            "avg_response_time": self.avg_response_time,
            "requests_today": self.requests_today,
            "rate_limited_until": self.rate_limited_until,
            "last_used": self.last_used,
            "total_requests": self.total_requests,
            "total_failures": self.total_failures,
            "historical_response_times": self.historical_response_times,
            "historical_error_counts": self.historical_error_counts,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data["name"],
            tier=ProviderTier(data["tier"]),
            speed=ProviderSpeed(data["speed"]),
            success_rate=data.get("success_rate", 100.0),
            avg_response_time=data.get("avg_response_time", 0.0),
            requests_today=data.get("requests_today", 0),
            rate_limited_until=data.get("rate_limited_until", 0.0),
            last_used=data.get("last_used", 0.0),
            total_requests=data.get("total_requests", 0),
            total_failures=data.get("total_failures", 0),
            historical_response_times=data.get("historical_response_times", []),
            historical_error_counts=data.get("historical_error_counts", []),
        )


class SmartProviderRouter:
    """Intelligent routing between AI providers with load balancing and cost optimization."""

    METRICS_FILE = Path("provider_metrics.json")

    def __init__(self, health_monitor=None):
        self.providers: dict[str, BaseLLMProvider] = {}
        self.metrics: dict[str, ProviderMetrics] = {}
        self.routing_strategy = (
            "cost_optimized"  # Options: cost_optimized, speed_first, balanced
        )
        # Health monitor is optional - can be set later to avoid circular imports
        self.health_monitor = health_monitor
        self._load_metrics()
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize all available AI providers."""
        provider_configs = [
            # Free/Ultra-Fast Providers
            (
                "groq",
                GroqProvider,
                ProviderTier.FREE,
                ProviderSpeed.ULTRA_FAST,
                "llama-3.1-8b-instant",
            ),
            (
                "cerebras",
                CerebrasProvider,
                ProviderTier.FREE,
                ProviderSpeed.ULTRA_FAST,
                "llama3.1-8b",
            ),
            # Free Providers
            ("ai21", AI21Provider, ProviderTier.FREE, ProviderSpeed.MEDIUM, "j2-ultra"),
            (
                "cohere",
                CohereProvider,
                ProviderTier.FREE,
                ProviderSpeed.MEDIUM,
                "command",
            ),
            (
                "perplexity",
                PerplexityProvider,
                ProviderTier.FREE,
                ProviderSpeed.MEDIUM,
                "llama-3.1-sonar-small-128k-online",
            ),
            # Low-Cost High-Speed Providers
            (
                "fireworks",
                FireworksProvider,
                ProviderTier.LOW_COST,
                ProviderSpeed.VERY_FAST,
                "accounts/fireworks/models/llama-v3p1-70b-instruct",
            ),
            (
                "together",
                TogetherProvider,
                ProviderTier.LOW_COST,
                ProviderSpeed.FAST,
                "togethercomputer/llama-2-70b-chat",
            ),
            (
                "deepseek",
                DeepSeekProvider,
                ProviderTier.LOW_COST,
                ProviderSpeed.FAST,
                "deepseek-chat",
            ),
            (
                "hyperbolic",
                HyperbolicProvider,
                ProviderTier.LOW_COST,
                ProviderSpeed.VERY_FAST,
                "meta-llama/Llama-3.1-70B-Instruct",
            ),
            (
                "openrouter",
                OpenRouterProvider,
                ProviderTier.LOW_COST,
                ProviderSpeed.FAST,
                "meta-llama/llama-3.1-8b-instruct:free",
            ),
            # Enhanced existing providers
            (
                "mistral",
                EnhancedMistralProvider,
                ProviderTier.LOW_COST,
                ProviderSpeed.FAST,
                "mistral-small-latest",
            ),
        ]

        for name, provider_class, tier, speed, default_model in provider_configs:
            try:
                config = LLMConfig(
                    model_name=default_model, max_tokens=500, temperature=0.7
                )

                provider = provider_class(config)

                if provider.is_available():
                    self.providers[name] = provider
                    self.metrics[name] = ProviderMetrics(name, tier, speed)
                    logger.info(f"✅ {name.title()} provider initialized")
                else:
                    logger.info(
                        f"⚠️ {name.title()} provider not configured (missing API key)"
                    )

            except Exception as e:
                logger.warning(f"❌ Failed to initialize {name}: {e}")

        console.print(f"🤖 Initialized {len(self.providers)} AI providers")

    def _load_metrics(self):
        """Load provider metrics from file."""
        if self.METRICS_FILE.exists():
            try:
                with open(self.METRICS_FILE) as f:
                    data = json.load(f)
                    for name, metrics_data in data.items():
                        self.metrics[name] = ProviderMetrics.from_dict(metrics_data)
            except Exception as e:
                logger.warning(f"Could not load metrics: {e}")

    def _save_metrics(self):
        """Save provider metrics to file."""
        try:
            serializable_metrics = {
                name: metrics.to_dict() for name, metrics in self.metrics.items()
            }
            with open(self.METRICS_FILE, "w") as f:
                json.dump(serializable_metrics, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save metrics: {e}")

    def get_available_providers(
        self, tier_preference: ProviderTier | None = None
    ) -> list[str]:
        """Get list of available providers, optionally filtered by tier."""
        if tier_preference:
            return [
                name
                for name, metrics in self.metrics.items()
                if name in self.providers and metrics.tier == tier_preference
            ]
        return list(self.providers.keys())

    def select_best_provider(self, prompt: str, preference: str = "auto") -> str | None:
        """Select the best provider based on current metrics and strategy."""
        available = []
        current_time = time.time()

        # Filter out rate-limited and unhealthy providers
        for name, _provider in self.providers.items():
            metrics = self.metrics[name]
            provider_health = self.health_monitor.get_provider_status(name)

            if (
                current_time > metrics.rate_limited_until
                and provider_health.get("status") == "healthy"
            ):
                available.append((name, metrics))
            elif provider_health.get("status") == "unhealthy":
                logger.warning(f"Provider {name} is unhealthy, skipping selection.")

        if not available:
            return None

        # Apply selection strategy
        if preference == "free" or self.routing_strategy == "cost_optimized":
            # Prefer free providers first, then lowest cost based on historical data
            free_providers = [
                (n, m) for n, m in available if m.tier == ProviderTier.FREE
            ]
            if free_providers:
                available = free_providers

            # Sort by estimated cost (lower is better)
            available.sort(
                key=lambda x: self.get_cost_estimate(100, x[0]).get(x[0], 0.0)
            )

        elif preference == "speed" or self.routing_strategy == "speed_first":
            # Sort by speed priority
            speed_priority = {
                ProviderSpeed.ULTRA_FAST: 0,
                ProviderSpeed.VERY_FAST: 1,
                ProviderSpeed.FAST: 2,
                ProviderSpeed.MEDIUM: 3,
                ProviderSpeed.SLOW: 4,
            }
            available.sort(
                key=lambda x: (speed_priority[x[1].speed], -x[1].success_rate)
            )

        elif preference == "reliable":
            # Sort by success rate and low recent usage
            available.sort(key=lambda x: (-x[1].success_rate, x[1].requests_today))

        # Default: balanced approach (considers cost, speed, and reliability)
        if len(available) > 1 and preference == "auto":
            # Score each provider
            scored = []
            for name, metrics in available:
                score = 0

                # Cost bonus (free = +30, low = +15, premium = 0)
                # Incorporate estimated cost: lower cost = higher score
                estimated_cost = self.get_cost_estimate(100, name).get(
                    name, 0.002
                )  # Estimate for 100 tokens
                score += max(
                    0, (0.003 - estimated_cost) * 10000
                )  # Max 30 points for very low cost

                # Speed bonus (ultra_fast = +20, very_fast = +15, fast = +10, medium = +5)
                speed_bonus = {
                    ProviderSpeed.ULTRA_FAST: 20,
                    ProviderSpeed.VERY_FAST: 15,
                    ProviderSpeed.FAST: 10,
                    ProviderSpeed.MEDIUM: 5,
                    ProviderSpeed.SLOW: 0,
                }
                score += speed_bonus.get(metrics.speed, 0)

                # Reliability bonus
                score += metrics.success_rate / 5  # Max +20 for 100% success

                # Load balancing (penalize recently used providers)
                hours_since_last_use = (current_time - metrics.last_used) / 3600
                if hours_since_last_use < 1:
                    score -= 10

                # Avoid heavily used providers today
                if metrics.requests_today > 50:
                    score -= 10

                scored.append((name, score, metrics))

            # Select highest scoring provider
            scored.sort(key=lambda x: x[1], reverse=True)
            return scored[0][0]

        # Return first available provider
        return available[0][0]

    def generate_with_fallback(
        self, prompt: str, preference: str = "auto", max_attempts: int = 3
    ) -> tuple[str, str]:
        """Generate response with automatic provider fallback."""
        attempts = 0
        last_error = "No providers available"

        while attempts < max_attempts:
            attempts += 1

            # Select best available provider
            provider_name = self.select_best_provider(prompt, preference)

            if not provider_name:
                break

            provider = self.providers[provider_name]
            metrics = self.metrics[provider_name]

            # Record attempt
            start_time = time.time()
            metrics.last_used = start_time
            metrics.requests_today += 1
            metrics.total_requests += 1

            try:
                console.print(f"🤖 Using {provider_name.title()} (attempt {attempts})")

                response = provider.generate(prompt)

                # Record success
                response_time = time.time() - start_time
                metrics.avg_response_time = (
                    metrics.avg_response_time + response_time
                ) / 2

                # Update success rate
                total_attempts = metrics.total_requests
                success_attempts = total_attempts - metrics.total_failures
                metrics.success_rate = (success_attempts / total_attempts) * 100

                # Return successful response
                if not response.startswith("❌"):
                    return response, provider_name
                else:
                    raise Exception(response)

            except Exception as e:
                error_msg = str(e)
                last_error = f"{provider_name}: {error_msg}"

                # Record failure
                metrics.total_failures += 1

                # Check for rate limiting
                if "429" in error_msg or "rate limit" in error_msg.lower():
                    metrics.rate_limited_until = time.time() + (10 * 60)  # 10 minutes
                    console.print(
                        f"⏳ {provider_name.title()} rate limited, trying next provider..."
                    )
                    continue

                # Check for quota exceeded
                if "quota" in error_msg.lower() or "exceeded" in error_msg.lower():
                    metrics.rate_limited_until = time.time() + (60 * 60)  # 1 hour
                    console.print(
                        f"🚫 {provider_name.title()} quota exceeded, trying next provider..."
                    )
                    continue

                # Other errors - try different provider
                console.print(f"❌ {provider_name.title()} failed: {error_msg}")

                # Save metrics after each attempt
                self._save_metrics()

                # Remove failed provider from current session
                if attempts < max_attempts:
                    continue

        return f"❌ All providers failed. Last error: {last_error}", "none"

    def get_provider_status(self) -> Table:
        """Generate a status table for all providers."""
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Provider", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Tier", style="green")
        table.add_column("Speed", style="yellow")
        table.add_column("Success Rate", style="magenta")
        table.add_column("Requests Today", style="blue")
        table.add_column("Avg Response", style="white")

        current_time = time.time()

        for name, metrics in self.metrics.items():
            # Determine status
            if name not in self.providers:
                status = "❌ Not Available"
                status_style = "red"
            elif current_time < metrics.rate_limited_until:
                status = "⏳ Rate Limited"
                status_style = "yellow"
            else:
                status = "✅ Available"
                status_style = "green"

            table.add_row(
                name.title(),
                f"[{status_style}]{status}[/{status_style}]",
                metrics.tier.value.title(),
                metrics.speed.value.replace("_", "-").title(),
                f"{metrics.success_rate:.1f}%",
                str(metrics.requests_today),
                f"{metrics.avg_response_time:.1f}s",
            )

        return table

    def reset_daily_limits(self):
        """Reset daily request counters."""
        for metrics in self.metrics.values():
            metrics.requests_today = 0
        console.print("🔄 Daily limits reset")

    def set_routing_strategy(self, strategy: str):
        """Set the provider routing strategy."""
        valid_strategies = ["cost_optimized", "speed_first", "balanced"]
        if strategy in valid_strategies:
            self.routing_strategy = strategy
            console.print(f"🎯 Routing strategy set to: {strategy}")
        else:
            console.print(f"❌ Invalid strategy. Choose from: {valid_strategies}")

    def get_cost_estimate(
        self, tokens: int, provider_name: str = None
    ) -> dict[str, float]:
        """Estimate cost for each provider (in USD), optionally for a specific provider."""
        # Rough cost estimates per 1K tokens (as of 2024)
        cost_per_1k = {
            "groq": 0.0,  # Free tier
            "cerebras": 0.0,  # Free tier
            "ai21": 0.0,  # Free tier
            "cohere": 0.0,  # Free tier
            "perplexity": 0.0,  # Free tier
            "fireworks": 0.0009,
            "together": 0.0008,
            "deepseek": 0.0014,
            "hyperbolic": 0.0015,
            "openrouter": 0.0,  # Using free models
            "mistral": 0.0025,
        }

        estimates = {}
        providers_to_estimate = (
            [provider_name] if provider_name else self.providers.keys()
        )

        for name in providers_to_estimate:
            rate = cost_per_1k.get(name, 0.002)  # Default rate
            estimated_cost = (tokens / 1000) * rate

            # Factor in historical average response time (penalize slower providers)
            metrics = self.metrics.get(name)
            if metrics and metrics.avg_response_time > 0:
                # Simple penalty: 10% cost increase for every 500ms above 1s avg response time
                penalty_factor = max(0, (metrics.avg_response_time - 1.0) / 0.5) * 0.1
                estimated_cost *= 1 + penalty_factor

            estimates[name] = estimated_cost

        return estimates

    def interactive_provider_selection(self) -> str | None:
        """Interactive provider selection menu."""
        available = self.get_available_providers()

        if not available:
            console.print("❌ No providers available")
            return None

        console.print("\n🤖 Available AI Providers:")

        table = Table(show_header=True, header_style="bold blue")
        table.add_column("#", style="cyan")
        table.add_column("Provider", style="green")
        table.add_column("Tier", style="yellow")
        table.add_column("Speed", style="magenta")
        table.add_column("Status", style="white")

        current_time = time.time()

        for i, name in enumerate(available, 1):
            metrics = self.metrics[name]

            status = "Available"
            if current_time < metrics.rate_limited_until:
                status = "Rate Limited"

            table.add_row(
                str(i),
                name.title(),
                metrics.tier.value.title(),
                metrics.speed.value.replace("_", "-").title(),
                status,
            )

        console.print(table)

        while True:
            try:
                choice = console.input(
                    f"\nSelect provider (1-{len(available)}) or 'auto' for smart selection: "
                )

                if choice.lower() == "auto":
                    return "auto"

                index = int(choice) - 1
                if 0 <= index < len(available):
                    return available[index]
                else:
                    console.print("❌ Invalid selection")

            except (ValueError, KeyboardInterrupt):
                return None


def demo_multi_provider_system():
    """Demonstrate the multi-provider system."""
    console.print(
        Panel.fit("🎭 AI Orchestra - Multi-Provider Demo", style="bold magenta")
    )

    from ai_orchestra.health import AIHealthMonitor

    router = SmartProviderRouter()
    health_monitor = AIHealthMonitor(router)
    router.health_monitor = health_monitor

    if not router.providers:
        console.print("❌ No providers configured. Please set up API keys.")
        return

    # Show provider status
    console.print("\n📊 Provider Status:")
    status_table = router.get_provider_status()
    console.print(status_table)

    # Demo queries with different preferences
    test_queries = [
        ("Explain quantum computing in simple terms", "free"),
        ("Write a Python function to sort a list", "speed"),
        ("What are the benefits of renewable energy?", "reliable"),
        ("Create a haiku about artificial intelligence", "auto"),
    ]

    console.print(f"\n🧪 Testing with {len(test_queries)} sample queries...")

    for i, (query, preference) in enumerate(test_queries, 1):
        console.print(f"\n🎯 Query {i}: {query[:50]}...")
        console.print(f"Preference: {preference}")

        response, used_provider = router.generate_with_fallback(query, preference)

        if not response.startswith("❌"):
            console.print(
                f"✅ Response from {used_provider.title()}: {response[:100]}..."
            )
        else:
            console.print(f"❌ Failed: {response}")

        # Brief pause between requests
        time.sleep(1)

    # Final status
    console.print("\n📈 Final Provider Status:")
    final_status = router.get_provider_status()
    console.print(final_status)


def main():
    """Main function for testing."""
    try:
        demo_multi_provider_system()
    except KeyboardInterrupt:
        console.print("\n👋 Demo interrupted by user")
    except Exception as e:
        console.print(f"\n❌ Demo failed: {e}")


if __name__ == "__main__":
    main()
