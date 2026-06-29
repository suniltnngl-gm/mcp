#!/usr/bin/env python3
"""
🎭 AI Orchestra - Multi-Agent Collaborative Intelligence System
==============================================================

A sophisticated framework for orchestrating multiple AI agents to solve complex problems
through collaborative analysis, suggestion generation, and iterative feedback loops.

Features:
- 🤖 Specialized AI agents (Security, Performance, General)
- 🎼 Orchestrator for managing multi-agent workflows
- 🧠 Memory system for context retention
- 🔄 Round-robin collaboration patterns
- 📊 Rich output formatting and logging
"""

import json
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Protocol

import typer
from pydantic import BaseModel, ConfigDict
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

# Import tracking systems
try:
    from session_tracker import SessionTracker
    from ai_action_tracker import AIActionTracker
    TRACKING_ENABLED = True
except ImportError:
    TRACKING_ENABLED = False

# Configure rich logging
console = Console()
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)],
)
logger = logging.getLogger("ai_orchestra")


class AgentRole(str, Enum):
    """Defines the specialized roles available for AI agents."""

    SECURITY = "Security Analyst"
    PERFORMANCE = "Performance Engineer"
    ORCHESTRATOR = "Orchestrator"
    GENERAL = "General Assistant"


class AnalysisResult(BaseModel):
    """Structured result from AI analysis."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    agent_name: str
    role: AgentRole
    summary: str
    confidence: float = 0.0
    metadata: dict[str, Any] = {}
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class SuggestionSet(BaseModel):
    """Collection of suggestions from an agent."""

    agent_name: str
    suggestions: list[str]
    priority_scores: dict[str, float] = {}
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class LLMProvider(Protocol):
    """Protocol defining the interface for LLM providers."""

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text response from the model."""
        ...


# Import the intelligent provider system
try:
    from llm_providers import SmartLLMProvider

    SMART_PROVIDER_AVAILABLE = True
except ImportError:
    SMART_PROVIDER_AVAILABLE = False


class MockLLMProvider:
    """Mock LLM provider for testing and demonstration."""

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate a mock response based on prompt content."""
        if "security" in prompt.lower():
            return "🔒 Security Analysis: No critical vulnerabilities detected. Recommend implementing additional logging for audit trails."
        elif "performance" in prompt.lower():
            return "⚡ Performance Analysis: Detected potential bottleneck in data processing. Suggest implementing caching layer and optimizing database queries."
        elif "orchestrat" in prompt.lower():
            return "🎼 Orchestration: Successfully coordinating agent collaboration. All systems operating within normal parameters."
        else:
            return f"🤖 Analysis complete. Based on the input: '{prompt[:100]}...', I recommend further investigation and monitoring."


class BaseAI(ABC):
    """Abstract base class for all AI agents."""

    def __init__(self, name: str, llm_provider: LLMProvider, role: AgentRole):
        self.name = name
        self.llm_provider = llm_provider
        self.role = role
        self.memory: list[dict[str, Any]] = []
        self.logger = logging.getLogger(
            f"ai_orchestra.{name.lower().replace(' ', '_')}"
        )

    def add_to_memory(self, message: dict[str, Any]) -> None:
        """Add structured information to agent memory."""
        memory_entry = {
            "timestamp": datetime.now().isoformat(),
            "content": message,
            "agent": self.name,
        }
        self.memory.append(memory_entry)
        self.logger.debug(f"Added to memory: {message}")

    def get_memory_context(self, limit: int = 5) -> str:
        """Get recent memory context as formatted string."""
        recent_memories = self.memory[-limit:] if self.memory else []
        return "\n".join(
            [
                f"[{mem['timestamp']}] {json.dumps(mem['content'])}"
                for mem in recent_memories
            ]
        )

    @abstractmethod
    def analyze(self, data: str) -> AnalysisResult:
        """Analyze input data and return structured results."""

    @abstractmethod
    def suggest(self, analysis_results: dict[str, AnalysisResult]) -> SuggestionSet:
        """Generate suggestions based on analysis results."""

    def provide_feedback(self, suggestions: list[SuggestionSet]) -> dict[str, Any]:
        """Provide feedback on suggestions from other agents."""
        all_suggestions = []
        for suggestion_set in suggestions:
            all_suggestions.extend(suggestion_set.suggestions)

        prompt = f"""As a {self.role.value}, review these suggestions and provide feedback:

