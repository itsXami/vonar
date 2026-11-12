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
- **Licencja JUCE:** JUCE 8 jest dostępny na AGPLv3 albo licencji komercyjnej/Starter. Wybrana ścieżka: AGPLv3
  dla całego projektu (patrz „Wersja publiczna – neutralizacja i licencja”).

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
- **Bez obsługi pitch bend i pedału sustain (CC64)** – nie ma ich w specyfikacji (dodane później, w etapie C
  wersji publicznej – patrz „Etap C”). Obsługiwane są Mod Wheel (CC1),
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

## Etap 6 – presety

- **Presety generowane skryptem `tools/presets/generate_presets.py`** (czytelna definicja każdego brzmienia w Pythonie
  → rzadki JSON w `presets/`). Skrypt sprawdza poprawność nazw tablic, źródeł i celów modulacji, liczności grup
  oraz limit 8 slotów modulacji. Zapisane JSON-y są artefaktem źródłowym w repo (plugin osadza je przez BinaryData).
- **Każdy preset ma 4 makra podpięte w macierzy i opisane** (np. Grit, Snarl, Sync, Crush). Makra startują z wartością 0,
  więc preset brzmi „bazowo”, a makra dodają charakter.
- **Korekta poziomów na podstawie raportów:** `generate_presets.py --trim render-out/report.json` przesuwa `out_gain`
  każdego presetu w kierunku −15 LUFS (filtr K, część aktywna frazy). Trymy są zapisane w `tools/presets/gain_trims.json`,
  więc generator odtwarza dokładnie te same pliki. Wykonano kilka iteracji render → korekta → render.
- **Zmiany brzmień wymuszone raportem:** presety z wąskim BP (Funky Filter Keys, Funk Clav Keys) przełączone na LP24
  z rezonansem (BP tracił za dużo energii), krótkie stab-y i pluck-i (Chicago Organ Stab, Breaker Keys, Gloss Pluck,
  Funky Filter Keys, Funk Clav Keys) dostały dłuższy decay / sustain i lekki Squash, bo przy równej głośności ich szczyty
  wymuszały > 3 dB pracy limitera; Scrapyard Hit i Grinding Sweep dostały wyższe poziomy źródeł.
- **Wynik końcowy:** 121/121 presetów przechodzi render; głośność −17,2…−14,9 LUFS (mediana −15,0), maksymalna redukcja
  limitera 2,4 dB, najdłuższy ogon 3,0 s.
- **Nazwy presetów nie zawierają nazwisk, albumów ani tytułów** – pilnuje tego test z listą zakazanych słów.
  (Pierwotnie tagi i `docs/PRESETS.md` wskazywały inspirację konkretnymi artystami i albumami; usunięto to
  w etapie A wersji publicznej – patrz „Wersja publiczna – neutralizacja i licencja”.)
- **Organy (Drawbars/Drive Organ):** stopa 16′ jest 1. harmoniczną tablicy, więc presety organowe mają Oct +1, żeby
  grać w typowym rejestrze 8′.

## Etap 7 – dokumentacja

- **README po polsku** z instalacją w FL Studio, skróconą instrukcją i jawnym podziałem: co sprawdza CI, a co wymaga
  odsłuchu i ręcznego testu w FL Studio na Windows.
- **`docs/PRESETS.md` jest generowany** przez `tools/presets/generate_presets.py` z tych samych danych co presety
  (lista nie rozjedzie się z plikami JSON). Wstęp po polsku, opisy presetów po angielsku – takie same jak w interfejsie.

## Przebudowa interfejsu (po uwagach użytkownika)

Użytkownik ocenił pierwszą wersję jako „wyglądającą bardzo AI” i poprosił o coś pomiędzy Zenology a Vitalem,
z naciskiem na to, żeby łatwo było widzieć, co czym jest. Ustalone z użytkownikiem:
- **Kolor na sekcję zamiast jednego akcentu** (świadoma zmiana względem pierwotnej specyfikacji): oscylatory/unison/sub
  turkus, filtr pomarańcz, obwiednie zieleń (także obwiednia filtra wewnątrz sekcji filtra), LFO/modulacja/arp/voice
  fiolet, efekty i wyjście niebieski, makra żółty. Kolor ma nagłówek sekcji, łuki pokręteł, strzałki list i przyciski.
  Pasek z kluczem kolorów pod logo.
