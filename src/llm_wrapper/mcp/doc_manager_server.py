"""MCP server for managing and searching documents.

Firestore-backed document index with directory scanning and
keyword-in-context search. Replaces legacy SQLite storage.
"""

import asyncio
import json
from pathlib import Path
from typing import List, Optional

from mcp.server.fastmcp import FastMCP
from mcp.types import CallToolResult, Resource
from pydantic import BaseModel, Field

from src.llm_wrapper.mcp import firestore_doc_service as fds


class IndexDirectoryInput(BaseModel):
    directory_path: str = Field(
        ..., description="Absolute path to the directory to scan and index."
    )
    include_patterns: Optional[List[str]] = Field(
        None, description="Glob patterns to include (e.g., ['*.md', '*.txt'])."
    )
    exclude_patterns: Optional[List[str]] = Field(
        None, description="Glob patterns to exclude."
    )


class SearchContextInput(BaseModel):
    query: str = Field(..., description="Search query to find relevant context.")
    limit: int = Field(5, description="Maximum context snippets to return.")


class DocManagerServer:
    """MCP server for scanning, indexing, and searching documents via Firestore."""

    def __init__(self):
        self.mcp_server = FastMCP(name="document_manager")
        self.mcp_server.add_tool(
            self._index_directory_tool,
            name="index_directory",
            description="Scans a directory, extracts text from documents, and indexes them in Firestore.",
        )
        self.mcp_server.add_tool(
            self._search_context_tool,
            name="search_context",
            description="Searches indexed documents for relevant context snippets.",
        )
        self.mcp_server.add_tool(
            self._list_documents_tool,
            name="list_documents",
            description="Lists all indexed documents with metadata.",
        )
        self.mcp_server.add_tool(
            self._delete_document_tool,
            name="delete_document",
            description="Removes a document from the index by file path.",
        )

    def _extract_text_from_file(self, file_path: Path) -> str:
        return file_path.read_text(encoding="utf-8", errors="ignore")

    async def _index_directory_tool(self, input: IndexDirectoryInput) -> CallToolResult:
        directory = Path(input.directory_path)
        if not directory.is_dir():
            return CallToolResult(
                content=f"Error: Directory not found: {directory}", success=False
            )

        indexed_count = 0
        errors = []

        for file_path in directory.rglob("*"):
            if not file_path.is_file():
                continue

            if input.include_patterns and not any(
                file_path.match(p) for p in input.include_patterns
            ):
                continue
            if input.exclude_patterns and any(
                file_path.match(p) for p in input.exclude_patterns
            ):
                continue

            try:
                text_content = self._extract_text_from_file(file_path)
                summary = text_content.split("\n", 3)[0] if text_content else ""
                title = file_path.stem

                fds.index_document(
                    file_path=str(file_path),
                    title=title,
                    content=text_content,
                    summary=summary,
                )
                indexed_count += 1
            except Exception as e:
                errors.append(f"{file_path}: {e}")

        msg = f"Indexed {indexed_count} documents from {directory}"
        if errors:
            msg += f" ({len(errors)} errors — first: {errors[0]})"
        return CallToolResult(content=msg, success=True)

    async def _search_context_tool(self, input: SearchContextInput) -> CallToolResult:
        try:
            results = fds.search_documents(query=input.query, limit=input.limit)
        except fds.FirestoreInitError as e:
            return CallToolResult(content=f"Firestore unavailable: {e}", success=False)

        if not results:
            return CallToolResult(
                content=f"No context found for query: '{input.query}'", success=True
            )

        return CallToolResult(
            content=f"Found {len(results)} relevant context snippets.",
            resources=[Resource(data=json.dumps(results))],
        )

    async def _list_documents_tool(self) -> CallToolResult:
        try:
            docs = fds.list_documents()
        except fds.FirestoreInitError as e:
            return CallToolResult(content=f"Firestore unavailable: {e}", success=False)

        if not docs:
            return CallToolResult(content="No documents indexed yet.", success=True)

        return CallToolResult(
            content=f"Found {len(docs)} indexed documents.",
            resources=[Resource(data=json.dumps(docs))],
        )

    async def _delete_document_tool(self, file_path: str = ...) -> CallToolResult:
        try:
            deleted = fds.delete_document(file_path)
        except fds.FirestoreInitError as e:
            return CallToolResult(content=f"Firestore unavailable: {e}", success=False)

        if deleted:
            return CallToolResult(content=f"Deleted: {file_path}", success=True)
        return CallToolResult(
            content=f"Document not found in index: {file_path}", success=False
        )

    async def run_forever(self):
        print("Document Manager Server starting (Firestore backend)...")
        await self.mcp_server.run_stdio_async()


if __name__ == "__main__":

    async def main():
        print("--- Testing DocManagerServer (Firestore) ---")
        server = DocManagerServer()

        dummy_dir = Path("./dummy_docs")
        dummy_dir.mkdir(exist_ok=True)
        (dummy_dir / "test_doc_1.md").write_text(
            "# Hello World\nThis is a test markdown document with important information about project setup."
        )
        (dummy_dir / "notes.txt").write_text("Plain text notes. Remember to buy milk.")

        try:
            # Test list (should be empty)
            list_res = await server._list_documents_tool()
            print(f"\nList before indexing: {list_res.content}")

            # Test indexing
            print("\nCalling index_directory tool:")
            index_input = IndexDirectoryInput(
                directory_path=str(dummy_dir),
                include_patterns=["*.md", "*.txt"],
            )
            index_result = await server._index_directory_tool(index_input)
            print(f"Index Result: {index_result.content}")

            # Test list (should have 2)
            list_res2 = await server._list_documents_tool()
            print(f"\nList after indexing: {list_res2.content}")

            # Test search
            print("\nSearching for 'project setup':")
            search_res = await server._search_context_tool(
                SearchContextInput(query="project setup", limit=2)
            )
            print(f"Search Result: {search_res.content}")

            # Test delete
            print("\nDeleting notes.txt:")
            del_res = await server._delete_document_tool(
                file_path=str(dummy_dir / "notes.txt")
            )
            print(f"Delete Result: {del_res.content}")

        except Exception as e:
            print(f"An error occurred during test: {e}")
            import traceback
            traceback.print_exc()
        finally:
            import shutil
            if dummy_dir.is_dir():
                shutil.rmtree(dummy_dir)
                print(f"\nCleaned up: {dummy_dir}")

    asyncio.run(main())
