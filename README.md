# brief-calibration

The 0.8-confidence band scored a Brier of 0.64 — worse than a coin flip, and 0.48
past the floor that confidence was supposed to buy. The harness found that on n=1,
which is the whole point: it counts the misses before they pile up enough to feel
like a pattern.

## What it does

A weekly brief makes predictions whether it admits to or not. Which firm is
overrated, which paper won't replicate, which capex announcement evaporates — those
calls usually arrive as adjectives, unfalsifiable by design and forgotten by the
next issue. This repo makes the brief write the prediction down: an explicit,
horizon-tagged, falsifiable `predictions.yaml` block per item. Then it Brier-scores
them after the world has had its say at 30, 60, 90, and 180 days.

Every quarter it produces one calibration memo: per-band Brier and drift, a
"framings to retire" list (where the author is reliably over- or under-confident),
and source-pruning rows for the [source-decay-ledger](https://github.com/AthenaTheOwl/source-decay-ledger)
to consume. v0.1 runs end to end on a committed fixture — five hand-curated calls,
with the 2026-Q2 ledger and memo checked in as the worked example. The scorer is the
point; the data slice is deliberately narrow.

## Try it

```bash
python -m brief_calibration show
```

```
field brief calibration - 2026-Q2
overall brier 0.212 over n=5   (computed 2026-06-21)
lower brier is better; 0 = perfect, 0.25 = a coin flip.

rank   conf    n   brier   floor    drift  read
----------------------------------------------------------------
   1    0.8    1    0.64    0.16    +0.48  thin sample
   2    0.4    1    0.16    0.24    -0.08  thin sample
   3    0.6    1    0.16    0.24    -0.08  thin sample
   4    0.9    1    0.01    0.09    -0.08  thin sample
   5    0.7    1    0.09    0.21    -0.12  thin sample

headline: the 0.8 confidence band is the least calibrated - brier 0.64, +0.48 past its 0.16 floor (n=1). retire or re-band first.

source: E:\claude_code\random-apps\brief-calibration\data\ledger\2026-Q2.jsonl
```

`show` reads the committed ledger and ranks the bands by how far each drifted past
its calibrated floor, worst first. It writes nothing and exits zero. The band at the
top is the one whose stated confidence the record doesn't back up.

## live demo

A read-only Streamlit page (`streamlit_app.py`) renders the same result as
`show`: overall Brier, the per-band breakdown ranked by drift, and a headline
callout. It reads the committed `data/ledger/*.jsonl` directly — no network,
no secrets.

```bash
# local
python -m uv run --with streamlit streamlit run streamlit_app.py
# or, with requirements.txt installed:
streamlit run streamlit_app.py
```

Deploy on Streamlit Community Cloud: New app → repo `AthenaTheOwl/brief-calibration`,
branch `main`, main file `streamlit_app.py`.

<!-- live-url: (paste the Streamlit Community Cloud URL here once deployed) -->

## How it connects

- [ai-field-brief](https://github.com/AthenaTheOwl/ai-field-brief) — the weekly
  publication being scored. It makes the calls; this repo keeps the receipts. The
  brief lives there; this repo only grades it.
- [source-decay-ledger](https://github.com/AthenaTheOwl/source-decay-ledger) —
  consumes the source-pruning rows the memo emits. When a category is reliably
  wrong, the sources behind it get flagged for decay.
- [sports-prediction-os](https://github.com/AthenaTheOwl/sports-prediction-os) —
  a downstream forecasting app that wants a real prior on the author's calibration
  instead of a self-reported one.

The author is the only forecaster here, so this isn't a leaderboard. Resolution is a
human stamping resolved-true / resolved-false / unresolved — no model grades the
world. Some calls sit unresolved past 180 days and are tagged as such.

## How to run

```bash
uv sync

# typed-validate the fixture — this is the first user action
python -m brief_calibration validate --period 2026-Q2

# score and append a row to data/ledger/2026-Q2.jsonl
python -m brief_calibration score --period 2026-Q2

# render decisions/calibration-memo/2026-Q2.md from the latest row
python -m brief_calibration memo --period 2026-Q2

# print the latest committed result, ranked + readable (read-only, no args)
python -m brief_calibration show

# tests
pytest -q
```

## Layout

```
brief_calibration/   cli, score, ledger, report
data/fixtures/       2026-Q2-brief-calls.yaml — five hand-curated calls
data/ledger/         2026-Q2.jsonl — append-only scored rows
decisions/           DEC-CAL-001 rubric + calibration-memo/2026-Q2.md
docs/  specs/  tests/
```

## License

MIT. See `LICENSE`.
