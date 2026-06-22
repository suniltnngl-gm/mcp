"""MCP server wrapping Replit REST API v1.

Provides tools to manage Repls (coding environments), deployments,
and users on the Replit platform.

Requires REPLIT_API_KEY in ~/Public/ENV/.env.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.types import CallToolResult, TextContent
from pydantic import BaseModel, Field

_ENV_FILE = Path.home() / "Public" / "ENV" / ".env"
if _ENV_FILE.exists():
    load_dotenv(_ENV_FILE)

_API_KEY = os.environ.get("REPLIT_API_KEY", "")
_BASE = "https://replit.com/api/v1"


class ReplitError(Exception):
    """Wraps a Replit API error response."""


def _headers() -> Dict[str, str]:
    return {"Authorization": f"Bearer {_API_KEY}", "Content-Type": "application/json"}


def _get(path: str) -> Any:
    url = f"{_BASE}{path}"
    resp = httpx.get(url, headers=_headers(), timeout=30)
    if resp.status_code >= 400:
        raise ReplitError(f"GET {url}: {resp.status_code} {resp.text}")
    return resp.json()


def _post(path: str, data: dict) -> Any:
    url = f"{_BASE}{path}"
    resp = httpx.post(url, headers=_headers(), json=data, timeout=30)
    if resp.status_code >= 400:
        raise ReplitError(f"POST {url}: {resp.status_code} {resp.text}")
    return resp.json()


def _patch(path: str, data: dict) -> Any:
    url = f"{_BASE}{path}"
    resp = httpx.patch(url, headers=_headers(), json=data, timeout=30)
    if resp.status_code >= 400:
        raise ReplitError(f"PATCH {url}: {resp.status_code} {resp.text}")
    return resp.json()


def _delete(path: str) -> None:
    url = f"{_BASE}{path}"
    resp = httpx.delete(url, headers=_headers(), timeout=30)
    if resp.status_code >= 400:
        raise ReplitError(f"DELETE {url}: {resp.status_code} {resp.text}")


class CreateReplInput(BaseModel):
    title: str = Field(..., description="Title for the new Repl.")
    language: str = Field(..., description="Language template (python, nodejs, bash, etc.).")
    description: Optional[str] = Field(None, description="Description of the Repl.")
    is_private: bool = Field(True, description="Whether the Repl is private.")


class GetReplInput(BaseModel):
    repl_id: str = Field(..., description="Repl ID or slug.")


class UpdateReplInput(BaseModel):
    repl_id: str = Field(..., description="Repl ID.")
    title: Optional[str] = Field(None, description="New title.")
    description: Optional[str] = Field(None, description="New description.")
    is_private: Optional[bool] = Field(None, description="Privacy setting.")


class DeleteReplInput(BaseModel):
    repl_id: str = Field(..., description="Repl ID to delete.")


class ListReplsInput(BaseModel):
    limit: int = Field(20, description="Results per page.")
    cursor: Optional[str] = Field(None, description="Pagination cursor.")


class DeployReplInput(BaseModel):
    repl_id: str = Field(..., description="Repl ID to deploy.")


class ListDeploymentsInput(BaseModel):
    repl_id: str = Field(..., description="Repl ID.")


class GetDeploymentInput(BaseModel):
    deployment_id: str = Field(..., description="Deployment ID.")


class DeleteDeploymentInput(BaseModel):
    deployment_id: str = Field(..., description="Deployment ID to remove.")


class GetUserInput(BaseModel):
    username: Optional[str] = Field(None, description="Username. Omit to get current user.")


class ListUserReplsInput(BaseModel):
    username: str = Field(..., description="Username to list repls for.")
    limit: int = Field(20, description="Results per page.")
    cursor: Optional[str] = Field(None, description="Pagination cursor.")


class ReplitServer:
    """MCP server wrapping Replit REST API — manage repls, deployments, users."""

    def __init__(self):
        self.mcp_server = FastMCP(name="replit_manager")
        self.mcp_server.add_tool(
            self._list_repls, name="replit_list_repls",
            description="List all Repls accessible to the authenticated user.",
        )
        self.mcp_server.add_tool(
            self._create_repl, name="replit_create_repl",
            description="Create a new Repl (online coding environment).",
        )
        self.mcp_server.add_tool(
            self._get_repl, name="replit_get_repl",
            description="Get details for a specific Repl by ID or slug.",
        )
        self.mcp_server.add_tool(
            self._update_repl, name="replit_update_repl",
            description="Update a Repl's title, description, or privacy.",
        )
        self.mcp_server.add_tool(
            self._delete_repl, name="replit_delete_repl",
            description="Permanently delete a Repl.",
        )
        self.mcp_server.add_tool(
            self._deploy_repl, name="replit_deploy_repl",
            description="Deploy a Repl to production hosting.",
        )
        self.mcp_server.add_tool(
            self._list_deployments, name="replit_list_deployments",
            description="List all deployments for a Repl.",
        )
        self.mcp_server.add_tool(
            self._get_deployment, name="replit_get_deployment",
            description="Get details for a specific deployment.",
        )
        self.mcp_server.add_tool(
            self._delete_deployment, name="replit_delete_deployment",
            description="Remove a deployment from production.",
        )
        self.mcp_server.add_tool(
            self._get_user, name="replit_get_user",
            description="Get current user or a public user profile.",
        )
        self.mcp_server.add_tool(
            self._list_user_repls, name="replit_list_user_repls",
            description="List public Repls for a given username.",
        )

    async def _list_repls(self, input: ListReplsInput) -> CallToolResult:
        try:
            params = f"?limit={input.limit}"
            if input.cursor:
                params += f"&cursor={input.cursor}"
            data = _get(f"/repls{params}")
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(data, indent=2))]
            )
        except ReplitError as e:
            return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

    async def _create_repl(self, input: CreateReplInput) -> CallToolResult:
        try:
            data = _post("/repls", {
                "title": input.title,
                "language": input.language,
                "description": input.description or "",
                "isPrivate": input.is_private,
            })
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(data, indent=2))]
            )
        except ReplitError as e:
            return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

    async def _get_repl(self, input: GetReplInput) -> CallToolResult:
        try:
            data = _get(f"/repls/{input.repl_id}")
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(data, indent=2))]
            )
        except ReplitError as e:
            return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

    async def _update_repl(self, input: UpdateReplInput) -> CallToolResult:
        try:
            body: Dict[str, Any] = {}
            if input.title is not None:
                body["title"] = input.title
            if input.description is not None:
                body["description"] = input.description
            if input.is_private is not None:
                body["isPrivate"] = input.is_private
            data = _patch(f"/repls/{input.repl_id}", body)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(data, indent=2))]
            )
        except ReplitError as e:
            return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

    async def _delete_repl(self, input: DeleteReplInput) -> CallToolResult:
        try:
            _delete(f"/repls/{input.repl_id}")
            return CallToolResult(content=f"Deleted Repl {input.repl_id}.", success=True)
        except ReplitError as e:
            return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

    async def _deploy_repl(self, input: DeployReplInput) -> CallToolResult:
        try:
            data = _post(f"/repls/{input.repl_id}/deployments", {})
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(data, indent=2))]
            )
        except ReplitError as e:
            return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

    async def _list_deployments(self, input: ListDeploymentsInput) -> CallToolResult:
        try:
            data = _get(f"/repls/{input.repl_id}/deployments")
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(data, indent=2))]
            )
        except ReplitError as e:
            return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

    async def _get_deployment(self, input: GetDeploymentInput) -> CallToolResult:
        try:
            data = _get(f"/deployments/{input.deployment_id}")
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(data, indent=2))]
            )
        except ReplitError as e:
            return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

    async def _delete_deployment(self, input: DeleteDeploymentInput) -> CallToolResult:
        try:
            _delete(f"/deployments/{input.deployment_id}")
            return CallToolResult(content=f"Deleted deployment {input.deployment_id}.", success=True)
        except ReplitError as e:
            return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

    async def _get_user(self, input: GetUserInput) -> CallToolResult:
        try:
            path = f"/users/{input.username}" if input.username else "/user"
            data = _get(path)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(data, indent=2))]
            )
        except ReplitError as e:
            return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

    async def _list_user_repls(self, input: ListUserReplsInput) -> CallToolResult:
        try:
            params = f"?limit={input.limit}"
            if input.cursor:
                params += f"&cursor={input.cursor}"
            data = _get(f"/users/{input.username}/repls{params}")
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(data, indent=2))]
            )
        except ReplitError as e:
            return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

    async def run_forever(self):
        print("Replit Manager MCP Server starting...")
        await self.mcp_server.run_stdio_async()


if __name__ == "__main__":
    import asyncio

    async def main():
        if not _API_KEY:
            print("REPLIT_API_KEY not set in ~/Public/ENV/.env")
            return

        server = ReplitServer()
        print("--- Testing ReplitServer ---")
        try:
            user = await server._get_user(GetUserInput())
            print(f"Current user: {user.content}")
        except Exception as e:
            print(f"Error: {e}")

    asyncio.run(main())
