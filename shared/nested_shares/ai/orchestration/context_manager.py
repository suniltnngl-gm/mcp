#!/usr/bin/env python3
"""Context Manager - Agent safety and context preservation system"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set

class AgentContextManager:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.safety_rules_file = self.base_path / "AGENT_SAFETY_RULES.md"
        self.context_log_file = self.base_path / "agent_context_log.json"
        self.working_systems_file = self.base_path / "working_systems_registry.json"
        self.load_context()
    
    def load_context(self):
        """Load agent context and safety state"""
        # Load context log
        if self.context_log_file.exists():
            with open(self.context_log_file, 'r') as f:
                self.context_log = json.load(f)
        else:
            self.context_log = {
                "safety_violations": [],
                "successful_operations": [],
                "context_reviews": [],
                "created": datetime.now().isoformat()
            }
        
        # Load working systems registry
        if self.working_systems_file.exists():
            with open(self.working_systems_file, 'r') as f:
                self.working_systems = json.load(f)
        else:
            self.working_systems = {
                "protected_paths": [
                    "/media/sunil-kr/workspace/user-projects/shared-tools/nested-shares",
                    "/media/sunil-kr/workspace/user-projects/current"
                ],
                "working_tools": [],
                "safe_operations": ["analyze", "create_new", "report", "plan"],
                "high_risk_operations": ["move", "delete", "modify", "restructure"]
            }
    
    def check_operation_safety(self, operation: str, target_path: str = None) -> Dict:
        """Check if operation is safe to perform"""
        safety_check = {
            "safe": False,
            "risk_level": "unknown",
            "warnings": [],
            "required_approvals": []
        }
        
        # Check operation type
        if operation in self.working_systems["safe_operations"]:
            safety_check["safe"] = True
            safety_check["risk_level"] = "low"
        elif operation in self.working_systems["high_risk_operations"]:
            safety_check["safe"] = False
            safety_check["risk_level"] = "high"
            safety_check["required_approvals"].append("explicit_user_confirmation")
        
        # Check target path if provided
        if target_path:
            for protected_path in self.working_systems["protected_paths"]:
                if target_path.startswith(protected_path):
                    safety_check["warnings"].append(f"Operation targets protected path: {protected_path}")
                    if operation in self.working_systems["high_risk_operations"]:
                        safety_check["required_approvals"].append("backup_creation")
        
        return safety_check
    
    def register_working_system(self, system_path: str, description: str):
        """Register a working system that should be protected"""
        working_tool = {
            "path": system_path,
            "description": description,
            "registered": datetime.now().isoformat(),
            "status": "working"
        }
        
        if "working_tools" not in self.working_systems:
            self.working_systems["working_tools"] = []
        
        self.working_systems["working_tools"].append(working_tool)
        self.save_context()
    
    def log_operation(self, operation: str, target: str, success: bool, notes: str = ""):
        """Log agent operation for context tracking"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "target": target,
            "success": success,
            "notes": notes
        }
        
        if success:
            self.context_log["successful_operations"].append(log_entry)
        else:
            self.context_log["safety_violations"].append(log_entry)
        
        self.save_context()
    
    def perform_context_review(self) -> Dict:
        """Perform periodic context review"""
        review = {
            "timestamp": datetime.now().isoformat(),
            "safety_violations_count": len(self.context_log["safety_violations"]),
            "recent_violations": self.context_log["safety_violations"][-5:],
            "limiting_factors": [],
            "recommendations": []
        }
        
        # Analyze recent violations
        recent_violations = self.context_log["safety_violations"][-10:]
        
        # Check for patterns
        violation_types = {}
        for violation in recent_violations:
            op_type = violation.get("operation", "unknown")
            violation_types[op_type] = violation_types.get(op_type, 0) + 1
        
        # Identify limiting factors
        if violation_types.get("move", 0) > 2:
            review["limiting_factors"].append("Agent attempting too many file moves")
            review["recommendations"].append("Restrict file movement operations")
        
        if violation_types.get("modify", 0) > 2:
            review["limiting_factors"].append("Agent modifying working code without approval")
            review["recommendations"].append("Require explicit approval for code modifications")
        
        if len(recent_violations) > 5:
            review["limiting_factors"].append("High frequency of safety violations")
            review["recommendations"].append("Implement stricter safety checks")
        
        # Store review
        self.context_log["context_reviews"].append(review)
        self.save_context()
        
        return review
    
    def get_safety_summary(self) -> Dict:
        """Get current safety status summary"""
        return {
            "protected_systems": len(self.working_systems.get("working_tools", [])),
            "recent_violations": len([v for v in self.context_log["safety_violations"] 
                                   if (datetime.now() - datetime.fromisoformat(v["timestamp"])).days < 7]),
            "last_review": self.context_log["context_reviews"][-1]["timestamp"] if self.context_log["context_reviews"] else "never",
            "high_risk_operations": self.working_systems["high_risk_operations"],
            "safe_operations": self.working_systems["safe_operations"]
        }
    
    def save_context(self):
        """Save context state"""
        with open(self.context_log_file, 'w') as f:
            json.dump(self.context_log, f, indent=2)
        
        with open(self.working_systems_file, 'w') as f:
            json.dump(self.working_systems, f, indent=2)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent context manager")
    parser.add_argument("command", choices=["check", "review", "status", "register"])
    parser.add_argument("--operation", help="Operation to check")
    parser.add_argument("--path", help="Target path")
    parser.add_argument("--description", help="Description for registration")
    
    args = parser.parse_args()
    manager = AgentContextManager()
    
    if args.command == "check":
        if not args.operation:
            print("Error: --operation required for check")
            return
        
        safety = manager.check_operation_safety(args.operation, args.path)
        
        print("🛡️  Safety Check Result")
        print("=" * 20)
        print(f"Operation: {args.operation}")
        if args.path:
            print(f"Target: {args.path}")
        
        safety_emoji = "✅" if safety["safe"] else "⚠️"
        print(f"Safe: {safety_emoji} {safety['safe']}")
        print(f"Risk Level: {safety['risk_level']}")
        
        if safety["warnings"]:
            print(f"\n⚠️  Warnings:")
            for warning in safety["warnings"]:
                print(f"  • {warning}")
        
        if safety["required_approvals"]:
            print(f"\n📋 Required Approvals:")
            for approval in safety["required_approvals"]:
                print(f"  • {approval}")
    
    elif args.command == "review":
        review = manager.perform_context_review()
        
        print("🔍 Context Review")
        print("=" * 15)
        print(f"Safety Violations: {review['safety_violations_count']}")
        
        if review["limiting_factors"]:
            print(f"\n⚠️  Limiting Factors:")
            for factor in review["limiting_factors"]:
                print(f"  • {factor}")
        
        if review["recommendations"]:
            print(f"\n💡 Recommendations:")
            for rec in review["recommendations"]:
                print(f"  • {rec}")
    
    elif args.command == "status":
        summary = manager.get_safety_summary()
        
        print("📊 Safety Status")
        print("=" * 14)
        print(f"Protected Systems: {summary['protected_systems']}")
        print(f"Recent Violations: {summary['recent_violations']}")
        print(f"Last Review: {summary['last_review']}")
        
        print(f"\n✅ Safe Operations:")
        for op in summary["safe_operations"]:
            print(f"  • {op}")
        
        print(f"\n⚠️  High-Risk Operations:")
        for op in summary["high_risk_operations"]:
            print(f"  • {op}")
    
    elif args.command == "register":
        if not args.path or not args.description:
            print("Error: --path and --description required for register")
            return
        
        manager.register_working_system(args.path, args.description)
        print(f"✅ Registered working system: {args.path}")

if __name__ == "__main__":
    main()
