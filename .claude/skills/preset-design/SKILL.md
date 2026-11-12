---
name: preset-design
description: Zasady i proces projektowania presetów VOLT tak, żeby brzmiały różnorodnie i „ludzko”, a nie jak warianty jednego szablonu. Użyj ZAWSZE przed tworzeniem, poprawianiem lub wybieraniem presetów (generatory w tools/presets, JSON-y w presets/, strona odsłuchu, selection.json), także gdy użytkownik prosi o „nowe brzmienia”, „więcej plucków/padów” itp.
---

# Projektowanie presetów VOLT

Problem, który ten skill rozwiązuje: presety projektowane „na ślepo” z szablonu kategorii brzmią prawie tak samo
(pomiar z 2026-11-12: 136 presetów, mediana odległości do najbliższego sąsiada 1.39, pady/keys/brass ok. 1.2;
pary typu *Sunset Pad ~ Studio Poly Pad* 0.53). Każdy nowy preset ma przejść przez pomiar podobieństwa,
zanim trafi na stronę odsłuchu.

## Zasady nadrzędne (wersja publiczna)

- Żadnych nazw artystów, albumów, utworów ani marek w nazwie, tagach i opisie. Tagi opisują dźwięk
  (np. `Warm`, `Plucky`, `Detuned`, `Glassy`, `Evolving`, `Mono`, `Wide`, `Dark`, `Percussive`, `Lo-Fi`).
- Nie kopiujemy presetów, wavetable ani nazw z innych syntezatorów. Wzorce od użytkownika służą tylko do
  opisania charakteru („jasny, krótki, z metalicznym atakiem”), parametry projektujemy od zera.
- Nazwa: 1–3 słowa, opisowa albo obrazowa, unikalna w bibliotece, bez numerów wersji.
- Głośność: cel ok. -15 LUFS na frazie kategorii (trym w `candidate_trims.json`), limiter < 3 dB redukcji.
- Makra 1–4 zawsze coś sensownego robią i mają nazwy mówiące co (np. `Bite`, `Air`, `Motion`, `Space`).

## Jeden preset = jeden wyraźny pomysł

Zanim napiszesz parametry, zapisz w opisie presetu jedno zdanie: **czym ten dźwięk różni się od innych w tej
kategorii**. Jeśli nie da się tego powiedzieć, preset nie powstaje. Dobre pomysły to konkretna cecha:
„atak jak młoteczek, potem szklany ogon”, „bas, który przy każdej nucie otwiera się inaczej (Random)”,
„pad, który przez 8 s przechodzi z chóru w metal”.

Każdy preset w partii musi różnić się od poprzedniego w co najmniej **trzech** z tych osi:

| Oś | Przykładowe skrajności |
|---|---|
| Źródło | Wavetable / String (Karplus-Strong) / szum / sub |
| Tablica | 40 tablic – nie używaj ciągle `Analog Saw`, `Hyper Saw`, `Strings` |
| Warp | Off, Sync, Bend, Squeeze, Mirror, Quantize, FM, RM |
| Filtr | LP12, LP24, HP, BP, Notch, Ladder, Formant, Comb+, Comb- (albo filtr prawie otwarty) |
| Obwiednia | perkusyjna / pluck / organowa (0 attack, pełny sustain) / swell / odwrócona |
| Ruch | statyczny / LFO / Mod Env / Random per nuta / Velocity / Mod Wheel |
| Przestrzeń | sucho / krótki pokój / delay ping-pong / długi pogłos / mono |
| Charakter | czysty / nasycony / fold / bitcrush / lo-fi |

## Silnik v2 – używaj go

- **Warp** (`oscA_warp`, `oscA_warp_amt`, analogicznie B): FM i RM dają dzwony i metal, Sync i Bend
  agresywne leady/basy, Squeeze i Mirror nosowe/wokalne barwy, Quantize lo-fi. Modulacja celu `Warp A/B`
  przez Mod Env daje ewolucję barwy w czasie nuty.
- **String** (`oscA_type: "String"`, `str_decay`, `str_tone`): gitary, harfy, koto, szarpane basy, kalimby
  (krótki `str_decay` + jasny `str_tone`), dzwonki (String + FM na drugim oscylatorze).
- **Comb+/Comb-**: rezonujące rury, metaliczne plucki, „flanger” wewnątrz filtra; strojony przez key track.
- **Formant** (`flt_vowel`): chóry, talk-box, wokalne leady; modulowany LFO lub Mod Wheel.
- **Mod Env** (`menv_*`): druga obwiednia na WT Pos, Warp, Formant – zamiast w kółko Filter Env na Cutoff.
- **Random** (nowa wartość na nutę): humanizacja – lekko na Cutoff, Pitch (±kilka centów), Pan, WT Pos.
- **Velocity / Mod Wheel / Aftertouch**: każdy preset grany ręcznie powinien reagować na velocity
  (głośność albo jasność). Mod Wheel ma robić coś słyszalnego (vibrato, otwarcie, formant).
- Sloty modulacji: 1–4 zwykle zajmują makra, 5–12 to miejsce na ruch i ekspresję.

## Przepisy startowe per kategoria (punkt wyjścia, nie szablon)

Każdy przepis ma kilka *rodzin* – w partii rozkładaj presety równo między rodziny.

- **Bass**: sub sinus + krótki click; reese (2× saw, detune, LP24 z wolnym LFO); FM bass (warp FM);
  szarpany String bass; acid (Ladder, wysoka rezonans, filter env, glide w Legato); 808 (pitch env, dist).
- **Lead**: sync lead (warp Sync + Mod Env na Warp A); vocal lead (Formant + Mod Wheel); mono z glide i vibrato
  na Mod Wheel; fold/ostry; miękki sinus/flet z oddechem (noise + BP).
