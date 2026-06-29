#!/usr/bin/env python3
"""
🎯 AI Orchestra - Monitor Coordinator
=====================================

Lightweight coordinator that orchestrates modular monitoring components.
"""

import json
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from scripts.monitoring.dependency_monitor import DependencyMonitor
from scripts.monitoring.performance_monitor import PerformanceMonitor
from scripts.monitoring.security_monitor import SecurityMonitor

console = Console()


class MonitorCoordinator:
    """Coordinates and orchestrates all monitoring components."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.reports_dir = project_root / ".orchestration_reports"
        self.reports_dir.mkdir(exist_ok=True)

        # Initialize component monitors
        self.dependency_monitor = DependencyMonitor(project_root)
        self.security_monitor = SecurityMonitor(project_root)
        self.performance_monitor = PerformanceMonitor(project_root)

    def comprehensive_health_check(self) -> dict:
        """Run comprehensive health check across all components."""
        console.print(
            Panel.fit("🎯 Comprehensive System Health Check", style="bold blue")
        )

        health_report = {"timestamp": datetime.now().isoformat(), "components": {}}

        # Run dependency check
        console.print("📦 Running dependency health check...")
        dependency_report = self.dependency_monitor.generate_dependency_report()
        health_report["components"]["dependencies"] = dependency_report

        # Run security check
        console.print("🛡️ Running security health check...")
        security_report = self.security_monitor.generate_security_report()
        security_score = self.security_monitor.calculate_security_score(security_report)
        health_report["components"]["security"] = {
            "report": security_report,
            "score": security_score,
        }

        # Run performance check
        console.print("🚀 Running performance health check...")
        performance_report = self.performance_monitor.generate_performance_report()
        performance_health = self.performance_monitor.check_performance_health()
        health_report["components"]["performance"] = {
            "report": performance_report,
            "health": performance_health,
        }

        # Calculate overall health
        overall_health = self._calculate_overall_health(health_report)
        health_report["overall_health"] = overall_health

        return health_report

    def _calculate_overall_health(self, report: dict) -> dict:
        """Calculate overall system health score."""
        scores = []
        issues = []

        # Security score
        security_score = report["components"]["security"]["score"]["score"]
        scores.append(security_score)
        issues.extend(report["components"]["security"]["score"]["issues"])

        # Dependency score (simplified)
        deps = report["components"]["dependencies"]
        dep_score = 100
        if not deps["environment"]["python_available"]:
            dep_score -= 30
            issues.append("Python not available")
        if not deps["environment"]["uv_available"]:
            dep_score -= 20
            issues.append("UV package manager not available")
        if deps["updates"].get("lock_needs_update"):
            dep_score -= 10
            issues.append("Dependencies may be outdated")

        scores.append(dep_score)

        # Performance score (simplified)
        perf_health = report["components"].get("performance", {}).get("health", {})
        perf_score = 100
        if not perf_health.get("cpu_healthy", True):
            perf_score -= 20
            issues.append("High CPU usage detected")
        if not perf_health.get("memory_healthy", True):
            perf_score -= 25
            issues.append("High memory usage detected")
        if not perf_health.get("disk_healthy", True):
            perf_score -= 15
            issues.append("Low disk space")

        scores.append(perf_score)

        # Calculate overall
        overall_score = sum(scores) // len(scores) if scores else 0

        return {
            "score": overall_score,
            "grade": self._score_to_grade(overall_score),
            "component_scores": {
                "security": security_score,
                "dependencies": dep_score,
                "performance": perf_score,
            },
            "issues": issues,
            "recommendations": self._generate_overall_recommendations(issues),
        }

    def _score_to_grade(self, score: int) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _generate_overall_recommendations(self, issues: list) -> list:
        """Generate overall system recommendations."""
        recommendations = []

        if not issues:
            recommendations.append("System health looks excellent!")
            recommendations.append("Consider regular automated health checks")
        else:
            recommendations.append("Address identified issues to improve system health")
            if len(issues) > 5:
                recommendations.append(
                    "Focus on highest priority security and dependency issues first"
                )

        return recommendations

    def display_health_summary(self, report: dict):
        """Display a formatted health summary."""
        console.print("\n🎯 System Health Summary")
        console.print("=" * 50)

        overall = report["overall_health"]
        score_color = (
            "green"
            if overall["score"] >= 80
            else "yellow" if overall["score"] >= 60 else "red"
        )

        console.print(
            Panel(
                f"Overall Health: [bold {score_color}]{overall['score']}/100 (Grade: {overall['grade']})[/bold {score_color}]",
                style=score_color,
            )
        )

        # Component scores table
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Component", style="cyan")
        table.add_column("Score", style="bold")
        table.add_column("Status", style="white")

        for component, score in overall["component_scores"].items():
            score_color = "green" if score >= 80 else "yellow" if score >= 60 else "red"
            status = (
                "Excellent"
                if score >= 90
                else (
                    "Good"
                    if score >= 80
                    else "Needs Attention" if score >= 60 else "Critical"
                )
            )

            table.add_row(
                component.title(),
                f"[{score_color}]{score}/100[/{score_color}]",
                f"[{score_color}]{status}[/{score_color}]",
            )

        console.print(table)

        # Issues and recommendations
        if overall["issues"]:
            console.print("\n⚠️ Issues Requiring Attention:")
            for issue in overall["issues"]:
                console.print(f"  • {issue}")

        if overall["recommendations"]:
            console.print("\n💡 Recommendations:")
            for rec in overall["recommendations"]:
                console.print(f"  • {rec}")

    def save_health_report(self, report: dict, filename: str = None):
        """Save health report to file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"health_report_{timestamp}.json"

        report_file = self.reports_dir / filename
        report_file.write_text(json.dumps(report, indent=2, default=str))
        console.print(f"📄 Health report saved to: {report_file}")

        return report_file

    def quick_status_check(self) -> dict:
        """Quick system status check without full reports."""
        console.print("⚡ Quick status check...")

        status = {
            "timestamp": datetime.now().isoformat(),
            "python_available": False,
            "dependencies_ok": False,
            "security_clean": False,
            "overall_status": "unknown",
        }

        try:
            # Quick Python check
            import subprocess

            result = subprocess.run(
                ["python", "--version"], capture_output=True, timeout=5
            )
            status["python_available"] = result.returncode == 0

            # Quick dependency check
            deps_report = self.dependency_monitor.check_dependencies()
            status["dependencies_ok"] = deps_report.get("tree_available", False)

            # Quick security check
            secrets_report = self.security_monitor.scan_for_secrets()
            status["security_clean"] = secrets_report.get("clean", False)

            # Overall status
            if all(
                [
                    status["python_available"],
                    status["dependencies_ok"],
                    status["security_clean"],
                ]
            ):
                status["overall_status"] = "healthy"
            elif status["python_available"] and status["dependencies_ok"]:
                status["overall_status"] = "needs_attention"
            else:
                status["overall_status"] = "critical"

        except Exception as e:
            status["error"] = str(e)
            status["overall_status"] = "error"

        return status


