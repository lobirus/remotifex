"""MongoDB connection management using Motor async driver."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings

client: AsyncIOMotorClient | None = None
db: AsyncIOMotorDatabase | None = None


async def connect_db() -> None:
    """Connect to MongoDB and initialize indexes."""
    global client, db
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client.remotifex
    await _create_indexes()


async def close_db() -> None:
    """Close MongoDB connection."""
    global client
    if client:
        client.close()


async def _create_indexes() -> None:
    """Create required database indexes."""
    assert db is not None

    await db.users.create_index("username", unique=True)
    await db.projects.create_index("slug", unique=True)
    await db.environments.create_index(
        [("project_id", 1), ("type", 1)], unique=True
    )
    await db.environments.create_index("domain", unique=True, sparse=True)
    await db.chat_sessions.create_index("project_id")
    await db.chat_messages.create_index([("session_id", 1), ("created_at", 1)])
    await db.chat_messages.create_index("project_id")
    await db.deploys.create_index([("project_id", 1), ("version", 1)], unique=True)
    await db.tasks.create_index("task_id", unique=True)
    await db.tasks.create_index("project_id")
    await db.settings.create_index("type", unique=True)


def get_db() -> AsyncIOMotorDatabase:
    """Get database instance. Must be called after connect_db()."""
    assert db is not None, "Database not connected. Call connect_db() first."
    return db
