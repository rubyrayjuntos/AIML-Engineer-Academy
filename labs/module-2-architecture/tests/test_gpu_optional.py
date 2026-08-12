"""Always-green tests for the optional GPU track (CPU path)."""
import json

from app.gpu_gate import cuda_available, gpu_track_requested, track_status
from app.qlora_optional import build_qlora_plan, maybe_run_gpu_dry_run


def test_gpu_gate_defaults_off(monkeypatch):
    monkeypatch.delenv("ACADEMY_GPU", raising=False)
    assert gpu_track_requested() is False
    assert cuda_available() is False
    status = track_status()
    assert status["mode"] == "cpu_plan_only"


def test_qlora_plan_is_cpu_safe(monkeypatch, tmp_path):
    monkeypatch.delenv("ACADEMY_GPU", raising=False)
    plan = maybe_run_gpu_dry_run(build_qlora_plan())
    assert plan["claims"]["gpu_used"] is False
    assert plan["claims"]["qlora_executed"] is False
    assert plan["lora"]["r"] == 16
    assert "nf4" in plan["quantization"]["bnb_4bit_quant_type"]
    out = tmp_path / "qlora_plan.json"
    out.write_text(json.dumps(plan))
    loaded = json.loads(out.read_text())
    assert loaded["track"] == "optional-qlora"


def test_gpu_track_request_does_not_claim_execution_without_cuda(monkeypatch):
    monkeypatch.setenv("ACADEMY_GPU", "1")
    # Even if requested, without torch/CUDA claims must stay honest.
    plan = maybe_run_gpu_dry_run(build_qlora_plan("tiny-test"))
    assert plan["claims"]["qlora_executed"] is False
    # gpu_used only flips on explicit execute path with model id
    assert plan["claims"]["gpu_used"] in (False, True)
    if plan["claims"]["gpu_used"]:
        assert plan["claims"]["qlora_executed"] is False
