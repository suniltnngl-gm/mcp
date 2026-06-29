#!/usr/bin/env python3
"""
Repository Knowledge Base Generator

This script gathers information about all Git repositories in the workspace
and stores it in a TinyDB database.
"""

import os
import json
import subprocess
import datetime
from pathlib import Path
from tinydb import TinyDB, Query
from pydantic import ValidationError

from devflow_shared_tools.consolidated_ignore_patterns import is_ignored
from devflow_shared_tools.knowledge_base_schema import (
    GlobalInfo,
    RepositoryInfo,
    DuplicateInfo,
)

# --- Configuration ---
WORKSPACE_ROOT = Path("/media/sunil-kr/storage/workspace/")
OUTPUT_DIR = WORKSPACE_ROOT / "data"
DB_FILE = OUTPUT_DIR / "repo_knowledgebase.json"

# Ensure the output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)

# --- Helper Functions ---

def get_language_from_extension(ext):
    """Determines programming language based on file extension."""
    if ext == ".py":
        return "Python"
    if ext in (".js", ".jsx"):
        return "JavaScript"
    if ext in (".ts", ".tsx"):
        return "TypeScript"
    if ext == ".java":
        return "Java"
    if ext == ".go":
        return "Go"
    if ext == ".md":
        return "Markdown"
    if ext == ".sh":
        return "Shell"
    if ext == ".c":
        return "C"
    if ext == ".cpp":
        return "C++"
    if ext == ".cs":
        return "C#"
    if ext == ".html":
        return "HTML"
    if ext == ".css":
        return "CSS"
    if ext == ".php":
        return "PHP"
    if ext == ".rb":
        return "Ruby"
    if ext == ".rs":
        return "Rust"
    if ext == ".swift":
        return "Swift"
    if ext == ".kt":
        return "Kotlin"
    if ext == ".vue":
        return "Vue"
    if ext == ".json":
        return "JSON"
    if ext in (".yaml", ".yml"):
        return "YAML"
    if ext == ".xml":
        return "XML"
    return "Other"


# --- Main Script Logic ---

# Capture Git Version once
try:
    git_version = subprocess.check_output(
        "git version", shell=True, text=True, stderr=subprocess.PIPE
    ).strip()
except Exception as e:
    git_version = f"Error getting git version: {str(e)}"

# Initialize TinyDB
db = TinyDB(DB_FILE)
db.truncate()  # Clear existing data before populating

# Store global info (git_cli_version) as a separate document
global_info = GlobalInfo(type="global_info", git_cli_version=git_version)
db.insert(global_info.dict())

file_hashes = {}  # To store blob_hash -> [full_file_path1, full_file_path2, ...]

# Find all .git directories
find_command = f"find {WORKSPACE_ROOT} -type d -name '.git' -print0"
try:
    git_dirs_output = subprocess.check_output(
        find_command, shell=True, text=True, stderr=subprocess.PIPE
    )
    git_dirs = git_dirs_output.strip().split("\0")
except subprocess.CalledProcessError as e:
    print(f"Error finding git repositories: {e.stderr}")
    exit(1)

