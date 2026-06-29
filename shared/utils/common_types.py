from dataclasses import dataclass
from typing import Optional
from enum import Enum


class Severity(str, Enum):
    """Enum for the severity of a finding."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Category(str, Enum):
    """Enum for the category of a finding."""
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    STYLE = "style"
    DOCUMENTATION = "documentation"


@dataclass
class AIReviewFinding:
    """Represents a single AI review finding"""

    file: str
    line: Optional[int]
    severity: Severity
    category: Category
    issue: str
    suggestion: str
    confidence: float
