"""Claude Code runner: spawns Claude Code as subprocess and streams output."""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone

import redis.asyncio as aioredis
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger("remotifex.worker.claude")

PROJECTS_DATA_DIR = os.environ.get("PROJECTS_DATA_DIR", "/data/projects")


class ClaudeRunner:
    """Executes Claude Code tasks and streams results via Redis pub/sub."""

    def __init__(self, redis_url: str, mongodb_url: str):
        self.redis_url = redis_url
        self.mongodb_url = mongodb_url

    async def execute(self, task: dict) -> None:
        """Execute a Claude Code task.

        Spawns `claude -p` as a subprocess, reads stream-json output line by line,
        and publishes events to Redis pub/sub for real-time delivery to the frontend.
        """
        task_id = task["task_id"]
        project_id = task["project_id"]
        session_id = task["session_id"]
        channel = f"project:{project_id}:chat"

        project_dir = os.path.join(PROJECTS_DATA_DIR, project_id, "staging")
        home_dir = os.path.join(PROJECTS_DATA_DIR, project_id, ".home")

        # Ensure directories exist
        os.makedirs(project_dir, exist_ok=True)
        os.makedirs(home_dir, exist_ok=True)

        # Set up Claude Code API key
        api_key = task.get("api_key")
        if api_key:
            claude_dir = os.path.join(home_dir, ".claude")
            os.makedirs(claude_dir, exist_ok=True)

            # Write API key helper script
            key_script = os.path.join(claude_dir, "anthropic_key.sh")
            with open(key_script, "w") as f:
                f.write(f"#!/bin/sh\necho '{api_key}'\n")
            os.chmod(key_script, 0o700)

            # Write settings.json
            settings_path = os.path.join(claude_dir, "settings.json")
            settings_data = {"apiKeyHelper": f"{claude_dir}/anthropic_key.sh"}
            with open(settings_path, "w") as f:
                json.dump(settings_data, f)

        # Build command
        cmd = [
            "claude",
            "-p", task["prompt"],
            "--output-format", "stream-json",
            "--verbose",
            "--dangerously-skip-permissions",
        ]

        allowed_tools = task.get("allowed_tools")
        if allowed_tools:
            cmd.extend(["--allowedTools", ",".join(allowed_tools)])

        model = task.get("model")
        if model:
            cmd.extend(["--model", model])

        append_prompt = task.get("append_system_prompt")
        if append_prompt:
            cmd.extend(["--append-system-prompt", append_prompt])

        claude_session_id = task.get("claude_session_id")
        if claude_session_id:
            cmd.extend(["--resume", claude_session_id])

        # Environment variables
        env = os.environ.copy()
        env["HOME"] = home_dir
        if api_key:
            env["ANTHROPIC_API_KEY"] = api_key

        r = aioredis.from_url(self.redis_url)
        mongo = AsyncIOMotorClient(self.mongodb_url)
        db = mongo.remotifex

        # Update task status to running
        await db.tasks.update_one(
            {"task_id": task_id},
            {
                "$set": {
                    "status": "running",
                    "started_at": datetime.now(timezone.utc),
                }
            },
        )

        # Publish start event
        await r.publish(
            channel,
            json.dumps(
                {
                    "task_id": task_id,
                    "event": {"type": "task_start", "tool": "claude"},
                }
            ),
        )

        logger.info(f"Starting Claude Code: {' '.join(cmd[:6])}...")
        logger.info(f"Working directory: {project_dir}")

        accumulated_text = ""
        result_session_id = None

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=project_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )

            # Stream stdout line by line (NDJSON)
            async for line in process.stdout:
                line = line.decode("utf-8").strip()
                if not line:
                    continue

                try:
                    event = json.loads(line)
                    parsed = self._parse_event(event)
                    if parsed:
                        await r.publish(
                            channel,
                            json.dumps({"task_id": task_id, "event": parsed}),
                        )

                        # Accumulate text
                        if parsed["type"] == "text":
                            accumulated_text += parsed.get("content", "")

                        # Capture session ID
                        if parsed["type"] == "result" and parsed.get("session_id"):
                            result_session_id = parsed["session_id"]

                except json.JSONDecodeError:
                    logger.debug(f"Non-JSON line: {line[:100]}")

            # Read stderr for debugging
            stderr = await process.stderr.read()
            if stderr:
                logger.debug(f"Claude stderr: {stderr.decode()[:500]}")

            await process.wait()
            return_code = process.returncode

            logger.info(f"Claude Code exited with code {return_code}")

            # Store assistant message
            from app.stream_parser import StreamParser

            await db.chat_messages.insert_one(
                {
                    "session_id": session_id,
                    "project_id": project_id,
                    "role": "assistant",
                    "content": accumulated_text,
                    "tool_calls": [],
                    "metadata": {"return_code": return_code},
                    "created_at": datetime.now(timezone.utc),
                }
            )

            # Update session with Claude session ID for --resume
            if result_session_id:
                await db.chat_sessions.update_one(
                    {"_id": __import__("bson").ObjectId(session_id)},
                    {"$set": {"claude_session_id": result_session_id}},
                )

            # Update task status
            await db.tasks.update_one(
                {"task_id": task_id},
                {
                    "$set": {
                        "status": "completed" if return_code == 0 else "failed",
                        "completed_at": datetime.now(timezone.utc),
                        "result": {"return_code": return_code},
                    }
                },
            )

            # Publish completion event
            await r.publish(
                channel,
                json.dumps(
                    {
                        "task_id": task_id,
                        "event": {
                            "type": "task_complete",
                            "return_code": return_code,
                            "session_id": result_session_id,
                        },
                    }
                ),
            )

        except Exception as e:
            logger.exception(f"Error running Claude Code for task {task_id}")

            await db.tasks.update_one(
                {"task_id": task_id},
                {
                    "$set": {
                        "status": "failed",
                        "completed_at": datetime.now(timezone.utc),
                        "error": str(e),
                    }
                },
            )

            await r.publish(
                channel,
                json.dumps(
                    {
                        "task_id": task_id,
                        "event": {"type": "task_error", "error": str(e)},
                    }
                ),
            )

        finally:
            await r.aclose()
            mongo.close()

    def _parse_event(self, event: dict) -> dict | None:
        """Parse a Claude Code stream-json event into our normalized format."""
        event_type = event.get("type")

        # Content block delta (text streaming)
        if event_type == "content_block_delta":
            delta = event.get("delta", {})
            if delta.get("type") == "text_delta":
                return {"type": "text", "content": delta.get("text", "")}

        # Content block start (tool use)
        if event_type == "content_block_start":
            block = event.get("content_block", {})
            if block.get("type") == "tool_use":
                return {
                    "type": "tool_use_start",
                    "tool": block.get("name"),
                    "id": block.get("id"),
                }

        # Message start
        if event_type == "message_start":
            return {"type": "message_start"}

        # Message delta (stop reason, usage)
        if event_type == "message_delta":
            delta = event.get("delta", {})
            usage = event.get("usage", {})
            return {
                "type": "message_delta",
                "stop_reason": delta.get("stop_reason"),
                "usage": usage,
            }

        # Result message (final output)
        if event_type == "result":
            return {
                "type": "result",
                "session_id": event.get("session_id"),
                "cost_usd": event.get("cost_usd"),
                "duration_ms": event.get("duration_ms"),
                "num_turns": event.get("num_turns"),
            }

        return None
