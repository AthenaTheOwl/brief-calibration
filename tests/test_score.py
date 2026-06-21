"""Brier math against hand-computed values."""

from __future__ import annotations

import pytest

from brief_calibration.score import Call, compute_score


def _calls(rows):
    return [Call(id=r[0], claim="x", confidence_bucket=r[1], outcome=r[2]) for r in rows]


def test_overall_brier_matches_hand_compute():
    calls = _calls([
        ("a", 0.6, True),   # (0.6 - 1)^2 = 0.16
        ("b", 0.8, False),  # (0.8 - 0)^2 = 0.64
        ("c", 0.7, True),   # (0.7 - 1)^2 = 0.09
        ("d", 0.4, False),  # (0.4 - 0)^2 = 0.16
        ("e", 0.9, True),   # (0.9 - 1)^2 = 0.01
    ])
    score = compute_score("2026-Q2", calls)
    assert score.overall_brier == pytest.approx(0.212, abs=1e-9)
    assert score.n_items == 5


def test_per_bucket_brier_groups_correctly():
    calls = _calls([
        ("a", 0.7, True),
        ("b", 0.7, True),
        ("c", 0.7, False),
        ("d", 0.3, False),
    ])
    score = compute_score("2026-Q2", calls)
    by_conf = {b.confidence: b for b in score.buckets}
    # 0.7: [(0.7-1)^2, (0.7-1)^2, (0.7-0)^2] = [0.09, 0.09, 0.49], mean = 0.2233
    assert by_conf[0.7].n == 3
    assert by_conf[0.7].brier == pytest.approx(0.2233, abs=1e-4)
    # 0.3: [(0.3-0)^2] = [0.09]
    assert by_conf[0.3].n == 1
    assert by_conf[0.3].brier == pytest.approx(0.09, abs=1e-9)


def test_rejects_off_grid_bucket():
    with pytest.raises(Exception):
        Call(id="x", claim="x", confidence_bucket=0.55, outcome=True)


def test_empty_calls_raises():
    with pytest.raises(ValueError):
        compute_score("2026-Q2", [])
