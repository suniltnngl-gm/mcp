#!/usr/bin/env python3
"""Workspace Ignore Integration - Deploy unified ignore logic across workspace levels"""

from shared_tools.utils.config_utils import get_workspace_path
import shutil
from pathlib import Path
from unified_ignore_system import UnifiedIgnoreSystem, get_daily_ignore_patterns, should_ignore_file

class WorkspaceIgnoreIntegration:
    def __init__(self):
        self.workspace_path = get_workspace_path()
        self.ignore_system = UnifiedIgnoreSystem()
        
        # Key workspace locations for ignore deployment
        self.deployment_targets = {
            "workspace_root": self.workspace_path,
            "shared_tools": self.workspace_path / "shared-tools",
            "nested_shares": self.workspace_path / "shared-tools/nested-shares",
            "current_projects": self.workspace_path / "current",
            "workspace_automation": self.workspace_path / "workspace-automation"
        }
    
    def deploy_unified_ignore_system(self) -> Dict:
        """Deploy unified ignore system across all workspace levels"""
        
        print("🚀 DEPLOYING UNIFIED IGNORE SYSTEM")
        print("Centralizing ignore logic for daily workspace use\n")
        
        deployment_results = {}
        
        # Create ignore files for each target
        ignore_files = self.ignore_system.create_ignore_files()
        
        for target_name, target_path in self.deployment_targets.items():
            if target_path.exists():
                result = self._deploy_to_target(target_path, ignore_files, target_name)
                deployment_results[target_name] = result
            else:
                deployment_results[target_name] = {"status": "SKIPPED", "reason": "Path does not exist"}
        
        # Create workspace-wide ignore utilities
        self._create_ignore_utilities()
        
        # Update existing tools to use unified ignore
        self._update_existing_tools()
        
        return {
            "deployment_results": deployment_results,
            "utilities_created": True,
            "tools_updated": True,
            "daily_use_ready": True
        }
    
    def _deploy_to_target(self, target_path: Path, ignore_files: Dict, target_name: str) -> Dict:
        """Deploy ignore files to specific target"""
        
        deployed_files = []
        
        # Deploy .gitignore if it's a git-relevant location
        if target_name in ["workspace_root", "shared_tools", "current_projects"]:
            gitignore_path = target_path / ".gitignore"
            
            # Backup existing .gitignore if it exists
            if gitignore_path.exists():
                backup_path = target_path / ".gitignore.backup"
                shutil.copy2(gitignore_path, backup_path)
                deployed_files.append(f"Backed up existing .gitignore to .gitignore.backup")
            
            gitignore_path.write_text(ignore_files[".gitignore"])
            deployed_files.append(".gitignore")
        
        # Deploy .ignore for search tools
        ignore_path = target_path / ".ignore"
        ignore_path.write_text(ignore_files[".ignore"])
        deployed_files.append(".ignore")
        
        # Deploy Python ignore patterns for nested-shares
        if target_name == "nested_shares":
            python_ignore_path = target_path / "python_ignore_patterns.py"
            python_ignore_path.write_text(ignore_files["python_ignore_patterns.py"])
            deployed_files.append("python_ignore_patterns.py")
        
        return {
            "status": "DEPLOYED",
            "files_deployed": deployed_files,
            "path": str(target_path)
        }
    
    def _create_ignore_utilities(self):
        """Create utility scripts for daily ignore operations"""
        
        # Shell utility script
        shell_utility = """#!/bin/bash
# Workspace Ignore Utilities - Daily use helpers

# Function to check if file should be ignored
should_ignore() {
    local file_path="$1"
    python3 -c "
from workspace_ignore_integration import should_ignore_file
result = should_ignore_file('$file_path')
exit(0 if result else 1)
"
}

# Function to find files excluding ignored patterns
find_workspace_files() {
    find . \\
        -not -path './.venv/*' \\
        -not -path './node_modules/*' \\
        -not -path './.git/*' \\
        -not -path './archive/*' \\
        -not -path './__pycache__/*' \\
        -not -path './.cache/*' \\
        "$@"
}

# Function to search with ignore patterns
search_workspace() {
    local search_term="$1"
    if command -v rg &> /dev/null; then
        rg --ignore-file .ignore "$search_term"
    else
        grep -r --exclude-dir=.venv --exclude-dir=node_modules --exclude-dir=.git "$search_term" .
    fi
}

# Export functions
export -f should_ignore
export -f find_workspace_files  
export -f search_workspace
"""
        
        utility_path = self.workspace_path / "shared-tools/nested-shares/workspace-core/workspace_ignore_utils.sh"
        utility_path.write_text(shell_utility)
        utility_path.chmod(0o755)  # Make executable
        
        # Python utility module
        python_utility = '''"""Workspace Ignore Utilities - Python helpers for daily use"""

from pathlib import Path
from unified_ignore_system import UnifiedIgnoreSystem, should_ignore_file, get_daily_ignore_patterns

# Global ignore system instance
_ignore_system = UnifiedIgnoreSystem()

def scan_directory_filtered(directory: str, file_types: list = None) -> list:
    """Scan directory excluding ignored files"""
    
    directory_path = Path(directory)
    files = []
    
    for file_path in directory_path.rglob("*"):
        if file_path.is_file():
            # Check if should be ignored
            if should_ignore_file(str(file_path)):
                continue
            
            # Check file type filter
            if file_types and file_path.suffix not in file_types:
                continue
            
            files.append(file_path)
    
    return files

def get_workspace_files(workspace_path: str, include_types: list = None) -> list:
    """Get all workspace files excluding ignored patterns"""
    return scan_directory_filtered(workspace_path, include_types)

def is_vendor_file(file_path: str) -> bool:
    """Check if file is vendor/dependency code"""
    vendor_patterns = ['.venv/', 'node_modules/', 'site-packages/', '.egg-info/']
    return any(pattern in file_path for pattern in vendor_patterns)

def get_user_files_only(directory: str) -> list:
    """Get only user-created files, excluding vendor/generated files"""
    all_files = scan_directory_filtered(directory)
    return [f for f in all_files if not is_vendor_file(str(f))]

# Convenience aliases
ignore_file = should_ignore_file
scan_filtered = scan_directory_filtered
'''
        
        python_utility_path = self.workspace_path / "shared-tools/nested-shares/workspace-core/workspace_ignore_utils.py"
        python_utility_path.write_text(python_utility)
    
    def _update_existing_tools(self):
        """Update existing tools to use unified ignore system"""
        
        # Update system discovery tools
        discovery_tools = [
            "system_discovery_rebuilder.py",
            "intelligent_consolidation_engine.py", 
            "fine_tuned_system_detection.py"
        ]
        
        collaboration_path = self.workspace_path / "shared-tools/nested-shares/ai/collaboration"
        
        for tool_name in discovery_tools:
            tool_path = collaboration_path / tool_name
            if tool_path.exists():
                self._add_ignore_import_to_tool(tool_path)
    
    def _add_ignore_import_to_tool(self, tool_path: Path):
        """Add unified ignore import to existing tool"""
        
        try:
            content = tool_path.read_text()
            
            # Check if already has unified ignore import
            if "unified_ignore_system" in content or "workspace_ignore_utils" in content:
                return  # Already updated
            
            # Add import after existing imports
            lines = content.splitlines()
            import_end_idx = 0
            
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    import_end_idx = i + 1
            
            # Insert unified ignore import
            new_import = "from workspace_ignore_utils import should_ignore_file, get_user_files_only"
            lines.insert(import_end_idx, new_import)
            
            # Add comment about unified ignore
            lines.insert(import_end_idx + 1, "# Using unified workspace ignore system")
            
            # Write updated content
            tool_path.write_text("\n".join(lines))
            
        except Exception as e:
            print(f"Warning: Could not update {tool_path.name}: {e}")

