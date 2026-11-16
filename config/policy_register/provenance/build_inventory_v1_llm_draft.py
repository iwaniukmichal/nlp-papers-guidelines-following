"""Provenance record: the script that produced the first, LLM-drafted version of inventory.csv and
requirement_dictionary.csv (2026-11-15). Kept for auditability only. After human verification starts,
inventory.csv is the source of truth and is edited directly; do NOT re-run this script (it would overwrite
verification work).
"""
import csv
from emnlp_audit.policy import inventory as inv

CODER = "claude-opus-5-5 (LLM draft)"

DICTIONARY = [
    ("LIMITATIONS_SECTION", "limitations", 'A dedicated section titled "Limitations" (structure and placement)', "", ""),
    ("LIMITATIONS_DISCUSSION", "limitations", "Discussion of the limitations of the work (content; anywhere in the paper)", "A1", ""),
    ("RISKS", "responsible_research", "Discussion of potential risks or negative societal impact of the work", "A2", ""),
    ("ETHICS_DISCUSSION", "responsible_research", "Explicit discussion of ethical issues raised by the paper (ethics / broader impact statement)", "", ""),
    ("CLAIMS_SUMMARY", "claims", "Abstract and introduction summarize the paper's main claims", "A3", ""),
    ("ARTIFACT_CITATION", "data_model_documentation", "Creators of used artifacts (code, data, models) are cited", "B1", ""),
    ("ARTIFACT_LICENSE", "data_model_documentation", "License or terms of use / distribution of artifacts are discussed", "B2", ""),
    ("ARTIFACT_INTENDED_USE", "data_model_documentation", "Use of existing artifacts is consistent with their intended use; intended use of created artifacts is specified", "B3", ""),
    ("DATA_PII_OFFENSIVE", "data_model_documentation", "Steps to check data for personal identifiers or offensive content and to protect / anonymize it", "B4", ""),
    ("ARTIFACT_DOCUMENTATION", "data_model_documentation", "Documentation of artifacts: domains, languages, linguistic phenomena, demographic groups", "B5", ""),
    ("DATA_STATISTICS", "data_model_documentation", "Dataset statistics such as number of examples and train / validation / test splits", "B6", "Relevant statistics such as number of examples; Details of train/validation/test splits"),
    ("DATA_PREPROCESSING", "reproducibility", "Excluded data and pre-processing steps", "C2 (guidance)", "Explanation of any data that were excluded, and all pre-processing steps"),
    ("DATA_AVAILABILITY", "reproducibility", "Downloadable version (link or archive) of the data", "", "A link to a downloadable version of the data"),
    ("DATA_COLLECTION_DESCRIPTION", "human_participants", "Description of the collection process for new data (e.g. annotator instructions, quality control)", "", "For new data collected, a complete description of the data collection process"),
    ("METHOD_DESCRIPTION", "reproducibility", "Clear description of the mathematical setting / algorithm / model", "", "A clear description of the mathematical setting, algorithm, and/or model"),
    ("CODE_AVAILABILITY", "reproducibility", "Source code (link or archive) with dependencies", "", "A link to a downloadable source code, with specification of all dependencies"),
    ("COMPUTE_INFRASTRUCTURE", "reproducibility", "Description of the computing infrastructure used", "C1", "Description of computing infrastructure used"),
    ("COMPUTE_BUDGET", "reproducibility", "Runtime / total computational budget (e.g. GPU hours) or energy cost", "C1", "Average runtime for each approach"),
    ("MODEL_PARAMETERS", "reproducibility", "Number of parameters of the models used", "C1", "Number of parameters in each model"),
    ("VALIDATION_PERFORMANCE", "reproducibility", "Validation performance corresponding to each reported test result", "", "Corresponding validation performance for each reported test result"),
    ("EVALUATION_METRICS", "reproducibility", "Explanation of evaluation metrics (with code)", "", "Explanation of evaluation metrics used, with links to code"),
    ("HYPERPARAMETERS", "reproducibility", "Experimental setup incl. hyperparameter search (bounds, trials, selection method) and best values", "C2", "Bounds; best configurations; number of trials; selection method"),
    ("RESULT_STATISTICS", "reproducibility", "Descriptive statistics of results (number of runs; mean, variance, error bars; max vs mean vs single run)", "C3", "Expected validation performance (mean and variance over hyperparameter trials)"),
    ("SOFTWARE_PACKAGES", "reproducibility", "Implementation, model and parameter settings of existing packages used (e.g. NLTK, ROUGE)", "C4", ""),
    ("ANNOTATOR_INSTRUCTIONS", "human_participants", "Full text of instructions given to participants / annotators", "D1", ""),
    ("PARTICIPANT_RECRUITMENT_PAY", "human_participants", "How participants were recruited and paid, and whether pay is adequate", "D2", ""),
    ("CONSENT", "human_participants", "Whether and how consent was obtained from people whose data is used", "D3", ""),
    ("ETHICS_REVIEW_BOARD", "human_participants", "Approval (or exemption) of the data collection protocol by an ethics review board (IRB)", "D4", ""),
    ("ANNOTATOR_DEMOGRAPHICS", "human_participants", "Basic demographic and geographic characteristics of the annotators", "D5", ""),
    ("AI_ASSISTANCE_CHECKLIST", "ai_tools", "Disclosure of the use of AI assistants in the submission checklist", "E1", ""),
    ("AI_DISCLOSURE_IN_PAPER", "ai_tools", "Disclosure of the use and scope of AI writing / coding assistance in the paper itself (e.g. Acknowledgements)", "", ""),
]

