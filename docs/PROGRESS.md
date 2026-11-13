# VOLT – stan prac

Ten plik wystarcza, żeby nowa sesja mogła kontynuować pracę.

## Kontekst
- Repo: `itsXami/vst` (do 13.11.2026 `jakubnikapiotr-design/vst`; GitHub przekierowuje), branch roboczy: `feature/volt-synth`, PR do `main`.
- Specyfikacja: oryginalne polecenie użytkownika (syntezator wavetable VOLT, VST3 + Standalone, 121 presetów).
  Kluczowe wymagania są streszczone w sekcji „Checklista” poniżej.
- Sesja w chmurze: przed buildem doinstalować zależności (`apt-get update` + lista niżej) i sklonować JUCE
  (`git clone --depth 1 --branch 8.0.15 https://github.com/juce-framework/JUCE.git`) poza repo, potem
  `-DFETCHCONTENT_SOURCE_DIR_JUCE=…`; pluginval nie jest tam zainstalowany – sprawdza go CI.
- Build lokalny (Linux):
  ```
  cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release [-DFETCHCONTENT_SOURCE_DIR_JUCE=/ścieżka/do/JUCE-8.0.15]
  cmake --build build
  ./build/VOLT_Tests_artefacts/Release/VOLT_Tests
  ./build/VOLT_Render_artefacts/Release/VOLT_Render --out render-out
  xvfb-run -a pluginval --strictness-level 5 --validate-in-process --validate build/VOLT_artefacts/Release/VST3/VOLT.vst3
  ```
- Zależności Linux: `libasound2-dev libx11-dev libxrandr-dev libxinerama-dev libxcursor-dev libxcomposite-dev
  libxext-dev libxrender-dev libfreetype-dev libfontconfig1-dev xvfb`.

## Etapy
| # | Etap | Status |
|---|------|--------|
| 1 | Szkielet CMake + JUCE, pusty plugin, CI, artefakt Windows | ✅ CI zielone (Linux+Windows) |
| 2 | Silnik: oscylatory, głosy, filtr, obwiednie | ✅ lokalnie, testy DSP zielone |
| 3 | Modulacja, makra, arpeggiator, efekty | ✅ lokalnie, testy zielone, pluginval lokalnie OK |
| 4 | Interfejs i przeglądarka presetów | ✅ lokalnie (zrzut w docs/ui-snapshot.png), pluginval z testem edytora OK |
| 5 | Render CLI i testy | ✅ lokalnie |
| 6 | 121 presetów z korektą wg raportów | ✅ 121/121 przechodzi render lokalnie |
| 7 | README (PL) i docs/PRESETS.md | ✅ |

## Dziennik
- Etap 1: szkielet buduje się lokalnie na Linuksie (GCC 13, Ninja); pluginval strictness 5 lokalnie: SUCCESS.
- Etap 1: CI run 41461908895 – oba joby zielone, pluginval na Windows uruchomiony, artefakt VOLT-windows-x64 (~6 MB).
- Etap 2: `Source/dsp/` – Wavetables (32 tablice), Voice (2 osc + unison 8, sub, szum, filtr, ADSR×2, pitch env,
  LFO per głos), VoiceFilter (7 typów), SynthEngine (16 głosów, Poly/Mono/Legato, glide, macierz modulacji 8 slotów).
  Arpeggiator.h i Effects.h to na razie zaślepki (etap 3). Testy: `tests/DspTests.cpp`.

- Etap 3: `Arpeggiator.h`, `Effects.h/.cpp` (Distortion, ModFx, Pump, StereoDelay, ReverbFx, SquashCompressor,
  OutputStage), podpięte w `SynthEngine::renderChunk`. Testy: `tests/FxTests.cpp` (arp, FX, modulacja, wydajność:
  najgorszy przypadek ~18% jednego rdzenia przy 48 kHz na maszynie deweloperskiej).

- Etap 4: `Source/ui/` (LookAndFeel, Controls, Views, PresetBar), `PluginEditor.*` (układ całego ekranu),
  `PresetManager.*`. Standalone uruchamia się pod xvfb bez awarii (nie da się tu przetestować interakcji myszą).

- Etap 5: `tools/render/RenderMain.cpp` (render, raport, podglądy FLAC, `--snapshot`), `tests/PresetTests.cpp`.
  Uruchomienie: `VOLT_Render --out render-out [--preset tekst] [--no-previews]`; kod wyjścia 1 przy błędach.

- Etap 6: `tools/presets/generate_presets.py` + `gain_trims.json` → `presets/*.json` (Init + 120).
  Procedura korekty: `python3 tools/presets/generate_presets.py` → build → `VOLT_Render --out render-out --no-previews`
  → `python3 tools/presets/generate_presets.py --trim render-out/report.json` → build → render (powtarzać do 100%).
  Uwaga: od scalenia partii `generate_presets.py` przebudowuje całą bibliotekę przez `build_library.py`.

- Etap 7: README.md (PL), docs/PRESETS.md (generowany).


## Weryfikacja CI (commit 2301848, PR run 41471116114)
- Linux: build, `ctest` (wszystkie testy jednostkowe), render 121/121 presetów (mediana −15,0 LUFS), pluginval
  strictness 5: **SUCCESS**.
- Windows x64: build VST3 + Standalone (MSVC), pluginval strictness 5 (w tym testy edytora): **SUCCESS**.
- Artefakty: `VOLT-windows-x64` (README.md, VOLT.exe, VOLT.vst3/…), `VOLT-preset-previews` (121 plików FLAC),
  `VOLT-render-report` (report.md + report.json).

## Definicja ukończenia – stan
- [x] CI przechodzi na obu systemach, artefakty się generują.
- [x] pluginval przechodzi (Linux i Windows, strictness 5).
- [x] Wszystkie 121 presetów ładuje się i przechodzi testy renderu.
- [x] README opisuje, co zweryfikowano automatycznie, a co wymaga odsłuchu i testu w FL Studio.

## Otwarte (wymaga człowieka z Windows + FL Studio)
- Odsłuch presetów (`VOLT-preset-previews.zip`) i ewentualne poprawki brzmień w `tools/presets/generate_presets.py`.
- Test w FL Studio: skanowanie, zapis/odczyt projektu, automatyzacja, sync tempa, UI (Shift, dwuklik, skalowanie, HiDPI).
- Po każdej zmianie presetów: procedura z etapu 6 (render → `--trim` → render) i commit JSON-ów + `gain_trims.json`.

