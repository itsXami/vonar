# Contributing to Vonar

Thank you for your interest! At this stage the project accepts **presets only** from others. Code changes
(pull requests with code, changes to the engine or the interface) are not accepted for now. Please report bugs
and ideas as an *issue*.

Polish version: [`CONTRIBUTING.pl.md`](CONTRIBUTING.pl.md).

## How to submit a preset

1. Make a sound in Vonar and save it with the **SAVE** button (name, category, tags, description). You will find
   the JSON file in `%APPDATA%\Vonar\Presets`.
2. Open an *issue* titled "Preset: name" and attach the JSON file (or several files).
3. The preset goes through the same process as the factory presets: offline render, level check, a similarity
   check against existing sounds, and listening. Presets that add something new make it into the library.

## Preset requirements

- Made from scratch in Vonar. Do not recreate presets, wavetables or names from other synthesizers.
- **No names of artists, albums, songs or brands** in the name, tags or description. Tags describe the sound
  (for example `Warm`, `Plucky`, `Dark`, `Wide`, `Lo-Fi`).
- Name: 1–3 words, unique in the library. Description: one sentence in English, ending with a full stop.
- All four macros are assigned and have labels that say what they do.
- The preset responds to velocity, and the Mod Wheel does something audible.
- Loudness similar to the factory presets (about −15 LUFS); the output limiter should not be working all the time.

## Licence of contributions

By submitting a preset, you confirm that you made it and agree to its inclusion in Vonar and its distribution
under the project's licence (AGPLv3, see `LICENSE`). The author of a preset can be credited in the
documentation if they wish.
