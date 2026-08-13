from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

Stage = Literal["candidate", "canary", "production", "retired"]


@dataclass(frozen=True)
class ModelVersion:
    name: str
    version: str
    artifact_uri: str
    sha256: str


@dataclass(frozen=True)
class Evaluation:
    faithfulness: float
    relevancy: float
    safety: float
    p95_ms: float
    error_rate: float


@dataclass(frozen=True)
class Policy:
    min_faithfulness: float = 0.90
    min_relevancy: float = 0.85
    min_safety: float = 0.98
    max_p95_ms: float = 750.0
    max_error_rate: float = 0.01


def validate_digest(version: ModelVersion, artifact: bytes) -> None:
    actual = hashlib.sha256(artifact).hexdigest()
    if actual != version.sha256:
        raise ValueError("artifact checksum mismatch")


def evaluate_gates(metrics: Evaluation, policy: Policy = Policy()) -> dict[str, bool]:
    return {
        "faithfulness": metrics.faithfulness >= policy.min_faithfulness,
        "relevancy": metrics.relevancy >= policy.min_relevancy,
        "safety": metrics.safety >= policy.min_safety,
        "latency": metrics.p95_ms <= policy.max_p95_ms,
        "reliability": metrics.error_rate <= policy.max_error_rate,
    }


@dataclass(frozen=True)
class CanaryPolicy:
    """Absolute Policy gates plus optional deltas vs a healthy baseline."""

    absolute: Policy = Policy()
    max_faithfulness_drop: float = 0.05
    max_relevancy_drop: float = 0.05
    max_safety_drop: float = 0.02
    max_p95_ratio: float = 1.5


def canary_regression_gates(
    baseline: Evaluation,
    canary: Evaluation,
    policy: CanaryPolicy | None = None,
) -> dict[str, bool]:
    """Absolute release gates plus delta checks vs a healthy baseline."""
    policy = policy or CanaryPolicy()
    absolute = evaluate_gates(canary, policy.absolute)
    deltas = {
        "faithfulness_delta": (baseline.faithfulness - canary.faithfulness)
        <= policy.max_faithfulness_drop,
        "relevancy_delta": (baseline.relevancy - canary.relevancy)
        <= policy.max_relevancy_drop,
        "safety_delta": (baseline.safety - canary.safety) <= policy.max_safety_drop,
        "latency_ratio": canary.p95_ms
        <= max(policy.absolute.max_p95_ms, baseline.p95_ms * policy.max_p95_ratio),
    }
    return {**absolute, **deltas}


class ReleaseStore:
    """Append-only audit log plus a materialized deployment state."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write({"active": None, "previous": None, "stages": {}, "events": []})

    def _read(self) -> dict:
        return json.loads(self.path.read_text())

    def _write(self, state: dict) -> None:
        self.path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")

    def state(self) -> dict:
        return self._read()

    def _event(self, state: dict, action: str, version: str, actor: str, detail: dict) -> None:
        state["events"].append({
            "action": action,
            "version": version,
            "actor": actor,
            "detail": detail,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def register(self, model: ModelVersion, actor: str) -> None:
        state = self._read()
        if model.version in state["stages"]:
            raise ValueError("model version is immutable")
        state["stages"][model.version] = {"stage": "candidate", "model": asdict(model)}
        self._event(state, "register", model.version, actor, {})
        self._write(state)

    def promote(
        self,
        version: str,
        metrics: Evaluation,
        actor: str,
        target: Stage,
        *,
        baseline: Evaluation | None = None,
        canary_policy: CanaryPolicy | None = None,
    ) -> None:
        if target not in ("canary", "production"):
            raise ValueError("invalid promotion target")
        state = self._read()
        if version not in state["stages"]:
            raise KeyError(version)
        current_stage = state["stages"][version]["stage"]
        if target == "canary" and current_stage != "candidate":
            raise ValueError("canary promotion requires candidate stage")
        if target == "production" and current_stage != "canary":
            raise ValueError("production promotion requires canary stage")
        if target == "production" and baseline is not None:
            gates = canary_regression_gates(baseline, metrics, canary_policy)
        else:
            gates = evaluate_gates(metrics)
        if not all(gates.values()):
            self._event(state, "promotion_blocked", version, actor, {"gates": gates})
            self._write(state)
            raise ValueError("release gates failed")
        if target == "production":
            state["previous"] = state["active"]
            state["active"] = version
        state["stages"][version]["stage"] = target
        self._event(state, "promote", version, actor, {"target": target, "gates": gates})
        self._write(state)

    def reject_canary(self, version: str, actor: str, reason: str) -> None:
        """Retire a canary that must not reach production. Does not change active/previous."""
        if not reason.strip():
            raise ValueError("reject reason is required")
        state = self._read()
        if version not in state["stages"]:
            raise KeyError(version)
        if state["stages"][version]["stage"] != "canary":
            raise ValueError("reject_canary requires canary stage")
        state["stages"][version]["stage"] = "retired"
        self._event(
            state,
            "canary_rejected",
            version,
            actor,
            {"reason": reason},
        )
        self._write(state)

    def rollback(self, actor: str, reason: str) -> str:
        if not reason.strip():
            raise ValueError("rollback reason is required")
        state = self._read()
        previous, active = state["previous"], state["active"]
        if not previous or not active:
            raise ValueError("no previous production version")
        state["active"] = previous
        state["previous"] = active
        state["stages"][previous]["stage"] = "production"
        state["stages"][active]["stage"] = "retired"
        self._event(state, "rollback", active, actor, {"restored": previous, "reason": reason})
        self._write(state)
        return previous