DOCS_BY_YEAR = {
    2019: ["EMNLP2019-CFP"],
    2020: ["EMNLP2020-CFP", "EMNLP2020-REPRO-BLOG", "EMNLP2020-SUBMISSION-FAQ", "EMNLP2020-CAMERA"],
    2021: ["EMNLP2021-CFP", "EMNLP2021-ETHICS-FAQ", "EMNLP2021-SUBMISSION-FAQ", "EMNLP2021-ARR-PILOT", "EMNLP2021-CAMERA", "ACL-CODE-ETHICS-2021"],
    2022: ["EMNLP2022-CFP", "EMNLP2022-ETHICS-FAQ", "ARR-CFP-2022", "ARR-RNLP-2022"],
    2023: ["EMNLP2023-CFP", "ARR-CFP-2023", "ARR-RNLP-2023", "ACL2023-AI-POLICY"],
    2024: ["EMNLP2024-CFP", "ARR-CFP-2024", "ARR-RNLP-2024"],
    2025: ["EMNLP2025-CFP", "ARR-CFP-2025", "ARR-RNLP-2025"],
    2026: ["EMNLP2026-CFP", "ARR-CFP-2026", "ARR-RNLP-2026"],
}
TRACKS = {2019: "main", 2020: "main+findings", 2021: "main+findings"}  # 2022+: all_submissions

rows = []


def add(req, year, doc, quote, status, where="paper", condition="", route="all", location="", notes=""):
    rows.append({
        "req_id": req, "year": year, "doc_id": doc, "quote": quote, "location": location,
        "where_reported": where, "status": status, "condition": condition, "route": route,
        "tracks": TRACKS.get(year, "all_submissions"), "coded_by": CODER, "verified_by": "",
        "verification": "pending", "notes": notes,
    })


# ---------------------------------------------------------------- 2019 (pre-2020 baseline)
for req in ("CODE_AVAILABILITY", "DATA_AVAILABILITY"):
    add(req, 2019, "EMNLP2019-CFP", "EMNLP-IJCNLP 2019 encourages the submission of these supplementary materials to improve the reproducibility of results",
        "recommended", where="supplementary", location="Optional Supplementary Materials",
        notes="Optional software/data archives; no reproducibility checklist and no ethics policy in the 2019 CFP.")

