#!/usr/bin/env python3
"""DEPRECATED: Use existing duplicate_removal_plan.md instead
This tool was created redundantly - the workspace already has duplicate detection systems.
Use: shared-tools/config/duplicate_removal_plan.md
"""

# Original content below (deprecated)
#!/usr/bin/env python3
"""Safe duplicate remover - removes only exact duplicates, preserves all information"""

import hashlib
from pathlib import Path
from typing import Dict, List

class SafeDuplicateRemover:
    def __init__(self):
        self.workspace_path = Path("/media/sunil-kr/workspace/user-projects")
        self.protected_paths = ["archive/", "current/", ".git/", ".kiro/"]
        
    def find_exact_duplicates(self) -> List[Dict]:
        """Find files that are 100% identical (same content hash)"""
        
        file_hashes = {}
        duplicates = []
        
        # Scan only shared-tools and workspace-automation
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
                
                # Skip protected paths
                if any(protected in str(file_path) for protected in self.protected_paths):
                    continue
                
                try:
                    # Calculate content hash
                    content_hash = hashlib.md5(file_path.read_bytes()).hexdigest()
                    
                    if content_hash in file_hashes:
                        # Found exact duplicate
                        original = file_hashes[content_hash]
                        duplicates.append({
                            "original": str(original),
                            "duplicate": str(file_path),
                            "hash": content_hash,
                            "size": file_path.stat().st_size
                        })
                    else:
                        file_hashes[content_hash] = file_path
                        
                except Exception:
                    continue
        
        return duplicates
    
    def safe_remove_duplicates(self, dry_run=True) -> Dict:
        """Remove exact duplicates (keeps original, removes copies)"""
        
        duplicates = self.find_exact_duplicates()
        removed = []
        
        print(f"=== SAFE DUPLICATE REMOVAL ===")
        print(f"Mode: {'DRY RUN' if dry_run else 'ACTUAL REMOVAL'}")
        print(f"Found {len(duplicates)} exact duplicates")
        
        for dup in duplicates:
            print(f"\nOriginal: {dup['original']}")
            print(f"Duplicate: {dup['duplicate']}")
            print(f"Size: {dup['size']} bytes")
            
            if not dry_run:
                try:
                    Path(dup['duplicate']).unlink()
                    removed.append(dup['duplicate'])
                    print("✅ REMOVED")
                except Exception as e:
                    print(f"❌ ERROR: {e}")
            else:
                print("🔍 WOULD REMOVE (dry run)")
        
        return {
            "total_duplicates": len(duplicates),
            "removed_count": len(removed),
            "removed_files": removed,
            "dry_run": dry_run
        }

if __name__ == "__main__":
    remover = SafeDuplicateRemover()
    
    # First run dry run
    print("=== DRY RUN ===")
    result = remover.safe_remove_duplicates(dry_run=True)
    
    if result["total_duplicates"] > 0:
        print(f"\nFound {result['total_duplicates']} exact duplicates")
        print("Run with dry_run=False to actually remove them")
    else:
        print("No exact duplicates found - all files are unique!")

