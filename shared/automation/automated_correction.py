#!/usr/bin/env python3

import json
import subprocess
import os
from pathlib import Path
from datetime import datetime

class AutomatedCorrection:
    def __init__(self):
        self.kb_dir = Path(__file__).parent.parent / "knowledge_base"
        self.solutions = self._load_solutions()
        
    def _load_solutions(self):
        """Load solutions from knowledge base"""
        try:
            with open(self.kb_dir / "solutions.json") as f:
                return json.load(f)
        except:
            return {}
    
    def detect_and_fix(self, error_type, context, error_message=""):
        """Main correction workflow: detect issue and apply fix"""
        
        # Find matching solution
        solution = self._find_solution(error_type, context, error_message)
        if not solution:
            return {"fixed": False, "reason": "No solution found"}
        
        # Apply correction
        result = self._apply_correction(solution, context)
        
        # Validate fix
        if result["applied"]:
            validation = self._validate_fix(error_type, context)
            result["validated"] = validation
            
            # Update solution effectiveness
            self._update_effectiveness(solution["id"], validation)
        
        return result
    
    def _find_solution(self, error_type, context, error_message):
        """Find best matching solution from knowledge base"""
        
        for solution_id, solution in self.solutions.items():
            # Match by error type
            if solution.get("error_type") == error_type:
                # Check context relevance
                if self._context_matches(solution.get("context", ""), context):
                    return {"id": solution_id, **solution}
        
        return None
    
    def _context_matches(self, solution_context, current_context):
        """Check if solution context matches current situation"""
        if not solution_context:
            return True
        
        # Simple keyword matching
        solution_keywords = solution_context.lower().split()
        current_keywords = current_context.lower().split()
        
        return any(keyword in current_keywords for keyword in solution_keywords)
    
    def _apply_correction(self, solution, context):
        """Apply the correction solution"""
        
        fix_command = solution.get("fix_command", "")
        if not fix_command:
            return {"applied": False, "reason": "No fix command"}
        
        try:
            # Replace context variables in command
            fix_command = fix_command.replace("{context}", context)
            
            # Execute fix
            result = subprocess.run(
                fix_command, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            return {
                "applied": result.returncode == 0,
                "command": fix_command,
                "output": result.stdout,
                "error": result.stderr
            }
            
        except Exception as e:
            return {"applied": False, "reason": str(e)}
    
    def _validate_fix(self, error_type, context):
        """Validate that the fix resolved the issue"""
        
        # Run basic validation based on error type
        validation_commands = {
            "missing_file": f"test -f {context}",
            "permissions": f"test -r {context}",
            "missing_directory": f"test -d {context}",
            "command_not_found": f"command -v {context.split()[0]} >/dev/null"
        }
        
        cmd = validation_commands.get(error_type, "true")
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True)
            return result.returncode == 0
        except:
            return False
    
    def _update_effectiveness(self, solution_id, success):
        """Update solution effectiveness tracking"""
        
        if solution_id not in self.solutions:
            return
        
        solution = self.solutions[solution_id]
        
        # Initialize tracking if not exists
        if "effectiveness" not in solution:
            solution["effectiveness"] = {"successes": 0, "failures": 0}
        
        # Update counters
        if success:
            solution["effectiveness"]["successes"] += 1
        else:
            solution["effectiveness"]["failures"] += 1
        
        # Save updated solutions
        try:
            with open(self.kb_dir / "solutions.json", "w") as f:
                json.dump(self.solutions, f, indent=2)
        except:
            pass

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Automated correction system")
    parser.add_argument("--error-type", required=True, help="Type of error to fix")
    parser.add_argument("--context", required=True, help="Error context")
    parser.add_argument("--error-message", default="", help="Error message")
    
    args = parser.parse_args()
    
    corrector = AutomatedCorrection()
    result = corrector.detect_and_fix(args.error_type, args.context, args.error_message)
    
    if result.get("applied", False) and result.get("validated", False):
        print(f"✅ Issue automatically corrected: {args.error_type}")
        return 0
    else:
        print(f"❌ Could not auto-correct: {result.get('reason', 'Unknown')}")
        return 1

if __name__ == "__main__":
    exit(main())