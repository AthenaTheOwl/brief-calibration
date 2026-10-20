"""Locate and read a period's fixture of brief calls."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml

from brief_calibration.claims import PROVENANCES

FIXTURE_DIR = Path("data") / "fixtures"


def fixture_path(period: str, root: Optional[Path] = None) -> Path:
    base = (root or Path(".")) / FIXTURE_DIR
    return base / f"{period}-brief-calls.yaml"


def read_fixture(period: str, root: Optional[Path] = None) -> dict:
    path = fixture_path(period, root=root)
    if not path.exists():
        raise FileNotFoundError(f"no fixture for {period} at {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"fixture {path} must be a mapping")
    return raw


def provenance_of(raw: dict, path: Path) -> str:
    """The fixture's declared provenance: synthetic, brief, or unspecified."""
    provenance = raw.get("provenance", "unspecified")
    if provenance not in PROVENANCES:
        raise ValueError(
            f"fixture {path} provenance must be one of {sorted(PROVENANCES)}, "
            f"got {provenance!r}"
        )
    return provenance


def fixture_provenance(period: str, root: Optional[Path] = None) -> str:
    """Provenance of a period's fixture, or "unspecified" if it is missing."""
    try:
        raw = read_fixture(period, root=root)
        return provenance_of(raw, fixture_path(period, root=root))
    except (FileNotFoundError, ValueError, yaml.YAMLError):
        return "unspecified"
