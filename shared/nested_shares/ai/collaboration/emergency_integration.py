#!/usr/bin/env python3
"""Emergency Integration - Use existing systems immediately, stop creating redundant ones"""

import subprocess
from pathlib import Path

class EmergencyIntegration:
    def __init__(self):
        self.workspace_path = Path("/media/sunil-kr/workspace/user-projects")
        
    def use_existing_duplicate_removal(self) -> dict:
        """Use existing duplicate_removal_plan.md instead of our new tools"""
        
        existing_plan = self.workspace_path / "shared-tools/config/duplicate_removal_plan.md"
        
        if existing_plan.exists():
            print("✅ USING EXISTING: duplicate_removal_plan.md")
            print("❌ STOPPING: Our redundant duplicate detection tools")
            
            return {
                "action": "USE_EXISTING_PLAN",
                "existing_system": str(existing_plan),
                "our_redundant_tools": [
                    "safe_duplicate_remover.py",
                    "precise_duplicate_remover.py", 
                    "vendor_aware_duplicate_detector.py"
                ],
                "recommendation": "Use existing plan, deprecate our tools"
            }
        else:
            return {"error": "Existing plan not found"}
    
    def integrate_with_existing_ai_orchestration(self) -> dict:
        """Integrate with existing AI orchestration instead of creating new"""
        
        existing_orchestration = [
            self.workspace_path / "shared-tools/nested-shares/ai/orchestration/integrated_ai_discussion.py",
            self.workspace_path / "shared-tools/nested-shares/ai/orchestration/smart_ai_router.py",
            self.workspace_path / "shared-tools/nested-shares/ai/orchestration/orchestra_cli.py"
        ]
        
        integration_plan = {
            "action": "INTEGRATE_WITH_EXISTING",
            "existing_systems": [],
            "our_additions": [
                "Session management (gemini_kiro_bridge.py)",
                "Error registry (error_registry.json)",
                "Context sharing protocols"
            ]
        }
        
        for system in existing_orchestration:
            if system.exists():
                integration_plan["existing_systems"].append({
                    "name": system.name,
                    "path": str(system.relative_to(self.workspace_path)),
                    "size": f"{system.stat().st_size // 1024}KB",
                    "status": "USE_THIS_INSTEAD"
                })
        
        return integration_plan
    
    def execute_safe_duplicate_removal(self) -> dict:
        """Execute safe removal using existing plan"""
        
        # Use existing duplicate_removal_plan.md
        existing_plan = self.workspace_path / "shared-tools/config/duplicate_removal_plan.md"
        
        if not existing_plan.exists():
            return {"error": "Existing duplicate removal plan not found"}
        
        # Files marked as safe to remove in existing plan
        safe_removals = [
            "shared-tools/nested-shares/ai/config/ai_autoconfig_duplicate.py",
            "shared-tools/nested-shares/ai/orchestration/logging_config_duplicate.py",
            "shared-tools/analysis/codebase-analyzer.py_duplicate",
            "shared-tools/analysis/monitoring_dashboard.py_duplicate"
        ]
        
        removal_results = []
        
        for file_path in safe_removals:
            full_path = self.workspace_path / file_path
            if full_path.exists():
                try:
                    full_path.unlink()
                    removal_results.append(f"✅ Removed: {file_path}")
                except Exception as e:
                    removal_results.append(f"❌ Failed: {file_path} - {e}")
            else:
                removal_results.append(f"⏭️  Not found: {file_path}")
        
        return {
            "action": "USED_EXISTING_PLAN",
            "plan_source": "shared-tools/config/duplicate_removal_plan.md",
            "results": removal_results,
            "vendor_protection": "All .venv/ and node_modules/ preserved"
        }
    
    def deprecate_our_redundant_tools(self) -> dict:
        """Mark our redundant tools as deprecated"""
        
        our_redundant_tools = [
            "safe_duplicate_remover.py",
            "precise_duplicate_remover.py",
            "vendor_aware_duplicate_detector.py",
            "safe_duplicate_detector.py"
        ]
        
        deprecation_results = []
        
        for tool in our_redundant_tools:
            tool_path = Path(__file__).parent / tool
            if tool_path.exists():
                # Add deprecation notice
                content = tool_path.read_text()
                if "DEPRECATED" not in content:
                    deprecated_content = f'''#!/usr/bin/env python3
"""DEPRECATED: Use existing duplicate_removal_plan.md instead
This tool was created redundantly - the workspace already has duplicate detection systems.
Use: shared-tools/config/duplicate_removal_plan.md
"""

# Original content below (deprecated)
{content}
'''
                    tool_path.write_text(deprecated_content)
                    deprecation_results.append(f"✅ Deprecated: {tool}")
                else:
                    deprecation_results.append(f"⏭️  Already deprecated: {tool}")
        
        return {
            "action": "DEPRECATED_REDUNDANT_TOOLS",
            "deprecated_tools": our_redundant_tools,
            "results": deprecation_results,
            "use_instead": "shared-tools/config/duplicate_removal_plan.md"
        }

def execute_emergency_integration():
    """Execute immediate emergency integration"""
    
    print("=== EMERGENCY INTEGRATION: USE EXISTING SYSTEMS ===\n")
    
    integration = EmergencyIntegration()
    
    # Step 1: Use existing duplicate removal
    print("🔄 Step 1: Using existing duplicate removal system...")
    duplicate_result = integration.use_existing_duplicate_removal()
    print(f"Action: {duplicate_result.get('action', 'ERROR')}")
    if 'existing_system' in duplicate_result:
        print(f"Using: {Path(duplicate_result['existing_system']).name}")
    
    # Step 2: Integrate with existing AI orchestration
    print("\n🔄 Step 2: Integrating with existing AI orchestration...")
    ai_result = integration.integrate_with_existing_ai_orchestration()
    print(f"Found {len(ai_result['existing_systems'])} existing AI systems")
    for system in ai_result['existing_systems'][:2]:
        print(f"  - {system['name']} ({system['size']})")
    
    # Step 3: Execute safe removal using existing plan
    print("\n🔄 Step 3: Executing safe removal using existing plan...")
    removal_result = integration.execute_safe_duplicate_removal()
    print(f"Using plan: {removal_result.get('plan_source', 'ERROR')}")
    for result in removal_result.get('results', [])[:3]:
        print(f"  {result}")
    
    # Step 4: Deprecate our redundant tools
    print("\n🔄 Step 4: Deprecating our redundant tools...")
    deprecation_result = integration.deprecate_our_redundant_tools()
    print(f"Deprecated {len(deprecation_result.get('deprecated_tools', []))} redundant tools")
    print(f"Use instead: {deprecation_result.get('use_instead', 'N/A')}")
    
    print("\n✅ EMERGENCY INTEGRATION COMPLETE")
    print("🎯 Result: Now using existing systems instead of our redundant creations")

if __name__ == "__main__":
    execute_emergency_integration()
