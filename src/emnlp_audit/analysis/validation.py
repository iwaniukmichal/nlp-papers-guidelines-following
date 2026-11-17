"""Validation of an automatic evaluator against human labels (per-item P/R/F1, macro-F1)
with explicit adjudication of annotator disagreements."""

from collections import defaultdict
from pathlib import Path

from emnlp_audit.analysis.iaa import cohens_kappa, raw_agreement
from emnlp_audit.files import read_csv, write_csv


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


def load_adjudicated_labels(adjudication_path: Path | None) -> dict[tuple[str, str], str]:
    """Load resolved reference labels {(anthology_id, item_id): adjudicated_status}."""
    if not adjudication_path or not Path(adjudication_path).exists():
        return {}
    out = {}
    for r in read_csv(adjudication_path):
        val = (r.get("adjudicated_status") or "").strip()
        if val:
            out[(r["anthology_id"], r["item_id"])] = val
    return out


def sync_adjudication_sheet(grouped_human: dict, adjudication_path: Path) -> int:
    """Create or update `adjudication.csv` with any disagreements between annotators A and B."""
    existing = {}
    if Path(adjudication_path).exists():
        for r in read_csv(adjudication_path):
            existing[(r["anthology_id"], r["item_id"])] = r

    rows = []
    unresolved = 0
    for (aid, iid), ann_list in sorted(grouped_human.items()):
        if len(ann_list) >= 2:
            (ann_a, a_val), (ann_b, b_val) = ann_list[0], ann_list[1]
            if a_val != b_val:
                prev = existing.get((aid, iid), {})
                adj_val = (prev.get("adjudicated_status") or "").strip()
                if not adj_val:
                    unresolved += 1
                rows.append({
                    "anthology_id": aid,
                    "item_id": iid,
                    "annotator_a": ann_a,
                    "status_a": a_val,
                    "annotator_b": ann_b,
                    "status_b": b_val,
                    "adjudicated_status": adj_val,
                    "adjudicated_by": prev.get("adjudicated_by", ""),
                    "notes": prev.get("notes", ""),
                })
    if rows:
        write_csv(
            adjudication_path,
            rows,
            [
                "anthology_id",
                "item_id",
                "annotator_a",
                "status_a",
                "annotator_b",
                "status_b",
                "adjudicated_status",
                "adjudicated_by",
                "notes",
            ],
        )
    return unresolved


def iaa_and_validation_report(
    grouped_human: dict,
    evaluator_records: list[dict],
    adjudicated_labels: dict[tuple[str, str], str] | None = None,
) -> dict:
    """
    Per item: pre-adjudication human-human raw agreement and Cohen's kappa, plus
    evaluator-vs-human macro-F1 against reference labels (consensus when A == B, or
    adjudicated_status when A != B).
    """
    adjudicated = adjudicated_labels or {}
    eval_map = {(e["anthology_id"], e["item_id"]): e["evidence_status"] for e in evaluator_records}

    by_item_a, by_item_b = defaultdict(list), defaultdict(list)
    by_item_gold, by_item_pred = defaultdict(list), defaultdict(list)
    by_item_unadjudicated = defaultdict(int)

    for (aid, iid), ann_list in grouped_human.items():
        if len(ann_list) >= 2:
            a_val, b_val = ann_list[0][1], ann_list[1][1]
            by_item_a[iid].append(a_val)
            by_item_b[iid].append(b_val)
            if a_val == b_val:
                gold = a_val
            elif (aid, iid) in adjudicated:
                gold = adjudicated[(aid, iid)]
            else:
                by_item_unadjudicated[iid] += 1
                gold = None

            if gold is not None and (aid, iid) in eval_map:
                by_item_gold[iid].append(gold)
                by_item_pred[iid].append(eval_map[(aid, iid)])

    report = {}
    for iid in sorted(by_item_a.keys()):
        a_list, b_list = by_item_a[iid], by_item_b[iid]
        f1_stats = macro_f1(by_item_gold[iid], by_item_pred[iid])
        report[iid] = {
            "n_double_annotated": len(a_list),
            "n_reference_resolved": len(by_item_gold[iid]),
            "n_disagreements_pending_adjudication": by_item_unadjudicated[iid],
            "human_raw_agreement": raw_agreement(a_list, b_list),
            "human_cohens_kappa": cohens_kappa(a_list, b_list),
            "llm_vs_human_macro_f1": f1_stats["macro_f1"],
            "llm_per_class": f1_stats["per_class"],
        }
    return report
