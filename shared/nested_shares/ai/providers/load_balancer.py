#!/usr/bin/env python3
"""
⚖️ AI Orchestra - Advanced Load Balancer
========================================

Sophisticated load balancing and failover system with:
- Weighted routing based on performance metrics
- Circuit breaker patterns for failed providers
- Intelligent failover with exponential backoff
- Real-time metrics and analytics
"""

import random
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table

    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


@dataclass
class LoadBalancerMetrics:
    """Enhanced metrics for load balancing decisions."""

    provider_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    consecutive_failures: int = 0
    is_blacklisted: bool = False
    blacklist_until: float = 0.0
    rate_limited_until: float = 0.0
    circuit_state: str = "closed"  # closed, open, half-open
    circuit_failure_count: int = 0
    circuit_failure_threshold: int = 5
    circuit_open_timestamp: float = 0.0
    last_success_time: float = 0.0

    def record_success(self, response_time: float):
        """Record a successful request."""
        self.total_requests += 1
        self.successful_requests += 1
        self.consecutive_failures = 0
        self.last_success_time = time.time()

        # Update average response time
        if self.total_requests == 1:
            self.avg_response_time = response_time
        else:
            self.avg_response_time = (self.avg_response_time * 0.9) + (
                response_time * 0.1
            )

        # Circuit breaker recovery
        if self.circuit_state == "half-open":
            self.circuit_state = "closed"
            self.circuit_failure_count = 0

    def record_failure(self):
        """Record a failed request."""
        self.total_requests += 1
        self.failed_requests += 1
        self.consecutive_failures += 1

        # Circuit breaker logic
        if self.circuit_state == "half-open":
            self.circuit_state = "open"
            self.circuit_open_timestamp = time.time()
        else:
            self.circuit_failure_count += 1
            if self.circuit_failure_count >= self.circuit_failure_threshold:
                self.circuit_state = "open"
                self.circuit_open_timestamp = time.time()

        # Blacklist after too many consecutive failures
        if self.consecutive_failures >= 10:
            self.blacklist_provider(300)  # 5 minutes

    def blacklist_provider(self, duration: int = 300):
        """Temporarily blacklist a provider."""
        self.is_blacklisted = True
        self.blacklist_until = time.time() + duration

    def is_available(self) -> bool:
        """Check if provider is available."""
        current_time = time.time()

        # Check blacklist
        if self.is_blacklisted and current_time < self.blacklist_until:
            return False
        elif self.is_blacklisted and current_time >= self.blacklist_until:
            self.is_blacklisted = False
            self.consecutive_failures = 0

        # Check rate limiting
        if current_time < self.rate_limited_until:
            return False

        # Check circuit breaker
        if self.circuit_state == "open":
            if (
                time.time() - getattr(self, "circuit_open_timestamp", 0) > 10
            ):  # 10 seconds delay
                self.circuit_state = "half-open"
                self.circuit_failure_count = 0
                return True
            return False
        elif self.circuit_state == "half-open":
            return True

        return True

    def get_success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_requests == 0:
            return 100.0
        return (self.successful_requests / self.total_requests) * 100

    def calculate_health_score(self) -> float:
        """Calculate health score (0-100)."""
        if self.total_requests == 0:
            return 100.0

        success_rate = self.get_success_rate()
        health_score = success_rate

        # Penalty for slow responses
        if self.avg_response_time > 5.0:
            health_score -= min(20, (self.avg_response_time - 5.0) * 4)

        # Penalty for circuit breaker state
        if self.circuit_state == "open":
            health_score -= 30
        elif self.circuit_state == "half-open":
            health_score -= 15

        return max(0.0, min(100.0, health_score))