## Po ukończeniu – zmiany na prośbę użytkownika
- Poprawka: jedyny program VST3 ma nazwę „Default” (walidator VST3 Steinberga w pluginval 2.0 odrzucał pustą nazwę).
- Przebudowa UI: kolor na sekcję, 1200×740, wartości zawsze widoczne, krzywa filtra, czcionka Inter (DECISIONS.md).
- Otwarte: pluginval 1.0.4 na Linuksie ma rzadki crash we własnym kodzie hosta (RunLoop VST3, ok. 1 na 10–15
  uruchomień, backtrace bez ramek VOLT); pluginval 2.0.0-beta3 nie crashuje (40/40). Decyzja o zmianie wersji w CI
  czeka na użytkownika.

## Przegląd presetów z użytkownikiem (w toku)
- Strona odsłuchu 121 presetów fabrycznych: https://claude.ai/artifact/GSXfynmqsquptfcDrNtqAL (kolekcja `ratings`,
  dokument `pNNN` = indeks presetu). Wynik: 77 zostaw, 10 popraw, 34 usuń. Uwagi: Long Glide 808 „nic nie słychać”,
  Tom Drop 808 „za cicho”. Użytkownik zauważył, że pady brzmią podobnie (jeden przepis w generatorze).
- Druga partia: 100 kandydatów (20 gitar, 20 pianin/klawiszy, 25 leadów, 10 basów, 8 padów, 7 arpów, 5 brass, 5 FX)
  w `tools/presets/candidates/` (generator `tools/presets/generate_candidates.py`, trymy `candidate_trims.json`),
  render `VOLT_Render --dir tools/presets/candidates` → 100/100 przechodzi. Strona wyboru:
  https://claude.ai/artifact/4zcEKaiVxnxW9hdwkG4Tis (kolekcja `ratings`, `pNNN` = numer pliku kandydata 001–100).
- ZROBIONE: biblioteka złożona z obu partii wg `tools/presets/selection.json` (werdykty z obu stron) przez
  `tools/presets/build_library.py`: Init + 135 (pierwsza partia bez 34 „Usuń”, kandydaci bez 51 odrzuconych;
  presety „Popraw” – 10 + 4 – zostały w obecnej formie na prośbę użytkownika „nie poprawiaj żadnych na razie”).
  Kategoria „Guitar” dodana w pluginie. Render 136/136, −17,2…−13,6 LUFS, limiter ≤ 2,9 dB.
  Jedyna zmiana poziomu: Crystal Keys out_gain −1 dB (limiter 3,1 dB > progu), brzmienie bez zmian.
- DO ZROBIENIA: poprawić presety z listy „fix” w selection.json (uwagi: Long Glide 808 „nic nie słychać”,
  Tom Drop 808 „za cicho”) – etap C; nowe presety korzystające z silnika v2 (warp, String, Comb) – etap D;
  dalsze zmiany wyglądu – etap B.

## Silnik v2 + zakładki (na prośbę użytkownika)
- Warp (8 trybów) i typ String na oscylator, Comb+/Comb−, Mod Env, Random, 12 slotów, 8 nowych tablic, zakładki UI.
  Szczegóły i uzasadnienia w DECISIONS.md („Rozbudowa silnika”). Testy: `tests/EngineV2Tests.cpp`.
- Istniejące presety brzmią identycznie (render przed/po: 0,0 LU różnicy). Kandydaci z drugiej partii jeszcze nie
  korzystają z nowych funkcji – przy kolejnych presetach warto ich używać (warp, String, Comb, Random).
- Generator presetów zna nowe parametry (`generate_presets.py`: DEFAULTS, TABLES, SOURCES, DESTS, limit 12 slotów).

## Ścieżka rozwoju – wersja publiczna (ustalona z użytkownikiem 2026-11-12)
Cel: syntezator będzie publiczny, więc podejście neutralne i profesjonalne. Idziemy po kolei A → E; po każdym
etapie commit + push, aktualizacja tego pliku i krótki raport dla użytkownika (co gotowe, co sprawdzić).

| Etap | Status |
|---|---|
| A. Neutralizacja + licencja | ✅ zrobione 2026-11-12 (opis niżej), czeka na sprawdzenie przez użytkownika |
| B. Profesjonalny wygląd | ✅ wdrożone w kodzie 2026-11-12 (opis niżej), czeka na sprawdzenie przez użytkownika na Windows |
| C. Silnik: pitch bend, sustain, 14 presetów „Popraw” | ✅ zrobione 2026-11-12 (opis niżej) |
| D. Biblioteka ok. 300 presetów | ✅ zamknięta 2026-11-13: 327 presetów + Init, odsłuchane przez użytkownika |
| E. Wydanie | 🔶 przygotowane 2026-11-13 (wersja 1.0.0); czeka na merge PR #1 i opublikowanie Release przez użytkownika |

**Etap A – co zrobiono:**
- Usunięte wszystkie nazwy artystów i albumów z tagów presetów (biblioteka i 100 kandydatów), generatorów,
  README i `docs/PRESETS.md`. Grupy w generatorach to teraz neutralne rodziny stylistyczne z tagami stylu
  (Industrial, Stadium, Cold, Epic, Gospel, House + Raw, House + Disco, Mechanical, Cinematic, Analog).
- Biblioteka ułożona: kategoria → nazwa alfabetycznie (pliki `presets/NNN_*.json` przenumerowane).
- Zmienione nazwy: „Light Cycle Arp” → „Racing Saw Arp”, „Suitcase Electric Piano” → „Autopan Electric Piano”;
  opis Funky Filter Keys bez nazwy marki. Brzmienia bez zmian (JSON-y przed/po różnią się tylko tagami).
- Test zakazanych nazw został i jest rozszerzony o tagi, opisy i etykiety makr (`kBannedEverywhere`).
- Dodane: `LICENSE` (AGPLv3), `CONTRIBUTING.md` (tylko presety), sekcja „Licencja” w README (nazwa i logo poza
  licencją), `docs/SOUND_REFERENCES.md` (wzorce brzmień na etap D).
