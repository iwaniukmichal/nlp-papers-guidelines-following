"""
Fetch EMNLP 2020-2026 Main and Findings metadata from the official ACL Anthology XML repository,
compute exact eligible paper counts per year and track (Criterion 1.2),
and draw a reproducible stratified pilot sample of 14 papers (2 per year: 1 Main + 1 Findings)
for the Phase 2 Proof of Concept (PoC).
"""

import csv
import json
import os
import random
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

BASE_XML_URL = "https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml"
YEARS = [2020, 2021, 2022, 2023, 2024, 2025, 2026]
SEED = 42

OUT_DIR = Path(__file__).resolve().parent / "data"
XML_DIR = OUT_DIR / "xml"
PDF_DIR = OUT_DIR / "pdfs"


def fetch_xml(filename: str) -> Path | None:
    XML_DIR.mkdir(parents=True, exist_ok=True)
    local_path = XML_DIR / filename
    if local_path.exists() and local_path.stat().st_size > 100:
        return local_path
    url = f"{BASE_XML_URL}/{filename}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (EMNLP-Audit-PoC)"})
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
        # 2020.emnlp.xml has volume id="main" (2020.emnlp-main), plus sometimes demo/industry/tutorials
        # 2020.findings.xml has volume id="emnlp" (2020.findings-emnlp)
        if target_venue == "main" and vol_id != "main":
            continue
        if target_venue == "findings" and vol_id != "emnlp":
            continue

        for paper in volume.findall("paper"):
            paper_id = paper.attrib.get("id", "")
            # Exclude frontmatter (id="0")
            if paper_id == "0":
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

            pdf_url = f"https://aclanthology.org/{anthology_id}.pdf"
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
                "pdf_url": pdf_url,
            })

    return eligible


def download_pdf(paper: dict) -> str:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    safe_id = paper["anthology_id"].replace("/", "_")
    pdf_path = PDF_DIR / f"{safe_id}.pdf"
    if pdf_path.exists() and pdf_path.stat().st_size > 1000:
        return str(pdf_path)
    try:
        req = urllib.request.Request(paper["pdf_url"], headers={"User-Agent": "Mozilla/5.0 (EMNLP-Audit-PoC)"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            pdf_path.write_bytes(resp.read())
        return str(pdf_path)
    except Exception as e:
        print(f"[WARN] Could not download {paper['pdf_url']}: {e}")
        return ""


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    all_papers = []
    counts_by_year = {}

    for year in YEARS:
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
        print(f"EMNLP {year}: Main={len(main_papers)}, Findings={len(findings_papers)}, Total={counts_by_year[year]['Total']}")

    # Save full corpus metadata and summary counts
    counts_path = OUT_DIR / "corpus_counts_by_year_track.json"
    counts_path.write_text(json.dumps(counts_by_year, indent=2), encoding="utf-8")

    manifest_path = OUT_DIR / "emnlp_2020_2026_eligible_manifest.csv"
    with manifest_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["anthology_id", "year", "track", "paper_num", "title", "authors", "pages", "pdf_url"],
        )
        writer.writeheader()
        writer.writerows(all_papers)

    # Sample 2 papers per year (1 Main + 1 Findings) with fixed seed
    rng = random.Random(SEED)
    pilot_sample = []
    for year in YEARS:
        year_main = [p for p in all_papers if p["year"] == year and p["track"] == "Main"]
        year_findings = [p for p in all_papers if p["year"] == year and p["track"] == "Findings"]

        selected = []
        if year_main:
            selected.append(rng.choice(year_main))
        if year_findings:
            selected.append(rng.choice(year_findings))
        elif len(year_main) >= 2:
            remaining = [p for p in year_main if p not in selected]
            selected.append(rng.choice(remaining))

        for p in selected:
            p_copy = dict(p)
            p_copy["sample_split"] = "pilot_14"
            p_copy["random_seed"] = SEED
            track_total = len(year_main) if p["track"] == "Main" else len(year_findings)
            p_copy["inclusion_probability"] = round(1.0 / track_total, 6) if track_total > 0 else 0.0
            p_copy["local_pdf_path"] = download_pdf(p_copy)
            pilot_sample.append(p_copy)

    pilot_json_path = OUT_DIR / "pilot_14_sample.json"
    pilot_json_path.write_text(json.dumps(pilot_sample, indent=2, ensure_ascii=False), encoding="utf-8")

    pilot_csv_path = OUT_DIR / "pilot_14_sample.csv"
    if pilot_sample:
        with pilot_csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(pilot_sample[0].keys()))
            writer.writeheader()
            writer.writerows(pilot_sample)

    print(f"\nSaved {len(all_papers)} eligible papers to {manifest_path}")
    print(f"Saved {len(pilot_sample)} pilot papers to {pilot_json_path}")


if __name__ == "__main__":
    main()

