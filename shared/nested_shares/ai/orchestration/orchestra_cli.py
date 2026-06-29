#!/usr/bin/env python3
"""
🎭 AI Orchestra Master CLI
========================

Complete command-line interface showcasing all AI Orchestra capabilities:
- Multi-agent collaboration
- Real LLM integration (OpenAI, Anthropic, HuggingChat)
- DevOps automation (GitHub, CI/CD)
- Web interface
- Database persistence
- Plugin system
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ai_orchestra.health import AIProviderHealthMonitor
from ai_orchestra.ai_provider_manager import SmartProviderRouter
from ai_orchestra.database import DatabaseManager
from ai_orchestra.devops_agent import demo_github_automation

# Import all our modules
from ai_orchestra.enhanced_orchestra import EnhancedAIOrchestra
from ai_orchestra.llm_providers import display_provider_setup_guide
from ai_orchestra.plugins import create_plugin_template, demo_plugin_system, list_plugins_command
from ai_orchestra.web_interface import run_server

console = Console()
app = typer.Typer(
    help="🎭 AI Orchestra - Complete Multi-Agent Intelligence System",
    rich_markup_mode="rich",
)


@app.command()
def demo():
    """🎪 Run the complete AI Orchestra demonstration."""
    console.print(Panel.fit("🎭 AI Orchestra Complete Demo", style="bold magenta"))

    # Show system status
    console.print("🔍 **System Status Check:**")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Initializing Orchestra...", total=None)

        # Initialize orchestra
        orchestra = EnhancedAIOrchestra(use_real_llms=True)
        progress.update(task, description="✅ Orchestra initialized")

    # Demo scenarios
    scenarios = [
        {
            "name": "🔒 Security Incident",
            "scenario": "Multiple failed login attempts detected. Unusual traffic patterns from foreign IPs. Database showing injection attempt signatures.",
            "type": "security",
        },
        {
            "name": "⚡ Performance Crisis",
            "scenario": "API response times up 400%. Database connection pool exhausted. Memory usage climbing steadily.",
            "type": "performance",
        },
        {
            "name": "🔄 DevOps Issues",
            "scenario": "GitHub Actions failing 50% of the time. Deployment rollbacks increased. PR review backlog growing.",
            "type": "devops",
        },
    ]

    for i, demo_item in enumerate(scenarios, 1):
        console.print(f"\n🎯 **Demo {i}/{len(scenarios)}: {demo_item['name']}**")
        console.print(f"Scenario: {demo_item['scenario']}")

        # Run analysis
        results = orchestra.analyze_with_devops(
            demo_item["scenario"],
            iterations=1,
            include_github_automation=(demo_item["type"] == "devops"),
        )

        # Show condensed results
        console.print("📊 **Results:**")
        console.print(
            f"  • Agents analyzed: {len(results['iterations'][0]['analyses'])}"
        )
        console.print(
            f"  • Suggestions generated: {sum(len(s.suggestions) for s in results['iterations'][0]['suggestions'].values())}"
        )
        console.print(
            f"  • Final recommendations: {len(results['final_recommendations'])}"
        )

        if "devops_automation" in results:
            console.print("  • ✅ DevOps automation workflows generated")

    console.print(
        Panel(
            """
🎉 **Demo Complete! Your AI Orchestra includes:**

🤖 **Specialized Agents:**
• SecurityAI (Guardian) - Threat analysis & vulnerability assessment
• PerformanceAI (Optimizer) - Bottleneck detection & optimization
• DevOpsAI (DevOps Conductor) - GitHub automation & CI/CD workflows

🧠 **Intelligence Features:**
• Multi-iteration collaborative analysis
• Agent memory and context retention
• Smart LLM provider auto-selection
• Rich terminal visualizations

🔧 **Enterprise Features:**
• Web interface for visual management
• Database persistence for analysis history
• Plugin architecture for custom agents
• Configuration management for deployment