for git_dir in git_dirs:
    if not git_dir:
        continue

    repo_path = Path(git_dir).parent
    relative_repo_path = repo_path.relative_to(WORKSPACE_ROOT)

    repo_info_dict = {
        "type": "repository_info",  # Document type for TinyDB
        "path": str(repo_path),
        "relative_path": str(relative_repo_path),
        "name": repo_path.name,
    }

    original_cwd = os.getcwd()
    try:
        os.chdir(repo_path)

        # Git-based info
        try:
            repo_info_dict["current_branch"] = subprocess.check_output(
                "git rev-parse --abbrev-ref HEAD",
                shell=True,
                text=True,
                stderr=subprocess.PIPE,
            ).strip()
        except subprocess.CalledProcessError as e:
            repo_info_dict["current_branch"] = "N/A"
            repo_info_dict["current_branch_error"] = (
                e.stderr.strip()
                if e.stderr
                else "Unknown error during current branch retrieval."
            )

        try:
            repo_info_dict["local_branches"] = [
                b.strip()
                for b in subprocess.check_output(
                    "git branch", shell=True, text=True, stderr=subprocess.PIPE
                )
                .strip()
                .split("\n")
                if b.strip()
            ]
        except subprocess.CalledProcessError as e:
            repo_info_dict["local_branches"] = []
            repo_info_dict["local_branches_error"] = (
                e.stderr.strip()
                if e.stderr
                else "Unknown error during local branches retrieval."
            )

        try:
            repo_info_dict["remote_branches"] = [
                b.strip()
                for b in subprocess.check_output(
                    "git branch -r", shell=True, text=True, stderr=subprocess.PIPE
                )
                .strip()
                .split("\n")
                if b.strip()
            ]
        except subprocess.CalledProcessError as e:
            repo_info_dict["remote_branches"] = []
            repo_info_dict["remote_branches_error"] = (
                e.stderr.strip()
                if e.stderr
                else "Unknown error during remote branches retrieval."
            )

        try:
            repo_info_dict["remote_urls"] = [
                u.strip()
                for u in subprocess.check_output(
                    "git remote -v", shell=True, text=True, stderr=subprocess.PIPE
                )
                .strip()
                .split("\n")
                if u.strip()
            ]
        except subprocess.CalledProcessError as e:
            repo_info_dict["remote_urls"] = []
            repo_info_dict["remote_urls_error"] = (
                e.stderr.strip()
                if e.stderr
                else "Unknown error during remote URLs retrieval."
            )

        try:
            repo_info_dict["last_5_commits"] = [
                c.strip()
                for c in subprocess.check_output(
                    "git log -5 --pretty=format:%h - %an, %ar : %s",
                    shell=True,
                    text=True,
                    stderr=subprocess.PIPE,
                )
                .strip()
                .split("\n")
                if c.strip()
            ]
        except subprocess.CalledProcessError as e:
            repo_info_dict["last_5_commits"] = ["N/A"]
            repo_info_dict["last_commits_error"] = (
                e.stderr.strip()
                if e.stderr
                else "Unknown error during last commits retrieval."
            )

        try:
            status_output = subprocess.check_output(
                "git status --porcelain=v1", shell=True, text=True, stderr=subprocess.PIPE
            ).strip()
            repo_info_dict["is_clean"] = not bool(status_output)
            repo_info_dict["status_details"] = [
                s.strip() for s in status_output.split("\n") if s.strip()
            ]
        except subprocess.CalledProcessError as e:
            repo_info_dict["is_clean"] = False
            repo_info_dict["status_details"] = []
            repo_info_dict["status_error"] = (
                e.stderr.strip()
                if e.stderr
                else "Unknown error during status retrieval."
            )

        try:
            upstream_branch = subprocess.check_output(
                "git rev-parse --abbrev-ref @{upstream}",
                shell=True,
                text=True,
                stderr=subprocess.PIPE,
            ).strip()
            if upstream_branch:
                ahead_behind_output = subprocess.check_output(
                    f"git rev-list --left-right --count {upstream_branch}...HEAD",
                    shell=True,
                    text=True,
                    stderr=subprocess.PIPE,
                ).strip()
                if ahead_behind_output:
                    ahead_behind_counts = ahead_behind_output.split("\t")
                    repo_info_dict["behind_by"] = int(ahead_behind_counts[0])
                    repo_info_dict["ahead_by"] = int(ahead_behind_counts[1])
                else:
                    repo_info_dict["behind_by"] = 0
                    repo_info_dict["ahead_by"] = 0
            else:
                repo_info_dict["behind_by"] = 0
                repo_info_dict["ahead_by"] = 0
                repo_info_dict["remote_tracking_error"] = "No upstream branch configured."
        except subprocess.CalledProcessError as e:
            repo_info_dict["behind_by"] = 0
            repo_info_dict["ahead_by"] = 0
            repo_info_dict["remote_tracking_error"] = (
                e.stderr.strip()
                if e.stderr
                else "Could not determine upstream branch or no remote configured."
            )

        try:
            repo_info_dict["last_commit_date"] = subprocess.check_output(
                "git log -1 --format=%cd", shell=True, text=True, stderr=subprocess.PIPE
            ).strip()
            repo_info_dict["last_commit_author_email"] = subprocess.check_output(
                "git log -1 --format=%ae", shell=True, text=True, stderr=subprocess.PIPE
            ).strip()
            repo_info_dict["last_commit_subject"] = subprocess.check_output(
                "git log -1 --format=%s", shell=True, text=True, stderr=subprocess.PIPE
            ).strip()
        except subprocess.CalledProcessError as e:
            repo_info_dict["last_commit_date"] = "N/A"
            repo_info_dict["last_commit_author_email"] = "N/A"
            repo_info_dict["last_commit_subject"] = "N/A"
            repo_info_dict["last_commit_details_error"] = (
                e.stderr.strip()
                if e.stderr
                else "Error getting last commit details."
            )

        try:
            repo_info_dict["total_commits"] = int(
                subprocess.check_output(
                    "git rev-list --count HEAD",
                    shell=True,
                    text=True,
                    stderr=subprocess.PIPE,
                ).strip()
            )
        except subprocess.CalledProcessError as e:
            repo_info_dict["total_commits"] = 0
            repo_info_dict["total_commits_error"] = (
                e.stderr.strip()
                if e.stderr
                else "Error getting total commits."
            )

        try:
            repo_info_dict["configured_user_name"] = subprocess.check_output(
                "git config user.name", shell=True, text=True, stderr=subprocess.PIPE
            ).strip()
        except subprocess.CalledProcessError:
            repo_info_dict["configured_user_name"] = "Not configured"
        try:
            repo_info_dict["configured_user_email"] = subprocess.check_output(
                "git config user.email", shell=True, text=True, stderr=subprocess.PIPE
            ).strip()
        except subprocess.CalledProcessError:
            repo_info_dict["configured_user_email"] = "Not configured"

        try:
            submodule_output = subprocess.check_output(
                "git submodule status", shell=True, text=True, stderr=subprocess.PIPE
            ).strip()
            repo_info_dict["submodules"] = [
                s.strip() for s in submodule_output.split("\n") if s.strip()
            ]
        except subprocess.CalledProcessError:
            repo_info_dict["submodules"] = []

        try:
            tag_output = subprocess.check_output(
                "git tag", shell=True, text=True, stderr=subprocess.PIPE
            ).strip()
            repo_info_dict["tags"] = [
                t.strip() for t in tag_output.split("\n") if t.strip()
            ]
        except subprocess.CalledProcessError:
            repo_info_dict["tags"] = []

        try:
            stash_output = subprocess.check_output(
                "git stash list", shell=True, text=True, stderr=subprocess.PIPE
            ).strip()
            repo_info_dict["stash_list"] = [
                s.strip() for s in stash_output.split("\n") if s.strip()
            ]
        except subprocess.CalledProcessError:
            repo_info_dict["stash_list"] = []

        try:
            ignored_output = subprocess.check_output(
                "git status --ignored --porcelain=v1",
                shell=True,
                text=True,
                stderr=subprocess.PIPE,
            ).strip()
            repo_info_dict["ignored_files"] = [
                line[3:].strip() for line in ignored_output.split("\n") if line.startswith('!!')
            ]
        except subprocess.CalledProcessError:
            repo_info_dict["ignored_files"] = []

        # Capture file hashes for duplicate detection
        try:
            ls_files_output = subprocess.check_output(
                "git ls-files -s", shell=True, text=True, stderr=subprocess.PIPE
            ).strip()
            for line in ls_files_output.split("\n"):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        blob_hash = parts[1]
                        file_path_in_repo = "/".join(parts[3:])
                        full_file_path = os.path.join(repo_path, file_path_in_repo)
                        if blob_hash not in file_hashes:
                            file_hashes[blob_hash] = []
                        file_hashes[blob_hash].append(full_file_path)
        except subprocess.CalledProcessError as e:
            repo_info_dict["ls_files_error"] = (
                e.stderr.strip()
                if e.stderr
                else "Error listing files for duplicate detection."
            )

        # Non-Git based info
        total_files = 0
        total_size_bytes = 0
        languages_detected = {}
        frameworks_detected = set()
        dependency_files = []
        documentation_files = []
        config_files = []
        license_file = "N/A"
        build_test_commands = []

        for root, dirs, files in os.walk(repo_path):
            # Remove .git from dirs to avoid walking into it
            if ".git" in dirs:
                dirs.remove(".git")

            dirs_to_remove = []
            for d in dirs:
                if is_ignored(Path(root) / d):
                    dirs_to_remove.append(d)
            for d in dirs_to_remove:
                dirs.remove(d)

            for file in files:
                full_file_path = Path(root) / file

                if is_ignored(full_file_path):
                    continue

                total_files += 1
                try:
                    total_size_bytes += full_file_path.stat().st_size
                except OSError:
                    pass

                ext = full_file_path.suffix.lower()
                lang = get_language_from_extension(ext)
                languages_detected[lang] = languages_detected.get(lang, 0) + 1

                if file in (
                    "package.json",
                    "requirements.txt",
                    "pyproject.toml",
                    "pom.xml",
                    "build.gradle",
                    "Cargo.toml",
                ):
                    dependency_files.append(str(full_file_path.relative_to(repo_path)))

                if file.lower().startswith("readme") and ext == ".md":
                    documentation_files.append(str(full_file_path.relative_to(repo_path)))
                elif "docs" in root.lower() and ext in [".md", ".rst", ".txt"]:
                    documentation_files.append(str(full_file_path.relative_to(repo_path)))

                if file.upper() == "LICENSE":
                    license_file = str(full_file_path.relative_to(repo_path))

                if file.endswith((".json", ".yaml", ".yml", ".xml", ".env", ".ini", ".config")):
                    config_files.append(str(full_file_path.relative_to(repo_path)))

                if file == "package.json":
                    try:
                        with open(full_file_path, 'r') as f:
                            package_json = json.load(f)
                            if "dependencies" in package_json:
                                if "react" in package_json["dependencies"]:
                                    frameworks_detected.add("React")
                                if "express" in package_json["dependencies"]:
                                    frameworks_detected.add("Express.js")
                            if "devDependencies" in package_json:
                                if "jest" in package_json["devDependencies"]:
                                    frameworks_detected.add("Jest")
                    except Exception:
                        pass
                elif file == "requirements.txt":
                    try:
                        with open(full_file_path, 'r') as f:
                            content = f.read().lower()
                            if "django" in content:
                                frameworks_detected.add("Django")
                            if "flask" in content:
                                frameworks_detected.add("Flask")
                            if "fastapi" in content:
                                frameworks_detected.add("FastAPI")
                    except Exception:
                        pass

        repo_info_dict["total_files"] = total_files
        repo_info_dict["total_size_bytes"] = total_size_bytes
        repo_info_dict["languages_detected"] = languages_detected
        repo_info_dict["frameworks_detected"] = list(frameworks_detected)
        repo_info_dict["dependency_files"] = dependency_files
        repo_info_dict["documentation_files"] = documentation_files
        repo_info_dict["license_file"] = license_file
        repo_info_dict["config_files"] = config_files

        try:
            repo_info_dict["last_modified_timestamp"] = datetime.datetime.fromtimestamp(
                repo_path.stat().st_mtime
            ).isoformat()
        except OSError:
            repo_info_dict["last_modified_timestamp"] = "N/A"

        build_test_commands = []
        if (repo_path / "Makefile").exists():
            build_test_commands.append("make")
        if (repo_path / "build.sh").exists():
            build_test_commands.append("./build.sh")
        if (repo_path / "package.json").exists():
            try:
                with open(repo_path / "package.json", 'r') as f:
                    package_json = json.load(f)
                    if "scripts" in package_json:
                        for script_name in package_json["scripts"]:
                            build_test_commands.append(f"npm run {script_name}")
            except Exception:
                pass
        repo_info_dict["build_test_commands"] = build_test_commands

    except subprocess.CalledProcessError as e:
        repo_info_dict["error"] = f"Error processing repository: {e.stderr.strip() if e.stderr else 'Unknown error'}"
    except Exception as e:
        repo_info_dict["error"] = f"An unexpected error occurred: {str(e)}"
    finally:
        os.chdir(original_cwd)

    # Validate and insert repo_info into TinyDB
    try:
        repo_info = RepositoryInfo(**repo_info_dict)
        db.insert(repo_info.dict())
    except ValidationError as e:
        print(f"Error validating repository info for {repo_path}: {e}")

# Identify duplicates based on file hashes
duplicate_files_by_hash = {
    blob_hash: paths for blob_hash, paths in file_hashes.items() if len(paths) > 1
}
# Store duplicate info as a separate document
try:
    duplicate_info = DuplicateInfo(
        type="duplicate_info", duplicate_files_by_hash=duplicate_files_by_hash
    )
    db.insert(duplicate_info.dict())
except ValidationError as e:
    print(f"Error validating duplicate info: {e}")

print(f"Repository knowledge base generated at {DB_FILE}")
