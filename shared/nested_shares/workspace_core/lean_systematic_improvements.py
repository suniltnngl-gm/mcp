#!/usr/bin/env python3
"""Lean Systematic Improvements - Integration with lean versioning, no backup overhead"""

from shared_tools.utils.config_utils import get_workspace_path
import json
from pathlib import Path
from datetime import datetime
from lean_file_versioning import LeanFileVersioning

class LeanSystematicImprovements:
    def __init__(self):
        self.versioning = LeanFileVersioning()
        self.workspace_path = get_workspace_path()
        
    def lean_improvement_workflow(self, file_path: str, improvement_type: str, 
                                 agent_context: str, notes: str = "") -> dict:
        """Lean improvement workflow - versions without backup overhead"""
        
        print(f"🔄 LEAN IMPROVEMENT: {Path(file_path).name}")
        
        # 1. Create version snapshot BEFORE improvement
        pre_version_id = self.versioning.create_version_snapshot(
            file_path, f"pre_{improvement_type}", agent_context, 
            f"Before {improvement_type}: {notes}"
        )
        
        if pre_version_id.startswith("error_"):
            return {"error": pre_version_id, "workflow_status": "failed"}
        
        print(f"   📸 Pre-improvement snapshot: {pre_version_id[:16]}...")
        
        return {
            "pre_version_id": pre_version_id,
            "file_path": file_path,
            "improvement_type": improvement_type,
            "agent_context": agent_context,
            "workflow_status": "ready_for_improvement",
            "next_step": "Make improvements to file, then call finalize_lean_improvement()"
        }
    
    def finalize_lean_improvement(self, pre_version_id: str, 
                                 improvement_description: str = "") -> dict:
        """Finalize improvement with post-version snapshot and analysis"""
        
        # Get file path from pre-version
        versions = self.versioning._load_versions_registry()
        if pre_version_id not in versions:
            return {"error": "Pre-version not found", "status": "failed"}
        
        pre_version_data = versions[pre_version_id]
        file_path = pre_version_data["file_path"]
        improvement_type = pre_version_data["improvement_type"].replace("pre_", "")
        agent_context = pre_version_data["agent_context"]
        
        print(f"🎯 FINALIZING: {Path(file_path).name}")
        
        # 2. Create version snapshot AFTER improvement
        post_version_id = self.versioning.create_version_snapshot(
            file_path, f"post_{improvement_type}", agent_context,
            f"After {improvement_type}: {improvement_description}"
        )
        
        if post_version_id.startswith("error_"):
            return {"error": post_version_id, "status": "failed"}
        
        print(f"   📸 Post-improvement snapshot: {post_version_id[:16]}...")
        
        # 3. Compare versions for learning
        comparison = self.versioning.compare_versions(pre_version_id, post_version_id)
        
        print(f"   📊 Analysis:")
        print(f"      Lines changed: {comparison.get('line_change', 0):+d}")
        print(f"      Functions changed: {comparison.get('function_change', 0):+d}")
        print(f"      Size changed: {comparison.get('size_change', 0):+d} chars")
        print(f"      Similarity: {comparison.get('similarity', 0):.2f}")
        
        # 4. Record improvement in systematic framework
        improvement_record = {
            "improvement_id": f"{improvement_type}_{int(datetime.now().timestamp())}",
            "file_path": file_path,
            "improvement_type": improvement_type,
            "agent_context": agent_context,
            "pre_version_id": pre_version_id,
            "post_version_id": post_version_id,
            "improvement_description": improvement_description,
            "analysis": comparison,
            "completed_at": datetime.now().isoformat(),
            "learning_value": "high" if abs(comparison.get('line_change', 0)) > 10 else "medium"
        }
        
        self._record_improvement(improvement_record)
        
        return {
            "improvement_id": improvement_record["improvement_id"],
            "pre_version_id": pre_version_id,
            "post_version_id": post_version_id,
            "analysis": comparison,
            "status": "completed",
            "learning_extracted": True
        }
    
    def lean_consolidation_workflow(self, file_paths: list, consolidation_type: str,
                                   agent_context: str, target_file: str = None) -> dict:
        """Lean consolidation workflow for multiple files"""
        
        print(f"🔗 LEAN CONSOLIDATION: {len(file_paths)} files")
        
        # Create pre-consolidation snapshots for all files
        pre_version_ids = {}
        
        for file_path in file_paths:
            pre_version_id = self.versioning.create_version_snapshot(
                file_path, f"pre_{consolidation_type}", agent_context,
                f"Before consolidation into {target_file or 'merged_file'}"
            )
            
            if not pre_version_id.startswith("error_"):
                pre_version_ids[file_path] = pre_version_id
                print(f"   📸 {Path(file_path).name}: {pre_version_id[:16]}...")
        
        return {
            "pre_version_ids": pre_version_ids,
            "consolidation_type": consolidation_type,
            "agent_context": agent_context,
            "target_file": target_file,
            "workflow_status": "ready_for_consolidation",
            "next_step": "Perform consolidation, then call finalize_lean_consolidation()"
        }
    
    def finalize_lean_consolidation(self, pre_version_ids: dict, target_file: str,
                                   consolidation_description: str = "") -> dict:
        """Finalize consolidation with analysis"""
        
        print(f"🎯 FINALIZING CONSOLIDATION: {Path(target_file).name}")
        
        # Get consolidation details from first pre-version
        first_pre_version = list(pre_version_ids.values())[0]
        versions = self.versioning._load_versions_registry()
        
        if first_pre_version not in versions:
            return {"error": "Pre-version data not found", "status": "failed"}
        
        pre_version_data = versions[first_pre_version]
        consolidation_type = pre_version_data["improvement_type"].replace("pre_", "")
        agent_context = pre_version_data["agent_context"]
        
        # Create post-consolidation snapshot
        post_version_id = self.versioning.create_version_snapshot(
            target_file, f"post_{consolidation_type}", agent_context,
            f"After consolidation: {consolidation_description}"
        )
        
        if post_version_id.startswith("error_"):
            return {"error": post_version_id, "status": "failed"}
        
        print(f"   📸 Consolidated result: {post_version_id[:16]}...")
        
        # Analyze consolidation impact
        source_files = list(pre_version_ids.keys())
        total_source_size = sum(
            versions[vid]["size"] for vid in pre_version_ids.values()
            if vid in versions
        )
        
        target_size = versions[post_version_id]["size"]
        consolidation_ratio = target_size / total_source_size if total_source_size > 0 else 0
        
        print(f"   📊 Consolidation Analysis:")
        print(f"      Source files: {len(source_files)}")
        print(f"      Total source size: {total_source_size} chars")
        print(f"      Target size: {target_size} chars")
        print(f"      Consolidation ratio: {consolidation_ratio:.2f}")
        
        # Record consolidation
        consolidation_record = {
            "consolidation_id": f"{consolidation_type}_{int(datetime.now().timestamp())}",
            "source_files": source_files,
            "target_file": target_file,
            "consolidation_type": consolidation_type,
            "agent_context": agent_context,
            "pre_version_ids": pre_version_ids,
            "post_version_id": post_version_id,
            "consolidation_description": consolidation_description,
            "analysis": {
                "source_count": len(source_files),
                "total_source_size": total_source_size,
                "target_size": target_size,
                "consolidation_ratio": consolidation_ratio,
                "efficiency": "high" if consolidation_ratio < 0.8 else "medium"
            },
            "completed_at": datetime.now().isoformat(),
            "learning_value": "high"
        }
        
        self._record_consolidation(consolidation_record)
        
        return {
            "consolidation_id": consolidation_record["consolidation_id"],
            "pre_version_ids": pre_version_ids,
            "post_version_id": post_version_id,
            "analysis": consolidation_record["analysis"],
            "status": "completed",
            "learning_extracted": True
        }
    
    def get_improvement_history(self, file_path: str = None) -> dict:
        """Get improvement history for learning and analysis"""
        
        improvements_file = self.workspace_path / ".versions" / "improvements.json"
        consolidations_file = self.workspace_path / ".versions" / "consolidations.json"
        
        history = {
            "improvements": [],
            "consolidations": [],
            "total_improvements": 0,
            "total_consolidations": 0
        }
        
        # Load improvements
        if improvements_file.exists():
            try:
                improvements_data = json.loads(improvements_file.read_text())
                all_improvements = improvements_data.get("improvements", [])
                
                if file_path:
                    # Filter by file path
                    history["improvements"] = [
                        imp for imp in all_improvements 
                        if imp.get("file_path") == file_path
                    ]
                else:
                    history["improvements"] = all_improvements[-20:]  # Recent 20
                
                history["total_improvements"] = len(all_improvements)
            except:
                pass
        
        # Load consolidations
        if consolidations_file.exists():
            try:
                consolidations_data = json.loads(consolidations_file.read_text())
                all_consolidations = consolidations_data.get("consolidations", [])
                
                if file_path:
                    # Filter by target file or source files
                    history["consolidations"] = [
                        cons for cons in all_consolidations
                        if (cons.get("target_file") == file_path or 
                            file_path in cons.get("source_files", []))
                    ]
                else:
                    history["consolidations"] = all_consolidations[-10:]  # Recent 10
                
                history["total_consolidations"] = len(all_consolidations)
            except:
                pass
        
        return history
    
    def _record_improvement(self, improvement_record: dict):
        """Record improvement in systematic framework"""
        
        improvements_file = self.workspace_path / ".versions" / "improvements.json"
        
        if improvements_file.exists():
            try:
                data = json.loads(improvements_file.read_text())
            except:
                data = {"improvements": []}
        else:
            data = {"improvements": []}
        
        data["improvements"].append(improvement_record)
        
        # Keep recent improvements (lazy cleanup)
        data["improvements"] = data["improvements"][-100:]
        
        improvements_file.write_text(json.dumps(data, indent=2))
    
    def _record_consolidation(self, consolidation_record: dict):
        """Record consolidation in systematic framework"""
        
        consolidations_file = self.workspace_path / ".versions" / "consolidations.json"
        
        if consolidations_file.exists():
            try:
                data = json.loads(consolidations_file.read_text())
            except:
                data = {"consolidations": []}
        else:
            data = {"consolidations": []}
        
        data["consolidations"].append(consolidation_record)
        
        # Keep recent consolidations (lazy cleanup)
        data["consolidations"] = data["consolidations"][-50:]
        
        consolidations_file.write_text(json.dumps(data, indent=2))

