# TODO — do pełnego PoC

Stan (15.11): źródła polityk zebrane (`data/policy_sources/`), inwentarz wymogów zrobiony przez LLM i poprawiony po self-audycie (`config/policy_register/inventory.csv`, 362 wiersze, wszystkie `pending`). Proces: [docs/methodology/rubric-development.md](docs/methodology/rubric-development.md). Decyzje do podjęcia: [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md).

Terminy: 18.11 nagranie na półmetek (SOTA + PoC) i termin pilotażowej anotacji; 2.12 raport z fazy 2 i zamrożenie rubricu.

## 1. Inwentarz wymogów (etap 2)
- [x] Weryfikacja przez ludzi: w `inventory.csv` wpisać `verified_by` i `verification` (`verified` albo `disputed` + powód w `notes`). Minimum to wiersze przełomów:
  - Limitations 2021–2022;
  - etyka 2020;
  - status checklisty ARR 2022–2024;
  - AI 2023–2026;
  - `COMPUTE_*` 2020–2024;
  - `ARTIFACT_LICENSE`.
- [x] (Opcjonalnie) niezależna kontrola innym modelem, np. Gemini: [prompt](docs/methodology/inventory-verification-prompt.md).
- [x] Po każdej zmianie: `uv run python scripts/00_validate_inventory.py` (0 błędów).

## 2. Wybór itemów (etap 3)
- [ ] `config/rubric/item_selection.md`: wszystkie 34 wymogi z oceną według 6 kryteriów i decyzją. Punkt wyjścia: I1–I6, I3 jako „ryzyka i etyka”, I4 jako „czas + sprzęt” oraz link do kodu jako wskaźnik automatyczny (zob. OPEN_QUESTIONS).

## 3. Rubric v2 (etap 4)
- [ ] `config/rubric/rubric_v2.0.0.json` (v1 zostaje): definicja, reguła stosowalności, drzewo decyzyjne, dozwolone miejsca w pracy, statusy dowodu z `uncertain` i co najmniej 3 przykłady pozytywne oraz 3 negatywne z prac pilota.
- [ ] Wpis w `config/rubric/CHANGELOG.md`.

## 4. Status item × rok (etap 5)
- [ ] `config/policy_register/requirements.csv` wyliczony z `inventory_by_year.csv`.
- [ ] `src/emnlp_audit/evaluators/compliance.py`: liczyć `policy_applies` z `requirements.csv` zamiast z `policy_mandate_years`, uwzględniając ścieżkę zgłoszenia w 2022–23.

## 5. Pilot i ewaluatory
- [ ] Anotacja pilota (14 prac, rubric v1) do 18.11, potem `scripts/07_validate.py` (kappa).
- [ ] Rozstrzyganie rozbieżności między anotatorami: teraz etykieta referencyjna to po prostu anotator A (TODO w `analysis/validation.py`).
- [ ] Prompt LLM v2 (`config/prompts/`) i reguły baseline'u dla nowych itemów, potem nowe runy w `runs/`.
- [ ] Arkusze anotacji osobno dla każdego anotatora.
- [ ] Losowanie próbek dev (70) i test (140) z proporcjonalnym podziałem na tracki (`corpus/sampling.py`, TODO).

## 6. Znane problemy w kodzie
- [x] Weryfikacja cytatów LLM sprawdza tylko początek cytatu (`evaluators/llm.py`).
- [x] Obcinanie tekstu do 120 tys. znaków: logować i oznaczać `Uncertain`.
- [x] Parser: proposal mówi Docling, a kod używa PyMuPDF. Ujednolicić kod albo proposal.

## 7. Raport z fazy 2 (2.12)
- [ ] Deklaracja LLM: zebranie źródeł, szkic inwentarza i self-audyt (Claude), refactor kodu, ewaluator (Gemini).
- [ ] Tabela wkładu z godzinami.
- [ ] Tabela 2 w proposalu: zaktualizować, jeśli zmienią się itemy.
