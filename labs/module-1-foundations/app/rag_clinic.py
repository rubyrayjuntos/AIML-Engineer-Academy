"""
Module 1 — CPU RAG micro-lab
============================
Chunk a tiny policy corpus, retrieve with TF-IDF plus a hashed bag-of-words
"dense" score, and require a ``[doc_id]`` citation in the grounded answer.

This is **not** a neural embedding model or a vector database. Evidence claims
stay false for those.

Run:
    python -m app.rag_clinic
"""
from __future__ import annotations

import hashlib
import re
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

TOKEN_RE = re.compile(r"[a-z0-9]+")

CORPUS: list[dict[str, str]] = [
    {
        "doc_id": "policy-retention",
        "title": "Records retention",
        "text": (
            "Customer records are retained for 90 days after account closure. "
            "Retention clocks start on the closure date. Backup tapes follow the same 90-day rule."
        ),
    },
    {
        "doc_id": "policy-refund",
        "title": "Refunds",
        "text": (
            "Refunds may be requested within 14 days of purchase. "
            "The refund window starts on the purchase receipt date and excludes shipping."
        ),
    },
    {
        "doc_id": "policy-support",
        "title": "Support SLA",
        "text": (
            "Support tickets are answered within one business day. "
            "Severity-1 outages page the on-call engineer immediately."
        ),
    },
]


def chunk_documents(docs: list[dict[str, str]], max_chars: int = 160) -> list[dict[str, str]]:
    """Split each document into overlapping-free windows that keep ``doc_id``."""
    chunks: list[dict[str, str]] = []
    for doc in docs:
        text = " ".join(doc["text"].split())
        start = 0
        part = 0
        while start < len(text):
            end = min(start + max_chars, len(text))
            if end < len(text):
                cut = text.rfind(" ", start, end)
                if cut > start:
                    end = cut
            piece = text[start:end].strip()
            if piece:
                chunks.append(
                    {
                        "chunk_id": f"{doc['doc_id']}#{part}",
                        "doc_id": doc["doc_id"],
                        "text": piece,
                    }
                )
                part += 1
            if end >= len(text):
                break
            start = end
    return chunks


def _tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def hashed_bag_vector(text: str, dim: int = 64) -> np.ndarray:
    """Stable signed-hash bag-of-words. Not a trained embedding."""
    vec = np.zeros(dim, dtype=np.float64)
    for tok in _tokenize(text):
        digest = hashlib.md5(tok.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:4], "little") % dim
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vec[idx] += sign
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm
    return vec


def sparse_scores(query: str, chunks: list[dict[str, str]]) -> np.ndarray:
    corpus = [c["text"] for c in chunks]
    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform(corpus)
    q = vectorizer.transform([query])
    return cosine_similarity(q, matrix).ravel()


def dense_scores(query: str, chunks: list[dict[str, str]]) -> np.ndarray:
    q = hashed_bag_vector(query)
    rows = np.vstack([hashed_bag_vector(c["text"]) for c in chunks])
    dots = rows @ q
    return dots


def hybrid_retrieve(
    query: str,
    chunks: list[dict[str, str]],
    k: int = 3,
    alpha: float = 0.65,
) -> list[dict[str, Any]]:
    sparse = sparse_scores(query, chunks)
    dense = dense_scores(query, chunks)
    blended = alpha * sparse + (1.0 - alpha) * dense
    order = np.argsort(-blended)
    hits: list[dict[str, Any]] = []
    for idx in order[:k]:
        hit = dict(chunks[int(idx)])
        hit["sparse_score"] = float(sparse[int(idx)])
        hit["dense_score"] = float(dense[int(idx)])
        hit["hybrid_score"] = float(blended[int(idx)])
        hits.append(hit)
    return hits


def grounded_answer(query: str, retrieved: list[dict[str, Any]]) -> dict[str, Any]:
    if not retrieved:
        return {"text": "No sources retrieved.", "citations": []}
    top = retrieved[0]
    citation = top["doc_id"]
    text = f"{top['text']} [{citation}]"
    return {"text": text, "citations": [citation], "query": query}


def run_rag_clinic(query: str = "How long are customer records retained?") -> dict[str, Any]:
    chunks = chunk_documents(CORPUS, max_chars=200)
    hits = hybrid_retrieve(query, chunks, k=3)
    answer = grounded_answer(query, hits)
    return {
        "module": "module-1-foundations",
        "clinic": "rag_cpu",
        "query": query,
        "n_chunks": len(chunks),
        "top_doc_id": hits[0]["doc_id"] if hits else None,
        "answer": answer,
        "claims": {
            "embedding_model_used": False,
            "vector_db_used": False,
            "citation_required": True,
        },
    }


def format_rag_report(result: dict[str, Any]) -> str:
    lines = [
        "=== Module 1 CPU RAG Clinic ===",
        f"query          = {result['query']}",
        f"chunks         = {result['n_chunks']}",
        f"top_doc_id     = {result['top_doc_id']}",
        f"citations      = {result['answer']['citations']}",
        f"answer         = {result['answer']['text']}",
        f"claims         = {result['claims']}",
        "",
        "Hashed bag-of-words is a teaching dense score — not a neural embedding or vector DB.",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    print(format_rag_report(run_rag_clinic()))
