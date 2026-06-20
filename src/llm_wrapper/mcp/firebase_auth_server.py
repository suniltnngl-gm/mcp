"""MCP server wrapping Firebase Auth token verification as tools.

Stateless per CEG protocol — accepts tokens via tool arguments,
validates with Firebase Admin SDK, returns identity context.

Tools:
  verify_auth_token  — Verify a Firebase ID token, return user identity
  get_user_claims    — Fetch custom claims for a Firebase Auth UID
"""

import json
import os
import sys
from typing import Optional

# Allow cross-project import of firebase_app agent modules
_AGENT_PATH = os.path.expanduser("~/Public/Workspace/firebase-app")
if _AGENT_PATH not in sys.path:
    sys.path.insert(0, _AGENT_PATH)

from mcp.server.fastmcp import FastMCP
from mcp.types import CallToolResult, TextContent

from llm_wrapper.mcp.firebase_auth_middleware import (
    AuthError,
    ServiceAccountNotFound,
    TokenExpired,
    TokenInvalid,
    get_user_claims,
    verify_token,
)

_server = FastMCP(
    "firebase-auth",
    instructions="Firebase Auth identity verification for MCP — verify tokens, fetch claims",
)


def _error_result(error: AuthError) -> CallToolResult:
    return CallToolResult(
        content=[TextContent(type="text", text=str(error))],
        success=False,
    )


@_server.tool(
    name="verify_auth_token",
    description="Verify a Firebase ID token and return user identity context (UID, email, phone, claims)",
)
async def verify_auth_token(
    id_token: str = ...,
) -> CallToolResult:
    try:
        ctx = verify_token(id_token)
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(ctx.to_dict(), indent=2))],
            success=True,
        )
    except ServiceAccountNotFound as e:
        return _error_result(e)
    except TokenExpired as e:
        return _error_result(e)
    except TokenInvalid as e:
        return _error_result(e)
    except AuthError as e:
        return _error_result(e)


@_server.tool(
    name="get_user_claims",
    description="Fetch custom claims for a Firebase Auth user by UID",
)
async def get_claims(uid: str = ...) -> CallToolResult:
    try:
        claims = get_user_claims(uid)
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(claims, indent=2))],
            success=True,
        )
    except AuthError as e:
        return _error_result(e)


if __name__ == "__main__":
    _server.run(transport="stdio")
