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

from pydantic import ValidationError

from brief_calibration.claims import provenance_label
from brief_calibration.fixture import (
    FIXTURE_DIR,
    fixture_path,  # noqa: F401  (kept importable from cli)
    fixture_provenance,
    provenance_of,
    read_fixture,
)
from brief_calibration.ledger import append_row, ledger_path, read_latest
from brief_calibration.report import headline_lines, write_memo
from brief_calibration.score import Call, check_unique_ids, compute_score

# the repo root that ships the committed fixtures + ledger, resolved from
# this file so `show` reads the same artifact regardless of cwd.
REPO_ROOT = Path(__file__).resolve().parent.parent


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


def load_fixture(period: str, root: Optional[Path] = None) -> tuple[List[Call], str]:
    """The period's calls and the fixture's declared provenance."""
    path = fixture_path(period, root=root)
    raw = read_fixture(period, root=root)
    items = raw.get("items")
    if not items:
        raise ValueError(f"fixture {path} has no `items` list")
    if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
        raise ValueError(f"fixture {path} `items` must be a list of mappings")
    return [Call(**item) for item in items], provenance_of(raw, path)


def load_calls(period: str, root: Optional[Path] = None) -> List[Call]:
    return load_fixture(period, root=root)[0]


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
        calls, provenance = load_fixture(period)
        check_unique_ids(calls)
    except ValidationError as e:
        # before ValueError: pydantic v2 ValidationError subclasses it.
        print(f"validate: schema violation: {e}", file=sys.stderr)
        return 2
    except (FileNotFoundError, ValueError) as e:
        print(f"validate: {e}", file=sys.stderr)
        return 2
    print(f"validate: {period}: {len(calls)} calls ok ({provenance_label(provenance)})")
    return 0


def cmd_score(args: argparse.Namespace) -> int:
    period = resolve_period(args.period)
    if period is None:
        print("score: no fixtures found under data/fixtures", file=sys.stderr)
        return 2
    try:
        calls, provenance = load_fixture(period)
        score = compute_score(period, calls, provenance=provenance)
    except ValidationError as e:
        # before ValueError: pydantic v2 ValidationError subclasses it.
        print(f"score: schema violation: {e}", file=sys.stderr)
        return 2
    except (FileNotFoundError, ValueError) as e:
        print(f"score: {e}", file=sys.stderr)
        return 2
    path = append_row(score)
    print(f"score: {period}: overall brier {score.overall_brier} -> {path}")
    return 0


def cmd_memo(args: argparse.Namespace) -> int:
    period = resolve_period(args.period)
    if period is None:
        print("memo: no fixtures found under data/fixtures", file=sys.stderr)
        return 2
    try:
        path = write_memo(period)
    except (FileNotFoundError, ValueError) as e:
        print(f"memo: {e}", file=sys.stderr)
        print("memo: run `score` first to write a ledger row.", file=sys.stderr)
        return 2
    except ValidationError as e:
        print(f"memo: schema violation: {e}", file=sys.stderr)
        return 2
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

    try:
        claims = headline_lines(row, fixture_provenance(period, root=REPO_ROOT))
    except ValueError as e:
        print(f"show: {e}", file=sys.stderr)
        return 2
    for line in claims:
        print(line)
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
