# Inventory verification prompt

Prompt for an LLM (preferably a model family other than the one that drafted the inventory) or as a
checklist for a human verifier. Use one batch per year: attach `requirement_dictionary.csv`, the rows
of `inventory.csv` for that year (`inventory_<YEAR>.csv`) and the `.txt` files of that year's documents
from `data/policy_sources/` (named `<doc_id>.txt`). Results are input for the human verifier, who
records `verified_by` / `verification` in `inventory.csv`.

```
You are verifying a research dataset: an inventory of the reporting requirements that applied to
papers at the EMNLP conference (NLP, Association for Computational Linguistics) in a given year.
The inventory was drafted by another LLM from archived copies of the official policy documents.
Your job is an independent, critical check. Do not assume the draft is correct. Do not use your
own background knowledge about ACL/EMNLP policies as evidence: judge ONLY from the source texts
attached to this message. If something cannot be decided from them, say so.

Attached: requirement_dictionary.csv (req_id, definitions, ARR checklist code A1-E1 or 2020
reproducibility item); inventory_<YEAR>.csv (one row = requirement x year x source document;
columns req_id, year, doc_id, quote, location, where_reported, status, condition, route, tracks,
coded_by, verified_by, verification, notes; 'none' rows list the documents checked); one
<doc_id>.txt per source document (the ONLY evidence).

Route: direct = submitted to EMNLP; arr = committed from ACL Rolling Review; all = both.
In scope: anything asking authors to report, disclose or discuss content (paper, appendix,
supplementary, checklist). Out of scope: formatting, page limits, anonymity, dual submission,
presentation, registration, reviewing duties.

Status scale and wording rules:
none: no such requirement | recommended: "encouraged/we ask/should/optional", no sanction |
reviewer_criterion: reviewers assess it, no author obligation | checklist_question: checklist
question that must be answered, justified "No" acceptable (the checklist itself must be
mandatory that year) | conditional_mandatory: must/required/rejection limited by a condition, or a
request with an explicit sanction | mandatory_in_paper: must/required/desk-rejected for all papers |
unverified: no primary source, ambiguous wording or unclear scope.
Guidance bullets under a checklist question count as part of that question.

For EVERY row: (A) quote present and meaning correct in context; (B) right req_id; (C) status
follows the rules (read the surrounding paragraph); (D) route, tracks, condition, where_reported
correct; (E) for 'none' rows, search all documents (synonyms) for the requirement.
For the year: (F) list in-scope passages not represented by any row; (G) flag dictionary mappings
that merge or split requirements wrongly.

Output: 1) table: row_number | req_id | doc_id | AGREE/DISAGREE/UNSURE | proposed status |
evidence (verbatim quote <= 50 words, with doc_id) | reason (1-2 sentences);
2) missed requirements; 3) dictionary issues; 4) counts and the 3 most important problems.
Every quote must be copied verbatim from an attached file; otherwise write "not found in the
attached documents". If wording is ambiguous between two statuses, answer UNSURE and name both.
```