- **Okno 1200×740** (było ~1000×620), skalowanie 75–200% bez zmian (900×555 … 2400×1480).
- **Wartość zawsze widoczna pod każdym pokrętłem**, nazwa parametru nad nim (styl Zenology), normalna pisownia
  zamiast drobnych wersalików; suwaki macierzy modulacji pokazują wartość w procentach.
- **Krzywa filtra** (charakterystyka amplitudowa dla bieżącego typu, Cutoff, Resonance i Vowel; te same wzory co
  w `VoiceFilter`, prototyp analogowy, bez drive i modulacji). Pozostałe grafiki (krzywe obwiedni, kształt LFO,
  pierścienie modulacji) nie zostały wybrane.
- **Czcionka Inter** (Regular i SemiBold) osadzona przez BinaryData – licencja SIL OFL w `resources/fonts/OFL-Inter.txt`.
  Domyślna czcionka JUCE na Windows (Verdana) wyglądała przestarzale.

## Rozbudowa silnika (silnik v2) i zakładki – na prośbę użytkownika

Użytkownik zauważył, że wiele brzmień jest do siebie podobnych, i poprosił o mocne rozbudowanie silnika
(z dopuszczeniem zakładek jak w Vitalu zamiast jednego ekranu).
- **Tryby warp na oscylator** (`oscA_warp`, `oscA_warp_amt`, analogicznie B): Sync (wirtualny hard sync ×1…×8),
  Bend (krzywa fazy), Squeeze (phase distortion), Mirror (odbicie cyklu, crossfade), Quantize (schodkowanie fazy),
  FM i RM od drugiego oscylatora (modulatorem jest pierwszy głos unisonu drugiego oscylatora z jego tablicą,
  pozycją i wysokością – działa też, gdy drugi oscylator ma poziom 0, czyli jako „cichy operator”).
  Pętle renderujące są szablonem na tryb (`wavetableLoop<Mode>`), żeby nie płacić za `switch` w każdej próbce.
  Przy Sync/FM/Mirror mip wybierany jest z uwzględnieniem efektywnego mnożnika częstotliwości.
- **Oscylator String** (`oscA_type`: Wavetable/String): Karplus-Strong na każdy głos unisonu. Pobudzenie = jeden
  okres bieżącej klatki wavetable + 15% szumu (pozycja wavetable zmienia charakter szarpnięcia), w pętli
  jednobiegunowy LP (Tone) i wzmocnienie dające zanik −60 dB po czasie Decay. Strojenie kompensuje opóźnienie grupowe
  filtra pętli (test: błąd < 1,2% dla E2, A3, A4). Legato bez retriggera nie szarpie struny ponownie.
- **Filtry Comb+ i Comb−** (sprzężenie dodatnie/ujemne, opóźnienie = 1/cutoff, Resonance = siła sprzężenia,
  miękkie ograniczanie w pętli).
- **Mod Env** (trzecia obwiednia ADSR, `menv_*`) i **Random** (losowa wartość −1…1 przy każdej nucie, z osobnego
  generatora, żeby nie zmieniać losowania faz unisonu) jako nowe źródła; **12 slotów** macierzy (`mod9…mod12`);
  nowe cele: Warp A, Warp B, Detune.
- **8 nowych tablic** (dopisanych na końcu listy, więc indeksy starych się nie zmieniły): Pluck Body, Hammer Piano,
  Reed, Glass Harmonics, Vocal Fry, Even Saturate, Noise Cycle, Dual Formant.
- **Zgodność wstecz:** wszystkie nowe parametry mają wartości domyślne wyłączające nowe funkcje; nowe pozycje list
  wyboru dopisano na końcu. Render 121 presetów fabrycznych przed i po zmianie: różnica głośności 0,0 LU.
  `ParamSpec::id` jest teraz `juce::String` (ID slotów 9–12 są generowane).
