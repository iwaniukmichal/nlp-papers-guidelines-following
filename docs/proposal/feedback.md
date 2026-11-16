NLP project proposal - topic 4

Iwaniuk Michał 2 (STUD)
Śr, 4.11.2026 18:14
Dzień Dobry Przesyłam project proposal Pozdrawiam
Wróblewska Anna 1

Iwaniuk Michał 2 (STUD);
Borycki Bartłomiej (STUD);
Chodań Miłosz (STUD);
Guzik Mikołaj (STUD)
Kucia Filip (DOKT)
Dear Team,

Project: From guidelines to practice: Do NLP papers follow reporting requirements?

Your proposed Phase 1 assessment is shown below. The scientific score follows the published rubric; any verified administrative penalty is applied separately.

Phase 1 grade calculation

Item

Points

Scientific assessment (criteria 1.1–1.5)

5/10

Confirmed formal penalty

0

Phase 1 score after confirmed penalty

5/10

Exceptional research (provisional, separate)

0/1

No confirmed formal penalty has been applied. Any administrative issues described below are recorded for correction or an instructor decision, not treated as additional deductions.

The proposed exceptional-research point has not been added to the Phase 1 mark; it requires separate verification and approval.

Criterion-by-criterion assessment

Criterion

Proposed score

Maximum

1.1 State of the art

1.5

3

1.2 Datasets and their status

1.5

3

1.3 Solution concept and plan

1

2

1.4 Text quality and references

0.5

1

1.5 Data statement

0.5

1

Core total

5

10

Detailed justifications

1.1 State of the art — 1.5/3. Full-credit standard: At least 15 works, each with method, dataset, and result; quantitative comparison of published values with dataset and split for each value. Finding: A non-empty literature review discusses the reporting-requirements problem and several prior studies, even though only about seven works are discussed substantively and no numerical cross-study SOTA comparison is supplied. These are major omissions preventing full credit, but the review is present; the published full/half/zero scheme supports half credit.

Additional evidence: There is no table of published numbers, and only 7 research works are described (fewer than 8).

1.2 Datasets and their status — 1.5/3. Full-credit standard: For each dataset: size, labels, numeric class balance, licence, acquisition, readiness; collection quantity, date and annotator(s) where applicable. Finding: The licence and acquisition route are given, but there are no READY/TO COLLECT labels, no corpus size, no class balance, and no named annotators.

Details: • No dataset has a READY / TO COLLECT / RESTRICTED label, although the topic card supplies them. Label each one: • EMNLP 2020–2026 Main+Findings PDFs: READY. • Historical policy register: TO COLLECT. • Double-annotated sample (14 pilot + 70 development + 140 held-out papers): TO COLLECT. • LLM evaluator outputs: TO COLLECT. • There is no size. Section 4.1 promises counts “by year and track” but gives none. Give the eligible-paper counts per year and track from the Anthology now. This takes minutes, and it determines your LLM cost (Section 4.4) and the fallback to a probability sample (Section 3). • There is no class balance. You define labels (Compliant / Non-compliant / Not applicable / Uncertain, Section 4.3) but give no expected or pilot distribution per item. Without it, the claim that “kappa alone is unreliable under extreme imbalance” cannot be planned for. At minimum, quote the prevalence of Limitations sections before and after 2022 from Thaepprasit et al. • The TO COLLECT annotation lacks a responsible person. “Two annotators” are not named, and the deadline is only the block “3 Dec.–13 Jan.” in Table 1. State who annotates which batch and by which date. 224 papers × 6 items × 2 annotators is substantial work. • The policy register has no item count (how many editions × documents), no licence and no status. • Good: the acquisition route (ACL Anthology only, November 2026 snapshot, one version per Anthology ID, Docling parser) and the inclusion/exclusion rules in Section 4.1 are precise.

1.3 Solution concept and plan — 1/2. Full-credit standard: One pipeline figure; evaluation metrics chosen in advance; two or three concrete deliverables; weekly task/owner plan. Finding: The metrics are fixed in advance, but there is no pipeline figure, Table 1 has 2–6-week blocks without owners, and the deliverables are not listed.

