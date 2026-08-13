from __future__ import annotations

import asyncio
import hashlib
import hmac
import os
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, status
from pydantic import BaseModel, ConfigDict, Field

from app.engine import InferenceEngine


class GenerateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompt: str = Field(min_length=1, max_length=512)
    max_tokens: int = Field(default=32, ge=1, le=128)


class GenerateResponse(BaseModel):
    request_id: str
    model: str
    output: str
    input_tokens: int
    output_tokens: int
    elapsed_ms: float


class WindowRateLimiter:
    def __init__(self, limit: int, window_seconds: float) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def allow(self, identity: str) -> bool:
        now = time.monotonic()
        async with self._lock:
            events = self._events[identity]
            while events and now - events[0] >= self.window_seconds:
                events.popleft()
            if len(events) >= self.limit:
                return False
            events.append(now)
            return True


@dataclass(frozen=True)
class Settings:
    api_key: str = "academy-local-key"
    max_concurrency: int = 4
    request_timeout_seconds: float = 1.0
    rate_limit: int = 20
    rate_window_seconds: float = 60.0


class DeterministicEngine:
    name = "deterministic-cpu-v1"

    async def generate(self, prompt: str, max_tokens: int) -> tuple[str, int]:
        await asyncio.sleep(0.003 + min(len(prompt), 400) / 100_000)
        digest = hashlib.sha256(prompt.encode()).hexdigest()[:12]
        words = (f"grounded recommendation {digest} " * 64).split()[:max_tokens]
        return " ".join(words), len(words)


def create_app(settings: Settings | None = None, engine: InferenceEngine | None = None) -> FastAPI:
    cfg = settings or Settings(api_key=os.getenv("ACADEMY_API_KEY", "academy-local-key"))
    model: InferenceEngine = engine if engine is not None else DeterministicEngine()
    limiter = WindowRateLimiter(cfg.rate_limit, cfg.rate_window_seconds)
    semaphore = asyncio.Semaphore(cfg.max_concurrency)
    app = FastAPI(title="Module 4 Secure Inference", version="1.0.0")

    async def authenticate(x_api_key: str | None = Header(default=None)) -> str:
        if x_api_key is None or not hmac.compare_digest(x_api_key, cfg.api_key):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid API key")
        return hashlib.sha256(x_api_key.encode()).hexdigest()[:16]

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id
        response: Response = await call_next(request)
        response.headers["x-request-id"] = request_id
        response.headers["x-content-type-options"] = "nosniff"
        response.headers["cache-control"] = "no-store"
        return response

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "model": model.name}

    @app.post("/v1/generate", response_model=GenerateResponse)
    async def generate(payload: GenerateRequest, request: Request, identity: str = Depends(authenticate)):
        if not await limiter.allow(identity):
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="rate limit exceeded")
        request_id = request.state.request_id
        started = time.perf_counter()
        try:
            async with semaphore:
                output, output_tokens = await asyncio.wait_for(
                    model.generate(payload.prompt, payload.max_tokens),
                    timeout=cfg.request_timeout_seconds,
                )
        except TimeoutError as exc:
            raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="inference timeout") from exc
        elapsed_ms = (time.perf_counter() - started) * 1000
        return GenerateResponse(
            request_id=request_id,
            model=model.name,
            output=output,
            input_tokens=len(payload.prompt.split()),
            output_tokens=output_tokens,
            elapsed_ms=round(elapsed_ms, 3),
        )

    return app


# Module import path for uvicorn; always CPU-deterministic unless tests inject an engine.
# For optional vLLM: create_app(engine=build_engine_from_env()) in a custom entrypoint.
app = create_app()
