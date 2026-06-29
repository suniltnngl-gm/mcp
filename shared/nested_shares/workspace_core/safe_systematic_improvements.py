#!/usr/bin/env python3
"""Safe Systematic Improvements - Integration of safe versioning with systematic improvement framework"""

from pathlib import Path
from datetime import datetime
from shared_tools.utils.config_utils import get_workspace_path
from safe_file_versioning import SafeFileVersioning
from systematic_improvement_framework import SystematicImprovementFramework

class SafeSystematicImprovements:
    def __init__(self):
        self.versioning = SafeFileVersioning()
        self.framework = SystematicImprovementFramework()
        self.workspace_path = get_workspace_path()
        
    def safe_improvement_workflow(self, file_path: str, improvement_type: str, 
                                 agent_context: str, risk_level: str = "medium") -> dict:
        """Execute safe improvement workflow with versioning protection"""
        
        print(f"🛡️ SAFE IMPROVEMENT WORKFLOW: {Path(file_path).name}")
        print(f"   Type: {improvement_type} | Risk: {risk_level}")
        print(f"   Agent: {agent_context}\n")
        
        workflow_result = {
            "file_path": file_path,
            "improvement_type": improvement_type,
            "risk_level": risk_level,
            "agent_context": agent_context,
            "workflow_steps": [],
            "success": False,
            "version_id": None,
            "rollback_performed": False
        }
        
        try:
            # Step 1: Create safe backup
            print("📋 Step 1: Creating safe backup...")
            version_id = self.versioning.create_safe_backup_before_improvement(
                file_path, improvement_type, agent_context, risk_level
            )
            workflow_result["version_id"] = version_id
            workflow_result["workflow_steps"].append("backup_created")
            
            # Step 2: Improvement placeholder (actual improvement would happen here)
            print("\n📋 Step 2: Ready for improvement...")
            print("   ⚠️  IMPORTANT: Make your improvements now, then call validate_improvement()")
            print("   🛡️  If validation fails, automatic rollback will be triggered")
            workflow_result["workflow_steps"].append("ready_for_improvement")
            
            # Step 3: Validation instructions
            print("\n📋 Step 3: Validation required after improvement...")
            print(f"   Call: validate_improvement('{version_id}', 'validation_notes')")
            workflow_result["workflow_steps"].append("validation_pending")
            
            workflow_result["success"] = True
            
        except Exception as e:
            print(f"   ❌ Workflow failed: {e}")
            workflow_result["error"] = str(e)
        
        return workflow_result
    
    def validate_and_finalize_improvement(self, version_id: str, validation_notes: str = "") -> dict:
        """Validate improvement and finalize or rollback"""
        
        print(f"🔍 VALIDATING AND FINALIZING: {version_id}")
        
        # Perform validation
        validation_passed = self.versioning.validate_improvement(version_id, validation_notes)
        
        result = {
            "version_id": version_id,
            "validation_passed": validation_passed,
            "action_taken": "",
            "recommendation": ""
        }
        
        if validation_passed:
            print("   ✅ Validation PASSED - Improvement finalized")
            result["action_taken"] = "improvement_finalized"
            result["recommendation"] = "Improvement is superior to previous version"
        else:
            print("   ❌ Validation FAILED - Initiating rollback...")
            rollback_success = self.versioning.rollback_to_previous_version(
                version_id, "Validation failed - improvement not superior to original"
            )
            
            if rollback_success:
                result["action_taken"] = "rollback_successful"
                result["recommendation"] = "Rolled back to previous working version"
            else:
                result["action_taken"] = "rollback_failed"
                result["recommendation"] = "CRITICAL: Manual intervention required"
        
        return result
    
    def safe_consolidation_workflow(self, target_systems: list, consolidation_type: str) -> dict:
        """Execute safe consolidation with versioning for multiple files"""
        
        print(f"🔄 SAFE CONSOLIDATION WORKFLOW")
        print(f"   Type: {consolidation_type}")
        print(f"   Systems: {len(target_systems)} files\n")
        
        consolidation_result = {
            "consolidation_type": consolidation_type,
            "target_systems": target_systems,
            "version_ids": [],
            "success_count": 0,
            "failure_count": 0,
            "rollback_count": 0
        }
        
        # Create backups for all target systems
        for system_path in target_systems:
            try:
                version_id = self.versioning.create_safe_backup_before_improvement(
                    system_path, 
                    f"consolidation_{consolidation_type}",
                    f"systematic_improvement_agent_{datetime.now().strftime('%Y%m%d')}",
                    "high"  # Consolidation is high risk
                )
                consolidation_result["version_ids"].append(version_id)
                consolidation_result["success_count"] += 1
                
            except Exception as e:
                print(f"   ❌ Failed to backup {system_path}: {e}")
                consolidation_result["failure_count"] += 1
        
        print(f"   ✅ Created {consolidation_result['success_count']} backups")
        print(f"   ⚠️  Ready for consolidation - validate each improvement after completion")
        
        return consolidation_result
    
    def batch_validate_consolidation(self, version_ids: list) -> dict:
        """Batch validate consolidation results"""
        
        print(f"🔍 BATCH VALIDATING CONSOLIDATION: {len(version_ids)} versions")
        
        batch_result = {
            "total_versions": len(version_ids),
            "validated": 0,
            "failed": 0,
            "rolled_back": 0,
            "results": []
        }
        
        for version_id in version_ids:
            try:
                validation_result = self.validate_and_finalize_improvement(
                    version_id, "Batch consolidation validation"
                )
                
                batch_result["results"].append(validation_result)
                
                if validation_result["validation_passed"]:
                    batch_result["validated"] += 1
                else:
                    batch_result["failed"] += 1
                    if validation_result["action_taken"] == "rollback_successful":
                        batch_result["rolled_back"] += 1
                        
            except Exception as e:
                print(f"   ❌ Validation error for {version_id}: {e}")
                batch_result["failed"] += 1
        
        print(f"\n📊 BATCH VALIDATION RESULTS:")
        print(f"   ✅ Validated: {batch_result['validated']}")
        print(f"   ❌ Failed: {batch_result['failed']}")
        print(f"   🔄 Rolled back: {batch_result['rolled_back']}")
        
        return batch_result
    
    def maintenance_cleanup(self, days_to_keep: int = 30) -> dict:
        """Perform maintenance cleanup of old versions"""
        
        print(f"🧹 MAINTENANCE CLEANUP")
        
        # Cleanup old versions
        cleanup_result = self.versioning.cleanup_old_versions(days_to_keep)
        
        # Generate maintenance report
        maintenance_report = {
            "cleanup_performed": True,
            "days_to_keep": days_to_keep,
            "versions_archived": cleanup_result["moved_to_archive"],
            "versions_kept": cleanup_result["kept_versions"],
            "archive_location": cleanup_result["archive_path"],
            "maintenance_date": datetime.now().isoformat()
        }
        
        return maintenance_report
    
    def get_versioning_status(self) -> dict:
        """Get current versioning system status"""
        
        versions_registry = self.versioning._load_versions_registry()
        
        status = {
            "total_versions": len(versions_registry),
            "by_status": {},
            "by_risk_level": {},
            "recent_activity": [],
            "recommendations": []
        }
        
        # Analyze versions by status
        for version_data in versions_registry.values():
            status_key = version_data.get("validation_status", "unknown")
            status["by_status"][status_key] = status["by_status"].get(status_key, 0) + 1
            
            risk_key = version_data.get("risk_level", "unknown")
            status["by_risk_level"][risk_key] = status["by_risk_level"].get(risk_key, 0) + 1
        
        # Generate recommendations
        pending_count = status["by_status"].get("pending", 0)
        failed_count = status["by_status"].get("failed", 0)
        
        if pending_count > 5:
            status["recommendations"].append(f"Review {pending_count} pending validations")
        
        if failed_count > 0:
            status["recommendations"].append(f"Investigate {failed_count} failed improvements")
        
        return status

