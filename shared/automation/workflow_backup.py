#!/usr/bin/env python3
"""
🎭 AI Orchestra - Development Workflow Coordinator
=================================================

Lightweight coordinator for development workflow automation components.
"""

import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from scripts.workflows.demo_runner import DemoRunner
from scripts.workflows.dev_workflow import DevWorkflow
from scripts.workflows.health_check import HealthChecker

console = Console()


class WorkflowAutomator:
    """Lightweight coordinator for development workflow automation."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.health_checker = HealthChecker(project_root)
        self.demo_runner = DemoRunner(project_root)
        self.dev_workflow = DevWorkflow(project_root)

    def interactive_workflow(self):
        """Delegate to interactive workflow functionality."""
        console.print(
            Panel.fit("🎭 AI Orchestra - Interactive Workflow", style="bold magenta")
        )

        workflows = {
            "1": ("🎪 Demo", "Run complete demo"),
            "2": ("🌐 Web Dev", "Start web development server"),
            "3": ("🧪 Test", "Run test suite"),
            "4": ("🔍 Quality", "Run quality checks"),
            "5": ("❤️ Health", "System health check"),
            "6": ("🔄 CI/CD", "Simulate CI/CD pipeline"),
            "7": ("🚀 Deploy Prep", "Prepare for deployment"),
        }

        from rich.table import Table

        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Option", style="cyan")
        table.add_column("Workflow", style="green")
        table.add_column("Description", style="white")

        for key, (name, description) in workflows.items():
            table.add_row(key, name, description)

        console.print(table)

        while True:
            try:
                choice = console.input("\n🎯 Select workflow (1-7, or 'q' to quit): ")

                if choice.lower() == "q":
                    console.print("👋 Goodbye!")
                    break

                if choice in workflows:
                    workflow_name, _ = workflows[choice]
                    console.print(f"\n🚀 Running {workflow_name}...")

                    if choice == "1":
                        self.demo_runner.demo_workflow()
                    elif choice == "2":
                        self.dev_workflow.web_development_workflow()
                    elif choice == "3":
                        self.dev_workflow.test_workflow()
                    elif choice == "4":
                        from scripts.quality import CodeQualityChecker

                        checker = CodeQualityChecker(self.project_root)
                        results = checker.run_comprehensive_check()
                        checker.display_results(results)
                    elif choice == "5":
                        checks = self.health_checker.health_check_workflow()
                        self.health_checker.display_health_results(checks)
                    elif choice == "6":
                        self.dev_workflow.ci_cd_workflow()
                    elif choice == "7":
                        self.dev_workflow.deployment_prep_workflow()

                    console.print(f"\n✅ {workflow_name} completed!")
                else:
                    console.print("❌ Invalid choice. Please select 1-7 or 'q'.")

            except KeyboardInterrupt:
                console.print("\n👋 Goodbye!")
                break
            except Exception as e:
                console.print(f"❌ Error: {e}")

    def web_development_workflow(self, port: int = 8000) -> bool:
        """Start web development workflow."""
        console.print(
            Panel.fit("🌐 Starting Web Development Server", style="bold cyan")
        )

        # Check if port is available
        import socket

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("localhost", port)) == 0:
                console.print(f"⚠️ Port {port} is already in use")
                return False

        console.print(f"🚀 Starting web server on port {port}...")
        console.print("Press Ctrl+C to stop")

        try:
            # Start web server
            subprocess.run(
                ["uv", "run", "python", "orchestra_cli.py", "web"],
                cwd=self.project_root,
            )
            return True

        except KeyboardInterrupt:
            console.print("\n🛑 Web server stopped")
            return True
        except Exception as e:
            console.print(f"❌ Web server failed: {e}")
            return False

    def ci_cd_workflow(self) -> dict:
        """Simulate CI/CD workflow."""
        console.print(Panel.fit("🔄 CI/CD Workflow Simulation", style="bold yellow"))

        workflow_steps = [
            ("Setup", ["uv", "sync", "--dev"]),
            ("Format Check", ["uv", "run", "black", "--check", "."]),
            ("Type Check", ["uv", "run", "mypy", ".", "--ignore-missing-imports"]),
            ("Security Check", ["python", "scripts/dev.sh", "security"]),
            ("Tests", ["uv", "run", "pytest"]),
            ("Health Check", ["python", "scripts/dev.sh", "health"]),
        ]

        results = {}
        overall_success = True

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
        ) as progress:

            task = progress.add_task("CI/CD Pipeline...", total=len(workflow_steps))

            for step_name, cmd in workflow_steps:
                progress.update(task, description=f"Running {step_name}...")

                success, stdout, stderr = self.run_command_with_output(cmd, step_name)

                results[step_name] = {
                    "success": success,
                    "output": stdout[:200] + "..." if len(stdout) > 200 else stdout,
                    "error": stderr[:200] + "..." if len(stderr) > 200 else stderr,
                }

                if not success:
                    overall_success = False
                    console.print(f"❌ {step_name} failed!")
                else:
                    console.print(f"✅ {step_name} passed")

                progress.advance(task)

        results["overall_success"] = overall_success

        if overall_success:
            console.print(
                Panel(
                    "🎉 CI/CD workflow completed successfully! Ready for deployment.",
                    style="bold green",
                )
            )
        else:
            console.print(
                Panel(
                    "❌ CI/CD workflow failed. Please fix issues before deployment.",
                    style="bold red",
                )
            )

        return results

    def deployment_prep_workflow(self) -> dict:
        """Prepare for deployment workflow."""
        console.print(Panel.fit("🚀 Deployment Preparation", style="bold green"))

        prep_steps = ["security", "health", "full-check"]

        results = {}

        for step in prep_steps:
            console.print(f"🔄 Running {step}...")
            success, stdout, stderr = self.run_command_with_output(
                ["./scripts/dev.sh", step], f"Deployment prep: {step}"
            )

            results[step] = {"success": success, "output": stdout, "error": stderr}

        all_passed = all(result["success"] for result in results.values())

        if all_passed:
            console.print(
                Panel(
                    """
