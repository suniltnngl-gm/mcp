#!/usr/bin/env python3
"""Merge Pattern Analyzer - Learn from merge operations"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, asdict

@dataclass
class MergePattern:
    operation_type: str  # merge, split, refactor
    files_involved: List[str]
    success: bool
    conflicts: List[str]
    resolution_strategy: str
    time_taken: float
    complexity_score: float
    timestamp: str

class MergePatternAnalyzer:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.patterns_file = self.base_path / "merge_patterns.json"
        self.load_patterns()
    
    def load_patterns(self):
        """Load historical merge patterns"""
        if self.patterns_file.exists():
            with open(self.patterns_file, 'r') as f:
                data = json.load(f)
                self.patterns = [MergePattern(**p) for p in data.get("patterns", [])]
        else:
            self.patterns = []
    
    def record_merge_operation(self, operation_type: str, files: List[str], 
                             success: bool, conflicts: List[str] = None,
                             strategy: str = "unknown", time_taken: float = 0.0) -> str:
        """Record a merge operation for pattern learning"""
        
        complexity = self._calculate_complexity(files, conflicts or [])
        
        pattern = MergePattern(
            operation_type=operation_type,
            files_involved=files,
            success=success,
            conflicts=conflicts or [],
            resolution_strategy=strategy,
            time_taken=time_taken,
            complexity_score=complexity,
            timestamp=datetime.now().isoformat()
        )
        
        self.patterns.append(pattern)
        self.save_patterns()
        
        return f"pattern_{len(self.patterns)}"
    
    def _calculate_complexity(self, files: List[str], conflicts: List[str]) -> float:
        """Calculate merge complexity score"""
        base_score = len(files) * 0.1
        conflict_score = len(conflicts) * 0.3
        
        # File type complexity
        type_score = 0
        for file_path in files:
            if file_path.endswith('.py'):
                type_score += 0.2
            elif file_path.endswith('.js'):
                type_score += 0.15
            elif file_path.endswith('.md'):
                type_score += 0.05
        
        return min(1.0, base_score + conflict_score + type_score)
    
    def analyze_success_patterns(self) -> Dict:
        """Analyze patterns that lead to successful merges"""
        successful = [p for p in self.patterns if p.success]
        failed = [p for p in self.patterns if not p.success]
        
        analysis = {
            "total_operations": len(self.patterns),
            "success_rate": len(successful) / max(1, len(self.patterns)),
            "avg_complexity_success": sum(p.complexity_score for p in successful) / max(1, len(successful)),
            "avg_complexity_failed": sum(p.complexity_score for p in failed) / max(1, len(failed)),
            "common_strategies": self._analyze_strategies(successful),
            "failure_patterns": self._analyze_failures(failed)
        }
        
        return analysis
    
    def _analyze_strategies(self, successful_patterns: List[MergePattern]) -> Dict:
        """Analyze successful resolution strategies"""
        strategies = {}
        for pattern in successful_patterns:
            strategy = pattern.resolution_strategy
            if strategy not in strategies:
                strategies[strategy] = {"count": 0, "avg_time": 0, "avg_complexity": 0}
            
            strategies[strategy]["count"] += 1
            strategies[strategy]["avg_time"] += pattern.time_taken
            strategies[strategy]["avg_complexity"] += pattern.complexity_score
        
        # Calculate averages
        for strategy_data in strategies.values():
            count = strategy_data["count"]
            strategy_data["avg_time"] /= count
            strategy_data["avg_complexity"] /= count
        
        return strategies
    
    def _analyze_failures(self, failed_patterns: List[MergePattern]) -> Dict:
        """Analyze failure patterns"""
        failure_analysis = {
            "common_conflicts": {},
            "high_risk_operations": [],
            "complexity_threshold": 0.0
        }
        
        # Analyze common conflicts
        for pattern in failed_patterns:
            for conflict in pattern.conflicts:
                failure_analysis["common_conflicts"][conflict] = \
                    failure_analysis["common_conflicts"].get(conflict, 0) + 1
        
        # Find complexity threshold for failures
        if failed_patterns:
            complexities = [p.complexity_score for p in failed_patterns]
            failure_analysis["complexity_threshold"] = min(complexities)
        
        return failure_analysis
    
    def predict_merge_success(self, files: List[str], estimated_conflicts: List[str] = None) -> Dict:
        """Predict success probability for a proposed merge"""
        if not self.patterns:
            return {"probability": 0.5, "confidence": "low", "recommendation": "proceed_with_caution"}
        
        complexity = self._calculate_complexity(files, estimated_conflicts or [])
        
        # Find similar patterns
        similar_patterns = []
        for pattern in self.patterns:
            if abs(pattern.complexity_score - complexity) < 0.2:
                similar_patterns.append(pattern)
        
        if not similar_patterns:
            return {"probability": 0.5, "confidence": "low", "recommendation": "no_similar_patterns"}
        
        # Calculate success probability
        successes = sum(1 for p in similar_patterns if p.success)
        probability = successes / len(similar_patterns)
        
        # Determine confidence
        confidence = "high" if len(similar_patterns) >= 5 else "medium" if len(similar_patterns) >= 2 else "low"
        
        # Generate recommendation
        if probability >= 0.8:
            recommendation = "proceed"
        elif probability >= 0.6:
            recommendation = "proceed_with_backup"
        else:
            recommendation = "high_risk_consider_alternatives"
        
        return {
            "probability": probability,
            "confidence": confidence,
            "recommendation": recommendation,
            "similar_operations": len(similar_patterns),
            "complexity_score": complexity
        }
    
    def suggest_optimal_strategy(self, files: List[str], conflicts: List[str] = None) -> Dict:
        """Suggest optimal merge strategy based on patterns"""
        complexity = self._calculate_complexity(files, conflicts or [])
        
        # Analyze successful strategies by complexity range
        analysis = self.analyze_success_patterns()
        strategies = analysis.get("common_strategies", {})
        
        # Find best strategy for this complexity level
        best_strategy = None
        best_score = 0
        
        for strategy, data in strategies.items():
            if abs(data["avg_complexity"] - complexity) < 0.3:
                # Score based on success rate and efficiency
                score = data["count"] / (data["avg_time"] + 1)
                if score > best_score:
                    best_score = score
                    best_strategy = strategy
        
        return {
            "recommended_strategy": best_strategy or "selective_merge",
            "estimated_time": strategies.get(best_strategy, {}).get("avg_time", 30.0),
            "confidence": "high" if best_strategy else "low",
            "alternatives": list(strategies.keys())[:3]
        }
    
    def save_patterns(self):
        """Save patterns to file"""
        data = {
            "patterns": [asdict(p) for p in self.patterns],
            "last_updated": datetime.now().isoformat()
        }
        
        with open(self.patterns_file, 'w') as f:
            json.dump(data, f, indent=2)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Merge pattern analyzer")
    parser.add_argument("command", choices=["record", "analyze", "predict", "strategy"])
    parser.add_argument("--files", nargs="+", help="Files involved in operation")
    parser.add_argument("--conflicts", nargs="*", help="Conflicts encountered")
    parser.add_argument("--success", action="store_true", help="Operation was successful")
    parser.add_argument("--strategy", help="Resolution strategy used")
    parser.add_argument("--time", type=float, default=0.0, help="Time taken")
    
    args = parser.parse_args()
    analyzer = MergePatternAnalyzer()
    
    if args.command == "record":
        if not args.files:
            print("Error: --files required for record command")
            return
        
        pattern_id = analyzer.record_merge_operation(
            operation_type="merge",
            files=args.files,
            success=args.success,
            conflicts=args.conflicts or [],
            strategy=args.strategy or "unknown",
            time_taken=args.time
        )
        
        print(f"✅ Recorded merge pattern: {pattern_id}")
    
    elif args.command == "analyze":
        analysis = analyzer.analyze_success_patterns()
        
        print("📊 Merge Pattern Analysis")
        print("=" * 25)
        print(f"Total Operations: {analysis['total_operations']}")
        print(f"Success Rate: {analysis['success_rate']:.1%}")
        print(f"Avg Complexity (Success): {analysis['avg_complexity_success']:.2f}")
        print(f"Avg Complexity (Failed): {analysis['avg_complexity_failed']:.2f}")
        
        print(f"\n🎯 Successful Strategies:")
        for strategy, data in analysis["common_strategies"].items():
            print(f"  {strategy}: {data['count']} uses, {data['avg_time']:.1f}min avg")
    
    elif args.command == "predict":
        if not args.files:
            print("Error: --files required for predict command")
            return
        
        prediction = analyzer.predict_merge_success(args.files, args.conflicts or [])
        
        print("🔮 Merge Success Prediction")
        print("=" * 25)
        print(f"Success Probability: {prediction['probability']:.1%}")
        print(f"Confidence: {prediction['confidence']}")
        print(f"Recommendation: {prediction['recommendation']}")
        print(f"Similar Operations: {prediction['similar_operations']}")
    
    elif args.command == "strategy":
        if not args.files:
            print("Error: --files required for strategy command")
            return
        
        strategy = analyzer.suggest_optimal_strategy(args.files, args.conflicts or [])
        
        print("🎯 Optimal Strategy Suggestion")
        print("=" * 30)
        print(f"Recommended: {strategy['recommended_strategy']}")
        print(f"Estimated Time: {strategy['estimated_time']:.1f} minutes")
        print(f"Confidence: {strategy['confidence']}")
        print(f"Alternatives: {', '.join(strategy['alternatives'])}")

if __name__ == "__main__":
    main()