- **Zakładki:** SYNTH (oscylatory, filtr, unison/sub/szum, string, obwiednie, voice, arp), MODULATION (LFO 1/2 z dużymi
  pokrętłami, Mod Env, macierz 12 slotów), EFFECTS (6 efektów w kolejności łańcucha, numerowanych 1–6). Pasek
  presetów u góry oraz makra, wyjście i oscyloskop na dole są widoczne zawsze. Wybrana zakładka zapisywana jest
  we właściwości stanu `uiTab`. To świadome odejście od pierwotnego „jednego ekranu bez zakładek”, na prośbę użytkownika.

## Scalenie biblioteki presetów (po odsłuchu użytkownika)

- **Werdykty użytkownika zapisane w repo** (`tools/presets/selection.json`), a bibliotekę buduje
  `tools/presets/build_library.py` z obu partii. Dzięki temu decyzje są odtwarzalne, a generatory pozostają
  jedynym źródłem treści presetów.
- **Do biblioteki trafia wszystko, czego użytkownik nie odrzucił** – także presety oznaczone „Popraw” (14), bo
  użytkownik poprosił, żeby na razie niczego nie poprawiać; są oznaczone w `docs/PRESETS.md` jako „do poprawki”.
- **Kolejność według grupy stylistycznej**, w ramach grupy według kategorii (zastąpione w etapie A wersji
  publicznej kolejnością kategoria → nazwa).
- **Nowa kategoria „Guitar”** w `PresetManager::categories()` (renderer gra dla niej dwukrotne szarpnięcie akordu).
- **Determinizm renderu:** faza LFO Mod FX jest zerowana przy resecie – wcześniej render presetu zależał od
  poprzednio renderowanego (różnice do 1,4 dB pracy limitera między uruchomieniami).
- **Test liczności** nie wymaga już 121 presetów: sprawdza, że załadowano każdy osadzony plik, że jest ich > 100
  i że jest kategoria Guitar.

## Oszczędzanie minut GitHub Actions

- **CI uruchamia się raz na push** (wszystkie gałęzie) zamiast dwa razy (push + pull_request). PR pokazuje status
  tego samego przebiegu. Wcześniej każdy commit budował się podwójnie (ok. 30 min, z czego Windows ~20 min).
  Odejście od „każdy push i PR”: zmiany w PR i tak są pushami, więc nic nie traci pokrycia.
- **Artefakty trzymane 14 dni** (`retention-days: 14`) zamiast domyślnych 90 – darmowy plan GitHuba ma ograniczone
  miejsce na artefakty prywatnych repozytoriów; starsze paczki można zawsze odtworzyć z kodu.

## Wersja publiczna – neutralizacja i licencja (etap A)

- **Żadnych odwołań do artystów, albumów, utworów ani marek** w presetach, generatorach, README i `docs/PRESETS.md`.
  Syntezator będzie publiczny, więc presety opisują wyłącznie dźwięk. Dziesięć dawnych grup inspiracji zostało
  w generatorach jako neutralne rodziny stylistyczne (`industrial`, `stadium`, `cold`, `epic`, `gospel`, `rawhouse`,
  `discohouse`, `mechanical`, `cinematic`, `analog`), które wnoszą tagi stylu: Industrial, Stadium, Cold, Epic, Gospel,
  House + Raw, House + Disco, Mechanical, Cinematic, Analog. Parametry brzmień nie zostały zmienione (porównanie
  JSON-ów przed/po: różnią się tylko tagi i numeracja plików).
- **Dwie nazwy i jeden opis zmienione**, bo nawiązywały do filmu albo marki instrumentu: „Light Cycle Arp” →
  „Racing Saw Arp”, „Suitcase Electric Piano” → „Autopan Electric Piano”, opis Funky Filter Keys „Clavinet-like” →
  „Clav-style”. Trymy głośności przeniesione pod nowe nazwy.
- **Kolejność biblioteki: kategoria → nazwa alfabetycznie** (kolejność kategorii jak w `PresetManager::categories()`).
  Kolejność „wg ery” straciła sens, a układ alfabetyczny w kategorii jest standardem w przeglądarkach presetów.
  Numery plików `presets/NNN_*.json` zmieniły się; pluginu to nie dotyczy, bo presety są identyfikowane po nazwie.