Suggestions to review:
{chr(10).join(f'- {s}' for s in all_suggestions)}

Please provide:
1. Overall assessment
2. Potential conflicts or synergies
3. Priority recommendations
4. Risk assessment

Context from recent interactions:
{self.get_memory_context()}
"""

        response = self.llm_provider.generate(prompt)
        feedback = {
            "agent": self.name,
            "critique": response,
            "timestamp": datetime.now().isoformat(),
            "suggestion_count": len(all_suggestions),
        }

        self.add_to_memory({"type": "feedback", "content": feedback})
        return feedback


class SecurityAI(BaseAI):
    """AI agent specialized in security analysis."""

    def __init__(self, name: str, llm_provider: LLMProvider):
        super().__init__(name, llm_provider, AgentRole.SECURITY)

    def analyze(self, data: str) -> AnalysisResult:
        """Perform security-focused analysis."""
        prompt = f"""As a Security Analyst, analyze this data for security threats,
vulnerabilities, and suspicious activity:

{data}

Focus on:
- Authentication/authorization issues
- Data exposure risks
- Suspicious patterns
- Compliance concerns

Previous context:
{self.get_memory_context(3)}
"""

        response = self.llm_provider.generate(prompt)
        result = AnalysisResult(
            agent_name=self.name,
            role=self.role,
            summary=response,
            confidence=0.85,
            metadata={"analysis_type": "security", "data_size": len(data)},
        )

        self.add_to_memory({"type": "analysis", "result": result.model_dump()})
        return result

    def suggest(self, analysis_results: dict[str, AnalysisResult]) -> SuggestionSet:
        """Generate security-focused suggestions."""
        combined_analysis = "\n".join(
            [f"{name}: {result.summary}" for name, result in analysis_results.items()]
        )

        prompt = f"""Based on these analysis results, provide specific security recommendations:

{combined_analysis}

Generate 3-5 actionable security suggestions focusing on:
- Immediate security measures
- Long-term security improvements
- Monitoring and detection enhancements
"""

        response = self.llm_provider.generate(prompt)
        suggestions = [
            s.strip()
            for s in response.split("\n")
            if s.strip() and not s.strip().startswith("#")
        ]

        suggestion_set = SuggestionSet(
            agent_name=self.name,
            suggestions=suggestions[:5],  # Limit to 5 suggestions
            priority_scores=dict.fromkeys(suggestions[:5], 0.8),
        )

        self.add_to_memory(
            {"type": "suggestions", "content": suggestion_set.model_dump()}
        )
        return suggestion_set


class PerformanceAI(BaseAI):
    """AI agent specialized in performance analysis."""

    def __init__(self, name: str, llm_provider: LLMProvider):
        super().__init__(name, llm_provider, AgentRole.PERFORMANCE)

    def analyze(self, data: str) -> AnalysisResult:
        """Perform performance-focused analysis."""
        prompt = f"""As a Performance Engineer, analyze this data for performance issues:

{data}

Focus on:
- Latency and response times
- Resource utilization patterns
- Scalability bottlenecks
- Optimization opportunities

Previous context:
{self.get_memory_context(3)}
"""

        response = self.llm_provider.generate(prompt)
        result = AnalysisResult(
            agent_name=self.name,
            role=self.role,
            summary=response,
            confidence=0.82,
            metadata={"analysis_type": "performance", "data_size": len(data)},
        )

        self.add_to_memory({"type": "analysis", "result": result.model_dump()})
        return result

    def suggest(self, analysis_results: dict[str, AnalysisResult]) -> SuggestionSet:
        """Generate performance-focused suggestions."""
        combined_analysis = "\n".join(
            [f"{name}: {result.summary}" for name, result in analysis_results.items()]
        )

        prompt = f"""Based on these analysis results, provide specific performance recommendations:

{combined_analysis}

