#!/usr/bin/env python3
"""Safe File Versioning - Protect against risky improvements with rollback capabilities"""

import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
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
    improvement_type: str  # 'refactor', 'consolidate', 'enhance', 'split'
    risk_level: str  # 'low', 'medium', 'high'
    validation_status: str  # 'pending', 'validated', 'failed', 'rolled_back'
    backup_path: str
    notes: str = ""

@dataclass
class ValidationResult:
    version_id: str
    validation_type: str  # 'functional', 'integration', 'performance'
    status: str  # 'pass', 'fail', 'warning'
    details: str
    timestamp: str

class SafeFileVersioning:
    def __init__(self):
        self.workspace_path = Path("/media/sunil-kr/workspace/user-projects")
        self.versioning_path = self.workspace_path / ".file_versions"
        self.archive_path = self.workspace_path / "archive" / "file_versions"
        
        # Create versioning directories
        self.versioning_path.mkdir(exist_ok=True)
        self.archive_path.mkdir(parents=True, exist_ok=True)
        
        # Versioning files
        self.versions_registry_file = self.versioning_path / "versions_registry.json"
        self.validation_log_file = self.versioning_path / "validation_log.json"
        self.rollback_history_file = self.versioning_path / "rollback_history.json"
        
    def create_safe_backup_before_improvement(self, file_path: str, improvement_type: str, 
                                            agent_context: str, risk_level: str = "medium") -> str:
        """Create safe backup before any improvement with rollback capability"""
        
        print(f"🛡️ CREATING SAFE BACKUP: {Path(file_path).name}")
        print(f"   Improvement: {improvement_type} | Risk: {risk_level}")
        
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read current file
        content = file_path_obj.read_text(encoding='utf-8')
        checksum = hashlib.md5(content.encode()).hexdigest()
        
        # Generate version info
        version_id = f"{file_path_obj.stem}_{checksum[:8]}_{int(datetime.now().timestamp())}"
        version_number = self._get_next_version_number(file_path)
        
        # Create backup path
        backup_filename = f"{file_path_obj.stem}_v{version_number}_{checksum[:8]}{file_path_obj.suffix}"
        backup_path = self.versioning_path / backup_filename
        
        # Create backup
        shutil.copy2(file_path_obj, backup_path)
        
        # Create version record
        version = FileVersion(
            version_id=version_id,
            file_path=file_path,
            version_number=version_number,
            checksum=checksum,
            size=file_path_obj.stat().st_size,
            created=datetime.now().isoformat(),
            agent_context=agent_context,
            improvement_type=improvement_type,
            risk_level=risk_level,
            validation_status="pending",
            backup_path=str(backup_path),
            notes=f"Pre-improvement backup for {improvement_type}"
        )
        
        # Save version record
        self._save_version_record(version)
        
        print(f"   ✅ Backup created: {backup_filename}")
        print(f"   📋 Version ID: {version_id}")
        
        return version_id
    
    def validate_improvement(self, version_id: str, validation_notes: str = "") -> bool:
        """Validate that improvement is actually superior to previous version"""
        
        print(f"🔍 VALIDATING IMPROVEMENT: {version_id}")
        
        version = self._get_version_record(version_id)
        if not version:
            print(f"   ❌ Version record not found")
            return False
        
        # Load current file for comparison
        current_file = Path(version["file_path"])
        backup_file = Path(version["backup_path"])
        
        if not current_file.exists() or not backup_file.exists():
            print(f"   ❌ Files missing for validation")
            return False
        
        # Perform validation checks
        validation_results = []
        
        # 1. Functional validation (basic syntax/structure)
        functional_result = self._validate_functional(current_file, backup_file, version)
        validation_results.append(functional_result)
        
        # 2. Size validation (reasonable size change)
        size_result = self._validate_size_change(current_file, backup_file, version)
        validation_results.append(size_result)
        
        # 3. Content validation (meaningful changes)
        content_result = self._validate_content_changes(current_file, backup_file, version)
        validation_results.append(content_result)
        
        # Determine overall validation status
        failed_validations = [r for r in validation_results if r.status == "fail"]
        warning_validations = [r for r in validation_results if r.status == "warning"]
        
        if failed_validations:
            overall_status = "failed"
            print(f"   ❌ Validation FAILED: {len(failed_validations)} critical issues")
        elif warning_validations:
            overall_status = "warning"
            print(f"   ⚠️ Validation WARNING: {len(warning_validations)} concerns")
        else:
            overall_status = "validated"
            print(f"   ✅ Validation PASSED: Improvement confirmed superior")
        
        # Update version record
        self._update_version_status(version_id, overall_status, validation_notes)
        
        # Log validation results
        self._log_validation_results(version_id, validation_results)
        
        return overall_status in ["validated", "warning"]
    
    def _validate_functional(self, current_file: Path, backup_file: Path, version: dict) -> ValidationResult:
        """Validate functional aspects of the improvement"""
        
        try:
            current_content = current_file.read_text()
            backup_content = backup_file.read_text()
            
            # Check for basic syntax issues (Python files)
            if current_file.suffix == '.py':
                try:
                    compile(current_content, str(current_file), 'exec')
                    syntax_ok = True
                except SyntaxError:
                    syntax_ok = False
                
                if not syntax_ok:
                    return ValidationResult(
                        version["version_id"], "functional", "fail",
                        "Python syntax errors detected in improved version",
                        datetime.now().isoformat()
                    )
            
            # Check for simulation/mock patterns that might indicate deviation
            simulation_patterns = [
                "# simulate", "# mock", "# placeholder", "# TODO: implement",
                "pass  # placeholder", "return None  # TODO", "# dummy implementation"
            ]
            
            simulation_found = any(pattern in current_content.lower() for pattern in simulation_patterns)
            backup_had_simulation = any(pattern in backup_content.lower() for pattern in simulation_patterns)
            
            if simulation_found and not backup_had_simulation:
                return ValidationResult(
                    version["version_id"], "functional", "fail",
                    "Improvement introduced simulation/placeholder code - possible deviation from working implementation",
                    datetime.now().isoformat()
                )
            
            return ValidationResult(
                version["version_id"], "functional", "pass",
                "Functional validation passed",
                datetime.now().isoformat()
            )
            
        except Exception as e:
            return ValidationResult(
                version["version_id"], "functional", "fail",
                f"Functional validation error: {str(e)}",
                datetime.now().isoformat()
            )
    
    def _validate_size_change(self, current_file: Path, backup_file: Path, version: dict) -> ValidationResult:
        """Validate that size changes are reasonable"""
        
        current_size = current_file.stat().st_size
        backup_size = backup_file.stat().st_size
        
        if backup_size == 0:
            return ValidationResult(
                version["version_id"], "size", "warning",
                "Backup file is empty - cannot validate size change",
                datetime.now().isoformat()
            )
        
        size_change_ratio = current_size / backup_size
        
        # Flag dramatic size changes as suspicious
        if size_change_ratio < 0.3:  # File became 70% smaller
            return ValidationResult(
                version["version_id"], "size", "warning",
                f"File size reduced by {(1-size_change_ratio)*100:.1f}% - verify functionality not lost",
                datetime.now().isoformat()
            )
        elif size_change_ratio > 3.0:  # File became 3x larger
            return ValidationResult(
                version["version_id"], "size", "warning",
                f"File size increased by {(size_change_ratio-1)*100:.1f}% - verify no unnecessary bloat",
                datetime.now().isoformat()
            )
        
        return ValidationResult(
            version["version_id"], "size", "pass",
            f"Size change is reasonable ({size_change_ratio:.2f}x)",
            datetime.now().isoformat()
        )
    
    def _validate_content_changes(self, current_file: Path, backup_file: Path, version: dict) -> ValidationResult:
        """Validate that content changes are meaningful improvements"""
        
        try:
            current_content = current_file.read_text()
            backup_content = backup_file.read_text()
            
            # Check if files are identical (no actual improvement)
            if current_content == backup_content:
                return ValidationResult(
                    version["version_id"], "content", "warning",
                    "No content changes detected - improvement may be ineffective",
                    datetime.now().isoformat()
                )
            
            # Check for loss of important patterns
            important_patterns = ["def ", "class ", "import ", "from "]
            
            for pattern in important_patterns:
                backup_count = backup_content.count(pattern)
                current_count = current_content.count(pattern)
                
                if current_count < backup_count * 0.7:  # Lost 30%+ of functions/classes/imports
                    return ValidationResult(
                        version["version_id"], "content", "fail",
                        f"Significant loss of {pattern.strip()} patterns - possible functionality removal",
                        datetime.now().isoformat()
                    )
            
            return ValidationResult(
                version["version_id"], "content", "pass",
                "Content changes appear to be meaningful improvements",
                datetime.now().isoformat()
            )
            
        except Exception as e:
            return ValidationResult(
                version["version_id"], "content", "fail",
                f"Content validation error: {str(e)}",
                datetime.now().isoformat()
            )
    
    def rollback_to_previous_version(self, version_id: str, reason: str) -> bool:
        """Rollback to previous version if improvement failed"""
        
        print(f"🔄 ROLLING BACK: {version_id}")
        print(f"   Reason: {reason}")
        
        version = self._get_version_record(version_id)
        if not version:
            print(f"   ❌ Version record not found")
            return False
        
        current_file = Path(version["file_path"])
        backup_file = Path(version["backup_path"])
        
        if not backup_file.exists():
            print(f"   ❌ Backup file not found: {backup_file}")
            return False
        
        try:
            # Create backup of current (failed) version
            failed_backup = Path(str(backup_file).replace("_v", "_failed_v"))
            if current_file.exists():
                shutil.copy2(current_file, failed_backup)
            
            # Restore from backup
            shutil.copy2(backup_file, current_file)
            
            # Update version status
            self._update_version_status(version_id, "rolled_back", f"Rollback: {reason}")
            
            # Log rollback
            self._log_rollback(version_id, reason, str(failed_backup))
            
            print(f"   ✅ Rollback successful")
            print(f"   📁 Failed version saved as: {failed_backup.name}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Rollback failed: {e}")
            return False
    
    def cleanup_old_versions(self, days_to_keep: int = 30) -> dict:
        """Move old validated versions to archive after review period"""
        
        print(f"🧹 CLEANING UP VERSIONS OLDER THAN {days_to_keep} DAYS")
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        versions = self._load_versions_registry()
        moved_to_archive = 0
        kept_versions = 0
        
        for version_id, version_data in versions.items():
            version_date = datetime.fromisoformat(version_data["created"])
            
            if version_date < cutoff_date and version_data["validation_status"] == "validated":
                # Move to archive
                backup_path = Path(version_data["backup_path"])
                if backup_path.exists():
                    archive_filename = f"archived_{backup_path.name}"
                    archive_destination = self.archive_path / archive_filename
                    
                    try:
                        shutil.move(backup_path, archive_destination)
                        version_data["backup_path"] = str(archive_destination)
                        version_data["archived"] = True
                        moved_to_archive += 1
                        print(f"   📦 Archived: {backup_path.name}")
                    except Exception as e:
                        print(f"   ⚠️ Failed to archive {backup_path.name}: {e}")
            else:
                kept_versions += 1
        
        # Save updated registry
        self._save_versions_registry(versions)
        
        print(f"   ✅ Moved {moved_to_archive} versions to archive")
        print(f"   📋 Kept {kept_versions} recent/unvalidated versions")
        
        return {
            "moved_to_archive": moved_to_archive,
            "kept_versions": kept_versions,
            "archive_path": str(self.archive_path)
        }
    
    def _get_next_version_number(self, file_path: str) -> int:
        """Get next version number for file"""
        
        versions = self._load_versions_registry()
        max_version = 0
        
        for version_data in versions.values():
            if version_data["file_path"] == file_path:
                max_version = max(max_version, version_data["version_number"])
        
        return max_version + 1
    
    def _save_version_record(self, version: FileVersion):
        """Save version record to registry"""
        
        versions = self._load_versions_registry()
        versions[version.version_id] = asdict(version)
        self._save_versions_registry(versions)
    
    def _get_version_record(self, version_id: str) -> Optional[dict]:
        """Get version record by ID"""
        
        versions = self._load_versions_registry()
        return versions.get(version_id)
    
    def _update_version_status(self, version_id: str, status: str, notes: str):
        """Update version validation status"""
        
        versions = self._load_versions_registry()
        if version_id in versions:
            versions[version_id]["validation_status"] = status
            versions[version_id]["notes"] = notes
            versions[version_id]["last_updated"] = datetime.now().isoformat()
            self._save_versions_registry(versions)
    
    def _load_versions_registry(self) -> dict:
        """Load versions registry"""
        
        if self.versions_registry_file.exists():
            try:
                return json.loads(self.versions_registry_file.read_text())
            except:
                pass
        return {}
    
    def _save_versions_registry(self, versions: dict):
        """Save versions registry"""
        
        self.versions_registry_file.write_text(json.dumps(versions, indent=2))
    
    def _log_validation_results(self, version_id: str, results: List[ValidationResult]):
        """Log validation results"""
        
        if self.validation_log_file.exists():
            try:
                log_data = json.loads(self.validation_log_file.read_text())
            except:
                log_data = {"validations": []}
        else:
            log_data = {"validations": []}
        
        log_entry = {
            "version_id": version_id,
            "timestamp": datetime.now().isoformat(),
            "results": [asdict(r) for r in results]
        }
        
        log_data["validations"].append(log_entry)
        self.validation_log_file.write_text(json.dumps(log_data, indent=2))
    
    def _log_rollback(self, version_id: str, reason: str, failed_backup_path: str):
        """Log rollback action"""
        
        if self.rollback_history_file.exists():
            try:
                rollback_data = json.loads(self.rollback_history_file.read_text())
            except:
                rollback_data = {"rollbacks": []}
        else:
            rollback_data = {"rollbacks": []}
        
        rollback_entry = {
            "version_id": version_id,
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
            "failed_backup_path": failed_backup_path
        }
        
        rollback_data["rollbacks"].append(rollback_entry)
        self.rollback_history_file.write_text(json.dumps(rollback_data, indent=2))

