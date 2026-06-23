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

# the real engine: the same scorer the CLI `score` verb drives. we import and
# call it live below so the interactive section is not a re-implementation.
from brief_calibration.score import Call, compute_score
from pydantic import ValidationError

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

# --------------------------------------------------------------------------
# interactive: score your OWN brief calls with the real engine.
#
# everything below drives brief_calibration.score.compute_score directly - the
# same pure function the CLI `score` verb calls. edit the calls, hit score, and
# the overall + per-band Brier recompute live off your input. nothing is
# hardcoded; the numbers come straight out of the engine.
# --------------------------------------------------------------------------
st.divider()
st.header("score your own calls")
st.caption(
    "edit the table below - one row per forecast. confidence must sit on the "
    "0.1 grid (0.1 .. 0.9); outcome is whether the claim came true. press "
    "**score calls** to run the real `compute_score` engine on your input. a "
    "well-calibrated 0.8 call that comes true scores brier 0.04; the same call "
    "that comes false scores 0.64 - watch the band light up."
)

# pre-fill with the committed worked example so there is always something to run.
DEFAULT_CALLS = [
    {"claim": "Meta defers an announced 2026 expansion site", "confidence": 0.6, "outcome": True},
    {"claim": "The Q4 alignment paper fails to replicate in 90 days", "confidence": 0.8, "outcome": False},
    {"claim": "Oracle Texas capex produces no started build by mid-Q2", "confidence": 0.7, "outcome": True},
    {"claim": "TSMC tapes out N2 on the announced schedule", "confidence": 0.4, "outcome": False},
    {"claim": "CUDA share of new training runs stays above 85%", "confidence": 0.9, "outcome": True},
]

CONF_CHOICES = [round(0.1 * i, 1) for i in range(1, 10)]

edited = st.data_editor(
    DEFAULT_CALLS,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    key="own_calls",
    column_config={
        "claim": st.column_config.TextColumn("claim", width="large"),
        "confidence": st.column_config.SelectboxColumn(
            "confidence", options=CONF_CHOICES, required=True,
            help="stated confidence, on the 0.1 grid",
        ),
        "outcome": st.column_config.CheckboxColumn(
            "came true?", help="did the claim actually happen?",
        ),
    },
)

own_period = st.text_input("period label", value="my-calls")

if st.button("score calls", type="primary"):
    rows = [r for r in edited if str(r.get("claim", "")).strip()]
    if not rows:
        st.warning("add at least one call with a non-empty claim.")
        st.stop()

    # build the engine's typed input. Call() validates the 0.1-grid rule for us;
    # surface its real error rather than swallowing it.
    try:
        calls = [
            Call(
                id=f"row-{i}",
                claim=str(r["claim"]).strip(),
                confidence_bucket=float(r["confidence"]),
                outcome=bool(r["outcome"]),
            )
            for i, r in enumerate(rows)
        ]
    except (ValidationError, ValueError, KeyError, TypeError) as e:
        st.error(f"could not validate your calls: {e}")
        st.stop()

    # >>> the real engine <<<
    result = compute_score(own_period, calls)

    m1, m2, m3 = st.columns(3)
    m1.metric(
        "overall brier", f"{result.overall_brier:.3f}",
        help="mean over your calls; 0 perfect, 0.25 coin flip",
    )
    m2.metric("scored calls", f"{result.n_items}")
    own_ranked = sorted(
        result.buckets,
        key=lambda b: drift(b.confidence, b.brier),
        reverse=True,
    )
    own_worst = own_ranked[0] if own_ranked else None
    own_worst_drift = drift(own_worst.confidence, own_worst.brier) if own_worst else 0.0
    m3.metric(
        "worst band drift", f"{own_worst_drift:+.2f}",
        help="how far your least-calibrated band sits past its floor",
    )

    own_table = []
    for b in own_ranked:
        floor = round(b.confidence * (1 - b.confidence), 4)
        d = drift(b.confidence, b.brier)
        if b.n < 8:
            read = "thin sample"
        elif d > threshold:
            read = "drifted past floor"
        else:
            read = "within floor"
        own_table.append(
            {
                "confidence": b.confidence,
                "n": b.n,
                "brier": b.brier,
                "floor": floor,
                "drift": d,
                "read": read,
            }
        )
    st.subheader(f"your bands by drift - {own_period}")
    st.dataframe(own_table, use_container_width=True, hide_index=True)

    if own_worst and own_worst_drift > threshold:
        st.info(
            f"**your headline:** the {own_worst.confidence} band is least "
            f"calibrated - brier {own_worst.brier}, {own_worst_drift:+.2f} past "
            f"its {round(own_worst.confidence * (1 - own_worst.confidence), 4)} "
            f"floor (n={own_worst.n}). re-band or retire that vocabulary first."
        )
    else:
        st.success(
            f"**your headline:** no band drifted past {threshold:+.2f}; your "
            f"vocabulary held (worst was "
            f"{own_worst.confidence if own_worst else 'n/a'} at "
            f"{own_worst_drift:+.2f})."
        )
    st.caption(
        "computed live by `brief_calibration.score.compute_score` - the same "
        "engine the CLI `score` verb runs. drift threshold is shared with the "
        "slider above."
    )