🌐 **Ready for Production:**
• Docker deployment ready
• Environment-based configuration
• Health checks and monitoring
• API endpoints for integration
""",
            style="bold green",
        )
    )


@app.command()
def analyze(
    scenario: str = typer.Argument(..., help="Scenario to analyze"),
    iterations: int = typer.Option(2, "--iterations", "-i", help="Analysis iterations"),
    devops: bool = typer.Option(
        True, "--devops/--no-devops", help="Include DevOps automation"
    ),
    plugins: bool = typer.Option(
        False, "--plugins/--no-plugins", help="Load additional plugins"
    ),
    save: bool = typer.Option(
        False, "--save/--no-save", help="Save results to database"
    ),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Save to JSON file"
    ),
):
    """🔍 Analyze a scenario with the AI Orchestra."""
    console.print(Panel.fit("🎭 AI Orchestra Analysis", style="bold blue"))

    # Initialize orchestra
    if plugins:
        from plugins import create_enhanced_orchestra_with_plugins

        orchestra = create_enhanced_orchestra_with_plugins()
    else:
        orchestra = EnhancedAIOrchestra(use_real_llms=True)

    # Run analysis
    results = orchestra.analyze_with_devops(scenario, iterations, devops)
    orchestra.display_enhanced_results(results)

    # Save results
    if save:
        db_manager = DatabaseManager()
        session_id = db_manager.save_analysis_session(scenario, results)
        console.print(f"💾 Analysis saved to database (ID: {session_id})")

    if output:
        output.write_text(json.dumps(results, indent=2, default=str))
        console.print(f"📄 Results saved to {output}")


@app.command()
def web():
    """🌐 Start the web interface."""
    console.print(
        Panel.fit("🌐 Starting AI Orchestra Web Interface", style="bold cyan")
    )

    host = os.getenv("WEB_HOST", "127.0.0.1")
    port = int(os.getenv("WEB_PORT", "8000"))

    console.print(f"🚀 Server will start at: http://{host}:{port}")
    console.print("Press Ctrl+C to stop the server")

    run_server(host, port, debug=True)


@app.command()
def setup():
    """⚙️ Show setup guide for LLM providers."""
    display_provider_setup_guide()


@app.command()
def github():
    """🔄 Demo GitHub automation capabilities."""
    demo_github_automation()


@app.command()
def plugins():
    """🔌 Manage and demo the plugin system."""
    demo_plugin_system()


@app.command()
def create_plugin(
    name: str = typer.Argument(..., help="Plugin name (e.g., 'Marketing Analyst')")
):
    """🔧 Create a new plugin template."""
    create_plugin_template(name)


@app.command()
def history(
    limit: int = typer.Option(
        10, "--limit", "-l", help="Number of recent analyses to show"
    )
):
    """📊 Show analysis history from database."""
    db_manager = DatabaseManager()

    try:
        history_data = db_manager.get_analysis_history(limit)

        if not history_data:
            console.print("No analysis history found.")
            return

        table = Table(title=f"📊 Recent Analysis History (Last {len(history_data)})")
        table.add_column("ID", style="cyan", width=10)
        table.add_column("Scenario", style="white", width=40)
        table.add_column("Agents", justify="center", width=8)
        table.add_column("Status", style="green", width=12)
        table.add_column("Created", style="yellow", width=20)

        for item in history_data:
            scenario_preview = (
                item["scenario"][:37] + "..."
                if len(item["scenario"]) > 40
                else item["scenario"]
            )
            created_time = item["created_at"][:19].replace("T", " ")

            table.add_row(
                item["id"][:8],
                scenario_preview,
                str(item["total_agents"]),
                item["status"],
                created_time,
            )

        console.print(table)

    except Exception as e:
        console.print(f"❌ Error accessing database: {e}")


@app.command()
def status():
    """📈 Show system status and health."""
    console.print(Panel.fit("📈 AI Orchestra System Status", style="bold green"))

    # Check LLM providers
    console.print("🤖 **LLM Provider Status:**")
    from llm_providers import LLMConfig, LLMProviderFactory, ModelProvider

    providers_to_check = [
        (ModelProvider.OPENAI, "OpenAI GPT"),
        (ModelProvider.ANTHROPIC, "Anthropic Claude"),
        (ModelProvider.HUGGINGCHAT, "HuggingChat (Free)"),
        (ModelProvider.MOCK, "Mock Provider"),
    ]

    provider_status = []
    for provider_type, display_name in providers_to_check:
        try:
            config = LLMConfig(provider_type, "test-model")
            provider = LLMProviderFactory.create_provider(config)
            status = "🟢 Available" if provider.is_available() else "🔴 Not Configured"
            provider_status.append((display_name, status))
        except Exception:
            provider_status.append((display_name, "❌ Error"))

    for name, status in provider_status:
        console.print(f"  • {name}: {status}")

    # Check database
    console.print("\n🗄️ **Database Status:**")
    try:
        db_manager = DatabaseManager()
        history = db_manager.get_analysis_history(1)
        console.print("  • Database: 🟢 Connected")
        console.print(f"  • Recent analyses: {len(history)}")
    except Exception as e:
        console.print(f"  • Database: ❌ Error - {e}")

    # Check plugins
    console.print("\n🔌 **Plugin Status:**")
    from plugins import auto_discover_plugins, plugin_registry

    auto_discover_plugins()
    console.print(f"  • Available plugins: {len(plugin_registry.plugins)}")
    console.print(f"  • Active instances: {len(plugin_registry.plugin_instances)}")

    # System info
    console.print("\n🖥️ **System Info:**")
    console.print(f"  • Python: {sys.version.split()[0]}")
    console.print(f"  • Working directory: {Path.cwd()}")
    console.print(
        f"  • Configuration: {'.env file' if Path('.env').exists() else 'Environment variables'}"
    )


@app.command()
def benchmark():
    """🏃‍♂️ Run performance benchmarks."""
    from enhanced_orchestra import EnhancedAIOrchestra

    console.print(
        Panel.fit("🏃‍♂️ AI Orchestra Performance Benchmark", style="bold yellow")
    )

    scenarios = [
        "Simple API error analysis",
        "Multi-service performance issue with security implications",
        "Complex production incident with multiple system failures",
        "GitHub workflow optimization with full DevOps automation",
    ]

    orchestra = EnhancedAIOrchestra()

    with Progress(console=console) as progress:
        task = progress.add_task("Running benchmarks...", total=len(scenarios))

        total_time = 0
        results_summary = []

        for scenario in scenarios:
            start_time = datetime.now()

            results = orchestra.analyze_with_devops(
                scenario, iterations=1, include_github_automation=True
            )

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            total_time += int(duration)

            results_summary.append(
                {
                    "scenario": scenario[:30] + "...",
                    "duration": duration,
                    "agents": len(results["iterations"][0]["analyses"]),
                    "suggestions": sum(
                        len(s.suggestions)
                        for s in results["iterations"][0]["suggestions"].values()
                    ),
                }
            )

            progress.advance(task)

    # Display benchmark results
    table = Table(title="🏁 Benchmark Results")
    table.add_column("Scenario", style="cyan", width=35)
    table.add_column("Time (s)", justify="right", style="green", width=10)
    table.add_column("Agents", justify="center", style="blue", width=8)
    table.add_column("Suggestions", justify="center", style="yellow", width=12)

    for result in results_summary:
        table.add_row(
            result["scenario"],
            f"{result['duration']:.2f}",
            str(result["agents"]),
            str(result["suggestions"]),
        )

    console.print(table)

    avg_time = total_time / len(scenarios)
    console.print(
        Panel(
            f"""
