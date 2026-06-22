# Contributing Guidelines

This project is an LLM-Enhanced Distributed MCP Servers workspace under `suniltnngl-gm/mcp`. By following these guidelines, you help maintain code quality, consistency, and a smooth development workflow.

## How to Contribute

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/suniltnngl-gm/mcp.git
    cd mcp
    ```
2.  **Set Up Your Environment:**
    ```bash
    uv sync              # Install Python deps
    pre-commit install   # Install lint hooks
    ```
3.  **Create a New Branch:** Use a descriptive name (e.g., `feature/doc-manager`, `fix/auth-timing`).
    ```bash
    git checkout -b feature/your-feature-name
    ```
4.  **Make Your Changes:**
    *   Adhere to the project's coding style and conventions (refer to `CHECKLIST_DEVELOPMENT.md`).
    *   Write clear, concise code. Run the auto pipeline before committing.
    *   Add tests for new functionality or bug fixes.
    *   Ensure all existing tests pass (`uv run pytest .`).
    *   Run linting (`uv run ruff check . --fix`).
5.  **Write Meaningful Commit Messages:** Follow the Conventional Commits specification (detailed below).
6.  **Push Your Branch:**
    ```bash
    git push origin feature/your-feature-name
    ```
7.  **Create a Pull Request:**
    *   Go to the original `suniltnngl-gm/mcp` repository on GitHub.
    *   Open a new Pull Request from your branch to the `main` branch.
    *   Fill out the Pull Request template (refer to `.github/PULL_REQUEST_TEMPLATE.md`).
    *   Ensure all CI checks pass.
    *   Address any feedback from reviewers.

## Workspace Automation

This project integrates with `~/Public/workspace.sh` for automation:

- `./workspace.sh review` — run review cycle (git, tests, tasks)
- `./workspace.sh auto` — detect gaps, fix trivial issues, rebuild KB
- `./workspace.sh auto --apply` — apply auto-fixes
- `./workspace.sh ai ask <q>` — ask Ollama cloud AI for help
- `./workspace.sh brain learn <task> <fix>` — log a correction as a lesson

All commits should go through the standard cycle: review → auto → fix → commit.

## Conventional Commits

We follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification.

A commit message should be structured as follows:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Type

*   **`feat`**: A new feature
*   **`fix`**: A bug fix
*   **`docs`**: Documentation only changes
*   **`style`**: Changes that do not affect the meaning of the code
*   **`refactor`**: A code change that neither fixes a bug nor adds a feature
*   **`perf`**: A code change that improves performance
*   **`test`**: Adding missing tests or correcting existing tests
*   **`build`**: Changes that affect the build system or external dependencies
*   **`ci`**: Changes to CI configuration files and scripts
*   **`chore`**: Other changes that don't modify src or test files
*   **`revert`**: Reverts a previous commit

### Scope (Optional)

Provides additional contextual information (e.g., `feat(auth)`, `fix(parser)`).

### Description

Use the imperative mood ("add", "fix") not past tense ("added", "fixed").

### Examples

- `feat(auth): add Firebase token verification middleware`
- `fix(parser): handle null input in topic extractor`
- `docs: update CONTRIBUTING.md with workspace automation guide`
- `chore(deps): update ollama-sdk to v0.6.2`

## Security Issue Notifications

If you discover a security vulnerability, report it privately by opening a GitHub Security Advisory on the `suniltnngl-gm/mcp` repository instead of opening a public issue.

## File Editing and Backup Workflow

Before editing a crucial file, create a timestamped snapshot:

```bash
./pre_edit_backup.sh <path/to/file>
```

This creates a copy in `backups/pre_edit_snapshots/` as a local safety net beyond Git history.
