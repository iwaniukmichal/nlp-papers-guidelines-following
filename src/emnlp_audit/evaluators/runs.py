"""Run directories: every evaluator execution is archived in runs/<run_id>/ and never overwritten.

Each run folder contains evaluations.{csv,json}, config.json (model, prompt hash,
rubric version, parser, sample) and, for LLM runs, usage.json.
"""

import datetime as dt
from pathlib import Path

from emnlp_audit import paths


def make_run_id(split: str, evaluator: str, rubric_version: str, date: dt.date | None = None) -> str:
    date = date or dt.date.today()
    return f"{date.isoformat()}_{split}_{evaluator}_rubric-v{rubric_version}"


def create_run_dir(run_id: str) -> Path:
    run_dir = paths.RUNS_DIR / run_id
    if run_dir.exists():
        raise SystemExit(
            f"Run directory already exists: {run_dir}\n"
            "Runs are archived and never overwritten; use --run-id to choose a new name."
        )
    run_dir.mkdir(parents=True)
    return run_dir


def resolve_run_dir(run: str) -> Path:
    """Accept a run id (folder name under runs/) or a path."""
    candidate = Path(run)
    if not candidate.exists():
        candidate = paths.RUNS_DIR / run
    if not (candidate / "evaluations.json").exists():
        raise SystemExit(f"No evaluations.json found for run '{run}' (looked in {candidate}).")
    return candidate
