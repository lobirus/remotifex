"""Security utilities: JWT tokens, password hashing, and encryption."""

import base64
from datetime import datetime, timedelta, timezone

import bcrypt
from cryptography.fernet import Fernet
from jose import JWTError, jwt

from app.config import settings


def _get_fernet() -> Fernet:
    """Get Fernet instance for symmetric encryption."""
    # Derive a valid 32-byte key from the encryption_key setting
    key = settings.encryption_key.encode()
    # Pad or truncate to 32 bytes, then base64 encode for Fernet
    key = key.ljust(32, b"\0")[:32]
    return Fernet(base64.urlsafe_b64encode(key))


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(user_id: str) -> str:
    """Create a JWT access token."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_expire_minutes
    )
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str | None:
    """Decode a JWT token and return the user_id, or None if invalid."""
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        return payload.get("sub")
    except JWTError:
        return None


def encrypt_value(value: str) -> str:
    """Encrypt a string value for storage."""
    f = _get_fernet()
    return f.encrypt(value.encode()).decode()


def decrypt_value(encrypted_value: str) -> str:
    """Decrypt an encrypted string value."""
    f = _get_fernet()
    return f.decrypt(encrypted_value.encode()).decode()
