# Developer Guide

This project is an LLM-Enhanced Distributed MCP Servers workspace. It consists of Python-based MCP servers, automation modules, and cross-repo tooling.

## Quick Start

```bash
uv sync                # Install dependencies
pre-commit install     # Install git hooks
uv run pytest .        # Run all tests
```

## Project Structure

| Directory | Purpose |
|-----------|---------|
| `src/llm_wrapper/mcp/` | MCP server implementations (ollama, osenv, firebase auth, doc manager, etc.) |
| `src/llm_wrapper/llm/` | LLM client wrappers (local, remote, enricher) |
| `review_cycle/` | Automated review: git scanner, test runner, task checker |
| `autofix/` | Auto gap detection and fixing pipeline |
| `autokb/` | Cross-repo knowledge base index and search |
| `ai_assist/` | Ollama cloud AI workspace assistance |
| `brain/` | Self-improving lesson cache (Perplexity Brain-style) |
| `workspace-automation/` | File registry, auto-register, orchestrator tools |
| `backups/` | Pre-edit snapshots and timestamped backups |
| `tests/` | Test suite |

## Key Tools

- **workspace.sh** (`~/Public/workspace.sh`) — single entry point for all workspace ops
- **uv** — Python project manager (replaces pip/poetry)
- **ruff** — Python linter and formatter
- **pre-commit** — Git hook framework
- **pytest** — Test runner

## Development Cycle

1. `workspace.sh review` — check current health
2. `workspace.sh auto plan` — review what would be auto-fixed
3. `workspace.sh auto --apply` — apply trivial fixes
4. Make your code changes
5. `workspace.sh review` — verify no regressions
6. Commit (see `CONTRIBUTING.md` for commit format)

## MCP Servers

MCP servers live in `src/llm_wrapper/mcp/` and are registered in `mcp.json` (legacy) and `opencode.json` (native). Available servers:

- `ollama_cloud` — free Ollama cloud models (ministral-3, gpt-oss)
- `osenv_manager` — osenv environment tools
- `firebase_auth` — Firebase Authentication token verification
- `system_utility` — sandboxed file/system operations
- `doc_manager` — document CRUD with SQLite
- `game_rules_manager` — game rules storage

See `CONTRIBUTING.md` for contributing guidelines and `CHECKLIST_DEVELOPMENT.md` for task execution steps.
