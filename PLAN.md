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

Work done across all 8 active repos (tracked in `~/.opencode/`):

- **Consolidated 17→8 repos**: Archived 9 stale/empty repos
- **Git config unified**: All repos → `suniltnngl-gm`
- **Branch standardization**: `master` → `main` in next-steps & shared-tools
- **CI/CD added**: Workspace CI (shellcheck + firebase-app build), firebase-app CI
- **Dependabot**: Enabled on workspace, coding-agent, dropbox-utils, next-steps, shared-tools
- **READMEs**: Added to workspace, firebase-app, dropbox-utils
- **Test skeletons**: Vitest setup for firebase-app, test docs for workspace
- **next-step integration**: Added to ENTRY.md workflow, workspace.sh ns commands
- **Dropbox SDK**: v12.0.2 installed, API working (needs scope fix for file listing)
- **Ollama SDK**: v0.6.2 installed, cloud API at `https://ollama.com` (key in `ENV/.env`)
- **TODOs resolved**: 3 in project/ (dynamic commit msg, MCP config loading, .gitignore parsing)

## Detailed Plan & Todo List

The following tasks are organized into phases, reflecting the detailed steps required to achieve the project goal.

### Progress Summary

| Phase | Status | Tasks Done | Tasks Pending | Type Mix |
|-------|--------|------------|---------------|----------|
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
| 12. Cross-Project Integrations | 🔄 | 4/5 | 1 (#5) | build |
| 13. Automated Review Cycle | 🔄 | 0/5 | 5 | build |
| 14. Automated Knowledge Base | 🔄 | 4/5 | 1 | build |
| 15. Auto Gap-Find & Fix Pipeline | 🔄 | 5/5 | — | build |

**Task type legend:**
- `plan` — Design, research, architecture. Output: specs, diagrams, decision docs.
- `build` — Code, implement, test. Output: working code, passing tests.
- `plan+build` — Both design and implementation in one task.

Phases 1–11 complete. Phase 12 — 4/5 done. Phase 13 — 13.1 done. Phase 14 — 14.1–14.4 done. Phase 15 — all 5 tasks done.

### Phase 12: Cross-Project Integrations

**Status:** in progress

| # | Integration | Status | Blocked By | Blocks |
|---|-------------|--------|------------|--------|
| 1 | osenv → MCP Bridge | ✅ Completed | — | #2 |
| 2 | Antigravity Agent → MCP | ✅ Completed | #1 | — |
| 3 | Firebase Auth as MCP Identity | ✅ Completed | — | #5 |
| 4 | Shared Tools & Configs | ✅ Completed | — | — |
| 5 | Data Sharing (Firestore) | ⏳ Pending | — | — |

**Dependency chain:** `#3 → #5` (tools & configs #4 independent). #3 complete — #5 unblocked.

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
- **Note:** Created `~/.opencode/shared/` with canonical pyproject.toml, .editorconfig, .pre-commit-config.yaml, python-ci.yml, shellcheck.yml. Wired into project/ (updated CI, added pre-commit), Workspace/ (added .editorconfig), repositories/ (added pyproject.toml, .editorconfig, CI).

#### Task 12.5: Data Sharing (Firestore)
- **Status:** pending
- **Type:** build
- **Unblocked** by #3 completion.
- Replace local SQLite in MCP doc manager with Firestore-backed document service for real-time sync + auth across projects.

### Phase 13: Automated Review Cycle

**Status:** in progress

Automated system that periodically reviews all active repos, plans next actions, and optionally builds suggestions. See `REVIEW_CYCLE_PLAN.md` for full design.

| Task | Status | Type |
|------|--------|------|
| 13.1 Foundation — scanners (git, tests, tasks) | 🔄 In progress | build |
| 13.2 Review Engine — scoring, baseline, reports | ⏳ Pending | plan+build |
| 13.3 Automation — cron workflow, watch mode, hooks | ⏳ Pending | build |
| 13.4 Auto-fix & PR — known patterns, approval gate | ⏳ Pending | build |
| 13.5 Scoring & Trends — health score, dashboard badge | ⏳ Pending | build |

**Dependency chain:** `13.1 → 13.2 → 13.3 → 13.4 → 13.5`

### Phase 14: Automated Knowledge Base

**Status:** in progress

Auto-discovering, cross-repo knowledge base that indexes all code and docs, providing ranked search results. See `autokb/` for implementation.

| Task | Status | Type |
|------|--------|------|
| 14.1 Indexer — scan all 8 repos, build inverted index | ✅ Completed | build |
| 14.2 Search — ranked results with fuzzy matching, --json, --fast | ✅ Completed | build |
| 14.3 Unify KB.md + osenv/kb.py + raw code into one query | ✅ Completed | build |
| 14.4 workspace.sh commands (kb-auto search/scan/stats) | ✅ Completed | build |
| 14.5 Auto-index on schedule (cron / git hook) | ⏳ Pending | build |

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