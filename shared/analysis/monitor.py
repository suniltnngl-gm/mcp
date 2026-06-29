#!/usr/bin/env python3
"""
🎭 AI Orchestra - Project Monitoring & Maintenance
================================================

Automated monitoring and maintenance for the AI Orchestra project.
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from scripts.monitoring.dependency_monitor import DependencyMonitor
from scripts.monitoring.maintenance_monitor import MaintenanceMonitor
from scripts.monitoring.performance_monitor import PerformanceMonitor
from scripts.monitoring.security_monitor import SecurityMonitor

console = Console()


class ProjectMonitor:
    """Monitors and maintains the AI Orchestra project."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.reports_dir = project_root / "reports"
        self.reports_dir.mkdir(exist_ok=True)

        self.dependency_monitor = DependencyMonitor(project_root)
        self.security_monitor = SecurityMonitor(project_root)
        self.performance_monitor = PerformanceMonitor(project_root)
        self.maintenance_monitor = MaintenanceMonitor(project_root)

    def maintenance_report(self) -> dict:
        """Generate comprehensive maintenance report."""
        console.print(
            Panel.fit("🔧 Generating Maintenance Report", style="bold yellow")
        )

        report = {
            "timestamp": datetime.now().isoformat(),
            "dependencies": self.dependency_monitor.check_dependencies(),
            "security": self.security_monitor.security_scan(),
            "performance": self.performance_monitor.performance_monitoring(),
            "updates": self.dependency_monitor.dependency_update_check(),
        }

        # Calculate overall health score
        health_score = self._calculate_health_score(report)
        report["health_score"] = health_score

        return report

    def _calculate_health_score(self, report: dict) -> dict:
        """Calculate overall project health score."""
        score = 100
        issues = []

        # Security deductions
        if not report["security"]["secret_scan"]["clean"]:
            score -= 20
            issues.append("Hardcoded secrets found")

        if not report["security"]["env_security"]["in_gitignore"]:
            score -= 10
            issues.append(".env not in .gitignore")

        if not report["security"]["permissions"]["clean"]:
            score -= 5
            issues.append("File permission issues")

        # Dependency deductions
        if report["updates"].get("lock_needs_update", False):
            score -= 5
            issues.append("Dependencies may be outdated")

        # Performance considerations
        lines_per_file = report["performance"]["project_size"]["avg_lines_per_file"]
        if lines_per_file > 500:
            score -= 5
            issues.append("Large file sizes detected")

        test_ratio = report["performance"]["testing"]["test_coverage_ratio"]
        if test_ratio < 0.3:
            score -= 10
            issues.append("Low test coverage")

        return {
            "score": max(0, score),
            "grade": self._score_to_grade(score),
            "issues": issues,
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

    def display_maintenance_report(self, report: dict):
        """Display the maintenance report."""
        console.print("\n📋 Project Maintenance Report")
        console.print("=" * 50)

        # Health score
        health = report["health_score"]
        score_color = (
            "green"
            if health["score"] >= 80
            else "yellow" if health["score"] >= 60 else "red"
        )

        console.print(
            Panel(
                f"Overall Health: [bold {score_color}]{health['score']}/100 (Grade: {health['grade']})[/bold {score_color}]",
                style=score_color,
            )
        )

        if health["issues"]:
            console.print("\n⚠️ Issues Found:")
            for issue in health["issues"]:
                console.print(f"  • {issue}")

        # Security summary
        security = report["security"]
        security_status = (
            "🟢 SECURE"
            if all(
                [
                    security["secret_scan"]["clean"],
                    security["env_security"]["in_gitignore"],
                    security["permissions"]["clean"],
                ]
            )
            else "🟡 NEEDS ATTENTION"
        )

        console.print(f"\n🛡️ Security Status: {security_status}")

        # Dependencies summary
        deps = report["dependencies"]
        console.print(
            f"\n📦 Dependencies: {deps.get('dependency_count', 'Unknown')} packages"
        )

        if report["updates"].get("lock_needs_update"):
            console.print("  ⚠️ Lock file is over 7 days old - consider updating")

        # Performance summary
        perf = report["performance"]
        console.print(
            f"\n📈 Project Size: {perf['project_size']['python_files']} files, {perf['project_size']['total_lines']} lines"
        )
        console.print(f"🧪 Test Coverage: {perf['testing']['test_files']} test files")

    def save_report(self, report: dict, filename: str | None = None):
        """Save maintenance report to file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"maintenance_report_{timestamp}.json"

        report_file = self.reports_dir / filename
        report_file.write_text(json.dumps(report, indent=2, default=str))

        console.print(f"📄 Report saved to: {report_file}")

    def automated_maintenance(self) -> dict:
        """Run automated maintenance tasks."""
        return self.maintenance_monitor.automated_maintenance()

    def continuous_monitoring(self, interval_minutes: int = 30):
        """Run continuous monitoring."""
        console.print(
            Panel.fit(
                f"🔄 Continuous Monitoring (Every {interval_minutes} minutes)",
                style="bold green",
            )
        )
        console.print("Press Ctrl+C to stop monitoring")

        try:
            while True:
                timestamp = datetime.now().strftime("%H:%M:%S")
                console.print(f"\n⏰ {timestamp} - Running monitoring cycle...")

                # Quick health check
                basic_checks = {
                    "disk_space": self.performance_monitor._check_disk_space(),
                    "process_health": self.performance_monitor._check_process_health(),
                    "file_integrity": self.performance_monitor._check_file_integrity(),
                }

                # Display quick status
                table = Table(show_header=True, header_style="bold blue")
                table.add_column("Check", style="cyan")
                table.add_column("Status", style="bold")

                for check_name, status in basic_checks.items():
                    status_text = "✅ OK" if status else "❌ ISSUE"
                    status_style = "green" if status else "red"
                    table.add_row(
                        check_name.replace("_", " ").title(),
                        f"[{status_style}]{status_text}[/{status_style}]",
                    )

                console.print(table)

                # Sleep until next cycle
                time.sleep(interval_minutes * 60)

        except KeyboardInterrupt:
            console.print("\n🛑 Monitoring stopped")


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="🎭 AI Orchestra Project Monitor")
    parser.add_argument(
        "action",
        nargs="?",
        default="report",
        choices=["report", "monitor", "security", "deps", "maintain", "health"],
        help="Monitoring action to perform",
    )
    parser.add_argument("--save", action="store_true", help="Save report to file")
    parser.add_argument(
        "--interval", type=int, default=30, help="Monitoring interval in minutes"
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    monitor = ProjectMonitor(project_root)

    try:
        if args.action == "report":
            report = monitor.maintenance_report()
            monitor.display_maintenance_report(report)
            if args.save:
                monitor.save_report(report)

        elif args.action == "monitor":
            monitor.continuous_monitoring(args.interval)

        elif args.action == "security":
            security_results = monitor.security_monitor.security_scan()
            console.print("🛡️ Security Scan Results:")
            console.print(json.dumps(security_results, indent=2))

        elif args.action == "deps":
            deps_info = monitor.dependency_monitor.check_dependencies()
            console.print("📦 Dependency Information:")
            console.print(json.dumps(deps_info, indent=2))

        elif args.action == "maintain":
            maintenance_results = monitor.automated_maintenance()
            console.print("🔧 Maintenance Results:")
            console.print(json.dumps(maintenance_results, indent=2, default=str))

        elif args.action == "health":
            report = monitor.maintenance_report()
            health = report["health_score"]
            console.print(
                f"📊 Project Health: {health['score']}/100 (Grade: {health['grade']})"
            )

    except KeyboardInterrupt:
        console.print("\n❌ Monitoring cancelled by user")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n❌ Monitoring failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
