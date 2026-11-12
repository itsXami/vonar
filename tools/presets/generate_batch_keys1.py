#!/usr/bin/env python3
"""Stage D, batch 1: Keys (23 candidates). Warm direction from docs/SOUND_REFERENCES.md.

Plan (family -> one idea per preset). The existing 25 Keys lean on the "FM Bell" table (9 of 25), so this batch
avoids it and spreads over strings, warp FM, reed, organ and formant sources.

| Family        | Presets                                                                                   |
|---------------|-------------------------------------------------------------------------------------------|
| Electric piano| Chorus Tine EP, Phaser Tremolo EP, Barking Tine EP, Reed Growl Keys, Felt Tine EP          |
| Piano         | Muted Felt Upright, Tape Wobble Piano                                                      |
| Plucked keys  | String Clav, Wah Clav, Dulcimer Keys                                                       |
| Organ         | Warm Percussion Organ, Overdrive Rock Organ, Bellows Harmonium, Buzzy Combo Organ          |
| Synth keys    | Slow Phaser Chords, Soft Mirror Keys, Deep Echo Keys, Ooh Vowel Keys, Cross Mod Keys       |
| Lo-fi         | Smoky Lounge Keys, Cassette Keys, Dusty Upright, Warm Sine Keys                            |

    python3 tools/presets/generate_batch_keys1.py                      # write tools/presets/batches/keys1/
    python3 tools/presets/generate_batch_keys1.py --trim report.json   # level-match from a render report, then write
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import generate_candidates as gc  # noqa: E402

gp = gc.gp
BATCH = "keys1"
OUT_DIR = os.path.join(HERE, "batches", BATCH)
TRIM_FILE = os.path.join(HERE, "batches", BATCH + "_trims.json")
TARGET_LUFS = -15.0
M = gc.M
P = gp.P

gp.GROUP_TAGS.update({"warm": ["Warm"], "lofi": ["Lo-Fi"], "organ": ["Organ"], "vintage": ["Vintage"]})
_start = len(gp.PRESETS)

# ------------------------------------------------------------------------------------------- electric piano
P("warm", "Chorus Tine EP", "Keys", "Soft FM tine piano drifting through a slow, deep chorus.",
  M(("Bark", [("Warp A", 0.3)]), ("Wave", [("Mod FX Mix", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Mod Env", "Warp A", 0.35), ("Velocity", "Warp A", 0.3), ("Mod Wheel", "Mod FX Mix", 0.3)],
  tags=["Electric Piano", "Chorus", "Soft"],
  oscA_table="Basic Shapes", oscA_warp="FM", oscA_warp_amt=0.08, oscB_table="Basic Shapes", oscB_level=0.0,
  menv_decay=0.7, flt_type="LP12", flt_cutoff=3200.0, amp_attack=0.004, amp_decay=2.6, amp_sustain=0.15, amp_release=0.5,
  mfx_type="Chorus", mfx_rate=0.25, mfx_depth=0.85, mfx_mix=0.55, rev_size=0.45, rev_mix=0.12)
P("warm", "Phaser Tremolo EP", "Keys", "Round electric piano pulsing with a four-hertz tremolo inside a slow phaser.",
  M(("Trem", [("Level A", -0.3)]), ("Phase", [("Mod FX Mix", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("LFO 1", "Level A", 0.22), ("Velocity", "WT Pos A", 0.3), ("Mod Wheel", "Mod FX Mix", 0.3)],
  tags=["Electric Piano", "Phaser", "Tremolo"],
  oscA_table="Hammer Piano", oscA_pos=0.15, oscB_table="Basic Shapes", oscB_level=0.25, lfo1_rate=4.0,
  flt_type="LP24", flt_cutoff=2200.0, flt_keytrack=0.3, amp_decay=2.2, amp_sustain=0.25, amp_release=0.4,
  mfx_type="Phaser", mfx_rate=0.15, mfx_depth=0.8, mfx_mix=0.5)
P("vintage", "Barking Tine EP", "Keys", "Electric piano that stays mellow when played softly and barks with tube grit when hit hard.",
  M(("Bark", [("Warp A", 0.35)]), ("Drive", [("Dist Drive", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Warp A", 0.55), ("Velocity", "Dist Drive", 0.3), ("Mod Env", "Warp A", 0.25), ("Mod Wheel", "Mod FX Mix", 0.4)],
  tags=["Electric Piano", "Velocity", "Driven"],
  oscA_table="Basic Shapes", oscA_warp="FM", oscA_warp_amt=0.12, oscB_table="Basic Shapes", oscB_level=0.0,
  menv_decay=0.3, flt_type="LP24", flt_cutoff=1600.0, flt_envamt=0.35, fenv_decay=0.35, fenv_sustain=0.2,
  amp_decay=2.0, amp_sustain=0.2, amp_release=0.35, dist_type="Tube", dist_drive=0.55, dist_mix=0.75)
P("vintage", "Reed Growl Keys", "Keys", "Nasal reed piano squeezed into a vocal growl that opens with velocity.",
  M(("Growl", [("Warp A", 0.35)]), ("Body", [("Cutoff", 0.35)]), ("Vibe", [("Mod FX Mix", 0.4)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Warp A", 0.35), ("Velocity", "Formant", 0.2), ("LFO 1", "Pan A", 0.25), ("Mod Wheel", "Pitch", 0.003)],
  tags=["Electric Piano", "Reed", "Nasal"],
  oscA_table="Reed", oscA_pos=0.3, oscA_warp="Squeeze", oscA_warp_amt=0.45, lfo1_rate=5.2,
  flt_type="Formant", flt_cutoff=900.0, flt_res=0.4, flt_vowel=0.75, amp_decay=1.6, amp_sustain=0.45, amp_release=0.3,
  dist_type="Tube", dist_drive=0.45, dist_mix=0.6, rev_size=0.3, rev_mix=0.06)
P("warm", "Felt Tine EP", "Keys", "Muffled electric piano with a slow felt attack, made for quiet late-night chords.",
  M(("Felt", [("Cutoff", -0.3)]), ("Tine", [("Warp A", 0.3)]), ("Width", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.25), ("Random", "Pitch", 0.002), ("Mod Wheel", "Warp A", 0.3)],
  tags=["Electric Piano", "Soft", "Dark"],
  oscA_table="Basic Shapes", oscA_warp="FM", oscA_warp_amt=0.05, oscB_table="Basic Shapes", oscB_oct=1, oscB_level=0.0,
  flt_type="LP12", flt_cutoff=1400.0, amp_attack=0.025, amp_decay=3.0, amp_sustain=0.2, amp_release=0.6,
  mfx_type="Chorus", mfx_rate=0.2, mfx_mix=0.3, rev_size=0.7, rev_damping=0.75, rev_mix=0.22)

# ------------------------------------------------------------------------------------------- piano
P("warm", "Muted Felt Upright", "Keys", "Upright piano with felt over the strings: short, dark and intimate.",
  M(("Felt", [("Cutoff", -0.3)]), ("Ring", [("WT Pos A", 0.3)]), ("Air", [("Noise Level", 0.1)]), ("Room", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Random", "Pan A", 0.15)],
  tags=["Piano", "Dark", "Intimate"],
  oscA_type="String", oscA_table="Hammer Piano", oscA_pos=0.6, str_decay=7.0, str_tone=0.45,
  flt_type="LP24", flt_cutoff=1800.0, amp_sustain=1.0, amp_release=0.25, noise_level=0.01, squash=0.45,
  rev_size=0.3, rev_mix=0.12, amp_attack=0.022, dist_type="Soft", dist_drive=0.3, dist_tone=0.6, dist_mix=0.5)
P("lofi", "Tape Wobble Piano", "Keys", "Piano bounced to a worn tape: the pitch sags slowly and every note drifts a little.",
  M(("Wobble", [("Pitch", 0.004)]), ("Age", [("Dist Mix", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Room", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Pitch", 0.005), ("Random", "Pitch", 0.003), ("Velocity", "Cutoff", 0.25)],
  tags=["Piano", "Tape", "Wobble"],
  oscA_table="Hammer Piano", oscA_pos=0.25, lfo1_rate=0.45, noise_level=0.02, flt_type="LP24", flt_cutoff=1500.0,
  amp_decay=2.8, amp_sustain=0.1, amp_release=0.4, dist_type="Bitcrush", dist_drive=0.3, dist_tone=0.35, dist_mix=0.45,
  rev_size=0.4, rev_mix=0.14)

# ------------------------------------------------------------------------------------------- plucked keys
P("vintage", "String Clav", "Keys", "Thin plucked-string clav with a bright pick and a tight high-passed body.",
  M(("Pick", [("Cutoff", 0.35)]), ("Thin", [("Resonance", 0.3)]), ("Phase", [("Mod FX Mix", 0.4)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.35), ("Mod Wheel", "Resonance", 0.3)],
  tags=["Clav", "Funk", "Plucked"],
  oscA_type="String", oscA_table="Analog Square", oscA_pos=0.2, str_decay=5.0, str_tone=0.85,
  flt_type="HP", flt_cutoff=260.0, flt_res=0.25, amp_sustain=1.0, amp_release=0.08, squash=0.5, amp_attack=0.008, dist_type="Soft", dist_drive=0.5, dist_tone=0.6, dist_mix=0.75)
P("vintage", "Wah Clav", "Keys", "Clav that says 'wow' on every note as a formant envelope sweeps through it.",
  M(("Wah", [("Formant", 0.35)]), ("Quack", [("Resonance", 0.3)]), ("Grit", [("Dist Mix", 0.4)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Mod Env", "Formant", 0.6), ("Velocity", "Formant", 0.25)],
  tags=["Clav", "Funk", "Wah"],
  oscA_type="String", oscA_table="PWM", oscA_pos=0.3, str_decay=3.0, str_tone=0.8, menv_decay=0.3,
  flt_type="Formant", flt_cutoff=1000.0, flt_res=0.4, flt_vowel=0.1, amp_sustain=1.0, amp_release=0.08,
  squash=0.5, dly_time="1/16", dly_mix=0.0, amp_attack=0.008, dist_type="Soft", dist_drive=0.3, dist_tone=0.6, dist_mix=0.5)
P("warm", "Dulcimer Keys", "Keys", "Hammered dulcimer: doubled strings that beat against each other and ring on.",
  M(("Shimmer", [("Detune", 0.3)]), ("Bright", [("Cutoff", 0.35)]), ("Ring", [("WT Pos A", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Random", "Pan A", 0.3)],
  tags=["Plucked", "Folk", "Shimmer"],
  oscA_type="String", oscA_table="Pluck Body", oscA_pos=0.5, oscA_voices=2, uni_detune=0.12, uni_spread=0.8,
  str_decay=4.0, str_tone=0.65, flt_type="LP12", flt_cutoff=5000.0, amp_sustain=1.0, amp_release=0.6, squash=0.35,
  rev_size=0.55, rev_mix=0.18, amp_attack=0.008, dist_type="Soft", dist_drive=0.3, dist_tone=0.6, dist_mix=0.5)

# ------------------------------------------------------------------------------------------- organ
P("organ", "Warm Percussion Organ", "Keys", "Drawbar organ with a decaying third-harmonic click on every chord.",
  M(("Perc", [("Level B", 0.3)]), ("Drawbar", [("WT Pos A", 0.4)]), ("Rotor", [("Mod FX Mix", 0.4)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Mod Env", "Level B", 0.6), ("LFO 1", "Pan A", 0.3), ("Mod Wheel", "Mod FX Mix", 0.4)],
  tags=["Organ", "Percussion", "Drawbar"],
  oscA_table="Drawbars", oscA_pos=0.25, oscA_oct=1, oscB_table="Basic Shapes", oscB_oct=1, oscB_semi=7, oscB_level=0.0,
  menv_decay=0.25, lfo1_rate=0.8, flt_type="LP12", flt_cutoff=6000.0, amp_attack=0.002, amp_sustain=1.0, amp_release=0.06,
  mfx_type="Chorus", mfx_rate=0.8, mfx_depth=0.35, mfx_mix=0.3, rev_size=0.3, rev_mix=0.08)
P("organ", "Overdrive Rock Organ", "Keys", "Organ through a cranked amp and a spinning phaser, snarling on held chords.",
  M(("Drive", [("Dist Drive", 0.35)]), ("Spin", [("Mod FX Mix", 0.4)]), ("Bite", [("Cutoff", 0.35)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Mod Wheel", "Mod FX Mix", 0.4), ("Velocity", "Dist Drive", 0.15)],
  tags=["Organ", "Rock", "Driven"],
  oscA_table="Drive Organ", oscA_pos=0.4, oscA_oct=1, flt_type="LP24", flt_cutoff=4200.0, amp_sustain=1.0, amp_release=0.08,
  dist_type="Tube", dist_drive=0.55, dist_tone=0.55, dist_mix=0.85, mfx_type="Phaser", mfx_rate=0.9, mfx_depth=0.55,
  mfx_mix=0.35, squash=0.25)
P("organ", "Bellows Harmonium", "Keys", "Pumped reed organ that breathes in with each chord and sways with the bellows.",
  M(("Breath", [("Noise Level", 0.1)]), ("Reed", [("WT Pos A", 0.4)]), ("Sway", [("Level A", -0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("LFO 1", "Level A", 0.12), ("LFO 1", "Cutoff", 0.06), ("Mod Wheel", "Noise Level", 0.15)],
  tags=["Organ", "Reed", "Acoustic"],
  oscA_table="Reed", oscA_pos=0.5, oscB_table="Reed", oscB_pos=0.6, oscB_oct=-1, oscB_level=0.35, oscB_fine=4.0,
  noise_level=0.02, lfo1_rate=0.7, flt_type="LP24", flt_cutoff=2600.0, amp_attack=0.09, amp_sustain=1.0, amp_release=0.25,
  rev_size=0.45, rev_mix=0.14)
P("organ", "Buzzy Combo Organ", "Keys", "Thin, buzzy transistor organ with a quick vibrato, built for surf and garage.",
  M(("Buzz", [("WT Pos A", 0.4)]), ("Vibrato", [("Pitch", 0.006)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("LFO 1", "Pitch", 0.004), ("Mod Wheel", "Pitch", 0.004)],
  tags=["Organ", "Garage", "Buzzy"],
  oscA_table="PWM Saw", oscA_pos=0.35, lfo1_rate=6.5, flt_type="HP", flt_cutoff=180.0, amp_sustain=1.0, amp_release=0.05,
  dly_time="1/8", dly_feedback=0.25, dly_mix=0.1)

# ------------------------------------------------------------------------------------------- synth keys
P("warm", "Slow Phaser Chords", "Keys", "Warm analog major-seventh chords washed by a deep phaser that takes four seconds per sweep.",
  M(("Phase", [("Mod FX Mix", 0.4)]), ("Warmth", [("Cutoff", 0.35)]), ("Width", [("Detune", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.2), ("Mod Wheel", "Mod FX Mix", 0.3)],
  tags=["Phaser", "Chords", "Analog"],
  oscA_table="Analog Saw", oscA_voices=3, uni_detune=0.18, uni_spread=0.7, oscB_table="PWM", oscB_pos=0.4, oscB_level=0.35,
  flt_type="LP24", flt_cutoff=1300.0, flt_res=0.15, amp_attack=0.15, amp_decay=2.5, amp_sustain=0.6, amp_release=0.7,
  mfx_type="Phaser", mfx_rate=0.25, mfx_depth=0.9, mfx_mix=0.75, rev_size=0.6, rev_mix=0.18)
P("warm", "Soft Mirror Keys", "Keys", "Rounded triangle keys folded by mirror warp into a soft, hollow tone.",
  M(("Hollow", [("Warp A", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Vibrato", [("Pitch", 0.004)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Warp A", 0.3), ("Mod Wheel", "Warp A", 0.3), ("LFO 1", "Pitch", 0.0015)],
  tags=["Synth", "Soft", "Hollow"],
  oscA_table="Basic Shapes", oscA_pos=0.33, oscA_warp="Mirror", oscA_warp_amt=0.3, sub_level=0.15, lfo1_rate=5.0,
  flt_type="LP12", flt_cutoff=3000.0, amp_attack=0.01, amp_decay=1.5, amp_sustain=0.45, amp_release=0.35,
  rev_size=0.3, rev_mix=0.1)
P("warm", "Deep Echo Keys", "Keys", "Short, dark keys whose dotted echoes carry the rhythm.",
  M(("Echo", [("Delay Mix", 0.3)]), ("Tone", [("Cutoff", 0.35)]), ("Length", [("Level A", 0.2)]), ("Space", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Mod Wheel", "Delay Mix", 0.3)],
  tags=["Delay", "Dark", "Rhythmic"],
  oscA_table="Hollow", oscA_pos=0.4, oscB_table="Analog Square", oscB_level=0.25, oscB_oct=-1,
  flt_type="LP24", flt_cutoff=1100.0, flt_envamt=0.3, fenv_decay=0.15, fenv_sustain=0.0,
  amp_decay=0.7, amp_sustain=0.1, amp_release=0.25, squash=0.4,
  dly_mode="PingPong", dly_time="1/8D", dly_feedback=0.5, dly_mix=0.35)
P("warm", "Ooh Vowel Keys", "Keys", "Keys that sing a soft 'ooh' and open towards 'ah' the harder you play.",
  M(("Vowel", [("Formant", 0.35)]), ("Air", [("Noise Level", 0.1)]), ("Width", [("Detune", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Formant", 0.35), ("LFO 1", "Formant", 0.08), ("Mod Wheel", "Formant", 0.3)],
  tags=["Vocal", "Soft", "Formant"],
  oscA_table="Choir", oscA_pos=0.3, oscA_voices=3, uni_detune=0.15, uni_spread=0.9, lfo1_rate=0.9,
  flt_type="Formant", flt_cutoff=850.0, flt_res=0.35, flt_vowel=0.95, amp_attack=0.03, amp_decay=1.8, amp_sustain=0.4,
  amp_release=0.5, rev_size=0.6, rev_mix=0.2)
P("vintage", "Cross Mod Keys", "Keys", "Dark ring-modulated keys with a metallic edge that wobbles between the oscillators.",
  M(("Metal", [("Warp A", 0.35)]), ("Ratio", [("Pitch B", 0.02)]), ("Tone", [("Cutoff", 0.35)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Mod Env", "Warp A", 0.3), ("LFO 1", "Pitch B", 0.004), ("Mod Wheel", "Warp A", 0.3)],
  tags=["Metallic", "Dark", "Ring Mod"],
  oscA_table="Basic Shapes", oscA_pos=0.33, oscA_warp="RM", oscA_warp_amt=0.35, oscB_table="Basic Shapes",
  oscB_semi=7, oscB_fine=12.0, oscB_level=0.0, sub_level=0.2, menv_decay=0.4, lfo1_rate=4.8,
  flt_type="LP24", flt_cutoff=2000.0, amp_decay=1.4, amp_sustain=0.3, amp_release=0.3, rev_size=0.4, rev_mix=0.1)

# ------------------------------------------------------------------------------------------- lo-fi
P("lofi", "Smoky Lounge Keys", "Keys", "Dark, warm bar keys with a rounded attack, a little hiss and a tired, slightly detuned body.",
  M(("Smoke", [("Noise Level", 0.1)]), ("Warmth", [("Cutoff", 0.3)]), ("Wear", [("Dist Mix", 0.4)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Random", "Pitch", 0.004), ("Velocity", "Cutoff", 0.2), ("Mod Wheel", "Mod FX Mix", 0.3)],
  tags=["Dark", "Bar", "Warm"],
  oscA_table="Hammer Piano", oscA_pos=0.55, sub_level=0.2, noise_level=0.015,
  flt_type="LP24", flt_cutoff=1000.0, flt_res=0.15, amp_attack=0.02, amp_decay=2.2, amp_sustain=0.2, amp_release=0.4,
  dist_type="Bitcrush", dist_drive=0.12, dist_mix=0.2, mfx_type="Chorus", mfx_rate=0.3, mfx_mix=0.15, rev_size=0.3,
  rev_damping=0.8, rev_mix=0.12)
P("lofi", "Cassette Keys", "Keys", "Electric piano played back from a cassette: wow, flutter and a dull top end.",
  M(("Wow", [("Pitch", 0.004)]), ("Hiss", [("Noise Level", 0.1)]), ("Tone", [("Cutoff", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("LFO 1", "Pitch", 0.003), ("LFO 2", "Pitch", 0.0012), ("Velocity", "Warp A", 0.25)],
  tags=["Electric Piano", "Tape", "Wobble"],
  oscA_table="Basic Shapes", oscA_warp="FM", oscA_warp_amt=0.06, oscB_table="Basic Shapes", oscB_level=0.0,
  noise_level=0.02, lfo1_rate=0.5, lfo2_rate=7.0, flt_type="LP24", flt_cutoff=2000.0, amp_decay=2.4, amp_sustain=0.2,
  amp_release=0.4, dist_type="Tube", dist_drive=0.2, dist_mix=0.3)
P("lofi", "Dusty Upright", "Keys", "Hammered string piano sampled from dusty vinyl, saturated and narrow.",
  M(("Dust", [("Noise Level", 0.1)]), ("Crunch", [("Dist Mix", 0.4)]), ("Tone", [("Cutoff", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Random", "Pitch", 0.002)],
  tags=["Piano", "Vinyl", "Saturated"],
  oscA_type="String", oscA_table="Hammer Piano", oscA_pos=0.45, str_decay=7.0, str_tone=0.6, noise_level=0.025,
  uni_spread=0.0, flt_type="LP12", flt_cutoff=2200.0, amp_sustain=1.0, amp_release=0.3, squash=0.6,
  dist_type="Tube", dist_drive=0.4, dist_tone=0.45, dist_mix=0.6, rev_size=0.25, rev_mix=0.08, amp_attack=0.026)
P("warm", "Warm Sine Keys", "Keys", "Almost pure sine keys with a sub underneath: plain, round and soft.",
  M(("Body", [("Sub Level", 0.3)]), ("Edge", [("WT Pos A", 0.2)]), ("Trem", [("Level A", -0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("LFO 1", "Level A", 0.1), ("Velocity", "WT Pos A", 0.15), ("Mod Wheel", "Level A", -0.2)],
  tags=["Sine", "Soft", "Minimal"],
  oscA_table="Basic Shapes", oscA_pos=0.0, sub_level=0.3, lfo1_rate=3.5, flt_type="LP12", flt_cutoff=4000.0,
  amp_attack=0.006, amp_decay=1.8, amp_sustain=0.35, amp_release=0.4, rev_size=0.4, rev_mix=0.1)

CANDIDATES = gp.PRESETS[_start:]
del gp.PRESETS[_start:]


def preset_doc(p, trims):
    params = dict(p["params"])
    if abs(trims.get(p["name"], 0.0)) > 0.05:
        params["out_gain"] = trims[p["name"]]
    sparse = {k: (round(params[k], 5) if isinstance(params[k], float) else params[k])
              for k in gp.DEFAULTS if k in params and params[k] != gp.DEFAULTS[k]}
    return {"name": p["name"], "category": p["category"], "tags": p["tags"], "description": p["description"],
            "macros": p["macros"], "version": 1, "params": sparse}


def main():
    trims = json.load(open(TRIM_FILE)) if os.path.exists(TRIM_FILE) else {}
    if len(sys.argv) > 2 and sys.argv[1] == "--trim":
        report = json.load(open(sys.argv[2]))
        names = {p["name"] for p in CANDIDATES}
        for r in report["presets"]:
            if r["name"] in names:
                trims[r["name"]] = round(max(-24.0, min(12.0, trims.get(r["name"], 0.0) + TARGET_LUFS - r["loudness_lufs"])), 1)
        os.makedirs(os.path.dirname(TRIM_FILE), exist_ok=True)
        json.dump(dict(sorted(trims.items())), open(TRIM_FILE, "w"), indent=1)

    names = [p["name"] for p in CANDIDATES]
    existing = {p["name"].lower() for p in gp.PRESETS} | {p["name"].lower() for p in gc.CANDIDATES}
    assert len(names) == len(set(names)), "duplicate names in batch"
    clash = [n for n in names if n.lower() in existing]
    assert not clash, clash
    bad = [(n, w) for n in names for w in gc.banned_words() if gc.contains_word(n, w)]
    assert not bad, bad
    banned = gc.banned_words("kBannedEverywhere")
    for p in CANDIDATES:
        text = " | ".join([p["name"], p["description"]] + p["tags"] + p["macros"])
        assert not [w for w in banned if gc.contains_word(text, w)], p["name"]
        d = p["description"]
        assert d.endswith(".") and ". " not in d[:-1], p["name"]
    tables = {}
    for p in CANDIDATES:
        t = p["params"].get("oscA_table", "Analog Saw")
        tables[t] = tables.get(t, 0) + 1
    print("oscA tables:", dict(sorted(tables.items(), key=lambda kv: -kv[1])))

    os.makedirs(OUT_DIR, exist_ok=True)
    for f in os.listdir(OUT_DIR):
        if f.endswith(".json"):
            os.remove(os.path.join(OUT_DIR, f))
    for i, p in enumerate(CANDIDATES, start=1):
        with open(os.path.join(OUT_DIR, f"{i:03d}_{gp.slug(p['name'])}.json"), "w") as f:
            json.dump(preset_doc(p, trims), f, indent=2)
            f.write("\n")
    print("wrote", len(CANDIDATES), "candidates to", OUT_DIR)


if __name__ == "__main__":
    main()
