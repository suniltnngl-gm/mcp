#!/usr/bin/env python3
"""Fine-Tuned System Detection - Intelligent split/merge consolidation instead of immediate use or creation"""

from pathlib import Path
from intelligent_consolidation_engine import IntelligentConsolidationEngine, ConsolidationAction

class FineTunedSystemDetection:
    def __init__(self):
        self.consolidation_engine = IntelligentConsolidationEngine()
        self.workspace_path = Path("/media/sunil-kr/workspace/user-projects")
        
    def intelligent_system_approach(self, task_description: str) -> dict:
        """Fine-tuned approach: Detect → Analyze → Consolidate → Improve"""
        
        print("🎯 FINE-TUNED SYSTEM DETECTION")
        print("Strategy: Split/Merge/Enhance existing systems for improvement\n")
        
        # Phase 1: Detect existing systems
        detection_result = self._detect_systems_intelligently(task_description)
        
        # Phase 2: Analyze consolidation opportunities  
        consolidation_analysis = self.consolidation_engine.analyze_consolidation_opportunities(task_description)
        
        # Phase 3: Create improvement strategy
        improvement_strategy = self._create_improvement_strategy(detection_result, consolidation_analysis)
        
        # Phase 4: Generate action plan
        action_plan = self._generate_action_plan(improvement_strategy)
        
        return {
            "approach": "INTELLIGENT_CONSOLIDATION",
            "detection": detection_result,
            "consolidation": consolidation_analysis,
            "improvement_strategy": improvement_strategy,
            "action_plan": action_plan
        }
    
    def _detect_systems_intelligently(self, task: str) -> dict:
        """Intelligent detection focusing on improvement opportunities"""
        
        # Extract task keywords
        keywords = self._extract_smart_keywords(task)
        
        # Find systems with improvement potential
        systems_with_potential = self._find_systems_with_potential(keywords)
        
        # Analyze system quality and improvement needs
        quality_analysis = self._analyze_system_quality(systems_with_potential)
        
        return {
            "task_keywords": keywords,
            "systems_found": len(systems_with_potential),
            "improvement_candidates": systems_with_potential,
            "quality_analysis": quality_analysis
        }
    
    def _extract_smart_keywords(self, task: str) -> dict:
        """Extract keywords with context for intelligent matching"""
        
        task_lower = task.lower()
        
        # Smart keyword extraction with context
        keywords = {
            "primary_function": [],
            "quality_aspects": [],
            "integration_needs": [],
            "performance_needs": []
        }
        
        # Primary function keywords
        function_map = {
            "duplicate": ["duplicate", "dedup", "consolidate", "merge"],
            "ai_orchestration": ["ai", "orchestrate", "coordinate", "manage"],
            "code_review": ["review", "analyze", "check", "validate"],
            "file_management": ["file", "track", "registry", "catalog"],
            "automation": ["automate", "script", "workflow", "process"]
        }
        
        for category, terms in function_map.items():
            if any(term in task_lower for term in terms):
                keywords["primary_function"].extend(terms)
        
        # Quality aspects
        if any(word in task_lower for word in ["better", "improve", "enhance", "optimize"]):
            keywords["quality_aspects"].extend(["improvement", "optimization", "enhancement"])
        
        if any(word in task_lower for word in ["fast", "quick", "efficient"]):
            keywords["quality_aspects"].extend(["performance", "speed", "efficiency"])
        
        # Integration needs
        if any(word in task_lower for word in ["integrate", "connect", "combine"]):
            keywords["integration_needs"].extend(["integration", "connectivity", "interoperability"])
        
        return keywords
    
    def _find_systems_with_potential(self, keywords: dict) -> list:
        """Find systems that have improvement potential"""
        
        potential_systems = []
        
        # Search patterns based on keywords
        search_patterns = []
        search_patterns.extend(keywords.get("primary_function", []))
        
        for pattern in search_patterns:
            for file_path in self.workspace_path.rglob(f"*{pattern}*"):
                if self._is_improvement_candidate(file_path):
                    system_info = self._analyze_system_potential(file_path, keywords)
                    if system_info:
                        potential_systems.append(system_info)
        
        # Remove duplicates and sort by potential
        unique_systems = {}
        for system in potential_systems:
            key = system["path"]
            if key not in unique_systems or system["improvement_potential"] > unique_systems[key]["improvement_potential"]:
                unique_systems[key] = system
        
        return sorted(unique_systems.values(), key=lambda x: x["improvement_potential"], reverse=True)[:10]
    
    def _is_improvement_candidate(self, file_path: Path) -> bool:
        """Check if system is a candidate for improvement"""
        
        # Skip excluded paths
        exclude_patterns = ["archive/", ".git/", ".venv/", "node_modules/", "__pycache__/"]
        path_str = str(file_path)
        
        if any(pattern in path_str for pattern in exclude_patterns):
            return False
        
        # Include relevant file types
        if file_path.is_file() and file_path.suffix in ['.py', '.sh', '.md']:
            return True
        
        return False
    
    def _analyze_system_potential(self, file_path: Path, keywords: dict) -> dict:
        """Analyze system's improvement potential"""
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            stat = file_path.stat()
            
            # Calculate improvement potential score
            potential_score = 0
            improvement_reasons = []
            
            # Size-based potential
            if stat.st_size > 10000:  # Large files - split potential
                potential_score += 3
                improvement_reasons.append("Large system - split potential")
            elif stat.st_size < 1000:  # Small files - merge potential
                potential_score += 2
                improvement_reasons.append("Small system - merge potential")
            
            # Content-based potential
            if "TODO" in content or "FIXME" in content:
                potential_score += 2
                improvement_reasons.append("Has TODO/FIXME - enhancement potential")
            
            if "DEPRECATED" in content:
                potential_score += 1
                improvement_reasons.append("Deprecated - replacement potential")
            
            # Functionality overlap potential
            function_keywords = keywords.get("primary_function", [])
            matches = sum(1 for keyword in function_keywords if keyword in content.lower())
            if matches > 1:
                potential_score += matches
                improvement_reasons.append(f"Multiple function matches - consolidation potential")
            
            # API complexity potential
            if file_path.suffix == '.py':
                method_count = content.count('def ')
                if method_count > 20:  # Complex system
                    potential_score += 2
                    improvement_reasons.append("Complex API - refactoring potential")
            
            return {
                "name": file_path.name,
                "path": str(file_path.relative_to(self.workspace_path)),
                "size": stat.st_size,
                "improvement_potential": potential_score,
                "improvement_reasons": improvement_reasons,
                "type": file_path.suffix,
                "function_matches": matches if 'matches' in locals() else 0
            }
        
        except Exception:
            return None
    
    def _analyze_system_quality(self, systems: list) -> dict:
        """Analyze overall quality and improvement opportunities"""
        
        analysis = {
            "total_systems": len(systems),
            "high_potential": [],
            "medium_potential": [],
            "low_potential": [],
            "consolidation_opportunities": {
                "merge_candidates": [],
                "split_candidates": [],
                "enhance_candidates": []
            }
        }
        
        for system in systems:
            potential = system["improvement_potential"]
            
            if potential >= 5:
                analysis["high_potential"].append(system)
            elif potential >= 3:
                analysis["medium_potential"].append(system)
            else:
                analysis["low_potential"].append(system)
            
            # Categorize by consolidation type
            if system["size"] > 10000:
                analysis["consolidation_opportunities"]["split_candidates"].append(system)
            elif system["size"] < 1000 and system["function_matches"] > 0:
                analysis["consolidation_opportunities"]["merge_candidates"].append(system)
            else:
                analysis["consolidation_opportunities"]["enhance_candidates"].append(system)
        
        return analysis
    
    def _create_improvement_strategy(self, detection: dict, consolidation: dict) -> dict:
        """Create intelligent improvement strategy"""
        
        strategy = {
            "approach": "CONSOLIDATION_FIRST",
            "rationale": "Improve existing systems through intelligent split/merge/enhance",
            "priorities": [],
            "phases": {}
        }
        
        # Determine priorities based on analysis
        high_potential = detection["quality_analysis"]["high_potential"]
        consolidation_actions = consolidation.get("consolidation_actions", [])
        
        if high_potential and consolidation_actions:
            strategy["priorities"] = [
                "Consolidate high-potential systems first",
                "Execute high-impact consolidation actions",
                "Enhance systems with clear improvement paths"
            ]
        elif high_potential:
            strategy["priorities"] = [
                "Focus on high-potential systems",
                "Analyze consolidation opportunities",
                "Plan systematic improvements"
            ]
        else:
            strategy["priorities"] = [
                "Identify improvement opportunities",
                "Start with low-complexity enhancements",
                "Build consolidation momentum"
            ]
        
        # Create phased approach
        strategy["phases"] = {
            "phase_1": "Analyze and plan consolidation",
            "phase_2": "Execute high-impact improvements", 
            "phase_3": "Systematic enhancement and optimization"
        }
        
        return strategy
    
    def _generate_action_plan(self, strategy: dict) -> dict:
        """Generate specific action plan"""
        
        return {
            "immediate_actions": [
                "Review high-potential systems for consolidation",
                "Plan merge/split/enhance operations",
                "Execute lowest-risk improvements first"
            ],
            "success_metrics": [
                "Reduced system redundancy",
                "Improved system modularity",
                "Enhanced functionality without new creation"
            ],
            "next_steps": [
                "Execute consolidation actions",
                "Monitor improvement impact",
                "Iterate on consolidation strategy"
            ]
        }

def main():
    """Demonstrate fine-tuned system detection"""
    
    detector = FineTunedSystemDetection()
    
    test_tasks = [
        "Create better duplicate file detector",
        "Improve AI orchestration system",
        "Enhance code review workflow"
    ]
    
    print("=== FINE-TUNED SYSTEM DETECTION ===\n")
    
    for task in test_tasks:
        result = detector.intelligent_system_approach(task)
        
        print(f"📊 Systems found: {result['detection']['systems_found']}")
        print(f"🎯 High potential: {len(result['detection']['quality_analysis']['high_potential'])}")
        print(f"🔧 Consolidation actions: {len(result['consolidation'].get('consolidation_actions', []))}")
        print(f"💡 Strategy: {result['improvement_strategy']['approach']}")
        print(f"🚀 Priority: {result['improvement_strategy']['priorities'][0] if result['improvement_strategy']['priorities'] else 'None'}")
        print("-" * 60)

if __name__ == "__main__":
    main()
