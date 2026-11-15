"""Step 4: run the rule-based baseline evaluator on a sample; results go to a new runs/<run_id>/."""

import argparse
import datetime as dt

from emnlp_audit import paths
from emnlp_audit.evaluators import rules
from emnlp_audit.evaluators.runs import create_run_dir, make_run_id
from emnlp_audit.files import load_rubric, load_sample, write_json, write_records
from emnlp_audit.parsing.pdf_parser import parse_pdf


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", default="pilot_14")
    parser.add_argument("--rubric-version", default=paths.DEFAULT_RUBRIC_VERSION)
    parser.add_argument("--run-id", help="override the default <date>_<split>_<evaluator>_rubric-v<version>")
    args = parser.parse_args()

    rubric = load_rubric(args.rubric_version)
    papers = load_sample(args.split)
    run_id = args.run_id or make_run_id(args.split, rules.EVALUATOR_NAME.replace("_", "-"), args.rubric_version)
    run_dir = create_run_dir(run_id)

    all_evals, parsers_used = [], set()
    for paper in papers:
        parsed = parse_pdf(paper.get("local_pdf_path", ""))
        parsers_used.add(parsed.get("parser", "none"))
        all_evals.extend(rules.evaluate_paper(paper, parsed, rubric))

    write_records(run_dir / "evaluations", all_evals)
    write_json(run_dir / "config.json", {
        "run_id": run_id,
        "created": dt.datetime.now().isoformat(timespec="seconds"),
        "evaluator": rules.EVALUATOR_NAME,
        "split": args.split,
        "n_papers": len(papers),
        "rubric_version": rubric.get("rubric_version", args.rubric_version),
        "parser": sorted(parsers_used),
    })
    print(f"Saved {len(all_evals)} evaluations to {run_dir}")


if __name__ == "__main__":
    main()
