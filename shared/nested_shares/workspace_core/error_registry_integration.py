#!/usr/bin/env python3
"""
Error Registry Integration - Connect lean versioning with error tracking
Provides comprehensive error prevention through learning from version history
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from shared_tools.nested_shares.ai.collaboration.session_error_learnings import SessionErrorLearnings
from shared_tools.analysis.dedup_checker import find_duplicates
from current.workspace_system.src import prevention_system

class ErrorRegistryIntegration:
    def __init__(self, workspace_root: str = None):
        self.workspace_root = Path(workspace_root or os.getcwd())
        self.lean_registry_path = self.workspace_root / ".kiro" / "lean_versions.json"
        self.error_registry_path = self.workspace_root / ".kiro" / "error_registry.json"
    
    def load_lean_registry(self) -> Dict:
        """Load lean versioning registry"""
        if not self.lean_registry_path.exists():
            return {"versions": {}, "sessions": {}}
        return json.loads(self.lean_registry_path.read_text())
    
    def load_error_registry(self) -> Dict:
        """Load error registry"""
        if not self.error_registry_path.exists():
            return {"errors": {}, "patterns": {}, "prevention_rules": []}
        return json.loads(self.error_registry_path.read_text())
    
    def save_error_registry(self, registry: Dict):
        """Save error registry"""
        self.error_registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.error_registry_path.write_text(json.dumps(registry, indent=2))
    
    def extract_errors_from_versions(self) -> List[Dict]:
        """Extract error data from lean versioning history"""
        lean_registry = self.load_lean_registry()
        errors = []
        
        for version_id, version in lean_registry.get("versions", {}).items():
            if version.get("errors"):
                error_data = {
                    "version_id": version_id,
                    "timestamp": version.get("timestamp"),
                    "improvement_type": version.get("improvement_type"),
                    "file_path": version.get("file_path"),
                    "errors": version["errors"],
                    "context": version.get("context", {}),
                    "severity": version.get("severity", "unknown"),  # New field
                    "source": version.get("source", "unknown"),      # New field
                    "commit_hash": version.get("commit_hash", None), # New field
                    "user": version.get("user", "unknown"),          # New field
                    "log_snippets": version.get("log_snippets", []), # New field
                    "solution_proposed": version.get("solution_proposed", None), # New field
                    "solution_applied": version.get("solution_applied", None),   # New field
                    "solution_success_rate": version.get("solution_success_rate", None), # New field
                }
                errors.append(error_data)
        
        return errors
    
    def analyze_error_patterns(self, errors: List[Dict]) -> Dict:
        """Analyze error patterns from version history"""
        patterns = {}
        
        # Group by improvement type
        by_type = {}
        for error in errors:
            imp_type = error.get("improvement_type", "unknown")
            if imp_type not in by_type:
                by_type[imp_type] = []
            by_type[imp_type].append(error)
        
        # Analyze patterns
        for imp_type, type_errors in by_type.items():
            if len(type_errors) >= 2:  # Need at least 2 to find pattern
                patterns[imp_type] = {
                    "frequency": len(type_errors),
                    "common_files": self._find_common_files(type_errors),
                    "error_types": self._categorize_errors(type_errors)
                }
        
        return patterns
    
    def _find_common_files(self, errors: List[Dict]) -> List[str]:
        """Find files that commonly have errors"""
        file_counts = {}
        for error in errors:
            file_path = error.get("file_path", "unknown")
            file_counts[file_path] = file_counts.get(file_path, 0) + 1
        
        # Return files with multiple errors
        return [f for f, count in file_counts.items() if count > 1]
    
    def _categorize_errors(self, errors: List[Dict]) -> Dict:
        """Categorize error types"""
        categories = {}
        for error in errors:
            for err in error.get("errors", []):
                err_type = err.get("type", "unknown")
                categories[err_type] = categories.get(err_type, 0) + 1
        return categories
    
    def check_for_duplicates_in_new_versions(self, versions_to_check: List[Dict]) -> List[Dict]:
        """
        Checks for duplicates among newly added versions and returns duplicate findings as errors.
        This assumes 'versions_to_check' are versions that represent new content.
        """
        duplicate_errors = []
        for version in versions_to_check:
            # Construct a title for deduplication check. This might need refinement.
            # For now, a combination of improvement_type and file_path can serve as a 'title'.
            title_for_check = f"{version.get('improvement_type', '')} in {version.get('file_path', '')}"
            
            # Only proceed if there's a meaningful title to check
            if not title_for_check.strip():
                continue

            duplicates_found = find_duplicates(title_for_check)

            if duplicates_found:
                duplicate_errors.append({
                    "version_id": version.get("version_id"),
                    "timestamp": datetime.now().isoformat(),
                    "improvement_type": version.get("improvement_type"),
                    "file_path": version.get("file_path"),
                    "errors": [{
                        "type": "DUPLICATE_DETECTED",
                        "message": f"Potential duplicate of existing content detected.",
                        "details": duplicates_found
                    }],
                    "context": version.get("context", {}),
                    "severity": "warning",
                    "source": "deduplication_checker"
                })
        return duplicate_errors

    def generate_prevention_rules(self, patterns: Dict, critical_learnings: Dict) -> List[Dict]:
        """Generate prevention rules from error patterns and critical learnings"""
        rules = []
        
        for imp_type, pattern in patterns.items():
            if pattern["frequency"] >= 3:  # High frequency errors
                rule = {
                    "rule_type": "high_frequency_prevention",
                    "improvement_type": imp_type,
                    "description": f"High error frequency in {imp_type} improvements",
                    "action": "require_extra_validation",
                    "frequency": pattern["frequency"]
                }
                rules.append(rule)
            
            if imp_type == "DUPLICATE_DETECTED" and pattern["frequency"] >= 2: # If duplicates are frequent
                rules.append({
                    "rule_type": "duplicate_content_prevention",
                    "improvement_type": "new_content_creation", # This rule applies generally to new content
                    "description": "High frequency of duplicate content detected. Review new submissions carefully.",
                    "action": "require_manual_review_for_new_content",
                    "frequency": pattern["frequency"]
                })
            
            # File-specific rules
            for file_path in pattern["common_files"]:
                rule = {
                    "rule_type": "file_specific_prevention",
                    "file_path": file_path,
                    "improvement_type": imp_type,
                    "description": f"Frequent errors in {file_path} during {imp_type}",
                    "action": "require_backup_before_change"
                }
                rules.append(rule)
        
        # Add rules from critical learnings
        for error_id, learning in critical_learnings.items():
            if error_id == "CRITICAL_ERROR_1":
                rules.append({
                    "rule_type": "vendor_package_exclusion",
                    "description": learning["fix"],
                    "action": "block_modification_or_deletion",
                    "target_patterns": [".venv/", "node_modules/", "site-packages/"],
                    "source_learning": error_id
                })
            elif error_id == "CRITICAL_ERROR_2":
                rules.append({
                    "rule_type": "existing_dedup_check",
                    "description": learning["fix"],
                    "action": "require_check_before_new_dedup_tool",
                    "required_files": ["dedup_checker.py", "duplicate_removal_plan.md"],
                    "source_learning": error_id
                })
        
        return rules


    
    def sync_with_lean_versioning(self):
        """Sync error registry with lean versioning data"""
        error_registry = self.load_error_registry()
        
        # Extract new errors
        errors = self.extract_errors_from_versions()

        # Check for duplicates in new versions
        # For simplicity, we'll check all extracted errors, but in a real scenario,
        # one might only check versions that represent "new" ideas or proposals.
        duplicate_findings = self.check_for_duplicates_in_new_versions(errors)
        errors.extend(duplicate_findings)

        
        # Update error registry
        for error in errors:
            error_id = f"{error['version_id']}_{error['timestamp']}"
            error_registry["errors"][error_id] = error
        
        # Analyze patterns
        patterns = self.analyze_error_patterns(errors)
        error_registry["patterns"] = patterns
        
        # Generate prevention rules
        rules = self.generate_prevention_rules(patterns, critical_learnings)
        error_registry["prevention_rules"] = rules

        # Add/update rules in prevention_system
        for rule in rules:
            prevention_system.add_prevention_rule(
                name=rule.get("name", rule["rule_type"]), # Use rule_type if name is not explicitly defined
                type=rule["rule_type"],
                condition=json.dumps({k: v for k, v in rule.items() if k not in ["rule_type", "name", "action", "description"]}),
                action=rule["action"],
                overhead="low" # All rules generated here are considered low overhead
            )
        
        # Integrate critical learnings from SessionErrorLearnings
        session_learnings = SessionErrorLearnings(workspace_path=self.workspace_root)
        session_learnings.analyze_critical_errors()  # Ensure critical errors are analyzed and stored
        critical_learnings = session_learnings.get_all_errors()
        error_registry["critical_learnings"] = critical_learnings
        
        # Save updated registry
        self.save_error_registry(error_registry)
        
        return {
            "errors_processed": len(errors),
            "patterns_found": len(patterns),
            "rules_generated": len(rules),
            "critical_learnings_integrated": len(critical_learnings)
        }
    
    def get_prevention_advice(self, improvement_type: str, file_path: str = None) -> List[str]:
        """Get prevention advice for specific improvement"""
        error_registry = self.load_error_registry()
        advice = []
        
        for rule in error_registry.get("prevention_rules", []):
            if rule.get("improvement_type") == improvement_type:
                advice.append(rule["description"])
            
            if file_path and rule.get("file_path") == file_path:
                advice.append(f"File-specific: {rule['description']}")
        
        return advice

def main():
    """CLI interface for error registry integration"""
    import sys
    
    integration = ErrorRegistryIntegration()
    
    if len(sys.argv) < 2:
        print("Usage: error_registry_integration.py <command>")
        print("Commands: sync, advice <improvement_type> [file_path], stats")
        return
    
    command = sys.argv[1]
    
    if command == "sync":
        result = integration.sync_with_lean_versioning()
        print(f"Sync complete: {result}")
    
    elif command == "advice" and len(sys.argv) >= 3:
        improvement_type = sys.argv[2]
        file_path = sys.argv[3] if len(sys.argv) > 3 else None
        advice = integration.get_prevention_advice(improvement_type, file_path)
        
        if advice:
            print(f"Prevention advice for {improvement_type}:")
            for item in advice:
                print(f"  • {item}")
        else:
            print(f"No specific advice for {improvement_type}")
    
    elif command == "stats":
        error_registry = integration.load_error_registry()
        print(f"Total errors: {len(error_registry.get('errors', {}))}")
        print(f"Patterns found: {len(error_registry.get('patterns', {}))}")
        print(f"Prevention rules: {len(error_registry.get('prevention_rules', []))}")

if __name__ == "__main__":
    main()
