# Speaker script: mid-term video (SOTA + PoC)

Deck: `presentation.html` (PDF: `presentation.pdf`, built with `python html_to_pdf.py`).
Target length: about 10 minutes, roughly 1,300 spoken words. Times per slide are guides; the SOTA
slides (5–7) and the PoC results (10) carry the most weight, so do not rush them.

| # | Slide | Time |
|---|---|---|
| 1 | Title | 0:20 |
| 2 | Problem & research questions | 0:55 |
| 3 | Our approach (pipeline) | 0:55 |
| 4 | Data & rubric | 0:50 |
| 5 | SOTA 1/3: reproducibility audits | 0:55 |
| 6 | SOTA 2/3: ethics, limitations, checklists | 1:05 |
| 7 | SOTA 3/3: methods we reuse | 0:40 |
| 8 | From SOTA to our design | 0:50 |
| 9 | PoC setup | 0:45 |
| 10 | PoC results | 1:05 |
| 11 | PoC insights & limitations | 0:55 |
| 12 | Next steps | 0:35 |
| 13 | Thank you | 0:10 |
| | **Total** | **≈ 10:05** |

---

## Slide 1: Title (0:20)

Hello, we are Michał Iwaniuk, Bartłomiej Borycki, Miłosz Chodań and Mikołaj Guzik, supervised by
Filip Kucia. Our project asks a simple question: do NLP papers actually follow the reporting
requirements that conferences set for them? In this mid-term video we show the state of the art and
our proof of concept.

## Slide 2: Problem & research questions (0:55)

Over the last few years the ACL conferences have kept adding reporting rules. In 2020 authors
started filling in a reproducibility checklist at submission, but those answers were never
published. In 2021 ethics review arrived. In 2022 EMNLP made a dedicated Limitations section
mandatory. From 2023 we have the ACL policy on AI writing assistance and the Responsible NLP
checklist, which EMNLP 2025 even published with the papers.

What nobody checks systematically is whether the published papers actually comply. We study all
EMNLP Main and Findings papers from 2020 to 2026, with three research questions. RQ1: how does
compliance vary by year and by reporting item? RQ2: does adoption go up after a requirement is
introduced? That is our hypothesis H1. RQ3, exploratory: how does reporting after 2023 differ from
before? Because policy changes and the ChatGPT era overlap, we make no causal claims.

Our unit is one paper and one reporting item, and compliance means that an obligation that really
applied in that year is satisfied by evidence in the paper itself.

## Slide 3: Our approach (0:55)

This is our pipeline. We take a snapshot of the ACL Anthology and parse every PDF with PyMuPDF,
keeping page numbers, removing appended checklists and redacting e-mail addresses.

In parallel we build a policy register: we download dated Wayback Machine snapshots of calls for
papers, checklists and ACL policies, so we know what was required in each year, not what the
website says today. From that we define a rubric with six items and four evidence states.

Two automatic evaluators apply the rubric: a regex baseline and one LLM that must quote its evidence
verbatim. Two human annotators label a sample independently, and that is our reference. At the end
we estimate yearly compliance with confidence intervals and compare the years before and after each
mandate.

This gives three deliverables: the versioned register and rubric, a double-annotated sample with
Cohen's kappa and LLM-versus-human macro-F1, and the annual compliance series.

## Slide 4: Data & rubric (0:50)

Our corpus has 16,618 eligible papers: 9,254 Main and 7,364 Findings. The conference grows fast,
from about 1,200 papers in 2020 to over 5,000 in 2026. The policy register currently has 32 dated
source documents and 34 types of requirement.

On the right are our six items. Two are about limitations: is there a dedicated section, and does
it name a specific limitation rather than boilerplate. Then ethical risks, compute budget, asset
licensing and AI assistance. Only the limitation items have a verified mandate from 2022; compute
and licensing are checklist practices, and AI assistance is descriptive only.

Each item gets one of four evidence states, and compliance is derived from them. The key rule: a
paper can only be non-compliant if a verified obligation applied to it in that year.

## Slide 5: SOTA 1/3, reproducibility audits (0:55)

We grouped the literature into three themes. The first is reproducibility audits.

Gundersen and Kjensmo manually surveyed 400 AAAI and IJCAI papers: no paper documented everything
needed for reproduction, and only about a quarter of the variables were reported. Dodge et al.
audited 50 random EMNLP 2018 papers: splits were reported in 92 percent, but search bounds in only
8 percent. Their checklist became the NLP Reproducibility Checklist.