🎉 **Deployment Preparation Complete!**

✅ Security scan passed
✅ Health check passed
✅ Quality checks passed

🚀 **Ready for deployment!**

Next steps:
1. Commit any final changes
2. Tag the release: `git tag v1.0.0`
3. Deploy using your preferred method
            """,
                    style="bold green",
                )
            )
        else:
            console.print(
                Panel(
                    "❌ Deployment preparation failed. Fix issues before deploying.",
                    style="bold red",
                )
            )

        return results

    def interactive_workflow(self):
        """Interactive workflow selector."""
        console.print(
            Panel.fit("🎭 AI Orchestra - Interactive Workflow", style="bold magenta")
        )

        workflows = {
            "1": ("🎪 Demo", "Run complete demo"),
            "2": ("🌐 Web Dev", "Start web development server"),
            "3": ("🧪 Test", "Run test suite"),
            "4": ("🔍 Quality", "Run quality checks"),
            "5": ("❤️ Health", "System health check"),
            "6": ("🔄 CI/CD", "Simulate CI/CD pipeline"),
            "7": ("🚀 Deploy Prep", "Prepare for deployment"),
            "8": ("🤖 AI Review", "Review code with Gemini CLI"),
        }

        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Option", style="cyan")
        table.add_column("Workflow", style="green")
        table.add_column("Description", style="white")

        for key, (name, description) in workflows.items():
            table.add_row(key, name, description)

        console.print(table)

        while True:
            try:
                choice = console.input("\n🎯 Select workflow (1-8, or 'q' to quit): ")

                if choice.lower() == "q":
                    console.print("👋 Goodbye!")
                    break

                if choice in workflows:
                    workflow_name, _ = workflows[choice]
                    console.print(f"\n🚀 Running {workflow_name}...")

                    if choice == "1":
                        self.demo_runner.demo_workflow()
                    elif choice == "2":
                        self.dev_workflow.web_development_workflow()
                    elif choice == "3":
                        self.dev_workflow.test_workflow()
                    elif choice == "4":
                        from scripts.quality import CodeQualityChecker

                        checker = CodeQualityChecker(self.project_root)
                        results = checker.run_comprehensive_check()
                        checker.display_results(results)
                    elif choice == "5":
                        checks = self.health_checker.health_check_workflow()
                        self.health_checker.display_health_results(checks)
                    elif choice == "6":
                        self.dev_workflow.ci_cd_workflow()
                    elif choice == "7":
                        self.dev_workflow.deployment_prep_workflow()
                    elif choice == "8":
                        self.dev_workflow.ai_review_workflow()

                    console.print(f"\n✅ {workflow_name} completed!")

                else:
                    console.print("❌ Invalid choice. Please select 1-8 or 'q'.")

            except KeyboardInterrupt:
                console.print("\n👋 Goodbye!")
                break
            except Exception as e:
                console.print(f"❌ Error: {e}")

    def ai_review_workflow(self):
        """AI-powered code review workflow."""
        console.print(Panel.fit("🤖 AI Code Review Workflow", style="bold blue"))

        if not self._check_gemini_available():
            console.print("❌ Gemini CLI not available")
            return

        console.print("⚠️ This will use API credits")

        review_options = {
            "1": "Review changed files only",
            "2": "Review specific file",
            "3": "Review all Python files (limited)",
            "4": "Review with security focus",
            "5": "Review with performance focus",
        }

        for key, description in review_options.items():
            console.print(f"  {key}. {description}")

        choice = console.input("\nSelect review type (1-5): ")

        if choice == "1":
            self._review_changed_files()
        elif choice == "2":
            file_path = console.input("Enter file path: ")
            if Path(file_path).exists():
                self._review_single_file(Path(file_path))
            else:
                console.print("❌ File not found")
        elif choice == "3":
            self._review_all_files()
        elif choice == "4":
            self._review_with_focus(
                ["security", "vulnerabilities", "authentication", "input validation"]
            )
        elif choice == "5":
            self._review_with_focus(
                [
                    "performance",
                    "optimization",
                    "memory usage",
                    "algorithmic efficiency",
                ]
            )

    def _check_gemini_available(self) -> bool:
        """Check if Gemini CLI is available."""
        try:
            result = subprocess.run(
                ["gemini", "--help"], capture_output=True, timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def _review_changed_files(self):
        """Review only changed files."""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode == 0:
                changed_files = [
                    f
                    for f in result.stdout.split("\n")
                    if f.strip().endswith(".py")
                    and Path(self.project_root / f.strip()).exists()
                ]

                if changed_files:
                    console.print(f"📝 Found {len(changed_files)} changed Python files")
                    for file_path in changed_files[:3]:  # Limit to 3 files
                        self._review_single_file(self.project_root / file_path)
                else:
                    console.print("ℹ️ No changed Python files found")

        except Exception as e:
            console.print(f"❌ Error getting changed files: {e}")

    def _review_single_file(self, file_path: Path):
        """Review a single file with Gemini."""
        console.print(f"🔍 Reviewing: {file_path.name}")

        try:
            content = file_path.read_text()

            prompt = f"""Review this Python code for quality and best practices:

