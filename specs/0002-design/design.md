# Spec 0002 — Design (v0.1 calibration loop)

## shape of the loop

```
data/fixtures/<period>-brief-calls.yaml
        │  pyyaml + pydantic
        ▼
   list[Call]
        │  score.compute_score
        ▼
   PeriodScore  ──►  data/ledger/<period>.jsonl  (append-only)
        │
        ▼
   report.write_memo  ──►  decisions/calibration-memo/<period>.md
```

Three CLI subcommands map one-to-one with the three stages:
`validate`, `score`, `memo`.

## fixture shape

```yaml
period: 2026-Q2
items:
  - id: 2026-Q1-w03-meta-pause
    claim: "Meta will publicly defer at least one announced 2026 expansion site"
    confidence_bucket: 0.6
    outcome: true
  - ...
```

`confidence_bucket` is a float in `{0.1, 0.2, ..., 0.9}`. `outcome` is
strict bool — no `pending` state in the v0.1 fixture.

## modules

### score.py
Pure. Input: `list[Call]`. Output: `PeriodScore`. Computes
`brier_i = (confidence_bucket - int(outcome)) ** 2` per call and
aggregates per bucket and overall.

### ledger.py
Append-only writer over `data/ledger/<period>.jsonl`. The reader walks
the file and returns the last row (most recent scoring run).

### report.py
Reads one ledger row. Renders Markdown with:
- a header line naming the period and overall Brier
- a yield table (per-bucket n + Brier + a one-line read)
- a "buckets that drifted most" section
- a "follow-ups" section with 1-3 concrete actions

### cli.py
`argparse` group with three subcommands. Each takes `--period`. The
default fixture path is derived from the period.

## ledger row shape

```json
{
  "period": "2026-Q2",
  "overall_brier": 0.212,
  "n_items": 5,
  "buckets": [
    {"confidence": 0.4, "n": 1, "brier": 0.16},
    {"confidence": 0.6, "n": 1, "brier": 0.16},
    {"confidence": 0.7, "n": 1, "brier": 0.09},
    {"confidence": 0.8, "n": 1, "brier": 0.64},
    {"confidence": 0.9, "n": 1, "brier": 0.01}
  ],
  "computed_at": "2026-06-21"
}
```

Floats are rounded to 4 decimals in the row to keep the file
human-diffable.

## test discipline

- `tests/test_score.py` — Brier math against hand-computed values
- `tests/test_ledger.py` — round-trip a row, read it back, assert
  append (not overwrite)
- `tests/test_cli.py` — `validate --period 2026-Q2` on the shipped
  fixture exits zero

All tests run offline. No network. No external repos.
