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

## Etap 2 – silnik

- **Pełna tabela parametrów od razu (108 parametrów, `Source/Params.cpp`).** ID są stringami (np. `flt_cutoff`,
  `oscA_pos`) z wersją 1 w `juce::ParameterID`. Enum `volt::P` jest tylko wewnętrznym indeksem; host i presety
  używają wyłącznie ID. Zdefiniowanie wszystkich parametrów w etapie 2 gwarantuje, że ID nie zmienią się w kolejnych etapach.
- **Unison: liczba głosów osobno dla Osc A i B (`oscA_voices`, `oscB_voices`), Detune i Spread wspólne
  (`uni_detune`, `uni_spread`).** Specyfikacja wymienia jedno główne pokrętło „Unison Detune”; wspólny Detune/Spread
  daje jedno pokrętło bez dublowania parametrów. Detune: przesunięcie skrajnych głosów = detune² półtonu (max ±100 ct).
- **Wavetable: 32 tablice × 32 klatki × 10 mipmap.** Mip *m* zawiera harmoniczne ≤ 512/2^m (rozmiar cyklu
  max(256, 2048/2^m) + próbka ochronna). Mip wybierany per głos/blok tak, by najwyższa harmoniczna była < Nyquist.
  Klatki budowane przez własne FFT (widmo → odwrotne FFT na mip), normalizowane do szczytu 1 na klatkę.
  Generowane raz na proces (~0,3 s, ok. 20 MB), współdzielone przez wszystkie instancje.
- **Odczyt wavetable: interpolacja liniowa w próbkach i między klatkami.** Test aliasingu (nuta 100, ~2,6 kHz, 44,1 kHz)
  daje najgorszy składnik nieharmoniczny ok. −59 dB.
- **Przetwarzanie w pod-blokach po 32 próbki (control rate).** Modulacje, obwiednia filtra, LFO i glide liczone są
  na granicach pod-bloków, a w środku interpolowane liniowo (inkrementy faz, pozycja wavetable, wzmocnienia, współczynniki
  filtra). Obwiednia amplitudy liczona per próbka. Zdarzenia MIDI dzielą pod-bloki → próbkowa dokładność.
- **Wygładzanie parametrów:** wszystkie parametry typu float wygładzane jednobiegunowo (τ = 12 ms) na pod-blokach,
  cutoff w domenie logarytmicznej (wysokość MIDI) – brak zipper noise przy automatyzacji.
- **Filtr:** SVF TPT (LP12/HP/BP/Notch), LP24 = dwa SVF (rezonans na drugim), Ladder = 4-biegunowy ZDF z liniowym
  rozwiązaniem pętli i nasyceniem `tanh` na wejściu sprzężenia (k = 3,96·res, częściowa kompensacja basu),
  Formant = 3 równoległe BP z tabelą samogłosek A-E-I-O-U (podręcznikowe wartości formantów głosu basowego).
  W trybie Formant Cutoff przesuwa formanty (×0,5…×2 wokół 1 kHz), Resonance zawęża pasma.
- **Drive filtra** wchodzi płynnie od zera (mieszanie czystego i `tanh`), z kompensacją głośności.
- **Obwiednie:** atak liniowy, decay/release wykładnicze (czas = spadek o 40 dB); retrigger startuje od bieżącego
  poziomu (bez kliknięć przy kradzieży głosu i w trybie Mono).
- **Sub** podąża za wysokością Osc A (oktawa/półtony/dostrojenie/modulacje) o oktawę niżej.
- **Mono:** last-note priority, retrigger i glide zawsze. **Legato:** bez retriggera i z glide tylko przy nakładających
  się nutach. **Poly:** glide od ostatnio zagranej nuty; kradzież: najstarszy głos w release, inaczej najstarszy.
- **Bez obsługi pitch bend i pedału sustain (CC64)** – nie ma ich w specyfikacji. Obsługiwane są Mod Wheel (CC1),
  Aftertouch (channel i poly) jako źródła modulacji oraz CC120/CC123 (All Sound/Notes Off) dla higieny transportu.
