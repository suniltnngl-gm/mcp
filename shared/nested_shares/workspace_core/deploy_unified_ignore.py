#!/usr/bin/env python3
"""Deploy Unified Ignore System - Simple deployment script"""

from shared_tools.utils.config_utils import get_workspace_path
import shutil
from pathlib import Path
from unified_ignore_system import UnifiedIgnoreSystem

def deploy_ignore_system():
    """Deploy unified ignore system across workspace"""
    
    print("🚀 DEPLOYING UNIFIED IGNORE SYSTEM")
    print("Centralizing ignore logic for daily workspace use\n")
    
    workspace_path = get_workspace_path()
    ignore_system = UnifiedIgnoreSystem()
    
    # Create ignore files
    ignore_files = ignore_system.create_ignore_files()
    
    # Deployment targets
    targets = {
        "workspace_root": workspace_path,
        "shared_tools": workspace_path / "shared-tools", 
        "nested_shares": workspace_path / "shared-tools/nested-shares",
        "current": workspace_path / "current"
    }
    
    deployed_count = 0
    
    for target_name, target_path in targets.items():
        if target_path.exists():
            print(f"📁 Deploying to {target_name}...")
            
            # Deploy .ignore file (for ripgrep/fd)
            ignore_path = target_path / ".ignore"
            ignore_path.write_text(ignore_files[".ignore"])
            print(f"  ✅ Created .ignore")
            
            # Deploy .gitignore for git-relevant locations
            if target_name in ["workspace_root", "shared_tools", "current"]:
                gitignore_path = target_path / ".gitignore"
                
                # Backup existing if present
                if gitignore_path.exists():
                    backup_path = target_path / ".gitignore.backup"
                    shutil.copy2(gitignore_path, backup_path)
                    print(f"  📋 Backed up existing .gitignore")
                
                gitignore_path.write_text(ignore_files[".gitignore"])
                print(f"  ✅ Created .gitignore")
            
            deployed_count += 1
        else:
            print(f"⏭️  Skipped {target_name} (path not found)")
    
    # Create utility functions file
    utility_content = '''"""Workspace Ignore Utilities - Daily use helpers"""

from pathlib import Path

# Daily use ignore patterns
DAILY_IGNORE_PATTERNS = [
    '.git/', '.venv/', 'venv/', 'node_modules/', '__pycache__/',
    '*.pyc', '*.pyo', '.pytest_cache/', '.mypy_cache/', '.ruff_cache/',
    '*.log', '*.tmp', '.DS_Store', 'archive/', 'artifacts/',
    '.cache/', 'dist/', 'build/', '.eggs/', '*.egg-info/'
]

def should_ignore_file(file_path: str) -> bool:
    """Check if file should be ignored for daily operations"""
    path_lower = file_path.lower()
    
    for pattern in DAILY_IGNORE_PATTERNS:
        if pattern.endswith('/'):
            # Directory pattern
            dir_pattern = pattern[:-1]
            if f"/{dir_pattern}/" in path_lower or path_lower.endswith(f"/{dir_pattern}"):
                return True
        elif pattern.startswith('*.'):
            # Extension pattern
            if path_lower.endswith(pattern[1:]):
                return True
        else:
            # Substring pattern
            if pattern in path_lower:
                return True
    
    return False

def scan_directory_filtered(directory: str, file_types: list = None) -> list:
    """Scan directory excluding ignored files"""
    directory_path = Path(directory)
    files = []
    
    for file_path in directory_path.rglob("*"):
        if file_path.is_file():
            if should_ignore_file(str(file_path)):
                continue
            
            if file_types and file_path.suffix not in file_types:
                continue
            
            files.append(file_path)
    
    return files

def get_user_files_only(directory: str) -> list:
    """Get only user-created files, excluding vendor/generated"""
    all_files = scan_directory_filtered(directory)
    vendor_patterns = ['.venv/', 'node_modules/', 'site-packages/']
    return [f for f in all_files if not any(p in str(f) for p in vendor_patterns)]
'''
    
    utility_path = workspace_path / "shared-tools/nested-shares/workspace-core/ignore_utils.py"
    utility_path.write_text(utility_content)
    print(f"\n🛠️  Created ignore_utils.py")
    
    # Create shell utility
    shell_utility = '''#!/bin/bash
# Workspace Ignore Utilities

# Find files excluding common ignore patterns
find_workspace_files() {
    find . \\
        -not -path './.venv/*' \\
        -not -path './node_modules/*' \\
        -not -path './.git/*' \\
        -not -path './archive/*' \\
        -not -path './__pycache__/*' \\
        "$@"
}

# Search with ignore patterns
search_workspace() {
    if command -v rg &> /dev/null; then
        rg --ignore-file .ignore "$1"
    else
        grep -r --exclude-dir=.venv --exclude-dir=node_modules "$1" .
    fi
}
'''
    
    shell_utility_path = workspace_path / "shared-tools/nested-shares/workspace-core/ignore_utils.sh"
    shell_utility_path.write_text(shell_utility)
    shell_utility_path.chmod(0o755)
    print(f"🛠️  Created ignore_utils.sh")
    
    print(f"\n✅ DEPLOYMENT COMPLETE")
    print(f"📊 Deployed to {deployed_count} locations")
    print(f"🎯 Daily use patterns: {len(ignore_system.get_ignore_patterns('daily_use'))}")
    
    print(f"\n🚀 USAGE:")
    print(f"  Python: from ignore_utils import should_ignore_file")
    print(f"  Shell: source ignore_utils.sh && find_workspace_files")
    print(f"  Search: rg --ignore-file .ignore 'pattern'")
    
    return deployed_count

if __name__ == "__main__":
    deploy_ignore_system()
