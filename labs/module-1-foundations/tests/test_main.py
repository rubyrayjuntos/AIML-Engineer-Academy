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


def test_stream_generate_validates_prompt_too_long():
    response = client.post(
        "/api/v1/generate/stream",
        json={"prompt": "x" * 241, "temperature": 0.7},
    )

    assert response.status_code == 422


def test_stream_generate_validates_temperature_above_max():
    response = client.post(
        "/api/v1/generate/stream",
        json={"prompt": "hello world", "temperature": 2.1},
    )

    assert response.status_code == 422


def test_stream_generate_validates_temperature_below_min():
    response = client.post(
        "/api/v1/generate/stream",
        json={"prompt": "hello world", "temperature": -0.1},
    )

    assert response.status_code == 422


def test_stream_generate_accepts_boundary_temperature_values():
    for temp in (0.0, 2.0):
        with client.stream(
            "POST",
            "/api/v1/generate/stream",
            json={"prompt": "boundary test", "temperature": temp},
        ) as response:
            assert response.status_code == 200


def test_stream_generate_missing_prompt_field():
    response = client.post(
        "/api/v1/generate/stream",
        json={"temperature": 0.5},
    )

    assert response.status_code == 422


def test_stream_generate_done_token_is_last_frame():
    with client.stream(
        "POST",
        "/api/v1/generate/stream",
        json={"prompt": "verify done frame order", "temperature": 0.0},
    ) as response:
        body = b"".join(response.iter_bytes()).decode()

    frames = [line for line in body.splitlines() if line.startswith("data: ")]
    assert frames, "expected at least one SSE data frame"
    assert frames[-1] == "data: [DONE]"
