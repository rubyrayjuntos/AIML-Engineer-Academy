from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthcheck():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_stream_generate_sends_sse_frames():
    with client.stream(
        "POST",
        "/api/v1/generate/stream",
        json={"prompt": "ship reliable streaming APIs", "temperature": 0.4},
    ) as response:
        body = b"".join(response.iter_bytes()).decode()

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "data: Processing" in body
    assert "data: ship" in body
    assert "data: [DONE]" in body


def test_stream_generate_validates_empty_prompt():
    response = client.post(
        "/api/v1/generate/stream",
        json={"prompt": "", "temperature": 0.4},
    )

    assert response.status_code == 422
