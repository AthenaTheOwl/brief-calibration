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
    # the 0.8 band is the worst drifter in the committed ledger and must
    # rank first.
    body = out.split("headline:")[0]
    assert body.index("0.8") < body.index("0.7")
    # pin the computed floor and drift for the 0.8 row. the floor is the
    # calibrated value 0.8*(1-0.8)=0.16, so drift = 0.64 - 0.16 = +0.48.
    # under a p*p floor the 0.8 row would read floor 0.64, drift +0.00 and
    # the fixture's n=1-per-bucket ordering would not catch it.
    assert "0.8    1    0.64    0.16    +0.48" in body
    assert (
        "headline: the 0.8 confidence band is the least calibrated - "
        "brier 0.64, +0.48 past its 0.16 floor (n=1)."
    ) in out


def test_show_unknown_period_exits_nonzero():
    rc = main(["show", "--period", "1999-Q1"])
    assert rc != 0


def test_score_missing_fixture_exits_clean(capsys):
    # score must not raise a raw traceback on a missing fixture; it mirrors
    # validate's handler (stderr message, nonzero exit).
    rc = main(["score", "--period", "1999-Q1"])
    err = capsys.readouterr().err
    assert rc != 0
    assert err.startswith("score:")


def test_memo_missing_ledger_exits_clean(capsys):
    rc = main(["memo", "--period", "1999-Q1"])
    err = capsys.readouterr().err
    assert rc != 0
    assert err.startswith("memo:")
