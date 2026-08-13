"""
Optional vLLM / OpenAI-compatible engine adapter.

Does not import the `vllm` Python package. Talks HTTP to a running server
(started separately via scripts/start_vllm_optional.sh).
"""
from __future__ import annotations

import httpx


class OpenAICompatEngine:
    """HTTP client for an OpenAI-compatible completions endpoint (vLLM, etc.)."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8001",
        model: str = "local-model",
        timeout_seconds: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.name = f"vllm-openai-compat:{model}"

    async def generate(self, prompt: str, max_tokens: int) -> tuple[str, int]:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": 0.0,
        }
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(f"{self.base_url}/v1/completions", json=payload)
            response.raise_for_status()
            body = response.json()
        text = body["choices"][0].get("text", "")
        usage = body.get("usage") or {}
        output_tokens = int(usage.get("completion_tokens") or len(text.split()))
        return text, output_tokens
