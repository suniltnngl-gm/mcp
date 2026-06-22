# Design Guidelines

## Principles

- **Stateless middleware** — Auth and validation layers should be stateless where possible. State belongs in dedicated storage servers.
- **Small modules** — Each Python module should have a cyclomatic complexity ≤ 15. Split large functions.
- **Parseable errors** — All MCP servers return JSON error payloads with `code`, `message`, and `details` fields.
- **Type annotations** — All Python code must use type hints. Run `mypy` before committing.
- **Tests alongside code** — Every module should have a corresponding test file in `tests/`.

## Architecture Pattern

MCP servers follow a consistent pattern:

```
src/llm_wrapper/mcp/<name>_server.py
  ├── FastMCP server instance
  ├── Tool functions decorated with @server.tool()
  ├── Pydantic models for input/output
  └── Error handling returning JSON error contracts
```

Automation modules follow:

```
<module>/__init__.py    — Core logic + public API
<module>/__main__.py    — CLI entry point (argparse)
<module>/scanners/      — (optional) Pluggable scanners
<module>/fixers.py      — (optional) Auto-fix implementations
```

## Code Conventions

- **Line length**: 100 characters
- **Formatting**: `ruff format .`
- **Imports**: stdlib → third-party → local (alphabetical within groups)
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_CASE` for constants

Refer to `.opencode/shared/pyproject.toml` for exact tool configuration.

## MCP Server Design

- Each server owns a single domain (auth, docs, osenv, etc.)
- Use `FastMCP` from the `mcp` package
- Tools should return structured data (dicts), not raw strings
- Environment variables are preferred over config files; document required env vars

Refer to `PLAN.md` for architectural direction and `CHECKLIST_CODE_REVIEW.md` for review standards.
