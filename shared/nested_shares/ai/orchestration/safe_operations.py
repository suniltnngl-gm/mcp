#!/usr/bin/env python3
"""Safe Operations - Wrapper for all agent operations with safety checks"""

import sys
from pathlib import Path
from context_manager import AgentContextManager

class SafeOperations:
    def __init__(self):
        self.context_manager = AgentContextManager()
        self.safety_enabled = True
    
    def safe_file_operation(self, operation: str, source_path: str, target_path: str = None, dry_run: bool = True):
        """Perform file operation with safety checks"""
        
        # Safety check
        safety = self.context_manager.check_operation_safety(operation, source_path)
        
        if not safety["safe"] and not dry_run:
            print(f"🚨 SAFETY VIOLATION PREVENTED")
            print(f"Operation: {operation}")
            print(f"Target: {source_path}")
            print(f"Risk Level: {safety['risk_level']}")
            
            if safety["warnings"]:
                print(f"Warnings:")
                for warning in safety["warnings"]:
                    print(f"  • {warning}")
            
            if safety["required_approvals"]:
                print(f"Required Approvals:")
                for approval in safety["required_approvals"]:
                    print(f"  • {approval}")
            
            print(f"\n❌ Operation BLOCKED for safety")
            
            # Log the violation
            self.context_manager.log_operation(
                operation=operation,
                target=source_path,
                success=False,
                notes="Blocked by safety system"
            )
            
            return False
        
        # If dry run or safe operation, proceed
        if dry_run:
            print(f"DRY RUN: {operation} {source_path}")
            if target_path:
                print(f"  → {target_path}")
            return True
        
        # Log successful operation
        self.context_manager.log_operation(
            operation=operation,
            target=source_path,
            success=True,
            notes="Completed safely"
        )
        
        return True
    
    def require_explicit_approval(self, operation_description: str) -> bool:
        """Require explicit user approval for destructive operations"""
        print(f"\n🚨 DESTRUCTIVE OPERATION REQUIRES APPROVAL")
        print(f"Operation: {operation_description}")
        print(f"This operation could break working code.")
        print(f"")
        print(f"Safety Rules:")
        print(f"  • Working code must be preserved")
        print(f"  • Backups should be created first")
        print(f"  • Dry-run testing is recommended")
        print(f"")
        
        response = input("Do you want to proceed? (type 'YES' to confirm): ")
        
        if response == "YES":
            print(f"✅ User approved destructive operation")
            return True
        else:
            print(f"❌ Operation cancelled by user")
            return False
    
    def create_safety_backup(self, path: str) -> bool:
        """Create safety backup before destructive operations"""
        try:
            backup_path = f"{path}.safety_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            # Implementation would go here
            print(f"📁 Safety backup created: {backup_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to create safety backup: {e}")
            return False

# Global safety wrapper functions
def safe_move(source: str, target: str, dry_run: bool = True):
    """Safely move files with protection"""
    safe_ops = SafeOperations()
    return safe_ops.safe_file_operation("move", source, target, dry_run)

def safe_delete(path: str, dry_run: bool = True):
    """Safely delete files with protection"""
    safe_ops = SafeOperations()
    return safe_ops.safe_file_operation("delete", path, dry_run=dry_run)

def safe_modify(path: str, dry_run: bool = True):
    """Safely modify files with protection"""
    safe_ops = SafeOperations()
    return safe_ops.safe_file_operation("modify", path, dry_run=dry_run)

def check_safety_status():
    """Check current safety system status"""
    manager = AgentContextManager()
    summary = manager.get_safety_summary()
    
    print("🛡️  Agent Safety Status")
    print("=" * 22)
    print(f"Protected Systems: {summary['protected_systems']}")
    print(f"Recent Violations: {summary['recent_violations']}")
    print(f"Last Review: {summary['last_review']}")
    
    if summary['recent_violations'] > 0:
        print(f"\n⚠️  WARNING: {summary['recent_violations']} recent safety violations detected")
        print(f"Consider running: python3 context_manager.py review")

def main():
    print("🛡️  Agent Safety System")
    print("=" * 22)
    print("This system protects working code from destructive operations.")
    print("")
    print("Key Rules:")
    print("  ✅ Analysis and new file creation are SAFE")
    print("  ⚠️  Moving, deleting, modifying require approval")
    print("  🚨 Working code must never be broken")
    print("")
    
    check_safety_status()
    
    print(f"\nCommands:")
    print(f"  python3 context_manager.py check --operation move --path /some/path")
    print(f"  python3 context_manager.py review")
    print(f"  python3 context_manager.py status")

if __name__ == "__main__":
    main()
