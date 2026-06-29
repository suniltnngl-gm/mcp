"""
🧠 Intelligent Provider Strategy System
=====================================

Advanced provider selection, health monitoring, and routing system for AI Orchestra.
Considers cost, performance, reliability, task requirements, and user preferences.
"""

import json
import logging
import os
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# Ensure environment variables are loaded
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv not available, environment should be set manually

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
logger = logging.getLogger(__name__)


class TaskType(str, Enum):
    """Different types of AI tasks that may benefit from different providers."""

    SECURITY_ANALYSIS = "security_analysis"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    CODE_REVIEW = "code_review"
    CREATIVE_WRITING = "creative_writing"
    DATA_ANALYSIS = "data_analysis"
    GENERAL_ANALYSIS = "general_analysis"
    QUICK_RESPONSE = "quick_response"
    DETAILED_RESEARCH = "detailed_research"


class CostTier(str, Enum):
    """Cost tiers for different providers."""

    FREE = "free"  # HuggingChat, Mock
    LOW = "low"  # Gemini, some OpenRouter models
    MEDIUM = "medium"  # Mistral, most OpenRouter models
    HIGH = "high"  # OpenAI GPT-4, Claude
    PREMIUM = "premium"  # Latest/largest models


@dataclass
class ProviderMetrics:
    """Tracks performance and reliability metrics for a provider."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    recent_response_times: deque = field(default_factory=lambda: deque(maxlen=10))
    recent_errors: deque = field(default_factory=lambda: deque(maxlen=5))
    last_success_time: float | None = None
    last_failure_time: float | None = None
    consecutive_failures: int = 0
    rate_limit_until: float | None = None

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100

    @property
    def average_response_time(self) -> float:
        """Calculate average response time."""
        if self.successful_requests == 0:
            return float("inf")
        return self.total_response_time / self.successful_requests

    @property
    def recent_average_response_time(self) -> float:
        """Calculate recent average response time."""
        if not self.recent_response_times:
            return float("inf")
        return sum(self.recent_response_times) / len(self.recent_response_times)

    @property
    def is_rate_limited(self) -> bool:
        """Check if provider is currently rate limited."""
        return self.rate_limit_until and time.time() < self.rate_limit_until

    @property
    def reliability_score(self) -> float:
        """Calculate overall reliability score (0-100)."""
        if self.total_requests == 0:
            return 50.0  # Neutral score for untested providers

        # Base score from success rate
        base_score = self.success_rate

        # Penalty for consecutive failures
        failure_penalty = min(self.consecutive_failures * 10, 30)

        # Penalty for being rate limited
        rate_limit_penalty = 20 if self.is_rate_limited else 0

        # Bonus for recent success
        recent_success_bonus = (
            10
            if (
                self.last_success_time
                and time.time() - self.last_success_time < 300  # within 5 minutes
            )
            else 0
        )

        score = base_score - failure_penalty - rate_limit_penalty + recent_success_bonus
        return max(0.0, min(100.0, score))


@dataclass
class ProviderProfile:
    """Complete profile of a provider including capabilities and constraints."""

    name: str
    cost_tier: CostTier
    max_tokens_supported: int
    typical_response_time: float  # seconds
    strengths: list[TaskType]
    weaknesses: list[TaskType] = field(default_factory=list)
    rate_limit_rpm: int | None = None  # requests per minute
    rate_limit_tpm: int | None = None  # tokens per minute
    requires_internet: bool = True
    supports_streaming: bool = False
    model_variants: list[str] = field(default_factory=list)

    # Quality scores (0-100)
    code_quality: int = 50
    analysis_quality: int = 50
    creative_quality: int = 50
    speed_score: int = 50
    reliability_score: int = 50


class IntelligentProviderStrategy:
    """Advanced provider selection and management system."""

    def __init__(self):
        self.metrics: dict[str, ProviderMetrics] = {}
        self.profiles = self._initialize_provider_profiles()
        self.cost_budget_used = 0.0
        self.daily_cost_limit = float(os.getenv("DAILY_COST_LIMIT", "5.0"))
        self.preferred_providers = self._load_user_preferences()

    def _initialize_provider_profiles(self) -> dict[str, ProviderProfile]:
        """Initialize provider profiles with known characteristics."""
        return {
            "openai": ProviderProfile(
                name="OpenAI",
                cost_tier=CostTier.HIGH,
                max_tokens_supported=4096,
                typical_response_time=2.0,
                strengths=[
                    TaskType.CODE_REVIEW,
                    TaskType.GENERAL_ANALYSIS,
                    TaskType.CREATIVE_WRITING,
                ],
                rate_limit_rpm=3000,
                rate_limit_tpm=40000,
                supports_streaming=True,
                model_variants=["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"],
                code_quality=95,
                analysis_quality=90,
                creative_quality=85,
                speed_score=80,
                reliability_score=95,
            ),
            "anthropic": ProviderProfile(
                name="Anthropic",
                cost_tier=CostTier.HIGH,
                max_tokens_supported=8192,
                typical_response_time=2.5,
                strengths=[
                    TaskType.SECURITY_ANALYSIS,
                    TaskType.DATA_ANALYSIS,
                    TaskType.DETAILED_RESEARCH,
                ],
                rate_limit_rpm=1000,
                rate_limit_tpm=10000,
                supports_streaming=True,
                model_variants=["claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
                code_quality=90,
                analysis_quality=95,
                creative_quality=80,
                speed_score=75,
                reliability_score=90,
            ),
            "openrouter": ProviderProfile(
                name="OpenRouter",
                cost_tier=CostTier.MEDIUM,
                max_tokens_supported=4096,
                typical_response_time=3.0,
                strengths=[TaskType.GENERAL_ANALYSIS, TaskType.CODE_REVIEW],
                rate_limit_rpm=200,
                rate_limit_tpm=20000,
                supports_streaming=True,
                model_variants=[
                    "openai/gpt-4",
                    "anthropic/claude-3-sonnet",
                    "meta-llama/llama-2-70b-chat",
                ],
                code_quality=85,
                analysis_quality=85,
                creative_quality=75,
                speed_score=70,
                reliability_score=80,
            ),
            "mistral": ProviderProfile(
                name="Mistral",
                cost_tier=CostTier.MEDIUM,
                max_tokens_supported=4096,
                typical_response_time=1.5,
                strengths=[
                    TaskType.CODE_REVIEW,
                    TaskType.QUICK_RESPONSE,
                    TaskType.GENERAL_ANALYSIS,
                ],
                rate_limit_rpm=1000,
                rate_limit_tpm=15000,
                supports_streaming=True,
                model_variants=[
                    "mistral-large-latest",
                    "mistral-medium",
                    "mistral-small",
                ],
                code_quality=80,
                analysis_quality=85,
                creative_quality=70,
                speed_score=90,
                reliability_score=85,
            ),
            "gemini": ProviderProfile(
                name="Gemini",
                cost_tier=CostTier.LOW,
                max_tokens_supported=2048,
                typical_response_time=2.0,
                strengths=[
                    TaskType.DATA_ANALYSIS,
                    TaskType.GENERAL_ANALYSIS,
                    TaskType.QUICK_RESPONSE,
                ],
                rate_limit_rpm=60,
                rate_limit_tpm=32000,
                supports_streaming=False,
                model_variants=["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"],
                code_quality=75,
                analysis_quality=80,
                creative_quality=65,
                speed_score=85,
                reliability_score=75,
            ),
            "huggingchat": ProviderProfile(
                name="HuggingChat",
                cost_tier=CostTier.FREE,
                max_tokens_supported=2048,
                typical_response_time=8.0,
                strengths=[TaskType.CREATIVE_WRITING, TaskType.GENERAL_ANALYSIS],
                weaknesses=[TaskType.CODE_REVIEW, TaskType.SECURITY_ANALYSIS],
                rate_limit_rpm=10,  # Very limited for free service
                rate_limit_tpm=2000,
                supports_streaming=False,
                model_variants=["llama-2-70b-chat", "mistral-7b-instruct"],
                code_quality=60,
                analysis_quality=65,
                creative_quality=75,
                speed_score=30,
                reliability_score=40,  # Often has connectivity issues
            ),
            "groq": ProviderProfile(
                name="Groq",
                cost_tier=CostTier.FREE,
                max_tokens_supported=4096,
                typical_response_time=0.5,  # Ultra-fast
                strengths=[
                    TaskType.QUICK_RESPONSE,
                    TaskType.CODE_REVIEW,
                    TaskType.GENERAL_ANALYSIS,
                ],
                weaknesses=[TaskType.DETAILED_RESEARCH, TaskType.CREATIVE_WRITING],
                rate_limit_rpm=30,  # Free tier limit
                rate_limit_tpm=14400,  # Daily token limit
                supports_streaming=True,
                model_variants=[
                    "llama-3.1-8b-instant",
                    "mixtral-8x7b-32768",
                    "gemma-7b-it",
                ],
                code_quality=75,
                analysis_quality=70,
                creative_quality=60,
                speed_score=100,  # Ultra-fast
                reliability_score=75,
            ),
            "together": ProviderProfile(
                name="Together",
                cost_tier=CostTier.LOW,
                max_tokens_supported=16384,
                typical_response_time=1.8,
                strengths=[
                    TaskType.CODE_REVIEW,
                    TaskType.GENERAL_ANALYSIS,
                    TaskType.CREATIVE_WRITING,
                ],
                rate_limit_rpm=100,
                rate_limit_tpm=50000,
                supports_streaming=True,
                model_variants=[
                    "togethercomputer/llama-2-70b-chat",
                    "mistralai/Mixtral-8x7B-Instruct-v0.1",
                ],
                code_quality=80,
                analysis_quality=75,
                creative_quality=75,
                speed_score=85,
                reliability_score=80,
            ),
            "cohere": ProviderProfile(
                name="Cohere",
                cost_tier=CostTier.FREE,
                max_tokens_supported=4096,
                typical_response_time=3.0,
                strengths=[TaskType.DATA_ANALYSIS, TaskType.GENERAL_ANALYSIS],
                weaknesses=[TaskType.CODE_REVIEW, TaskType.CREATIVE_WRITING],
                rate_limit_rpm=20,  # Free tier
                rate_limit_tpm=4000,
                supports_streaming=False,
                model_variants=["command", "command-light", "command-nightly"],
                code_quality=65,
                analysis_quality=80,
                creative_quality=55,
                speed_score=70,
                reliability_score=85,
            ),
            "perplexity": ProviderProfile(
                name="Perplexity",
                cost_tier=CostTier.FREE,
                max_tokens_supported=16384,
                typical_response_time=4.0,
                strengths=[TaskType.DETAILED_RESEARCH, TaskType.DATA_ANALYSIS],
                weaknesses=[TaskType.CODE_REVIEW, TaskType.CREATIVE_WRITING],
                rate_limit_rpm=5,  # Very limited free tier
                rate_limit_tpm=1000,
                supports_streaming=True,
                model_variants=[
                    "llama-3.1-sonar-small-128k-online",
                    "llama-3.1-sonar-large-128k-online",
                ],
                code_quality=60,
                analysis_quality=90,  # Great for research
                creative_quality=50,
                speed_score=65,
                reliability_score=75,
            ),
            "deepseek": ProviderProfile(
                name="DeepSeek",
                cost_tier=CostTier.LOW,
                max_tokens_supported=32000,
                typical_response_time=2.0,
                strengths=[
                    TaskType.CODE_REVIEW,
                    TaskType.GENERAL_ANALYSIS,
                    TaskType.DATA_ANALYSIS,
                ],
                rate_limit_rpm=50,
                rate_limit_tpm=40000,
                supports_streaming=True,
                model_variants=["deepseek-chat", "deepseek-coder"],
                code_quality=85,  # Very good for coding
                analysis_quality=80,
                creative_quality=60,
                speed_score=85,
                reliability_score=80,
            ),
            "ollama": ProviderProfile(
                name="Ollama",
                cost_tier=CostTier.FREE,
                max_tokens_supported=8192,
                typical_response_time=8.0,  # Depends on hardware
                strengths=[
                    TaskType.CODE_REVIEW,
                    TaskType.GENERAL_ANALYSIS,
                    TaskType.CREATIVE_WRITING,
                ],
                requires_internet=False,
                rate_limit_rpm=1000,  # No external limits
                supports_streaming=True,
                model_variants=["llama3", "codellama", "mistral", "neural-chat"],
                code_quality=75,
                analysis_quality=70,
                creative_quality=70,
                speed_score=40,  # Variable based on hardware
                reliability_score=85,
            ),
            "replicate": ProviderProfile(
                name="Replicate",
                cost_tier=CostTier.MEDIUM,
                max_tokens_supported=4096,
                typical_response_time=10.0,  # Cold starts
                strengths=[TaskType.CREATIVE_WRITING, TaskType.GENERAL_ANALYSIS],
                weaknesses=[TaskType.QUICK_RESPONSE],
                rate_limit_rpm=100,
                supports_streaming=False,
                model_variants=[
                    "meta/llama-2-70b-chat",
                    "mistralai/mistral-7b-instruct-v0.1",
                ],
                code_quality=75,
                analysis_quality=80,
                creative_quality=85,
                speed_score=30,  # Cold start penalty
                reliability_score=75,
            ),
            "ai21": ProviderProfile(
                name="AI21",
                cost_tier=CostTier.FREE,
                max_tokens_supported=8192,
                typical_response_time=3.0,
                strengths=[TaskType.GENERAL_ANALYSIS, TaskType.CREATIVE_WRITING],
                weaknesses=[TaskType.CODE_REVIEW],
                rate_limit_rpm=20,  # Free tier
                rate_limit_tpm=10000,
                supports_streaming=False,
                model_variants=["j2-ultra", "j2-mid", "j2-light"],
                code_quality=60,
                analysis_quality=75,
                creative_quality=80,
                speed_score=70,
                reliability_score=80,
            ),
            "fireworks": ProviderProfile(
                name="Fireworks",
                cost_tier=CostTier.LOW,
                max_tokens_supported=16384,
                typical_response_time=1.2,
                strengths=[
                    TaskType.CODE_REVIEW,
                    TaskType.QUICK_RESPONSE,
                    TaskType.GENERAL_ANALYSIS,
                ],
                rate_limit_rpm=100,
                rate_limit_tpm=60000,
                supports_streaming=True,
                model_variants=[
                    "accounts/fireworks/models/llama-v3p1-70b-instruct",
                    "accounts/fireworks/models/mixtral-8x7b-instruct",
                ],
                code_quality=85,
                analysis_quality=80,
                creative_quality=70,
                speed_score=95,
                reliability_score=85,
            ),
            "cerebras": ProviderProfile(
                name="Cerebras",
                cost_tier=CostTier.FREE,
                max_tokens_supported=8192,
                typical_response_time=0.3,  # Ultra-fast
                strengths=[
                    TaskType.QUICK_RESPONSE,
                    TaskType.CODE_REVIEW,
                    TaskType.GENERAL_ANALYSIS,
                ],
                rate_limit_rpm=30,  # Free tier
                rate_limit_tpm=15000,
                supports_streaming=True,
                model_variants=["llama3.1-8b", "llama3.1-70b"],
                code_quality=80,
                analysis_quality=75,
                creative_quality=65,
                speed_score=100,  # Ultra-fast
                reliability_score=85,
            ),
            "sambanova": ProviderProfile(
                name="SambaNova",
                cost_tier=CostTier.FREE,
                max_tokens_supported=16384,
                typical_response_time=1.5,
                strengths=[
                    TaskType.CODE_REVIEW,
                    TaskType.GENERAL_ANALYSIS,
                    TaskType.DATA_ANALYSIS,
                ],
                rate_limit_rpm=50,  # Free tier
                rate_limit_tpm=50000,
                supports_streaming=True,
                model_variants=[
                    "Meta-Llama-3.1-70B-Instruct",
                    "Meta-Llama-3.1-8B-Instruct",
                ],
                code_quality=85,
                analysis_quality=80,
                creative_quality=70,
                speed_score=85,
                reliability_score=80,
            ),
            "hyperbolic": ProviderProfile(
                name="Hyperbolic",
                cost_tier=CostTier.LOW,
                max_tokens_supported=32000,
                typical_response_time=1.0,
                strengths=[
                    TaskType.QUICK_RESPONSE,
                    TaskType.CODE_REVIEW,
                    TaskType.GENERAL_ANALYSIS,
                ],
                rate_limit_rpm=100,
                rate_limit_tpm=80000,
                supports_streaming=True,
                model_variants=[
                    "meta-llama/Llama-3.1-70B-Instruct",
                    "mistralai/Mixtral-8x7B-Instruct-v0.1",
                ],
                code_quality=85,
                analysis_quality=80,
                creative_quality=75,
                speed_score=95,
                reliability_score=85,
            ),
            "mock": ProviderProfile(
                name="Mock",
                cost_tier=CostTier.FREE,
                max_tokens_supported=float("inf"),
                typical_response_time=0.1,
                strengths=[TaskType.QUICK_RESPONSE],
                weaknesses=[TaskType.DETAILED_RESEARCH, TaskType.CODE_REVIEW],
                requires_internet=False,
                supports_streaming=False,
                code_quality=30,
                analysis_quality=40,
                creative_quality=20,
                speed_score=100,
                reliability_score=100,
            ),
        }

    def _load_user_preferences(self) -> dict[str, int]:
        """Load user provider preferences from environment or config."""
        # Default preferences (higher number = higher preference)
        preferences = {
            "groq": 110,  # Ultra-fast, free tier - highest priority
            "mistral": 100,  # Your current default
            "deepseek": 95,  # Very affordable coding specialist
            "together": 90,  # Cheap and reliable
            "openrouter": 85,
            "cohere": 80,  # Good for analysis, free tier
            "gemini": 75,
            "anthropic": 70,
            "openai": 65,  # High quality but expensive
            "ollama": 60,  # Free local but requires setup
            "perplexity": 50,  # Limited free tier but great for research
            "replicate": 45,  # Pay-per-use, cold starts
            "huggingchat": 30,  # Often unreliable
            "mock": 10,  # Testing only
        }

        # Allow override via environment
        pref_override = os.getenv("PROVIDER_PREFERENCES")
        if pref_override:
            try:
                custom_prefs = json.loads(pref_override)
                preferences.update(custom_prefs)
            except json.JSONDecodeError:
                logger.warning("Invalid PROVIDER_PREFERENCES format, using defaults")

        return preferences

    def get_metrics(self, provider_name: str) -> ProviderMetrics:
        """Get or create metrics for a provider."""
        if provider_name not in self.metrics:
            self.metrics[provider_name] = ProviderMetrics()
        return self.metrics[provider_name]

    def record_success(
        self, provider_name: str, response_time: float, tokens_used: int = 0
    ):
        """Record a successful provider interaction."""
        metrics = self.get_metrics(provider_name)
        metrics.total_requests += 1
        metrics.successful_requests += 1
        metrics.total_response_time += response_time
        metrics.recent_response_times.append(response_time)
        metrics.last_success_time = time.time()
        metrics.consecutive_failures = 0

        # Estimate cost (rough approximation)
        profile = self.profiles.get(provider_name)
        if profile and profile.cost_tier != CostTier.FREE:
            estimated_cost = self._estimate_cost(provider_name, tokens_used)
            self.cost_budget_used += estimated_cost

    def record_failure(self, provider_name: str, error: str):
        """Record a failed provider interaction."""
        metrics = self.get_metrics(provider_name)
        metrics.total_requests += 1
        metrics.failed_requests += 1
        metrics.recent_errors.append(error)
        metrics.last_failure_time = time.time()
        metrics.consecutive_failures += 1

        # Check for rate limiting
        if "rate limit" in error.lower() or "429" in error:
            # Set rate limit backoff (exponential)
            backoff_minutes = min(2**metrics.consecutive_failures, 60)
            metrics.rate_limit_until = time.time() + (backoff_minutes * 60)

    def _estimate_cost(self, provider_name: str, tokens: int) -> float:
        """Rough cost estimation per provider."""
        # Approximate costs per 1K tokens (as of 2024)
        cost_per_1k = {
            "openai": 0.03,  # GPT-4 average
            "anthropic": 0.025,  # Claude-3 average
            "openrouter": 0.02,  # Varies, average estimate
            "mistral": 0.007,  # Much cheaper
            "gemini": 0.004,  # Very competitive
            "together": 0.0008,  # Very cheap
            "deepseek": 0.0014,  # Very affordable
            "replicate": 0.005,  # Pay per use
            "groq": 0.0,  # Free tier
            "cohere": 0.0,  # Free tier
            "perplexity": 0.0,  # Free tier (limited)
            "ollama": 0.0,  # Local, completely free
            "huggingchat": 0.0,  # Free
            "mock": 0.0,  # Free
        }

        rate = cost_per_1k.get(provider_name, 0.01)
        return (tokens / 1000) * rate

    def classify_task(self, prompt: str) -> TaskType:
        """Automatically classify the task type based on prompt content."""
        prompt_lower = prompt.lower()

        # Security-related keywords
        security_keywords = [
            "security",
            "vulnerability",
            "breach",
            "attack",
            "unauthorized",
            "penetration",
            "audit",
            "compliance",
            "threat",
            "malware",
            "encryption",
        ]

        # Performance-related keywords
        performance_keywords = [
            "performance",
            "optimize",
            "slow",
            "fast",
            "latency",
            "throughput",
            "bottleneck",
            "cpu",
            "memory",
            "database",
            "cache",
            "scaling",
        ]

        # Code-related keywords
        code_keywords = [
            "code",
            "function",
            "class",
            "method",
            "review",
            "refactor",
            "bug",
            "debug",
            "test",
            "implementation",
            "algorithm",
        ]

        # Creative keywords
        creative_keywords = [
            "write",
            "story",
            "creative",
            "blog",
            "article",
            "marketing",
            "copy",
            "content",
            "narrative",
            "brainstorm",
        ]

        # Data analysis keywords
        data_keywords = [
            "data",
            "analyze",
            "statistics",
            "trend",
            "pattern",
            "insight",
            "report",
            "visualization",
            "correlation",
            "regression",
        ]

        # Count keyword matches
        keyword_counts = {
            TaskType.SECURITY_ANALYSIS: sum(
                1 for word in security_keywords if word in prompt_lower
            ),
            TaskType.PERFORMANCE_OPTIMIZATION: sum(
                1 for word in performance_keywords if word in prompt_lower
            ),
            TaskType.CODE_REVIEW: sum(
                1 for word in code_keywords if word in prompt_lower
            ),
            TaskType.CREATIVE_WRITING: sum(
                1 for word in creative_keywords if word in prompt_lower
            ),
            TaskType.DATA_ANALYSIS: sum(
                1 for word in data_keywords if word in prompt_lower
            ),
        }

        # Return the task type with the most matches first
        if max(keyword_counts.values()) > 0:
            return max(keyword_counts.items(), key=lambda x: x[1])[0]

        # Check for detailed vs quick response needs if no specific task keywords found
        if (
            len(prompt) > 500
            or "detailed" in prompt_lower
            or "comprehensive" in prompt_lower
        ):
            return TaskType.DETAILED_RESEARCH
        elif len(prompt) < 50 or "quick" in prompt_lower or "briefly" in prompt_lower:
            return TaskType.QUICK_RESPONSE

        return TaskType.GENERAL_ANALYSIS

    def calculate_provider_score(
        self, provider_name: str, task_type: TaskType, available_providers: list[str]
    ) -> float:
        """Calculate a comprehensive score for provider selection with wide differentiation."""
        profile = self.profiles.get(provider_name)
        metrics = self.get_metrics(provider_name)

        if not profile or provider_name not in available_providers:
            return 0.0

        # === CORE SCORING COMPONENTS (0-100 each) ===

        # 1. Task Suitability Score (much more aggressive)
        if task_type in profile.strengths:
            task_score = 95  # Excellent match
        elif task_type in profile.weaknesses:
            task_score = 15  # Poor match - avoid
        else:
            task_score = 55  # Neutral

        # 2. Dynamic Quality Score based on task + provider capability
        quality_mapping = {
            TaskType.CODE_REVIEW: profile.code_quality,
            TaskType.SECURITY_ANALYSIS: profile.analysis_quality,
            TaskType.PERFORMANCE_OPTIMIZATION: profile.analysis_quality,
            TaskType.CREATIVE_WRITING: profile.creative_quality,
            TaskType.DATA_ANALYSIS: profile.analysis_quality,
            TaskType.QUICK_RESPONSE: profile.speed_score,
            TaskType.DETAILED_RESEARCH: profile.analysis_quality,
            TaskType.GENERAL_ANALYSIS: (profile.code_quality + profile.analysis_quality)
            / 2,
        }
        base_quality = quality_mapping.get(task_type, 50)

        # Boost quality score for proven track record
        if metrics.total_requests >= 5 and metrics.success_rate > 90:
            quality_score = min(
                100, base_quality * 1.15
            )  # 15% boost for reliable providers
        else:
            quality_score = base_quality

        # 3. Dynamic Reliability Score (heavily weighted by recent performance)
        reliability_base = metrics.reliability_score

        # Heavy penalties for current issues
        if metrics.is_rate_limited:
            reliability_score = max(5, reliability_base * 0.1)  # Severe penalty
        elif metrics.consecutive_failures >= 2:
            reliability_score = max(20, reliability_base * 0.4)  # Major penalty
        elif metrics.consecutive_failures == 1:
            reliability_score = max(40, reliability_base * 0.7)  # Moderate penalty
        else:
            reliability_score = reliability_base

        # Bonus for recent successful performance
        if metrics.last_success_time and time.time() - metrics.last_success_time < 300:
            reliability_score = min(100, reliability_score * 1.1)

        # 4. Speed Score with performance learning
        base_speed = max(10, 100 - (profile.typical_response_time * 15))

        # Use actual recent performance if available
        if metrics.recent_response_times:
            actual_avg_time = sum(metrics.recent_response_times) / len(
                metrics.recent_response_times
            )
            actual_speed = max(10, 100 - (actual_avg_time * 15))
            speed_score = (base_speed + actual_speed) / 2  # Blend expected and actual
        else:
            speed_score = base_speed

        # 5. Cost Efficiency with Budget Intelligence
        cost_base_scores = {
            CostTier.FREE: 100,
            CostTier.LOW: 85,
            CostTier.MEDIUM: 65,
            CostTier.HIGH: 35,
            CostTier.PREMIUM: 10,
        }
        cost_score = cost_base_scores.get(profile.cost_tier, 50)

        # Dynamic budget-based adjustments
        budget_usage_pct = (self.cost_budget_used / self.daily_cost_limit) * 100

        if budget_usage_pct > 90:  # Budget critical
            if profile.cost_tier in [CostTier.HIGH, CostTier.PREMIUM]:
                cost_score *= 0.1  # Almost eliminate expensive providers
            elif profile.cost_tier == CostTier.MEDIUM:
                cost_score *= 0.3
        elif budget_usage_pct > 70:  # Budget warning
            if profile.cost_tier in [CostTier.HIGH, CostTier.PREMIUM]:
                cost_score *= 0.4
            elif profile.cost_tier == CostTier.MEDIUM:
                cost_score *= 0.7

        # 6. User Preference Score (normalized to 0-100)
        preference_raw = self.preferred_providers.get(provider_name, 50)
        preference_score = min(100, max(0, preference_raw))  # Ensure 0-100 range

        # === ADVANCED SCORING LOGIC ===

        # Task-specific weighting (different tasks prioritize different factors)
        if task_type == TaskType.QUICK_RESPONSE:
            weights = {
                "speed": 0.40,
                "reliability": 0.25,
                "task": 0.15,
                "cost": 0.10,
                "quality": 0.05,
                "preference": 0.05,
            }
        elif task_type == TaskType.SECURITY_ANALYSIS:
            weights = {
                "quality": 0.35,
                "reliability": 0.30,
                "task": 0.20,
                "preference": 0.10,
                "speed": 0.03,
                "cost": 0.02,
            }
        elif task_type == TaskType.CODE_REVIEW:
            weights = {
                "quality": 0.35,
                "task": 0.25,
                "reliability": 0.20,
                "preference": 0.10,
                "speed": 0.05,
                "cost": 0.05,
            }
        elif task_type == TaskType.CREATIVE_WRITING:
            weights = {
                "quality": 0.40,
                "task": 0.25,
                "preference": 0.15,
                "reliability": 0.10,
                "cost": 0.05,
                "speed": 0.05,
            }
        elif task_type in [TaskType.PERFORMANCE_OPTIMIZATION, TaskType.DATA_ANALYSIS]:
            weights = {
                "quality": 0.30,
                "task": 0.25,
                "reliability": 0.20,
                "speed": 0.15,
                "preference": 0.07,
                "cost": 0.03,
            }
        else:  # GENERAL_ANALYSIS, DETAILED_RESEARCH
            weights = {
                "task": 0.25,
                "quality": 0.25,
                "reliability": 0.20,
                "preference": 0.15,
                "speed": 0.10,
                "cost": 0.05,
            }

        # Calculate weighted score
        final_score = (
            task_score * weights["task"]
            + quality_score * weights["quality"]
            + reliability_score * weights["reliability"]
            + speed_score * weights["speed"]
            + cost_score * weights["cost"]
            + preference_score * weights["preference"]
        )

        # === BONUS/PENALTY SYSTEM ===

        # Bonus for perfect task match + high quality
        if task_type in profile.strengths and base_quality >= 85:
            final_score += 15  # Excellence bonus

        # Bonus for being the only provider with specific strengths
        strength_providers = [
            name
            for name, p in self.profiles.items()
            if name in available_providers and task_type in p.strengths
        ]
        if len(strength_providers) == 1 and provider_name in strength_providers:
            final_score += 20  # Unique capability bonus

        # Penalty for known weaknesses in critical tasks
        if (
            task_type in [TaskType.SECURITY_ANALYSIS, TaskType.CODE_REVIEW]
            and task_type in profile.weaknesses
        ):
            final_score -= 25  # Critical task weakness penalty

        # Recent performance bonus/penalty
        if metrics.total_requests >= 3:
            recent_success_rate = metrics.success_rate
            if recent_success_rate >= 95:
                final_score += 10  # Excellent track record
            elif recent_success_rate <= 60:
                final_score -= 15  # Poor track record

        # Ensure final score is in valid range with better distribution
        final_score = max(5.0, min(100.0, final_score))

        return final_score

    def select_provider(
        self,
        prompt: str,
        available_providers: list[str],
        force_provider: str | None = None,
    ) -> tuple[str, TaskType, float]:
        """Intelligently select the best provider for a given task."""

        if force_provider and force_provider in available_providers:
            task_type = self.classify_task(prompt)
            score = self.calculate_provider_score(
                force_provider, task_type, available_providers
            )
            return force_provider, task_type, score

        # Classify the task
        task_type = self.classify_task(prompt)

        # Calculate scores for all available providers
        provider_scores = {}
        for provider in available_providers:
            score = self.calculate_provider_score(
                provider, task_type, available_providers
            )
            provider_scores[provider] = score

        if not provider_scores:
            return "mock", task_type, 0.0

        # Select provider with highest score
        best_provider = max(provider_scores.items(), key=lambda x: x[1])
        return best_provider[0], task_type, best_provider[1]

    def get_fallback_providers(
        self, failed_provider: str, task_type: TaskType, available_providers: list[str]
    ) -> list[str]:
        """Get ordered list of fallback providers when primary fails."""
        remaining_providers = [p for p in available_providers if p != failed_provider]

        # Score remaining providers
        fallback_scores = []
        for provider in remaining_providers:
            score = self.calculate_provider_score(
                provider, task_type, remaining_providers
            )
            fallback_scores.append((provider, score))

        # Sort by score (descending)
        fallback_scores.sort(key=lambda x: x[1], reverse=True)

        return [provider for provider, score in fallback_scores]

    def should_retry_failed_provider(self, provider_name: str) -> bool:
        """Determine if a failed provider should be retried."""
        metrics = self.get_metrics(provider_name)

        # Don't retry if rate limited
        if metrics.is_rate_limited:
            return False

        # Don't retry if too many consecutive failures
        if metrics.consecutive_failures >= 3:
            return False

        # Don't retry if recently failed (within last 60 seconds)
        return not (
            metrics.last_failure_time and time.time() - metrics.last_failure_time < 60
        )

    def display_provider_status(self, available_providers: list[str]):
        """Display comprehensive provider status table."""
        table = Table(title="🎯 Intelligent Provider Status")

        table.add_column("Provider", style="cyan", no_wrap=True)
        table.add_column("Status", justify="center")
        table.add_column("Cost Tier", justify="center")
        table.add_column("Reliability", justify="right")
        table.add_column("Avg Response", justify="right")
        table.add_column("Requests", justify="right")
        table.add_column("Success Rate", justify="right")
        table.add_column("Strengths", style="green")

        for provider_name in self.profiles:
            profile = self.profiles[provider_name]
            metrics = self.get_metrics(provider_name)

            # Status
            if provider_name in available_providers:
                if metrics.is_rate_limited:
                    status = "⏳ Rate Limited"
                elif metrics.consecutive_failures >= 3:
                    status = "❌ Failing"
                else:
                    status = "✅ Ready"
            else:
                status = "❌ Unavailable"

            # Format metrics
            reliability = f"{metrics.reliability_score:.1f}%"
            avg_response = (
                f"{metrics.recent_average_response_time:.1f}s"
                if metrics.successful_requests > 0
                else "N/A"
            )
            success_rate = (
                f"{metrics.success_rate:.1f}%" if metrics.total_requests > 0 else "N/A"
            )
            strengths = ", ".join(
                [t.value.replace("_", " ").title() for t in profile.strengths[:2]]
            )

            table.add_row(
                profile.name,
                status,
                profile.cost_tier.value.title(),
                reliability,
                avg_response,
                str(metrics.total_requests),
                success_rate,
                strengths,
            )

        console.print(table)

        # Budget status
        budget_used_pct = (self.cost_budget_used / self.daily_cost_limit) * 100
        budget_color = (
            "red"
            if budget_used_pct > 80
            else "yellow" if budget_used_pct > 60 else "green"
        )

        console.print(
            Panel(
                f"💰 Budget: ${self.cost_budget_used:.3f} / ${self.daily_cost_limit:.2f} "
                f"({budget_used_pct:.1f}% used)",
                style=budget_color,
            )
        )

    def recommend_task_optimization(self, task_type: TaskType) -> dict[str, Any]:
        """Provide optimization recommendations for specific task types."""
        recommendations = {
            TaskType.SECURITY_ANALYSIS: {
                "preferred_providers": ["anthropic", "openai", "mistral"],
                "avoid_providers": ["huggingchat", "mock"],
                "suggested_tokens": 800,
                "temperature": 0.3,
                "tips": "Use lower temperature for more focused analysis",
            },
            TaskType.PERFORMANCE_OPTIMIZATION: {
                "preferred_providers": ["mistral", "openai", "anthropic"],
                "avoid_providers": ["huggingchat"],
                "suggested_tokens": 600,
                "temperature": 0.4,
                "tips": "Mistral excels at technical optimization tasks",
            },
            TaskType.CODE_REVIEW: {
                "preferred_providers": ["openai", "mistral", "anthropic"],
                "avoid_providers": ["huggingchat", "mock"],
                "suggested_tokens": 1000,
                "temperature": 0.2,
                "tips": "Lower temperature for more consistent code analysis",
            },
            TaskType.CREATIVE_WRITING: {
                "preferred_providers": ["openai", "huggingchat", "anthropic"],
                "avoid_providers": ["mock"],
                "suggested_tokens": 800,
                "temperature": 0.8,
                "tips": "Higher temperature for more creative outputs",
            },
            TaskType.QUICK_RESPONSE: {
                "preferred_providers": ["mistral", "gemini", "mock"],
                "avoid_providers": ["huggingchat"],
                "suggested_tokens": 300,
                "temperature": 0.5,
                "tips": "Use fast providers with lower token limits",
            },
            TaskType.DETAILED_RESEARCH: {
                "preferred_providers": ["anthropic", "openai", "openrouter"],
                "avoid_providers": ["mock"],
                "suggested_tokens": 1500,
                "temperature": 0.4,
                "tips": "Use providers with higher token limits",
            },
        }

        return recommendations.get(
            task_type,
            {
                "preferred_providers": ["mistral", "openrouter", "gemini"],
                "avoid_providers": ["mock"],
                "suggested_tokens": 500,
                "temperature": 0.5,
                "tips": "General analysis works well with most providers",
            },
        )

    def get_optimal_config_for_task(
        self, task_type: TaskType, base_config
    ) -> dict[str, Any]:
        """Get optimal configuration parameters for a specific task type."""
        recommendations = self.recommend_task_optimization(task_type)

        # Create optimized config
        optimal_config = {
            "max_tokens": recommendations.get(
                "suggested_tokens", base_config.max_tokens
            ),
            "temperature": recommendations.get("temperature", base_config.temperature),
        }

        return optimal_config


def create_intelligent_strategy() -> IntelligentProviderStrategy:
    """Factory function to create the intelligent provider strategy."""
    return IntelligentProviderStrategy()


# Example usage and testing
if __name__ == "__main__":
    strategy = create_intelligent_strategy()

    # Test task classification
    test_prompts = [
        "Analyze this security vulnerability in our web application",
        "Optimize this slow database query for better performance",
        "Review this Python code for potential bugs",
        "Write a creative story about AI assistants",
        "Quickly summarize this data trend",
        "Perform comprehensive analysis of our cloud infrastructure",
    ]

    console.print("🧪 Testing Task Classification:")
    for prompt in test_prompts:
        task_type = strategy.classify_task(prompt)
        recommendations = strategy.recommend_task_optimization(task_type)
        console.print(f"📝 '{prompt[:50]}...' → {task_type.value}")
        console.print(
            f"   Preferred: {', '.join(recommendations['preferred_providers'][:3])}"
        )
        console.print()

    # Test provider scoring
    available_providers = ["mistral", "openrouter", "gemini", "mock"]
    test_prompt = "Analyze this security incident in our production environment"

    provider, task_type, score = strategy.select_provider(
        test_prompt, available_providers
    )
    console.print(f"🎯 Selected: {provider} (Score: {score:.1f}) for {task_type.value}")
