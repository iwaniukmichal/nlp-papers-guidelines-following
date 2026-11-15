"""Canonical repository paths. All paths are derived from the repository root,
so scripts work regardless of the current working directory."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

CONFIG_DIR = REPO_ROOT / "config"
RUBRIC_DIR = CONFIG_DIR / "rubric"
POLICY_REGISTER_PATH = CONFIG_DIR / "policy_register" / "register.json"
PROMPTS_DIR = CONFIG_DIR / "prompts"

DATA_DIR = REPO_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"  # gitignored
XML_DIR = RAW_DIR / "xml"
PDF_DIR = RAW_DIR / "pdfs"
PARSED_DIR = DATA_DIR / "interim" / "parsed"  # gitignored
MANIFEST_DIR = DATA_DIR / "manifest"
MANIFEST_PATH = MANIFEST_DIR / "eligible_manifest.csv"
COUNTS_PATH = MANIFEST_DIR / "counts_by_year_track.json"
SAMPLES_DIR = DATA_DIR / "samples"
ANNOTATIONS_DIR = DATA_DIR / "annotations"

RUNS_DIR = REPO_ROOT / "runs"
RESULTS_DIR = REPO_ROOT / "results"

DEFAULT_RUBRIC_VERSION = "1.0.0"


def rubric_path(version: str = DEFAULT_RUBRIC_VERSION) -> Path:
    return RUBRIC_DIR / f"rubric_v{version}.json"


def sample_path(split: str) -> Path:
    return SAMPLES_DIR / f"{split}.json"


def to_repo_relative(path: Path) -> str:
    """Store paths inside data files relative to the repo root (portable across machines)."""
    return Path(path).resolve().relative_to(REPO_ROOT).as_posix()


def from_repo_relative(path: str) -> Path:
    return REPO_ROOT / path
