"""MCP server that wraps the osenv CLI utility modules."""

import asyncio
import json
import os
import sys
from typing import List, Literal, Optional

# Add osenv to path (cross-project import)
_OSENV_PATH = os.path.expanduser("~/Public/Workspace/os-env-manager")
if _OSENV_PATH not in sys.path:
    sys.path.insert(0, _OSENV_PATH)

from mcp.server.fastmcp import FastMCP
from mcp.types import CallToolResult, TextContent
from pydantic import BaseModel, Field

# Import osenv modules
from osenv.audit import audit as run_audit
from osenv.media import review as run_media_review
from osenv.understand import understand as run_media_understand
from osenv.kb import add_entry as kb_add_entry
from osenv.kb import list_entries as kb_list_entries
from osenv.kb import search as kb_search
from osenv.kb import stats as kb_stats


class MediaReviewInput(BaseModel):
    directory_path: str = Field(
        ..., description="The absolute path to the directory containing media files to review."
    )


class MediaUnderstandInput(BaseModel):
    file_path: str = Field(
        ..., description="The absolute path to the video, audio, or image file to analyze."
    )
    backend: Literal["auto", "api", "local"] = Field(
        "auto", description="The transcription backend to use (auto, api, or local)."
    )
    vision: bool = Field(
        False, description="Whether to generate AI vision descriptions for images."
    )


class KbSearchInput(BaseModel):
    query: str = Field(
        ..., description="The query string to search for in keys, values, summaries, or tags."
    )


class KbListInput(BaseModel):
    tags: Optional[List[str]] = Field(
        None, description="Optional list of tags to filter knowledge base entries."
    )


class KbAddInput(BaseModel):
    key: str = Field(
        ..., description="The unique key identifier for the knowledge entry."
    )
    value: str = Field(
        ..., description="The value or content associated with the key."
    )
    source: str = Field(
        "user", description="The source of the knowledge (e.g., 'user', 'agent')."
    )
    tags: Optional[List[str]] = Field(
        None, description="Optional tags to categorize the entry."
    )
    summary: str = Field(
        "", description="A brief summary of the knowledge entry."
    )