Details: • There is no pipeline figure. The report has no figure at all. Draw one figure covering: Anthology snapshot → parsing (Docling) → policy register → rubric → rules + LLM evaluator → human double annotation and adjudication → validation → longitudinal estimates. • The plan is not week-by-week and has no owners. Table 1 (p. 2) has four blocks of 2–6 weeks and no person per task. Split it into weeks and assign each task to a named member. Table 3 records who wrote which section of the proposal; it is not a project plan. • The success deliverables are not stated as such. List 2–3 concrete deliverables matching the card (at present they are scattered across Sections 2, 4.3–4.5 and 5): • the versioned policy register and rubric with coding rules; • the adjudicated double-annotated sample with per-item kappa and LLM-vs-human macro-F1; • annual compliance series with 95% intervals and Holm-adjusted before/after tests. • Name the primary metric explicitly. The evaluator metrics (per-item P/R/F1, macro-F1 ≥ 0.80 as a feasibility target) and the estimation metric (resolved-case compliance rate in Section 4.5 with stratified finite-population 95% intervals) are fixed before results, but no single primary metric is named. Choose one per RQ. • Good: the metrics and the statistical design (inverse-inclusion weighting, best/worst-case bounds, Holm adjustment, explicit non-causal framing of the era comparison) are chosen before results and are methodologically careful.

1.4 Text quality and references — 0.5/1. Full-credit standard: Scientific language and defined abbreviations; accurate published-version citations; fewer than one-third preprint-only references. Finding: Only 1/15 references is preprint-only, but there are undefined abbreviations (AI, API, GPU, F1, CC BY, checklist codes C1/B2), a misspelt first-author name, and over-compressed sentences.

Details: • Undefined abbreviations: AI, API, GPU, F1, CC BY, PDF. The checklist codes “C1” and “B2” (Table 2) are not explained, and “EthiCon” (p. 1) is named without saying what it is. • Reference metadata: the first author of the EMNLP 2026 Findings paper is “Thaepprasit” in the ACL Anthology/Crossref record. You write “Thaeprasit”, which is the spelling in the arXiv PDF. • Citation keys render as “ACL Rolling Review, nda” / “ndb” (pp. 2–3). Use “n.d.-a” / “n.d.-b” or give dates. • Several sentences are compressed to the point of being hard to parse; each needs one more clause explaining what is meant: • “nested criteria do not form an independent hypothesis” (p. 1); • “theme papers enter only under the same reporting rules” (p. 2); • “Sparse cells use conservative bounds instead of Wald tests” (p. 4). • The references are otherwise sound. 15 references: 6 peer-reviewed papers, 1 preprint-only (Jinnath & Zhao, arXiv 2608.09280, no published version found), and 8 policy/web documents. Every work that has a published version is cited in that version.

1.5 Data statement — 0.5/1. Full-credit standard: Data source, licence, personal-data status and concrete handling safeguards. Finding: The source and the CC BY 4.0 licence are stated, but the licence for policy documents is vague and personal-data handling is “where feasible”.

Details: • The licence is vague for half of the data. “Policy documents retain source-specific terms” (Section 5) does not state any licence, yet Section 5 says releases will contain “policy provenance” and Section 4.2 archives “policy wording/snapshots”. State the terms of each policy source, or release only URLs, checksums and short quotations. • Personal data is not stated explicitly. Say plainly that the papers contain author names, affiliations and e-mails (personal data). “Removed from evaluator inputs where feasible” is vague: say when it is not feasible, and whether released evidence excerpts and Anthology IDs allow re-identification of authors for “non-compliant” labels. • Add one sentence on sending full texts to a third-party LLM API (which provider, and its terms of use and data retention). • Good: the aggregate-only reporting, the refusal to profile authors or detect AI authorship, and the CC BY 4.0 basis for post-2016 Anthology material are correct and match the topic card.

Strengths, weaknesses, and methodological observations

WHAT DESERVES PRAISE (not scored): Thoughtful separation between a mandatory policy, optional practice and applicability; the paper correctly avoids interpreting pre/post differences as causal.

EXPERT NOTE / RISK (not scored): Praise: principled classification of unknown and inapplicable evidence; no overclaiming policy causality. | Coordinate venue boundaries with the ACL/EACL and NAACL teams so shared rubric items remain comparable.

SCORING CONSISTENCY: Partially completed SOTA must be distinguished from an absent or unverifiable SOTA. The half-credit outcome does not imply that seven works satisfy the full requirement.

