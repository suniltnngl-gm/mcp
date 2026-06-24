"""Code Review Toolkit - Unified code review tools

This package provides:
- AI-powered code review with caching
- Parallel processing for faster reviews
- Custom rule engine for team standards
- Pattern learning from review history
"""

__version__ = "1.0.0"

from code_review_toolkit.cache import ReviewCache
from code_review_toolkit.custom_rules import CustomRuleEngine, CustomRule
from code_review_toolkit.ai_reviewer import AICodeReviewer
from code_review_toolkit.common_types import AIReviewFinding

__all__ = [
    "ReviewCache",
    "CustomRuleEngine",
    "CustomRule",
    "AICodeReviewer",
    "AIReviewFinding",
]

# Pattern Learning
from .pattern_learner import PatternLearner, Pattern
