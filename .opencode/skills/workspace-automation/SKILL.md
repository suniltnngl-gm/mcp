---
name: workspace-automation
description: Use when the user asks to run workspace maintenance, cycle, review, sync, auto-fix, knowledge search, AI assist, or brain memory operations. Use ONLY when the task involves workspace health, automation, or cross-repo operations — NOT for general coding. Covers the ~/Public/workspace.sh interface.
---

# Workspace Automation

Single entry point for all workspace operations: **`~/Public/workspace.sh`**

Run from any directory under `~/Public/`.

## Quick reference

| Command | What it does |
|---------|-------------|
| `workspace.sh review` | Full review cycle (git + tests + tasks) |
| `workspace.sh review --fast` | Quick git-only review |
| `workspace.sh auto` | Auto pipeline (detect gaps, fix, rebuild KB) |
| `workspace.sh auto --apply` | Auto pipeline with fixes applied |
| `workspace.sh ai ask <q>` | Ask Ollama cloud AI |
| `workspace.sh ai summarize` | AI summary of latest review |
| `workspace.sh kb-auto <query>` | Search cross-repo knowledge base |
| `workspace.sh kb-auto <query> --explain` | Search + AI explanation |
| `workspace.sh brain learn <task> <fix>` | Log a correction as a lesson |
| `workspace.sh brain status` | Show lesson/suppression stats |
| `workspace.sh brain sync` | Overnight sync |
| `workspace.sh plan` | Show current phase plan |
| `workspace.sh next` | Show next unblocked task |
| `workspace.sh cron-install` | Install 2 AM daily cron |

## Standard cycle (recommended)

1. `workspace.sh review` — assess health
2. `workspace.sh auto plan` — review what would be fixed
3. `workspace.sh auto --apply` — fix trivial gaps + rebuild KB
4. `workspace.sh ai summarize` — get AI summary
5. `workspace.sh brain sync` — sync lessons into context graph

## Agents

Custom agents available via `@agent-name`:
- `@review` — Run review cycle and summarize
- `@auto` — Run auto pipeline
- `@brain` — Manage lesson cache and context graph
- `@kb` — Search cross-repo knowledge base

## Project structure

- **project/** — MCP servers, automation modules, PLAN.md
- **Workspace/** — workspace.sh, os-env-manager, firebase-app
- **.opencode/** — Global config, KB, ENTRY.md, DASHBOARD.md
- **repositories/** — Dropbox utils, other repos
- **coding-agent/**, **next-steps/**, **shared-tools/** — Additional active repos
