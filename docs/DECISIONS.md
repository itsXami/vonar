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

## Etap 3 – modulacja, makra, arpeggiator, efekty

- **Macierz modulacji: 8 slotów (źródło, cel, ilość −1…1), obliczana per głos co 32 próbki.** Skale celów przy
  ilości 1: pitch ±24 st, cutoff ±60 st, pozostałe ±pełny zakres parametru (pozycje WT, rezonans, drive, formant,
  poziomy, panoramy, Distortion Drive, miksy FX). Cele „Pitch” = obie oscylatory (+sub), „Pitch A/B” = pojedyncza.
  Cele globalne (Distortion Drive, Dist/Mod FX/Delay/Reverb Mix) używają LFO w wersji free-running (globalnej),
  kontrolerów, makr oraz Filter Env/Velocity/Key Track najnowszego brzmiącego głosu.
- **„FX Mix” ze specyfikacji rozpisany na cztery cele:** Dist Mix, Mod FX Mix, Delay Mix, Reverb Mix.
- **LFO:** Retrigger = osobna faza per głos resetowana przy nucie; bez Retrigger wszystkie głosy dzielą jedno globalne LFO.
  Tempo sync przy grającym transporcie liczy fazę bezpośrednio z PPQ hosta (stała synchronizacja z taktem).
- **Arpeggiator** działa przed alokacją głosów (więc działa w Poly/Mono/Legato). Przy grającym transporcie siatka
  kroków liczona z PPQ hosta; przy zatrzymanym – kotwiczona w chwili pierwszego naciśnięcia (brak skróconego pierwszego kroku).
  Zdarzenia kroków i gate-off są próbkowo dokładne (silnik dzieli pod-bloki na granicach zdarzeń arpeggiatora).
- **Distortion:** 4× oversampling (`juce::dsp::Oversampling`, 2 stopnie half-band IIR) dla Soft/Tube/Hard/Fold;
  Bitcrush bez oversamplingu (aliasing jest tu efektem zamierzonym). Drive 0–36 dB z kompensacją głośności,
  Tone = filtr LP 600 Hz–19 kHz, filtr DC po kształtowaniu (Tube jest asymetryczny).
- **Mod FX:** Chorus (11 ms ± 6,5 ms, kanały w kwadraturze), Flanger (1,2–5,2 ms, sprzężenie 0,55–0,85),
  Phaser (6 all-passów, sprzężenie 0,55). Mix to crossfade dry/wet; dla phasera i flangera „wet” zawiera już
  sumę z sygnałem suchym, więc Mix 100% = najgłębszy efekt.
- **Pump:** obwiednia ducking zsynchronizowana z PPQ (1/2, 1/4, 1/8, 1/16), zjazd w 2% cyklu (bez kliku),
  powrót gładki do ~64% cyklu. Leży przed Delay/Reverb – ogony nie pompują.
- **Delay:** tylko tempo-sync (podziały 1/32…1/1, w tym triole i kropkowane), Stereo lub Ping-Pong,
  w pętli sprzężenia LP 7 kHz, HP 120 Hz i miękkie nasycenie (stabilny przy feedback 0,95).
- **Reverb:** `juce::Reverb` (algorytm Freeverb z JUCE), Size mapowany na roomSize 0,30–0,92 – górna granica
  ograniczona, żeby ogon zawsze zanikał (test: −70 dB po 8 s przy Size 100%).
- **Prawo miksu Delay/Reverb:** dry = min(1, 2·(1−mix)), wet = min(1, 2·mix) – przy 50% oba sygnały w pełni.
- **Squash:** 3 pasma (Linkwitz-Riley 150 Hz / 2,5 kHz), próg −8…−30 dB, ratio 1…6, wspólny make-up;
  przy dużym Amount ciche fragmenty mogą wyjść głośniej niż głośne (zachowanie typu „OTT”).
- **Output:** gain −24…+12 dB (wygładzany) + ochronny limiter szczytowy bez latencji (natychmiastowy atak,
  release 120 ms, sufit −0,5 dBFS, twarde obcięcie jako ostatnie zabezpieczenie i zerowanie NaN/Inf).
  Silnik raportuje maksymalną redukcję limitera – renderer presetów używa jej do kontroli gain stagingu.

## Etap 4 – interfejs i przeglądarka presetów

- **Jeden ekran 1000×620 w pikselach logicznych**, skalowany przez `AffineTransform` (75–200%): lista w pasku
  górnym albo przeciąganie narożnika (stałe proporcje). Wybrana skala zapisywana jest we właściwości stanu `uiScale`.
- **Styl:** ciemne panele, jeden kolor akcentu (bursztynowy `#FFB52E`), pokrętła rysowane wektorowo
  w `VoltLookAndFeel` (łuk wartości, dla parametrów symetrycznych od środka), bez bitmap.
