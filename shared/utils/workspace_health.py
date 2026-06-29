#!/usr/bin/env python3
"""
DevFlow Workspace Health Monitor
Comprehensive health check for the workspace
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

class WorkspaceHealthMonitor:
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.issues = []
        self.warnings = []
        
    def check_structure(self) -> bool:
        """Check workspace structure integrity"""
        required_dirs = ["packages", "tools", "scripts", "docs"]
        required_files = ["pyproject.toml", "Makefile", ".gitignore"]
        
        for dir_name in required_dirs:
            if not (self.workspace_root / dir_name).exists():
                self.issues.append(f"Missing required directory: {dir_name}")
                
        for file_name in required_files:
            if not (self.workspace_root / file_name).exists():
                self.issues.append(f"Missing required file: {file_name}")
                
        return len(self.issues) == 0
    
    def check_dependencies(self) -> bool:
        """Check dependency health"""
        try:
            result = subprocess.run(
                ["uv", "sync", "--dry-run"], 
                capture_output=True, text=True, cwd=self.workspace_root
            )
            if result.returncode != 0:
                self.issues.append(f"Dependency sync issues: {result.stderr}")
                return False
        except FileNotFoundError:
            self.issues.append("UV not installed")
            return False
        return True
    
    def check_git_status(self) -> bool:
        """Check git repository health"""
        try:
            # Check for individual .git directories
            git_dirs = list(self.workspace_root.rglob(".git"))
            workspace_git = self.workspace_root / ".git"
            
            if workspace_git in git_dirs:
                git_dirs.remove(workspace_git)
                
            if git_dirs:
                self.warnings.append(f"Found {len(git_dirs)} individual .git directories")
                
            # Check git status
            result = subprocess.run(
                ["git", "status", "--porcelain"], 
                capture_output=True, text=True, cwd=self.workspace_root
            )
            if result.stdout.strip():
                self.warnings.append("Uncommitted changes detected")
                
        except FileNotFoundError:
            self.issues.append("Git not available")
            return False
        return True
    
    def check_virtual_envs(self) -> bool:
        """Check for individual virtual environments"""
        venv_dirs = []
        for pattern in [".venv", "venv", ".env"]:
            venv_dirs.extend(list(self.workspace_root.rglob(pattern)))
            
        workspace_venv = self.workspace_root / ".venv"
        if workspace_venv in venv_dirs:
            venv_dirs.remove(workspace_venv)
            
        if venv_dirs:
            self.warnings.append(f"Found {len(venv_dirs)} individual virtual environments")
            
        return True
    
    def check_test_health(self) -> bool:
        """Check test suite health"""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "--collect-only", "-q"], 
                capture_output=True, text=True, cwd=self.workspace_root
            )
            if "error" in result.stderr.lower():
                self.warnings.append("Test collection issues detected")
        except Exception as e:
            self.warnings.append(f"Cannot run test health check: {e}")
        return True
    
    def generate_report(self) -> Dict:
        """Generate comprehensive health report"""
        report = {
            "workspace_root": str(self.workspace_root),
            "structure_ok": self.check_structure(),
            "dependencies_ok": self.check_dependencies(),
            "git_ok": self.check_git_status(),
            "venv_ok": self.check_virtual_envs(),
            "tests_ok": self.check_test_health(),
            "issues": self.issues,
            "warnings": self.warnings
        }
        
        report["overall_health"] = (
            len(self.issues) == 0 and 
            report["structure_ok"] and 
            report["dependencies_ok"]
        )
        
        return report
    
    def print_report(self, report: Dict):
        """Print formatted health report"""
        print("🏥 DevFlow Workspace Health Report")
        print("=" * 50)
        
        # Overall status
        status = "✅ HEALTHY" if report["overall_health"] else "❌ ISSUES FOUND"
        print(f"\nOverall Status: {status}")
        
        # Component status
        print(f"\n📁 Structure: {'✅' if report['structure_ok'] else '❌'}")
        print(f"📦 Dependencies: {'✅' if report['dependencies_ok'] else '❌'}")
        print(f"🔄 Git: {'✅' if report['git_ok'] else '❌'}")
        print(f"🐍 Virtual Envs: {'✅' if report['venv_ok'] else '❌'}")
        print(f"🧪 Tests: {'✅' if report['tests_ok'] else '❌'}")
        
        # Issues
        if report["issues"]:
            print(f"\n❌ Issues ({len(report['issues'])}):")
            for issue in report["issues"]:
                print(f"  • {issue}")
                
        # Warnings
        if report["warnings"]:
            print(f"\n⚠️  Warnings ({len(report['warnings'])}):")
            for warning in report["warnings"]:
                print(f"  • {warning}")
                
        print("\n" + "=" * 50)

def main():
    workspace_root = Path(__file__).parent.parent
    monitor = WorkspaceHealthMonitor(workspace_root)
    report = monitor.generate_report()
    monitor.print_report(report)
    
    # Exit with error code if issues found
    sys.exit(0 if report["overall_health"] else 1)

if __name__ == "__main__":
    main()
