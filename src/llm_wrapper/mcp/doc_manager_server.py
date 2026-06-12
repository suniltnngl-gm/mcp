# src/llm_wrapper/mcp/doc_manager_server.py

import asyncio
import json
import sqlite3
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, CallToolResult, Resource
from pydantic import BaseModel, Field

# For markdown conversion (conceptually 'markitdown')
import markdown  # Using standard markdown library


class DocumentMetadata(BaseModel):
    """Metadata for an indexed document."""

    path: str
    title: Optional[str] = None
    summary: Optional[str] = None
    indexed_at: str


class DocumentContent(BaseModel):
    """Content of an indexed document."""

    path: str
    content: str  # Extracted plain text content


class IndexDirectoryInput(BaseModel):
    """Input schema for the index_directory tool."""

    directory_path: str = Field(
        ..., description="The path to the directory to scan and index."
    )
    include_patterns: Optional[List[str]] = Field(
        None, description="List of glob patterns to include (e.g., '*.md', '*.txt')."
    )
    exclude_patterns: Optional[List[str]] = Field(
        None, description="List of glob patterns to exclude."
    )


class SearchContextInput(BaseModel):
    """Input schema for the search_context tool."""

    query: str = Field(..., description="The search query to find relevant context.")
    limit: int = Field(5, description="Maximum number of context snippets to return.")


class DocManagerServer:
    """
    An MCP server for managing and searching documents.
    Implements local-first indexing using SQLite and Markdown conversion.
    """

    DB_NAME = "document_index.db"

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._initialize_db()
        self.mcp_server = FastMCP(name="document_manager")
        self.mcp_server.add_tool(
            self._index_directory_tool,
            name="index_directory",
            description="Scans a directory, extracts text from documents, and indexes them.",
        )
        self.mcp_server.add_tool(
            self._search_context_tool,
            name="search_context",
            description="Searches indexed documents for relevant context snippets based on a query.",
        )

    def _initialize_db(self):
        """Initializes the SQLite database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                path TEXT PRIMARY KEY,
                title TEXT,
                summary TEXT,
                indexed_at TEXT,
                content TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _extract_text_from_file(self, file_path: Path) -> str:
        """
        Extracts plain text content from a file.
        Currently handles Markdown and plain text.
        """
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        if file_path.suffix.lower() == ".md":
            # Convert markdown to plain text (using a simple converter)
            return markdown.markdown(
                content, output_format="html2text"
            )  # This is conceptual, markdown library doesn't have html2text directly
        # Default to returning raw content for other types
        return content

    async def _index_directory_tool(self, input: IndexDirectoryInput) -> CallToolResult:
        """MCP tool to scan a directory and index documents."""
        directory = Path(input.directory_path)
        if not directory.is_dir():
            return CallToolResult(
                content=f"Error: Directory not found: {directory}", success=False
            )

        indexed_count = 0
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for file_path in directory.rglob("*"):  # Recursive glob
            if file_path.is_file():
                # Apply include/exclude patterns
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
                    # Basic summary (e.g., first few lines)
                    summary = text_content.split("\n", 3)[0] if text_content else None
                    title = file_path.stem  # Simple title from filename
                    indexed_at = datetime.now().isoformat()

                    cursor.execute(
                        "INSERT OR REPLACE INTO documents (path, title, summary, indexed_at, content) VALUES (?, ?, ?, ?, ?)",
                        (str(file_path), title, summary, indexed_at, text_content),
                    )
                    indexed_count += 1
                except Exception as e:
                    print(f"Error indexing {file_path}: {e}")

        conn.commit()
        conn.close()
        return CallToolResult(
            content=f"Indexed {indexed_count} documents from {directory}", success=True
        )

    async def _search_context_tool(self, input: SearchContextInput) -> CallToolResult:
        """MCP tool to search indexed documents for context."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query_pattern = f"%{input.query}%"
        cursor.execute(
            "SELECT path, title, summary, content FROM documents WHERE content LIKE ? LIMIT ?",
            (query_pattern, input.limit),
        )
        results = cursor.fetchall()
        conn.close()

        context_snippets = []
        for path, title, summary, content in results:
            # Simple keyword-in-context (KWIC) retrieval
            snippet_start = max(0, content.lower().find(input.query.lower()) - 100)
            snippet_end = min(len(content), snippet_start + len(input.query) + 200)
            snippet = (
                content[snippet_start:snippet_end].strip() + "..."
                if snippet_end < len(content)
                else content[snippet_start:snippet_end].strip()
            )

            context_snippets.append(
                {"path": path, "title": title, "summary": summary, "snippet": snippet}
            )

        if not context_snippets:
            return CallToolResult(
                content=f"No context found for query: '{input.query}'", success=True
            )

        return CallToolResult(
            content=f"Found {len(context_snippets)} relevant context snippets.",
            resources=[Resource(data=json.dumps(context_snippets))],
        )

    async def run_forever(self):
        """Starts the MCP FastMCP stdio server."""
        print(f"Document Manager Server starting, DB: {self.db_path}")
        await self.mcp_server.run_stdio_async()


