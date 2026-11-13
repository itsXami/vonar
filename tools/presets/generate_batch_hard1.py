#!/usr/bin/env python3
"""Stage D: Hard batch 1 (30) - sounds that really hit, for trap, rage, drill, bass house and rave.

Written after the diagnosis of 2026-11-12 (docs/DIAGNOZA_2026-11-12.md): most "aggressive" presets were dark basses
whose distortion only warmed them, because the distortion sat behind a low filter and the limiter test pushed
hard presets to be softened. Rules for this batch, from the research notes:
  - distortion audible: open filters (3-12 kHz), Hard / Fold / Bitcrush, lots of 1-4 kHz content;
  - basses with rich mids keep a clean sub: the new Keep Low switch distorts only above ~160 Hz (not on the
    sine 808s: almost all of their energy is below the split, so they are clipped full-band instead);
  - attacks 0-2 ms, a click from Mod Env -> Noise Level or a Pitch Env dive where it fits;
  - macro 1 is always "Energy" (drive + top end), so each preset can go from tight to blown-out;
  - loudness follows the mood (Aggressive presets sit ~2.5 dB above the library), no softening to pass a test.
Families: 808s (4), mid-range basses (6), leads (7), stabs and hits (5), guitars (2), arps (2), FX (4).

    python3 tools/presets/generate_batch_hard1.py [--trim report.json]
"""
import batch_common as bc

P, M = bc.P, bc.M
bc.gp.GROUP_TAGS.update({"house": ["House"], "hiphop": ["Hip-Hop"], "trap": ["Hip-Hop", "Trap"],
                         "rave": ["House", "Rave"], "rage": ["Hip-Hop", "Rage"], "industrial": ["Industrial"]})
_s = bc.begin()
A = "Aggressive"

# ============================================================================================ 808s
P("trap", "Clipped 808", "Bass", "Hard-clipped 808 whose upper harmonics read on phone speakers while the sub stays clean.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Punch", [("Pitch A", 0.04)]), ("Tone", [("Cutoff", 0.3)]),
    ("Sub", [("Sub Level", 0.3)])),
  mods=[("Velocity", "Dist Drive", 0.25), ("Mod Env", "Noise Level", 0.25)], tags=["808", "Clipped", "Loud"], mood=A,
  voice_mode="Legato", glide=0.06, oscA_table="Sine Drive", oscA_pos=0.45, oscA_level=0.95, sub_level=0.35,
  penv_amount=14.0, penv_decay=0.045, menv_decay=0.01, flt_type="LP24", flt_cutoff=9000.0, amp_attack=0.0005,
  amp_decay=1.6, amp_sustain=0.55, amp_release=0.25, dist_type="Hard", dist_drive=0.8, dist_tone=0.7, dist_mix=1.0,
  squash=0.3)
P("trap", "Fold Glide 808", "Bass", "Wavefolded 808 that growls as it slides, the fold sweeping with every note.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Fold", [("Dist Mix", 0.3)]), ("Slide", [("Pitch A", -0.03)]),
    ("Sub", [("Sub Level", 0.3)])),
  mods=[("Mod Env", "Dist Drive", 0.3), ("Velocity", "Cutoff", 0.2)], tags=["808", "Glide", "Fold"], mood=A,
  voice_mode="Legato", glide=0.14, oscA_table="Sine Drive", oscA_pos=0.5, oscA_level=0.95,
  sub_level=0.3, penv_amount=7.0, penv_decay=0.06, menv_decay=0.5, menv_sustain=0.2, flt_type="LP12",
  flt_cutoff=7000.0, amp_attack=0.0005, amp_decay=2.2, amp_sustain=0.6, amp_release=0.3, dist_type="Fold",
  dist_drive=0.85, dist_tone=0.65, dist_mix=0.9)
