"""argparse entry point for brief-calibration.

Subcommands:
    validate --period <p>   typed-validate the fixture
    score    --period <p>   compute Brier, append a ledger row
    memo     --period <p>   render the memo from the latest ledger row
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

import yaml
from pydantic import ValidationError

from brief_calibration.ledger import append_row, ledger_path, read_latest
from brief_calibration.report import write_memo
from brief_calibration.score import Call, compute_score


FIXTURE_DIR = Path("data") / "fixtures"

# the repo root that ships the committed fixtures + ledger, resolved from
# this file so `show` reads the same artifact regardless of cwd.
REPO_ROOT = Path(__file__).resolve().parent.parent


def fixture_path(period: str, root: Optional[Path] = None) -> Path:
    base = (root or Path(".")) / FIXTURE_DIR
    return base / f"{period}-brief-calls.yaml"


def discover_periods(root: Optional[Path] = None) -> List[str]:
    """Return all periods that have a shipped fixture, sorted ascending."""
    base = (root or Path(".")) / FIXTURE_DIR
    if not base.exists():
        return []
    suffix = "-brief-calls.yaml"
    periods = [p.name[: -len(suffix)] for p in base.glob(f"*{suffix}")]
    return sorted(periods)


def latest_period(root: Optional[Path] = None) -> Optional[str]:
    """Return the newest shipped period, or None if no fixtures exist."""
    periods = discover_periods(root=root)
    return periods[-1] if periods else None


def load_calls(period: str, root: Optional[Path] = None) -> List[Call]:
    path = fixture_path(period, root=root)
    if not path.exists():
        raise FileNotFoundError(f"no fixture for {period} at {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    items = raw.get("items") if isinstance(raw, dict) else None
    if not items:
        raise ValueError(f"fixture {path} has no `items` list")
    return [Call(**item) for item in items]


def resolve_period(period: Optional[str]) -> Optional[str]:
    """Use the explicit period if given, else the newest shipped period."""
    if period:
        return period
    return latest_period()


def cmd_validate(args: argparse.Namespace) -> int:
    period = resolve_period(args.period)
    if period is None:
        print("validate: no fixtures found under data/fixtures", file=sys.stderr)
        return 2
    try:
        calls = load_calls(period)
    except (FileNotFoundError, ValueError) as e:
        print(f"validate: {e}", file=sys.stderr)
        return 2
    except ValidationError as e:
        print(f"validate: schema violation: {e}", file=sys.stderr)
        return 2
    print(f"validate: {period}: {len(calls)} calls ok")
    return 0


def cmd_score(args: argparse.Namespace) -> int:
    period = resolve_period(args.period)
    if period is None:
        print("score: no fixtures found under data/fixtures", file=sys.stderr)
        return 2
    calls = load_calls(period)
    score = compute_score(period, calls)
    path = append_row(score)
    print(f"score: {period}: overall brier {score.overall_brier} -> {path}")
    return 0


def cmd_memo(args: argparse.Namespace) -> int:
    period = resolve_period(args.period)
    if period is None:
        print("memo: no fixtures found under data/fixtures", file=sys.stderr)
        return 2
    path = write_memo(period)
    print(f"memo: {period}: wrote {path}")
    return 0


def _drift(conf: float, brier: float) -> float:
    """observed brier minus the calibrated floor p*(1-p) for that bucket.

    positive = worse than a perfectly-calibrated forecaster at that confidence.
    """
    return round(brier - conf * (1 - conf), 4)


def cmd_show(args: argparse.Namespace) -> int:
    """read-only: print the latest committed calibration result, ranked.

    no args, no writes, offline. defaults to the newest shipped period.
    """
    period = args.period or latest_period(root=REPO_ROOT)
    if period is None:
        print("show: no fixtures found under data/fixtures", file=sys.stderr)
        return 2
    try:
        row = read_latest(period, root=REPO_ROOT)
    except (FileNotFoundError, ValueError) as e:
        print(f"show: {e}", file=sys.stderr)
        print("show: run `score` first to write a ledger row.", file=sys.stderr)
        return 2

    overall = row["overall_brier"]
    n_items = row["n_items"]
    computed = row.get("computed_at", "unknown")
    buckets = row.get("buckets", [])

    # rank by drift past the calibrated floor, worst first.
    ranked = sorted(
        buckets, key=lambda b: _drift(b["confidence"], b["brier"]), reverse=True
    )

    print(f"field brief calibration - {period}")
    print(f"overall brier {overall} over n={n_items}   (computed {computed})")
    print("lower brier is better; 0 = perfect, 0.25 = a coin flip.")
    print()
    print(f"{'rank':>4}  {'conf':>5}  {'n':>3}  {'brier':>6}  {'floor':>6}  "
          f"{'drift':>7}  read")
    print("-" * 64)
    for i, b in enumerate(ranked, start=1):
        conf, n, brier = b["confidence"], b["n"], b["brier"]
        floor = round(conf * (1 - conf), 4)
        drift = _drift(conf, brier)
        if n < 8:
            read = "thin sample"
        elif drift > 0.05:
            read = "drifted past floor"
        else:
            read = "within floor"
        print(f"{i:>4}  {conf:>5}  {n:>3}  {brier:>6}  {floor:>6}  "
              f"{drift:>+7.2f}  {read}")
    print()

    if ranked:
        worst = ranked[0]
        wdrift = _drift(worst["confidence"], worst["brier"])
        if wdrift > 0.05:
            print(
                f"headline: the {worst['confidence']} confidence band is the "
                f"least calibrated - brier {worst['brier']}, "
                f"{wdrift:+.2f} past its {round(worst['confidence']*(1-worst['confidence']),4)} "
                f"floor (n={worst['n']}). retire or re-band first."
            )
        else:
            print(
                f"headline: no band drifted past the 0.05 threshold; the "
                f"vocabulary held this period (worst was {worst['confidence']} "
                f"at {wdrift:+.2f})."
            )
    print()
    print(f"source: {ledger_path(period, root=REPO_ROOT)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="brief_calibration")
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="typed-validate the fixture")
    v.add_argument("--period", default=None, help="defaults to the newest shipped period")
    v.set_defaults(func=cmd_validate)

    s = sub.add_parser("score", help="compute brier, append a ledger row")
    s.add_argument("--period", default=None, help="defaults to the newest shipped period")
    s.set_defaults(func=cmd_score)

    m = sub.add_parser("memo", help="render the memo for a period")
    m.add_argument("--period", default=None, help="defaults to the newest shipped period")
    m.set_defaults(func=cmd_memo)

    sh = sub.add_parser(
        "show", help="print the latest committed calibration result, ranked (read-only)"
    )
    sh.add_argument("--period", default=None, help="defaults to the newest shipped period")
    sh.set_defaults(func=cmd_show)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
