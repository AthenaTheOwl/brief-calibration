# system map

Three modules. Two data layers. One memo per period.

## modules

```
brief_calibration/
  score.py    — Brier math over a list of resolved calls
  ledger.py   — append-only JSONL writer + per-period reader
  report.py   — composes the quarterly memo from a ledger row
  cli.py      — argparse entry: validate | score | memo
```

`score.py` is pure: it takes a list of `Call` objects and returns a
`PeriodScore` (overall Brier + per-bucket breakdown). No I/O.

`ledger.py` is the only writer of `data/ledger/<period>.jsonl`. Append
only. One row per scoring run. The reader returns the most recent row
for a given period.

`report.py` reads one ledger row and emits the memo Markdown. It does
not recompute the score. The ledger is the source of truth.

## layers

```
        fixtures (yaml, hand-curated)
              │
              ▼
        validate (pydantic)
              │
              ▼
        score    ──►  ledger row (jsonl)
              │
              ▼
        report   ──►  memo (markdown)
```

The flow is one-way. The fixture is the input; the memo is the output;
the ledger is the durable typed record in between.

## data shapes

`Call` — one row from the fixture:
- `id` (string, stable identifier)
- `claim` (string, the brief's framing)
- `confidence_bucket` (float in {0.1, 0.2, ..., 0.9})
- `outcome` (bool, manually resolved)

`BucketScore`:
- `confidence` (float)
- `n` (int)
- `brier` (float)

`PeriodScore` — one row of the ledger:
- `period` (string, e.g. "2026-Q2")
- `overall_brier` (float)
- `n_items` (int)
- `buckets` (list of BucketScore)
- `computed_at` (ISO date)

## what is not in the map

- No HTTP. No daemon. No scheduler. The CLI runs to completion and
  exits.
- No database. JSONL on disk is the ledger.
- No remote calls. Everything is local file I/O.
- No image rendering in v0.1. The calibration curve SVG is deferred
  to spec 0003.
