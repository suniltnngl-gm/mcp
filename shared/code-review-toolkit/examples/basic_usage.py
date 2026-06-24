#!/usr/bin/env python3
"""Basic usage example for code-review-toolkit"""

from pathlib import Path
from code_review_toolkit import AICodeReviewer, ReviewCache, CustomRuleEngine

def main():
    # Example 1: AI Review with caching
    print("Example 1: AI Review with Caching")
    print("=" * 50)
    
    reviewer = AICodeReviewer(
        provider="gemini_api",
        enable_cache=True,
        cache_ttl_hours=24
    )
    
    success, stdout, stderr = reviewer.review_directory(
        root_dir=Path("."),
        aspects=["security", "performance"],
        max_files=5
    )
    
    print(stdout)
    
    # Example 2: Custom Rules
    print("\nExample 2: Custom Rules")
    print("=" * 50)
    
    rules = CustomRuleEngine()
    findings = rules.review_directory(Path("."))
    
    if findings:
        print(f"Found {len(findings)} rule violations")
        for finding in findings[:5]:
            print(f"  - {finding.file}:{finding.line} - {finding.message}")
    else:
        print("No violations found!")

if __name__ == "__main__":
    main()