- Weryfikacja lokalna: build Linux OK, testy 46 grup / 0 błędów, render 136/136 (−17,2…−13,6 LUFS, limiter
  ≤ 2,9 dB – identycznie jak przed zmianą). pluginval i build Windows sprawdza CI po pushu.
- Do decyzji użytkownika: (1) wpis o prawach autorskich w README to na razie „autorzy projektu VOLT” – można
  podać imię/pseudonim; (2) nazwy z luźnymi skojarzeniami zostały (np. Throne Brass, Sunday Drawbars, Praise Bass,
  Neon Grid Pad) – to zwykłe słowa, ale użytkownik może je zmienić; (3) jeden stary komunikat commita nadal
  wymienia artystów – przy upublicznieniu scalić PR metodą „squash” i usunąć gałąź (tytuł i opis PR #1 są już
  zneutralizowane).
- CI po etapie A (commit 7e995c0, run 43276908313): Linux i Windows zielone.

**Etap B – makiety (czeka na wybór):**
- Trzy kierunki jako rysunki wektorowe okna 1200×740 (zakładka SYNTH): `docs/mockups/volt-ui-1.svg` „Łuk”
  (jeden akcent – elektryczny błękit, obwiednie i LFO stale widoczne jako pasek wykresów), `volt-ui-2.svg`
  „Spektrum” (kolor na sekcję jak dziś, ale dojrzalej; jeden duży wykres obwiedni z przełącznikiem, mini-LFO;
  nic nie zmienia zakładki), `volt-ui-3.svg` „Żarnik” (duży ekran kontekstowy u góry, pulpit pokręteł bez ramek,
  ciepła czerń i pomarańcz). Generator: `python3 tools/ui/mockups.py [--html plik.html]`.
- Strona porównania dla użytkownika: https://claude.ai/artifact/4PoVCLzn4xfhM6WgvS39dd (rekomendacja Claude: 1;
  bezpieczniejsza alternatywa: 2). Użytkownik może też łączyć (np. układ z 1, kolory z 2).
- **Wybór użytkownika (2026-11-12): makieta 2** (kolor na sekcję, wszystko na jednym ekranie), z uwagą
  „to nadal wygląda AI” – szkic był za prosty (zaokrąglone karty z ramką, pastelowe kolory, gołe pierścienie
  pokręteł, owalne przełączniki, dużo pustego miejsca).
- **Runda 2 (czeka na wybór):** ten sam układ w docelowej szczegółowości, dwa wykończenia:
  `docs/mockups/volt-ui-2a.svg` „Techniczne” (płaskie panele na styk, cienkie łuki, odczyty czcionką mono) i
  `volt-ui-2b.svg` „Sprzętowe” (cieniowane główki pokręteł, wgłębione ekrany, świecące linie, diody). Wspólne
  zmiany: panele na styk, gęstszy ekran, głębsze kolory sekcji, wavetable jako pełna powierzchnia, siatka i
  podziałka na wykresach, prostokątne przełączniki w nagłówkach, znak VOLT z pokrętłem w miejscu „O”, miernik
  poziomu wyjścia (nowa funkcja). Generator: `python3 tools/ui/mockups_detail.py`. Ta sama strona porównania
  (runda 2 na górze). Rekomendacja Claude: 2B; można mieszać (np. panele z 2A, pokrętła z 2B).
- **Wybór użytkownika: 2A (techniczne)**, z uwagą „nadal wygląda AI, coś z czcionką i ogólnym wyglądem” i prośbą
  o sprawdzenie w sieci, co poprawić. Wnioski z przeglądu (źródła w DECISIONS.md) i **runda 3 (czeka na wybór)**:
  `docs/mockups/volt-ui-3a.svg` (krój Barlow Semi Condensed) i `volt-ui-3b.svg` (krój Oxanium), ten sam układ.
  Generator: `python3 tools/ui/mockups_final.py`. Zmiany względem 2A: jeden wybrany krój zamiast Inter + mono;
  hierarchia (Cutoff i Position jako duże pokrętła, ciemniejszy pasek pomocniczy bez ramek, makra jako osobny
  jaśniejszy pas z podpisem celu); oba oscylatory na jednej powierzchni; tytuły sekcji w kolorze sekcji zamiast
  paska nagłówka; 4 kolory sekcji + bursztyn tylko dla makr, wyjście i oscyloskop neutralne; różne style wykresów;
  znak VOLT rysowany od zera. Nowe funkcje na makiecie (do zrobienia przy wdrożeniu): miernik poziomu wyjścia,
  podpis celu pod makrem.
- **Wybór użytkownika: 3B (Oxanium)**, z prośbą, żeby kolejną makietę pokazać dopiero, gdy będzie „bardziej
  ludzka”. **Runda 4 (czeka na akceptację):** `docs/mockups/volt-ui-4.svg`, generator
  `python3 tools/ui/mockups_v4.py`. Doszło: ciepły grafit i złamana biel, przygaszone kolory sekcji, ziarno na
  powierzchniach, krawędź światła na panelach i ekranach, cieniowane główki pokręteł z obwódką, podziałka na
  dużych pokrętłach (Cutoff ze skalą 20–20k), jednostki mniejsze niż liczby, ikony kształtu LFO i typu filtra,
  bursztynowa kropka pod pokrętłem sterowanym przez makro. Po akceptacji: wdrożenie w kodzie i prawdziwe zrzuty.
