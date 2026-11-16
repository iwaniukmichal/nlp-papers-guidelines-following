"""Requirement inventory (stage 2 of docs/methodology/rubric-development.md).

One inventory row = one piece of evidence: requirement x year x source document, with a verbatim
quote and a status on the scale below. Rows with status `none` or `unverified` record that the
documents of that year were checked and contain no such requirement, or that it cannot be
established; they may list several doc_ids separated by ';'.

Year-level status: for each submission route of a year (`direct`, `arr`), the strongest status
among rows whose route is that route or `all`; a route with no row has status `none`.
"""

import re
from collections import defaultdict

from emnlp_audit import paths
from emnlp_audit.files import read_csv

INVENTORY_PATH = paths.POLICY_REGISTER_DIR / "inventory.csv"
DICTIONARY_PATH = paths.POLICY_REGISTER_DIR / "requirement_dictionary.csv"
BY_YEAR_PATH = paths.POLICY_REGISTER_DIR / "inventory_by_year.csv"
REQUIREMENTS_PATH = paths.POLICY_REQUIREMENTS_PATH

INVENTORY_FIELDS = [
    "req_id", "year", "doc_id", "quote", "location", "where_reported", "status", "condition",
    "route", "tracks", "coded_by", "verified_by", "verification", "notes",
]
DICTIONARY_FIELDS = [
    "req_id", "area", "definition", "arr_checklist_code", "repro_checklist_item", "source_wording", "mapping_note",
]
AREAS = {"limitations", "reproducibility", "responsible_research", "model_data_documentation", "ai_tools", "other"}
TRACKS = {"all_submissions", "main", "findings"}

# Ordered from weakest to strongest; `unverified` is handled separately.
STATUS_ORDER = [
    "none", "recommended", "reviewer_criterion", "checklist_question",
    "conditional_mandatory", "mandatory_in_paper",
]
STATUSES = STATUS_ORDER + ["unverified"]
ROUTES = {"all", "direct", "arr"}
WHERE = {"paper", "appendix", "supplementary", "checklist", "unspecified", ""}
VERIFICATION = {"pending", "verified", "disputed"}
YEARS = list(range(2020, 2027))
MAX_QUOTE_WORDS = 50

_QUOTE_MAP = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-", " ": " "})


def normalize(text: str) -> str:
    """Make quotes comparable with source text: unify quotation marks/dashes, collapse whitespace."""
    return re.sub(r"\s+", " ", text.translate(_QUOTE_MAP)).strip().lower()


def load_inventory() -> list[dict]:
    return read_csv(INVENTORY_PATH)


def load_dictionary() -> dict[str, dict]:
    return {r["req_id"]: r for r in read_csv(DICTIONARY_PATH)}


def _source_texts() -> dict[str, str]:
    texts = {}
    for row in read_csv(paths.POLICY_DOCUMENTS_PATH):
        if row["local_path"]:
            txt = paths.from_repo_relative(row["local_path"]).with_suffix(".txt")
            texts[row["doc_id"]] = normalize(txt.read_text(encoding="utf-8"))
        else:
            texts[row["doc_id"]] = None  # documented as unavailable
    return texts


def validate_dictionary(dictionary: dict[str, dict]) -> list[str]:
    """Areas are valid and every source_wording occurs verbatim in at least one source document."""
    errors = []
    corpus = [t for t in _source_texts().values() if t]
    for req_id, d in dictionary.items():
        if d.get("area") not in AREAS:
            errors.append(f"dictionary {req_id}: unknown area '{d.get('area')}'")
        wording = d.get("source_wording", "")
        if not wording:
            errors.append(f"dictionary {req_id}: source_wording is empty")
        elif not any(normalize(wording) in t for t in corpus):
            errors.append(f"dictionary {req_id}: source_wording not found in any source document")
    return errors


def validate(rows: list[dict], dictionary: dict[str, dict]) -> list[str]:
    errors = []
    texts = _source_texts()
    covered = set()

    for i, r in enumerate(rows, start=2):  # line numbers as in the CSV file
        where = f"line {i} ({r['req_id']} {r['year']} {r['doc_id']})"
        if r["req_id"] not in dictionary:
            errors.append(f"{where}: unknown req_id")
        if r["status"] not in STATUSES:
            errors.append(f"{where}: unknown status '{r['status']}'")
        if r["route"] not in ROUTES:
            errors.append(f"{where}: unknown route '{r['route']}'")
        if r["tracks"] not in TRACKS:
            errors.append(f"{where}: unknown tracks '{r['tracks']}'")
        if r["where_reported"] not in WHERE:
            errors.append(f"{where}: unknown where_reported '{r['where_reported']}'")
        if r["verification"] not in VERIFICATION:
            errors.append(f"{where}: verification must be one of {sorted(VERIFICATION)}")
        if r["verification"] == "verified" and (not r["verified_by"] or r["verified_by"] == r["coded_by"]):
            errors.append(f"{where}: verified rows need a verifier different from the coder")

        doc_ids = [d for d in r["doc_id"].split(";") if d]
        for d in doc_ids:
            if d not in texts:
                errors.append(f"{where}: doc_id '{d}' not in documents.csv")

        if r["status"] in ("none", "unverified"):
            if r["status"] == "unverified" and not r["notes"]:
                errors.append(f"{where}: unverified rows must explain why in notes")
        elif not r["quote"]:
            errors.append(f"{where}: status '{r['status']}' requires a quote")

        if r["quote"]:
            if len(doc_ids) != 1:
                errors.append(f"{where}: a quoted row must cite exactly one document")
            elif texts.get(doc_ids[0]) is None:
                errors.append(f"{where}: document has no snapshot, quote cannot be checked")
            elif normalize(r["quote"]) not in texts[doc_ids[0]]:
                errors.append(f"{where}: quote not found verbatim in the source text")
            if len(r["quote"].split()) > MAX_QUOTE_WORDS:
                errors.append(f"{where}: quote longer than {MAX_QUOTE_WORDS} words")

        covered.add((r["req_id"], int(r["year"])))

    for req_id in dictionary:
        for year in YEARS:
            if (req_id, year) not in covered:
                errors.append(f"coverage: no row for {req_id} x {year}")
    return errors


