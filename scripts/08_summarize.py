"""Step 8: summarize a pilot (label distributions, rule-vs-LLM agreement, cost projection).

Output: results/<split>/summary_report.json
"""

import argparse
import json

from emnlp_audit import paths
from emnlp_audit.analysis.summary import summarize
from emnlp_audit.evaluators.runs import resolve_run_dir
from emnlp_audit.files import read_json, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", default="pilot_14")
    parser.add_argument("--rules-run", required=True, help="run id of the rule baseline")
    parser.add_argument("--llm-run", required=True, help="run id of the LLM evaluator")
    args = parser.parse_args()

    rules_dir, llm_dir = resolve_run_dir(args.rules_run), resolve_run_dir(args.llm_run)
    summary = summarize(
        llm_evals=read_json(llm_dir / "evaluations.json"),
        rule_evals=read_json(rules_dir / "evaluations.json"),
        usage_stats=read_json(llm_dir / "usage.json"),
        corpus_counts=read_json(paths.COUNTS_PATH),
    )

    out_path = paths.RESULTS_DIR / args.split / "summary_report.json"
    write_json(out_path, summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
