#!/usr/bin/env python3
"""
Unified Code Review - Enhanced with Shared Package
Maintains backward compatibility while using shared toolkit
"""

from pathlib import Path
from code_review_toolkit import AICodeReviewer, ReviewCache, PatternLearner
import sys

def main():
    """Main entry point for unified code review"""
    root_dir = Path.cwd()
    
    print("🔍 Unified Code Review with Pattern Learning")
    print("=" * 50)
    
    # Initialize components
    reviewer = AICodeReviewer(enable_cache=True)
    pattern_learner = PatternLearner(root_dir / "knowledge_base")
    
    # Get files to review
    files = list(root_dir.rglob("*.py"))
    files = [f for f in files if not any(p in str(f) for p in ['.venv', '__pycache__', '.git'])]
    
    print(f"\nReviewing {len(files)} Python files...")
    
    # Review files
    all_findings = []
    for file in files[:10]:  # Limit for demo
        try:
            findings = reviewer.review_file(file)
            all_findings.extend(findings)
            print(f"  ✓ {file.name}: {len(findings)} findings")
        except Exception as e:
            print(f"  ✗ {file.name}: {e}")
    
    # Learn from findings
    findings_dict = [
        {
            'category': f.category,
            'severity': f.severity,
            'issue': f.issue
        }
        for f in all_findings
    ]
    pattern_learner.learn_from_findings(findings_dict)
    
    # Get insights
    insights = pattern_learner.get_insights()
    
    print(f"\n📊 Review Summary")
    print(f"  Total findings: {len(all_findings)}")
    print(f"  Patterns learned: {len(insights)}")
    
    if insights:
        print(f"\n🔍 Top Insights:")
        for i, insight in enumerate(insights[:5], 1):
            print(f"  {i}. [{insight['severity'].upper()}] {insight['description']}")
            print(f"     Frequency: {insight['frequency']} times")
    
    print("\n✅ Review complete!")

if __name__ == "__main__":
    main()
