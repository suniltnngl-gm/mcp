#!/usr/bin/env python3
"""Unified Ignore System - Centralized ignore logic for shared-tools, nested-shares, and deep-nesting"""

import json
from pathlib import Path
from typing import List, Dict, Set
from dataclasses import dataclass, asdict

@dataclass
class IgnoreRule:
    pattern: str
    scope: str  # 'global', 'development', 'production', 'analysis'
    reason: str
    priority: int  # 1=critical, 2=important, 3=optional

from shared_tools.utils.config_utils import get_workspace_path

class UnifiedIgnoreSystem:
    def __init__(self):
        self.workspace_path = get_workspace_path()
        self.ignore_config_file = Path(__file__).parent / "unified_ignore_config.json"
        
        # Initialize ignore rules
        self.ignore_rules = self._initialize_ignore_rules()
        
    def _initialize_ignore_rules(self) -> Dict[str, List[IgnoreRule]]:
        """Initialize comprehensive ignore rules for all workspace levels"""
        
        rules = {
            "critical_always_ignore": [
                IgnoreRule(".git/objects/", "global", "Git internals - never scan", 1),
                IgnoreRule(".git/refs/", "global", "Git references - never scan", 1),
                IgnoreRule(".git/logs/", "global", "Git logs - never scan", 1),
                IgnoreRule("node_modules/", "global", "Node.js dependencies - vendor code", 1),
                IgnoreRule(".venv/", "global", "Python virtual env - vendor packages", 1),
                IgnoreRule("venv/", "global", "Python virtual env - vendor packages", 1),
                IgnoreRule("__pycache__/", "global", "Python cache - generated files", 1),
            ],
            
            "development_ignore": [
                IgnoreRule("*.pyc", "development", "Python bytecode - generated", 2),
                IgnoreRule("*.pyo", "development", "Python optimized bytecode", 2),
                IgnoreRule(".pytest_cache/", "development", "Pytest cache - temporary", 2),
                IgnoreRule(".mypy_cache/", "development", "MyPy cache - temporary", 2),
                IgnoreRule(".ruff_cache/", "development", "Ruff cache - temporary", 2),
                IgnoreRule("*.log", "development", "Log files - temporary data", 2),
                IgnoreRule("*.tmp", "development", "Temporary files", 2),
                IgnoreRule(".DS_Store", "development", "macOS system files", 2),
            ],
            
            "analysis_ignore": [
                IgnoreRule("archive/", "analysis", "Archive is reference only - skip in analysis", 2),
                IgnoreRule("artifacts/", "analysis", "Build artifacts - skip in analysis", 2),
                IgnoreRule("backups/", "analysis", "Backup files - skip in analysis", 3),
                IgnoreRule("*.backup", "analysis", "Backup files - skip in analysis", 3),
                IgnoreRule("*_old", "analysis", "Old versions - skip in analysis", 3),
                IgnoreRule("*_backup", "analysis", "Backup versions - skip in analysis", 3),
            ],
            
            "workspace_structure_ignore": [
                IgnoreRule(".cache/", "global", "Cache directories - temporary", 2),
                IgnoreRule("dist/", "global", "Distribution files - generated", 2),
                IgnoreRule("build/", "global", "Build directories - generated", 2),
                IgnoreRule(".eggs/", "global", "Python egg directories", 2),
                IgnoreRule("*.egg-info/", "global", "Python package info", 2),
            ]
        }
        
        return rules
    
    def get_ignore_patterns(self, scope: str = "daily_use", include_optional: bool = False) -> List[str]:
        """Get ignore patterns for specific scope and daily use"""
        
        patterns = []
        
        # Always include critical patterns
        for rule in self.ignore_rules["critical_always_ignore"]:
            patterns.append(rule.pattern)
        
        # Include based on scope
        if scope in ["daily_use", "development", "all"]:
            for rule in self.ignore_rules["development_ignore"]:
                if include_optional or rule.priority <= 2:
                    patterns.append(rule.pattern)
        
        if scope in ["analysis", "daily_use", "all"]:
            for rule in self.ignore_rules["analysis_ignore"]:
                if include_optional or rule.priority <= 2:
                    patterns.append(rule.pattern)
        
        if scope in ["workspace", "daily_use", "all"]:
            for rule in self.ignore_rules["workspace_structure_ignore"]:
                if include_optional or rule.priority <= 2:
                    patterns.append(rule.pattern)
        
        return list(set(patterns))  # Remove duplicates
    
    def should_ignore(self, file_path: str, scope: str = "daily_use") -> tuple[bool, str]:
        """Check if file/path should be ignored with reason"""
        
        ignore_patterns = self.get_ignore_patterns(scope)
        path_lower = file_path.lower()
        
        for pattern in ignore_patterns:
            if self._pattern_matches(path_lower, pattern.lower()):
                # Find the reason
                reason = self._get_ignore_reason(pattern)
                return True, reason
        
        return False, "Not ignored"
    
    def _pattern_matches(self, path: str, pattern: str) -> bool:
        """Check if path matches ignore pattern"""
        
        if pattern.endswith('/'):
            # Directory pattern
            dir_pattern = pattern[:-1]
            return f"/{dir_pattern}/" in path or path.endswith(f"/{dir_pattern}")
        elif pattern.startswith('*.'):
            # Extension pattern
            extension = pattern[1:]
            return path.endswith(extension)
        else:
            # Substring pattern
            return pattern in path
    
    def _get_ignore_reason(self, pattern: str) -> str:
        """Get reason for ignoring this pattern"""
        
        for category_rules in self.ignore_rules.values():
            for rule in category_rules:
                if rule.pattern == pattern:
                    return rule.reason
        
        return "Standard ignore pattern"
    
    def create_ignore_files(self) -> Dict[str, str]:
        """Create ignore files for different tools and contexts"""
        
        ignore_files = {}
        
        # .gitignore for git operations
        gitignore_patterns = self.get_ignore_patterns("development")
        gitignore_content = "# Unified Workspace Ignore Rules\n"
        gitignore_content += "# Generated by unified_ignore_system.py\n\n"
        
        for pattern in gitignore_patterns:
            if not pattern.startswith('.git/'):  # Don't ignore .git in .gitignore
                gitignore_content += f"{pattern}\n"
        
        ignore_files[".gitignore"] = gitignore_content
        
        # .ignore for ripgrep/fd tools
        ignore_patterns = self.get_ignore_patterns("daily_use")
        ignore_content = "# Unified Workspace Ignore Rules\n"
        ignore_content += "# For ripgrep, fd, and other search tools\n\n"
        
        for pattern in ignore_patterns:
            ignore_content += f"{pattern}\n"
        
        ignore_files[".ignore"] = ignore_content
        
        # Python-specific ignore list
        python_patterns = [p for p in self.get_ignore_patterns("all") 
                          if any(x in p for x in ['py', 'cache', 'egg'])]
        python_ignore = "# Python-specific ignore patterns\nPYTHON_IGNORE_PATTERNS = [\n"
        for pattern in python_patterns:
            python_ignore += f"    '{pattern}',\n"
        python_ignore += "]\n"
        
        ignore_files["python_ignore_patterns.py"] = python_ignore
        
        return ignore_files
    
    def get_daily_use_config(self) -> Dict:
        """Get optimized ignore config for daily workspace use"""
        
        return {
            "daily_patterns": self.get_ignore_patterns("daily_use"),
            "analysis_patterns": self.get_ignore_patterns("analysis"),
            "development_patterns": self.get_ignore_patterns("development"),
            "usage_guide": {
                "file_operations": "Use daily_patterns for general file operations",
                "code_analysis": "Use analysis_patterns for code scanning",
                "development": "Use development_patterns for dev tools",
                "search_tools": "Use .ignore file for ripgrep/fd"
            },
            "integration_examples": {
                "python": "from unified_ignore_system import UnifiedIgnoreSystem; ignore = UnifiedIgnoreSystem()",
                "shell": "grep -v -f .ignore",
                "find": "find . -not -path './.venv/*' -not -path './node_modules/*'"
            }
        }
    
    def save_unified_config(self) -> str:
        """Save unified ignore configuration"""
        
        config = {
            "version": "1.0.0",
            "created": "2025-12-14T00:28:00",
            "description": "Centralized ignore logic for workspace-wide use",
            "rules": {category: [asdict(rule) for rule in rules] 
                     for category, rules in self.ignore_rules.items()},
            "daily_use_config": self.get_daily_use_config(),
            "ignore_files": self.create_ignore_files()
        }
        
        self.ignore_config_file.write_text(json.dumps(config, indent=2))
        return str(self.ignore_config_file)

