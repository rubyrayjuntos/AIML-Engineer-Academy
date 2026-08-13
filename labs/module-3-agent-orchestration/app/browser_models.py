"""Pydantic models for the Module 3 browser micro-lab (stub + optional Playwright)."""
from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class BrowserAction(str, Enum):
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    EXTRACT_A11Y = "extract_a11y"
    EVALUATE_JS = "evaluate_js"  # always rejected by policy


class BrowserToolCall(BaseModel):
    action: BrowserAction
    url: str | None = None
    selector: str | None = Field(default=None, description="Prefer role+name a11y selectors")
    text: str | None = None
    requires_approval: bool = False
    js: str | None = None

    @field_validator("url")
    @classmethod
    def strip_url(cls, value: str | None) -> str | None:
        return value.strip() if value else value


class A11yNode(BaseModel):
    role: str
    name: str
    value: str | None = None


class Observation(BaseModel):
    kind: Literal["a11y", "screenshot_summary", "none"]
    untrusted: bool = True
    nodes: list[A11yNode] = Field(default_factory=list)
    text: str = ""
    ipi_flags: list[str] = Field(default_factory=list)
    raw_suppressed: bool = True


class ApprovalState(str, Enum):
    not_required = "not_required"
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class BrowserStepResult(BaseModel):
    action: BrowserAction
    status: Literal["ready", "awaiting_approval", "executed", "rejected"]
    detail: str = ""
    observation: Observation | None = None
    approval: ApprovalState = ApprovalState.not_required
    meta: dict[str, Any] = Field(default_factory=dict)


class BrowserRunResult(BaseModel):
    status: Literal["ok", "awaiting_approval", "rejected", "failed"]
    goal: str
    steps: list[BrowserStepResult] = Field(default_factory=list)
    claims: dict[str, Any] = Field(default_factory=dict)
