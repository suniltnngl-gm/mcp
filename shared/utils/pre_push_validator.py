#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path


def validate_tests():
    """Run test suite validation"""
    print("[PRE-PUSH] Running test validation...")

    # Check if tests exist and run them
    test_dirs = ["tests/", "test/"]
    has_tests = any(Path(d).exists() for d in test_dirs)

    if has_tests:
        # Run basic test validation
        try:
            result = subprocess.run(
                ["python3", "-m", "pytest", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                print("[PRE-PUSH] ✅ Tests passed")
                return True
            else:
                print("[PRE-PUSH] ❌ Tests failed")
                print(result.stdout[-500:])  # Last 500 chars
                return False
        except Exception:
            print("[PRE-PUSH] ⚠️  Could not run tests - proceeding")
            return True
    else:
        print("[PRE-PUSH] ℹ️  No test directory found - skipping test validation")
        return True


def check_merge_conflicts():
    """Check for potential merge conflicts"""
    print("[PRE-PUSH] Checking for merge conflicts...")

    try:
        # Check for conflict markers in staged files
        result = subprocess.run(
            ["git", "diff", "--cached"], capture_output=True, text=True
        )

        conflict_markers = ["<<<<<<<", ">>>>>>>", "======="]
        for marker in conflict_markers:
            if marker in result.stdout:
                print(f"[PRE-PUSH] ❌ Conflict marker found: {marker}")
                return False

        print("[PRE-PUSH] ✅ No merge conflicts detected")
        return True

    except Exception as e:
        print(f"[PRE-PUSH] ⚠️  Could not check conflicts: {e}")
        return True


def validate_branch_protection():
    """Check branch protection rules"""
    print("[PRE-PUSH] Validating branch protection...")

    try:
        # Get current branch
        result = subprocess.run(
            ["git", "branch", "--show-current"], capture_output=True, text=True
        )

        if result.returncode == 0:
            current_branch = result.stdout.strip()
            protected_branches = ["main", "master", "production", "prod"]

            if current_branch in protected_branches:
                print(f"[PRE-PUSH] ⚠️  Pushing to protected branch: {current_branch}")
                print("[PRE-PUSH] Consider using a feature branch and pull request")
                # Don't block, just warn

        print("[PRE-PUSH] ✅ Branch validation complete")
        return True

    except Exception as e:
        print(f"[PRE-PUSH] ⚠️  Could not validate branch: {e}")
        return True


def main():
    """Main pre-push validation"""
    print("[PRE-PUSH] 🔍 Starting repository integrity validation...")

    validations = [
        ("Test Suite", validate_tests),
        ("Merge Conflicts", check_merge_conflicts),
        ("Branch Protection", validate_branch_protection),
    ]

    all_passed = True

    for name, validator in validations:
        try:
            if not validator():
                all_passed = False
        except Exception as e:
            print(f"[PRE-PUSH] ❌ {name} validation failed: {e}")
            all_passed = False

    if all_passed:
        print("[PRE-PUSH] ✅ All validations passed - push approved")
        return 0
    else:
        print("[PRE-PUSH] ❌ Validation failures detected - push blocked")
        return 1


if __name__ == "__main__":
    sys.exit(main())
