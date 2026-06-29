"""
🩺 Provider Health Monitor and Failover System
=============================================

Comprehensive health monitoring, diagnostics, and automatic failover
for AI providers. Monitors API health, rate limits, response times,
and provides robust failover mechanisms.
"""

import asyncio
import json
import logging
import random
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table

try:
    from provider_config_manager import ProviderConfig, create_config_manager
except ImportError:
    # For standalone usage
    from typing import Any

    @dataclass
    class ProviderConfig:
        name: str
        enabled: bool = True

    def create_config_manager():
        return None


console = Console()
logger = logging.getLogger(__name__)


@dataclass
class HealthStatus:
    """Health status for a provider."""

    is_available: bool = True
    last_check_time: float = field(default_factory=time.time)
    response_time_ms: float | None = None
    error_message: str | None = None
    rate_limited: bool = False
    rate_limit_reset: float | None = None
    consecutive_failures: int = 0
    alert_level: str = "normal"  # normal, warning, critical
    quota_remaining: float | None = None
    quota_reset_time: float | None = None
    historical_response_times: list[float] = field(default_factory=list)


@dataclass
class ProviderHealthConfig:
    """Configuration for health monitoring."""

    check_interval_seconds: int = 300  # 5 minutes
    failure_threshold: int = 3  # Mark as unavailable after 3 consecutive failures
    rate_limit_backoff_seconds: int = 60  # Minimum backoff when rate limited
    response_time_warning_ms: int = 5000  # Slow response warning threshold
    response_time_critical_ms: int = 10000  # Very slow response critical threshold
    auto_failover: bool = True  # Automatically switch to fallback
    alert_on_failures: bool = True  # Trigger alerts on failures
    metrics_retention_days: int = 7  # How long to keep metrics
    parallel_health_checks: bool = True  # Run health checks in parallel


