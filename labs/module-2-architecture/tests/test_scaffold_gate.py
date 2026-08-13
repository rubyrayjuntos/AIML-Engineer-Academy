"""Scaffold / solution-mode honesty checks for Module 2 mechanics."""
from __future__ import annotations

import os

import numpy as np
import pytest

from app import mechanics_reference as ref


def test_reference_module_is_complete():
    """CI and learners must always have a working reference, independent of stubs."""
    rewards = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    adv = ref.grpo_advantages(rewards)
    assert abs(adv.mean()) < 1e-6
    alpha_bar = ref.cosine_alpha_bar(64)
    assert alpha_bar.shape == (64,)
    assert alpha_bar[0] > alpha_bar[-1]


def test_mechanics_matches_reference_when_implemented():
    """Under ACADEMY_SOLUTION=1 (or after TODOs), public mechanics must match reference."""
    from app import mechanics

    rewards = np.array([0.5, -1.5, 2.0])
    try:
        got = mechanics.grpo_advantages(rewards)
    except NotImplementedError:
        if os.environ.get("ACADEMY_SOLUTION", "").strip() == "1":
            pytest.fail("ACADEMY_SOLUTION=1 must overlay mechanics_reference")
        pytest.skip("TODO not implemented yet — complete app/mechanics.py")
    np.testing.assert_allclose(got, ref.grpo_advantages(rewards))
