"""The Claude Code guard: reads a tool call as JSON and refuses non-practice recipients."""

from typing import Any

from mailroom.policy import recipient_allowed

GUARDED_TOOLS = {"send-email", "send-batch-emails"}


def guard_decision(payload: dict[str, Any]) -> tuple[int, str]:
    """Return (exit code, message). Exit code 2 blocks the tool call."""
    if payload.get("tool_name") not in GUARDED_TOOLS:
        return 0, ""
    tool_input = payload.get("tool_input") or {}
    addresses: list[str] = []
    for field in ("to", "cc", "bcc"):
        value = tool_input.get(field)
        if isinstance(value, str):
            addresses.append(value)
        elif isinstance(value, list):
            addresses.extend(str(item) for item in value)
    for address in addresses:
        if not recipient_allowed(address):
            return 2, f"Blocked: {address} is not a practice address. Use @example.com or @resend.dev."
    return 0, ""
