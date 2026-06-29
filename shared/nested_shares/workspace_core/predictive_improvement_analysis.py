#!/usr/bin/env python3
"""
Predictive Improvement Analysis - Use version evolution data to predict success
Analyzes patterns to identify successful strategies and risk factors
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

class PredictiveImprovementAnalysis:
    def __init__(self, workspace_root: str = None):
        self.workspace_root = Path(workspace_root or os.getcwd())
        self.registry_path = self.workspace_root / ".kiro" / "lean_versions.json"
    
    def load_registry(self) -> Dict:
        """Load version registry"""
        if not self.registry_path.exists():
            return {"versions": {}, "sessions": {}}
        return json.loads(self.registry_path.read_text())
    
    def analyze_success_patterns(self) -> Dict:
        """Analyze patterns that lead to successful improvements"""
        registry = self.load_registry()
        versions = registry.get("versions", {})
        
        successful = [v for v in versions.values() if v.get("success", False)]
        failed = [v for v in versions.values() if not v.get("success", True)]
        
        patterns = {
            "success_factors": self._extract_success_factors(successful),
            "risk_factors": self._extract_risk_factors(failed),
            "optimal_conditions": self._find_optimal_conditions(successful)
        }
        
        return patterns
    
    def _extract_success_factors(self, successful: List[Dict]) -> Dict:
        """Extract factors that correlate with success"""
        factors = {}
        
        # Improvement type success rates
        type_success = {}
        for version in successful:
            imp_type = version.get("improvement_type", "unknown")
            type_success[imp_type] = type_success.get(imp_type, 0) + 1
        
        factors["improvement_types"] = type_success
        
        # File size patterns
        sizes = [v.get("context", {}).get("file_size", 0) for v in successful if v.get("context", {}).get("file_size")]
        if sizes:
            factors["optimal_file_size"] = {"min": min(sizes), "max": max(sizes), "avg": sum(sizes) / len(sizes)}
        
        return factors
    
    def _extract_risk_factors(self, failed: List[Dict]) -> Dict:
        """Extract factors that correlate with failure"""
        factors = {}
        
        # Common error types
        error_types = {}
        for version in failed:
            for error in version.get("errors", []):
                err_type = error.get("type", "unknown")
                error_types[err_type] = error_types.get(err_type, 0) + 1
        
        factors["common_errors"] = error_types
        
        # Risky file patterns
        risky_files = {}
        for version in failed:
            file_path = version.get("file_path", "unknown")
            risky_files[file_path] = risky_files.get(file_path, 0) + 1
        
        factors["risky_files"] = {f: count for f, count in risky_files.items() if count > 1}
        
        return factors
    
    def _find_optimal_conditions(self, successful: List[Dict]) -> Dict:
        """Find optimal conditions for improvements"""
        conditions = {}
        
        # Time patterns
        hours = [int(v.get("timestamp", "").split("T")[1][:2]) for v in successful if "T" in v.get("timestamp", "")]
        if hours:
            conditions["optimal_hours"] = list(set(h for h in hours if hours.count(h) > 1))
        
        # Session length patterns
        session_lengths = []
        for version in successful:
            context = version.get("context", {})
            if "session_start" in context and "session_end" in context:
                # Simple duration calculation
                session_lengths.append(1)  # Placeholder
        
        return conditions
    
    def predict_success_probability(self, improvement_type: str, file_path: str = None, context: Dict = None) -> Tuple[float, List[str]]:
        """Predict success probability for a proposed improvement"""
        patterns = self.analyze_success_patterns()
        probability = 0.5  # Base probability
        recommendations = []
        
        # Check improvement type success rate
        success_factors = patterns.get("success_factors", {})
        type_success = success_factors.get("improvement_types", {})
        
        if improvement_type in type_success:
            # Higher success rate for proven improvement types
            probability += 0.2
            recommendations.append(f"✅ {improvement_type} has proven success history")
        else:
            probability -= 0.1
            recommendations.append(f"⚠️ {improvement_type} is untested - proceed with caution")
        
        # Check risk factors
        risk_factors = patterns.get("risk_factors", {})
        risky_files = risk_factors.get("risky_files", {})
        
        if file_path and file_path in risky_files:
            probability -= 0.3
            recommendations.append(f"🚨 {file_path} has high failure rate - extra validation needed")
        
        # Check file size if available
        if context and "file_size" in context:
            optimal_size = success_factors.get("optimal_file_size", {})
            if optimal_size:
                size = context["file_size"]
                if optimal_size["min"] <= size <= optimal_size["max"]:
                    probability += 0.1
                    recommendations.append("✅ File size is in optimal range")
        
        return max(0.0, min(1.0, probability)), recommendations
    
    def get_improvement_recommendations(self) -> List[Dict]:
        """Get recommendations for future improvements"""
        patterns = self.analyze_success_patterns()
        recommendations = []
        
        # Recommend high-success improvement types
        success_types = patterns.get("success_factors", {}).get("improvement_types", {})
        for imp_type, count in sorted(success_types.items(), key=lambda x: x[1], reverse=True)[:3]:
            recommendations.append({
                "type": "high_success_strategy",
                "improvement_type": imp_type,
                "success_count": count,
                "recommendation": f"Focus on {imp_type} improvements - high success rate"
            })
        
        # Warn about risky files
        risky_files = patterns.get("risk_factors", {}).get("risky_files", {})
        for file_path, failure_count in risky_files.items():
            recommendations.append({
                "type": "risk_warning",
                "file_path": file_path,
                "failure_count": failure_count,
                "recommendation": f"Avoid or use extra caution with {file_path}"
            })
        
        return recommendations

def main():
    """CLI interface for predictive analysis"""
    import sys
    
    analyzer = PredictiveImprovementAnalysis()
    
    if len(sys.argv) < 2:
        print("Usage: predictive_improvement_analysis.py <command>")
        print("Commands: predict <type> [file], recommendations, patterns")
        return
    
    command = sys.argv[1]
    
    if command == "predict" and len(sys.argv) >= 3:
        improvement_type = sys.argv[2]
        file_path = sys.argv[3] if len(sys.argv) > 3 else None
        
        probability, recommendations = analyzer.predict_success_probability(improvement_type, file_path)
        
        print(f"Success Probability: {probability:.1%}")
        print("Recommendations:")
        for rec in recommendations:
            print(f"  {rec}")
    
    elif command == "recommendations":
        recs = analyzer.get_improvement_recommendations()
        for rec in recs:
            print(f"• {rec['recommendation']}")
    
    elif command == "patterns":
        patterns = analyzer.analyze_success_patterns()
        print("Success Patterns:")
        print(json.dumps(patterns, indent=2))

if __name__ == "__main__":
    main()
