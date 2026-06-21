"""Compose the quarterly calibration memo from a ledger row."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from brief_calibration.ledger import read_latest


MEMO_DIR = Path("decisions") / "calibration-memo"


def memo_path(period: str, root: Optional[Path] = None) -> Path:
    base = (root or Path(".")) / MEMO_DIR
    return base / f"{period}.md"


def _bucket_read(conf: float, n: int, brier: float) -> str:
    """One-line plain-language read for a bucket row.

    Calibrated Brier at confidence p on a perfectly calibrated basket
    is p*(1-p). We compare observed to that floor.
    """
    floor = round(conf * (1 - conf), 4)
    drift = round(brier - floor, 4)
    if n < 8:
        return f"n={n}, noisy; floor {floor}"
    if drift <= 0.05:
        return f"within {drift:+.2f} of floor {floor}"
    return f"drifted {drift:+.2f} past floor {floor}"


def _drift_amount(conf: float, brier: float) -> float:
    return round(brier - conf * (1 - conf), 4)


def _follow_ups(row: dict) -> list[str]:
    """Up to three concrete follow-ups derived from the buckets."""
    buckets = sorted(
        row["buckets"], key=lambda b: _drift_amount(b["confidence"], b["brier"]), reverse=True
    )
    out: list[str] = []
    for b in buckets[:3]:
        drift = _drift_amount(b["confidence"], b["brier"])
        if drift <= 0.05:
            continue
        if b["n"] < 8:
            out.append(
                f"grow the n={b['n']} sample at confidence {b['confidence']} "
                f"before deciding whether to retire that band"
            )
        else:
            out.append(
                f"re-band the topic clusters that resolved against "
                f"confidence {b['confidence']} (Brier {b['brier']}, "
                f"drift {drift:+.2f})"
            )
    if not out:
        out.append("no bucket exceeded the 0.05 drift threshold; hold the vocabulary")
    return out


def render_memo(row: dict) -> str:
    """Render the memo Markdown from a ledger row dict."""
    period = row["period"]
    overall = row["overall_brier"]
    n_items = row["n_items"]
    buckets = sorted(row["buckets"], key=lambda b: b["confidence"])

    lines: list[str] = []
    lines.append(f"# field brief calibration — {period}")
    lines.append("")
    lines.append(f"- overall brier: **{overall}** over n = {n_items}")
    lines.append(f"- computed at: {row.get('computed_at', 'unknown')}")
    lines.append("")
    lines.append("## yield by confidence bucket")
    lines.append("")
    lines.append("| confidence | n | brier | read |")
    lines.append("|---|---|---|---|")
    for b in buckets:
        lines.append(
            f"| {b['confidence']} | {b['n']} | {b['brier']} | "
            f"{_bucket_read(b['confidence'], b['n'], b['brier'])} |"
        )
    lines.append("")
    drifted = [
        b for b in sorted(buckets, key=lambda b: _drift_amount(b["confidence"], b["brier"]), reverse=True)
        if _drift_amount(b["confidence"], b["brier"]) > 0.05
    ]
    lines.append("## buckets that drifted most")
    lines.append("")
    if not drifted:
        lines.append("none past the 0.05 threshold this period.")
    else:
        for b in drifted[:2]:
            d = _drift_amount(b["confidence"], b["brier"])
            lines.append(
                f"- confidence {b['confidence']}: brier {b['brier']}, "
                f"drift {d:+.2f} past calibrated floor (n = {b['n']})"
            )
    lines.append("")
    lines.append("## follow-ups")
    lines.append("")
    for f in _follow_ups(row):
        lines.append(f"- {f}")
    lines.append("")
    lines.append("## methodology")
    lines.append("")
    lines.append("see `docs/METHODOLOGY.md` for the rubric and revisit conditions.")
    lines.append("")
    return "\n".join(lines)


def write_memo(period: str, root: Optional[Path] = None) -> Path:
    row = read_latest(period, root=root)
    path = memo_path(period, root=root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_memo(row), encoding="utf-8")
    return path