def _strongest(statuses: list[str]) -> str:
    known = [s for s in statuses if s in STATUS_ORDER]
    if known:
        return max(known, key=STATUS_ORDER.index)
    return "unverified" if "unverified" in statuses else "none"


def year_level(rows: list[dict]) -> list[dict]:
    """Collapse evidence rows into one status per requirement x year x route."""
    grouped = defaultdict(list)
    routes_by_year = defaultdict(set)
    for r in rows:
        grouped[(r["req_id"], int(r["year"]))].append(r)
        if r["route"] != "all":
            routes_by_year[int(r["year"])].add(r["route"])

    out = []
    for (req_id, year), group in sorted(grouped.items()):
        routes = sorted(routes_by_year[year]) or ["all"]
        for route in routes:
            applicable = [g for g in group if g["route"] in (route, "all")]
            out.append({
                "req_id": req_id,
                "year": year,
                "route": route,
                "status": _strongest([g["status"] for g in applicable]),
                "sources": ";".join(sorted({g["doc_id"] for g in applicable if g["status"] not in ("none",)})),
                "verified": all(g["verification"] == "verified" for g in (applicable or group)),
            })
    return out


def _status_applies_to_compliance(status: str, descriptive_only: bool = False) -> bool | str:
    if descriptive_only:
        return False
    if status == "unverified":
        return "unverified"
    return status in ("mandatory_in_paper", "conditional_mandatory")


def build_requirements_table(by_year: list[dict], rubric: dict) -> list[dict]:
    """Derive config/policy_register/requirements.csv (Stage 5) from inventory_by_year.csv and rubric v2."""
    lookup: dict[tuple[str, int, str], dict] = {}
    routes_by_year: dict[int, set[str]] = defaultdict(set)
    for r in by_year:
        y = int(r["year"])
        lookup[(r["req_id"], y, r["route"])] = r
        routes_by_year[y].add(r["route"])

    all_items = list(rubric.get("items", [])) + [
        {
            "item_id": ind["indicator_id"],
            "req_ids": ind["req_ids"],
            "descriptive_only": True,
        }
        for ind in rubric.get("automatic_indicators", [])
    ]

    out = []
    for item in all_items:
        iid = item["item_id"]
        req_ids = item.get("req_ids", [])
        descriptive_only = bool(item.get("descriptive_only", False)) or iid == "I6_ai_assistance"

        for year in YEARS:
            year_routes = routes_by_year.get(year, {"all"})
            route_statuses = {}
            route_sources = set()
            all_verified = True

            for route in ("direct", "arr"):
                r_key = route if route in year_routes else "all"
                statuses = []
                for req_id in req_ids:
                    cell = lookup.get((req_id, year, r_key)) or lookup.get((req_id, year, "all"))
                    if cell:
                        statuses.append(cell["status"])
                        if cell["sources"]:
                            route_sources.update(cell["sources"].split(";"))
                        if not str(cell["verified"]).lower() == "true":
                            all_verified = False
                route_statuses[route] = _strongest(statuses) if statuses else "none"

            st_direct = route_statuses["direct"]
            st_arr = route_statuses["arr"]
            if st_direct == st_arr:
                combined_status = st_direct
            elif year == 2021 and st_arr == "unverified":
                # In 2021 only a small pilot fraction came from ARR; direct CFP is the primary known status
                combined_status = st_direct
            else:
                combined_status = f"direct:{st_direct}|arr:{st_arr}"

            app_direct = _status_applies_to_compliance(st_direct, descriptive_only)
            app_arr = _status_applies_to_compliance(st_arr, descriptive_only)
            if app_direct == app_arr:
                pol_applies = app_direct
            elif year == 2021 and app_arr == "unverified":
                pol_applies = app_direct
            else:
                pol_applies = "unverified"

            out.append({
                "item_id": iid,
                "year": year,
                "req_ids": ";".join(req_ids),
                "status_direct": st_direct,
                "status_arr": st_arr,
                "status": combined_status,
                "policy_applies_direct": app_direct,
                "policy_applies_arr": app_arr,
                "policy_applies": pol_applies,
                "sources": ";".join(sorted(s for s in route_sources if s)),
                "verified": all_verified,
            })
    return out