class AdvancedLoadBalancer:
    """Advanced load balancer with intelligent routing."""

    def __init__(self):
        self.metrics: dict[str, LoadBalancerMetrics] = {}
        self.providers: dict = {}
        self.total_requests: int = 0

    def register_provider(self, name: str, provider: Any):
        """Register a provider."""
        self.providers[name] = provider
        if name not in self.metrics:
            # Initialize avg_response_time with provider's expected average time if available
            initial_avg_time = getattr(provider, "avg_time", 0.0)
            self.metrics[name] = LoadBalancerMetrics(
                provider_name=name,
                avg_response_time=(
                    float(initial_avg_time)
                    if hasattr(initial_avg_time, "__float__") and initial_avg_time > 0
                    else 0.0
                ),
            )

    def calculate_provider_weight(self, provider_name: str) -> float:
        """Calculate weight for a provider."""
        metrics = self.metrics.get(provider_name)
        if not metrics or not metrics.is_available():
            return 0.0

        health_score = metrics.calculate_health_score()
        if health_score < 50.0:
            return 0.1  # A very small weight

        # Response time factor (faster = higher weight)
        time_factor = 100.0
        if metrics.avg_response_time > 0:
            time_factor = max(10.0, 100.0 - (metrics.avg_response_time * 10))

        return health_score * 0.7 + time_factor * 0.3

    def select_provider_weighted(self, available_providers: list[str]) -> str | None:
        """Select provider using weighted selection."""
        if not available_providers:
            return None

        weights = []
        provider_names = []

        for provider_name in available_providers:
            weight = self.calculate_provider_weight(provider_name)
            if weight > 0:
                weights.append(weight)
                provider_names.append(provider_name)

        if not weights:
            if provider_names:
                return random.choice(provider_names)
            return None

        # Weighted random selection
        total_weight = sum(weights)
        if total_weight == 0:
            return random.choice(provider_names)

        rand = random.uniform(0, total_weight)
        cumulative = 0.0

        for i, weight in enumerate(weights):
            cumulative += weight
            if rand <= cumulative:
                return provider_names[i]

        return provider_names[-1]

    def execute_with_failover(
        self, prompt: str, strategy: str = "balanced", max_attempts: int = 3
    ) -> tuple[str, dict[str, Any]]:
        """Execute request with failover."""
        self.total_requests += 1

        # Get available providers
        available_providers = [
            name for name in self.providers if self.metrics[name].is_available()
        ]

        if not available_providers:
            return "❌ No available providers", {"attempts": 0}

        execution_log = {"attempts": 0, "details": [], "final_provider": None}

        for attempt in range(max_attempts):
            # Select provider for this attempt
            if attempt == 0:
                provider_name = self.select_provider_weighted(available_providers)
            else:
                # For retry attempts, try other providers
                tried_providers = [
                    detail["provider"] for detail in execution_log["details"]
                ]
                remaining = [p for p in available_providers if p not in tried_providers]
                if not remaining and tried_providers:
                    remaining = [tried_providers[-1]]

                if not remaining:
                    break
                provider_name = self.select_provider_weighted(remaining)

            if not provider_name:
                break

            execution_log["attempts"] = attempt + 1
            execution_log["final_provider"] = provider_name

            # Try the provider
            metrics = self.metrics.get(
                provider_name, LoadBalancerMetrics(provider_name)
            )

            try:
                start_time = time.time()
                provider = self.providers[provider_name]
                response = provider.generate(prompt)
                response_time = time.time() - start_time

                execution_log["details"].append(
                    {
                        "attempt": attempt + 1,
                        "provider": provider_name,
                        "response_time": response_time,
                        "status": (
                            "success" if not response.startswith("❌") else "failed"
                        ),
                    }
                )

                if not response.startswith("❌"):
                    metrics.record_success(response_time)
                    return response, execution_log
                else:
                    metrics.record_failure()

            except Exception as e:
                metrics.record_failure()
                execution_log["details"].append(
                    {
                        "attempt": attempt + 1,
                        "provider": provider_name,
                        "status": "error",
                        "error": str(e)[:100],
                    }
                )

            # Wait before retry
            if attempt < max_attempts - 1:
                time.sleep(2**attempt)  # Exponential backoff

        return (
            f"❌ All providers failed after {execution_log['attempts']} attempts",
            execution_log,
        )

    def simulate_load_balancing(
        self, num_requests: int = 10, strategy: str = "balanced"
    ):
        """Simulate load balancing."""
        if RICH_AVAILABLE:
            console.print(
                Panel.fit(
                    f"🧪 Load Balancing Simulation ({num_requests} requests)",
                    style="bold yellow",
                )
            )
        else:
            print(f"🧪 Load Balancing Simulation ({num_requests} requests)")

        results = {
            "successful": 0,
            "failed": 0,
            "provider_usage": defaultdict(int),
            "failover_events": 0,
        }

        if RICH_AVAILABLE:
            with Progress(SpinnerColumn(), TextColumn("Simulating...")) as progress:
                task = progress.add_task("requests", total=num_requests)

                for i in range(num_requests):
                    prompt = f"Test request {i+1}"
                    response, log = self.execute_with_failover(prompt, strategy)

                    if not response.startswith("❌"):
                        results["successful"] += 1
                        if log["final_provider"]:
                            results["provider_usage"][log["final_provider"]] += 1
                    else:
                        results["failed"] += 1

                    if log["attempts"] > 1:
                        results["failover_events"] += 1

                    progress.advance(task)
                    time.sleep(0.1)
        else:
            for i in range(num_requests):
                prompt = f"Test request {i+1}"
                response, log = self.execute_with_failover(prompt, strategy)

                if not response.startswith("❌"):
                    results["successful"] += 1
                    if log["final_provider"]:
                        results["provider_usage"][log["final_provider"]] += 1
                else:
                    results["failed"] += 1

                if log["attempts"] > 1:
                    results["failover_events"] += 1

                print(
                    f"  Request {i+1}: {'✅' if not response.startswith('❌') else '❌'}"
                )

        # Display results
        success_rate = (results["successful"] / num_requests) * 100

        if RICH_AVAILABLE:
            results_table = Table(show_header=True, header_style="bold green")
            results_table.add_column("Metric", style="cyan")
            results_table.add_column("Value", style="green")

            results_table.add_row("Total Requests", str(num_requests))
            results_table.add_row(
                "Successful", f"{results['successful']} ({success_rate:.1f}%)"
            )
            results_table.add_row("Failed", str(results["failed"]))
            results_table.add_row("Failover Events", str(results["failover_events"]))

            console.print(results_table)

            # Provider usage
            if results["provider_usage"]:
                usage_table = Table(show_header=True, header_style="bold blue")
                usage_table.add_column("Provider", style="cyan")
                usage_table.add_column("Requests", style="green")
                usage_table.add_column("Load %", style="yellow")

                for provider, count in results["provider_usage"].items():
                    load_pct = (
                        (count / results["successful"]) * 100
                        if results["successful"] > 0
                        else 0
                    )
                    usage_table.add_row(
                        provider.title(), str(count), f"{load_pct:.1f}%"
                    )

                console.print(Panel(usage_table, title="📊 Load Distribution"))
        else:
            print("\nResults:")
            print(f"  Success Rate: {success_rate:.1f}%")
            print(f"  Failover Events: {results['failover_events']}")

            if results["provider_usage"]:
                print("\nLoad Distribution:")
                for provider, count in results["provider_usage"].items():
                    load_pct = (
                        (count / results["successful"]) * 100
                        if results["successful"] > 0
                        else 0
                    )
                    print(f"  {provider.title()}: {count} requests ({load_pct:.1f}%)")

    def print_status(self):
        """Print load balancer status."""
        if RICH_AVAILABLE:
            console.print(Panel.fit("⚖️ Load Balancer Status", style="bold cyan"))

            table = Table(show_header=True, header_style="bold blue")
            table.add_column("Provider", style="cyan")
            table.add_column("Health", style="green")
            table.add_column("Weight", style="yellow")
            table.add_column("Requests", style="white")
            table.add_column("Success Rate", style="magenta")
            table.add_column("Status", style="white")

            for name, metrics in self.metrics.items():
                health_score = metrics.calculate_health_score()
                weight = self.calculate_provider_weight(name)

                status_parts = []
                if metrics.is_blacklisted:
                    status_parts.append("Blacklisted")
                if metrics.circuit_state != "closed":
                    status_parts.append(f"Circuit {metrics.circuit_state}")

                status = ", ".join(status_parts) if status_parts else "Available"

                table.add_row(
                    name.title(),
                    f"{health_score:.1f}%",
                    f"{weight:.1f}",
                    str(metrics.total_requests),
                    f"{metrics.get_success_rate():.1f}%",
                    status,
                )

            console.print(table)
        else:
            print("⚖️ Load Balancer Status")
            for name, metrics in self.metrics.items():
                print(
                    f"{name.title()}: {metrics.get_success_rate():.1f}% success, "
                    f"health: {metrics.calculate_health_score():.1f}"
                )


