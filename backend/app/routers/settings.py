"""Settings routes: setup status, AI config, domain config, access config, updates."""

import json
import logging
import socket
import uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import APP_VERSION
from app.db.mongodb import get_db
from app.dependencies import get_admin_user
from app.models.settings import create_default_settings_doc
from app.schemas.settings import (
    AISettingsUpdate,
    AccessSettingsUpdate,
    DomainSettingsUpdate,
    ServerInfoResponse,
    SetupCompleteRequest,
    SetupStatusResponse,
    UpdateStatusResponse,
    VersionInfoResponse,
)
from app.utils.security import encrypt_value

UPDATE_DIR = Path("/app/.update")

logger = logging.getLogger(__name__)

router = APIRouter()


async def _get_or_create_settings(db: AsyncIOMotorDatabase) -> dict:
    """Get global settings, creating default if not exists."""
    doc = await db.settings.find_one({"type": "global"})
    if doc is None:
        doc = create_default_settings_doc()
        await db.settings.insert_one(doc)
        doc = await db.settings.find_one({"type": "global"})
    return doc


async def _detect_public_ip() -> str | None:
    """Detect the server's public IP address."""
    # Try external service first
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get("https://api.ipify.org")
            if resp.status_code == 200:
                return resp.text.strip()
    except Exception:
        pass

    # Fallback: socket-based detection (gets local/LAN IP)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


async def _write_env_value(key: str, value: str) -> None:
    """Write or update a key=value pair in the .env file."""
    import os
    from pathlib import Path

    # In Docker, .env is mounted at /app/.env or project root
    env_path = Path(os.environ.get("ENV_FILE_PATH", "/app/.env"))
    if not env_path.exists():
        env_path.write_text(f"{key}={value}\n")
        return

    lines = env_path.read_text().splitlines()
    found = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(f"{key}=") or stripped.startswith(f"{key} ="):
            lines[i] = f"{key}={value}"
            found = True
            break
    if not found:
        lines.append(f"{key}={value}")

    env_path.write_text("\n".join(lines) + "\n")


async def _reload_caddy_config(settings_doc: dict) -> None:
    """Reload Caddy configuration via its admin API."""
    access = settings_doc.get("access", {})
    domain_section = settings_doc.get("domain", {})

    remotifex_domain = access.get("remotifex_domain")
    port = access.get("port", 80)
    base_domain = domain_section.get("base_domain")
    ssl_email = domain_section.get("ssl_email")

    # Build Caddy JSON config
    routes = []

    # Main Remotifex app route
    listen_match = remotifex_domain if remotifex_domain else ""

    # Backend API route
    routes.append({
        "match": [{"host": [remotifex_domain] if remotifex_domain else [], "path": ["/api/*"]}],
        "handle": [{"handler": "reverse_proxy", "upstreams": [{"dial": "backend:8000"}]}],
    })
    # WebSocket route
    routes.append({
        "match": [{"host": [remotifex_domain] if remotifex_domain else [], "path": ["/ws/*"]}],
        "handle": [{"handler": "reverse_proxy", "upstreams": [{"dial": "backend:8000"}]}],
    })
    # Frontend route (catch-all for the host)
    routes.append({
        "match": [{"host": [remotifex_domain] if remotifex_domain else []}],
        "handle": [{"handler": "reverse_proxy", "upstreams": [{"dial": "frontend:3000"}]}],
    })

    # Project subdomain routes (if base_domain configured)
    if base_domain:
        routes.append({
            "match": [{"host": [f"*.{base_domain}"]}],
            "handle": [{"handler": "reverse_proxy", "upstreams": [{"dial": "backend:8000"}]}],
        })

    # Clean up match objects — remove empty host arrays
    for route in routes:
        for match in route.get("match", []):
            if "host" in match and not match["host"]:
                del match["host"]

    caddy_config = {
        "apps": {
            "http": {
                "servers": {
                    "main": {
                        "listen": [f":{port}"],
                        "routes": routes,
                    }
                }
            }
        }
    }

    # Add TLS config if we have a domain and SSL email
    if (remotifex_domain or base_domain) and ssl_email:
        caddy_config["apps"]["tls"] = {
            "automation": {
                "policies": [{
                    "issuers": [{
                        "module": "acme",
                        "email": ssl_email,
                    }]
                }]
            }
        }
        # Switch to 443 if using TLS
        if port == 80:
            caddy_config["apps"]["http"]["servers"]["main"]["listen"] = [":443", ":80"]

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "http://caddy:2019/load",
                json=caddy_config,
                headers={"Content-Type": "application/json"},
            )
            if resp.status_code != 200:
                logger.warning("Caddy config reload failed: %s %s", resp.status_code, resp.text)
    except Exception as e:
        logger.warning("Could not reach Caddy admin API: %s", e)


