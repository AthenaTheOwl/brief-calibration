# Spec 0001 — Acceptance (Brief Calibration)

v0 (this scaffold PR) is done when:

- `README.md`, `LICENSE`, `AGENTS.md`, `.gitignore` exist
- `specs/0001-foundation/{requirements,design,tasks,acceptance}.md` exist
- `docs/first-pr.md` describes the second PR
- README status checkboxes show the scaffold rows checked
- No code beyond what spec 0001 names lives in this repo

Spec 0002 (schema + extractor) is done when:

```bash
uv sync
uv run pytest                                            # all green
uv run brief-cal ingest \
    --brief-repo tests/fixtures/brief_min \
    --since 4w \
    --out scratch/predictions.yaml
uv run python scripts/validate_schemas.py scratch/predictions.yaml
uv run python scripts/voice_lint.py
uv run python scripts/spec_check.py
```

And:

- The extractor pulls every `predictions.yaml` block out of the
  fixture brief items
- The extracted file validates against
  `schemas/predictions.schema.json`
- The test suite runs offline

Spec 0003 (scorer + memo) is done when:

```bash
uv run brief-cal score \
    --predictions tests/fixtures/predictions_resolved.yaml \
    --as-of 2026-09-30 \
    --out scratch/scores.json
uv run brief-cal memo \
    --scores scratch/scores.json \
    --out scratch/2026-Q3.md
uv run python scripts/resolution_required.py predictions/
```

And:

- Brier scores match the hand-computed expected values within 1e-9
- The memo includes a calibration-curve SVG
- The `recommendations:` block in the memo validates against the
  source-pruning schema the Source Decay Ledger expects

Gates: `voice_lint`, `validate_schemas`, `resolution_required`,
`spec_check`. A PR that fails any gate is not merged.
