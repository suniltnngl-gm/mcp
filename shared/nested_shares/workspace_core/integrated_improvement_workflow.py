#!/usr/bin/env python3
"""Integrated Automated Improvement Workflow - Complete lean improvement system"""

from shared_tools.utils.config_utils import get_workspace_path
import json
from pathlib import Path
from datetime import datetime
from automated_duplicate_detection import AutomatedDuplicateDetection
from lean_systematic_improvements import LeanSystematicImprovements

class IntegratedImprovementWorkflow:
    def __init__(self):
        self.workspace_path = get_workspace_path()
        self.duplicate_detector = AutomatedDuplicateDetection()
        self.lean_improvements = LeanSystematicImprovements()
        
        # Registry paths
        self.error_registry_path = self.workspace_path / "shared-tools" / "nested-shares" / "ai" / "collaboration" / "enhanced_file_registry.json"
        self.results_path = self.workspace_path / ".versions" / "integrated_workflow_results.json"
        
    def load_error_registry(self) -> dict:
        """Load error registry for improvement guidance"""
        if self.error_registry_path.exists():
            try:
                with open(self.error_registry_path) as f:
                    data = json.load(f)
                    # Handle both dict and list formats
                    if isinstance(data, list):
                        return {"error_patterns": data, "improvement_history": []}
                    return data
            except:
                pass
        return {"error_patterns": [], "improvement_history": []}
    
    def apply_lean_improvement(self, duplicate_info: dict) -> dict:
        """Apply lean improvement workflow to a duplicate"""
        
        files = duplicate_info['files']
        primary_file = files[0]  # Use first file as primary
        
        print(f"🔄 APPLYING LEAN IMPROVEMENT: {Path(primary_file).name}")
        
        # Start lean improvement workflow
        workflow_result = self.lean_improvements.lean_improvement_workflow(
            primary_file,
            "duplicate_refactor",
            "integrated_workflow_automation",
            f"Refactoring duplicate code found in {len(files)} files"
        )
        
        if workflow_result.get("workflow_status") != "ready_for_improvement":
            return {"error": "Failed to start lean improvement", "result": workflow_result}
        
        # Create improvement plan
        improvement_plan = {
            "type": "duplicate_refactor",
            "primary_file": primary_file,
            "duplicate_files": files[1:],
            "snippet_info": duplicate_info,
            "pre_version_id": workflow_result["pre_version_id"],
            "improvement_strategy": self._determine_strategy(duplicate_info),
            "status": "ready_for_manual_implementation"
        }
        
        return {
            "improvement_started": True,
            "plan": improvement_plan,
            "next_steps": [
                "Review duplicate code in all files",
                "Extract common function/class to shared module",
                "Update all files to use shared implementation",
                "Call finalize_lean_improvement() when complete"
            ]
        }
    
    def _determine_strategy(self, duplicate_info: dict) -> str:
        """Determine improvement strategy based on duplicate characteristics"""
        
        size = duplicate_info['size']
        count = duplicate_info['count']
        snippet_type = duplicate_info['type']
        
        if snippet_type == 'function' and count >= 3:
            return "extract_to_shared_module"
        elif snippet_type == 'function' and size < 200:
            return "inline_refactor"
        elif count == 2 and size < 300:
            return "merge_implementations"
        else:
            return "manual_review_required"
    
    def update_error_registry(self, improvement_result: dict):
        """Update error registry with improvement learnings"""
        
        error_registry = self.load_error_registry()
        
        # Add improvement to history
        improvement_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "duplicate_refactor",
            "files_involved": improvement_result.get("files_involved", []),
            "strategy_used": improvement_result.get("strategy", "unknown"),
            "success": improvement_result.get("success", False),
            "lessons_learned": improvement_result.get("lessons", [])
        }
        
        if "improvement_history" not in error_registry:
            error_registry["improvement_history"] = []
        
        error_registry["improvement_history"].append(improvement_entry)
        
        # Keep only recent 50 entries
        error_registry["improvement_history"] = error_registry["improvement_history"][-50:]
        
        # Save updated registry
        self.error_registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.error_registry_path.write_text(json.dumps(error_registry, indent=2))
    
    def run_complete_workflow(self) -> dict:
        """Run complete integrated improvement workflow"""
        
        print("🚀 INTEGRATED AUTOMATED IMPROVEMENT WORKFLOW")
        print("Combining: Duplicate Detection + Lean Versioning + Error Registry\n")
        
        workflow_start = datetime.now()
        
        # Step 1: Run duplicate detection
        print("📋 Step 1: Automated Duplicate Detection")
        detection_results = self.duplicate_detector.run_automated_detection()
        
        # Step 2: Load error registry for guidance
        print("\n🧠 Step 2: Loading Error Registry")
        error_registry = self.load_error_registry()
        print(f"   Loaded {len(error_registry.get('improvement_history', []))} previous improvements")
        
        # Step 3: Apply lean improvements to top duplicates
        print("\n🔄 Step 3: Applying Lean Improvements")
        improvement_results = []
        
        priority_list = detection_results.get('priority_list', [])
        top_duplicates = priority_list[:3]  # Process top 3
        
        for i, duplicate in enumerate(top_duplicates, 1):
            print(f"\n   Processing duplicate {i}/{len(top_duplicates)}...")
            
            improvement_result = self.apply_lean_improvement(duplicate)
            improvement_results.append(improvement_result)
            
            # Update error registry with each improvement
            if improvement_result.get("improvement_started"):
                self.update_error_registry({
                    "files_involved": duplicate['files'],
                    "strategy": improvement_result['plan']['improvement_strategy'],
                    "success": True,
                    "lessons": ["Automated detection successful", "Lean workflow initiated"]
                })
        
        # Step 4: Compile complete results
        workflow_duration = (datetime.now() - workflow_start).total_seconds()
        
        complete_results = {
            "workflow_type": "integrated_automated_improvement",
            "workflow_duration": f"{workflow_duration:.2f}s",
            "detection_results": detection_results,
            "improvement_results": improvement_results,
            "error_registry_updated": True,
            "summary": {
                "duplicates_found": detection_results['summary']['total_duplicates'],
                "improvements_initiated": len([r for r in improvement_results if r.get("improvement_started")]),
                "files_processed": detection_results['summary']['files_analyzed'],
                "lean_workflows_started": len(improvement_results)
            },
            "next_actions": [
                "Review improvement plans for manual implementation",
                "Execute refactoring according to determined strategies",
                "Call finalize_lean_improvement() for each completed improvement",
                "Monitor error registry for learning patterns"
            ],
            "completed_at": datetime.now().isoformat()
        }
        
        # Step 5: Save complete results
        self.results_path.write_text(json.dumps(complete_results, indent=2))
        
        # Step 6: Display summary
        print(f"\n📊 INTEGRATED WORKFLOW COMPLETE:")
        print(f"   Duration: {workflow_duration:.2f}s")
        print(f"   Duplicates found: {complete_results['summary']['duplicates_found']}")
        print(f"   Improvements initiated: {complete_results['summary']['improvements_initiated']}")
        print(f"   Error registry updated: ✅")
        
        print(f"\n🎯 READY FOR MANUAL IMPLEMENTATION:")
        for i, result in enumerate(improvement_results, 1):
            if result.get("improvement_started"):
                plan = result['plan']
                print(f"   {i}. {plan['improvement_strategy']} in {Path(plan['primary_file']).name}")
        
        print(f"\n💾 Complete results: {self.results_path}")
        
        return complete_results

def main():
    """Run complete integrated improvement workflow"""
    
    workflow = IntegratedImprovementWorkflow()
    results = workflow.run_complete_workflow()
    
    print(f"\n✅ INTEGRATED AUTOMATED IMPROVEMENT WORKFLOW COMPLETE")
    print(f"🎯 System inventory, error registry, file registry, and lean versioning all integrated!")

if __name__ == "__main__":
    main()