- **Wdrożenie (po „wdrażaj”):** makieta 4 przeniesiona do pluginu. Zmienione pliki: `Source/ui/VoltLookAndFeel.*`
  (paleta, pokrętła z podziałką i znacznikiem makra, style przycisków tab/seg/preset/arrow/ghost), `Controls.*`
  (`ValueText` – jednostka mniejsza od liczby, `Knob` w rozmiarach Small/Medium/Hero, `MacroCell`), `Views.h`
  (wavetable jako powierzchnia, `EnvelopeView`, `LfoView`, `LevelMeter`), `PluginEditor.*` (nowy układ SYNTH,
  ziarno, znaczniki makr, cele makr), `PresetBar.*` (znak VOLT, okno „O programie” po kliknięciu znaku),
  `PluginProcessor.*` (szczyt wyjścia dla miernika). Czcionka: Oxanium Medium + SemiBold
  (`resources/fonts`, instancje statyczne z pliku zmiennego, OFL), Inter usunięty.
  Zmiany funkcjonalne w UI: obwiednie Amp/Filter/Mod/Pitch w jednym panelu z przełącznikiem i wykresem; LFO 1/2
  (kształt, Sync, Rate/podział, Depth) także na zakładce SYNTH (Retrigger tylko na MODULATION); miernik poziomu;
  podpis celu pod makrem; bursztynowa kropka przy pokrętle sterowanym makrem. Parametry i brzmienia bez zmian.
  Weryfikacja lokalna: build OK, testy 46/0, render 136/136, zrzuty `docs/ui-*.png` z `VOLT_Render --snapshot`.
  Nie sprawdzono (wymaga Windows): obsługa myszą, okno „O programie”, wygląd przy skalach innych niż 100%.
- Ustalenie z wcześniejszej przebudowy UI nadal obowiązuje: nazwa parametru nad pokrętłem, wartość zawsze pod
  nim, normalna pisownia etykiet (nie drobne wersaliki).

**Etap C – stan:**
- Zrobione: pitch bend (parametr `bend_range`, pokrętło **Bend** w VOICE), sustain CC64 (także z arpeggiatorem),
  testy `tests/ExpressionTests.cpp`. Lokalnie: build OK, testy 52 grupy / 0 błędów, render 136/136 bez zmian
  (0,0 LU różnicy względem stanu sprzed etapu C).
- Presety: 14 nowych wersji w `tools/presets/generate_fixes.py` → `tools/presets/fixes/`, render 14/14,
  `similarity.py` 14/14 „ok”. Strona porównania stara/nowa: https://claude.ai/artifact/PSiYaBRbHaaxroPi6uSd9V
  (baza artefaktu, kolekcja `verdicts`, dokument = nazwa pliku, pole `verdict`: `new` / `old` / `neither`, `note`).
- Użytkownik: „dodaj wszystkie” – 14 nowych wersji w `selection.json` → `fixes_accepted`, biblioteka przebudowana.
  Render 136/136 (mediana −15,0 LUFS). Mediany odległości do najbliższego sąsiada po etapie C: Arp 1.71 (było 1.36),
  Bass 1.66 (1.70), Guitar 1.65 (1.93), Lead 1.40 (1.38), Keys 1.24 (1.26), Brass 1.22, Pad 1.21, FX 2.70.
  Cel ≥ 1.6 w każdej kategorii – Keys, Pad, Brass i Lead nadal poniżej; to zadanie dla nowych partii w etapie D.
- **Decyzja użytkownika (2026-11-12) – wybór w etapie D:** lekki wybór. Partie po 20–30 presetów jednej kategorii,
  każdy domyślnie zostaje; użytkownik obiektywnie odrzuca słabe („Usuń”) i pilnuje, żeby nie były takie same
  („Za podobny do…” – wskazuje, do którego presetu). Strona odsłuchu ma więc dla każdego presetu: odtwarzacz,
  „Usuń”, „Za podobny do…” (wybór presetu z listy), pole na uwagę; brak kliknięcia = zostaje. Propozycja Claude:
  lekki wybór – partie 20–30 presetów z jednej kategorii, domyślnie „zostaw”, użytkownik zaznacza tylko
  „usuń”/„popraw”.
- Po wyborze: wpisać decyzję do DECISIONS.md i wdrożyć w `Source/ui/*` + `PluginEditor.*` (logo, typografia,
  pokrętła, wykresy obwiedni i LFO, przeglądarka presetów, okno „O programie” z licencją), zrzuty przez
  `VOLT_Render --snapshot`, odświeżyć `docs/ui-*.png` i README.
- **A. Neutralizacja:** usunąć wszystkie odwołania do artystów/albumów (tagi presetów, docs/PRESETS.md, README,
  grupy w generatorach); neutralne tagi stylu (Dark, Bright, Aggressive, Vintage, Cinematic, Lo-Fi, House, Trap,
  Synthwave…); lista presetów wg kategorii brzmienia (kategorie „wg ery” odpadają). Test zakazanych nazw zostaje.
- **B. Profesjonalny wygląd:** kierunek „nowoczesny, w stylu Serum 2” (ciemny, czysty, dużo wizualizacji: wavetable,
  obwiednie, LFO, wyrazisty akcent) – inspiracja ogólnym stylem, bez kopiowania grafik/układu. Najpierw 2–3 makiety,
  potem wdrożenie (logo, typografia, pokrętła, grafiki obwiedni i LFO, przeglądarka presetów, okno „O programie”).
- **C. Silnik:** pitch bend + sustain (CC64) – niezbędne dla publicznego wydania; poprawa 14 presetów „Popraw”.
- **D. Biblioteka ok. 300 presetów** partiami wg kategorii, z odsłuchem i wyborem przez użytkownika. Proponowane
  kategorie: Bass, Lead, Pluck, Bell & Mallet, Keys & Piano, Pad, Strings, Brass, Guitar, Arp & Sequence, Organ,
  Vocal & Choir, FX. Plucki/belle/mallety/gitary na oscylatorze String i trybach warp. ~135 obecnych zostaje.
- **E. Wydanie:** instalator Windows, podpis kodu (koszt), wersja 1.0.0, instrukcja, plik licencji (JUCE, Inter OFL),
  testy w kilku DAW i betatesty.
- **F. Później:** presety do Vitala, instrumenty z sampli.
- **Decyzje użytkownika (2026-11-12):**
  - Licencja: open source na AGPLv3, darmowe, bez rejestracji. Od innych na start przyjmujemy tylko presety,
    bez kodu. Nazwa i logo nie są objęte licencją. (Zrobione w etapie A: `LICENSE`, `CONTRIBUTING.md`, README.)
  - Platformy: 1.0 tylko Windows (VST3 + Standalone). Linux zostaje w CI do testów, bez paczki do pobrania.
    macOS po wydaniu jako wersja eksperymentalna, gdy znajdzie się tester z Makiem.
  - GitHub: zaplecze na kod i automatyczne budowanie paczki; repo prywatne do 1.0, potem publiczne z ochroną `main`.
