"""CPU-safe tests for the optional vLLM engine factory / adapter shape."""
import asyncio

import pytest

from app.engine import InferenceEngine, build_engine_from_env, selected_engine_name
from app.service import DeterministicEngine, create_app
from app.vllm_adapter import OpenAICompatEngine


def test_selected_engine_defaults_deterministic(monkeypatch):
    monkeypatch.delenv("ACADEMY_ENGINE", raising=False)
    assert selected_engine_name() == "deterministic"


def test_build_engine_defaults_to_cpu(monkeypatch):
    monkeypatch.delenv("ACADEMY_ENGINE", raising=False)
    monkeypatch.delenv("ACADEMY_GPU", raising=False)
    engine = build_engine_from_env()
    assert isinstance(engine, DeterministicEngine)
    assert isinstance(engine, InferenceEngine)


def test_vllm_engine_requires_gpu_flag(monkeypatch):
    monkeypatch.setenv("ACADEMY_ENGINE", "vllm")
    monkeypatch.delenv("ACADEMY_GPU", raising=False)
    with pytest.raises(RuntimeError, match="ACADEMY_GPU=1"):
        build_engine_from_env()


def test_openai_compat_engine_name():
    engine = OpenAICompatEngine(base_url="http://127.0.0.1:9", model="demo")
    assert engine.name.startswith("vllm-openai-compat:")


def test_create_app_accepts_protocol_engine():
    class Tiny:
        name = "tiny-test"

        async def generate(self, prompt: str, max_tokens: int):
            return prompt[:max_tokens], min(len(prompt.split()), max_tokens)

    app = create_app(engine=Tiny())
    assert app.title.startswith("Module 4")


@pytest.mark.gpu
def test_live_vllm_optional(monkeypatch):
    """Skipped unless ACADEMY_GPU=1 and ACADEMY_VLLM_URL is healthy."""
    import os

    import httpx

    if os.getenv("ACADEMY_GPU") != "1":
        pytest.skip("ACADEMY_GPU!=1")
    url = os.getenv("ACADEMY_VLLM_URL", "").rstrip("/")
    if not url:
        pytest.skip("ACADEMY_VLLM_URL unset")
    try:
        httpx.get(f"{url}/health", timeout=2.0).raise_for_status()
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"vLLM not reachable: {exc}")
    monkeypatch.setenv("ACADEMY_ENGINE", "vllm")
    engine = build_engine_from_env()
    text, n = asyncio.run(engine.generate("hello", 4))
    assert isinstance(text, str) and n >= 0
