#!/usr/bin/env python3
"""
Workspace-wide Lean Versioning Deployment
Integrates lean versioning into all existing systematic improvement tools
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List

class WorkspaceLeanDeployment:
    def __init__(self, workspace_root: str = None):
        self.workspace_root = Path(workspace_root or os.getcwd())
        self.tools_dir = self.workspace_root / "shared-tools" / "nested-shares"
        
    def find_improvement_tools(self) -> List[Path]:
        """Find all systematic improvement tools in workspace"""
        tools = []
        
        # Core improvement tools
        core_patterns = [
            "*improvement*.py", "*refactor*.py", "*optimize*.py", 
            "*consolidate*.py", "*systematic*.py"
        ]
        
        for pattern in core_patterns:
            tools.extend(self.tools_dir.rglob(pattern))
        
        return tools
    
    def integrate_tool(self, tool_path: Path) -> bool:
        """Integrate lean versioning into a specific tool"""
        try:
            content = tool_path.read_text()
            
            # Check if already integrated
            if "lean_versioning_integration" in content:
                return True
            
            # Add import at top
            import_line = "from workspace_core.lean_versioning_integration import LeanVersioningIntegration\n"
            
            # Find import section
            lines = content.split('\n')
            import_idx = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    import_idx = i + 1
            
            # Insert lean versioning import
            lines.insert(import_idx, import_line.strip())
            
            # Add integration initialization
            init_code = """
# Lean versioning integration
lean_versioning = LeanVersioningIntegration()
"""
            
            # Find class or main function
            for i, line in enumerate(lines):
                if 'class ' in line or 'def main(' in line:
                    lines.insert(i, init_code.strip())
                    break
            
            # Write back
            tool_path.write_text('\n'.join(lines))
            return True
            
        except Exception:
            return False
    
    def create_integration_wrapper(self) -> Path:
        """Create wrapper script for easy lean versioning access"""
        wrapper_path = self.workspace_root / "lean_versioning_cli.py"
        
        wrapper_content = '''#!/usr/bin/env python3
"""
Lean Versioning CLI - Unified interface for all lean versioning tools
"""

import sys
import os
from pathlib import Path

# Add shared tools to path
sys.path.insert(0, str(Path(__file__).parent / "shared-tools" / "nested-shares"))

from workspace_core.lean_versioning_integration import LeanVersioningIntegration
from workspace_core.lean_versioning_dashboard import LeanVersioningDashboard
from workspace_core.error_registry_integration import ErrorRegistryIntegration
from workspace_core.predictive_improvement_analysis import PredictiveImprovementAnalysis

def main():
    if len(sys.argv) < 2:
        print("Lean Versioning CLI")
        print("Commands:")
        print("  dashboard - Show version dashboard")
        print("  predict <type> [file] - Predict improvement success")
        print("  advice <type> [file] - Get error prevention advice")
        print("  sync - Sync error registry")
        return
    
    command = sys.argv[1]
    
    if command == "dashboard":
        dashboard = LeanVersioningDashboard()
        dashboard.display_dashboard()
    
    elif command == "predict":
        if len(sys.argv) < 3:
            print("Usage: predict <improvement_type> [file_path]")
            return
        analyzer = PredictiveImprovementAnalysis()
        improvement_type = sys.argv[2]
        file_path = sys.argv[3] if len(sys.argv) > 3 else None
        prob, recs = analyzer.predict_success_probability(improvement_type, file_path)
        print(f"Success Probability: {prob:.1%}")
        for rec in recs:
            print(f"  {rec}")
    
    elif command == "advice":
        if len(sys.argv) < 3:
            print("Usage: advice <improvement_type> [file_path]")
            return
        integration = ErrorRegistryIntegration()
        improvement_type = sys.argv[2]
        file_path = sys.argv[3] if len(sys.argv) > 3 else None
        advice = integration.get_prevention_advice(improvement_type, file_path)
        if advice:
            for item in advice:
                print(f"  • {item}")
        else:
            print("No specific advice available")
    
    elif command == "sync":
        integration = ErrorRegistryIntegration()
        result = integration.sync_with_lean_versioning()
        print(f"Sync complete: {result}")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
'''
        
        wrapper_path.write_text(wrapper_content)
        wrapper_path.chmod(0o755)
        return wrapper_path
    
    def deploy_workspace_wide(self) -> Dict:
        """Deploy lean versioning across entire workspace"""
        results = {
            "tools_found": 0,
            "tools_integrated": 0,
            "wrapper_created": False,
            "integration_status": []
        }
        
        # Find and integrate tools
        tools = self.find_improvement_tools()
        results["tools_found"] = len(tools)
        
        for tool in tools:
            if self.integrate_tool(tool):
                results["tools_integrated"] += 1
                results["integration_status"].append(f"✅ {tool.name}")
            else:
                results["integration_status"].append(f"❌ {tool.name}")
        
        # Create CLI wrapper
        wrapper = self.create_integration_wrapper()
        results["wrapper_created"] = wrapper.exists()
        
        # Update systematic improvement master
        self._update_master_integration()
        
        return results
    
    def _update_master_integration(self):
        """Ensure systematic improvement master is fully integrated"""
        master_path = self.tools_dir / "workspace-core" / "systematic_improvement_master.py"
        if master_path.exists():
            content = master_path.read_text()
            if "# LEAN VERSIONING DEPLOYED" not in content:
                content += "\n# LEAN VERSIONING DEPLOYED - Workspace-wide integration complete\n"
                master_path.write_text(content)

def main():
    """CLI interface for deployment"""
    import sys
    
    deployment = WorkspaceLeanDeployment()
    
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        tools = deployment.find_improvement_tools()
        print(f"Found {len(tools)} improvement tools:")
        for tool in tools:
            print(f"  • {tool.relative_to(deployment.workspace_root)}")
        return
    
    print("Deploying lean versioning workspace-wide...")
    results = deployment.deploy_workspace_wide()
    
    print(f"✅ Deployment complete!")
    print(f"📊 Tools found: {results['tools_found']}")
    print(f"🔧 Tools integrated: {results['tools_integrated']}")
    print(f"🖥️ CLI wrapper: {'✅' if results['wrapper_created'] else '❌'}")
    
    print("\nIntegration Status:")
    for status in results["integration_status"]:
        print(f"  {status}")
    
    print(f"\n🚀 Use: python3 lean_versioning_cli.py <command>")

if __name__ == "__main__":
    main()
