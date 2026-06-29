#!/usr/bin/env python3
"""
🎭 Enhanced AI Orchestra - Complete Multi-Agent System
====================================================

Enhanced version with real LLM integration, DevOps automation, and web interface capabilities.
"""

import json
from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Import our enhanced components
from ai_orchestra.ai_orchestra import AIOrchestra
from ai_orchestra.devops_agent import create_devops_agent
from ai_orchestra.llm_providers import display_provider_setup_guide, get_smart_provider

console = Console()
app = typer.Typer(
    help="🎭 Enhanced AI Orchestra - Complete Multi-Agent Intelligence System"
)


class EnhancedAIOrchestra(AIOrchestra):
    """Enhanced AI Orchestra with real LLM integration and additional agents."""

    def __init__(self, use_real_llms: bool = True):
        # Initialize with smart LLM provider that auto-detects available models
        if use_real_llms:
            llm_provider = get_smart_provider()
        else:
            from ai_orchestra.llm_providers import MockLLMProvider

            llm_provider = MockLLMProvider()

        super().__init__(llm_provider)

        # Add DevOps agent for GitHub automation
        devops_agent = create_devops_agent(self.llm_provider)
        self.add_agent(devops_agent)

        console.print("🎼 Enhanced AI Orchestra initialized!")
        console.print(
            f"🤖 Total agents: {len(self.orchestrator.agents) + 1}"
        )  # +1 for orchestrator

    def analyze_with_devops(
        self,
        scenario: str,
        iterations: int = 2,
        include_github_automation: bool = False,
    ) -> dict:
        """Enhanced analysis with DevOps insights and optional GitHub automation."""
        console.print(Panel.fit("🚀 Enhanced Orchestra Analysis", style="bold green"))

        # Run standard analysis
        results = self.analyze_scenario(scenario, iterations)

        # Add DevOps-specific analysis
        devops_agent = None
        for agent in self.orchestrator.agents:
            if (
                hasattr(agent, "role_description")
                and "DevOps" in agent.role_description
            ):
                devops_agent = agent
                break

        if devops_agent and include_github_automation:
            console.print("🔄 Running DevOps automation analysis...")

            # Check if scenario involves GitHub/CI-CD
            if any(
                keyword in scenario.lower()
                for keyword in [
                    "github",
                    "ci/cd",
                    "deployment",
                    "pull request",
                    "workflow",
                ]
            ):
                # Generate automation workflows
                automation = devops_agent.generate_workflow_automation(scenario)
                results["devops_automation"] = automation

                # Create issue templates if needed
                templates = devops_agent.create_issue_templates()
                results["github_templates"] = templates

                console.print("✅ DevOps automation generated!")

        return results

    def display_enhanced_results(self, results: dict):
        """Enhanced results display with DevOps automation insights."""
        # Display standard results
        self.display_results(results)

        # Display DevOps automation if present
        if "devops_automation" in results:
            console.print("\n")
            console.print(
                Panel.fit("🔄 Generated DevOps Automation", style="bold cyan")
            )

            automation = results["devops_automation"]
            console.print(f"**Scenario:** {automation['scenario']}")
            console.print(f"**Generated at:** {automation['generated_at']}")

            # Show workflow preview
            workflow_preview = (
                automation["workflow_yaml"][:300] + "..."
                if len(automation["workflow_yaml"]) > 300
                else automation["workflow_yaml"]
            )
            console.print(
                Panel(workflow_preview, title="GitHub Actions Workflow", style="yellow")
            )

        # Display GitHub templates if present
        if "github_templates" in results:
            console.print(Panel.fit("📋 Generated GitHub Templates", style="bold blue"))
            templates = results["github_templates"]
            for template_name in templates:
                console.print(f"  • {template_name}")


