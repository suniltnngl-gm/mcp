# Design Guidelines

## Overview
These design guidelines establish consistent patterns for developing new MCP servers and tools in the project.

## Project Philosophy

### 1. Provider-Agnostic Architecture
The system is designed to be cloud-neutral and provider-agnostic:
- Each service has pluggable backends
- Start with preferred implementation, easily swap to alternatives
- Configuration-driven backend selection

### 2. Tool-Based Interaction
All server capabilities are exposed through tools:
- Each tool has a single responsibility
- Tools are discoverable via standardized schema
- Tool execution follows async/await pattern

### 3. Configuration-First
Configuration drives behavior:
- YAML/JSON configuration files
- Environment variable overrides
- Schema validation for all configs

## Code Structure

### 1. Module Organization
```
src/
├── llm_wrapper/                    # Core framework
│   ├── __init__.py
│   ├── base.py                     # Base classes
│   ├── config.py                   # Configuration management
│   ├── router.py                   # Request routing
│   └── server_factory.py            # Server instantiation
│
├── llm_wrapper/                    # LLM integration
│   ├── __init__.py
│   ├── core/                       # Core LLM components
│   │   ├── client.py               # LLM client interface
│   │   ├── config.py               # LLM configuration
│   │   └── prompt.py               # Prompt templates
│   ├── llm/                        # LLM implementations
│   │   ├── __init__.py
│   │   ├── local_client.py         # Local LLM
│   │   └── provider_client.py      # Cloud providers
│   └── providers/                  # Provider implementations
│       ├── __init__.py
│       └── google.py               # Google Cloud provider
│
├── llm_wrapper/                    # MCP integration
│   ├── __init__.py
│   ├── client.py                   # MCP client
│   ├── interfaces.py               # MCP interfaces
│   ├── mcp/                        # MCP server implementations
│   │   ├── __init__.py
│   │   ├── server_base.py           # Base MCP server
│   │   ├── tools/                   # Tool implementations
│   │   └── server_factory.py        # Server factory
│   └── schema.py                   # MCP schema definitions
```

### 2. Tool Design Patterns

#### Tool Base Class
All tools inherit from `ToolBase`:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class ToolBase(ABC):
    def __init__(self, name, description, schema):
        self.name = name
        self.description = description
        self.schema = schema
    
    @abstractmethod
    async def execute(self, params):
        pass
    
    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "schema": self.schema
        }
```

#### Tool Schema Structure
Tool schemas should follow this pattern:

```python
{
    "type": "object",
    "properties": {
        "param1": {
            "type": "string",
            "description": "First parameter",
            "default": "default_value"
        },
        "param2": {
            "type": "integer",
            "description": "Second parameter",
            "minimum": 0,
            "maximum": 100
        }
    },
    "required": ["param1"],
    "optional": ["param2"]
}
```

### 3. Server Implementation Pattern

#### Server Base Class
MCP servers should implement this pattern:

```python
from .base import MCPServerBase

class MyServer(MCPServerBase):
    def __init__(self, config):
        super().__init__(config)
        self.name = "my_server"
    
    async def initialize(self):
        # Initialize resources
        pass
    
    async def cleanup(self):
        # Clean up resources
        pass
    
    async def get_tools(self):
        # Return list of available tools
        return [
            MyTool1(),
            MyTool2()
        ]
```

## Tool Design Guidelines

### 1. Naming Conventions
- Use snake_case for tool names
- Keep names concise but descriptive
- Avoid generic names like "tool", "action", "command"
- Follow pattern: `[domain]_[action]` or `[entity]_[operation]`

### 2. Documentation
Each tool should have:

#### Clear Description
- Concise 1-2 sentence explanation
- What the tool does
- When to use it

#### Parameter Documentation
- Each parameter with type and description
- Mark required vs optional parameters
- Provide examples where helpful

#### Return Value Documentation
- What the tool returns
- Structure of return value
- Possible error conditions

### 3. Error Handling

#### Error Categories
- **Validation Errors**: Invalid parameter values
- **Runtime Errors**: Tool-specific issues
- **System Errors**: Framework or resource problems

#### Error Response Format
```python
{
    "success": False,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid parameter value",
        "details": {
            "field": "param1",
            "issue": "Value must be greater than 0"
        }
    }
}
```

#### Successful Response Format
```python
{
    "success": True,
    "data": {
        "result": "Tool execution result",
        "metadata": {
            "timestamp": "2024-01-01T12:00:00Z",
            "execution_time_ms": 100
        }
    }
}
```

### 4. Performance Guidelines

#### Resource Management
- Use connection pooling for external services
- Implement proper timeout handling
- Cache expensive operations
- Clean up resources on error

#### Async Patterns
```python
async def execute(self, params):
    # Use async context managers
    async with self.db_connection() as conn:
        # Execute operations
        result = await conn.query("SELECT ...")
        return result
```

## Configuration Guidelines

### 1. Configuration Schema
All configuration should follow JSON Schema:

```json
{
    "type": "object",
    "properties": {
        "server": {
            "type": "object",
            "properties": {
                "host": {"type": "string", "default": "localhost"},
                "port": {"type": "integer", "default": 8080},
                "enabled": {"type": "boolean", "default": true}
            }
        }
    }
}
```

### 2. Environment Variables
Use consistent naming:
- `PREFIX_SETTING` for server-specific settings
- `ENV_` prefix for environment variables
- Underscore-separated words

```bash
# Example
MY_SERVER_HOST=localhost
MY_SERVER_PORT=8080
MY_SERVER_ENABLED=true
```

## Testing Guidelines

### 1. Unit Tests
- Test each tool in isolation
- Mock external dependencies
- Test parameter validation
- Test error handling

### 2. Integration Tests
- Test server initialization
- Test tool registration
- Test end-to-end scenarios
- Test error scenarios

### 3. Performance Tests
- Measure execution time
- Test with realistic data volumes
- Test under load

## Security Guidelines

### 1. Input Validation
- Validate all input parameters
- Use allowlists over denylists
- Sanitize user input

### 2. Authentication
- Use standardized authentication mechanisms
- Implement proper authorization checks
- Log authentication attempts

### 3. Data Protection
- Encrypt sensitive data
- Use secure storage for credentials
- Implement proper access controls

## Documentation Guidelines

### 1. Tool Documentation
```
# Tool Name

Description: Brief explanation of what the tool does.

Parameters:
- param1 (required): Description of first parameter
- param2 (optional): Description of second parameter

Returns:
- result: Description of the result

Examples:
```
# Example 1
Tool call with parameters...
Returns: Result...

# Example 2
Another example...
Returns: Another result...
```

## Continuous Integration

### 1. GitHub Actions
- Linting (`ruff`, `mypy`)
- Type checking
- Unit tests
- Integration tests
- Build validation

### 2. Code Quality
- Maintain 100% test coverage
- Follow PEP 8 style guide
- Use type hints
- Keep functions small and focused

## Future Considerations

### 1. Extensibility
- Design for easy plugin addition
- Use interfaces for loose coupling
- Support for configuration-driven behavior

### 2. Scalability
- Implement horizontal scaling support
- Design for load balancing
- Consider distributed deployment

### 3. Observability
- Add comprehensive logging
- Implement metrics collection
- Add tracing for distributed systems