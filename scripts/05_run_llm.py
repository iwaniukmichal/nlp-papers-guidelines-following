"""Step 5: run the LLM evaluator on a sample; results go to a new runs/<run_id>/.

Requires the GEMINI_API_KEY environment variable.
"""

import argparse
import datetime as dt
import os

from emnlp_audit import paths
from emnlp_audit.evaluators import llm
from emnlp_audit.evaluators.runs import create_run_dir, make_run_id
from emnlp_audit.files import load_rubric, load_sample, write_json, write_records
from emnlp_audit.parsing.pdf_parser import parse_pdf


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", default="pilot_14")
    parser.add_argument("--model", default=llm.DEFAULT_MODEL)
    parser.add_argument("--prompt", default=llm.DEFAULT_PROMPT, help="file name in config/prompts/")
    parser.add_argument("--rubric-version", default=paths.DEFAULT_RUBRIC_VERSION)
    parser.add_argument("--run-id", help="override the default <date>_<split>_<model>_rubric-v<version>")
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("ERROR: GEMINI_API_KEY environment variable is not set.")

    rubric = load_rubric(args.rubric_version)
    papers = load_sample(args.split)
    template = llm.load_prompt_template(args.prompt)
    run_id = args.run_id or make_run_id(args.split, args.model, args.rubric_version)
    run_dir = create_run_dir(run_id)

    all_evals, usage_logs, parsers_used = [], [], set()
    for idx, paper in enumerate(papers, 1):
        aid = paper["anthology_id"]
        parsed = parse_pdf(paper.get("local_pdf_path", ""))
        full_text = parsed.get("full_text", "")
        if not full_text:
            print(f"[{idx}/{len(papers)}] No parsed text for {aid} ({parsed.get('status')}), skipping.")
            continue
        parsers_used.add(parsed.get("parser"))

        truncated = len(full_text) > llm.MAX_PAPER_CHARS
        if truncated:
            print(
                f"  [WARN] {aid}: extracted text ({len(full_text)} chars) exceeds "
                f"MAX_PAPER_CHARS ({llm.MAX_PAPER_CHARS}); truncating and marking 'not_reported' as 'uncertain'."
            )
        print(f"[{idx}/{len(papers)}] Evaluating {aid} ({paper['track']} {paper['year']}) with {args.model}...")
        response, usage = llm.call_gemini_api(llm.build_prompt(template, paper, full_text, rubric), api_key, args.model)
        usage["anthology_id"] = aid
        usage["full_text_chars"] = len(full_text)
        usage["text_truncated"] = truncated
        usage_logs.append(usage)
        all_evals.extend(llm.to_records(paper, response, full_text, rubric, args.model))

    write_records(run_dir / "evaluations", all_evals)
    write_json(run_dir / "usage.json", usage_logs)
    write_json(run_dir / "config.json", {
        "run_id": run_id,
        "created": dt.datetime.now().isoformat(timespec="seconds"),
        "evaluator": args.model,
        "temperature": llm.TEMPERATURE,
        "prompt_file": f"config/prompts/{args.prompt}",
        "prompt_sha256": llm.prompt_sha256(template),
        "max_paper_chars": llm.MAX_PAPER_CHARS,
        "split": args.split,
        "n_papers": len(papers),
        "rubric_version": rubric.get("rubric_version", args.rubric_version),
        "parser": sorted(parsers_used),
    })
    print(f"\nCompleted {len(all_evals)} LLM evaluations -> {run_dir}")


if __name__ == "__main__":
    main()
