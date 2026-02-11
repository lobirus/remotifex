"""Settings request/response schemas."""

from pydantic import BaseModel, Field


class SetupStatusResponse(BaseModel):
    setup_completed: bool


class AISettingsUpdate(BaseModel):
    default_tool: str | None = Field(None, pattern="^(claude|amp)$")
    claude_api_key: str | None = None
    claude_default_model: str | None = None
    amp_api_key: str | None = None


class DomainSettingsUpdate(BaseModel):
    base_domain: str | None = None
    ssl_email: str | None = None


class AccessSettingsUpdate(BaseModel):
    remotifex_domain: str | None = None
    port: int | None = Field(None, ge=1, le=65535)


class ServerInfoResponse(BaseModel):
    ip: str | None
    port: int
    remotifex_domain: str | None
    current_url: str


class SetupCompleteRequest(BaseModel):
    ai_settings: AISettingsUpdate
    domain_settings: DomainSettingsUpdate | None = None
    access_settings: AccessSettingsUpdate | None = None


class VersionInfoResponse(BaseModel):
    current_version: str
    latest_version: str | None = None
    update_available: bool = False
    release_notes: str | None = None
    release_url: str | None = None


class UpdateStatusResponse(BaseModel):
    status: str  # idle | in_progress | completed | failed
    step: str | None = None
    current_version: str | None = None
    new_version: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    error: str | None = None
    log: str | None = None
    log_lines: int | None = None
