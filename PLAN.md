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

## Detailed Plan & Todo List

The following tasks are organized into phases, reflecting the detailed steps required to achieve the project goal.

### Phase 1: Foundational Setup & Project Structure
**Status:** pending

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
**Status:** in_progress

*   **Task 7.1: Cloud-Neutral MCP Server for Generic Services**
    *   **Status:** completed
    *   **Note:** Implemented with `SystemUtilityServer` providing sandboxed file operations.
    *   Develop an MCP server to expose capabilities for generic distributed services, not tied to a specific cloud provider.
*   **Task 7.2: Cloud-Specific MCP Server Examples (e.g., AWS, Azure, GCP)**
    *   **Status:** pending
    *   Develop example MCP servers for specific cloud services (e.g., AWS DocumentDB, Azure Cosmos DB, GCP Firestore), demonstrating cloud-neutral design principles.
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
**Status:** pending

*   **Task 9.1: Hybrid LLM Orchestrator**
    *   **Status:** completed
    *   Create a central `LLMOrchestrator` class responsible for intelligently routing requests between local and provider LLMs, applying boosting/optimization strategies.
    *   Manage parallel execution and selection criteria based on performance, cost, and specific task requirements.
*   **Task 9.2: MCP Registry/Discovery**
    *   **Status:** completed
    *   Implement a mechanism for the orchestration layer to discover and register all available MCP servers (local and provider-based).
*   **Task 9.3: Cooperative Strategy Implementation**
    *   **Status:** pending
    *   Define and implement strategies for "co-operative" behavior between LLMs and MCP servers, including chaining calls and parallel execution for enhanced capabilities.

### Phase 10: Testing & Optimization
**Status:** pending

*   **Task 10.1: Write Comprehensive Unit Tests**
    *   **Status:** pending
    *   Develop unit tests for each class and function across the system.
*   **Task 10.2: Develop Integration Tests**
    *   **Status:** pending
    *   Create integration tests to verify seamless interaction between components.
*   **Task 10.3: Perform Performance Benchmarking**
    *   **Status:** completed
    *   Conduct benchmarking for all integrated components, with a focus on hybrid LLM performance.
*   **Task 10.4: Improve Error Handling & Robustness**
    *   **Status:** completed
    *   Enhance error handling mechanisms, logging, and implement strategies to ensure the system's robustness and graceful degradation under various failure scenarios.

### Phase 11: Workflow Unification & Automation
**Status:** pending

*   **Task 11.1: Design Unified Backup Orchestration (Pre-edit & Periodic Snapshots)**
    *   **Status:** pending
    *   **Note:** Design the orchestration of both `pre_edit_backup.sh` for individual file snapshots and `simple_backup.sh` for periodic project snapshots, as an interim strategy towards a more comprehensive incremental backup.
*   **Task 11.2: Implement Unified Backup Script (orchestrated_backup.sh)**
    *   **Status:** pending
    *   **Note:** Implement a mechanism to orchestrate the use of `pre_edit_backup.sh` and `simple_backup.sh` as part of the unified backup strategy.
*   **Task 11.3: Integrate Unified Backup into workspace_sync.sh**
    *   **Status:** pending
    *   Ensure the unified backup mechanism is used strategically within `workspace_sync.sh` before significant modifications or commits.
*   **Task 11.4: Refine CHANGELOG.md generation in workspace_sync.sh (PR-based)**
    *   **Status:** in_progress
    *   **Note:** Implement `CHANGELOG.md` generation based on Pull Request information (e.g., merged PR titles and descriptions) rather than directly from individual commit messages. This likely involves configuring `git-changelog` or a similar tool to process PR metadata.
*   **Task 11.5: Update GEMINI.md to describe the unified workflow**
    *   **Status:** pending
    *   Add a section to `GEMINI.md` detailing the unified project management, backup strategy, and change tracking processes.
*   **Task 11.6: Implement Agent Operation Logging**
    *   **Status:** in_progress
    *   Develop a mechanism to systematically record significant actions, decisions, and their rationale (why, what, how, when) taken by the agent into a dedicated log (e.g., `AGENT_LOG.md` or as structured entries in `ERROR_REGISTRY.md`).