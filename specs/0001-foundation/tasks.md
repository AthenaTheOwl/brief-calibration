# Spec 0001 — Tasks (Brief Calibration)

First PR (the scaffold — this commit):

- [x] R-BCL-001 scaffold: README + LICENSE + AGENTS.md + .gitignore
- [x] R-BCL-001 specs/0001-foundation/{requirements,design,tasks,acceptance}.md
- [x] R-BCL-001 docs/first-pr.md

Second PR (foundation runnable code — schema + extractor):

- [ ] R-BCL-002 `schemas/predictions.schema.json`
- [ ] R-BCL-002 `schemas/brief_item.schema.json`
- [ ] R-BCL-003 `src/ingest/brief_loader.py`
- [ ] R-BCL-003 `src/ingest/predictions_extractor.py`
- [ ] R-BCL-011 `tests/fixtures/brief_min/` with 3 brief items
- [ ] CLI: `cli/main.py` with `ingest` subcommand
- [ ] `scripts/voice_lint.py`
- [ ] `scripts/validate_schemas.py`
- [ ] `scripts/spec_check.py`
- [ ] Tests: extractor, schema validation, CLI

Third PR (backfill + scorer + memo):

- [ ] R-BCL-004 backfilled `predictions/2026-W14_to_W25.yaml`
      (manual pass against the real Field Brief repo)
- [ ] R-BCL-005 `src/score/brier.py`
- [ ] R-BCL-006 `src/score/calibration_curve.py` with SVG output
- [ ] R-BCL-007 `src/score/citation_uptake.py`
- [ ] R-BCL-008 `src/memo/renderer.py`
- [ ] R-BCL-009 `schemas/memo.schema.json` with `recommendations:` block
- [ ] CLI: `score` and `memo` subcommands
- [ ] `scripts/resolution_required.py`
- [ ] First memo `brief_calibration/2026-Q3.md`
