# VOLT – stan prac

Ten plik wystarcza, żeby nowa sesja mogła kontynuować pracę.

## Kontekst
- Repo: `jakubnikapiotr-design/vst`, branch roboczy: `feature/volt-synth`, PR do `main`.
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
| B. Profesjonalny wygląd | ⏳ układ wybrany (makieta 2); czekamy na wybór wykończenia 2A/2B (opis niżej); wdrożenie po wyborze |
| C. Silnik: pitch bend, sustain, 14 presetów „Popraw” | – |
| D. Biblioteka ok. 300 presetów (pierwsza partia: Keys) | – |
| E. Wydanie | – |

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
- Ustalenie z wcześniejszej przebudowy UI nadal obowiązuje: nazwa parametru nad pokrętłem, wartość zawsze pod
  nim, normalna pisownia etykiet (nie drobne wersaliki).
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
  kopiujemy) są w `docs/SOUND_REFERENCES.md`. Na razie dwa, oba dla Keys: miękkie elektryczne pianino z falującym
  chorusem; ciemne, ciepłe, lekko lo-fi barowe klawisze bez ostrego ataku. Pierwsza partia w etapie D to Keys.
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
- `Source/ui/*`, `Source/PluginEditor.*` – interfejs.
- `tests/` – testy jednostkowe (JUCE UnitTest), `tools/render/` – renderer presetów.