- **Pokrętła (`FineSlider`):** przeciąganie względne (pion/poziom), **Shift** = ok. 7× dokładniej, **dwuklik** = wartość
  domyślna parametru, tooltip „nazwa: wartość”; podczas najechania/przeciągania etykieta pod pokrętłem pokazuje wartość.
- **Główne (duże) pokrętła:** Cutoff, Resonance, Filter Drive, Distortion, Wavetable A i B, Unison Detune,
  Macro 1–4, Pump, Delay (mix), Reverb (mix), Output – zgodnie ze specyfikacją. Pozostałe parametry są małymi
  pokrętłami / listami na tym samym ekranie (bez zakładek).
- **Podgląd wavetable** rysuje kilka klatek „w głąb” i bieżącą klatkę w kolorze akcentu; **oscyloskop** jest zasilany
  przez `juce::AbstractFifo` (lock-free, wątek audio nie czeka na UI).
- **Przeglądarka presetów w górnym pasku:** poprzedni/następny (w obrębie aktualnego filtra), menu z podziałem
  na kategorie, filtr kategorii, filtr tagów, wyszukiwarka (nazwa, tagi, opis), zapis presetu użytkownika (okno
  z nazwą, kategorią, tagami, opisem). Nazwa fabryczna nie może zostać nadpisana.
- **Stan sesji:** APVTS + właściwości `presetName`, `presetCategory`, `macroLabel1..4`, `uiScale` w drzewie stanu.
  Etykiety makr edytuje się dwuklikiem pod pokrętłem makra.
- **Presety fabryczne zapisane rzadko** (tylko wartości różne od domyślnych; brakujące = domyślne), presety użytkownika
  zapisywane są w całości (wszystkie parametry), żeby były odporne na ewentualne zmiany wartości domyślnych.
  Wybory (choice) zapisywane po nazwie, nie po indeksie. Walidacja: nieznane ID, złe nazwy wyborów i wartości
  spoza zakresu są raportowane (test jednostkowy wymaga zera błędów dla presetów fabrycznych).
- **Katalog presetów użytkownika:** `userApplicationDataDirectory/VOLT/Presets` – na Windows `%APPDATA%\VOLT\Presets`.
- **`VOLT_Render --snapshot plik.png [skala]`** zapisuje zrzut edytora bez ekranu (narzędzie deweloperskie do
  sprawdzania układu na Linuksie w chmurze); zrzut: `docs/ui-snapshot.png`.

## Etap 5 – renderer presetów i testy

- **`VOLT_Render` używa prawdziwego `VoltAudioProcessor`** (APVTS, `PresetManager`, wygładzanie, FX), z `AudioPlayHead`
  zwracającym 120 BPM i grający transport – Pump, arpeggiator, LFO i delay w trybie sync zachowują się jak w DAW.
  Render 48 kHz, blok 512.
- **Frazy testowe wg kategorii:** Bass – nuta C2 1,6 s; Lead – sekwencja C4-Eb4-G4-Bb4-C5; Pad/Keys/Brass – akord
  Cmaj7 2,4 s; Arp – trzymany akord Cm 2,6 s; FX – nuta C4 2 s. Po ostatnim note-off renderowane jest 8 s ogona.
- **Kryteria niezaliczenia:** NaN/Inf (liczone także przed sanityzacją w stopniu wyjściowym), cisza (szczyt < −40 dBFS),
  szczyt > 0 dBFS, |DC| > 0,01 w części aktywnej, RMS ostatnich 0,5 s ogona > −60 dBFS, redukcja limitera > 3 dB
  (limiter ma tylko chronić – zła wartość oznacza zły gain staging), głośność poza [−24, −9] LUFS albo odchylenie
  > 5 LU od mediany wszystkich presetów (spójność poziomów).
- **Głośność** liczona jako nieważona bramką głośność zintegrowana z filtrem K (ITU-R BS.1770) w części aktywnej frazy;
  raport zawiera też RMS, szczyt, centroid widmowy (średnie widmo, FFT 4096, okno Hanna), czas ogona i redukcję limitera.
- **Podglądy audio:** FLAC 48 kHz/16 bit, fraza + 1,6 s ogona z 0,25 s wyciszeniem (FLAC odtwarza Windows 10/11
  i FL Studio; mniejszy niż WAV). Pliki `previews/NNN_Nazwa.flac`, raport `report.md` i `report.json`.
- **Testy presetów (`tests/PresetTests.cpp`):** parsowanie bez błędów, unikalne nazwy, Init pierwszy, lista zakazanych
  słów w nazwach (artyści, albumy, tytuły utworów), kategoria, tagi, opis jednym zdaniem, każde z 4 makr podpięte
  w macierzy i opisane etykietą. Testy stanu: pełny round-trip parametrów, nazwy presetu i etykiet makr; zapis
  i ponowne wczytanie presetu użytkownika.