P("trap", "Drill Slide 808", "Bass", "Short, gritty 808 with a fast downward slide into every note, for drill patterns.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Slide", [("Pitch A", 0.04)]), ("Grit", [("Dist Mix", 0.3)]),
    ("Length", [("Sub Level", 0.3)])),
  mods=[("Velocity", "Dist Drive", 0.2)], tags=["808", "Drill", "Slide"], mood=A,
  voice_mode="Legato", glide=0.09, oscA_table="Sine Drive", oscA_pos=0.6, oscA_level=0.95, sub_level=0.3,
  penv_amount=-5.0, penv_decay=0.12, flt_type="LP24", flt_cutoff=6000.0, flt_res=0.15, amp_attack=0.0005,
  amp_decay=0.9, amp_sustain=0.25, amp_release=0.18, dist_type="Tube", dist_drive=0.75, dist_tone=0.65, dist_mix=1.0,
  squash=0.25)
P("rage", "Crushed Rage 808", "Bass", "Bitcrushed, buzzing 808 with a square edge for rage beats.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Buzz", [("WT Pos A", 0.3)]), ("Crush", [("Dist Mix", 0.3)]),
    ("Sub", [("Sub Level", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.25), ("Random", "WT Pos A", 0.08)], tags=["808", "Rage", "Bitcrush"], mood=A,
  voice_mode="Legato", glide=0.05, oscA_table="Basic Shapes", oscA_pos=0.75, oscA_level=0.8,
  sub_level=0.45, penv_amount=12.0, penv_decay=0.04, flt_type="LP24", flt_cutoff=4500.0, amp_attack=0.0005,
  amp_decay=1.4, amp_sustain=0.5, amp_release=0.25, dist_type="Bitcrush", dist_drive=0.55, dist_tone=0.75,
  dist_mix=0.75, squash=0.35)

# ============================================================================================ MID-RANGE BASSES
P("house", "Bass House Snarl", "Bass", "Talking, snarling bass-house growl with a hard-clipped top and a clean sub under it.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Talk", [("Formant", 0.35)]), ("Res", [("Resonance", 0.3)]),
    ("Sub", [("Sub Level", 0.3)])),
  mods=[("LFO 1", "Formant", 0.5), ("Velocity", "Cutoff", 0.2)], tags=["Bass House", "Growl", "Formant"], mood=A,
  voice_mode="Mono", oscA_table="Buzz", oscA_pos=0.4, oscA_voices=2, uni_detune=0.1, oscB_table="Analog Saw",
  oscB_level=0.5, oscB_oct=-1, sub_level=0.4, lfo1_shape="Square", lfo1_sync=True, lfo1_div="1/16", lfo1_retrig=True,
  flt_type="Formant", flt_cutoff=2200.0, flt_res=0.5, flt_vowel=0.4, amp_attack=0.0005, amp_release=0.06,
  dist_type="Hard", dist_drive=0.7, dist_mix=1.0, dist_keep_low=True, squash=0.45, pump_amount=0.3)
P("house", "Sync Punch Bass", "Bass", "Bright sync bass that snaps open on every note, for speed garage and bassline.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Sync", [("Warp A", 0.35)]), ("Snap", [("Cutoff", 0.3)]),
    ("Sub", [("Sub Level", 0.3)])),
  mods=[("Mod Env", "Warp A", 0.55), ("Velocity", "Warp A", 0.2), ("Mod Env", "Noise Level", 0.2)],
  tags=["Bassline", "Sync", "Punchy"], mood=A,
  voice_mode="Mono", oscA_table="Sync Saw", oscA_pos=0.2, oscA_warp="Sync", oscA_warp_amt=0.15, sub_level=0.4,
  menv_decay=0.16, flt_type="LP24", flt_cutoff=5500.0, flt_res=0.25, amp_attack=0.0005, amp_decay=0.4,
  amp_sustain=0.6, amp_release=0.06, dist_type="Tube", dist_drive=0.6, dist_mix=0.85, dist_keep_low=True, squash=0.35)
