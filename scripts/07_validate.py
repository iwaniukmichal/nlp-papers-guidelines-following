"""Step 7: human-human agreement (Cohen's kappa) and evaluator-vs-human validation (macro-F1).

Output: results/<split>/iaa_and_validation_<run_id>.json
"""

import argparse

from emnlp_audit import paths
from emnlp_audit.analysis.iaa import load_double_annotations
from emnlp_audit.analysis.validation import iaa_and_validation_report
from emnlp_audit.evaluators.runs import resolve_run_dir
from emnlp_audit.files import read_json, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", default="pilot_14")
    parser.add_argument("--run", required=True, help="run id under runs/ (the evaluator to validate)")
    args = parser.parse_args()

    sheet = paths.ANNOTATIONS_DIR / args.split / "annotation_sheet.csv"
    if not sheet.exists():
        raise SystemExit(f"Annotation sheet not found: {sheet}")

    grouped = load_double_annotations(sheet)
    if not grouped:
        print(f"No completed human annotations found yet in {sheet}.")
        print("Fill in the 'evidence_status_human' column and re-run to get Cohen's kappa and macro-F1.")
        return

    run_dir = resolve_run_dir(args.run)
    report = iaa_and_validation_report(grouped, read_json(run_dir / "evaluations.json"))

    out_path = paths.RESULTS_DIR / args.split / f"iaa_and_validation_{run_dir.name}.json"
    write_json(out_path, report)
    print(f"Saved report to {out_path}")


if __name__ == "__main__":
    main()
