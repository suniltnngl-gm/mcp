#!/usr/bin/env python3
"""DEPRECATED: Use existing duplicate_removal_plan.md instead
This tool was created redundantly - the workspace already has duplicate detection systems.
Use: shared-tools/config/duplicate_removal_plan.md
"""

# Original content below (deprecated)
#!/usr/bin/env python3
"""Safe duplicate detector with explicit criteria for unwanted files"""

import hashlib
from pathlib import Path
from typing import Dict, List, Set

class SafeDuplicateDetector:
    def __init__(self):
        self.workspace_path = Path("/media/sunil-kr/workspace/user-projects")
        
        # EXPLICIT CRITERIA for "confidant unwanted files"
        self.unwanted_criteria = {
            "extensions": [".pyc", ".pyo", ".tmp", ".log", ".bak", ".old"],
            "patterns": ["*_backup", "*_old", "temp_*", "*~", ".DS_Store"],
            "exact_names": [".gitkeep", "Thumbs.db", "desktop.ini"],
            "directories": ["__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"]
        }
        
        # PROTECTED AREAS (never touch)
        self.protected_paths = [
            "archive/",  # Archive is reference only
            ".git/",     # Git internals
            ".kiro/",    # Kiro configuration
            "current/",  # Active projects
        ]
    
    def is_unwanted_file(self, file_path: Path) -> tuple[bool, str]:
        """Check if file meets unwanted criteria with reason"""
        
        # Never touch protected paths
        for protected in self.protected_paths:
            if protected in str(file_path):
                return False, f"Protected path: {protected}"
        
        # Check extension
        if file_path.suffix in self.unwanted_criteria["extensions"]:
            return True, f"Unwanted extension: {file_path.suffix}"
        
        # Check exact name
        if file_path.name in self.unwanted_criteria["exact_names"]:
            return True, f"Unwanted exact name: {file_path.name}"
        
        # Check patterns
        for pattern in self.unwanted_criteria["patterns"]:
            if pattern.replace("*", "") in file_path.name:
                return True, f"Unwanted pattern: {pattern}"
        
        # Check if in unwanted directory
        for unwanted_dir in self.unwanted_criteria["directories"]:
            if unwanted_dir in file_path.parts:
                return True, f"Unwanted directory: {unwanted_dir}"
        
        return False, "File is wanted"
    
    def find_safe_duplicates(self) -> Dict:
        """Find duplicates that are safe to remove"""
        
        duplicates = []
        file_hashes = {}
        
        # Scan only non-protected areas
        scan_paths = [
            self.workspace_path / "shared-tools",
            self.workspace_path / "workspace-automation"
        ]
        
        for scan_path in scan_paths:
            if not scan_path.exists():
                continue
                
            for file_path in scan_path.rglob("*"):
                if not file_path.is_file():
                    continue
                
                # Check if unwanted
                is_unwanted, reason = self.is_unwanted_file(file_path)
                
                if is_unwanted:
                    # Calculate hash for exact duplicates
                    try:
                        file_hash = hashlib.md5(file_path.read_bytes()).hexdigest()
                        
                        if file_hash in file_hashes:
                            duplicates.append({
                                "original": str(file_hashes[file_hash]),
                                "duplicate": str(file_path),
                                "reason": reason,
                                "hash": file_hash,
                                "size": file_path.stat().st_size
                            })
                        else:
                            file_hashes[file_hash] = file_path
                    except:
                        pass
        
        return {
            "safe_duplicates": duplicates,
            "criteria_used": self.unwanted_criteria,
            "protected_paths": self.protected_paths,
            "total_found": len(duplicates)
        }

if __name__ == "__main__":
    detector = SafeDuplicateDetector()
    result = detector.find_safe_duplicates()
    
    print(f"=== SAFE DUPLICATE DETECTION ===")
    print(f"Criteria: {result['criteria_used']}")
    print(f"Protected: {result['protected_paths']}")
    print(f"Safe duplicates found: {result['total_found']}")
    
    for dup in result['safe_duplicates'][:5]:  # Show first 5
        print(f"  - {dup['duplicate']} (reason: {dup['reason']})")

