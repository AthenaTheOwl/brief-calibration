"""CLI surface — `validate` on the shipped fixture exits zero."""

from __future__ import annotations

from brief_calibration.cli import main


def test_validate_shipped_fixture_exits_zero():
    rc = main(["validate", "--period", "2026-Q2"])
    assert rc == 0


def test_validate_unknown_period_exits_nonzero():
    rc = main(["validate", "--period", "1999-Q1"])
    assert rc != 0
