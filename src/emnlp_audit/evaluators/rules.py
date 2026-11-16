"""Deterministic regex/heading baseline evaluator for the rubric items."""

import re

from emnlp_audit.evaluators.compliance import derive_compliance, policy_applies

EVALUATOR_NAME = "rule_baseline_v1"

LIM_HEADING = re.compile(
    r"(?:^|\n)\s*(?:\d+\.?\s*)?(Limitations(?:\s+and\s+[^\n]{1,30})?)\s*\n([^\n]{20,400})", re.I | re.S
)
LIM_MENTION = re.compile(r"\blimitation(?:s)?\b[^.\n]{0,200}", re.I)
ETH_HEADING = re.compile(
    r"(?:^|\n)\s*(?:\d+\.?\s*)?(Ethics\s+Statement|Ethical\s+Considerations|Broader\s+Impact)\s*\n(.{20,400})",
    re.I | re.S,
)
ETH_BOILERPLATE = re.compile(r"no\s+ethical\s+(?:concerns|issues|risks)", re.I)
COMP_FULL = re.compile(
    r"(\b\d+(?:\.\d+)?\s*(?:GPU[\s-]*hours?|CPU[\s-]*hours?|hours?\s+on\s+\d*\s*(?:NVIDIA|A100|V100|RTX|TPU|GPU))[^.\n]{0,120})",
    re.I,
)
COMP_HW_ONLY = re.compile(r"\b(NVIDIA\s+(?:A100|V100|RTX|T4|P100|H100)|GeForce|TPU\s*v\d)\b[^.\n]{0,100}", re.I)
LICENSE = re.compile(
    r"\b(CC[\s-]BY(?:[\s-](?:SA|NC|ND))*[\s-]*\d\.\d|MIT\s+License|Apache[\s-]*2\.0|GPL[\s-]*v?[23]|BSD\s+License)\b[^.\n]{0,100}",
    re.I,
)
ARTIFACT_URL = re.compile(r"https?://(?:github\.com|huggingface\.co)/[^\s)\]]+", re.I)
AI_ASSIST = re.compile(
    r"((?:ChatGPT|Copilot|Grammarly|Claude|LLM|AI\s+assistant)[^.\n]{0,120}(?:writing|editing|grammar|polishing|coding|proofreading)[^.\n]{0,80})",
    re.I,
)


def find_page_for_offset(text: str, offset: int) -> str:
    """Find the most recent --- [PAGE X] --- marker before the given character offset."""
    pages = list(re.finditer(r"--- \[PAGE (\d+)\] ---", text[:offset]))
    if pages:
        return f"Page {pages[-1].group(1)}"
    return "Page 1"


def _record(paper: dict, item_id: str, pol_applies: bool, prac_applies, ev_status: str,
            compliance: str, quote: str, loc: str) -> dict:
    return {
        "anthology_id": paper["anthology_id"],
        "year": int(paper["year"]),
        "track": paper["track"],
        "item_id": item_id,
        "policy_applies": pol_applies,
        "practice_applies": prac_applies,
        "evidence_status": ev_status,
        "derived_compliance": compliance,
        "evidence_quote": quote.replace("\n", " "),
        "location": loc,
        "evaluator": EVALUATOR_NAME,
    }


def evaluate_paper(paper: dict, parsed: dict, rubric: dict) -> list[dict]:
    text = parsed.get("full_text", "") if parsed else ""
    year = int(paper["year"])

    if not text:
        return [
            _record(paper, item["item_id"], policy_applies(item, year), "uncertain", "uncertain", "Uncertain", "", "")
            for item in rubric["items"]
        ]

    lim_heading = LIM_HEADING.search(text)
    lim_mention = LIM_MENTION.search(text)
    eth_match = ETH_HEADING.search(text)
    eth_boilerplate = bool(eth_match and ETH_BOILERPLATE.search(eth_match.group(2)))
    comp_full = COMP_FULL.search(text)
    comp_hw_only = COMP_HW_ONLY.search(text)
    lic_match = LICENSE.search(text)
    url_only = ARTIFACT_URL.search(text)
    ai_match = AI_ASSIST.search(text)

    results = []
    for item in rubric["items"]:
        iid = item["item_id"]
        pol_applies = policy_applies(item, year)
        prac_applies = True
        ev_status = "not_reported"
        quote = ""
        loc = ""

        if iid == "I1_limitations_section":
            if lim_heading:
                ev_status = "adequately_reported"
                loc = find_page_for_offset(text, lim_heading.start())
                quote = lim_heading.group(1).strip()
            elif lim_mention:
                ev_status = "explicitly_reported_inadequate"
                loc = find_page_for_offset(text, lim_mention.start())
                quote = lim_mention.group(0).strip()

        elif iid == "I2_specific_limitation":
            if lim_heading:
                ev_status = "adequately_reported"
                loc = find_page_for_offset(text, lim_heading.start())
                quote = lim_heading.group(2).strip()[:250]
            elif lim_mention:
                ev_status = "explicitly_reported_inadequate"
                loc = find_page_for_offset(text, lim_mention.start())
                quote = lim_mention.group(0).strip()

        elif iid == "I3_ethical_risks":
            if eth_match:
                loc = find_page_for_offset(text, eth_match.start())
                quote = f"{eth_match.group(1)}: {eth_match.group(2).strip()[:220]}"
                ev_status = "explicitly_reported_inadequate" if eth_boilerplate else "adequately_reported"

        elif iid == "I4_computational_budget":
            if comp_full:
                ev_status = "adequately_reported"
                loc = find_page_for_offset(text, comp_full.start())
                quote = comp_full.group(1).strip()
            elif comp_hw_only:
                ev_status = "explicitly_reported_inadequate"
                loc = find_page_for_offset(text, comp_hw_only.start())
                quote = comp_hw_only.group(0).strip()

        elif iid == "I5_asset_licensing":
            if lic_match:
                ev_status = "adequately_reported"
                loc = find_page_for_offset(text, lic_match.start())
                quote = lic_match.group(0).strip()
            elif url_only:
                ev_status = "explicitly_reported_inadequate"
                loc = find_page_for_offset(text, url_only.start())
                quote = f"Artifact URL without named license: {url_only.group(0)}"

        elif iid == "I6_ai_assistance":
            pol_applies = False  # descriptive indicator only (proposal: never a compliance test)
            if ai_match:
                ev_status = "adequately_reported"
                loc = find_page_for_offset(text, ai_match.start())
                quote = ai_match.group(1).strip()

        compliance = derive_compliance(pol_applies, prac_applies, ev_status)
        results.append(_record(paper, iid, pol_applies, prac_applies, ev_status, compliance, quote, loc))

    return results
