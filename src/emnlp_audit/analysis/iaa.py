"""Inter-annotator agreement between two human annotators."""

from collections import Counter, defaultdict
from pathlib import Path

from emnlp_audit.files import read_csv


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


def raw_agreement(labels_a: list[str], labels_b: list[str]) -> float:
    return round(sum(1 for x, y in zip(labels_a, labels_b) if x == y) / len(labels_a), 4)


def load_double_annotations(sheet_path: Path) -> dict[tuple[str, str], list[tuple[str, str]]]:
    """Return {(anthology_id, item_id): [(annotator, evidence_status), ...]} for filled rows.

    Reads from individual files in `<sheet_path.parent>/by_annotator/*.csv` if any have filled labels,
    otherwise reads from `sheet_path`.
    """
    by_ann_dir = Path(sheet_path).parent / "by_annotator"
    rows = []
    if by_ann_dir.exists():
        for p in sorted(by_ann_dir.glob("annotation_sheet_*.csv")):
            rows.extend(read_csv(p))
    if not rows or not any(
        r.get([k for k in rows[0].keys() if k.startswith("evidence_status_human")][0], "").strip()
        for r in rows
    ):
        rows = read_csv(sheet_path) if Path(sheet_path).exists() else []
    if not rows:
        return {}
    status_col = [k for k in rows[0].keys() if k.startswith("evidence_status_human")][0]
    grouped = defaultdict(list)
    for r in rows:
        val = r[status_col].strip()
        if val:
            grouped[(r["anthology_id"], r["item_id"])].append((r["annotator_name"], val))
    return grouped
