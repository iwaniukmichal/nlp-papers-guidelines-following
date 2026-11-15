"""Pilot summary: label distributions, pre/post-2022 comparison, rule-vs-LLM agreement,
token usage and full-corpus cost projection."""

from collections import Counter, defaultdict

# Gemini 2.5 Flash pricing estimate ($0.15 / 1M input, $0.60 / 1M output; half in Batch API)
PRICE_INPUT_PER_M = 0.15
PRICE_OUTPUT_PER_M = 0.60
BATCH_DISCOUNT = 0.5


def summarize(llm_evals: list[dict], rule_evals: list[dict], usage_stats: list[dict], corpus_counts: dict) -> dict:
    total_corpus_papers = sum(v["Total"] for v in corpus_counts.values())

    # 1. Per-item distribution (LLM evaluator)
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
        r = rule_map.get((l["anthology_id"], l["item_id"]))
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

    est_cost_pilot_usd = (total_prompt_tok / 1e6) * PRICE_INPUT_PER_M + (
        (total_cand_tok + total_thought_tok) / 1e6
    ) * PRICE_OUTPUT_PER_M
    est_cost_full_standard = est_cost_pilot_usd * (total_corpus_papers / n_papers)

    return {
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
            "mean_prompt_tokens_per_paper": round(total_prompt_tok / n_papers, 1),
            "mean_output_tokens_per_paper": round((total_cand_tok + total_thought_tok) / n_papers, 1),
            "total_pilot_latency_sec": round(total_latency, 2),
            "mean_latency_sec_per_paper": round(total_latency / n_papers, 2),
            "estimated_pilot_cost_usd": round(est_cost_pilot_usd, 4),
            "total_eligible_corpus_papers_2020_2026": total_corpus_papers,
            "projected_full_corpus_cost_standard_usd": round(est_cost_full_standard, 2),
            "projected_full_corpus_cost_batch_api_usd": round(est_cost_full_standard * BATCH_DISCOUNT, 2),
        },
        "notable_rule_vs_llm_disagreements": disagreements[:15],
    }
