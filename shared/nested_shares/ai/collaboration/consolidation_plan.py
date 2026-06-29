#!/usr/bin/env python3
"""Consolidation plan for roadmap/todo/progress files"""

import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict

@dataclass
class ConsolidationAction:
    action: str  # 'merge', 'delete', 'move', 'keep'
    source_files: List[str]
    target_file: str
    reason: str

class ConsolidationPlanner:
    def __init__(self):
        self.base_path = Path(__file__).parent
        
    def create_plan(self) -> Dict:
        """Create comprehensive consolidation plan"""
        
        # Key orchestration files to keep and enhance
        keep_files = [
            "/media/sunil-kr/workspace/user-projects/shared-tools/nested-shares/ai/orchestration/IMPROVEMENT_ROADMAP.md",
            "/media/sunil-kr/workspace/user-projects/shared-tools/nested-shares/ai/orchestration/roadmap_data.json", 
            "/media/sunil-kr/workspace/user-projects/shared-tools/nested-shares/ai/orchestration/roadmap_metrics.json",
            "/media/sunil-kr/workspace/user-projects/shared-tools/nested-shares/ai/orchestration/progress_tracker.py"
        ]
        
        actions = [
            ConsolidationAction(
                action="keep",
                source_files=keep_files,
                target_file="orchestration/unified_roadmap.json",
                reason="Core orchestration files - consolidate into unified system"
            ),
            ConsolidationAction(
                action="mark_for_review/archive",
                source_files=["archive duplicate files (40 identified)"],
                target_file="",
                reason="Identified duplicates in archive - to be reviewed and managed, not deleted."
            ),
            ConsolidationAction(
                action="merge",
                source_files=[
                    "IMPROVEMENT_ROADMAP.md",
                    "SAFETY_INTEGRATED_ROADMAP.md"
                ],
                target_file="orchestration/MASTER_ROADMAP.md",
                reason="Combine roadmap documents into single source"
            )
        ]
        
        plan = {
            "total_files": 44,
            "duplicates_to_remove": 40,
            "files_to_consolidate": 4,
            "actions": [asdict(action) for action in actions],
            "suggested_next_steps": [
                "Review consolidation_plan.json for detailed actions.",
                "cd shared-tools/nested-shares/ai/orchestration/",
                "python3 ../collaboration/consolidation_plan.py --execute"
            ]
        }
        
        # Save plan
        plan_file = self.base_path / "consolidation_plan.json"
        plan_file.write_text(json.dumps(plan, indent=2))
        
        return plan

if __name__ == "__main__":
    planner = ConsolidationPlanner()
    plan = planner.create_plan()
    print(f"Consolidation plan: {plan['duplicates_to_remove']} duplicates, {plan['files_to_consolidate']} to merge")
