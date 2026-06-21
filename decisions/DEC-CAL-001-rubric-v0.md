# DEC-CAL-001 — calibration rubric v0

- **date:** 2026-06-21
- **status:** accepted
- **revisits:** see `docs/METHODOLOGY.md` § "what revisits this"

## decision

v0.1 of the calibration harness scores brief items with Brier on a
discretized confidence vocabulary `{0.1, 0.2, ..., 0.9}`. A bucket
"drifted" if its observed Brier exceeds the calibrated floor
`p * (1 - p)` by more than 0.05. The memo names the top two drifted
buckets and proposes one of three follow-ups per bucket: retire the
band, re-band the topic cluster, or grow the sample at that bucket.

Sample size is honest: with `n < 8` in a bucket, the memo will not
propose retiring a band on that bucket's Brier alone.

## context

The Field Brief uses confidence-shaped language ("likely," "high
confidence," "I'd put this at 0.7") whose calibration has never been
measured. The author needs a quarterly verdict on which bands of the
vocabulary the brief is licensed to use. A Brier score over a small
hand-curated fixture is the cheapest mechanism that produces a useful
verdict and survives the first cycle.

## alternatives considered

- **Per-horizon Brier (30/60/90/180 days).** Deferred to spec 0003.
  v0.1 collapses to one horizon per quarter to keep the rubric
  legible. A horizon dimension lands when there's enough resolved
  data per horizon to make per-horizon Brier non-noise.
- **Cross-bucket regression instead of bucketed Brier.** Rejected for
  v0.1. Buckets are how the brief actually speaks; the rubric should
  match the vocabulary it's grading.
- **LLM-graded resolutions.** Rejected. Outcomes are human-assigned
  by the author. The rubric is a self-assessment, not a benchmark.
- **Real-time scoreboard.** Rejected. Quarterly cadence is the
  discipline; scoring more often would amplify noise.

## consequences

- The memo is the single durable artifact per quarter.
- The ledger is append-only and survives schema changes (later specs
  can add fields without rewriting history).
- The "what revisits this" section in `docs/METHODOLOGY.md` is the
  trigger for re-opening this DEC; an updated rubric becomes
  DEC-CAL-002.

## cross-references

- `PRODUCT_BRIEF.md` — who this serves and the decision it helps
- `SYSTEM_MAP.md` — the three modules and two data layers
- `docs/METHODOLOGY.md` — the rubric and its revisit conditions
- `specs/0002-design/` — the v0.1 spec set
