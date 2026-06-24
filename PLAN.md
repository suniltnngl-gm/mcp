# Project Plan: LLM-Enhanced Distributed MCP Servers

## Project Goal
Implement a hybrid Large Language Model (LLM) system where a local LLM can boost and optimize provider LLMs, with both co-existing and running in parallel for an optimum developer experience. This core LLM integration will be preceded by a foundational wrapper phase, and subsequently followed by a suite of specialized Model Context Protocol (MCP) servers focusing on cloud-neutral context and document management to create robust, LLM-enhanced applications leveraging distributed capabilities.

## Assumptions
*   **Language:** Python
*   **MCP Definition:** Model Context Protocol (standardized specification for model capabilities/configuration).
*   **Core Focus:** Prioritize initial wrapper development, then hybrid LLM integration (local boosting provider), and foundational planning structures.
*   **Parallel Execution:** Local and provider LLMs, along with MCP servers, will be designed to run in parallel for optimal developer experience.
*   **Cloud Neutral Architecture:** The system will be designed to be cloud-neutral, avoiding vendor lock-in and allowing deployment across various cloud providers or on-premise environments.

## High-Level Roadmap

1.  **Foundational Setup & Project Structure:** Establish basic environment, core data models (including 'Plan' structures), and essential utilities.
2.  **Pre-LLM Wrapper Development:** Build the foundational wrapper that will eventually integrate with and manage LLMs.
3.  **Local LLM Integration:** Integrate local LLM models and fine-tune the wrapper for local boosting/optimization.
4.  **Provider LLM Integration:** Integrate external provider LLMs and enhance the wrapper for parallel execution and optimization.
5.  **MCP Foundational Elements:** Define MCP Data Models and the basic Server/Client Framework.
6.  **Document Management System:** Implement capabilities for scanning, analyzing, and indexing documents for LLM context.
7.  **Distributed MCP Server Development:** Develop specialized MCP servers focusing on cloud-neutral services.
8.  **Interactive Rules/Game Integration:** Implement interactive reasoning rules or game mechanics.
9.  **Hybrid LLM/MCP Orchestration & Refinement:** Orchestrate the hybrid LLM system with MCP servers, and refine the overall architecture.
10. **Testing & Optimization:** Comprehensive testing and performance optimization.
11. **Workflow Unification & Automation:** Streamline project management, backups, and change tracking.

### Cross-Project Integrations (Phase 12 — 4/5 done)

Work done across all 6 active repos (tracked in `~/.opencode/`):

- **Consolidated 17→9 repos**: Archived 9 stale/empty repos, merged 5 into project/ + devflow-intelligence/
- **Git config unified**: All repos → `suniltnngl-gm`
- **Branch standardization**: `master` → `main` in next-steps & project/shared
- **CI/CD added**: Workspace CI (shellcheck + firebase-app build), firebase-app CI
- **Dependabot**: Enabled on workspace, coding-agent, dropbox-utils, next-steps, project/shared
- **READMEs**: Added to workspace, firebase-app, dropbox-utils
- **Test skeletons**: Vitest setup for firebase-app, test docs for workspace
- **next-step integration**: Added to ENTRY.md workflow, workspace.sh ns commands
- **Dropbox SDK**: v12.0.2 installed, API working (needs scope fix for file listing)
- **Ollama SDK**: v0.6.2 installed, cloud API at `https://ollama.com` (key in `ENV/.env`)
- **TODOs resolved**: 3 in project/ (dynamic commit msg, MCP config loading, .gitignore parsing)
- **Health audit standardized**: `review_cycle/health_audit.py` with 36 checks, integrated into auto pipeline, `workspace.sh health-audit` command
- **Templates created**: Issue/finding + decision templates at `~/.opencode/templates/`
- **Deep merge analysis**: All 9 repos analyzed, zero real code duplication confirmed
- **Tests consolidated**: 40 orphan test stubs moved to respective repos
- **ENV/ + hf/ merged** into project/ with backward-compat symlinks
- **Renamed**: `data_models/llm_wrapper.py` → `llm_wrapper/models.py`; removed dead `enhanced_agent_v2.py`; consolidated `src/tests/` → `tests/`

## Detailed Plan & Todo List

The following tasks are organized into phases, reflecting the detailed steps required to achieve the project goal.

### Progress Summary

| Phase | Status | Tasks Done | Tasks Pending | Type Mix |
|-------|--------|------------|---------------|----------|
| 0. Genesis | ✅ | 7/7 | — | plan+build |
| 1. Foundational Setup | ✅ | 5/5 | — | build |
| 2. Pre-LLM Wrapper | ✅ | 2/2 | — | plan+build |
| 3. Local LLM | ✅ | 2/2 | — | build |
| 4. Provider LLM | ✅ | 3/3 | — | build |
| 5. MCP Foundational | ✅ | 3/3 | — | plan+build |
| 6. Document Management | ✅ | 3/3 | — | build |
| 7. Distributed MCP Servers | ✅ | 3/3 | — | build |
| 8. Game Integration | ✅ | 1/1 | — | build |
| 9. Orchestration | ✅ | 3/3 | — | build |
| 10. Testing | ✅ | 4/4 | — | build |
| 11. Workflow Automation | ✅ | 6/6 | — | plan+build |
| 12. Cross-Project Integrations | ✅ | 5/5 | — | build |
| 13. Automated Review Cycle | ✅ | 5/5 | — | build |
| 14. Automated Knowledge Base | ✅ | 5/5 | — | build |
| 15. Auto Gap-Find & Fix Pipeline | ✅ | 5/5 | — | build |
| 16. DevFlow Intelligence | ✅ | Complete | — | build |
| 17. Code Review Consolidation | ✅ | Complete | — | build |
| 18. Git Todo Monitor | ✅ | 4/4 | — | build |
| 19. Hugging Face Hub CLI | ✅ | 4/4 | — | build |
| 20. GitHub Automation | ✅ | 3/3 | — | build |
| 21. Web Dashboard | ⏳ | 0/3 | 3 (~2h) | build |
| 22. Cloud Storage Sync | ⏳ | 0/3 | 3 (~1h) | build |
| 23. Deploy Apps | ⏳ | 0/2 | 2 (~45min) | build |
| 24. Softr API Integration | ✅ | 9/9 | — | build |
| 25. Replit API Integration | ✅ | 11/11 | — | build |
| 26. DevEnvSync | 🔍 Review | 0/4 | 4 | build |
| 27. DevFlow Wiki | ⏳ | 1/N | ~46 | docs |
| 28. Repo Restructure | ✅ | 6/6 | — | plan+build |
| 29. KB & coding-agent overhaul | 🔄 | 4/5 | 1 (~30min) | plan+build |

**Task type legend:**
- `plan` — Design, research, architecture. Output: specs, diagrams, decision docs.
- `build` — Code, implement, test. Output: working code, passing tests.
- `plan+build` — Both design and implementation in one task.

