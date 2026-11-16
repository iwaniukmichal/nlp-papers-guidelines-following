"""ACL Anthology access: XML metadata, eligible-paper extraction and PDF download."""

import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from emnlp_audit import paths

BASE_XML_URL = "https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml"
USER_AGENT = "Mozilla/5.0 (EMNLP-Audit-PoC)"
MANIFEST_FIELDS = ["anthology_id", "year", "track", "paper_num", "title", "authors", "pages", "pdf_url"]


def fetch_xml(filename: str) -> Path | None:
    paths.XML_DIR.mkdir(parents=True, exist_ok=True)
    local_path = paths.XML_DIR / filename
    if local_path.exists() and local_path.stat().st_size > 100:
        return local_path
    url = f"{BASE_XML_URL}/{filename}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        local_path.write_bytes(data)
        return local_path
    except Exception as e:
        print(f"[WARN] Could not fetch {url}: {e}")
        return None


def parse_volume_papers(xml_path: Path, year: int, target_venue: str) -> list[dict]:
    """
    Parse ACL Anthology XML and extract eligible EMNLP Main and Findings papers.
    Excludes front matter (paper id == '0'), workshops, demos, tutorials, industry tracks.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    eligible = []

    for volume in root.findall("volume"):
        vol_id = volume.attrib.get("id", "")
        # In ACL Anthology XML:
        # {year}.emnlp.xml has volume id="main" (emnlp-main), plus sometimes demo/industry/tutorials
        # {year}.findings.xml has volume id="emnlp" (findings-emnlp)
        if target_venue == "main" and vol_id != "main":
            continue
        if target_venue == "findings" and vol_id != "emnlp":
            continue

        for paper in volume.findall("paper"):
            paper_id = paper.attrib.get("id", "")
            if paper_id == "0":  # front matter
                continue

            title_el = paper.find("title")
            title = "".join(title_el.itertext()).strip() if title_el is not None else ""

            url_el = paper.find("url")
            anthology_id = "".join(url_el.itertext()).strip() if url_el is not None else ""
            if not anthology_id:
                if target_venue == "main":
                    anthology_id = f"{year}.emnlp-main.{paper_id}"
                else:
                    anthology_id = f"{year}.findings-emnlp.{paper_id}"

            pages_el = paper.find("pages")
            pages = "".join(pages_el.itertext()).strip() if pages_el is not None else ""

            authors = []
            for author in paper.findall("author"):
                first = "".join(author.find("first").itertext()).strip() if author.find("first") is not None else ""
                last = "".join(author.find("last").itertext()).strip() if author.find("last") is not None else ""
                full_name = f"{first} {last}".strip()
                if full_name:
                    authors.append(full_name)

            eligible.append({
                "anthology_id": anthology_id,
                "year": year,
                "track": "Main" if target_venue == "main" else "Findings",
                "paper_num": int(paper_id) if paper_id.isdigit() else paper_id,
                "title": title,
                "authors": "; ".join(authors),
                "pages": pages,
                "pdf_url": f"https://aclanthology.org/{anthology_id}.pdf",
            })

    return eligible


def build_manifest(years: list[int]) -> tuple[list[dict], dict]:
    """Return (all eligible papers, counts by year and track)."""
    all_papers = []
    counts_by_year = {}
    for year in years:
        main_xml = fetch_xml(f"{year}.emnlp.xml")
        findings_xml = fetch_xml(f"{year}.findings.xml")

        main_papers = parse_volume_papers(main_xml, year, "main") if main_xml else []
        findings_papers = parse_volume_papers(findings_xml, year, "findings") if findings_xml else []

        counts_by_year[year] = {
            "Main": len(main_papers),
            "Findings": len(findings_papers),
            "Total": len(main_papers) + len(findings_papers),
        }
        all_papers.extend(main_papers)
        all_papers.extend(findings_papers)
        print(f"EMNLP {year}: Main={len(main_papers)}, Findings={len(findings_papers)}, "
              f"Total={counts_by_year[year]['Total']}")
    return all_papers, counts_by_year


def manifest_row_from_csv(row: dict) -> dict:
    """Restore types lost when the manifest is read back from CSV."""
    paper = dict(row)
    paper["year"] = int(paper["year"])
    if str(paper["paper_num"]).isdigit():
        paper["paper_num"] = int(paper["paper_num"])
    return paper


def download_pdf(paper: dict) -> str:
    """Download a paper PDF into data/raw/pdfs/ and return its repo-relative path ('' on failure)."""
    paths.PDF_DIR.mkdir(parents=True, exist_ok=True)
    safe_id = paper["anthology_id"].replace("/", "_")
    pdf_path = paths.PDF_DIR / f"{safe_id}.pdf"
    if pdf_path.exists() and pdf_path.stat().st_size > 1000:
        return paths.to_repo_relative(pdf_path)
    try:
        req = urllib.request.Request(paper["pdf_url"], headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=60) as resp:
            pdf_path.write_bytes(resp.read())
        return paths.to_repo_relative(pdf_path)
    except Exception as e:
        print(f"[WARN] Could not download {paper['pdf_url']}: {e}")
        return ""
