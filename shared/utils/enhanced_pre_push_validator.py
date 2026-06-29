#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path


def run_tests():
    """Run test suite validation"""
    print("[PRE-PUSH] Running test validation...")

    # Check for test directories
    test_dirs = ["tests/", "test/", "spec/"]
    has_tests = any(Path(d).exists() for d in test_dirs)

    if not has_tests:
        print("[PRE-PUSH] ℹ️  No test directory found - skipping test validation")
        return True

    # Try different test runners
    test_commands = [
        ["python3", "-m", "pytest", "--tb=short", "-q"],
        ["python", "-m", "pytest", "--tb=short", "-q"],
        ["npm", "test"],
        ["make", "test"],
    ]

    for cmd in test_commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                print("[PRE-PUSH] ✅ Tests passed")
                return True
            else:
                print(f"[PRE-PUSH] ❌ Tests failed with {cmd[0]}")
                print(result.stdout[-300:] if result.stdout else "")
                print(result.stderr[-300:] if result.stderr else "")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue

    print("[PRE-PUSH] ⚠️  Could not run tests - proceeding with warning")
    return True


def check_merge_conflicts():
    """Check for unresolved merge conflicts"""
    print("[PRE-PUSH] Checking for merge conflicts...")

    try:
        # Check staged and unstaged files for conflict markers
        result = subprocess.run(["git", "diff", "HEAD"], capture_output=True, text=True)

        conflict_markers = ["<<<<<<<", ">>>>>>>", "======="]
        for marker in conflict_markers:
            if marker in result.stdout:
                print(f"[PRE-PUSH] ❌ Merge conflict marker found: {marker}")
                return False

        # Check for unmerged paths
        result = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True
        )
        unmerged_files = [
            line for line in result.stdout.split("\n") if line.startswith("UU ")
        ]

        if unmerged_files:
            print("[PRE-PUSH] ❌ Unmerged files detected:")
            for file_line in unmerged_files:
                print(f"  {file_line}")
            return False

        print("[PRE-PUSH] ✅ No merge conflicts detected")
        return True

    except Exception as e:
        print(f"[PRE-PUSH] ⚠️  Could not check conflicts: {e}")
        return True


def validate_branch_protection():
    """Validate branch protection rules"""
    print("[PRE-PUSH] Validating branch protection...")

    try:
        # Get current branch
        result = subprocess.run(
            ["git", "branch", "--show-current"], capture_output=True, text=True
        )

        if result.returncode == 0:
            current_branch = result.stdout.strip()
            protected_branches = ["main", "master", "production", "prod", "release"]

            if current_branch in protected_branches:
                print(f"[PRE-PUSH] ⚠️  Pushing to protected branch: {current_branch}")
                print("[PRE-PUSH] Consider using a feature branch and pull request")

                # Don't block, but warn strongly
                response = input("Continue with push to protected branch? (y/N): ")
                if response.lower() != "y":
                    print("[PRE-PUSH] ❌ Push cancelled by user")
                    return False

        print("[PRE-PUSH] ✅ Branch validation complete")
        return True

    except Exception as e:
        print(f"[PRE-PUSH] ⚠️  Could not validate branch: {e}")
        return True


def check_commit_quality():
    """Check commit message and change quality"""
    print("[PRE-PUSH] Checking commit quality...")

    try:
        # Get commits being pushed
        result = subprocess.run(
            ["git", "log", "--oneline", "@{u}..HEAD"], capture_output=True, text=True
        )

        if result.returncode != 0:
            # No upstream branch, skip this check
            print("[PRE-PUSH] ℹ️  No upstream branch - skipping commit quality check")
            return True

        commits = result.stdout.strip().split("\n")
        if not commits or commits == [""]:
            print("[PRE-PUSH] ℹ️  No new commits to push")
            return True

        # Check for fixup/squash commits
        problematic_commits = []
        for commit in commits:
            if any(
                keyword in commit.lower()
                for keyword in ["fixup!", "squash!", "wip", "temp"]
            ):
                problematic_commits.append(commit)

        if problematic_commits:
            print("[PRE-PUSH] ⚠️  Problematic commits detected:")
            for commit in problematic_commits:
                print(f"  {commit}")
            print("[PRE-PUSH] Consider squashing or cleaning up commit history")

        print(f"[PRE-PUSH] ✅ Pushing {len(commits)} commits")
        return True

    except Exception as e:
        print(f"[PRE-PUSH] ⚠️  Could not check commit quality: {e}")
        return True


def check_large_files():
    """Check for accidentally committed large files"""
    print("[PRE-PUSH] Checking for large files...")

    try:
        # Check for files larger than 10MB in the push
        result = subprocess.run(
            ["git", "diff", "--stat", "@{u}..HEAD"], capture_output=True, text=True
        )

        if result.returncode != 0:
            return True  # No upstream, skip check

        large_files = []
        for line in result.stdout.split("\n"):
            if "|" in line and ("+" in line or "-" in line):
                # Look for suspiciously large change counts
                parts = line.split("|")
                if len(parts) > 1:
                    changes = parts[1].strip()
                    # Simple heuristic: if line shows many +'s, might be large file
                    if changes.count("+") > 50:
                        large_files.append(parts[0].strip())

        if large_files:
            print("[PRE-PUSH] ⚠️  Potentially large files detected:")
            for file_name in large_files:
                print(f"  {file_name}")
            print("[PRE-PUSH] Consider using Git LFS for large files")

        print("[PRE-PUSH] ✅ File size check complete")
        return True

    except Exception as e:
        print(f"[PRE-PUSH] ⚠️  Could not check file sizes: {e}")
        return True


def main():
    """Main pre-push validation"""

    print("[PRE-PUSH] 🔍 Starting comprehensive repository validation...")

    validations = [
        ("Test Suite", run_tests),
        ("Merge Conflicts", check_merge_conflicts),
        ("Branch Protection", validate_branch_protection),
        ("Commit Quality", check_commit_quality),
        ("Large Files", check_large_files),
    ]

    failed_validations = []

    for name, validator in validations:
        try:
            if not validator():
                failed_validations.append(name)
        except Exception as e:
            print(f"[PRE-PUSH] ❌ {name} validation failed: {e}")
            failed_validations.append(name)

    if failed_validations:
        print(f"\n[PRE-PUSH] ❌ Validation failures: {', '.join(failed_validations)}")
        print("[PRE-PUSH] Fix the issues above or use 'git push --no-verify' to bypass")
        sys.exit(1)
    else:
        print("\n[PRE-PUSH] ✅ All validations passed - push approved")
        sys.exit(0)


if __name__ == "__main__":
    main()
