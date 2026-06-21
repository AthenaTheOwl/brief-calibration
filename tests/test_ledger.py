"""Ledger writer is append-only; reader returns the latest row."""

from __future__ import annotations

from datetime import date

import pytest

from brief_calibration.ledger import append_row, read_latest, ledger_path
from brief_calibration.score import Call, compute_score


def _score(period: str = "2099-Q1"):
    calls = [
        Call(id="a", claim="x", confidence_bucket=0.6, outcome=True),
        Call(id="b", claim="x", confidence_bucket=0.4, outcome=False),
    ]
    return compute_score(period, calls)


def test_append_creates_file_and_writes_row(tmp_path):
    s = _score()
    append_row(s, computed_at=date(2026, 6, 21), root=tmp_path)
    path = ledger_path(s.period, root=tmp_path)
    assert path.exists()
    text = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(text) == 1


def test_append_is_append_only(tmp_path):
    s = _score()
    append_row(s, computed_at=date(2026, 6, 21), root=tmp_path)
    append_row(s, computed_at=date(2026, 6, 22), root=tmp_path)
    path = ledger_path(s.period, root=tmp_path)
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2


def test_read_latest_returns_most_recent(tmp_path):
    s = _score()
    append_row(s, computed_at=date(2026, 6, 21), root=tmp_path)
    append_row(s, computed_at=date(2026, 6, 22), root=tmp_path)
    latest = read_latest(s.period, root=tmp_path)
    assert latest["computed_at"] == "2026-06-22"
    assert latest["period"] == s.period


def test_read_latest_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_latest("9999-Q9", root=tmp_path)