Assessment summary: All five conditions of acceptance are met, so the report is accepted for grading. The single most important problem is that Section 2 has no comparison table of published numbers and only seven research works, which is a core-element failure for 1.1 (0/3). The single most important fix is a SOTA table with at least 15 described works, each with its corpus, years, sample size and the reported rate or agreement figure. Second, the corpus and annotation sample need a full dataset card with READY / TO COLLECT labels, sizes and class balance.

Required revisions and priority actions for Phase 2

1)               Build the SOTA comparison table: at least 15 works, each with venue/years, unit, n, method and the published figure (rate, kappa, F1), with the corpus and sample named for every number. Describe each work (what / data / result) in the text, and include Thaepprasit et al.’s figures as your main comparison point (criterion 2.5 requires an extended SOTA table).

2)               Write a dataset card per dataset (EMNLP corpus, policy register, annotated sample, LLM outputs) with a READY / TO COLLECT label, size (eligible papers per year × track, now), label definition, expected or pilot class balance per item, licence and acquisition route. For TO COLLECT items, give counts, dates and named annotators.

3)               Agree and state a disjoint division of work with aguilar_abbadessa_bernard and Leong_Momot_Poltorak_Tkaczyk (Topic 4 has three teams for two slots), approved by the supervisor, and write it into Section 1.

4)               Add one pipeline figure, and replace Table 1 with a week-by-week plan with a named owner per task.

5)               List 2–3 success deliverables explicitly and name the primary metric for each RQ.

6)               Fix the data statement: the licence or redistribution policy for policy documents, an explicit personal-data statement, what “where feasible” means, and LLM-API data handling.

7)               Define all abbreviations at first use, correct “Thaepprasit”, fix the “nda/ndb” citation keys, and expand the over-compressed sentences listed under 1.4.

8)               Phase 2 requires a rebuttal that answers every point of this feedback and names the place (section/table/page) where each was addressed (criterion 2.4).

Further actions raised in the parallel review:

1)               Build a 15-study SOTA table with what/data/numeric results and publication splits; it is the decisive missing Phase 1 component.

2)               Provide corpus sizes by year/track, status labels, sample-size/annotation counts and named individuals responsible for acquisition.

3)               Add the workflow diagram, three verifiable outputs and weekly assignments.

Alignment with the assigned project topic (formative, not an additional Phase 1 deduction)

• Research question: RQ1–RQ3 (p. 1) answer the card’s question directly, restricted to EMNLP 2020–2026. You correctly state that policy and era effects cannot be separated by this design and that a null result is valid. • Deliverables: you plan all three card deliverables (policy/rubric dataset, validated sample with IAA and LLM-vs-human agreement, longitudinal analysis with CIs and tests around breakpoints), but none is listed explicitly (see 1.3). • Data-readiness labels: the card’s READY / TO COLLECT labels are not used (see 1.2). • Out of scope: respected. There is no judging of individual authors, no AI-authorship detection and no quality ranking (Section 5). Table 2 also correctly treats AI-assistance disclosure as descriptive only. • Seed and comparison point: the card names no single seed paper. Magnusson et al. 2023 and Thaepprasit et al. 2026 are the natural comparison points, and both are cited, but neither is compared with numbers. • Over-subscribed topic. Topic 4 allows at most 2 teams, but three submitted: Leong_Momot_Poltorak_Tkaczyk, aguilar_abbadessa_bernard and this team. This report does not mention the other teams and states no division of work. • Reading the three PDFs, the split is by venue only. Your team covers EMNLP 2020–2026; aguilar_abbadessa_bernard covers NAACL with the same longitudinal question and H1, and states it runs “in parallel with teams working on ACL and EMNLP”; Leong_Momot_Poltorak_Tkaczyk covers ACL/EACL 2023–2026, checklist declarations vs evidence, plus automated reproduction. • Your report combines both card roles: (A) longitudinal human-coded compliance and (B) LLM-evaluator reliability. It therefore overlaps with aguilar_abbadessa_bernard on (A) and with Leong_Momot_Poltorak_Tkaczyk on (B). • The card requires disjoint questions, not just disjoint venues. Agree a written division with the other teams and the supervisor, and state it in Section 1. Consider sharing the policy register and rubric so that the EMNLP, NAACL and ACL series are comparable.

Questions to answer in the Phase 2 rebuttal

1.               How will your coding scheme distinguish not-applicable, not-reported and explicitly reported-inadequate cases?

