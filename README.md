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

v0 scaffold. No predictions schema yet — only the spec ledger and the
file layout below. First runnable code lands in spec 0002.

- [x] Repo scaffold + LICENSE + AGENTS.md
- [x] Spec 0001 (foundation) — requirements, design, tasks, acceptance
- [x] First-PR plan in `docs/first-pr.md`
- [ ] `predictions.yaml` block schema
- [ ] Brier scorer at 30/60/90/180-day horizons
- [ ] Backfill 12 weeks of implicit predictions into explicit ones
- [ ] First quarterly memo `brief_calibration/2026-Q3.md`

## How to run

Placeholder. The runnable CLI lands in spec 0002. Intended shape:

```bash
uv sync
uv run brief-cal ingest --brief-repo ../ai-field-brief --since 12w \
    --out predictions/2026-W14_to_W25.yaml
uv run brief-cal score --predictions predictions/ --as-of 2026-09-30 \
    --out scores/2026-Q3.json
uv run brief-cal memo --scores scores/2026-Q3.json \
    --out brief_calibration/2026-Q3.md
```

Until spec 0002 lands, the only thing that runs is
`python -c "print('scaffold')"`.

## Layout

```
brief-calibration/
  README.md
  LICENSE
  AGENTS.md
  .gitignore
  specs/
    0001-foundation/
      requirements.md
      design.md
      tasks.md
      acceptance.md
  docs/
    first-pr.md
```

Planned but not yet present:

```
  cli/
    main.py
  src/
    ingest/
      brief_loader.py
      predictions_extractor.py
    score/
      brier.py
      calibration_curve.py
      citation_uptake.py
    memo/
      renderer.py
  schemas/
    predictions.schema.json
    brief_item.schema.json
    memo.schema.json
  predictions/
    2026-W14_to_W25.yaml
  scores/
    2026-Q3.json
  brief_calibration/
    2026-Q3.md
  tests/
    fixtures/
  pyproject.toml
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