# ---------------------------------------------------------------- 2020
REPRO_2020_NOTE = ("CFP: authors must answer the checklist at submission but 'are not required to meet all criteria'; "
                   "EMNLP2020-REPRO-BLOG: the PC 'does not require that any items on the checklist be included in the paper'.")
repro_2020 = [
    ("METHOD_DESCRIPTION", "A clear description of the mathematical setting, algorithm, and/or model."),
    ("CODE_AVAILABILITY", "A link to a downloadable source code, with specification of all dependencies, including external libraries"),
    ("COMPUTE_INFRASTRUCTURE", "Description of computing infrastructure used"),
    ("COMPUTE_BUDGET", "Average runtime for each approach"),
    ("MODEL_PARAMETERS", "Number of parameters in each model"),
    ("VALIDATION_PERFORMANCE", "Corresponding validation performance for each reported test result"),
    ("EVALUATION_METRICS", "Explanation of evaluation metrics used, with links to code"),
    ("HYPERPARAMETERS", "Bounds for each hyperparameter"),
    ("HYPERPARAMETERS", "Hyperparameter configurations for best-performing models"),
    ("RESULT_STATISTICS", "Expected validation performance, as introduced in Section 3.1 in * Dodge et al, 2019 , or another measure of the mean and variance as a function of the number of hyperparameter trials."),
    ("DATA_STATISTICS", "Relevant statistics such as number of examples"),
    ("DATA_STATISTICS", "Details of train/validation/test splits"),
    ("DATA_PREPROCESSING", "Explanation of any data that were excluded, and all pre-processing steps"),
    ("DATA_AVAILABILITY", "A link to a downloadable version of the data"),
    ("DATA_COLLECTION_DESCRIPTION", "For new data collected, a complete description of the data collection process, such as instructions to annotators and methods for quality control."),
]
for req, q in repro_2020:
    add(req, 2020, "EMNLP2020-CFP", q, "checklist_question", where="checklist", location="NEW: Reproducibility Criteria", notes=REPRO_2020_NOTE)
add("ETHICS_DISCUSSION", 2020, "EMNLP2020-CFP",
    "Where a paper may raise ethical issues, we ask that you include in the paper an explicit discussion of these issues, which will be taken into account in the review process.",
    "conditional_mandatory", condition="paper may raise ethical issues", location="NEW: Ethics Policy",
    notes="'we ask' alone would be 'recommended'; the same paragraph states a sanction ('We reserve the right to reject papers on ethical grounds ... inadequately addressed legitimate ethical concerns').")

# ---------------------------------------------------------------- 2021
REPRO_2021_NOTE = ("CFP: authors 'will be asked to answer the questions from the Reproducibility Checklist'; "
                   "'The papers are not required to meet all reproducibility criteria listed.'")
repro_2021 = [
    ("METHOD_DESCRIPTION", "A clear description of the mathematical setting, algorithm, and/or model."),
    ("CODE_AVAILABILITY", "Submission of a zip file containing source code, with specification of all dependencies, including external libraries, or a link to such resources"),
    ("COMPUTE_INFRASTRUCTURE", "Description of computing infrastructure used"),
    ("COMPUTE_BUDGET", "The average runtime for each model or algorithm (e.g., training, inference, etc.), or estimated energy cost"),
    ("MODEL_PARAMETERS", "Number of parameters in each model"),
    ("VALIDATION_PERFORMANCE", "Corresponding validation performance for each reported test result"),
    ("EVALUATION_METRICS", "Explanation of evaluation metrics used, with links to code"),
    ("HYPERPARAMETERS", "Bounds for each hyperparameter"),
    ("HYPERPARAMETERS", "Hyperparameter configurations for best-performing models"),
    ("RESULT_STATISTICS", "Summary statistics of the results (e.g., mean, variance, error bars, etc.)"),
    ("RESULT_STATISTICS", "The exact number of training and evaluation runs"),
    ("DATA_STATISTICS", "Relevant details such as languages, and number of examples and label distributions"),
    ("DATA_STATISTICS", "Details of train/validation/test splits"),
    ("DATA_PREPROCESSING", "Explanation of any data that were excluded, and all pre-processing steps"),
    ("DATA_AVAILABILITY", "A zip file containing data or link to a downloadable version of the data"),
    ("DATA_COLLECTION_DESCRIPTION", "For new data collected, a complete description of the data collection process, such as instructions to annotators and methods for quality control."),
]
for req, q in repro_2021:
    add(req, 2021, "EMNLP2021-CFP", q, "checklist_question", where="checklist", location="Reproducibility Criteria", route="direct", notes=REPRO_2021_NOTE)