P("industrial", "Shredder Reese", "Bass", "Wide, tearing reese with heavy clipping on the mids and a solid mono sub.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Tear", [("Detune", 0.3)]), ("Motion", [("Cutoff", 0.25)]),
    ("Sub", [("Sub Level", 0.3)])),
  mods=[("LFO 1", "Cutoff", 0.12), ("LFO 2", "WT Pos A", 0.15)], tags=["Reese", "Distorted", "Wide"], mood=A,
  voice_mode="Mono", oscA_table="Hyper Saw", oscA_pos=0.5, oscA_voices=4, uni_detune=0.3, uni_spread=0.9,
  oscB_table="Analog Saw", oscB_level=0.5, oscB_fine=-14.0, sub_level=0.45, lfo1_rate=0.35, lfo2_rate=0.13,
  flt_type="LP24", flt_cutoff=3800.0, flt_res=0.3, amp_attack=0.002, amp_release=0.12, dist_type="Hard",
  dist_drive=0.75, dist_mix=1.0, dist_keep_low=True, squash=0.4)
P("industrial", "FM Snarl Bass", "Bass", "Metallic FM bass whose index jumps on every hit, folded into a snarl.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Index", [("Warp A", 0.35)]), ("Fold", [("Dist Mix", 0.3)]),
    ("Sub", [("Sub Level", 0.3)])),
  mods=[("Mod Env", "Warp A", 0.6), ("Velocity", "Warp A", 0.25), ("Random", "Warp A", 0.1)],
  tags=["FM", "Metallic", "Snarl"], mood=A,
  voice_mode="Mono", oscA_table="FM Bass", oscA_pos=0.4, oscA_warp="FM", oscA_warp_amt=0.25, sub_level=0.4,
  menv_decay=0.22, flt_type="LP12", flt_cutoff=8000.0, amp_attack=0.0005, amp_decay=0.5, amp_sustain=0.55,
  amp_release=0.08, dist_type="Fold", dist_drive=0.5, dist_mix=0.8, dist_keep_low=True, squash=0.3)
P("rave", "Acid Burn Bass", "Bass", "Screaming acid line pushed into a hard clipper, resonance biting through.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Acid", [("Resonance", 0.25)]), ("Env", [("Cutoff", 0.3)]),
    ("Slide", [("Pitch A", 0.02)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Mod Wheel", "Resonance", 0.2)], tags=["Acid", "Squelch", "Distorted"], mood=A,
  voice_mode="Legato", glide=0.07, oscA_table="Analog Saw", oscA_pos=0.1, oscA_level=0.9, flt_type="Ladder",
  flt_cutoff=1800.0, flt_res=0.72, flt_envamt=0.7, fenv_decay=0.2, fenv_sustain=0.1, amp_attack=0.0005,
  amp_sustain=0.9, amp_release=0.05, dist_type="Hard", dist_drive=0.65, dist_tone=0.8, dist_mix=0.9, squash=0.3)
P("industrial", "Grind Square Bass", "Bass", "Crushed square bass with a buzzing top end for dark, heavy grooves.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Width", [("WT Pos A", 0.3)]), ("Crush", [("Dist Mix", 0.3)]),
    ("Sub", [("Sub Level", 0.3)])),
  mods=[("LFO 1", "WT Pos A", 0.2), ("Velocity", "Cutoff", 0.2)], tags=["Square", "Bitcrush", "Heavy"], mood="Dark",
  voice_mode="Mono", oscA_table="PWM", oscA_pos=0.3, oscA_oct=-1, sub_level=0.4, lfo1_rate=0.6, flt_type="LP24",
  flt_cutoff=2800.0, flt_res=0.2, amp_attack=0.001, amp_release=0.1, dist_type="Bitcrush", dist_drive=0.45,
  dist_tone=0.6, dist_mix=0.7, dist_keep_low=True, squash=0.3)

