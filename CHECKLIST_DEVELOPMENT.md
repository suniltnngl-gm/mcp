# Development Task Checklist

This checklist outlines the standard steps for executing any development task within this workspace.

## Phase 1: Understanding and Planning

*   [ ] **Understand the Request:** Clearly comprehend the objective and specific requirements.
*   [ ] **Contextual Analysis:**
    *   Investigate relevant codebase areas, existing files, dependencies, and project conventions.
    *   Search KB: `workspace.sh kb-auto <query>` or `workspace.sh kb-auto <query> --explain`
    *   Review PLAN.md for phase/task context.
*   [ ] **Formulate a Plan:** Outline a clear approach. Break complex tasks into subtasks.
*   [ ] **Identify Testing Strategy:** Plan for new tests or identify existing tests to run.

## Phase 2: Implementation

*   [ ] **Adhere to Conventions:** Follow existing style, formatting, naming, and architectural patterns. See `DESIGN_GUIDELINES.md`.
*   [ ] **Implement Changes:** Make modifications using appropriate tools.
*   [ ] **Run Auto Pipeline:**
    ```bash
    workspace.sh review           # Check current health
    workspace.sh auto plan        # See what would be auto-fixed
    workspace.sh brain learn <task> <fix>  # Log any corrections
    ```

## Phase 3: Verification

*   [ ] **Run Tests:** `uv run pytest .` or `uv run pytest tests/<module>/`
*   [ ] **Check Standards:**
    *   `uv run ruff check . --fix` — linting
    *   `uv run ruff format . --check` — formatting
*   [ ] **Review Changes:** Self-review all modifications for quality and completeness.
*   [ ] **Commit Changes:** Use Conventional Commits format (see `CONTRIBUTING.md`).

## Phase 4: Post-Completion

*   [ ] **Update Documents:** Update `PLAN.md`, `ERROR_REGISTRY.md`, `CHANGELOG.md` as appropriate.
*   [ ] **Rebuild KB:** `workspace.sh kb-auto scan`
*   [ ] **Sync Brain:** `workspace.sh brain sync`
*   [ ] **Confirm completion** and await further input.