- **Pluck**: String z krótkim decay; wavetable z bardzo krótkim fenv i Ladder; Comb+ pluck; FM pluck;
  pizzicato (BP + krótki ogon); każdy pluck inny atak (miękki/twardy) i inny ogon (sucho/delay/pogłos).
- **Bell & Mallet**: FM/RM warp z niecałkowitymi stosunkami (`oscB_semi` 7, 12, 19, 24 + `fine`), `Bell Metal`,
  `Glass Harmonics`; marimba/wibrafon (sinus + krótki fenv + tremolo LFO); dzwony rurowe (Comb + długi ogon);
  kalimba (String, jasny tone, krótki decay).
- **Keys & Piano**: `Hammer Piano`, e-piano (FM + tremolo/chorus), clav (String + HP), organy przeniesione
  do Organ; velocity zawsze na jasność.
- **Organ**: `Drawbars`, `Pipe Organ`, `Drive Organ`; amp 0 attack, sustain 1; rotary = Chorus/Phaser +
  LFO na Pan; bez długich ogonów.
- **Pad**: każdy pad ma inny *ruch*: WT Pos sweep (Mod Env 4–10 s), Random per nuta, LFO S&H, formant drift,
  ewolucja warp. Unikaj kolejnego „saw + chorus + reverb”.
- **Strings**: ensemble (`Strings`, unison, wolny attack), pizzicato, solowa smyczka z vibrato na Mod Wheel,
  tremolo (LFO na amp/Level).
- **Brass**: `FM Brass`/`Brass`, filter env z attackiem 30–80 ms (nie zero), velocity na cutoff, stab vs swell.
- **Guitar**: String jako podstawa; muted (krótki decay, ciemny tone), czysta (chorus), przester (dist Tube/Hard
  po String), slide (glide w Legato).
- **Arp & Sequence**: `arp_on`, różne `arp_mode`, `arp_rate`, `arp_gate`; dźwięk musi mieć krótką obwiednię;
  ruch synchronizowany z tempem (LFO sync, delay 1/8D).
- **Vocal & Choir**: `Choir`, `Vowels`, `Dual Formant`, `Talk Box`, filtr Formant; oddech z noise.
- **FX**: riser (pitch env/LFO w górę + noise), impakty, drony, glitch (S&H, bitcrush); tu wolno szaleć.

## Efekty – nie ten sam łańcuch

Nie dawaj każdemu presetowi chorus + delay + reverb. W partii pilnuj rozkładu: ok. 1/3 bez pogłosu albo z bardzo
krótkim, część z samym delayem, część z Phaser/Flanger zamiast Chorus, część z dist jako barwą (Fold, Bitcrush).
`pump_amount` tylko tam, gdzie preset jest z założenia „sidechainowany”.

## Proces (obowiązkowy)

1. **Plan partii**: tabela nazwa → kategoria → rodzina → jeden pomysł → osie, którymi różni się od sąsiadów.
   Sprawdź tabelę: żadna rodzina nie ma więcej niż ~1/4 partii.
2. **Generator**: dopisz presety w `tools/presets/generate_candidates.py` (lub nowym generatorze) i wygeneruj
   JSON-y do `tools/presets/candidates/`.
3. **Render z cechami** (build: `cmake --build build --target VOLT_Render`):
   ```bash
   ./build/VOLT_Render_artefacts/Release/VOLT_Render --out /tmp/render-lib --no-previews
   ./build/VOLT_Render_artefacts/Release/VOLT_Render --dir tools/presets/candidates --out /tmp/render-new
   ```
   Raport `report.json` zawiera blok `features` (16 pasm, jasność, ruch, atak, sustain, szumowość,
   szerokość, udział basu). Odrzuć wszystko, co ma błąd techniczny w `report.md`.
4. **Podobieństwo**:
   ```bash
   python3 tools/presets/similarity.py /tmp/render-lib/report.json /tmp/render-new/report.json --json /tmp/sim.json
   ```
   Kandydat z werdyktem `reject` (odległość < 1.2 od presetu z biblioteki lub zaakceptowanego kandydata)
   nie idzie na odsłuch – popraw go według osi z tabeli wyżej albo usuń. Cel dla biblioteki: mediana
   odległości do najbliższego sąsiada ≥ 1.6 w każdej kategorii. Sama liczba nie zastępuje słuchu – to sito.
5. **Trym głośności** (`candidate_trims.json`) i ponowny render.
6. **Strona odsłuchu** dla użytkownika (FLAC-i z renderu); werdykty użytkownika zapisuj w
   `tools/presets/selection.json`. Użytkownik decyduje, Claude nie zatwierdza presetów sam.
7. **Biblioteka**: `python3 tools/presets/build_library.py`, potem pełny render i `similarity.py` na całości;
   wynik (mediany per kategoria) wpisz do `docs/PROGRESS.md`.

## Czego unikać (lista kontrolna przed oddaniem partii)

- [ ] Ten sam `oscA_table` w więcej niż 3 presetach partii.
- [ ] `oscA_warp: "Off"` we wszystkich presetach – w partii co najmniej połowa używa warp, String, Comb lub Formant.
- [ ] Filter Env → Cutoff jako jedyna modulacja.
- [ ] Identyczny zestaw efektów w kolejnych presetach.
- [ ] Opis, który pasuje do dowolnego presetu z kategorii („ciepły, szeroki pad”).
- [ ] Tagi z nazwami ludzi, albumów, gatunków przypisanych do konkretnych artystów.
- [ ] Preset nieprzepuszczony przez `similarity.py`.