- **Test zakazanych nazw rozszerzony:** dotychczasowa lista (`kBannedInNames`, wiele zwykłych słów) nadal dotyczy
  tylko nazw; nowa, krótka lista jednoznacznych nazw artystów, albumów i marek (`kBannedEverywhere`) obowiązuje
  w nazwach, tagach, opisach i etykietach makr. Generator kandydatów czyta obie listy z `tests/PresetTests.cpp`.
- **Licencja AGPLv3** (plik `LICENSE`, tekst pobrany z gnu.org bez zmian): decyzja użytkownika – projekt otwarty,
  darmowy, bez rejestracji; zgodna z licencją AGPLv3 frameworka JUCE, więc nie trzeba licencji komercyjnej JUCE.
  Nazwa i logo nie są objęte licencją (README). Od innych przyjmujemy na start tylko presety (`CONTRIBUTING.md`).
- **Wzorce brzmień od użytkownika** są zapisywane w `docs/SOUND_REFERENCES.md` wyłącznie jako opis charakteru;
  nazwy wzorców nie trafiają do presetów.
- **Czego neutralizacja nie obejmuje:** starszych komunikatów commitów na gałęzi `feature/volt-synth` (jeden z nich
  wymienia artystów). Przy upublicznieniu repo scalić PR metodą „squash”, żeby historia `main` była czysta.

## Wygląd – etap B (makiety, w toku)

- **Układ: makieta 2** (kolor na sekcję, wszystko z zakładki SYNTH na jednym ekranie) – wybór użytkownika.
- **Wykończenie: 2A „techniczne”** (płaskie panele na styk, cienkie łuki) – wybór użytkownika.
- **Runda 3 – dlaczego makiety wyglądały na wygenerowane** (użytkownik: „coś z czcionką i ogólnym wyglądem”).
  Przegląd poradników o typowych cechach projektów generowanych i o projektowaniu wtyczek audio wskazał:
  krój wybrany „domyślnie” (Inter) bez decyzji typograficznej; jednakowe ramki, odstępy i rozmiary wszystkiego;
  obramowane sekcje wszędzie („wygląd okna ustawień”); zbyt wiele równie mocnych kolorów; brak jednego punktu
  skupienia i hierarchii rozmiarów; mało wyrazista nazwa pluginu. Zastosowane poprawki są opisane w PROGRESS.md.
  Źródła: prg.sh „Why Your AI Keeps Building the Same Purple Gradient Website”, 925studios.co „AI slop design
  tells”, world.hey.com/kostac „Spot the slop”, plugin-builder-docs „Design guide / Anti-patterns”,
  iZotope „Creating the gauge”.
- **Krój: Oxanium** (wybór użytkownika, 3B).
- **Kroje do wyboru były: Barlow Semi Condensed albo Oxanium** (oba SIL OFL, można osadzić w pluginie jak dotąd Inter).
  Po wyborze Inter zostaje usunięty z zasobów, jeśli nie będzie już używany.
- **Makieta 4 zaakceptowana i wdrożona.** Ciepły grafit, przygaszone kolory sekcji, ziarno (kafelkowany obraz
  szumu rysowany nad wszystkim w `paintOverChildren`, generowany raz ze stałego ziarna losowego), cieniowane
  główki pokręteł, podziałka na dużych pokrętłach, jednostki mniejsze od liczb.
- **Trzy rozmiary pokręteł** (Hero / Medium / Small) zamiast dwóch: Hero mają Position i Cutoff oraz główne
  pokrętła zakładek MODULATION i EFFECTS.
- **Zakładki są w górnym pasku**, więc strony mają 534 px wysokości zamiast 514; dolny pas ma 154 px.
- **Obwiednie w jednym panelu z przełącznikiem** (AMP / FILTER / MOD / PITCH). Wykres pokazuje kształt według
  położeń pokręteł, a nie liniową oś czasu (inaczej krótkie czasy byłyby niewidoczne), dlatego nie ma podpisów
  sekund, które były na makiecie.
