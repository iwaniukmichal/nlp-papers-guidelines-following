"""Step 1: build the manifest of eligible EMNLP Main + Findings papers from ACL Anthology XML.

Outputs: data/manifest/eligible_manifest.csv, data/manifest/counts_by_year_track.json
"""

import argparse

from emnlp_audit import paths
from emnlp_audit.corpus.anthology import MANIFEST_FIELDS, build_manifest
from emnlp_audit.files import write_csv, write_json

DEFAULT_YEARS = [2020, 2021, 2022, 2023, 2024, 2025, 2026]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--years", type=int, nargs="+", default=DEFAULT_YEARS)
    args = parser.parse_args()

    all_papers, counts = build_manifest(args.years)
    write_json(paths.COUNTS_PATH, counts)
    write_csv(paths.MANIFEST_PATH, all_papers, fieldnames=MANIFEST_FIELDS)
    print(f"\nSaved {len(all_papers)} eligible papers to {paths.MANIFEST_PATH}")


if __name__ == "__main__":
    main()
