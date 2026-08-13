"""
Module 1 — Leakage & Metrics Clinic
===================================
Teaching lab that contrasts *leaky* evaluation paths with an honest held-out
baseline. The correct production path remains ``app.pipeline.build_pipeline``;
this module intentionally builds contaminated / target-leaky / preprocess-leaky
scenarios so learners can see inflated metrics and practice detectors.

Run:
    python -m app.leakage_clinic
"""
from __future__ import annotations

import pathlib
from typing import Any

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from app.pipeline import clean_text, load_and_clean

_LAB_ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_PATH = _LAB_ROOT / "data" / "prompts.csv"

LEAK_COLUMN = "post_outcome_code"


# ---------------------------------------------------------------------------
# Detectors
# ---------------------------------------------------------------------------


def detect_train_test_overlap(train_texts: list[str] | pd.Series, test_texts: list[str] | pd.Series) -> set[str]:
    """Return the set of exact string values that appear in both train and test."""
    train_set = {str(t) for t in train_texts}
    test_set = {str(t) for t in test_texts}
    return train_set & test_set


def detect_target_leakage_columns(
    df: pd.DataFrame,
    label_col: str = "label",
    exclude: frozenset[str] | set[str] | None = None,
) -> list[str]:
    """Flag columns that are deterministic functions of the label.

    A column is flagged when every distinct value maps to exactly one label
    (perfect purity) and the column is not the label itself / excluded text.
    """
    exclude = set(exclude or set()) | {label_col, "text", "clean_text"}
    flagged: list[str] = []
    labels = df[label_col]
    for col in df.columns:
        if col in exclude:
            continue
        series = df[col]
        if series.nunique(dropna=False) == 0:
            continue
        # Group by feature value → unique labels; purity requires singleton sets.
        purity_ok = True
        for _, group in df.groupby(col, dropna=False)[label_col]:
            if group.nunique(dropna=False) != 1:
                purity_ok = False
                break
        # Also require the feature to vary with the label (not a constant).
        if purity_ok and series.nunique(dropna=False) > 1 and labels.nunique() > 1:
            # Prefer columns that recover the label partition (at least as many
            # unique values as labels, or exact equality after string cast).
            if series.astype(str).equals(labels.astype(str)) or series.nunique() >= labels.nunique():
                flagged.append(col)
    return flagged


def held_out_prf1(y_true, y_pred, labels: list[str] | None = None) -> dict[str, Any]:
    """Return per-class and macro precision / recall / F1 on a held-out split only."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    if labels is None:
        labels = sorted(set(y_true) | set(y_pred))
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=labels,
        zero_division=0,
    )
    per_class = {
        str(label): {
            "precision": float(precision[i]),
            "recall": float(recall[i]),
            "f1-score": float(f1[i]),
            "support": int(support[i]),
        }
        for i, label in enumerate(labels)
    }
    return {
        "per_class": per_class,
        "macro": {
            "precision": float(np.mean(precision)),
            "recall": float(np.mean(recall)),
            "f1-score": float(np.mean(f1)),
        },
        "accuracy": float(np.mean(y_true == y_pred)),
        "labels": list(labels),
    }


# ---------------------------------------------------------------------------
# Scenario builders
# ---------------------------------------------------------------------------


def make_contaminated_frame(
    df: pd.DataFrame,
    n_overlap: int = 8,
    random_state: int = 42,
) -> pd.DataFrame:
    """Duplicate rows so identical ``clean_text`` values can land in train and test."""
    rng = np.random.default_rng(random_state)
    out = df.copy().reset_index(drop=True)
    if "clean_text" not in out.columns:
        out["clean_text"] = out["text"].astype(str).map(clean_text)
    n_overlap = min(n_overlap, len(out))
    idx = rng.choice(len(out), size=n_overlap, replace=False)
    dupes = out.iloc[idx].copy()
    return pd.concat([out, dupes], ignore_index=True)


def make_target_leak_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Add a post-outcome feature that is a deterministic encoding of the label."""
    out = df.copy()
    if "clean_text" not in out.columns:
        out["clean_text"] = out["text"].astype(str).map(clean_text)
    encoder = LabelEncoder()
    out[LEAK_COLUMN] = encoder.fit_transform(out["label"].astype(str))
    return out


