# Rubric development process

How we build the historical policy register and the compliance rubric for EMNLP 2020–2026.
The process is bottom-up: we first reconstruct **what was required**, and only then decide
**what we measure**. Every step leaves a file in the repository, so the rubric can be audited
back to the source documents.

Requirements that this process implements:

- Topic: *"Reconstruct a set of reporting requirements across selected years and operationalise
  them as an auditable compliance rubric"*; success = *"a documented historical guideline/rubric
  dataset with clear coding rules"*.
- Proposal: dated obligations from official calls, author/camera-ready instructions,
  reproducibility criteria, checklists and incorporated ACL/ARR policies, *"including pre-2020
  origins"*; source URLs, retrieval dates, checksums, wording, effective periods, tracks and stage;
  *"Current pages cannot establish historical rules"*; *"Missing historical policies will remain
  unresolved"*; *"Recommendations and practices without mandates are excluded from compliance
  denominators"*.

## Overview

| Stage | Output | Who |
|---|---|---|
| 1. Collect sources | `config/policy_register/documents.csv`, snapshots in `data/policy_sources/` | 1 person per edition |
| 2. Build requirement inventory | `config/policy_register/requirement_dictionary.csv`, `inventory.csv` | LLM draft + human verifier |
| 3. Select rubric items | decision log in `config/rubric/item_selection.md` | whole team |
| 4. Operationalise items | `config/rubric/rubric_v<version>.json` | item owner + reviewer |
| 5. Assign policy status per item × year | `config/policy_register/requirements.csv` | coder + verifier |
| 6. Pilot and revise | new rubric version + `CHANGELOG.md` entry | annotators |
| 7. Freeze | tagged version used for dev/test runs | whole team |

Stages 1–2 do not depend on the rubric at all. Stage 5 depends on the items chosen in stage 3.

---

## Stage 1: Collect source documents

**Goal:** a complete, dated set of documents that defined reporting obligations for each edition.

Document types to look for, per edition 2020–2026 (and 2019 for pre-2020 origins):

1. EMNLP call for papers (main conference; check whether Findings had separate rules).
2. Author guidelines and camera-ready instructions (obligations can be added at camera-ready stage).
3. Every ACL/ARR page the call incorporates by reference: ARR call for papers, Responsible NLP
   checklist, reproducibility checklist/criteria, ethics policy, ACL policy on AI writing assistance.
4. Front matter of the proceedings in the ACL Anthology (e.g. `2020.emnlp-main.0`): the programme
   chairs' preface often describes new policies of that year.

**Dating rule.** A document counts for an edition only in the version that was online **before that
edition's submission deadline**. Live pages are not used directly because they may have changed
since (the current ARR call itself notes that Limitations were optional before the December 2023
cycle). We take the closest earlier capture from the Internet Archive (Wayback Machine CDX API) and
download it in raw mode (`/web/<timestamp>id_/<url>`), which returns the original bytes, so every
team member gets an identical file with the same SHA-256.

**Secondary sources** (Dodge et al. 2019; Rogers et al. 2021; Magnusson et al. 2023; blog posts)
only help locate primary documents. A status is never assigned from a secondary source alone.

**Record** one row per document in `documents.csv`:

| Column | Example |
|---|---|
| `doc_id` | `EMNLP2020-CFP` |
| `year` | `2020` |
| `issuer` | `EMNLP` / `ARR` / `ACL` |
| `doc_type` | `cfp`, `camera_ready`, `author_guidelines`, `checklist`, `ethics_policy`, `ai_policy`, `front_matter` |
| `url` | original URL |
| `wayback_timestamp` | `20200528034026` (empty for Anthology PDFs) |
| `retrieved_at` | date we downloaded it |
| `sha256` | checksum of the downloaded file |
| `notes` | e.g. "page offline since 2023; Wayback only" |

