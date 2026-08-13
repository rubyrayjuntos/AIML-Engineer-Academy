"""Shared GPU-track gating helpers for Module 2 (CPU-safe, no torch required)."""
from __future__ import annotations

import os


def gpu_track_requested() -> bool:
    """Return True only when the operator explicitly opts into the GPU track."""
    return os.getenv("ACADEMY_GPU", "").strip() == "1"


def cuda_available() -> bool:
    """Best-effort CUDA probe. Never imports torch unless the GPU track is requested."""
    if not gpu_track_requested():
        return False
    try:
        import torch  # type: ignore
    except Exception:
        return False
    try:
        return bool(torch.cuda.is_available())
    except Exception:
        return False


def track_status() -> dict:
    requested = gpu_track_requested()
    cuda = cuda_available() if requested else False
    return {
        "academy_gpu": requested,
        "cuda_available": cuda,
        "mode": "gpu" if requested and cuda else "cpu_plan_only",
    }
