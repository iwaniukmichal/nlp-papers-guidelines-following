# Open questions

Kontekst: macierz statusów wymóg × rok w `config/policy_register/inventory_by_year.csv` (`uv run python scripts/00_validate_inventory.py`).

## Do decyzji zespołu

1. **Zakres weryfikacji inwentarza:** cały (362 wiersze) czy tylko wiersze przełomów? Kto weryfikuje które lata?
2. **Itemy rubricu** (proposal mówi o 6):
   - I3: zostawić „etykę” (warunkowy obowiązek przez cały okres 2020–26, czyli brak przełomu) czy zmienić na „ryzyka i etyka” (A2 dla wszystkich prac od 2024)?
   - I4: wspólny wskaźnik „czas obliczeń + sprzęt” (runtime 2020–23, łączny budżet od 2024) czy zamiana na statystyki wyników (C3, wymóg ciągły od 2020)?
   - Czy dodać link do kodu jako wskaźnik liczony automatycznie, bez anotacji? To jedyny wymóg, który słabnie: z checklisty do samego zalecenia.
3. **Zatwierdzić reguły kodowania przyjęte po self-audycie:**
   - checklista ARR 2022–23 („should upload”) = `recommended`;
   - objaśnienia pod pytaniem checklisty liczą się jako część pytania;
   - reguły specyficzne dla EMNLP w 2022–23 dotyczą tylko zgłoszeń bezpośrednich.
4. **Pilot:** anotować według v1 (termin 18.11) i traktować rozbieżności jako materiał do v2, czy poczekać na v2?
5. **Pary anotatorów pokrywają się z trackami** (para 1 → Main, para 2 → Findings). Kappa miesza wtedy efekt pary z efektem tracku. Zmienić przydział w próbkach dev i test?

## Do Filipa Kucii (spotkanie)

1. **2022–2023: dwie ścieżki zgłoszeń** (bezpośrednio do EMNLP lub przez ARR) miały różne wymogi, a ścieżki konkretnej pracy nie znamy. Wystarczy porównanie 2020–21 vs 2024–26 z 2022–23 jako okresem mieszanym? Czy da się ustalić ścieżkę pracy?
2. **Zmiana itemów względem proposala** (I3, I4, dodatkowy wskaźnik automatyczny): czy jest akceptowalna i jak ją opisać w raporcie z fazy 2?
3. **Użycie LLM:** szkic inwentarza wymogów i self-audyt zrobił Claude, weryfikują ludzie. Czy to w porządku i czy wystarczy weryfikacja wierszy przełomów zamiast całości?
4. **Dowody z późniejszych dokumentów:** polityka ACL z 2026 podaje datę wejścia w życie 25.04.2025, ale kopii sprzed terminu EMNLP 2025 nie ma. Uznać to za dowód czy zostawić `unverified`?
5. **Findings:** nie znaleźliśmy reguł specyficznych dla Findings (zakładamy te same co dla Main, bo prace pochodzą z jednej puli zgłoszeń). Czy to założenie jest OK?
6. **Etyka bez zmian polityki w całym okresie:** czy taki item ma sens jako punkt odniesienia (np. dla RQ3, era ChatGPT)?
7. **Parser:** proposal deklaruje Docling, a PoC używa PyMuPDF. Czy to ważne?