Snapshots are stored and **committed** in `data/policy_sources/<doc_id>/` as the original file
(`<wayback_timestamp>.html` or `.pdf`) plus a plain-text extraction (`.txt`) used for reading and for
checking quotes. The Wayback timestamp and checksum also make every file re-downloadable and
verifiable by anyone.

Tooling:

- `uv run python scripts/00_fetch_policy_sources.py`: fetches every row of `documents.csv` that has
  no snapshot yet (finds the capture, downloads it, fills `wayback_timestamp`, `retrieved_at`,
  `sha256`, `local_path`). To add a document, append a row with `doc_id`, `year`, `issuer`,
  `doc_type`, `title`, `url`, `capture_before` and run the script.
- `--verify`: offline check that all committed files match their checksums.
- `--refetch`: re-downloads recorded captures and checks that they reproduce the checksums.

A document with no capture on or before its deadline is reported by the script and left without a
snapshot; we do not substitute a later capture without saying so in `notes`.

Proceedings front matter (ACL Anthology `<year>.emnlp-main.0`) is not snapshotted yet: the PDFs
range from 0.4 MB to 51 MB (full table of contents), too large to commit whole.

---

## Stage 2: Build the requirement inventory

**Goal:** a complete list of every **reporting requirement** in the collected documents, before
deciding what to measure. This is what lets us justify a small rubric: the register shows the full
picture and the rubric is a documented subset of it.

**In scope:** anything that asks authors to report, disclose or discuss content (in the paper, an
appendix, supplementary material or a checklist): limitations, ethics/risks, reproducibility
details, data and model documentation, human participants, licences, AI assistance.
**Out of scope:** formatting, page limits, anonymity, dual submission, presentation and
registration rules. (A page-limit *exemption* for a Limitations section is recorded as context.)

### Files

- `config/policy_register/requirement_dictionary.csv`: one row per `req_id` with its definition,
  topic area (`limitations`, `reproducibility`, `responsible_research`, `model_data_documentation`,
  `ai_tools`, or `other`), the matching ARR Responsible NLP checklist code (A1–E1), the
  reproducibility-checklist item, `source_wording` (verbatim wording from a source document,
  checked by the validator) and `mapping_note` (why items were merged or split). The ARR checklist
  is the backbone; 2020–2023 reproducibility items are mapped onto the same ids (as Magnusson et al.
  2023 do across venues), and requirements that only appear in calls for papers or ACL policies get
  their own ids (e.g. `LIMITATIONS_SECTION`, `ETHICS_DISCUSSION`, `AI_DISCLOSURE_IN_PAPER`,
  `COORDINATED_DISCLOSURE`). Items are split when their wording measures different things (e.g.
  `COMPUTE_RUNTIME` per run vs `COMPUTE_BUDGET_TOTAL` over all experiments); one item may map to
  two requirements (the 2021–23 "languages … number of examples" item → B5 and B6).
- `config/policy_register/inventory.csv`: the evidence rows (below).
- `config/policy_register/inventory_by_year.csv`: derived, one status per requirement × year ×
  route; regenerated by the validator, never edited by hand.

### One row = one piece of evidence

A row is **requirement × year × source document**. A requirement stated in several documents of
the same year (e.g. the EMNLP call and the ARR checklist) has several rows.