class OsenvServer:
    """
    An MCP server wrapping the local Ubuntu Environment Manager (osenv) modules.
    Provides system audits, media analysis, OCR/transcription, and a persistent knowledge base.
    """

    def __init__(self):
        self.mcp_server = FastMCP(name="osenv_manager")
        
        # Register tools
        self.mcp_server.add_tool(
            self._osenv_audit_tool,
            name="osenv_audit",
            description="Performs a full Ubuntu system health & security audit (CPU, memory, updates, failed services, open ports).",
        )
        self.mcp_server.add_tool(
            self._osenv_media_review_tool,
            name="osenv_media_review",
            description="Scans and reviews metadata of media files (video, audio, images) in a directory.",
        )
        self.mcp_server.add_tool(
            self._osenv_media_understand_tool,
            name="osenv_media_understand",
            description="Transcribes audio/video speech to text, extracts image text via OCR, or describes images using AI vision.",
        )
        self.mcp_server.add_tool(
            self._osenv_kb_search_tool,
            name="osenv_kb_search",
            description="Searches the local persistent knowledge base for matching entries.",
        )
        self.mcp_server.add_tool(
            self._osenv_kb_list_tool,
            name="osenv_kb_list",
            description="Lists all entries in the persistent knowledge base, optionally filtered by tags.",
        )
        self.mcp_server.add_tool(
            self._osenv_kb_add_tool,
            name="osenv_kb_add",
            description="Saves a new key-value entry with optional tags and summary to the persistent knowledge base.",
        )

    async def _osenv_audit_tool(self) -> CallToolResult:
        """Runs the system health audit."""
        try:
            # Run the audit function in a thread pool since it runs shell commands
            loop = asyncio.get_running_loop()
            results = await loop.run_in_executor(None, run_audit)
            
            passed = sum(1 for r in results if r["status"] == "pass")
            warned = sum(1 for r in results if r["status"] == "warn")
            failed = sum(1 for r in results if r["status"] == "fail")
            
            summary = f"Audit complete: {passed} passed, {warned} warned, {failed} failed."
            return CallToolResult(
                content=[
                    TextContent(type="text", text=summary),
                    TextContent(type="text", text=json.dumps(results, indent=2))
                ]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error running system audit: {e}")],
                isError=True,
            )

    async def _osenv_media_review_tool(self, input: MediaReviewInput) -> CallToolResult:
        """Runs media scan and review."""
        try:
            loop = asyncio.get_running_loop()
            results = await loop.run_in_executor(None, run_media_review, input.directory_path)
            
            if "error" in results:
                return CallToolResult(
                    content=[TextContent(type="text", text=results["error"])],
                    isError=True
                )
                
            summary = (
                f"Reviewed media in '{input.directory_path}'. "
                f"Found {results['summary']['videos']} videos, {results['summary']['audio']} audio, "
                f"{results['summary']['images']} images."
            )
            return CallToolResult(
                content=[
                    TextContent(type="text", text=summary),
                    TextContent(type="text", text=json.dumps(results, indent=2))
                ]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error reviewing media directory: {e}")],
                isError=True,
            )

    async def _osenv_media_understand_tool(self, input: MediaUnderstandInput) -> CallToolResult:
        """Transcribes, performs OCR, or describes media files."""
        try:
            loop = asyncio.get_running_loop()
            # Run understand with quiet=True to avoid stdout pollution
            results = await loop.run_in_executor(
                None, 
                lambda: run_media_understand(
                    input.file_path, 
                    backend=input.backend, 
                    vision=input.vision, 
                    quiet=True
                )
            )
            
            if "error" in results:
                return CallToolResult(
                    content=[TextContent(type="text", text=results["error"])],
                    isError=True
                )
                
            return CallToolResult(
                content=[
                    TextContent(type="text", text=f"Successfully analyzed file: {results['file']}"),
                    TextContent(type="text", text=json.dumps(results, indent=2))
                ]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error analyzing media file: {e}")],
                isError=True,
            )

    async def _osenv_kb_search_tool(self, input: KbSearchInput) -> CallToolResult:
        """Searches persistent knowledge base."""
        try:
            results = kb_search(input.query)
            return CallToolResult(
                content=[
                    TextContent(type="text", text=f"Found {len(results)} matching knowledge base entries."),
                    TextContent(type="text", text=json.dumps(results, indent=2))
                ]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error searching knowledge base: {e}")],
                isError=True,
            )

    async def _osenv_kb_list_tool(self, input: KbListInput) -> CallToolResult:
        """Lists persistent knowledge base entries."""
        try:
            results = kb_list_entries(input.tags)
            return CallToolResult(
                content=[
                    TextContent(type="text", text=f"Retrieved {len(results)} knowledge base entries."),
                    TextContent(type="text", text=json.dumps(results, indent=2))
                ]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error listing knowledge base entries: {e}")],
                isError=True,
            )

    async def _osenv_kb_add_tool(self, input: KbAddInput) -> CallToolResult:
        """Adds a knowledge entry to the persistent knowledge base."""
        try:
            entry, action = kb_add_entry(
                key=input.key,
                value=input.value,
                source=input.source,
                tags=input.tags,
                summary=input.summary,
            )
            return CallToolResult(
                content=[
                    TextContent(type="text", text=f"Successfully {action} entry '{input.key}'."),
                    TextContent(type="text", text=json.dumps(entry, indent=2))
                ]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error adding entry to knowledge base: {e}")],
                isError=True,
            )

    async def run_forever(self):
        """Starts the MCP FastMCP stdio server."""
        print("osenv_manager MCP Server starting...")
        await self.mcp_server.run_stdio_async()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="osenv MCP Server")
    parser.add_argument(
        "--test", 
        action="store_true", 
        help="Run self-tests and exit instead of starting stdio server"
    )
    args = parser.parse_args()

    async def main():
        server = OsenvServer()
        if args.test:
            print("--- Testing osenv MCP Server locally ---")
            
            # 1. Test kb stats
            stats_info = kb_stats()
            print(f"KB Stats: {json.dumps(stats_info, indent=2)}")
            
            # 2. Test system audit
            print("\nTesting system audit:")
            audit_res = await server._osenv_audit_tool()
            print(f"Audit Result Summary: {audit_res.content}")
            
            # 3. Test KB add/list/search
            print("\nTesting KB tools:")
            add_res = await server._osenv_kb_add_tool(
                KbAddInput(
                    key="test.mcp_check",
                    value="Success",
                    source="mcp_test",
                    tags=["test", "mcp"],
                    summary="Test entry created during MCP self-test"
                )
            )
            print(f"KB Add Result: {add_res.content}")
            
            list_res = await server._osenv_kb_list_tool(KbListInput(tags=["mcp"]))
            print(f"KB List Result (tag=mcp): {list_res.content}")
            
            search_res = await server._osenv_kb_search_tool(KbSearchInput(query="mcp_test"))
            print(f"KB Search Result (query=mcp_test): {search_res.content}")
            
        else:
            await server.run_forever()

    asyncio.run(main())
