#!/usr/bin/env python3

import os
import json
import datetime
import subprocess
from typing import Dict, Any


def run_shell_command(command: str) -> str:
    """Helper to run shell commands and return stdout."""
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def generate_inventory(project_root: str = ".") -> Dict[str, Any]:
    """
    Scans the project directory, respecting .gitignore, and generates an inventory
    of files and directories with metadata.
    """
    file_registry: Dict[str, Any] = {
        "timestamp": str(datetime.datetime.now()),
        "scanned_path": os.path.abspath(project_root),
        "files": [],
        "directories": [],
        "summary": {},
    }

    all_paths = []
    try:
        # Use git ls-files to get all tracked and untracked (but not ignored) files
        # This implicitly respects .gitignore
        tracked_files = run_shell_command(f"git -C {project_root} ls-files")
        untracked_files = run_shell_command(
            f"git -C {project_root} ls-files --others --exclude-standard"
        )
        all_paths = tracked_files.splitlines() + untracked_files.splitlines()
        all_paths = [
            os.path.join(project_root, p) for p in all_paths if p
        ]  # Make paths relative to root

    except subprocess.CalledProcessError:
        print(
            "Git not found or project is not a git repository. Falling back to os.walk."
        )
        # Fallback if not a git repository or git command fails
        for root, dirs, files in os.walk(project_root):
            for name in files:
                all_paths.append(os.path.join(root, name))
            for name in dirs:
                # Add directories that are not explicitly ignored by git ls-files if it were used
                # For os.walk fallback, we include all directories for now.
                pass  # Directories are processed based on file paths for simplicity in fallback

    processed_dirs = set()
    total_files = 0
    total_dirs = 0

    for path in all_paths:
        abs_path = os.path.abspath(path)
        rel_path = os.path.relpath(abs_path, project_root)

        if os.path.isfile(abs_path):
            total_files += 1
            stat = os.stat(abs_path)
            file_registry["files"].append(
                {
                    "path": rel_path,
                    "size_bytes": stat.st_size,
                    "last_modified": str(
                        datetime.datetime.fromtimestamp(stat.st_mtime)
                    ),
                    "file_type": os.path.splitext(rel_path)[1],
                }
            )
            # Also record directories encountered
            dir_name = os.path.dirname(rel_path)
            if dir_name and dir_name not in processed_dirs:
                file_registry["directories"].append({"path": dir_name})
                processed_dirs.add(dir_name)
                total_dirs += 1
        elif os.path.isdir(abs_path) and rel_path not in processed_dirs:
            # This branch mainly for cases where a directory might be in `all_paths` from git,
            # but git ls-files typically returns files.
            file_registry["directories"].append({"path": rel_path})
            processed_dirs.add(rel_path)
            total_dirs += 1

    # Ensure project_root itself is considered a directory
    if project_root not in processed_dirs:
        file_registry["directories"].append({"path": project_root})
        processed_dirs.add(project_root)
        total_dirs += 1

    file_registry["summary"] = {
        "total_files": total_files,
        "total_directories": total_dirs,
    }
    return file_registry


def write_system_inventory_md(
    file_registry: Dict[str, Any], output_path: str = "SYSTEM_INVENTORY.md"
):
    """
    Generates a human-readable SYSTEM_INVENTORY.md from the file registry.
    """
    with open(output_path, "w") as f:
        f.write("# System Inventory\n\n")
        f.write(f"Generated on: {file_registry['timestamp']}\n")
        f.write(f"Scanned path: `{file_registry['scanned_path']}`\n\n")
        f.write("## Summary\n")
        f.write(f"- Total Files: {file_registry['summary']['total_files']}\n")
        f.write(
            f"- Total Directories: {file_registry['summary']['total_directories']}\n\n"
        )

        f.write("## Directories\n")
        # Sort directories for consistent output
        sorted_dirs = sorted([d["path"] for d in file_registry["directories"]])
        for dir_path in sorted_dirs:
            f.write(f"- `{dir_path}/`\n")
        f.write("\n")

        f.write("## Files\n")
        # Sort files by path for consistent output
        sorted_files = sorted(file_registry["files"], key=lambda x: x["path"])
        for file_data in sorted_files:
            f.write(
                f"- `{file_data['path']}` (Size: {file_data['size_bytes']} bytes, Last Modified: {file_data['last_modified']})\n"
            )


def main():
    project_root = os.getenv(
        "PROJECT_ROOT", "."
    )  # Allow PROJECT_ROOT to be set via env var
    file_registry = generate_inventory(project_root)

    registry_path = os.path.join("workspace-automation", "file_registry.json")
    os.makedirs(os.path.dirname(registry_path), exist_ok=True)
    with open(registry_path, "w") as f:
        json.dump(file_registry, f, indent=4)
    print(f"File registry created at {registry_path}")

    write_system_inventory_md(file_registry)
    print("SYSTEM_INVENTORY.md generated.")


if __name__ == "__main__":
    main()