| Column | Meaning |
|---|---|
| `req_id` | id from the dictionary, the same in every year |
| `year` | edition (2019 = pre-2020 baseline; 2020–2026 analysed) |
| `doc_id` | source document from `documents.csv`; `none` / `unverified` rows may list several, separated by `;` |
| `quote` | verbatim wording, at most 50 words, copied from the document's `.txt` extraction |
| `location` | section or heading in the document |
| `where_reported` | `paper`, `appendix`, `supplementary`, `checklist`, `unspecified` |
| `status` | see the status scale below |
| `condition` | when it applies, e.g. "sensitive data or sensitive tasks", "AI assistants were used" |
| `route` | `all`, `direct` (submitted to EMNLP) or `arr` (committed from ACL Rolling Review). 2022–2023 had both routes; 2021 had a small ARR pilot with no archived ARR documents (`arr` = `unverified`); from 2024 ARR only. EMNLP-specific rules (EMNLP CFP ethics sanction, EMNLP Ethics FAQ, EMNLP supplementary-material clause) are coded `direct` in 2022–2023, because committed ARR papers "cannot be modified" and are reviewed under ARR's rules; the Limitations requirement is `all` because the EMNLP CFP explicitly extends it to ARR papers |
| `tracks` | `all_submissions`: rules apply to all submissions and Findings papers are selected from the same pool. The 2020–2021 camera-ready instructions state this explicitly; no Findings-specific rule was found in any year |
| `coded_by`, `verified_by` | who coded and who verified the row (different people) |
| `verification` | `pending`, `verified` or `disputed` |
| `notes` | reasoning for borderline statuses, related sentences, reasons for `unverified` |

Every requirement in the dictionary has at least one row for every year 2020–2026. When the
documents of a year were read and contain no such requirement, the row has `status = none` and
lists the documents checked. When a requirement cannot be established (missing document,
ambiguous wording, unclear scope), the row has `status = unverified` and the reason in `notes`;
we never infer a status from neighbouring years.

### Coding procedure (per year)

1. Read the `.txt` files of the year in a fixed order: EMNLP call for papers → ARR call for
   papers → checklist → ethics / AI policies → FAQs and blog posts → camera-ready instructions.
2. For every passage that asks authors to report, disclose or discuss something: map it to a
   `req_id` (or add one), copy a quote of at most 50 words, and assign a status with the rules below.
3. Record the route and tracks the passage applies to.
4. Add `none` / `unverified` rows for dictionary entries without evidence.
5. Run `uv run python scripts/00_validate_inventory.py`.

### Status from wording

| Wording in the document | Status |
|---|---|
| "must", "required", "will be desk rejected / automatically rejected" for all papers | `mandatory_in_paper` |
| the same, limited by a condition ("papers working with sensitive data … will not be accepted"), or a request combined with an explicit sanction ("we ask that you include … We reserve the right to reject papers … [that] inadequately addressed legitimate ethical concerns") | `conditional_mandatory` |
| a checklist question that must be answered, where a justified "No" is acceptable | `checklist_question` |
| criteria reviewers are asked to assess, with no author obligation ("Reviewers will be asked to assess …") | `reviewer_criterion` |
| "encouraged", "we ask", "should", "optional", with no sanction | `recommended` |

Further coding rules (fixed after the verification of 2026-11-15):

- **Guidance text counts.** Explanatory bullets under a checklist question are part of that
  question's scope (e.g. C2 guidance "how data was preprocessed" → `DATA_PREPROCESSING`; C3 guidance
  "report a result of the same model on the validation set" → `VALIDATION_PERFORMANCE`).
- **The checklist itself has a status.** The ARR call for papers says the checklist "should" be
  uploaded in 2022–2023 (→ `recommended`) and "must" be completed from 2024 (→ `checklist_question`);
  the status of every checklist question follows the status of the checklist in that year.
- **Content restrictions are not requirements.** Rules that limit what a section may contain (e.g.
  "this section should not introduce new methods") are recorded in `notes`, not as rows.
- **Conditions of checklist sections.** Questions under "Did you use or create scientific
  artifacts?", "Did you run computational experiments?" and "Did you use human annotators …?" carry
  that condition in `condition`; reproducibility-checklist items carry the heading of their block
  ("For all datasets used", …).

Year-level status (used from stage 5 on): for each route of a year, the strongest status among
the rows whose route is that route or `all`; a known status takes precedence over `unverified`.

### Validation

`scripts/00_validate_inventory.py` checks that every quote occurs verbatim in the text of its
source snapshot (whitespace, quotation marks and dashes normalized), that quotes have at most 50
words, that ids, statuses and routes are valid, that every requirement × year 2020–2026 is covered,
and that verified rows have a verifier different from the coder. It also writes
`inventory_by_year.csv` and prints a requirement × year matrix. The same checks run in the tests.

