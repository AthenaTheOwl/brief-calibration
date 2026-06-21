# Spec 0002 — Acceptance (v0.1 calibration loop)

v0.1 is done when:

```
python -m brief_calibration validate --period 2026-Q2
python -m brief_calibration score    --period 2026-Q2
python -m brief_calibration memo     --period 2026-Q2
pytest -q
```

all exit zero, and:

- `data/fixtures/2026-Q2-brief-calls.yaml` exists with 3-5 items
- `data/ledger/2026-Q2.jsonl` contains at least one row written by
  the `score` subcommand
- `decisions/calibration-memo/2026-Q2.md` exists and names the
  overall Brier, the top-drifted bucket(s), and 1-3 follow-ups
- `docs/METHODOLOGY.md` has a "## what revisits this" section
- `decisions/DEC-CAL-001-rubric-v0.md` cross-references the
  methodology doc
- `STATUS.md` lists the next feature in `next_feature_queue`

Per-call Brier math matches hand-computed values to within 1e-9. The
ledger writer never rewrites an existing row; second run appends.

Out of scope for this acceptance:
- Real backfill against the Field Brief repo (spec 0003)
- Multi-horizon scoring (spec 0003)
- SVG calibration curve (spec 0003)
