"""LLM evaluator (Gemini API): prompt construction, API call, quote verification.

The API key is read only from the GEMINI_API_KEY environment variable and never stored on disk.
"""

import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

from emnlp_audit import paths
from emnlp_audit.evaluators.compliance import derive_compliance, policy_applies

DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_PROMPT = "llm_eval_v1.txt"
TEMPERATURE = 0.0
MAX_PAPER_CHARS = 120_000  # longer texts are truncated (long appendices may be cut)


def load_prompt_template(name: str = DEFAULT_PROMPT) -> str:
    return (paths.PROMPTS_DIR / name).read_text(encoding="utf-8")


def prompt_sha256(template: str) -> str:
    return hashlib.sha256(template.encode("utf-8")).hexdigest()


def build_prompt(template: str, paper: dict, full_text: str, rubric: dict) -> str:
    """Fill the frozen prompt template with paper metadata, rubric items and paper text."""
    return template.format(
        anthology_id=paper["anthology_id"],
        year=paper["year"],
        track=paper["track"],
        title=paper["title"],
        rubric_items=json.dumps(rubric["items"], indent=2, ensure_ascii=False),
        paper_text=full_text[:MAX_PAPER_CHARS],
    )


def call_gemini_api(prompt: str, api_key: str, model: str = DEFAULT_MODEL) -> tuple[dict, dict]:
    """Call Gemini generateContent with temperature=0 and JSON response mime type."""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": TEMPERATURE,
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


_LIGATURES = str.maketrans({
    "ﬁ": "fi",
    "ﬂ": "fl",
    "ﬀ": "ff",
    "ﬃ": "ffi",
    "ﬄ": "ffl",
    "’": "'",
    "‘": "'",
    "“": '"',
    "”": '"',
    "–": "-",
    "—": "-",
    "−": "-",
})


def _strip_page_markers(text: str) -> str:
    # Remove inserted page markers and adjacent running page numbers across page breaks
    return re.sub(r"(?:\b\d{1,5}\s+)?---\s*\[PAGE\s+\d+\]\s*---(?:\s+\d{1,5}\b)?", " ", text)


def _normalize_text(text: str) -> str:
    text = _strip_page_markers(text).translate(_LIGATURES)
    # Join words split across PDF line breaks with a hyphen
    text = re.sub(r"([A-Za-z])-\s+([A-Za-z])", r"\1\2", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def _normalize_alnum(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", _strip_page_markers(text).translate(_LIGATURES).lower())


def verify_quote_in_text(quote: str, full_text: str) -> bool:
    """Verify that the entire quoted evidence span matches extracted text.

    Normalises ligatures, whitespace, and PDF line-break hyphenation. If the quote
    contains explicit ellipses ('...' or '…') joining non-adjacent excerpts, every
    segment must appear in full and in order in `full_text`.
    """
    if not quote or not quote.strip():
        return True
    if not full_text:
        return False

    segments = [s.strip() for s in re.split(r"(?:\.\.\.|…)+", quote) if s.strip()]
    if not segments:
        return False

    norm_text = _normalize_text(full_text)
    alpha_text = _normalize_alnum(full_text)

    norm_pos = 0
    alpha_pos = 0
    for seg in segments:
        norm_seg = _normalize_text(seg)
        alpha_seg = _normalize_alnum(seg)
        if not alpha_seg:
            continue

        found_norm = norm_text.find(norm_seg, norm_pos) if norm_seg else -1
        if found_norm != -1:
            norm_pos = found_norm + len(norm_seg)
            found_alpha = alpha_text.find(alpha_seg, alpha_pos)
            if found_alpha != -1:
                alpha_pos = found_alpha + len(alpha_seg)
            continue

        found_alpha = alpha_text.find(alpha_seg, alpha_pos)
        if found_alpha != -1:
            alpha_pos = found_alpha + len(alpha_seg)
        else:
            return False

    return True


def to_records(paper: dict, response: dict, full_text: str, rubric: dict, model: str) -> list[dict]:
    """Turn the raw LLM JSON response into one evaluation record per rubric item."""
    year = int(paper["year"])
    eval_items = {e["item_id"]: e for e in response.get("evaluations", []) if "item_id" in e}
    truncated = len(full_text) > MAX_PAPER_CHARS
    evaluated_text = full_text[:MAX_PAPER_CHARS]

    records = []
    for item in rubric["items"]:
        iid = item["item_id"]
        e = eval_items.get(iid, {})
        pol_applies = policy_applies(item, year)
        prac_applies = e.get("practice_applies", True)
        ev_status = e.get("evidence_status", "uncertain")
        quote = (e.get("evidence_quote") or "").strip().replace("\n", " ")
        loc = (e.get("location") or "").strip()
        just = (e.get("justification") or "").strip().replace("\n", " ")

        if ev_status in ("adequately_reported", "explicitly_reported_inadequate"):
            quote_ok = bool(quote) and verify_quote_in_text(quote, evaluated_text)
            if not quote_ok:
                ev_status = "uncertain"
                just = f"{just} [Quote verification failed or missing quote -> uncertain]".strip()
        else:
            quote_ok = verify_quote_in_text(quote, evaluated_text)

        if truncated and ev_status == "not_reported":
            ev_status = "uncertain"
            just = (
                f"{just} [Paper text truncated at {MAX_PAPER_CHARS} chars; "
                f"absence in truncated tail cannot be ruled out -> uncertain]"
            ).strip()

        records.append({
            "anthology_id": paper["anthology_id"],
            "year": year,
            "track": paper["track"],
            "item_id": iid,
            "policy_applies": pol_applies,
            "practice_applies": prac_applies,
            "evidence_status": ev_status,
            "derived_compliance": derive_compliance(pol_applies, prac_applies, ev_status),
            "evidence_quote": quote,
            "quote_verified_in_text": quote_ok,
            "text_truncated": truncated,
            "location": loc,
            "justification": just,
            "evaluator": model,
        })
    return records