Generate 3-5 actionable performance suggestions focusing on:
- Immediate performance wins
- Architectural improvements
- Monitoring and alerting
- Capacity planning
"""

        response = self.llm_provider.generate(prompt)
        suggestions = [
            s.strip()
            for s in response.split("\n")
            if s.strip() and not s.strip().startswith("#")
        ]

        suggestion_set = SuggestionSet(
            agent_name=self.name,
            suggestions=suggestions[:5],
            priority_scores=dict.fromkeys(suggestions[:5], 0.75),
        )

        self.add_to_memory(
            {"type": "suggestions", "content": suggestion_set.model_dump()}
        )
        return suggestion_set


class OrchestratorAI(BaseAI):
    """AI agent responsible for orchestrating multi-agent collaboration."""

    def __init__(self, name: str, llm_provider: LLMProvider):
        super().__init__(name, llm_provider, AgentRole.ORCHESTRATOR)
        self.agents: list[BaseAI] = []

    def register_agent(self, agent: BaseAI) -> None:
        """Register an agent for orchestration."""
        self.agents.append(agent)
        self.logger.info(f"Registered agent: {agent.name} ({agent.role.value})")

    def select_relevant_agents(self, data: str) -> list[BaseAI]:
        """Select relevant agents based on data content."""
        # Simple keyword-based selection (can be enhanced with ML)
        relevant_agents = []
        data_lower = data.lower()

        keywords_to_agents = {
            (
                "security",
                "breach",
                "unauthorized",
                "vulnerability",
                "attack",
            ): AgentRole.SECURITY,
            (
                "performance",
                "slow",
                "latency",
                "cpu",
                "memory",
                "bottleneck",
            ): AgentRole.PERFORMANCE,
        }

        for keywords, role in keywords_to_agents.items():
            if any(keyword in data_lower for keyword in keywords):
                matching_agents = [agent for agent in self.agents if agent.role == role]
                relevant_agents.extend(matching_agents)

        # If no specific matches, include all non-orchestrator agents
        if not relevant_agents:
            relevant_agents = [
                agent for agent in self.agents if agent.role != AgentRole.ORCHESTRATOR
            ]

        return relevant_agents

    def orchestrate_analysis(self, data: str, iterations: int = 2) -> dict[str, Any]:
        """Orchestrate multi-agent analysis with multiple iterations."""
        console.print(
            Panel.fit("🎼 Starting AI Orchestra Analysis", style="bold magenta")
        )

        results = {
            "iterations": [],
            "final_recommendations": [],
            "agent_summaries": {},
            "metadata": {
                "total_agents": len(self.agents),
                "data_size": len(data),
                "timestamp": datetime.now().isoformat(),
            },
        }

        # Select relevant agents
        active_agents = self.select_relevant_agents(data)
        console.print(f"🎯 Selected {len(active_agents)} agents for analysis")

        for iteration in range(iterations):
            console.print(f"\n🔄 Iteration {iteration + 1}/{iterations}")

            iteration_data = {
                "iteration": iteration + 1,
                "analyses": {},
                "suggestions": {},
                "feedback": {},
            }

            # Phase 1: Analysis
            with console.status("[bold green]Running analysis phase..."):
                for agent in active_agents:
                    analysis = agent.analyze(data)
                    iteration_data["analyses"][agent.name] = analysis
                    console.print(f"  ✅ {agent.name} completed analysis")

            # Phase 2: Suggestions
            with console.status("[bold blue]Generating suggestions..."):
                for agent in active_agents:
                    suggestions = agent.suggest(iteration_data["analyses"])
                    iteration_data["suggestions"][agent.name] = suggestions
                    console.print(f"  💡 {agent.name} provided suggestions")

            # Phase 3: Feedback
            with console.status("[bold yellow]Collecting feedback..."):
                all_suggestions = list(iteration_data["suggestions"].values())
                for agent in active_agents:
                    feedback = agent.provide_feedback(all_suggestions)
                    iteration_data["feedback"][agent.name] = feedback
                    console.print(f"  🔍 {agent.name} provided feedback")

            results["iterations"].append(iteration_data)

            # Update data with insights for next iteration
            if iteration < iterations - 1:
                data += f"\n\nPrevious iteration insights:\n{self._summarize_iteration(iteration_data)}"

        # Generate final recommendations
        results["final_recommendations"] = self._generate_final_recommendations(
            results["iterations"]
        )

        self.add_to_memory({"type": "orchestration", "results": results})
        return results

    def _summarize_iteration(self, iteration_data: dict[str, Any]) -> str:
        """Summarize an iteration for context in next iteration."""
        summary_parts = []

        for agent_name, analysis in iteration_data["analyses"].items():
            summary_parts.append(f"{agent_name}: {analysis.summary[:100]}...")

        return "\n".join(summary_parts)

    def _generate_final_recommendations(
        self, iterations: list[dict[str, Any]]
    ) -> list[str]:
        """Generate final consolidated recommendations."""
        all_suggestions = []

        for iteration in iterations:
            for _agent_name, suggestion_set in iteration["suggestions"].items():
                all_suggestions.extend(suggestion_set.suggestions)

        # Simple deduplication and prioritization
        unique_suggestions = list(set(all_suggestions))
        return unique_suggestions[:10]  # Return top 10

    def analyze(self, data: str) -> AnalysisResult:
        """Orchestrator's own analysis capability."""
        prompt = f"""As an Orchestrator, provide a high-level analysis of this situation:

{data}

Focus on:
- Overall system health
- Coordination needs
- Priority assessment
- Resource allocation
"""

        response = self.llm_provider.generate(prompt)
        return AnalysisResult(
            agent_name=self.name, role=self.role, summary=response, confidence=0.90
        )

    def suggest(self, analysis_results: dict[str, AnalysisResult]) -> SuggestionSet:
        """Generate orchestration-level suggestions."""
        suggestions = [
            "Coordinate cross-functional response team",
            "Implement monitoring dashboard",
            "Schedule follow-up analysis session",
            "Document lessons learned",
            "Update response procedures",
        ]

        return SuggestionSet(
            agent_name=self.name,
            suggestions=suggestions,
            priority_scores=dict.fromkeys(suggestions, 0.7),
        )


