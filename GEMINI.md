**GEMINI.md**

```markdown
# Project Overview

This directory contains the "LLM-Enhanced Distributed MCP Servers" project, a suite of specialized Model Context Protocol (MCP) servers designed to enhance Large Language Model (LLM) applications with cloud-neutral context. The project aims to improve the quality of AI-generated outputs by providing relevant documentation, best practices, and workflow automation capabilities across various cloud environments. It utilizes a client-server architecture where MCP clients (such as AI coding assistants and chatbots) connect to MCP servers to access distributed capabilities. The core technology is the open-source Model Context Protocol.

**Note:** While the project is designed to *enhance LLM applications*, direct LLM implementation within this project is planned for a future phase.

# Key Capabilities

Based on the provided code snippets and updated project scope, the project is designed to provide the following capabilities:

- **Document Management & Analysis:** Features for listing, scanning, and analyzing documents, including services for document operations (`document_service`), handling vector documents, and planned integration with LLMs (`get_llm()`, `get_search()`) and search engines (e.g., Elasticsearch).
- **Interactive Rules/Games:** Implements logic for "Lateral Thinking Puzzles" or "Turtle Soup" style games, with `rules()` and `rules_solver()` functions defining mechanics for interactive reasoning and knowledge exploration, often following human-like interaction guidelines.
- **Distributed MCP Servers:** Specialized servers for interacting with various distributed services, with examples for specific cloud providers (e.g., AWS DocumentDB, AWS Cloud Control API, etc.).
    - **Cloud-Neutral Service Integration:** Tools for integrating with generic distributed services.
    - **Cloud-Specific Examples:** Demonstrations for services like Amazon DocumentDB and Cloud Control API.

# Key Technologies

- **Model Context Protocol (MCP):** An open protocol for integrating LLM applications with external data sources and tools.
- **Cloud-Neutral Design:** Emphasizes architecture and implementation that avoids vendor lock-in.
- **Python:** Implied as the primary development language, with `uv` and `uvx` used for dependency management.
- **Elasticsearch (Planned):** Indicated integration with Elasticsearch for document indexing and search.

# Building and Running

The installation and setup process generally includes:

1. **Installing `uv`:** Obtain from Astral, as the package manager.  
   `uv python install 3.10`
2. **Installing Python:** Using `uv`.
3. **Configuring AWS Credentials:** Ensure access to required AWS services.
4. **Adding the server to your MCP client configuration:**  
   Specific instructions vary by client (Amazon Q Developer CLI, Kiro, Cline, Cursor, Windsurf, VS Code, Claude Code). Detailed configuration examples for various MCP clients (as displayed by `gh repo view`) typically involve creating a JSON configuration file (e.g., `~/.aws/amazonq/mcp.json`, `kiro_mcp_settings.json`, `.cursor/mcp.json`, etc.) with server definitions.

Individual server READMEs (located in `src/<server-name>/README.md`) provide additional installation requirements and configuration details.

# Development Conventions

- **Contributing:** Refer to `CONTRIBUTING.md` for guidelines on contributing to the project.
- **Adding New MCP Servers:** See `DEVELOPER_GUIDE.md` for guidance on adding new MCP servers to the library.
- **Design Guidelines:** Adherence to `DESIGN_GUIDELINES.md` is expected when developing new servers.
- **Security:** Information regarding security issue notifications is available in `CONTRIBUTING.md#security-issue-notifications`.

# AI Interaction

This `GEMINI.md` file is used by the AI agent to understand the project's structure, purpose, and conventions for tasks such as answering questions, implementing features, fixing bugs, and refactoring code. Please avoid manual edits to this file, as they may be overwritten during AI analysis and updates.

# Cross-Project Context

This project lives at `~/Public/project/` alongside sibling projects under `~/Public/`:

### Sibling: `~/Public/Workspace/`
- **Firebase web app** (Auth, Firestore, Hosting, FCM, Gemini 1.5 Flash, PWA)
- **os-env-manager** — CLI tool for system audit, media understanding, knowledge base (`python3 -m osenv`)
- **Antigravity agent** — autonomous AI agent with Firebase Admin SDK + GCP AI tools
- **Integration potential**: Wrap osenv modules as MCP servers; consume MCP servers as Antigravity tools; use Firebase Auth for MCP identity; use Firestore as distributed MCP data store

### Sibling: `~/Public/repositories/`
- Dropbox API file listing utility (simple Python script)
- **Integration potential**: None direct; useful as reference for Dropbox API patterns

### Shared Context
- **`~/Public/.opencode/guidelines.md`** — session start/end rituals, project landscape, known gotchas
- **`~/Public/.opencode/CROSS_PROJECT.md`** — detailed integration map between all projects
- **Global config** at `~/.config/opencode/opencode.jsonc` loads guidelines automatically

# Project Documentation

Below are links to key project-specific documentation:

- **[PLAN.md](PLAN.md):** Details the project plan, high-level roadmap, and current task list (to-dos) for the "Hybrid LLM System with MCP Orchestration" project.
- **[ERROR_REGISTRY.md](ERROR_REGISTRY.md):** Contains a registry of significant errors and issues encountered during development, including their context, resolution, and impact.
- **[CHANGELOG.md](CHANGELOG.md):** Documents the history of project evolution, including significant changes, new features, and bug fixes.
- **[CHECKLIST_DEVELOPMENT.md](CHECKLIST_DEVELOPMENT.md):** Outlines the standard steps for executing development tasks, ensuring consistency and quality.
- **[CHECKLIST_CODE_REVIEW.md](CHECKLIST_CODE_REVIEW.md):** Provides a structured approach for conducting code reviews to maintain code quality and adherence to best practices.
- **[CHECKLIST_PROJECT_GROWTH.md](CHECKLIST_PROJECT_GROWTH.md):** Offers guidelines for developing and maintaining the project with a focus on sustainable growth, scalability, and extensibility.

## Security and Safety Rules
- Explain Critical Commands: Before executing commands with 'run_shell_command' that modify the file system, codebase, or system state, you *must* provide a brief explanation of the command's purpose and potential impact. Prioritize user understanding and safety. You should not ask permission to use the tool; the user will be presented with a confirmation dialogue upon use (you do not need to tell them this).
- Security First: Always apply security best practices. Never introduce code that exposes, logs, or commits secrets, API keys, or other sensitive information.

## No-Pypass File Editing Enforcement

- **Agent's Commitment:** I will always execute `pre_edit_backup.sh` on any file I am about to modify using tools like `replace` or `write_file`. This action will be explicitly stated before the modification occurs.
- **User Reminder:** Before I perform any file modification, I will remind the user of the importance of using `pre_edit_backup.sh` for their manual edits, especially for crucial development files. This ensures a consistent "no-pypass" approach to file editing that is critical for error tracking and project history.

## Tool Usage
- Parallelism: Execute multiple independent tool calls in parallel when feasible (i.e., searching the codebase).
```