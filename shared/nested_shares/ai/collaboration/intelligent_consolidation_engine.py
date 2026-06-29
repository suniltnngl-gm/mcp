#!/usr/bin/env python3
"""Intelligent Consolidation Engine - Split/Merge existing systems to improve rather than create new"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict

@dataclass
class ConsolidationAction:
    action_type: str  # 'split', 'merge', 'enhance', 'refactor'
    source_systems: List[str]
    target_system: str
    reason: str
    improvement_type: str
    complexity: str  # 'low', 'medium', 'high'
    impact: str

from shared_tools.utils.config_utils import get_workspace_path

class IntelligentConsolidationEngine:
    def __init__(self):
        self.workspace_path = get_workspace_path()
        self.inventory_file = Path(__file__).parent / "SYSTEM_INVENTORY.json"
        self.consolidation_plan_file = Path(__file__).parent / "consolidation_plan.json"
        
    def analyze_consolidation_opportunities(self, task_description: str) -> Dict:
        """Analyze how to improve existing systems rather than create new ones"""
        
        print(f"🔍 ANALYZING CONSOLIDATION OPPORTUNITIES")
        print(f"Task: {task_description}")
        print("Strategy: Improve existing systems via split/merge/enhance\n")
        
        # Load system inventory
        if not self.inventory_file.exists():
            return {"error": "System inventory not found. Run system_inventory.py first"}
        
        inventory = json.loads(self.inventory_file.read_text())
        
        # Extract task requirements
        requirements = self._extract_task_requirements(task_description)
        
        # Find relevant existing systems
        relevant_systems = self._find_relevant_systems(inventory, requirements)
        
        # Analyze consolidation opportunities
        consolidation_actions = self._analyze_consolidation_actions(relevant_systems, requirements)
        
        # Create improvement plan
        improvement_plan = self._create_improvement_plan(consolidation_actions)
        
        return {
            "task": task_description,
            "requirements": requirements,
            "relevant_systems": relevant_systems,
            "consolidation_actions": consolidation_actions,
            "improvement_plan": improvement_plan,
            "recommendation": self._generate_recommendation(consolidation_actions)
        }
    
    def _extract_task_requirements(self, task: str) -> Dict:
        """Extract what the task actually needs"""
        
        task_lower = task.lower()
        
        requirements = {
            "functionality": [],
            "performance": [],
            "integration": [],
            "scalability": []
        }
        
        # Functionality requirements
        if "duplicate" in task_lower:
            requirements["functionality"].extend(["duplicate_detection", "file_comparison", "safe_removal"])
        if "ai" in task_lower or "orchestrat" in task_lower:
            requirements["functionality"].extend(["ai_coordination", "provider_selection", "cost_optimization"])
        if "review" in task_lower:
            requirements["functionality"].extend(["code_analysis", "quality_check", "feedback_generation"])
        if "file" in task_lower:
            requirements["functionality"].extend(["file_management", "registry", "tracking"])
        
        # Performance requirements
        if "fast" in task_lower or "quick" in task_lower:
            requirements["performance"].append("speed_optimization")
        if "scale" in task_lower:
            requirements["performance"].append("scalability")
        
        # Integration requirements
        if "workflow" in task_lower:
            requirements["integration"].append("workflow_integration")
        if "api" in task_lower:
            requirements["integration"].append("api_integration")
        
        return requirements
    
    def _find_relevant_systems(self, inventory: Dict, requirements: Dict) -> List[Dict]:
        """Find existing systems relevant to requirements"""
        
        relevant = []
        
        for system_id, system_info in inventory.get("systems", {}).items():
            relevance_score = 0
            
            # Check functionality match
            for func in requirements["functionality"]:
                if func in system_info["name"].lower() or func in system_info["path"].lower():
                    relevance_score += 3
                
                # Check API methods
                for method in system_info.get("api_methods", []):
                    if func in method.lower():
                        relevance_score += 2
            
            # Check category match
            category = system_info.get("category", "")
            for func in requirements["functionality"]:
                if func in category:
                    relevance_score += 1
            
            if relevance_score > 0:
                system_info["relevance_score"] = relevance_score
                relevant.append(system_info)
        
        # Sort by relevance
        return sorted(relevant, key=lambda x: x["relevance_score"], reverse=True)[:10]
    
    def _analyze_consolidation_actions(self, relevant_systems: List[Dict], requirements: Dict) -> List[ConsolidationAction]:
        """Analyze what consolidation actions would improve existing systems"""
        
        actions = []
        
        # Group systems by functionality
        functionality_groups = {}
        for system in relevant_systems:
            for func in requirements["functionality"]:
                if func in system["name"].lower() or func in system["path"].lower():
                    if func not in functionality_groups:
                        functionality_groups[func] = []
                    functionality_groups[func].append(system)
        
        # Analyze each functionality group
        for func, systems in functionality_groups.items():
            if len(systems) > 1:
                # Multiple systems doing similar things - MERGE opportunity
                actions.append(ConsolidationAction(
                    action_type="merge",
                    source_systems=[s["name"] for s in systems],
                    target_system=f"unified_{func}_system",
                    reason=f"Multiple systems ({len(systems)}) handling {func} - consolidate for efficiency",
                    improvement_type="reduce_redundancy",
                    complexity="medium",
                    impact="high"
                ))
            
            elif len(systems) == 1:
                system = systems[0]
                
                # Single system - check if it needs SPLITTING or ENHANCEMENT
                if system["size"] > 10000:  # Large system
                    actions.append(ConsolidationAction(
                        action_type="split",
                        source_systems=[system["name"]],
                        target_system=f"modular_{func}_components",
                        reason=f"Large system ({system['size']} bytes) - split into focused modules",
                        improvement_type="improve_modularity",
                        complexity="high",
                        impact="medium"
                    ))
                
                else:
                    # Check if enhancement is needed
                    missing_requirements = self._find_missing_requirements(system, requirements)
                    if missing_requirements:
                        actions.append(ConsolidationAction(
                            action_type="enhance",
                            source_systems=[system["name"]],
                            target_system=f"enhanced_{system['name']}",
                            reason=f"Add missing capabilities: {', '.join(missing_requirements)}",
                            improvement_type="add_functionality",
                            complexity="low",
                            impact="medium"
                        ))
        
        return actions
    
    def _find_missing_requirements(self, system: Dict, requirements: Dict) -> List[str]:
        """Find what requirements are missing from existing system"""
        
        missing = []
        system_content = system["name"].lower() + " ".join(system.get("api_methods", []))
        
        for func in requirements["functionality"]:
            if func not in system_content:
                missing.append(func)
        
        return missing
    
    def _create_improvement_plan(self, actions: List[ConsolidationAction]) -> Dict:
        """Create detailed improvement plan"""
        
        plan = {
            "strategy": "improve_existing_systems",
            "total_actions": len(actions),
            "phases": {
                "phase_1_merge": [],
                "phase_2_enhance": [],
                "phase_3_split": []
            },
            "expected_outcomes": []
        }
        
        # Organize actions by type and complexity
        for action in actions:
            action_dict = asdict(action)
            
            if action.action_type == "merge":
                plan["phases"]["phase_1_merge"].append(action_dict)
            elif action.action_type == "enhance":
                plan["phases"]["phase_2_enhance"].append(action_dict)
            elif action.action_type == "split":
                plan["phases"]["phase_3_split"].append(action_dict)
        
        # Expected outcomes
        merge_count = len(plan["phases"]["phase_1_merge"])
        enhance_count = len(plan["phases"]["phase_2_enhance"])
        split_count = len(plan["phases"]["phase_3_split"])
        
        if merge_count > 0:
            plan["expected_outcomes"].append(f"Reduce redundancy by merging {merge_count} system groups")
        if enhance_count > 0:
            plan["expected_outcomes"].append(f"Improve functionality by enhancing {enhance_count} systems")
        if split_count > 0:
            plan["expected_outcomes"].append(f"Improve modularity by splitting {split_count} large systems")
        
        return plan
    
    def _generate_recommendation(self, actions: List[ConsolidationAction]) -> Dict:
        """Generate final recommendation"""
        
        if not actions:
            return {
                "action": "CREATE_NEW",
                "reason": "No existing systems found for improvement",
                "priority": "LOW"
            }
        
        # Prioritize by impact and complexity
        high_impact_actions = [a for a in actions if a.impact == "high"]
        low_complexity_actions = [a for a in actions if a.complexity == "low"]
        
        if high_impact_actions:
            primary_action = high_impact_actions[0]
            return {
                "action": f"{primary_action.action_type.upper()}_EXISTING",
                "reason": f"High impact improvement: {primary_action.reason}",
                "priority": "HIGH",
                "next_step": f"{primary_action.action_type} {primary_action.source_systems[0]}"
            }
        
        elif low_complexity_actions:
            primary_action = low_complexity_actions[0]
            return {
                "action": f"{primary_action.action_type.upper()}_EXISTING",
                "reason": f"Low complexity improvement: {primary_action.reason}",
                "priority": "MEDIUM",
                "next_step": f"{primary_action.action_type} {primary_action.source_systems[0]}"
            }
        
        else:
            return {
                "action": "ENHANCE_EXISTING",
                "reason": "Multiple improvement opportunities available",
                "priority": "MEDIUM",
                "next_step": "Start with lowest complexity action"
            }
    
    def execute_consolidation_action(self, action: ConsolidationAction) -> Dict:
        """Execute a specific consolidation action"""
        
        print(f"🔧 EXECUTING: {action.action_type.upper()}")
        print(f"Target: {action.target_system}")
        print(f"Reason: {action.reason}\n")
        
        if action.action_type == "merge":
            return self._execute_merge(action)
        elif action.action_type == "split":
            return self._execute_split(action)
        elif action.action_type == "enhance":
            return self._execute_enhance(action)
        else:
            return {"error": f"Unknown action type: {action.action_type}"}
    
    def _execute_merge(self, action: ConsolidationAction) -> Dict:
        """Execute merge consolidation"""
        return {
            "action": "MERGE_PLANNED",
            "source_systems": action.source_systems,
            "target": action.target_system,
            "next_steps": [
                "Analyze APIs of source systems",
                "Design unified interface",
                "Implement merged system",
                "Test integration",
                "Deprecate source systems"
            ]
        }
    
    def _execute_split(self, action: ConsolidationAction) -> Dict:
        """Execute split consolidation"""
        return {
            "action": "SPLIT_PLANNED",
            "source_system": action.source_systems[0],
            "target": action.target_system,
            "next_steps": [
                "Analyze system components",
                "Identify split boundaries",
                "Create modular components",
                "Test component integration",
                "Update system architecture"
            ]
        }
    
    def _execute_enhance(self, action: ConsolidationAction) -> Dict:
        """Execute enhancement consolidation"""
        return {
            "action": "ENHANCE_PLANNED",
            "source_system": action.source_systems[0],
            "target": action.target_system,
            "next_steps": [
                "Identify enhancement points",
                "Design new functionality",
                "Implement enhancements",
                "Test enhanced system",
                "Update documentation"
            ]
        }

def demonstrate_intelligent_consolidation():
    """Demonstrate intelligent consolidation approach"""
    
    engine = IntelligentConsolidationEngine()
    
    test_tasks = [
        "Create duplicate file detector",
        "Build AI orchestration system",
        "Develop code review workflow"
    ]
    
    print("=== INTELLIGENT CONSOLIDATION ENGINE ===\n")
    
    for task in test_tasks:
        result = engine.analyze_consolidation_opportunities(task)
        
        if "error" not in result:
            print(f"📊 Found {len(result['relevant_systems'])} relevant systems")
            print(f"🔧 Consolidation actions: {len(result['consolidation_actions'])}")
            print(f"🎯 Recommendation: {result['recommendation']['action']}")
            print(f"💡 Reason: {result['recommendation']['reason']}")
            
            if result['consolidation_actions']:
                action = result['consolidation_actions'][0]
                print(f"🔄 Primary action: {action['action_type']} - {action['reason']}")
        
        print("-" * 60)

if __name__ == "__main__":
    demonstrate_intelligent_consolidation()