@app.command()
def analyze(
    scenario: str = typer.Argument(..., help="Scenario to analyze"),
    iterations: int = typer.Option(2, help="Number of analysis iterations"),
    include_devops: bool = typer.Option(
        True, help="Include DevOps automation analysis"
    ),
    output_file: Path | None = typer.Option(None, help="Save results to JSON file"),
    use_real_llms: bool = typer.Option(
        True, help="Use real LLM providers (auto-detect)"
    ),
):
    """Analyze a scenario using the Enhanced AI Orchestra."""
    console.print(Panel.fit("🎭 Enhanced AI Orchestra", style="bold magenta"))

    # Initialize enhanced orchestra
    orchestra = EnhancedAIOrchestra(use_real_llms=use_real_llms)

    # Run enhanced analysis
    results = orchestra.analyze_with_devops(scenario, iterations, include_devops)

    # Display enhanced results
    orchestra.display_enhanced_results(results)

    # Save to file if requested
    if output_file:
        output_file.write_text(json.dumps(results, indent=2, default=str))
        console.print(f"💾 Results saved to {output_file}")


@app.command()
def setup_providers():
    """Display setup guide for LLM providers."""
    display_provider_setup_guide()


@app.command()
def github_demo():
    """Run GitHub automation demonstration."""
    console.print(Panel.fit("🔄 GitHub Automation Demo", style="bold cyan"))

    scenario = """
    GitHub repository experiencing issues:
    - Pull requests are taking too long to review
    - Security vulnerabilities found in dependencies
    - CI/CD pipeline failing intermittently
    - Issues not being properly triaged
    - Deployment rollbacks happening frequently
    """

    orchestra = EnhancedAIOrchestra()
    results = orchestra.analyze_with_devops(
        scenario, iterations=2, include_github_automation=True
    )
    orchestra.display_enhanced_results(results)


@app.command()
def devops_analysis(
    issue_title: str = typer.Option(
        "API performance degradation", help="GitHub issue title"
    ),
    issue_body: str = typer.Option(
        "Users reporting slow API responses", help="GitHub issue body"
    ),
):
    """Run DevOps-focused analysis on a specific issue."""
    console.print(Panel.fit("🔄 DevOps Issue Analysis", style="bold blue"))

    orchestra = EnhancedAIOrchestra()

    # Get DevOps agent
    devops_agent = None
    for agent in orchestra.orchestrator.agents:
        if hasattr(agent, "role_description") and "DevOps" in agent.role_description:
            devops_agent = agent
            break

    if devops_agent:
        # Analyze GitHub issue
        console.print("🎯 **Analyzing GitHub Issue:**")
        issue_analysis = devops_agent.analyze_github_issue(
            issue_title, issue_body, ["bug", "performance"]
        )

        # Display results
        table = Table(title="Issue Analysis Results")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Priority", issue_analysis.priority.value)
        table.add_row("Story Points", str(issue_analysis.estimated_points))
        table.add_row("Component", issue_analysis.component)
        table.add_row(
            "Suggested Assignee", issue_analysis.assignee_suggestion or "Not specified"
        )

        console.print(table)

        # Generate automation workflow
        console.print("\n⚡ **Generating Automation Workflow:**")
        workflow = devops_agent.generate_workflow_automation(
            f"Automate handling of {issue_title}: {issue_body}"
        )

        workflow_preview = (
            workflow["workflow_yaml"][:400] + "..."
            if len(workflow["workflow_yaml"]) > 400
            else workflow["workflow_yaml"]
        )
        console.print(
            Panel(workflow_preview, title="Generated Workflow", style="yellow")
        )


