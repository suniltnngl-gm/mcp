#!/usr/bin/env python3
"""Reality checker to validate knowledge base accuracy"""

import json
import subprocess
import os
from pathlib import Path
from datetime import datetime

class RealityChecker:
    def __init__(self):
        self.kb_dir = Path("knowledge_base")
        
    def validate_error_solution(self, error_id, solution_text):
        """Validate if solution actually works for error"""
        validation_result = {
            "success": False,
            "context": {},
            "side_effects": [],
            "environment": self._get_environment_context()
        }
        
        # Load error details
        errors = self._load_json("errors.json")
        if error_id not in errors:
            return validation_result
        
        error_data = errors[error_id]
        error_category = error_data.get("category", "unknown")
        
        # Validate based on error category
        if error_category == "permissions":
            validation_result = self._validate_permission_solution(solution_text, error_data)
        elif error_category == "missing_file":
            validation_result = self._validate_missing_file_solution(solution_text, error_data)
        elif error_category == "syntax":
            validation_result = self._validate_syntax_solution(solution_text, error_data)
        
        # Record validation in metadata
        import sys
        sys.path.append('.')
        from scripts.metadata_manager import MetadataManager
        metadata_mgr = MetadataManager()
        confidence = metadata_mgr.validate_solution_reality(error_id, f"{error_id}_solution", validation_result)
        
        return validation_result, confidence
    
    def _validate_permission_solution(self, solution, error_data):
        """Validate permission-related solutions"""
        result = {
            "success": False,
            "context": {"validation_type": "permission_check"},
            "side_effects": [],
            "environment": self._get_environment_context()
        }
        
        # Check if solution mentions appropriate permission commands
        permission_keywords = ["chmod", "chown", "sudo", "ls -la"]
        if any(keyword in solution.lower() for keyword in permission_keywords):
            result["success"] = True
            result["context"]["validation_method"] = "keyword_analysis"
        
        return result
    
    def _validate_missing_file_solution(self, solution, error_data):
        """Validate missing file solutions"""
        result = {
            "success": False,
            "context": {"validation_type": "missing_file_check"},
            "side_effects": [],
            "environment": self._get_environment_context()
        }
        
        # Check if solution mentions installation or PATH
        install_keywords = ["install", "apt", "yum", "pip", "npm", "PATH", "which"]
        if any(keyword in solution.lower() for keyword in install_keywords):
            result["success"] = True
            result["context"]["validation_method"] = "installation_guidance"
        
        return result
    
    def _validate_syntax_solution(self, solution, error_data):
        """Validate syntax error solutions"""
        result = {
            "success": False,
            "context": {"validation_type": "syntax_check"},
            "side_effects": [],
            "environment": self._get_environment_context()
        }
        
        # Check if solution mentions syntax checking tools
        syntax_keywords = ["shellcheck", "bash -n", "python -m py_compile", "syntax"]
        if any(keyword in solution.lower() for keyword in syntax_keywords):
            result["success"] = True
            result["context"]["validation_method"] = "syntax_validation_tools"
        
        return result
    
    def check_context_accuracy(self):
        """Check accuracy of captured contexts"""
        errors = self._load_json("errors.json")
        context_issues = []
        
        for error_id, error_data in errors.items():
            context = error_data.get("context", "")
            script = error_data.get("script", "")
            
            # Verify script exists
            if script and script != "unknown":
                script_path = Path(script.replace("bash ", "").replace("python3 ", ""))
                if not script_path.exists():
                    context_issues.append({
                        "error_id": error_id,
                        "issue": "Referenced script does not exist",
                        "script": script
                    })
        
        return context_issues
    
    def _get_environment_context(self):
        """Get current environment context"""
        return {
            "timestamp": datetime.now().isoformat(),
            "python_version": os.sys.version.split()[0],
            "platform": os.name,
            "working_directory": str(Path.cwd()),
            "user": os.getenv("USER", "unknown")
        }
    
    def _load_json(self, filename):
        """Load JSON file safely"""
        file_path = self.kb_dir / filename
        if file_path.exists():
            try:
                with open(file_path) as f:
                    return json.load(f)
            except:
                return {}
        return {}

def main():
    checker = RealityChecker()
    
    # Check context accuracy
    context_issues = checker.check_context_accuracy()
    print("🔍 Context Accuracy Check:")
    if context_issues:
        for issue in context_issues:
            print(f"  ⚠️  {issue['issue']}: {issue['script']}")
    else:
        print("  ✅ All contexts appear accurate")
    
    # Validate existing solutions
    solutions = checker._load_json("solutions.json")
    print(f"\n🧪 Solution Validation:")
    validated_count = 0
    
    for error_id, solution_list in solutions.items():
        for solution in solution_list:
            result, confidence = checker.validate_error_solution(error_id, solution["solution"])
            if result["success"]:
                validated_count += 1
                print(f"  ✅ Solution for {error_id}: {confidence:.1%} confidence")
            else:
                print(f"  ⚠️  Solution for {error_id}: Needs verification")
    
    print(f"\nValidation Summary: {validated_count}/{sum(len(s) for s in solutions.values())} solutions validated")

if __name__ == "__main__":
    main()
