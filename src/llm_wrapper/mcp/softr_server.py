"""MCP server wrapping Softr Studio API and Database API.

Provides tools for managing users via Studio API and performing
CRUD on database tables via Tables API.

API keys loaded from ~/Public/ENV/.env via dotenv.
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

_API_KEY = os.environ.get("SOFTR_API_KEY", "")
_STUDIO_API = "https://studio-api.softr.io/v1/api"
_TABLES_API = "https://tables-api.softr.io/api/v1"


class SoftrError(Exception):
    """Wraps a Softr API error response."""


def _headers() -> Dict[str, str]:
    return {
        "Softr-Api-Key": _API_KEY,
        "Content-Type": "application/json",
    }


def _get(path: str, base: str = _TABLES_API) -> Any:
    url = f"{base}{path}"
    resp = httpx.get(url, headers=_headers(), timeout=30)
    if resp.status_code >= 400:
        raise SoftrError(f"GET {url}: {resp.status_code} {resp.text}")
    return resp.json()


def _post(path: str, data: dict, base: str = _TABLES_API) -> Any:
    url = f"{base}{path}"
    resp = httpx.post(url, headers=_headers(), json=data, timeout=30)
    if resp.status_code >= 400:
        raise SoftrError(f"POST {url}: {resp.status_code} {resp.text}")
    return resp.json()


def _patch(path: str, data: dict, base: str = _TABLES_API) -> Any:
    url = f"{base}{path}"
    resp = httpx.patch(url, headers=_headers(), json=data, timeout=30)
    if resp.status_code >= 400:
        raise SoftrError(f"PATCH {url}: {resp.status_code} {resp.text}")
    return resp.json()


def _delete(path: str, base: str = _TABLES_API) -> None:
    url = f"{base}{path}"
    resp = httpx.delete(url, headers=_headers(), timeout=30)
    if resp.status_code >= 400:
        raise SoftrError(f"DELETE {url}: {resp.status_code} {resp.text}")


class ListDatabasesInput(BaseModel):
    pass


class ListTablesInput(BaseModel):
    database_id: str = Field(..., description="Database ID from list_databases.")


class QueryRecordsInput(BaseModel):
    database_id: str = Field(..., description="Database ID.")
    table_id: str = Field(..., description="Table ID.")
    limit: int = Field(10, description="Max records to return.")
    field_names: bool = Field(True, description="Return field names instead of keys.")


class CreateRecordInput(BaseModel):
    database_id: str = Field(..., description="Database ID.")
    table_id: str = Field(..., description="Table ID.")
    fields: Dict[str, Any] = Field(..., description="Field key-value pairs.")


class UpdateRecordInput(BaseModel):
    database_id: str = Field(..., description="Database ID.")
    table_id: str = Field(..., description="Table ID.")
    record_id: str = Field(..., description="Record ID.")
    fields: Dict[str, Any] = Field(..., description="Fields to update.")


class DeleteRecordInput(BaseModel):
    database_id: str = Field(..., description="Database ID.")
    table_id: str = Field(..., description="Table ID.")
    record_id: str = Field(..., description="Record ID to delete.")


class CreateUserInput(BaseModel):
    full_name: str = Field(..., description="User's full name.")
    email: str = Field(..., description="User's email address.")
    password: str = Field(..., description="Initial password.")
    domain: str = Field(..., description="Softr app domain (subdomain.softr.app).")


class GetUserInput(BaseModel):
    email: str = Field(..., description="User's email address.")
    domain: str = Field(..., description="Softr app domain.")


class DeleteUserInput(BaseModel):
    email: str = Field(..., description="User's email address.")
    domain: str = Field(..., description="Softr app domain.")


class SoftrServer:
    """MCP server wrapping Softr APIs — database CRUD and user management."""

    def __init__(self):
        self.mcp_server = FastMCP(name="softr_manager")
        self.mcp_server.add_tool(
            self._list_databases, name="softr_list_databases",
            description="List all Softr databases accessible to the API key.",
        )
        self.mcp_server.add_tool(
            self._list_tables, name="softr_list_tables",
            description="List tables in a Softr database.",
        )
        self.mcp_server.add_tool(
            self._query_records, name="softr_query_records",
            description="Query records from a Softr table.",
        )
        self.mcp_server.add_tool(
            self._create_record, name="softr_create_record",
            description="Create a new record in a Softr table.",
        )
        self.mcp_server.add_tool(
            self._update_record, name="softr_update_record",
            description="Update an existing record in a Softr table.",
        )
        self.mcp_server.add_tool(
            self._delete_record, name="softr_delete_record",
            description="Delete a record from a Softr table.",
        )
        self.mcp_server.add_tool(
            self._create_user, name="softr_create_user",
            description="Create a user account in a Softr app.",
        )
        self.mcp_server.add_tool(
            self._get_user, name="softr_get_user",
            description="Look up a user by email in a Softr app.",
        )
        self.mcp_server.add_tool(
            self._delete_user, name="softr_delete_user",
            description="Delete a user from a Softr app.",
        )

    async def _list_databases(self) -> CallToolResult:
        try:
            data = _get("/databases")
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(data, indent=2))]
            )
        except SoftrError as e:
            return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

    async def _list_tables(self, input: ListTablesInput) -> CallToolResult:
        try:
            data = _get(f"/databases/{input.database_id}/tables")
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(data, indent=2))]
            )
        except SoftrError as e:
            return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

    async def _query_records(self, input: QueryRecordsInput) -> CallToolResult:
        try:
            path = f"/databases/{input.database_id}/tables/{input.table_id}/records"
            params = f"?limit={input.limit}&fieldNames={str(input.field_names).lower()}"
            data = _get(path + params)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(data, indent=2))]
            )
        except SoftrError as e:
            return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

    async def _create_record(self, input: CreateRecordInput) -> CallToolResult:
        try:
            path = f"/databases/{input.database_id}/tables/{input.table_id}/records"
            data = _post(path, {"fields": input.fields})
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(data, indent=2))]
            )
        except SoftrError as e:
            return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

    async def _update_record(self, input: UpdateRecordInput) -> CallToolResult:
        try:
            path = f"/databases/{input.database_id}/tables/{input.table_id}/records/{input.record_id}"
            data = _patch(path, {"fields": input.fields})
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(data, indent=2))]
            )
        except SoftrError as e:
            return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

    async def _delete_record(self, input: DeleteRecordInput) -> CallToolResult:
        try:
            path = f"/databases/{input.database_id}/tables/{input.table_id}/records/{input.record_id}"
            _delete(path)
            return CallToolResult(content=f"Deleted record {input.record_id}.", success=True)
        except SoftrError as e:
            return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

    async def _create_user(self, input: CreateUserInput) -> CallToolResult:
        try:
            data = _post(
                "/users",
                {
                    "full_name": input.full_name,
                    "email": input.email,
                    "password": input.password,
                    "generate_magic_link": False,
                },
                base=_STUDIO_API,
            )
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(data, indent=2))]
            )
        except SoftrError as e:
            return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

    async def _get_user(self, input: GetUserInput) -> CallToolResult:
        try:
            data = _get(f"/users/{input.email}", base=_STUDIO_API)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(data, indent=2))]
            )
        except SoftrError as e:
            return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

    async def _delete_user(self, input: DeleteUserInput) -> CallToolResult:
        try:
            _delete(f"/users/{input.email}", base=_STUDIO_API)
            return CallToolResult(content=f"Deleted user {input.email}.", success=True)
        except SoftrError as e:
            return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

    async def run_forever(self):
        print("Softr Manager MCP Server starting...")
        await self.mcp_server.run_stdio_async()


if __name__ == "__main__":
    import asyncio

    async def main():
        if not _API_KEY:
            print("SOFTR_API_KEY not set in ~/Public/ENV/.env")
            return

        server = SoftrServer()
        print("--- Testing SoftrServer ---")
        try:
            dbs = await server._list_databases()
            print(f"Databases: {dbs.content}")
        except Exception as e:
            print(f"Error: {e}")

    asyncio.run(main())
