"""Validate config/policy_register/inventory.csv and write the derived year-level table.

Checks: known req_ids / statuses / routes; every quote occurs verbatim in the text of its source
snapshot (whitespace and quotation marks normalized); quotes <= 50 words; every requirement x year
(2020-2026) has at least one row; verified rows have a verifier different from the coder.

Writes config/policy_register/inventory_by_year.csv (strongest status per requirement x year x route)
and prints a compact requirement x year matrix.
"""

import argparse
from collections import Counter

from emnlp_audit.files import write_csv
from emnlp_audit.policy import inventory as inv

ABBREV = {
    "none": ".", "recommended": "rec", "reviewer_criterion": "rev", "checklist_question": "chk",
    "conditional_mandatory": "COND", "mandatory_in_paper": "MAND", "unverified": "?",
}


def print_matrix(by_year: list[dict]) -> None:
    cells = {}
    for r in by_year:
        key = (r["req_id"], r["year"])
        label = ABBREV[r["status"]] if r["route"] == "all" else f"{r['route'][0]}:{ABBREV[r['status']]}"
        cells[key] = f"{cells[key]} {label}" if key in cells else label
    req_ids = sorted({r["req_id"] for r in by_year})
    print(f"{'requirement':<28}" + "".join(f"{y:>16}" for y in inv.YEARS))
    for req in req_ids:
        print(f"{req:<28}" + "".join(f"{cells.get((req, y), '-'):>16}" for y in inv.YEARS))
    print("\nLegend: MAND mandatory_in_paper, COND conditional_mandatory, chk checklist_question, "
          "rev reviewer_criterion, rec recommended, . none, ? unverified; d:/a: = direct/ARR route")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--quiet", action="store_true", help="do not print the matrix")
    args = parser.parse_args()

    rows = inv.load_inventory()
    dictionary = inv.load_dictionary()
    errors = inv.validate_dictionary(dictionary) + inv.validate(rows, dictionary)
    for e in errors:
        print(f"[ERROR] {e}")

    by_year = inv.year_level(rows)
    write_csv(inv.BY_YEAR_PATH, by_year)
    rubric_v2_path = inv.paths.rubric_path("2.0.0")
    if rubric_v2_path.exists():
        from emnlp_audit.files import read_json

        req_rows = inv.build_requirements_table(by_year, read_json(rubric_v2_path))
        write_csv(inv.REQUIREMENTS_PATH, req_rows)
    if not args.quiet:
        print_matrix(by_year)

    verification = Counter(r["verification"] for r in rows)
    print(f"\n{len(rows)} rows; verification: {dict(verification)}; {len(errors)} errors")
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
