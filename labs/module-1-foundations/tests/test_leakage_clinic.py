"""Tests for Module 1 leakage & metrics clinic."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from app.leakage_clinic import (
    LEAK_COLUMN,
    detect_target_leakage_columns,
    detect_train_test_overlap,
    format_clinic_report,
    held_out_prf1,
    make_contaminated_frame,
    make_target_leak_frame,
    run_clinic,
    run_honest_text_pipeline,
    run_leaky_preprocess_pipeline,
    run_target_leak_ablation,
    run_target_leak_pipeline,
)
from app.pipeline import load_and_clean


@pytest.fixture(scope="module")
def base_df() -> pd.DataFrame:
    return load_and_clean()


def test_overlap_detector_finds_injected_duplicates(base_df):
    left = ["alpha", "beta", "gamma"]
    right = ["beta", "delta"]
    assert detect_train_test_overlap(left, right) == {"beta"}
    contaminated = make_contaminated_frame(base_df, n_overlap=6, random_state=42)
    assert len(contaminated) == len(base_df) + 6


def test_polluted_test_accuracy_exceeds_clean(base_df):
    from app.leakage_clinic import evaluate_with_forced_contamination

    result = evaluate_with_forced_contamination(base_df, n_overlap=10, random_state=42)
    assert result["overlap_count"] >= 10
    assert result["polluted_test_accuracy"] > result["clean_test_accuracy"]


def test_target_leak_feature_flagged_and_inflates_f1(base_df):
    leaky_df = make_target_leak_frame(base_df)
    flagged = detect_target_leakage_columns(leaky_df)
    assert LEAK_COLUMN in flagged

    leaky = run_target_leak_pipeline(base_df, random_state=42)
    ablated = run_target_leak_ablation(base_df, random_state=42)
    assert leaky["macro_f1"] > ablated["macro_f1"] + 0.15
    assert leaky["macro_f1"] > 0.9


def test_dropping_leak_column_collapses_f1(base_df):
    leaky = run_target_leak_pipeline(base_df, random_state=42)
    ablated = run_target_leak_ablation(base_df, random_state=42)
    assert ablated["macro_f1"] < leaky["macro_f1"]


def test_fit_on_full_data_vocab_or_idf_differs(base_df):
    honest = run_honest_text_pipeline(base_df, random_state=42)
    leaky = run_leaky_preprocess_pipeline(base_df, random_state=42)
    honest_vocab = set(honest["vectorizer"].vocabulary_.keys())
    leaky_vocab = set(leaky["vectorizer"].vocabulary_.keys())
    vocab_differs = honest_vocab != leaky_vocab
    idf_differs = True
    if honest["vectorizer"].vocabulary_ == leaky["vectorizer"].vocabulary_:
        idf_differs = not np.allclose(honest["vectorizer"].idf_, leaky["vectorizer"].idf_)
    assert vocab_differs or idf_differs


def test_held_out_prf1_matches_sklearn_keys(base_df):
    result = run_honest_text_pipeline(base_df, random_state=42)
    prf1 = result["held_out_prf1"]
    assert set(prf1["macro"]) >= {"precision", "recall", "f1-score"}
    for label in ("quality", "safety", "performance"):
        assert label in prf1["per_class"]
        assert set(prf1["per_class"][label]) >= {"precision", "recall", "f1-score", "support"}


def test_held_out_prf1_helper_direct():
    y_true = np.array(["a", "a", "b", "b"])
    y_pred = np.array(["a", "b", "b", "b"])
    report = held_out_prf1(y_true, y_pred, labels=["a", "b"])
    assert report["per_class"]["a"]["recall"] == pytest.approx(0.5)
    assert report["accuracy"] == pytest.approx(0.75)


def test_clinic_run_is_deterministic(base_df):
    a = run_clinic(base_df, random_state=42, n_overlap=8)
    b = run_clinic(base_df, random_state=42, n_overlap=8)
    assert a["contamination"]["polluted_accuracy"] == b["contamination"]["polluted_accuracy"]
    assert a["target_leakage"]["leaky_macro_f1"] == b["target_leakage"]["leaky_macro_f1"]
    assert a["honest_held_out"]["accuracy"] == b["honest_held_out"]["accuracy"]


def test_clinic_report_renders(base_df):
    findings = run_clinic(base_df, random_state=42)
    text = format_clinic_report(findings)
    assert "Train/test contamination" in text
    assert "Target leakage" in text
    assert "Preprocess leakage" in text
    assert "Honest held-out" in text


def test_clinic_flags_leak_column(base_df):
    findings = run_clinic(base_df, random_state=42)
    assert LEAK_COLUMN in findings["target_leakage"]["flagged_columns"]
    assert findings["contamination"]["overlap_count"] > 0
    assert findings["contamination"]["polluted_accuracy"] > findings["contamination"]["honest_accuracy"]
    assert findings["preprocess_leakage"]["vocab_equal"] is False or (
        findings["preprocess_leakage"]["idf_equal"] is False
    )
