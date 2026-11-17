"""Reproducible sampling of papers from the eligible manifest."""

import random

from emnlp_audit import paths
from emnlp_audit.files import read_json


def _load_existing_sample_ids() -> set[str]:
    """Return all anthology_ids already drawn in any frozen sample in data/samples/*.json."""
    used = set()
    if paths.SAMPLES_DIR.exists():
        for p in sorted(paths.SAMPLES_DIR.glob("*.json")):
            for row in read_json(p):
                if "anthology_id" in row:
                    used.add(row["anthology_id"])
    return used


def draw_pilot_sample(all_papers: list[dict], years: list[int], seed: int, split_name: str) -> list[dict]:
    """
    Pilot design: 1 Main + 1 Findings paper per year, drawn uniformly within each year-track stratum.
    Records the split name, seed and inclusion probability on every sampled paper.
    """
    rng = random.Random(seed)
    sample = []
    for year in years:
        year_main = [p for p in all_papers if p["year"] == year and p["track"] == "Main"]
        year_findings = [p for p in all_papers if p["year"] == year and p["track"] == "Findings"]

        selected = []
        if year_main:
            selected.append(rng.choice(year_main))
        if year_findings:
            selected.append(rng.choice(year_findings))
        elif len(year_main) >= 2:
            remaining = [p for p in year_main if p not in selected]
            selected.append(rng.choice(remaining))

        for p in selected:
            p_copy = dict(p)
            p_copy["sample_split"] = split_name
            p_copy["random_seed"] = seed
            track_total = len(year_main) if p["track"] == "Main" else len(year_findings)
            p_copy["inclusion_probability"] = round(1.0 / track_total, 6) if track_total > 0 else 0.0
            sample.append(p_copy)
    return sample


def draw_proportional_sample(
    all_papers: list[dict],
    years: list[int],
    per_year: int,
    seed: int,
    split_name: str,
    exclude_ids: set[str] | None = None,
) -> list[dict]:
    """
    Stratified proportional design for dev (10/year = 70) and test (20/year = 140) samples:
    - Strictly disjoint from `exclude_ids` (defaults to all existing samples in data/samples/).
    - Within each year, `per_year` papers are allocated proportionally across Main and Findings
      based on total eligible year-track stratum sizes, with both tracks represented (>= 1 each).
    - Records `inclusion_probability = n_stratum / N_stratum_eligible`.
    """
    excluded = _load_existing_sample_ids() if exclude_ids is None else set(exclude_ids)
    rng = random.Random(seed)
    sample = []

    for year in years:
        all_main = [p for p in all_papers if p["year"] == year and p["track"] == "Main"]
        all_findings = [p for p in all_papers if p["year"] == year and p["track"] == "Findings"]
        avail_main = [p for p in all_main if p["anthology_id"] not in excluded]
        avail_findings = [p for p in all_findings if p["anthology_id"] not in excluded]

        n_total_year = len(all_main) + len(all_findings)
        if n_total_year == 0:
            continue

        if all_findings and per_year >= 2:
            n_main = round(per_year * len(all_main) / n_total_year)
            n_main = max(1, min(per_year - 1, n_main))
            n_findings = per_year - n_main
        else:
            n_main = per_year
            n_findings = 0

        chosen_main = rng.sample(avail_main, min(n_main, len(avail_main)))
        chosen_findings = rng.sample(avail_findings, min(n_findings, len(avail_findings)))

        for p in chosen_main + chosen_findings:
            p_copy = dict(p)
            p_copy["sample_split"] = split_name
            p_copy["random_seed"] = seed
            if p["track"] == "Main":
                p_copy["inclusion_probability"] = round(len(chosen_main) / len(all_main), 6) if all_main else 0.0
            else:
                p_copy["inclusion_probability"] = (
                    round(len(chosen_findings) / len(all_findings), 6) if all_findings else 0.0
                )
            sample.append(p_copy)
            excluded.add(p["anthology_id"])

    return sample


def draw_dev_sample(all_papers: list[dict], years: list[int], seed: int, split_name: str) -> list[dict]:
    """Development sample: 10 papers/year (70 total), proportional across tracks and disjoint from pilot."""
    return draw_proportional_sample(all_papers, years, per_year=10, seed=seed, split_name=split_name)


def draw_test_sample(all_papers: list[dict], years: list[int], seed: int, split_name: str) -> list[dict]:
    """Held-out test sample: 20 papers/year (140 total), proportional across tracks and disjoint from pilot+dev."""
    return draw_proportional_sample(all_papers, years, per_year=20, seed=seed, split_name=split_name)
