#!/usr/bin/env python3
"""DEPRECATED: Use existing duplicate_removal_plan.md instead
This tool was created redundantly - the workspace already has duplicate detection systems.
Use: shared-tools/config/duplicate_removal_plan.md
"""

# Original content below (deprecated)
#!/usr/bin/env python3
"""Precise duplicate remover - excludes .venv and focuses on actual user duplicates"""

import hashlib
from pathlib import Path
from typing import Dict, List

class PreciseDuplicateRemover:
    def __init__(self):
        self.workspace_path = Path("/media/sunil-kr/workspace/user-projects")
        
        # STRICT exclusions - never touch these
        self.strict_exclusions = [
            "archive/",     # Reference only
            "current/",     # Active projects  
            ".git/",        # Git internals
            ".kiro/",       # Kiro config
            ".venv/",       # Python environments
            "venv/",        # Python environments
            "__pycache__/", # Python cache
            "node_modules/" # Node dependencies
        ]
        
    def find_user_duplicates(self) -> List[Dict]:
        """Find duplicates only in user-created files"""
        
        file_hashes = {}
        duplicates = []
        
        # Only scan workspace-automation (user scripts)
        scan_path = self.workspace_path / "workspace-automation"
        
        if not scan_path.exists():
            return []
            
        for file_path in scan_path.rglob("*"):
            if not file_path.is_file():
                continue
            
            # Skip all exclusions
            if any(exclusion in str(file_path) for exclusion in self.strict_exclusions):
                continue
            
            # Only process user file types
            if file_path.suffix not in ['.py', '.sh', '.md', '.json', '.txt']:
                continue
                
            try:
                content_hash = hashlib.md5(file_path.read_bytes()).hexdigest()
                
                if content_hash in file_hashes:
                    original = file_hashes[content_hash]
                    duplicates.append({
                        "original": str(original),
                        "duplicate": str(file_path),
                        "hash": content_hash,
                        "size": file_path.stat().st_size,
                        "type": "user_file"
                    })
                else:
                    file_hashes[content_hash] = file_path
                    
            except Exception:
                continue
        
        return duplicates
    
    def safe_remove_user_duplicates(self, dry_run=True) -> Dict:
        """Remove only user file duplicates"""
        
        duplicates = self.find_user_duplicates()
        removed = []
        
        print(f"=== PRECISE USER DUPLICATE REMOVAL ===")
        print(f"Mode: {'DRY RUN' if dry_run else 'ACTUAL REMOVAL'}")
        print(f"Exclusions: {self.strict_exclusions}")
        print(f"Found {len(duplicates)} user file duplicates")
        
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
            "dry_run": dry_run,
            "exclusions_applied": self.strict_exclusions
        }

if __name__ == "__main__":
    remover = PreciseDuplicateRemover()
    result = remover.safe_remove_user_duplicates(dry_run=True)
    
    if result["total_duplicates"] == 0:
        print("\n✅ No user file duplicates found - workspace is clean!")
    else:
        print(f"\nFound {result['total_duplicates']} user duplicates")
        print("These are safe to remove (user files only, no dependencies)")

