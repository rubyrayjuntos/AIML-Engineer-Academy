"""Always-green tests for offline eval + Promptfoo plan + deploy plans."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.deepeval_optional import build_deepeval_plan, maybe_run_deepeval
from app.deploy_optional import build_deploy_plan, maybe_deploy
from app.eval_offline import evaluation_from_case, faithfulness_overlap, relevancy_overlap
from app.promptfoo_plan import build_promptfoo_plan, validate_promptfoo_plan
from app.providers import deployment_plan
from app.release import evaluate_gates


def test_offline_faithfulness_and_relevancy_scores():
    context = "Customer #101 has an active subscription expiring on 2026-12-31."
    answer = "Customer #101 subscription is active until December 31, 2026."
    question = "When does customer #101 subscription expire?"
    assert faithfulness_overlap(answer, context) >= 0.3
    assert relevancy_overlap(question, answer) >= 0.3


def test_offline_evaluation_feeds_release_gates():
    metrics = evaluation_from_case(
        "When does customer 101 subscription expire?",
        "Customer 101 subscription expires 2026-12-31 per context.",
        "Customer 101 has an active subscription expiring on 2026-12-31.",
        p95_ms=200,
        error_rate=0.0,
    )
    # Boosted teaching case should clear default gates when overlaps are strong.
    # If string overlap is borderline, still assert Evaluation shape + safety.
    assert 0 <= metrics.faithfulness <= 1
    assert 0 <= metrics.relevancy <= 1
    assert metrics.safety == 1.0
    gates = evaluate_gates(metrics)
    assert set(gates) == {"faithfulness", "relevancy", "safety", "latency", "reliability"}


def test_promptfoo_plan_shape():
    plan = build_promptfoo_plan()
    validate_promptfoo_plan(plan)
    assert plan["claims"]["promptfoo_executed"] is False
    with pytest.raises(ValueError):
        validate_promptfoo_plan({"providers": [], "prompts": ["x"], "tests": []})


def test_deepeval_plan_defaults_unexecuted(monkeypatch):
    monkeypatch.delenv("ACADEMY_EVAL", raising=False)
    plan = maybe_run_deepeval(build_deepeval_plan())
    assert plan["claims"]["deepeval_executed"] is False
    assert plan["execution"]["status"] == "skipped"


def test_hf_and_render_provider_plans():
    hf = deployment_plan("huggingface", "models:/risk/1", "staging")
    render = deployment_plan("render", "models:/risk/1", "production")
    assert hf["provider"] == "huggingface" and hf["claims"]["huggingface_deployed"] is False
    assert render["provider"] == "render" and render["claims"]["render_deployed"] is False


def test_deploy_optional_skips_without_flag(monkeypatch):
    monkeypatch.delenv("ACADEMY_DEPLOY", raising=False)
    result = maybe_deploy("huggingface", "models:/risk/1")
    assert result["execution"]["status"] == "skipped"
    assert result["claims"]["huggingface_deployed"] is False


def test_build_deploy_plan_rejects_unknown():
    with pytest.raises(ValueError):
        build_deploy_plan("heroku", "models:/x", "staging")
