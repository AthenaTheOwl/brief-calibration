"""Memo rendering pinned to current output — a golden-master lock.

The drift math floors observed Brier at the calibrated value p*(1-p).
These characterization assertions pin that floor so any change to the
formula (e.g. p*p) fails here.
"""

from __future__ import annotations

from brief_calibration.report import _drift_amount, render_memo


# hand-built row. the 0.8 bucket makes p*(1-p) and p*p diverge:
#   correct floor 0.8*(1-0.8) = 0.16 -> drift 0.64 - 0.16 = +0.48
#   wrong   floor 0.8*0.8     = 0.64 -> drift 0.64 - 0.64 = +0.00
# the 0.3 bucket flips the drifted-most ordering under the same mutation:
#   correct floor 0.3*(1-0.3) = 0.21 -> drift 0.30 - 0.21 = +0.09
#   wrong   floor 0.3*0.3     = 0.09 -> drift 0.30 - 0.09 = +0.21
ROW = {
    "period": "2099-Q9",
    "overall_brier": 0.47,
    "n_items": 20,
    "computed_at": "2099-01-01",
    "buckets": [
        {"confidence": 0.8, "n": 10, "brier": 0.64},
        {"confidence": 0.3, "n": 10, "brier": 0.30},
    ],
}


def test_drift_amount_uses_calibrated_floor():
    assert _drift_amount(0.8, 0.64) == 0.48
    assert _drift_amount(0.3, 0.30) == 0.09


def test_render_memo_pins_drift_and_ranking():
    out = render_memo(ROW)
    # the worst-drifting band and its magnitude, verbatim.
    assert "drifted +0.48 past floor 0.16" in out
    # the drifted-most section ranks 0.8 (+0.48) above 0.3 (+0.09); under a
    # p*p floor the order flips and 0.8 drops to +0.00.
    section = out.split("## buckets that drifted most")[1]
    assert section.index("confidence 0.8") < section.index("confidence 0.3")
    assert "confidence 0.8: brier 0.64, drift +0.48 past calibrated floor (n = 10)" in section


def test_render_memo_golden_master():
    assert render_memo(ROW) == GOLDEN


GOLDEN = """# field brief calibration — 2099-Q9

- overall brier: **0.47** over n = 20
- computed at: 2099-01-01

## yield by confidence bucket

| confidence | n | brier | read |
|---|---|---|---|
| 0.3 | 10 | 0.3 | drifted +0.09 past floor 0.21 |
| 0.8 | 10 | 0.64 | drifted +0.48 past floor 0.16 |

## buckets that drifted most

- confidence 0.8: brier 0.64, drift +0.48 past calibrated floor (n = 10)
- confidence 0.3: brier 0.3, drift +0.09 past calibrated floor (n = 10)

## follow-ups

- re-band the topic clusters that resolved against confidence 0.8 (Brier 0.64, drift +0.48)
- re-band the topic clusters that resolved against confidence 0.3 (Brier 0.3, drift +0.09)

## methodology

see `docs/METHODOLOGY.md` for the rubric and revisit conditions.
"""
