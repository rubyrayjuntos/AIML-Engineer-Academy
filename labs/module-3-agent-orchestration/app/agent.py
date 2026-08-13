from __future__ import annotations

import time
import uuid
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Callable

from pydantic import ValidationError

from app.models import Citation, Recommendation, RiskLevel, WorkflowResult, WorkflowStatus
from app.store import Store


class ToolFailure(RuntimeError):
    pass


def execute_with_policy(fn: Callable, *args, retries: int = 2, timeout_seconds: float = 1.0):
    """Run a tool with a wait budget and retry count.

    Timeout bounds ``future.result`` only — it does not kill a running worker
    thread. ``ThreadPoolExecutor.shutdown(wait=True)`` still waits for in-flight
    work. This lab teaches the policy seam, not process isolation.
    """
    last_error: Exception | None = None
    with ThreadPoolExecutor(max_workers=1) as pool:
        for _ in range(retries + 1):
            future = pool.submit(fn, *args)
            try:
                return future.result(timeout=timeout_seconds)
            except (TimeoutError, Exception) as exc:
                last_error = exc
                future.cancel()
    raise ToolFailure(f"tool failed after {retries + 1} attempts: {last_error}")


class CustomerSuccessAgent:
    """Deterministic state machine; an LLM adapter may replace propose()."""

    def __init__(self, store: Store):
        self.store = store

    def assess(self, account_id: str, run_id: str | None = None) -> WorkflowResult:
        run_id = run_id or str(uuid.uuid4())
        self.store.save_run(run_id, account_id, WorkflowStatus.started.value, {})
        try:
            customer = execute_with_policy(self.store.customer, account_id)
            if customer is None:
                raise ToolFailure(f"unknown account: {account_id}")
            evidence = execute_with_policy(
                self.store.search, account_id, "renewal risk outage reliability executive plan", 3
            )
            self.store.save_run(run_id, account_id, WorkflowStatus.evidence_retrieved.value, {"evidence": evidence})
            recommendation = self.propose(customer, evidence)
            state = {"recommendation": recommendation.model_dump(mode="json")}
            self.store.save_run(run_id, account_id, WorkflowStatus.awaiting_approval.value, state)
            return WorkflowResult(
                run_id=run_id, status=WorkflowStatus.awaiting_approval, recommendation=recommendation
            )
        except (ToolFailure, ValidationError, ValueError) as exc:
            self.store.save_run(run_id, account_id, WorkflowStatus.failed.value, {"error": str(exc)})
            return WorkflowResult(run_id=run_id, status=WorkflowStatus.failed, error=str(exc))

    def propose(self, customer: dict, evidence: list[dict]) -> Recommendation:
        if not evidence:
            raise ValueError("a recommendation requires retrieved evidence")
        risk = RiskLevel.high if customer["health_score"] < 40 else RiskLevel.medium
        citations = [
            Citation(interaction_id=e["interaction_id"], excerpt=e["content"], score=abs(float(e["score"])))
            for e in evidence
        ]
        return Recommendation(
            account_id=customer["account_id"], risk=risk,
            rationale=f"{customer['name']} has health score {customer['health_score']} and documented renewal/reliability concerns.",
            proposed_action="Prepare an executive recovery review with a named owner and weekly reliability updates.",
            citations=citations, confidence=0.88 if risk == RiskLevel.high else 0.7,
        )

    def decide(self, run_id: str, approved: bool) -> WorkflowResult:
        saved = self.store.load_run(run_id)
        if not saved or saved["status"] != WorkflowStatus.awaiting_approval.value:
            raise ValueError("run is not awaiting approval")
        recommendation = Recommendation.model_validate(saved["state"]["recommendation"])
        status = WorkflowStatus.approved if approved else WorkflowStatus.rejected
        self.store.save_run(run_id, saved["account_id"], status.value, saved["state"])
        # Approval records a decision only. No outbound tool exists in this lab.
        return WorkflowResult(run_id=run_id, status=status, recommendation=recommendation)
