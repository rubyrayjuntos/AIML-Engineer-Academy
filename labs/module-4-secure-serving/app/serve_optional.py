"""Optional uvicorn entry that honors ACADEMY_ENGINE / ACADEMY_GPU."""
from __future__ import annotations

from app.engine import build_engine_from_env
from app.service import create_app

app = create_app(engine=build_engine_from_env())
