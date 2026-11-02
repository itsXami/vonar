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
| 1 | Szkielet CMake + JUCE, pusty plugin, CI, artefakt Windows | w toku |
| 2 | Silnik: oscylatory, głosy, filtr, obwiednie | – |
| 3 | Modulacja, makra, arpeggiator, efekty | – |
| 4 | Interfejs i przeglądarka presetów | – |
| 5 | Render CLI i testy | – |
| 6 | 121 presetów z korektą wg raportów | – |
| 7 | README (PL) i docs/PRESETS.md | – |

## Dziennik
- Etap 1: szkielet buduje się lokalnie na Linuksie (GCC 13, Ninja); pluginval strictness 5 lokalnie: SUCCESS.