def main():
    """Demonstrate safe systematic improvements"""
    
    safe_improvements = SafeSystematicImprovements()
    
    print("🛡️ SAFE SYSTEMATIC IMPROVEMENTS")
    print("Integration of safe versioning with systematic improvement framework\n")
    
    print("📋 SAFE WORKFLOWS AVAILABLE:")
    print("1. safe_improvement_workflow() - Single file improvement with protection")
    print("2. safe_consolidation_workflow() - Multi-file consolidation with backups")
    print("3. validate_and_finalize_improvement() - Validation with auto-rollback")
    print("4. batch_validate_consolidation() - Batch validation for consolidations")
    print("5. maintenance_cleanup() - Archive old validated versions")
    
    print(f"\n🔍 VALIDATION PROTECTION:")
    print("   - Detects working code → simulation conversion")
    print("   - Prevents functionality loss during refactoring")
    print("   - Automatic rollback on validation failure")
    print("   - Agent context tracking across sessions")
    
    print(f"\n🛡️ RISK MITIGATION:")
    print("   - Pre-improvement backups (always)")
    print("   - Multi-level validation (functional, size, content)")
    print("   - Risk level tracking (low/medium/high)")
    print("   - Archive system for validated versions")
    
    # Get current status
    status = safe_improvements.get_versioning_status()
    
    print(f"\n📊 CURRENT STATUS:")
    print(f"   Total versions tracked: {status['total_versions']}")
    
    if status["by_status"]:
        print("   By validation status:")
        for status_type, count in status["by_status"].items():
            print(f"     - {status_type}: {count}")
    
    if status["recommendations"]:
        print("   Recommendations:")
        for rec in status["recommendations"]:
            print(f"     - {rec}")
    
    print(f"\n✅ SAFE SYSTEMATIC IMPROVEMENTS READY")
    print(f"🎯 Always use safe workflows to prevent improvement risks!")

if __name__ == "__main__":
    main()
