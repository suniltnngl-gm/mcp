# benchmark_orchestrator.py

import asyncio
import time
import json
from pathlib import Path
import os
import shutil
from typing import Dict, List, Any, Optional

from src.llm_wrapper.mcp.config import (
    load_mcp_config,
    create_dummy_mcp_config,
    cleanup_dummy_mcp_config,
)
from src.llm_wrapper.mcp.stdio_client import (
    create_dummy_mcp_server_script,
    cleanup_dummy_mcp_server_script,
)
from src.llm_wrapper.orchestrator import LLMOrchestrator
from mcp.types import CallToolResult


class BenchmarkTask:
    """Defines a single task for benchmarking."""

    def __init__(
        self,
        name: str,
        prompt: str,
        expected_tool_call: Optional[Dict[str, Any]] = None,
        expected_response_substring: Optional[str] = None,
    ):
        self.name = name
        self.prompt = prompt
        self.expected_tool_call = (
            expected_tool_call  # e.g., {"name": "index_directory", "arguments": {...}}
        )
        self.expected_response_substring = (
            expected_response_substring  # e.g., "Indexed 2 documents"
        )

    def __str__(self):
        return self.name


async def run_benchmark_task(
    orchestrator: LLMOrchestrator,
    task: BenchmarkTask,
    mode: str,
    game_session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Runs a single benchmark task in a given mode and returns metrics."""
    start_time = time.monotonic()

    use_local_llm = "local" in mode.lower() or "hybrid" in mode.lower()
    use_provider_llm = "provider" in mode.lower() or "hybrid" in mode.lower()

    # Special handling for game tasks to inject session_id
    current_prompt = task.prompt
    current_expected_tool_call = task.expected_tool_call
    if (
        game_session_id and "Session " in task.prompt
    ):  # Simple heuristic to identify game prompts
        current_prompt = current_prompt.replace(
            f"Session {game_session_id}:", f"Session {game_session_id}:"
        )
        if current_expected_tool_call:
            current_expected_tool_call = current_expected_tool_call.copy()
            if "arguments" in current_expected_tool_call:
                current_expected_tool_call["arguments"] = current_expected_tool_call[
                    "arguments"
                ].copy()
                current_expected_tool_call["arguments"]["session_id"] = game_session_id

    try:
        response = await orchestrator.orchestrate_response(
            current_prompt,
            use_local_llm=use_local_llm,
            use_provider_llm=use_provider_llm,
        )
        end_time = time.monotonic()
        latency = end_time - start_time

        # Evaluate accuracy based on expected outcomes
        accuracy_score = 0

        # Check tool call accuracy first
        llm_response_tool_call = None
        if (
            "local_llm_response" in response
            and "tool_call" in response["local_llm_response"]
        ):
            llm_response_tool_call = response["local_llm_response"]["tool_call"]
        elif (
            "provider_llm_response" in response
            and "tool_call" in response["provider_llm_response"]
        ):
            llm_response_tool_call = response["provider_llm_response"]["tool_call"]

        if task.expected_tool_call and llm_response_tool_call:
            if llm_response_tool_call["name"] == task.expected_tool_call["name"]:
                accuracy_score += 0.5  # Correct tool identified
                # A more robust comparison would involve argument validation
                # For now, a simple check if arguments are present
                if llm_response_tool_call["arguments"]:
                    accuracy_score += 0.5
        elif task.expected_tool_call is None and llm_response_tool_call is None:
            accuracy_score = 1.0  # Expected no tool call, and none occurred

        # Check response substring if applicable (and no tool call expected/occurred)
        if accuracy_score == 1.0 and task.expected_response_substring:
            llm_response_content = ""
            if "local_llm_tool_result" in response:
                llm_response_content = str(response["local_llm_tool_result"])
            elif "provider_llm_tool_result" in response:
                llm_response_content = str(response["provider_llm_tool_result"])
            elif (
                "local_llm_response" in response
                and "response" in response["local_llm_response"]
            ):
                llm_response_content = response["local_llm_response"]["response"]
            elif (
                "provider_llm_response" in response
                and "response" in response["provider_llm_response"]
            ):
                llm_response_content = response["provider_llm_response"]["response"]

            if task.expected_response_substring.lower() in llm_response_content.lower():
                accuracy_score = 1.0
            else:
                accuracy_score = 0.5  # Partial accuracy if substring not found

        # Aggregate token usage
        token_usage = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
        if (
            "provider_llm_response" in response
            and "token_usage" in response["provider_llm_response"]
        ):
            token_usage = response["provider_llm_response"]["token_usage"]

        return {
            "task_name": task.name,
            "mode": mode,
            "latency": latency,
            "accuracy": accuracy_score,
            "token_usage": token_usage,
            "raw_response": response,  # Include raw response for debugging
        }
    except Exception as e:
        print(f"Error running benchmark task '{task.name}' in mode '{mode}': {e}")
        return {
            "task_name": task.name,
            "mode": mode,
            "latency": -1,  # Indicate failure
            "accuracy": 0,
            "token_usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
            "error": str(e),
        }


async def main():
    print("--- Running LLM Orchestrator Benchmarks ---")

    # --- Setup Environment ---
    dummy_server_path = Path("my_mcp_server.py")
    await create_dummy_mcp_server_script(dummy_server_path)
    dummy_config_path = Path("mcp.json")
    create_dummy_mcp_config(dummy_config_path, dummy_server_path)

    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)
    os.environ["DB_PATH"] = str(data_dir / "docs.db")
    os.environ["GAME_RULES_DB_PATH"] = str(data_dir / "game_rules.db")

    # Create dummy docs for DocManagerServer
    dummy_docs_dir = Path("./dummy_docs_for_dm")
    dummy_docs_dir.mkdir(exist_ok=True)
    (dummy_docs_dir / "project_info.md").write_text(
        "# Project Info\nThis project aims to build a hybrid LLM system for developer assistance."
    )
    (dummy_docs_dir / "architecture.md").write_text(
        "The architecture consists of an Orchestrator, MultiClientManager, and various MCP servers."
    )

    mcp_config = load_mcp_config(dummy_config_path)

    if not mcp_config:
        print("Failed to load MCP configuration. Exiting benchmark.")
        await cleanup_environment(
            dummy_server_path, dummy_config_path, data_dir, dummy_docs_dir
        )
        return

    benchmark_results: List[Dict[str, Any]] = []

    try:
        async with LLMOrchestrator(mcp_config) as orchestrator:
            # --- Initialize servers and tools for benchmarking ---
            # Index dummy documents first
            await orchestrator._multi_client_manager.call_tool(
                "index_directory",
                {
                    "directory_path": str(dummy_docs_dir),
                    "include_patterns": ["*.md", "*.txt"],
                },
                server_name="doc_manager",
            )
            print("Documents indexed for DocManagerServer.")

            # Start a game session for GameRulesServer
            start_game_result: CallToolResult = (
                await orchestrator._multi_client_manager.call_tool(
                    "start_game",
                    {"puzzle_id": "turtle_soup"},
                    server_name="game_rules_manager",
                )
            )
            if start_game_result.success and start_game_result.resources:
                session_data = json.loads(start_game_result.resources[0].data)
                game_session_id = session_data["session_id"]
                print(f"Game session started: {game_session_id}")
            else:
                game_session_id = None
                print("Failed to start game session for benchmarking.")

            # --- Define Benchmark Tasks ---
            benchmark_tasks = [
                BenchmarkTask(
                    name="Simple Text Generation",
                    prompt="Tell me a very short, positive affirmation.",
                    expected_response_substring="You are amazing",  # A generic positive phrase for partial accuracy
                ),
                BenchmarkTask(
                    name="Document Search (Tool)",
                    prompt="Find information about the project's architecture.",
                    expected_tool_call={
                        "name": "search_context",
                        "arguments": {"query": "architecture", "limit": 1},
                    },
                    expected_response_substring="The architecture consists of an Orchestrator",
                ),
            ]
            # Add game tasks only if session was successfully started
            if game_session_id:
                benchmark_tasks.extend(
                    [
                        BenchmarkTask(
                            name="Game Question (Yes)",
                            prompt=f"Session {game_session_id}: Was the man in the soup a friend of the one who shot himself?",
                            expected_tool_call={
                                "name": "evaluate_question",
                                "arguments": {
                                    "session_id": game_session_id,
                                    "question": "Was the man in the soup a friend of the one who shot himself?",
                                },
                            },
                            expected_response_substring="Yes",  # Based on simplified judge logic
                        ),
                        BenchmarkTask(
                            name="Game Question (Irrelevant)",
                            prompt=f"Session {game_session_id}: What color was the turtle?",
                            expected_tool_call={
                                "name": "evaluate_question",
                                "arguments": {
                                    "session_id": game_session_id,
                                    "question": "What color was the turtle?",
                                },
                            },
                            expected_response_substring="Irrelevant",  # Based on simplified judge logic
                        ),
                        BenchmarkTask(
                            name="Game Guess (Incorrect)",
                            prompt=f"Session {game_session_id}: My guess is he was allergic to seafood.",
                            expected_tool_call={
                                "name": "check_guess",
                                "arguments": {
                                    "session_id": game_session_id,
                                    "user_guess": "He was allergic to seafood.",
                                },
                            },
                            expected_response_substring="not quite right",
                        ),
                        BenchmarkTask(
                            name="Game Guess (Correct)",
                            prompt=f"Session {game_session_id}: My guess is he realized he ate his friend.",
                            expected_tool_call={
                                "name": "check_guess",
                                "arguments": {
                                    "session_id": game_session_id,
                                    "user_guess": "he realized he ate his friend",
                                },
                            },
                            expected_response_substring="Correct! You've solved the puzzle!",
                        ),
                    ]
                )

            modes = ["Local Only", "Provider Only", "Hybrid"]

            for task in benchmark_tasks:
                print(f"\n--- Running Task: {task.name} ---")
                for mode in modes:
                    print(f"  Mode: {mode}")
                    result = await run_benchmark_task(
                        orchestrator, task, mode, game_session_id
                    )
                    benchmark_results.append(result)
                    print(
                        f"    Latency: {result['latency']:.4f}s, Accuracy: {result['accuracy']:.2f}, Tokens (P): {result['token_usage']['total_tokens']}"
                    )
                    if result.get("error"):
                        print(f"    Error: {result['error']}")
                    # Small delay to avoid hammering local server or API limits
                    await asyncio.sleep(0.5)

    except Exception as e:
        print(f"An error occurred during benchmarking: {e}")
    finally:
        await cleanup_environment(
            dummy_server_path, dummy_config_path, data_dir, dummy_docs_dir
        )
        print("\n--- Benchmarking Complete ---")
        print("\nSummary of Results:")
        for res in benchmark_results:
            print(
                f"[{res['mode']}] {res['task_name']}: Latency={res['latency']:.4f}s, Accuracy={res['accuracy']:.2f}, Tokens (P)={res['token_usage']['total_tokens']}"
            )
            if res.get("error"):
                print(f"  Error: {res['error']}")


async def cleanup_environment(
    dummy_server_path: Path,
    dummy_config_path: Path,
    data_dir: Path,
    dummy_docs_dir: Path,
):
    """Cleans up all dummy files and directories."""
    print("\n--- Cleaning up environment ---")
    cleanup_dummy_mcp_config(dummy_config_path)
    await cleanup_dummy_mcp_server_script(dummy_server_path)
    if data_dir.exists():
        shutil.rmtree(data_dir)
        print(f"Cleaned up data directory: {data_dir}")
    if dummy_docs_dir.exists():
        shutil.rmtree(dummy_docs_dir)
        print(f"Cleaned up dummy docs directory: {dummy_docs_dir}")


if __name__ == "__main__":
    asyncio.run(main())