- **LFO na zakładce SYNTH i MODULATION jednocześnie** (ten sam parametr ma dwa pokrętła); na pasku SYNTH pokrętło
  Rate i lista podziału taktu zajmują to samo miejsce i przełączają się przyciskiem SYNC.
- **Wyjście i oscyloskop bez koloru sekcji**; niebieski został tylko na zakładce EFFECTS.
- **Miernik poziomu**: procesor zapisuje szczyt bloku na kanał w `std::atomic`, edytor pobiera go 30 razy na
  sekundę; opadanie ok. 48 dB/s, znacznik szczytu trzymany 1 s, kolor pomarańczowy powyżej −0,6 dBFS.
- **Okno „O programie”** otwiera kliknięcie znaku VOLT: wersja, licencja AGPLv3, JUCE, Oxanium.
- **Czcionka w dwóch grubościach** (Medium i SemiBold) jako statyczne instancje pliku zmiennego Oxanium,
  bo `createSystemTypefaceFor` ładuje tylko domyślną instancję czcionki zmiennej.

## Etap C – silnik i poprawki presetów (wersja publiczna)

- **Pitch bend:** nowy parametr `bend_range` (Int 0–24 półtonów, domyślnie 2), dopisany na końcu tabeli
  parametrów, więc kolejność i ID istniejących parametrów się nie zmieniły; presety bez tego pola dostają 2.
  Kółko jest wygładzane per pod-blok (τ ≈ 5 ms), żeby kółka o małej rozdzielczości nie dawały słyszalnych
  schodków. Bend przesuwa wysokość wszystkich głosów (oba oscylatory, sub; tak jak cel modulacji „Pitch”).
  Zakres 2 półtonów to standard większości syntezatorów i kontrolerów.
- **Sustain (CC64 ≥ 64 = wciśnięty):** działa przed arpeggiatorem – klawisz puszczony przy wciśniętym pedale
  nie wysyła note-off, tylko zostaje zapamiętany; po puszczeniu pedału note-off dostają zapamiętane klawisze,
  których palec już nie trzyma. Ponowne uderzenie trzymanego pedałem klawisza gra nutę od nowa. Z włączonym
  arpeggiatorem pedał podtrzymuje wzór (jak „hold”). All Notes Off / All Sound Off czyszczą stan pedału.
  Testy: `tests/ExpressionTests.cpp`.
- **14 presetów „Popraw”:** nowe wersje w `tools/presets/generate_fixes.py` (JSON-y w `tools/presets/fixes/`,
  trymy `fix_trims.json`); stare zostają w generatorach. Do biblioteki nowa wersja trafia dopiero, gdy
  użytkownik wybierze ją na stronie porównania (`selection.json` → `fixes_accepted`; czyta to
  `build_library.py`). Dwie miały uwagi użytkownika: Long Glide 808 („nic nie słychać”: był oktawę za nisko,
  ~33 Hz bez harmonicznych – teraz oktawę wyżej, przester Fold, sub zostaje) i Tom Drop 808 („za cicho”: krótka
  obwiednia + szczyt zjazdu wysokości wymuszał niski poziom – teraz dłuższe ciało, przester i kompresja).
  Pozostałe 12 nie miało uwag, więc każda nowa wersja jest zbudowana wokół jednego wyraźnego pomysłu na
  silniku v2 (String, warp Sync/FM, Comb, Mod Env, Random) i reaguje na velocity i Mod Wheel.
  Wszystkie 14 przechodzą render i `similarity.py` (≥ 1.2 od biblioteki).
- **Filtr DC w głosie (wykryty przy partii Keys 1):** tryb warp Squeeze ściska jedną połowę cyklu, przez co kształt
  spędza więcej czasu po jednej stronie zera (Reed + Squeeze: DC −0,2; wcześniej to samo w Sawblade Arp). Głos nie
  miał żadnego usuwania DC. Dodany jednobiegunowy filtr górnoprzepustowy ~5 Hz przed filtrem głównym (stan zerowany
  przy starcie z ciszy). Wpływ na bibliotekę: najwyżej 0,19 LU różnicy głośności; Marimba Keys przekroczyła przez to
  próg limitera o 0,05 dB, więc jej trym zmieniono z −0,3 na −1,0 dB. Test: `Engine v2 / Phase-shaping warps leave
  no DC offset`.

