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
    _, _, report_a, _ = build_pipeline(df, random_state=42)
    _, _, report_b, _ = build_pipeline(df, random_state=42)
    assert report_a["accuracy"] == report_b["accuracy"]


def test_pipeline_produces_non_trivial_accuracy():
    df = load_and_clean()
    _, _, report, _ = build_pipeline(df)
    assert report["accuracy"] > 0.5, (
        f"Expected accuracy > 0.5, got {report['accuracy']:.3f}"
    )


def test_pipeline_returns_report_for_all_label_classes():
    df = load_and_clean()
    _, _, report, _ = build_pipeline(df)
    for label in ("quality", "safety", "performance"):
        assert label in report, f"Missing class '{label}' in classification report"
        assert "f1-score" in report[label]


def test_vectorizer_vocabulary_size_respects_max_features():
    df = load_and_clean()
    vectorizer, _, _, _ = build_pipeline(df, max_features=50)
    assert len(vectorizer.vocabulary_) <= 50


def test_pipeline_report_is_held_out_test_split_only():
    """Classification report must reflect held-out test data, not the full dataset."""
    from sklearn.metrics import classification_report as sk_report
    from sklearn.model_selection import train_test_split

    df = load_and_clean()
    vectorizer, clf, report, report_str = build_pipeline(df, random_state=42)

    # Accuracy on the full dataset would be higher (training data memorised).
    X_all_tfidf = vectorizer.transform(df["clean_text"])
    full_acc = sk_report(df["label"], clf.predict(X_all_tfidf), output_dict=True)["accuracy"]

    # Reconstruct the exact 20 % test split that build_pipeline uses.
    _, X_test, _, y_test = train_test_split(
        df["clean_text"],
        df["label"],
        test_size=0.2,
        stratify=df["label"],
        random_state=42,
    )
    test_acc = sk_report(y_test, clf.predict(vectorizer.transform(X_test)), output_dict=True)["accuracy"]

    # The returned dict must match the held-out split, not the full dataset.
    assert report["accuracy"] == pytest.approx(test_acc), (
        "report dict does not match held-out test accuracy"
    )
    # Full-dataset accuracy is at least as high; confirming the two values differ
    # would validate that we're not reporting on training data.  When the model
    # is perfect on both splits they may be equal, so we only assert the dict
    # matches the test split (checked above) rather than asserting inequality.
    assert report_str is not None and len(report_str) > 0
