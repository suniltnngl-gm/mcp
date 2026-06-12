# Developer Guide

## Overview
This guide provides step-by-step instructions for adding new Model Context Protocol (MCP) servers to the project.

## Prerequisites
- Python 3.8+ installed
- `uv` for dependency management
- Basic understanding of MCP protocol

## Adding a New MCP Server

### 1. Directory Structure
Create a new directory under `src/llm_wrapper/mcp/servers/` with the following structure:

```
new_server/
├── __init__.py                    # Server initialization
├── server.py                       # Main server implementation
├── tools/                          # Server tools
│   ├── __init__.py
│   └── tool_name.py
└── README.md                      # Server documentation
```

### 2. Server Registration
Add your server to `src/llm_wrapper/mcp/server_factory.py`:

```python
def create_server(server_name):
    if server_name == "new_server":
        from servers.new_server.server import NewServer
        return NewServer()
    # ... existing servers
```

### 3. Tool Implementation
Implement tools as classes inheriting from `ToolBase`:

```python
from .base import ToolBase

class NewServerTool(ToolBase):
    def __init__(self):
        super().__init__(
            name="new_server_tool",
            description="A tool that does something useful",
            schema={
                "type": "object",
                "properties": {
                    "input": {"type": "string", "description": "Input parameter"}
                },
                "required": ["input"]
            }
        )
    
    async def execute(self, params):
        # Implement your tool logic here
        return {"result": f"Processed: {params['input']}"}
```

### 4. Update Configuration
Add your server configuration to `src/llm_wrapper/mcp/config.py`:

```python
SERVER_CONFIGS = {
    # ... existing servers
    "new_server": {
        "path": "servers.new_server",
        "enabled": True,
        "dependencies": ["requests", "pydantic"]
    }
}
```

### 5. Documentation
Create a `README.md` in your server directory:
- Explain what the server does
- Document all available tools
- Provide usage examples

### 6. Testing
Add unit tests in `tests/`:

```python
# tests/test_new_server.py
import pytest
from mcp.servers.new_server import NewServer

def test_server_initialization():
    server = NewServer()
    assert server.name == "new_server"
    
    # Test tools
    tools = server.get_tools()
    assert len(tools) > 0
    assert any(tool.name == "new_server_tool" for tool in tools)
```

### 7. CI/CD Integration
Update GitHub Actions workflow:
- Add your server to the test matrix
- Ensure dependencies are properly installed

## Best Practices

### 1. Error Handling
- Always handle exceptions gracefully
- Log errors using the structured logging system
- Return user-friendly error messages

### 2. Tool Design
- Make tools as granular as possible
- Use clear, descriptive names
- Include comprehensive parameter validation
- Add type hints and docstrings

### 3. Documentation
- Keep documentation in sync with code
- Use Markdown for readability
- Include examples and edge cases

### 4. Testing
- Write unit tests for all tool functions
- Add integration tests for server connectivity
- Use fixtures for test setup/teardown

### 5. Performance
- Implement proper caching where appropriate
- Use async/await for I/O operations
- Monitor resource usage

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all dependencies are listed in `pyproject.toml`
2. **Tool Registration**: Verify tool is properly registered in `tools/__init__.py`
3. **Configuration**: Check that server is listed in `SERVER_CONFIGS`

### Getting Help
- Check `ERROR_REGISTRY.md` for known issues
- Review `CONTRIBUTING.md` for contributing guidelines
- Consult `README.md` for project overview