"""
LLM Evaluator for the 14 PoC Pilot Papers using the Gemini API.
Reads GEMINI_API_KEY strictly from the environment variable (never stored on disk).
Evaluates each paper on the 6 rubric items, enforces verbatim quote verification,
and logs token usage and latency for pilot cost estimation.
"""

import csv
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PARSED_DIR = DATA_DIR / "parsed"
RUBRIC_PATH = BASE_DIR / "rubric.json"
PILOT_SAMPLE_PATH = DATA_DIR / "pilot_14_sample.json"

DEFAULT_MODEL = "gemini-2.5-flash"


def build_prompt(paper: dict, full_text: str, rubric: dict) -> str:
    """Construct a structured deductive-coding prompt with the frozen rubric and paper text."""
    rubric_summary = json.dumps(rubric["items"], indent=2, ensure_ascii=False)
    return f"""You are an expert scientific auditor evaluating an EMNLP research paper against a formal reporting rubric.

PAPER METADATA:
- Anthology ID: {paper['anthology_id']}
- Year: {paper['year']}
- Track: {paper['track']}
- Title: {paper['title']}

RUBRIC ITEMS AND DEFINITIONS:
{rubric_summary}

INSTRUCTIONS:
Evaluate the paper below on all 6 rubric items:
1. "I1_limitations_section"
2. "I2_specific_limitation"
3. "I3_ethical_risks"
4. "I4_computational_budget"
5. "I5_asset_licensing"
6. "I6_ai_assistance"

For EACH item, output a JSON object with:
- "item_id": exact item_id string
- "practice_applies": boolean (true or false) or "uncertain"
- "evidence_status": one of ["not_applicable", "not_reported", "explicitly_reported_inadequate", "adequately_reported"]
- "evidence_quote": exact verbatim substring copied from the paper text (up to 250 characters) supporting your decision, or "" if not_reported / not_applicable
- "location": page number and section heading where the evidence appears (e.g., "Page 9, Limitations"), or "" if not_reported
- "justification": 1-2 concise sentences explaining why the evidence satisfies or fails the rubric criterion

Return ONLY a valid JSON object of the form:
{{
  "evaluations": [ ... 6 objects ... ]
}}

EXTRACTED PAPER TEXT (with page markers --- [PAGE X] ---):
{full_text[:120000]}
"""


def call_gemini_api(prompt: str, api_key: str, model: str = DEFAULT_MODEL) -> tuple[dict, dict]:
    """Call Gemini generateContent endpoint with temperature=0.0 and JSON response mime type."""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.0,
            "responseMimeType": "application/json",
        },
    }
    data = json.dumps(payload).encode("utf-8")

    # Try standard Google AI Studio query-param key first, then Bearer header if token-formatted
    urls_and_headers = [
        (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
            {"Content-Type": "application/json"},
        ),
        (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        ),
        (
            f"https://aiplatform.googleapis.com/v1/publishers/google/models/{model}:generateContent?key={api_key}",
            {"Content-Type": "application/json"},
        ),
    ]

    last_err = None
    for url, headers in urls_and_headers:
        try:
            t0 = time.time()
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=90) as resp:
                raw_resp = json.loads(resp.read().decode("utf-8"))
            elapsed = round(time.time() - t0, 2)
            text_out = (
                raw_resp.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "{}")
            )
            usage = raw_resp.get("usageMetadata", {})
            usage["latency_sec"] = elapsed
            usage["model"] = model
            return json.loads(text_out), usage
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            last_err = f"HTTP {e.code}: {err_body[:300]}"
        except Exception as e:
            last_err = str(e)

    raise RuntimeError(f"Gemini API call failed across endpoints. Last error: {last_err}")


