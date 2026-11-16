"""Collection of dated policy source documents (stage 1 of docs/methodology/rubric-development.md).

Web pages are taken from the Internet Archive (Wayback Machine): the latest successful capture
on or before `capture_before` is downloaded in raw mode (`/web/<ts>id_/<url>`), which returns the
original bytes, so the SHA-256 is reproducible. ACL Anthology PDFs are downloaded directly.
Each document is stored in data/policy_sources/<doc_id>/ (committed) together with a plain-text
extraction used for reading and for verifying quotes.
"""

import gzip
import hashlib
import html
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

import truststore

from emnlp_audit import paths

truststore.inject_into_ssl()  # use the OS certificate store (works behind TLS-inspecting antivirus/proxies)

USER_AGENT = "emnlp-audit-research/0.1 (academic policy archive)"
CDX_API = "https://web.archive.org/cdx/search/cdx"

DOCUMENT_FIELDS = [
    "doc_id", "year", "issuer", "doc_type", "title", "url", "capture_before",
    "wayback_timestamp", "retrieved_at", "sha256", "local_path", "notes",
]


REQUEST_DELAY_SEC = 4  # be polite: the Wayback Machine refuses connections when hit too fast
_last_request = 0.0


def _get(url: str, timeout: int = 90, retries: int = 4) -> tuple[bytes, dict]:
    global _last_request
    last = None
    for attempt in range(retries):
        wait = REQUEST_DELAY_SEC - (time.time() - _last_request)
        if wait > 0:
            time.sleep(wait)
        _last_request = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read()
                headers = {k.lower(): v for k, v in resp.headers.items()}
            if headers.get("content-encoding") == "gzip" or body[:2] == b"\x1f\x8b":
                body = gzip.decompress(body)
            return body, headers
        except Exception as e:  # network hiccups and Wayback rate limiting
            last = e
            time.sleep(30 * (attempt + 1))
    raise RuntimeError(f"GET failed for {url}: {last}")


def _url_variants(url: str) -> list[str]:
    bare = re.sub(r"^https?://", "", url).rstrip("/")
    return [bare + "/", bare]


def find_capture(url: str, before: str) -> tuple[str, str] | None:
    """Latest HTTP-200 capture of `url` on or before `before` (YYYY-MM-DD). Returns (timestamp, original)."""
    to = before.replace("-", "") + "235959"
    best = None
    for variant in _url_variants(url):
        query = urllib.parse.urlencode({
            "url": variant, "to": to, "output": "json", "fl": "timestamp,original,statuscode",
        })
        body, _ = _get(f"{CDX_API}?{query}")
        rows = json.loads(body or b"[]")[1:]
        rows = [r for r in rows if r[2] == "200"]
        if rows and (best is None or rows[-1][0] > best[0]):
            best = (rows[-1][0], rows[-1][1])
    return best


def is_anthology(url: str) -> bool:
    return "aclanthology.org" in url


def download(row: dict) -> bytes:
    if is_anthology(row["url"]):
        body, _ = _get(row["url"])
        return body
    body, _ = _get(f"https://web.archive.org/web/{row['wayback_timestamp']}id_/{row['url']}")
    return body


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def html_to_text(raw: bytes) -> str:
    text = raw.decode("utf-8", errors="replace")
    text = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", text)
    text = re.sub(r"(?i)<br\s*/?>|</(p|div|li|h[1-6]|tr|section|ul|ol|table|blockquote)>", "\n", text)
    text = re.sub(r"(?i)<li[^>]*>", "\n- ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line not in {"-", "|", "•"}]  # empty navigation bullets
    text = "\n".join(lines)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip() + "\n"


def write_text(original: Path) -> None:
    """(Re)create the .txt extraction next to a stored original."""
    raw = original.read_bytes()
    text = pdf_to_text(raw) if original.suffix == ".pdf" else html_to_text(raw)
    original.with_suffix(".txt").write_text(text, encoding="utf-8", newline="\n")


def pdf_to_text(raw: bytes) -> str:
    import pymupdf

    doc = pymupdf.open(stream=raw, filetype="pdf")
    return "\n".join(f"--- [PAGE {i + 1}] ---\n{page.get_text('text')}" for i, page in enumerate(doc))


def store(row: dict, raw: bytes) -> Path:
    """Write the original file and its text extraction; return the path of the original."""
    is_pdf = raw[:5] == b"%PDF-"
    stem = row["wayback_timestamp"] or "anthology"
    out_dir = paths.POLICY_SOURCES_DIR / row["doc_id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    original = out_dir / f"{stem}.{'pdf' if is_pdf else 'html'}"
    original.write_bytes(raw)
    write_text(original)
    return original


def text_path(row: dict) -> Path:
    return paths.from_repo_relative(row["local_path"]).with_suffix(".txt")