- **Otwarte:** nazwa (VOLT koliduje z interfejsami Universal Audio Volt – użytkownik zajmie się tym później).
- **Wzorce brzmień od użytkownika** (punkt odniesienia dla partii presetów, tylko opis charakteru, nic nie
  kopiujemy) są w `docs/SOUND_REFERENCES.md`: 2 z Vitala (Keys) i 9 z Zenology (nagranie analizowane 2026-11-12,
  pliku nie ma w repo). Wspólny mianownik: ciepło i ciemno, energia głównie poniżej 1 kHz, sporo phasera,
  tremola i echa. Pierwsza partia w etapie D to Keys.
- **Jakość presetów (2026-11-12):** `VOLT_Render` zapisuje w `report.json` odcisk barwy każdego presetu (`features`:
  16 pasm, jasność, ruch barwy, atak, sustain, szumowość, szerokość, udział basu). `tools/presets/similarity.py`
  wskazuje pary zbyt podobnych presetów i odrzuca kandydatów bliższych niż 1.2 bibliotece lub sobie nawzajem.
  Stan biblioteki 136: 49 par < 1.2, mediana odległości do najbliższego sąsiada 1.39 (Pad 1.22, Brass 1.22,
  Keys 1.26, Arp 1.36, Lead 1.39, Bass 1.82, Guitar 1.97); cel ≥ 1.6 w każdej kategorii. Najbliższe pary:
  Sunset Pad ~ Studio Poly Pad 0.53, Grey Sky Strings ~ Sweet Analog Pad 0.55, Disco Strings ~ Vintage String
  Ensemble 0.59, Grand Synth Keys ~ House Piano Stab 0.67. Zasady projektowania i obowiązkowy proces
  (plan partii → generator → render → similarity → trym → odsłuch) są w skillu `.claude/skills/preset-design/SKILL.md`.
- Commity samej dokumentacji mają `[skip ci]`, żeby nie zużywać minut GitHub Actions.

## Mapa kodu
- `Source/Params.*` – tabela parametrów (ID, zakresy, domyślne), snapshot dla wątku audio.
- `Source/dsp/Wavetables.*` – generatory tablic i mipmapy.
- `Source/dsp/Voice.*`, `VoiceFilter.h`, `Modulators.h` (ADSR, LFO), `DspUtil.h`, `Formants.h`.
- `Source/dsp/SynthEngine.*` – MIDI, alokacja głosów, modulacja globalna, łańcuch FX.
- `Source/PresetManager.*` – presety fabryczne (BinaryData) i użytkownika, stan presetu w drzewie APVTS.
- `Source/ui/*`, `Source/PluginEditor.*` – interfejs; makiety i ich generatory: `docs/mockups/`, `tools/ui/`.
- `tests/` – testy jednostkowe (JUCE UnitTest), `tools/render/` – renderer presetów.

## Etap D – stan (2026-11-12)
- Partia **Keys 1**: `tools/presets/generate_batch_keys1.py` → `tools/presets/batches/keys1/` (23 presety),
  render 23/23 (−15,0 LUFS, limiter ≤ 2,5 dB), `similarity.py` 23/23 „ok” (najbliżej: Dusty Upright ~ Reed Electric
  Piano 1.23, Phaser Tremolo EP ~ Honky Tonk Bar 1.31).
- Strona odsłuchu: https://claude.ai/artifact/5h4y2WKbszZwnf4XKTw8e1 (baza artefaktu, kolekcja `keys1`, dokument =
  nazwa pliku, pola `verdict`: "" = zostaje, `remove`, `similar` + `similarTo`, `note`).
- DO ZROBIENIA po odsłuchu: wpisać do `selection.json` (`batches.keys1.removed`, `.similar`), dopisać obsługę partii
  w `build_library.py` (import `generate_batch_*`, kandydaci bez usuniętych), przebudować bibliotekę, render,
  `similarity.py` na całości, mediany tutaj; presety „za podobny” – zmienić albo usunąć wg uwagi.
- (Zrealizowane częściowo, patrz „Etap D – 300 presetów”.) Kolejne partie (propozycja kolejności): Bass, Pad, Lead, Pluck/Bell, Organ (osobna kategoria w pluginie?),
  Vocal & Choir, Strings, Brass, Guitar, Arp, FX. Nowe kategorie wymagają zmiany `PresetManager::categories()` i
  `CATEGORY_ORDER` w `build_library.py`.

## Etap D – 300 presetów (2026-11-12)
- Keys 1 po odsłuchu: odrzucony tylko Barking Tine EP (`selection.json` → `batches.keys1.removed`).
- Użytkownik: „dorób do 300: gitary, plucki, pady, belle, ogólne instrumenty”. Nowe kategorie w pluginie: **Pluck,
  Bell, Strings, Woodwind** (`PresetManager::categories()`, frazy testowe w `VOLT_Render`: Pluck – melodia
  krótkich nut, Bell – trzy nuty + akord, Woodwind – linia legato, Strings – akord jak Pad/Keys).
- Partie (każda: render 100 %, `similarity.py` 100 % „ok”, zakresy parametrów sprawdzane przy generowaniu):
  `guitar2` 26, `pluck1` 31, `bell1` 25, `pad2` 28, `orch1` 32 (15 Strings + 17 Woodwind) = 142.
  Wspólny kod: `tools/presets/batch_common.py`; generatory `generate_batch_<nazwa>.py`.
- Biblioteka: **300 presetów** (Init + 299). Wszystkie partie są w `build_library.py` → `BATCHES` (domyślnie
  zostają); pięć dawnych padów smyczkowych przeniesione do Strings (`RECATEGORISE`). Render 300/300,
  testy 53/0. Liczności: Bass 33, Lead 24, Guitar 36, Pluck 31, Keys 47, Bell 25, Pad 46, Strings 20, Brass 10,
  Woodwind 17, Arp 8, FX 3. Mediany odległości do najbliższego sąsiada (cała biblioteka): Pluck 1.68,
  Woodwind 1.81, Arp 1.55, Guitar 1.47, Bell 1.45, Strings 1.45, Bass 1.39, Keys 1.35, Pad 1.34, Lead 1.27,
  Brass 1.23, FX 2.24.
