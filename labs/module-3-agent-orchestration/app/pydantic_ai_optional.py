"""
Optional live PydanticAI structured-output track for Module 3.

Default (CI / Cloud Agent): write a CPU-safe *plan* JSON. Never claims a live
``pydantic_ai.Agent`` ran. Does not import pydantic-ai unless
``ACADEMY_LIVE_LLM=1`` and an API key is present.

Optional live path (local / paid CI only):
  pip install -r requirements-live.txt
  export ACADEMY_LIVE_LLM=1
  export XAI_API_KEY=...   # or OPENAI_API_KEY
  # optional: export ACADEMY_LIVE_MODEL=grok-4.6
  python -m app.pydantic_ai_optional --output artifacts/live_structured_plan.json
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import time
from typing import Any

from app.live_gate import (
    api_key_present,
    live_llm_requested,
    live_model_id,
    resolve_api_key,
    track_status,
)
from app.sql_agent import SQLQueryResult

_LAB_ROOT = pathlib.Path(__file__).resolve().parent.parent

DEFAULT_SCHEMAS = {
    "users": (
        "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, "
        "created_at TEXT NOT NULL)"
    ),
    "orders": (
        "CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, "
        "amount REAL NOT NULL, created_at TEXT NOT NULL)"
    ),
}


def build_live_structured_plan(
    nl_question: str | None = None,
    schemas: dict[str, str] | None = None,
) -> dict[str, Any]:
    status = track_status()
    return {
        "track": "optional-pydantic-ai-structured",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "framework": "pydantic-ai",
        "output_type": "SQLQueryResult",
        "sample_question": nl_question
        or "What is total order revenue?",
        "schemas": schemas or DEFAULT_SCHEMAS,
        "gate": status,
        "claims": {
            "pydantic_ai_executed": False,
            "sql_structured_live": False,
            "note": (
                "Install requirements-live.txt and set ACADEMY_LIVE_LLM=1 + "
                "XAI_API_KEY/OPENAI_API_KEY to run a live Agent(output_type=SQLQueryResult)"
            ),
        },
        "maps_from_lab": {
            "deterministic_propose": "app.sql_agent.SqlAgent.propose",
            "firewall": "app.sql_guard.reject_dangerous_sql",
            "note": "Live path must still pass the RO firewall + repair loop before execution",
        },
    }


def _openai_compatible_model(model_id: str, provider: str, api_key: str):
    """Build a pydantic-ai model for xAI or OpenAI (OpenAI-compatible HTTP)."""
    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.openai import OpenAIProvider

    if provider == "xai":
        base_url = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1").rstrip("/")
        return OpenAIChatModel(
            model_id,
            provider=OpenAIProvider(base_url=base_url, api_key=api_key),
        )
    return OpenAIChatModel(model_id, provider=OpenAIProvider(api_key=api_key))


def propose_sql_live(
    nl_question: str,
    schemas: dict[str, str] | None = None,
) -> SQLQueryResult:
    """Run a live pydantic-ai Agent with output_type=SQLQueryResult.

    Raises ImportError / RuntimeError when deps or credentials are missing.
    Callers should only invoke this after gate + key checks.
    """
    api_key, provider = resolve_api_key()
    if not api_key:
        raise RuntimeError("missing XAI_API_KEY/OPENAI_API_KEY for live structured output")

    try:
        from pydantic_ai import Agent
    except Exception as exc:  # noqa: BLE001
        raise ImportError(
            "pydantic-ai not installed — pip install -r requirements-live.txt"
        ) from exc

    schema_blob = "\n\n".join(
        f"-- {name}\n{ddl}" for name, ddl in (schemas or DEFAULT_SCHEMAS).items()
    )
    model = _openai_compatible_model(live_model_id(), provider, api_key)
    agent = Agent(
        model,
        output_type=SQLQueryResult,
        system_prompt=(
            "You are a senior analytics engineer. Emit ONE read-only SQL query "
            "for the schema below. Prefer SELECT / aggregates. Never emit "
            "INSERT/UPDATE/DELETE/DROP/PRAGMA or stacked statements.\n\n"
            f"{schema_blob}"
        ),
    )
    result = agent.run_sync(nl_question)
    # pydantic-ai versions expose .output (newer) or .data (older)
    output = getattr(result, "output", None) or getattr(result, "data", None)
    if not isinstance(output, SQLQueryResult):
        output = SQLQueryResult.model_validate(output)
    return output


def maybe_run_live_sql(
    plan: dict[str, Any] | None = None,
    *,
    nl_question: str | None = None,
    schemas: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Execute live structured SQL propose only when gate + key + deps allow."""
    plan = plan or build_live_structured_plan(nl_question=nl_question, schemas=schemas)
    question = nl_question or plan.get("sample_question") or "What is total order revenue?"
    schema_map = schemas or plan.get("schemas") or DEFAULT_SCHEMAS

    if not live_llm_requested():
        plan["execution"] = {"status": "skipped", "reason": "ACADEMY_LIVE_LLM!=1"}
        return plan
    if not api_key_present():
        plan["execution"] = {
            "status": "skipped",
            "reason": "missing XAI_API_KEY/OPENAI_API_KEY",
        }
        return plan

    try:
        draft = propose_sql_live(question, schemas=schema_map)
    except ImportError as exc:
        plan["execution"] = {
            "status": "skipped",
            "reason": str(exc),
            "hint": "pip install -r requirements-live.txt",
        }
        return plan
    except Exception as exc:  # noqa: BLE001
        plan["execution"] = {
            "status": "skipped",
            "reason": f"live Agent failed: {exc}",
        }
        return plan

    plan["execution"] = {
        "status": "ran",
        "question": question,
        "result": draft.model_dump(),
        "model": live_model_id(),
        "provider": track_status()["provider"],
    }
    plan["claims"]["pydantic_ai_executed"] = True
    plan["claims"]["sql_structured_live"] = True
    return plan


def propose_sql_with_optional_live(
    nl_question: str,
    *,
    schemas: dict[str, str] | None = None,
    deterministic_fallback,
) -> tuple[SQLQueryResult, dict[str, Any]]:
    """Try live propose when gated; otherwise / on failure use deterministic_fallback().

    Returns (SQLQueryResult, meta) where meta documents which path ran.
    """
    meta: dict[str, Any] = {"path": "deterministic", "live_attempted": False}
    if not (live_llm_requested() and api_key_present()):
        return deterministic_fallback(), meta

    meta["live_attempted"] = True
    try:
        draft = propose_sql_live(nl_question, schemas=schemas)
        meta["path"] = "live_pydantic_ai"
        return draft, meta
    except Exception as exc:  # noqa: BLE001
        meta["path"] = "deterministic_fallback"
        meta["live_error"] = str(exc)
        return deterministic_fallback(), meta


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optional live PydanticAI structured-output track")
    parser.add_argument("--output", type=pathlib.Path, default=None)
    parser.add_argument(
        "--question",
        default="What is total order revenue?",
        help="Natural-language analytics question for the live Agent",
    )
    args = parser.parse_args()
    result = maybe_run_live_sql(build_live_structured_plan(nl_question=args.question))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {"claims": result["claims"], "execution": result.get("execution")},
            sort_keys=True,
        )
    )
