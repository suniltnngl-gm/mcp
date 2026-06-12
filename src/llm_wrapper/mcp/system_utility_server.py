"""MCP server that exposes sandboxed file/system utility tools."""

import asyncio
import json
from pathlib import Path
from typing import List, Literal, Optional
import os
import shutil  # Directory copy operations for project snapshots.
from datetime import datetime  # Timestamping snapshot directory names.
import psutil

from mcp.server.fastmcp import FastMCP
from mcp.types import CallToolResult, Resource, Tool
from pydantic import BaseModel, Field

# Default sandbox for read/write tools. Operations are constrained to this tree.
# In production, consider injecting this path from configuration or environment.
DEFAULT_SANDBOX_ROOT = Path("./llm_sandbox").resolve()
# Root directory where full project snapshots are written.
PROJECT_BACKUP_ROOT = Path("./backups/project_snapshots").resolve()


class SafeWriteInput(BaseModel):
    """Input schema for the safe_write tool."""

    file_path: str = Field(
        ..., description="The path to the file to write (relative to sandbox)."
    )
    content: str = Field(..., description="The content to write to the file.")
    overwrite: bool = Field(
        False, description="Whether to overwrite the file if it exists."
    )


class ReadPathInput(BaseModel):
    """Input schema for the read_path tool."""

    file_path: str = Field(
        ..., description="The path to the file to read (relative to sandbox)."
    )
    limit: Optional[int] = Field(
        None, description="Optional: Maximum number of lines to read for text files."
    )
    offset: Optional[int] = Field(
        None, description="Optional: 0-based line number to start reading from."
    )


class GetSystemMetricsInput(BaseModel):
    """Input schema for the get_system_metrics tool."""

    sample_interval_seconds: float = Field(
        0.1,
        ge=0.0,
        le=2.0,
        description="Sampling interval used for CPU percent calculation.",
    )


class GetSystemMetricsOutput(BaseModel):
    """Output schema for system metrics."""

    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float


class ProcessInfo(BaseModel):
    """Process information returned by list_processes."""

    pid: int
    name: Optional[str] = None
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    status: Optional[str] = None
    username: Optional[str] = None


class ListProcessesInput(BaseModel):
    """Input schema for the list_processes tool."""

    limit: int = Field(10, ge=1, le=500, description="Maximum processes to return.")
    sort_by: Literal[
        "cpu_percent", "memory_percent", "pid", "name", "status", "username"
    ] = Field(
        "cpu_percent",
        description="Field used to sort results in descending order.",
    )


class ListProcessesOutput(BaseModel):
    """Output schema for listed processes."""

    processes: List[ProcessInfo]


class CreateProjectSnapshotInput(BaseModel):
    """Input schema for the create_project_snapshot tool."""

    pass