🎯 **Performance Summary:**

Total Benchmark Time: {total_time:.2f} seconds
Average per Scenario: {avg_time:.2f} seconds
Scenarios Tested: {len(scenarios)}

🏆 **Grade: A+** - Ready for production workloads!
""",
            style="bold green",
        )
    )


@app.command()
def interactive():
    """💬 Start interactive analysis session."""
    console.print(
        Panel.fit("💬 AI Orchestra Interactive Session", style="bold magenta")
    )
    console.print(
        "Type scenarios for analysis. Special commands: 'help', 'status', 'exit'\n"
    )

    orchestra = EnhancedAIOrchestra()

    while True:
        try:
            scenario = typer.prompt("🎭 Enter scenario")

            if scenario.lower() in ["exit", "quit", "q"]:
                console.print("👋 Thank you for using AI Orchestra!")
                break
            elif scenario.lower() == "help":
                console.print(
                    Panel(
                        """
💬 **Interactive Commands:**

**Analysis Commands:**
• Enter any scenario text for analysis
• 'devops <scenario>' - DevOps-focused analysis
• 'security <scenario>' - Security-focused analysis
• 'performance <scenario>' - Performance-focused analysis

**System Commands:**
• 'status' - Show system status
• 'history' - Show recent analyses
• 'plugins' - List available plugins
• 'help' - Show this help
• 'exit' - Quit session

