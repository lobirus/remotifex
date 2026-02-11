"""Project request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)


class AIConfigUpdate(BaseModel):
    tool: str | None = Field(None, pattern="^(claude|amp)$")
    model: str | None = None
    allowed_tools: list[str] | None = None
    append_system_prompt: str | None = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: str
    owner_id: str
    status: str
    ai_config: dict
    git: dict
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(BaseModel):
    projects: list[ProjectResponse]
    total: int
