"""CLI surface — `validate`/`show` on the shipped fixture exit zero."""

from __future__ import annotations

from brief_calibration.cli import main


def test_validate_shipped_fixture_exits_zero():
    rc = main(["validate", "--period", "2026-Q2"])
    assert rc == 0


def test_validate_unknown_period_exits_nonzero():
    rc = main(["validate", "--period", "1999-Q1"])
    assert rc != 0


def test_show_no_args_exits_zero():
    # no-arg show reads the committed ledger and exits clean.
    rc = main(["show"])
    assert rc == 0


def test_show_prints_ranked_result(capsys):
    rc = main(["show", "--period", "2026-Q2"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "field brief calibration - 2026-Q2" in out
    assert "overall brier 0.212" in out
    assert "headline:" in out
    # the 0.8 band is the worst drifter in the committed ledger and must
    # rank first.
    body = out.split("headline:")[0]
    assert body.index("0.8") < body.index("0.7")


def test_show_unknown_period_exits_nonzero():
    rc = main(["show", "--period", "1999-Q1"])
    assert rc != 0
