#!/usr/bin/env python3
"""Stage D: Bell batch 1 (25). New category "Bell" (bells, mallets, metal and glass).

Families: struck bells (7), mallet percussion (7), glass and music box (5), gongs and bowls (3), synthetic
bells (3). Inharmonic partials come from FM / RM warp with non-integer ratios (semitones + fine), comb filters
and the metal / glass tables.

    python3 tools/presets/generate_batch_bell1.py [--trim report.json]
"""
import batch_common as bc

P, M = bc.P, bc.M
_s = bc.begin()
C = "Bell"

# struck bells -------------------------------------------------------------------------------------------------
P("orchestral", "Tubular Bell", C, "Orchestral tubular bell: a bright strike and a long, slightly out-of-tune hum.",
  M(("Strike", [("Warp A", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Hum", [("Level B", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Mod Env", "Warp A", 0.4), ("Velocity", "Warp A", 0.25)], tags=["Tubular", "Orchestral"],
  oscA_table="Basic Shapes", oscA_warp="FM", oscA_warp_amt=0.12, oscB_table="Basic Shapes", oscB_oct=1, oscB_semi=5,
  oscB_fine=20.0, oscB_level=0.0, menv_decay=0.4, flt_type="LP12", flt_cutoff=7000.0, amp_decay=4.0, amp_sustain=0.0,
  amp_release=2.0, rev_size=0.8, rev_mix=0.24)
P("metallic", "Church Bell Toll", C, "Heavy tower bell with a dark, beating hum under clanging partials.",
  M(("Clang", [("Warp A", 0.35)]), ("Weight", [("Sub Level", 0.25)]), ("Tone", [("Cutoff", 0.35)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Mod Env", "Warp A", 0.35), ("Velocity", "Cutoff", 0.2)], tags=["Church", "Dark", "Heavy"],
  oscA_table="Basic Shapes", oscA_oct=-1, oscA_warp="RM", oscA_warp_amt=0.5, oscB_table="Basic Shapes", oscB_semi=-3,
  oscB_fine=-35.0, oscB_level=0.0, sub_level=0.12, menv_decay=1.0, flt_type="LP24", flt_cutoff=3000.0,
  amp_decay=5.0, amp_sustain=0.0, amp_release=2.5, rev_size=0.9, rev_damping=0.6, rev_mix=0.3)
P("acoustic", "Handbell Choir", C, "Soft handbells ringing in a choir, each note with its own small wobble.",
  M(("Bright", [("Warp A", 0.3)]), ("Wobble", [("Pitch", 0.003)]), ("Width", [("Pan A", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Random", "Pitch", 0.003), ("Random", "Pan A", 0.35), ("Mod Env", "Warp A", 0.3)], tags=["Handbell", "Soft"],
  oscA_table="Basic Shapes", oscA_warp="FM", oscA_warp_amt=0.08, oscB_table="Basic Shapes", oscB_oct=1, oscB_semi=10,
  oscB_level=0.0, menv_decay=0.3, flt_type="LP12", flt_cutoff=6000.0, amp_attack=0.004, amp_decay=2.5,
  amp_sustain=0.0, amp_release=1.2, rev_size=0.7, rev_mix=0.22)
P("metallic", "Clock Chime", C, "Mantel clock chime: a small hammer on a coiled rod, clear and a little boxy.",
  M(("Rod", [("Resonance", 0.3)]), ("Tone", [("Cutoff", 0.35)]), ("Box", [("Level B", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Chime", "Clock"],
  oscA_table="Bell Metal", oscA_pos=0.25, oscB_table="Hollow", oscB_level=0.15, flt_type="Comb+", flt_cutoff=1000.0,
  flt_res=0.4, flt_keytrack=1.0, amp_decay=2.2, amp_sustain=0.0, amp_release=1.0, rev_size=0.35, rev_mix=0.12)
P("metallic", "Temple Bell Strike", C, "Deep temple bell hit with a wooden beam: soft thud, then a slow, wide ring.",
  M(("Ring", [("Warp A", 0.35)]), ("Thud", [("Noise Level", 0.1)]), ("Beat", [("Detune", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Mod Env", "Warp A", 0.3), ("Mod Env", "Noise Level", 0.2)], tags=["Temple", "Deep"],
  oscA_table="Basic Shapes", oscA_oct=-1, oscA_voices=2, uni_detune=0.06, uni_spread=0.8, oscA_warp="FM",
  oscA_warp_amt=0.15, oscB_table="Basic Shapes", oscB_semi=8, oscB_fine=15.0, oscB_level=0.0, menv_decay=0.15,
  flt_type="LP24", flt_cutoff=2500.0, amp_attack=0.008, amp_decay=6.0, amp_sustain=0.0, amp_release=3.0,
  rev_size=0.88, rev_mix=0.28)
P("acoustic", "Sleigh Bell Shimmer", C, "Bright little jingle bells shaken with every note.",
  M(("Shake", [("Noise Level", 0.15)]), ("Bright", [("Cutoff", 0.35)]), ("Ring", [("Resonance", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("LFO 1", "Level A", 0.3), ("Random", "Cutoff", 0.15)], tags=["Jingle", "Bright", "Festive"],
  oscA_table="Bell Metal", oscA_pos=0.8, oscA_oct=2, noise_level=0.15, lfo1_rate=12.0, flt_type="HP", flt_cutoff=2500.0,
  flt_res=0.3, amp_decay=0.6, amp_sustain=0.0, amp_release=0.3, rev_size=0.4, rev_mix=0.12)
P("orchestral", "Crotale Ring", C, "Small antique cymbals tuned high: a piercing, pure ring.",
  M(("Ring", [("Warp A", 0.3)]), ("Bright", [("Cutoff", 0.35)]), ("Shimmer", [("Detune", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Warp A", 0.3)], tags=["Crotale", "High", "Pure"],
  oscA_table="Basic Shapes", oscA_oct=1, oscA_warp="FM", oscA_warp_amt=0.06, oscB_table="Basic Shapes", oscB_oct=1,
  oscB_semi=4, oscB_fine=40.0, oscB_level=0.0, flt_type="LP12", flt_cutoff=10000.0, amp_decay=3.5, amp_sustain=0.0,
  amp_release=1.5, rev_size=0.7, rev_mix=0.2)

# mallet percussion ------------------------------------------------------------------------------------------
P("acoustic", "Vibraphone Motor", C, "Soft vibraphone with the motor on: a warm bar tone pulsing in slow tremolo.",
  M(("Motor", [("Level A", -0.3)]), ("Mallet", [("Cutoff", 0.35)]), ("Width", [("Pan A", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("LFO 1", "Level A", 0.3), ("LFO 1", "Pan A", 0.2), ("Velocity", "Cutoff", 0.25)], tags=["Vibraphone", "Tremolo", "Warm"],
  oscA_table="Basic Shapes", oscB_table="Basic Shapes", oscB_oct=2, oscB_level=0.12, lfo1_rate=4.5, flt_type="LP12",
  flt_cutoff=3500.0, flt_envamt=0.2, fenv_decay=0.05, fenv_sustain=0.0, amp_attack=0.003, amp_decay=3.0,
  amp_sustain=0.0, amp_release=1.0, rev_size=0.45, rev_mix=0.14)
P("acoustic", "Rosewood Marimba", C, "Warm wooden marimba bars with soft yarn mallets and a short resonator ring.",
  M(("Mallet", [("Cutoff", 0.35)]), ("Wood", [("Level B", 0.3)]), ("Ring", [("Resonance", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Random", "Pitch", 0.0015)], tags=["Marimba", "Wood", "Warm"],
  oscA_table="Basic Shapes", oscB_table="Basic Shapes", oscB_oct=2, oscB_level=0.2, flt_type="LP12", flt_cutoff=2600.0,
  flt_envamt=0.3, fenv_decay=0.04, fenv_sustain=0.0, amp_attack=0.005, amp_decay=1.0, amp_sustain=0.0,
  amp_release=0.3, squash=0.4, rev_size=0.3, rev_mix=0.08)
P("acoustic", "Xylophone Bright", C, "Hard-mallet xylophone: short, bright and clicky.",
  M(("Click", [("Cutoff", 0.35)]), ("Bar", [("Level B", 0.3)]), ("Length", [("Level A", 0.2)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.3)], tags=["Xylophone", "Bright", "Short"],
  oscA_table="Basic Shapes", oscA_oct=1, oscB_table="Basic Shapes", oscB_oct=2, oscB_semi=7, oscB_level=0.15,
  flt_type="LP12", flt_cutoff=8000.0, flt_envamt=0.3, fenv_decay=0.02, fenv_sustain=0.0, amp_decay=1.0, amp_attack=0.007,
  amp_sustain=0.0, amp_release=0.15, squash=0.6, dist_type="Soft", dist_drive=0.3, dist_mix=0.5, rev_size=0.3, rev_mix=0.08)
P("acoustic", "Glockenspiel", C, "Steel-bar glockenspiel, high and sparkling, with a crisp metal mallet.",
  M(("Sparkle", [("Level B", 0.3)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Level B", 0.2)], tags=["Glockenspiel", "Sparkle", "High"],
  oscA_table="Basic Shapes", oscA_oct=2, oscB_table="Basic Shapes", oscB_oct=3, oscB_semi=5, oscB_fine=25.0,
  oscB_level=0.2, flt_type="LP12", flt_cutoff=12000.0, amp_decay=1.8, amp_sustain=0.0, amp_release=0.8,
  rev_size=0.6, rev_mix=0.18)
P("metallic", "Steel Pan Melody", C, "Caribbean steel pan with its hollow, slightly detuned overtones and short sustain.",
  M(("Pan", [("Warp A", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Mod Env", "Warp A", 0.3), ("Velocity", "Warp A", 0.2)], tags=["Steel Pan", "Caribbean"],
  oscA_table="Basic Shapes", oscA_warp="FM", oscA_warp_amt=0.3, oscB_table="Basic Shapes", oscB_oct=1,
  oscB_fine=35.0, oscB_level=0.0, penv_amount=0.4, penv_decay=0.04, menv_decay=0.2, menv_sustain=0.2,
  flt_type="LP12", flt_cutoff=5000.0, amp_decay=1.2, amp_sustain=0.0, amp_release=0.4, mfx_type="Chorus", mfx_rate=0.5, mfx_mix=0.25, rev_size=0.4, rev_mix=0.12)
P("acoustic", "Balafon Buzz", C, "Wooden mallet bars with gourd resonators that add a soft buzz.",
  M(("Buzz", [("Dist Mix", 0.3)]), ("Mallet", [("Cutoff", 0.35)]), ("Wood", [("Resonance", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.25), ("Random", "Pitch", 0.002)], tags=["Balafon", "Wood", "Buzz"],
  oscA_table="Hollow", oscA_pos=0.3, oscB_table="Buzz", oscB_level=0.08, flt_type="BP", flt_cutoff=1300.0,
  flt_res=0.3, flt_keytrack=0.7, amp_decay=0.5, amp_sustain=0.0, amp_release=0.2, dist_type="Fold",
  dist_drive=0.2, dist_mix=0.2, squash=0.3)
P("ambient", "Soft Mallet Bowl", C, "Felt mallet on a metal bowl: no click, just a round swell of tone.",
  M(("Felt", [("Cutoff", -0.3)]), ("Hum", [("Detune", 0.3)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.2)], tags=["Soft", "Bowl", "Round"],
  oscA_table="Basic Shapes", oscA_voices=2, uni_detune=0.05, oscA_warp="FM", oscA_warp_amt=0.05,
  oscB_table="Basic Shapes", oscB_oct=1, oscB_semi=9, oscB_level=0.0, flt_type="LP12", flt_cutoff=2400.0,
  amp_attack=0.035, amp_decay=3.5, amp_sustain=0.0, amp_release=1.5, rev_size=0.7, rev_mix=0.22)

# glass and music box --------------------------------------------------------------------------------------
P("acoustic", "Celesta Box", C, "Celesta hammers on steel plates inside a wooden box: soft, sweet and dreamy.",
  M(("Hammer", [("Cutoff", 0.35)]), ("Sweet", [("Level B", 0.3)]), ("Box", [("Resonance", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Celesta", "Sweet", "Dreamy"],
  oscA_table="Glass Harmonics", oscA_pos=0.15, oscB_table="Basic Shapes", oscB_oct=1, oscB_level=0.25,
  flt_type="LP12", flt_cutoff=5000.0, flt_envamt=0.2, fenv_decay=0.03, fenv_sustain=0.0, amp_decay=1.6,
  amp_sustain=0.0, amp_release=0.8, rev_size=0.65, rev_mix=0.2)
P("lofi", "Wind-Up Music Box", C, "Tiny comb music box, a little out of tune and slowing down.",
  M(("Wind", [("Pitch", 0.004)]), ("Tine", [("Cutoff", 0.35)]), ("Box", [("Resonance", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Random", "Pitch", 0.006), ("LFO 1", "Pitch", 0.002)], tags=["Music Box", "Lo-Fi", "Nostalgic"],
  oscA_type="String", oscA_table="Glass Harmonics", oscA_pos=0.3, oscA_oct=2, str_decay=2.4, str_tone=0.95,
  lfo1_rate=0.3, flt_type="LP12", flt_cutoff=7000.0, amp_attack=0.016, amp_sustain=1.0, amp_release=0.6,
  squash=0.3, rev_size=0.35, rev_mix=0.12)
P("ambient", "Glass Harmonica", C, "Wet glass rims rubbed into a soft, eerie, hovering tone.",
  M(("Rim", [("WT Pos A", 0.4)]), ("Air", [("Noise Level", 0.1)]), ("Shimmer", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "WT Pos A", 0.1), ("Mod Wheel", "Noise Level", 0.1)], tags=["Glass", "Eerie", "Soft"],
  oscA_table="Glass Harmonics", oscA_pos=0.1, noise_level=0.01, lfo1_rate=0.4, flt_type="LP12", flt_cutoff=4000.0,
  amp_attack=0.3, amp_decay=2.0, amp_sustain=0.7, amp_release=1.2, mfx_type="Chorus", mfx_rate=0.2, mfx_mix=0.3,
  rev_size=0.7, rev_mix=0.24)
P("ambient", "Frozen Glass Bell", C, "Crystal bell frozen in a huge, dark reverb that hangs long after the strike.",
  M(("Crystal", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Freeze", [("Reverb Mix", 0.3)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Velocity", "WT Pos A", 0.25)], tags=["Glass", "Cold", "Huge"],
  oscA_table="Glass Harmonics", oscA_pos=0.5, flt_type="LP24", flt_cutoff=6000.0, amp_decay=2.5, amp_sustain=0.0,
  amp_release=2.0, rev_size=0.92, rev_damping=0.7, rev_mix=0.42)
P("acoustic", "Toy Bell Piano", C, "Toy piano metal rods: thin, tinkly and charming.",
  M(("Tink", [("Cutoff", 0.35)]), ("Rod", [("Level B", 0.3)]), ("Wobble", [("Pitch", 0.004)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Random", "Pitch", 0.004), ("Velocity", "Cutoff", 0.25)], tags=["Toy", "Tinkly"],
  oscA_table="Bell Metal", oscA_pos=0.1, oscA_oct=1, oscB_table="Basic Shapes", oscB_oct=2, oscB_semi=3,
  oscB_fine=20.0, oscB_level=0.15, flt_type="LP12", flt_cutoff=6500.0, amp_decay=0.9, amp_sustain=0.0,
  amp_release=0.3, rev_size=0.3, rev_mix=0.08)

# gongs and bowls ----------------------------------------------------------------------------------------------
P("ambient", "Singing Bowl", C, "Tibetan singing bowl: two close partials beating slowly over a long sustain.",
  M(("Beat", [("Detune", 0.3)]), ("Rim", [("Warp A", 0.3)]), ("Air", [("Noise Level", 0.1)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Level A", 0.12), ("Mod Wheel", "Warp A", 0.25)], tags=["Bowl", "Meditative"],
  oscA_table="Basic Shapes", oscA_voices=2, uni_detune=0.04, uni_spread=0.7, oscA_warp="FM", oscA_warp_amt=0.06,
  oscB_table="Basic Shapes", oscB_oct=1, oscB_semi=6, oscB_fine=-20.0, oscB_level=0.0, lfo1_rate=0.6,
  flt_type="LP12", flt_cutoff=3000.0, amp_attack=0.05, amp_decay=8.0, amp_sustain=0.2, amp_release=3.0,
  rev_size=0.75, rev_mix=0.22)
P("metallic", "Gamelan Gong", C, "Bronze gamelan gong: a soft knock and a deep, wavering tone.",
  M(("Bronze", [("Warp A", 0.35)]), ("Waver", [("Pitch", 0.004)]), ("Knock", [("Noise Level", 0.1)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Pitch", 0.002), ("Mod Env", "Warp A", 0.3)], tags=["Gamelan", "Gong", "Bronze"],
  oscA_table="Basic Shapes", oscA_oct=-1, oscA_warp="RM", oscA_warp_amt=0.35, oscB_table="Basic Shapes",
  oscB_semi=14, oscB_fine=30.0, oscB_level=0.0, noise_level=0.01, lfo1_rate=1.2, menv_decay=0.5,
  flt_type="LP24", flt_cutoff=2000.0, amp_attack=0.006, amp_decay=4.5, amp_sustain=0.0, amp_release=2.0,
  rev_size=0.75, rev_mix=0.22)
P("metallic", "Bowed Cymbal", C, "A bow drawn across a cymbal edge: a rising metallic shimmer with no attack.",
  M(("Bow", [("Resonance", 0.3)]), ("Metal", [("WT Pos A", 0.4)]), ("Air", [("Noise Level", 0.1)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Mod Env", "Cutoff", 0.4), ("LFO 1", "WT Pos A", 0.15)], tags=["Cymbal", "Bowed", "Eerie"],
  oscA_table="Metal Comb", oscA_pos=0.6, noise_level=0.08, lfo1_rate=0.5, menv_attack=1.5, menv_sustain=0.8,
  flt_type="Comb+", flt_cutoff=1800.0, flt_res=0.6, flt_keytrack=0.8, amp_attack=0.8, amp_sustain=0.9,
  amp_release=1.5, rev_size=0.8, rev_mix=0.26)

# synthetic bells --------------------------------------------------------------------------------------------
P("electronic", "Classic FM Bell", C, "Clean digital FM bell with a bright strike that rounds off into a pure tail.",
  M(("Index", [("Warp A", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Mod Env", "Warp A", 0.5), ("Velocity", "Warp A", 0.3)], tags=["FM", "Digital", "Clean"],
  oscA_table="Basic Shapes", oscA_warp="FM", oscA_warp_amt=0.12, oscB_table="Basic Shapes", oscB_oct=1, oscB_semi=10,
  oscB_fine=-14.0, oscB_level=0.0, menv_decay=0.25, flt_type="LP12", flt_cutoff=12000.0, amp_decay=1.6,
  amp_sustain=0.0, amp_release=1.2, dly_mode="PingPong", dly_time="1/4D", dly_mix=0.14, rev_size=0.6, rev_mix=0.16)
P("lofi", "Crushed Bell", C, "Bell played through a cheap sampler: crunchy bits and a dull, warm ring.",
  M(("Bits", [("Dist Mix", 0.3)]), ("Tone", [("Cutoff", 0.35)]), ("Wobble", [("Pitch", 0.004)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Random", "Pitch", 0.003)], tags=["Lo-Fi", "Crushed"],
  oscA_table="FM Bell", oscA_pos=0.35, flt_type="LP24", flt_cutoff=2400.0, amp_decay=1.8, amp_sustain=0.0,
  amp_release=0.6, dist_type="Bitcrush", dist_drive=0.35, dist_mix=0.45, rev_size=0.35, rev_mix=0.1)
P("ambient", "Bell Swell Pad", C, "Bell whose strike is hidden: the tone fades in and holds like a pad of chimes.",
  M(("Strike", [("Warp A", 0.3)]), ("Swell", [("Level A", 0.2)]), ("Width", [("Detune", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Warp A", 0.08), ("Mod Wheel", "Warp A", 0.3)], tags=["Swell", "Pad", "Chimes"],
  oscA_table="Basic Shapes", oscA_voices=3, uni_detune=0.08, uni_spread=0.9, oscA_warp="FM", oscA_warp_amt=0.1,
  oscB_table="Basic Shapes", oscB_oct=1, oscB_semi=7, oscB_fine=8.0, oscB_level=0.0, lfo1_rate=0.25,
  flt_type="LP12", flt_cutoff=5000.0, amp_attack=0.5, amp_decay=2.0, amp_sustain=0.7, amp_release=1.8,
  rev_size=0.8, rev_mix=0.26)

CANDIDATES = bc.end(_s)

if __name__ == "__main__":
    bc.write("bell1", CANDIDATES)
