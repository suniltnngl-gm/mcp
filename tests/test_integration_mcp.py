"""Integration tests for MCP servers and cooperative strategies.

These tests require:
- OLLAMA_API_KEY environment variable set
- Network access to https://ollama.com
"""

import asyncio
import json
import os
import shutil
import subprocess
import sys

import pytest

from src.llm_wrapper.mcp.cooperative_strategy import (
    StrategyStep,
    StrategyResult,
    chain,
    fallback,
    parallel,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.skipif(
        not os.environ.get("OLLAMA_API_KEY"),
        reason="OLLAMA_API_KEY not set",
    ),
]

UV_PATH = os.path.expanduser("~/.local/bin/uv")
PROJECT_DIR = os.path.expanduser("~/Public/project")


class MCPStdioClient:
    """Minimal MCP stdio client for test purposes."""

    def __init__(self, server_module: str):
        self.proc: subprocess.Popen | None = None
        self.server_module = server_module

    async def start(self):
        self.proc = subprocess.Popen(
            [UV_PATH, "run", "--with", "ollama", "python3", "-m", self.server_module],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=PROJECT_DIR,
            env={
                "OLLAMA_API_KEY": os.environ["OLLAMA_API_KEY"],
                "PATH": f"{os.path.expanduser('~/.local/bin')}:/usr/bin:/bin",
                "HOME": os.path.expanduser("~"),
            },
        )
        await asyncio.sleep(3)
        # Initialize
        resp = await self._send({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "0.1.0",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1"},
            },
        })
        assert resp.get("result"), f"Init failed: {resp}"

    async def _send(self, msg: dict) -> dict:
        if not self.proc or not self.proc.stdin:
            raise RuntimeError("Server not running")
        req = json.dumps(msg) + "\n"
        self.proc.stdin.write(req.encode())
        self.proc.stdin.flush()
        line = await asyncio.get_event_loop().run_in_executor(
            None, self.proc.stdout.readline
        )
        return json.loads(line.decode())

    async def list_tools(self) -> list:
        resp = await self._send({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        })
        return resp.get("result", {}).get("tools", [])

    async def call_tool(self, name: str, arguments: dict) -> dict:
        resp = await self._send({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        })
        return resp.get("result", {})

    def stop(self):
        if self.proc:
            self.proc.terminate()
            self.proc.wait(timeout=5)


class TestOllamaCloudMCPIntegration:
    """Integration tests for the Ollama Cloud MCP server via stdio protocol."""

    async def _with_server(self, test_fn):
        client = MCPStdioClient("src.llm_wrapper.mcp.ollama_cloud_server")
        try:
            await client.start()
            return await test_fn(client)
        finally:
            client.stop()

    async def test_list_tools(self):
        async def _test(client):
            tools = await client.list_tools()
            tool_names = [t["name"] for t in tools]
            assert "ollama_chat" in tool_names
            assert "ollama_list_models" in tool_names
        await self._with_server(_test)

    async def test_ollama_chat_mini(self):
        async def _test(client):
            result = await client.call_tool("ollama_chat", {
                "model": "ministral-3:8b",
                "messages": '[{"role":"user","content":"Say hi in 2 words"}]',
            })
            content = result.get("content", [{}])[0].get("text", "")
            assert len(content) > 0
        await self._with_server(_test)

    async def test_ollama_chat_default_model(self):
        async def _test(client):
            result = await client.call_tool("ollama_chat", {
                "messages": '[{"role":"user","content":"Reply with just: OK"}]',
            })
            content = result.get("content", [{}])[0].get("text", "")
            assert len(content) > 0
        await self._with_server(_test)

    async def test_ollama_list_models(self):
        async def _test(client):
            result = await client.call_tool("ollama_list_models", {})
            content = result.get("content", [{}])[0].get("text", "")
            models = json.loads(content)
            assert isinstance(models, list)
            assert len(models) >= 5
        await self._with_server(_test)


class TestStrategiesWithRealActions:
    @pytest.mark.skipif(
        not shutil.which("ls"),
        reason="ls command required",
    )
    async def test_parallel_async_actions(self):
        async def read_file():
            return "file content"

        async def list_dir():
            return "dir content"

        steps = [
            StrategyStep("read", read_file),
            StrategyStep("ls", list_dir),
        ]
        result = await parallel(steps).execute()
        assert result.success
        assert len(result.data) == 2

    async def test_chain_with_sync_actions(self):
        """Chain strategy with simple async wrappers."""
        results = []

        async def step_a():
            results.append("a")
            return "a"

        async def step_b():
            results.append("b")
            return "b"

        strategy = chain([
            StrategyStep("a", step_a),
            StrategyStep("b", step_b),
        ])
        result = await strategy.execute()
        assert result.success
        assert results == ["a", "b"]

    async def test_fallback_strategy_real(self):
        """Fallback from a failing action to a working one."""
        async def fails():
            raise ValueError("fail")

        async def works():
            return "fallback_ok"

        strategy = fallback(
            StrategyStep("fail", fails),
            StrategyStep("works", works),
        )
        result = await strategy.execute()
        assert result.success
        assert result.metadata["used"] == "fallback"
        assert result.data == "fallback_ok"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