## Etap D – biblioteka ok. 300 presetów

- **Partie jako osobne generatory** (`tools/presets/generate_batch_<nazwa>.py`, JSON-y w
  `tools/presets/batches/<nazwa>/`, trymy `batches/<nazwa>_trims.json`). Do biblioteki trafiają po odsłuchu.
- **Wybór lekki** (decyzja użytkownika): preset domyślnie zostaje; na stronie odsłuchu tylko „Usuń” albo
  „Za podobny do…” (z listy) i uwaga. Obok kandydata gra jego najbliższy według pomiaru preset z biblioteki.
- **Keys 1 (23 presety):** ciepły kierunek z `docs/SOUND_REFERENCES.md`; świadomie bez tablicy FM Bell (9 z 25
  dotychczasowych Keys ją ma). Rodziny: pianina elektryczne, pianina, klawisze szarpane, organy, syntezatorowe,
  lo-fi. Presety na oscylatorze String miały za ostry szczyt ataku akordu względem ciała (limiter 4–13 dB);
  pomogły dłuższy `str_decay`, atak 8–26 ms (miękki młoteczek) i lekkie nasycenie Soft/Tube. Upright Room Piano
  odpadł (za blisko istniejących, a dwa inne pianina na strunie zostały).
- **Nowe kategorie Pluck, Bell, Strings, Woodwind** (na prośbę użytkownika o plucki, belle i „ogólne instrumenty”).
  Organy zostały w Keys (osobna kategoria Organ – do decyzji). Kolejność kategorii w menu: Bass, Lead, Guitar,
  Pluck, Keys, Bell, Pad, Strings, Brass, Woodwind, Arp, FX. Każda nowa kategoria ma frazę testową typową dla
  sposobu grania (pomiar głośności i podobieństwa zależy od frazy).
- **Partie D trafiają do biblioteki od razu**, bez czekania na odsłuch (ustalenie „domyślnie zostaje”); po odsłuchu
  usuwa się wskazane. Dzięki temu plugin w CI ma od razu pełną bibliotekę do testów w DAW.
- **Ograniczenie miary podobieństwa:** presety ocenia się na jednej krótkiej frazie, więc wolny ruch padów i różnice
  w ekspresji (velocity, Mod Wheel) są niewidoczne; smyczki i pady grane akordem zbliżają się do siebie. Przy
  padach i smyczkach rozróżnialność osiągnięto głównie przez jasność, atak, szerokość stereo, rejestr i ruch
  w obrębie frazy. Ostateczne „za podobny” rozstrzyga odsłuch.
- **Krótkie artykulacje grane akordem** (pizzicato, staccato, col legno, szarpane struny) mają szczyt ataku wysoko
  ponad ciałem, a korekta głośności do −15 LUFS przenosi szczyt w limiter. Rozwiązania: atak 8–25 ms (miękki
  młoteczek / smyczek), dłuższe wybrzmienie, lekka saturacja Soft/Tube, Squash; col legno powtarzane
  arpeggiatorem w szesnastkach.
- **Kontrola zakresów parametrów w generatorze partii** (`batch_common.param_ranges()` czyta Params.cpp) – po tym,
  jak Gamelan Gong miał `oscB_semi` = 14 (zakres ±12), co wyłapał dopiero test jednostkowy.
- **Kierunek brzmieniowy po uwagach użytkownika:** domyślnie „ciepło” z wzorców okazało się za jednostronne; nowe
  partie mają być jasne, suche i dosadne, z naciskiem na house i hip-hop. Lo-fi, brzmienia „growe” i flety –
  oszczędnie.
- **Klawiatura do grania:** `juce::MidiKeyboardComponent` w nakładce na dolny pas (okno nie zmienia rozmiaru, więc
  proporcje i skalowanie zostają). Klawiatura komputera działa, gdy panel ma fokus (dostaje go po otwarciu).
  Domyślne mapowanie JUCE (A–K, W–U) plus własne Z/X do zmiany oktawy.

