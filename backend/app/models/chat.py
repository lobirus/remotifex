"""Chat session and message document models."""

from datetime import datetime, timezone


def create_chat_session_doc(
    project_id: str,
    title: str = "New conversation",
) -> dict:
    """Create a chat session document for MongoDB insertion."""
    now = datetime.now(timezone.utc)
    return {
        "project_id": project_id,
        "claude_session_id": None,
        "title": title,
        "status": "active",
        "created_at": now,
        "updated_at": now,
    }


def create_chat_message_doc(
    session_id: str,
    project_id: str,
    role: str,
    content: str,
    tool_calls: list | None = None,
    metadata: dict | None = None,
) -> dict:
    """Create a chat message document for MongoDB insertion."""
    return {
        "session_id": session_id,
        "project_id": project_id,
        "role": role,
        "content": content,
        "tool_calls": tool_calls or [],
        "metadata": metadata or {},
        "created_at": datetime.now(timezone.utc),
    }