- Strona odsłuchu 142 nowych: https://claude.ai/artifact/S4h6gjhRp6NKfRxZSVyQrK (kolekcja `d300`, dokument =
  nazwa presetu z `_`, pola `verdict` "" / `remove` / `similar`, `similarTo`, `note`, `batch`).
- DO ZROBIENIA po odsłuchu: nazwy z `remove` i `similar` wpisać do `selection.json` → `batches.<batch>`, przebudować
  bibliotekę (spadnie poniżej 300 – dorobić brakujące w kolejnej partii), render, similarity, commit.
- Pomysły na kolejne partie: Bass 2, Lead 2, Brass 2, Organ jako osobna kategoria, Vocal & Choir, Arp 2, FX 2.

## Etap D – uwagi użytkownika po odsłuchu 300 i partia House / Hip-Hop (2026-11-12)
- Odsłuch 142 (`d300`): usunięte Doom Drop Guitar, Octave Shimmer Pad („piszczy”), Xylophone Bright; Vibraphone
  Motor „za podobny” do Rosewood Marimba.
- Uwagi ogólne użytkownika: za mało do house i hip-hopu; za dużo lo-fi i brzmień „jak w grze metroidvania”;
  zredukować instrumenty typu flet; całość „nijaka i tylko ciepła”. Na tej podstawie Claude usunął dodatkowo
  21 presetów (lista w `selection.json` → `batches.*.removed`, komentarz w polu `comment`): flety i ludowe dęte
  (Pan Flute, Piccolo, Alto Flute, Recorder, Ocarina, Shakuhachi, Drone Chanter), brzmienia „growe” i lo-fi
  (Quantize Chip Pluck, Wind-Up Music Box, Toy Bell Piano, Sleigh Bell Shimmer, Crushed Bell, Clock Chime,
  Detuned Lo-Fi Pluck, Gated Glitch Pluck, Tin Can Pluck, Bedroom Lo-Fi Guitar, Tape Hiss Pad, Cassette Keys,
  Dusty Upright, Tape Wobble Piano). Smoky Lounge Keys zostaje (wzorzec użytkownika).
- **Nowa partia `urban1` (35)**: House 17 (organ bass, rolling tech bass, bass-house wobble, future house bass i
  pluck, house piano, dub stab, garage organ, rave stab, vocal chop, hoover, festival saw, tech perc, disco
  strings, groove arp, riser, downlifter) i Hip-Hop/trap 18 (808 punch / sliding / rage, G-funk bass, sinister,
  rage, plugg, portamento whine i hyper pluck leady, dark trap piano, boom bap EP, rap stab, Detroit pluck, trap
  arp, trap bell, brass stab, choir hit, vocal pad). Jasno, sucho, twardy atak, pump przy house. Render 35/35,
  similarity 35/35 (względem obecnej biblioteki). Odrzucone przez podobieństwo: Drill Slide Bass (≈ Tom Drop 808),
  Garage Reese, Deep House Pad, Horn Section Hit, Rap String Stab.
- Tagi: presety z tagiem 808 dostają też „Hip-Hop”; trap ma tagi Hip-Hop + Trap, rave – House + Rave.
  Liczności tagów: House 51, Hip-Hop 25, Trap 8.
- Biblioteka: **310 presetów**, render 310/310, testy 53/0. Kategorie: Bass 41, Lead 32, Guitar 34, Pluck 30,
  Keys 51, Bell 19, Pad 45, Strings 21, Brass 11, Woodwind 10, Arp 10, FX 6.
- Strona odsłuchu `urban1`: https://claude.ai/artifact/58GuSBQCQfgQCrfELBB3m4 (kolekcja `urban1`).
- Klawiatura do grania została dodana do pluginu przez pomyłkę i usunięta: użytkownik chciał klawiatury do
  przeglądania dźwięków na stronie odsłuchu, nie w pluginie.

## Naprawa różnorodności (2026-11-12, w toku)
- Problem wg użytkownika: presety brzmią prawie tak samo, prawie wszystko jest spokojne/„soft”; ma być rozrzut od
  spokojnych po mocno uderzające, nastroje Dark / Medium / Soft / Sad / Aggressive, soft najwyżej 30 %.
- Pomiar: `tools/presets/energy_mood.py` liczy poziom energii 1–5 (jasność względem kategorii, twardy atak,
  przester, gęstość, pump, ruch, minus pogłos i powolne narastanie) i proponuje nastrój. Stan 309 presetów:
  energia 1–5 = 125 / 45 / 59 / 40 / 40 (40 % bardzo spokojnych), Soft 37 %, Sad 6 %.
- `VOLT_Render --samples` zapisuje dla każdego presetu nuty C2, C3, C4, C5 (po 2,5 s) do `samples/*.flac` –
  materiał do klawiatury na stronie przeglądu.
- Strona przeglądu: https://claude.ai/artifact/BMQsLcGGQxdgUVt3BDU7mi – każdy preset do zagrania myszą i z
  klawiatury komputera, energia, nastrój (do zmiany), propozycja usunięcia (78: najspokojniejsze z bliskim
  sąsiadem, min. 2 spokojne na kategorię zostają, chronione wzorce użytkownika), „Brzmi jak…”. Kolekcja `review`
  (dokument = numer wiersza, pola `remove`, `mood`, `like`, `note`, `name`).
- Po zatwierdzeniu: usunąć zaznaczone, zapisać nastrój każdego presetu (tag + pole), nowa partia głównie Sad /
  Dark / Aggressive / Medium na poziomach 3–5 do ok. 280, filtr Mood w pluginie, test „soft ≤ 30 %”, zasady
  w skillu preset-design.
- **Stan na koniec sesji 2026-11-12:** diagnoza i plan naprawy w `docs/DIAGNOZA_2026-11-12.md` – zacząć od niego.
  Propozycja usunięć (78, jeszcze niezastosowana) w `tools/presets/review_2026-11-12.json`. Biblioteka w repo:
  310 presetów (bez zmian względem commitu z partią `urban1`).