### How the first version was produced (LLM use)

The first version of `requirement_dictionary.csv` and `inventory.csv` (296 rows, 2026-11-15) was
drafted by an LLM (Claude Opus 5.5, via Claude Code) from the archived source documents of stage 1:
the model read the `.txt` extractions, selected the passages, copied the quotes, and proposed the
`req_id`, status, route and notes for each row, following the procedure and status rules above.
All drafted rows are marked `coded_by = claude-opus-5-5 (LLM draft)` and `verification = pending`.
The script that wrote the draft is kept in
`config/policy_register/provenance/build_inventory_v1_llm_draft.py` for auditability.

The safeguards against LLM errors are: (1) every quote is checked automatically against the
archived source text, so no quote can be invented; (2) every row is verified by a team member, who
checks the assigned status and searches the year's documents for missed requirements;
(3) borderline statuses carry their reasoning in `notes` so the verifier can contest them.
Statuses are not used in the analysis until their rows are `verified`. This use of an LLM is
declared in the project's LLM-use declaration.

**LLM self-audit (2026-11-15).** A second session of the same model checked all 296 draft rows
against the sources with a fixed prompt (236 agree, 20 disagree, 40 unsure), reported in
`provenance/verification_2026-11-15.md` and `provenance/verification_2026-11-15_verdicts.csv`.
Because the coder and the checker are the same model, this is a self-audit, not an independent
verification and not an inter-coder agreement. The resulting decisions were taken by a team member
and applied by `provenance/apply_verification_2026-11-15.py` (documented decisions 1–11 in its
header; changed rows are tagged in `notes`). The audit also identified a missing source, the ACL
Policy on Publication Ethics, which was added to stage 1. After the corrections the inventory has
362 rows for 34 requirements; all rows remain `pending` until verified by a team member. An
independent second opinion can be obtained by running the same prompt with a model from a
different family.

### Status scale

Ordered from weakest to strongest:

| Status | Meaning |
|---|---|
| `none` | documents for that year were checked and contain no such requirement |
| `recommended` | authors are encouraged to report it |
| `reviewer_criterion` | reviewers are asked to assess it; authors are not required to report it |
| `checklist_question` | authors must answer a checklist question; a justified "No" is acceptable |
| `conditional_mandatory` | must be in the paper when a condition holds (e.g. sensitive data) |
| `mandatory_in_paper` | must be in the paper for all papers (e.g. desk rejection if missing) |
| `unverified` | no primary source found or the wording is ambiguous; never guessed |

Derived quantities used in the analysis:

- **Introduced in year t:** the first year with status other than `none`/`unverified`.
- **Strengthened in year t:** status is higher than in year t−1. Introduction and strengthening
  years are the breakpoints for RQ2 (adoption).
- **Policy applies (compliance):** status is `mandatory_in_paper`, or `conditional_mandatory` and
  the condition holds for the paper. Only these enter compliance denominators (RQ1).

---

## Stage 3: Select rubric items

**Goal:** choose which inventory requirements become rubric items, and document why.

Each candidate is scored against these criteria:

1. **Topic coverage:** belongs to one of the topic's five areas: limitations, reproducibility,
   responsible research, model/data documentation, AI tools. The final set should cover all five.
2. **Variation in policy:** its status changes at least once in 2020–2026 (gives a breakpoint for
   H1/RQ2), or it is kept deliberately as a fixed adoption indicator.
3. **Observable in the paper:** can be judged from the main text and ordinary appendices
   (checklists are excluded as evidence for papers, although they are sources of policy).
4. **Reliably codable:** two annotators can agree on it with a written definition; checked in the pilot.
5. **Applicability decidable:** we can tell whether it applies to a given paper.
6. **Workload:** total annotation effort stays feasible (140 test papers × 2 annotators × items).

