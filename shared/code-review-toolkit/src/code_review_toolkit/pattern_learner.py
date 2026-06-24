"""
Pattern Learning Module
Extracted from unified-devflow for shared use
"""

from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class Pattern:
    """Represents a learned pattern from code reviews"""
    pattern_type: str
    description: str
    frequency: int
    severity: str
    examples: List[str]
    last_seen: str

class PatternLearner:
    """Learn from review patterns and provide insights"""
    
    def __init__(self, kb_dir: Path):
        self.kb_dir = Path(kb_dir)
        self.kb_dir.mkdir(exist_ok=True)
        self.patterns_file = self.kb_dir / "learned_patterns.json"
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict[str, Pattern]:
        """Load patterns from knowledge base"""
        if not self.patterns_file.exists():
            return {}
        
        try:
            data = json.loads(self.patterns_file.read_text())
            return {
                k: Pattern(**v) for k, v in data.items()
            }
        except Exception as e:
            print(f"Warning: Could not load patterns: {e}")
            return {}
    
    def _save_patterns(self):
        """Save patterns to knowledge base"""
        data = {
            k: {
                'pattern_type': v.pattern_type,
                'description': v.description,
                'frequency': v.frequency,
                'severity': v.severity,
                'examples': v.examples,
                'last_seen': v.last_seen,
            }
            for k, v in self.patterns.items()
        }
        self.patterns_file.write_text(json.dumps(data, indent=2))
    
    def learn_from_findings(self, findings: List[Dict]):
        """Learn patterns from review findings"""
        for finding in findings:
            pattern_key = f"{finding.get('category', 'unknown')}_{finding.get('severity', 'low')}"
            
            if pattern_key in self.patterns:
                # Update existing pattern
                pattern = self.patterns[pattern_key]
                pattern.frequency += 1
                pattern.last_seen = datetime.now().isoformat()
                if finding.get('issue') not in pattern.examples:
                    pattern.examples.append(finding.get('issue', ''))
            else:
                # Create new pattern
                self.patterns[pattern_key] = Pattern(
                    pattern_type=finding.get('category', 'unknown'),
                    description=finding.get('issue', ''),
                    frequency=1,
                    severity=finding.get('severity', 'low'),
                    examples=[finding.get('issue', '')],
                    last_seen=datetime.now().isoformat()
                )
        
        self._save_patterns()
    
    def get_insights(self) -> List[Dict]:
        """Get insights from learned patterns"""
        insights = []
        
        # Sort patterns by frequency
        sorted_patterns = sorted(
            self.patterns.items(),
            key=lambda x: x[1].frequency,
            reverse=True
        )
        
        for key, pattern in sorted_patterns[:10]:  # Top 10
            insights.append({
                'type': pattern.pattern_type,
                'description': pattern.description,
                'frequency': pattern.frequency,
                'severity': pattern.severity,
                'recommendation': f"Consider addressing this recurring {pattern.severity} issue"
            })
        
        return insights
    
    def get_top_issues(self, limit: int = 5) -> List[Dict]:
        """Get top recurring issues"""
        sorted_patterns = sorted(
            self.patterns.items(),
            key=lambda x: x[1].frequency,
            reverse=True
        )
        
        return [
            {
                'pattern': p.pattern_type,
                'count': p.frequency,
                'severity': p.severity,
                'example': p.examples[0] if p.examples else ''
            }
            for _, p in sorted_patterns[:limit]
        ]