# ============================================================================================ LEADS
P("rage", "Rage Sync Screamer", "Lead", "Piercing sync lead that screams on long notes, for rage and hyper beats.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Scream", [("Warp A", 0.35)]), ("Width", [("Detune", 0.3)]),
    ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Mod Env", "Warp A", 0.4), ("Mod Wheel", "Warp A", 0.3), ("Velocity", "Cutoff", 0.2)],
  tags=["Sync", "Screaming", "Rage"], mood=A,
  voice_mode="Legato", glide=0.04, oscA_table="Sync Saw", oscA_pos=0.4, oscA_warp="Sync", oscA_warp_amt=0.3,
  oscA_voices=3, uni_detune=0.12, menv_attack=0.05, menv_decay=0.6, menv_sustain=0.5, flt_type="LP12",
  flt_cutoff=11000.0, amp_attack=0.001, amp_release=0.12, dist_type="Hard", dist_drive=0.6, dist_mix=0.8, squash=0.4,
  dly_mode="PingPong", dly_time="1/8", dly_feedback=0.3, dly_mix=0.12)
P("rage", "Blown Supersaw", "Lead", "Huge supersaw driven into a wavefolder until it fizzes, for hard drops.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Fold", [("Dist Mix", 0.3)]), ("Width", [("Detune", 0.3)]),
    ("Space", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.2), ("Random", "Detune", 0.05)], tags=["Supersaw", "Fold", "Huge"], mood=A,
  oscA_table="Hyper Saw", oscA_pos=0.6, oscA_voices=7, uni_detune=0.35, uni_spread=1.0, oscB_table="Saw Octaves",
  oscB_level=0.3, oscB_oct=1, flt_type="LP12", flt_cutoff=12000.0, amp_attack=0.001, amp_sustain=1.0,
  amp_release=0.25, dist_type="Fold", dist_drive=0.45, dist_tone=0.7, dist_mix=0.7, squash=0.5, rev_size=0.45,
  rev_mix=0.08)
P("rave", "Acid Scream Lead", "Lead", "High, squealing acid lead with the resonance near self-oscillation.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Squeal", [("Resonance", 0.25)]), ("Env", [("Cutoff", 0.3)]),
    ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.3), ("LFO 1", "Cutoff", 0.08)], tags=["Acid", "Squeal", "Rave"], mood=A,
  voice_mode="Legato", glide=0.05, oscA_table="Acid", oscA_pos=0.7, lfo1_sync=True, lfo1_div="1/8", flt_type="Ladder",
  flt_cutoff=1500.0, flt_res=0.8, flt_envamt=0.5, fenv_decay=0.25, fenv_sustain=0.2, amp_attack=0.0005,
  amp_release=0.08, dist_type="Fold", dist_drive=0.4, dist_mix=0.6, dly_mode="PingPong", dly_time="1/8D",
  dly_feedback=0.4, dly_mix=0.18)
P("rave", "Rave Siren Lead", "Lead", "Detuned octave saws wailing like a siren, with a fast vibrato for old-school rave.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Siren", [("Pitch", 0.03)]), ("Width", [("Detune", 0.3)]),
    ("Hall", [("Reverb Mix", 0.25)])),
  mods=[("LFO 1", "Pitch", 0.012), ("Mod Wheel", "Pitch", 0.02)], tags=["Rave", "Siren", "Detuned"], mood=A,
  voice_mode="Legato", glide=0.09, oscA_table="Saw Octaves", oscA_pos=0.5, oscA_voices=4, uni_detune=0.3,
  lfo1_rate=6.5, flt_type="LP24", flt_cutoff=7000.0, amp_attack=0.002, amp_release=0.2, dist_type="Hard",
  dist_drive=0.45, dist_mix=0.55, squash=0.35, rev_size=0.6, rev_mix=0.1)
