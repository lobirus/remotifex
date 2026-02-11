"""File browser routes: list, read, write files within project directories."""

import mimetypes
import os
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

from app.config import settings
from app.db.mongodb import get_db
from app.dependencies import get_current_user

router = APIRouter()

# Maximum file size for reading/writing (10 MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


class FileEntry(BaseModel):
    name: str
    type: str  # "file" or "directory"
    size: int
    modified: datetime


class DirectoryListing(BaseModel):
    path: str
    entries: list[FileEntry]


class FileContent(BaseModel):
    path: str
    content: str
    language: str | None = None
    size: int


class FileWriteRequest(BaseModel):
    path: str = Field(..., min_length=1)
    content: str


def _resolve_project_path(project_id: str, env: str, file_path: str) -> str:
    """Resolve and validate a file path within a project directory.

    Prevents path traversal attacks by ensuring the resolved path
    stays within the project directory.
    """
    if env not in ("staging", "prod"):
        raise HTTPException(status_code=400, detail="Invalid environment")

    base_dir = os.path.join(settings.projects_data_dir, project_id, env)
    # Normalize and join the path
    resolved = os.path.normpath(os.path.join(base_dir, file_path.lstrip("/")))

    # Prevent path traversal
    if not resolved.startswith(os.path.normpath(base_dir)):
        raise HTTPException(status_code=403, detail="Access denied: path traversal")

    return resolved


def _detect_language(file_path: str) -> str | None:
    """Detect editor language from file extension."""
    ext_map = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "javascriptreact",
        ".tsx": "typescriptreact",
        ".vue": "vue",
        ".html": "html",
        ".css": "css",
        ".scss": "scss",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".md": "markdown",
        ".sh": "shell",
        ".bash": "shell",
        ".sql": "sql",
        ".go": "go",
        ".rs": "rust",
        ".rb": "ruby",
        ".php": "php",
        ".java": "java",
        ".toml": "toml",
        ".xml": "xml",
        ".dockerfile": "dockerfile",
        ".env": "dotenv",
    }
    _, ext = os.path.splitext(file_path.lower())
    name = os.path.basename(file_path.lower())

    if name == "dockerfile":
        return "dockerfile"
    if name == "makefile":
        return "makefile"

    return ext_map.get(ext)


@router.get("/list", response_model=DirectoryListing)
async def list_directory(
    project_id: str,
    path: str = Query(default="/"),
    env: str = Query(default="staging"),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """List files and directories at the given path."""
    # Verify project ownership
    project = await db.projects.find_one(
        {"_id": ObjectId(project_id), "owner_id": user["_id"]}
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    resolved = _resolve_project_path(project_id, env, path)

    if not os.path.isdir(resolved):
        raise HTTPException(status_code=404, detail="Directory not found")

    entries = []
    try:
        for entry_name in sorted(os.listdir(resolved)):
            # Skip hidden files like .git internals, but keep .env, .gitignore etc.
            if entry_name in (".git",):
                continue

            entry_path = os.path.join(resolved, entry_name)
            stat = os.stat(entry_path)
            entries.append(
                FileEntry(
                    name=entry_name,
                    type="directory" if os.path.isdir(entry_path) else "file",
                    size=stat.st_size,
                    modified=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
                )
            )
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")

    return DirectoryListing(path=path, entries=entries)


@router.get("/content", response_model=FileContent)
async def read_file(
    project_id: str,
    path: str = Query(...),
    env: str = Query(default="staging"),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Read a file's content."""
    project = await db.projects.find_one(
        {"_id": ObjectId(project_id), "owner_id": user["_id"]}
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    resolved = _resolve_project_path(project_id, env, path)

    if not os.path.isfile(resolved):
        raise HTTPException(status_code=404, detail="File not found")

    file_size = os.path.getsize(resolved)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 10 MB)")

    # Check if file is binary
    mime_type, _ = mimetypes.guess_type(resolved)
    if mime_type and not mime_type.startswith("text") and mime_type != "application/json":
        raise HTTPException(
            status_code=415, detail="Binary files cannot be displayed"
        )

    try:
        with open(resolved, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        raise HTTPException(status_code=415, detail="File is not valid UTF-8 text")

    return FileContent(
        path=path,
        content=content,
        language=_detect_language(path),
        size=file_size,
    )


@router.put("/content")
async def write_file(
    project_id: str,
    request: FileWriteRequest,
    env: str = Query(default="staging"),
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Write content to a file."""
    project = await db.projects.find_one(
        {"_id": ObjectId(project_id), "owner_id": user["_id"]}
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    resolved = _resolve_project_path(project_id, env, request.path)

    # Create parent directories if needed
    os.makedirs(os.path.dirname(resolved), exist_ok=True)

    with open(resolved, "w", encoding="utf-8") as f:
        f.write(request.content)

    return {"status": "ok", "path": request.path}
