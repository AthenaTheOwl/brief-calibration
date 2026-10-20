"""Calibration claims carry their n; chance claims need a minimum n; the
shipped fixture is labelled synthetic wherever its scores are shown."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from brief_calibration import report
from brief_calibration.claims import (
    CHANCE_CLAIM_RE,
    MIN_N_FOR_CHANCE_CLAIM,
    chance_verdict,
    check_claims,
    claim_errors,
)
from brief_calibration.cli import load_fixture, main
from brief_calibration.ledger import read_latest
from brief_calibration.report import render_memo
from brief_calibration.score import Call, compute_score

REPO = Path(__file__).resolve().parent.parent

THIN_ROW = {
    "period": "2099-Q1",
    "overall_brier": 0.212,
    "n_items": 5,
    "computed_at": "2099-01-01",
    "buckets": [
        {"confidence": 0.8, "n": 1, "brier": 0.64},
        {"confidence": 0.6, "n": 4, "brier": 0.16},
    ],
}


def test_shipped_fixture_is_labelled_synthetic():
    calls, provenance = load_fixture("2026-Q2", root=REPO)
    assert provenance == "synthetic"
    raw = yaml.safe_load((REPO / "data/fixtures/2026-Q2-brief-calls.yaml").read_text(encoding="utf-8"))
    assert "appear in no issue" in raw["provenance_note"]
    # the ids name weeks before the brief's first issue (2026-W20)
    assert all(call.id.startswith("2026-Q1-w") for call in calls)


def test_score_writes_provenance_into_the_ledger_row(tmp_path, monkeypatch):
    fixtures = tmp_path / "data" / "fixtures"
    fixtures.mkdir(parents=True)
    (fixtures / "2099-Q2-brief-calls.yaml").write_text(
        "period: 2099-Q2\n"
        "provenance: synthetic\n"
        "items:\n"
        "  - {id: a, claim: x, confidence_bucket: 0.8, outcome: false}\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    assert main(["score", "--period", "2099-Q2"]) == 0
    assert read_latest("2099-Q2", root=tmp_path)["provenance"] == "synthetic"


def test_unknown_provenance_is_rejected(tmp_path, monkeypatch, capsys):
    fixtures = tmp_path / "data" / "fixtures"
    fixtures.mkdir(parents=True)
    (fixtures / "2099-Q4-brief-calls.yaml").write_text(
        "period: 2099-Q4\nprovenance: made-up\nitems:\n"
        "  - {id: a, claim: x, confidence_bucket: 0.8, outcome: false}\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    assert main(["validate", "--period", "2099-Q4"]) != 0
    assert "provenance must be one of" in capsys.readouterr().err


def test_chance_verdict_needs_the_minimum_n():
    assert MIN_N_FOR_CHANCE_CLAIM == 30
    below = chance_verdict(0.64, 1)
    assert below.startswith("not compared: n=1 is below the minimum of 30")
    assert not CHANCE_CLAIM_RE.search(below)
    assert chance_verdict(0.3, 40) == "brier 0.3 is worse than a coin flip (0.25) on n=40"
    assert chance_verdict(0.2, 30) == "brier 0.2 is better than a coin flip (0.25) on n=30"


def test_guard_refuses_a_chance_claim_below_the_minimum_n():
    with pytest.raises(ValueError, match="chance claim on n=1"):
        check_claims("the 0.8 band scored a Brier of 0.64, worse than a coin flip (n=1)")
    with pytest.raises(ValueError, match="without n"):
        check_claims("the 0.8 band scored a Brier of 0.64, worse than a coin flip")
    with pytest.raises(ValueError, match="without n"):
        check_claims("overall brier 0.212")
    assert check_claims("overall brier 0.3 is worse than a coin flip on n=40")


def test_memo_prints_n_beside_every_claim_and_no_chance_claim_on_thin_data():
    memo = render_memo(THIN_ROW, provenance="synthetic")
    assert claim_errors(memo.splitlines()) == []
    assert not CHANCE_CLAIM_RE.search(memo)
    assert "- data: synthetic fixtures: illustrative calls, not Field Brief items (n=5)" in memo
    assert (
        "- headline (synthetic fixtures): the 0.8 confidence band is the least "
        "calibrated - brier 0.64, +0.48 past its 0.16 floor (n=1). grow the sample "
        "before re-banding."
    ) in memo
    assert "- vs chance (overall): not compared: n=5 is below the minimum of 30" in memo


def test_memo_states_chance_at_or_above_the_minimum_n():
    row = dict(THIN_ROW, n_items=40, overall_brier=0.3, provenance="brief")
    memo = render_memo(row)
    assert "- vs chance (overall): brier 0.3 is worse than a coin flip (0.25) on n=40." in memo
    assert "- data: Field Brief items (n=40)" in memo
    assert "headline (synthetic" not in memo


def test_memo_render_fails_on_a_claim_without_n(monkeypatch):
    monkeypatch.setattr(report, "_follow_ups", lambda row: ["re-band confidence 0.8 (Brier 0.64)"])
    with pytest.raises(ValueError, match="calibration claim without n"):
        render_memo(THIN_ROW)


def test_shipped_memo_names_synthetic_fixtures_and_n():
    memo = (REPO / "decisions/calibration-memo/2026-Q2.md").read_text(encoding="utf-8")
    assert claim_errors(memo.splitlines()) == []
    assert not CHANCE_CLAIM_RE.search(memo)
    assert "synthetic fixtures: illustrative calls, not Field Brief items (n=5)" in memo
    # the committed memo is what `memo` renders from the committed ledger row
    row = read_latest("2026-Q2", root=REPO)
    assert memo == render_memo(row, provenance="synthetic")


def test_show_labels_synthetic_data_and_declines_chance(capsys):
    assert main(["show", "--period", "2026-Q2"]) == 0
    out = capsys.readouterr().out
    assert "data: synthetic fixtures: illustrative calls, not Field Brief items (n=5)" in out
    assert "vs chance (overall): not compared: n=5 is below the minimum of 30" in out
    assert not CHANCE_CLAIM_RE.search(out)


def test_compute_score_defaults_provenance_to_unspecified():
    score = compute_score("2099-Q1", [Call(id="a", claim="x", confidence_bucket=0.6, outcome=True)])
    assert score.provenance == "unspecified"