Outcome: `config/rubric/item_selection.md` with a table of all candidates (`req_id`, scores on 1–6,
decision, reason). Excluded requirements remain in the inventory with their exclusion reason.
Items are not merged across requirements whose wording changed; a changed definition requires a
common indicator or a separate series (proposal, Rubric and Annotation Protocol).

---

## Stage 4: Operationalise each item

**Goal:** a definition precise enough that two annotators and the LLM apply it the same way.
For each item the rubric records:

- **Definition** and the `req_id`(s) it measures.
- **Applicability rule** (`practice_applies`: true / false / uncertain) with examples.
- **Permitted evidence locations:** main text, appendix, acknowledgements, footnotes.
- **Decision procedure:** ordered questions, e.g. "Is there a heading? → Is a concrete assumption
  or failure stated? → Is its consequence stated?".
- **Evidence states:** `not_applicable`, `not_reported`, `explicitly_reported_inadequate`,
  `adequately_reported`, `uncertain`, each with a definition.
- **Examples:** at least 3 positive, 3 negative and the known boundary cases, taken from real
  papers (pilot/dev only), with the reason for each label.
- **Hints for the rule baseline** (headings, keywords), kept separate from the definition.

---

## Stage 5: Policy status per item × year

**Goal:** link every rubric item to the obligations that applied in each year.

`requirements.csv` has one row per `item_id × year` (2020–2026). Its `status` is taken from the
inventory rows of the `req_id`(s) the item measures, with a reference to those rows. The rubric
no longer stores `policy_mandate_years`; `policy_applies` and the breakpoints are computed from
this file.

Known open question to resolve in this stage: in 2022–2023 EMNLP accepted both direct
submissions and ARR commitments, which may have had different checklists. If the two routes had
different obligations and we cannot tell which route a paper took, the status is `unverified`
for the affected item and year.

---

## Stage 6: Pilot and revise

1. Both annotators of each pair label the pilot sample independently with the draft rubric.
2. Compare labels; list every disagreement with its cause (unclear definition, missing boundary
   case, applicability, parsing problem).
3. Revise definitions and examples; record each change in `config/rubric/CHANGELOG.md` and save it
   as a new rubric version (old versions are kept).
4. Repeat on the development sample if needed.

Only pilot and development papers may be used to revise the rubric or the evaluator (proposal).

---

## Stage 7: Freeze

Before the held-out test sample is annotated, the rubric version, the LLM prompt and model
settings are frozen. Any later change creates a new version and its results are reported as
exploratory or re-tested on fresh papers.

---

## Verification rules (all stages)

- Every inventory and requirements row has a coder and a different verifier.
- The verifier checks the quote against the snapshot and the assigned status; disagreements are
  marked `disputed` and resolved in a team discussion, with the decision recorded in `notes`.
- Anything without a primary source is `unverified`. It stays unresolved in the analysis
  (reported separately), as the proposal requires.

## Status of the current rubric

`rubric_v1.0.0.json` and the current `register.json` were written for the proof of concept before
this process existed. They have no source snapshots, retrieval dates, checksums or verbatim quotes,
and spot checks found statuses that the sources do not support (e.g. a Responsible NLP checklist
attributed to 2021; checklist rules attributed to the 2022 and 2023 calls; the 2020 ethics policy
missing). They are treated as a draft. The next rubric version will be produced with stages 1–7.

## Timeline

Fits the proposal schedule ("19 Nov.–2 Dec.: collect corpus; freeze rubric"):

| Dates | Stages |
|---|---|
| until 22 Nov. | 1–2 (sources and inventory), in parallel with pilot annotation of v1.0.0 |
| 23–26 Nov. | 3–5 (selection, operationalisation, item × year statuses) |
| 27 Nov.–1 Dec. | 6 (re-check pilot disagreements, development sample) |
| 2 Dec. | 7 (freeze) |
