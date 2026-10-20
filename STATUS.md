# status

## Current state

- typed validation of the brief-calls fixture
- Brier scoring per bucket, overall and per confidence band
- append-only JSONL ledger at `data/ledger/<period>.jsonl`
- quarterly memo renderer writing
  `decisions/calibration-memo/<period>.md`
- one CLI entry: `python -m brief_calibration {validate|score|memo} --period <p>`
- first ledger row and first memo for 2026-Q2, scored on five synthetic
  fixture calls (`provenance: synthetic`): illustrative calls that predate
  the brief and appear in no issue, so the 2026-Q2 numbers describe the
  fixture, not the brief
- the memo and `show` print the provenance and the n beside every
  calibration claim, and make no comparison with chance below n = 30

## Known limits

- no real Field Brief items scored yet: the 12-week backfill against the
  real Field Brief repo has not run
- per-horizon scoring (30/60/90/180 days) — v0.1 collapses to one
  horizon per quarter
- calibration-curve SVG in the memo
- citation-uptake metric
- source-pruning recommendations block
- voice_lint / validate_schemas / resolution_required / spec_check
  gates wired into CI

## Next feature queue

1. **backfill 12 weeks of real Field Brief items** into the fixture
   format. Once n per bucket crosses 8, the memo's drift threshold
   becomes load-bearing rather than illustrative.
2. **horizon dimension** on the fixture and on the scorer. The
   ledger row grows a `by_horizon` field; the memo grows a horizon
   axis on the yield table.
3. **calibration-curve SVG** rendered into the memo. Decile bins,
   empirical resolution rate per bin, no external image hosts.
4. **citation-uptake metric** counting external citations of brief
   items within their horizon window. Reported per category.
5. **source-pruning recommendations block** in the memo, consumable
   by the Source Decay Ledger sibling repo.
6. **gates in CI** — at minimum, `pytest` on every PR and a memo
   voice check on memos.

- Resolve factory defect: METHODOLOGY.md missing revisit section
- Resolve factory defect: STATUS.md missing required section '## Current state'
- Resolve factory defect: STATUS.md missing required section '## Known limits'
- Resolve factory defect: STATUS.md missing required section '## Next feature queue'
- Resolve factory defect: claude_code review requested patch; inspect defect log