add("ETHICS_DISCUSSION", 2021, "EMNLP2021-CFP",
    "Note that an ethical considerations section is not required, but papers working with sensitive data or on sensitive tasks that do not discuss these issues will not be accepted.",
    "conditional_mandatory", condition="sensitive data or sensitive tasks", route="direct", location="Ethics Policy",
    notes="Extra space after page 8 (4) allowed for a broader impact statement or other discussion of ethics.")
add("ETHICS_DISCUSSION", 2021, "EMNLP2021-ETHICS-FAQ",
    "Papers that report on research which raises ethical issues that do not discuss such issues are likely to be rejected on ethical grounds.",
    "conditional_mandatory", condition="research raises ethical issues", route="direct",
    location="Should I have an 'ethical considerations' section in my paper?", notes="FAQ answers 'Yes.' and 'we strongly encourage you to use it'.")
add("DATA_COLLECTION_DESCRIPTION", 2021, "EMNLP2021-ETHICS-FAQ", "Detail the dataset collection process and conditions.",
    "recommended", condition="paper presents a new dataset", route="direct", location="What should I be aware of if my paper presents a new dataset?")
add("PARTICIPANT_RECRUITMENT_PAY", 2021, "EMNLP2021-ETHICS-FAQ",
    "If manual work was involved, describe measures taken to ensure that crowd workers or other annotators were treated fairly.",
    "recommended", condition="new dataset with manual work", route="direct", location="What should I be aware of if my paper presents a new dataset?",
    notes="Includes 'compensating them fairly'.")
add("CONSENT", 2021, "EMNLP2021-ETHICS-FAQ", "compensating them fairly and ensuring that they were able to give informed consent",
    "recommended", condition="new dataset with manual work", route="direct", location="What should I be aware of if my paper presents a new dataset?")
add("ETHICS_REVIEW_BOARD", 2021, "EMNLP2021-ETHICS-FAQ", "Please indicate if your project was approved by an IRB (institutional review board).",
    "recommended", condition="paper presents a new dataset", route="direct", location="What should I be aware of if my paper presents a new dataset?")
add("COMPUTE_BUDGET", 2021, "EMNLP2021-ETHICS-FAQ",
    "We encourage authors to use tools such as Henderson et al’s (2020) experiment impact tracker or other available information to estimate the energy requirement of the experiments reported in the paper",
    "recommended", condition="experiments with lots of compute", route="direct", location="... if my paper reports on experiments that involve lots of compute time/power?")

# ---------------------------------------------------------------- 2022 and 2023 (two routes)
REVIEWER_NOTE = ("Direct submissions: 'Reviewers will be asked to assess the reproducibility of the work as part of their reviews.' "
                 "No author checklist is mentioned in the CFP.")