## Naprawa różnorodności i perkusja (2026-11-13)
Plan z `docs/DIAGNOZA_2026-11-12.md` wykonany w całości, plus perkusja na prośbę użytkownika.
- **Silnik:** przełącznik **Keep Low** w Distortion (`dist_keep_low`, zwrotnica Linkwitz-Riley ~160 Hz: przester tylko
  góry, sub czysty; test: przesterowany sinus 50 Hz ma 0,0001 energii harmonicznych zamiast 0,22). LFO do 100 Hz.
  Kategoria **Drums**, pole **mood** w presetach, filtr **Mood** w pasku presetów, nastrój w oknie zapisu.
- **Pomiar z dźwięku:** renderer liczy udział pasma 1–8 kHz, „air”, gęstość harmonicznych, crest i ostrość ataku;
  `energy_mood.py` ocenia energię z audio (nie z ustawień) i z bezwzględnej jasności. Wniosek: z 309 starych
  presetów tylko ~37 naprawdę mocno uderzało; „przesterowane” basy za ciemnym filtrem wychodzą spokojne.
- **Głośność wg nastroju:** Aggressive +2,5 dB … Soft −2 dB wokół −15 LUFS; Aggressive może dociskać limiter do 5 dB.
  Perkusja normalizowana szczytem (−1 dBFS) jak sample one-shot – renderer sprawdza dla niej szczyt zamiast LUFS.
- **Usunięcia:** 77 spokojnych z bliskim sąsiadem (propozycja ze strony przeglądu; Acid Bath i Fingerpicked
  Pattern Guitar zostały na życzenie użytkownika) – `selection.json` → `review_2026_11_12_removed`.
- **Nastroje starych presetów:** `tools/presets/moods.json` (pomiar + ręczna korekta, np. czyste dzwonki FM nie są
  Aggressive, miękkie EP nie są Dark). Nowe partie mają nastrój w generatorze.
- **Nowe partie** (strona odsłuchu z klawiaturą: https://claude.ai/artifact/N9pTkbj8dkoWF9VMLTgx6J, kolekcja
  `review2`, wszystkie domyślnie zostają):
  - `drums1` (32): 8 kicków, 6 werbli, 5 klaśnięć (prawdziwe 2–4 uderzenia: LFO 90 Hz bramkowany Mod Env),
    7 hi-hatów, 4 shakery/tamburyn, wood block, finger snap – house i hip-hop/trap.
  - `hard1` (30, 28 w bibliotece; 2 prawie-duplikaty odrzucone): 808 clipped/fold/drill/crushed, basy z Keep Low,
    leady sync/fold/bitcrush/formant, staby, gitary, arpy, FX. 19/30 na energii 4–5.
  - `basics1` (29): czysty sub, zwykłe 808, saw/square/supersaw/pulse lead, piano, EP, organy, pady, smyczki, brass.
    Zwolnione z wymogu „oryginalności” (bliscy sąsiedzi zapisani w `selection.json`).
  - `sad1` (21): smutne/mroczne do emocjonalnego rapu i trapu, energia 1–4.
- **Każdy nowy preset ma makro 1 „Energy”** (drive + jasność) – ten sam preset od spokojnego do mocnego.
- **Biblioteka: 342 presety** (+ Init). Energia 1–5 = 61 / 69 / 105 / 59 / 48 (18 / 20 / 31 / 17 / 14 %).
  Nastroje: Medium 39 %, Dark 23 %, Aggressive 17 %, Soft 14 %, Sad 7 %. Test pilnuje Soft ≤ 30 %.
- **Do sprawdzenia przez użytkownika:** odsłuch nowych partii na stronie (Usuń / nastrój / Brzmi jak…), szczególnie
  perkusja (kicki, klapy) i presety oznaczone „Blisko”. Sad jest wciąż najmniejszy (7 %) – kolejna partia albo
  zmiana nastroju części Dark na Sad po odsłuchu.
- **Odsłuch użytkownika (2026-11-13):** „dobrze się słucha”, „trochę za dużo sad, reszta okej”. Usunięte z partii
  hard1 na stronie: Rage Sync Screamer, Shouting Formant Lead, Siren Riser → biblioteka 339 presetów.
  Perkusja strojona pod C3 = C4 w FL Studio (FL liczy oktawy o jedną wyżej, środkowe C to C5).
- **Biblioteka zamknięta (2026-11-13):** ostatni odsłuch całości (https://claude.ai/artifact/9tbnCmuGkTDJETBNWieChi,
  kolekcja `review3`). Usunięte: Acid Burn Bass, Bass House Wobble, Static Throat, Clockwork Arp → **335 presetów + Init**.
  Church Bell Toll – notatka użytkownika „zajebiste” (zapisane w `selection.json`). Następny etap: E – wydanie.

## Optymalizacja CPU (2026-11-13)
- `VOLT_Render --bench`: ranking CPU wszystkich presetów (akord 8 nut + bezczynność), wynik w `docs/CPU.md`.
  Granie: mediana 1,8 %, najcięższy 5 % jednego rdzenia (Xeon 2,1 GHz) – bez problemu dla słabych laptopów.
- Uśpienie bezczynnego pluginu: koszt bezczynnej instancji 0,45 % → 0,04 % (mediana). Render bez zmian.
- Do sprawdzenia przez użytkownika: CPU okna pluginu (oscyloskop, mierniki) w FL Studio na słabszym laptopie.

## Instalator (2026-11-13)
- `installer/VOLT.iss` (Inno Setup), budowany w CI na Windowsie → artefakt `VOLT-windows-installer`
  (`VOLT-<wersja>-Setup.exe`). Wersja testowa 0.9.0. Kreator po angielsku, instaluje tylko VST3 do
  `Common Files\VST3` (aplikację Standalone użytkownik odrzucił; nie trafia do instalatora ani paczki ZIP).
- Ostrzeżenie SmartScreen bez podpisu: na razie zostaje; ewentualnie informacja na stronie. Opcje na później:
  SignPath Foundation (darmowy dla open source), Certum Open Source Code Signing.
- Użytkownik zainstalował 0.9.0 – działa. Następne: efekty w stylu „lista efektów z włącznikami i panelami”
  (inspiracja Vitalem, bez kopiowania) – najpierw makiety.

## Efekty jak rack (2026-11-13)
- Makiety: https://claude.ai/artifact/2CEEDny2kbQquTsLittGkz – użytkownik wybrał wariant A (lista + panele) z
  przeciąganymi punktami na wykresach.
