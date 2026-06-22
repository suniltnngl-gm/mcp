"""Firestore-backed document storage for MCP document manager.

Replaces local SQLite with Firestore for real-time document sync
and Firebase Auth integration across projects.

Collection: mcp_documents
Document ID: file path (hashed for Firestore key rules)
"""

import hashlib
import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_SERVICE_ACCOUNT_PATH = os.environ.get(
    "FIREBASE_SERVICE_ACCOUNT_PATH",
    os.path.expanduser("~/Public/Workspace/firebase-app/agent/service-account.json"),
)

_COLLECTION = "mcp_documents"


class FirestoreInitError(Exception):
    """Raised when Firebase Admin SDK cannot be initialized."""


def _make_doc_id(file_path: str) -> str:
    """Firestore document IDs cannot contain `/` — hash the path."""
    return hashlib.sha256(file_path.encode()).hexdigest()[:32]


def _init_admin():
    import firebase_admin
    from firebase_admin import credentials

    try:
        return firebase_admin.get_app()
    except ValueError:
        pass

    if not os.path.exists(_SERVICE_ACCOUNT_PATH):
        raise FirestoreInitError(
            f"Firebase service account not found at {_SERVICE_ACCOUNT_PATH}. "
            "Set FIREBASE_SERVICE_ACCOUNT_PATH env var or place the key file."
        )

    cred = credentials.Certificate(_SERVICE_ACCOUNT_PATH)
    return firebase_admin.initialize_app(cred)


def _db():
    _init_admin()
    from firebase_admin import firestore
    return firestore.client()


def index_document(
    file_path: str,
    title: str,
    content: str,
    summary: str = "",
    user_id: str = "",
) -> str:
    """Store or update an indexed document in Firestore.

    Args:
        file_path: Absolute path to the source file.
        title: Display title (usually file stem).
        content: Extracted plain text content.
        summary: Optional first-line summary.
        user_id: Firebase Auth UID of the indexing user.

    Returns:
        The Firestore document ID.
    """
    doc_id = _make_doc_id(file_path)
    data = {
        "path": file_path,
        "title": title[:500],
        "summary": summary[:1000],
        "content": content,
        "indexed_at": datetime.now(timezone.utc).isoformat(),
        "userId": user_id,
    }
    _db().collection(_COLLECTION).document(doc_id).set(data)
    return doc_id


def search_documents(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Search indexed documents by content.

    Firestore lacks full-text search, so this fetches recent documents
    and applies client-side pattern matching — suitable for local doc counts.

    Returns:
        List of dicts with path, title, summary, snippet.
    """
    docs = (
        _db()
        .collection(_COLLECTION)
        .order_by("indexed_at", direction="desc")
        .limit(200)
        .stream()
    )

    results: List[Dict[str, Any]] = []
    query_lower = query.lower()

    for snap in docs:
        data = snap.to_dict()
        content: str = data.get("content") or ""
        if query_lower not in content.lower():
            continue

        pos = content.lower().find(query_lower)
        start = max(0, pos - 100)
        end = min(len(content), pos + len(query) + 200)
        snippet = content[start:end].strip()
        if end < len(content):
            snippet += "..."

        results.append({
            "path": data.get("path", ""),
            "title": data.get("title", ""),
            "summary": data.get("summary", ""),
            "snippet": snippet,
            "indexed_at": data.get("indexed_at", ""),
        })

        if len(results) >= limit:
            break

    return results


def list_documents(limit: int = 50) -> List[Dict[str, Any]]:
    """List all indexed documents (metadata only, no content)."""
    docs = (
        _db()
        .collection(_COLLECTION)
        .order_by("indexed_at", direction="desc")
        .limit(limit)
        .stream()
    )
    return [
        {
            "path": d.to_dict().get("path", d.id),
            "title": d.to_dict().get("title", ""),
            "summary": d.to_dict().get("summary", ""),
            "indexed_at": d.to_dict().get("indexed_at", ""),
            "userId": d.to_dict().get("userId", ""),
        }
        for d in docs
    ]


def delete_document(file_path: str) -> bool:
    """Remove a document from the index by file path."""
    doc_id = _make_doc_id(file_path)
    snap = _db().collection(_COLLECTION).document(doc_id).get()
    if not snap.exists:
        return False
    _db().collection(_COLLECTION).document(doc_id).delete()
    return True


def get_document_count() -> int:
    """Return total number of indexed documents."""
    docs = _db().collection(_COLLECTION).limit(1000).stream()
    return len([d for d in docs])


def clear_all(user_id: Optional[str] = None) -> int:
    """Delete all documents, optionally filtered by userId.

    Returns count of deleted documents.
    """
    ref = _db().collection(_COLLECTION)
    if user_id:
        docs = ref.where("userId", "==", user_id).stream()
    else:
        docs = ref.stream()

    batch = _db().batch()
    count = 0
    for snap in docs:
        batch.delete(snap.reference)
        count += 1
        if count % 500 == 0:
            batch.commit()
            batch = _db().batch()

    if count % 500 != 0:
        batch.commit()
    return count
