"""WebSocket handler for real-time chat streaming."""

import asyncio
import json

import redis.asyncio as aioredis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.config import settings
from app.utils.security import decode_access_token

router = APIRouter()


@router.websocket("/chat/{project_id}")
async def chat_websocket(
    websocket: WebSocket,
    project_id: str,
):
    """WebSocket endpoint for streaming AI chat output.

    Subscribes to Redis pub/sub channel for the project and forwards
    all events to the connected client.
    """
    # Authenticate via query parameter
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing authentication token")
        return

    user_id = decode_access_token(token)
    if user_id is None:
        await websocket.close(code=4001, reason="Invalid token")
        return

    await websocket.accept()

    r = aioredis.from_url(settings.redis_url)
    pubsub = r.pubsub()
    channel = f"project:{project_id}:chat"
    await pubsub.subscribe(channel)

    try:
        while True:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True, timeout=1.0
            )
            if message and message["type"] == "message":
                data = message["data"]
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                await websocket.send_text(data)

            # Small sleep to prevent busy-waiting
            await asyncio.sleep(0.01)
    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.aclose()
        await r.aclose()
