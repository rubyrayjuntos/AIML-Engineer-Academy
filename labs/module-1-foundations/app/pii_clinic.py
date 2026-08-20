"""
Module 1 — PII masking clinic (beside leakage)
==============================================
Detect email/phone columns on a teaching frame and redact them before any
retrieval or logging path would ingest the text.

Run via the leakage clinic report, or:
    python -m app.pii_clinic
"""
from __future__ import annotations

import re
from typing import Any

import pandas as pd

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\+?\d[\d.\-() ]{8,}\d")

TEACHING_ROWS = pd.DataFrame(
    {
        "note": ["Follow up with the account owner."],
        "customer_email": ["ada@example.com"],
        "callback_phone": ["+1-415-555-0100"],
        "label": ["quality"],
    }
)


def detect_pii_columns(df: pd.DataFrame) -> list[str]:
    flagged: list[str] = []
    for col in df.columns:
        sample = " ".join(df[col].astype(str).tolist())
        if EMAIL_RE.search(sample) or PHONE_RE.search(sample):
            flagged.append(col)
    return flagged


def mask_pii_text(text: str) -> str:
    masked = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    return PHONE_RE.sub("[REDACTED_PHONE]", masked)


def run_pii_pass(df: pd.DataFrame | None = None) -> dict[str, Any]:
    frame = TEACHING_ROWS if df is None else df
    flagged = detect_pii_columns(frame)
    joined_raw = " ".join(frame.astype(str).to_numpy().ravel())
    joined_masked = mask_pii_text(joined_raw)
    raw_email_surviving = bool(EMAIL_RE.search(joined_masked))
    return {
        "flagged_columns": flagged,
        "raw_email_surviving": raw_email_surviving,
        "masked_sample": joined_masked,
        "finding": (
            "Email/phone columns flagged and redacted before downstream use."
            if flagged and not raw_email_surviving
            else "PII pass did not fully redact teaching emails."
        ),
    }


def format_pii_report(result: dict[str, Any]) -> str:
    return (
        "=== Module 1 PII Clinic ===\n"
        f"flagged_columns      = {result['flagged_columns']}\n"
        f"raw_email_surviving  = {result['raw_email_surviving']}\n"
        f"finding: {result['finding']}\n"
    )


if __name__ == "__main__":
    print(format_pii_report(run_pii_pass()))