- Silnik: 10 efektów z włącznikami i zmienną kolejnością (`fx_*_on`, `fxOrder` w stanie / `fx_order` w presecie):
  Distortion, Chorus, Phaser, Flanger (osobno, mogą grać naraz), Filter (SVF LP/HP/BP/Notch), EQ (low shelf, peak
  z Q, high shelf), Pump, Delay, Reverb (+ Low Cut / High Cut ogona), Compressor (Squash + próg/ratio/attack/
  release/gain). Wyłączony efekt wycisza się płynnie i nie kosztuje CPU.
- Zgodność: stare presety (format 1) i projekty (bez `fx_dist_on`) są przerabiane przy wczytaniu
  (`PresetManager::migrateLegacyFx`, ta sama reguła w `batch_common.modernize_fx`). Presety fabryczne zapisane
  w formacie 2. Render całej biblioteki przed/po: różnica ≤ 3·10⁻⁵ (1 LSB 16 bit) – brzmią tak samo.
- Błąd znaleziony i naprawiony w trakcie: nowe presety bez włączonego przesteru były brane za stare (migracja
  wyłączała chorus) → rozpoznawanie po numerze formatu; test regresji w `tests/RackTests.cpp`.
- Testy (68 grup, 0 błędów): kolejność, EQ (+6 dB = +6 dB, płaski = bypass), Filter (−40 dB 3,3 okt. nad
  cutoff), Compressor (4:1 przy −20 dB), barwa pogłosu, włączniki, migracja presetów i projektów, kolejność w
  presetach użytkownika, interfejs (przeciąganie punktu EQ i filtra, włącznik, zmiana kolejności). CI uruchamia
  testy pod xvfb.
- Do sprawdzenia przez użytkownika w FL Studio: przeciąganie punktów, zmiana kolejności, włączniki, automatyzacja
  nowych parametrów, otwarcie starego projektu z VOLT 0.9.0.

## Nowa nazwa: Vonar (2026-11-13)
- „VOLT” było zajęte w audio (interfejsy Universal Audio Volt, wtyczki Lunacy Volt i Air-G Volt, syntezator
  Volt od Numerical Audio). Użytkownik wybrał **Vonar** (sprawdzone: brak znaków towarowych VONAR w USA, brak
  produktu audio, brak firmy o tej nazwie). Logo: wariant A z makiety https://claude.ai/artifact/BKk7ExiM8YaXpNDpfZk2Fv
  (litery kreską, „O” = pokrętło z bursztynową wskazówką).
- Zmienione: nazwa w hoście (`PRODUCT_NAME`, `getName`), producent „Vonar”, logo w pasku, okno „O programie”,
  folder presetów użytkownika `%APPDATA%\Vonar\Presets` (przy pierwszym uruchomieniu kopiuje presety ze starego
  folderu VOLT), instalator `installer/Vonar.iss` → `Vonar-<wersja>-Setup.exe` (ta sama AppId = aktualizacja,
  usuwa stary `VOLT.vst3`), artefakty CI `Vonar-*`, README, CONTRIBUTING, zrzuty ekranu.
- Bez zmian (zgodność): kody pluginu `Vltx`/`Vlt1` (VST3 ID), typ drzewa stanu „VOLT”, wewnętrzne nazwy w kodzie
  (namespace `volt`, cele CMake `VOLT_*`), więc projekty FL Studio z VOLT dalej się otwierają.
- Do sprawdzenia przez użytkownika: instalacja nowym instalatorem na komputerze z VOLT, czy FL pokazuje tylko
  Vonar i czy stary projekt się otwiera.
- **Mniej Sad (2026-11-13):** użytkownik: „za dużo Sad, ale nie redukuj o więcej niż 5 %”. Usunięte 8 presetów Sad –
  z każdej bardzo podobnej pary bliższy (Emo Saw Lead, Weeping Guitar, Grieving Strings, Audible 808 Glide, Rainy Day
  EP, Empty Room Pad, Winter Choir, Ghost Vocal Pad); Lilting Voice Pad (wzorzec użytkownika) zostaje. Biblioteka
  335 → **327** (−2,4 %), Sad 7,5 % → 5,2 %.

## Podpis i prywatność (2026-11-13)
- Podpis: **„Vonar by Xami”** (pseudonim użytkownika). Bez prawdziwego imienia, wieku i miasta w czymkolwiek
  publicznym. README: copyright Xami + sekcja „How Vonar was made” (pomoc AI Claude); okno „O programie” i wydawca
  w instalatorze: Xami.
- Zrobione: login GitHub `itsXami`; adres e-mail usunięty z historii (`main` i `feature/volt-synth` przepisane i
  wypchnięte za zgodą użytkownika; pliki identyczne). Stara kopia PR-a (`refs/pull/1/head`) zostaje po stronie
  GitHuba – użytkownik zdecydował, że nie zgłasza tego do pomocy GitHuba.
- Zalecone użytkownikowi: „Keep my email addresses private” i blokada pushy z adresem.

## Etap E – wydanie 1.0.0 (2026-11-13)
- Wersja **1.0.0** (`CMakeLists.txt`, okno „O programie”, nazwa instalatora).
- `installer/THIRD-PARTY-NOTICES.txt` (EN): JUCE (AGPLv3), VST3 SDK (MIT, znak towarowy Steinberg), Oxanium (OFL 1.1).
  Instalator kopiuje go z licencją do `Program Files\Vonar`; ZIP zawiera `Vonar.vst3`, `LICENSE.txt` i ten plik.
- CI: build Windows bez Standalone (zgodnie z decyzją „b”); po opublikowaniu GitHub Release CI buduje pliki od nowa
  i sam dołącza `Vonar-1.0.0-Setup.exe` oraz `Vonar-1.0.0-Windows-x64.zip`.
- Opis wydania (EN): `docs/releases/v1.0.0.md`. README: instalacja ze strony Releases + uwaga o SmartScreen.
- Kolejność do końca: zielone CI → squash-merge PR #1 do `main` → użytkownik tworzy Release `v1.0.0` z `main`
  (opis z `docs/releases/v1.0.0.md`) → CI dołącza pliki → repo publiczne.
