from typing import Any, Dict
from src.llm_wrapper.core.config import settings
from src.llm_wrapper.core.router import RequestRouter
from src.llm_wrapper.providers.local_client import LocalCLIClient
from src.llm_wrapper.providers.remote_client import ProviderSDKClient
from src.llm_wrapper.mcp.manager import MCPManager
from src.llm_wrapper.core.enricher import ContextEnricher  # Import ContextEnricher
from src.data_models.llm_wrapper import InferenceRequest, InferenceResponse
import logging
import datetime

logger = logging.getLogger(__name__)


class MCPOrchestrator:
    """
    The main orchestrator for the LLM wrapper. It acts as the "brain" of the wrapper,
    coordinating between MCP servers, local LLMs, and provider LLMs.
    """

    def __init__(self):
        """
        Initializes the MCPOrchestrator, loading configuration and setting up
        core components.
        """
        self.settings = settings
        logger.info(
            f"MCPOrchestrator initialized with settings: {self.settings.dict()}"
        )

        # Instantiate clients and pass them to the router
        self.local_client = LocalCLIClient()
        self.provider_client = ProviderSDKClient()
        self.router = RequestRouter(self.local_client, self.provider_client)

        # Initialize MCP Manager and Context Enricher
        self.mcp_manager = MCPManager()
        self.enricher = ContextEnricher()  # Instantiate ContextEnricher

        logger.info("Core components initialized.")

    async def startup(self):
        """
        Performs startup operations, such as connecting to MCP servers.
        """
        logger.info("Starting up MCPOrchestrator...")
        # TODO: Load MCP server configurations from a dedicated config file
        await self.mcp_manager.register_server(
            "filesystem",
            "npx",
            [
                "-y",
                "@modelcontextprotocol/server-filesystem",
                "/tmp",
            ],  # Use /tmp for now as a safe default
        )
        # Register other servers as needed

        await self.mcp_manager.initialize_all()
        logger.info("MCPOrchestrator startup complete.")

    async def shutdown(self):
        """
        Performs graceful shutdown operations, such as disconnecting from MCP servers.
        """
        logger.info("Shutting down MCPOrchestrator...")
        await self.mcp_manager.shutdown()
        logger.info("MCPOrchestrator shutdown complete.")

    async def health_check(self) -> Dict[str, Any]:
        """
        Performs a health check of the orchestrator and its integrated components.

        Returns:
            Dict[str, Any]: A dictionary containing health status of various components.
        """
        status = {
            "status": "UP",
            "timestamp": datetime.datetime.now().isoformat(),
            "config_loaded": bool(self.settings),
            "router_status": "OK",
            "local_llm_client_status": "OK",
            "provider_llm_client_status": "OK",
            "mcp_manager_status": "OK"
            if self.mcp_manager._is_initialized
            else "NOT_INITIALIZED",
        }
        logger.info(f"Health check performed: {status}")
        return status

    async def process_request(self, request: InferenceRequest) -> InferenceResponse:
        """
        Processes an incoming LLM inference request, routing it to the appropriate LLM with fallback.
        It also enriches the request with MCP tools based on the chosen client.
        """
        logger.info(
            f"Processing request for prompt: '{request.prompt[:50]}...' (model_id: {request.model_id or 'auto'})"
        )

        # 1. Discover tools from all servers
        tools_map = await self.mcp_manager.get_all_tools()
        flattened_tools = [t for tools in tools_map.values() for t in tools]

        # 2. Determine which route to take
        client, clean_prompt = self.router.determine_route(request.prompt)

        # 3. Enrich the request based on the client type
        if isinstance(client, ProviderSDKClient):
            # SDK uses native tool calling
            gemini_tools = self.enricher.enrich_for_sdk(flattened_tools)
            response = await client.generate(
                clean_prompt,
                parameters=request.parameters.dict(),
                context=request.context,
                tools=gemini_tools,
            )
        else:  # LocalCLIClient
            # CLI uses a system prompt injection
            system_instruction = self.enricher.enrich_for_cli(tools_map)
            full_prompt = f"{system_instruction}\n\nUSER REQUEST: {clean_prompt}"
            response = await client.generate(
                full_prompt,
                parameters=request.parameters.dict(),
                context=request.context,
            )

        return response
