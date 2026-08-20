"""Tests for Module 1 CPU RAG micro-lab (sparse + hashed dense + citations)."""
from __future__ import annotations

from app.rag_clinic import (
    CORPUS,
    chunk_documents,
    grounded_answer,
    hybrid_retrieve,
    run_rag_clinic,
)


def test_chunks_preserve_source_doc_ids():
    chunks = chunk_documents(CORPUS, max_chars=160)
    assert chunks
    assert {c["doc_id"] for c in chunks} == {d["doc_id"] for d in CORPUS}
    assert all(len(c["text"]) <= 160 for c in chunks)


def test_retention_query_retrieves_retention_policy():
    chunks = chunk_documents(CORPUS, max_chars=200)
    hits = hybrid_retrieve("How long are customer records retained?", chunks, k=3)
    assert hits[0]["doc_id"] == "policy-retention"


def test_grounded_answer_cites_retrieved_doc():
    chunks = chunk_documents(CORPUS, max_chars=200)
    hits = hybrid_retrieve("How long are customer records retained?", chunks, k=2)
    answer = grounded_answer("How long are customer records retained?", hits)
    assert "policy-retention" in answer["citations"]
    assert "[policy-retention]" in answer["text"]


def test_rag_claims_stay_honest():
    result = run_rag_clinic()
    assert result["claims"]["embedding_model_used"] is False
    assert result["claims"]["vector_db_used"] is False
    assert result["claims"]["citation_required"] is True


def test_hybrid_uses_both_sparse_and_dense_scores():
    chunks = chunk_documents(CORPUS, max_chars=200)
    hits = hybrid_retrieve("refund window after purchase", chunks, k=3)
    assert "sparse_score" in hits[0] and "dense_score" in hits[0]
    assert hits[0]["doc_id"] == "policy-refund"