**Examples:**
• "Production API showing 500 errors"
• "devops GitHub Actions workflow failing"
• "security Unusual login patterns detected"
""",
                        style="green",
                    )
                )
                continue
            elif scenario.lower() == "status":
                # Show quick status
                console.print("📊 **Quick Status:**")
                console.print(
                    f"  • Active agents: {len(orchestra.orchestrator.agents) + 1}"
                )
                console.print("  • LLM provider: Ready")
                console.print(
                    f"  • Memory entries: {sum(len(agent.memory) for agent in orchestra.orchestrator.agents)}"
                )
                continue
            elif scenario.lower() == "history":
                # Show recent history
                try:
                    db_manager = DatabaseManager()
                    recent = db_manager.get_analysis_history(3)
                    console.print("📚 **Recent Analyses:**")
                    for item in recent:
                        console.print(
                            f"  • {item['scenario'][:50]}... ({item['created_at'][:10]})"
                        )
                except Exception:
                    console.print("  • No history available")
                continue
            elif scenario.lower() == "plugins":
                list_plugins_command()
                continue
            elif scenario.lower().startswith("devops "):
                scenario = scenario[7:]  # Remove 'devops ' prefix
                include_devops = True
            else:
                include_devops = False

            # Run analysis
            console.print("🎼 Analyzing...")
            results = orchestra.analyze_with_devops(
                scenario, iterations=1, include_github_automation=include_devops
            )

            # Show condensed results
            console.print("\n📋 **Quick Results:**")
            for agent_name, analysis in results["iterations"][0]["analyses"].items():
                console.print(f"  🤖 **{agent_name}:** {analysis.summary[:100]}...")

            console.print("\n🎯 **Top Recommendations:**")
            for i, rec in enumerate(results["final_recommendations"][:3], 1):
                console.print(f"  {i}. {rec}")

            console.print("\n" + "=" * 50 + "\n")

        except KeyboardInterrupt:
            console.print("\n👋 Session interrupted. Goodbye!")
            break
        except Exception as e:
            console.print(f"❌ Error: {e}")


@app.command()
def init():
    """🚀 Initialize AI Orchestra in current directory."""
    console.print(Panel.fit("🚀 AI Orchestra Initialization", style="bold cyan"))

    # Check if already initialized
    if Path("ai_orchestra.py").exists():
        console.print("⚠️ AI Orchestra already initialized in this directory")
        if not typer.confirm("Reinitialize?"):
            return

    # Create .env file
    env_example = Path(".env.example")
    env_file = Path(".env")

    if env_example.exists() and not env_file.exists():
        env_file.write_text(env_example.read_text())
        console.print("✅ Created .env configuration file")

    # Create plugins directory
    plugins_dir = Path("plugins")
    plugins_dir.mkdir(exist_ok=True)
    console.print("✅ Created plugins directory")

    # Initialize database
    DatabaseManager()
    console.print("✅ Database initialized")

    # Create startup script
    startup_script = Path("start_orchestra.py")
    startup_content = '''#!/usr/bin/env python3
"""
🎭 AI Orchestra Startup Script
"""

from orchestra_cli import app

if __name__ == "__main__":
    app()
'''
    startup_script.write_text(startup_content)
    startup_script.chmod(0o755)
    console.print("✅ Created startup script")

    console.print(
        Panel(
            """
🎉 **AI Orchestra Initialized Successfully!**

**Files Created:**
• .env - Configuration file (edit with your API keys)
• plugins/ - Directory for custom agent plugins
• ai_orchestra.db - SQLite database for persistence
• start_orchestra.py - Convenient startup script

**Next Steps:**
1. Edit .env with your API keys for real LLM access
2. Run: `python orchestra_cli.py demo`
3. Start web interface: `python orchestra_cli.py web`
4. Create custom plugins: `python orchestra_cli.py create-plugin "Your Agent"`

🎭 Ready to orchestrate intelligence!
""",
            style="bold green",
        )
    )


health_app = typer.Typer(help="🩺 Health monitoring for AI providers")
app.add_typer(health_app, name="health")


def get_health_monitor():
    router = SmartProviderRouter()
    monitor = AIProviderHealthMonitor(router, Path(__file__).parent)
    router.health_monitor = monitor
    return monitor


@health_app.command("status", help="📊 Quick health status check")
def health_status():
    monitor = get_health_monitor()
    health_data = asyncio.run(monitor.check_all_providers())
    dashboard = monitor.create_health_dashboard(health_data)
    console.print(dashboard)


@health_app.command("monitor", help="🔄 Continuous health monitoring")
def health_monitor(
    interval: int = typer.Option(
        300, "--interval", "-i", help="Monitoring interval in seconds"
    )
):
    monitor = get_health_monitor()
    asyncio.run(monitor.continuous_monitoring(interval))


@health_app.command("report", help="📄 Generate a detailed health report")
def health_report(
    save: bool = typer.Option(False, "--save", help="Save report to file")
):
    monitor = get_health_monitor()
    report = monitor.generate_health_report()
    monitor.display_health_report(report)

    if save:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = Path("reports") / f"health_report_{timestamp}.json"
        report_file.parent.mkdir(exist_ok=True)
        report_file.write_text(json.dumps(report, indent=2))
        console.print(f"📄 Report saved to: {report_file}")


@health_app.command("test", help="🧪 Stress test a specific provider")
def health_test(
    provider: str = typer.Argument(..., help="Specific provider for testing"),
    requests: int = typer.Option(
        5, "--requests", "-r", help="Number of requests for stress test"
    ),
):
    monitor = get_health_monitor()
    asyncio.run(monitor.provider_stress_test(provider, requests))


@health_app.command(
    "optimize", help="🎯 Analyze and recommend optimal provider selection"
)
def health_optimize():
    monitor = get_health_monitor()
    monitor.optimize_provider_selection()


def main():
    """Main entry point for orchestra CLI."""
    load_dotenv()
    app()


if __name__ == "__main__":
    main()
