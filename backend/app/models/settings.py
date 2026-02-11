"""Settings document model."""

from datetime import datetime, timezone


def create_default_settings_doc() -> dict:
    """Create default global settings document."""
    return {
        "type": "global",
        "setup_completed": False,
        "ai": {
            "default_tool": "claude",
            "claude_api_key_encrypted": None,
            "claude_default_model": "sonnet",
            "amp_api_key_encrypted": None,
        },
        "email": {
            "provider": None,
            "smtp": {
                "host": None,
                "port": 587,
                "username": None,
                "password_encrypted": None,
            },
            "resend": {"api_key_encrypted": None},
            "postmark": {"api_key_encrypted": None},
        },
        "domain": {
            "base_domain": None,
            "ssl_email": None,
        },
        "access": {
            "remotifex_domain": None,
            "port": 80,
        },
        "api": {
            "enabled": False,
            "api_keys": [],
        },
        "mcp": {
            "enabled": False,
        },
        "updated_at": datetime.now(timezone.utc),
    }
