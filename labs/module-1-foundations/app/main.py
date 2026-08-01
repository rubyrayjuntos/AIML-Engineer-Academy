import asyncio

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Module 1 Streaming Lab", version="1.0.0")


class PromptRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=240)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


async def token_generator(prompt: str):
    tokens = ["Processing", "prompt:", *prompt.split()[:4], "[DONE]"]
    for token in tokens:
        await asyncio.sleep(0.01)
        yield f"data: {token}\n\n"


@app.get("/health")
async def healthcheck():
    return {"status": "ok"}


@app.post("/api/v1/generate/stream")
async def stream_generate(req: PromptRequest):
    return StreamingResponse(token_generator(req.prompt), media_type="text/event-stream")
