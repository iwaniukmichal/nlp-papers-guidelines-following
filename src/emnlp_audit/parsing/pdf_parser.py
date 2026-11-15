"""PDF text extraction with page markers and a JSON cache in data/interim/parsed/.

Parser: PyMuPDF, with pypdf as a fallback when PyMuPDF is not installed.
NOTE: the proposal names Docling as the parser; it is not integrated yet.
"""

import json
from pathlib import Path

from emnlp_audit import paths
from emnlp_audit.parsing.checklist_strip import join_pages_without_checklist
from emnlp_audit.parsing.pii import redact_emails


def _extract_pages(path: Path) -> tuple[list[dict], str]:
    try:
        import pymupdf

        doc = pymupdf.open(str(path))
        return [{"page": i + 1, "text": page.get_text("text")} for i, page in enumerate(doc)], "PyMuPDF"
    except ImportError:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        return [{"page": i + 1, "text": page.extract_text() or ""} for i, page in enumerate(reader.pages)], "pypdf"


def parse_pdf(pdf_path: str | Path) -> dict:
    """
    Extract full text from a PDF, preserving page markers, removing the appended
    checklist and redacting e-mail addresses. Results are cached per PDF stem.
    `pdf_path` may be absolute or relative to the repository root.
    """
    path = Path(pdf_path)
    if not path.is_absolute():
        path = paths.from_repo_relative(str(pdf_path))
    if not pdf_path or not path.exists():
        return {"status": "missing_pdf", "pages": [], "full_text": "", "parser": "none"}

    paths.PARSED_DIR.mkdir(parents=True, exist_ok=True)
    cached_json = paths.PARSED_DIR / f"{path.stem}.json"
    if cached_json.exists():
        return json.loads(cached_json.read_text(encoding="utf-8"))

    try:
        pages_text, parser_used = _extract_pages(path)
    except Exception as e:
        return {"status": f"parse_error: {e}", "pages": [], "full_text": "", "parser": "error"}

    full_text, checklist_cut_page = join_pages_without_checklist(pages_text)

    result = {
        "status": "ok",
        "parser": parser_used,
        "num_pages": len(pages_text),
        "checklist_excluded_from_page": checklist_cut_page,
        "full_text": redact_emails(full_text),
    }
    cached_json.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


def load_parsed(anthology_id: str) -> dict | None:
    """Return the cached parse for a paper, or None if it has not been parsed yet."""
    cached_json = paths.PARSED_DIR / f"{anthology_id.replace('/', '_')}.json"
    if not cached_json.exists():
        return None
    return json.loads(cached_json.read_text(encoding="utf-8"))