# Convenience functions for daily use
def get_daily_ignore_patterns() -> List[str]:
    """Quick function to get daily use ignore patterns"""
    return UnifiedIgnoreSystem().get_ignore_patterns("daily_use")

def should_ignore_file(file_path: str) -> bool:
    """Quick function to check if file should be ignored"""
    ignore_system = UnifiedIgnoreSystem()
    should_ignore, _ = ignore_system.should_ignore(file_path)
    return should_ignore

def create_workspace_ignore_files(target_dir: str = None) -> Dict[str, str]:
    """Create ignore files in target directory"""
    
    ignore_system = UnifiedIgnoreSystem()
    ignore_files = ignore_system.create_ignore_files()
    
    if target_dir:
        target_path = Path(target_dir)
        for filename, content in ignore_files.items():
            (target_path / filename).write_text(content)
    
    return ignore_files

def main():
    """Initialize unified ignore system"""
    
    print("=== UNIFIED IGNORE SYSTEM ===")
    print("Centralizing ignore logic for workspace-wide use\n")
    
    ignore_system = UnifiedIgnoreSystem()
    
    # Save configuration
    config_file = ignore_system.save_unified_config()
    print(f"✅ Saved unified config: {Path(config_file).name}")
    
    # Show daily use patterns
    daily_patterns = ignore_system.get_ignore_patterns("daily_use")
    print(f"\n📋 Daily use ignore patterns ({len(daily_patterns)}):")
    for pattern in daily_patterns[:10]:
        should_ignore, reason = ignore_system.should_ignore(f"test/{pattern}", "daily_use")
        print(f"  - {pattern} ({reason})")
    if len(daily_patterns) > 10:
        print(f"  ... and {len(daily_patterns) - 10} more")
    
    # Create ignore files
    ignore_files = ignore_system.create_ignore_files()
    print(f"\n📁 Created ignore files:")
    for filename in ignore_files.keys():
        print(f"  - {filename}")
    
    # Show usage examples
    print(f"\n🚀 Usage Examples:")
    print(f"  Python: should_ignore_file('path/to/file')")
    print(f"  Shell: grep -v -f .ignore")
    print(f"  Find: find . -not -path './.venv/*'")
    
    print(f"\n✅ UNIFIED IGNORE SYSTEM READY")
    print(f"🎯 Use for: shared-tools, nested-shares, deep-nesting, daily operations")

if __name__ == "__main__":
    main()
