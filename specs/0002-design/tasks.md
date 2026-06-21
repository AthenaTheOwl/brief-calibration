# Spec 0002 — Tasks (v0.1 calibration loop)

This PR — the v0.1 useful slice:

- [x] R-BCL-020 `data/fixtures/2026-Q2-brief-calls.yaml` with 5 items
- [x] R-BCL-021 `brief_calibration/cli.py` — `validate` subcommand
- [x] R-BCL-022 `brief_calibration/score.py` — `compute_score`
- [x] R-BCL-023 `brief_calibration/ledger.py` — append + read
- [x] R-BCL-024 `brief_calibration/report.py` — `write_memo`
- [x] R-BCL-025 `brief_calibration/cli.py` — `score` + `memo`
- [x] R-BCL-025 `brief_calibration/__main__.py` — `python -m` entry
- [x] R-BCL-026 `docs/METHODOLOGY.md` with "what revisits this"
- [x] DEC-CAL-001 `decisions/DEC-CAL-001-rubric-v0.md`
- [x] R-BCL-022 `tests/test_score.py`
- [x] R-BCL-023 `tests/test_ledger.py`
- [x] R-BCL-021 `tests/test_cli.py`
- [x] `pyproject.toml` declaring pyyaml + pydantic + pytest
- [x] First real ledger row `data/ledger/2026-Q2.jsonl`
- [x] First real memo `decisions/calibration-memo/2026-Q2.md`

Spec 0003 (deferred from this PR):

- [ ] R-BCL-028 12-week backfill from the real Field Brief repo
- [ ] R-BCL-028 30/60/90/180-day horizon dimension
- [ ] R-BCL-028 calibration-curve SVG embedded in the memo
- [ ] R-BCL-028 citation-uptake metric
- [ ] R-BCL-028 source-pruning recommendations block
- [ ] R-BCL-028 gates wired into CI
