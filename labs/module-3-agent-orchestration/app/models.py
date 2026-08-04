from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field, model_validator


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Citation(BaseModel):
    interaction_id: int
    excerpt: str = Field(min_length=1, max_length=280)
    score: float = Field(ge=0)


class Recommendation(BaseModel):
    account_id: str
    risk: RiskLevel
    rationale: str = Field(min_length=20)
    proposed_action: str = Field(min_length=10)
    citations: list[Citation] = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)
    requires_human_approval: bool = True

    @model_validator(mode="after")
    def enforce_governance(self) -> "Recommendation":
        if not self.requires_human_approval:
            raise ValueError("customer interventions always require human approval")
        return self


class WorkflowStatus(str, Enum):
    started = "started"
    evidence_retrieved = "evidence_retrieved"
    awaiting_approval = "awaiting_approval"
    approved = "approved"
    rejected = "rejected"
    failed = "failed"


class WorkflowResult(BaseModel):
    run_id: str
    status: WorkflowStatus
    recommendation: Recommendation | None = None
    error: str | None = None
