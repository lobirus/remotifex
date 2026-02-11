"""Worker main loop: consumes AI tasks from Redis queue."""

import asyncio
import json
import logging
import os
import signal
import sys

import redis.asyncio as aioredis

from app.claude_runner import ClaudeRunner

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("remotifex.worker")

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
MONGODB_URL = os.environ.get("MONGODB_URL", "mongodb://mongo:27017/remotifex")

shutdown = False


def handle_signal(sig, frame):
    global shutdown
    logger.info("Shutdown signal received, finishing current task...")
    shutdown = True


async def main():
    """Main worker loop: pop tasks from Redis and execute them."""
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    logger.info("Remotifex Worker starting...")
    logger.info(f"Redis: {REDIS_URL}")
    logger.info(f"MongoDB: {MONGODB_URL}")

    r = aioredis.from_url(REDIS_URL)

    # Test Redis connection
    await r.ping()
    logger.info("Connected to Redis")

    claude_runner = ClaudeRunner(redis_url=REDIS_URL, mongodb_url=MONGODB_URL)

    while not shutdown:
        try:
            # Blocking pop with 5 second timeout
            result = await r.brpop("ai_tasks", timeout=5)
            if result is None:
                continue

            _, task_json = result
            task = json.loads(task_json)

            logger.info(
                f"Received task {task['task_id']} for project {task['project_id']}"
            )

            # Execute the task
            tool = task.get("tool", "claude")
            if tool == "claude":
                await claude_runner.execute(task)
            else:
                logger.warning(f"Unknown tool: {tool}, skipping task")

        except aioredis.ConnectionError:
            logger.error("Lost Redis connection, retrying in 5s...")
            await asyncio.sleep(5)
        except Exception:
            logger.exception("Error processing task")
            await asyncio.sleep(1)

    await r.aclose()
    logger.info("Worker shut down cleanly")


if __name__ == "__main__":
    asyncio.run(main())
