# Vonar

A wavetable synthesizer plugin (VST3) with a clear interface, live graphs of everything that shapes the sound, and a
library of **327 presets**: basses, leads, guitars, plucks, keys, bells and mallets, pads, strings, brass, woodwinds,
arps, drums (kicks, snares, claps, hi-hats and shakers for house and hip-hop) and effects – from gentle to hard-hitting,
in five moods (Soft, Medium, Sad, Dark, Aggressive).
Main target: **Windows x64 and FL Studio**. Free and open source (AGPLv3), no registration.

![The Vonar interface – SYNTH tab](docs/ui-snapshot.png)

See also the [MODULATION](docs/ui-modulation.png) and [EFFECTS](docs/ui-effects.png) tabs.

## Download

Get the latest version from the [**Releases**](https://github.com/itsXami/vonar/releases/latest) page
(*Assets* section):

- **`Vonar-<version>-Setup.exe`** – installer with a setup wizard (recommended),
- **`Vonar-<version>-Windows-x64.zip`** – the same plugin without an installer.

## Features

- **Engine:** 16 voices, Poly / Mono / Legato modes, glide.
- **Oscillators A and B:** 40 wavetables generated in code (analog, supersaw, PWM, organ, vocal/formant, metallic, FM,
  gritty, strings, piano, reed, glass), smooth position morphing, anti-aliasing mipmaps,
  octave / semitone / fine tune / level / pan, unison up to 8 voices (Detune and Spread).
- **Warp per oscillator:** Sync, Bend, Squeeze, Mirror, Quantize, and FM and RM from the other oscillator (with a
  modulatable Amount).
- **String oscillator:** a plucked-string model (Karplus-Strong) excited by the wavetable shape – guitars, harps,
  plucks; shared Decay and Tone knobs.
- **Sub** (sine/triangle, one octave below Osc A) and **noise**.
- **Per-voice filter:** LP12, LP24, HP, BP, Notch, Ladder (acid-style resonance), Formant (A-E-I-O-U vowel morphing,
  talkbox-style sounds), Comb+ and Comb− (metallic resonances); Cutoff, Resonance, Drive, Key Track, Env Amount.
- **Envelopes:** Amp ADSR, Filter ADSR, Mod Env (a free envelope for any target), Pitch Env (Amount, Decay) for 808s
  and pitch drops.
- **2 LFOs** (sine, triangle, saw, square, S&H; tempo sync, Rate up to 100 Hz, Depth, Retrigger).
- **Modulation matrix:** 12 slots (source, target, amount) picked from lists; sources include the LFOs, envelopes,
  Velocity, Mod Wheel, Aftertouch, Key Track, Random (a new value for every note) and the macros.
- **4 macros** with labels saved in the preset.
- **Arpeggiator:** Up, Down, UpDown, Random; rate, octaves, gate.
- **Ten effects in any order, each with an on/off switch:** Distortion (Soft, Tube, Hard, Fold, Bitcrush;
  4× oversampling, Keep Low), Chorus, Phaser, Flanger, Filter (LP / HP / BP / Notch), EQ (3 bands), Pump
  (tempo-synced ducking), Delay (stereo / ping-pong, sync), Reverb (with Low Cut / High Cut tone), Compressor
  (Squash – 3-band on a single knob – plus threshold, ratio, attack, release, gain). Output Gain and a limiter at the end.
- **Interface:** a 1200×740 window (scalable 75–200%) with SYNTH / MODULATION / EFFECTS tabs. The SYNTH tab shows
  the oscillators with wavetable previews, the filter with its curve, the envelopes with a graph, both LFOs, voice
  and arpeggiator at once. Macros, the output with a level meter, and an oscilloscope are always visible at the
  bottom. Every section has its own colour.
- **Low CPU use:** effects go to sleep when nothing is playing.

## Installing in FL Studio (Windows x64)

1. Download **`Vonar-<version>-Setup.exe`** from the
   [**Releases**](https://github.com/itsXami/vonar/releases/latest) page. Windows may show a SmartScreen warning
   because the installer is not signed with a paid certificate: click **More info → Run anyway**.
2. Run the installer and follow the wizard: licence → install → finish. The plugin goes to
   `C:\Program Files\Common Files\VST3\Vonar.vst3`; uninstall it from **Settings → Apps**.
   Without the installer: download `Vonar-<version>-Windows-x64.zip` from the same page and copy the whole
   `Vonar.vst3` folder to the same place.
3. In FL Studio open **Options → Manage plugins** and click **Find installed plugins**.
   Vonar appears under **Generators** (vendor: *Vonar*). Tick the star to show it in the instrument menu.
4. Add the instrument: in the **Channel Rack** click **+** and choose **Vonar**.
5. Pick presets in the top bar of the Vonar window (not in FL Studio's preset menu – the plugin exposes a single
   "program" to the host). The plugin state, including the preset name and macro labels, is saved in your
   FL Studio project.

Notes:
- **Vonar was called VOLT during development.** The installer removes the old `VOLT.vst3` so FL Studio does not
  list the plugin twice; the plugin's internal ID is unchanged, so projects made with VOLT still open. User presets
  from `%APPDATA%\VOLT\Presets` are copied to `%APPDATA%\Vonar\Presets` on first launch.
- The plugin is 64-bit (x64). There is no ARM64 build.
- Pump, the arpeggiator, synced LFOs and Delay follow FL Studio's tempo. When the transport is stopped they use the
  project tempo and their own clock; during playback they lock to the bar position.

## Quick guide

**Knobs**
- drag up/down (or right/left) to change the value, hold **Shift** for fine adjustment,
- **double-click** restores the default value, the mouse wheel works too,
- the parameter name is above the knob and the **current value is always below it**; hover for a tooltip.

**Section colours** show what a control belongs to: teal – oscillators, unison, sub, noise and string; orange –
filter; green – envelopes; violet – LFOs, modulation matrix, arpeggiator, voice mode; blue – effects; amber – macros.
An **amber dot under a knob** means a macro controls it.

**Window layout:** the Vonar logo at the top (click it for program and licence information), the tabs and the preset
bar; MACROS, OUTPUT and the oscilloscope are always visible at the bottom.
1. **Preset bar:** click the name to open the preset menu grouped by category; the `<` `>` arrows go to the
   previous/next preset (within the active filter); then the category, mood (Soft, Medium, Sad, Dark, Aggressive) and
   tag filters, and search (name, tags, description, mood). **SAVE** stores a user preset; the **75–200%** list resizes
   the window (you can also drag the corner).
2. **SYNTH tab:** OSC A / OSC B (wavetable, Wavetable/String type, the table shown as a surface, a large Position knob,
   Warp and warp mode, Octave, Semi, Fine, Level, Pan, Unison), FILTER (type, curve, a large Cutoff knob, Resonance,
   Drive, Keytrack, Env amount, Vowel), ENVELOPES (AMP / FILTER / MOD / PITCH switch, a graph of the selected envelope
   and its knobs), and a strip below: UNISON, SUB / NOISE, STRING (Decay and Tone for oscillators in String mode),
   LFO 1 and LFO 2 (shape, Sync, Rate or note value, Depth), VOICE (Poly/Mono/Legato, Glide), ARP. VOICE also has
   **Bend**: the pitch-bend range in semitones.
3. **MODULATION tab:** LFO 1 and LFO 2 with large knobs and a Retrigger switch, MOD ENVELOPE and the
   MODULATION MATRIX: 12 source → target slots with an amount slider from −100 to +100%.
4. **EFFECTS tab:** on the left, the list of ten effects in chain order – the dot turns an effect on or off, clicking
   the name scrolls to its panel, dragging the ⋮⋮ handle changes the order. On the right, a panel for every effect with
   a live graph (switched-off effects are collapsed). The **EQ, Filter, Reverb and Compressor** graphs have points you
   can drag: EQ – band frequency and gain (mouse wheel on the middle band: Q), Filter – Cutoff and Resonance,
   Reverb – Low Cut and High Cut, Compressor – threshold (up/down: ratio). Double-click a point to reset it.
   The **KEEP LOW** switch on Distortion distorts only the range above about 160 Hz.
5. **MACROS:** next to each knob are its name (double-click to rename), the target(s) it controls, and its value.

**User presets** are saved as JSON files in `%APPDATA%\Vonar\Presets` (on Linux `~/.config/Vonar/Presets`). You can
copy them between computers; afterwards choose *Rescan user presets* in the preset menu.

**MIDI controllers:** pitch bend (set the range with the **Bend** knob in VOICE, 0–24 semitones, default 2), sustain
pedal (CC64, also works with the arpeggiator), Mod Wheel and Aftertouch (as modulation sources), and
All Notes/Sound Off.

Preset categories: Bass, Lead, Guitar, Pluck, Keys, Bell, Pad, Strings, Brass, Woodwind, Arp, Drums, FX. Every preset
has a mood (Mood filter). Drums are tuned to C3; other keys change their pitch. The preset menu is sorted by category,
then alphabetically; pick a style (e.g. "Industrial", "House", "Cinematic", "Lo-Fi") with the tag filter.

## Testing

**Checked automatically in CI (GitHub Actions, on every push):**
- builds on **Linux** (VST3, Standalone, tests, renderer) and **Windows x64** (VST3, MSVC, installer),
- **DSP and plugin unit tests** (`tests/`): wavetable mipmap bandwidth, aliasing of high notes (< −50 dB),
  slopes and stability of every filter type at maximum resonance and drive, envelope times, the 16-voice limit,
  Mono/Legato, arpeggiator patterns and timing, every distortion type, the effects rack (order, EQ, filter,
  compressor, reverb tone), Pump, Delay, reverb decay, Squash, limiter ceiling, macros and the modulation matrix,
  random-parameter fuzzing (no NaN/Inf), worst-case performance, saving/loading session state, saving and loading
  user presets, migration of older presets and projects, and validity of every factory preset,
- **offline render of every factory preset** (`VOLT_Render`): fails on silence, NaN/Inf, peaks above 0 dBFS, large DC,
  tails that never decay, excessive limiting or inconsistent loudness,
- **pluginval** (strictness 5) on Linux and Windows, including opening the editor, saving/loading state and
  parameter automation.

**Checked by hand:** listening to every preset, and loading, saving projects and using the interface in FL Studio
on Windows.

## Building from source

Requirements: CMake ≥ 3.22, a C++20 compiler (Visual Studio 2022 on Windows, GCC/Clang on Linux), Git.
JUCE 8.0.15 is downloaded automatically (CMake FetchContent).

Windows:

```bash
cmake -S . -B build -A x64 -DVOLT_BUILD_TOOLS=OFF
```

```bash
cmake --build build --config Release --target VOLT_VST3
```

Result: `build/VOLT_artefacts/Release/VST3/Vonar.vst3`.

Linux (Ubuntu 24.04), with tests and the preset renderer:

```bash
sudo apt-get install -y ninja-build libasound2-dev libx11-dev libxrandr-dev libxinerama-dev libxcursor-dev libxcomposite-dev libxext-dev libxrender-dev libfreetype-dev libfontconfig1-dev xvfb
```

```bash
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release
```

```bash
cmake --build build
```

```bash
xvfb-run -a ctest --test-dir build --output-on-failure
```

```bash
./build/VOLT_Render_artefacts/Release/VOLT_Render --out render-out
```

The internal build targets are still called `VOLT_*` (the project's working name); this does not affect the plugin.
Factory presets are generated by scripts in `tools/presets/`.

## Project documentation

The project notes are written in Polish:

- [`docs/PRESETS.md`](docs/PRESETS.md) – preset list, categories, tags, macros.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) – how to submit your own presets.
- [`docs/DECISIONS.md`](docs/DECISIONS.md) – design decisions and their reasons.
- [`docs/PROGRESS.md`](docs/PROGRESS.md) – development log.

## Licence

Vonar is free software under the **GNU Affero General Public License, version 3** (AGPLv3) – full text in
[`LICENSE`](LICENSE). The plugin is free and needs no registration. You may use it (also commercially, in your
music), copy, modify and distribute it under the AGPLv3; modified versions must stay under the same licence and make
their source code available. **The music and sounds you make with Vonar are yours** – the licence does not cover them.

- **The name "Vonar" and the logo are not covered by the licence.** Distribute modified versions under a different
  name and logo so they cannot be mistaken for the original.
- **Contributions:** for now only presets are accepted, no code changes – see [`CONTRIBUTING.md`](CONTRIBUTING.md).
- The software comes with no warranty (sections 15 and 16 of the licence).

Copyright © 2026 Xami.

## Third-party components

- **JUCE 8** (audio framework, Raw Material Software Limited) – used under the AGPLv3, compatible with Vonar's licence.
  JUCE includes Steinberg's VST3 SDK (MIT licence). VST is a trademark of Steinberg Media Technologies GmbH.
- Interface font **Oxanium** – SIL Open Font License 1.1 (`resources/fonts/OFL-Oxanium.txt`).
- All wavetables, presets and artwork were made for this project (the wavetables are generated in code). No code,
  tables, presets or artwork from other synthesizers were used.
- Presets describe only the character of the sound; they contain no names of artists, albums, songs or brands, and
  the project is not affiliated with any artist or instrument maker.

Full notices: [`installer/THIRD-PARTY-NOTICES.txt`](installer/THIRD-PARTY-NOTICES.txt).

## How Vonar was made

Vonar was designed, sound-checked and tested by **Xami**. The code and presets were developed with the help of
Claude (Anthropic's AI assistant), with every sound reviewed by ear before it made it into the library.
