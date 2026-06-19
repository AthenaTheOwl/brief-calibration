# Spec 0001 — Foundation (Brief Calibration)

## R-BCL-001 — repo scaffold
Repo lives at `e:/claude_code/random-apps/brief-calibration`. MIT
license, copyright Vignesh Gopalakrishnan. README, AGENTS.md,
.gitignore, and `specs/0001-foundation/` exist before any runnable
code lands.

## R-BCL-002 — predictions block schema
`schemas/predictions.schema.json` defines the YAML block that every
brief item must carry: claim, category, horizon (30 / 60 / 90 / 180
days), probability (0..1), resolution-criteria, resolution (pending
until horizon passes; true / false / unresolved-with-rationale after).

## R-BCL-003 — extractor
`src/ingest/predictions_extractor.py` reads brief Markdown files,
extracts the `predictions.yaml` block from each item, and emits a
typed list of Prediction objects.

## R-BCL-004 — backfill rule
The first run backfills 12 weeks of brief items into explicit
predictions. Implicit predictions (adjectives, hedged claims) are
made explicit by the author in a manual pass, with each backfilled
prediction marked `backfilled: true` so future calibration can be
computed separately on backfilled vs prospective predictions.

## R-BCL-005 — Brier scorer
`src/score/brier.py` computes per-category, per-horizon Brier scores
from a list of resolved predictions. Unresolved predictions are
excluded from the score; their count is reported separately.

## R-BCL-006 — calibration curve
`src/score/calibration_curve.py` bins resolved predictions by stated
probability (deciles) and reports the empirical resolution rate per
bin. Renders to a static SVG image embedded in the memo.

## R-BCL-007 — citation-uptake metric
`src/score/citation_uptake.py` counts how often a brief item or its
prediction was cited (linked back) by external sources within the
horizon window. The metric is reported per category alongside Brier.

## R-BCL-008 — quarterly memo
`src/memo/renderer.py` assembles
`brief_calibration/YYYY-Qn.md` with per-category Brier, calibration
curve, citation-uptake table, framings-to-retire list, and
source-pruning recommendations.

## R-BCL-009 — source-pruning output
The memo emits a structured `recommendations:` block consumable by
the Source Decay Ledger repo. The block lists sources whose linked
predictions performed systematically badly.

## R-BCL-010 — gates
Four gates run in CI and locally: `voice_lint`, `validate_schemas`,
`resolution_required`, `spec_check`. A PR that fails any gate is not
merged.

## R-BCL-011 — fixture
`tests/fixtures/brief_min/` ships three brief items with
`predictions.yaml` blocks (two resolved, one pending) so the test
suite runs offline.