class AIOrchestra:
    """Main class for managing the AI Orchestra system."""

    def __init__(self, llm_provider: LLMProvider | None = None, enable_tracking: bool = True):
        if llm_provider is None:
            # Try to use SmartLLMProvider if available, otherwise fall back to MockLLMProvider
            if SMART_PROVIDER_AVAILABLE:
                try:
                    from dotenv import load_dotenv

                    load_dotenv()

                    self.llm_provider = SmartLLMProvider()
                    console.print(
                        "🧠 Using Intelligent Provider Strategy", style="green"
                    )
                except Exception as e:
                    console.print(
                        f"⚠️ Smart provider initialization failed: {e}", style="yellow"
                    )
                    console.print("🔄 Falling back to Mock provider", style="yellow")
                    self.llm_provider = MockLLMProvider()
            else:
                console.print(
                    "📝 Using Mock provider (Smart provider not available)",
                    style="cyan",
                )
                self.llm_provider = MockLLMProvider()
        else:
            self.llm_provider = llm_provider

        self.orchestrator = OrchestratorAI("The Conductor", self.llm_provider)
        self.console = console

        # Initialize tracking
        self.tracking_enabled = enable_tracking and TRACKING_ENABLED
        if self.tracking_enabled:
            self.session_tracker = SessionTracker("session_history.jsonl")
            self.action_tracker = AIActionTracker("ai_action_history.jsonl")

        # Initialize default agents
        self._initialize_default_agents()

    def _initialize_default_agents(self):
        """Initialize the default set of AI agents."""
        security_agent = SecurityAI("Guardian", self.llm_provider)
        performance_agent = PerformanceAI("Optimizer", self.llm_provider)

        self.orchestrator.register_agent(security_agent)
        self.orchestrator.register_agent(performance_agent)

    def add_agent(self, agent: BaseAI):
        """Add a custom agent to the orchestra."""
        self.orchestrator.register_agent(agent)

    def analyze_scenario(self, scenario: str, iterations: int = 2) -> dict[str, Any]:
        """Analyze a scenario using the full orchestra."""
        # Track session start
        if self.tracking_enabled:
            self.session_tracker.start_session(f"Orchestra analysis: {scenario[:100]}")
            self.session_tracker.add_thinking(f"Orchestrating {len(self.orchestrator.agents)} agents for {iterations} iterations")
        
        start_time = time.time()
        results = self.orchestrator.orchestrate_analysis(scenario, iterations)
        latency = time.time() - start_time
        
        # Track orchestration action
        if self.tracking_enabled:
            self.action_tracker.log_action(
                action_type="orchestration",
                provider="multi-agent",
                model="ai_orchestra",
                input_tokens=len(scenario.split()) * 2,
                output_tokens=sum(len(str(r).split()) for r in results.get("final_recommendations", [])),
                cost=0.0,  # Would aggregate from individual agent calls
                latency=latency,
                success=True,
                context={
                    "agents": len(self.orchestrator.agents),
                    "iterations": iterations,
                    "recommendations": len(results.get("final_recommendations", []))
                },
                result=f"Completed {iterations} iterations with {len(results.get('final_recommendations', []))} recommendations"
            )
            self.session_tracker.complete_session(f"Orchestra analysis completed: {len(results.get('final_recommendations', []))} recommendations generated")
        
        return results

    def display_results(self, results: dict[str, Any]):
        """Display analysis results in a beautiful format."""
        # Create results tree
        tree = Tree("🎭 AI Orchestra Results")

        # Add metadata
        metadata = results["metadata"]
        tree.add(
            f"📊 Analysis Overview: {metadata['total_agents']} agents, {metadata['data_size']} chars"
        )

        # Add iterations
        for i, iteration in enumerate(results["iterations"], 1):
            iter_branch = tree.add(f"🔄 Iteration {i}")

            # Add analyses
            analysis_branch = iter_branch.add("🧠 Analyses")
            for agent_name, analysis in iteration["analyses"].items():
                analysis_branch.add(
                    f"[bold]{agent_name}[/bold]: {analysis.summary[:80]}..."
                )

            # Add suggestions
            suggestions_branch = iter_branch.add("💡 Suggestions")
            for agent_name, suggestion_set in iteration["suggestions"].items():
                agent_suggestions = suggestions_branch.add(f"[bold]{agent_name}[/bold]")
                for suggestion in suggestion_set.suggestions[:3]:  # Show top 3
                    agent_suggestions.add(f"• {suggestion[:60]}...")

        # Add final recommendations
        recommendations_branch = tree.add("🎯 Final Recommendations")
        for i, rec in enumerate(results["final_recommendations"][:5], 1):
            recommendations_branch.add(f"{i}. {rec}")

        self.console.print(tree)

        # Create summary table
        table = Table(title="Agent Performance Summary", show_header=True)
        table.add_column("Agent", style="cyan", width=15)
        table.add_column("Role", style="green", width=20)
        table.add_column("Analyses", justify="center", width=10)
        table.add_column("Suggestions", justify="center", width=12)

        for iteration in results["iterations"]:
            for agent_name, analysis in iteration["analyses"].items():
                suggestions_count = len(
                    iteration["suggestions"][agent_name].suggestions
                )
                table.add_row(
                    agent_name, analysis.role.value, "✅", str(suggestions_count)
                )
                break  # Only show once per agent

        self.console.print("\n")
        self.console.print(table)


