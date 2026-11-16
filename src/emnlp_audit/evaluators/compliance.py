"""Single source of truth for policy applicability and derived compliance labels.

Used by the rule baseline, the LLM evaluator and the human annotation sheets,
so all of them derive compliance in exactly the same way (rubric: derived_compliance_rules).
"""

EVIDENCE_STATUSES = ["not_applicable", "not_reported", "explicitly_reported_inadequate", "adequately_reported"]
COMPLIANCE_LABELS = ["Compliant", "Non-compliant", "Not applicable", "Uncertain"]


def policy_applies(item: dict, year: int) -> bool:
    """True if the rubric records a mandatory obligation for this item in this publication year."""
    return int(year) in item["policy_mandate_years"]


def derive_compliance(pol_applies: bool, prac_applies, ev_status: str) -> str:
    if prac_applies == "uncertain" or ev_status == "uncertain":
        return "Uncertain"
    if not pol_applies or not prac_applies or ev_status == "not_applicable":
        return "Not applicable"
    if ev_status == "adequately_reported":
        return "Compliant"
    if ev_status in ("not_reported", "explicitly_reported_inadequate"):
        return "Non-compliant"
    return "Uncertain"