2.               Can teams working on Topic 4 agree on distinct, pre-specified corpus or research-question boundaries while sharing an audit protocol?

Additional methodological validity checks (formative, not scored in Phase 1)

Additional evidence to seek for Phase 2 (not part of the Phase 1 grade): Validate a portable reporting-evidence codebook that handles missing versus inapplicable statements.

Formal completeness and submission issues

The required formal elements were reviewed. Final confirmation remains with the responsible supervisor.

Evidence recorded during the independent review:

• Contribution table: present-complete — Table 3 (p. 4) lists all four members, their tasks and hours (5/4/3/3 h). • LLM-use declaration: present-complete — Section 7 names Claude (literature search, language editing). “NLP course platform assistant” is not a named tool; name the underlying model. • Folder naming: compliant — The folder iwaniuk_borycki_chodan_guzik matches the four authors (Iwaniuk, Borycki, Chodań, Guzik). • Template: compliant — The report uses the course ACL-2015-derived two-column template with the “Project Proposal for NLP Course, Winter 2026/27” header and supervisor block. • Deadline: on time — Committed on 4.11 before midnight CET.

Proposed exceptional-research recognition: 0/1. This optional point is not a deduction and does not change the /10 score; it is awarded only for a completed, verifiable contribution beyond the core rubric.

Suggested literature and bibliographic checks for Phase 2

The entries below are suggestions from an independent bibliographic review. Verify all metadata and the suitability of each source against the original publication before citing it.

1)               Anna Rogers, Timothy Baldwin, Kobi Leins. 2021. “‘Just What do You Think You’re Doing, Dave?’ A Checklist for Responsible Data Use in NLP.” Findings of EMNLP 2021, pp. 4821–4833. https://doi.org/10.18653/v1/2021.findings-emnlp.414. This is the origin of the data/licensing items of the ARR Responsible NLP checklist (your item B2 “Asset licensing”), so the item’s historical definition should be traced to it.

2)               Mohammad Arvan, Luís Pina, Natalie Parde. 2022. “Reproducibility in Computational Linguistics: Is Source Code Enough?” EMNLP 2022, pp. 2350–2361. https://doi.org/10.18653/v1/2022.emnlp-main.150. It measures trends in code availability across ACL venues over time; this is a direct longitudinal comparison point with published numbers for your SOTA table.

3)               Odd Erik Gundersen, Sigbjørn Kjensmo. 2018. “State of the Art: Reproducibility in Artificial Intelligence.” AAAI 2018. https://doi.org/10.1609/aaai.v32i1.11503. This is a paper-level audit of 400 AI papers on fixed documentation variables with trends across years: the closest design precedent for a longitudinal reporting rubric.

4)               Anya Belz, Shubham Agarwal, Anastasia Shimorina, Ehud Reiter. 2021. “A Systematic Review of Reproducibility Research in Natural Language Processing.” EACL 2021, pp. 381–393. https://doi.org/10.18653/v1/2021.eacl-main.29. It frames why the reporting items (compute budget, hyperparameters) matter, and it is the standard review of NLP reproducibility work.

5)               Shaurya Rohatgi, Yanxia Qin, Benjamin Aw, Niranjana Unnithan, Min-Yen Kan. 2023. “The ACL OCL Corpus: Advancing Open Science in Computational Linguistics.” EMNLP 2023, pp. 10348–10361. https://doi.org/10.18653/v1/2023.emnlp-main.640. This is a full-text, structured ACL Anthology corpus that could replace or cross-check your own Docling parsing for 2020–2022 and report parse-failure rates.

For Phase 2, respond point by point to the substantive feedback and questions, indicating whether each item was corrected, rejected with justification, or deferred. Refer to the corresponding section, table, figure, code file or experiment. Additional advice above does not retroactively reduce the Phase 1 core score.

Best regards, Anna Wróblewska




Anna Wróblewska, Ph.D.

Assistant Professor

Faculty of Mathematics and Information Science,

Warsaw University of Technology


mobile +48506631964

---

dr inż. Anna Wróblewska

adiunkt naukowo-dydaktyczny

Wydział Matematyki i Nauk Informacyjnych

Politechnika Warszawska

tel. +48506631964

---

LinkedIn: https://www.linkedin.com/in/awroblewska/
Google Scholar: https://scholar.google.com/citations?user=RdIysMkAAAAJ
ORCID: https://orcid.org/0000-0002-3407-7570