P("industrial", "Bit Riot Lead", "Lead", "Bitcrushed square lead that sputters on loud notes, raw and digital.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Crush", [("Dist Mix", 0.3)]), ("Pulse", [("WT Pos A", 0.3)]),
    ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Velocity", "Dist Drive", 0.3), ("LFO 1", "WT Pos A", 0.2)], tags=["Bitcrush", "Square", "Digital"], mood=A,
  voice_mode="Mono", glide=0.03, oscA_table="PWM", oscA_pos=0.25, lfo1_rate=5.0, flt_type="LP12", flt_cutoff=9000.0,
  amp_attack=0.0005, amp_release=0.08, dist_type="Bitcrush", dist_drive=0.65, dist_tone=0.85, dist_mix=0.85,
  squash=0.3, dly_time="1/16", dly_feedback=0.25, dly_mix=0.1)
P("industrial", "Shouting Formant Lead", "Lead", "Distorted lead that shouts vowels as it moves, like a voice through a megaphone.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Vowel", [("Formant", 0.35)]), ("Width", [("Detune", 0.3)]),
    ("Room", [("Reverb Mix", 0.25)])),
  mods=[("LFO 1", "Formant", 0.35), ("Mod Wheel", "Formant", 0.3), ("Velocity", "Dist Drive", 0.2)],
  tags=["Formant", "Vocal", "Distorted"], mood=A,
  voice_mode="Legato", glide=0.05, oscA_table="Vocal Fry", oscA_pos=0.5, oscA_voices=2, uni_detune=0.08,
  lfo1_sync=True, lfo1_div="1/4", flt_type="Formant", flt_cutoff=2000.0, flt_res=0.45, flt_vowel=0.2,
  amp_attack=0.002, amp_release=0.12, dist_type="Hard", dist_drive=0.65, dist_mix=0.85, squash=0.35)
P("house", "Festival Sync Lead", "Lead", "Bright, punchy sync lead for big-room house hooks, loud but clean.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Sync", [("Warp A", 0.3)]), ("Width", [("Detune", 0.3)]),
    ("Space", [("Reverb Mix", 0.25)])),
  mods=[("Mod Env", "Warp A", 0.35), ("Velocity", "Cutoff", 0.2)], tags=["Big Room", "Sync", "Bright"], mood="Medium",
  oscA_table="Sync Square", oscA_pos=0.3, oscA_warp="Sync", oscA_warp_amt=0.2, oscA_voices=5, uni_detune=0.2,
  uni_spread=0.9, menv_decay=0.3, flt_type="LP24", flt_cutoff=9500.0, amp_attack=0.001, amp_decay=0.6,
  amp_sustain=0.75, amp_release=0.2, dist_type="Tube", dist_drive=0.4, dist_mix=0.4, squash=0.45, pump_amount=0.35,
  rev_size=0.5, rev_mix=0.1)

# ============================================================================================ STABS AND HITS
P("rave", "Hard House Stab", "Keys", "Clipped saw chord stab with a punchy attack, ducking hard under the kick.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Snap", [("Cutoff", 0.3)]), ("Pump", [("Level A", -0.2)]),
    ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Hard House", "Stab", "Clipped"], mood=A,
  oscA_table="Saw Octaves", oscA_pos=0.4, oscA_voices=3, uni_detune=0.15, oscB_table="Analog Square",
  oscB_level=0.35, flt_type="LP24", flt_cutoff=5000.0, flt_envamt=0.4, fenv_decay=0.1, fenv_sustain=0.1,
  amp_attack=0.0005, amp_decay=0.6, amp_sustain=0.15, amp_release=0.3, dist_type="Hard", dist_drive=0.6,
  dist_mix=0.85, squash=0.45, pump_amount=0.5, dly_time="1/8D", dly_feedback=0.3, dly_mix=0.12)