class ProviderHealthMonitor:
    """Monitors health of AI providers and manages failover."""

    def __init__(self, config: ProviderHealthConfig | None = None):
        self.config = config or ProviderHealthConfig()
        self.provider_status: dict[str, HealthStatus] = {}
        self.system_status = {
            "overall_health": "normal",  # normal, degraded, critical
            "available_providers": 0,
            "total_providers": 0,
            "last_system_check": time.time(),
            "alerts": [],
        }
        self.alert_callbacks: list[Callable[[str, str, Any], None]] = []
        self.monitoring_thread: threading.Thread | None = None
        self.stop_monitoring = threading.Event()

        # Load config manager if available
        self.config_manager = create_config_manager()

        # Initialize status for known providers
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize status for all known providers."""
        if self.config_manager:
            for provider_name in self.config_manager.get_enabled_providers():
                if provider_name not in self.provider_status:
                    self.provider_status[provider_name] = HealthStatus()
        else:
            # Default providers if no config manager
            default_providers = [
                "openai",
                "anthropic",
                "huggingchat",
                "mistral",
                "gemini",
                "groq",
                "cerebras",
                "ollama",
                "ai21",
                "cohere",
                "perplexity",
                "together",
                "deepseek",
                "fireworks",
                "sambanova",
                "hyperbolic",
                "mock",
            ]
            for provider in default_providers:
                if provider not in self.provider_status:
                    self.provider_status[provider] = HealthStatus()

    def start_monitoring(self):
        """Start background health monitoring thread."""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            console.print("Health monitoring already running")
            return

        self.stop_monitoring.clear()
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitoring_thread.start()
        console.print("🩺 Provider health monitoring started")

    def stop_monitoring_thread(self):
        """Stop the monitoring thread."""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.stop_monitoring.set()
            self.monitoring_thread.join(timeout=5)
            console.print("Health monitoring stopped")

    def _monitoring_loop(self):
        """Background monitoring loop."""
        while not self.stop_monitoring.is_set():
            try:
                # Run health checks
                if self.config.parallel_health_checks:
                    asyncio.run(self._check_all_providers_async())
                else:
                    self._check_all_providers()

                # Update system status
                self._update_system_status()

                # Wait for next check interval
                for _ in range(self.config.check_interval_seconds):
                    if self.stop_monitoring.is_set():
                        break
                    time.sleep(1)
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                time.sleep(60)  # Wait a minute before retrying

    async def _check_all_providers_async(self):
        """Check health of all providers in parallel."""
        tasks = []
        for provider_name in list(self.provider_status.keys()):
            tasks.append(self._check_provider_health_async(provider_name))

        await asyncio.gather(*tasks)

    def _check_all_providers(self):
        """Check health of all providers sequentially."""
        for provider_name in list(self.provider_status.keys()):
            self._check_provider_health(provider_name)

    async def _check_provider_health_async(self, provider_name: str):
        """Asynchronously check health of a specific provider."""
        # Run the synchronous version in a thread pool
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._check_provider_health, provider_name)

    def _check_provider_health(self, provider_name: str):
        """Check health of a specific provider."""
        status = self.provider_status.get(provider_name)
        if not status:
            status = HealthStatus()
            self.provider_status[provider_name] = status

        # Skip if already rate limited and not reset yet
        if status.rate_limited and status.rate_limit_reset:
            if time.time() < status.rate_limit_reset:
                return

        try:
            # Perform a lightweight health check with a simple request
            # This is a simulation - in production, this would make actual API calls
            start_time = time.time()

            # Simulate API call latency and possible errors
            response, error = self._simulate_provider_health_check(provider_name)

            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000

            if error:
                # Handle error case
                status.consecutive_failures += 1
                status.error_message = str(error)
                status.response_time_ms = response_time_ms
                status.last_check_time = time.time()

                # Check if rate limited
                if "rate limit" in str(error).lower() or "429" in str(error):
                    status.rate_limited = True
                    # Exponential backoff
                    backoff_seconds = min(
                        self.config.rate_limit_backoff_seconds
                        * (2**status.consecutive_failures),
                        3600,  # Max 1 hour
                    )
                    status.rate_limit_reset = time.time() + backoff_seconds

                    self._trigger_alert(
                        provider_name,
                        "warning",
                        f"Rate limited - backing off for {backoff_seconds}s",
                    )

                # Check if reached failure threshold
                if status.consecutive_failures >= self.config.failure_threshold:
                    status.is_available = False
                    status.alert_level = "critical"

                    self._trigger_alert(
                        provider_name,
                        "critical",
                        f"Provider unavailable after {status.consecutive_failures} failures",
                    )
            else:
                # Success case
                old_status = "unavailable" if not status.is_available else "available"

                status.is_available = True
                status.consecutive_failures = 0
                status.error_message = None
                status.rate_limited = False
                status.rate_limit_reset = None
                status.response_time_ms = response_time_ms
                status.last_check_time = time.time()

                # Update historical data (keep last 100 data points)
                status.historical_response_times.append(response_time_ms)
                if len(status.historical_response_times) > 100:
                    status.historical_response_times.pop(0)

                # Set alert level based on response time
                if response_time_ms > self.config.response_time_critical_ms:
                    status.alert_level = "warning"
                    self._trigger_alert(
                        provider_name,
                        "warning",
                        f"Slow response time: {response_time_ms:.0f}ms",
                    )
                elif response_time_ms > self.config.response_time_warning_ms:
                    status.alert_level = "warning"
                else:
                    status.alert_level = "normal"

                # If provider was previously unavailable, alert that it's back
                if old_status == "unavailable":
                    self._trigger_alert(
                        provider_name,
                        "info",
                        f"Provider back online, response time: {response_time_ms:.0f}ms",
                    )

            # Parse response for quota information if available
            if response and isinstance(response, dict):
                if "quota_remaining" in response:
                    status.quota_remaining = response["quota_remaining"]
                if "quota_reset" in response:
                    status.quota_reset_time = response["quota_reset"]

        except Exception as e:
            logger.error(f"Error checking health for {provider_name}: {e}")
            status.error_message = f"Health check error: {str(e)}"
            status.last_check_time = time.time()
            status.consecutive_failures += 1

    def _simulate_provider_health_check(
        self, provider_name: str
    ) -> tuple[dict | None, Exception | None]:
        """
        Simulate a provider health check for testing.
        In a real implementation, this would make an actual API call.
        """
        # Simulate different provider characteristics
        provider_configs = {
            "openai": {
                "success_rate": 0.98,
                "avg_latency": 500,
                "rate_limit_chance": 0.01,
            },
            "anthropic": {
                "success_rate": 0.97,
                "avg_latency": 600,
                "rate_limit_chance": 0.01,
            },
            "huggingchat": {
                "success_rate": 0.7,
                "avg_latency": 2000,
                "rate_limit_chance": 0.2,
            },
            "mistral": {
                "success_rate": 0.95,
                "avg_latency": 400,
                "rate_limit_chance": 0.02,
            },
            "gemini": {
                "success_rate": 0.96,
                "avg_latency": 450,
                "rate_limit_chance": 0.01,
            },
            "groq": {
                "success_rate": 0.92,
                "avg_latency": 300,
                "rate_limit_chance": 0.05,
            },
            "cerebras": {
                "success_rate": 0.90,
                "avg_latency": 250,
                "rate_limit_chance": 0.07,
            },
            "ollama": {
                "success_rate": 0.99,
                "avg_latency": 1500,
                "rate_limit_chance": 0,
            },
        }

        # Default config for providers not explicitly defined
        default_config = {
            "success_rate": 0.9,
            "avg_latency": 800,
            "rate_limit_chance": 0.03,
        }
        config = provider_configs.get(provider_name, default_config)

        # Simulate latency
        latency = random.gauss(config["avg_latency"], config["avg_latency"] * 0.3)
        latency = max(50, latency)  # Minimum 50ms
        time.sleep(latency / 1000)

        # Simulate rate limiting
        if random.random() < config["rate_limit_chance"]:
            return None, Exception("Rate limit exceeded. Try again in 60 seconds.")

        # Simulate success/failure
        if random.random() < config["success_rate"]:
            # Success
            response = {
                "status": "ok",
                "provider": provider_name,
                "quota_remaining": random.randint(50, 1000),
                "quota_reset": time.time() + 3600,  # 1 hour
            }
            return response, None
        else:
            # Failure (not rate limit)
            return None, Exception(
                f"API error: {random.choice(['timeout', 'server error', 'connection refused'])}"
            )

    def _update_system_status(self):
        """Update overall system status based on provider health."""
        available_count = sum(
            1 for status in self.provider_status.values() if status.is_available
        )
        total_count = len(self.provider_status)

        self.system_status["available_providers"] = available_count
        self.system_status["total_providers"] = total_count
        self.system_status["last_system_check"] = time.time()

        # Determine overall health
        if available_count == 0:
            self.system_status["overall_health"] = "critical"
            self._trigger_alert("system", "critical", "All providers unavailable")
        elif available_count < total_count * 0.5:
            self.system_status["overall_health"] = "critical"
            self._trigger_alert(
                "system",
                "critical",
                f"Only {available_count}/{total_count} providers available",
            )
        elif available_count < total_count * 0.8:
            self.system_status["overall_health"] = "degraded"
            self._trigger_alert(
                "system",
                "warning",
                f"{total_count - available_count} providers unavailable",
            )
        else:
            self.system_status["overall_health"] = "normal"

    def get_provider_status(self, provider_name: str) -> HealthStatus | None:
        """Get health status for a specific provider."""
        return self.provider_status.get(provider_name)

    def is_provider_available(self, provider_name: str) -> bool:
        """Check if a provider is available."""
        status = self.get_provider_status(provider_name)
        return status is not None and status.is_available and not status.rate_limited

    def get_available_providers(self) -> list[str]:
        """Get list of currently available providers."""
        return [
            name
            for name, status in self.provider_status.items()
            if status.is_available and not status.rate_limited
        ]

    def get_fallback_providers(self, primary_provider: str) -> list[str]:
        """Get ordered list of fallback providers if primary fails."""
        available = self.get_available_providers()
        if primary_provider in available:
            available.remove(primary_provider)

        # Try to get provider profiles for smart ordering
        if self.config_manager:
            # Order by priority if config manager available
            providers_with_priority = []
            for name in available:
                config = self.config_manager.get_provider_config(name)
                priority = config.priority if config else 50
                providers_with_priority.append((name, priority))

            # Sort by priority (highest first)
            providers_with_priority.sort(key=lambda x: x[1], reverse=True)
            return [name for name, _ in providers_with_priority]

        # Default ordering if no config manager
        return available

    def select_provider(self, preferred_providers: list[str]) -> str | None:
        """Select the best available provider from preferred list."""
        available = self.get_available_providers()

        # Find first available from preferred list
        for provider in preferred_providers:
            if provider in available:
                return provider

        # If none of preferred are available, return first available
        return available[0] if available else None

    def register_alert_callback(self, callback: Callable[[str, str, Any], None]):
        """Register a callback for health alerts."""
        self.alert_callbacks.append(callback)

    def _trigger_alert(self, provider: str, level: str, message: str):
        """Trigger health alert to all registered callbacks."""
        if not self.config.alert_on_failures and level in ["warning", "critical"]:
            return

        alert = {
            "provider": provider,
            "level": level,
            "message": message,
            "timestamp": time.time(),
        }

        # Store alert
        self.system_status["alerts"].append(alert)
        # Limit alerts history
        if len(self.system_status["alerts"]) > 100:
            self.system_status["alerts"] = self.system_status["alerts"][-100:]

        # Notify callbacks
        for callback in self.alert_callbacks:
            try:
                callback(provider, level, message)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")

    def get_system_health(self) -> dict[str, Any]:
        """Get comprehensive system health status."""
        return {
            "system": self.system_status,
            "providers": {
                name: {
                    "is_available": status.is_available,
                    "rate_limited": status.rate_limited,
                    "alert_level": status.alert_level,
                    "response_time_ms": status.response_time_ms,
                    "last_check_time": datetime.fromtimestamp(
                        status.last_check_time
                    ).isoformat(),
                    "consecutive_failures": status.consecutive_failures,
                    "error_message": status.error_message,
                    "quota_remaining": status.quota_remaining,
                    "rate_limit_reset": (
                        datetime.fromtimestamp(status.rate_limit_reset).isoformat()
                        if status.rate_limit_reset
                        else None
                    ),
                }
                for name, status in self.provider_status.items()
            },
        }

    def export_metrics(self, format: str = "json") -> str:
        """Export health metrics in the specified format."""
        metrics = self.get_system_health()

        if format.lower() == "json":
            return json.dumps(metrics, indent=2)
        elif format.lower() == "csv":
            # Simple CSV export for provider metrics
            csv_lines = [
                "provider,available,rate_limited,response_time_ms,alert_level,consecutive_failures"
            ]
            for name, data in metrics["providers"].items():
                csv_lines.append(
                    f"{name},{data['is_available']},{data['rate_limited']},{data['response_time_ms']},{data['alert_level']},{data['consecutive_failures']}"
                )
            return "\n".join(csv_lines)
        else:
            return f"Unsupported format: {format}"

    def display_health_dashboard(self):
        """Display rich health dashboard in the console."""
        table = Table(title="🩺 Provider Health Status")

        table.add_column("Provider", style="cyan", no_wrap=True)
        table.add_column("Status", justify="center")
        table.add_column("Response Time", justify="right")
        table.add_column("Last Check", justify="right")
        table.add_column("Quota", justify="right")
        table.add_column("Alert Level", justify="center")
        table.add_column("Details", style="dim")

        metrics = self.get_system_health()

        for name, data in sorted(metrics["providers"].items()):
            # Status
            if not data["is_available"]:
                status = "❌ Offline"
                status_style = "red"
            elif data["rate_limited"]:
                status = "⏳ Rate Limited"
                status_style = "yellow"
            else:
                status = "✅ Available"
                status_style = "green"

            # Format response time
            response_time = (
                f"{data['response_time_ms']:.0f}ms"
                if data["response_time_ms"] is not None
                else "N/A"
            )

            # Format last check time
            last_check = data["last_check_time"].split("T")[1].split(".")[0]

            # Format quota
            quota = (
                f"{data['quota_remaining']}"
                if data["quota_remaining"] is not None
                else "Unknown"
            )

            # Alert level with color
            if data["alert_level"] == "critical":
                alert_level = "[red]Critical[/red]"
            elif data["alert_level"] == "warning":
                alert_level = "[yellow]Warning[/yellow]"
            else:
                alert_level = "[green]Normal[/green]"

            # Details
            details = data["error_message"] if data["error_message"] else ""

            table.add_row(
                name,
                f"[{status_style}]{status}[/{status_style}]",
                response_time,
                last_check,
                quota,
                alert_level,
                details,
            )

        console.print(table)

        # System summary
        system = metrics["system"]
        health_color = "green"
        if system["overall_health"] == "critical":
            health_color = "red"
        elif system["overall_health"] == "degraded":
            health_color = "yellow"

        console.print(
            Panel(
                f"Overall System Health: [{health_color}]{system['overall_health'].upper()}[/{health_color}]\n"
                f"Available Providers: {system['available_providers']}/{system['total_providers']}\n"
                f"Last Check: {datetime.fromtimestamp(system['last_system_check']).strftime('%H:%M:%S')}\n"
                f"Recent Alerts: {len(system['alerts'])}"
            )
        )

        # Recent alerts
        if system["alerts"]:
            console.print("\n[bold]Recent Alerts:[/bold]")
            for alert in system["alerts"][-5:]:  # Show last 5 alerts
                alert_time = datetime.fromtimestamp(alert["timestamp"]).strftime(
                    "%H:%M:%S"
                )
                level_color = (
                    "green"
                    if alert["level"] == "info"
                    else "yellow" if alert["level"] == "warning" else "red"
                )
                console.print(
                    f"[{level_color}]{alert['level'].upper()}[/{level_color}] "
                    f"[{alert_time}] {alert['provider']}: {alert['message']}"
                )


class ProviderHealthDashboard:
    """Interactive dashboard for monitoring provider health."""

    def __init__(self, monitor: ProviderHealthMonitor):
        self.monitor = monitor
        self.refresh_interval = 10  # seconds

    def start(self):
        """Start the interactive dashboard."""
        try:
            console.clear()
            with Progress() as progress:
                refresh_task = progress.add_task(
                    "[cyan]Next refresh...", total=self.refresh_interval
                )

                while True:
                    # Display dashboard
                    console.clear()
                    self.monitor.display_health_dashboard()

                    # Reset progress
                    progress.reset(refresh_task)

                    # Wait with progress indicator
                    for i in range(self.refresh_interval):
                        progress.update(refresh_task, completed=i)
                        time.sleep(1)

        except KeyboardInterrupt:
            console.print("\n[yellow]Dashboard stopped.[/yellow]")


def create_health_monitor() -> ProviderHealthMonitor:
    """Factory function to create health monitor."""
    return ProviderHealthMonitor()


if __name__ == "__main__":
    import sys

    monitor = create_health_monitor()

    if len(sys.argv) > 1 and sys.argv[1] == "dashboard":
        # Run interactive dashboard
        monitor.start_monitoring()
        dashboard = ProviderHealthDashboard(monitor)
        dashboard.start()
    else:
        # Run quick health check
        for provider in monitor.provider_status:
            monitor._check_provider_health(provider)

        monitor.display_health_dashboard()

        console.print(
            "\n[cyan]For continuous monitoring, run:[/cyan] python provider_health_monitor.py dashboard"
        )