@router.get("/setup-status", response_model=SetupStatusResponse)
async def get_setup_status(
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Check if initial setup has been completed. No auth required."""
    user_count = await db.users.count_documents({})
    settings_doc = await db.settings.find_one({"type": "global"})
    setup_done = user_count > 0 and (
        settings_doc is not None and settings_doc.get("setup_completed", False)
    )
    return SetupStatusResponse(setup_completed=setup_done)


@router.get("/server-info", response_model=ServerInfoResponse)
async def get_server_info(
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """Get server IP and current access configuration. No auth required."""
    ip = await _detect_public_ip()

    doc = await db.settings.find_one({"type": "global"})
    access = (doc or {}).get("access", {})
    remotifex_domain = access.get("remotifex_domain")
    port = access.get("port", 80)

    # Build current URL
    if remotifex_domain:
        scheme = "https" if port == 443 else "http"
        current_url = f"{scheme}://{remotifex_domain}"
        if port not in (80, 443):
            current_url += f":{port}"
    elif ip:
        current_url = f"http://{ip}"
        if port != 80:
            current_url += f":{port}"
    else:
        current_url = f"http://localhost:{port}" if port != 80 else "http://localhost"

    return ServerInfoResponse(
        ip=ip,
        port=port,
        remotifex_domain=remotifex_domain,
        current_url=current_url,
    )


@router.post("/complete-setup")
async def complete_setup(
    request: SetupCompleteRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_admin_user),
):
    """Complete the setup wizard by saving AI, domain, and access settings."""
    await _get_or_create_settings(db)
    from datetime import datetime, timezone

    update = {"setup_completed": True, "updated_at": datetime.now(timezone.utc)}

    # AI settings
    ai_data = request.ai_settings.model_dump(exclude_none=True)
    if "claude_api_key" in ai_data:
        update["ai.claude_api_key_encrypted"] = encrypt_value(ai_data["claude_api_key"])
    if "claude_default_model" in ai_data:
        update["ai.claude_default_model"] = ai_data["claude_default_model"]
    if "default_tool" in ai_data:
        update["ai.default_tool"] = ai_data["default_tool"]
    if "amp_api_key" in ai_data:
        update["ai.amp_api_key_encrypted"] = encrypt_value(ai_data["amp_api_key"])

    # Domain settings (project base domain)
    if request.domain_settings:
        domain_data = request.domain_settings.model_dump(exclude_none=True)
        if "base_domain" in domain_data:
            update["domain.base_domain"] = domain_data["base_domain"]
        if "ssl_email" in domain_data:
            update["domain.ssl_email"] = domain_data["ssl_email"]

    # Access settings (Remotifex itself)
    if request.access_settings:
        access_data = request.access_settings.model_dump(exclude_none=True)
        if "remotifex_domain" in access_data:
            update["access.remotifex_domain"] = access_data["remotifex_domain"]
            await _write_env_value("DOMAIN", access_data["remotifex_domain"])
        if "port" in access_data:
            update["access.port"] = access_data["port"]
            await _write_env_value("PORT", str(access_data["port"]))

    await db.settings.update_one({"type": "global"}, {"$set": update})

    # Reload Caddy with new config
    updated_doc = await db.settings.find_one({"type": "global"})
    await _reload_caddy_config(updated_doc)

    return {"status": "ok"}


@router.get("")
async def get_settings(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_admin_user),
):
    """Get current settings (admin only). Secrets are masked."""
    doc = await _get_or_create_settings(db)
    doc.pop("_id", None)

    # Mask encrypted values
    if doc.get("ai", {}).get("claude_api_key_encrypted"):
        doc["ai"]["claude_api_key_set"] = True
        del doc["ai"]["claude_api_key_encrypted"]
    else:
        doc["ai"]["claude_api_key_set"] = False
        doc["ai"].pop("claude_api_key_encrypted", None)

    if doc.get("ai", {}).get("amp_api_key_encrypted"):
        doc["ai"]["amp_api_key_set"] = True
        del doc["ai"]["amp_api_key_encrypted"]
    else:
        doc["ai"]["amp_api_key_set"] = False
        doc["ai"].pop("amp_api_key_encrypted", None)

    return doc


@router.patch("/ai")
async def update_ai_settings(
    request: AISettingsUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_admin_user),
):
    """Update AI settings (admin only)."""
    from datetime import datetime, timezone

    update = {"updated_at": datetime.now(timezone.utc)}
    data = request.model_dump(exclude_none=True)

    if "claude_api_key" in data:
        update["ai.claude_api_key_encrypted"] = encrypt_value(data["claude_api_key"])
    if "claude_default_model" in data:
        update["ai.claude_default_model"] = data["claude_default_model"]
    if "default_tool" in data:
        update["ai.default_tool"] = data["default_tool"]
    if "amp_api_key" in data:
        update["ai.amp_api_key_encrypted"] = encrypt_value(data["amp_api_key"])

    await db.settings.update_one({"type": "global"}, {"$set": update})
    return {"status": "ok"}


@router.patch("/domain")
async def update_domain_settings(
    request: DomainSettingsUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_admin_user),
):
    """Update project domain settings (admin only)."""
    from datetime import datetime, timezone

    update = {"updated_at": datetime.now(timezone.utc)}
    data = request.model_dump(exclude_none=True)

    if "base_domain" in data:
        update["domain.base_domain"] = data["base_domain"]
    if "ssl_email" in data:
        update["domain.ssl_email"] = data["ssl_email"]

    await db.settings.update_one({"type": "global"}, {"$set": update})

    # Reload Caddy to pick up new domain config
    updated_doc = await db.settings.find_one({"type": "global"})
    await _reload_caddy_config(updated_doc)

    return {"status": "ok"}


@router.patch("/access")
async def update_access_settings(
    request: AccessSettingsUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: dict = Depends(get_admin_user),
):
    """Update Remotifex access settings — domain and port (admin only)."""
    from datetime import datetime, timezone

    update = {"updated_at": datetime.now(timezone.utc)}
    data = request.model_dump(exclude_none=True)

    if "remotifex_domain" in data:
        update["access.remotifex_domain"] = data["remotifex_domain"]
        await _write_env_value("DOMAIN", data["remotifex_domain"])
    if "port" in data:
        update["access.port"] = data["port"]
        await _write_env_value("PORT", str(data["port"]))

    await db.settings.update_one({"type": "global"}, {"$set": update})

    # Reload Caddy with new config
    updated_doc = await db.settings.find_one({"type": "global"})
    await _reload_caddy_config(updated_doc)

    return {"status": "ok"}


# --- Version & Update endpoints ---


@router.get("/version", response_model=VersionInfoResponse)
async def get_version_info(
    check_latest: bool = False,
    user: dict = Depends(get_admin_user),
):
    """Get current version and optionally check for latest available."""
    result = VersionInfoResponse(current_version=APP_VERSION)

    if check_latest:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    "https://api.github.com/repos/remotifex/remotifex/releases/latest",
                    headers={"Accept": "application/vnd.github.v3+json"},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    latest = data["tag_name"].lstrip("v")
                    result.latest_version = latest
                    result.update_available = latest != APP_VERSION
                    result.release_notes = data.get("body")
                    result.release_url = data.get("html_url")
        except Exception:
            logger.debug("Failed to check GitHub for latest version")

    return result


@router.post("/update")
async def trigger_update(
    user: dict = Depends(get_admin_user),
):
    """Trigger a system update by writing a signal file for the host-side watcher."""
    if not UPDATE_DIR.exists():
        raise HTTPException(
            status_code=503,
            detail="Update service not configured. Run: curl -fsSL https://update.remotifex.com | sh",
        )

    # Check if an update is already in progress
    status_file = UPDATE_DIR / "status.json"
    if status_file.exists():
        try:
            status = json.loads(status_file.read_text())
            if status.get("status") == "in_progress":
                raise HTTPException(status_code=409, detail="Update already in progress")
        except (json.JSONDecodeError, OSError):
            pass

    # Clear previous status and log
    for f in (status_file, UPDATE_DIR / "output.log"):
        if f.exists():
            f.unlink()

    # Write trigger file
    update_id = str(uuid.uuid4())
    trigger = {
        "id": update_id,
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "requested_by": str(user.get("_id", "")),
    }
    (UPDATE_DIR / "trigger.json").write_text(json.dumps(trigger))

    return {"status": "triggered", "update_id": update_id}


@router.get("/update/status", response_model=UpdateStatusResponse)
async def get_update_status(
    include_log: bool = False,
    log_offset: int = 0,
    user: dict = Depends(get_admin_user),
):
    """Get current update status by reading the status file written by update.sh."""
    result = UpdateStatusResponse(status="idle")

    status_file = UPDATE_DIR / "status.json"
    if status_file.exists():
        try:
            data = json.loads(status_file.read_text())
            result.status = data.get("status", "idle")
            result.step = data.get("step")
            result.current_version = data.get("current_version")
            result.new_version = data.get("new_version")
            result.started_at = data.get("started_at")
            result.completed_at = data.get("completed_at")
            error = data.get("error")
            result.error = error if error else None
        except (json.JSONDecodeError, OSError):
            pass

    if include_log:
        log_file = UPDATE_DIR / "output.log"
        if log_file.exists():
            try:
                lines = log_file.read_text().splitlines()
                result.log = "\n".join(lines[log_offset:])
                result.log_lines = len(lines)
            except OSError:
                pass

    return result