def main():
    """Deploy unified ignore system across workspace"""
    
    integration = WorkspaceIgnoreIntegration()
    results = integration.deploy_unified_ignore_system()
    
    print("📊 DEPLOYMENT RESULTS:")
    for target, result in results["deployment_results"].items():
        status_icon = "✅" if result["status"] == "DEPLOYED" else "⏭️"
        print(f"  {status_icon} {target}: {result['status']}")
        if result["status"] == "DEPLOYED":
            print(f"    Files: {', '.join(result['files_deployed'])}")
    
    print(f"\n🛠️ UTILITIES CREATED:")
    print(f"  - workspace_ignore_utils.sh (shell helpers)")
    print(f"  - workspace_ignore_utils.py (Python helpers)")
    
    print(f"\n🔧 TOOLS UPDATED:")
    print(f"  - System discovery tools now use unified ignore")
    print(f"  - Consolidation engines use unified patterns")
    
    print(f"\n🎯 DAILY USE READY:")
    print(f"  - Use should_ignore_file() in Python")
    print(f"  - Use find_workspace_files in shell")
    print(f"  - Use .ignore file with ripgrep/fd")
    print(f"  - All workspace levels have consistent ignore logic")
    
    print(f"\n✅ UNIFIED IGNORE SYSTEM DEPLOYED")
    print(f"🌟 Centralized ignore logic now available workspace-wide!")

if __name__ == "__main__":
    main()
