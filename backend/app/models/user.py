"""User document model."""

from datetime import datetime, timezone


def create_user_doc(
    username: str,
    password_hash: str,
    is_admin: bool = False,
) -> dict:
    """Create a user document for MongoDB insertion."""
    now = datetime.now(timezone.utc)
    return {
        "username": username,
        "password_hash": password_hash,
        "is_admin": is_admin,
        "created_at": now,
        "updated_at": now,
    }
