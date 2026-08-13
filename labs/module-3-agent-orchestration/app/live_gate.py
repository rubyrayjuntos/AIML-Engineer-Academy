"""
Optional live-LLM gate for Module 3 structured-output tracks.

Default (CI / Cloud Agent): leave ACADEMY_LIVE_LLM unset. Deterministic
propose() seams stay offline. Keys alone must never trigger paid calls.
"""
from __future__ import annotations

import os


def live_llm_requested() -> bool:
    return os.getenv("ACADEMY_LIVE_LLM", "").strip() == "1"


def api_key_present() -> bool:
    return bool(os.getenv("XAI_API_KEY") or os.getenv("OPENAI_API_KEY"))


def resolve_api_key() -> tuple[str | None, str]:
    """Return (api_key, provider) where provider is 'xai' or 'openai'."""
    xai = os.getenv("XAI_API_KEY", "").strip()
    if xai:
        return xai, "xai"
    openai = os.getenv("OPENAI_API_KEY", "").strip()
    if openai:
        return openai, "openai"
    return None, "none"


def live_model_id() -> str:
    return os.getenv("ACADEMY_LIVE_MODEL", "").strip() or "grok-4.6"


def track_status() -> dict:
    key, provider = resolve_api_key()
    return {
        "academy_live_llm": live_llm_requested(),
        "api_key_present": bool(key),
        "provider": provider,
        "model": live_model_id(),
        "mode": (
            "live"
            if live_llm_requested() and key
            else "plan_only"
        ),
    }
