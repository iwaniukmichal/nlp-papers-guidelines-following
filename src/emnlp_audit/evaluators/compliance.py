"""Single source of truth for policy applicability and derived compliance labels.

Used by the rule baseline, the LLM evaluator and the human annotation sheets,
so all of them derive compliance in exactly the same way (rubric: derived_compliance_rules).
Policy applicability is computed from config/policy_register/requirements.csv (derived from
inventory_by_year.csv), taking into account submission route (direct vs arr) in 2022-2023.
"""

from functools import lru_cache

from emnlp_audit import paths
from emnlp_audit.files import read_csv

EVIDENCE_STATUSES = [
    "not_applicable",
    "not_reported",
    "explicitly_reported_inadequate",
    "adequately_reported",
    "uncertain",
]
COMPLIANCE_LABELS = ["Compliant", "Non-compliant", "Not applicable", "Uncertain"]


def _parse_bool_or_unverified(val) -> bool | str:
    if isinstance(val, bool):
        return val
    s = str(val).strip().lower()
    if s == "true":
        return True
    if s == "false":
        return False
    return "unverified"


@lru_cache(maxsize=1)
def _load_requirements_map() -> dict[tuple[str, int], dict]:
    if not paths.POLICY_REQUIREMENTS_PATH.exists():
        return {}
    return {(r["item_id"], int(r["year"])): r for r in read_csv(paths.POLICY_REQUIREMENTS_PATH)}


def policy_applies(item: dict | str, year: int, route: str = "all") -> bool | str:
    """Return True, False, or 'unverified' for (item, year, route) from requirements.csv.

    Falls back to `item['policy_mandate_years']` only if `item` is an inline dict not present
    in requirements.csv.
    """
    item_id = item if isinstance(item, str) else item.get("item_id", "")
    req_map = _load_requirements_map()
    row = req_map.get((item_id, int(year)))
    if row is not None:
        if route == "direct":
            return _parse_bool_or_unverified(row["policy_applies_direct"])
        if route == "arr":
            return _parse_bool_or_unverified(row["policy_applies_arr"])
        return _parse_bool_or_unverified(row["policy_applies"])

    if isinstance(item, dict) and "policy_mandate_years" in item:
        return int(year) in item["policy_mandate_years"]
    return False


def derive_compliance(pol_applies: bool | str, prac_applies, ev_status: str) -> str:
    if pol_applies == "unverified" or prac_applies == "uncertain" or ev_status == "uncertain":
        return "Uncertain"
    if not pol_applies or not prac_applies or ev_status == "not_applicable":
        return "Not applicable"
    if ev_status == "adequately_reported":
        return "Compliant"
    if ev_status in ("not_reported", "explicitly_reported_inadequate"):
        return "Non-compliant"
    return "Uncertain"
