#!/usr/bin/env python3
"""DEPRECATED: Use existing duplicate_removal_plan.md instead
This tool was created redundantly - the workspace already has duplicate detection systems.
Use: shared-tools/config/duplicate_removal_plan.md
"""

# Original content below (deprecated)
#!/usr/bin/env python3
"""Vendor-Aware Duplicate Detector - Learns from session errors and integrates existing systems"""

import sys
from pathlib import Path

# Import existing duplicate detection systems we forgot!
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "analysis"))
from dedup_checker import find_duplicates, similarity

class VendorAwareDuplicateDetector:
    def __init__(self):
        self.workspace_path = Path("/media/sunil-kr/workspace/user-projects")
        
        # CRITICAL: Vendor/dependency exclusions we missed
        self.vendor_exclusions = [
            ".venv/",           # Python virtual environments  
            "venv/",            # Python virtual environments
            "node_modules/",    # Node.js dependencies
            "__pycache__/",     # Python cache
            ".pytest_cache/",   # Pytest cache
            ".mypy_cache/",     # MyPy cache
            "site-packages/",   # Python packages
            "dist-info/",       # Package metadata
            ".egg-info/",       # Python egg info
        ]
        
        # Existing systems we forgot to check
        self.existing_systems = {
            "dedup_checker.py": "Database-based duplicate detection",
            "duplicate_removal_plan.md": "Planned duplicate removals", 
            "mark_duplicates.sh": "Shell script for marking duplicates"
        }
    
    def check_existing_systems(self) -> dict:
        """Check existing duplicate detection systems we forgot"""
        
        existing_found = {}
        
        # Check for existing dedup systems
        analysis_path = self.workspace_path / "shared-tools/analysis"
        config_path = self.workspace_path / "shared-tools/config"
        
        for system_file, description in self.existing_systems.items():
            for search_path in [analysis_path, config_path]:
                system_path = search_path / system_file
                if system_path.exists():
                    existing_found[system_file] = {
                        "path": str(system_path),
                        "description": description,
                        "status": "FORGOT_TO_USE"
                    }
        
        return existing_found
    
    def identify_vendor_vs_user_duplicates(self) -> dict:
        """Distinguish vendor packages from user duplicates"""
        
        analysis = {
            "vendor_packages": [],
            "user_duplicates": [],
            "existing_marked_duplicates": []
        }
        
        # Find files marked as duplicates by existing systems
        for duplicate_file in self.workspace_path.rglob("*duplicate*"):
            if duplicate_file.is_file():
                # Check if it's a vendor package
                is_vendor = any(exclusion in str(duplicate_file) for exclusion in self.vendor_exclusions)
                
                if is_vendor:
                    analysis["vendor_packages"].append({
                        "path": str(duplicate_file),
                        "type": "vendor_dependency",
                        "action": "PRESERVE - Essential dependency"
                    })
                elif "_duplicate" in duplicate_file.name:
                    # These are marked by existing systems
                    analysis["existing_marked_duplicates"].append({
                        "path": str(duplicate_file),
                        "type": "user_duplicate_marked",
                        "action": "SAFE_TO_REMOVE - Already consolidated"
                    })
                else:
                    analysis["user_duplicates"].append({
                        "path": str(duplicate_file),
                        "type": "user_duplicate",
                        "action": "REVIEW_NEEDED"
                    })
        
        return analysis
    
    def integrate_with_existing_systems(self) -> dict:
        """Integrate with existing duplicate detection systems"""
        
        integration_report = {
            "existing_systems_found": self.check_existing_systems(),
            "vendor_analysis": self.identify_vendor_vs_user_duplicates(),
            "session_errors_learned": [
                "Almost removed 751 vendor packages from .venv directories",
                "Forgot to check existing dedup_checker.py system",
                "Ignored duplicate_removal_plan.md with safe removal list"
            ],
            "corrective_actions": [
                "Always check vendor exclusions before duplicate removal",
                "Integrate with existing dedup_checker.py for database duplicates", 
                "Use existing duplicate_removal_plan.md for safe removals",
                "Distinguish vendor packages from user duplicates"
            ]
        }
        
        return integration_report
    
    def safe_duplicate_removal_plan(self) -> dict:
        """Create safe removal plan using existing systems"""
        
        # Use existing duplicate_removal_plan.md
        plan_file = self.workspace_path / "shared-tools/config/duplicate_removal_plan.md"
        
        if plan_file.exists():
            return {
                "status": "EXISTING_PLAN_FOUND",
                "plan_file": str(plan_file),
                "action": "USE_EXISTING_PLAN",
                "safe_removals": "Files already marked as _duplicate by consolidation",
                "vendor_protection": "All .venv/ and node_modules/ excluded"
            }
        else:
            return {
                "status": "NO_EXISTING_PLAN",
                "action": "CREATE_NEW_PLAN",
                "vendor_protection": "Mandatory exclusions applied"
            }

if __name__ == "__main__":
    print("=== VENDOR-AWARE DUPLICATE DETECTION ===")
    print("Learning from session errors...\n")
    
    detector = VendorAwareDuplicateDetector()
    
    # Check what we forgot
    existing_systems = detector.check_existing_systems()
    print(f"🚨 EXISTING SYSTEMS WE FORGOT: {len(existing_systems)}")
    for system, info in existing_systems.items():
        print(f"   - {system}: {info['description']}")
        print(f"     Path: {info['path']}")
        print(f"     Status: {info['status']}")
    
    # Analyze vendor vs user duplicates
    analysis = detector.identify_vendor_vs_user_duplicates()
    print(f"\n📊 DUPLICATE ANALYSIS:")
    print(f"   Vendor packages: {len(analysis['vendor_packages'])}")
    print(f"   User duplicates: {len(analysis['user_duplicates'])}")
    print(f"   Existing marked duplicates: {len(analysis['existing_marked_duplicates'])}")
    
    # Integration report
    report = detector.integrate_with_existing_systems()
    print(f"\n🎯 SESSION ERRORS LEARNED:")
    for error in report["session_errors_learned"]:
        print(f"   ❌ {error}")
    
    print(f"\n✅ CORRECTIVE ACTIONS:")
    for action in report["corrective_actions"]:
        print(f"   🔧 {action}")
    
    # Safe removal plan
    plan = detector.safe_duplicate_removal_plan()
    print(f"\n📋 SAFE REMOVAL PLAN: {plan['status']}")
    if plan['status'] == 'EXISTING_PLAN_FOUND':
        print(f"   📁 Use existing: {Path(plan['plan_file']).name}")
        print(f"   🛡️ Vendor protection: {plan['vendor_protection']}")

