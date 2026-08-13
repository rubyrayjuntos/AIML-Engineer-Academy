"""Observation sanitizer — page content is always an IPI surface."""
from __future__ import annotations

import re

from app.browser_models import A11yNode, Observation

_IPI_PATTERNS = [
    re.compile(r"ignore\s+previous\s+instructions", re.I),
    re.compile(r"system\s*:", re.I),
    re.compile(r"approve\s+purchase\s+without\s+human", re.I),
    re.compile(r"exfiltrate", re.I),
]


def detect_ipi_flags(text: str) -> list[str]:
    flags: list[str] = []
    for pattern in _IPI_PATTERNS:
        if pattern.search(text):
            flags.append(pattern.pattern)
    return flags


def sanitize_observation(
    *,
    kind: str,
    nodes: list[A11yNode] | None = None,
    raw_text: str = "",
) -> Observation:
    """Return a minimized observation; never pass raw HTML to the planner."""
    nodes = nodes or []
    combined = " ".join(
        [raw_text] + [f"{n.role}:{n.name}:{n.value or ''}" for n in nodes]
    )
    flags = detect_ipi_flags(combined)
    # Drop nodes that look like instruction banners from the planner view.
    clean_nodes = [
        n
        for n in nodes
        if not detect_ipi_flags(f"{n.name} {n.value or ''}")
    ]
    summary_parts = [f"{n.role}:{n.name}" + (f"={n.value}" if n.value else "") for n in clean_nodes]
    text = " ; ".join(summary_parts) if summary_parts else "[sanitized empty]"
    if flags:
        text = f"[ipi_quarantined] {text}"
    return Observation(
        kind=kind if kind in {"a11y", "screenshot_summary", "none"} else "a11y",
        untrusted=True,
        nodes=clean_nodes,
        text=text,
        ipi_flags=flags,
        raw_suppressed=True,
    )