repro_2223 = [
    ("METHOD_DESCRIPTION", "A clear description of the mathematical setting, algorithm, and/or model"),
    ("CODE_AVAILABILITY", "Submission of a zip file containing source code, with specification of all dependencies, including external libraries, or a link to such resources"),
    ("COMPUTE_INFRASTRUCTURE", "Description of computing infrastructure used"),
    ("COMPUTE_BUDGET", "The average runtime for each model or algorithm (e.g., training, inference, etc.), or estimated energy cost"),
    ("MODEL_PARAMETERS", "Number of parameters in each model"),
    ("VALIDATION_PERFORMANCE", "Corresponding validation performance for each reported test result"),
    ("EVALUATION_METRICS", "Explanation of evaluation metrics used, with links to code"),
    ("HYPERPARAMETERS", "Bounds for each hyperparameter"),
    ("RESULT_STATISTICS", "Summary statistics of the results (e.g., mean, variance, error bars, etc.)"),
    ("DATA_STATISTICS", "Relevant details such as languages, and number of examples and label distributions"),
    ("DATA_PREPROCESSING", "Explanation of any data that were excluded, and all pre-processing steps"),
    ("DATA_AVAILABILITY", "A zip file containing data or link to a downloadable version of the data"),
    ("DATA_COLLECTION_DESCRIPTION", "For new data collected, a complete description of the data collection process, such as instructions to annotators and methods for quality control."),
]
RNLP_HEADERS = {
    "LIMITATIONS_DISCUSSION": "A1. Did you describe the limitations of your work?",
    "RISKS": "A2. Did you discuss any potential risks of your work?",
    "CLAIMS_SUMMARY": "A3. Do the abstract and introduction summarize the paper’s main claims?",
    "ARTIFACT_CITATION": "B1. Did you cite the creators of artifacts you used?",
    "ARTIFACT_LICENSE": "B2. Did you discuss the license or terms for use and / or distribution of any artifacts?",
    "ARTIFACT_INTENDED_USE": "B3. Did you discuss if your use of existing artifact(s) was consistent with their intended use",
    "DATA_PII_OFFENSIVE": "B4. Did you discuss the steps taken to check whether the data that was collected / used contains any information that names or uniquely identifies individual people or offensive content",
    "ARTIFACT_DOCUMENTATION": "B5. Did you provide documentation of the artifacts, e.g., coverage of domains, languages, and linguistic phenomena, demographic groups represented, etc.?",
    "DATA_STATISTICS": "B6. Did you report relevant statistics like the number of examples, details of train / test / dev splits, etc. for the data that you used / created?",
    "MODEL_PARAMETERS": "C1. Did you report the number of parameters in the models used, the total computational budget (e.g., GPU hours), and computing infrastructure used?",
    "COMPUTE_BUDGET": "C1. Did you report the number of parameters in the models used, the total computational budget (e.g., GPU hours), and computing infrastructure used?",
    "COMPUTE_INFRASTRUCTURE": "C1. Did you report the number of parameters in the models used, the total computational budget (e.g., GPU hours), and computing infrastructure used?",
    "HYPERPARAMETERS": "C2. Did you discuss the experimental setup, including hyperparameter search and best-found hyperparameter values?",
    "DATA_PREPROCESSING": "how data was preprocessed",
    "RESULT_STATISTICS": "C3. Did you report descriptive statistics about your results (e.g., error bars around results, summary statistics from sets of experiments), and is it transparent whether you are reporting the max, mean, etc. or just a single run?",
    "ANNOTATOR_INSTRUCTIONS": "D1. Did you report the full text of instructions given to participants, including e.g., screenshots, disclaimers of any risks to participants or annotators, etc.?",
    "PARTICIPANT_RECRUITMENT_PAY": "D2. Did you report information about how you recruited (e.g., crowdsourcing platform, students) and paid participants",
    "CONSENT": "D3. Did you discuss whether and how consent was obtained from people whose data you’re using/curating?",
    "ETHICS_REVIEW_BOARD": "D4. Was the data collection protocol approved (or determined exempt) by an ethics review board?",
    "ANNOTATOR_DEMOGRAPHICS": "D5. Did you report the basic demographic and geographic characteristics of the annotator population that is the source of the data?",
}
SOFTWARE_OLD = "C4. If you used existing packages (e.g., for preprocessing, for normalization, or for evaluation), did you report the implementation, model, and parameter settings used (e.g., NLTK, Spacy, ROUGE, etc.)?"
SOFTWARE_NEW = "C4. If you used existing packages (e.g., for preprocessing, for normalization, or for evaluation, such as NLTK, Spacy, ROUGE, etc.), did you report the implementation, model, and parameter settings used?"
RNLP_NOTES = {
    2022: "Checklist answers with section references or a justification for 'No'; reviewers use it as one factor.",
    2023: "'it is perfectly acceptable that it does not, provided a proper justification is given'.",
    2024: "Completed in the submission form from Feb 2024; justified 'No' acceptable.",
    2025: "Justified 'No' acceptable; ARR CFP: desk rejection for incorrect or misleading filing of the checklist from Dec 2024.",
    2026: "Justified 'No' acceptable; 'Submissions that systematically fail to provide either specific relevant sections or justification ... will be desk-rejected.'",
}


