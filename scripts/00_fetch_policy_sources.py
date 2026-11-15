"""Step 0: download dated snapshots of policy documents listed in config/policy_register/documents.csv.

For each row without a snapshot: find the latest Wayback capture on or before `capture_before`
(or download the ACL Anthology PDF), store it in data/policy_sources/<doc_id>/ with a text
extraction, and record wayback_timestamp, retrieved_at, sha256 and local_path in the CSV.

  --verify   no network: check that every stored file still matches its recorded SHA-256
  --refetch  re-download recorded captures and check they reproduce the recorded SHA-256
  --retext   no network: regenerate the .txt extractions from stored originals
"""

import argparse
import datetime as dt

from emnlp_audit import paths
from emnlp_audit.files import read_csv, write_csv
from emnlp_audit.policy import sources


def verify(rows: list[dict]) -> int:
    problems = documented_absent = 0
    for row in rows:
        if not row["local_path"] and row["notes"].startswith("NO SNAPSHOT"):
            documented_absent += 1  # deliberately missing, reason recorded in notes
            continue
        if not row["local_path"]:
            print(f"[MISSING] {row['doc_id']}: not fetched yet")
            problems += 1
            continue
        path = paths.from_repo_relative(row["local_path"])
        if not path.exists():
            print(f"[MISSING] {row['doc_id']}: {row['local_path']} not found")
            problems += 1
        elif sources.sha256(path.read_bytes()) != row["sha256"]:
            print(f"[CHANGED] {row['doc_id']}: checksum differs from documents.csv")
            problems += 1
    checked = len(rows) - documented_absent
    print(f"{checked - problems}/{checked} snapshots verified; {documented_absent} documented as unavailable")
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--refetch", action="store_true")
    parser.add_argument("--retext", action="store_true", help="no network: regenerate .txt files from stored originals")
    parser.add_argument("--only", nargs="+", help="process only these doc_ids")
    args = parser.parse_args()

    rows = read_csv(paths.POLICY_DOCUMENTS_PATH)
    if args.verify:
        raise SystemExit(1 if verify(rows) else 0)
    if args.retext:
        for row in rows:
            if row["local_path"]:
                sources.write_text(paths.from_repo_relative(row["local_path"]))
        print("Text extractions regenerated.")
        return

    for row in rows:
        if args.only and row["doc_id"] not in args.only:
            continue
        if row["local_path"] and not args.refetch:
            continue

        try:
            if not sources.is_anthology(row["url"]) and not row["wayback_timestamp"]:
                capture = sources.find_capture(row["url"], row["capture_before"])
                if capture is None:
                    print(f"[NO CAPTURE] {row['doc_id']}: nothing archived on or before {row['capture_before']}")
                    continue
                row["wayback_timestamp"] = capture[0]
            raw = sources.download(row)
        except RuntimeError as e:
            print(f"[ERROR] {row['doc_id']}: {e} (re-run the script to retry)")
            continue

        digest = sources.sha256(raw)
        if row["sha256"] and digest != row["sha256"]:
            print(f"[MISMATCH] {row['doc_id']}: re-downloaded file differs from recorded checksum; kept old record")
            continue

        stored = sources.store(row, raw)
        row["sha256"] = digest
        row["local_path"] = paths.to_repo_relative(stored)
        row["retrieved_at"] = row["retrieved_at"] or dt.date.today().isoformat()
        print(f"[OK] {row['doc_id']}: {row['wayback_timestamp'] or 'anthology'} -> {row['local_path']}")
        write_csv(paths.POLICY_DOCUMENTS_PATH, rows, fieldnames=sources.DOCUMENT_FIELDS)  # save progress


if __name__ == "__main__":
    main()
