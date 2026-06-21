# Spec 0002 — Requirements (v0.1 calibration loop)

## R-BCL-020 — fixture
`data/fixtures/<period>-brief-calls.yaml` holds 3-5 hand-curated brief
calls per period. Each call has a stable id, a claim string, a
confidence bucket in {0.1..0.9}, and a binary `outcome` flag that the
author sets after the horizon has passed.

## R-BCL-021 — typed validation
A `validate` CLI subcommand parses the fixture, validates against the
pydantic `Call` model, and exits non-zero on any schema violation.
This is the first user action and must run with no arguments other
than the period.

## R-BCL-022 — Brier scorer
`brief_calibration/score.py::compute_score(calls)` returns a
`PeriodScore` with overall Brier (mean of per-call Briers) and a
per-bucket breakdown (n and Brier per bucket present in the input).
Pure function, no I/O.

## R-BCL-023 — ledger writer
`brief_calibration/ledger.py::append_row(period, score)` appends one
JSONL row to `data/ledger/<period>.jsonl`. The writer never rewrites
existing rows. The reader returns the most recent row for the period.

## R-BCL-024 — memo
`brief_calibration/report.py::write_memo(period)` reads the most
recent ledger row for `period` and writes
`decisions/calibration-memo/<period>.md`. The memo names the score,
the top-drifted buckets, and 1-3 follow-ups.

## R-BCL-025 — CLI surface
```
python -m brief_calibration validate --period <p>
python -m brief_calibration score    --period <p>
python -m brief_calibration memo     --period <p>
```
Each subcommand exits zero on success. No interactive prompts. No
network calls.

## R-BCL-026 — methodology doc
`docs/METHODOLOGY.md` documents the rubric (Brier formula, bucket
definition, drift threshold, sample-size honesty rule) and a "what
revisits this" section listing the conditions under which the rubric
itself gets re-opened. DEC-CAL-001 cross-references it.

## R-BCL-027 — sample size honesty
The memo names the per-bucket n explicitly and does not recommend
retiring a confidence band on n < 8. v0.1 ships with n = 1 per bucket
and the memo reads as a worked example.

## R-BCL-028 — deferred
Out of scope for v0.1 (defer to spec 0003):
- 12-week backfill against a real Field Brief repo
- 30/60/90/180-day horizons (v0.1 collapses to one horizon per quarter)
- Calibration-curve SVG
- Citation-uptake metric
- Source-pruning recommendations block
- `voice_lint`, `validate_schemas`, `resolution_required`, `spec_check`
  gates wired into CI
