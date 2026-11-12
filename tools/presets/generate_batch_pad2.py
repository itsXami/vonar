#!/usr/bin/env python3
"""Stage D: Pad batch 2 (28). Every pad is built around a different kind of movement, so they do not collapse into
"saw + chorus + reverb" (the existing pads measure only 1.21 median distance to their nearest neighbour).

Movement families: wavetable sweep by Mod Env (5), LFO / sample-and-hold (5), formant and vocal (5), warp
evolution (4), filter and phaser (4), noise, comb and texture (5). Warm by default (docs/SOUND_REFERENCES.md).

    python3 tools/presets/generate_batch_pad2.py [--trim report.json]
"""
import batch_common as bc

P, M = bc.P, bc.M
_s = bc.begin()
C = "Pad"

# wavetable sweep by Mod Env -----------------------------------------------------------------------------------
P("ambient", "Slow Bloom Pad", C, "Dark pad that opens over eight seconds, like a flower unfolding.",
  M(("Bloom", [("WT Pos A", 0.4)]), ("Warmth", [("Cutoff", 0.35)]), ("Width", [("Detune", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Mod Env", "WT Pos A", 0.7), ("Mod Env", "Cutoff", 0.3), ("Mod Wheel", "Cutoff", 0.3)], tags=["Evolving", "Dark", "Slow"],
  oscA_table="Formant Sweep", oscA_pos=0.0, oscA_voices=3, uni_detune=0.15, uni_spread=0.8, menv_attack=8.0,
  menv_sustain=1.0, menv_release=4.0, flt_type="LP24", flt_cutoff=900.0, amp_attack=1.2, amp_sustain=1.0,
  amp_release=2.5, rev_size=0.8, rev_mix=0.26)
P("ambient", "Glacier Drift", C, "Cold glassy pad sliding slowly from bright ice to a deep blue hum.",
  M(("Ice", [("WT Pos A", 0.4)]), ("Depth", [("Sub Level", 0.25)]), ("Shimmer", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Mod Env", "WT Pos A", -0.7), ("LFO 1", "Pan A", 0.25)], tags=["Cold", "Glassy", "Evolving"],
  oscA_table="Glass Harmonics", oscA_pos=0.9, oscA_voices=2, uni_detune=0.1, menv_attack=0.01, menv_decay=10.0,
  menv_sustain=0.0, lfo1_rate=0.15, flt_type="LP12", flt_cutoff=5000.0, amp_attack=0.9, amp_sustain=1.0,
  amp_release=2.5, mfx_type="Chorus", mfx_rate=0.2, mfx_mix=0.4, rev_size=0.85, rev_mix=0.28)
P("warm", "Choir To Metal Pad", C, "Starts as a warm choir and slowly turns into ringing metal over the held chord.",
  M(("Morph", [("WT Pos B", 0.4)]), ("Choir", [("Level A", 0.2)]), ("Width", [("Detune", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Mod Env", "Level B", 0.6), ("Mod Env", "Level A", -0.4)], tags=["Choir", "Metallic", "Morph"],
  oscA_table="Choir", oscA_pos=0.3, oscA_voices=3, uni_detune=0.12, oscB_table="Bell Metal", oscB_pos=0.4,
  oscB_level=0.0, menv_attack=6.0, menv_sustain=1.0, flt_type="LP24", flt_cutoff=3000.0, amp_attack=0.7,
  amp_sustain=1.0, amp_release=2.0, rev_size=0.75, rev_mix=0.24)
P("warm", "Saturated Sweep Pad", C, "Even-harmonic warm pad whose saturation rises the longer you hold.",
  M(("Heat", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Drive", [("Dist Drive", 0.35)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Mod Env", "WT Pos A", 0.6), ("Mod Env", "Dist Drive", 0.2)], tags=["Warm", "Saturated"],
  oscA_table="Even Saturate", oscA_pos=0.1, oscA_voices=4, uni_detune=0.14, uni_spread=0.8, menv_attack=5.0,
  menv_sustain=1.0, flt_type="LP24", flt_cutoff=1600.0, amp_attack=0.6, amp_sustain=1.0, amp_release=1.8,
  dist_type="Tube", dist_drive=0.3, dist_mix=0.5, rev_size=0.6, rev_mix=0.2)
P("ambient", "Spectral Rise Pad", C, "Each chord climbs through the harmonic series, ending bright and airy.",
  M(("Rise", [("WT Pos A", 0.4)]), ("Air", [("Noise Level", 0.1)]), ("Width", [("Detune", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Mod Env", "WT Pos A", 0.8), ("Mod Env", "Cutoff", 0.4)], tags=["Rising", "Bright", "Evolving"],
  oscA_table="Saw Octaves", oscA_pos=0.0, oscA_voices=3, uni_detune=0.1, menv_attack=1.8, menv_sustain=1.0,
  noise_level=0.03, flt_type="LP12", flt_cutoff=3200.0, amp_attack=0.6, amp_sustain=1.0, amp_release=2.0,
  rev_size=0.75, rev_mix=0.24)

# LFO / sample-and-hold -----------------------------------------------------------------------------------------
P("electronic", "Random Step Pad", C, "Pad whose filter jumps to a new random spot on every eighth note.",
  M(("Steps", [("Cutoff", 0.35)]), ("Res", [("Resonance", 0.3)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Cutoff", 0.35)], tags=["Sample & Hold", "Rhythmic"],
  oscA_table="Analog Saw", oscA_voices=3, uni_detune=0.15, lfo1_shape="S&H", lfo1_sync=True, lfo1_div="1/8",
  flt_type="LP24", flt_cutoff=1200.0, flt_res=0.35, amp_attack=0.3, amp_sustain=1.0, amp_release=1.0,
  dly_mode="PingPong", dly_time="1/8D", dly_mix=0.15, rev_size=0.6, rev_mix=0.18)
P("warm", "Breathing Pad", C, "Warm pad that swells and fades like slow breathing, twice per bar.",
  M(("Breath", [("Level A", -0.3)]), ("Warmth", [("Cutoff", 0.35)]), ("Width", [("Detune", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Level A", 0.55), ("LFO 1", "Cutoff", 0.3)], tags=["Breathing", "Warm", "Pulsing"],
  oscA_table="Hollow", oscA_pos=0.4, oscA_voices=2, uni_detune=0.06, uni_spread=0.1, lfo1_shape="Triangle", lfo1_sync=True,
  lfo1_div="1/2", flt_type="LP24", flt_cutoff=850.0, amp_attack=0.6, amp_sustain=1.0, amp_release=1.5,
  rev_size=0.6, rev_mix=0.2)
P("ambient", "Octave Shimmer Pad", C, "Airy pad with a glassy layer two octaves up that fades in slowly above the chord.",
  M(("Shimmer", [("Level B", 0.3)]), ("Air", [("Cutoff", 0.35)]), ("Width", [("Detune", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Mod Env", "Level B", 0.5), ("LFO 1", "Pan B", 0.4)], tags=["Shimmer", "Airy", "Bright"],
  oscA_table="Basic Shapes", oscA_pos=0.33, oscA_voices=2, uni_detune=0.08, oscB_table="Glass Harmonics", oscB_pos=0.5,
  oscB_oct=2, oscB_level=0.0, menv_attack=3.0, menv_sustain=1.0, lfo1_rate=0.2, flt_type="LP12", flt_cutoff=9000.0,
  amp_attack=1.2, amp_sustain=1.0, amp_release=2.5, rev_size=0.9, rev_mix=0.34)
P("electronic", "Stereo Swirl Pad", C, "Pad that circles around your head as two LFOs pan its oscillators apart.",
  M(("Swirl", [("Pan A", 0.3)]), ("Tone", [("Cutoff", 0.35)]), ("Width", [("Detune", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Pan A", 0.8), ("LFO 2", "Pan B", -0.8)], tags=["Stereo", "Swirling", "Wide"],
  oscA_table="Saw Octaves", oscA_pos=0.25, oscB_table="Hollow", oscB_pos=0.4, oscB_level=0.6, lfo1_rate=0.3,
  lfo2_rate=0.23, flt_type="LP24", flt_cutoff=1800.0, amp_attack=0.5, amp_sustain=1.0, amp_release=1.5,
  rev_size=0.65, rev_mix=0.2)
P("ambient", "Tremolo Halo Pad", C, "Soft halo of sine and triangle, shimmering in a fast, gentle tremolo.",
  M(("Shimmer", [("Level A", -0.3)]), ("Halo", [("Level B", 0.3)]), ("Air", [("Cutoff", 0.35)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Level A", 0.5), ("LFO 2", "Level B", 0.5)], tags=["Tremolo", "Soft", "Halo"],
  oscA_table="Basic Shapes", oscA_pos=0.1, oscB_table="Basic Shapes", oscB_pos=0.33, oscB_oct=2, oscB_level=0.45,
  lfo1_rate=7.5, lfo2_rate=5.0, flt_type="LP12", flt_cutoff=5000.0, amp_attack=0.6, amp_sustain=1.0,
  amp_release=2.0, rev_size=0.8, rev_mix=0.26)

# formant and vocal --------------------------------------------------------------------------------------------
P("warm", "Granite Drone Pad", C, "Low, dark drone with a folded grit that grinds slowly under the chord.",
  M(("Grit", [("Dist Drive", 0.35)]), ("Weight", [("Sub Level", 0.25)]), ("Tone", [("Cutoff", 0.35)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Dist Drive", 0.15), ("Mod Wheel", "Cutoff", 0.3)], tags=["Drone", "Dark", "Gritty"],
  oscA_table="Rasp", oscA_pos=0.3, oscA_oct=-1, sub_level=0.2, lfo1_rate=0.15, flt_type="LP24", flt_cutoff=650.0,
  flt_res=0.2, amp_attack=1.5, amp_sustain=1.0, amp_release=2.5, dist_type="Fold", dist_drive=0.35, dist_mix=0.6,
  rev_size=0.5, rev_mix=0.12)
P("ambient", "Lilting Voice Pad", C, "Voice and synth layered in a gentle, swaying lilt with a soft vibrato.",
  M(("Voice", [("Level A", 0.2)]), ("Lilt", [("Pitch", 0.004)]), ("Width", [("Detune", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Pitch", 0.0025), ("LFO 2", "Formant", 0.15)], tags=["Vocal", "Gentle", "Wide"],
  oscA_table="Vowels", oscA_pos=0.6, oscA_voices=3, uni_detune=0.1, uni_spread=1.0, oscB_table="Analog Saw",
  oscB_level=0.3, lfo1_rate=5.2, lfo2_rate=0.35, flt_type="Formant", flt_cutoff=900.0, flt_res=0.25,
  flt_vowel=0.5, amp_attack=0.45, amp_sustain=1.0, amp_release=1.5, rev_size=0.75, rev_mix=0.24)
P("ambient", "Whispered Vowels", C, "Breathy, almost whispered vowels drifting from 'ah' to 'oo'.",
  M(("Whisper", [("Noise Level", 0.15)]), ("Vowel", [("Formant", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Formant", 0.4)], tags=["Breathy", "Vocal", "Whisper"],
  oscA_table="Vocal Fry", oscA_pos=0.3, oscA_level=0.4, noise_level=0.12, lfo1_shape="Triangle", lfo1_rate=0.12,
  flt_type="Formant", flt_cutoff=1000.0, flt_res=0.45, flt_vowel=0.5, amp_attack=0.7, amp_sustain=1.0,
  amp_release=1.8, rev_size=0.8, rev_mix=0.28)
P("warm", "Talking Pad", C, "Pad that slowly mouths words: dual formants trading places every bar.",
  M(("Talk", [("WT Pos A", 0.4)]), ("Mouth", [("Formant", 0.35)]), ("Width", [("Detune", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "WT Pos A", 0.4), ("LFO 1", "Formant", 0.2)], tags=["Talking", "Formant"],
  oscA_table="Dual Formant", oscA_pos=0.3, oscA_voices=2, uni_detune=0.08, lfo1_shape="Triangle", lfo1_sync=True,
  lfo1_div="1/4", flt_type="LP24", flt_cutoff=2600.0, flt_res=0.35, amp_attack=0.4, amp_sustain=1.0, amp_release=1.4,
  rev_size=0.6, rev_mix=0.2)
P("ambient", "Distant Choir Pad", C, "Choir heard from the far end of a cathedral, soft and blurred.",
  M(("Distance", [("Cutoff", -0.3)]), ("Choir", [("WT Pos A", 0.4)]), ("Blur", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Random", "WT Pos A", 0.15)], tags=["Choir", "Distant", "Cathedral"],
  oscA_table="Choir", oscA_pos=0.55, oscA_voices=5, uni_detune=0.18, uni_spread=1.0, flt_type="LP24",
  flt_cutoff=1300.0, amp_attack=1.0, amp_sustain=1.0, amp_release=2.5, mfx_type="Chorus", mfx_rate=0.15,
  mfx_mix=0.3, rev_size=0.92, rev_damping=0.7, rev_mix=0.45)

# warp evolution -------------------------------------------------------------------------------------------------
P("electronic", "Sync Sweep Pad", C, "Wide pad whose hard-sync edge sweeps up and down every two bars.",
  M(("Sync", [("Warp A", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Width", [("Detune", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Warp A", 0.35)], tags=["Sync", "Sweep", "Wide"],
  oscA_table="Analog Saw", oscA_voices=4, uni_detune=0.15, uni_spread=0.9, oscA_warp="Sync", oscA_warp_amt=0.2,
  lfo1_shape="Triangle", lfo1_sync=True, lfo1_div="2/1", flt_type="LP24", flt_cutoff=2400.0, amp_attack=0.4,
  amp_sustain=1.0, amp_release=1.5, rev_size=0.6, rev_mix=0.2)
P("metallic", "FM Desert Pad", C, "Hot, dusty FM pad where the brightness shimmers like air above sand.",
  M(("Heat", [("Warp A", 0.35)]), ("Haze", [("Mod FX Mix", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Warp A", 0.12), ("LFO 2", "Pitch B", 0.003)], tags=["FM", "Warm", "Shimmer"],
  oscA_table="Basic Shapes", oscA_voices=3, uni_detune=0.1, oscA_warp="FM", oscA_warp_amt=0.2, oscB_table="Basic Shapes",
  oscB_semi=7, oscB_level=0.0, lfo1_rate=0.3, lfo2_rate=0.17, flt_type="LP24", flt_cutoff=2800.0, amp_attack=0.6,
  amp_sustain=1.0, amp_release=1.8, mfx_type="Flanger", mfx_rate=0.1, mfx_mix=0.25, rev_size=0.7, rev_mix=0.22)
P("warm", "Mirror Fold Pad", C, "Folded, hollow pad that grows from flute-soft to reedy as you push the mod wheel.",
  M(("Fold", [("Warp A", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Width", [("Detune", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Mod Wheel", "Warp A", 0.5), ("LFO 1", "Warp A", 0.08)], tags=["Hollow", "Expressive"],
  oscA_table="Basic Shapes", oscA_pos=0.33, oscA_voices=1, noise_level=0.03, oscA_warp="Mirror", oscA_warp_amt=0.25,
  lfo1_rate=0.25, flt_type="LP12", flt_cutoff=1800.0, amp_attack=0.5, amp_sustain=1.0, amp_release=1.5,
  rev_size=0.6, rev_mix=0.2)
P("metallic", "Ring Mod Haze", C, "Hazy pad with ring-modulated overtones that drift slowly in and out of tune.",
  M(("Ring", [("Warp A", 0.35)]), ("Drift", [("Pitch B", 0.01)]), ("Tone", [("Cutoff", 0.35)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Pitch B", 0.006), ("LFO 2", "Warp A", 0.1)], tags=["Ring Mod", "Hazy", "Eerie"],
  oscA_table="Hollow", oscA_pos=0.3, oscA_oct=-1, oscA_voices=2, uni_detune=0.08, oscA_warp="RM", oscA_warp_amt=0.75,
  oscB_table="Basic Shapes", oscB_semi=12, oscB_level=0.0, lfo1_rate=0.4, lfo2_rate=0.7, flt_type="LP24",
  flt_cutoff=4500.0, amp_attack=1.3, amp_sustain=1.0, amp_release=2.0, rev_size=0.75, rev_mix=0.24)

# filter and phaser -------------------------------------------------------------------------------------------
P("warm", "Phaser Wash Pad", C, "Warm major-seventh pad washed by a deep, slow phaser.",
  M(("Phase", [("Mod FX Mix", 0.4)]), ("Warmth", [("Cutoff", 0.35)]), ("Width", [("Detune", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Mod Wheel", "Mod FX Mix", 0.3)], tags=["Phaser", "Warm", "Wash"],
  oscA_table="Analog Saw", oscA_voices=2, uni_detune=0.1, uni_spread=0.5, flt_type="LP24", flt_cutoff=1000.0,
  amp_attack=0.15, amp_sustain=1.0, amp_release=1.6, mfx_type="Phaser", mfx_rate=0.3, mfx_depth=0.95,
  mfx_mix=0.85, rev_size=0.6, rev_mix=0.2)
P("electronic", "Notch Sweep Pad", C, "Bright pad carved by a notch that sweeps through it every bar.",
  M(("Sweep", [("Cutoff", 0.35)]), ("Depth", [("Resonance", 0.3)]), ("Width", [("Detune", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Cutoff", 0.4)], tags=["Notch", "Sweep"],
  oscA_table="Hyper Saw", oscA_pos=0.2, oscA_voices=4, uni_detune=0.2, lfo1_shape="Triangle", lfo1_sync=True,
  lfo1_div="1/1", flt_type="Notch", flt_cutoff=1500.0, flt_res=0.4, amp_attack=0.4, amp_sustain=1.0,
  amp_release=1.4, rev_size=0.6, rev_mix=0.2)
P("warm", "Ladder Glow Pad", C, "Resonant ladder pad glowing around the cutoff, opened with the mod wheel.",
  M(("Glow", [("Resonance", 0.25)]), ("Open", [("Cutoff", 0.35)]), ("Drive", [("Filter Drive", 0.35)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Mod Wheel", "Cutoff", 0.4), ("LFO 1", "Cutoff", 0.06)], tags=["Resonant", "Analog", "Warm"],
  oscA_table="Analog Square", oscA_pos=0.3, oscA_oct=-1, oscA_voices=1, lfo1_rate=0.2, flt_type="Ladder",
  flt_cutoff=600.0, flt_res=0.75, flt_drive=0.25, amp_attack=0.5, amp_sustain=1.0, amp_release=1.5, rev_size=0.6,
  rev_mix=0.2)
P("ambient", "Flanged Jet Pad", C, "Airy pad pulled through a slow flanger like a jet passing far overhead.",
  M(("Jet", [("Mod FX Mix", 0.4)]), ("Air", [("Noise Level", 0.1)]), ("Tone", [("Cutoff", 0.35)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Mod Wheel", "Mod FX Mix", 0.3)], tags=["Flanger", "Airy"],
  oscA_table="Hyper Saw", oscA_pos=0.5, oscA_voices=3, uni_detune=0.1, noise_level=0.08, flt_type="LP12",
  flt_cutoff=6500.0, amp_attack=0.6, amp_sustain=1.0, amp_release=1.8, mfx_type="Flanger", mfx_rate=0.2,
  mfx_depth=0.8, mfx_mix=0.7, rev_size=0.7, rev_mix=0.24)

# noise, comb and texture -------------------------------------------------------------------------------------
P("ambient", "Ocean Wash", C, "Filtered noise surf rolling in and out under a soft tonal bed.",
  M(("Surf", [("Noise Level", 0.15)]), ("Tide", [("Cutoff", 0.35)]), ("Bed", [("Level A", 0.2)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Cutoff", 0.35), ("LFO 1", "Noise Level", 0.1)], tags=["Noise", "Ocean", "Ambient"],
  oscA_table="Basic Shapes", oscA_pos=0.2, oscA_level=0.4, noise_level=0.5, lfo1_shape="Triangle", lfo1_rate=0.1,
  flt_type="LP24", flt_cutoff=1400.0, amp_attack=1.5, amp_sustain=1.0, amp_release=3.0, rev_size=0.85,
  rev_mix=0.3)
P("metallic", "Bowed Metal Pad", C, "Noise through a tuned comb filter, singing like bowed metal plates.",
  M(("Bow", [("Noise Level", 0.15)]), ("Ring", [("Resonance", 0.25)]), ("Tone", [("Cutoff", 0.35)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Resonance", 0.05)], tags=["Metallic", "Bowed", "Comb"],
  oscA_table="Noise Cycle", oscA_pos=0.3, oscA_level=0.4, noise_level=0.4, lfo1_rate=0.3, flt_type="Comb-",
  flt_cutoff=262.0, flt_res=0.8, flt_keytrack=1.0, amp_attack=0.9, amp_sustain=1.0, amp_release=2.0,
  rev_size=0.8, rev_mix=0.26)
P("lofi", "Tape Hiss Pad", C, "Warm pad played from an old tape: gentle wow, hiss and a soft top.",
  M(("Wow", [("Pitch", 0.004)]), ("Hiss", [("Noise Level", 0.1)]), ("Tone", [("Cutoff", 0.35)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Pitch", 0.003), ("Random", "Pitch", 0.002)], tags=["Tape", "Lo-Fi", "Warm"],
  oscA_table="Analog Saw", oscA_voices=3, uni_detune=0.12, noise_level=0.05, uni_spread=0.2, lfo1_rate=0.45, flt_type="LP24",
  flt_cutoff=1000.0, amp_attack=0.4, amp_sustain=1.0, amp_release=1.4, dist_type="Tube", dist_drive=0.3,
  dist_mix=0.4, rev_size=0.5, rev_mix=0.16)
P("ambient", "Echo Cloud Pad", C, "Short soft chords that become a cloud of dotted echoes.",
  M(("Cloud", [("Delay Mix", 0.3)]), ("Tone", [("Cutoff", 0.35)]), ("Width", [("Detune", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Mod Wheel", "Delay Mix", 0.3)], tags=["Delay", "Cloud", "Ambient"],
  oscA_table="Hollow", oscA_pos=0.5, oscA_voices=3, uni_detune=0.1, flt_type="LP24", flt_cutoff=1800.0,
  amp_attack=0.15, amp_decay=1.2, amp_sustain=0.4, amp_release=1.0, dly_mode="PingPong", dly_time="1/8D",
  dly_feedback=0.65, dly_mix=0.4, rev_size=0.7, rev_mix=0.22)
P("warm", "Deep Sub Pad", C, "Dark, low pad built on a sub and a soft square, felt more than heard.",
  M(("Sub", [("Sub Level", 0.3)]), ("Tone", [("Cutoff", 0.35)]), ("Drive", [("Dist Drive", 0.35)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Mod Wheel", "Cutoff", 0.35)], tags=["Dark", "Low", "Sub"],
  oscA_table="Analog Square", oscA_pos=0.2, oscA_oct=-1, oscA_voices=2, uni_detune=0.08, sub_level=0.3,
  flt_type="LP24", flt_cutoff=500.0, amp_attack=0.6, amp_sustain=1.0, amp_release=1.8, dist_type="Tube",
  dist_drive=0.25, dist_mix=0.3, rev_size=0.6, rev_mix=0.14)

CANDIDATES = bc.end(_s)

if __name__ == "__main__":
    bc.write("pad2", CANDIDATES)