File: {file_path.name}

```python
{content}
```

Provide:
1. Overall quality rating (EXCELLENT/GOOD/NEEDS_WORK/POOR)
2. Top 3 specific improvements
3. Any critical issues
4. Code style observations
"""

            result = subprocess.run(
                ["gemini", "-m", "gemini-2.5-flash", "-p", prompt],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                console.print(
                    Panel(
                        result.stdout, title=f"Review: {file_path.name}", style="blue"
                    )
                )
            else:
                console.print(f"❌ Review failed: {result.stderr}")

        except Exception as e:
            console.print(f"❌ Error reviewing {file_path.name}: {e}")

    def _review_all_files(self):
        """Review all Python files (limited)."""
        python_files = [
            f for f in self.project_root.rglob("*.py") if not is_path_ignored(f)
        ]

        console.print(f"📚 Found {len(python_files)} Python files")
        console.print("⚠️ Limiting to first 3 files to conserve API credits")

        for file_path in python_files[:3]:
            self._review_single_file(file_path)
            time.sleep(1)  # Rate limiting

    def _review_with_focus(self, focus_areas: list[str]):
        """Review files with specific focus areas."""
        python_files = [
            f for f in self.project_root.rglob("*.py") if not is_path_ignored(f)
        ]

        console.print(f"🎯 Focused review on: {', '.join(focus_areas)}")
        console.print(f"📚 Reviewing {min(len(python_files), 2)} files")

        for file_path in python_files[:2]:  # Limit to 2 files for focused review
            console.print(f"🔍 Reviewing: {file_path.name}")

            try:
                content = file_path.read_text()

                prompt = f"""Review this Python code with focus on: {', '.join(focus_areas)}