def main():
    """Demonstrate lean systematic improvements"""
    
    lean_improvements = LeanSystematicImprovements()
    
    print("🔄 LEAN SYSTEMATIC IMPROVEMENTS")
    print("Versions without backup/rollback overhead - preserves all information\n")
    
    print("🎯 LEAN PRINCIPLES:")
    print("   ✅ No backup files (content stored in version registry)")
    print("   ✅ No rollback overhead (versions are permanent record)")
    print("   ✅ Lazy cleanup (preserve learning, clean when needed)")
    print("   ✅ Error learning compatible (extract insights before cleanup)")
    print("   ✅ Agent session tracking (link improvements to contexts)")
    
    print(f"\n📋 LEAN WORKFLOWS:")
    print("1. lean_improvement_workflow() - Single file improvement")
    print("2. finalize_lean_improvement() - Complete with analysis")
    print("3. lean_consolidation_workflow() - Multi-file consolidation")
    print("4. finalize_lean_consolidation() - Complete with analysis")
    print("5. get_improvement_history() - Learning and analysis")
    
    print(f"\n🧠 LEARNING INTEGRATION:")
    print("   - Version evolution tracking")
    print("   - Improvement pattern analysis")
    print("   - Consolidation efficiency metrics")
    print("   - Agent context correlation")
    print("   - Error prevention insights")
    
    # Get current improvement history
    history = lean_improvements.get_improvement_history()
    
    print(f"\n📊 CURRENT STATUS:")
    print(f"   Total improvements tracked: {history['total_improvements']}")
    print(f"   Total consolidations tracked: {history['total_consolidations']}")
    print(f"   Recent improvements: {len(history['improvements'])}")
    print(f"   Recent consolidations: {len(history['consolidations'])}")
    
    print(f"\n✅ LEAN SYSTEMATIC IMPROVEMENTS READY")
    print(f"🎯 Versions over backups - preserves information, learns from errors!")

if __name__ == "__main__":
    main()
