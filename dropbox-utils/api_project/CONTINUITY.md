# Dropbox File Listing Utility

## Purpose
A lightweight Python script (`list_dropbox_files.py`) that lists root folder contents from Dropbox or shows file revision history. Wrapped by a smart `run.sh` that adapts to three environments:

- **Dropbox mode**: syncs scripts to execution + repo dirs, then executes
- **Repo mode**: only allows `git` commands (init/status/add/commit/push/pull)
- **Execution mode**: runs the Python script directly, creating a uv venv if needed

## Usage
```bash
cd ~/Public/repositories/api_project
./run.sh                    # default: list Dropbox root
./run.sh list               # same as default
./run.sh revisions <path>   # show revision history for a file
```

## Requirements
- `DROPBOX_ACCESS_TOKEN` in `.env` (gitignored)
- `uv` for Python venv management
- Dropbox App with `files.metadata.read` scope

## Cross-Project Context
This project lives at `~/Public/repositories/` alongside:
- **`~/Public/Workspace/`** — Firebase app + osenv CLI + Antigravity agent
- **`~/Public/project/`** — LLM-MCP server orchestration

No direct integration with either project. Useful as reference for Dropbox API patterns.

## Shared Context
- `~/Public/.opencode/guidelines.md` — session rituals, project landscape
- `~/Public/.opencode/CROSS_PROJECT.md` — detailed cross-project integration map
- `~/.config/opencode/opencode.jsonc` — global opencode config (auto-loads guidelines)