def add_rnlp(year, route):
    doc = f"ARR-RNLP-{year}"
    for req, q in RNLP_HEADERS.items():
        if req == "CLAIMS_SUMMARY" and year >= 2025:
            continue
        loc = "C2 guidance" if req == "DATA_PREPROCESSING" else q.split(".")[0]
        add(req, year, doc, q, "checklist_question", where="checklist", route=route, location=loc, notes=RNLP_NOTES[year])
    add("SOFTWARE_PACKAGES", year, doc, SOFTWARE_OLD if year <= 2024 else SOFTWARE_NEW, "checklist_question",
        where="checklist", route=route, location="C4", notes=RNLP_NOTES[year])


for year in (2022, 2023):
    cfp = f"EMNLP{year}-CFP"
    for req, q in repro_2223:
        add(req, year, cfp, q, "reviewer_criterion", where="unspecified", route="direct", location="Reproducibility Criteria", notes=REVIEWER_NOTE)
    add("LIMITATIONS_SECTION", year, cfp, "Papers without a limitation section will be automatically rejected without review.",
        "mandatory_in_paper", location="Mandatory Discussion of Limitations",
        notes="Applies to ARR-committed papers too: they must add the section if missing ('with the exception of adding the required \"limitations\" section').")
    add("LIMITATIONS_DISCUSSION", year, cfp,
        f"EMNLP {year} requires all papers to have a clear discussion of limitations, in a dedicated section titled “Limitations”.",
        "mandatory_in_paper", location="Mandatory Discussion of Limitations",
        notes="Placement: 'at the end of the paper, after the discussion/conclusions section and before the references'; does not count towards the page limit.")
    add("ETHICS_DISCUSSION", year, cfp,
        "Note that an ethical considerations section is not required, but papers working with sensitive data or on sensitive tasks that do not discuss these issues will not be accepted.",
        "conditional_mandatory", condition="sensitive data or sensitive tasks", location="Ethics Policy")
    add_rnlp(year, "arr")
    for req in ("CODE_AVAILABILITY", "DATA_AVAILABILITY"):
        add(req, year, cfp, f"EMNLP {year} encourages the submission of these supplementary materials to improve the reproducibility of results",
            "recommended", where="supplementary", location="Optional Supplementary Materials")

add("DATA_COLLECTION_DESCRIPTION", 2022, "EMNLP2022-ETHICS-FAQ", "Detail the dataset collection process and conditions.",
    "recommended", condition="paper presents a new dataset", location="Ethics FAQ: new dataset")
add("PARTICIPANT_RECRUITMENT_PAY", 2022, "EMNLP2022-ETHICS-FAQ",
    "describe measures taken to ensure that crowd workers or other annotators were fairly compensated and how fair compensation was determined.",
    "recommended", condition="new dataset with manual work", location="Ethics FAQ: new dataset")
add("ETHICS_REVIEW_BOARD", 2022, "EMNLP2022-ETHICS-FAQ", "Please indicate if your project was approved by an IRB (institutional review board).",
    "recommended", condition="paper presents a new dataset", location="Ethics FAQ: new dataset")
