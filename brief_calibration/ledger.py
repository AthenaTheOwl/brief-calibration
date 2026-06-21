"""Append-only JSONL ledger over data/ledger/<period>.jsonl."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Optional

from brief_calibration.score import PeriodScore


LEDGER_DIR = Path("data") / "ledger"


def ledger_path(period: str, root: Optional[Path] = None) -> Path:
    base = (root or Path(".")) / LEDGER_DIR
    return base / f"{period}.jsonl"


def append_row(
    score: PeriodScore,
    *,
    computed_at: Optional[date] = None,
    root: Optional[Path] = None,
) -> Path:
    """Append one row to data/ledger/<period>.jsonl. Never rewrites.

    Returns the path written to.
    """
    path = ledger_path(score.period, root=root)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = score.model_dump()
    payload["computed_at"] = (computed_at or date.today()).isoformat()

    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, sort_keys=False) + "\n")
    return path


def read_latest(period: str, root: Optional[Path] = None) -> dict:
    """Return the most recent ledger row for the given period."""
    path = ledger_path(period, root=root)
    if not path.exists():
        raise FileNotFoundError(f"no ledger for {period} at {path}")
    last: Optional[dict] = None
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                last = json.loads(line)
    if last is None:
        raise ValueError(f"ledger file {path} is empty")
    return last
