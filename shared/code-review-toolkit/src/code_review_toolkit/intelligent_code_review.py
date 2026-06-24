#!/usr/bin/env python3
"""Intelligent code review with knowledge base learning"""

import os
import json
import subprocess
import re
from pathlib import Path
from datetime import datetime

class IntelligentCodeReview:
    def __init__(self):
        self.kb_dir = Path("knowledge_base")
        self.review_patterns_file = self.kb_dir / "review_patterns.json"
        self.code_issues_file = self.kb_dir / "code_issues.json"
        
    def review_file(self, file_path):
        """Review single file with learning"""
        issues = []
        
        if file_path.endswith('.sh'):
            issues.extend(self._review_shell_script(file_path))
        elif file_path.endswith('.py'):
            issues.extend(self._review_python_file(file_path))
        
        # Learn from review patterns
        self._learn_review_patterns(file_path, issues)
        
        return issues
    
    def _review_shell_script(self, file_path):
        """Review shell script with pattern matching"""
        issues = []
        
        with open(file_path, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Check common shell issues
        for i, line in enumerate(lines, 1):
            # Missing quotes around variables
            if re.search(r'\$\w+(?!\s*["\'])', line) and not line.strip().startswith('#'):
                issues.append({
                    "line": i,
                    "type": "shell_quoting",
                    "message": "Variable should be quoted to prevent word splitting",
                    "severity": "medium",
                    "suggestion": "Use \"$variable\" instead of $variable"
                })
            
            # Missing error handling
            if 'rm ' in line and 'rm -f' not in line and not any(x in line for x in ['||', '&&', 'if']):
                issues.append({
                    "line": i,
                    "type": "error_handling",
                    "message": "Potentially dangerous rm command without error handling",
                    "severity": "high",
                    "suggestion": "Add error handling or use rm -f"
                })
        
        return issues
    
    def _review_python_file(self, file_path):
        """Review Python file with pattern matching"""
        issues = []
        
        with open(file_path, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Check common Python issues
        for i, line in enumerate(lines, 1):
            # Bare except clauses
            if re.match(r'\s*except\s*:', line):
                issues.append({
                    "line": i,
                    "type": "exception_handling",
                    "message": "Bare except clause catches all exceptions",
                    "severity": "medium",
                    "suggestion": "Specify exception type: except SpecificException:"
                })
            
            # Missing docstrings for functions
            if line.strip().startswith('def ') and i < len(lines) - 1:
                next_line = lines[i].strip() if i < len(lines) else ""
                if not next_line.startswith('"""') and not next_line.startswith("'''"):
                    issues.append({
                        "line": i,
                        "type": "documentation",
                        "message": "Function missing docstring",
                        "severity": "low",
                        "suggestion": "Add docstring to document function purpose"
                    })
        
        return issues
    
    def _learn_review_patterns(self, file_path, issues):
        """Learn from review patterns for future improvements"""
        patterns = self._load_json(self.review_patterns_file)
        
        file_type = Path(file_path).suffix
        if file_type not in patterns:
            patterns[file_type] = {}
        
        for issue in issues:
            issue_type = issue["type"]
            if issue_type not in patterns[file_type]:
                patterns[file_type][issue_type] = {
                    "count": 0,
                    "examples": [],
                    "solutions": []
                }
            
            patterns[file_type][issue_type]["count"] += 1
            
            # Store example if not too many
            if len(patterns[file_type][issue_type]["examples"]) < 5:
                patterns[file_type][issue_type]["examples"].append({
                    "file": file_path,
                    "line": issue["line"],
                    "message": issue["message"]
                })
        
        self._save_json(self.review_patterns_file, patterns)
    
    def get_review_insights(self):
        """Get insights from accumulated review data"""
        patterns = self._load_json(self.review_patterns_file)
        insights = []
        
        for file_type, issues in patterns.items():
            for issue_type, data in issues.items():
                if data["count"] > 3:  # Frequent issue
                    insights.append({
                        "type": issue_type,
                        "file_type": file_type,
                        "frequency": data["count"],
                        "recommendation": f"Consider creating automated check for {issue_type}"
                    })
        
        return insights
    
    def _load_json(self, file_path):
        """Load JSON file safely"""
        if file_path.exists():
            try:
                with open(file_path) as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_json(self, file_path, data):
        """Save JSON file safely"""
        file_path.parent.mkdir(exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

def main():
    reviewer = IntelligentCodeReview()
    
    if len(os.sys.argv) > 1:
        action = os.sys.argv[1]
        
        if action == "review" and len(os.sys.argv) > 2:
            file_path = os.sys.argv[2]
            issues = reviewer.review_file(file_path)
            
            print(f"Code review for {file_path}:")
            for issue in issues:
                print(f"  Line {issue['line']}: [{issue['severity'].upper()}] {issue['message']}")
                print(f"    Suggestion: {issue['suggestion']}")
        
        elif action == "insights":
            insights = reviewer.get_review_insights()
            print("Review insights:")
            for insight in insights:
                print(f"  {insight['type']} in {insight['file_type']} files: {insight['frequency']} occurrences")
                print(f"    {insight['recommendation']}")

if __name__ == "__main__":
    main()

def analyze_staged_files():
    """Analyze only staged files for commit"""
    import subprocess
    
    try:
        # Get staged files
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            return []
        
        staged_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
        
        # Filter for code files
        code_extensions = ['.py', '.sh', '.js', '.ts', '.json', '.yaml', '.yml']
        code_files = [f for f in staged_files 
                     if any(f.endswith(ext) for ext in code_extensions)]
        
        return code_files
        
    except Exception as e:
        print(f"Error getting staged files: {e}")
        return []

if __name__ == "__main__" and "--staged" in sys.argv:
    staged_files = analyze_staged_files()
    if staged_files:
        print(f"[INTELLIGENCE] Analyzing {len(staged_files)} staged files...")
        for file_path in staged_files:
            if os.path.exists(file_path):
                analyze_file(file_path)
    else:
        print("[INTELLIGENCE] No staged code files to analyze")
