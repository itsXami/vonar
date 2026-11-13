#!/usr/bin/env python3
"""Stage D: Guitar batch 2 (25). Built on the String (plucked-string) oscillator wherever a pick is heard.

Families: clean (6), driven (6), leads (6), other plucked instruments (5), patterns and textures (3). Ideas the user rejected
in the first rounds (acoustic strum, e-bow style swell, jangle arp, surf tremolo, twelve-string) are not repeated.

    python3 tools/presets/generate_batch_guitar2.py [--trim report.json]
"""
import batch_common as bc

P, M = bc.P, bc.M
_s = bc.begin()
G = "Guitar"

# clean -------------------------------------------------------------------------------------------------------
P("acoustic", "Clean Bridge Guitar", G, "Bright bridge-pickup clean tone with a snappy pick and a short room.",
  M(("Pick", [("Cutoff", 0.35)]), ("Body", [("WT Pos A", 0.3)]), ("Chorus", [("Mod FX Mix", 0.4)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Random", "Pitch", 0.0015)], tags=["Clean", "Bright"],
  oscA_type="String", oscA_table="Analog Saw", oscA_pos=0.2, str_decay=3.5, str_tone=0.8, flt_type="LP12",
  flt_cutoff=6000.0, amp_attack=0.004, amp_sustain=1.0, amp_release=0.15, squash=0.35, rev_size=0.3, rev_mix=0.1)
P("warm", "Jazz Neck Guitar", G, "Round, dark neck-pickup tone for soft chords and walking lines.",
  M(("Tone", [("Cutoff", 0.35)]), ("Thumb", [("WT Pos A", 0.3)]), ("Air", [("Noise Level", 0.08)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Clean", "Jazz", "Dark"],
  oscA_type="String", oscA_table="Basic Shapes", oscA_pos=0.4, str_decay=3.0, str_tone=0.42, flt_type="LP24",
  flt_cutoff=1600.0, amp_attack=0.006, amp_sustain=1.0, amp_release=0.2, squash=0.3, rev_size=0.4, rev_mix=0.12)
P("acoustic", "Chorused Clean Guitar", G, "Glassy clean guitar spread wide by a slow, deep chorus.",
  M(("Depth", [("Mod FX Mix", 0.4)]), ("Bright", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.25), ("Mod Wheel", "Mod FX Mix", 0.3)], tags=["Clean", "Chorus", "Wide"],
  oscA_type="String", oscA_table="PWM", oscA_pos=0.3, str_decay=4.0, str_tone=0.72, flt_type="LP12", flt_cutoff=5000.0,
  amp_attack=0.004, amp_sustain=1.0, amp_release=0.2, squash=0.3, mfx_type="Chorus", mfx_rate=0.35, mfx_depth=0.8,
  mfx_mix=0.6, rev_size=0.5, rev_mix=0.14)
P("acoustic", "Bossa Nylon Guitar", G, "Soft nylon strings plucked with the thumb, close and dry.",
  M(("Thumb", [("Cutoff", -0.3)]), ("Body", [("Level B", 0.3)]), ("Ring", [("WT Pos A", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Random", "Pan A", 0.15)], tags=["Nylon", "Soft", "Dry"],
  oscA_type="String", oscA_table="Pluck Body", oscA_pos=0.6, str_decay=2.4, str_tone=0.5, oscB_table="Pluck Body",
  oscB_level=0.12, oscB_oct=-1, flt_type="LP12", flt_cutoff=3200.0, amp_attack=0.008, amp_sustain=1.0, amp_release=0.15,
  squash=0.3, rev_size=0.25, rev_mix=0.06)
P("vintage", "Country Twang Guitar", G, "Compressed, twangy single-coil picking with a quick slapback echo.",
  M(("Twang", [("Resonance", 0.3)]), ("Snap", [("Cutoff", 0.35)]), ("Slap", [("Delay Mix", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.3)], tags=["Clean", "Twang", "Slapback"],
  oscA_type="String", oscA_table="Analog Square", oscA_pos=0.3, str_decay=2.6, str_tone=0.85, flt_type="BP",
  flt_cutoff=1800.0, flt_res=0.25, flt_keytrack=0.4, amp_attack=0.012, amp_sustain=1.0, amp_release=0.1, squash=0.55, dist_type="Soft", dist_drive=0.3, dist_mix=0.5,
  dly_time="1/16", dly_feedback=0.1, dly_mix=0.18)
P("warm", "Clean Delay Lead Guitar", G, "Clean singing lead with dotted-eighth echoes that fill the space between notes.",
  M(("Echo", [("Delay Mix", 0.3)]), ("Tone", [("Cutoff", 0.35)]), ("Vibrato", [("Pitch", 0.004)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Mod Wheel", "Pitch", 0.004), ("Velocity", "Cutoff", 0.2)], tags=["Clean", "Delay", "Lead"],
  oscA_type="String", oscA_table="Analog Saw", oscA_pos=0.35, str_decay=5.0, str_tone=0.78, flt_type="LP12",
  flt_cutoff=5500.0, amp_attack=0.005, amp_sustain=1.0, amp_release=0.3, squash=0.35,
  dly_mode="PingPong", dly_time="1/8D", dly_feedback=0.45, dly_mix=0.28, rev_size=0.5, rev_mix=0.12)

# driven ------------------------------------------------------------------------------------------------------
P("vintage", "Crunch Rhythm Guitar", G, "Edge-of-breakup amp crunch that cleans up when you play softly.",
  M(("Gain", [("Dist Drive", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Body", [("Sub Level", 0.2)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Dist Drive", 0.35), ("Velocity", "Cutoff", 0.2)], tags=["Crunch", "Rhythm"],
  oscA_type="String", oscA_table="Analog Saw", oscA_pos=0.25, str_decay=3.0, str_tone=0.7, flt_type="LP24",
  flt_cutoff=2800.0, flt_res=0.15, amp_attack=0.004, amp_sustain=1.0, amp_release=0.12, dist_type="Tube", dist_drive=0.55,
  dist_tone=0.55, dist_mix=0.85, squash=0.25, rev_size=0.3, rev_mix=0.08)
P("acoustic", "Fingerpicked Pattern Guitar", G, "Held chords turn into a gentle fingerpicked pattern on nylon strings.",
  M(("Thumb", [("Cutoff", -0.3)]), ("Ring", [("WT Pos A", 0.3)]), ("Echo", [("Delay Mix", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.25), ("Random", "Pan A", 0.2), ("Random", "Cutoff", 0.08)], tags=["Fingerpicking", "Nylon", "Pattern"],
  arp_on=True, arp_mode="UpDown", arp_rate="1/8", arp_octaves=1, arp_gate=0.95, oscA_type="String",
  oscA_table="Pluck Body", oscA_pos=0.45, str_decay=3.0, str_tone=0.55, flt_type="LP12", flt_cutoff=3600.0,
  amp_attack=0.008, amp_sustain=1.0, amp_release=0.4, squash=0.3, rev_size=0.4, rev_mix=0.14)
P("electronic", "Doom Drop Guitar", G, "Down-tuned, slow and heavy: a dark wall of fuzz an octave below.",
  M(("Weight", [("Sub Level", 0.3)]), ("Fuzz", [("Dist Drive", 0.35)]), ("Dark", [("Cutoff", -0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Dist Drive", 0.2)], tags=["Distorted", "Heavy", "Dark"],
  oscA_type="String", oscA_table="Rasp", oscA_pos=0.4, oscA_oct=-1, str_decay=8.0, str_tone=0.5, sub_level=0.15,
  flt_type="LP24", flt_cutoff=1400.0, flt_res=0.2, amp_attack=0.006, amp_sustain=1.0, amp_release=0.3,
  dist_type="Fold", dist_drive=0.5, dist_tone=0.4, dist_mix=0.85, squash=0.35)
P("ambient", "Shoegaze Wall Guitar", G, "Fuzzed chords smeared by chorus and a huge reverb into a soft roar.",
  M(("Fuzz", [("Dist Drive", 0.35)]), ("Wash", [("Reverb Mix", 0.3)]), ("Swirl", [("Mod FX Mix", 0.4)]), ("Tone", [("Cutoff", 0.35)])),
  mods=[("Mod Wheel", "Pitch", -0.01), ("Velocity", "Cutoff", 0.15)], tags=["Fuzz", "Wash", "Dreamy"],
  oscA_type="String", oscA_table="Hyper Saw", oscA_pos=0.3, oscA_voices=2, uni_detune=0.1, str_decay=8.0, str_tone=0.6,
  flt_type="LP24", flt_cutoff=2600.0, amp_attack=0.04, amp_sustain=1.0, amp_release=1.0, dist_type="Fold",
  dist_drive=0.45, dist_mix=0.8, mfx_type="Chorus", mfx_rate=0.3, mfx_depth=0.9, mfx_mix=0.6, rev_size=0.92,
  rev_damping=0.6, rev_mix=0.45)
P("vintage", "Funk Scratch Guitar", G, "Muted, percussive scratch strums with a tight high-passed bite.",
  M(("Mute", [("Cutoff", -0.3)]), ("Bite", [("Resonance", 0.3)]), ("Grit", [("Dist Mix", 0.3)]), ("Room", [("Reverb Mix", 0.2)])),
  mods=[("Velocity", "Cutoff", 0.35), ("Random", "Cutoff", 0.1)], tags=["Muted", "Funk", "Percussive"],
  oscA_type="String", oscA_table="Noise Cycle", oscA_pos=0.3, str_decay=0.35, str_tone=0.55, noise_level=0.04,
  flt_type="HP", flt_cutoff=450.0, flt_res=0.2, amp_attack=0.003, amp_sustain=1.0, amp_release=0.05,
  dist_type="Soft", dist_drive=0.4, dist_mix=0.6, squash=0.6)
P("vintage", "Rubber Bridge Guitar", G, "Thuddy vintage guitar muted with foam at the bridge: short, round notes.",
  M(("Thud", [("Sub Level", 0.2)]), ("Tone", [("Cutoff", 0.35)]), ("Ring", [("WT Pos A", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Random", "Pitch", 0.0015)], tags=["Muted", "Vintage", "Round"],
  oscA_type="String", oscA_table="Analog Square", oscA_pos=0.5, str_decay=0.9, str_tone=0.35, sub_level=0.1,
  flt_type="LP24", flt_cutoff=1500.0, amp_attack=0.01, amp_decay=0.6, amp_sustain=0.3, amp_release=0.1,
  dist_type="Tube", dist_drive=0.3, dist_mix=0.5, squash=0.45, rev_size=0.25, rev_mix=0.06)
P("lofi", "Bedroom Lo-Fi Guitar", G, "Cheap guitar recorded to a worn tape: wobbly pitch and a dull, warm top.",
  M(("Wobble", [("Pitch", 0.004)]), ("Tape", [("Dist Mix", 0.3)]), ("Tone", [("Cutoff", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("LFO 1", "Pitch", 0.004), ("Random", "Pitch", 0.003), ("Velocity", "Cutoff", 0.2)], tags=["Lo-Fi", "Tape", "Warm"],
  oscA_type="String", oscA_table="Pluck Body", oscA_pos=0.35, str_decay=3.0, str_tone=0.55, lfo1_rate=0.5,
  noise_level=0.015, flt_type="LP24", flt_cutoff=1900.0, amp_attack=0.006, amp_sustain=1.0, amp_release=0.2,
  dist_type="Tube", dist_drive=0.35, dist_tone=0.35, dist_mix=0.5, squash=0.3, rev_size=0.3, rev_mix=0.08)

# leads -------------------------------------------------------------------------------------------------------
P("electronic", "High Gain Lead Guitar", G, "Saturated singing lead that sustains forever, with mod-wheel vibrato.",
  M(("Gain", [("Dist Drive", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Vibrato", [("Pitch", 0.006)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Mod Wheel", "Pitch", 0.005), ("LFO 1", "Pitch", 0.002), ("Velocity", "Dist Drive", 0.15)], tags=["Lead", "Distorted", "Sustain"],
  voice_mode="Legato", glide=0.04, oscA_type="String", oscA_table="Analog Saw", oscA_pos=0.3, str_decay=10.0,
  str_tone=0.7, lfo1_rate=5.5, flt_type="LP24", flt_cutoff=4600.0, amp_attack=0.005, amp_sustain=1.0, amp_release=0.25,
  dist_type="Hard", dist_drive=0.8, dist_tone=0.5, dist_mix=0.95, dly_time="1/8D", dly_mix=0.12, rev_mix=0.08)
P("electronic", "Searing Sustain Lead", G, "Synced, screaming lead tone that bends up into its notes and holds them.",
  M(("Scream", [("Warp A", 0.35)]), ("Gain", [("Dist Drive", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Mod Env", "Warp A", 0.3), ("Mod Wheel", "Pitch", 0.005), ("Velocity", "Warp A", 0.2)], tags=["Lead", "Distorted", "Sync"],
  voice_mode="Legato", glide=0.08, oscA_table="Sync Saw", oscA_pos=0.25, oscA_warp="Sync", oscA_warp_amt=0.15,
  penv_amount=-1.5, penv_decay=0.12, menv_decay=0.8, menv_sustain=0.3, flt_type="LP24", flt_cutoff=3800.0,
  amp_attack=0.01, amp_sustain=1.0, amp_release=0.3, dist_type="Hard", dist_drive=0.55, dist_mix=0.9,
  dly_time="1/4", dly_feedback=0.3, dly_mix=0.1, rev_mix=0.08)
P("vintage", "Slide Blues Guitar", G, "Bottleneck slide guitar that glides between notes and hums with a little grit.",
  M(("Slide", [("Pitch", 0.004)]), ("Grit", [("Dist Drive", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("LFO 1", "Pitch", 0.003), ("Mod Wheel", "Pitch", 0.004)], tags=["Slide", "Blues"],
  voice_mode="Legato", glide=0.18, oscA_type="String", oscA_table="Analog Saw", oscA_pos=0.4, str_decay=6.0,
  str_tone=0.6, lfo1_rate=5.0, flt_type="LP24", flt_cutoff=2800.0, amp_attack=0.005, amp_sustain=1.0, amp_release=0.3,
  dist_type="Tube", dist_drive=0.4, dist_mix=0.7, rev_size=0.4, rev_mix=0.12)
P("electronic", "Fuzz Octave Lead", G, "Gated fuzz with an octave-up layer that spits on every note.",
  M(("Octave", [("Level B", 0.3)]), ("Fuzz", [("Dist Drive", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Velocity", "Level B", 0.25), ("Mod Wheel", "Pitch", 0.005)], tags=["Fuzz", "Octave", "Lead"],
  voice_mode="Mono", oscA_type="String", oscA_table="Analog Square", oscA_pos=0.3, str_decay=6.0, str_tone=0.7,
  oscB_table="Analog Square", oscB_oct=1, oscB_level=0.3, flt_type="LP24", flt_cutoff=3000.0, amp_attack=0.004,
  amp_sustain=1.0, amp_release=0.1, dist_type="Fold", dist_drive=0.55, dist_mix=0.9, dly_time="1/8", dly_mix=0.1)
P("vintage", "Pedal Wah Lead", G, "Overdriven lead with a wah pedal on the mod wheel, from heel-down growl to toe-down squeal.",
  M(("Wah", [("Formant", 0.35)]), ("Gain", [("Dist Drive", 0.35)]), ("Peak", [("Resonance", 0.3)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Mod Wheel", "Formant", 0.7), ("Velocity", "Formant", 0.15)], tags=["Wah", "Lead", "Expressive"],
  voice_mode="Legato", glide=0.03, oscA_type="String", oscA_table="Analog Saw", oscA_pos=0.3, str_decay=8.0,
  str_tone=0.7, flt_type="Formant", flt_cutoff=1000.0, flt_res=0.5, flt_vowel=0.15, amp_attack=0.005, amp_sustain=1.0,
  amp_release=0.25, dist_type="Tube", dist_drive=0.5, dist_mix=0.85, dly_time="1/8D", dly_mix=0.1)
P("warm", "Harmony Twin Lead", G, "Two guitars in harmony a major third apart, singing one melody together.",
  M(("Harmony", [("Level B", 0.3)]), ("Gain", [("Dist Drive", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Mod Wheel", "Pitch", 0.005), ("LFO 1", "Pitch", 0.002)], tags=["Lead", "Harmony"],
  voice_mode="Legato", glide=0.04, oscA_type="String", oscA_table="Analog Saw", oscA_pos=0.3, oscA_pan=-0.5,
  oscB_type="String", oscB_table="Analog Saw", oscB_pos=0.35, oscB_semi=4, oscB_level=0.6, oscB_pan=0.5,
  str_decay=7.0, str_tone=0.68, lfo1_rate=5.2, flt_type="LP24", flt_cutoff=3200.0, amp_attack=0.005, amp_sustain=1.0,
  amp_release=0.25, dist_type="Tube", dist_drive=0.45, dist_mix=0.8, dly_time="1/8D", dly_mix=0.1, rev_mix=0.08)

# other plucked instruments -----------------------------------------------------------------------------------
P("acoustic", "Banjo Pluck", G, "Bright, short banjo twang with a metallic ring from its drum head.",
  M(("Ring", [("Resonance", 0.3)]), ("Bright", [("Cutoff", 0.35)]), ("Roll", [("Delay Mix", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Random", "Pitch", 0.0015)], tags=["Banjo", "Bright", "Folk"],
  oscA_type="String", oscA_table="Metal Comb", oscA_pos=0.3, str_decay=1.4, str_tone=0.9, flt_type="Comb+",
  flt_cutoff=2600.0, flt_res=0.2, amp_attack=0.004, amp_sustain=1.0, amp_release=0.1, squash=0.45, rev_size=0.25, rev_mix=0.06)
P("acoustic", "Mandolin Tremolo", G, "Mandolin played with fast tremolo picking on every held note.",
  M(("Speed", [("Level A", 0.2)]), ("Bright", [("Cutoff", 0.35)]), ("Width", [("Detune", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.25), ("Random", "Pan A", 0.25)], tags=["Mandolin", "Tremolo", "Folk"],
  arp_on=True, arp_mode="Up", arp_rate="1/32", arp_gate=0.8, oscA_type="String", oscA_table="Pluck Body",
  oscA_pos=0.3, oscA_voices=2, uni_detune=0.08, str_decay=1.6, str_tone=0.85, flt_type="LP12", flt_cutoff=6500.0,
  amp_attack=0.003, amp_sustain=1.0, amp_release=0.08, squash=0.35, rev_size=0.4, rev_mix=0.12)
P("metallic", "Sitar Buzz", G, "Droning plucked strings with the buzzing bridge of a sitar and a slow bend.",
  M(("Buzz", [("Resonance", 0.3)]), ("Bend", [("Pitch", 0.01)]), ("Drone", [("Level B", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Mod Wheel", "Pitch", 0.01), ("Velocity", "Resonance", 0.15)], tags=["Sitar", "Drone", "Buzz"],
  oscA_type="String", oscA_table="Buzz", oscA_pos=0.6, str_decay=6.0, str_tone=0.85, oscB_table="Buzz",
  oscB_oct=-1, oscB_level=0.12, flt_type="Comb-", flt_cutoff=1400.0, flt_res=0.55, flt_keytrack=1.0,
  amp_attack=0.004, amp_sustain=1.0, amp_release=0.4, squash=0.35, rev_size=0.5, rev_mix=0.14)
P("warm", "Lap Steel Glide", G, "Clean lap steel sliding smoothly between chords with a gentle vibrato.",
  M(("Glide", [("Pitch", 0.004)]), ("Tone", [("Cutoff", 0.35)]), ("Swell", [("Level A", 0.2)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Pitch", 0.0025), ("Mod Wheel", "Pitch", 0.004)], tags=["Slide", "Steel", "Smooth"],
  voice_mode="Legato", glide=0.3, oscA_type="String", oscA_table="Basic Shapes", oscA_pos=0.5, str_decay=8.0,
  str_tone=0.62, lfo1_rate=5.5, flt_type="LP12", flt_cutoff=3500.0, amp_attack=0.008, amp_sustain=1.0, amp_release=0.4,
  squash=0.3, rev_size=0.6, rev_mix=0.18)
P("acoustic", "Ukulele Strum", G, "Small, bright nylon ukulele with a soft body and quick decay.",
  M(("Bright", [("Cutoff", 0.35)]), ("Body", [("WT Pos A", 0.3)]), ("Strum", [("Pan A", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Random", "Pan A", 0.2)], tags=["Ukulele", "Nylon", "Bright"],
  oscA_type="String", oscA_table="Pluck Body", oscA_pos=0.2, oscA_oct=1, str_decay=2.4, str_tone=0.7, flt_type="LP12",
  flt_cutoff=5500.0, amp_attack=0.012, amp_sustain=1.0, amp_release=0.12, squash=0.4, rev_size=0.3, rev_mix=0.08)

# textures ----------------------------------------------------------------------------------------------------
P("metallic", "Harmonics Chime Guitar", G, "Natural harmonics plucked high on the neck, chiming like small bells.",
  M(("Chime", [("Level B", 0.3)]), ("Bright", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.25), ("Random", "Pan A", 0.3)], tags=["Harmonics", "Chime", "Clean"],
  oscA_type="String", oscA_table="Glass Harmonics", oscA_pos=0.4, oscA_oct=1, str_decay=4.0, str_tone=0.95,
  oscB_table="Basic Shapes", oscB_oct=2, oscB_semi=7, oscB_level=0.06, flt_type="LP12", flt_cutoff=9000.0,
  amp_attack=0.004, amp_sustain=1.0, amp_release=0.5, squash=0.3, dly_mode="PingPong", dly_time="1/4D", dly_mix=0.16,
  rev_size=0.7, rev_mix=0.2)
P("ambient", "Reverse Bloom Guitar", G, "Guitar chords that swell in backwards and bloom into an echoing tail.",
  M(("Bloom", [("Reverb Mix", 0.3)]), ("Echo", [("Delay Mix", 0.3)]), ("Tone", [("Cutoff", 0.35)]), ("Shimmer", [("Mod FX Mix", 0.4)])),
  mods=[("Mod Env", "Cutoff", 0.3), ("Mod Wheel", "Mod FX Mix", 0.3)], tags=["Ambient", "Swell", "Reverse"],
  oscA_type="String", oscA_table="Analog Saw", oscA_pos=0.3, str_decay=9.0, str_tone=0.6, menv_attack=0.6,
  menv_sustain=0.7, flt_type="LP24", flt_cutoff=1200.0, amp_attack=0.55, amp_sustain=1.0, amp_release=0.8,
  mfx_type="Flanger", mfx_rate=0.15, mfx_mix=0.25, dly_mode="PingPong", dly_time="1/4", dly_feedback=0.5, dly_mix=0.3,
  rev_size=0.85, rev_mix=0.35)

CANDIDATES = bc.end(_s)

if __name__ == "__main__":
    bc.write("guitar2", CANDIDATES)
