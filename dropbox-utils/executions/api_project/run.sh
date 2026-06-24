#!/bin/bash

# --- Environment Configuration ---
# Updated paths as per your request
DROPBOX_DIR="$HOME/Dropbox/api_project"
EXECUTION_BASE_DIR="$HOME/executions"
REPO_BASE_DIR="$HOME/repositories"

EXECUTION_DIR="$EXECUTION_BASE_DIR/api_project"
REPO_DIR="$REPO_BASE_DIR/api_project"

CURRENT_DIR=$(pwd)

# --- Main Logic ---

if [ "$CURRENT_DIR" == "$DROPBOX_DIR" ]; then
    # --- Sync Mode ---
    echo "Running in Dropbox directory. Syncing files..."
    
    # Ensure target directories exist
    mkdir -p "$EXECUTION_DIR"
    mkdir -p "$REPO_DIR"

    # Copy the core scripts to both locations
    cp "$DROPBOX_DIR/run.sh" "$EXECUTION_DIR/run.sh" && chmod +x "$EXECUTION_DIR/run.sh"
    cp "$DROPBOX_DIR/list_dropbox_files.py" "$EXECUTION_DIR/list_dropbox_files.py"
    
    cp "$DROPBOX_DIR/run.sh" "$REPO_DIR/run.sh" && chmod +x "$REPO_DIR/run.sh"
    cp "$DROPBOX_DIR/list_dropbox_files.py" "$REPO_DIR/list_dropbox_files.py"
    
    echo "Sync complete. Forwarding command..."
    echo "----------------------------------------------------"

    # The primary execution still happens in the EXECUTION_DIR
    cd "$EXECUTION_DIR" || exit
    exec "./run.sh" "$@"
    
elif [ "$CURRENT_DIR" == "$REPO_DIR" ]; then
    # --- Repo Mode ---
    if [ "$1" != "git" ]; then
        echo "Error: In this directory, only 'git' commands are supported." >&2
        echo "Usage: ./run.sh git <sub-command>" >&2
        exit 1
    fi
    shift
    GIT_SUB_COMMAND=$1
    if [ -z "$GIT_SUB_COMMAND" ]; then
        echo "Error: Please provide a git sub-command (e.g., init, status, add, commit)." >&2
        exit 1
    fi
    case "$GIT_SUB_COMMAND" in
        init) git init ;; 
        status) git status ;; 
        add) 
            [ -z "$2" ] && { echo "Usage: ./run.sh git add <file|.>" >&2; exit 1; }
            git add "$2"
            ;; 
        commit) 
            [ "$2" != "-m" ] || [ -z "$3" ] && { echo "Usage: ./run.sh git commit -m \"<your message>\"" >&2; exit 1; }
            git commit -m "$3"
            ;; 
        push) git push ;; 
        pull) git pull ;; 
        *) echo "Error: Unknown git command '$GIT_SUB_COMMAND'" >&2; exit 1 ;; 
    esac
    exit 0

elif [ "$CURRENT_DIR" != "$EXECUTION_DIR" ]; then
    echo "Error: This script must be run from one of the following directories:" >&2
    echo "1. Dev/Source Directory: $DROPBOX_DIR" >&2
    echo "2. Execution Directory:  $EXECUTION_DIR" >&2
    echo "3. Repo Directory:       $REPO_DIR" >&2
    exit 1
fi

# --- Execution Mode Logic ---
VENV_DIR="$EXECUTION_DIR/.venv"
PYTHON_VENV="$VENV_DIR/bin/python"
PYTHON_SCRIPT="$EXECUTION_DIR/list_dropbox_files.py"


show_help() {
    echo "Usage: ./run.sh [COMMAND] [OPTIONS]"
    echo ""
    echo "This script is environment-aware. Its behavior changes based on the directory it's run from."
    echo ""
    echo "--- In Execution Directory ($EXECUTION_DIR): ---"
    echo "  list              (Default) Lists files in the root Dropbox folder."
    echo "  revisions [PATH]  Lists the version history of a specific file."
    echo "  activate          Shows the command to activate the virtual environment."
    echo ""
    echo "--- In Git Repo Directory ($REPO_DIR): ---"
    echo "  git init                Initializes a new git repository."
    echo "  git status              Shows the git status."
    echo "  git add <file|.>        Adds files to the staging area."
    echo "  git commit -m \"msg\"   Commits the staged files."
    echo "  git push/pull           Pushes or pulls changes to/from the remote."
    echo ""
    echo "--- In Dropbox Directory ($DROPBOX_DIR): ---"
    echo "  Running any command will first sync scripts, then forward the execution."
    echo ""
}

run_python_command() {
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment in $VENV_DIR..."
        uv venv "$VENV_DIR"
    fi
    uv pip install --python "$PYTHON_VENV" dropbox python-dotenv --quiet
    echo "Running python script..."
    uv run --python "$PYTHON_VENV" "$PYTHON_SCRIPT" "$@"
}

COMMAND=${1:-list}
case "$COMMAND" in
    list) run_python_command "list" ;; 
    revisions) 
        [ -z "$2" ] && { echo "Error: 'revisions' command requires a file path." >&2; exit 1; }
        run_python_command "revisions" "$2"
        ;; 
    activate) echo -e "\nTo activate, run:\nsource $VENV_DIR/bin/activate\n" ;; 
    help) show_help ;; 
    *) echo "Error: Unknown command '$COMMAND'" >&2; show_help; exit 1 ;; 
esac