P("rave", "Hoover Stab", "Keys", "Thick, detuned pulse stab that bends down on every chord, the rave hoover.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Bend", [("Pitch", -0.02)]), ("Width", [("Detune", 0.3)]),
    ("Hall", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.2)], tags=["Rave", "Hoover", "Detuned"], mood=A,
  oscA_table="PWM Saw", oscA_pos=0.5, oscA_voices=6, uni_detune=0.4, uni_spread=1.0, penv_amount=-3.0,
  penv_decay=0.35, flt_type="LP12", flt_cutoff=6000.0, amp_attack=0.002, amp_decay=0.7, amp_sustain=0.3,
  amp_release=0.3, dist_type="Tube", dist_drive=0.5, dist_mix=0.6, squash=0.4, rev_size=0.6, rev_mix=0.12)
P("industrial", "Metal Smash Stab", "Pluck", "Ring-modulated metallic hit with a clipped attack, like hitting sheet metal.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Ring", [("Warp A", 0.35)]), ("Tail", [("Reverb Mix", 0.3)]),
    ("Pitch", [("Pitch", 0.1)])),
  mods=[("Mod Env", "Warp A", 0.4), ("Random", "Warp A", 0.1), ("Mod Env", "Noise Level", 0.4)],
  tags=["Metallic", "Hit", "Ring Mod"], mood=A,
  oscA_table="Metal Comb", oscA_pos=0.4, oscA_warp="RM", oscA_warp_amt=0.5, oscB_table="Bell Metal", oscB_level=0.4,
  oscB_semi=7, oscB_fine=13.0, menv_decay=0.08, flt_type="HP", flt_cutoff=180.0, amp_attack=0.0005, amp_decay=0.45,
  amp_sustain=0.0, amp_release=0.4, dist_type="Hard", dist_drive=0.6, dist_mix=0.8, rev_size=0.35, rev_mix=0.12)
P("trap", "Trap Brass Hit", "Brass", "Short, distorted brass blast for trap intros and hard hooks.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Blare", [("Cutoff", 0.3)]), ("Low", [("Sub Level", 0.3)]),
    ("Hall", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.3)], tags=["Brass", "Hit", "Trap"], mood=A,
  oscA_table="FM Brass", oscA_pos=0.6, oscA_voices=3, uni_detune=0.1, oscB_table="Brass", oscB_level=0.5,
  oscB_oct=-1, flt_type="LP24", flt_cutoff=1800.0, flt_envamt=0.5, fenv_attack=0.004, fenv_decay=0.18,
  fenv_sustain=0.3, amp_attack=0.002, amp_decay=0.9, amp_sustain=0.15, amp_release=0.4, dist_type="Tube",
  dist_drive=0.65, dist_mix=0.7, squash=0.4, rev_size=0.55, rev_mix=0.12)
P("trap", "Broken Bell", "Bell", "Bell melody driven into a clipper so the strike cracks, for dark, hard trap.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Metal", [("Warp A", 0.3)]), ("Tail", [("Reverb Mix", 0.3)]),
    ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Mod Env", "Warp A", 0.35), ("Velocity", "Dist Drive", 0.25)], tags=["Bell", "Distorted", "Trap"], mood=A,
  oscA_table="FM Bell", oscA_pos=0.5, oscA_warp="FM", oscA_warp_amt=0.3, menv_decay=0.3, flt_type="LP12",
  flt_cutoff=10000.0, amp_attack=0.0005, amp_decay=1.2, amp_sustain=0.0, amp_release=1.0, dist_type="Hard",
  dist_drive=0.55, dist_mix=0.7, dly_mode="PingPong", dly_time="1/4T", dly_feedback=0.35, dly_mix=0.15,
  rev_size=0.6, rev_mix=0.12)

