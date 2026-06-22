"""Auto-fix approval gate and PR generation for review cycle findings."""

from review_cycle.autofix.approval_gate import needs_approval, create_pr
from review_cycle.autofix.pr_generator import generate_pr

__all__ = ["needs_approval", "create_pr", "generate_pr"]
