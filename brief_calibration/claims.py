"""Guard for calibration claims: every claim carries its n, and a claim
about chance needs a minimum n.

A Brier score on one call is a single squared error. "Worse than a coin
flip" from n=1 says nothing about the forecaster, so the memo and `show`
refuse that comparison below MIN_N_FOR_CHANCE_CLAIM resolved calls and
print the n beside every line that states a Brier, a drift or a
calibration verdict. The threshold is documented in docs/METHODOLOGY.md
("sample size honesty").
"""

from __future__ import annotations

import re
from typing import Iterable, Optional

# resolved calls behind a Brier before it may be compared with chance
MIN_N_FOR_CHANCE_CLAIM = 30

# Brier of always saying 0.5: the coin-flip reference
COIN_FLIP_BRIER = 0.25

PROVENANCES = {"synthetic", "brief", "unspecified"}

CHANCE_CLAIM_RE = re.compile(
    r"\b(?:worse|better|no better|no worse)\s+than\s+(?:a\s+)?(?:coin[\s-]?flip|chance|random)",
    re.IGNORECASE,
)
CLAIM_WORD_RE = re.compile(r"\bbrier\b|\bdrift|\bcalibrat", re.IGNORECASE)
N_RE = re.compile(r"\bn\s*=\s*(\d+)")


def provenance_label(provenance: Optional[str]) -> str:
    """Plain words for where a period's calls came from."""
    if provenance == "synthetic":
        return "synthetic fixtures: illustrative calls, not Field Brief items"
    if provenance == "brief":
        return "Field Brief items"
    return "provenance not declared"


def chance_verdict(brier: float, n: int) -> str:
    """Compare a Brier with a coin flip, or say why it is not compared."""
    if n < MIN_N_FOR_CHANCE_CLAIM:
        return (
            f"not compared: n={n} is below the minimum of "
            f"{MIN_N_FOR_CHANCE_CLAIM} for a comparison with a coin flip"
        )
    if brier > COIN_FLIP_BRIER:
        side = "worse than a coin flip"
    elif brier < COIN_FLIP_BRIER:
        side = "better than a coin flip"
    else:
        side = "level with a coin flip"
    return f"brier {brier} is {side} ({COIN_FLIP_BRIER}) on n={n}"


def claim_errors(lines: Iterable[str]) -> list[str]:
    """Lines that state a calibration claim without n, or that compare
    with chance on fewer than MIN_N_FOR_CHANCE_CLAIM calls.

    Table rows and headings are skipped: a table carries n in its own
    column.
    """
    errors: list[str] = []
    for line in lines:
        text = line.strip()
        if not text or text.startswith(("|", "#")):
            continue
        is_chance = bool(CHANCE_CLAIM_RE.search(text))
        if not (is_chance or CLAIM_WORD_RE.search(text)):
            continue
        counts = [int(m) for m in N_RE.findall(text)]
        if not counts:
            errors.append(f"calibration claim without n: {text}")
        elif is_chance and min(counts) < MIN_N_FOR_CHANCE_CLAIM:
            errors.append(
                f"chance claim on n={min(counts)}, below the minimum of "
                f"{MIN_N_FOR_CHANCE_CLAIM}: {text}"
            )
    return errors


def check_claims(text: str) -> str:
    """Return `text` unchanged, or raise ValueError naming each bad line."""
    errors = claim_errors(text.splitlines())
    if errors:
        raise ValueError("; ".join(errors))
    return text