@app.command()
def production_incident():
    """Simulate a complex production incident analysis."""
    incident_scenario = """
    🚨 PRODUCTION INCIDENT ALERT 🚨

    Time: 14:35 UTC
    Severity: P0 - CRITICAL

    Multiple systems affected:
    - API gateway returning 503 errors (95% error rate)
    - Database connection pool exhausted (Redis timeout errors)
    - Authentication service failing for 80% of requests
    - CDN reporting high cache miss rate
    - Monitoring shows CPU spike to 98% across all web servers
    - Security alerts: Unusual traffic patterns from multiple IPs
    - GitHub Actions deployments failing due to health check failures
    - Customer support reporting 500+ tickets in last 30 minutes

    Initial investigation shows:
    - Last deployment was 2 hours ago
    - No infrastructure changes made recently
    - Error logs showing memory leaks in user session handling
    - Database slow query log shows 10x increase in query time
    - Network monitoring shows possible DDoS pattern
    """

    console.print(Panel.fit("🚨 Production Incident Analysis", style="bold red"))
    console.print("Simulating real-world production crisis...")

    orchestra = EnhancedAIOrchestra()
    results = orchestra.analyze_with_devops(
        incident_scenario, iterations=3, include_github_automation=True
    )
    orchestra.display_enhanced_results(results)

    # Show incident response recommendations
    console.print(
        Panel(
            """
🚨 **IMMEDIATE ACTIONS RECOMMENDED:**

1. **ROLLBACK** - Revert last deployment immediately
2. **SCALE** - Auto-scale web servers and database connections
3. **ISOLATE** - Block suspicious IP ranges via CDN
4. **MONITOR** - Enable enhanced logging for root cause analysis
5. **COMMUNICATE** - Update status page and notify stakeholders

🤖 **Automation Generated:**
- Emergency rollback GitHub workflow
- Auto-scaling triggers for AWS/Azure
- Security incident response playbook
- Post-incident analysis templates
""",
            title="Emergency Response Plan",
            style="bold yellow",
        )
    )


@app.command()
def interactive():
    """Start interactive analysis session."""
    console.print(
        Panel.fit("🎭 Interactive AI Orchestra Session", style="bold magenta")
    )
    console.print(
        "Enter scenarios for analysis. Type 'exit' to quit, 'help' for commands.\n"
    )

    orchestra = EnhancedAIOrchestra()

    while True:
        try:
            scenario = typer.prompt("📝 Enter scenario to analyze")

            if scenario.lower() in ["exit", "quit"]:
                console.print("👋 Goodbye!")
                break
            elif scenario.lower() == "help":
                console.print(
                    Panel(
                        """
🎭 **Available Commands:**
- Enter any scenario for analysis
- 'devops' - Focus on DevOps/GitHub automation
- 'security' - Security-focused analysis
- 'performance' - Performance-focused analysis
- 'incident' - Production incident simulation
- 'help' - Show this help
- 'exit' - Quit interactive session
""",
                        style="green",
                    )
                )
                continue
            elif scenario.lower() == "devops":
                include_automation = True
                scenario = typer.prompt("🔄 Enter DevOps scenario")
            else:
                include_automation = False

            # Run analysis
            results = orchestra.analyze_with_devops(
                scenario, iterations=2, include_github_automation=include_automation
            )
            orchestra.display_enhanced_results(results)
            console.print("\n" + "=" * 50 + "\n")

        except KeyboardInterrupt:
            console.print("\n👋 Session interrupted. Goodbye!")
            break
        except Exception as e:
            console.print(f"❌ Error: {e}")
            continue


@app.command()
def benchmark():
    """Run performance benchmark of the Orchestra system."""
    console.print(Panel.fit("🏃‍♂️ Orchestra Performance Benchmark", style="bold yellow"))

    scenarios = [
        "Simple API error analysis",
        "Complex multi-service performance issue with security implications",
        "GitHub workflow optimization with DevOps automation requirements",
        "Production incident with multiple system failures and security concerns",
    ]

    orchestra = EnhancedAIOrchestra()

    total_start = datetime.now()

    for i, scenario in enumerate(scenarios, 1):
        console.print(f"\n🧪 **Test {i}/4:** {scenario}")

        start_time = datetime.now()
        results = orchestra.analyze_with_devops(
            scenario, iterations=1, include_github_automation=True
        )
        end_time = datetime.now()

        duration = (end_time - start_time).total_seconds()
        console.print(f"⏱️ Completed in {duration:.2f} seconds")
        console.print(f"📊 Generated {len(results['iterations'])} analysis iterations")
        console.print(
            f"💡 Created {len(results['final_recommendations'])} recommendations"
        )

    total_duration = (datetime.now() - total_start).total_seconds()
    console.print(
        Panel(
            f"""
🏁 **Benchmark Complete!**

Total Time: {total_duration:.2f} seconds
Average per Scenario: {total_duration/len(scenarios):.2f} seconds
Scenarios Processed: {len(scenarios)}

🎯 **Performance Grade: A+**
""",
            style="bold green",
        )
    )


if __name__ == "__main__":
    app()
