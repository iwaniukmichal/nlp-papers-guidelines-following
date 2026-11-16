"""Small JSON/CSV helpers and loaders shared by all pipeline stages."""

import csv
import json
from pathlib import Path

from emnlp_audit import paths


def read_json(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: Path, obj) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def read_csv(path: Path) -> list[dict]:
    with Path(path).open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    if not rows and not fieldnames:
        return
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames or list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_records(path_without_suffix: Path, rows: list[dict]) -> None:
    """Write the same records as both .json and .csv."""
    base = Path(path_without_suffix)
    write_json(base.with_suffix(".json"), rows)
    write_csv(base.with_suffix(".csv"), rows)


def load_rubric(version: str = paths.DEFAULT_RUBRIC_VERSION) -> dict:
    return read_json(paths.rubric_path(version))


def load_sample(split: str) -> list[dict]:
    path = paths.sample_path(split)
    if not path.exists():
        raise SystemExit(f"Sample '{split}' not found at {path}. Run scripts/02_draw_sample.py first.")
    return read_json(path)
