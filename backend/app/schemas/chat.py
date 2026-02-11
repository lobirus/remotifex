"""Chat request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class ChatMessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=50000)
    session_id: str | None = None


class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    project_id: str
    role: str
    content: str
    tool_calls: list[dict]
    metadata: dict
    created_at: datetime


class ChatSessionResponse(BaseModel):
    id: str
    project_id: str
    title: str
    status: str
    created_at: datetime
    updated_at: datetime


class ChatSendResponse(BaseModel):
    task_id: str
    message_id: str
    session_id: str
