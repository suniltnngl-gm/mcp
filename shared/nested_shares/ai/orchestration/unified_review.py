#!/usr/bin/env python3
"""Unified Review System - AI-powered code review with tracking"""

import sys
import time
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

# Import tracking systems
try:
    from session_tracker import SessionTracker
    from ai_action_tracker import AIActionTracker
    TRACKING_ENABLED = True
except ImportError:
    TRACKING_ENABLED = False

@dataclass
class ReviewFinding:
    file: str
    line: int
    severity: str
    category: str
    issue: str
    suggestion: str

class UnifiedReview:
    """AI-powered code review with tracking"""
    
    def __init__(self, enable_tracking: bool = True):
        self.tracking_enabled = enable_tracking and TRACKING_ENABLED
        if self.tracking_enabled:
            self.session_tracker = SessionTracker("session_history.jsonl")
            self.action_tracker = AIActionTracker("ai_action_history.jsonl")
    
    def review_file(self, file_path: Path, ai_provider: str = "mock") -> List[ReviewFinding]:
        """Review a single file with AI"""
        start_time = time.time()
        
        # Read file
        try:
            content = file_path.read_text()
        except Exception as e:
            if self.tracking_enabled:
                self.action_tracker.log_action(
                    action_type="review",
                    provider=ai_provider,
                    model="code-review",
                    input_tokens=0,
                    output_tokens=0,
                    cost=0.0,
                    latency=time.time() - start_time,
                    success=False,
                    context={"file": str(file_path)},
                    error=str(e)
                )
            return []
        
        # Mock AI review (replace with actual AI call)
        findings = self._mock_review(file_path, content)
        
        # Track action
        if self.tracking_enabled:
            latency = time.time() - start_time
            self.action_tracker.log_action(
                action_type="review",
                provider=ai_provider,
                model="code-review",
                input_tokens=len(content.split()),
                output_tokens=sum(len(f.issue.split()) + len(f.suggestion.split()) for f in findings),
                cost=0.0,  # Would calculate based on actual API usage
                latency=latency,
                success=True,
                context={
                    "file": str(file_path),
                    "lines": len(content.splitlines()),
                    "findings": len(findings)
                },
                result=f"Found {len(findings)} issues"
            )
        
        return findings
    
    def review_directory(self, directory: Path, pattern: str = "*.py") -> Dict[str, List[ReviewFinding]]:
        """Review all files in directory"""
        if self.tracking_enabled:
            self.session_tracker.start_session(f"Review directory: {directory}")
            self.session_tracker.add_thinking(f"Scanning for {pattern} files")
        
        files = list(directory.rglob(pattern))
        files = [f for f in files if not any(p in str(f) for p in ['.venv', '__pycache__', '.git', 'node_modules'])]
        
        if self.tracking_enabled:
            self.session_tracker.add_action(
                purpose="Scan directory",
                action=f"Found {len(files)} files",
                result=f"Ready to review {len(files)} files"
            )
        
        results = {}
        for file in files:
            findings = self.review_file(file)
            if findings:
                results[str(file)] = findings
        
        if self.tracking_enabled:
            total_findings = sum(len(f) for f in results.values())
            self.session_tracker.complete_session(
                f"Reviewed {len(files)} files, found {total_findings} issues in {len(results)} files"
            )
        
        return results
    
    def _mock_review(self, file_path: Path, content: str) -> List[ReviewFinding]:
        """Mock review for demonstration"""
        findings = []
        lines = content.splitlines()
        
        # Simple pattern detection
        for i, line in enumerate(lines, 1):
            if "TODO" in line:
                findings.append(ReviewFinding(
                    file=str(file_path),
                    line=i,
                    severity="low",
                    category="maintenance",
                    issue="TODO comment found",
                    suggestion="Complete or remove TODO"
                ))
            if "print(" in line and "debug" in line.lower():
                findings.append(ReviewFinding(
                    file=str(file_path),
                    line=i,
                    severity="medium",
                    category="code_quality",
                    issue="Debug print statement",
                    suggestion="Remove debug print or use logging"
                ))
            if len(line) > 120:
                findings.append(ReviewFinding(
                    file=str(file_path),
                    line=i,
                    severity="low",
                    category="style",
                    issue="Line too long",
                    suggestion="Break line into multiple lines"
                ))
        
        return findings[:10]  # Limit findings
    
    def print_results(self, results: Dict[str, List[ReviewFinding]]):
        """Print review results"""
        total_findings = sum(len(f) for f in results.values())
        
        print(f"\n{'='*60}")
        print(f"Review Results: {len(results)} files, {total_findings} findings")
        print(f"{'='*60}\n")
        
        for file, findings in results.items():
            print(f"\n{file}:")
            for finding in findings:
                severity_icon = {"low": "ℹ️", "medium": "⚠️", "high": "🔴"}.get(finding.severity, "•")
                print(f"  {severity_icon} Line {finding.line}: [{finding.category}] {finding.issue}")
                print(f"     → {finding.suggestion}")

def main():
    """CLI interface"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  unified_review.py <file_or_directory> [pattern]")
        print("\nExamples:")
        print("  unified_review.py myfile.py")
        print("  unified_review.py ./src *.py")
        sys.exit(1)
    
    target = Path(sys.argv[1])
    pattern = sys.argv[2] if len(sys.argv) > 2 else "*.py"
    
    reviewer = UnifiedReview()
    
    if target.is_file():
        findings = reviewer.review_file(target)
        results = {str(target): findings} if findings else {}
    else:
        results = reviewer.review_directory(target, pattern)
    
    reviewer.print_results(results)

if __name__ == '__main__':
    main()
