# product brief

## who this serves

The Field Brief author. One forecaster, one author, one publication.
Not subscribers, not employers, not a downstream prediction-market app
in some future quarter. The user is the person who wrote the brief and
is now reading the calibration verdict.

## decision this helps

Whether to keep, retire, or re-band the confidence vocabulary the brief
uses. Concretely:

- Should the 0.8 band stay in the vocabulary, or does the author
  systematically over-claim at that band?
- Are there topic clusters where the author should drop confidence
  language entirely and switch to hedged description?
- Is a stated 0.6 actually closer to a 0.5 coin flip in practice?

The decision is not "is the brief good" or "should the brief continue."
The decision is which probabilistic claims the brief is licensed to make.

## output that matters

One file per quarter: `decisions/calibration-memo/YYYY-Qn.md`. It names
the overall Brier score, the confidence buckets that drifted most, and
one to three concrete follow-ups (retire a band, re-band a topic
cluster, increase or decrease sample size at a horizon).

Everything else in the repo — the ledger, the fixtures, the CLI — is
plumbing for that one memo.

## what this is not

- Not a leaderboard. The author is the only forecaster.
- Not an oracle. Resolution is a manual outcome flag set by the author.
- Not a publication platform. The brief lives in another repo.
- Not LLM-graded. Outcomes are human-assigned.
- Not real-time. Quarterly cadence is the discipline.

## v0.1 scope

A committed fixture of 3-5 brief calls with stated confidence plus a
manual outcome flag. One CLI command computes Brier per bucket and
appends a typed row to the ledger. A second CLI command renders the
memo. Backfilling 12 weeks of real brief items is deferred to spec 0003.
