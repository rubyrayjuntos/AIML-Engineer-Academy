"""
Teaching stub for DSPy-style prompt compilation (no dspy dependency).

Mirrors the curriculum idea: treat instructions + few-shot demos as a compiled
artifact scored by a metric on a trainset, then freeze for production.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import re


@dataclass(frozen=True)
class Example:
    question: str
    gold_sql: str


@dataclass
class CompiledPrompt:
    instruction: str
    demos: list[Example] = field(default_factory=list)

    def render(self) -> str:
        parts = [self.instruction.strip(), "", "Demonstrations:"]
        for i, demo in enumerate(self.demos, start=1):
            parts.append(f"{i}. Q: {demo.question}")
            parts.append(f"   SQL: {demo.gold_sql}")
        return "\n".join(parts)


def _normalize(sql: str) -> str:
    return re.sub(r"\s+", " ", sql.strip().rstrip(";")).lower()


def metric_exact_select(pred_sql: str, gold_sql: str) -> float:
    """Binary exact-match metric after whitespace/case normalization."""
    return 1.0 if _normalize(pred_sql) == _normalize(gold_sql) else 0.0


def bootstrap_fewshot(
    trainset: list[Example],
    seed_instruction: str,
    k: int = 3,
) -> CompiledPrompt:
    """
    Pick up to k demos from the trainset (teaching stand-in for BootstrapFewShot).

    Real DSPy would run a student program, score with a metric, and search over
    instructions/demos. Here we keep CI offline: take the first k examples whose
    gold SQL is a read-only SELECT.
    """
    if k < 1:
        raise ValueError("k must be >= 1")
    demos: list[Example] = []
    for example in trainset:
        if example.gold_sql.strip().lower().startswith("select"):
            demos.append(example)
        if len(demos) >= k:
            break
    if not demos:
        raise ValueError("trainset produced no SELECT demos")
    instruction = seed_instruction.strip() or (
        "Generate a single read-only SQL SELECT for the analytics schema."
    )
    return CompiledPrompt(instruction=instruction, demos=demos)