def evaluate_with_forced_contamination(
    df: pd.DataFrame,
    *,
    n_overlap: int = 8,
    random_state: int = 42,
    max_features: int = 500,
) -> dict[str, Any]:
    """Train on a clean split, then score a test set polluted with train rows.

    This is the classic train/test contamination failure mode: the model is
    graded on examples it already saw, so held-out accuracy is inflated.
    """
    work = df.copy()
    if "clean_text" not in work.columns:
        work["clean_text"] = work["text"].astype(str).map(clean_text)
    work = work.drop_duplicates(subset=["clean_text"]).reset_index(drop=True)

    X_train, X_test, y_train, y_test = train_test_split(
        work["clean_text"],
        work["label"],
        test_size=0.2,
        stratify=work["label"],
        random_state=random_state,
    )
    n_overlap = min(n_overlap, len(X_train))
    inject_x = X_train.iloc[:n_overlap]
    inject_y = y_train.iloc[:n_overlap]
    X_test_polluted = pd.concat([X_test, inject_x], ignore_index=True)
    y_test_polluted = pd.concat([y_test, inject_y], ignore_index=True)

    vectorizer, clf, clean_report, _ = _fit_text_classifier(
        X_train,
        X_test,
        y_train,
        y_test,
        max_features=max_features,
        random_state=random_state,
        fit_vectorizer_on="train",
    )
    y_pred_polluted = clf.predict(vectorizer.transform(X_test_polluted))
    polluted_report = classification_report(
        y_test_polluted,
        y_pred_polluted,
        output_dict=True,
        zero_division=0,
    )
    overlap = detect_train_test_overlap(X_train, X_test_polluted)
    return {
        "mode": "forced_contamination",
        "overlap_count": len(overlap),
        "overlap_texts": sorted(overlap)[:5],
        "clean_test_accuracy": float(clean_report["accuracy"]),
        "polluted_test_accuracy": float(polluted_report["accuracy"]),
        "n_injected": n_overlap,
    }


# ---------------------------------------------------------------------------
# Pipelines (honest vs leaky)
# ---------------------------------------------------------------------------


def _fit_text_classifier(
    X_train: pd.Series,
    X_test: pd.Series,
    y_train: pd.Series,
    y_test: pd.Series,
    *,
    max_features: int = 500,
    random_state: int = 42,
    fit_vectorizer_on: str = "train",
) -> tuple[TfidfVectorizer, LogisticRegression, dict, np.ndarray]:
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=(1, 2),
        sublinear_tf=True,
    )
    if fit_vectorizer_on == "train":
        X_train_tfidf = vectorizer.fit_transform(X_train)
        X_test_tfidf = vectorizer.transform(X_test)
    elif fit_vectorizer_on == "full":
        # LEAK: fit on train+test text before scoring the "held-out" split.
        vectorizer.fit(pd.concat([X_train, X_test], ignore_index=True))
        X_train_tfidf = vectorizer.transform(X_train)
        X_test_tfidf = vectorizer.transform(X_test)
    else:
        raise ValueError("fit_vectorizer_on must be 'train' or 'full'")

    clf = LogisticRegression(solver="liblinear", max_iter=300, random_state=random_state)
    clf.fit(X_train_tfidf, y_train)
    y_pred = clf.predict(X_test_tfidf)
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    return vectorizer, clf, report, y_pred


def run_honest_text_pipeline(
    df: pd.DataFrame,
    *,
    random_state: int = 42,
    max_features: int = 500,
) -> dict[str, Any]:
    """Stratified split + TF-IDF fit on train only + held-out P/R/F1."""
    work = df.copy()
    if "clean_text" not in work.columns:
        work["clean_text"] = work["text"].astype(str).map(clean_text)

    X_train, X_test, y_train, y_test = train_test_split(
        work["clean_text"],
        work["label"],
        test_size=0.2,
        stratify=work["label"],
        random_state=random_state,
    )
    overlap = detect_train_test_overlap(X_train, X_test)
    vectorizer, clf, report, y_pred = _fit_text_classifier(
        X_train,
        X_test,
        y_train,
        y_test,
        max_features=max_features,
        random_state=random_state,
        fit_vectorizer_on="train",
    )
    prf1 = held_out_prf1(y_test, y_pred, labels=sorted(work["label"].unique()))
    return {
        "mode": "honest",
        "overlap_texts": sorted(overlap),
        "overlap_count": len(overlap),
        "accuracy": float(report["accuracy"]),
        "macro_f1": float(report["macro avg"]["f1-score"]),
        "held_out_prf1": prf1,
        "vocabulary_size": int(len(vectorizer.vocabulary_)),
        "vectorizer": vectorizer,
        "classifier": clf,
    }


