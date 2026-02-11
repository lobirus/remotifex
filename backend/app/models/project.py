"""Project document model."""

import re
from datetime import datetime, timezone


def slugify(name: str) -> str:
    """Convert a project name to a URL-safe slug."""
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def create_project_doc(
    name: str,
    description: str,
    owner_id: str,
) -> dict:
    """Create a project document for MongoDB insertion."""
    now = datetime.now(timezone.utc)
    return {
        "name": name,
        "slug": slugify(name),
        "description": description,
        "owner_id": owner_id,
        "status": "active",
        "git": {
            "repo_url": None,
            "branch": "main",
            "credentials": None,
        },
        "ai_config": {
            "tool": "claude",
            "model": "sonnet",
            "allowed_tools": ["Bash", "Read", "Edit", "Write", "Glob", "Grep"],
            "append_system_prompt": None,
        },
        "created_at": now,
        "updated_at": now,
    }