def demo_load_balancer():
    """Demo the load balancer with mock providers."""
    balancer = AdvancedLoadBalancer()

    # Mock providers for demo
    class MockProvider:
        def __init__(self, name: str, success_rate: float = 0.9, avg_time: float = 2.0):
            self.name = name
            self.success_rate = success_rate
            self.avg_time = avg_time

        def generate(self, prompt: str) -> str:
            # Simulate response time
            time.sleep(random.uniform(self.avg_time * 0.5, self.avg_time * 1.5))

            # Simulate success/failure
            if random.random() < self.success_rate:
                return f"Response from {self.name}: {prompt[:30]}..."
            else:
                return "❌ Provider temporarily unavailable"

    # Register providers with different characteristics
    providers = {
        "groq": MockProvider("Groq", 0.95, 1.0),  # Fast, reliable
        "cerebras": MockProvider("Cerebras", 0.90, 1.5),  # Fast, good
        "ai21": MockProvider("AI21", 0.85, 3.0),  # Slower, less reliable
        "openai": MockProvider("OpenAI", 0.98, 4.0),  # Slow but very reliable
    }

    for name, provider in providers.items():
        balancer.register_provider(name, provider)

    if RICH_AVAILABLE:
        console.print(Panel.fit("🎭 Advanced Load Balancer Demo", style="bold magenta"))
    else:
        print("🎭 Advanced Load Balancer Demo")

    # Run simulation
    balancer.simulate_load_balancing(15, "balanced")

    # Show status
    balancer.print_status()


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="⚖️ AI Orchestra Load Balancer")
    parser.add_argument(
        "action",
        nargs="?",
        default="demo",
        choices=["demo", "status", "simulate"],
        help="Action to perform",
    )
    parser.add_argument(
        "--requests", type=int, default=10, help="Number of requests for simulation"
    )
    parser.add_argument(
        "--strategy",
        choices=["balanced", "cost_optimized", "speed_first"],
        default="balanced",
        help="Strategy to use",
    )

    args = parser.parse_args()

    if args.action == "demo":
        demo_load_balancer()
    elif args.action == "simulate":
        balancer = AdvancedLoadBalancer()
        balancer.simulate_load_balancing(args.requests, args.strategy)
    elif args.action == "status":
        balancer = AdvancedLoadBalancer()
        balancer.print_status()


if __name__ == "__main__":
    main()
