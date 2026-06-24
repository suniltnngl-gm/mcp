# Code Review Toolkit

Unified code review tools with AI, caching, custom rules, and pattern learning.

## Features

- ✅ **AI-Powered Review**: Intelligent code analysis using LLMs
- ✅ **Smart Caching**: 90% cost reduction through content-based caching
- ✅ **Parallel Processing**: 3-4x faster reviews
- ✅ **Custom Rules**: Team-specific coding standards
- ✅ **Pattern Learning**: Learn from review history

## Installation

### Development Mode
```bash
pip install -e /path/to/code-review-toolkit
```

### Production Mode
```bash
pip install /path/to/code-review-toolkit
```

## Quick Start

```python
from code_review_toolkit import AICodeReviewer, ReviewCache, CustomRuleEngine
from pathlib import Path

# AI review with caching
reviewer = AICodeReviewer(enable_cache=True)
success, stdout, stderr = reviewer.review_directory(
    root_dir=Path("."),
    aspects=["security", "performance"],
    max_files=10
)

# Custom rules
rules = CustomRuleEngine()
findings = rules.review_directory(Path("."))

# Get cache statistics
if reviewer.cache:
    reviewer.cache.print_stats()
```

## Usage in Projects

### coding-agent
```python
from code_review_toolkit import AICodeReviewer
# Use as before
```

### unified-devflow
```python
from code_review_toolkit import AICodeReviewer, PatternLearner
# Combine AI review with pattern learning
```

### dev-refactor
```python
from code_review_toolkit import CustomRuleEngine
# Use custom rules
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run linter
ruff check .

# Type checking
mypy src/
```

## Version History

- **1.0.0** (2025-10-15): Initial release
  - AI code review
  - Caching system
  - Parallel processing
  - Custom rules engine

## License

MIT
