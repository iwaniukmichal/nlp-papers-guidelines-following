Review z 3 listopada 2026 r. Dotyczy `proposal/project-proposal.tex`, `proposal/project-proposal.bib`, szablonu oraz instrukcji przekazanych w rozmowie. Numery linii odnoszą się do obecnej wersji `.tex`. Pola TODO pominięto. Plików źródłowych propozycji nie zmieniono.

**Ocena:** projekt odpowiada zadaniu, a podstawowa koncepcja metodologiczna jest rozsądna. Weryfikacja nie wykazała fałszywych podstawowych twierdzeń w cytowanych opisach prac i polityk. Główne braki dotyczą konkretności rubryki, porównywalności pomiaru między latami, walidacji rzadkich naruszeń oraz uzasadnienia wnioskowania statystycznego. Tekst można skrócić przez usunięcie powtórzeń i przeniesienie szczegółów technicznych do aneksu.

**Uwagi według ważności.** P1 oznacza problem istotny dla wiarygodności wyników; P2 — doprecyzowanie lub ograniczenie interpretacji. To review projektu badania, więc brak wykonanych eksperymentów nie jest zarzutem.

1. **[P1] Publikacja checklist zmienia dostępność dowodów — linie 112, 148.**

   Protokół dopuszcza dowody z publicznych checklist, ale nie określa, jak zachować porównywalność z wcześniejszymi latami. ARR ogłosiło 11 czerwca 2025 r., że od EMNLP 2025 checklisty będą publikowane przy zaakceptowanych pracach. Wzrost wykrywalności informacji od 2025 r. może więc wynikać z udostępnienia nowego dokumentu. Samo oznaczenie wcześniejszych checklist jako niedostępnych tego nie rozwiązuje. [Oficjalne ogłoszenie ARR](https://aclrollingreview.org/responsible-nlp-checklist-appendices).

   **Poprawka:** zdefiniować główną serię na wspólnym materiale: artykuł i jego zwykłe aneksy, z wyłączeniem checklist. Dodatkową serię uwzględniającą publiczne checklisty pokazać dla lat, w których są dostępne. Jeśli badana reguła dopuszcza dowód wyłącznie w checkliście, oceniać ją osobno, z odpowiednim zakresem obserwowalności. Publikację checklist można także badać jako odrębną zmianę polityki.

2. **[P1] Rubryka pozostaje zapowiedzią zamiast sprawdzalnego projektu — linie 115–126.**

   Są rodziny wymagań i plan wyboru 4–6 pozycji, ale brakuje choćby wstępnej tabeli konkretnych pozycji: źródło, okres, obowiązkowość, zastosowanie, kryterium zaliczenia i dozwolony nośnik dowodu. Bez tego trudno ocenić, czy powstanie pomiar zgodności poza sekcją Limitations.

   Szczególnie ważne jest rozdzielenie obowiązku odpowiedzi na checklistę od obowiązku uzyskania odpowiedzi „Yes”. Aktualne instrukcje ARR dopuszczają odpowiedź „No” z właściwym uzasadnieniem. Magnusson i in. opisują również, że w badanej starszej checkliście wymagano odpowiedzi, a nie zamieszczenia każdej wymienionej informacji. Sam brak danych o zasobach obliczeniowych nie musi więc oznaczać naruszenia reguły konferencji. [ARR: zasady odpowiedzi](https://aclrollingreview.org/responsibleNLPresearch/), [Magnusson i in., §2](https://aclanthology.org/2023.findings-acl.809.pdf).

   **Poprawka:** pokazać teraz kilka pozycji roboczych. Dla EMNLP 2022 można już udokumentować obowiązkową sekcję Limitations oraz warunkowy obowiązek dyskusji etycznej przy wrażliwych danych lub zadaniach; osobna sekcja etyczna nie była ogólnie wymagana. [CFP EMNLP 2022](https://2022.emnlp.org/calls/main_conference_papers/). Inne pozycje oznaczyć jako wskaźniki adopcji, dopóki nie zostanie potwierdzony obowiązek.

   Dodatkowo zapisać oddzielnie: `policy_applies`, `practice_present` oraz wynik zgodności wyprowadzany z reguły. Obecne cztery etykiety zgodności nie wystarczają jako jedyny zapis: przed wprowadzeniem obowiązku praktyka nadal może być obecna albo nieobecna. Potrzebne są także etykiety adopcji. To doprecyzowuje już zapowiedziane rozróżnienie, nie zmienia celu badania.

3. **[P1] SOTA pomija bezpośrednio istotnego poprzednika — linie 65–76.**

   Należy dodać **Magnusson, Smith i Dodge (2023), „Reproducibility in NLP: What Have We Learned from the Checklist?”**. Praca analizuje 10 405 odpowiedzi i zestawia raportowanie po wprowadzeniu checklisty z wcześniejszymi obserwacjami. Jest bliższa RQ2 niż sama motywacyjna praca Dodge'a z 2019 r. Powinna wejść do głównego porównania i uzasadnienia nowości. [Publikacja](https://aclanthology.org/2023.findings-acl.809/).

   Wkład projektu warto określić raz: **wieloletnia ocena jawnie odtworzonych, obowiązujących reguł w kilku rodzinach raportowania, z niezależną walidacją dowodów w publikacjach**. Samo badanie zmian po polityce ani rozszerzenie tematu poza Limitations nie wystarczą jako opis nowości.

   Jako dodatkowy punkt porównania dla etyki i danych warto rozważyć EthiCon: 1 580 wypowiedzi etycznych z ACL Anthology. Nie trzeba rozbudowywać przeglądu; wystarczy wiersz w tabeli porównawczej. [Karamolegkou i in. (2025)](https://aclanthology.org/2025.naacl-long.580/).

4. **[P1] Walidacja może nie uchwycić błędów istotnych dla trendów — linie 128–137.**

   140 prac testowych oznacza 20 na rok, następnie dzielonych między tracki i warunki zastosowania pozycji. Ilustracyjnie, dla prostej próby losowej wynik 10/20 daje 95% przedział Wilsona około 30–70%. Jeśli naruszenia dotyczą 5% prac, prawdopodobieństwo niewylosowania żadnego w 20 pracach wynosi około 36%. Przy częstości 0,5% nawet w 140 pracach prawdopodobieństwo zera naruszeń wynosi około 50%. To obliczenia ilustracyjne, nie prognoza częstości w tym korpusie.

   **Poprawka:** zachować próbę probabilistyczną do estymacji, lecz dobrać dodatkowy, niezależnie oceniony zbiór diagnostyczny rzadkich przypadków. Dla sekcji strukturalnych rozważyć audyt wszystkich wykrytych braków oraz losowej części wyników dodatnich. Taki audyt nadal wymaga znanych prawdopodobieństw doboru, jeśli ma służyć estymacji. Projekt słusznie oddziela już diagnostykę od próby reprezentatywnej; trzeba dopisać, jak diagnostyka wesprze ocenę rzadkich naruszeń.

   Nie ma jednej obowiązkowej liczebności: należy ustalić, jaką wielkość zmiany projekt chce rozróżniać. Jeżeli budżet zostaje bez zmian, nie obiecywać wiarygodnej oceny jakości automatu osobno w każdym roku i tracku. Podać liczebności klas i niepewność metryk. Macro-F1 ≥ 0,80 nie zastępuje tej oceny — tekst trafnie już to zastrzega.

5. **[P1] Propagacja błędu automatu wymaga konkretnej procedury — linia 148.**

   Rozróżnienie pełnego spisu predykcji od prawdziwych etykiet jest poprawne. Jednak „propagate that error through stratified resampling” nie określa estymatora, korekty obciążenia ani sposobu traktowania błędów zastosowania reguły i abstencji. Sam bootstrap predykcji nie naprawi systematycznego błędu klasyfikacji.

   **Poprawka:** wybrać prosty wariant: ważone estymaty ludzkie jako punkt odniesienia, a wyniki automatu jako oddzielny pomiar z analizą wrażliwości. Alternatywnie zadeklarować estymator wspomagany predykcjami: pełny korpus dostarcza predykcji, a niezależna próba ludzka — ważonej korekty ich błędów. Przy ilorazie C/(C+N) trzeba uwzględnić błąd obu liczników, w tym zastosowania reguły. Możliwą podstawą jest [Prediction-powered inference, Angelopoulos i in. (2023)](https://arxiv.org/abs/2301.09633), po dostosowaniu do warstwowego doboru i docelowej populacji. Nie jest to wymaganie zastosowania tej konkretnej metody.

6. **[P2] Zmiana ekstraktora może nałożyć się na zmianę polityki — linia 112.**

   Oryginalny ACL OCL obejmuje publikacje do września 2022 r., a EMNLP 2022 odbyło się później. Przy wykorzystaniu OCL dla starszych prac i nowego parsera dla pozostałych granica narzędzi może wypaść dokładnie przy badanym obowiązku Limitations. Ogólny audyt jakości według roku jest przydatny, ale nie opisuje kontroli tego konkretnego problemu. [Opis zakresu OCL](https://aclanthology.org/2023.emnlp-main.640.pdf).

   **Poprawka:** preferować ten sam parser dla całego korpusu albo wykonać porównanie obu ekstrakcji na wspólnych PDF-ach, szczególnie wokół granicy czasowej. Zapisać pochodzenie tekstu i wersję narzędzia. Kosztowniejszy parser można ograniczyć do dokumentów wymagających ponownej ekstrakcji.

7. **[P2] H2 i testy czasowe wymagają węższej interpretacji — linie 60, 150–152.**

   H2 porównuje wymagania strukturalne i treściowe, choć mogą mieć inne populacje zastosowania, inne lata obowiązywania i różną jakość pomiaru. Jeśli kryterium treściowe wymaga też obecności sekcji, niższy wynik wynika częściowo z konstrukcji kryterium. Lepiej potraktować to jako pytanie opisowe albo zdefiniować porównanie na tych samych pracach i wskazać, co wykracza poza tę zależność.

   Zastrzeżenia o siedmiu edycjach i braku identyfikacji przyczynowej są właściwe. Trzeba jednak sprecyzować, co ma uzasadniać test na poziomie artykułów: dokumenty z jednego roku podlegają wspólnym zmianom, a tysiące prac nie tworzą tysięcy niezależnych wdrożeń polityki. Zalecam opisowe różnice jako analizę główną; ewentualny model ma szacować jasno określone związki pod podanymi założeniami. Nie wystarczy dopisać standardowych błędów grupowanych po roku przy zaledwie siedmiu grupach.

   RQ3 może pozostać eksploracyjne. Warto już teraz podać roboczy podział kohort i sposób traktowania edycji przejściowych, zamiast pozostawiać cały wybór później. Wyniki dotyczą zaakceptowanych publikacji: zmiana może wynikać zarówno ze zmian tekstów, jak i selekcji prac w recenzji.

8. **[P2] Sekcja danych potrzebuje krótkiego bilansu dostępnych zasobów — linie 74, 108–112.**

   Kryteria włączenia są dobre, ale na raport skupiony na SOTA, danych i metodologii przyda się tabela: zasób, okres, dostępny materiał, planowane wykorzystanie, ograniczenia. Powinna rozdzielać pełny korpus PDF od zbiorów zawierających tylko wybrane sekcje i etykiety.

   Zbiór autorów „What Limits Us?” jest publiczny. Występuje jednak rozbieżność: publikacja opisuje 16 067 sekcji, a README udostępnionego zbioru LLM podaje 16 047 prac. Liczba 16 067 w propozycji jest poprawnym przytoczeniem publikacji; nie należy jej automatycznie zmieniać. Przed wykorzystaniem danych trzeba przypiąć wersję i sprawdzić faktyczne rekordy. [Repozytorium autorów](https://github.com/Sundione/nlp-self-reported-limitations).

   EMNLP Main + Findings to uzasadniony, określony zakres wobec pierwotnego zadania przewidującego wybrane konferencje. Sformułowanie prowadzącego „all available papers” warto realizować jako wszystkie kwalifikujące się prace tego zakresu i nazwać ten zakres wprost. Nie ma podstaw, aby z samego opisu uznać obowiązek analizy całej Anthology. Przyda się jedno zdanie uzasadnienia wyboru EMNLP. Nie trzeba teraz przeprowadzać eksperymentów ani kończyć zbierania korpusu.

**Weryfikacja źródeł i twierdzeń.** Sprawdzono wszystkie 12 pozycji bibliograficznych oraz ich zastosowanie w tekście. Dla Xiao i in. wydawca blokował bezpośredni odczyt; treść i DOI potwierdza autorska wersja pracy. Poniższa weryfikacja nie zastępuje zaplanowanej rekonstrukcji wszystkich historycznych reguł 2020–2026.

| Twierdzenie / źródło | Wynik |
|---|---|
| [Dodge i in. (2019)](https://aclanthology.org/D19-1224/) | Poprawnie: wynik testowy sam nie wystarcza do porównania modeli; znaczenie mają wyniki walidacyjne i budżet obliczeniowy. |
| [Benotti i Blackburn (2022)](https://aclanthology.org/2022.emnlp-main.299/) | Poprawnie: ręczna klasyfikacja sekcji etycznych z ACL 2021, w tym korzyści, szkody i grupy wrażliwe. Rok publikacji i rok analizowanego korpusu są różne i dobrze podane. |
| [Jinnath i Zhao (2026)](https://arxiv.org/abs/2608.09280) | Poprawnie: preprint, analiza 73 922 odpowiedzi i uzasadnień z EMNLP 2025. Propozycja ostrożnie relacjonuje wyniki autorów. |
| [„What Limits Us?” (2026)](https://aclanthology.org/2026.findings-emnlp.2386.pdf) | Opis zakresu, liczby sekcji, kodowania i ręcznego audytu braków jest zgodny z pracą. Pisownia nazwiska w `.bib` odpowiada PDF; strona Anthology stosuje inny wariant. Nie uznaję tego za błąd autora propozycji. |
| [Rohatgi i in. (2023)](https://aclanthology.org/2023.emnlp-main.640/) | Poprawnie opisane metadane i strukturyzowane teksty. Warto doprecyzować granicę oryginalnego wydania: wrzesień 2022. |
| [Xiao i in. (2023)](https://arxiv.org/html/2304.10548v1) | Poprawnie: dedukcyjne kodowanie z wcześniej zdefiniowaną książką kodową i GPT-3; tekst nie przypisuje im dowodu jakości dla obecnego zadania. |
| [CFP EMNLP 2022](https://2022.emnlp.org/calls/main_conference_papers/) | Wymóg dedykowanej sekcji Limitations potwierdzony. |
| [CFP EMNLP 2025](https://2025.emnlp.org/calls/main_conference_papers/) | Potwierdzone odesłania do wymagań ARR i polityki Writing Assistance. |
| [CFP EMNLP 2026](https://2026.emnlp.org/calls/main_conference_papers/) | Potwierdzone odesłania do wymagań ARR i polityki Writing Assistance. |
| [ARR authorchecklist](https://aclrollingreview.org/authorchecklist) | Cytowanie poprawne: końcowa część strony rzeczywiście mówi o publikacji checklist EMNLP 2025 i zachęca do data sheets oraz model cards. Wcześniejsza uwaga w rozmowie o braku tych informacji została skorygowana. |
| [ACL 2023 AI Writing Assistance](https://2023.aclweb.org/blog/ACL-2023-policy/) | Rozróżnienie zastosowań i wyjątków jest prawidłowe. Brak deklaracji nie dowodzi nieujawnionego użycia. |
| [Licencja ACL Anthology](https://aclanthology.org/faq/copyright/) | CC BY 4.0 dla materiałów ACL od 2016 r. potwierdzona. Zastrzeżenie osobnych warunków dla innych zasobów jest zasadne. |

**Zgodność z zadaniem i szablonem.**

| Element | Ocena |
|---|---|
| Limit | Spełniony według późniejszej instrukcji prowadzącego: 5 stron tekstu głównego. PDF ma 6 stron łącznie; bibliografia zaczyna się na stronie 5. Nie należy zgłaszać przekroczenia na podstawie całkowitej liczby stron ani stosować starszego limitu 4 stron. |
| Abstract | Około 190 słów; poniżej limitu 250. |
| Cel, RQ, hipotezy, znaczenie, plan, ryzyka, metody i wyposażenie | Są. H2 i procedury statystyczne wymagają doprecyzowania opisanego wyżej. |
| SOTA i dane | Obecne; najważniejsze uzupełnienia to Magnusson (2023), tabela dostępności danych i konkretne pozycje rubryki. |
| Badania wstępne | Wskazano sprawdzoną obserwację polityki. Brak eksperymentów jest zgodny z etapem projektu i terminem styczniowym. |
| Data statement | Obejmuje źródło, licencję, dane osobowe i sposób postępowania z nimi. |
| Format | Zachowane 11 pt, Times, dwie kolumny, A4; pliki `.sty` i `.bst` są identyczne z dostarczonymi. Powiększenie pola tytułowego do 8 cm jest dozwolone przez szablon. |
| Kompilacja | Kompilacja kopii źródeł w `/tmp/nlp-proposal-review-build` z BibTeX zakończona powodzeniem, bez niezdefiniowanych cytowań i odwołań; pozostały komunikaty `Underfull`. |
| TODO | Nie oceniano ich wypełnienia. |

Przed wysłaniem należy także zastosować wymagany przez szablon folder z nazwiskami w ustalonej kolejności. Nie jest to zarzut do roboczego katalogu `proposal/`.

**Skróty bez utraty informacji w całym dokumencie.** Tekst poza TODO ma orientacyjnie 2,6 tys. słów, licząc fragmenty źródła. Najwięcej można odzyskać przez pozostawienie każdej informacji w jednym właściwym miejscu. Nie ma potrzeby zmniejszania fontu ani odstępów.

| Miejsce | Zmiana |
|---|---|
| Abstract, linia 46 | Skrócić do celu, zakresu, metody, walidacji i głównego wkładu. Pełną listę produktów pozostawić w jednym miejscu. |
| SOTA, linie 68 i 71 | Usunąć powtarzane wyjaśnienia, że projekt nie jest pierwszym audytem ani pierwszą analizą podłużną. Jedno precyzyjne zdanie o wkładzie po uwzględnieniu Magnussona wystarczy. |
| Linie 74 i 108–112 | Opis ACL OCL i jego ograniczeń umieścić w tabeli danych; nie powtarzać go w SOTA i metodologii. |
| Expected contribution, linia 77 | Zachować jedno zdanie o wkładzie naukowym. Lista produktów powtarza abstract. |
| Linia 81 | Usunąć całe zdanie wprowadzające: kolejność prac i planowany charakter dat wynikają z tabeli i czasu przyszłego. |
| Linia 100 | Usunąć wyjaśnienie, że są to „design observations” i nie wykonano jeszcze eksperymentów. To propozycja; pozostawić konkretne ustalenie polityki. |
| Linia 103 | Zastąpić akapit tabelą ryzyko → działanie lub przenieść szczegóły do aneksu. Zasady walidacji są już opisane niżej. |
| Linie 110 i 115 | Szczegółowe listy pól manifestu i rejestru polityk przenieść do aneksu; w tekście zachować zakres, wersjonowanie i pochodzenie. |
| Linie 119–121 | Skondensować przykłady obowiązków, rekomendacji i nieobserwowalnego użycia AI do tabeli rubryki. Zachować zasadę, że brak deklaracji nie dowodzi użycia AI. |
| Linie 128–130 | Liczebności próbek przedstawić w jednym wierszu/tabeli. Zachować niezależność anotacji, rozłączność zbiorów i zakaz strojenia na teście. |
| Linia 135 | Listę parametrów odtwarzalności przenieść do aneksu; pozostawić informację o zamrożeniu modelu i protokołu przed testem. |
| Linie 146, 148, 152 | Zachować mianowniki, niepewność i ograniczenia identyfikacji. Usunąć powtórzenia wyjaśnień o osobnej serii adopcji oraz braku wnioskowania przyczynowego z innych sekcji. |
| Linie 47, 77, 121, 155 | Zakaz profilowania autorów i detekcji tekstu AI zapisać raz w zakresie/etyce. W pozostałych miejscach zostawić tylko niepowtarzające się ograniczenia pomiarowe. |

Przykładowe krótsze zamienniki zdań:

- Linia 51: “We study whether EMNLP reporting requirements are reflected in published Main and Findings papers from 2020–2026.” Definicję zgodności i jednostkę analizy pozostawić w następnym zdaniu.
- Linia 65: “Dodge et al. (2019) show that model comparisons depend on validation performance and computational budgets, motivating more complete experimental reporting.” Zastrzeżenie o niewiążących rekomendacjach pozostawić raz przy rubryce.
- Linia 110, po przeniesieniu schematu do aneksu: “A versioned manifest will identify each paper, source PDF and extraction status; counts and exclusions will be reported by year and track.” Nie usuwać samego schematu z dokumentacji.
- Linia 139: “We will use a laptop, Python, an annotation interface, statistical software and, if affordable, an LLM API; pilot timings and token use will determine workload and cost.”

Najpierw warto uzupełnić trzy konkretne elementy — porównanie z Magnussonem, tabelę danych i tabelę rubryki — a następnie usunąć powtarzające je deklaracje. W głównym tekście powinny zostać pytania, najbliższe prace, zakres danych, reguły pomiaru, walidacja i plan analizy. Szczegóły schematów i konfiguracji mogą trafić do aneksu zgodnie z instrukcją prowadzącego.
