"""Tests for speculative decoding teaching helpers."""
import pytest

from app.speculation import expected_accepted_length, speculative_speedup


def test_expected_accepted_length_gamma1_always_bonus():
    # With gamma=1 and p=0, still emit the bonus/corrected token.
    assert expected_accepted_length(1, 0.0) == pytest.approx(1.0)
    # With p=1, accept the single draft + bonus => 2
    assert expected_accepted_length(1, 1.0) == pytest.approx(2.0)


def test_expected_accepted_length_increases_with_p():
    low = expected_accepted_length(5, 0.3)
    high = expected_accepted_length(5, 0.8)
    assert high > low
    assert low > 1.0


def test_speculative_speedup_positive_when_drafts_cheap():
    speedup = speculative_speedup(gamma=5, accept_prob=0.7, t_draft=0.2, t_verify=1.0)
    assert speedup > 1.0
    # Expensive drafts + low acceptance should beat less hard (may drop below 1)
    slow = speculative_speedup(gamma=8, accept_prob=0.2, t_draft=0.9, t_verify=1.0)
    assert slow < speedup


def test_speculation_rejects_bad_args():
    with pytest.raises(ValueError):
        expected_accepted_length(0, 0.5)
    with pytest.raises(ValueError):
        expected_accepted_length(3, 1.5)
    with pytest.raises(ValueError):
        speculative_speedup(3, 0.5, t_draft=0.0, t_verify=1.0)
