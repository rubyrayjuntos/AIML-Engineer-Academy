import pathlib

import pandas as pd
import pytest

from app.pipeline import DATA_PATH, build_pipeline, clean_text, load_and_clean


def test_clean_text_lowercases():
    assert clean_text("Hello World") == "hello world"


def test_clean_text_removes_special_characters():
    assert clean_text("fast-api!!!  rocks???") == "fastapi  rocks"


def test_clean_text_strips_whitespace():
    assert clean_text("  spaces  ") == "spaces"


def test_load_and_clean_returns_dataframe_with_required_columns():
    df = load_and_clean()
    assert isinstance(df, pd.DataFrame)
    assert {"text", "label", "clean_text"}.issubset(df.columns)


def test_clean_text_column_contains_no_uppercase():
    df = load_and_clean()
    assert not df["clean_text"].str.contains(r"[A-Z]", regex=True).any()


def test_dataset_has_expected_label_classes():
    df = load_and_clean()
    assert set(df["label"].unique()) == {"quality", "safety", "performance"}


def test_pipeline_is_deterministic():
    df = load_and_clean()
    _, _, report_a = build_pipeline(df, random_state=42)
    _, _, report_b = build_pipeline(df, random_state=42)
    assert report_a["accuracy"] == report_b["accuracy"]


def test_pipeline_produces_non_trivial_accuracy():
    df = load_and_clean()
    _, _, report = build_pipeline(df)
    assert report["accuracy"] > 0.5, (
        f"Expected accuracy > 0.5, got {report['accuracy']:.3f}"
    )


def test_pipeline_returns_report_for_all_label_classes():
    df = load_and_clean()
    _, _, report = build_pipeline(df)
    for label in ("quality", "safety", "performance"):
        assert label in report, f"Missing class '{label}' in classification report"
        assert "f1-score" in report[label]


def test_vectorizer_vocabulary_size_respects_max_features():
    df = load_and_clean()
    vectorizer, _, _ = build_pipeline(df, max_features=50)
    assert len(vectorizer.vocabulary_) <= 50