Phase 0 (Genesis) — foundational workspace infrastructure, conventions, and cross-project tooling established before Phase 1.
Phases 1–11 complete. Phase 12 — 5/5 done. Phase 13 — 13.1–13.5 done. Phase 14 — 14.1–14.5 done. Phase 15 — all 5 tasks done. Phase 18 v2.0 shipped.
Phases 16–17 complete (historical projects discovered during repo audit).
Phases 18–20 discovered during repo audit — each has its own git history and independent plan.
Phases 19–23 cloud/web tool ecosystem — HF Hub, GitHub auto, dashboard, cloud storage, deploy.
Phases 24–25 MCP servers — Softr and Replit API wrappers (completed).
Phases 26–27 discovered during repo audit — DevEnvSync, devflow-intelligence/wiki.

### Phase 12: Cross-Project Integrations

**Status:** in progress

| # | Integration | Status | Blocked By | Blocks |
|---|-------------|--------|------------|--------|
| 1 | osenv → MCP Bridge | ✅ Completed | — | #2 |
| 2 | Antigravity Agent → MCP | ✅ Completed | #1 | — |
| 3 | Firebase Auth as MCP Identity | ✅ Completed | — | #5 |
| 4 | Shared Tools & Configs | ✅ Completed | — | — |
| 5 | Data Sharing (Firestore) | ✅ Completed | — | — |

