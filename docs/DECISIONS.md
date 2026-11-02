# VOLT – decyzje projektowe

Każdy wpis: decyzja → powód. Najnowsze na dole.

## Etap 1 – szkielet

- **JUCE 8.0.15 przez FetchContent (`GIT_TAG 8.0.15`, shallow).** Najnowszym tagiem w repozytorium JUCE jest już 9.0.5,
  ale specyfikacja wymaga JUCE 8, więc przypinamy najnowszy stabilny tag gałęzi 8.x. Lokalnie można podać
  `-DFETCHCONTENT_SOURCE_DIR_JUCE=<ścieżka>`, żeby nie klonować JUCE przy każdym czystym buildzie.
- **Biblioteka `VoltCore` typu INTERFACE** zawiera wszystkie źródła z `Source/` i moduły JUCE. Linkują ją plugin,
  `VOLT_Tests` i `VOLT_Render`, więc testy i renderer korzystają z dokładnie tego samego procesora,
  parametrów, presetów i DSP co wtyczka (koszt: JUCE kompiluje się osobno dla każdego celu).
- **Statyczny runtime MSVC** (`/MT`) – VST3 nie wymaga zainstalowanego VC++ Redistributable w systemie użytkownika FL Studio.
- **`JUCE_WEB_BROWSER=0`, `JUCE_USE_CURL=0`** – brak zależności od WebKit/curl, prostszy build na Linuksie i mniejszy plugin.
- **Bez LTO** – krótszy czas CI; zysk wydajności dla tego projektu jest pomijalny.
- **Kody pluginu:** producent `Vltx`, plugin `Vlt1`, firma „VOLT Instruments”. Kody muszą pozostać stałe,
  bo FL Studio identyfikuje po nich wtyczkę w zapisanych projektach.
- **Na Windows CI buduje tylko `VOLT_VST3` i `VOLT_Standalone`** (`-DVOLT_BUILD_TOOLS=OFF`); testy i render presetów
  działają na Linuksie, bo wynik DSP jest niezależny od platformy, a skraca to czas zadania Windows.
- **Artefakt `VOLT-windows-x64`** jest uploadowany jako katalog `dist/` zawierający `VOLT.vst3/` i `VOLT.exe`.
  GitHub pakuje artefakt do pliku `VOLT-windows-x64.zip`, więc po pobraniu użytkownik dostaje zip z folderem `VOLT.vst3`
  (bez „zipa w zipie”). Analogicznie `VOLT-preset-previews.zip`.
- **pluginval 1.0.4** (ostatnie wydanie) z `--strictness-level 5 --validate-in-process`; na Linuksie pod `xvfb-run`,
  bo test edytora potrzebuje serwera X. Na Windows krok uruchamiany w bashu, żeby proces był synchronicznie oczekiwany
  i zwracał kod wyjścia.
- **Licencja JUCE:** JUCE 8 jest dostępny na AGPLv3 albo licencji komercyjnej/Starter. Repozytorium jest prywatne;
  przed publiczną dystrybucją binariów trzeba wybrać jedną z tych ścieżek (odnotowane w README).
