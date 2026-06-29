#!/usr/bin/env python3
"""Lean File Versioning - Versions without backup/rollback overhead, lazy cleanup, error learning compatible"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, asdict

@dataclass
class FileVersion:
    version_id: str
    file_path: str
    version_number: int
    checksum: str
    size: int
    created: str
    agent_context: str
    improvement_type: str
    content_snapshot: str  # Store content directly
    validation_notes: str = ""
    learning_value: str = "high"  # high/medium/low for error learning

from shared_tools.utils.config_utils import get_workspace_path

class LeanFileVersioning:
    def __init__(self):
        self.workspace_path = get_workspace_path()
        self.versions_path = self.workspace_path / ".versions"
        self.versions_path.mkdir(exist_ok=True)
        
        # Single registry file - no complex backup system
        self.versions_registry = self.versions_path / "file_versions.json"
        
    def create_version_snapshot(self, file_path: str, improvement_type: str, 
                              agent_context: str, notes: str = "") -> str:
        """Create version snapshot - simple, no backup overhead"""
        
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            return f"error_file_not_found_{file_path}"
        
        # Read content and create snapshot
        content = file_path_obj.read_text(encoding='utf-8', errors='ignore')
        checksum = hashlib.md5(content.encode()).hexdigest()
        
        # Generate simple version ID
        timestamp = int(datetime.now().timestamp())
        version_id = f"{file_path_obj.stem}_{checksum[:8]}_{timestamp}"
        
        # Create version record with content snapshot
        version = FileVersion(
            version_id=version_id,
            file_path=file_path,
            version_number=self._get_next_version_number(file_path),
            checksum=checksum,
            size=len(content),
            created=datetime.now().isoformat(),
            agent_context=agent_context,
            improvement_type=improvement_type,
            content_snapshot=content,  # Store content directly
            validation_notes=notes,
            learning_value="high" if improvement_type in ["refactor", "consolidate"] else "medium"
        )
        
        # Save to registry
        self._add_version_to_registry(version)
        
        return version_id
    
    def get_version_content(self, version_id: str) -> str:
        """Get content of specific version - no file system overhead"""
        
        versions = self._load_versions_registry()
        
        if version_id in versions:
            return versions[version_id]["content_snapshot"]
        
        return ""
    
    def compare_versions(self, version_id_1: str, version_id_2: str) -> dict:
        """Compare two versions for learning purposes"""
        
        content_1 = self.get_version_content(version_id_1)
        content_2 = self.get_version_content(version_id_2)
        
        if not content_1 or not content_2:
            return {"error": "Version content not found"}
        
        # Simple comparison metrics
        lines_1 = len(content_1.splitlines())
        lines_2 = len(content_2.splitlines())
        
        # Function/class count comparison
        functions_1 = content_1.count('def ')
        functions_2 = content_2.count('def ')
        classes_1 = content_1.count('class ')
        classes_2 = content_2.count('class ')
        
        return {
            "version_1": version_id_1,
            "version_2": version_id_2,
            "line_change": lines_2 - lines_1,
            "function_change": functions_2 - functions_1,
            "class_change": classes_2 - classes_1,
            "size_change": len(content_2) - len(content_1),
            "similarity": self._calculate_similarity(content_1, content_2),
            "comparison_type": "version_evolution_analysis"
        }
    
    def _calculate_similarity(self, content1: str, content2: str) -> float:
        """Calculate content similarity for learning"""
        
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def lazy_cleanup_old_versions(self, keep_versions_per_file: int = 5) -> dict:
        """Lazy cleanup - keep recent versions, learn from old ones before cleanup"""
        
        print(f"🧹 LAZY CLEANUP: Keeping {keep_versions_per_file} versions per file")
        
        versions = self._load_versions_registry()
        
        # Group versions by file
        file_versions = {}
        for version_id, version_data in versions.items():
            file_path = version_data["file_path"]
            if file_path not in file_versions:
                file_versions[file_path] = []
            file_versions[file_path].append((version_id, version_data))
        
        cleanup_stats = {
            "files_processed": 0,
            "versions_kept": 0,
            "versions_cleaned": 0,
            "learning_data_extracted": 0
        }
        
        # Process each file's versions
        for file_path, file_version_list in file_versions.items():
            # Sort by creation date (newest first)
            sorted_versions = sorted(file_version_list, 
                                   key=lambda x: x[1]["created"], reverse=True)
            
            # Keep recent versions
            keep_versions = sorted_versions[:keep_versions_per_file]
            cleanup_versions = sorted_versions[keep_versions_per_file:]
            
            # Extract learning data from versions being cleaned
            for version_id, version_data in cleanup_versions:
                if version_data.get("learning_value") == "high":
                    self._extract_learning_data(version_id, version_data)
                    cleanup_stats["learning_data_extracted"] += 1
                
                # Remove from registry (lazy cleanup)
                del versions[version_id]
                cleanup_stats["versions_cleaned"] += 1
            
            cleanup_stats["versions_kept"] += len(keep_versions)
            cleanup_stats["files_processed"] += 1
        
        # Save updated registry
        self._save_versions_registry(versions)
        
        print(f"   ✅ Processed {cleanup_stats['files_processed']} files")
        print(f"   📋 Kept {cleanup_stats['versions_kept']} recent versions")
        print(f"   🧹 Cleaned {cleanup_stats['versions_cleaned']} old versions")
        print(f"   🧠 Extracted learning from {cleanup_stats['learning_data_extracted']} versions")
        
        return cleanup_stats
    
    def _extract_learning_data(self, version_id: str, version_data: dict):
        """Extract learning data from version before cleanup"""
        
        learning_file = self.versions_path / "version_learning_data.json"
        
        # Load existing learning data
        if learning_file.exists():
            try:
                learning_data = json.loads(learning_file.read_text())
            except:
                learning_data = {"learning_records": []}
        else:
            learning_data = {"learning_records": []}
        
        # Extract key learning points
        learning_record = {
            "version_id": version_id,
            "file_path": version_data["file_path"],
            "improvement_type": version_data["improvement_type"],
            "agent_context": version_data["agent_context"],
            "size": version_data["size"],
            "created": version_data["created"],
            "learning_insights": self._analyze_version_for_learning(version_data),
            "extracted_at": datetime.now().isoformat()
        }
        
        learning_data["learning_records"].append(learning_record)
        
        # Keep only recent learning records (lazy cleanup here too)
        learning_data["learning_records"] = learning_data["learning_records"][-100:]
        
        # Save learning data
        learning_file.write_text(json.dumps(learning_data, indent=2))
    
    def _analyze_version_for_learning(self, version_data: dict) -> dict:
        """Analyze version for learning insights"""
        
        content = version_data.get("content_snapshot", "")
        
        insights = {
            "code_patterns": [],
            "improvement_patterns": [],
            "risk_indicators": []
        }
        
        # Analyze code patterns
        if "def " in content:
            insights["code_patterns"].append(f"functions: {content.count('def ')}")
        if "class " in content:
            insights["code_patterns"].append(f"classes: {content.count('class ')}")
        
        # Analyze improvement patterns
        improvement_type = version_data.get("improvement_type", "")
        if improvement_type == "refactor":
            insights["improvement_patterns"].append("refactoring_attempt")
        elif improvement_type == "consolidate":
            insights["improvement_patterns"].append("consolidation_attempt")
        
        # Analyze risk indicators
        if "TODO" in content or "FIXME" in content:
            insights["risk_indicators"].append("incomplete_implementation")
        if "# simulate" in content.lower() or "# mock" in content.lower():
            insights["risk_indicators"].append("simulation_code_present")
        
        return insights
    
    def get_file_version_history(self, file_path: str) -> list:
        """Get version history for specific file - for learning and comparison"""
        
        versions = self._load_versions_registry()
        file_versions = []
        
        for version_id, version_data in versions.items():
            if version_data["file_path"] == file_path:
                file_versions.append({
                    "version_id": version_id,
                    "version_number": version_data["version_number"],
                    "created": version_data["created"],
                    "improvement_type": version_data["improvement_type"],
                    "agent_context": version_data["agent_context"],
                    "size": version_data["size"],
                    "checksum": version_data["checksum"][:8]
                })
        
        # Sort by version number
        return sorted(file_versions, key=lambda x: x["version_number"])
    
    def _get_next_version_number(self, file_path: str) -> int:
        """Get next version number for file"""
        
        versions = self._load_versions_registry()
        max_version = 0
        
        for version_data in versions.values():
            if version_data["file_path"] == file_path:
                max_version = max(max_version, version_data["version_number"])
        
        return max_version + 1
    
    def _add_version_to_registry(self, version: FileVersion):
        """Add version to registry"""
        
        versions = self._load_versions_registry()
        versions[version.version_id] = asdict(version)
        self._save_versions_registry(versions)
    
    def _load_versions_registry(self) -> dict:
        """Load versions registry"""
        
        if self.versions_registry.exists():
            try:
                return json.loads(self.versions_registry.read_text())
            except:
                pass
        return {}
    
    def _save_versions_registry(self, versions: dict):
        """Save versions registry"""
        
        self.versions_registry.write_text(json.dumps(versions, indent=2))

def main():
    """Demonstrate lean file versioning system"""
    
    versioning = LeanFileVersioning()
    
    print("📝 LEAN FILE VERSIONING SYSTEM")
    print("Versions without backup/rollback overhead - lazy cleanup compatible\n")
    
    print("🎯 KEY PRINCIPLES:")
    print("   ✅ Store versions as content snapshots (no file system overhead)")
    print("   ✅ Preserve all information (no backup/rollback deletion)")
    print("   ✅ Lazy cleanup (keep recent versions, learn from old)")
    print("   ✅ Error learning compatible (extract insights before cleanup)")
    print("   ✅ Agent context tracking (link versions to sessions)")
    
    print(f"\n📋 LEAN WORKFLOW:")
    print("1. create_version_snapshot() - Store current state before improvement")
    print("2. Make improvements directly to file")
    print("3. create_version_snapshot() - Store improved state")
    print("4. compare_versions() - Analyze changes for learning")
    print("5. lazy_cleanup_old_versions() - Clean when needed, preserve learning")
    
    print(f"\n🧠 LEARNING INTEGRATION:")
    print("   - Extract insights from versions before cleanup")
    print("   - Track improvement patterns across agent sessions")
    print("   - Preserve error examples for future prevention")
    print("   - Maintain version evolution history")
    
    print(f"\n📁 STORAGE:")
    print(f"   Versions: {versioning.versions_path}/file_versions.json")
    print(f"   Learning: {versioning.versions_path}/version_learning_data.json")
    print("   No backup files - content stored in registry")
    
    # Demonstrate lazy cleanup
    cleanup_result = versioning.lazy_cleanup_old_versions(keep_versions_per_file=5)
    
    print(f"\n🧹 LAZY CLEANUP DEMO:")
    print(f"   Files processed: {cleanup_result['files_processed']}")
    print(f"   Versions kept: {cleanup_result['versions_kept']}")
    print(f"   Learning extracted: {cleanup_result['learning_data_extracted']}")
    
    print(f"\n✅ LEAN FILE VERSIONING READY")
    print(f"🎯 No backup overhead, preserves information, learns from errors!")

if __name__ == "__main__":
    main()
