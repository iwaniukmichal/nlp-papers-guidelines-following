# From guidelines to practice: Do NLP papers follow reporting requirements?

NLP course project (Warsaw University of Technology, Winter 2026/27). We audit reporting in all eligible
EMNLP Main and Findings papers from 2020–2026 against a historical policy register and a versioned
rubric, using a rule baseline, one LLM evaluator and double human annotation.
See [docs/proposal/project-proposal.tex](docs/proposal/project-proposal.tex).

## Repository layout

```
docs/                proposal, course rules, LaTeX templates
  methodology/       rubric-development.md (how the policy register and rubric are built)
config/              everything that is frozen and versioned
  rubric/            rubric_v<version>.json + CHANGELOG.md
  policy_register/   documents.csv (dated policy sources), requirement_dictionary.csv,
                     inventory.csv (requirement x year evidence); register.json (v1 PoC draft)
  prompts/           LLM prompt templates
src/emnlp_audit/     pipeline code (installable package)
  corpus/            ACL Anthology manifest, sampling, PDF download
  parsing/           PDF -> text, checklist removal, e-mail redaction
  evaluators/        rules.py, llm.py, compliance.py (shared), runs.py
  annotation/        human annotation sheets
  analysis/          inter-annotator agreement, validation, pilot summary
scripts/             numbered entry points (01 ... 08)
data/
  manifest/          eligible_manifest.csv, counts_by_year_track.json
  policy_sources/    committed Wayback/Anthology snapshots of policy documents (+ .txt)
  samples/           frozen samples: pilot_14, later dev_70, test_140
  annotations/       human annotation sheets per sample
  raw/, interim/     PDFs, XML, parsed text (gitignored, re-creatable)
runs/                one folder per evaluator run, never overwritten
results/             reports derived from runs and annotations
tests/
```

Each folder in `runs/` holds `evaluations.{csv,json}`, `config.json` (evaluator, model, prompt hash,
rubric version, parser, sample) and, for LLM runs, `usage.json`.

## Setup

Dependencies are managed with [uv](https://docs.astral.sh/uv/) (`pyproject.toml` + `uv.lock`):

```bash
uv sync                      # creates .venv, installs the package and dev tools
uv add <package>             # add a dependency (updates pyproject.toml and uv.lock)
```

Run any script with `uv run`, e.g. `uv run python scripts/01_build_manifest.py`.

## Pipeline

| Step | Command | Output |
|---|---|---|
| 0 | `python scripts/00_fetch_policy_sources.py` (`--verify` offline) | `data/policy_sources/`, fills `documents.csv` |
| 0 | `python scripts/00_validate_inventory.py` | checks `inventory.csv`, writes `inventory_by_year.csv` |
| 1 | `python scripts/01_build_manifest.py` | `data/manifest/` |
| 2 | `python scripts/02_draw_sample.py --split pilot_14 --seed 42` | `data/samples/pilot_14.*`, PDFs in `data/raw/pdfs/` |
| 3 | `python scripts/03_parse.py --split pilot_14` | `data/interim/parsed/` |
| 4 | `python scripts/04_run_rules.py --split pilot_14` | `runs/<date>_pilot_14_rule-baseline-v1_rubric-v1.0.0/` |
| 5 | `GEMINI_API_KEY=... python scripts/05_run_llm.py --split pilot_14` | `runs/<date>_pilot_14_gemini-2.5-flash_rubric-v1.0.0/` |
| 6 | `python scripts/06_make_annotation_sheets.py --split pilot_14 --deadline 2026-11-18` | `data/annotations/pilot_14/annotation_sheet.csv` |
| 7 | `python scripts/07_validate.py --split pilot_14 --run <run_id>` | `results/pilot_14/iaa_and_validation_<run_id>.json` |
| 8 | `python scripts/08_summarize.py --split pilot_14 --rules-run <id> --llm-run <id>` | `results/pilot_14/summary_report.json` |

The `pilot_14` sample is already drawn and frozen. After cloning, fetch its PDFs with
`python scripts/02_draw_sample.py --split pilot_14 --download-only`, then continue from step 3.
Samples, annotation sheets and runs are protected against accidental overwriting.

Tests: `uv run pytest`.

## Pilot (PoC) status

- Corpus: 16,618 eligible papers (9,254 Main + 7,364 Findings).
- Pilot: 14 papers (1 Main + 1 Findings per year, seed 42), evaluated by the rule baseline and
  `gemini-2.5-flash` (runs dated 2026-11-15); summary in `results/pilot_14/summary_report.json`.
- Human double annotation of the pilot: in progress (`data/annotations/pilot_14/`).
