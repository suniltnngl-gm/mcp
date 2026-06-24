# Google Antigravity SDK

Wires the Antigravity agent (`~/Public/Workspace/firebase-app/agent/`) to MCP servers in `~/Public/project/`.

## Quick Start

```python
from google.antigravity import Agent, LocalAgentConfig
from google.antigravity.types import McpStdioServer

config = LocalAgentConfig(
    mcp_servers=[McpStdioServer(
        name="ollama_cloud",
        command="uv",
        args=["run", "--with", "ollama", "python3", "-m",
              "src.llm_wrapper.mcp.ollama_cloud_server"],
    )],
)
async with Agent(config) as agent:
    response = await agent.chat("Use the available tools.")
    print(await response.text())
```

## Key Concepts

| Concept | Description |
|---------|-------------|
| `Agent` | High-level entry point (batteries-included) |
| `Conversation` | Stateful session with step history |
| `LocalConnectionStrategy` | Low-level adapter for transport |
| `MCP Stdio Server` | Wire external MCP servers as agent tools |

See full Antigravity docs at [google-antigravity on PyPI](https://pypi.org/project/google-antigravity/).
