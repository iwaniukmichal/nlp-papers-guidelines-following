"""Blind double-annotation sheets for human annotators."""

import re
from collections import defaultdict
from pathlib import Path

from emnlp_audit.evaluators.compliance import policy_applies
from emnlp_audit.files import write_csv

TEAM_PAIRS = [
    ("M. Iwaniuk", "B. Borycki"),
    ("M. Chodań", "M. Guzik"),
]

STATUS_COL = (
    "evidence_status_human "
    "(not_applicable / not_reported / explicitly_reported_inadequate / adequately_reported / uncertain)"
)


def annotator_slug(name: str) -> str:
    slug = name.lower().translate(str.maketrans({"ń": "n", "ł": "l", "ś": "s", "ć": "c", "ź": "z", "ż": "z", "ó": "o", "ą": "a", "ę": "e"}))
    return re.sub(r"[^a-z0-9]+", "_", slug).strip("_")


def build_annotation_rows(papers: list[dict], rubric: dict, split: str, deadline: str) -> list[dict]:
    """
    Every paper is labelled independently by both members of one pair.
    Pairs alternate within each track so that neither annotator pair is confounded with track
    (Main vs Findings). The sheet contains no evaluator predictions (blind to automatic labels).
    """
    rows = []
    track_counter: dict[str, int] = defaultdict(int)
    for idx, paper in enumerate(papers):
        track = paper.get("track", "Main")
        pair = TEAM_PAIRS[track_counter[track] % len(TEAM_PAIRS)]
        track_counter[track] += 1
        for annotator in pair:
            for item in rubric["items"]:
                rows.append({
                    "batch": split,
                    "deadline": deadline,
                    "annotator_name": annotator,
                    "paper_index": idx + 1,
                    "anthology_id": paper["anthology_id"],
                    "year": paper["year"],
                    "track": paper["track"],
                    "title": paper["title"],
                    "pdf_url": paper["pdf_url"],
                    "item_id": item["item_id"],
                    "item_name": item["name"],
                    "policy_applies_auto": policy_applies(item, paper["year"]),
                    "practice_applies_human (true/false/uncertain)": "",
                    STATUS_COL: "",
                    "derived_compliance_human (Compliant / Non-compliant / Not applicable / Uncertain)": "",
                    "evidence_quote_human": "",
                    "page_or_section_human": "",
                    "notes": "",
                })
    return rows


def export_annotation_sheet(path: Path, papers: list[dict], rubric: dict, split: str, deadline: str) -> int:
    """Write the combined annotation sheet and separate per-annotator sheets in `by_annotator/`."""
    rows = build_annotation_rows(papers, rubric, split, deadline)
    write_csv(path, rows)

    by_ann_dir = path.parent / "by_annotator"
    by_ann_dir.mkdir(parents=True, exist_ok=True)
    grouped: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        grouped[r["annotator_name"]].append(r)
    for annotator, ann_rows in grouped.items():
        ann_path = by_ann_dir / f"annotation_sheet_{annotator_slug(annotator)}.csv"
        write_csv(ann_path, ann_rows)

    return len(rows)