def run_leaky_preprocess_pipeline(
    df: pd.DataFrame,
    *,
    random_state: int = 42,
    max_features: int = 500,
) -> dict[str, Any]:
    """Same split as honest path, but TF-IDF is fit on train+test (preprocess leak)."""
    work = df.copy()
    if "clean_text" not in work.columns:
        work["clean_text"] = work["text"].astype(str).map(clean_text)

    X_train, X_test, y_train, y_test = train_test_split(
        work["clean_text"],
        work["label"],
        test_size=0.2,
        stratify=work["label"],
        random_state=random_state,
    )
    vectorizer, clf, report, y_pred = _fit_text_classifier(
        X_train,
        X_test,
        y_train,
        y_test,
        max_features=max_features,
        random_state=random_state,
        fit_vectorizer_on="full",
    )
    prf1 = held_out_prf1(y_test, y_pred, labels=sorted(work["label"].unique()))
    return {
        "mode": "leaky_preprocess",
        "accuracy": float(report["accuracy"]),
        "macro_f1": float(report["macro avg"]["f1-score"]),
        "held_out_prf1": prf1,
        "vocabulary_size": int(len(vectorizer.vocabulary_)),
        "vocabulary": set(vectorizer.vocabulary_.keys()),
        "vectorizer": vectorizer,
        "classifier": clf,
    }


def run_target_leak_pipeline(
    df: pd.DataFrame,
    *,
    leak_col: str = LEAK_COLUMN,
    random_state: int = 42,
    max_features: int = 200,
) -> dict[str, Any]:
    """Train on TF-IDF features concatenated with a label-derived leak column."""
    work = make_target_leak_frame(df) if leak_col not in df.columns else df.copy()
    X_train, X_test, y_train, y_test = train_test_split(
        work[["clean_text", leak_col]],
        work["label"],
        test_size=0.2,
        stratify=work["label"],
        random_state=random_state,
    )
    vectorizer = TfidfVectorizer(max_features=max_features, ngram_range=(1, 1), sublinear_tf=True)
    X_train_tfidf = vectorizer.fit_transform(X_train["clean_text"])
    X_test_tfidf = vectorizer.transform(X_test["clean_text"])

    # Append the leaky numeric column (dense) to sparse TF-IDF.
    train_leak = X_train[leak_col].to_numpy().reshape(-1, 1).astype(np.float64)
    test_leak = X_test[leak_col].to_numpy().reshape(-1, 1).astype(np.float64)
    from scipy.sparse import csr_matrix, hstack

    X_train_all = hstack([X_train_tfidf, csr_matrix(train_leak)])
    X_test_all = hstack([X_test_tfidf, csr_matrix(test_leak)])

    clf = LogisticRegression(solver="liblinear", max_iter=300, random_state=random_state)
    clf.fit(X_train_all, y_train)
    y_pred = clf.predict(X_test_all)
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    prf1 = held_out_prf1(y_test, y_pred, labels=sorted(work["label"].unique()))
    flagged = detect_target_leakage_columns(work)
    return {
        "mode": "target_leak",
        "flagged_columns": flagged,
        "accuracy": float(report["accuracy"]),
        "macro_f1": float(report["macro avg"]["f1-score"]),
        "held_out_prf1": prf1,
        "leak_column": leak_col,
    }


def run_target_leak_ablation(
    df: pd.DataFrame,
    *,
    leak_col: str = LEAK_COLUMN,
    random_state: int = 42,
    max_features: int = 200,
) -> dict[str, Any]:
    """Same split/features as the leaky path but drop the leak column before fit."""
    work = make_target_leak_frame(df) if leak_col not in df.columns else df.copy()
    # Reuse honest text-only path on the same frame (ignores leak col).
    return run_honest_text_pipeline(work, random_state=random_state, max_features=max_features)


# ---------------------------------------------------------------------------
# Clinic runner
# ---------------------------------------------------------------------------


