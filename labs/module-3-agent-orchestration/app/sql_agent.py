"""
Deterministic text-to-SQL agent seam (PydanticAI output_type shape).

CI stays offline: `propose()` is a rule/template stand-in for a hosted
`pydantic_ai.Agent(..., output_type=SQLQueryResult)`. Swap the seam for a live
model without changing the schema, SQL firewall, or MCP tool boundary.
"""
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from app.sql_guard import reject_dangerous_sql
from app.sql_store import AnalyticsStore


class SQLQueryResult(BaseModel):
    query_explanation: str = Field(min_length=8)
    sql_query: str = Field(min_length=6)
    confidence_score: float = Field(ge=0.0, le=1.0)

    @field_validator("sql_query")
    @classmethod
    def strip_sql(cls, value: str) -> str:
        return value.strip()


class SqlAgent:
    def __init__(self, store: AnalyticsStore):
        self.store = store

    def schema_for(self, table: str) -> str:
        return self.store.schema_for(table)

    def propose(self, nl_question: str) -> SQLQueryResult:
        """Deterministic proposer — mirrors PydanticAI structured output."""
        q = nl_question.lower()
        if "revenue" in q or "total" in q and "order" in q:
            return SQLQueryResult(
                query_explanation="Sum order amounts as total revenue.",
                sql_query="SELECT SUM(amount) AS total_revenue FROM orders",
                confidence_score=0.91,
            )
        if "user" in q and ("count" in q or "how many" in q):
            return SQLQueryResult(
                query_explanation="Count rows in the users table.",
                sql_query="SELECT COUNT(*) AS user_count FROM users",
                confidence_score=0.88,
            )
        if "join" in q or ("orders" in q and "name" in q):
            return SQLQueryResult(
                query_explanation="List user names with order amounts.",
                sql_query=(
                    "SELECT u.name, o.amount FROM users u "
                    "JOIN orders o ON o.user_id = u.id ORDER BY o.id"
                ),
                confidence_score=0.84,
            )
        # Intentionally weak draft so repair loop can be demonstrated in tests.
        return SQLQueryResult(
            query_explanation="Fallback draft — may need repair.",
            sql_query="SELECT * FROM unknown_table",
            confidence_score=0.35,
        )

    def validate_and_repair(
        self,
        draft: SQLQueryResult,
        error: str,
        attempt: int,
    ) -> SQLQueryResult:
        del attempt  # teaching seam records attempt count in callers
        # Prefer a safe aggregation when the draft referenced a missing table.
        if "unknown_table" in draft.sql_query.lower() or "no such table" in error.lower():
            return SQLQueryResult(
                query_explanation="Repaired to a known users count after schema feedback.",
                sql_query="SELECT COUNT(*) AS user_count FROM users",
                confidence_score=min(1.0, draft.confidence_score + 0.4),
            )
        if "rejected" in error.lower():
            return SQLQueryResult(
                query_explanation="Repaired write/stacking attempt into a read-only select.",
                sql_query="SELECT COUNT(*) AS user_count FROM users",
                confidence_score=0.8,
            )
        return draft

    def run(self, nl_question: str, max_repairs: int = 2) -> dict:
        schemas = {t: self.schema_for(t) for t in self.store.list_tables()}
        draft = self.propose(nl_question)
        repairs = 0
        last_error: str | None = None
        while True:
            try:
                reject_dangerous_sql(draft.sql_query)
                rows = self.store.execute_readonly(draft.sql_query)
                return {
                    "status": "ok",
                    "schemas": schemas,
                    "result": draft.model_dump(),
                    "rows": rows,
                    "repairs": repairs,
                    "error": last_error,
                }
            except Exception as exc:  # noqa: BLE001 - teaching repair loop
                last_error = str(exc)
                if repairs >= max_repairs:
                    return {
                        "status": "failed",
                        "schemas": schemas,
                        "result": draft.model_dump(),
                        "rows": [],
                        "repairs": repairs,
                        "error": last_error,
                    }
                draft = self.validate_and_repair(draft, last_error, repairs)
                repairs += 1