add("ETHICS_DISCUSSION", 2022, "ARR-CFP-2022",
    "We reserve the right to reject papers on ethical grounds, where the authors are judged to have operated counter to the code of ethics, or have inadequately addressed legitimate ethical concerns with their work.",
    "conditional_mandatory", condition="legitimate ethical concerns", route="arr", location="Ethics Policy",
    notes="Same paragraph: 'Authors are encouraged to devote a section of their paper to concerns of the ethical impact of the work'.")
add("LIMITATIONS_SECTION", 2023, "ARR-CFP-2023",
    "We encourage authors to discuss the limitations of their work in a dedicated section titled “Limitations”.",
    "recommended", route="arr", location="Limitations", notes="Superseded for EMNLP 2023 by the EMNLP CFP, which requires the section for all papers including ARR commitments.")
add("ETHICS_DISCUSSION", 2023, "ARR-CFP-2023",
    "We reserve the right to reject papers on ethical grounds, where the authors are judged to have operated counter to the code of ethics, or have inadequately addressed legitimate ethical concerns with their work.",
    "conditional_mandatory", condition="legitimate ethical concerns", route="arr", location="Ethics Policy")
for req in ("CODE_AVAILABILITY", "DATA_AVAILABILITY"):
    add(req, 2022, "ARR-CFP-2022", "ARR encourages the submission of these supplementary materials to improve the reproducibility of results",
        "recommended", where="supplementary", route="arr", location="Optional Supplementary Materials")
    add(req, 2023, "ARR-CFP-2023", "ARR encourages the submission of these supplementary materials to improve the reproducibility of results",
        "recommended", where="supplementary", route="arr", location="Optional Supplementary Materials")
AI_2023_NOTE = ("The ACL 2023 policy adds a checklist question for ACL 2023; the ARR checklist page captured before the EMNLP 2023 deadline "
                "(ARR-RNLP-2023, 2023-06-01) has no such question and the EMNLP 2023 CFP does not mention AI assistance.")
add("AI_ASSISTANCE_CHECKLIST", 2023, "ACL2023-AI-POLICY",
    "ACL 2023 expands the mandatory Responsible NLP Checklist developed at NAACL 2022 by one more question concerning the use of writing assistants.",
    "unverified", where="checklist", condition="AI writing assistants were used", notes=AI_2023_NOTE)
add("AI_DISCLOSURE_IN_PAPER", 2023, "ACL2023-AI-POLICY", "They should specify where such text was used",
    "unverified", condition="low-novelty generated text", notes=AI_2023_NOTE)

# ---------------------------------------------------------------- 2024-2026 (ARR only)
for year in (2024, 2025, 2026):
    cfp = f"ARR-CFP-{year}"
    add("LIMITATIONS_SECTION", year, cfp, "Papers without a limitations section will be desk rejected.", "mandatory_in_paper",
        location="Limitations (required section)", notes="EMNLP CFP lists 'Limitations' among the ARR submission requirements to follow.")
    add("LIMITATIONS_DISCUSSION", year, cfp, "Authors are required to discuss the limitations of their work in a dedicated section titled “Limitations”.",
        "mandatory_in_paper", location="Limitations (required section)")
    if year >= 2025:
        add("LIMITATIONS_SECTION", year, cfp, "We reserve the right to desk reject the submissions that use this section to introduce more content that should have been part of the main paper.",
            "mandatory_in_paper", location="Limitations (required section)", notes="Content restriction: no new methods, analysis or results.")
    add("ETHICS_DISCUSSION", year, cfp,
        "We reserve the right to reject papers on ethical grounds, where the authors are judged to have operated counter to the code of ethics, or have inadequately addressed legitimate ethical concerns with their work.",
        "conditional_mandatory", condition="legitimate ethical concerns", location="Ethics Policy",
        notes="Same paragraph: 'Authors are encouraged to devote a section of their paper to concerns about the ethical impact of the work'.")
    for req in ("CODE_AVAILABILITY", "DATA_AVAILABILITY"):
        add(req, year, cfp, "ARR encourages the submission of these supplementary materials to improve the reproducibility of results",
            "recommended", where="supplementary", location="Optional Supplementary Materials")
    add_rnlp(year, "all")

