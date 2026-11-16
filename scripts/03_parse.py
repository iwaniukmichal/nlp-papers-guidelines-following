"""Step 3: parse the PDFs of a sample into data/interim/parsed/ (cached, gitignored)."""

import argparse
from collections import Counter

from emnlp_audit.files import load_sample
from emnlp_audit.parsing.pdf_parser import parse_pdf


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", default="pilot_14")
    args = parser.parse_args()

    statuses = Counter()
    for paper in load_sample(args.split):
        parsed = parse_pdf(paper.get("local_pdf_path", ""))
        statuses[parsed["status"]] += 1
        if parsed["status"] != "ok":
            print(f"[WARN] {paper['anthology_id']}: {parsed['status']}")
    print(f"Parse status counts: {dict(statuses)}")


if __name__ == "__main__":
    main()
