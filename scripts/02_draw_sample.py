"""Step 2: draw a reproducible sample from the manifest and download its PDFs.

Outputs: data/samples/<split>.{json,csv}, PDFs in data/raw/pdfs/ (gitignored)
"""

import argparse

from emnlp_audit import paths
from emnlp_audit.corpus.anthology import download_pdf, manifest_row_from_csv
from emnlp_audit.corpus.sampling import draw_pilot_sample
from emnlp_audit.files import read_csv, read_json, write_csv, write_json

DESIGNS = {"pilot": draw_pilot_sample}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", default="pilot_14", help="name of the sample, e.g. pilot_14, dev_70, test_140")
    parser.add_argument("--design", choices=sorted(DESIGNS), default="pilot")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-download", action="store_true", help="only draw the sample, skip PDF download")
    parser.add_argument("--download-only", action="store_true",
                        help="do not draw; download PDFs of an existing (frozen) sample, e.g. after cloning")
    args = parser.parse_args()

    out_json = paths.sample_path(args.split)
    if args.download_only:
        papers = read_json(out_json)
        ok = sum(bool(download_pdf(p)) for p in papers)
        print(f"Downloaded {ok}/{len(papers)} PDFs for '{args.split}' into {paths.PDF_DIR}")
        return
    if out_json.exists():
        raise SystemExit(f"{out_json} already exists; samples are frozen once drawn. Choose another --split.")

    all_papers = [manifest_row_from_csv(r) for r in read_csv(paths.MANIFEST_PATH)]
    years = sorted({p["year"] for p in all_papers})
    sample = DESIGNS[args.design](all_papers, years, args.seed, args.split)

    for p in sample:
        p["local_pdf_path"] = "" if args.no_download else download_pdf(p)

    write_json(out_json, sample)
    write_csv(out_json.with_suffix(".csv"), sample)
    print(f"Saved {len(sample)} papers to {out_json}")


if __name__ == "__main__":
    main()
