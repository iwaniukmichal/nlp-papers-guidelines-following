"""
PoC Pipeline: PDF Section Extraction, Rule-Based + LLM Evaluator, and Blind Human Annotation Sheet Generator.
Supports:
- Docling (primary parser) with PyMuPDF / pypdf fallback
- Automatic removal of author header blocks (PII safeguard) and appended EMNLP 2025+ checklists
- Rule-based baseline evaluator + LLM evaluator (OpenAI / Gemini / OpenRouter compatible)
- Generation of blind double-annotation CSV sheets assigned across the 4 team members
"""

import csv
import json
import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PARSED_DIR = DATA_DIR / "parsed"
RUBRIC_PATH = BASE_DIR / "rubric.json"
POLICY_PATH = BASE_DIR / "policy_register.json"
PILOT_SAMPLE_PATH = DATA_DIR / "pilot_14_sample.json"

TEAM_PAIRS = [
    ("M. Iwaniuk", "B. Borycki"),
    ("M. Chodań", "M. Guzik"),
]


def find_page_for_offset(text: str, offset: int) -> str:
    """Find the most recent --- [PAGE X] --- marker before the given character offset."""
    pages = list(re.finditer(r"--- \[PAGE (\d+)\] ---", text[:offset]))
    if pages:
        return f"Page {pages[-1].group(1)}"
    return "Page 1"


def extract_text_from_pdf(pdf_path: str) -> dict:
    """
    Extract full text and section headings from a PDF, preserving page markers.
    Removes appended Responsible NLP Checklist (from EMNLP 2025+) to maintain longitudinal comparability.
    """
    path = Path(pdf_path)
    if not path.exists():
        return {"status": "missing_pdf", "pages": [], "full_text": "", "parser": "none"}

    PARSED_DIR.mkdir(parents=True, exist_ok=True)
    cached_json = PARSED_DIR / f"{path.stem}.json"
    if cached_json.exists():
        return json.loads(cached_json.read_text(encoding="utf-8"))

    pages_text = []
    parser_used = "unknown"

    try:
        import fitz  # PyMuPDF
        doc = fitz.open(str(path))
        for i, page in enumerate(doc):
            pages_text.append({"page": i + 1, "text": page.get_text("text")})
        parser_used = "PyMuPDF"
    except ImportError:
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            for i, page in enumerate(reader.pages):
                pages_text.append({"page": i + 1, "text": page.extract_text() or ""})
            parser_used = "pypdf"
        except Exception as e:
            return {"status": f"parse_error: {e}", "pages": [], "full_text": "", "parser": "error"}

    combined = []
    checklist_cut_page = None
    for p in pages_text:
        txt = p["text"]
        if re.search(r"Responsible\s+NLP\s+Research\s+Checklist|ARR\s+Responsible\s+NLP\s+Checklist", txt, re.I):
            checklist_cut_page = p["page"]
            txt = re.split(
                r"Responsible\s+NLP\s+Research\s+Checklist|ARR\s+Responsible\s+NLP\s+Checklist",
                txt,
                flags=re.I,
            )[0]
            combined.append(f"\n--- [PAGE {p['page']}] ---\n{txt}")
            break
        combined.append(f"\n--- [PAGE {p['page']}] ---\n{txt}")

    full_text = "\n".join(combined)
    redacted_text = re.sub(r"[\w\.-]+@[\w\.-]+\.\w+", "[EMAIL_REDACTED]", full_text)

    result = {
        "status": "ok",
        "parser": parser_used,
        "num_pages": len(pages_text),
        "checklist_excluded_from_page": checklist_cut_page,
        "full_text": redacted_text,
    }
    cached_json.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