# CLI Interface
app = typer.Typer(help="🎭 AI Orchestra - Multi-Agent Intelligence System")


@app.command()
def analyze(
    scenario: str = typer.Argument(..., help="Scenario to analyze"),
    iterations: int = typer.Option(2, help="Number of analysis iterations"),
    output_file: Path | None = typer.Option(None, help="Save results to JSON file"),
):
    """Analyze a scenario using the AI Orchestra."""
    console.print(Panel.fit("🎭 Welcome to AI Orchestra", style="bold blue"))

    # Initialize orchestra
    orchestra = AIOrchestra()

    # Run analysis
    results = orchestra.analyze_scenario(scenario, iterations)

    # Display results
    orchestra.display_results(results)

    # Save to file if requested
    if output_file:
        output_file.write_text(json.dumps(results, indent=2, default=str))
        console.print(f"💾 Results saved to {output_file}")


@app.command()
def demo():
    """Run a demonstration of the AI Orchestra."""
    demo_scenario = """
    System Alert: High CPU usage detected on production server (95% utilization).
    Multiple failed login attempts from IP 192.168.1.100.
    Database query response times increased by 300% in the last hour.
    Memory usage at 88% and climbing.
    Security scan detected potential SQL injection vulnerability in user input validation.
    """

    console.print(Panel.fit("🎪 AI Orchestra Demo", style="bold cyan"))
    console.print("Analyzing a complex production scenario...\n")

    orchestra = AIOrchestra()
    results = orchestra.analyze_scenario(demo_scenario, iterations=2)
    orchestra.display_results(results)


if __name__ == "__main__":
    app()
