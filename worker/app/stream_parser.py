"""Stream parser: normalizes stream-json events from Claude Code and Amp."""


class StreamParser:
    """Normalizes streaming events from different AI tools into a unified format.

    Unified event types:
    - text: Text content being streamed
    - tool_use_start: Start of a tool call
    - tool_use_input: Tool call input data
    - tool_result: Tool call result
    - message_start: Start of a new message
    - message_delta: Message metadata update
    - task_start: Task execution started
    - task_complete: Task finished
    - task_error: Task failed
    - result: Final result with session info
    """

    @staticmethod
    def parse_claude_event(raw: dict) -> dict | None:
        """Parse a Claude Code stream-json event."""
        event_type = raw.get("type")

        if event_type == "content_block_delta":
            delta = raw.get("delta", {})
            if delta.get("type") == "text_delta":
                return {"type": "text", "content": delta.get("text", "")}
            if delta.get("type") == "input_json_delta":
                return {
                    "type": "tool_use_input",
                    "partial_json": delta.get("partial_json", ""),
                }

        if event_type == "content_block_start":
            block = raw.get("content_block", {})
            if block.get("type") == "tool_use":
                return {
                    "type": "tool_use_start",
                    "tool": block.get("name"),
                    "id": block.get("id"),
                }
            if block.get("type") == "text":
                return {"type": "text_start"}

        if event_type == "content_block_stop":
            return {"type": "content_block_stop", "index": raw.get("index")}

        if event_type == "message_start":
            return {"type": "message_start"}

        if event_type == "message_delta":
            return {
                "type": "message_delta",
                "stop_reason": raw.get("delta", {}).get("stop_reason"),
                "usage": raw.get("usage", {}),
            }

        if event_type == "message_stop":
            return {"type": "message_stop"}

        if event_type == "result":
            return {
                "type": "result",
                "session_id": raw.get("session_id"),
                "cost_usd": raw.get("cost_usd"),
                "duration_ms": raw.get("duration_ms"),
                "num_turns": raw.get("num_turns"),
            }

        return None

    @staticmethod
    def parse_amp_event(raw: dict) -> dict | None:
        """Parse an Amp stream-json event.

        TODO: Implement when Amp support is added in Phase 5.
        """
        return None
