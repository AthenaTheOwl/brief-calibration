# First PR after the scaffold

This file describes the literal next PR after the v0 scaffold lands.
Spec 0002 is the work plan; this file is the file-level changeset.

## Goal

A `brief-cal ingest` command that walks a Field Brief repo, pulls
every `predictions.yaml` block out of the brief items, and emits a
single combined predictions file. Schemas land for both the per-item
predictions block and the per-brief-item front-matter.

No scoring yet, no memo yet. The point of this PR is to lock in the
predictions block shape and the extractor so the Field Brief author
can start emitting structured predictions in the next weekly cycle.

## Files changed

New:

- `pyproject.toml` — Python 3.11, `uv`, `pyyaml`, `pydantic`,
  `jsonschema`, `click`
- `cli/main.py` — `click` group with `ingest`
- `src/__init__.py`
- `src/ingest/__init__.py`
- `src/ingest/brief_loader.py` — walks the Field Brief repo, returns
  brief-item paths
- `src/ingest/predictions_extractor.py` — pulls predictions block,
  validates, returns Prediction list
- `schemas/predictions.schema.json`
- `schemas/brief_item.schema.json`
- `tests/fixtures/brief_min/2026-W22-ai-infra-watch.md` (with valid
  predictions block)
- `tests/fixtures/brief_min/2026-W23-supply-chain-watch.md`
- `tests/fixtures/brief_min/2026-W24-meta-pause.md`
- `tests/fixtures/expected/2026-W22_to_W24_predictions.yaml`
- `tests/test_brief_loader.py`
- `tests/test_predictions_extractor.py`
- `tests/test_cli_ingest.py`
- `tests/test_schema_validates.py`
- `scripts/voice_lint.py`
- `scripts/validate_schemas.py`
- `scripts/spec_check.py`
- `predictions/.gitkeep`

Modified:

- `README.md` — replace placeholder "How to run" with the real command
- `specs/0001-foundation/tasks.md` — check off spec-0002 rows
- `AGENTS.md` — point Gates section at the real scripts

## Verification

```bash
uv sync
uv run pytest -v
uv run brief-cal ingest \
    --brief-repo tests/fixtures/brief_min \
    --since 4w \
    --out scratch/predictions.yaml
diff scratch/predictions.yaml \
     tests/fixtures/expected/2026-W22_to_W24_predictions.yaml
uv run python scripts/validate_schemas.py scratch/predictions.yaml
uv run python scripts/voice_lint.py
uv run python scripts/spec_check.py
```

## Out of scope for this PR

- The Brier scorer (spec 0003)
- The calibration curve + SVG (spec 0003)
- The citation-uptake metric (spec 0003)
- The memo renderer (spec 0003)
- The first real quarterly memo (spec 0003)
- The 12-week manual backfill (spec 0003)