**Dependency chain:** `#3 → #5` (tools & configs #4 independent). #3 complete — #5 unblocked. #5 complete.

#### Task 12.3: Firebase Auth as MCP Identity
- **Status:** completed
- **Type:** build
- **Delivered:**
  - `firebase_auth_middleware.py` — stateless token verification, `IdentityContext` dataclass, 4 error types (`TOKEN_EXPIRED`, `TOKEN_INVALID`, `TOKEN_REVOKED`, `SERVICE_ACCOUNT_MISSING`) with parseable JSON contracts
  - `firebase_auth_server.py` — MCP server exposing `verify_auth_token` and `get_user_claims` tools
  - Registered in `mcp.json` as `firebase_auth`, wired into Antigravity agent (`agent/main.py`)
  - `workspace.sh` — `auth-verify` and `auth-claims` CLI commands
  - ✅ Passes CEG: stateless (no disk writes), modular CC (10–15), parseable JSON error contracts

#### Task 12.4: Shared Tools & Configs
- **Status:** completed
- **Type:** build
- **Note:** Created `~/.opencode/shared/` with canonical pyproject.toml, .editorconfig, .pre-commit-config.yaml, python-ci.yml, shellcheck.yml. Wired into project/ (updated CI, added pre-commit), Workspace/ (added .editorconfig), project/dropbox-utils/ (added pyproject.toml, .editorconfig, CI).

#### Task 12.5: Data Sharing (Firestore)
- **Status:** completed
- **Type:** build
- **Unblocked** by #3 completion.
- **Delivered:**
  - `firestore_doc_service.py` — Firestore-backed document storage replacing local SQLite. Lazy Firebase Admin init, SHA256-hashed doc IDs, client-side search for full-text matching, batch delete support.
  - `doc_manager_server.py` — Updated to use Firestore via `firestore_doc_service`. Added `list_documents` and `delete_document` tools. Removed SQLite dependency.
  - `project/mcp.json` — Updated doc_manager entry: uses `uv run` for dependency resolution, service account env var instead of DB_PATH.
  - `~/.gemini/config/mcp_config.json` — Updated doc_manager env with `FIREBASE_SERVICE_ACCOUNT_PATH`.
  - Wired into Antigravity agent (`agent/main.py`) — already registered as `doc_manager` MCP server. No agent config change needed.
- Removes SQLite dependency from doc manager. Enables real-time document sync across projects with Firebase Auth isolation.

### Phase 13: Automated Review Cycle

**Status:** in progress

Automated system that periodically reviews all active repos, plans next actions, and optionally builds suggestions. See `REVIEW_CYCLE_PLAN.md` for full design.

| Task | Status | Type |
|------|--------|------|
| 13.1 Foundation — scanners (git, tests, tasks) | ✅ Completed | build |
| 13.2 Review Engine — scoring, baseline, reports | ✅ Completed | plan+build |
| 13.3 Automation — cron workflow, watch mode, hooks | ✅ Completed | build |
| 13.4 Auto-fix & PR — known patterns, approval gate | ✅ Completed | build |
| 13.5 Scoring & Trends — health score, dashboard badge | ✅ Completed | build |

**Dependency chain:** `13.1 → 13.2 → 13.3 → 13.4 → 13.5`

### Phase 14: Automated Knowledge Base

**Status:** in progress

Auto-discovering, cross-repo knowledge base that indexes all code and docs, providing ranked search results. See `autokb/` for implementation.

Existing implementation has been confirmed in `devflow-intelligence/src/intelligence/knowledge_base.py`, `devflow-intelligence/scripts/populate_kb_with_patterns.py`, `devflow-intelligence/examples/kb_demo.py`, and the workspace search wrapper `./kb.sh`. The remaining work is operational integration, scheduled refresh, and workflow attachment.

| Task | Status | Type |
|------|--------|------|
| 14.1 Indexer — scan all 8 repos, build inverted index | ✅ Completed | build |
| 14.2 Search — ranked results with fuzzy matching, --json, --fast | ✅ Completed | build |
| 14.3 Unify KB.md + osenv/kb.py + raw code into one query | ✅ Completed | build |
| 14.4 `Workspace/workspace.sh` commands (kb-auto search/scan/stats) | ✅ Completed | build |
| 14.5 Auto-index on schedule (cron / git hook) | ✅ Completed | build |

### Phase 15: Auto Gap-Find & Fix Pipeline

**Status:** completed

Automated pipeline that detects gaps, fixes trivial ones, rebuilds the knowledge base, and integrates with the plan/build workflow. See `autofix/` for implementation.

| Task | Status | Type |
|------|--------|------|
| 15.1 Gap detectors — missing docs, tests, .env.example, orphaned files, stale tracking | ✅ Completed | build |
| 15.2 Auto-fixers — registry of 6 fixers with approval gate | ✅ Completed | build |
| 15.3 Auto-rebuild autokb after pipeline run | ✅ Completed | build |
| 15.4 workspace.sh auto command (run/plan/status/fixable) | ✅ Completed | build |
| 15.5 Integrated with review cycle + plan/build workflow | ✅ Completed | build |

### Phase 16: DevFlow Intelligence Platform

**Status:** completed (historical)

**Repos:** `progressive-build/` (build docs, archive), `devflow-intelligence/` (code, 7K lines Python)

A completed AI-powered development automation platform with 20+ production modules, built via iterative progressive build methodology. Combines knowledge base, pattern recognition, safety checks, smart git operations, and workflow automation.

| Module | Lines | Confidence |
|--------|-------|------------|
| Core (config, safety, secrets, subprocess, plugins, validation) | ~1,200 | 90–95% |
| Intelligence (knowledge base, pattern recognition, code gen, self-improvement) | ~900 | 87–92% |
| Automation (backup, health monitor, task manager, test gen, workflow) | ~1,100 | 85–90% |
| Git integration (safe merge, smart add) | ~400 | 90% |
| Analysis (duplication detector) | ~200 | 87% |
| CLI (interactive) | ~125 | 85% |
| **Total** | **~3,925** | **87–95%** |

| Task | Status | Type |
|------|--------|------|
| 16.1 Core — config management, safety checks, secret handling, subprocess runner, plugin system, input validation | ✅ Complete | build |
| 16.2 Intelligence — knowledge base, pattern recognition, code generation, self-improvement loop | ✅ Complete | build |
| 16.3 Automation — backup system, health monitor, task manager, test generation, workflow engine | ✅ Complete | build |
| 16.4 Git integration — safe merge, smart add with context awareness | ✅ Complete | build |
| 16.5 Analysis — duplication detector, code smell scanner | ✅ Complete | build |
| 16.6 CLI — interactive shell, command autocomplete, status dashboard | ✅ Complete | build |

**Next steps:**
- Archive `progressive-build/` build docs (keep only FINAL_REPORT.md + CLEANUP_PLAN.md) → ✅ archived to `archive/progressive-build/`
- Fix broken symlinks in `devflow-intelligence/` (consolidation-docs, toolkit)
- Evaluate if devflow-intelligence code should merge into main `project/` or stay standalone

### Phase 17: Code Review Consolidation

**Status:** completed (historical)

**Repo:** `consolidation/` — 11-phase migration of code-review logic from 8 projects into `project/shared/code-review-toolkit/`

Migrated duplicate code-review logic from coding-agent, unified-devflow, dev-refactor, ai-orchestra, coding-tools-wrapper, todo-automator, and unified-project into a single shared Python package.

| Task | Status | Type |
|------|--------|------|
| 17.1 Audit — identify all code-review logic across 8 repos, catalog duplicate functionality | ✅ Complete | plan |
| 17.2 Shared package — create `project/shared/code-review-toolkit/` (AICodeReviewer, ReviewCache, CustomRuleEngine, PatternLearner) | ✅ Complete | build |
| 17.3 coding-agent migration — port to shared package, remove local copy | ✅ Complete | build |
| 17.4 unified-devflow migration — port, remove local copy | ✅ Complete | build |
| 17.5 dev-refactor migration — port, remove local copy | ✅ Complete | build |
| 17.6 ai-orchestra migration — port, remove local copy | ✅ Complete | build |
| 17.7 coding-tools-wrapper migration — port, remove local copy | ✅ Complete | build |
| 17.8 todo-automator migration — port, remove local copy | ✅ Complete | build |
| 17.9 unified-project migration — port, remove local copy | ✅ Complete | build |
| 17.10 Test — verify all imports resolve, run consolidated test suite | ✅ Complete | build |
| 17.11 Finalize — archive `consolidation/` repo, update cross-repo READMEs | ✅ Complete | plan |

**Results:** 0% code duplication, 80%+ maintenance reduction, 4x faster feature deployment.

**Next steps:**
- Archive `consolidation/` repo (keep only FINAL_STATUS.md) → ✅ archived to `archive/consolidation/`
- Ensure `project/shared/code-review-toolkit/` still exists and is importable

### Phase 18: Git Todo Monitor

**Status:** v1.0 shipped, v2.0+ planned

**Repo:** `project/todo-automator/` — TODO tracking CLI with AI summaries

Current v1.0 monitors git repos for TODO/FIXME comments, sends AI summaries via OpenAI, and displays Ubuntu desktop notifications. 903 lines Python across 7 modules.

| Milestone | Target | Progress | Features |
|-----------|--------|----------|----------|
| v1.0 | Shipped | ✅ 100% | Core monitoring, AI summaries, cron/hook scheduling |
| v2.0 | 2026-06-22 | ✅ 100% | Ollama cloud AI, GitHub Issues sync via gh CLI, Commit Analysis |
| v2.1 | 2025-12-11 | ⏳ 0% | Multi-repo config, aggregated summaries, repo comparison |
| v3.0 | 2026-01-10 | ⏳ 0% | Web dashboard, analytics, interactive charts, export |

**Next steps:**
- Replace OpenAI dependency with free Ollama cloud models (OLLAMA_API_KEY already loaded)
- Build v2.0: GitHub Issues integration via `gh` CLI
- Build v2.1: Multi-repo support
- Build v3.0: Web dashboard

### Phase 26: DevEnvSync

**Status:** review — merge analysis complete, keep standalone

**📋 Prepare — complete before starting:**
- [x] **📐 Design:** Deep merge analysis — confirmed zero MCP overlap, Windows-specific, messy
- [ ] **📐 Design:** Review REFACTOR_PROGRESS.json (40 tasks, 0%)
- [ ] **🧹 Cleanup:** Remove bloated planning artifacts (504-line JSON at 0%)
- [ ] **🛠 Tool:** Fix hardcoded Windows paths in restructure_plan.py

**✅ Post — complete after finishing:**
- [ ] **🏷 Tag:** Git tag `anchor-YYYYMMDD`
- [ ] **📝 Log:** Update AGENT_LOG.md
- [ ] **📋 Plan:** Mark Phase 26 complete
- [ ] **📊 Dash:** Update DASHBOARD.md
- [ ] **🗳 Vote:** Re-run vote
- [ ] **📚 KB:** Rebuild KB

**Repo:** `DevEnvSync/` — Professional dev environment sync tool (57MB, 174 Python files, 26K lines)

Windows-focused CLI tool with "MCP" context manager (misnamed — actually a context persistence logger, not Model Context Protocol). AWS integration, AI agent, context management, and race-detection systems.

**Deep merge analysis result** (2026-06-24):
- **Zero actual MCP overlap** with project/llm_wrapper/mcp/ — DevEnvSync's `mcp_context_manager.py` writes JSON context snapshots; project/ has real MCP protocol using `mcp` PyPI library
- **Zero Python imports** cross-repo — all repos are functionally independent
- **Recommendation: Keep standalone.** Architectural mismatch (Windows paths, 129 files, Amazon Q dependency). Consider archiving if no active external consumers.
- Contribution: Move `src/data_models/llm_wrapper.py` → `src/llm_wrapper/models.py` (done for project/)

| Component | Files | Lines | Description |
|-----------|-------|-------|-------------|
| `devenv_sync/` package | ~40 | ~8,000 | CLI app, core engine, services, AWS integration |
| Root scripts | ~30 | ~6,000 | MCP server, AI manager, context manager |
| `scripts/` | ~40 | ~5,000 | Automation agents, git managers, AWS cost tools |
| Tests | 18+ | ~5,000 | Integration, unit, performance tests |
| Config/docs/batch | ~133 files | — | Planning artifacts, docs, CI/CD, batch files |

**Next steps:**
- Consider archiving if no active consumers — compare with archive/ pattern
- Clean up planning artifacts (REFACTOR_PROGRESS.json is 504 lines of planning at 0%)

### Phase 27: DevFlow Wiki

**Status:** partial — infrastructure ready, content missing. Wiki repo merged into devflow-intelligence/

**📋 Prepare — complete before starting:**
- [x] **📐 Design:** Deep merge analysis — keep standalone, KB is complementary to project/autokb/
- [ ] **📐 Design:** Content plan — which 4/50 pages exist, which to write next
- [x] **🛠 Tool:** MkDocs + Material theme — already set up ✅
- [x] **🛠 Tool:** GitHub Pages deploy — already configured ✅
- [x] **🧹 Merge:** `devflow-wiki/` → `devflow-intelligence/wiki/` (embedded .git removed, commits flattened)

**✅ Post — complete after finishing:**
- [ ] **🏷 Tag:** Git tag `anchor-YYYYMMDD`
- [ ] **📝 Log:** Update AGENT_LOG.md
- [ ] **📋 Plan:** Mark Phase 27 complete
- [ ] **📊 Dash:** Update DASHBOARD.md
- [ ] **✅ Verify:** Confirm GitHub Pages renders correctly
- [ ] **📚 KB:** Rebuild KB

**Location:** `devflow-intelligence/wiki/` — MkDocs wiki for DevFlow Intelligence platform (merged from devflow-wiki/)

MkDocs site with Material theme, dark/light mode, search, Mermaid diagrams, Google Analytics, GitHub Pages auto-deploy. 50-page structure defined in mkdocs.yml, but only 4 content pages written.

**Deep merge analysis result** (2026-06-24):
- devflow-intelligence `knowledge_base.py` is a structured KB (Pattern, Learning, BestPractice dataclasses)
- project/autokb/ is a file-level TF-IDF search index — **zero code overlap**, complementary systems
- Recommendation: Keep standalone for now. If merging, only merge `knowledge_base.py` as `project/shared/structured_kb.py`

| Section | Pages | Status |
|---------|-------|--------|
| Getting Started | 4 pages | 1/4 written |
| Core Concepts | 5 pages | 0/5 |
| Components | 6 pages | 0/6 |
| User Guides | 5 pages | 0/5 |
| API Reference | 5 pages | 0/5 |
| Tutorials | 4 pages | 0/4 |
| Reference | 4 pages | 0/4 |
| Best Practices | 4 pages | 0/4 |
| Troubleshooting | 4 pages | 0/4 |
| Contributing | 4 pages | 0/4 |
| About | 4 pages | 0/4 |
| **Total** | **~50 pages** | **4/50 written** |

**Next steps:**
- Write content for all 50 pages
- Deploy to GitHub Pages
- Link from project README

### Phase 28: Repo Restructure & Renaming

**Status:** completed

**Stack:** bash + git + mv

**Tasks:**

| Task | Status | Type |
|------|--------|------|
| 28.1 Deep merge/split analysis — overlap matrix, dependency graph, trade-off table | ✅ Complete | plan |
| 28.2 Move test stubs → respective repos (40 files) | ✅ Complete | build |
| 28.3 Merge ENV/ → project/ (symlink backward compat) | ✅ Complete | build |
| 28.4 Merge hf/ → project/ (symlink backward compat) | ✅ Complete | build |
| 28.5 Rename `data_models/llm_wrapper.py` → `llm_wrapper/models.py` | ✅ Complete | build |
| 28.6 Remove dead `enhanced_agent_v2.py` | ✅ Complete | cleanup |

**Key findings from deep analysis:**
- **Zero real code duplication** across all 9 repos — all suspected overlap pairs confirmed as different concerns sharing similar names
- `coding-agent/providers` vs `project/llm_wrapper`: ~30% domain overlap, 0% code, different architecture (sync vs async)
- `DevEnvSync/mcp` vs `project/llm_wrapper/mcp`: Zero overlap — DevEnvSync's "MCP" is a context logger, not Model Context Protocol
- `project/autokb` vs `devflow-intelligence/knowledge_base`: Zero overlap — file search vs structured learning
- **project/ is not too big** (252 source files) — splitting would add friction for no gain

### Phase 29: KB & coding-agent overhaul

**Status:** in progress (0/5)

**Stack:** Python, bash, git, autokb

**Tasks:**

| Task | Status | Type | ⏱ |
|------|--------|------|----|
| 29.1 autokb legacy+user-files — include both predecessor workspaces with user-files-only filter | ✅ Complete | build | 30min |
| 29.2 coding-agent — consolidate 37 root .py files into agent/ package | ✅ Complete | build | 30min |
| 29.3 next_step.py — split monolithic 6.8K file into modules | ✅ Complete | build | 20min |
| 29.4 shared-tools extraction — mine 670 .py files from legacy workspace | ✅ Complete | build | 45min |
| 29.5 todo-automator v2.0 — replace OpenAI dependency with free Ollama cloud API | ✅ Complete | docs | 10min |

**What changed:**
- autokb now indexes both legacy workspaces (`/media/sunil-kr/storage/user-projects/` and `workspace/`) labeled `legacy/` prefix
- All generated/cache/third-party files excluded from index (built caches, venvs, archives, build output, tool configs)
- EXCLUDE_PATTERNS filtering applied to both `git ls-files` and `find` code paths
- Index: 7,093 user files, 120,827 terms, 9 repos + osenv
- Health: 95/100

**Decisions:**
- Legacy repos use `find` (not `git ls-files`) to catch files in independent child repos with their own `.git`
- Excluded: `.kiro/`, `.versions/`, `.gemini/`, `artifacts/`, `dist/`, `build/`, `.next/`, `.egg-info/`, `package-lock.json`, `file_registry_cache*`, `workspace_review.json`

**Next:** coding-agent consolidation, next_step.py split, shared-tools extraction, todo-automator v2.0

### Phase 21: Softr API Integration

**Status:** completed

**Repos:** `project/src/llm_wrapper/mcp/softr_server.py`

MCP server wrapping the Softr Studio API (user management) and Softr Database API (table CRUD). Requires `SOFTR_API_KEY` in `~/Public/ENV/.env`.

| Tool | API | Description |
|------|-----|-------------|
| `softr_list_databases` | Tables | List accessible databases |
| `softr_list_tables` | Tables | List tables in a database |
| `softr_query_records` | Tables | Query records with limit |
| `softr_create_record` | Tables | Insert a new record |
| `softr_update_record` | Tables | Update by record ID |
| `softr_delete_record` | Tables | Delete by record ID |
| `softr_create_user` | Studio | Create app user |
| `softr_get_user` | Studio | Lookup by email |
| `softr_delete_user` | Studio | Delete app user |

**Next steps:**
- Register `Softr-Domain` header support per-app (currently reads from tool input)
- Add webhook event listing if Softr exposes it

### Phase 22: Replit API Integration

**Status:** completed

**Repos:** `project/src/llm_wrapper/mcp/replit_server.py`

MCP server wrapping the Replit REST API v1 (`replit.com/api/v1`). Requires `REPLIT_API_KEY` in `~/Public/ENV/.env` (generate at `replit.com/account#api-tokens`).

| Tool | Endpoint | Description |
|------|----------|-------------|
| `replit_list_repls` | GET /repls | List all Repls |
| `replit_create_repl` | POST /repls | Create a Repl |
| `replit_get_repl` | GET /repls/{id} | Get Repl details |
| `replit_update_repl` | PATCH /repls/{id} | Update Repl metadata |
| `replit_delete_repl` | DELETE /repls/{id} | Delete a Repl |
| `replit_deploy_repl` | POST /repls/{id}/deployments | Deploy to production |
| `replit_list_deployments` | GET /repls/{id}/deployments | List deployments |
| `replit_get_deployment` | GET /deployments/{id} | Get deployment details |
| `replit_delete_deployment` | DELETE /deployments/{id} | Remove deployment |
| `replit_get_user` | GET /user or /users/{username} | Get current/public user |
| `replit_list_user_repls` | GET /users/{username}/repls | List user's public Repls |

**Next steps:**
- Add Repl file read/write if Replit exposes a filesystem API
- Add webhook management endpoints

### Phase 0: Genesis — Workspace Infrastructure & Conventions

**Status:** completed (foundational)

The meta-layer that makes every other phase possible: workspace directory structure, cross-project conventions, automation framework, and knowledge infrastructure. All established before Phase 1.

**Why:** Without a shared convention for repos, commit messages, environment variables, and automation scripts, every phase reinvents the wheel. Genesis standardizes the foundation so all 14+ repos behave as one coherent system.

| Task | Status | Type |
|------|--------|------|
| 0.1 Workspace directory layout (~/Public/) | ✅ Complete | plan |
| 0.2 .opencode/ conventions (ENTRY.md, guidelines, DASHBOARD, AGENT_LOG) | ✅ Complete | plan+build |
| 0.3 workspace.sh — unified CLI across all repos | ✅ Complete | build |
| 0.4 ENV/.env — centralized secret management | ✅ Complete | plan |
| 0.5 Git conventions — branch naming, commit format (<scope>: <desc>), pre-push hooks | ✅ Complete | plan+build |
| 0.6 Cross-project knowledge infrastructure — autokb, PLAN.md, AGENTS.md | ✅ Complete | build |
| 0.7 Cross-project review cycle — review_cycle/ engine, scanners, vote, decision system | ✅ Complete | build |

**Deliverables:**
- `~/Public/.opencode/` — ENTRY.md (session lifecycle), guidelines.md (session continuity), DASHBOARD.md (health/status), AGENT_LOG.md (audit trail)
- `~/Public/workspace.sh` — 1K+ line unified CLI with 40+ commands across 8 command groups
- `~/Public/ENV/.env` — 8+ API keys loaded by all tools, gitignored
- `~/Public/project/review_cycle/` — scoring engine, scanners, vote, decision log, scheduler, priority, session manager, compact, data collector, prepost checklists
- `~/Public/project/autokb/` — auto-discovering knowledge base indexing all 14+ repos
- Git pre-push hooks installed across all repos from single source

**Next steps:**
- None — foundational layer is complete and stable. Future changes are additive (new commands, new tools) but the structure is frozen.

### Phase 1: Foundational Setup & Project Structure
**Status:** completed

*   **Task 1.1: Project Setup & Virtual Environment**
    *   **Status:** completed
    *   Create project directory (already exists).
    *   Set up a Python virtual environment (using `uv venv`).
    *   Install core dependencies (`uv`, `pydantic` for config, `requests`, `httpx`).
*   **Task 1.2: Define Core Project Data Models (Python using Pydantic)**
    *   **Status:** completed
    *   Based on the immediate need for the pre-LLM wrapper phase, define Python data models (e.g., using Pydantic) for core entities related to the wrapper's internal state, configuration, and its eventual interaction with a local LLM. This includes models for `WrapperConfig`, `LocalLLMConfig`, `ModelParameters`, `InferenceRequest`, and `InferenceResponse`.
*   **Task 1.3: Implement Generic Workspace Inventory (auto_register.py)**
    *   **Status:** completed
    *   Develop `workspace-automation/src/auto_register.py` to scan the project directory, respect `.gitignore`, and generate `file_registry.json` and `SYSTEM_INVENTORY.md`.
*   **Task 1.4: Implement Light Local Backup Script (simple_backup.sh)**
    *   **Status:** completed
    *   **Note:** This script is part of the current active backup strategy for periodic project snapshots.
    *   Develop `simple_backup.sh` to create timestamped copies of essential project files/directories in a local `backups/simple_copies` folder.
*   **Task 1.5: Implement Pre-Edit Backup Helper Script (pre_edit_backup.sh)**
    *   **Status:** completed
    *   Develop `pre_edit_backup.sh` to create timestamped copies of a file to `backups/pre_edit_snapshots` before it's edited.

### Phase 2: Pre-LLM Wrapper Development
**Status:** completed

*   **Task 2.1: Define Wrapper Architecture & Core Components:**
    *   **Status:** completed
    *   Design the high-level architecture for the wrapper that will eventually manage LLM interactions.
    *   Identify core components, interfaces, and data flows.
*   **Task 2.2: Implement Basic Wrapper Structure:**
    *   **Status:** completed
    *   Develop the initial Python classes and modules for the wrapper, focusing on its foundational structure without direct LLM integration yet.

### Phase 3: Local LLM Integration
**Status:** completed

*   **Task 3.1: Local LLM Environment Setup:**
    *   **Status:** completed
    *   Select and integrate a local LLM library (e.g., `ollama`, `llama-cpp-python`).
    *   Acquire and load a suitable tiny model.
*   **Task 3.2: Integrate Local LLM into Wrapper:**
    *   **Status:** completed
    *   Modify the wrapper to interact with the local LLM, enabling basic invocation and initial boosting/optimization strategies.

### Phase 4: Provider LLM Integration
**Status:** completed

*   **Task 4.1: Provider LLM Environment Setup:**
    *   **Status:** completed
    *   Choose and integrate with an external LLM provider (e.g., OpenAI, AWS Bedrock).
    *   Manage API calls, messages, and token usage.
*   **Task 4.2: Integrate Provider LLM into Wrapper:**
    *   **Status:** completed
    *   Enhance the wrapper to interact with the provider LLM, enabling parallel execution and further optimization strategies.
*   **Task 4.3: Develop Hybrid LLM Client:**
    *   **Status:** completed
    *   Create a generic Python class (`LLMClient`) to abstract and manage interactions with both local and provider LLMs, enabling boosting/optimization strategies and parallel execution.

### Phase 5: MCP Foundational Elements
**Status:** completed

*   **Task 5.1: Define MCP Data Models (Python using Pydantic) based on the Model Context Protocol specification**
    *   **Status:** completed
    *   The MCP Data Models are defined by directly importing robust Pydantic-based data models from `mcp.types`, ensuring full compliance with the protocol. This establishes the schema for how model information is communicated within the hybrid system.
*   **Task 5.2: Basic MCP Server/Client Framework (abstract base classes)**
    *   **Status:** completed
    *   Develop abstract Python classes for `MCPServer` and `MCPClient` that define the core interface for MCP interactions.
    *   Implement placeholder methods for `connect`, `cleanup`, `list_tools`, `call_tool`, etc., to guide future implementations.
*   **Task 5.3: Configuration Management for MCP servers (using .env and mcp.json)**
    *   **Status:** completed
    *   Implement a `Config` class to load settings from environment variables (e.g., from `.env`) and a dedicated `mcp.json` file for MCP-specific configurations (e.g., server addresses, model mappings).
    *   Ensure secure handling of sensitive information.

### Phase 6: Document Management System
**Status:** completed

*   **Task 6.1: Document Storage & Retrieval (e.g., Elasticsearch Integration)**
    *   **Status:** completed
    *   **Note:** Implemented local-first with SQLite and Markdown conversion.
    *   Set up and integrate with a document storage solution (e.g., Elasticsearch).
    *   Implement `ElasticsearchManager` for document indexing and retrieval.
*   **Task 6.2: Document Scanner & Parser:**
    *   **Status:** completed
    *   Develop `scan_documents()` functionality to ingest documents from various sources.
    *   Implement parsers for different document types.
*   **Task 6.3: Document Analysis Framework:**
    *   **Status:** completed
    *   Implement `analyze_documents()` to process document content.
    *   Develop `VectorDocument` structure for documents with embeddings (to be populated by LLM phase).

### Phase 7: Distributed MCP Server Development
**Status:** completed

*   **Task 7.1: Cloud-Neutral MCP Server for Generic Services**
    *   **Status:** completed
    *   **Note:** Implemented with `SystemUtilityServer` providing sandboxed file operations.
    *   Develop an MCP server to expose capabilities for generic distributed services, not tied to a specific cloud provider.
*   **Task 7.2: Cloud-Specific MCP Server Examples (e.g., AWS, Azure, GCP)**
     *   **Status:** completed
     *   **Type:** build
     *   **Note:** Built `ollama_cloud_server.py` — wraps 5 free Ollama cloud models (gpt-oss:120b, gpt-oss:20b, gemma3:12b, ministral-3:8b, rnj-1:8b) as MCP tools (`ollama_chat`, `ollama_list_models`). Registered in dummy MCP config as `ollama_cloud` server.
*   **Task 7.3: osenv → MCP Bridge (Cross-Project Integration)**
    *   **Status:** completed
    *   **Note:** Implemented `osenv_server.py` wrapping Workspace osenv modules (audit, media, understand, kb) as MCP tools via FastMCP. Uses `sys.path.insert` for cross-project import — no pip install needed. Registered in dummy MCP config as `osenv_manager` server.

### Phase 8: Interactive Rules/Game Integration
**Status:** completed

*   **Task 8.1: Implement Lateral Thinking Puzzle/Turtle Soup Game Rules**
    *   **Status:** completed
    *   Develop `rules()` and `rules_solver()` functions to define the game mechanics.
    *   Focus on managing game state and player interactions (e.g., yes/no/irrelevant questions).

### Phase 9: Hybrid LLM/MCP Orchestration & Refinement
**Status:** completed

*   **Task 9.1: Hybrid LLM Orchestrator**
    *   **Status:** completed
    *   Create a central `LLMOrchestrator` class responsible for intelligently routing requests between local and provider LLMs, applying boosting/optimization strategies.
    *   Manage parallel execution and selection criteria based on performance, cost, and specific task requirements.
*   **Task 9.2: MCP Registry/Discovery**
    *   **Status:** completed
    *   Implement a mechanism for the orchestration layer to discover and register all available MCP servers (local and provider-based).
*   **Task 9.3: Cooperative Strategy Implementation**
     *   **Status:** completed
     *   **Type:** plan+build
     *   **Note:** Built `cooperative_strategy.py` with 4 composable patterns (ParallelStrategy, ChainStrategy, FallbackStrategy, RouterStrategy). Integrated into `LLMOrchestrator` via `execute_strategy()`, `chain_tool_calls()`, `parallel_tool_calls()` methods. 15 unit tests pass.

### Phase 10: Testing & Optimization
**Status:** completed

*   **Task 10.1: Write Comprehensive Unit Tests**
     *   **Status:** completed
     *   **Type:** build
     *   **Note:** 15 unit tests for cooperative strategy (parallel, chain, fallback, router) — all passing.
*   **Task 10.2: Develop Integration Tests**
     *   **Status:** completed
     *   **Type:** build
     *   **Note:** 7 integration tests: MCP stdio protocol (list tools, chat with mini model, chat with default model, list models) + strategy integration (parallel, chain, fallback with real I/O). Requires OLLAMA_API_KEY. All passing.
*   **Task 10.3: Perform Performance Benchmarking**
    *   **Status:** completed
    *   Conduct benchmarking for all integrated components, with a focus on hybrid LLM performance.
*   **Task 10.4: Improve Error Handling & Robustness**
    *   **Status:** completed
    *   Enhance error handling mechanisms, logging, and implement strategies to ensure the system's robustness and graceful degradation under various failure scenarios.

### Phase 11: Workflow Unification & Automation
**Status:** completed

*   **Task 11.1: Design Unified Backup Orchestration (Pre-edit & Periodic Snapshots)**
    *   **Status:** completed
    *   **Type:** plan
    *   **Completed:** Designed orchestration of `pre_edit_backup.sh` + `simple_backup.sh` via `orchestrated_backup.sh`.
*   **Task 11.2: Implement Unified Backup Script (orchestrated_backup.sh)**
    *   **Status:** completed
    *   **Type:** build
    *   **Completed:** Created `orchestrated_backup.sh` with `pre <file>` and full-backup modes.
*   **Task 11.3: Integrate Unified Backup into workspace_sync.sh**
    *   **Status:** completed
    *   **Type:** build
    *   **Completed:** Added orchestrated backup call at the start of `workspace_sync.sh`.
*   **Task 11.4: Refine CHANGELOG.md generation in workspace_sync.sh (PR-based)**
    *   **Status:** completed
    *   **Type:** build
    *   **Completed:** Created `workspace-automation/src/generate_changelog.sh` — generates changelog from merged PRs using `gh` CLI.
*   **Task 11.5: Update GEMINI.md to describe the unified workflow**
    *   **Status:** completed
    *   **Type:** plan
    *   **Note:** GEMINI.md updated to cover unified project management, backup strategy, and change tracking.
*   **Task 11.6: Implement Agent Operation Logging**
    *   **Status:** completed
    *   **Type:** build
    *   **Note:** `AGENT_LOG.md` in `.opencode/` tracks all sessions with structured entries. Agent activity is recorded in `AGENT_LOG.md` with per-session entries.

### Phase 19: Hugging Face Hub CLI

**Status:** completed

**Stack:** Python (uv) + cURL + bash

**📋 Prepare — complete before starting:**
- [x] **🔑 Env:** HF_TOKEN in ENV/.env (generate at huggingface.co/settings/tokens)
- [x] **📁 Space:** Create `~/Public/hf/` cache dir
- [x] **📐 Design:** Confirm scope (download small models/tokenizers only — 3.7GB RAM limit)

**✅ Post — complete after finishing:**
- [ ] **🏷 Tag:** Git tag `anchor-YYYYMMDD` across touched repos
- [ ] **📝 Log:** Update AGENT_LOG.md with deliverables
- [ ] **📋 Plan:** Mark Phase 19 complete
- [ ] **📊 Dash:** Update DASHBOARD.md
- [ ] **🗳 Vote:** Re-run vote
- [ ] **🔍 Scan:** Run auto-scan to verify no regressions
- [ ] **📚 KB:** Rebuild KB

Integrate Hugging Face Hub APIs — search models/datasets, download, push. No GPU needed; uses HF REST API. CLI-first with workspace.sh commands.

**Why:** HF Hub is the largest model/dataset repo (1M+). Currently we have no CLI to search or download models. Every ML workflow starts with "find model → download → run." Building this avoids manual browser navigation and enables scripted model discovery.

**Why this approach:** Python + cURL avoids adding heavy SDKs. HF's REST API is simple (few endpoints). We skip the full `huggingface_hub` SDK to keep the dependency footprint minimal — just `requests` or raw cURL.

**⏱ Estimated total: ~1.5h**

**⚠ Criticism:** HF_TOKEN is a manual step (sign up at huggingface.co → generate token). Rate limits on free tier (60 req/hr for unauthenticated, higher with token). Large models (6B+ params) are impractical to download on this machine (3.7GB RAM, no GPU) — this tool is primarily for small models/tokenizers/datasets. The CLI adds value only if you regularly interact with HF Hub; for one-off usage, the browser is faster.

**💬 Discussion — Alternatives considered:**
| Option | Pros | Cons |
|--------|------|------|
| `huggingface_hub` SDK (Python) | Full feature set, caching built-in | Heavy dependency (20+ deps), complex API |
| Raw cURL scripts | Zero deps, simple | No resume logic, no structured output |
| **This approach (Python + requests)** | Lightweight, resume support, structured JSON | Need to implement caching ourselves |

The SDK was rejected to keep the dependency footprint minimal. cURL alone lacks structured error handling. Python strikes the right balance.

| Task | Status | Type | ⏱ |
|------|--------|------|----|
| 19.1 HF API client — search models/datasets, list files | ✅ Complete | build | 20min |
| 19.2 Download model — snapshot, resume, cache | ✅ Complete | build | 30min |
| 19.3 Push dataset/model — auth, upload, version | ✅ Complete | build | 20min |
| 19.4 workspace.sh commands (hf-search, hf-dl, hf-push) | ✅ Complete | build | 15min |

**Dependency chain:** `19.1 → 19.2 → 19.3 → 19.4`

### Phase 20: GitHub Automation

**Status:** completed

**Stack:** bash + gh CLI + GitHub Actions

**📋 Prepare — complete before starting:**
- [x] **Design:** Map local repos → GitHub names (project/ → `suniltnngl-gm/mcp`, etc.)
- [x] **Design:** Set severity threshold (which findings become issues)
- [x] **Design:** Define dedup strategy (use `finding_id` as issue body anchor)
- [x] **Design:** Define label schema (severity + category labels)
- [x] **Tool:** gh CLI authenticated ✅ (already done)
- [x] **Tool:** GitHub Issues enabled on target repos (mcp, workspace, etc.)
- [x] **🔑 Env:** GH_TOKEN or gh auth token available

**✅ Post — complete after finishing:**
- [x] **Tag:** Git tag `anchor-YYYYMMDD` across touched repos
- [x] **Log:** Update AGENT_LOG.md with deliverables
- [x] **Plan:** Mark Phase 20 complete in PLAN.md
- [x] **Dash:** Update DASHBOARD.md progress
- [x] **Vote:** Re-run vote — Phase 21 may gain weight
- [x] **Scan:** Run auto-scan to verify issue creation works
- [x] **KB:** Rebuild KB: `workspace.sh kb-auto scan`

Extend existing review_cycle autofix pipeline: auto-create issues from scan findings, auto-label PRs, manage releases via `gh` CLI.

**Why:** Review_cycle already generates findings. Turning findings into GitHub Issues creates a persistent audit trail. Auto-labeling PRs by changed paths surfaces risk areas (e.g., "touches auth → needs security review"). Release automation eliminates manual tag/changelog busiwork.

**Why this approach:** gh CLI is already authenticated. We extend existing review_cycle code rather than adding a new service. GitHub Actions for labeling (cheap, event-driven) vs. a daemon.

**⏱ Estimated total: ~1h**

**⚠ Criticism:** Issue creation from every finding can generate noise — needs dedup logic. PR labeling by path only works if PRs touch predictable paths. `gh` CLI rate limits apply (5000 req/hr for authenticated users). If the scan runs hourly and finds 10 issues each time, that's 240 issues/day — useless. Dedup and severity thresholds are essential.

**💬 Discussion — Alternatives considered:**
| Option | Pros | Cons |
|--------|------|------|
| GitHub API via Python (requests) | Full control, batch operations | Need token management, pagination logic |
| **gh CLI** | Already authenticated, simple subprocess | Slower (spawns process per call), less flexible |
| Webhook server (listen for events) | Real-time, event-driven | Need to host a server, more complex |

gh CLI was chosen because it's already authenticated and requires zero setup. If we hit rate limits or need batch operations, we can migrate to the API.

| Task | Status | Type | ⏱ |
|------|--------|------|----|
| 20.1 Auto-issue creator — scan findings → GitHub Issues | ✅ Complete | build | 25min |
| 20.2 Auto-PR labeler — label PRs by changed paths | ✅ Complete | build | 20min |
| 20.3 Release manager — tag, changelog, GitHub release | ✅ Complete | build | 20min |

**Dependency chain:** `20.1 → 20.2 → 20.3`

### Phase 21: Web Dashboard

**Status:** pending

**Stack:** Node.js (fnm) + Vercel (frontend) + Supabase (DB + Auth) + Python (uv) / FastAPI (backend API)

**📋 Prepare — complete before starting:**
- [ ] **🔑 Env:** SUPABASE_URL in ENV/.env
- [ ] **🔑 Env:** SUPABASE_ANON_KEY in ENV/.env
- [ ] **🛠 Tool:** Node.js via fnm (v24) ✅ (already done)
- [ ] **🛠 Tool:** Vercel CLI installed (`npm i -g vercel`)
- [ ] **🛠 Tool:** `vercel --login` done
- [ ] **📐 Design:** Dashboard wireframe — which cards, what data sources
- [ ] **📁 Space:** Choose location (`~/Public/dashboard/` or inside project/)

**✅ Post — complete after finishing:**
- [ ] **🏷 Tag:** Git tag `anchor-YYYYMMDD` across touched repos
- [ ] **📝 Log:** Update AGENT_LOG.md
- [ ] **📋 Plan:** Mark Phase 21 complete
- [ ] **📊 Dash:** Update DASHBOARD.md
- [ ] **🗳 Vote:** Re-run vote
- [ ] **🔍 Scan:** Run scan — verify health endpoint works
- [ ] **📚 KB:** Rebuild KB
- [ ] **🚀 Deploy:** Push to Vercel production

Lightweight web UI for workspace health, scan results, logs. Supabase for persistence + auth, Vercel for frontend hosting.

**Why:** Currently health is text in DASHBOARD.md. A web dashboard makes it glanceable: live health score, finding trends, next priority card, logs timeline. Supabase gives us free PostgreSQL (500MB) + auth — we skip writing a DB layer. Vercel gives free hosting + preview deploys per git push.

**Why this approach:** Supabase replaces building our own auth + DB (would take days). Vercel replaces managing a server. FastAPI backend is minimal — a few endpoints that read review_cycle output. Dashboard is a Next.js static export (no server runtime).

**⏱ Estimated total: ~2h**

**⚠ Criticism:** Dashboard is "nice to have" not "need to have" — the existing DASHBOARD.md + `./workspace.sh dashboard` already works. Adding a full web stack (FastAPI + Next.js + Supabase + Vercel) is significant maintenance surface for a read-only display. Supabase free tier is 500MB, 2 projects — if we ever need more, it's $25/mo. Vercel free tier: 100GB bandwidth, 6000 build minutes/mo — sufficient for now but not infinite.

**💬 Discussion — Alternatives considered:**
| Option | Pros | Cons |
|--------|------|------|
| Static HTML + JS (no framework) | Zero deps, CDN-hosted | Manual state management, no SSR |
| Python Flask + Jinja templates | Simple, server-rendered | No real-time updates, no SPA feel |
| **Next.js + Vercel** | Auto-deploy, SSR, React ecosystem | Heavier build step, Node.js dependency |
| Grafana + Prometheus | Already exists for metrics | Overkill for our scale, complex setup |

Next.js + Vercel was chosen because it gives us auto-deploy on git push (zero config) and preview URLs per branch. The health endpoint stays in Python (our stack). If the dashboard proves low-value, it can be retired independently — the FastAPI endpoint is useful standalone.

| Task | Status | Type | ⏱ |
|------|--------|------|----|
| 21.1 Health endpoint — FastAPI JSON API from review_cycle + autokb | ⏳ Pending | build | 30min |
| 21.2 Dashboard UI — Next.js cards for health, findings, logs, priority | ⏳ Pending | build | 1h |
| 21.3 Auto-refresh + deploy — cron update + vercel deploy | ⏳ Pending | build | 20min |

### Phase 22: Cloud Storage Sync

**Status:** pending

**Stack:** bash + cURL + existing dropbox-utils + rclone

**📋 Prepare — complete before starting:**
- [ ] **🛠 Tool:** rclone installed (`sudo apt install rclone`)
- [ ] **🛠 Tool:** rclone config for Dropbox or S3
- [ ] **🔑 Env:** DROPBOX_ACCESS_TOKEN in ENV/.env ✅ (already done)
- [ ] **📐 Design:** Decide what to sync (backups/, snapshots/, kb/)
- [ ] **📐 Design:** Choose schedule (daily cron? post-scan hook?)

**✅ Post — complete after finishing:**
- [ ] **🏷 Tag:** Git tag `anchor-YYYYMMDD`
- [ ] **📝 Log:** Update AGENT_LOG.md
- [ ] **📋 Plan:** Mark Phase 22 complete
- [ ] **📊 Dash:** Update DASHBOARD.md
- [ ] **🗳 Vote:** Re-run vote
- [ ] **✅ Verify:** Test restore from cloud backup
- [ ] **📚 KB:** Rebuild KB

Sync workspace backups, snapshots, and KB to Dropbox, S3-compatible, or Google Drive.

**Why:** We already have DROPBOX_ACCESS_TOKEN and dropbox-utils in repositories/. Currently backups sit on local disk — no offsite copy. A fire/laptop failure loses everything. Cloud sync is cheap insurance.

**Why this approach:** rclone handles S3/GDrive/Dropbox with a single config — we don't implement file transfer. Dropbox uses existing token (already works). For S3, rclone avoids adding boto3 (heavy). Cron for scheduling keeps it simple — no daemon needed.

**⏱ Estimated total: ~1h**

**⚠ Criticism:** Backup is only as good as its restore process — untested restores are false security. Dropbox free tier is 2GB which fills quickly with model files. rclone needs manual auth setup (OAuth flow). S3 costs money (even minimal usage is ~$1-2/mo). Local backups to a second disk would be simpler and faster — cloud sync only helps if the machine itself is lost.

**💬 Discussion — Alternatives considered:**
| Option | Pros | Cons |
|--------|------|------|
| Local USB/external disk backup | Fast, simple, no cloud costs | Not offsite, requires physical access |
| **rclone + Dropbox** | Existing token, already partially set up | 2GB free limit, slow for large files |
| restic (encrypted backup) | Built-in encryption, dedup, S3/Wasabi | New tool to learn, more complex |
| boto3 (direct S3) | Full AWS control | Heavy dependency, AWS free tier expires |

rclone + Dropbox is the fastest path to offsite backup (existing token). If we need more space, rclone can switch to Wasabi (S3-compatible, $6/TB/mo) with a config change — no code change.

| Task | Status | Type | ⏱ |
|------|--------|------|----|
| 22.1 Dropbox sync — extend existing dropbox-utils with cron trigger | ⏳ Pending | build | 25min |
| 22.2 S3-compatible backup — rclone config + bash wrapper | ⏳ Pending | build | 30min |
| 22.3 Schedule + restore — cron sync, integrity verify script | ⏳ Pending | build | 15min |

### Phase 23: Deploy Apps

**Status:** pending

**Stack:** Python (uv) + Node.js (fnm) + Docker + Render (backend APIs) + Vercel (frontend)

**📋 Prepare — complete before starting:**
- [ ] **🛠 Tool:** Docker installed (`docker --version`)
- [ ] **🛠 Tool:** Vercel CLI (from Phase 21) ✅ (assuming Phase 21 is done)
- [ ] **🔑 Env:** RENDER_API_KEY in ENV/.env (optional)
- [ ] **📐 Design:** Which services deploy (health API, dashboard, both?)
- [ ] **📐 Design:** Dockerfile for Python health endpoint

**✅ Post — complete after finishing:**
- [ ] **🏷 Tag:** Git tag `anchor-YYYYMMDD`
- [ ] **📝 Log:** Update AGENT_LOG.md
- [ ] **📋 Plan:** Mark Phase 23 complete
- [ ] **📊 Dash:** Update DASHBOARD.md
- [ ] **🗳 Vote:** Re-run vote — Phases 26-27 next
- [ ] **✅ Verify:** Test cold-start on Render
- [ ] **📚 KB:** Rebuild KB

One-command deploy to Render or Vercel. Auto-deploy on git push.

**Why:** Currently nothing is deployed — no staging, no production URL. Deploying gives us shareable preview links, discovers deployment bugs early, and makes demos possible. Vercel handles frontend (free, instant rollback), Render handles backend APIs (free tier, auto-spindown after 15min idle).

**Why this approach:** Dockerfile + render.yaml is the standard Render blueprint — minimal config. Vercel auto-deploys from git (no config needed). No need for Kubernetes or complex CD — our scale is 1-2 services. gh action CI already exists, just needs deploy step.

**⏱ Estimated total: ~45min**

**⚠ Criticism:** Render free tier spins down web services after 15 minutes of inactivity — first request after idle takes 30+ seconds (cold start). No custom domain on free tier (`.onrender.com` subdomain). Free PostgreSQL on Render is limited to 256MB. If the dashboard or API gets real usage, we'll need to upgrade ($7-19/mo). Vercel free tier is more generous (100GB bandwidth) but serverless functions have 10s timeout — too short for model inference.

**💬 Discussion — Alternatives considered:**
| Option | Pros | Cons |
|--------|------|------|
| **Render (backend) + Vercel (frontend)** | Auto-deploy from git, free tiers exist | Cold starts, no custom domain on free |
| Fly.io | Always-on low-power VMs ($1.68/mo minimum) | Credit card required, more config |
| Cloudflare Pages + Workers | 100k req/day free, global CDN | Workers have 30ms CPU time limit per request |
| Railway | Similar to Render, generous free tier | Newer platform, smaller community |

Render + Vercel split was chosen because each does one thing well: Render for persistent backend services (Python), Vercel for static frontends (Next.js). Migrating either to a different provider is independent of the other.

| Task | Status | Type | ⏱ |
|------|--------|------|----|
| 23.1 Deploy blueprint — Dockerfile + render.yaml | ⏳ Pending | plan+build | 30min |
| 23.2 Auto-deploy on push — GitHub Action + workspace.sh deploy cmd | ⏳ Pending | build | 15min |