class SystemUtilityServer:
    """
    An MCP server providing basic sandboxed system utilities to LLMs.
    Includes file operations (read/write), system metrics, process listing, and project snapshots.
    """

    def __init__(self, sandbox_root: Optional[Path] = None):
        self.sandbox_root = (sandbox_root or DEFAULT_SANDBOX_ROOT).resolve()
        self.sandbox_root.mkdir(
            parents=True, exist_ok=True
        )  # Create sandbox root if missing.
        print(f"SystemUtilityServer initialized with sandbox root: {self.sandbox_root}")

        PROJECT_BACKUP_ROOT.mkdir(
            parents=True, exist_ok=True
        )  # Create snapshot root if missing.
        print(f"Project snapshot root: {PROJECT_BACKUP_ROOT}")

        self.mcp_server = FastMCP(name="system_utility")
        self.mcp_server.add_tool(
            self._safe_write_tool,
            name="safe_write",
            description="Writes content to a file within the designated sandbox root.",
        )
        self.mcp_server.add_tool(
            self._read_path_tool,
            name="read_path",
            description="Reads content from a file within the designated sandbox root.",
        )
        self.mcp_server.add_tool(
            self._get_system_metrics_tool,
            name="get_system_metrics",
            description="Retrieves current CPU, memory, and disk usage of the system.",
        )
        self.mcp_server.add_tool(
            self._list_processes_tool,
            name="list_processes",
            description="Lists running processes with their resource usage.",
        )
        self.mcp_server.add_tool(
            self._create_project_snapshot_tool,
            name="create_project_snapshot",
            description="Creates a timestamped, recursive backup of the entire project directory (excluding ignored files).",
        )

    def _get_safe_path(self, relative_path: str) -> Optional[Path]:
        """
        Validates that the target path is within the sandbox root.
        Returns the absolute Path if safe, None otherwise.
        """
        try:
            target_path = (self.sandbox_root / relative_path).resolve()
        except (
            Exception
        ):  # Handle cases where path is invalid, e.g., contains null bytes
            return None

        # Ensure the resolved path still points inside sandbox_root.
        if not target_path.is_relative_to(self.sandbox_root):
            print(
                f"SECURITY ALERT: Attempt to access path outside sandbox: {target_path}"
            )
            return None
        return target_path

    async def _safe_write_tool(self, input: SafeWriteInput) -> CallToolResult:
        """MCP tool to write content to a file within the sandbox."""
        safe_path = self._get_safe_path(input.file_path)
        if not safe_path:
            return CallToolResult(
                content=f"Error: Path '{input.file_path}' is outside sandbox or invalid.",
                success=False,
            )

        if safe_path.exists() and not input.overwrite:
            return CallToolResult(
                content=f"Error: File '{input.file_path}' already exists and overwrite is false.",
                success=False,
            )

        try:
            safe_path.parent.mkdir(
                parents=True, exist_ok=True
            )  # Create parent directories as needed.
            safe_path.write_text(input.content, encoding="utf-8")
            return CallToolResult(
                content=f"Successfully wrote to '{input.file_path}'.", success=True
            )
        except Exception as e:
            return CallToolResult(
                content=f"Error writing to '{input.file_path}': {e}", success=False
            )

    async def _read_path_tool(self, input: ReadPathInput) -> CallToolResult:
        """MCP tool to read content from a file within the sandbox."""
        safe_path = self._get_safe_path(input.file_path)
        if not safe_path:
            return CallToolResult(
                content=f"Error: Path '{input.file_path}' is outside sandbox or invalid.",
                success=False,
            )

        if not safe_path.is_file():
            return CallToolResult(
                content=f"Error: File '{input.file_path}' not found or is not a file.",
                success=False,
            )

        try:
            with open(safe_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            start_line = input.offset if input.offset is not None else 0
            end_line = start_line + (
                input.limit if input.limit is not None else len(lines)
            )

            content_lines = lines[start_line:end_line]
            content = "".join(content_lines)

            truncated = len(lines) > len(content_lines)

            message = f"Successfully read from '{input.file_path}'."
            if truncated:
                message += " (Truncated)"

            return CallToolResult(
                content=message,
                success=True,
                resources=[Resource(data=content)],
            )
        except Exception as e:
            return CallToolResult(
                content=f"Error reading from '{input.file_path}': {e}", success=False
            )

    async def _get_system_metrics_tool(
        self, input: GetSystemMetricsInput
    ) -> CallToolResult:
        """MCP tool to get system-wide CPU, memory, and disk usage."""
        try:
            cpu = psutil.cpu_percent(interval=input.sample_interval_seconds)
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage("/").percent  # Root filesystem usage.

            metrics = GetSystemMetricsOutput(
                cpu_percent=cpu, memory_percent=memory, disk_usage_percent=disk
            )
            return CallToolResult(
                content="Successfully retrieved system metrics.",
                success=True,
                resources=[Resource(data=metrics.model_dump_json())],
            )
        except Exception as e:
            return CallToolResult(
                content=f"Error retrieving system metrics: {e}", success=False
            )

    async def _list_processes_tool(self, input: ListProcessesInput) -> CallToolResult:
        """MCP tool to list running processes."""
        try:
            processes_data: List[ProcessInfo] = []
            for proc in psutil.process_iter(
                ["pid", "name", "cpu_percent", "memory_percent", "status", "username"]
            ):
                try:
                    processes_data.append(
                        ProcessInfo(
                            pid=proc.info["pid"],
                            name=proc.info["name"],
                            cpu_percent=proc.info["cpu_percent"],
                            memory_percent=proc.info["memory_percent"],
                            status=proc.info["status"],
                            username=proc.info["username"],
                        )
                    )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    # Process may have exited mid-iteration or be inaccessible.
                    continue

            # Sort process output when the requested sort key is valid.
            if input.sort_by in ProcessInfo.model_fields:
                processes_data.sort(
                    key=lambda p: getattr(p, input.sort_by), reverse=True
                )

            # Truncate to requested maximum size.
            processes_data = processes_data[: input.limit]

            output = ListProcessesOutput(processes=processes_data)
            return CallToolResult(
                content=f"Successfully listed {len(processes_data)} processes.",
                success=True,
                resources=[Resource(data=output.model_dump_json())],
            )
        except Exception as e:
            return CallToolResult(
                content=f"Error listing processes: {e}", success=False
            )

    async def _create_project_snapshot_tool(
        self, input: CreateProjectSnapshotInput
    ) -> CallToolResult:
        """MCP tool to create a timestamped snapshot of the entire project directory."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_dir_name = f"project_snapshot_{timestamp}"
            target_path = PROJECT_BACKUP_ROOT / snapshot_dir_name
            target_path.mkdir(parents=True, exist_ok=True)

            # Exclude heavy/generated directories from snapshot copies.
            # TODO: optionally align this with parsed .gitignore patterns.
            exclude_dirs = [
                ".git",
                "__pycache__",
                ".venv",
                "backups",
                "llm_sandbox",
                "data",
            ]

            def ignore_patterns(path, names):
                ignored_names = []
                for name in names:
                    if (Path(path) / name).is_dir() and name in exclude_dirs:
                        ignored_names.append(name)
                    # Additional ignore rules can be added here if needed.
                return set(ignored_names)

            print(f"Creating project snapshot to {target_path}...")
            # Copy current working directory into the timestamped snapshot target.
            shutil.copytree(
                os.getcwd(),  # Use process CWD as project root snapshot source.
                target_path,
                ignore=ignore_patterns,
                dirs_exist_ok=True,  # Safe here because target path includes a timestamp.
            )
            print(f"Project snapshot successfully created at {target_path}.")
            return CallToolResult(
                content=f"Project snapshot created at '{target_path}'.", success=True
            )
        except Exception as e:
            print(f"Error creating project snapshot: {e}")
            return CallToolResult(
                content=f"Error creating project snapshot: {e}", success=False
            )

    async def run_forever(self):
        """Starts the MCP FastMCP stdio server."""
        print(f"System Utility Server starting, Sandbox Root: {self.sandbox_root}")
        await self.mcp_server.run_stdio_async()


if __name__ == "__main__":

    async def main():
        print("--- Testing SystemUtilityServer ---")
        temp_sandbox_root = Path(
            "./temp_llm_sandbox"
        ).resolve()  # Isolated temp sandbox for local tests.

        if temp_sandbox_root.exists():
            shutil.rmtree(temp_sandbox_root)  # Remove previous test artifacts.
        temp_sandbox_root.mkdir()

        # Clean up existing project snapshots for test
        if PROJECT_BACKUP_ROOT.exists():
            shutil.rmtree(PROJECT_BACKUP_ROOT)
        PROJECT_BACKUP_ROOT.mkdir(parents=True, exist_ok=True)

        server = SystemUtilityServer(sandbox_root=temp_sandbox_root)

        try:
            # Test safe_write
            print("\nCalling safe_write tool:")
            write_input = SafeWriteInput(
                file_path="test_dir/hello.txt", content="Hello, LLM!", overwrite=True
            )
            write_result = await server._safe_write_tool(write_input)
            print(
                f"Write Result: {write_result.content}, Success: {write_result.success}"
            )

            # Test read_path
            print("\nCalling read_path tool:")
            read_input = ReadPathInput(file_path="test_dir/hello.txt")
            read_result = await server._read_path_tool(read_input)
            print(f"Read Result: {read_result.content}, Success: {read_result.success}")
            if read_result.resources:
                print(f"Read Content: {read_result.resources[0].data}")

            # Test safe_write (no overwrite)
            print("\nCalling safe_write tool (no overwrite):")
            write_input_no_overwrite = SafeWriteInput(
                file_path="test_dir/hello.txt", content="New content."
            )
            write_result_no_overwrite = await server._safe_write_tool(
                write_input_no_overwrite
            )
            print(
                f"Write (no overwrite) Result: {write_result_no_overwrite.content}, Success: {write_result_no_overwrite.success}"
            )

            # Test safe_write (outside sandbox - should fail)
            print("\nCalling safe_write tool (outside sandbox):")
            write_input_unsafe = SafeWriteInput(
                file_path="../../../unsafe.txt",
                content="Malicious content.",
                overwrite=True,
            )
            write_result_unsafe = await server._safe_write_tool(write_input_unsafe)
            print(
                f"Unsafe Write Result: {write_result_unsafe.content}, Success: {write_result_unsafe.success}"
            )

            # Test read_path (outside sandbox - should fail)
            print("\nCalling read_path tool (outside sandbox):")
            read_input_unsafe = ReadPathInput(file_path="../../../some_system_file.txt")
            read_result_unsafe = await server._read_path_tool(read_input_unsafe)
            print(
                f"Unsafe Read Result: {read_result_unsafe.content}, Success: {read_result_unsafe.success}"
            )

            # Test reading with limit and offset
            print("\nCreating multi-line file for limit/offset test:")
            multi_line_content = "\n".join([f"Line {i}" for i in range(20)])
            write_input_multi = SafeWriteInput(
                file_path="multi_line.txt", content=multi_line_content, overwrite=True
            )
            await server._safe_write_tool(write_input_multi)

            print("\nReading multi_line.txt with limit=5, offset=10:")
            read_input_limited = ReadPathInput(
                file_path="multi_line.txt", limit=5, offset=10
            )
            read_result_limited = await server._read_path_tool(read_input_limited)
            print(
                f"Read Limited Result: {read_result_limited.content}, Success: {read_result_limited.success}"
            )
            if read_result_limited.resources:
                print(f"Read Limited Content:\n{read_result_limited.resources[0].data}")

            # --- New Tests for Environment Inspection Tools ---
            print("\n--- Testing Environment Inspection Tools ---")

            print("\nCalling get_system_metrics tool:")
            metrics_input = GetSystemMetricsInput()
            metrics_result = await server._get_system_metrics_tool(metrics_input)
            print(
                f"Metrics Result: {metrics_result.content}, Success: {metrics_result.success}"
            )
            if metrics_result.resources:
                print(
                    f"System Metrics: {json.dumps(json.loads(metrics_result.resources[0].data), indent=2)}"
                )

            print("\nCalling list_processes tool (top 5 by CPU):")
            list_proc_input = ListProcessesInput(limit=5, sort_by="cpu_percent")
            list_proc_result = await server._list_processes_tool(list_proc_input)
            print(
                f"List Processes Result: {list_proc_result.content}, Success: {list_proc_result.success}"
            )
            if list_proc_result.resources:
                print(
                    f"Processes: {json.dumps(json.loads(list_proc_result.resources[0].data), indent=2)}"
                )

            # --- New Test for create_project_snapshot Tool ---
            print("\n--- Testing create_project_snapshot Tool ---")
            snapshot_input = CreateProjectSnapshotInput()
            snapshot_result = await server._create_project_snapshot_tool(snapshot_input)
            print(
                f"Snapshot Result: {snapshot_result.content}, Success: {snapshot_result.success}"
            )

            # Verify snapshot creation (optional, but good for robust testing)
            if snapshot_result.success:
                snapshot_dirs = list(PROJECT_BACKUP_ROOT.glob("project_snapshot_*"))
                if snapshot_dirs:
                    print(f"Found created snapshot directory: {snapshot_dirs[0].name}")
                else:
                    print(
                        "Error: No snapshot directory found despite reported success."
                    )

        except Exception as e:
            print(f"An error occurred during SystemUtilityServer test: {e}")
        finally:
            if temp_sandbox_root.exists():
                shutil.rmtree(temp_sandbox_root)
                print(f"Cleaned up temporary sandbox: {temp_sandbox_root}")

            if PROJECT_BACKUP_ROOT.exists():
                shutil.rmtree(PROJECT_BACKUP_ROOT)
                print(f"Cleaned up project snapshot root: {PROJECT_BACKUP_ROOT}")

    asyncio.run(main())
