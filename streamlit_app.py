"""brief-calibration - live demo (Streamlit Community Cloud).

Reads the committed calibration ledger under data/ledger/<period>.jsonl and
shows how well the Field Brief's stated confidence matched reality: an overall
Brier score plus a per-confidence-band breakdown ranked by how far each band
drifted past its calibrated floor p*(1-p). No network, no secrets - runs
entirely off the committed ledger.

Deploy: Streamlit Community Cloud -> New app -> repo AthenaTheOwl/brief-calibration,
branch main, main file streamlit_app.py.
"""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

REPO = Path(__file__).resolve().parent
LEDGER = REPO / "data" / "ledger"


def list_periods() -> list[str]:
    return sorted(p.stem for p in LEDGER.glob("*.jsonl"))


def load_latest_row(period: str) -> dict | None:
    path = LEDGER / f"{period}.jsonl"
    if not path.exists():
        return None
    last = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            last = json.loads(line)
    return last


def drift(conf: float, brier: float) -> float:
    """observed brier minus the calibrated floor p*(1-p) for that band."""
    return round(brier - conf * (1 - conf), 4)


st.set_page_config(page_title="brief-calibration", layout="wide")
st.title("brief-calibration")
st.caption(
    "brier-score the Field Brief's stated confidence against what actually "
    "happened. lower brier is better: 0 is perfect, 0.25 is a coin flip. "
    "drift is observed brier minus the p*(1-p) floor a perfectly-calibrated "
    "forecaster would hit at that confidence."
)

periods = list_periods()
if not periods:
    st.warning("no ledger found under data/ledger/*.jsonl - run `score` first.")
    st.stop()

period = st.selectbox("period", periods, index=len(periods) - 1)
row = load_latest_row(period)
if not row:
    st.warning(f"ledger for {period} is empty.")
    st.stop()

overall = row.get("overall_brier", 0.0)
n_items = row.get("n_items", 0)
computed = row.get("computed_at", "unknown")
buckets = row.get("buckets", [])

ranked = sorted(buckets, key=lambda b: drift(b["confidence"], b["brier"]), reverse=True)
worst = ranked[0] if ranked else None
worst_drift = drift(worst["confidence"], worst["brier"]) if worst else 0.0

c1, c2, c3 = st.columns(3)
c1.metric("overall brier", f"{overall:.3f}", help="mean over all scored calls; 0 perfect, 0.25 coin flip")
c2.metric("scored calls", f"{n_items}")
c3.metric(
    "worst band drift",
    f"{worst_drift:+.2f}",
    help="how far the least-calibrated band sat past its floor",
)

threshold = st.slider(
    "drift threshold (highlight bands past this)", 0.0, 0.5, 0.05, step=0.01
)

table = []
for b in ranked:
    conf, n, brier = b["confidence"], b["n"], b["brier"]
    floor = round(conf * (1 - conf), 4)
    d = drift(conf, brier)
    if n < 8:
        read = "thin sample"
    elif d > threshold:
        read = "drifted past floor"
    else:
        read = "within floor"
    table.append(
        {
            "confidence": conf,
            "n": n,
            "brier": brier,
            "floor": floor,
            "drift": d,
            "read": read,
        }
    )

st.subheader(f"bands by drift - {period}  (computed {computed})")
st.dataframe(table, use_container_width=True, hide_index=True)

flagged = [t for t in table if t["read"] == "drifted past floor"]
if worst and worst_drift > threshold:
    st.info(
        f"**headline:** the {worst['confidence']} confidence band is the least "
        f"calibrated - brier {worst['brier']}, {worst_drift:+.2f} past its "
        f"{round(worst['confidence'] * (1 - worst['confidence']), 4)} floor "
        f"(n={worst['n']}). {len(flagged)} band(s) drifted past {threshold:+.2f}. "
        f"retire or re-band these first."
    )
else:
    st.info(
        f"**headline:** no band drifted past {threshold:+.2f} this period; the "
        f"vocabulary held (worst was {worst['confidence'] if worst else 'n/a'} "
        f"at {worst_drift:+.2f})."
    )

st.caption(
    "v0.1 ships one quarter (2026-Q2) as the worked example; bands are thin "
    "(n=1) until the 12-week backfill lands. the scorer + ledger live in "
    "`brief_calibration/`; this page reads the committed `data/ledger/*.jsonl`. "
    "repo: github.com/AthenaTheOwl/brief-calibration"
)
