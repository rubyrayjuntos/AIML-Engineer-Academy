"""Read-only SQL firewall helpers for the Module 3 text-to-SQL lane."""
from __future__ import annotations

import re

_WRITE_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|TRUNCATE|ATTACH|DETACH|VACUUM|REINDEX|GRANT|REVOKE)\b",
    re.IGNORECASE,
)
_PRAGMA = re.compile(r"\bPRAGMA\b", re.IGNORECASE)


def normalize_sql(sql: str) -> str:
    return " ".join(sql.strip().rstrip(";").split())


def is_read_only_sql(sql: str) -> bool:
    """Return True when the statement is a single SELECT/WITH query."""
    cleaned = normalize_sql(sql)
    if not cleaned:
        return False
    if ";" in cleaned:
        return False  # statement stacking
    if _WRITE_KEYWORDS.search(cleaned) or _PRAGMA.search(cleaned):
        return False
    head = cleaned.lstrip("(").upper()
    return head.startswith("SELECT") or head.startswith("WITH")


def reject_dangerous_sql(sql: str) -> str:
    """Validate and return normalized SQL, or raise ValueError."""
    cleaned = normalize_sql(sql)
    if not is_read_only_sql(cleaned):
        raise ValueError(
            "rejected: only a single read-only SELECT/WITH statement is allowed "
            "(no stacking, writes, or PRAGMA)"
        )
    return cleaned


def enforce_timeout_budget(timeout_seconds: float = 5.0) -> float:
    if timeout_seconds <= 0 or timeout_seconds > 30:
        raise ValueError("timeout_seconds must be in (0, 30]")
    return float(timeout_seconds)
