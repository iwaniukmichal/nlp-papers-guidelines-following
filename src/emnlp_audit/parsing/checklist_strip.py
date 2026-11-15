"""Removal of the Responsible NLP Checklist appended to camera-ready PDFs (EMNLP 2025+).

The proposal excludes checklists from the evidence base to keep 2020-2026 comparable."""

import re

CHECKLIST_PATTERN = re.compile(
    r"Responsible\s+NLP\s+Research\s+Checklist|ARR\s+Responsible\s+NLP\s+Checklist",
    re.I,
)


def join_pages_without_checklist(pages_text: list[dict]) -> tuple[str, int | None]:
    """
    Join per-page text with '--- [PAGE X] ---' markers, stopping at the first page
    that contains the checklist heading (text before the heading on that page is kept).
    Returns (joined_text, page_number_where_checklist_starts_or_None).
    """
    combined = []
    checklist_cut_page = None
    for p in pages_text:
        txt = p["text"]
        if CHECKLIST_PATTERN.search(txt):
            checklist_cut_page = p["page"]
            txt = CHECKLIST_PATTERN.split(txt)[0]
            combined.append(f"\n--- [PAGE {p['page']}] ---\n{txt}")
            break
        combined.append(f"\n--- [PAGE {p['page']}] ---\n{txt}")
    return "\n".join(combined), checklist_cut_page