# ============================================================================================ GUITARS
P("rage", "Rage Guitar Lead", "Guitar", "Overdriven plucked-string lead with a slide, cutting like a rage hook.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Bright", [("Cutoff", 0.3)]), ("Slide", [("Pitch", 0.02)]),
    ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Velocity", "Dist Drive", 0.25), ("Mod Wheel", "Pitch", 0.01)], tags=["Guitar", "Overdrive", "Lead"], mood=A,
  voice_mode="Legato", glide=0.06, oscA_type="String", str_decay=3.0, str_tone=0.8, oscB_table="Analog Saw",
  oscB_level=0.25, flt_type="LP12", flt_cutoff=7500.0, amp_attack=0.0005, amp_decay=2.0, amp_sustain=0.6,
  amp_release=0.2, dist_type="Hard", dist_drive=0.7, dist_tone=0.6, dist_mix=1.0, squash=0.4, dly_mode="PingPong",
  dly_time="1/8D", dly_feedback=0.3, dly_mix=0.12)
P("industrial", "Fuzz Wall Riff", "Guitar", "Folded, fuzzy power-chord wall for heavy riffs.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Fuzz", [("Dist Mix", 0.3)]), ("Mute", [("Cutoff", -0.3)]),
    ("Width", [("Detune", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Guitar", "Fuzz", "Riff"], mood=A,
  oscA_type="String", str_decay=2.5, str_tone=0.7, oscB_table="Buzz", oscB_level=0.35, oscB_oct=-1, oscB_voices=2,
  uni_detune=0.1, flt_type="LP24", flt_cutoff=5500.0, amp_attack=0.0005, amp_decay=1.6, amp_sustain=0.5,
  amp_release=0.15, dist_type="Fold", dist_drive=0.6, dist_tone=0.55, dist_mix=1.0, squash=0.5)

# ============================================================================================ ARPS
P("rave", "Hard Trance Gate", "Arp", "Driven saw arp in sixteenths with a tight gate, for hard trance and rave builds.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Gate", [("Cutoff", 0.3)]), ("Width", [("Detune", 0.3)]),
    ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.2), ("LFO 1", "Cutoff", 0.1)], tags=["Trance", "Gate", "Driven"], mood=A,
  arp_on=True, arp_mode="UpDown", arp_rate="1/16", arp_octaves=2, arp_gate=0.4, oscA_table="Hyper Saw", oscA_pos=0.4,
  oscA_voices=4, uni_detune=0.2, lfo1_sync=True, lfo1_div="2/1", flt_type="LP24", flt_cutoff=4500.0, flt_envamt=0.3,
  fenv_decay=0.08, fenv_sustain=0.2, amp_attack=0.0005, amp_decay=0.12, amp_sustain=0.3, amp_release=0.05,
  dist_type="Hard", dist_drive=0.5, dist_mix=0.65, squash=0.4, dly_mode="PingPong", dly_time="1/8D",
  dly_feedback=0.3, dly_mix=0.12)
P("rave", "Acid Rave Arp", "Arp", "Random acid arp with a screaming resonant filter and a crushed edge.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Acid", [("Resonance", 0.2)]), ("Env", [("Cutoff", 0.3)]),
    ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Random", "Cutoff", 0.15), ("Velocity", "Cutoff", 0.2)], tags=["Acid", "Random", "Rave"], mood=A,
  arp_on=True, arp_mode="Random", arp_rate="1/16", arp_octaves=2, arp_gate=0.55, oscA_table="Acid", oscA_pos=0.5,
  flt_type="Ladder", flt_cutoff=900.0, flt_res=0.7, flt_envamt=0.55, fenv_decay=0.12, fenv_sustain=0.0,
  amp_attack=0.0005, amp_decay=0.2, amp_sustain=0.4, amp_release=0.05, dist_type="Bitcrush", dist_drive=0.4,
  dist_tone=0.8, dist_mix=0.45, dly_time="1/8D", dly_feedback=0.35, dly_mix=0.15)

