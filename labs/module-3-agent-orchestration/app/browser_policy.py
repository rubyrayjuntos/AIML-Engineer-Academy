"""Least-privilege policy for browser tool calls."""
from __future__ import annotations

from urllib.parse import urlparse

from app.browser_models import BrowserAction, BrowserToolCall

ALLOWED_ORIGINS = frozenset(
    {
        "https://vendor.example",
        "https://vendor.example/",
    }
)

# Consequential writes that must stop at HITL before mutating the page.
HITL_WRITE_ACTIONS = frozenset({BrowserAction.CLICK})

# Type is reversible form fill — allowed without HITL but still a write-capable tool.
REVERSIBLE_WRITES = frozenset({BrowserAction.TYPE})


def origin_allowed(url: str, allowlist: frozenset[str] | set[str] = ALLOWED_ORIGINS) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    origin = f"{parsed.scheme}://{parsed.netloc}"
    return origin in allowlist or f"{origin}/" in allowlist


def classify_tool(call: BrowserToolCall) -> dict:
    """Return policy decision without executing anything."""
    if call.action == BrowserAction.EVALUATE_JS:
        return {
            "allowed": False,
            "status": "rejected",
            "reason": "evaluate_js is disabled — use typed tools only",
            "requires_hitl": False,
        }
    if call.action == BrowserAction.NAVIGATE:
        if not call.url:
            return {
                "allowed": False,
                "status": "rejected",
                "reason": "navigate requires url",
                "requires_hitl": False,
            }
        if not origin_allowed(call.url):
            return {
                "allowed": False,
                "status": "rejected",
                "reason": f"origin not allowlisted: {call.url}",
                "requires_hitl": False,
            }
        return {"allowed": True, "status": "ready", "reason": "navigate ok", "requires_hitl": False}

    if call.action in HITL_WRITE_ACTIONS:
        # Click on Continue/submit is consequential — require approval unless already flagged.
        needs = call.requires_approval or True
        return {
            "allowed": True,
            "status": "awaiting_approval" if needs else "ready",
            "reason": "consequential click requires HITL",
            "requires_hitl": True,
        }

    if call.action in REVERSIBLE_WRITES:
        if call.requires_approval:
            return {
                "allowed": True,
                "status": "awaiting_approval",
                "reason": "caller requested HITL for type",
                "requires_hitl": True,
            }
        return {"allowed": True, "status": "ready", "reason": "reversible type", "requires_hitl": False}

    # scroll / extract_a11y
    return {"allowed": True, "status": "ready", "reason": "read tool", "requires_hitl": False}


def plan_tool(call: BrowserToolCall) -> dict:
    """Teaching API matching curriculum c3_browser_tools."""
    decision = classify_tool(call)
    return {
        "action": call.action.value,
        "status": decision["status"],
        "observation_kind": (
            "a11y" if call.action == BrowserAction.EXTRACT_A11Y else "none"
        ),
        "untrusted": True,
        "allowed": decision["allowed"],
        "reason": decision["reason"],
        "requires_hitl": decision["requires_hitl"],
    }
