"""Step 6: generate the blind double-annotation sheet for a sample.

Output: data/annotations/<split>/annotation_sheet.csv
"""

import argparse

from emnlp_audit import paths
from emnlp_audit.annotation.sheets import export_annotation_sheet
from emnlp_audit.files import load_rubric, load_sample


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", default="pilot_14")
    parser.add_argument("--deadline", required=True, help="e.g. 2026-11-18")
    parser.add_argument("--rubric-version", default=paths.DEFAULT_RUBRIC_VERSION)
    parser.add_argument("--force", action="store_true", help="overwrite an existing sheet (destroys filled labels!)")
    args = parser.parse_args()

    out_path = paths.ANNOTATIONS_DIR / args.split / "annotation_sheet.csv"
    if out_path.exists() and not args.force:
        raise SystemExit(f"{out_path} already exists and may contain human labels. Use --force to overwrite.")

    papers = load_sample(args.split)
    n_rows = export_annotation_sheet(out_path, papers, load_rubric(args.rubric_version), args.split, args.deadline)
    print(f"Saved blind double-annotation sheet ({n_rows} rows, {len(papers)} papers) to {out_path}")


if __name__ == "__main__":
    main()