# ============================================================================================ FX
P("rave", "Siren Riser", "FX", "Noisy, distorted riser that climbs two octaves while a siren LFO speeds the tension.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Noise", [("Noise Level", 0.3)]), ("Climb", [("Pitch", 0.2)]),
    ("Hall", [("Reverb Mix", 0.25)])),
  mods=[("Mod Env", "Pitch", 1.0), ("Mod Env", "Cutoff", 0.4), ("LFO 1", "Pitch", 0.02)], tags=["Riser", "Siren", "Build"],
  mood=A,
  oscA_table="Saw Octaves", oscA_pos=0.5, oscA_voices=4, uni_detune=0.25, noise_level=0.25, menv_attack=4.0,
  menv_decay=0.5, menv_sustain=1.0, menv_release=0.4, lfo1_rate=7.0, flt_type="LP24", flt_cutoff=1500.0,
  amp_attack=0.05, amp_release=0.5, dist_type="Hard", dist_drive=0.5, dist_mix=0.7, squash=0.4, rev_size=0.7,
  rev_mix=0.15)
P("trap", "Distorted Impact", "FX", "Huge clipped impact: a sub drop and a noise blast for the first beat of a drop.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Blast", [("Noise Level", 0.3)]), ("Drop", [("Sub Level", 0.3)]),
    ("Hall", [("Reverb Mix", 0.25)])),
  mods=[("Mod Env", "Noise Level", 0.8), ("Mod Env", "Cutoff", 0.3)], tags=["Impact", "Drop", "Sub"], mood=A,
  oscA_table="Sine Drive", oscA_pos=0.4, oscA_oct=-2, oscA_level=0.95, sub_level=0.4, penv_amount=36.0,
  penv_decay=0.4, menv_decay=0.4, flt_type="LP24", flt_cutoff=5000.0, amp_attack=0.0005, amp_decay=1.8,
  amp_sustain=0.0, amp_release=1.6, dist_type="Hard", dist_drive=0.7, dist_mix=0.9, rev_size=0.8, rev_mix=0.15)
P("industrial", "Glitch Stutter", "FX", "Random sample-and-hold stutter that chops pitch and tone into crushed bits.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Chop", [("Pitch", 0.2)]), ("Crush", [("Dist Mix", 0.3)]),
    ("Echo", [("Delay Mix", 0.3)])),
  mods=[("LFO 1", "Pitch", 0.25), ("LFO 2", "Cutoff", 0.35), ("LFO 1", "WT Pos A", 0.4)], tags=["Glitch", "Stutter", "S&H"],
  mood=A,
  oscA_table="FM Digital", oscA_pos=0.4, lfo1_shape="S&H", lfo1_sync=True, lfo1_div="1/16", lfo1_retrig=True,
  lfo2_shape="S&H", lfo2_sync=True, lfo2_div="1/32", flt_type="BP", flt_cutoff=2500.0, flt_res=0.35,
  amp_attack=0.0005, amp_release=0.1, dist_type="Bitcrush", dist_drive=0.6, dist_tone=0.85, dist_mix=0.8,
  dly_mode="PingPong", dly_time="1/16", dly_feedback=0.4, dly_mix=0.15)
P("house", "Laser Gun Zap", "FX", "Short, hard laser zap diving three octaves, for fills and drop accents.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Dive", [("Pitch", 0.2)]), ("Echo", [("Delay Mix", 0.3)]),
    ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.2)], tags=["Zap", "Laser", "Fill"], mood=A,
  oscA_table="Sync Square", oscA_pos=0.6, oscA_warp="Sync", oscA_warp_amt=0.4, oscA_oct=2, penv_amount=-36.0,
  penv_decay=0.25, flt_type="LP12", flt_cutoff=12000.0, amp_attack=0.0005, amp_decay=0.3, amp_sustain=0.0,
  amp_release=0.25, dist_type="Hard", dist_drive=0.55, dist_mix=0.75, dly_mode="PingPong", dly_time="1/16",
  dly_feedback=0.35, dly_mix=0.18)

CANDIDATES = bc.end(_s)

if __name__ == "__main__":
    bc.write("hard1", CANDIDATES)
