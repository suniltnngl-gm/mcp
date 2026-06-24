#!/usr/bin/env python3
"""Git Diff Helper for Incremental Code Reviews

This module provides utilities to detect changed files using git diff,
enabling efficient incremental reviews for pull requests and commits.
"""

import subprocess
from pathlib import Path
from typing import List, Optional, Set, Tuple


class GitDiffHelper:
    """Helper class for git diff operations"""

    def __init__(self, repo_root: Path):
        """Initialize GitDiffHelper
        
        Args:
            repo_root: Root directory of the git repository
        """
        self.repo_root = repo_root
        self._is_git_repo = self._check_git_repo()

    def _check_git_repo(self) -> bool:
        """Check if the directory is a git repository"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def is_git_repo(self) -> bool:
        """Check if current directory is a git repository"""
        return self._is_git_repo

    def get_changed_files(
        self,
        base: Optional[str] = None,
        include_untracked: bool = False,
        include_staged: bool = True,
        file_patterns: Optional[List[str]] = None,
    ) -> Tuple[bool, List[Path], str]:
        """Get list of changed files using git diff
        
        Args:
            base: Base branch/commit to compare against (e.g., 'main', 'HEAD~1')
                  If None, compares working directory with HEAD
            include_untracked: Include untracked files
            include_staged: Include staged files
            file_patterns: Optional list of file patterns to filter (e.g., ['*.py', '*.js'])
            
        Returns:
            Tuple of (success, list of changed file paths, error message)
        """
        if not self._is_git_repo:
            return False, [], "Not a git repository"

        changed_files: Set[Path] = set()
        error_msg = ""

        try:
            # Get modified and staged files
            if include_staged:
                # Staged files (in index)
                result = subprocess.run(
                    ["git", "diff", "--name-only", "--cached"],
                    cwd=self.repo_root,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                for line in result.stdout.strip().split("\n"):
                    if line:
                        changed_files.add(self.repo_root / line)

            # Get working directory changes
            if base:
                # Compare against a specific base (branch/commit)
                result = subprocess.run(
                    ["git", "diff", "--name-only", base],
                    cwd=self.repo_root,
                    capture_output=True,
                    text=True,
                    check=True,
                )
            else:
                # Compare working directory with HEAD
                result = subprocess.run(
                    ["git", "diff", "--name-only", "HEAD"],
                    cwd=self.repo_root,
                    capture_output=True,
                    text=True,
                    check=True,
                )

            for line in result.stdout.strip().split("\n"):
                if line:
                    changed_files.add(self.repo_root / line)

            # Get untracked files if requested
            if include_untracked:
                result = subprocess.run(
                    ["git", "ls-files", "--others", "--exclude-standard"],
                    cwd=self.repo_root,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                for line in result.stdout.strip().split("\n"):
                    if line:
                        changed_files.add(self.repo_root / line)

        except subprocess.CalledProcessError as e:
            error_msg = f"Git command failed: {e.stderr}"
            return False, [], error_msg
        except Exception as e:
            error_msg = f"Error getting changed files: {str(e)}"
            return False, [], error_msg

        # Filter by file patterns if provided
        if file_patterns:
            filtered_files = []
            for file_path in changed_files:
                if any(file_path.match(pattern) for pattern in file_patterns):
                    filtered_files.append(file_path)
            changed_files = set(filtered_files)

        # Filter out non-existent files (deleted files)
        existing_files = [f for f in changed_files if f.exists() and f.is_file()]

        return True, existing_files, ""

    def get_current_branch(self) -> Tuple[bool, str, str]:
        """Get the current git branch name
        
        Returns:
            Tuple of (success, branch_name, error_message)
        """
        if not self._is_git_repo:
            return False, "", "Not a git repository"

        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
            branch_name = result.stdout.strip()
            return True, branch_name, ""
        except subprocess.CalledProcessError as e:
            return False, "", f"Failed to get branch name: {e.stderr}"

    def get_default_branch(self) -> Tuple[bool, str, str]:
        """Get the default branch name (usually 'main' or 'master')
        
        Returns:
            Tuple of (success, branch_name, error_message)
        """
        if not self._is_git_repo:
            return False, "", "Not a git repository"

        try:
            # Try to get the default branch from remote
            result = subprocess.run(
                ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )
            
            if result.returncode == 0:
                # Extract branch name from refs/remotes/origin/HEAD -> refs/remotes/origin/main
                branch_ref = result.stdout.strip()
                branch_name = branch_ref.split("/")[-1]
                return True, branch_name, ""
            
            # Fallback: check if 'main' or 'master' exists
            for branch in ["main", "master"]:
                result = subprocess.run(
                    ["git", "rev-parse", "--verify", branch],
                    cwd=self.repo_root,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0:
                    return True, branch, ""
            
            return False, "", "Could not determine default branch"
            
        except Exception as e:
            return False, "", f"Error getting default branch: {str(e)}"

    def get_file_diff(self, file_path: Path, base: Optional[str] = None) -> Tuple[bool, str, str]:
        """Get the diff for a specific file
        
        Args:
            file_path: Path to the file
            base: Base branch/commit to compare against
            
        Returns:
            Tuple of (success, diff_content, error_message)
        """
        if not self._is_git_repo:
            return False, "", "Not a git repository"

        try:
            relative_path = file_path.relative_to(self.repo_root)
            
            if base:
                cmd = ["git", "diff", base, "--", str(relative_path)]
            else:
                cmd = ["git", "diff", "HEAD", "--", str(relative_path)]
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
            
            return True, result.stdout, ""
            
        except subprocess.CalledProcessError as e:
            return False, "", f"Failed to get diff: {e.stderr}"
        except Exception as e:
            return False, "", f"Error getting file diff: {str(e)}"


def get_changed_files_for_review(
    repo_root: Path,
    base: Optional[str] = None,
    file_patterns: Optional[List[str]] = None,
    include_untracked: bool = False,
) -> Tuple[bool, List[Path], str]:
    """Convenience function to get changed files for review
    
    Args:
        repo_root: Root directory of the git repository
        base: Base branch/commit to compare against
        file_patterns: File patterns to include (e.g., ['*.py', '*.js'])
        include_untracked: Include untracked files
        
    Returns:
        Tuple of (success, list of changed files, error_message)
    """
    helper = GitDiffHelper(repo_root)
    
    if not helper.is_git_repo():
        return False, [], "Not a git repository"
    
    return helper.get_changed_files(
        base=base,
        include_untracked=include_untracked,
        file_patterns=file_patterns,
    )


if __name__ == "__main__":
    # Test the git diff helper
    import sys

    repo_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    helper = GitDiffHelper(repo_root)

    if not helper.is_git_repo():
        print("❌ Not a git repository")
        sys.exit(1)

    print("✓ Git repository detected")

    # Get current branch
    success, branch, error = helper.get_current_branch()
    if success:
        print(f"Current branch: {branch}")

    # Get default branch
    success, default_branch, error = helper.get_default_branch()
    if success:
        print(f"Default branch: {default_branch}")

    # Get changed files
    success, changed_files, error = helper.get_changed_files(
        base=default_branch if success else None,
        file_patterns=["*.py", "*.js", "*.md"],
    )

    if success:
        print(f"\nChanged files ({len(changed_files)}):")
        for file in changed_files:
            print(f"  - {file.relative_to(repo_root)}")
    else:
        print(f"❌ Error: {error}")