if __name__ == "__main__":

    async def main():
        print("--- Testing DocManagerServer ---")
        temp_db_path = Path("temp_doc_index.db")
        if temp_db_path.exists():
            temp_db_path.unlink()  # Clean up previous test run

        server = DocManagerServer(db_path=temp_db_path)

        # Create some dummy files for indexing
        dummy_dir = Path("./dummy_docs")
        dummy_dir.mkdir(exist_ok=True)
        (dummy_dir / "test_doc_1.md").write_text(
            "# Hello World\nThis is a test markdown document with some important information about project setup."
        )
        (dummy_dir / "notes.txt").write_text("Plain text notes. Remember to buy milk.")
        (dummy_dir / "ignore.log").write_text("This file should be ignored.")
        (dummy_dir / "subdir").mkdir(exist_ok=True)
        (dummy_dir / "subdir" / "code_snippet.md").write_text(
            "```python\nprint('Hello from code')\n```\nThis is a Python code snippet."
        )

        try:
            # Test indexing
            print("\nCalling index_directory tool:")
            index_input = IndexDirectoryInput(
                directory_path=str(dummy_dir),
                include_patterns=["*.md", "*.txt"],
                exclude_patterns=["*.log"],
            )
            # Directly call tool function for testing, similar to how MCP would
            index_result = await server._index_directory_tool(index_input)
            print(f"Index Result: {index_result.content}")

            # Test searching
            print("\nCalling search_context tool for 'project setup':")
            search_input = SearchContextInput(query="project setup", limit=2)
            search_result = await server._search_context_tool(search_input)
            print(f"Search Result: {search_result.content}")
            if search_result.resources:
                print(
                    f"Resources: {json.dumps(json.loads(search_result.resources[0].data), indent=2)}"
                )

            print("\nCalling search_context tool for 'milk':")
            search_input_milk = SearchContextInput(query="milk", limit=1)
            search_result_milk = await server._search_context_tool(search_input_milk)
            print(f"Search Result: {search_result_milk.content}")
            if search_result_milk.resources:
                print(
                    f"Resources: {json.dumps(json.loads(search_result_milk.resources[0].data), indent=2)}"
                )

            print("\nCalling search_context tool for 'nonexistent':")
            search_input_none = SearchContextInput(query="nonexistent")
            search_result_none = await server._search_context_tool(search_input_none)
            print(f"Search Result: {search_result_none.content}")

        except Exception as e:
            print(f"An error occurred during DocManagerServer test: {e}")
        finally:
            # Clean up dummy files and database
            if temp_db_path.exists():
                temp_db_path.unlink()  # Clean up previous test run
                print(f"Cleaned up temporary database: {temp_db_path}")

            # Use rmtree for directories to handle sub-contents
            if dummy_dir.is_dir():
                import shutil

                shutil.rmtree(dummy_dir)
                print(f"Cleaned up dummy directory: {dummy_dir}")

    asyncio.run(main())