File: {file_path.name}

```python
{content}
```

Specifically analyze:
{chr(10).join(f'- {area}' for area in focus_areas)}

Provide detailed assessment and recommendations for the focus areas.
"""

                result = subprocess.run(
                    ["gemini", "-m", "gemini-2.5-flash", "-p", prompt],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    console.print(
                        Panel(
                            result.stdout,
                            title=f"Focused Review: {file_path.name}",
                            style="blue",
                        )
                    )

            except Exception as e:
                console.print(f"❌ Error in focused review: {e}")

            time.sleep(1)  # Rate limiting

    def benchmark_workflow(self) -> dict:
        """Run performance benchmarking workflow."""
        console.print(Panel.fit("📈 Performance Benchmarking", style="bold yellow"))

        benchmarks = {}

        # Test scenarios for benchmarking
        test_scenarios = [
            "Security incident with multiple threat vectors",
            "Performance degradation across microservices",
            "DevOps pipeline failure analysis",
        ]

        for i, scenario in enumerate(test_scenarios, 1):
            console.print(f"🎯 Benchmark {i}/{len(test_scenarios)}: {scenario[:50]}...")

            start_time = time.time()
            success, stdout, stderr = self.run_command_with_output(
                ["uv", "run", "python", "orchestra_cli.py", "analyze", scenario],
                f"Benchmark scenario {i}",
            )
            end_time = time.time()

            benchmarks[f"scenario_{i}"] = {
                "success": success,
                "duration": end_time - start_time,
                "scenario": scenario,
                "output_length": len(stdout) if stdout else 0,
            }

        # Display benchmark results
        table = Table(show_header=True, header_style="bold yellow")
        table.add_column("Scenario", style="cyan")
        table.add_column("Duration (s)", style="green")
        table.add_column("Status", style="bold")
        table.add_column("Output Size", style="white")

        for _bench_name, result in benchmarks.items():
            status = "✅ OK" if result["success"] else "❌ FAIL"
            table.add_row(
                result["scenario"][:30] + "...",
                f"{result['duration']:.2f}",
                status,
                str(result["output_length"]),
            )

        console.print(table)

        avg_duration = sum(b["duration"] for b in benchmarks.values()) / len(benchmarks)
        console.print(f"\n📊 Average analysis time: {avg_duration:.2f} seconds")

        return benchmarks


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

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    automator = WorkflowAutomator(project_root)

    try:
        if args.workflow == "interactive":
            automator.interactive_workflow()
        elif args.workflow == "health":
            checks = automator.health_checker.health_check_workflow()
            automator.health_checker.display_health_results(checks)
        elif args.workflow == "demo":
            automator.demo_runner.demo_workflow()
        elif args.workflow == "test":
            automator.dev_workflow.test_workflow(args.test_type)
        elif args.workflow == "web":
            automator.dev_workflow.web_development_workflow(args.port)
        elif args.workflow == "cicd":
            automator.dev_workflow.ci_cd_workflow()
        elif args.workflow == "deploy-prep":
            automator.dev_workflow.deployment_prep_workflow()
        elif args.workflow == "benchmark":
            automator.dev_workflow.benchmark_workflow()

    except KeyboardInterrupt:
        console.print("\n❌ Workflow cancelled by user")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n❌ Workflow failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