Belz et al. reviewed reproduction studies in NLP: only 14 percent of 513 scores were reproduced
exactly. Arvan et al. show that code sharing grows at venues that push for it, but only 2 of 8
EMNLP 2021 papers with code ran without problems. Finally, Magnusson et al. analysed over 10,000
checklist responses: reporting rose after the checklist and then stagnated. But these are
self-reports, which likely overestimate.

## Slide 6: SOTA 2/3, ethics, limitations, checklists (1:05)

The second theme is closest to us: audits of the content of ethics and limitations sections.

Benotti and Blackburn read all ethics sections from ACL 2021. Only 15.7 percent of papers had one,
and a fifth of those were pure disclaimers. Karamolegkou et al. built EthiCon, 1,580 ethics
statements with human agreement of kappa 0.77. Two thirds contain disclaimers, and open LLMs could
extract concerns but struggled with negation.

Our main reference point is Thaepprasit et al. at EMNLP 2026. They analysed over 16,000
Limitations sections with a Gemini-based coder and humans in the loop. Adoption jumped from under
10 percent before the mandate to 97.8 percent at EMNLP 2022 and 100 percent by 2025. Importantly,
of 136 papers flagged as missing the section, 41 were parser failures. Their LLM coder reached
F1 0.80, with agreement on par with humans.

Finally, Jinnath and Zhao, a preprint, analysed the public EMNLP 2025 checklists: almost 45
percent of "No" answers have a brief or empty justification, and more than half of authors dismiss
potential risks.

## Slide 7: SOTA 3/3, methods we reuse (0:40)

The third theme is methods and resources we build on. Rogers et al. is a position paper that
proposed a responsible data-use checklist. It is the origin of the licensing questions in the ARR
checklist, and it defines our licensing item.

Xiao et al. showed that GPT-3 with an expert codebook reaches moderate to substantial agreement with
experts, and that codebook-style prompts with at least one example work best. That is how our
prompt is built. Rohatgi et al. released the ACL OCL corpus, which we can use to cross-check our
parsing for 2020 to 2022.

## Slide 8: From SOTA to our design (0:50)

What do we take from this? First, presence is not content: sections and checklist answers are often
disclaimers, so we separate structural items from substantive ones. Second, self-reports
overestimate, so we audit the paper text and quote evidence. Third, mandates change structure
quickly, so H1 is testable on fixed indicators. Fourth, LLM coding works, but only if it is
validated, so we use double human annotation on a held-out set. Fifth, parsers fail silently, so
parse failures become "uncertain", never "non-compliant". And obligations change every year, which
is why we need the dated register.

The gap: prior work audits one item, or relies on self-reports. We audit several items in the paper
text, against the rules that were valid in each year.

## Slide 9: PoC setup (0:45)

For the proof of concept we drew a pilot of 14 papers: one Main and one Findings paper per year,
with a fixed random seed. That is 84 paper-item pairs.

We ran two evaluators with the same rubric. The baseline is pure regular expressions: it looks for
headings like "Limitations" or "Ethics Statement", for GPU-hours, licence names and AI-tool
mentions. Run 1 of the LLM evaluator is Gemini 2.5 Flash at temperature zero. It reads the full
paper and returns, for every item, the evidence status, a verbatim quote, the location and a short
justification. We then check that every quote really occurs in the text. Both runs are archived
with their exact configuration.

## Slide 10: PoC results (1:05)

Here are the results. The bars show how many of the 14 papers each evaluator rated as adequately
reporting an item: orange is the rule baseline, blue is Gemini.

On the Limitations section, where there is a clear heading, both agree. For everything that is not
signalled by a heading, the LLM finds more: specific limitations, ethical risks, compute budgets
and licences.

Overall, the two evaluators assign the same evidence status in two thirds of cases, 56 out of 84.
And 83 of the 84 LLM quotes were found verbatim in the paper, so the LLM is not inventing
evidence.

The table on the right shows that every one of the 28 disagreements goes the same way: the rules say
"not reported", and the LLM finds evidence or decides the item does not apply. This is agreement
between two machines, not accuracy. Which one is right will be decided by the human labels.

## Slide 11: PoC insights & limitations (0:55)

