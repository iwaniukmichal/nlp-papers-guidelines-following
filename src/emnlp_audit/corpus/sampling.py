"""Reproducible sampling of papers from the eligible manifest."""

import random


def draw_pilot_sample(all_papers: list[dict], years: list[int], seed: int, split_name: str) -> list[dict]:
    """
    Pilot design: 1 Main + 1 Findings paper per year, drawn uniformly within each year-track stratum.
    Records the split name, seed and inclusion probability on every sampled paper.

    TODO (dev/test splits): the proposal requires disjoint samples allocated proportionally
    across tracks (10/year dev, 20/year test); implement as a separate design function.
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