def run_clinic(
    df: pd.DataFrame | None = None,
    *,
    random_state: int = 42,
    n_overlap: int = 8,
) -> dict[str, Any]:
    """Execute all clinic scenarios and return a structured findings dict."""
    base = df if df is not None else load_and_clean()
    if "clean_text" not in base.columns:
        base = base.copy()
        base["clean_text"] = base["text"].astype(str).map(clean_text)

    # Deduplicate base for the honest reference (clinic data may be clean already).
    honest_base = base.drop_duplicates(subset=["clean_text"]).reset_index(drop=True)
    honest = run_honest_text_pipeline(honest_base, random_state=random_state)

    contamination = evaluate_with_forced_contamination(
        honest_base,
        n_overlap=n_overlap,
        random_state=random_state,
    )

    leaky_preprocess = run_leaky_preprocess_pipeline(honest_base, random_state=random_state)
    # Vocabulary / IDF differ when test tokens influence the fit.
    vocab_equal = set(honest["vectorizer"].vocabulary_.keys()) == set(
        leaky_preprocess["vectorizer"].vocabulary_.keys()
    )
    idf_equal = np.allclose(
        honest["vectorizer"].idf_,
        leaky_preprocess["vectorizer"].idf_,
    ) if (
        honest["vectorizer"].vocabulary_ == leaky_preprocess["vectorizer"].vocabulary_
    ) else False

    leaky_target = run_target_leak_pipeline(honest_base, random_state=random_state)
    ablation = run_target_leak_ablation(honest_base, random_state=random_state)

    findings = {
        "module": "module-1-foundations",
        "clinic": "leakage_metrics",
        "random_state": random_state,
        "contamination": {
            "overlap_count": contamination["overlap_count"],
            "overlap_texts_sample": contamination["overlap_texts"][:3],
            "n_injected": contamination["n_injected"],
            "polluted_accuracy": contamination["polluted_test_accuracy"],
            "honest_accuracy": contamination["clean_test_accuracy"],
            "finding": (
                "Injecting train prompts into the test set inflates held-out accuracy."
                if contamination["polluted_test_accuracy"] > contamination["clean_test_accuracy"]
                else "Contamination injection did not inflate accuracy (unexpected)."
            ),
        },
        "target_leakage": {
            "flagged_columns": leaky_target["flagged_columns"],
            "leaky_macro_f1": leaky_target["macro_f1"],
            "ablated_macro_f1": ablation["macro_f1"],
            "finding": (
                f"Column(s) {leaky_target['flagged_columns']} are deterministic of the label; "
                "dropping them collapses macro-F1 toward the honest text-only baseline."
            ),
        },
        "preprocess_leakage": {
            "vocab_equal": vocab_equal,
            "idf_equal": bool(idf_equal),
            "honest_vocab_size": honest["vocabulary_size"],
            "leaky_vocab_size": leaky_preprocess["vocabulary_size"],
            "leaky_accuracy": leaky_preprocess["accuracy"],
            "honest_accuracy": honest["accuracy"],
            "finding": (
                "Fitting TF-IDF on train+test changes vocabulary/IDF versus train-only fit."
                if (not vocab_equal or not idf_equal)
                else "Unexpected: leaky and honest vectorizers matched."
            ),
        },
        "honest_held_out": honest["held_out_prf1"],
    }
    return findings


def format_clinic_report(findings: dict[str, Any]) -> str:
    lines = [
        "=== Module 1 Leakage & Metrics Clinic ===",
        "",
        "[1] Train/test contamination",
        f"  overlap_count          = {findings['contamination']['overlap_count']}",
        f"  polluted accuracy      = {findings['contamination']['polluted_accuracy']:.3f}",
        f"  honest accuracy        = {findings['contamination']['honest_accuracy']:.3f}",
        f"  finding: {findings['contamination']['finding']}",
        "",
        "[2] Target leakage",
        f"  flagged_columns        = {findings['target_leakage']['flagged_columns']}",
        f"  leaky macro-F1         = {findings['target_leakage']['leaky_macro_f1']:.3f}",
        f"  ablated macro-F1       = {findings['target_leakage']['ablated_macro_f1']:.3f}",
        f"  finding: {findings['target_leakage']['finding']}",
        "",
        "[3] Preprocess leakage (TF-IDF fit on full data)",
        f"  vocab_equal            = {findings['preprocess_leakage']['vocab_equal']}",
        f"  idf_equal              = {findings['preprocess_leakage']['idf_equal']}",
        f"  honest vocab size      = {findings['preprocess_leakage']['honest_vocab_size']}",
        f"  leaky vocab size       = {findings['preprocess_leakage']['leaky_vocab_size']}",
        f"  finding: {findings['preprocess_leakage']['finding']}",
        "",
        "[4] Honest held-out P/R/F1 (macro)",
        f"  precision = {findings['honest_held_out']['macro']['precision']:.3f}",
        f"  recall    = {findings['honest_held_out']['macro']['recall']:.3f}",
        f"  f1-score  = {findings['honest_held_out']['macro']['f1-score']:.3f}",
        f"  accuracy  = {findings['honest_held_out']['accuracy']:.3f}",
    ]
    for label, scores in findings["honest_held_out"]["per_class"].items():
        lines.append(
            f"  {label:12s}  P={scores['precision']:.3f}  R={scores['recall']:.3f}  "
            f"F1={scores['f1-score']:.3f}  n={scores['support']}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    result = run_clinic()
    print(format_clinic_report(result))
