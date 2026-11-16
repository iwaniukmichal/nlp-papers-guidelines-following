"""Blind double-annotation sheets for human annotators."""

from pathlib import Path

from emnlp_audit.evaluators.compliance import policy_applies
from emnlp_audit.files import write_csv

TEAM_PAIRS = [
    ("M. Iwaniuk", "B. Borycki"),
    ("M. Chodań", "M. Guzik"),
]

STATUS_COL = "evidence_status_human (not_applicable / not_reported / explicitly_reported_inadequate / adequately_reported)"


def build_annotation_rows(papers: list[dict], rubric: dict, split: str, deadline: str) -> list[dict]:
    """
    Every paper is labelled independently by both members of one pair (pairs alternate by paper).
    The sheet contains no evaluator predictions (blind to automatic labels).
    """
    rows = []
    for idx, paper in enumerate(papers):
        pair = TEAM_PAIRS[idx % len(TEAM_PAIRS)]
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
    rows = build_annotation_rows(papers, rubric, split, deadline)
    write_csv(path, rows)
    return len(rows)