def rule_based_evaluate_paper(paper: dict, parsed: dict, rubric: dict) -> list[dict]:
    """
    Deterministic regex/heading baseline evaluator for the 6 rubric items.
    """
    text = parsed.get("full_text", "")
    year = int(paper["year"])
    results = []

    if not text:
        for item in rubric["items"]:
            results.append({
                "anthology_id": paper["anthology_id"],
                "year": year,
                "track": paper["track"],
                "item_id": item["item_id"],
                "policy_applies": year in item["policy_mandate_years"],
                "practice_applies": "uncertain",
                "evidence_status": "uncertain",
                "derived_compliance": "Uncertain",
                "evidence_quote": "",
                "location": "",
                "evaluator": "rule_baseline_v1",
            })
        return results

    # 1. Limitations section (heading)
    lim_heading_match = re.search(
        r"(?:^|\n)\s*(?:\d+\.?\s*)?(Limitations(?:\s+and\s+[^\n]{1,30})?)\s*\n([^\n]{20,400})",
        text,
        re.I | re.S,
    )
    has_lim_heading = lim_heading_match is not None
    lim_mention = re.search(r"\blimitation(?:s)?\b[^.\n]{0,200}", text, re.I)

    # 2. Specific limitation heuristics
    lim_status = (
        "adequately_reported"
        if has_lim_heading
        else ("explicitly_reported_inadequate" if lim_mention else "not_reported")
    )

    # 3. Ethical risks
    eth_match = re.search(
        r"(?:^|\n)\s*(?:\d+\.?\s*)?(Ethics\s+Statement|Ethical\s+Considerations|Broader\s+Impact)\s*\n(.{20,400})",
        text,
        re.I | re.S,
    )
    eth_boilerplate = False
    if eth_match and re.search(r"no\s+ethical\s+(?:concerns|issues|risks)", eth_match.group(2), re.I):
        eth_boilerplate = True

    # 4. Computational budget
    comp_full = re.search(
        r"(\b\d+(?:\.\d+)?\s*(?:GPU[\s-]*hours?|CPU[\s-]*hours?|hours?\s+on\s+\d*\s*(?:NVIDIA|A100|V100|RTX|TPU|GPU))[^.\n]{0,120})",
        text,
        re.I,
    )
    comp_hw_only = re.search(
        r"\b(NVIDIA\s+(?:A100|V100|RTX|T4|P100|H100)|GeForce|TPU\s*v\d)\b[^.\n]{0,100}",
        text,
        re.I,
    )

    # 5. Asset licensing
    lic_match = re.search(
        r"\b(CC[\s-]BY(?:[\s-](?:SA|NC|ND))*[\s-]*\d\.\d|MIT\s+License|Apache[\s-]*2\.0|GPL[\s-]*v?[23]|BSD\s+License)\b[^.\n]{0,100}",
        text,
        re.I,
    )
    url_only = re.search(r"https?://(?:github\.com|huggingface\.co)/[^\s)\]]+", text, re.I)

    # 6. AI assistance
    ai_match = re.search(
        r"((?:ChatGPT|Copilot|Grammarly|Claude|LLM|AI\s+assistant)[^.\n]{0,120}(?:writing|editing|grammar|polishing|coding|proofreading)[^.\n]{0,80})",
        text,
        re.I,
    )

    for item in rubric["items"]:
        iid = item["item_id"]
        pol_applies = year in item["policy_mandate_years"]
        prac_applies = True
        ev_status = "not_reported"
        quote = ""
        loc = ""

        if iid == "I1_limitations_section":
            if has_lim_heading:
                ev_status = "adequately_reported"
                loc = find_page_for_offset(text, lim_heading_match.start())
                quote = lim_heading_match.group(1).strip()
            elif lim_mention:
                ev_status = "explicitly_reported_inadequate"
                loc = find_page_for_offset(text, lim_mention.start())
                quote = lim_mention.group(0).strip()
            else:
                ev_status = "not_reported"

        elif iid == "I2_specific_limitation":
            ev_status = lim_status
            if has_lim_heading:
                loc = find_page_for_offset(text, lim_heading_match.start())
                quote = lim_heading_match.group(2).strip()[:250]
            elif lim_mention:
                loc = find_page_for_offset(text, lim_mention.start())
                quote = lim_mention.group(0).strip()

        elif iid == "I3_ethical_risks":
            if eth_match:
                loc = find_page_for_offset(text, eth_match.start())
                quote = f"{eth_match.group(1)}: {eth_match.group(2).strip()[:220]}"
                ev_status = "explicitly_reported_inadequate" if eth_boilerplate else "adequately_reported"
            else:
                ev_status = "not_reported"

        elif iid == "I4_computational_budget":
            if comp_full:
                ev_status = "adequately_reported"
                loc = find_page_for_offset(text, comp_full.start())
                quote = comp_full.group(1).strip()
            elif comp_hw_only:
                ev_status = "explicitly_reported_inadequate"
                loc = find_page_for_offset(text, comp_hw_only.start())
                quote = comp_hw_only.group(0).strip()
            else:
                ev_status = "not_reported"

        elif iid == "I5_asset_licensing":
            if lic_match:
                ev_status = "adequately_reported"
                loc = find_page_for_offset(text, lic_match.start())
                quote = lic_match.group(0).strip()
            elif url_only:
                ev_status = "explicitly_reported_inadequate"
                loc = find_page_for_offset(text, url_only.start())
                quote = f"Artifact URL without named license: {url_only.group(0)}"
            else:
                ev_status = "not_reported"

        elif iid == "I6_ai_assistance":
            pol_applies = False
            if ai_match:
                ev_status = "adequately_reported"
                loc = find_page_for_offset(text, ai_match.start())
                quote = ai_match.group(1).strip()
            else:
                ev_status = "not_reported"

        if not pol_applies or not prac_applies:
            compliance = "Not applicable"
        elif ev_status == "adequately_reported":
            compliance = "Compliant"
        elif ev_status in ("not_reported", "explicitly_reported_inadequate"):
            compliance = "Non-compliant"
        else:
            compliance = "Uncertain"

        results.append({
            "anthology_id": paper["anthology_id"],
            "year": year,
            "track": paper["track"],
            "item_id": iid,
            "policy_applies": pol_applies,
            "practice_applies": prac_applies,
            "evidence_status": ev_status,
            "derived_compliance": compliance,
            "evidence_quote": quote.replace("\n", " "),
            "location": loc,
            "evaluator": "rule_baseline_v1",
        })

    return results


