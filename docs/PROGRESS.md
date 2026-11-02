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
| 3 | Modulacja, makra, arpeggiator, efekty | – |
| 4 | Interfejs i przeglądarka presetów | – |
| 5 | Render CLI i testy | – |
| 6 | 121 presetów z korektą wg raportów | – |
| 7 | README (PL) i docs/PRESETS.md | – |

## Dziennik
- Etap 1: szkielet buduje się lokalnie na Linuksie (GCC 13, Ninja); pluginval strictness 5 lokalnie: SUCCESS.
- Etap 1: CI run 41461908895 – oba joby zielone, pluginval na Windows uruchomiony, artefakt VOLT-windows-x64 (~6 MB).
- Etap 2: `Source/dsp/` – Wavetables (32 tablice), Voice (2 osc + unison 8, sub, szum, filtr, ADSR×2, pitch env,
  LFO per głos), VoiceFilter (7 typów), SynthEngine (16 głosów, Poly/Mono/Legato, glide, macierz modulacji 8 slotów).
  Arpeggiator.h i Effects.h to na razie zaślepki (etap 3). Testy: `tests/DspTests.cpp`.

## Mapa kodu
- `Source/Params.*` – tabela parametrów (ID, zakresy, domyślne), snapshot dla wątku audio.
- `Source/dsp/Wavetables.*` – generatory tablic i mipmapy.
- `Source/dsp/Voice.*`, `VoiceFilter.h`, `Modulators.h` (ADSR, LFO), `DspUtil.h`, `Formants.h`.
- `Source/dsp/SynthEngine.*` – MIDI, alokacja głosów, modulacja globalna, łańcuch FX.
- `tests/` – testy jednostkowe (JUCE UnitTest), `tools/render/` – renderer presetów.
