#!/usr/bin/env python3
"""Stage D: House and Hip-Hop batch 1 (35). Asked for by the user after the first 300: "too little for house and
hip-hop, too much lo-fi and game-like sound, everything is warm and bland". So this batch is bright, punchy and
dry by default: higher cutoffs, short rooms, hard attacks, sidechain pump on the house sounds, loud 808s whose
harmonics are audible on small speakers.

House (17): basses (4), stabs and keys (4), leads and plucks (5), strings, arp, two transition FX.
Hip-Hop / trap / G-funk (18): 808s and basses (4), leads (5), keys (3), plucks and arp (2), bell, brass, choir hit,
vocal pad. (Garage Reese, Deep House Pad, Horn Section Hit, Rap String Stab and Drill Slide Bass were dropped:
the library already had near-identical sounds.)

    python3 tools/presets/generate_batch_urban1.py [--trim report.json]
"""
import batch_common as bc

P, M = bc.P, bc.M
bc.gp.GROUP_TAGS.update({"house": ["House"], "hiphop": ["Hip-Hop"], "trap": ["Hip-Hop", "Trap"], "rave": ["House", "Rave"]})
_s = bc.begin()

# =============================================================================================== HOUSE
P("house", "Deep House Organ Bass", "Bass", "Short organ bass with a click and a round sub, the backbone of deep house.",
  M(("Click", [("WT Pos A", 0.3)]), ("Tone", [("Cutoff", 0.35)]), ("Sub", [("Sub Level", 0.3)]), ("Pump", [("Level A", -0.2)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Deep House", "Organ", "Punchy"],
  voice_mode="Mono", oscA_table="Drawbars", oscA_pos=0.6, oscA_oct=-1, sub_level=0.35, flt_type="LP24",
  flt_cutoff=900.0, flt_envamt=0.35, fenv_decay=0.12, fenv_sustain=0.2, amp_decay=0.35, amp_sustain=0.45,
  amp_release=0.08, squash=0.3)
P("house", "Rolling Tech Bass", "Bass", "Tight FM pluck bass that rolls under the kick, ducking on every beat.",
  M(("Index", [("Warp A", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Sub", [("Sub Level", 0.3)]), ("Drive", [("Dist Drive", 0.35)])),
  mods=[("Mod Env", "Warp A", 0.4), ("Velocity", "Warp A", 0.2)], tags=["Tech House", "FM", "Rolling"],
  voice_mode="Mono", oscA_table="Basic Shapes", oscA_oct=-1, oscA_warp="FM", oscA_warp_amt=0.1, oscB_table="Basic Shapes",
  oscB_oct=1, oscB_level=0.0, sub_level=0.3, menv_decay=0.12, flt_type="LP24", flt_cutoff=2400.0, amp_decay=0.3,
  amp_sustain=0.3, amp_release=0.06, dist_type="Soft", dist_drive=0.3, dist_mix=0.5, pump_amount=0.45)
P("house", "Bass House Wobble", "Bass", "Gritty bass-house growl that talks in eighth notes.",
  M(("Talk", [("Formant", 0.35)]), ("Grit", [("Dist Drive", 0.35)]), ("Res", [("Resonance", 0.3)]), ("Sub", [("Sub Level", 0.3)])),
  mods=[("LFO 1", "Formant", 0.45), ("Velocity", "Dist Drive", 0.2)], tags=["Bass House", "Wobble", "Growl"],
  voice_mode="Mono", oscA_table="Analog Saw", oscA_voices=2, uni_detune=0.12, oscB_table="Buzz", oscB_level=0.4,
  sub_level=0.3, lfo1_shape="Triangle", lfo1_sync=True, lfo1_div="1/8", lfo1_retrig=True, flt_type="Formant",
  flt_cutoff=900.0, flt_res=0.45, flt_vowel=0.3, amp_release=0.08, dist_type="Hard", dist_drive=0.5, dist_mix=0.85,
  squash=0.4)
P("house", "Future House Bass", "Bass", "Bouncy metallic future-house bass with a quick pitch drop on every hit.",
  M(("Metal", [("Warp A", 0.35)]), ("Bounce", [("Pitch A", 0.02)]), ("Tone", [("Cutoff", 0.35)]), ("Grit", [("Dist Mix", 0.3)])),
  mods=[("Mod Env", "Warp A", 0.35), ("Velocity", "Cutoff", 0.2)], tags=["Future House", "Metallic", "Bouncy"],
  voice_mode="Mono", oscA_table="Sync Square", oscA_pos=0.3, oscA_warp="Sync", oscA_warp_amt=0.2, sub_level=0.25,
  penv_amount=5.0, penv_decay=0.05, menv_decay=0.18, flt_type="LP24", flt_cutoff=3200.0, amp_decay=0.35,
  amp_sustain=0.5, amp_release=0.08, dist_type="Hard", dist_drive=0.35, dist_mix=0.5, squash=0.35)
P("house", "Nineties House Piano", "Keys", "Bright, stacked piano for big house chords, pumping with the kick.",
  M(("Bright", [("Cutoff", 0.35)]), ("Organ", [("Level B", 0.3)]), ("Pump", [("Level A", -0.2)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Piano", "Bright", "Classic"],
  oscA_table="Hammer Piano", oscA_pos=0.15, oscA_voices=2, uni_detune=0.08, oscB_table="Drawbars", oscB_pos=0.5,
  oscB_oct=1, oscB_level=0.4, flt_type="LP12", flt_cutoff=9000.0, amp_decay=1.4, amp_sustain=0.4, amp_release=0.3,
  mfx_type="Chorus", mfx_mix=0.2, pump_amount=0.55, squash=0.3, rev_size=0.35, rev_mix=0.1)
P("house", "Dub Chord Stab", "Keys", "Deep house chord stab dissolving into dotted echoes.",
  M(("Snap", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Res", [("Resonance", 0.3)]), ("Space", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Mod Wheel", "Delay Mix", 0.3)], tags=["Deep House", "Dub", "Stab"],
  oscA_table="Saw Octaves", oscA_pos=0.3, oscB_table="Analog Square", oscB_level=0.3, flt_type="LP24",
  flt_cutoff=2400.0, flt_res=0.3, flt_envamt=0.45, fenv_decay=0.15, fenv_sustain=0.0, amp_decay=0.6, amp_sustain=0.25,
  amp_release=0.2, squash=0.5, dly_mode="PingPong", dly_time="1/8D", dly_feedback=0.6, dly_mix=0.4, rev_mix=0.12)
P("house", "Garage Organ Stab", "Keys", "Bright, percussive organ stab with a hard click for garage and speed house.",
  M(("Click", [("WT Pos A", 0.3)]), ("Bite", [("Cutoff", 0.35)]), ("Drive", [("Dist Drive", 0.35)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Garage", "Organ", "Stab"],
  oscA_table="Drive Organ", oscA_pos=0.7, oscA_oct=1, flt_type="LP12", flt_cutoff=7000.0, amp_decay=0.6,
  amp_sustain=0.25, amp_release=0.08, dist_type="Tube", dist_drive=0.35, dist_mix=0.5, squash=0.5, rev_size=0.3,
  rev_mix=0.06)
P("rave", "Rave Piano Stab", "Keys", "Early-nineties rave stab: piano and saw octaves hit hard together.",
  M(("Saw", [("Level B", 0.3)]), ("Bright", [("Cutoff", 0.35)]), ("Grit", [("Dist Mix", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Rave", "Stab", "Bright"],
  oscA_table="Hammer Piano", oscA_pos=0.1, oscB_table="Saw Octaves", oscB_pos=0.4, oscB_level=0.75, flt_type="LP12",
  flt_cutoff=12000.0, amp_decay=0.8, amp_sustain=0.25, amp_release=0.2, dist_type="Soft", dist_drive=0.5,
  dist_mix=0.5, squash=0.5, mfx_type="Chorus", mfx_mix=0.3, rev_size=0.4, rev_mix=0.1)
P("house", "Future House Pluck", "Pluck", "Bright metallic pluck that bends up into the note, made for drops.",
  M(("Metal", [("Warp A", 0.35)]), ("Bend", [("Pitch A", 0.02)]), ("Bright", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Mod Env", "Warp A", 0.3), ("Velocity", "Cutoff", 0.2)], tags=["Future House", "Metallic", "Drop"],
  oscA_table="Sync Saw", oscA_pos=0.4, oscA_warp="Sync", oscA_warp_amt=0.25, penv_amount=-2.0, penv_decay=0.05,
  menv_decay=0.2, flt_type="LP24", flt_cutoff=6000.0, amp_decay=0.35, amp_sustain=0.0, amp_release=0.15,
  squash=0.35, dly_time="1/8", dly_mix=0.1)
P("house", "Vocal Chop Stab", "Lead", "Short vocal 'hey' chops that pitch up through the vowel, like a sliced acapella.",
  M(("Vowel", [("Formant", 0.35)]), ("Pitch", [("Pitch A", 0.02)]), ("Air", [("Noise Level", 0.1)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Mod Env", "Formant", 0.5), ("Random", "Formant", 0.15)], tags=["Vocal Chop", "Stab"],
  oscA_table="Vowels", oscA_pos=0.5, oscB_table="Talk Box", oscB_level=0.4, menv_decay=0.15, flt_type="Formant",
  flt_cutoff=1300.0, flt_res=0.45, flt_vowel=0.2, amp_decay=0.25, amp_sustain=0.0, amp_release=0.08,
  dly_time="1/8", dly_mix=0.12)
P("rave", "Hoover Lead", "Lead", "Classic rave hoover: detuned pulses swooping down into every note.",
  M(("Swoop", [("Pitch A", 0.02)]), ("Width", [("Detune", 0.3)]), ("Tone", [("Cutoff", 0.35)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Mod Wheel", "Detune", 0.3)], tags=["Rave", "Hoover", "Classic"],
  voice_mode="Legato", glide=0.08, oscA_table="PWM Saw", oscA_pos=0.9, oscA_voices=5, uni_detune=0.4,
  uni_spread=0.4, penv_amount=-12.0, penv_decay=0.18, flt_type="LP24", flt_cutoff=3500.0, amp_release=0.25,
  mfx_type="Chorus", mfx_rate=0.9, mfx_mix=0.4, squash=0.3)
P("house", "Festival Saw Stab", "Lead", "Huge, bright seven-voice saw stab for big-room drops.",
  M(("Width", [("Detune", 0.3)]), ("Bright", [("Cutoff", 0.35)]), ("Octave", [("Level B", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.2)], tags=["Big Room", "Supersaw", "Drop"],
  oscA_table="Hyper Saw", oscA_pos=0.4, oscA_voices=7, uni_detune=0.4, uni_spread=1.0, oscB_table="Hyper Saw",
  oscB_oct=1, oscB_level=0.3, flt_type="LP12", flt_cutoff=10000.0, amp_decay=0.5, amp_sustain=0.3, amp_release=0.25,
  squash=0.5, rev_size=0.6, rev_mix=0.14)
P("house", "Tech Perc Pluck", "Pluck", "Dry, clicky FM blip that sits between hi-hats in a tech house groove.",
  M(("Click", [("Warp A", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Pump", [("Level A", -0.2)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Random", "Warp A", 0.2), ("Velocity", "Cutoff", 0.2)], tags=["Tech House", "Percussive", "Dry"],
  oscA_table="Basic Shapes", oscA_warp="FM", oscA_warp_amt=0.3, oscB_table="Basic Shapes", oscB_oct=2, oscB_semi=5,
  oscB_level=0.0, flt_type="HP", flt_cutoff=500.0, amp_decay=0.12, amp_sustain=0.0, amp_release=0.05,
  pump_amount=0.35, squash=0.4)
P("house", "Disco String Stab", "Strings", "Short, bright disco string stabs that pump with the beat.",
  M(("Bright", [("Cutoff", 0.35)]), ("Ensemble", [("Detune", 0.3)]), ("Pump", [("Level A", -0.2)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Disco", "Stab", "Strings"],
  oscA_table="Strings", oscA_pos=0.4, oscA_voices=5, uni_detune=0.15, oscB_table="Analog Saw", oscB_oct=1,
  oscB_level=0.45, flt_type="LP12", flt_cutoff=7000.0, amp_attack=0.01, amp_decay=0.3, amp_sustain=0.2,
  amp_release=0.2, pump_amount=0.6, squash=0.35, rev_size=0.5, rev_mix=0.12)
P("house", "House Groove Arp", "Arp", "Plucky up-down arp with ping-pong echoes, pumping under the kick.",
  M(("Snap", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Pump", [("Level A", -0.2)]), ("Res", [("Resonance", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.2)], tags=["House", "Arp", "Groove"],
  arp_on=True, arp_mode="UpDown", arp_rate="1/16", arp_octaves=2, arp_gate=0.4, oscA_table="Analog Square",
  oscA_pos=0.4, flt_type="LP24", flt_cutoff=1200.0, flt_res=0.3, flt_envamt=0.45, fenv_decay=0.1, fenv_sustain=0.0,
  amp_decay=0.2, amp_sustain=0.0, amp_release=0.1, pump_amount=0.4, dly_mode="PingPong", dly_time="1/8D",
  dly_mix=0.16)
P("house", "White Noise Riser", "FX", "Build-up riser: filtered noise climbing in pitch and brightness over two seconds.",
  M(("Rise", [("Cutoff", 0.35)]), ("Pitch", [("Pitch", 0.1)]), ("Space", [("Reverb Mix", 0.3)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Mod Env", "Cutoff", 0.8), ("Mod Env", "Pitch", 0.4)], tags=["Riser", "Build-Up", "Transition"],
  oscA_table="Hyper Saw", oscA_pos=0.5, oscA_level=0.3, noise_level=0.8, menv_attack=2.0, menv_sustain=1.0,
  flt_type="BP", flt_cutoff=400.0, flt_res=0.35, amp_attack=0.8, amp_sustain=1.0, amp_release=0.5,
  rev_size=0.7, rev_mix=0.25)
P("house", "Impact Downlifter", "FX", "Hit followed by a falling sweep, for the first beat after a drop.",
  M(("Fall", [("Pitch", 0.1)]), ("Noise", [("Noise Level", 0.15)]), ("Tone", [("Cutoff", 0.35)]), ("Space", [("Reverb Mix", 0.3)])),
  mods=[("Mod Env", "Cutoff", 0.6)], tags=["Downlifter", "Impact", "Transition"],
  oscA_table="Sine Drive", oscA_pos=0.4, oscA_oct=-1, noise_level=0.5, penv_amount=-24.0, penv_decay=1.2,
  menv_decay=1.5, flt_type="LP24", flt_cutoff=500.0, amp_decay=2.0, amp_sustain=0.0, amp_release=0.8,
  dist_type="Tube", dist_drive=0.3, dist_mix=0.4, rev_size=0.8, rev_mix=0.25)

# =============================================================================================== HIP-HOP
P("trap", "Trap 808 Punch", "Bass", "Hard trap 808 with a knock on top and a saturated tail you can hear on a phone.",
  M(("Knock", [("Pitch A", 0.03)]), ("Drive", [("Dist Drive", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Sub", [("Sub Level", 0.3)])),
  mods=[("Velocity", "Dist Drive", 0.25), ("Mod Wheel", "Cutoff", 0.3)], tags=["808", "Trap", "Hard"],
  voice_mode="Legato", glide=0.08, oscA_table="Sine Drive", oscA_pos=0.5, oscA_level=0.9, penv_amount=12.0,
  penv_decay=0.035, flt_type="LP24", flt_cutoff=2500.0, amp_decay=2.5, amp_sustain=0.6, amp_release=0.4,
  dist_type="Tube", dist_drive=0.5, dist_mix=0.7, squash=0.3)
P("trap", "Sliding 808", "Bass", "Long, clean 808 built for slides: every overlapping note glides into the next.",
  M(("Slide", [("Pitch", 0.02)]), ("Warmth", [("Dist Drive", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Sub", [("Sub Level", 0.3)])),
  mods=[("Velocity", "Dist Drive", 0.2)], tags=["808", "Glide", "Trap"],
  voice_mode="Legato", glide=0.16, oscA_table="Sine Drive", oscA_pos=0.3, oscA_level=0.9, penv_amount=4.0,
  penv_decay=0.05, flt_type="LP24", flt_cutoff=2800.0, amp_decay=3.0, amp_sustain=0.8, amp_release=0.5,
  dist_type="Tube", dist_drive=0.45, dist_mix=0.7)
P("trap", "Rage 808 Distorted", "Bass", "Blown-out 808 folded until it buzzes, for rage and hard trap.",
  M(("Fold", [("Dist Drive", 0.35)]), ("Buzz", [("WT Pos A", 0.3)]), ("Tone", [("Cutoff", 0.35)]), ("Sub", [("Sub Level", 0.3)])),
  mods=[("Velocity", "Dist Drive", 0.2)], tags=["808", "Rage", "Distorted"],
  voice_mode="Legato", glide=0.07, oscA_table="Sine Drive", oscA_pos=0.7, oscA_level=0.9, sub_level=0.2,
  penv_amount=10.0, penv_decay=0.04, flt_type="LP24", flt_cutoff=5000.0, amp_decay=2.0, amp_sustain=0.6,
  amp_release=0.3, dist_type="Fold", dist_drive=0.6, dist_mix=0.85, squash=0.35)
P("hiphop", "G-Funk Rubber Bass", "Bass", "Round, rubbery analog bass that slides between notes, West Coast style.",
  M(("Rubber", [("Resonance", 0.3)]), ("Tone", [("Cutoff", 0.35)]), ("Slide", [("Pitch", 0.02)]), ("Drive", [("Filter Drive", 0.35)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["G-Funk", "Analog", "Rubber"],
  voice_mode="Legato", glide=0.08, oscA_table="Analog Saw", oscA_oct=-1, oscB_table="Analog Square", oscB_oct=-1,
  oscB_level=0.5, flt_type="Ladder", flt_cutoff=500.0, flt_res=0.45, flt_drive=0.3, flt_envamt=0.35, fenv_decay=0.2,
  fenv_sustain=0.3, amp_release=0.1)
P("hiphop", "Sinister Saw Lead", "Lead", "Dark, detuned saw lead for menacing rap hooks.",
  M(("Menace", [("Detune", 0.3)]), ("Tone", [("Cutoff", 0.35)]), ("Grit", [("Dist Mix", 0.3)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Mod Wheel", "Pitch", 0.005), ("Velocity", "Cutoff", 0.2)], tags=["Dark", "Lead", "Menacing"],
  voice_mode="Legato", glide=0.04, oscA_table="Analog Saw", oscA_voices=3, uni_detune=0.25, oscB_table="Analog Saw",
  oscB_oct=-1, oscB_level=0.4, flt_type="LP24", flt_cutoff=3000.0, flt_res=0.15, amp_release=0.2,
  dist_type="Soft", dist_drive=0.3, dist_mix=0.0, dly_time="1/8D", dly_mix=0.12, rev_mix=0.08)
P("trap", "Rage Synth Lead", "Lead", "Screaming, clipped supersaw lead for rage beats.",
  M(("Clip", [("Dist Drive", 0.35)]), ("Width", [("Detune", 0.3)]), ("Bright", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Mod Wheel", "Pitch", 0.006)], tags=["Rage", "Supersaw", "Distorted"],
  voice_mode="Legato", glide=0.03, oscA_table="Hyper Saw", oscA_pos=0.5, oscA_voices=7, uni_detune=0.45,
  uni_spread=1.0, flt_type="LP12", flt_cutoff=9000.0, amp_release=0.2, dist_type="Hard", dist_drive=0.6, dist_mix=0.85,
  squash=0.4, dly_time="1/16", dly_mix=0.08)
P("trap", "Plugg Lead", "Lead", "Soft, bright saw-sine lead with a slow vibrato and a short echo, plugg style.",
  M(("Saw", [("Level B", 0.3)]), ("Vibrato", [("Pitch", 0.005)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("LFO 1", "Pitch", 0.003), ("Mod Wheel", "Pitch", 0.004)], tags=["Plugg", "Soft", "Lead"],
  voice_mode="Legato", glide=0.06, oscA_table="Basic Shapes", oscA_pos=0.15, oscB_table="Analog Saw", oscB_level=0.2,
  lfo1_rate=4.5, flt_type="LP12", flt_cutoff=3500.0, amp_attack=0.01, amp_release=0.25, dly_mode="PingPong",
  dly_time="1/8", dly_mix=0.15, mfx_type="Chorus", mfx_mix=0.3, rev_mix=0.15)
P("hiphop", "Portamento Whine Lead", "Lead", "High, whistling portamento lead that slides around the melody, G-funk style.",
  M(("Whine", [("Resonance", 0.3)]), ("Slide", [("Pitch", 0.01)]), ("Vibrato", [("Pitch", 0.005)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("LFO 1", "Pitch", 0.0035), ("Mod Wheel", "Pitch", 0.005)], tags=["G-Funk", "Portamento", "Whistle"],
  voice_mode="Legato", glide=0.14, oscA_table="Basic Shapes", oscA_pos=0.2, oscA_oct=1, lfo1_rate=5.5,
  flt_type="LP12", flt_cutoff=5000.0, flt_res=0.2, amp_attack=0.02, amp_release=0.2, dly_time="1/8", dly_mix=0.12,
  rev_mix=0.08)
P("hiphop", "Hyper Pluck Lead", "Lead", "Bright, bouncy pluck-lead with a quick pitch flick, for catchy rap melodies.",
  M(("Flick", [("Pitch A", 0.02)]), ("Bright", [("Cutoff", 0.35)]), ("Body", [("Level B", 0.3)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Bright", "Bouncy", "Catchy"],
  oscA_table="Analog Square", oscA_pos=0.3, oscB_table="Analog Saw", oscB_oct=1, oscB_level=0.3, penv_amount=3.0,
  penv_decay=0.03, flt_type="LP24", flt_cutoff=2500.0, flt_envamt=0.4, fenv_decay=0.2, fenv_sustain=0.3,
  amp_decay=0.4, amp_sustain=0.4, amp_release=0.15, dly_time="1/8", dly_mix=0.1)
P("trap", "Dark Trap Piano", "Keys", "Hard-hit, clean piano with a long dark tail for moody trap.",
  M(("Hit", [("Cutoff", 0.35)]), ("Body", [("WT Pos A", 0.3)]), ("Tail", [("Reverb Mix", 0.3)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.35)], tags=["Piano", "Dark", "Moody"],
  oscA_type="String", oscA_table="Hammer Piano", oscA_pos=0.3, str_decay=6.0, str_tone=0.55, flt_type="LP12",
  flt_cutoff=6000.0, amp_attack=0.008, amp_sustain=1.0, amp_release=1.0, squash=0.35, rev_size=0.85, rev_mix=0.36)
P("hiphop", "Boom Bap Jazz EP", "Keys", "Clean, punchy jazz electric piano for boom bap chords, no dust.",
  M(("Bark", [("Warp A", 0.3)]), ("Tone", [("Cutoff", 0.35)]), ("Chorus", [("Mod FX Mix", 0.4)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Warp A", 0.35), ("Mod Env", "Warp A", 0.2)], tags=["Boom Bap", "Electric Piano", "Jazz"],
  oscA_table="Basic Shapes", oscA_warp="FM", oscA_warp_amt=0.18, oscB_table="Basic Shapes", oscB_level=0.0,
  menv_decay=0.25, flt_type="LP12", flt_cutoff=6500.0, amp_decay=2.0, amp_sustain=0.2, amp_release=0.3,
  mfx_type="Chorus", mfx_mix=0.3, squash=0.3, rev_size=0.3, rev_mix=0.08)
P("hiphop", "Rap Synth Stab", "Keys", "Short, dark saw stab for punchy rap beats.",
  M(("Snap", [("Cutoff", 0.35)]), ("Grit", [("Dist Drive", 0.35)]), ("Octave", [("Level B", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.3)], tags=["Stab", "Dark", "Punchy"],
  oscA_table="Analog Saw", oscA_voices=2, uni_detune=0.12, oscB_table="Analog Saw", oscB_oct=-1, oscB_level=0.4,
  flt_type="LP24", flt_cutoff=1200.0, flt_envamt=0.5, fenv_decay=0.12, fenv_sustain=0.0, amp_decay=0.6,
  amp_sustain=0.25, amp_release=0.1, dist_type="Tube", dist_drive=0.4, dist_mix=0.6, squash=0.5)
P("hiphop", "Detroit Bounce Pluck", "Pluck", "Hard, high square pluck that bounces over Detroit-style beats.",
  M(("Bounce", [("Cutoff", 0.35)]), ("High", [("Level B", 0.3)]), ("Grit", [("Dist Mix", 0.3)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Detroit", "Bouncy", "Hard"],
  oscA_table="Analog Square", oscA_pos=0.5, oscB_table="Analog Square", oscB_oct=1, oscB_level=0.35, flt_type="LP24",
  flt_cutoff=3500.0, flt_envamt=0.35, fenv_decay=0.08, fenv_sustain=0.0, amp_decay=0.3, amp_sustain=0.1,
  amp_release=0.08, squash=0.5, amp_attack=0.004)
P("trap", "Dark Trap Arp", "Arp", "Minor triplet arpeggio with a short bell-pluck, the classic trap melody loop.",
  M(("Bell", [("Warp A", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Warp A", 0.2)], tags=["Trap", "Arp", "Triplets"],
  arp_on=True, arp_mode="Up", arp_rate="1/16T", arp_octaves=2, arp_gate=0.5, oscA_table="Basic Shapes",
  oscA_warp="FM", oscA_warp_amt=0.15, oscB_table="Basic Shapes", oscB_oct=1, oscB_level=0.0, flt_type="LP12",
  flt_cutoff=6000.0, amp_decay=0.3, amp_sustain=0.0, amp_release=0.15, rev_size=0.6, rev_mix=0.16)
P("trap", "Trap Bell Melody", "Bell", "Bright, short FM bell for trap and drill melodies.",
  M(("Shine", [("Warp A", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Mod Env", "Warp A", 0.3), ("Velocity", "Warp A", 0.25)], tags=["Trap", "Bell", "Bright"],
  oscA_table="Bell Metal", oscA_pos=0.15, oscA_oct=1, oscA_voices=2, uni_detune=0.06, oscA_warp="FM", oscA_warp_amt=0.05, oscB_table="Basic Shapes", oscB_oct=1,
  oscB_semi=7, oscB_level=0.0, menv_decay=0.3, flt_type="LP12", flt_cutoff=11000.0, amp_decay=0.5, amp_sustain=0.0,
  amp_release=0.3, dly_mode="PingPong", dly_time="1/8", dly_mix=0.14, rev_size=0.4, rev_mix=0.1)
P("hiphop", "Orchestral Brass Stab", "Brass", "Big, bright brass section hit for epic rap intros.",
  M(("Blast", [("Cutoff", 0.35)]), ("Section", [("Detune", 0.3)]), ("Grit", [("Dist Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.3)], tags=["Brass", "Epic", "Stab"],
  oscA_table="Brass", oscA_pos=0.7, oscA_voices=4, uni_detune=0.12, oscB_table="FM Brass", oscB_oct=-1,
  oscB_level=0.4, flt_type="LP24", flt_cutoff=1500.0, flt_envamt=0.45, fenv_attack=0.01, fenv_decay=0.25,
  fenv_sustain=0.3, amp_decay=0.6, amp_sustain=0.2, amp_release=0.3, squash=0.35, rev_size=0.7, rev_mix=0.2)
P("hiphop", "Choir Hit", "FX", "Huge choir 'ahh' hit with a cathedral tail, for dramatic drops.",
  M(("Choir", [("WT Pos A", 0.3)]), ("Tone", [("Cutoff", 0.35)]), ("Width", [("Detune", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Choir", "Hit", "Dramatic"],
  oscA_table="Choir", oscA_pos=0.6, oscA_voices=5, uni_detune=0.15, uni_spread=1.0, sub_level=0.15, flt_type="LP24",
  flt_cutoff=3500.0, amp_attack=0.005, amp_decay=0.8, amp_sustain=0.0, amp_release=0.6, squash=0.3, rev_size=0.9,
  rev_mix=0.35)
P("hiphop", "Vocal Ahh Pad", "Pad", "Bright, wide 'ahh' vocal pad for rap hooks and choruses.",
  M(("Vowel", [("Formant", 0.35)]), ("Air", [("Noise Level", 0.1)]), ("Width", [("Detune", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Mod Wheel", "Formant", 0.3)], tags=["Vocal", "Bright", "Hook"],
  oscA_table="Choir", oscA_pos=0.35, oscA_voices=4, uni_detune=0.14, uni_spread=1.0, oscB_table="Analog Saw",
  oscB_level=0.25, noise_level=0.015, flt_type="Formant", flt_cutoff=1600.0, flt_res=0.3, flt_vowel=0.0,
  amp_attack=0.15, amp_sustain=1.0, amp_release=0.8, rev_size=0.7, rev_mix=0.2)

CANDIDATES = bc.end(_s)

if __name__ == "__main__":
    bc.write("urban1", CANDIDATES)
