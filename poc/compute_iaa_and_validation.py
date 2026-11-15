"""
Compute Human Inter-Annotator Agreement (Cohen's kappa, raw agreement)
and LLM-vs-Human Validation Metrics (Precision, Recall, F1, Macro-F1)
from the completed human_annotation_sheet_pilot14.csv and poc_llm_evaluations.json.
"""

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
HUMAN_SHEET = DATA_DIR / "human_annotation_sheet_pilot14.csv"
LLM_JSON = DATA_DIR / "poc_llm_evaluations.json"


def cohens_kappa(labels_a: list[str], labels_b: list[str]) -> float:
    assert len(labels_a) == len(labels_b) and len(labels_a) > 0
    n = len(labels_a)
    classes = sorted(set(labels_a) | set(labels_b))
    po = sum(1 for a, b in zip(labels_a, labels_b) if a == b) / n
    cnt_a = Counter(labels_a)
    cnt_b = Counter(labels_b)
    pe = sum((cnt_a[c] / n) * (cnt_b[c] / n) for c in classes)
    if abs(1.0 - pe) < 1e-9:
        return 1.0
    return round((po - pe) / (1.0 - pe), 4)


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


def main():
    if not HUMAN_SHEET.exists():
        print(f"Human sheet not found: {HUMAN_SHEET}")
        return

    with HUMAN_SHEET.open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    status_col = [k for k in rows[0].keys() if k.startswith("evidence_status_human")][0]
    grouped = defaultdict(list)
    for r in rows:
        val = r[status_col].strip()
        if val:
            grouped[(r["anthology_id"], r["item_id"])].append((r["annotator_name"], val))

    if not grouped:
        print("No completed human annotations found yet in human_annotation_sheet_pilot14.csv.")
        print("Fill in the 'evidence_status_human' column and re-run this script to get Cohen's kappa and Macro-F1.")
        return

    llm_map = {
        (e["anthology_id"], e["item_id"]): e["evidence_status"]
        for e in json.loads(LLM_JSON.read_text(encoding="utf-8"))
    }

    by_item_a, by_item_b = defaultdict(list), defaultdict(list)
    by_item_gold, by_item_llm = defaultdict(list), defaultdict(list)

    for (aid, iid), ann_list in grouped.items():
        if len(ann_list) >= 2:
            a_val, b_val = ann_list[0][1], ann_list[1][1]
            by_item_a[iid].append(a_val)
            by_item_b[iid].append(b_val)
            gold = a_val if a_val == b_val else a_val
            if (aid, iid) in llm_map:
                by_item_gold[iid].append(gold)
                by_item_llm[iid].append(llm_map[(aid, iid)])

    report = {}
    for iid in sorted(by_item_a.keys()):
        a_list, b_list = by_item_a[iid], by_item_b[iid]
        raw_agr = round(sum(1 for x, y in zip(a_list, b_list) if x == y) / len(a_list), 4)
        kappa = cohens_kappa(a_list, b_list)
        f1_stats = macro_f1(by_item_gold[iid], by_item_llm[iid])
        report[iid] = {
            "n_double_annotated": len(a_list),
            "human_raw_agreement": raw_agr,
            "human_cohens_kappa": kappa,
            "llm_vs_human_macro_f1": f1_stats["macro_f1"],
            "llm_per_class": f1_stats["per_class"],
        }

    out_path = DATA_DIR / "poc_iaa_and_validation_metrics.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

