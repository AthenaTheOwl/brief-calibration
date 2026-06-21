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

from brief_calibration.ledger import append_row
from brief_calibration.report import write_memo
from brief_calibration.score import Call, compute_score


FIXTURE_DIR = Path("data") / "fixtures"


def fixture_path(period: str, root: Optional[Path] = None) -> Path:
    base = (root or Path(".")) / FIXTURE_DIR
    return base / f"{period}-brief-calls.yaml"


def load_calls(period: str, root: Optional[Path] = None) -> List[Call]:
    path = fixture_path(period, root=root)
    if not path.exists():
        raise FileNotFoundError(f"no fixture for {period} at {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    items = raw.get("items") if isinstance(raw, dict) else None
    if not items:
        raise ValueError(f"fixture {path} has no `items` list")
    return [Call(**item) for item in items]


def cmd_validate(args: argparse.Namespace) -> int:
    try:
        calls = load_calls(args.period)
    except (FileNotFoundError, ValueError) as e:
        print(f"validate: {e}", file=sys.stderr)
        return 2
    except ValidationError as e:
        print(f"validate: schema violation: {e}", file=sys.stderr)
        return 2
    print(f"validate: {args.period}: {len(calls)} calls ok")
    return 0


def cmd_score(args: argparse.Namespace) -> int:
    calls = load_calls(args.period)
    score = compute_score(args.period, calls)
    path = append_row(score)
    print(f"score: {args.period}: overall brier {score.overall_brier} -> {path}")
    return 0


def cmd_memo(args: argparse.Namespace) -> int:
    path = write_memo(args.period)
    print(f"memo: {args.period}: wrote {path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="brief_calibration")
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="typed-validate the fixture")
    v.add_argument("--period", required=True)
    v.set_defaults(func=cmd_validate)

    s = sub.add_parser("score", help="compute brier, append a ledger row")
    s.add_argument("--period", required=True)
    s.set_defaults(func=cmd_score)

    m = sub.add_parser("memo", help="render the memo for a period")
    m.add_argument("--period", required=True)
    m.set_defaults(func=cmd_memo)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