def main():
    """Main entry point for standalone execution."""
    import argparse

    parser = argparse.ArgumentParser(description="🎯 Monitor Coordinator")
    parser.add_argument(
        "action",
        nargs="?",
        default="health",
        choices=["health", "quick", "dependencies", "security", "performance"],
        help="Monitoring action to perform",
    )
    parser.add_argument("--save", action="store_true", help="Save report to file")
    parser.add_argument("--context-in", type=str, help="Path to input context file")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    coordinator = MonitorCoordinator(project_root)

    try:
        if args.action == "health":
            report = coordinator.comprehensive_health_check()
            coordinator.display_health_summary(report)

            if args.save:
                coordinator.save_health_report(report)

            # Output JSON for orchestrator
            output_context = {"health_report": report}
            print(json.dumps(output_context))

        elif args.action == "quick":
            status = coordinator.quick_status_check()
            console.print("⚡ Quick Status:")
            console.print(f"  Overall: {status['overall_status'].upper()}")
            console.print(f"  Python: {'✅' if status['python_available'] else '❌'}")
            console.print(
                f"  Dependencies: {'✅' if status['dependencies_ok'] else '❌'}"
            )
            console.print(f"  Security: {'✅' if status['security_clean'] else '❌'}")

            # Output JSON for orchestrator
            output_context = {"quick_status": status}
            print(json.dumps(output_context))

        elif args.action == "dependencies":
            report = coordinator.dependency_monitor.generate_dependency_report()
            console.print("📦 Dependency Report Generated")

            # Output JSON for orchestrator
            output_context = {"dependency_report": report}
            print(json.dumps(output_context))

        elif args.action == "security":
            report = coordinator.security_monitor.generate_security_report()
            score = coordinator.security_monitor.calculate_security_score(report)
            console.print("🛡️ Security Report Generated")
            console.print(f"Security Score: {score['score']}/100 ({score['grade']})")

            # Output JSON for orchestrator
            output_context = {"security_report": report, "security_score": score}
            print(json.dumps(output_context))

        elif args.action == "performance":
            report = coordinator.performance_monitor.generate_performance_report()
            health = coordinator.performance_monitor.check_performance_health()
            console.print("🚀 Performance Report Generated")
            console.print(
                f"Performance: {'Healthy' if health.get('overall_healthy', False) else 'Needs Attention'}"
            )

            # Output JSON for orchestrator
            output_context = {
                "performance_report": report,
                "performance_health": health,
            }
            print(json.dumps(output_context))

    except KeyboardInterrupt:
        console.print("\n❌ Monitoring cancelled by user")
        exit(1)
    except Exception as e:
        console.print(f"\n❌ Monitoring failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()
