"""Brier scoring over a list of brief calls.

Pure module. No file I/O. The CLI handles loading and writing.
"""

from __future__ import annotations

from collections import defaultdict
from typing import List

from pydantic import BaseModel, Field, field_validator


VALID_BUCKETS = {round(b * 0.1, 1) for b in range(1, 10)}


class Call(BaseModel):
    """One scored brief item."""

    id: str
    claim: str
    confidence_bucket: float
    outcome: bool

    @field_validator("confidence_bucket")
    @classmethod
    def _bucket_in_range(cls, v: float) -> float:
        rounded = round(v, 1)
        if rounded not in VALID_BUCKETS:
            raise ValueError(
                f"confidence_bucket must be one of {sorted(VALID_BUCKETS)}, got {v}"
            )
        return rounded


class BucketScore(BaseModel):
    confidence: float
    n: int
    brier: float


class PeriodScore(BaseModel):
    period: str
    overall_brier: float
    n_items: int
    buckets: List[BucketScore] = Field(default_factory=list)


def _round4(x: float) -> float:
    return round(x, 4)


def compute_score(period: str, calls: List[Call]) -> PeriodScore:
    """Compute overall and per-bucket Brier for a period.

    brier_i = (confidence_bucket - int(outcome)) ** 2
    overall = mean over calls
    per-bucket = mean over calls whose bucket matches
    """
    if not calls:
        raise ValueError("compute_score requires at least one call")

    per_bucket: dict[float, list[float]] = defaultdict(list)
    total = 0.0
    for c in calls:
        b = (c.confidence_bucket - (1.0 if c.outcome else 0.0)) ** 2
        per_bucket[c.confidence_bucket].append(b)
        total += b

    overall = total / len(calls)
    buckets = [
        BucketScore(
            confidence=conf,
            n=len(briers),
            brier=_round4(sum(briers) / len(briers)),
        )
        for conf, briers in sorted(per_bucket.items())
    ]

    return PeriodScore(
        period=period,
        overall_brier=_round4(overall),
        n_items=len(calls),
        buckets=buckets,
    )
