#!/usr/bin/env python3
"""
🤖 AI Orchestra - AI-Powered Report Analyzer
===========================================

Uses the project's own AI capabilities to analyze and summarize orchestration reports.
"""

import argparse
import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from ai_provider_manager import SmartProviderRouter

console = Console()


def analyze_report(report_path: Path) -> str:
    """Analyzes an orchestration report and returns a human-readable summary."""
    try:
        with open(report_path) as f:
            report = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return f"Error reading report file: {e}"

    # Prepare a summary of the report for the AI prompt
    summary = {
        "run_id": report.get("run_id"),
        "overall_status": report.get("overall_status"),
        "start_time": report.get("start_time"),
        "end_time": report.get("end_time"),
        "rollback_status": report.get("rollback_status"),
        "tasks": [],
    }

    for task_name, task_details in report.get("tasks", {}).items():
        summary["tasks"].append(
            {
                "name": task_name,
                "status": task_details.get("status"),
                "duration_seconds": task_details.get("duration_seconds"),
            }
        )

    prompt = f"""
    Please analyze the following JSON summary of an orchestration run.
    Provide a brief, human-readable summary of the key outcomes.
    Focus on the overall status, any failed tasks, and the total duration.

    Report Summary:
    ```json
    {json.dumps(summary, indent=2)}
    ```
    """

    console.print("🤖 Asking AI to analyze the report...")
    try:
        router = SmartProviderRouter()
        ai_summary = router.generate(prompt, strategy="cost_optimized")
        return ai_summary
    except Exception as e:
        return f"Error getting AI summary: {e}"


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="AI-Powered Report Analyzer")
    parser.add_argument(
        "--report-path",
        type=str,
        required=True,
        help="Path to the orchestration report JSON file.",
    )
    args = parser.parse_args()

    summary = analyze_report(Path(args.report_path))

    console.print(
        Panel(
            summary,
            title="[bold green]🤖 AI Analysis of Orchestration Run[/bold green]",
            border_style="green",
        )
    )


if __name__ == "__main__":
    main()