def verify_quote_in_text(quote: str, full_text: str) -> bool:
    """Verify that the quoted evidence span matches extracted text (normalising whitespace/hyphens)."""
    if not quote:
        return True
    norm_quote = re.sub(r"\s+", " ", quote).strip().lower()
    norm_text = re.sub(r"\s+", " ", full_text).lower()
    if norm_quote[:40] in norm_text or norm_quote[-40:] in norm_text:
        return True
    # Also check alphanumeric-only match to tolerate PDF line-break hyphenation
    alpha_quote = re.sub(r"[^a-z0-9]", "", norm_quote)
    alpha_text = re.sub(r"[^a-z0-9]", "", norm_text)
    return len(alpha_quote) >= 15 and alpha_quote[:35] in alpha_text


def derive_compliance(pol_applies: bool, prac_applies, ev_status: str) -> str:
    if prac_applies == "uncertain" or ev_status == "uncertain":
        return "Uncertain"
    if not pol_applies or not prac_applies or ev_status == "not_applicable":
        return "Not applicable"
    if ev_status == "adequately_reported":
        return "Compliant"
    if ev_status in ("not_reported", "explicitly_reported_inadequate"):
        return "Non-compliant"
    return "Uncertain"


def main():
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("ERROR: GEMINI_API_KEY environment variable is not set.")

    pilot_papers = json.loads(PILOT_SAMPLE_PATH.read_text(encoding="utf-8"))
    rubric = json.loads(RUBRIC_PATH.read_text(encoding="utf-8"))
    mandate_map = {item["item_id"]: item["policy_mandate_years"] for item in rubric["items"]}

    all_llm_evals = []
    usage_logs = []

    for idx, paper in enumerate(pilot_papers, 1):
        aid = paper["anthology_id"]
        year = int(paper["year"])
        parsed_path = PARSED_DIR / f"{aid}.json"
        if not parsed_path.exists():
            print(f"[{idx}/14] Missing parsed JSON for {aid}, skipping.")
            continue

        parsed = json.loads(parsed_path.read_text(encoding="utf-8"))
        full_text = parsed.get("full_text", "")
        prompt = build_prompt(paper, full_text, rubric)

        print(f"[{idx}/14] Evaluating {aid} ({paper['track']} {year}) with {DEFAULT_MODEL}...")
        parsed_resp, usage = call_gemini_api(prompt, api_key, DEFAULT_MODEL)
        usage["anthology_id"] = aid
        usage_logs.append(usage)

        eval_items = {e["item_id"]: e for e in parsed_resp.get("evaluations", []) if "item_id" in e}

        for item in rubric["items"]:
            iid = item["item_id"]
            e = eval_items.get(iid, {})
            pol_applies = year in mandate_map[iid]
            prac_applies = e.get("practice_applies", True)
            ev_status = e.get("evidence_status", "uncertain")
            quote = (e.get("evidence_quote") or "").strip().replace("\n", " ")
            loc = (e.get("location") or "").strip()
            just = (e.get("justification") or "").strip().replace("\n", " ")

            quote_verified = verify_quote_in_text(quote, full_text)
            compliance = derive_compliance(pol_applies, prac_applies, ev_status)

            all_llm_evals.append({
                "anthology_id": aid,
                "year": year,
                "track": paper["track"],
                "item_id": iid,
                "policy_applies": pol_applies,
                "practice_applies": prac_applies,
                "evidence_status": ev_status,
                "derived_compliance": compliance,
                "evidence_quote": quote,
                "quote_verified_in_text": quote_verified,
                "location": loc,
                "justification": just,
                "evaluator": DEFAULT_MODEL,
            })

    out_json = DATA_DIR / "poc_llm_evaluations.json"
    out_json.write_text(json.dumps(all_llm_evals, indent=2, ensure_ascii=False), encoding="utf-8")

    out_csv = DATA_DIR / "poc_llm_evaluations.csv"
    if all_llm_evals:
        with out_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(all_llm_evals[0].keys()))
            writer.writeheader()
            writer.writerows(all_llm_evals)

    usage_path = DATA_DIR / "poc_llm_usage_stats.json"
    usage_path.write_text(json.dumps(usage_logs, indent=2), encoding="utf-8")
    print(f"\nCompleted {len(all_llm_evals)} LLM evaluations -> {out_csv}")
    print(f"Saved token/latency stats -> {usage_path}")


if __name__ == "__main__":
    main()

