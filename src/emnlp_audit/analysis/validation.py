"""Validation of an automatic evaluator against human labels (per-item P/R/F1, macro-F1)."""

from collections import defaultdict

from emnlp_audit.analysis.iaa import cohens_kappa, raw_agreement


def macro_f1(y_true: list[str], y_pred: list[str]) -> dict:
    classes = sorted(set(y_true) | set(y_pred))
    per_class = {}
    f1s = []
    for c in classes:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == c and p == c)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != c and p == c)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == c and p != c)
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
        support = sum(1 for t in y_true if t == c)
        per_class[c] = {
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "support": support,
        }
        if support > 0:
            f1s.append(f1)
    return {
        "macro_f1": round(sum(f1s) / len(f1s), 4) if f1s else 0.0,
        "per_class": per_class,
    }


def iaa_and_validation_report(grouped_human: dict, evaluator_records: list[dict]) -> dict:
    """
    Per item: human-human raw agreement and Cohen's kappa, plus evaluator-vs-human macro-F1.

    TODO: the reference label currently falls back to annotator A when annotators disagree;
    replace with adjudicated labels once adjudication is done (proposal: adjudication supplies reference labels).
    """
    eval_map = {(e["anthology_id"], e["item_id"]): e["evidence_status"] for e in evaluator_records}

    by_item_a, by_item_b = defaultdict(list), defaultdict(list)
    by_item_gold, by_item_pred = defaultdict(list), defaultdict(list)

    for (aid, iid), ann_list in grouped_human.items():
        if len(ann_list) >= 2:
            a_val, b_val = ann_list[0][1], ann_list[1][1]
            by_item_a[iid].append(a_val)
            by_item_b[iid].append(b_val)
            gold = a_val  # placeholder until adjudication (see TODO above)
            if (aid, iid) in eval_map:
                by_item_gold[iid].append(gold)
                by_item_pred[iid].append(eval_map[(aid, iid)])

    report = {}
    for iid in sorted(by_item_a.keys()):
        a_list, b_list = by_item_a[iid], by_item_b[iid]
        f1_stats = macro_f1(by_item_gold[iid], by_item_pred[iid])
        report[iid] = {
            "n_double_annotated": len(a_list),
            "human_raw_agreement": raw_agreement(a_list, b_list),
            "human_cohens_kappa": cohens_kappa(a_list, b_list),
            "llm_vs_human_macro_f1": f1_stats["macro_f1"],
            "llm_per_class": f1_stats["per_class"],
        }
    return report