add("AI_ASSISTANCE_CHECKLIST", 2024, "ARR-RNLP-2024", "E1. Did you include information about your use of AI assistants?", "checklist_question",
    where="checklist", location="E1", notes=RNLP_NOTES[2024])
add("AI_ASSISTANCE_CHECKLIST", 2024, "ARR-CFP-2024",
    "The policy introduces a new item in the responsible research checklist, where authors disclose use of AI assistance.",
    "checklist_question", where="checklist", condition="AI assistance beyond language polishing / short-form input", location="AI Writing Assistance Policy")
add("AI_DISCLOSURE_IN_PAPER", 2024, "ARR-CFP-2024", "Specify where such text was used",
    "unverified", condition="low-novelty generated text", location="AI Writing Assistance Policy",
    notes="Disclosure is routed through the checklist item; the CFP does not say whether the location of generated text must be given in the paper itself.")
add("AI_ASSISTANCE_CHECKLIST", 2025, "ARR-RNLP-2025", "E1. Did you include information about your use of AI assistants?", "checklist_question",
    where="checklist", location="E1", notes=RNLP_NOTES[2025])
add("AI_DISCLOSURE_IN_PAPER", 2025, "ARR-CFP-2025",
    "Their use for writing or coding, as well as its scope, must be disclosed in the Acknowledgements section, as well as flagged in the Responsible NLP Checklist.",
    "conditional_mandatory", condition="generative AI used for writing or coding beyond language polishing / short-form input",
    location="AI Writing/Coding Assistance Policy")
add("AI_ASSISTANCE_CHECKLIST", 2026, "ARR-RNLP-2026", "E1. If you used any AI assistants, did you include information about your use?", "checklist_question",
    where="checklist", condition="AI assistants were used", location="E1", notes=RNLP_NOTES[2026])
add("AI_DISCLOSURE_IN_PAPER", 2026, "ARR-CFP-2026", "Details should be included in the Acknowledgements section.",
    "recommended", condition="generative AI used for writing or coding beyond language polishing / short-form input",
    location="AI Writing/Coding Assistance Policy",
    notes="Weaker than 2025: disclosure 'must' now go to the checklist, details in the paper 'should'.")

# ---------------------------------------------------------------- explicit 'none' rows for uncovered cells
UNVERIFIED_2023_ETHICS_FAQ = {"DATA_COLLECTION_DESCRIPTION", "PARTICIPANT_RECRUITMENT_PAY", "ETHICS_REVIEW_BOARD", "CONSENT"}
covered = {(r["req_id"], r["year"]) for r in rows}
for year, docs in DOCS_BY_YEAR.items():
    for req, *_ in DICTIONARY:
        if (req, year) in covered:
            continue
        notes = "No such requirement in the documents checked for this year."
        if req == "CLAIMS_SUMMARY" and year >= 2025:
            notes = "Question A3 was removed from the ARR checklist (present in 2022-2024)."
        add(req, year, ";".join(docs), "", "none", where="", notes=notes)

# rows for 2023 where the (unarchived) EMNLP 2023 ethics FAQ may have contained guidance
for req in sorted(UNVERIFIED_2023_ETHICS_FAQ):
    add(req, 2023, "EMNLP2023-ETHICS-FAQ", "", "unverified", where="",
        notes="The EMNLP 2023 ethics FAQ (recommendations in 2021-2022) has no Wayback capture before the deadline.")

rows.sort(key=lambda r: ([d[0] for d in DICTIONARY].index(r["req_id"]), int(r["year"])))

with open(inv.DICTIONARY_PATH, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(inv.DICTIONARY_FIELDS)
    w.writerows(DICTIONARY)
with open(inv.INVENTORY_PATH, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=inv.INVENTORY_FIELDS)
    w.writeheader()
    w.writerows(rows)
print(len(rows), "rows")
