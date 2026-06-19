# AGENTS.md — brief-calibration

Operating contract for AI agents (Claude, Codex, Cursor) working in
this repo. Conventions match the rest of the AthenaTheOwl portfolio.

## What this repo is

A calibration harness over the weekly Field Brief. Every brief item
ships a `predictions.yaml` block; this repo ingests them, Brier-scores
them at 30/60/90/180-day horizons, and emits a quarterly memo plus a
"framings to retire" list plus source-pruning recommendations.

## Roles you may see in tasks

| Role | What they do |
|---|---|
| `predictions-extractor` | Reads brief Markdown items, pulls the `predictions.yaml` block |
| `resolution-curator` | Hand-resolves predictions whose horizon has passed |
| `brier-scorer` | Computes Brier per category and per horizon |
| `calibration-plotter` | Builds the calibration curve image for the memo |
| `framings-author` | Drafts the "framings to retire" list from systematic mis-calibration |
| `memo-renderer` | Assembles the quarterly memo file |

These roles exist in the spec ledger; v0 does not implement them.

## Voice constraints

- No marketing words. The memo is a self-assessment, not a launch.
- No antithetical reversals as a structural device.
- Plain assertions. The Brier score is the discipline; the prose is
  scaffolding.

## Gates (will land in spec 0002)

- `voice_lint` on every memo and predictions file
- `validate_schemas.py` — every `predictions.yaml` validates against
  `schemas/predictions.schema.json`
- `resolution_required.py` — every prediction whose horizon has passed
  has a resolution field (true / false / unresolved-with-rationale)
- `spec_check.py` — every `R-BCL-*` ID is implemented or tested by
  the time its parent PR merges

## Out of scope

- LLM-assigned resolution. A human (the author) resolves predictions.
- Cross-author calibration. The author is the only forecaster.
- Publishing the Field Brief. The brief lives in another repo; this
  repo only scores it.
- A real-time scoreboard. Quarterly cadence is the whole point.
