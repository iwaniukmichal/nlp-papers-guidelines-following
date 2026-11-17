# Rubric changelog

Every change to the rubric creates a new file `rubric_v<version>.json`; earlier versions are kept
so that archived runs in `runs/` stay reproducible. Per the proposal, revisions may be based only on
pilot/development cases; later revisions require fresh testing or an exploratory designation.

## 2.0.0 (2026-11-16, field `rubric_version: "2.0.0"`)

- Grounded all six rubric items (`I1`–`I6`) in the verified historical requirement inventory
  (`config/policy_register/inventory.csv` and `config/rubric/item_selection.md`), adding explicit
  `req_ids`, `area`, `permitted_locations`, and ordered `decision_tree` procedures.
- Added the fifth evidence state `uncertain` across all items (handling undecidable applicability,
  truncated papers above `MAX_PAPER_CHARS`, and unverified LLM quotes).
- Refined `I3_ethical_risks` (`ETHICS_DISCUSSION` + `RISKS`) applicability so compliance denominators
  only include papers with human subjects/annotators, sensitive/personal data, or sensitive/dual-use
  tasks, while preserving adoption tracking across all papers.
- Defined `I4_computational_budget` (`COMPUTE_INFRASTRUCTURE` + `COMPUTE_RUNTIME` / `COMPUTE_BUDGET_TOTAL`)
  as a common longitudinal indicator requiring both hardware specification and quantitative compute
  duration/budget/energy.
- Expanded examples to at least 3 positive and 3 negative examples per item drawn from `pilot_14`
  papers (with `anthology_id`, verbatim quote, location, status, and reason), plus boundary cases
  and separate `rule_baseline_hints`.
- Added `A1_code_link` (`CODE_AVAILABILITY`) under `automatic_indicators` for zero-cost automatic
  tracking of code link availability across 2020–2026.

## 1.0.0 (2026-11-15, field `rubric_version: "1.0.0-poc"`)

- Initial six-item rubric used in the 14-paper pilot (I1 Limitations section, I2 Specific limitation,
  I3 Ethical risks, I4 Computational budget, I5 Asset licensing, I6 AI assistance disclosure).
- Four evidence states, derived compliance rules, one positive and one negative example per item.