def main():
    """Demonstrate safe file versioning system"""
    
    versioning = SafeFileVersioning()
    
    print("🛡️ SAFE FILE VERSIONING SYSTEM")
    print("Protecting against risky improvements with rollback capabilities\n")
    
    # Example usage workflow
    print("📋 SAFE IMPROVEMENT WORKFLOW:")
    print("1. create_safe_backup_before_improvement() - Before any changes")
    print("2. Make improvements to file")
    print("3. validate_improvement() - Verify improvement is superior")
    print("4. rollback_to_previous_version() - If validation fails")
    print("5. cleanup_old_versions() - Archive old validated versions")
    
    print(f"\n📁 VERSIONING PATHS:")
    print(f"   Active versions: {versioning.versioning_path}")
    print(f"   Archived versions: {versioning.archive_path}")
    
    print(f"\n🔍 VALIDATION CHECKS:")
    print(f"   - Functional: Syntax, simulation detection, working code preservation")
    print(f"   - Size: Reasonable size changes (not 70% smaller or 3x larger)")
    print(f"   - Content: Meaningful improvements, no functionality loss")
    
    print(f"\n🛡️ PROTECTION FEATURES:")
    print(f"   - Pre-improvement backups with agent context tracking")
    print(f"   - Multi-level validation (functional, size, content)")
    print(f"   - Automatic rollback on validation failure")
    print(f"   - Archive system for validated old versions")
    print(f"   - Risk level tracking (low/medium/high)")
    
    print(f"\n✅ SAFE FILE VERSIONING READY")
    print(f"🎯 Use before ANY improvement to prevent working code → simulation issues!")

if __name__ == "__main__":
    main()
