#!/bin/bash

# simple_backup.sh: Create timestamped snapshots of selected project files/directories.
# Snapshots are stored locally under BACKUP_DIR and preserve source subdirectories.
# This is a lightweight convenience backup, not a full versioned backup system.

# Directory where snapshots are stored.
# Keep this path in .gitignore so backups are not committed accidentally.
BACKUP_DIR="backups/simple_copies"
mkdir -p "$BACKUP_DIR"

# Files/directories to snapshot.
# Prefer critical project metadata and generated files that change frequently.
# Adjust this list based on your workflow.
declare -a ITEMS_TO_BACKUP=(
    "workspace-automation/file_registry.json"
    "SYSTEM_INVENTORY.md"
    "CHANGELOG.md"
    "PLAN.md" # Project roadmap and phase tracker
    # Example: If there's a critical configuration file that gets updated by tooling
    # "config/mcp.json"
    # Example: If there's a directory of logs or data you want to snapshot
    # "data/important_logs"
)

# For single-file snapshots before manual edits, use pre_edit_backup.sh.
# Example: ./pre_edit_backup.sh src/my_module.py

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "Starting light backup by creating timestamped copies..."

for ITEM_PATH in "${ITEMS_TO_BACKUP[@]}"; do
    if [ -e "$ITEM_PATH" ]; then # Only process paths that currently exist.
        # Build the destination subdirectory while preserving source structure.
        DIR_NAME=$(dirname "$ITEM_PATH")
        BASE_NAME=$(basename "$ITEM_PATH")
        
        TARGET_BACKUP_SUBDIR="$BACKUP_DIR/$DIR_NAME"
        mkdir -p "$TARGET_BACKUP_SUBDIR" # Ensure destination directory exists.
        
        if [ -f "$ITEM_PATH" ]; then
            # For files, append the timestamp to the output filename.
            # Handle files with no extension separately.
            if [[ "$BASE_NAME" == "${BASE_NAME%.*}" ]]; then
                RENAMED_FILE="$TARGET_BACKUP_SUBDIR/${BASE_NAME}_${TIMESTAMP}"
            else
                RENAMED_FILE="$TARGET_BACKUP_SUBDIR/${BASE_NAME%.*}_${TIMESTAMP}.${BASE_NAME##*.}"
            fi
            cp "$ITEM_PATH" "$RENAMED_FILE"
            echo "Copied file '$ITEM_PATH' to '$RENAMED_FILE'"
        elif [ -d "$ITEM_PATH" ]; then
            # For directories, copy recursively and timestamp the directory name.
            RENAMED_DIR="$TARGET_BACKUP_SUBDIR/${BASE_NAME}_${TIMESTAMP}"
            cp -r "$ITEM_PATH" "$RENAMED_DIR"
            echo "Copied directory '$ITEM_PATH' to '$RENAMED_DIR'"
        fi
    else
        echo "Warning: '$ITEM_PATH' not found, skipping."
    fi
done

echo "Light backup complete! Check the '$BACKUP_DIR' directory."