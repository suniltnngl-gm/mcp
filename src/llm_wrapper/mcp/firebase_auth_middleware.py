"""Firebase Auth verification middleware for MCP servers.

Stateless token verification using Firebase Admin SDK.
Designed for Cyclomatic Complexity 10–15, modular claim mapping.
"""

import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

_SERVICE_ACCOUNT_PATH = os.environ.get(
    "FIREBASE_SERVICE_ACCOUNT_PATH",
    os.path.expanduser("~/Public/Workspace/firebase-app/agent/service-account.json"),
)


class AuthError(Exception):
    """Raised on token verification failures. Message is parseable JSON."""

    def __init__(self, code: str, message: str, status: int = 401):
        self.code = code
        self.http_status = status
        detail = json.dumps({"error": {"code": code, "message": message}})
        super().__init__(detail)


class TokenExpired(AuthError):
    def __init__(self):
        super().__init__("TOKEN_EXPIRED", "Firebase ID token has expired")


class TokenInvalid(AuthError):
    def __init__(self, detail: str = "Token verification failed"):
        super().__init__("TOKEN_INVALID", detail)


class ServiceAccountNotFound(AuthError):
    def __init__(self):
        super().__init__(
            "SERVICE_ACCOUNT_MISSING",
            "Firebase service account key not found",
            status=503,
        )


@dataclass
class IdentityContext:
    uid: str
    email: Optional[str] = None
    email_verified: bool = False
    phone: Optional[str] = None
    claims: Dict[str, Any] = None
    tenant: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uid": self.uid,
            "email": self.email,
            "email_verified": self.email_verified,
            "phone": self.phone,
            "claims": self.claims or {},
            "tenant": self.tenant,
        }


_admin_app = None


def _init_admin():
    global _admin_app
    if _admin_app is not None:
        return _admin_app

    if not os.path.exists(_SERVICE_ACCOUNT_PATH):
        raise ServiceAccountNotFound()

    import firebase_admin
    from firebase_admin import credentials

    try:
        _admin_app = firebase_admin.get_app()
        return _admin_app
    except ValueError:
        pass

    try:
        cred = credentials.Certificate(_SERVICE_ACCOUNT_PATH)
        _admin_app = firebase_admin.initialize_app(cred)
        return _admin_app
    except Exception as e:
        raise AuthError(
            "ADMIN_INIT_FAILED", f"Failed to initialize Firebase Admin: {e}", status=503
        )


def verify_token(id_token: str) -> IdentityContext:
    """Verify a Firebase ID token and return the identity context.

    Args:
        id_token: Firebase ID token (JWT) from the client.

    Returns:
        IdentityContext with verified UID, email, phone, and custom claims.

    Raises:
        TokenExpired: Token has expired.
        TokenInvalid: Token is malformed or invalid.
        ServiceAccountNotFound: Firebase Admin SDK not configured.
    """
    _init_admin()
    from firebase_admin import auth

    try:
        decoded = auth.verify_id_token(id_token, check_revoked=True)
    except auth.ExpiredIdTokenError:
        raise TokenExpired()
    except auth.RevokedIdTokenError:
        raise TokenInvalid("Token has been revoked")
    except auth.UserDisabledError:
        raise TokenInvalid("User account is disabled")
    except ValueError as e:
        raise TokenInvalid(str(e))
    except Exception as e:
        raise TokenInvalid(f"Unexpected verification error: {e}")

    return IdentityContext(
        uid=decoded.get("uid", ""),
        email=decoded.get("email"),
        email_verified=decoded.get("email_verified", False),
        phone=decoded.get("phone_number"),
        claims=decoded.get("claims", decoded.get("firebase", {}).get("claims", {})),
        tenant=decoded.get("tenant"),
    )


def get_user_claims(uid: str) -> Dict[str, Any]:
    """Fetch custom claims for a Firebase Auth user by UID.

    Args:
        uid: Firebase Auth UID.

    Returns:
        Dict of custom claims, or empty dict if none set.
    """
    _init_admin()
    from firebase_admin import auth

    try:
        user = auth.get_user(uid)
        return user.custom_claims or {}
    except auth.UserNotFoundError:
        raise AuthError("USER_NOT_FOUND", f"No user with UID: {uid}", status=404)
    except Exception as e:
        raise AuthError("CLAIMS_FETCH_FAILED", str(e), status=503)
