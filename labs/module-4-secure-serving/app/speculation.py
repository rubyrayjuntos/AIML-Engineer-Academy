"""
Teaching helpers for speculative decoding estimates.

These are closed-form CPU models for curriculum labs — not measured GPU/vLLM
results. Correct production acceptance sampling preserves the target model
distribution; this module only estimates expected accepted length and a
relative speedup under an i.i.d. acceptance probability.
"""
from __future__ import annotations


def expected_accepted_length(gamma: int, accept_prob: float) -> float:
    """Expected tokens emitted per speculative cycle (drafts + bonus).

    Under an i.i.d. teaching model, draft token k is reached with probability
    accept_prob**k. Summing k=1..gamma gives expected accepted drafts; the
    verify step always contributes one bonus/corrected token.
    """
    if gamma < 1:
        raise ValueError("gamma must be >= 1")
    if not 0.0 <= accept_prob <= 1.0:
        raise ValueError("accept_prob must be in [0, 1]")
    accepted_drafts = sum(accept_prob**k for k in range(1, gamma + 1))
    return float(accepted_drafts + 1.0)


def speculative_speedup(
    gamma: int,
    accept_prob: float,
    t_draft: float,
    t_verify: float,
) -> float:
    """Relative teaching speedup versus baseline one-token target decode.

    baseline throughput ∝ 1 / t_verify
    speculative throughput ∝ E[tokens] / (gamma * t_draft + t_verify)
    """
    if t_draft <= 0 or t_verify <= 0:
        raise ValueError("t_draft and t_verify must be > 0")
    tokens = expected_accepted_length(gamma, accept_prob)
    cycle_time = gamma * t_draft + t_verify
    baseline_tps = 1.0 / t_verify
    return (tokens / cycle_time) / baseline_tps
