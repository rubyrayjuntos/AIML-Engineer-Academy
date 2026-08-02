"""
Deterministic text-classification baseline (Module 1 competency evidence):

  1. Load data/prompts.csv with Pandas
  2. Clean text: lowercase, strip whitespace, remove non-alphanumeric characters
  3. Stratified 80/20 train/test split (random_state=42)
  4. TF-IDF vectorization (max_features=500, unigrams + bigrams)
  5. Logistic Regression classifier (random_state=42)
  6. Print classification report (precision, recall, F1 per class)
  7. Persist fitted artefacts to pipeline_artifacts/

Run:
    python -m app.pipeline
"""
import pathlib
import re

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

_LAB_ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_PATH = _LAB_ROOT / "data" / "prompts.csv"
ARTIFACTS_DIR = _LAB_ROOT / "pipeline_artifacts"

_NONALPHA_RE = re.compile(r"[^a-z0-9\s]")


def clean_text(text: str) -> str:
    """Lowercase, strip whitespace, and remove non-alphanumeric characters."""
    return _NONALPHA_RE.sub("", text.lower().strip())


def load_and_clean(path: pathlib.Path = DATA_PATH) -> pd.DataFrame:
    """Return a DataFrame with an added ``clean_text`` column."""
    df = pd.read_csv(path)
    df["clean_text"] = df["text"].apply(clean_text)
    return df


def build_pipeline(
    df: pd.DataFrame,
    random_state: int = 42,
    max_features: int = 500,
) -> tuple[TfidfVectorizer, LogisticRegression, dict]:
    """
    Fit a TF-IDF + Logistic Regression pipeline on *df* and return
    ``(vectorizer, classifier, classification_report_dict)``.

    The split and both estimators use *random_state* so results are fully
    deterministic when called with the same data and seed.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        df["clean_text"],
        df["label"],
        test_size=0.2,
        stratify=df["label"],
        random_state=random_state,
    )

    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=(1, 2),
        sublinear_tf=True,
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    clf = LogisticRegression(solver="liblinear", max_iter=300, random_state=random_state)
    clf.fit(X_train_tfidf, y_train)

    y_pred = clf.predict(X_test_tfidf)
    report: dict = classification_report(y_test, y_pred, output_dict=True)

    return vectorizer, clf, report


if __name__ == "__main__":
    ARTIFACTS_DIR.mkdir(exist_ok=True)

    df = load_and_clean()
    vectorizer, clf, report = build_pipeline(df)

    joblib.dump(vectorizer, ARTIFACTS_DIR / "tfidf.joblib")
    joblib.dump(clf, ARTIFACTS_DIR / "classifier.joblib")

    print(classification_report(df["label"], clf.predict(vectorizer.transform(df["clean_text"]))))
    print(f"Test accuracy: {report['accuracy']:.3f}")
    print(f"Artefacts written to {ARTIFACTS_DIR}/")
