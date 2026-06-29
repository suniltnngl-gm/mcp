#!/usr/bin/env python3
"""Integration Planner - Plan discussion_manager + ai_orchestra merge"""

import json
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class IntegrationStep:
    step: int
    action: str
    description: str
    files_affected: List[str]
    risk_level: str
    estimated_time: str

class IntegrationPlanner:
    def __init__(self):
        self.base_path = Path(__file__).parent
    
    def analyze_current_state(self) -> Dict:
        """Analyze current discussion_manager and ai_orchestra state"""
        
        discussion_path = self.base_path.parent / "discussions" / "discussion_manager.py"
        orchestra_path = self.base_path / "ai_orchestra.py"
        
        state = {
            "discussion_manager": {
                "exists": discussion_path.exists(),
                "path": str(discussion_path),
                "features": ["persistent_discussions", "tracking_integration", "message_management"]
            },
            "ai_orchestra": {
                "exists": orchestra_path.exists(), 
                "path": str(orchestra_path),
                "features": ["multi_agent_collaboration", "memory_system", "rich_output"]
            },
            "integration_ready": discussion_path.exists() and orchestra_path.exists()
        }
        
        return state
    
    def create_integration_plan(self) -> List[IntegrationStep]:
        """Create step-by-step integration plan"""
        
        steps = [
            IntegrationStep(
                step=1,
                action="backup_files",
                description="Create backup of both files before integration",
                files_affected=["discussion_manager.py", "ai_orchestra.py"],
                risk_level="low",
                estimated_time="2 minutes"
            ),
            IntegrationStep(
                step=2,
                action="extract_ai_interface",
                description="Extract AI provider interface from ai_orchestra for reuse",
                files_affected=["ai_orchestra.py"],
                risk_level="medium",
                estimated_time="15 minutes"
            ),
            IntegrationStep(
                step=3,
                action="add_orchestra_to_discussion",
                description="Import and integrate AIOrchestra class into DiscussionManager",
                files_affected=["discussion_manager.py"],
                risk_level="medium", 
                estimated_time="20 minutes"
            ),
            IntegrationStep(
                step=4,
                action="implement_real_ai_responses",
                description="Replace mock AI responses with actual AI calls via orchestra",
                files_affected=["discussion_manager.py"],
                risk_level="high",
                estimated_time="30 minutes"
            ),
            IntegrationStep(
                step=5,
                action="integrate_smart_router",
                description="Use smart_ai_router for cost-optimized provider selection",
                files_affected=["discussion_manager.py"],
                risk_level="medium",
                estimated_time="15 minutes"
            ),
            IntegrationStep(
                step=6,
                action="preserve_tracking",
                description="Ensure session and action tracking remains functional",
                files_affected=["discussion_manager.py"],
                risk_level="low",
                estimated_time="10 minutes"
            ),
            IntegrationStep(
                step=7,
                action="test_integration",
                description="Test complete workflow with real AI responses",
                files_affected=["discussion_manager.py"],
                risk_level="low",
                estimated_time="15 minutes"
            ),
            IntegrationStep(
                step=8,
                action="update_documentation",
                description="Update docs to reflect real AI integration",
                files_affected=["README.md", "AI_DISCUSSION_SYSTEM.md"],
                risk_level="low",
                estimated_time="10 minutes"
            )
        ]
        
        return steps
    
    def estimate_total_time(self, steps: List[IntegrationStep]) -> str:
        """Estimate total integration time"""
        time_map = {
            "2 minutes": 2,
            "10 minutes": 10, 
            "15 minutes": 15,
            "20 minutes": 20,
            "30 minutes": 30
        }
        
        total_minutes = sum(time_map.get(step.estimated_time, 15) for step in steps)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def get_risk_summary(self, steps: List[IntegrationStep]) -> Dict:
        """Summarize integration risks"""
        risks = {"low": 0, "medium": 0, "high": 0}
        
        for step in steps:
            risks[step.risk_level] += 1
        
        return risks
    
    def save_plan(self, steps: List[IntegrationStep], output_file: str = "integration_plan.json"):
        """Save integration plan to file"""
        plan_data = {
            "created": str(Path(__file__).stat().st_mtime),
            "total_steps": len(steps),
            "estimated_time": self.estimate_total_time(steps),
            "risk_summary": self.get_risk_summary(steps),
            "steps": [
                {
                    "step": s.step,
                    "action": s.action,
                    "description": s.description,
                    "files_affected": s.files_affected,
                    "risk_level": s.risk_level,
                    "estimated_time": s.estimated_time
                }
                for s in steps
            ]
        }
        
        output_path = self.base_path / output_file
        with open(output_path, 'w') as f:
            json.dump(plan_data, f, indent=2)
        
        return output_path

def main():
    import sys
    
    planner = IntegrationPlanner()
    
    # Analyze current state
    state = planner.analyze_current_state()
    
    print("🔍 Current State Analysis")
    print("=" * 30)
    print(f"Discussion Manager: {'✅' if state['discussion_manager']['exists'] else '❌'}")
    print(f"AI Orchestra: {'✅' if state['ai_orchestra']['exists'] else '❌'}")
    print(f"Integration Ready: {'✅' if state['integration_ready'] else '❌'}")
    
    if not state['integration_ready']:
        print("\n❌ Missing required files for integration")
        sys.exit(1)
    
    # Create integration plan
    steps = planner.create_integration_plan()
    
    print(f"\n📋 Integration Plan ({len(steps)} steps)")
    print("=" * 40)
    
    for step in steps:
        risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}[step.risk_level]
        print(f"\n{step.step}. {step.action} {risk_emoji}")
        print(f"   {step.description}")
        print(f"   Time: {step.estimated_time} | Files: {', '.join(step.files_affected)}")
    
    # Summary
    total_time = planner.estimate_total_time(steps)
    risks = planner.get_risk_summary(steps)
    
    print(f"\n📊 Summary")
    print(f"Total Time: {total_time}")
    print(f"Risk Levels: 🟢{risks['low']} 🟡{risks['medium']} 🔴{risks['high']}")
    
    # Save plan
    if len(sys.argv) > 1 and sys.argv[1] == "--save":
        plan_file = planner.save_plan(steps)
        print(f"\n💾 Plan saved to: {plan_file}")

if __name__ == "__main__":
    main()
