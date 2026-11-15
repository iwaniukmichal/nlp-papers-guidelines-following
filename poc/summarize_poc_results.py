"""
Summarize PoC Pilot Results (14 papers x 6 rubric items = 84 evaluations):
1. Class balance / label distribution for Evidence Status (4 classes) and Derived Compliance (4 classes)
2. Pre-mandate (2020-2021) vs. Post-mandate (2022-2026) adoption & compliance rates
3. Rule Baseline vs. Gemini-2.5-Flash comparison (agreement & qualitative differences)
4. Token usage, latency, and full-corpus cost projection (for N = 16,618 eligible EMNLP papers)
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def main():
    llm_evals = json.loads((DATA_DIR / "poc_llm_evaluations.json").read_text(encoding="utf-8"))
    rule_evals = json.loads((DATA_DIR / "poc_baseline_evaluations.json").read_text(encoding="utf-8"))
    usage_stats = json.loads((DATA_DIR / "poc_llm_usage_stats.json").read_text(encoding="utf-8"))
    corpus_counts = json.loads((DATA_DIR / "corpus_counts_by_year_track.json").read_text(encoding="utf-8"))

    total_corpus_papers = sum(v["Total"] for v in corpus_counts.values())

    # 1. Per-item distribution (LLM Evaluator)
    by_item_status = defaultdict(Counter)
    by_item_compliance = defaultdict(Counter)
    by_era_item = defaultdict(lambda: defaultdict(Counter))

    quote_verified_count = sum(1 for e in llm_evals if e.get("quote_verified_in_text"))

    for e in llm_evals:
        iid = e["item_id"]
        era = "2020-2021 (Pre-mandate)" if int(e["year"]) < 2022 else "2022-2026 (Post-mandate)"
        by_item_status[iid][e["evidence_status"]] += 1
        by_item_compliance[iid][e["derived_compliance"]] += 1
        by_era_item[iid][era][e["evidence_status"]] += 1

    # 2. Rule vs LLM agreement
    rule_map = {(r["anthology_id"], r["item_id"]): r for r in rule_evals}
    agreements_status = 0
    agreements_compliance = 0
    disagreements = []

    for l in llm_evals:
        key = (l["anthology_id"], l["item_id"])
        r = rule_map.get(key)
        if not r:
            continue
        if r["evidence_status"] == l["evidence_status"]:
            agreements_status += 1
        else:
            disagreements.append({
                "anthology_id": l["anthology_id"],
                "year": l["year"],
                "item_id": l["item_id"],
                "rule_status": r["evidence_status"],
                "llm_status": l["evidence_status"],
                "llm_quote": l["evidence_quote"][:140],
                "llm_justification": l["justification"],
            })
        if r["derived_compliance"] == l["derived_compliance"]:
            agreements_compliance += 1

    # 3. Token & latency statistics
    n_papers = len(usage_stats)
    total_prompt_tok = sum(u.get("promptTokenCount", 0) for u in usage_stats)
    total_cand_tok = sum(u.get("candidatesTokenCount", 0) for u in usage_stats)
    total_thought_tok = sum(u.get("thoughtsTokenCount", 0) for u in usage_stats)
    total_all_tok = sum(u.get("totalTokenCount", 0) for u in usage_stats)
    total_latency = sum(u.get("latency_sec", 0.0) for u in usage_stats)

    mean_prompt = total_prompt_tok / n_papers
    mean_output = (total_cand_tok + total_thought_tok) / n_papers
    mean_latency = total_latency / n_papers

    # Gemini 2.5 Flash standard/batch pricing estimate ($0.15 / 1M input, $0.60-$3.50 / 1M output; half in Batch API)
    est_cost_pilot_usd = (total_prompt_tok / 1e6) * 0.15 + ((total_cand_tok + total_thought_tok) / 1e6) * 0.60
    est_cost_full_corpus_standard_usd = est_cost_pilot_usd * (total_corpus_papers / n_papers)
    est_cost_full_corpus_batch_usd = est_cost_full_corpus_standard_usd * 0.5

    summary = {
        "pilot_papers_count": n_papers,
        "total_evaluations": len(llm_evals),
        "verbatim_quote_verification_rate": round(quote_verified_count / len(llm_evals), 4),
        "rule_vs_llm_status_agreement": round(agreements_status / len(llm_evals), 4),
        "rule_vs_llm_compliance_agreement": round(agreements_compliance / len(llm_evals), 4),
        "per_item_evidence_status_counts": {k: dict(v) for k, v in by_item_status.items()},
        "per_item_derived_compliance_counts": {k: dict(v) for k, v in by_item_compliance.items()},
        "pre_vs_post_2022_status_counts": {
            k: {era: dict(cnt) for era, cnt in eras.items()} for k, eras in by_era_item.items()
        },
        "workload_and_cost_estimates": {
            "total_pilot_prompt_tokens": total_prompt_tok,
            "total_pilot_output_and_thought_tokens": total_cand_tok + total_thought_tok,
            "total_pilot_tokens": total_all_tok,
            "mean_prompt_tokens_per_paper": round(mean_prompt, 1),
            "mean_output_tokens_per_paper": round(mean_output, 1),
            "total_pilot_latency_sec": round(total_latency, 2),
            "mean_latency_sec_per_paper": round(mean_latency, 2),
            "estimated_pilot_cost_usd": round(est_cost_pilot_usd, 4),
            "total_eligible_corpus_papers_2020_2026": total_corpus_papers,
            "projected_full_corpus_cost_standard_usd": round(est_cost_full_corpus_standard_usd, 2),
            "projected_full_corpus_cost_batch_api_usd": round(est_cost_full_corpus_batch_usd, 2),
        },
        "notable_rule_vs_llm_disagreements": disagreements[:15],
    }

    out_path = DATA_DIR / "poc_summary_report.json"
    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

