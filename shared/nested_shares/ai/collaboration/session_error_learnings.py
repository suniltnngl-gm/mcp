#!/usr/bin/env python3
"""Session Error Learnings - Critical mistakes we made with duplicates and existing systems"""

from pathlib import Path
import json
from datetime import datetime

ERROR_REGISTRY_FILE = Path(__file__).parent / "error_registry.json"

class SessionErrorLearnings:
    def __init__(self):
        self.workspace_path = Path("/media/sunil-kr/workspace/user-projects")
        self.error_registry = self._load_registry()

    def _load_registry(self) -> dict:
        if ERROR_REGISTRY_FILE.exists():
            with open(ERROR_REGISTRY_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_registry(self):
        with open(ERROR_REGISTRY_FILE, 'w') as f:
            json.dump(self.error_registry, f, indent=4)

    def get_all_errors(self) -> dict:
        """Retrieve all recorded errors from the registry."""
        return self.error_registry

        
    def analyze_critical_errors(self) -> dict:
        """Analyze the critical errors we made this session and add them to the registry"""
        current_errors = {
            "CRITICAL_ERROR_1": {
                "timestamp": datetime.now().isoformat(),
                "error": "Almost removed 751 vendor packages",
                "details": "Identified .venv/ Python packages as 'duplicates'",
                "impact": "Would have broken all Python environments",
                "root_cause": "Failed to distinguish vendor vs user files",
                "fix": "Always exclude .venv/, node_modules/, site-packages/",
                "status": "LEARNED_AND_PREVENTED"
            },
            
            "CRITICAL_ERROR_2": {
                "timestamp": datetime.now().isoformat(),
                "error": "Forgot existing duplicate detection systems",
                "details": "dedup_checker.py, duplicate_removal_plan.md already exist",
                "impact": "Reinvented the wheel, ignored existing work",
                "root_cause": "Didn't check for existing systems first",
                "fix": "Always scan for existing tools before creating new ones",
                "status": "LEARNED_AND_PREVENTED"
            },
            
            "CRITICAL_ERROR_3": {
                "timestamp": datetime.now().isoformat(),
                "error": "Ignored files already marked as duplicates",
                "details": "Files with '_duplicate' suffix already identified",
                "impact": "Missed obvious safe removal candidates",
                "root_cause": "Focused on complex detection vs simple patterns",
                "fix": "Check for existing duplicate markers first",
                "status": "LEARNED_AND_PREVENTED"
            }
        }
        
        for error_id, error_data in current_errors.items():
            if error_id not in self.error_registry:
                self.error_registry[error_id] = error_data
        self._save_registry()
        return current_errors
    
    def find_existing_systems_we_forgot(self) -> dict:
        """Find existing duplicate/dedup systems we should have used"""
        
        existing_systems = {}
        
        # Search patterns for existing systems
        search_patterns = [
            "*duplicate*", "*dedup*", "*consolidat*", 
            "*merge*", "*unif*", "*clean*"
        ]
        
        for pattern in search_patterns:
            for file_path in self.workspace_path.rglob(pattern):
                if file_path.is_file() and "archive" not in str(file_path):
                    system_type = "unknown"
                    
                    if file_path.suffix == ".py":
                        system_type = "python_tool"
                    elif file_path.suffix == ".sh":
                        system_type = "shell_script"
                    elif file_path.suffix == ".md":
                        system_type = "documentation"
                    
                    existing_systems[file_path.name] = {
                        "path": str(file_path),
                        "type": system_type,
                        "status": "FORGOT_TO_CHECK"
                    }
        
        return existing_systems
    
    def identify_vendor_packages_we_almost_removed(self) -> dict:
        """Identify vendor packages we almost mistakenly removed"""
        
        vendor_analysis = {
            "python_packages": [],
            "node_packages": [],
            "other_vendor": []
        }
        
        # Check .venv directories we almost touched
        for venv_dir in self.workspace_path.rglob(".venv"):
            if venv_dir.is_dir():
                package_count = len(list(venv_dir.rglob("*.py")))
                vendor_analysis["python_packages"].append({
                    "path": str(venv_dir),
                    "estimated_files": package_count,
                    "risk": "HIGH - Would break Python environment"
                })
        
        # Check node_modules we might have touched
        for node_dir in self.workspace_path.rglob("node_modules"):
            if node_dir.is_dir():
                package_count = len(list(node_dir.rglob("*.js")))
                vendor_analysis["node_packages"].append({
                    "path": str(node_dir),
                    "estimated_files": package_count,
                    "risk": "HIGH - Would break Node.js dependencies"
                })
        
        return vendor_analysis
    
    def create_error_prevention_checklist(self) -> list:
        """Create checklist to prevent these errors in future"""
        
        return [
            "✅ BEFORE any duplicate detection:",
            "   1. Check for existing dedup/duplicate tools",
            "   2. Look for files already marked with '_duplicate'",
            "   3. Exclude ALL vendor directories (.venv/, node_modules/)",
            "   4. Read existing duplicate_removal_plan.md if exists",
            "",
            "✅ DURING duplicate detection:",
            "   1. Distinguish vendor packages from user files",
            "   2. Use existing systems instead of creating new ones",
            "   3. Focus on user-created duplicates only",
            "   4. Verify file ownership (user vs system vs vendor)",
            "",
            "✅ BEFORE any removal:",
            "   1. Double-check vendor exclusions",
            "   2. Test removal on single file first",
            "   3. Backup critical files",
            "   4. Use existing safe removal plans"
        ]

if __name__ == "__main__":
    print("=== SESSION ERROR LEARNINGS ===")
    print("Analyzing critical mistakes made this session and updating registry...\n")
    
    learnings = SessionErrorLearnings()
    
    # Analyze critical errors (this now also adds them to the registry)
    learnings.analyze_critical_errors() # Call to populate/update registry

    # Retrieve all errors from the persistent registry
    all_errors = learnings.get_all_errors()
    print("🚨 CRITICAL ERRORS IN REGISTRY:")
    for error_id, details in all_errors.items():
        print(f"\n{error_id}: {details['error']}")
        print(f"   Timestamp: {details.get('timestamp', 'N/A')}")
        print(f"   Status: {details.get('status', 'N/A')}")
        print(f"   Impact: {details['impact']}")
        print(f"   Root Cause: {details['root_cause']}")
        print(f"   Fix: {details['fix']}")
    
    # Find existing systems we forgot
    existing = learnings.find_existing_systems_we_forgot()
    print(f"\n📋 EXISTING SYSTEMS WE FORGOT ({len(existing)}):")
    for system, info in list(existing.items())[:5]:  # Show first 5
        print(f"   - {system} ({info['type']})")
        print(f"     Path: {Path(info['path']).parent.name}/{Path(info['path']).name}")
    
    # Vendor packages we almost removed
    vendor = learnings.identify_vendor_packages_we_almost_removed()
    print(f"\n⚠️  VENDOR PACKAGES WE ALMOST REMOVED:")
    print(f"   Python environments: {len(vendor['python_packages'])}")
    print(f"   Node.js packages: {len(vendor['node_packages'])}")
    
    # Prevention checklist
    checklist = learnings.create_error_prevention_checklist()
    print(f"\n🛡️  ERROR PREVENTION CHECKLIST:")
    for item in checklist:
        print(f"{item}")
    
    print(f"\n✅ KEY LEARNING: Always check existing systems BEFORE creating new ones!")
    print(f"✅ KEY LEARNING: Vendor packages are NOT duplicates - they're dependencies!")
