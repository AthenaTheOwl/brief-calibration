# Field Brief Calibration Harness

Treats each weekly Field Brief as a model whose explicit predictions
are Brier-scored at 30, 60, 90, and 180 days. Per-category calibration
error feeds back into source pruning and editorial voice. Per-quarter
output is a single calibration memo plus a "framings to retire" list.

## What this is

The Field Brief is a weekly publication. Every week it makes implicit
predictions: which firm is overrated, which paper will fail to
replicate, which capex announcement will not materialize. Those
predictions usually live as adjectives. This repo asks every brief
item to expose a `predictions.yaml` block — explicit, falsifiable,
horizon-tagged — and then scores them after the fact.

The output, every quarter, is one memo with three things:

1. Per-category Brier score, calibration curve, and citation-uptake
2. A "framings to retire" list (categories where the author is
   systematically over- or under-confident)
3. Source-pruning recommendations for the Source Decay Ledger to
   consume

## Status

v0.1 — a useful narrow slice runs end to end on a committed fixture.

- [x] Repo scaffold + LICENSE + AGENTS.md
- [x] Spec 0001 (foundation) — requirements, design, tasks, acceptance
- [x] Spec 0002 (v0.1 calibration loop) — requirements, design,
      tasks, acceptance
- [x] Brier scorer over `data/fixtures/<period>-brief-calls.yaml`
- [x] Append-only JSONL ledger at `data/ledger/<period>.jsonl`
- [x] First quarterly memo at
      `decisions/calibration-memo/2026-Q2.md`
- [x] DEC-CAL-001 rubric and `docs/METHODOLOGY.md`
- [ ] Backfill 12 weeks of real brief items (spec 0003)
- [ ] Per-horizon scoring at 30/60/90/180 days (spec 0003)
- [ ] Calibration-curve SVG embedded in the memo (spec 0003)

See `STATUS.md` for the next-feature queue.

## How to run

```bash
uv sync

# typed-validate the fixture — this is the first user action
python -m brief_calibration validate --period 2026-Q2

# score and append a row to data/ledger/2026-Q2.jsonl
python -m brief_calibration score --period 2026-Q2

# render decisions/calibration-memo/2026-Q2.md from the latest row
python -m brief_calibration memo --period 2026-Q2

# tests
pytest -q
```

The fixture at `data/fixtures/2026-Q2-brief-calls.yaml` ships with
five hand-curated calls; the ledger and memo for 2026-Q2 are
committed as the worked example.

## Layout

```
brief-calibration/
  README.md
  LICENSE
  AGENTS.md
  PRODUCT_BRIEF.md
  SYSTEM_MAP.md
  STATUS.md
  pyproject.toml
  brief_calibration/
    __init__.py
    __main__.py
    cli.py
    score.py
    ledger.py
    report.py
  data/
    fixtures/
      2026-Q2-brief-calls.yaml
    ledger/
      2026-Q2.jsonl
  decisions/
    DEC-CAL-001-rubric-v0.md
    calibration-memo/
      2026-Q2.md
  docs/
    METHODOLOGY.md
    first-pr.md
  specs/
    0001-foundation/
    0002-design/
  tests/
    test_score.py
    test_ledger.py
    test_cli.py
```

## Who this is for

- The Field Brief author (the primary consumer) — calibration over
  vibes
- The Source Decay Ledger (a sibling repo) which consumes the
  source-pruning recommendations
- Anyone running a regular prediction-shaped publication who wants a
  scoring discipline that survives more than two cycles
- Downstream: a prediction-market or forecasting app in the big-app
  set that wants a real prior on the author's calibration

## What this is not

- Not an oracle. Resolution depends on the world; some predictions
  remain unresolved past the 180-day horizon and are tagged as such.
- Not a leaderboard. The author is the only forecaster. The point is
  calibration over time, not ranking.
- Not a publication platform. The Field Brief lives in another repo.
  This repo only scores it.
- Not LLM-graded resolution. A human (the author) assigns
  resolved-true / resolved-false / unresolved.

## License

MIT. See `LICENSE`.