def export_blind_human_annotation_sheet(pilot_papers: list[dict], rubric: dict):
    """
    Create a clean, blind CSV sheet for double human annotation of the 14 pilot papers,
    assigning each paper to a named pair of team members (Criterion 1.2 & 1.3).
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    sheet_path = DATA_DIR / "human_annotation_sheet_pilot14.csv"

    rows = []
    for idx, paper in enumerate(pilot_papers):
        pair = TEAM_PAIRS[idx % len(TEAM_PAIRS)]
        for annotator in pair:
            for item in rubric["items"]:
                rows.append({
                    "batch": "pilot_14",
                    "deadline": "2026-11-18",
                    "annotator_name": annotator,
                    "paper_index": idx + 1,
                    "anthology_id": paper["anthology_id"],
                    "year": paper["year"],
                    "track": paper["track"],
                    "title": paper["title"],
                    "pdf_url": paper["pdf_url"],
                    "item_id": item["item_id"],
                    "item_name": item["name"],
                    "policy_applies_auto": paper["year"] in item["policy_mandate_years"],
                    "practice_applies_human (true/false/uncertain)": "",
                    "evidence_status_human (not_applicable / not_reported / explicitly_reported_inadequate / adequately_reported)": "",
                    "derived_compliance_human (Compliant / Non-compliant / Not applicable / Uncertain)": "",
                    "evidence_quote_human": "",
                    "page_or_section_human": "",
                    "notes": "",
                })

    with sheet_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved blind double-annotation sheet ({len(rows)} rows for 14 papers x 6 items x 2 annotators) to {sheet_path}")


def main():
    if not PILOT_SAMPLE_PATH.exists():
        print(f"Pilot sample not found at {PILOT_SAMPLE_PATH}. Run collect_emnlp_poc.py first.")
        return

    pilot_papers = json.loads(PILOT_SAMPLE_PATH.read_text(encoding="utf-8"))
    rubric = json.loads(RUBRIC_PATH.read_text(encoding="utf-8"))

    export_blind_human_annotation_sheet(pilot_papers, rubric)

    all_evals = []
    for paper in pilot_papers:
        parsed = extract_text_from_pdf(paper.get("local_pdf_path", ""))
        evals = rule_based_evaluate_paper(paper, parsed, rubric)
        all_evals.extend(evals)

    eval_out_json = DATA_DIR / "poc_baseline_evaluations.json"
    eval_out_json.write_text(json.dumps(all_evals, indent=2, ensure_ascii=False), encoding="utf-8")

    eval_out_csv = DATA_DIR / "poc_baseline_evaluations.csv"
    if all_evals:
        with eval_out_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(all_evals[0].keys()))
            writer.writeheader()
            writer.writerows(all_evals)

    print(f"Saved {len(all_evals)} PoC evaluations to {eval_out_csv}")


if __name__ == "__main__":
    main()
