from dataclasses import dataclass
from typing import Optional

@dataclass
class AIReviewFinding:
    """Represents a single AI review finding"""

    file: str
    line: Optional[int]
    severity: str  # "critical", "high", "medium", "low", "info"
    category: (
        str  # "security", "performance", "maintainability", "style", "documentation"
    )
    issue: str
    suggestion: str
    confidence: float  # 0.0 to 1.0