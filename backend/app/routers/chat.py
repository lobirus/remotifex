"""Chat routes: send messages, list sessions and messages."""

import json
import uuid

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import settings
from app.db.mongodb import get_db
from app.dependencies import get_current_user
from app.models.chat import create_chat_message_doc, create_chat_session_doc
from app.schemas.chat import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatSendResponse,
    ChatSessionResponse,
)

router = APIRouter()


def _message_to_response(doc: dict) -> ChatMessageResponse:
    return ChatMessageResponse(
        id=str(doc["_id"]),
        session_id=doc["session_id"],
        project_id=doc["project_id"],
        role=doc["role"],
        content=doc["content"],
        tool_calls=doc.get("tool_calls", []),
        metadata=doc.get("metadata", {}),
        created_at=doc["created_at"],
    )


def _session_to_response(doc: dict) -> ChatSessionResponse:
    return ChatSessionResponse(
        id=str(doc["_id"]),
        project_id=doc["project_id"],
        title=doc["title"],
        status=doc["status"],
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )


@router.get("/sessions", response_model=list[ChatSessionResponse])
async def list_sessions(
    project_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """List chat sessions for a project."""
    # Verify project ownership
    project = await db.projects.find_one(
        {"_id": ObjectId(project_id), "owner_id": user["_id"]}
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    cursor = db.chat_sessions.find({"project_id": project_id}).sort("created_at", -1)
    sessions = await cursor.to_list(length=50)
    return [_session_to_response(s) for s in sessions]


@router.get("/messages", response_model=list[ChatMessageResponse])
async def list_messages(
    project_id: str,
    session_id: str | None = None,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """List messages for a project, optionally filtered by session."""
    project = await db.projects.find_one(
        {"_id": ObjectId(project_id), "owner_id": user["_id"]}
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    query = {"project_id": project_id}
    if session_id:
        query["session_id"] = session_id

    cursor = db.chat_messages.find(query).sort("created_at", 1)
    messages = await cursor.to_list(length=200)
    return [_message_to_response(m) for m in messages]


@router.post("/messages", response_model=ChatSendResponse)
async def send_message(
    project_id: str,
    request: ChatMessageCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """Send a chat message and trigger an AI task."""
    project = await db.projects.find_one(
        {"_id": ObjectId(project_id), "owner_id": user["_id"]}
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get or create session
    if request.session_id:
        session = await db.chat_sessions.find_one(
            {"_id": ObjectId(request.session_id), "project_id": project_id}
        )
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")
        session_id = request.session_id
    else:
        # Create new session
        session_doc = create_chat_session_doc(
            project_id=project_id,
            title=request.content[:50],
        )
        result = await db.chat_sessions.insert_one(session_doc)
        session_id = str(result.inserted_id)

    # Store user message
    message_doc = create_chat_message_doc(
        session_id=session_id,
        project_id=project_id,
        role="user",
        content=request.content,
    )
    msg_result = await db.chat_messages.insert_one(message_doc)
    message_id = str(msg_result.inserted_id)

    # Load global settings for API key
    global_settings = await db.settings.find_one({"type": "global"})
    api_key = None
    if global_settings and global_settings.get("ai", {}).get("claude_api_key_encrypted"):
        from app.utils.security import decrypt_value

        api_key = decrypt_value(global_settings["ai"]["claude_api_key_encrypted"])

    # Get session's claude_session_id for --resume
    session = await db.chat_sessions.find_one({"_id": ObjectId(session_id)})
    claude_session_id = session.get("claude_session_id") if session else None

    # Submit task to Redis queue
    task_id = str(uuid.uuid4())
    ai_config = project.get("ai_config", {})

    task = {
        "task_id": task_id,
        "project_id": project_id,
        "session_id": session_id,
        "prompt": request.content,
        "tool": ai_config.get("tool", "claude"),
        "model": ai_config.get("model", "sonnet"),
        "api_key": api_key,
        "allowed_tools": ai_config.get(
            "allowed_tools", ["Bash", "Read", "Edit", "Write", "Glob", "Grep"]
        ),
        "append_system_prompt": ai_config.get("append_system_prompt"),
        "claude_session_id": claude_session_id,
    }

    import redis.asyncio as aioredis

    r = aioredis.from_url(settings.redis_url)
    await r.lpush("ai_tasks", json.dumps(task))
    await r.aclose()

    # Store task record
    from datetime import datetime, timezone

    await db.tasks.insert_one(
        {
            "task_id": task_id,
            "project_id": project_id,
            "session_id": session_id,
            "status": "queued",
            "tool": ai_config.get("tool", "claude"),
            "prompt": request.content,
            "started_at": None,
            "completed_at": None,
            "result": None,
            "error": None,
            "usage": {"tokens_in": 0, "tokens_out": 0, "cost_usd": 0},
            "created_at": datetime.now(timezone.utc),
        }
    )

    return ChatSendResponse(
        task_id=task_id,
        message_id=message_id,
        session_id=session_id,
    )