Some observations, which are purely descriptive with 14 papers. The mandate is visible even here:
none of the four papers from 2020 and 2021 has a Limitations section, while all ten from 2022
onwards do. The LLM finds evidence outside headings, for example "four V100 GPUs" and the training
time in a 2021 paper, and it correctly marks a position paper as not applicable for compute. Nine
of 14 papers mention reused assets without naming a licence, and only one discloses AI assistance.

The LLM run is cheap: about 8 cents for the pilot, roughly 95 dollars for the full corpus, or half
that with the batch API.

The limitations are clear. We have no human reference yet. Fourteen papers allow no statistics. The
rubric is not frozen. Compute, licensing and AI assistance have no verified mandate yet, so we only
track their presence. And so far we have one model, one run, with no repeats.

## Slide 12: Next steps (0:35)

Next, by Phase 2 we finish the double annotation of the pilot, compute kappa and compare both
evaluators with humans, and revise the rubric. Then we tune the prompt only on 70 development
papers and freeze everything. The frozen evaluator is validated on 140 held-out papers with
per-item precision, recall and F1, and finally run on all 16,618 papers to produce yearly trends
with confidence intervals. In Phase 2 we also address the proposal feedback: dataset cards, the
extended SOTA table, a weekly plan, and an agreed split of work with the NAACL and ACL teams.

## Slide 13: Thank you (0:10)

To sum up: a dated register of rules, a six-item rubric, and an LLM evaluator that we validate
against humans. Thank you, and we look forward to your questions.

---

## Fact sheet (sources for every number on the slides)

- Corpus counts: `data/manifest/counts_by_year_track.json`. Register: `config/policy_register/documents.csv` (32 rows), `requirement_dictionary.csv` (34 rows).
- PoC numbers: `runs/2026-11-15_pilot_14_rule-baseline-v1_rubric-v1.0.0/evaluations.csv`, `runs/2026-11-15_pilot_14_gemini-2.5-flash_rubric-v1.0.0/evaluations.csv`, `results/pilot_14/summary_report.json` (cost and token estimates).
- SOTA figures were checked against the full papers:
  - Gundersen & Kjensmo 2018: abstract, Survey and Results sections, Tables 2–3 (R1D/R2D/R3D = 0.24/0.25/0.26; only R1D improves significantly).
  - Dodge et al. 2019: §5 "EMNLP 2018 checklist coverage" and appendix Table 1 of the arXiv version (92/74/30/24/18/14/14/10/10/8%).
  - Belz et al. 2021: §3 (35 Anthology + 25 other papers; 34 paper pairs; 77/513 = 14.03% identical; 59.2% of the rest worse).
  - Arvan et al. 2022: §4–5 (723 of 1,300+ EMNLP 2021 papers with code; 2 of 8 reproduced; trend shown in Figure 1 only).
  - Magnusson et al. 2023: abstract, §3, §7 (10,405 responses; 8 of 10 items up vs. EMNLP 2018; 46% open code, +8% reproducibility score).
  - Benotti & Blackburn 2022: §3 (90/572 = 15.7%; ACL 2022 23.3%; 74/52/23%; 20% disclaimers; reviewed vs. not: harms .69 vs .43).
  - Karamolegkou et al. 2025: §3–4, Table 1 (1,580 of 8,048; κ 0.77; 67.18% disclaimers, 40.36% concerns; BERTScore-F1 0.81–0.83).
  - Thaepprasit et al. 2026: §3.4, Table 2, §4.1, Table 3, Figure 2 (F1 0.801, α 0.647 vs 0.644; 97.8% EMNLP 2022, 100% EMNLP 2025; 41/50/45 of 136).
  - Jinnath & Zhao 2026 (arXiv 2608.09280): abstract, §5 (44.9% brief or empty "No" justifications; 53% dismiss risks). Note: the abstract gives 6% of checklists with contradictions while §5.4 reports 15.5% of main-track papers with at least one; the slide therefore says only that contradictions are common.
  - Rogers et al. 2021: §2 and §4, Figure 2 (position paper, no empirical figures).
  - Xiao et al. 2023: §4, Figure 1 (κ 0.61 / 0.38; experts 0.88 / 0.90).
  - Rohatgi et al. 2023: §3–4 (73,285 papers to Sept 2022; 210K figures; GROBID; manual check of 21 documents).
