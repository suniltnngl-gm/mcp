"""CLI helper to call a single MCP tool via LLMOrchestrator.

Usage:
    python3 workspace-automation/src/run_orchestrator_tool.py <tool_name> <arguments_json> <server_name>
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to sys.path so local imports work when this file is run directly.
# Assumes this script lives at workspace-automation/src/.
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.llm_wrapper.mcp.config import load_mcp_config
from src.llm_wrapper.orchestrator import LLMOrchestrator


async def run_tool_via_orchestrator(
    tool_name: str, arguments: Dict[str, Any], server_name: str
) -> bool:
    """
    Initialize LLMOrchestrator and invoke one tool on one MCP server.
    Returns True when the tool reports success, otherwise False.
    """
    # Load MCP configuration using the project's default discovery logic.
    mcp_config = load_mcp_config()
    if not mcp_config:
        print(
            "Error: Could not load MCP configuration for Orchestrator.", file=sys.stderr
        )
        return False

    # Provide fallback environment variables expected by MCP services.
    # setdefault() preserves externally supplied values.
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)
    os.environ.setdefault("DB_PATH", str(data_dir / "docs.db"))
    os.environ.setdefault("GAME_RULES_DB_PATH", str(data_dir / "game_rules.db"))
    llm_sandbox_root = Path("./llm_sandbox")
    llm_sandbox_root.mkdir(exist_ok=True)
    os.environ.setdefault("SANDBOX_ROOT", str(llm_sandbox_root))

    try:
        async with LLMOrchestrator(mcp_config) as orchestrator:
            print(
                f"Calling tool '{tool_name}' on server '{server_name}' via Orchestrator..."
            )
            result = await orchestrator._multi_client_manager.call_tool(
                tool_name, arguments, server_name
            )
            if result.success:
                print(f"Tool call successful: {result.content}")
                return True
            else:
                print(f"Tool call failed: {result.content}", file=sys.stderr)
                return False
    except Exception as e:
        print(
            f"Error calling tool '{tool_name}' via Orchestrator: {e}", file=sys.stderr
        )
        return False


if __name__ == "__main__":
    # Expected CLI: tool name, JSON arguments string, and server name.
    if len(sys.argv) < 4:
        print(
            "Usage: python3 run_orchestrator_tool.py <tool_name> <arguments_json> <server_name>",
            file=sys.stderr,
        )
        sys.exit(1)

    tool_name = sys.argv[1]
    arguments_json = sys.argv[2]
    server_name = sys.argv[3]

    try:
        arguments = json.loads(arguments_json)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON for arguments: {arguments_json}", file=sys.stderr)
        sys.exit(1)

    success = asyncio.run(run_tool_via_orchestrator(tool_name, arguments, server_name))
    sys.exit(0 if success else 1)
