#!/usr/bin/env python3
"""Stage D: general instruments, batch 1 (32): Strings (15) and Woodwind (17), both new categories.

Strings: ensembles (4), solo (3), articulations (6), synthetic (2). Woodwind: flutes (6), single and double
reeds (6), free reeds and folk winds (4), extra sax (1). Solo instruments are mono / legato with vibrato on the mod wheel and
velocity on brightness, so they can be played expressively.

    python3 tools/presets/generate_batch_orch1.py [--trim report.json]
"""
import batch_common as bc

P, M = bc.P, bc.M
_s = bc.begin()
S, W = "Strings", "Woodwind"
VIB = ("Mod Wheel", "Pitch", 0.005)

# strings: ensembles -----------------------------------------------------------------------------------------
P("orchestral", "Warm String Section", S, "Full, warm string section with a slow bow and a wide concert hall.",
  M(("Bow", [("Cutoff", 0.35)]), ("Ensemble", [("Detune", 0.3)]), ("Expression", [("Level A", 0.2)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.2), ("Mod Wheel", "Cutoff", 0.3)], tags=["Ensemble", "Warm", "Orchestral"],
  oscA_table="Strings", oscA_pos=0.45, oscA_voices=5, uni_detune=0.14, uni_spread=1.0, oscB_table="Strings", oscB_pos=0.6, oscB_oct=-1, oscB_level=0.45, noise_level=0.01,
  flt_type="LP24", flt_cutoff=1800.0, amp_attack=0.9, amp_sustain=1.0, amp_release=0.9, mfx_type="Chorus", mfx_rate=0.3, mfx_mix=0.3, rev_size=0.85, rev_mix=0.35)
P("orchestral", "Chamber Strings", S, "A small chamber group: fewer players, more detail and bow noise.",
  M(("Bow", [("Noise Level", 0.1)]), ("Bright", [("Cutoff", 0.35)]), ("Players", [("Detune", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.25), ("LFO 1", "Pitch", 0.0015)], tags=["Chamber", "Intimate"],
  oscA_table="Strings", oscA_pos=0.6, oscA_voices=2, uni_detune=0.08, uni_spread=0.7, noise_level=0.012,
  lfo1_rate=5.2, flt_type="LP24", flt_cutoff=3800.0, amp_attack=0.15, amp_sustain=1.0, amp_release=0.5,
  rev_size=0.45, rev_mix=0.14)
P("orchestral", "Low Octave Strings", S, "Celli and basses in octaves: dark, heavy and growling in the low end.",
  M(("Growl", [("WT Pos A", 0.4)]), ("Weight", [("Level B", 0.3)]), ("Tone", [("Cutoff", 0.35)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Low", "Dark", "Cinematic"],
  oscA_table="Strings", oscA_pos=0.7, oscA_oct=-1, oscA_voices=3, uni_detune=0.1, oscB_table="Strings", oscB_pos=0.5,
  oscB_oct=-2, oscB_level=0.4, flt_type="LP24", flt_cutoff=1200.0, amp_attack=0.12, amp_sustain=1.0,
  amp_release=0.6, rev_size=0.7, rev_mix=0.2)
P("orchestral", "High Strings Shimmer", S, "Violins high up, divided and soft, shimmering like light on water.",
  M(("Shimmer", [("Detune", 0.3)]), ("Air", [("Cutoff", 0.35)]), ("Soft", [("Level A", -0.2)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Pitch", 0.002), ("Mod Wheel", "Detune", 0.2)], tags=["High", "Soft", "Shimmer"],
  oscA_table="Strings", oscA_pos=0.3, oscA_oct=1, oscA_voices=6, uni_detune=0.12, uni_spread=1.0, lfo1_rate=5.5,
  flt_type="LP12", flt_cutoff=6000.0, amp_attack=0.6, amp_sustain=1.0, amp_release=1.4, rev_size=0.85, rev_mix=0.3)

# strings: solo -------------------------------------------------------------------------------------------------
P("orchestral", "Solo Cello", S, "Expressive solo cello: legato bowing, mod-wheel vibrato and velocity on the bite.",
  M(("Bite", [("Cutoff", 0.35)]), ("Bow", [("Noise Level", 0.1)]), ("Body", [("WT Pos A", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[VIB, ("LFO 1", "Pitch", 0.002), ("Velocity", "Cutoff", 0.3)], tags=["Solo", "Cello", "Expressive"],
  voice_mode="Legato", glide=0.06, oscA_table="Strings", oscA_pos=0.75, oscA_oct=-1, noise_level=0.01, lfo1_rate=5.0,
  flt_type="LP24", flt_cutoff=2000.0, flt_res=0.15, amp_attack=0.12, amp_sustain=1.0, amp_release=0.4,
  rev_size=0.6, rev_mix=0.2)
P("orchestral", "Solo Violin", S, "Singing solo violin with a quick bow, a touch of rosin and a lyrical vibrato.",
  M(("Bite", [("Cutoff", 0.35)]), ("Rosin", [("Noise Level", 0.1)]), ("Vibrato", [("Pitch", 0.005)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[VIB, ("LFO 1", "Pitch", 0.0025), ("Velocity", "Cutoff", 0.3)], tags=["Solo", "Violin", "Lyrical"],
  voice_mode="Legato", glide=0.05, oscA_table="Strings", oscA_pos=0.5, oscA_oct=1, noise_level=0.012, lfo1_rate=5.8,
  flt_type="LP24", flt_cutoff=4500.0, flt_res=0.12, amp_attack=0.08, amp_sustain=1.0, amp_release=0.35,
  rev_size=0.65, rev_mix=0.22)
P("acoustic", "Fiddle Folk", S, "Rough folk fiddle with a nasal bow and quick slides into notes.",
  M(("Nasal", [("Formant", 0.35)]), ("Rasp", [("Noise Level", 0.1)]), ("Slide", [("Pitch", 0.004)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[VIB, ("Velocity", "Formant", 0.2)], tags=["Fiddle", "Folk", "Nasal"],
  voice_mode="Legato", glide=0.09, oscA_table="Strings", oscA_pos=0.85, oscA_oct=1, noise_level=0.02,
  penv_amount=-0.6, penv_decay=0.08, flt_type="Formant", flt_cutoff=1300.0, flt_res=0.35, flt_vowel=0.3,
  amp_attack=0.04, amp_sustain=1.0, amp_release=0.25, rev_size=0.3, rev_mix=0.08)

# strings: articulations -------------------------------------------------------------------------------------
P("orchestral", "Pizzicato Section", S, "Plucked string section: short, round pops with a wooden body.",
  M(("Pop", [("Cutoff", 0.35)]), ("Body", [("Resonance", 0.3)]), ("Length", [("Level A", 0.2)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Random", "Pan A", 0.3)], tags=["Pizzicato", "Plucked"],
  oscA_type="String", oscA_table="Strings", oscA_pos=0.5, oscA_voices=2, uni_detune=0.06, uni_spread=0.9,
  str_decay=1.2, str_tone=0.5, flt_type="LP24", flt_cutoff=2200.0, amp_attack=0.014, amp_sustain=1.0,
  amp_release=0.12, squash=0.6, dist_type="Soft", dist_drive=0.3, dist_mix=0.5, rev_size=0.8, rev_mix=0.35)
P("orchestral", "Tremolo Strings", S, "Strings bowing a fast measured tremolo, every stroke rearticulated, for suspense.",
  M(("Bite", [("Cutoff", 0.35)]), ("Tension", [("Resonance", 0.3)]), ("Ensemble", [("Detune", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Mod Wheel", "Cutoff", 0.3), ("Random", "Cutoff", 0.06)], tags=["Tremolo", "Suspense", "Cinematic"],
  arp_on=True, arp_mode="Up", arp_rate="1/32", arp_gate=0.75, oscA_table="Strings", oscA_pos=0.75, oscA_oct=-1, oscA_voices=3,
  uni_detune=0.12, noise_level=0.012, flt_type="LP24", flt_cutoff=1700.0, flt_res=0.2, amp_attack=0.006, amp_decay=0.08,
  amp_sustain=0.6, amp_release=0.05, rev_size=0.75, rev_mix=0.24)
P("orchestral", "Staccato Strings", S, "Short, punchy string stabs for rhythmic orchestral parts.",
  M(("Punch", [("Cutoff", 0.35)]), ("Length", [("Level A", 0.2)]), ("Ensemble", [("Detune", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.35)], tags=["Staccato", "Punchy", "Rhythmic"],
  oscA_table="Strings", oscA_pos=0.65, oscA_oct=-1, oscA_voices=4, uni_detune=0.12, flt_type="LP24", flt_cutoff=1400.0,
  flt_envamt=0.5, fenv_decay=0.12, fenv_sustain=0.2, amp_attack=0.015, amp_decay=0.35, amp_sustain=0.25,
  amp_release=0.15, squash=0.3, noise_level=0.015, rev_size=0.85, rev_mix=0.4)
P("ambient", "Harmonics Strings", S, "Glassy, whistling string harmonics floating high and thin.",
  M(("Glass", [("WT Pos A", 0.4)]), ("Air", [("Noise Level", 0.1)]), ("Float", [("Pitch", 0.003)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Pitch", 0.002), ("Random", "Pan A", 0.3)], tags=["Harmonics", "Glassy", "Eerie"],
  oscA_table="Glass Harmonics", oscA_pos=0.2, oscA_oct=1, oscA_voices=2, uni_detune=0.06, noise_level=0.015,
  lfo1_rate=5.0, flt_type="BP", flt_cutoff=2400.0, flt_res=0.2, flt_keytrack=0.6, amp_attack=0.5, amp_sustain=1.0,
  amp_release=1.2, rev_size=0.85, rev_mix=0.3)
P("metallic", "Sul Ponticello", S, "Bow played right at the bridge: thin, metallic, ghostly overtones.",
  M(("Bridge", [("Resonance", 0.3)]), ("Metal", [("WT Pos A", 0.4)]), ("Bow", [("Noise Level", 0.1)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "WT Pos A", 0.1), ("Mod Wheel", "Resonance", 0.3)], tags=["Ponticello", "Ghostly", "Thin"],
  oscA_table="Strings", oscA_pos=0.95, oscA_voices=3, uni_detune=0.1, noise_level=0.02, lfo1_rate=0.8,
  flt_type="HP", flt_cutoff=900.0, flt_res=0.35, amp_attack=0.3, amp_sustain=1.0, amp_release=0.8,
  rev_size=0.75, rev_mix=0.26)
P("orchestral", "Crescendo Swell Strings", S, "Strings that start in a whisper and swell to full force over three seconds.",
  M(("Swell", [("Cutoff", 0.35)]), ("Force", [("Dist Mix", 0.3)]), ("Ensemble", [("Detune", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Mod Env", "Cutoff", 0.5), ("Mod Env", "WT Pos A", 0.3)], tags=["Swell", "Crescendo", "Cinematic"],
  oscA_table="Strings", oscA_pos=0.35, oscA_oct=-1, oscA_voices=5, uni_detune=0.14, uni_spread=1.0, menv_attack=3.0,
  menv_sustain=1.0, flt_type="LP24", flt_cutoff=800.0, amp_attack=1.5, amp_sustain=1.0, amp_release=1.0,
  dist_type="Tube", dist_drive=0.35, dist_mix=0.4, rev_size=0.85, rev_mix=0.28)

# strings: synthetic --------------------------------------------------------------------------------------------
P("orchestral", "Piccolo Bright", W, "Piccolo flute an octave above the flute: bright, piercing and agile.",
  M(("Bright", [("Cutoff", 0.35)]), ("Breath", [("Noise Level", 0.1)]), ("Vibrato", [("Pitch", 0.005)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[VIB, ("LFO 1", "Pitch", 0.0015), ("Mod Env", "Noise Level", 0.05)], tags=["Piccolo", "Bright", "High"],
  voice_mode="Legato", glide=0.02, oscA_table="Basic Shapes", oscA_pos=0.12, oscA_oct=1, noise_level=0.015,
  lfo1_rate=5.8, menv_decay=0.05, flt_type="LP12", flt_cutoff=9000.0, amp_attack=0.025, amp_sustain=1.0,
  amp_release=0.12, rev_size=0.6, rev_mix=0.18)
P("vintage", "Divide Down Strings", S, "Thin, buzzy string machine with octave layers and a flanged shimmer.",
  M(("Octave", [("Level B", 0.3)]), ("Buzz", [("WT Pos A", 0.4)]), ("Flange", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Pitch", 0.002)], tags=["String Machine", "Buzzy"],
  oscA_table="PWM Saw", oscA_pos=0.6, oscB_table="PWM Saw", oscB_pos=0.6, oscB_oct=1, oscB_level=0.5, lfo1_rate=6.0,
  flt_type="HP", flt_cutoff=250.0, amp_attack=0.2, amp_sustain=1.0, amp_release=0.6, mfx_type="Flanger",
  mfx_rate=0.25, mfx_mix=0.4, rev_size=0.5, rev_mix=0.14)
P("orchestral", "Col Legno Taps", S, "Strings struck with the wood of the bow, ticking in eighth notes while you hold the chord.",
  M(("Wood", [("Noise Level", 0.1)]), ("Pitch", [("Resonance", 0.3)]), ("Length", [("Level A", 0.2)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Random", "Pan A", 0.3)], tags=["Col Legno", "Percussive", "Dry"],
  arp_on=True, arp_mode="Up", arp_rate="1/16", arp_gate=0.4, oscA_table="Strings", oscA_pos=0.8, oscA_level=1.0, noise_level=0.4, flt_type="BP", flt_cutoff=1500.0, flt_res=0.45,
  flt_keytrack=0.8, amp_attack=0.002, amp_decay=0.18, amp_sustain=0.0, amp_release=0.08, squash=0.45,
  rev_size=0.6, rev_mix=0.16)
P("orchestral", "Concert Flute", W, "Pure concert flute with a soft breath, a chiff on the attack and a lyrical vibrato.",
  M(("Breath", [("Noise Level", 0.1)]), ("Tone", [("Cutoff", 0.35)]), ("Vibrato", [("Pitch", 0.005)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[VIB, ("LFO 1", "Pitch", 0.002), ("Velocity", "Noise Level", 0.05), ("Mod Env", "Noise Level", 0.08)],
  tags=["Flute", "Breathy", "Lyrical"],
  voice_mode="Legato", glide=0.04, oscA_table="Basic Shapes", oscA_pos=0.08, oscB_table="Basic Shapes", oscB_oct=1,
  oscB_level=0.12, noise_level=0.03, lfo1_rate=5.2, menv_decay=0.08, flt_type="LP12", flt_cutoff=4500.0,
  amp_attack=0.05, amp_sustain=1.0, amp_release=0.2, rev_size=0.6, rev_mix=0.2)
P("acoustic", "Breathy Pan Flute", W, "Bamboo pan pipes: more air than tone, with a hollow chiff on every note.",
  M(("Air", [("Noise Level", 0.15)]), ("Hollow", [("Resonance", 0.3)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[VIB, ("Mod Env", "Noise Level", 0.15), ("Velocity", "Noise Level", 0.06)], tags=["Pan Flute", "Breathy", "Bamboo"],
  voice_mode="Legato", glide=0.03, oscA_table="Basic Shapes", oscA_pos=0.0, noise_level=0.12, menv_decay=0.1,
  flt_type="BP", flt_cutoff=1200.0, flt_res=0.25, flt_keytrack=1.0, amp_attack=0.03, amp_sustain=1.0,
  amp_release=0.25, dly_time="1/4", dly_mix=0.08, rev_size=0.7, rev_mix=0.24)
P("orchestral", "Alto Flute Warm", W, "Lower, warmer alto flute with a dark, velvety breath.",
  M(("Breath", [("Noise Level", 0.1)]), ("Warmth", [("Cutoff", 0.35)]), ("Vibrato", [("Pitch", 0.005)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[VIB, ("LFO 1", "Pitch", 0.0018), ("Velocity", "Cutoff", 0.2)], tags=["Flute", "Warm", "Dark"],
  voice_mode="Legato", glide=0.05, oscA_table="Hollow", oscA_pos=0.1, oscA_oct=-1, noise_level=0.025, lfo1_rate=4.8,
  flt_type="LP24", flt_cutoff=1800.0, amp_attack=0.08, amp_sustain=1.0, amp_release=0.25, rev_size=0.6, rev_mix=0.2)
P("acoustic", "Wooden Recorder", W, "Plain wooden recorder: pure, a little hollow, no vibrato.",
  M(("Wood", [("Level B", 0.3)]), ("Tone", [("Cutoff", 0.35)]), ("Breath", [("Noise Level", 0.1)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Mod Env", "Noise Level", 0.06)], tags=["Recorder", "Pure", "Plain"],
  voice_mode="Legato", glide=0.02, oscA_table="Basic Shapes", oscA_pos=0.15, oscB_table="Analog Square",
  oscB_level=0.08, noise_level=0.01, menv_decay=0.06, flt_type="LP12", flt_cutoff=3500.0, amp_attack=0.03,
  amp_sustain=1.0, amp_release=0.12, rev_size=0.35, rev_mix=0.1)
P("ambient", "Ocarina Song", W, "Round clay ocarina, soft and pure, singing in a small stone room.",
  M(("Clay", [("Cutoff", 0.35)]), ("Breath", [("Noise Level", 0.1)]), ("Vibrato", [("Pitch", 0.005)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[VIB, ("LFO 1", "Pitch", 0.0012)], tags=["Ocarina", "Round", "Pure"],
  voice_mode="Legato", glide=0.04, oscA_table="Basic Shapes", oscA_pos=0.0, oscA_oct=1, sub_level=0.0,
  noise_level=0.008, lfo1_rate=4.5, flt_type="LP12", flt_cutoff=2600.0, amp_attack=0.06, amp_sustain=1.0,
  amp_release=0.2, rev_size=0.45, rev_damping=0.6, rev_mix=0.16)

# woodwind: single and double reeds ------------------------------------------------------------------------------
P("orchestral", "Clarinet Chalumeau", W, "Clarinet in its low register: hollow, woody and round.",
  M(("Reed", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Breath", [("Noise Level", 0.1)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[VIB, ("Velocity", "Cutoff", 0.3)], tags=["Clarinet", "Hollow", "Woody"],
  voice_mode="Legato", glide=0.03, oscA_table="Analog Square", oscA_pos=0.25, oscA_oct=-1, noise_level=0.008,
  flt_type="LP24", flt_cutoff=1500.0, flt_envamt=0.15, fenv_decay=0.2, fenv_sustain=0.6, amp_attack=0.04,
  amp_sustain=1.0, amp_release=0.15, rev_size=0.55, rev_mix=0.16)
P("orchestral", "Oboe Solo", W, "Nasal, singing oboe with a focused reed tone and gentle vibrato.",
  M(("Nasal", [("Formant", 0.35)]), ("Reed", [("WT Pos A", 0.4)]), ("Vibrato", [("Pitch", 0.005)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[VIB, ("LFO 1", "Pitch", 0.0018), ("Velocity", "Formant", 0.15)], tags=["Oboe", "Nasal", "Solo"],
  voice_mode="Legato", glide=0.03, oscA_table="Reed", oscA_pos=0.55, lfo1_rate=5.4, flt_type="Formant",
  flt_cutoff=1100.0, flt_res=0.35, flt_vowel=0.3, amp_attack=0.05, amp_sustain=1.0, amp_release=0.15,
  rev_size=0.55, rev_mix=0.18)
P("orchestral", "Bassoon Low", W, "Low, buzzy bassoon with a dry, slightly comic reed.",
  M(("Buzz", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Nasal", [("Formant", 0.35)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[VIB, ("Velocity", "Cutoff", 0.25)], tags=["Bassoon", "Low", "Reedy"],
  voice_mode="Legato", glide=0.03, oscA_table="Reed", oscA_pos=0.8, oscA_oct=-2, flt_type="Formant",
  flt_cutoff=700.0, flt_res=0.3, flt_vowel=0.7, amp_attack=0.05, amp_sustain=1.0, amp_release=0.15,
  rev_size=0.5, rev_mix=0.14)
P("warm", "Tenor Sax Growl", W, "Breathy tenor sax that growls when you play harder.",
  M(("Growl", [("Dist Drive", 0.35)]), ("Breath", [("Noise Level", 0.1)]), ("Tone", [("Cutoff", 0.35)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[VIB, ("Velocity", "Dist Drive", 0.35), ("Velocity", "Cutoff", 0.25), ("LFO 1", "Pitch", 0.0015)],
  tags=["Saxophone", "Breathy", "Growl"],
  voice_mode="Legato", glide=0.05, oscA_table="Reed", oscA_pos=0.4, oscA_oct=-1, oscA_warp="Squeeze",
  oscA_warp_amt=0.4, noise_level=0.045, lfo1_rate=5.0, flt_type="LP24", flt_cutoff=3200.0, flt_res=0.2,
  amp_attack=0.04, amp_sustain=1.0, amp_release=0.2, dist_type="Tube", dist_drive=0.3, dist_mix=0.6,
  rev_size=0.4, rev_mix=0.12)
P("warm", "Soprano Sax Smooth", W, "Smooth, sweet soprano sax with a bright reed and long vibrato.",
  M(("Sweet", [("Cutoff", 0.35)]), ("Reed", [("WT Pos A", 0.4)]), ("Vibrato", [("Pitch", 0.005)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[VIB, ("LFO 1", "Pitch", 0.002), ("Velocity", "Cutoff", 0.25)], tags=["Saxophone", "Smooth", "Sweet"],
  voice_mode="Legato", glide=0.06, oscA_table="Reed", oscA_pos=0.3, noise_level=0.01, lfo1_rate=5.6,
  flt_type="LP24", flt_cutoff=3600.0, amp_attack=0.05, amp_sustain=1.0, amp_release=0.25, mfx_type="Chorus",
  mfx_mix=0.15, rev_size=0.6, rev_mix=0.2)
P("ambient", "Duduk Lament", W, "Dark, mournful double reed with a slow breath and long, bending notes.",
  M(("Mourn", [("Cutoff", -0.3)]), ("Bend", [("Pitch", 0.006)]), ("Breath", [("Noise Level", 0.1)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[VIB, ("Velocity", "Cutoff", 0.2)], tags=["Double Reed", "Dark", "Mournful"],
  voice_mode="Legato", glide=0.14, oscA_table="Reed", oscA_pos=0.2, noise_level=0.015, penv_amount=-0.4,
  penv_decay=0.25, flt_type="LP24", flt_cutoff=850.0, flt_res=0.15, amp_attack=0.15, amp_sustain=1.0,
  amp_release=0.4, rev_size=0.75, rev_mix=0.26)

# woodwind: free reeds and folk ----------------------------------------------------------------------------------
P("vintage", "Blues Harmonica", W, "Cupped blues harp: reedy, overdriven and bending down into notes.",
  M(("Cup", [("Formant", 0.35)]), ("Drive", [("Dist Drive", 0.35)]), ("Bend", [("Pitch", 0.006)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[VIB, ("Velocity", "Dist Drive", 0.25), ("LFO 1", "Level A", 0.12)], tags=["Harmonica", "Blues", "Driven"],
  voice_mode="Legato", glide=0.08, oscA_table="Reed", oscA_pos=0.6, penv_amount=-0.8, penv_decay=0.12,
  lfo1_rate=5.5, flt_type="Formant", flt_cutoff=1200.0, flt_res=0.3, flt_vowel=0.4, amp_attack=0.03,
  amp_sustain=1.0, amp_release=0.15, dist_type="Tube", dist_drive=0.45, dist_mix=0.7, rev_size=0.3, rev_mix=0.08)
P("acoustic", "Musette Accordion", W, "French musette accordion: three reeds tuned apart for that wavering shimmer.",
  M(("Musette", [("Detune", 0.3)]), ("Bellows", [("Level A", 0.2)]), ("Tone", [("Cutoff", 0.35)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("LFO 1", "Level A", 0.08)], tags=["Accordion", "Musette", "Wavering"],
  oscB_table="Reed", oscB_pos=0.7, oscB_oct=-1, oscB_level=0.5, oscA_table="Reed", oscA_pos=0.5, oscA_voices=3, uni_detune=0.2, uni_spread=0.6, lfo1_rate=0.6, flt_type="LP24",
  flt_cutoff=2600.0, amp_attack=0.012, amp_sustain=1.0, amp_release=0.12, rev_size=0.35, rev_mix=0.1)
P("ambient", "Shakuhachi Breath", W, "Bamboo shakuhachi: breathy, bending attacks and a wild, airy tone.",
  M(("Breath", [("Noise Level", 0.15)]), ("Bend", [("Pitch A", 0.03)]), ("Tone", [("Cutoff", 0.35)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[VIB, ("Mod Env", "Noise Level", 0.2), ("Velocity", "Noise Level", 0.08)], tags=["Shakuhachi", "Breathy", "Airy"],
  voice_mode="Legato", glide=0.06, oscA_table="Basic Shapes", oscA_pos=0.12, oscA_oct=-1, noise_level=0.035, penv_amount=-2.0,
  penv_decay=0.25, menv_decay=0.3, flt_type="LP12", flt_cutoff=2200.0,
  amp_attack=0.08, amp_sustain=1.0, amp_release=0.3, rev_size=0.8, rev_mix=0.28)
P("warm", "Subtone Alto Sax", W, "Breathy subtone alto sax for late-night ballads: more air than reed.",
  M(("Air", [("Noise Level", 0.15)]), ("Reed", [("Cutoff", 0.35)]), ("Vibrato", [("Pitch", 0.005)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[VIB, ("LFO 1", "Pitch", 0.0015), ("Velocity", "Cutoff", 0.3)], tags=["Saxophone", "Subtone", "Breathy"],
  voice_mode="Legato", glide=0.07, oscA_table="Reed", oscA_pos=0.25, oscA_oct=-1, noise_level=0.06, lfo1_rate=4.6,
  flt_type="LP24", flt_cutoff=1300.0, amp_attack=0.1, amp_sustain=1.0, amp_release=0.3, rev_size=0.45, rev_mix=0.14)
P("acoustic", "Drone Chanter", W, "Bagpipe-style chanter over a held drone a fifth and an octave below.",
  M(("Drone", [("Level B", 0.3)]), ("Reed", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.15)], tags=["Bagpipe", "Drone", "Reedy"],
  voice_mode="Legato", glide=0.01, oscA_table="Reed", oscA_pos=0.75, oscB_table="Reed", oscB_pos=0.6, oscB_oct=-1,
  oscB_semi=-5, oscB_level=0.5, flt_type="Formant", flt_cutoff=1400.0, flt_res=0.4, flt_vowel=0.2, amp_attack=0.03, amp_sustain=1.0,
  amp_release=0.15, rev_size=0.6, rev_mix=0.16)

CANDIDATES = bc.end(_s)

if __name__ == "__main__":
    bc.write("orch1", CANDIDATES)
