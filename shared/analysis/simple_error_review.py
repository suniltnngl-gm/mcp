#!/usr/bin/env python3
"""Simple error review without complex dependencies"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE_PATH = os.path.join(PROJECT_ROOT, "logs", "system.log")

def main():
    """Review errors in log files"""
    if not os.path.exists(LOG_FILE_PATH):
        print("📝 No system log found. Creating logs directory...")
        os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
        print("✅ Logs directory ready")
        return
    
    with open(LOG_FILE_PATH, 'r') as f:
        lines = f.readlines()
    
    error_lines = [line.strip() for line in lines if "ERROR" in line]
    warn_lines = [line.strip() for line in lines if "WARN" in line]
    
    print("🔍 Log Analysis Summary")
    print("=" * 30)
    print(f"Total lines: {len(lines)}")
    print(f"Errors: {len(error_lines)}")
    print(f"Warnings: {len(warn_lines)}")
    
    if error_lines:
        print("\n❌ Recent Errors:")
        for error in error_lines[-5:]:  # Last 5 errors
            print(f"  {error}")
    
    if warn_lines:
        print("\n⚠️  Recent Warnings:")
        for warn in warn_lines[-3:]:  # Last 3 warnings
            print(f"  {warn}")
    
    if not error_lines and not warn_lines:
        print("\n✅ No errors or warnings found!")

if __name__ == "__main__":
    main()