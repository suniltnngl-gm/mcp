#!/usr/bin/env python3
"""
🎭 AI Orchestra - Development Workflow Coordinator
=================================================

Lightweight coordinator for development workflow automation components.
"""

import sys
from pathlib import Path

from rich.console import Console

from scripts.workflows.demo_runner import DemoRunner
from scripts.workflows.dev_workflow import DevWorkflow
from scripts.workflows.health_check import HealthChecker
from scripts.workflows.learning_workflow import LearningWorkflow
from scripts.workflows.refactor_workflow import RefactorWorkflow

console = Console()


class WorkflowAutomator:
    """Lightweight coordinator for development workflow automation."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.health_checker = HealthChecker(project_root)
        self.demo_runner = DemoRunner(project_root)
        self.dev_workflow = DevWorkflow(project_root)
        self.learning_workflow = LearningWorkflow(project_root)
        self.refactor_workflow = RefactorWorkflow(project_root)

    def interactive_workflow(self):
        """Delegate to interactive workflow selector."""
        return self.dev_workflow.interactive_workflow()

    def health_check_workflow(self):
        """Delegate to health check workflow."""
        return self.health_checker.health_check_workflow()

    def demo_workflow(self):
        """Delegate to demo workflow."""
        return self.demo_runner.demo_workflow()

    def test_workflow(self, test_type: str = "all"):
        """Delegate to test workflow."""
        return self.dev_workflow.test_workflow(test_type)

    def ci_cd_workflow(self):
        """Delegate to CI/CD workflow."""
        return self.dev_workflow.ci_cd_workflow()

    def deployment_prep_workflow(self):
        """Delegate to deployment preparation workflow."""
        return self.dev_workflow.deployment_prep_workflow()

    def web_development_workflow(self, port: int = 8000):
        """Delegate to web development workflow."""
        return self.dev_workflow.web_development_workflow(port)

    def benchmark_workflow(self):
        """Delegate to benchmark workflow."""
        return self.dev_workflow.benchmark_workflow()

    def learn_workflow(self):
        """Delegate to learning workflow."""
        return self.learning_workflow.learn_from_errors()

    def refactor_workflow(self, items_to_refactor: list[str], refactor_type: str):
        """Delegate to refactor workflow."""
        return self.refactor_workflow.safe_refactor(items_to_refactor, refactor_type)


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="🎭 AI Orchestra Workflow Automator")
    parser.add_argument(
        "workflow",
        nargs="?",
        default="interactive",
        choices=[
            "interactive",
            "health",
            "demo",
            "test",
            "web",
            "cicd",
            "deploy-prep",
            "benchmark",
            "learn",
            "refactor",
        ],
        help="Workflow to run",
    )
    parser.add_argument(
        "--test-type",
        default="all",
        choices=["all", "unit", "integration", "coverage"],
        help="Type of tests to run",
    )
    parser.add_argument("--port", type=int, default=8000, help="Port for web server")
    parser.add_argument("--items", nargs="+", help="List of items to refactor")
    parser.add_argument("--type", default="merge", help="Type of refactoring")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    automator = WorkflowAutomator(project_root)

    try:
        if args.workflow == "interactive":
            automator.interactive_workflow()
        elif args.workflow == "health":
            automator.health_check_workflow()
            console.print("✅ Health check completed")
        elif args.workflow == "demo":
            automator.demo_workflow()
        elif args.workflow == "test":
            automator.test_workflow(args.test_type)
        elif args.workflow == "web":
            automator.web_development_workflow(args.port)
        elif args.workflow == "cicd":
            automator.ci_cd_workflow()
        elif args.workflow == "deploy-prep":
            automator.deployment_prep_workflow()
        elif args.workflow == "benchmark":
            automator.benchmark_workflow()
        elif args.workflow == "learn":
            automator.learn_workflow()
        elif args.workflow == "refactor":
            if not args.items:
                console.print(
                    "\n❌ Please provide a list of items to refactor with --items"
                )
                sys.exit(1)
            automator.refactor_workflow(args.items, args.type)

    except KeyboardInterrupt:
        console.print("\n❌ Workflow cancelled by user")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n❌ Workflow failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
