"""Inference engine Protocol and factory for Module 4 serving."""
from __future__ import annotations

import os
from typing import Protocol, runtime_checkable


@runtime_checkable
class InferenceEngine(Protocol):
    name: str

    async def generate(self, prompt: str, max_tokens: int) -> tuple[str, int]:
        """Return (output_text, output_token_count)."""


def selected_engine_name() -> str:
    return os.getenv("ACADEMY_ENGINE", "deterministic").strip().lower() or "deterministic"


def build_engine_from_env() -> InferenceEngine:
    """
    Default: DeterministicEngine (CPU CI path).

    Optional GPU track:
      export ACADEMY_GPU=1
      export ACADEMY_ENGINE=vllm
      export ACADEMY_VLLM_URL=http://127.0.0.1:8001
    """
    from app.service import DeterministicEngine

    choice = selected_engine_name()
    if choice in {"vllm", "openai_compat", "openai"}:
        gpu = os.getenv("ACADEMY_GPU", "").strip() == "1"
        if not gpu:
            raise RuntimeError(
                "ACADEMY_ENGINE=vllm requires ACADEMY_GPU=1 "
                "(refusing silent fallback that would mislabel evidence)"
            )
        from app.vllm_adapter import OpenAICompatEngine

        return OpenAICompatEngine(
            base_url=os.getenv("ACADEMY_VLLM_URL", "http://127.0.0.1:8001").rstrip("/"),
            model=os.getenv("ACADEMY_VLLM_MODEL", "local-model"),
        )
    return DeterministicEngine()
