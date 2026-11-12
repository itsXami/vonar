#!/usr/bin/env python3
"""Stage D: Pluck batch 1 (30). New category "Pluck".

Families (no family above a quarter of the batch): plucked strings (7), filter / analog plucks (7), FM and metallic
plucks (6), resonator and noise plucks (5), lo-fi and echo plucks (5). Attack and tail differ from neighbour to
neighbour: soft / hard attack, dry / delay / reverb tail.

    python3 tools/presets/generate_batch_pluck1.py [--trim report.json]
"""
import batch_common as bc

P, M = bc.P, bc.M
_s = bc.begin()
C = "Pluck"

# plucked strings ----------------------------------------------------------------------------------------------
P("acoustic", "Kalimba Thumb", C, "Thumb piano tine: a bright click, a hollow body and a short, sweet ring.",
  M(("Tine", [("Cutoff", 0.35)]), ("Body", [("Level B", 0.3)]), ("Echo", [("Delay Mix", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Random", "Pitch", 0.002)], tags=["Kalimba", "Tine", "Sweet"],
  oscA_type="String", oscA_table="Glass Harmonics", oscA_pos=0.2, str_decay=1.2, str_tone=0.9, oscB_table="Basic Shapes",
  oscB_level=0.25, flt_type="LP12", flt_cutoff=7000.0, amp_attack=0.004, amp_decay=1.0, amp_sustain=0.0,
  amp_release=0.3, squash=0.3, rev_size=0.35, rev_mix=0.1)
P("orchestral", "Concert Harp", C, "Concert harp strings that ring long and sweet in a wide hall.",
  M(("Ring", [("WT Pos A", 0.3)]), ("Bright", [("Cutoff", 0.35)]), ("Width", [("Pan A", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Random", "Pan A", 0.35)], tags=["Harp", "Orchestral", "Sweet"],
  oscA_type="String", oscA_table="Basic Shapes", oscA_pos=0.45, str_decay=4.5, str_tone=0.75, flt_type="LP12",
  flt_cutoff=5000.0, amp_attack=0.006, amp_sustain=1.0, amp_release=1.2, squash=0.3, rev_size=0.8, rev_mix=0.24)
P("acoustic", "Koto Bend Pluck", C, "Koto-like silk string plucked hard, with the pitch pushed up a touch at the attack.",
  M(("Bend", [("Pitch A", 0.02)]), ("Bright", [("Cutoff", 0.35)]), ("Ring", [("WT Pos A", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Mod Wheel", "Pitch", 0.006)], tags=["Koto", "Bend", "Plucked"],
  oscA_type="String", oscA_table="Pluck Body", oscA_pos=0.25, str_decay=3.2, str_tone=0.7, penv_amount=-1.2,
  penv_decay=0.18, flt_type="LP12", flt_cutoff=6000.0, amp_attack=0.004, amp_sustain=1.0, amp_release=0.4,
  squash=0.35, rev_size=0.2, rev_mix=0.05)
P("acoustic", "Plectrum Synth Pluck", C, "Saw-excited string with a hard plastic pick and a thin, cutting body.",
  M(("Pick", [("Cutoff", 0.35)]), ("Thin", [("Resonance", 0.3)]), ("Echo", [("Delay Mix", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.3)], tags=["Bright", "Thin", "Plucked"],
  oscA_type="String", oscA_table="Sync Saw", oscA_pos=0.4, str_decay=1.4, str_tone=0.92, flt_type="HP",
  flt_cutoff=380.0, flt_res=0.2, amp_attack=0.004, amp_sustain=1.0, amp_release=0.15, squash=0.45,
  dly_time="1/16", dly_mix=0.1)
P("warm", "Wooden Pluck", C, "Short, dark plucked wood with almost no ring.",
  M(("Wood", [("WT Pos A", 0.3)]), ("Tone", [("Cutoff", 0.35)]), ("Length", [("Level A", 0.2)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Random", "Cutoff", 0.08)], tags=["Wood", "Dark", "Dry"],
  oscA_type="String", oscA_table="Pluck Body", oscA_pos=0.7, str_decay=0.6, str_tone=0.4, flt_type="LP24",
  flt_cutoff=2400.0, amp_attack=0.004, amp_sustain=1.0, amp_release=0.08, squash=0.45)
P("acoustic", "Double Course Pluck", C, "Paired strings tuned a hair apart, so every note shimmers like a lute.",
  M(("Shimmer", [("Detune", 0.3)]), ("Bright", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Random", "Pan A", 0.2)], tags=["Lute", "Shimmer", "Plucked"],
  oscA_type="String", oscA_table="Analog Saw", oscA_pos=0.3, oscA_voices=2, uni_detune=0.1, uni_spread=0.9,
  str_decay=2.6, str_tone=0.72, flt_type="LP12", flt_cutoff=4500.0, amp_attack=0.005, amp_sustain=1.0, amp_release=0.5,
  squash=0.35, rev_size=0.55, rev_mix=0.16)
P("warm", "Sub Sine Pluck", C, "Deep round pluck with a sine sub, made for melodic bass lines and low hooks.",
  M(("Sub", [("Sub Level", 0.3)]), ("Click", [("Cutoff", 0.35)]), ("Drive", [("Dist Drive", 0.35)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.3)], tags=["Deep", "Round", "Bass"],
  oscA_table="Basic Shapes", oscA_pos=0.15, oscA_oct=-1, sub_level=0.35, flt_type="LP24", flt_cutoff=600.0,
  flt_envamt=0.35, fenv_decay=0.12, fenv_sustain=0.0, amp_decay=0.45, amp_sustain=0.0, amp_release=0.15,
  dist_type="Tube", dist_drive=0.25, dist_mix=0.4)

# filter / analog plucks -------------------------------------------------------------------------------------
P("electronic", "Classic Saw Pluck", C, "Bright saw pluck with a snappy filter envelope, the everyday workhorse.",
  M(("Snap", [("Cutoff", 0.35)]), ("Res", [("Resonance", 0.3)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Saw", "Snappy"],
  oscA_table="Analog Saw", oscA_voices=2, uni_detune=0.12, flt_type="LP24", flt_cutoff=500.0, flt_res=0.2,
  flt_envamt=0.55, fenv_decay=0.2, fenv_sustain=0.0, amp_decay=0.4, amp_sustain=0.0, amp_release=0.25,
  dly_mode="PingPong", dly_time="1/8D", dly_mix=0.14, rev_mix=0.12)
P("electronic", "Rubber Ladder Pluck", C, "Resonant ladder pluck that bounces with a rubbery squelch.",
  M(("Squelch", [("Resonance", 0.25)]), ("Open", [("Cutoff", 0.35)]), ("Drive", [("Filter Drive", 0.35)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.25), ("Random", "Cutoff", 0.06)], tags=["Resonant", "Squelch"],
  oscA_table="Analog Square", oscA_pos=0.3, flt_type="Ladder", flt_cutoff=350.0, flt_res=0.65, flt_drive=0.3,
  flt_envamt=0.5, fenv_decay=0.18, fenv_sustain=0.0, amp_decay=0.35, amp_sustain=0.0, amp_release=0.15)
P("electronic", "Supersaw Pluck", C, "Wide seven-voice saw pluck with a quick, bright bloom.",
  M(("Width", [("Detune", 0.3)]), ("Bright", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.2)], tags=["Supersaw", "Wide", "Bright"],
  oscA_table="Hyper Saw", oscA_pos=0.3, oscA_voices=7, uni_detune=0.3, uni_spread=1.0, flt_type="LP24",
  flt_cutoff=900.0, flt_envamt=0.5, fenv_decay=0.28, fenv_sustain=0.05, amp_decay=0.5, amp_sustain=0.0,
  amp_release=0.3, rev_size=0.6, rev_mix=0.18)
P("electronic", "PWM Pluck", C, "Pulse pluck whose width wobbles slowly, so held phrases shimmer.",
  M(("Width", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("LFO 1", "WT Pos A", 0.3), ("Velocity", "Cutoff", 0.25)], tags=["PWM", "Analog"],
  oscA_table="PWM", oscA_pos=0.4, lfo1_rate=0.7, flt_type="LP12", flt_cutoff=1200.0, flt_envamt=0.45, fenv_decay=0.22,
  fenv_sustain=0.0, amp_decay=0.45, amp_sustain=0.05, amp_release=0.2, mfx_type="Chorus", mfx_mix=0.2)
P("warm", "Velvet Pluck", C, "Soft, round pluck with a gentle attack and no edge at all.",
  M(("Soft", [("Cutoff", -0.3)]), ("Body", [("Level B", 0.3)]), ("Width", [("Mod FX Mix", 0.4)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.2)], tags=["Soft", "Round", "Warm"],
  oscA_table="Basic Shapes", oscA_pos=0.3, oscB_table="Basic Shapes", oscB_level=0.3, oscB_oct=-1, flt_type="LP12",
  flt_cutoff=1400.0, flt_envamt=0.25, fenv_decay=0.3, fenv_sustain=0.0, amp_attack=0.012, amp_decay=0.7,
  amp_sustain=0.0, amp_release=0.3, mfx_type="Chorus", mfx_rate=0.3, mfx_mix=0.3, rev_size=0.4, rev_mix=0.12)
P("electronic", "Vowel Pluck", C, "Pluck that says 'wah' as the formant envelope closes on every note.",
  M(("Vowel", [("Formant", 0.35)]), ("Peak", [("Resonance", 0.3)]), ("Echo", [("Delay Mix", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Mod Env", "Formant", -0.6), ("Velocity", "Formant", 0.2)], tags=["Vocal", "Formant"],
  oscA_table="Saw Octaves", oscA_pos=0.3, menv_decay=0.3, flt_type="Formant", flt_cutoff=1000.0, flt_res=0.45,
  flt_vowel=0.85, amp_decay=0.45, amp_sustain=0.0, amp_release=0.2, dly_time="1/8", dly_mix=0.12)
P("electronic", "Sync Zap Pluck", C, "Hard-synced pluck whose overtones zap downward on every hit.",
  M(("Zap", [("Warp A", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Grit", [("Dist Mix", 0.3)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Mod Env", "Warp A", 0.6), ("Velocity", "Warp A", 0.2)], tags=["Sync", "Zap", "Aggressive"],
  oscA_table="Analog Saw", oscA_warp="Sync", oscA_warp_amt=0.05, menv_decay=0.15, flt_type="LP24", flt_cutoff=5000.0,
  amp_decay=0.35, amp_sustain=0.0, amp_release=0.15, dist_type="Soft", dist_drive=0.3, dist_mix=0.0,
  dly_mode="PingPong", dly_time="1/16", dly_mix=0.1)
P("warm", "Mirror Hollow Pluck", C, "Hollow, woody pluck folded by mirror warp, somewhere between a flute and a marimba.",
  M(("Hollow", [("Warp A", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Warp A", 0.3), ("Mod Env", "Warp A", 0.25)], tags=["Hollow", "Woody"],
  oscA_table="Hollow", oscA_pos=0.3, oscA_warp="Mirror", oscA_warp_amt=0.45, menv_decay=0.2, flt_type="LP12",
  flt_cutoff=3000.0, amp_decay=0.5, amp_sustain=0.0, amp_release=0.2, rev_size=0.35, rev_mix=0.1)

# FM and metallic ---------------------------------------------------------------------------------------------
P("metallic", "FM Glass Pluck", C, "Clear FM pluck at a three-to-one ratio: glassy attack, round tail.",
  M(("Index", [("Warp A", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Mod Env", "Warp A", 0.45), ("Velocity", "Warp A", 0.25)], tags=["FM", "Glassy"],
  oscA_table="Basic Shapes", oscA_warp="FM", oscA_warp_amt=0.05, oscB_table="Basic Shapes", oscB_oct=1, oscB_semi=7,
  oscB_level=0.0, menv_decay=0.18, flt_type="LP12", flt_cutoff=9000.0, amp_decay=0.8, amp_sustain=0.0,
  amp_release=0.3, rev_size=0.5, rev_mix=0.14)
P("metallic", "Ring Clang Pluck", C, "Ring-modulated pluck with clanging, out-of-tune partials.",
  M(("Clang", [("Warp A", 0.35)]), ("Ratio", [("Pitch B", 0.03)]), ("Tone", [("Cutoff", 0.35)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Warp A", 0.2), ("Random", "Pitch B", 0.01)], tags=["Ring Mod", "Metallic"],
  oscA_table="Basic Shapes", oscA_pos=0.33, oscA_warp="RM", oscA_warp_amt=0.6, oscB_table="Basic Shapes",
  oscB_semi=11, oscB_fine=30.0, oscB_level=0.0, flt_type="LP24", flt_cutoff=4000.0, amp_decay=0.4, amp_sustain=0.0,
  amp_release=0.2, rev_size=0.4, rev_mix=0.12)
P("metallic", "Digital Bell Pluck", C, "Short digital FM blip with a metallic sparkle on top.",
  M(("Sparkle", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "WT Pos A", 0.3), ("Filter Env", "WT Pos A", 0.3)], tags=["Digital", "FM", "Bright"],
  oscA_table="FM Digital", oscA_pos=0.3, flt_type="LP24", flt_cutoff=1500.0, flt_envamt=0.5, fenv_decay=0.12,
  fenv_sustain=0.0, amp_decay=0.3, amp_sustain=0.0, amp_release=0.15, dly_mode="PingPong", dly_time="1/16",
  dly_mix=0.12)
P("metallic", "Steel Tongue Pluck", C, "Steel tongue drum: soft mallet, rounded metal tone and a long, pure tail.",
  M(("Metal", [("Warp A", 0.35)]), ("Soft", [("Cutoff", -0.3)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Mod Env", "Warp A", 0.3), ("Velocity", "Cutoff", 0.2)], tags=["Tongue Drum", "Metallic", "Soft"],
  oscA_table="Basic Shapes", oscA_warp="FM", oscA_warp_amt=0.04, oscB_table="Basic Shapes", oscB_oct=1,
  oscB_semi=5, oscB_level=0.0, menv_decay=0.3, flt_type="LP12", flt_cutoff=3500.0, amp_attack=0.006,
  amp_decay=1.6, amp_sustain=0.0, amp_release=0.6, rev_size=0.6, rev_mix=0.18)
P("metallic", "Tin Can Pluck", C, "Small, tinny pluck from a resonant metal can, bright and boxy.",
  M(("Tin", [("Resonance", 0.3)]), ("Box", [("Cutoff", 0.35)]), ("Grit", [("Dist Mix", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Tinny", "Boxy"],
  oscA_table="Metal Comb", oscA_pos=0.5, flt_type="BP", flt_cutoff=2200.0, flt_res=0.45, flt_keytrack=0.5,
  amp_decay=0.3, amp_sustain=0.0, amp_release=0.1, dist_type="Soft", dist_drive=0.3, dist_mix=0.0, squash=0.3)
P("electronic", "Quantize Chip Pluck", C, "Stepped, game-console square pluck with a quick pitch blip.",
  M(("Steps", [("Warp A", 0.35)]), ("Blip", [("Pitch A", 0.03)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Velocity", "Warp A", 0.2)], tags=["Chiptune", "Stepped"],
  oscA_table="Analog Square", oscA_warp="Quantize", oscA_warp_amt=0.5, penv_amount=12.0, penv_decay=0.02,
  flt_type="LP12", flt_cutoff=7000.0, amp_decay=0.25, amp_sustain=0.15, amp_release=0.08, dly_time="1/8",
  dly_mix=0.1)

# resonator and noise ------------------------------------------------------------------------------------------
P("electronic", "Comb Tube Pluck", C, "Noise burst ringing through a tuned comb filter like a struck metal tube.",
  M(("Ring", [("Resonance", 0.25)]), ("Tone", [("Cutoff", 0.35)]), ("Noise", [("Noise Level", 0.15)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Resonance", 0.15)], tags=["Comb", "Resonator", "Tube"],
  oscA_table="Noise Cycle", oscA_pos=0.4, oscA_level=0.5, noise_level=0.4, flt_type="Comb+", flt_cutoff=262.0,
  flt_res=0.82, flt_keytrack=1.0, amp_decay=0.6, amp_sustain=0.0, amp_release=0.3, rev_size=0.45, rev_mix=0.14)
P("ambient", "Water Drop Pluck", C, "Sine droplet whose pitch falls as it lands, echoing in a cave.",
  M(("Drop", [("Pitch A", 0.03)]), ("Echo", [("Delay Mix", 0.3)]), ("Cave", [("Reverb Mix", 0.3)]), ("Tone", [("Cutoff", 0.35)])),
  mods=[("Random", "Pitch", 0.005), ("Velocity", "Cutoff", 0.2)], tags=["Water", "Drop", "Ambient"],
  oscA_table="Basic Shapes", oscA_pos=0.0, penv_amount=9.0, penv_decay=0.03, flt_type="LP12", flt_cutoff=6000.0,
  amp_decay=0.25, amp_sustain=0.0, amp_release=0.2, dly_mode="PingPong", dly_time="1/8D", dly_feedback=0.5,
  dly_mix=0.25, rev_size=0.85, rev_mix=0.3)
P("acoustic", "Pizz Hollow Pluck", C, "Short band-passed pizzicato pop with a hollow wooden body.",
  M(("Pop", [("Cutoff", 0.35)]), ("Body", [("Resonance", 0.3)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Random", "Pan A", 0.25)], tags=["Pizzicato", "Hollow"],
  oscA_table="Strings", oscA_pos=0.4, flt_type="BP", flt_cutoff=900.0, flt_res=0.35, flt_keytrack=0.6,
  flt_envamt=0.3, fenv_decay=0.08, fenv_sustain=0.0, amp_decay=0.25, amp_sustain=0.0, amp_release=0.15, squash=0.3,
  rev_size=0.6, rev_mix=0.18)
P("ambient", "Breath Bubble Pluck", C, "Breathy resonant bubbles that land on a slightly different pitch each time.",
  M(("Bubble", [("Resonance", 0.3)]), ("Breath", [("Noise Level", 0.15)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Random", "Cutoff", 0.25), ("Random", "Pitch", 0.004), ("Velocity", "Resonance", 0.15)], tags=["Bubbles", "Breathy"],
  oscA_table="Basic Shapes", oscA_pos=0.0, oscA_level=1.0, noise_level=0.35, sub_level=0.2, flt_type="BP",
  flt_cutoff=1500.0, flt_res=0.3, flt_keytrack=0.5, flt_envamt=0.3, fenv_decay=0.15, fenv_sustain=0.0,
  amp_attack=0.02, amp_decay=0.6, amp_sustain=0.4, squash=0.45, amp_release=0.25, rev_size=0.6, rev_mix=0.18)
P("acoustic", "Clave Click Pluck", C, "Dry, clicky hollow-wood pluck for tight percussive melodies.",
  M(("Click", [("Cutoff", 0.35)]), ("Wood", [("WT Pos A", 0.3)]), ("Length", [("Level A", 0.2)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Random", "Cutoff", 0.08)], tags=["Percussive", "Dry", "Wood"],
  oscA_table="Hollow", oscA_pos=0.6, flt_type="BP", flt_cutoff=1800.0, flt_res=0.3, flt_keytrack=0.6,
  amp_decay=0.12, amp_sustain=0.0, amp_release=0.06, squash=0.4)

# lo-fi and echo ---------------------------------------------------------------------------------------------
P("ambient", "Dub Echo Pluck", C, "Dark, short pluck feeding a long ping-pong echo that carries the groove.",
  M(("Echo", [("Delay Mix", 0.3)]), ("Tone", [("Cutoff", 0.35)]), ("Grit", [("Dist Mix", 0.3)]), ("Space", [("Reverb Mix", 0.3)])),
  mods=[("Mod Wheel", "Delay Mix", 0.3), ("Velocity", "Cutoff", 0.25)], tags=["Dub", "Echo", "Dark"],
  oscA_table="Analog Square", oscA_pos=0.4, flt_type="LP24", flt_cutoff=700.0, flt_envamt=0.35, fenv_decay=0.12,
  fenv_sustain=0.0, amp_decay=0.3, amp_sustain=0.0, amp_release=0.15, dist_type="Tube", dist_drive=0.3,
  dist_mix=0.0, dly_mode="PingPong", dly_time="1/8D", dly_feedback=0.62, dly_mix=0.35)
P("lofi", "Detuned Lo-Fi Pluck", C, "Warbly, slightly out-of-tune pluck with crushed bits and a dusty top.",
  M(("Warble", [("Pitch", 0.004)]), ("Crush", [("Dist Mix", 0.3)]), ("Tone", [("Cutoff", 0.35)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Random", "Pitch", 0.006), ("LFO 1", "Pitch", 0.002), ("Velocity", "Cutoff", 0.2)], tags=["Lo-Fi", "Detuned", "Crushed"],
  oscA_table="Analog Saw", oscA_pos=0.2, lfo1_rate=0.8, noise_level=0.02, flt_type="LP24", flt_cutoff=850.0,
  flt_envamt=0.3, fenv_decay=0.3, fenv_sustain=0.0, amp_decay=0.9, amp_sustain=0.0, amp_release=0.3,
  mfx_type="Chorus", mfx_rate=1.2, mfx_depth=0.6, mfx_mix=0.4,
  dist_type="Bitcrush", dist_drive=0.3, dist_mix=0.35)
P("ambient", "Backwards Pluck", C, "A pluck played in reverse: it swells up and cuts off sharply.",
  M(("Swell", [("Level A", 0.2)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Mod Env", "Cutoff", 0.4), ("Velocity", "Cutoff", 0.15)], tags=["Reverse", "Swell"],
  oscA_table="Saw Octaves", oscA_pos=0.3, menv_attack=0.25, menv_decay=0.05, menv_sustain=0.0, flt_type="LP24",
  flt_cutoff=600.0, amp_attack=0.25, amp_decay=0.02, amp_sustain=0.0, amp_release=0.04, rev_size=0.7, rev_mix=0.22)
P("electronic", "Gated Glitch Pluck", C, "Pluck chopped into sixteenth stutters that fade with every repeat.",
  M(("Stutter", [("Level A", 0.2)]), ("Tone", [("Cutoff", 0.35)]), ("Crush", [("Dist Mix", 0.3)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("LFO 1", "Level A", -0.6), ("Velocity", "Cutoff", 0.2)], tags=["Glitch", "Gated", "Rhythmic"],
  oscA_table="FM Digital", oscA_pos=0.5, lfo1_shape="Square", lfo1_sync=True, lfo1_div="1/16", lfo1_retrig=True,
  flt_type="LP24", flt_cutoff=2200.0, amp_decay=0.6, amp_sustain=0.0, amp_release=0.1, dist_type="Bitcrush",
  dist_drive=0.25, dist_mix=0.0)
P("warm", "Bossa Organ Pluck", C, "Percussive organ blip with a quick decay, like a short drawbar stab.",
  M(("Perc", [("WT Pos A", 0.3)]), ("Tone", [("Cutoff", 0.35)]), ("Spin", [("Mod FX Mix", 0.4)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Organ", "Percussive"],
  oscA_table="Drawbars", oscA_pos=0.5, oscA_oct=1, flt_type="LP12", flt_cutoff=4500.0, amp_decay=0.35,
  amp_sustain=0.0, amp_release=0.15, mfx_type="Chorus", mfx_rate=0.8, mfx_mix=0.2, rev_size=0.35, rev_mix=0.1)

CANDIDATES = bc.end(_s)

if __name__ == "__main__":
    bc.write("pluck1", CANDIDATES)
