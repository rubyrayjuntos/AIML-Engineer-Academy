"""PII detection/masking beside the Module 1 leakage clinic."""
from __future__ import annotations

import pandas as pd

from app.leakage_clinic import format_clinic_report, run_clinic
from app.pii_clinic import detect_pii_columns, mask_pii_text, run_pii_pass


def test_detect_pii_columns_flags_email_and_phone():
    df = pd.DataFrame(
        {
            "text": ["hello"],
            "customer_email": ["ada@example.com"],
            "callback_phone": ["+1-415-555-0100"],
            "label": ["quality"],
        }
    )
    flagged = detect_pii_columns(df)
    assert "customer_email" in flagged
    assert "callback_phone" in flagged
    assert "text" not in flagged


def test_mask_pii_redacts_email_and_phone():
    raw = "Contact ada@example.com or +1-415-555-0100 for follow-up."
    masked = mask_pii_text(raw)
    assert "ada@example.com" not in masked
    assert "+1-415-555-0100" not in masked
    assert "[REDACTED_EMAIL]" in masked
    assert "[REDACTED_PHONE]" in masked


def test_pii_pass_and_clinic_report_include_masking():
    result = run_pii_pass()
    assert result["flagged_columns"]
    assert result["raw_email_surviving"] is False
    findings = run_clinic()
    text = format_clinic_report(findings)
    assert "PII" in text
    assert findings["pii"]["raw_email_surviving"] is False
