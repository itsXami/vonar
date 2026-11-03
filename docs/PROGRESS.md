# VOLT – stan prac

Ten plik wystarcza, żeby nowa sesja mogła kontynuować pracę.

## Kontekst
- Repo: `jakubnikapiotr-design/vst`, branch roboczy: `feature/volt-synth`, PR do `main`.
- Specyfikacja: oryginalne polecenie użytkownika (syntezator wavetable VOLT, VST3 + Standalone, 121 presetów).
  Kluczowe wymagania są streszczone w sekcji „Checklista” poniżej.
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
  → `python3 tools/presets/generate_presets.py --trim render-out/report.json` → build → render (powtarzać do 121/121).

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
- Do zrobienia po wyborze użytkownika: usunąć „Usuń” z pierwszej partii, poprawić „Popraw”, dodać wybranych
  kandydatów do `presets/`, kategoria „Guitar” w pluginie, kategorie/filtr wg ery artysty w przeglądarce presetów,
  aktualizacja testów (liczność 121 przestanie obowiązywać), potem dalsze zmiany wyglądu.

## Silnik v2 + zakładki (na prośbę użytkownika)
- Warp (8 trybów) i typ String na oscylator, Comb+/Comb−, Mod Env, Random, 12 slotów, 8 nowych tablic, zakładki UI.
  Szczegóły i uzasadnienia w DECISIONS.md („Rozbudowa silnika”). Testy: `tests/EngineV2Tests.cpp`.
- Istniejące presety brzmią identycznie (render przed/po: 0,0 LU różnicy). Kandydaci z drugiej partii jeszcze nie
  korzystają z nowych funkcji – przy kolejnych presetach warto ich używać (warp, String, Comb, Random).
- Generator presetów zna nowe parametry (`generate_presets.py`: DEFAULTS, TABLES, SOURCES, DESTS, limit 12 slotów).

## Mapa kodu
- `Source/Params.*` – tabela parametrów (ID, zakresy, domyślne), snapshot dla wątku audio.
- `Source/dsp/Wavetables.*` – generatory tablic i mipmapy.
- `Source/dsp/Voice.*`, `VoiceFilter.h`, `Modulators.h` (ADSR, LFO), `DspUtil.h`, `Formants.h`.
- `Source/dsp/SynthEngine.*` – MIDI, alokacja głosów, modulacja globalna, łańcuch FX.
- `Source/PresetManager.*` – presety fabryczne (BinaryData) i użytkownika, stan presetu w drzewie APVTS.
- `Source/ui/*`, `Source/PluginEditor.*` – interfejs.
- `tests/` – testy jednostkowe (JUCE UnitTest), `tools/render/` – renderer presetów.
