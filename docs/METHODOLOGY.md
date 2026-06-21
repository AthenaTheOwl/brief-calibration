# methodology

How a quarter is scored, and when this rubric revisits itself.

## the rubric

Each call in the fixture is a probabilistic claim with a stated
confidence band and a binary outcome. The Brier score per call is

    brier_i = (confidence_i - outcome_i) ** 2

where `outcome_i` is 1 if the claim resolved true and 0 if it
resolved false. The overall Brier for the period is the unweighted
mean of per-call Briers. The per-bucket Brier is the mean of per-call
Briers within that confidence bucket.

A lower Brier is better. A perfectly calibrated forecaster who states
0.7 on a basket of independent claims that resolve true 70% of the
time gets a Brier of 0.21 on that basket; it is not zero, and that is
the point of the metric.

## confidence buckets

The brief's stated vocabulary discretizes to tenths:
`0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9`. A bucket of 0.5 is the
explicit coin flip and is allowed but flagged in the memo.

## what counts as resolved

- `outcome: true` — a public event (filing, statement, observable
  outcome) matches the claim's resolution criteria within the horizon
- `outcome: false` — the horizon passed and the resolution criteria
  did not occur
- Anything else is excluded from the score for this period and will
  be re-resolved next quarter

In v0.1 the fixture is hand-curated and every row has a resolved
`outcome`. The "unresolved" path lands when the spec 0003 backfill
runs against real brief items.

## confidence bucket drift

A bucket "drifted" if its Brier is meaningfully worse than the bucket
label predicts. Concretely: the bucket Brier exceeds the optimal
Brier of a calibrated forecaster at that confidence by more than
0.05. The memo names the top two buckets by drift and proposes one
of three follow-ups per bucket: retire the band, re-band the topic
cluster, or grow the sample size before re-scoring.

## sample size honesty

With fewer than 8 calls in a bucket, the per-bucket Brier is noisy.
The memo says so in plain language and does not propose retiring a
band on n < 8 alone. v0.1 ships with n = 1 per bucket; the memo will
read as a worked example, not as a verdict.

## What revisits this

DEC-CAL-001 (this rubric) revisits whenever any of the following
becomes true:

- The total resolved-call count across all quarters reaches 100,
  at which point per-bucket Brier is no longer noise-dominated and
  the bucket drift threshold should be re-derived empirically
- A bucket gets retired by a memo (the vocabulary changed; the
  rubric should record the change)
- The brief adds a new prediction horizon longer than 180 days
  (the bucket semantics may need a horizon dimension)
- Two consecutive quarters report the same top-drifted bucket
  with the same proposed follow-up and no follow-up was taken
  (the rubric is naming a problem the author won't act on; either
  the threshold or the proposal is wrong)
