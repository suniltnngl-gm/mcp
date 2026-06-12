import asyncio
import json
from typing import Dict, List, Any

from mcp.types import Tool  # Use actual mcp types

from src.llm_wrapper.mcp.client_manager import MultiClientManager
from src.llm_wrapper.mcp.config import McpConfig
from src.llm_wrapper.llm.local_client import (
    LocalLLMClient,
)  # Import the real LocalLLMClient
from src.llm_wrapper.llm.provider_client import (
    ProviderLLMClient,
)  # Import the real ProviderLLMClient


class LLMOrchestrator:
    """
    Manages the interaction between local/provider LLMs and MCP tools.
    Acts as the central "brain" for routing, tool selection, and result synthesis.
    """

    _multi_client_manager: MultiClientManager
    _local_llm: LocalLLMClient
    _provider_llm: ProviderLLMClient  # Type hint for the real ProviderLLMClient

    def __init__(self, mcp_config: McpConfig):
        self._multi_client_manager = MultiClientManager(mcp_config)
        self._local_llm = LocalLLMClient()  # Instantiate the real LocalLLMClient
        self._provider_llm = (
            ProviderLLMClient()
        )  # Instantiate the real ProviderLLMClient

    async def __aenter__(self):
        """Connects the MultiClientManager on entering the context."""
        await (
            self._multi_client_manager.__aenter__()
        )  # Manually call __aenter__ for MultiClientManager
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Disconnects the MultiClientManager on exiting the context."""
        await self._multi_client_manager.__aexit__(
            exc_type, exc_val, exc_tb
        )  # Manually call __aexit__

    async def _format_tools_for_llm(self, tools: List[Tool]) -> List[Dict[str, Any]]:
        """
        Converts MCP Tool objects into a format suitable for LLMs (e.g., Gemini SDK Function Declarations).
        This method is adapted from src/llm_wrapper/core/enricher.py's enrich_for_sdk.
        """
        formatted_tools = []
        for tool in tools:
            formatted_tools.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    # Assuming inputSchema has a model_json_schema method or similar
                    # For mcp.types.Tool, inputSchema is already a dict
                    "parameters": tool.inputSchema,
                }
            )
        return formatted_tools

    async def orchestrate_response(
        self, prompt: str, use_local_llm: bool = True, use_provider_llm: bool = True
    ) -> Dict[str, Any]:
        """
        Orchestrates the LLM response, potentially involving parallel execution
        and tool utilization.
        """
        all_available_tools = await self._multi_client_manager.list_tools()
        formatted_tools = await self._format_tools_for_llm(all_available_tools)

        local_llm_task = None
        provider_llm_task = None

        results = {}

        if use_local_llm:
            local_llm_task = self._local_llm.generate(prompt, tools=formatted_tools)
        if use_provider_llm:
            provider_llm_task = self._provider_llm.generate(
                prompt, tools=formatted_tools
            )

        if local_llm_task and provider_llm_task:
            local_result, provider_result = await asyncio.gather(
                local_llm_task, provider_llm_task
            )
            results["local_llm_response"] = local_result
            results["provider_llm_response"] = provider_result
        elif local_llm_task:
            results["local_llm_response"] = await local_llm_task
        elif provider_llm_task:
            results["provider_llm_response"] = await provider_llm_task
        else:
            return {"error": "No LLM client enabled for orchestration."}

        # --- Tool Call Handling (Simplified for now) ---
        # This part would be significantly more complex in a real scenario,
        # involving parsing LLM output for tool calls, executing them via
        # MultiClientManager, and feeding results back.
        if (
            "local_llm_response" in results
            and "tool_call" in results["local_llm_response"]
        ):
            tool_call = results["local_llm_response"]["tool_call"]
            print(
                f"Orchestrator: Local LLM requested tool call: {tool_call['name']}({tool_call['arguments']})"
            )
            try:
                tool_result = await self._multi_client_manager.call_tool(
                    tool_call["name"],
                    tool_call["arguments"],
                    server_name="local_dev_server",  # Assuming local tool for local LLM
                )
                results["local_llm_tool_result"] = tool_result.content
                print(
                    f"Orchestrator: Local LLM tool call result: {tool_result.content}"
                )
            except Exception as e:
                results["local_llm_tool_error"] = str(e)
                print(f"Orchestrator: Error executing local LLM tool call: {e}")

        if (
            "provider_llm_response" in results
            and "tool_call" in results["provider_llm_response"]
        ):
            tool_call = results["provider_llm_response"]["tool_call"]
            print(
                f"Orchestrator: Provider LLM requested tool call: {tool_call['name']}({tool_call['arguments']})"
            )
            try:
                tool_result = await self._multi_client_manager.call_tool(
                    tool_call["name"],
                    tool_call["arguments"],
                    server_name="remote_prod_server",  # Assuming remote tool for provider LLM
                )
                results["provider_llm_tool_result"] = tool_result.content
                print(
                    f"Orchestrator: Provider LLM tool call result: {tool_result.content}"
                )
            except Exception as e:
                results["provider_llm_tool_error"] = str(e)
                print(f"Orchestrator: Error executing provider LLM tool call: {e}")

        return results


if __name__ == "__main__":
    from src.llm_wrapper.mcp.config import (
        create_dummy_mcp_config,
        cleanup_dummy_mcp_config,
    )
    from src.llm_wrapper.mcp.stdio_client import (
        create_dummy_mcp_server_script,
        cleanup_dummy_mcp_server_script,
    )
    from pathlib import Path
    import os
    import shutil

    async def main():
        print("--- Testing LLMOrchestrator with GameRulesServer Integration ---")

        # Setup dummy MCP config and server
        dummy_server_path = Path("my_mcp_server.py")
        await create_dummy_mcp_server_script(dummy_server_path)
        dummy_config_path = Path("mcp.json")
        create_dummy_mcp_config(dummy_config_path, dummy_server_path)
        # Load the newly created dummy MCP config
        from src.llm_wrapper.mcp.config import load_mcp_config

        mcp_config = load_mcp_config(dummy_config_path)

        # Ensure the data directory exists for doc_manager_server's DB and game_rules_server's DB
        data_dir = Path("./data")
        data_dir.mkdir(exist_ok=True)
        # Set the DB_PATH environment variables for the subprocesses
        os.environ["DB_PATH"] = str(data_dir / "docs.db")  # For DocManagerServer
        os.environ["GAME_RULES_DB_PATH"] = str(
            data_dir / "game_rules.db"
        )  # For GameRulesServer

        if mcp_config:
            async with LLMOrchestrator(mcp_config) as orchestrator:
                # --- Test DocManagerServer Tools (existing tests) ---
                print("\n--- Testing DocManagerServer via Orchestrator ---")
                dummy_docs_dir = Path("./dummy_docs_for_dm")
                dummy_docs_dir.mkdir(exist_ok=True)
                (dummy_docs_dir / "project_info.md").write_text(
                    "# Project Info\nThis project aims to build a hybrid LLM system."
                )
                (dummy_docs_dir / "requirements.txt").write_text(
                    "ollama\nopenai\nmcp\nmarkdown"
                )

                print(f"\nIndexing directory: {dummy_docs_dir}")
                index_tool_call_sim = {
                    "tool_call": {
                        "name": "index_directory",
                        "arguments": {
                            "directory_path": str(dummy_docs_dir),
                            "include_patterns": ["*.md", "*.txt"],
                        },
                    }
                }
                print("Simulating local LLM requesting index_directory tool...")
                index_result_content = (
                    await orchestrator._multi_client_manager.call_tool(
                        index_tool_call_sim["tool_call"]["name"],
                        index_tool_call_sim["tool_call"]["arguments"],
                        server_name="doc_manager",
                    )
                )
                print(f"Index Tool Result: {index_result_content.content}")

                print("\nSearching context for 'hybrid LLM system':")
                search_tool_call_sim = {
                    "tool_call": {
                        "name": "search_context",
                        "arguments": {"query": "hybrid LLM system", "limit": 1},
                    }
                }
                print("Simulating local LLM requesting search_context tool...")
                search_result_content = (
                    await orchestrator._multi_client_manager.call_tool(
                        search_tool_call_sim["tool_call"]["name"],
                        search_tool_call_sim["tool_call"]["arguments"],
                        server_name="doc_manager",
                    )
                )
                print(f"Search Tool Result: {search_result_content.content}")
                if search_result_content.resources:
                    print(
                        f"Resources: {json.dumps(json.loads(search_result_content.resources[0].data), indent=2)}"
                    )

                # --- Test GameRulesServer Tools ---
                print("\n--- Testing GameRulesServer via Orchestrator ---")

                print("\nStarting 'turtle_soup' game:")
                start_game_call_sim = {
                    "tool_call": {
                        "name": "start_game",
                        "arguments": {"puzzle_id": "turtle_soup"},
                    }
                }
                start_game_result = await orchestrator._multi_client_manager.call_tool(
                    start_game_call_sim["tool_call"]["name"],
                    start_game_call_sim["tool_call"]["arguments"],
                    server_name="game_rules_manager",
                )
                print(f"Start Game Result: {start_game_result.content}")
                if (
                    start_game_result.resources
                ):  # Check if resources exist before trying to parse
                    session_data = json.loads(start_game_result.resources[0].data)
                    game_session_id = session_data["session_id"]
                    print(f"Game Session ID: {game_session_id}")
                else:
                    game_session_id = None
                    print("Could not get game session ID from start_game result.")

                if game_session_id:
                    print("\nEvaluating a question (Yes):")
                    evaluate_question_call_sim = {
                        "tool_call": {
                            "name": "evaluate_question",
                            "arguments": {
                                "session_id": game_session_id,
                                "question": "Was the man killed because of the soup?",
                            },
                        }
                    }
                    evaluate_result = (
                        await orchestrator._multi_client_manager.call_tool(
                            evaluate_question_call_sim["tool_call"]["name"],
                            evaluate_question_call_sim["tool_call"]["arguments"],
                            server_name="game_rules_manager",
                        )
                    )
                    print(f"Evaluate Question Result: {evaluate_result.content}")

                    print("\nChecking a guess (Incorrect):")
                    check_guess_call_sim = {
                        "tool_call": {
                            "name": "check_guess",
                            "arguments": {
                                "session_id": game_session_id,
                                "user_guess": "He was allergic to shellfish.",
                            },
                        }
                    }
                    check_guess_result = (
                        await orchestrator._multi_client_manager.call_tool(
                            check_guess_call_sim["tool_call"]["name"],
                            check_guess_call_sim["tool_call"]["arguments"],
                            server_name="game_rules_manager",
                        )
                    )
                    print(f"Check Guess Result: {check_guess_result.content}")

                print("\n--- Testing Orchestrator's LLM paths (original tests) ---")
                print("\nOrchestrating response (both LLMs):")
                response = await orchestrator.orchestrate_response(
                    "Tell me about something and use_tool"
                )
                print("\nOrchestration Result:")
                print(json.dumps(response, indent=2))

                print("\nOrchestrating response (local LLM only):")
                response_local = await orchestrator.orchestrate_response(
                    "Local only query and use_tool", use_provider_llm=False
                )
                print("\nOrchestration Result (Local only):")
                print(json.dumps(response_local, indent=2))

                print("\nOrchestrating response (provider LLM only):")
                response_provider = await orchestrator.orchestrate_response(
                    "Provider only query and use_tool", use_local_llm=False
                )
                print("\nOrchestration Result (Provider only):")
                print(json.dumps(response_provider, indent=2))

                print("\nOrchestrating response (no tool call):")
                response_no_tool = await orchestrator.orchestrate_response(
                    "Just a regular query."
                )
                print("\nOrchestration Result (No tool):")
                print(json.dumps(response_no_tool, indent=2))

        else:
            print("Failed to load MCP configuration, cannot test LLMOrchestrator.")

        # Cleanup dummy files
        cleanup_dummy_mcp_config(dummy_config_path)
        await cleanup_dummy_mcp_server_script(dummy_server_path)
        if data_dir.exists():
            shutil.rmtree(data_dir)
            print(f"Cleaned up data directory: {data_dir}")
        if dummy_docs_dir.exists():
            shutil.rmtree(dummy_docs_dir)
            print(f"Cleaned up dummy docs directory: {dummy_docs_dir}")

    asyncio.run(main())
