# Code Review Checklist

## General Checks

*   [ ] **Purpose & Scope:** Does the code implement the intended feature or fix correctly?
*   [ ] **Readability & Clarity:** Are names descriptive? Are comments explaining *why* (not *what*)?
*   [ ] **Adherence to Conventions:** Does the code follow `DESIGN_GUIDELINES.md` and project patterns?
*   [ ] **Type Annotations:** Are all function signatures typed? Does `mypy` pass?

## Functionality & Logic

*   [ ] **Correctness:** Does the code behave correctly under happy path, edge cases, and errors?
*   [ ] **MCP Error Contracts:** Do MCP server tools return JSON errors with `code`, `message`, `details`?
*   [ ] **Security:** Any injection flaws, data validation issues, or exposed credentials?
*   [ ] **Efficiency:** Any obvious performance bottlenecks?

## Testing

*   [ ] **Unit Tests:** Are new/modified tests present and passing?
*   [ ] **Coverage:** Do tests cover edge cases and error paths?
*   [ ] **Test Quality:** Are tests clear and maintainable?

## Documentation & Maintainability

*   [ ] **Docs Updated:** Are relevant `.md` files, KB entries, and inline docs updated?
*   [ ] **Changelog:** Is `CHANGELOG.md` updated for significant changes?
*   [ ] **Complexity:** Is cyclomatic complexity ≤ 15 per module?

## Before Approval

*   [ ] **Lint & Format:** `ruff check . --fix` and `ruff format . --check` pass.
*   [ ] **Tests:** `uv run pytest .` passes.
*   [ ] **No Unnecessary Changes:** No commented-out code, debug statements, or unrelated diffs.
*   [ ] **No Credentials:** No hardcoded secrets, keys, or tokens.
