# Spec 0001 — Design (Brief Calibration)

## Pipeline shape

```
Field Brief repo (../ai-field-brief)
     │
     │  weekly Markdown items, each with a predictions.yaml block
     ▼
ingest ──► predictions/<weeks>.yaml
             │
             ▼
(horizon passes; human resolves)
             │
             ▼
score ──► scores/YYYY-Qn.json
             │
             ▼
memo  ──► brief_calibration/YYYY-Qn.md
```

Three CLI commands map one-to-one with the three stages:
`brief-cal ingest`, `brief-cal score`, `brief-cal memo`.

## Predictions block shape

```yaml
# embedded in a brief item's Markdown front-matter
predictions:
  - id: 2026-W22-meta-pause
    claim: "Meta will publicly defer at least one announced 2026 expansion site"
    category: ai-infra
    horizon_days: 90
    probability: 0.6
    resolution_criteria: >
      Public statement, SEC filing, or news report confirming a
      named expansion site is paused, delayed, or cancelled.
    resolution: pending          # pending | true | false | unresolved
    backfilled: false
```

## Module map

```
cli/
  main.py
src/
  ingest/
    brief_loader.py            # walks the Field Brief repo
    predictions_extractor.py   # pulls predictions.yaml blocks
  score/
    brier.py                   # per-category, per-horizon
    calibration_curve.py       # decile binning + SVG
    citation_uptake.py
  memo/
    renderer.py
schemas/
  predictions.schema.json
  brief_item.schema.json
  memo.schema.json
predictions/
  2026-W14_to_W25.yaml         # ingested + resolved over time
scores/
  2026-Q3.json
brief_calibration/
  2026-Q3.md
```

## Resolution discipline

- Resolution is a human-only operation. The author opens
  `predictions/<file>.yaml` and updates `resolution:` once the
  horizon has passed.
- A `resolution_required.py` gate fails CI if any prediction whose
  horizon is in the past is still `pending` past a 14-day grace.
- An `unresolved-with-rationale` resolution is allowed and excluded
  from the Brier score; the rationale is included in the memo.

## Memo shape

```markdown
# Field Brief Calibration — 2026-Q3
- Predictions resolved this quarter: 47
- Predictions backfilled: 21 (excluded from prospective Brier)
- Predictions unresolved: 5

## Brier by category (prospective only)
| category    | n | Brier | calibration |
|-------------|---|-------|-------------|
| ai-infra    | 12 | 0.18 | well-calibrated at 0.6-0.8 band |
| ...

## Calibration curve
![calibration](2026-Q3-calibration.svg)

## Framings to retire
- "the X capex announcement is real": consistently overconfident
- ...

## Source-pruning recommendations
recommendations:
  - source: <name>
    reason: linked predictions scored 0.35 Brier over n=8
  - ...
```

## Test discipline

- One unit test per `R-BCL-*` requirement
- Integration test over `tests/fixtures/brief_min/` running the
  three-stage pipeline end-to-end
- All tests offline
