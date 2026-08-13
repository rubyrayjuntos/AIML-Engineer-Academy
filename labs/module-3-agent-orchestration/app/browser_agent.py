"""Governed browser agent loop over a stub (or optional Playwright) runtime."""
from __future__ import annotations

import re

from app.browser_models import (
    ApprovalState,
    BrowserAction,
    BrowserRunResult,
    BrowserStepResult,
    BrowserToolCall,
)
from app.browser_policy import classify_tool, plan_tool
from app.browser_runtime import BrowserRuntime, StubDomRuntime


class BrowserAgent:
    """Least-privilege browser loop with HITL on consequential clicks."""

    def __init__(self, runtime: BrowserRuntime | None = None):
        self.runtime = runtime or StubDomRuntime()
        self._pending: BrowserToolCall | None = None
        self._steps: list[BrowserStepResult] = []

    def plan(self, call: BrowserToolCall) -> dict:
        return plan_tool(call)

    def step(self, call: BrowserToolCall, *, approved: bool | None = None) -> BrowserStepResult:
        decision = classify_tool(call)
        if not decision["allowed"]:
            result = BrowserStepResult(
                action=call.action,
                status="rejected",
                detail=decision["reason"],
                approval=ApprovalState.not_required,
            )
            self._steps.append(result)
            return result

        if decision["requires_hitl"] and approved is not True:
            self._pending = call
            result = BrowserStepResult(
                action=call.action,
                status="awaiting_approval",
                detail=decision["reason"],
                approval=ApprovalState.pending,
                meta={"selector": call.selector},
            )
            self._steps.append(result)
            return result

        if decision["requires_hitl"] and approved is True:
            self._pending = None

        observation = self.runtime.execute(call)
        result = BrowserStepResult(
            action=call.action,
            status="executed",
            detail="ok",
            observation=observation,
            approval=(
                ApprovalState.approved
                if decision["requires_hitl"]
                else ApprovalState.not_required
            ),
        )
        self._steps.append(result)
        return result

    def decide(self, approved: bool) -> BrowserStepResult:
        if self._pending is None:
            raise ValueError("no pending write awaiting approval")
        call = self._pending
        if not approved:
            self._pending = None
            result = BrowserStepResult(
                action=call.action,
                status="rejected",
                detail="human rejected consequential write",
                approval=ApprovalState.rejected,
            )
            self._steps.append(result)
            return result
        return self.step(call, approved=True)

    def run(self, goal: str, account_id: str = "ACME-001") -> BrowserRunResult:
        """Deterministic teaching trajectory mirroring BrowserAgentSimulator."""
        self._steps = []
        self._pending = None
        wants_write = bool(re.search(r"submit|purchase|buy|checkout|send|renew|pay", goal, re.I))

        self.step(
            BrowserToolCall(
                action=BrowserAction.NAVIGATE,
                url="https://vendor.example/portal",
            )
        )
        self.step(BrowserToolCall(action=BrowserAction.EXTRACT_A11Y, selector="main"))
        self.step(
            BrowserToolCall(
                action=BrowserAction.TYPE,
                selector="textbox:Account ID",
                text=account_id,
            )
        )

        claims = {
            "browser_runtime": "stub",
            "playwright_executed": False,
            "hitl_required": wants_write,
            "ipi_detected": any(
                s.observation and s.observation.ipi_flags for s in self._steps if s.observation
            ),
        }

        if not wants_write:
            return BrowserRunResult(status="ok", goal=goal, steps=self._steps, claims=claims)

        pending = self.step(
            BrowserToolCall(
                action=BrowserAction.CLICK,
                selector="button:Continue",
                requires_approval=True,
            )
        )
        assert pending.status == "awaiting_approval"
        return BrowserRunResult(
            status="awaiting_approval",
            goal=goal,
            steps=self._steps,
            claims=claims,
        )
