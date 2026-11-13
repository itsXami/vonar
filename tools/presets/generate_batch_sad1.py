#!/usr/bin/env python3
"""Stage D: Sad / Dark batch 1 (21) - melancholy and dark sounds, mostly for emotional rap, trap and drill.

The library had only ~6 % Sad presets. Sad here does not mean quiet: the batch spans energy levels 2-4 - a sad
piano can be soft, but an emo-rap lead or a drill bell still cuts through. Recipes: minor-sounding detune, slow
vibrato, dark but not muffled filters (1.5-4 kHz), dotted or triplet delays, damped rooms, a few eerie metallic
tones. No lo-fi wobble, no flutes. Macro 1 is the Energy macro (drive + brightness).

    python3 tools/presets/generate_batch_sad1.py [--trim report.json]
"""
import batch_common as bc

P, M = bc.P, bc.M
bc.gp.GROUP_TAGS.update({"hiphop": ["Hip-Hop"], "trap": ["Hip-Hop", "Trap"], "cinematic": ["Cinematic"]})
_s = bc.begin()
E = ("Energy", [("Dist Mix", 0.35), ("Cutoff", 0.25)])
S, D = "Sad", "Dark"

# ============================================================================================ KEYS
P("trap", "Sad Trap Piano", "Keys", "Hushed piano with a long damped room, for slow, emotional trap chords.",
  M(E, ("Bright", [("Cutoff", 0.3)]), ("Echo", [("Delay Mix", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.35), ("Random", "Pitch", 0.0008)], tags=["Piano", "Emotional", "Minor"], mood=S,
  oscA_table="Hammer Piano", oscA_pos=0.1, flt_type="LP12", flt_cutoff=3200.0, amp_attack=0.001, amp_decay=3.0,
  amp_sustain=0.0, amp_release=0.8, dly_mode="PingPong", dly_time="1/4D", dly_feedback=0.3, dly_mix=0.1,
  rev_size=0.75, rev_damping=0.7, rev_mix=0.22)
P("hiphop", "Rainy Day EP", "Keys", "Soft electric piano with a slow wobble and a sigh of detune, for sad rap verses.",
  M(E, ("Bell", [("Warp A", 0.3)]), ("Wobble", [("Mod FX Mix", 0.4)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Warp A", 0.25), ("LFO 1", "Pitch", 0.001)], tags=["Electric Piano", "Melancholy", "Soft"], mood=S,
  oscA_table="Basic Shapes", oscA_pos=0.05, oscA_warp="FM", oscA_warp_amt=0.12, oscA_voices=2, uni_detune=0.06,
  lfo1_rate=0.6, flt_type="LP12", flt_cutoff=3500.0, amp_attack=0.002, amp_decay=2.5, amp_sustain=0.15,
  amp_release=0.5, mfx_type="Chorus", mfx_rate=0.3, mfx_mix=0.3, rev_size=0.6, rev_mix=0.15)
P("cinematic", "Funeral Organ", "Keys", "Low pipe organ in a cold stone room, dark and heavy.",
  M(E, ("Pipes", [("WT Pos A", 0.3)]), ("Weight", [("Sub Level", 0.3)]), ("Hall", [("Reverb Mix", 0.25)])),
  mods=[("LFO 1", "Level A", -0.05)], tags=["Organ", "Pipe", "Cold"], mood=D,
  oscA_table="Pipe Organ", oscA_pos=0.5, sub_level=0.15, lfo1_rate=5.5, flt_type="LP24", flt_cutoff=3000.0,
  amp_attack=0.05, amp_sustain=1.0, amp_release=1.0, rev_size=0.85, rev_damping=0.6, rev_mix=0.25)

# ============================================================================================ PLUCKS AND BELLS
P("trap", "Pain Pluck", "Pluck", "Bright, aching pluck with a triplet echo, the melody of an emotional trap beat.",
  M(E, ("Tone", [("Cutoff", 0.3)]), ("Echo", [("Delay Mix", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Random", "Pitch", 0.001)], tags=["Pluck", "Emotional", "Melody"], mood=S,
  oscA_type="String", str_decay=1.2, str_tone=0.75, oscB_table="Glass Harmonics", oscB_level=0.15, oscB_oct=1,
  flt_type="LP12", flt_cutoff=6000.0, amp_attack=0.0005, amp_decay=1.2, amp_sustain=0.0, amp_release=0.6,
  dly_mode="PingPong", dly_time="1/8T", dly_feedback=0.4, dly_mix=0.2, rev_size=0.6, rev_mix=0.15)
P("trap", "Eerie Music Box", "Bell", "Detuned music box ringing in a dark room, the eerie top line of a horror beat.",
  M(E, ("Detune", [("Detune", 0.3)]), ("Echo", [("Delay Mix", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Random", "Pitch", 0.003), ("Velocity", "Warp A", 0.2)], tags=["Music Box", "Eerie", "Detuned"], mood=D,
  oscA_table="Basic Shapes", oscA_pos=0.0, oscA_oct=1, oscA_warp="FM", oscA_warp_amt=0.4, oscA_voices=2,
  uni_detune=0.12, flt_type="HP", flt_cutoff=500.0, amp_attack=0.0005, amp_decay=1.0, amp_sustain=0.0,
  amp_release=1.0, dly_time="1/4D", dly_feedback=0.4, dly_mix=0.18, rev_size=0.8, rev_damping=0.5, rev_mix=0.25)
P("trap", "Drill Bell", "Bell", "Cold, hard bell with a quick metallic strike, for drill and dark trap melodies.",
  M(E, ("Metal", [("Warp A", 0.3)]), ("Glide", [("Pitch", 0.02)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Mod Env", "Warp A", 0.4), ("Velocity", "Cutoff", 0.25)], tags=["Bell", "Drill", "Cold"], mood=D,
  voice_mode="Legato", glide=0.05, oscA_table="Bell Metal", oscA_pos=0.4, oscA_warp="RM", oscA_warp_amt=0.25,
  menv_decay=0.12, flt_type="LP12", flt_cutoff=8000.0, amp_attack=0.0005, amp_decay=1.6, amp_sustain=0.1,
  amp_release=0.8, dist_type="Tube", dist_drive=0.5, dist_mix=0.5, squash=0.45, rev_size=0.5, rev_mix=0.12)
P("hiphop", "Detuned Lullaby", "Bell", "Childlike celesta slightly out of tune, sweet and sad at once.",
  M(E, ("Tone", [("Cutoff", 0.3)]), ("Wobble", [("Pitch", 0.01)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("LFO 1", "Pitch", 0.002), ("Velocity", "Cutoff", 0.25)], tags=["Celesta", "Detuned", "Melancholy"], mood=S,
  oscA_table="Glass Harmonics", oscA_pos=0.3, oscA_oct=1, oscB_table="Basic Shapes", oscB_level=0.3, oscB_oct=1,
  oscB_fine=-18.0, lfo1_rate=0.8, flt_type="LP12", flt_cutoff=7000.0, amp_attack=0.0005, amp_decay=1.4,
  amp_sustain=0.0, amp_release=1.0, rev_size=0.6, rev_mix=0.18)
P("hiphop", "Weeping Guitar", "Guitar", "Nylon-string melody with a slow vibrato, for sad intros and hooks.",
  M(E, ("Tone", [("Cutoff", 0.3)]), ("Vibrato", [("Pitch", 0.01)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Mod Wheel", "Pitch", 0.006)], tags=["Nylon", "Vibrato", "Melancholy"], mood=S,
  oscA_type="String", str_decay=2.2, str_tone=0.45, flt_type="LP12", flt_cutoff=4500.0, amp_attack=0.0005,
  amp_decay=2.0, amp_sustain=0.0, amp_release=0.6, mfx_type="Chorus", mfx_mix=0.15, rev_size=0.55, rev_mix=0.15)
P("hiphop", "Emo Guitar Pluck", "Guitar", "Lightly driven guitar pluck with a dotted echo, for emo rap and sad rock beats.",
  M(E, ("Drive", [("Dist Drive", 0.3)]), ("Echo", [("Delay Mix", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Dist Drive", 0.25)], tags=["Guitar", "Emo", "Driven"], mood=S,
  oscA_type="String", str_decay=1.6, str_tone=0.7, flt_type="LP12", flt_cutoff=6500.0, amp_attack=0.0005,
  amp_decay=1.6, amp_sustain=0.0, amp_release=0.4, dist_type="Tube", dist_drive=0.45, dist_mix=0.55,
  dly_mode="PingPong", dly_time="1/8D", dly_feedback=0.35, dly_mix=0.18, rev_size=0.5, rev_mix=0.1)

# ============================================================================================ LEADS
P("hiphop", "Emo Saw Lead", "Lead", "Bright, crying saw lead with a slow vibrato and a little grit, for melodic rap hooks.",
  M(E, ("Cry", [("Cutoff", 0.3)]), ("Vibrato", [("Pitch", 0.01)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("LFO 1", "Pitch", 0.003), ("Mod Wheel", "Pitch", 0.006), ("Velocity", "Cutoff", 0.2)],
  tags=["Saw", "Emotional", "Vibrato"], mood=S,
  voice_mode="Legato", glide=0.07, oscA_table="Analog Saw", oscA_voices=3, uni_detune=0.12, lfo1_rate=4.5,
  flt_type="LP24", flt_cutoff=4200.0, flt_res=0.2, amp_attack=0.003, amp_release=0.25, dist_type="Tube",
  dist_drive=0.4, dist_mix=0.4, squash=0.3, dly_mode="PingPong", dly_time="1/4D", dly_feedback=0.35, dly_mix=0.15,
  rev_size=0.6, rev_mix=0.12)
P("cinematic", "Sinister Choir Lead", "Lead", "Dark choir voice that bends between notes, menacing and low.",
  M(E, ("Vowel", [("Formant", 0.3)]), ("Bend", [("Pitch", 0.02)]), ("Hall", [("Reverb Mix", 0.25)])),
  mods=[("Mod Wheel", "Formant", 0.3), ("LFO 1", "Pitch", 0.002)], tags=["Choir", "Sinister", "Glide"], mood=D,
  voice_mode="Legato", glide=0.12, oscA_table="Choir", oscA_pos=0.7, oscA_voices=3, uni_detune=0.1, lfo1_rate=4.0,
  flt_type="Formant", flt_cutoff=1300.0, flt_res=0.35, flt_vowel=0.7, amp_attack=0.05, amp_release=0.6,
  rev_size=0.8, rev_damping=0.6, rev_mix=0.22)
P("trap", "Lonely Whistle Lead", "Lead", "Thin, high whistle lead with a breathy edge, lonely over a sparse beat.",
  M(E, ("Breath", [("Noise Level", 0.1)]), ("Vibrato", [("Pitch", 0.01)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("LFO 1", "Pitch", 0.003), ("Mod Wheel", "Pitch", 0.006)], tags=["Whistle", "Thin", "Lonely"], mood=S,
  voice_mode="Legato", glide=0.08, oscA_table="Basic Shapes", oscA_pos=0.15, oscA_oct=1, noise_level=0.03,
  lfo1_rate=5.5, flt_type="BP", flt_cutoff=2500.0, flt_res=0.25, flt_keytrack=0.8, amp_attack=0.03,
  amp_release=0.4, dly_mode="PingPong", dly_time="1/4D", dly_feedback=0.4, dly_mix=0.2, rev_size=0.7, rev_mix=0.2)

# ============================================================================================ PADS AND STRINGS
P("cinematic", "Grieving Strings", "Strings", "Slow string section swelling with a weary vibrato, for sad endings.",
  M(E, ("Bow", [("Cutoff", 0.3)]), ("Vibrato", [("Pitch", 0.01)]), ("Hall", [("Reverb Mix", 0.25)])),
  mods=[("LFO 1", "Pitch", 0.002), ("Velocity", "Cutoff", 0.2)], tags=["Strings", "Slow", "Melancholy"], mood=S,
  oscA_table="Strings", oscA_pos=0.3, oscA_voices=5, uni_detune=0.12, uni_spread=1.0, lfo1_rate=4.2,
  flt_type="LP12", flt_cutoff=3500.0, amp_attack=0.5, amp_sustain=1.0, amp_release=1.4, rev_size=0.8,
  rev_damping=0.6, rev_mix=0.22)
P("cinematic", "Dark Cello Line", "Strings", "Solo cello biting into low notes, a dark and tense melodic line.",
  M(E, ("Bite", [("Cutoff", 0.3)]), ("Vibrato", [("Pitch", 0.01)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Mod Wheel", "Pitch", 0.006)], tags=["Cello", "Solo", "Tense"], mood=D,
  voice_mode="Legato", glide=0.04, oscA_table="Strings", oscA_pos=0.6, oscA_oct=-1, oscB_table="Rasp",
  oscB_level=0.2, oscB_oct=-1, flt_type="LP24", flt_cutoff=2800.0, flt_res=0.15, amp_attack=0.06, amp_release=0.35,
  rev_size=0.5, rev_mix=0.12)
P("hiphop", "Empty Room Pad", "Pad", "Hollow pad that feels like an empty room at night, with a faint distant shimmer.",
  M(E, ("Shimmer", [("WT Pos A", 0.3)]), ("Width", [("Detune", 0.3)]), ("Space", [("Reverb Mix", 0.25)])),
  mods=[("LFO 1", "WT Pos A", 0.12), ("Random", "Pan A", 0.3)], tags=["Hollow", "Night", "Melancholy"], mood=S,
  oscA_table="Hollow", oscA_pos=0.5, oscA_voices=3, uni_detune=0.1, uni_spread=1.0, oscB_table="Glass Harmonics",
  oscB_level=0.12, oscB_oct=1, lfo1_rate=0.12, flt_type="LP12", flt_cutoff=2600.0, amp_attack=0.9, amp_sustain=1.0,
  amp_release=2.0, rev_size=0.85, rev_mix=0.25)
P("trap", "Haunted Choir Pad", "Pad", "Low, ghostly choir drifting between vowels, the dark bed of a horror beat.",
  M(E, ("Vowel", [("Formant", 0.3)]), ("Ghost", [("Noise Level", 0.1)]), ("Space", [("Reverb Mix", 0.25)])),
  mods=[("LFO 1", "Formant", 0.3), ("LFO 2", "Pitch", 0.002)], tags=["Choir", "Ghostly", "Horror"], mood=D,
  oscA_table="Choir", oscA_pos=0.8, oscA_voices=4, uni_detune=0.16, uni_spread=1.0, noise_level=0.02,
  lfo1_rate=0.1, lfo2_rate=0.25, flt_type="Formant", flt_cutoff=1100.0, flt_res=0.3, flt_vowel=0.6,
  amp_attack=1.0, amp_sustain=1.0, amp_release=2.0, rev_size=0.85, rev_damping=0.5, rev_mix=0.28)
P("hiphop", "Ghost Vocal Pad", "Pad", "Breathy, airy 'ooh' that hangs behind a sad hook like a memory.",
  M(E, ("Breath", [("Noise Level", 0.1)]), ("Vowel", [("Formant", 0.3)]), ("Space", [("Reverb Mix", 0.25)])),
  mods=[("Mod Wheel", "Formant", 0.3)], tags=["Vocal", "Breathy", "Melancholy"], mood=S,
  oscA_table="Vowels", oscA_pos=0.75, oscA_voices=3, uni_detune=0.1, uni_spread=1.0, noise_level=0.04,
  flt_type="LP12", flt_cutoff=3000.0, amp_attack=0.4, amp_sustain=1.0, amp_release=1.6, dly_time="1/4D",
  dly_feedback=0.4, dly_mix=0.12, rev_size=0.8, rev_mix=0.25)
P("cinematic", "Cold Brass Swell", "Brass", "Low brass swelling in slowly, cold and ominous.",
  M(E, ("Swell", [("Cutoff", 0.3)]), ("Weight", [("Sub Level", 0.3)]), ("Hall", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Brass", "Swell", "Ominous"], mood=D,
  oscA_table="Brass", oscA_pos=0.5, oscA_oct=-1, oscA_voices=3, uni_detune=0.1, flt_type="LP24", flt_cutoff=600.0,
  flt_envamt=0.4, fenv_attack=1.2, fenv_decay=1.0, fenv_sustain=0.7, amp_attack=0.6, amp_sustain=1.0,
  amp_release=1.0, rev_size=0.8, rev_mix=0.2)

# ============================================================================================ BASS, ARP, FX
P("trap", "Slow Tears 808", "Bass", "Warm, slightly saturated 808 with a long slow glide, for sad melodic trap.",
  M(E, ("Glide", [("Pitch A", -0.02)]), ("Warmth", [("WT Pos A", 0.3)]), ("Tail", [("Sub Level", 0.3)])),
  mods=[("Velocity", "Level A", 0.15)], tags=["808", "Glide", "Melodic"], mood=S,
  voice_mode="Legato", glide=0.18, oscA_table="Sine Drive", oscA_pos=0.25, oscA_level=0.95, penv_amount=5.0,
  penv_decay=0.06, flt_type="LP24", flt_cutoff=2200.0, amp_attack=0.001, amp_decay=2.5, amp_sustain=0.5,
  amp_release=0.4, dist_type="Tube", dist_drive=0.35, dist_mix=0.4)
P("trap", "Night Drive Arp", "Arp", "Dark minor-key arp gliding in eighth-note triplets through a ping-pong echo.",
  M(E, ("Tone", [("Cutoff", 0.3)]), ("Echo", [("Delay Mix", 0.3)]), ("Space", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.2), ("LFO 1", "Cutoff", 0.1)], tags=["Arp", "Night", "Triplets"], mood=D,
  arp_on=True, arp_mode="UpDown", arp_rate="1/8T", arp_octaves=2, arp_gate=0.6, oscA_table="Hollow", oscA_pos=0.6,
  oscB_table="Analog Saw", oscB_level=0.3, oscB_fine=-8.0, lfo1_sync=True, lfo1_div="4/1", flt_type="LP24",
  flt_cutoff=2400.0, flt_res=0.25, amp_attack=0.002, amp_decay=0.35, amp_sustain=0.3, amp_release=0.2,
  dly_mode="PingPong", dly_time="1/4T", dly_feedback=0.45, dly_mix=0.2, rev_size=0.6, rev_mix=0.12)
P("cinematic", "Dark Drone", "FX", "Low, slowly beating drone with a metallic undertone for tense intros.",
  M(E, ("Metal", [("Warp A", 0.3)]), ("Beat", [("Detune", 0.3)]), ("Space", [("Reverb Mix", 0.25)])),
  mods=[("LFO 1", "Warp A", 0.2), ("LFO 2", "Cutoff", 0.1)], tags=["Drone", "Tense", "Metallic"], mood=D,
  oscA_table="Metal Comb", oscA_pos=0.3, oscA_oct=-1, oscA_warp="RM", oscA_warp_amt=0.2, oscA_voices=3,
  uni_detune=0.08, sub_level=0.3, lfo1_rate=0.07, lfo2_rate=0.11, flt_type="LP24", flt_cutoff=900.0,
  amp_attack=1.2, amp_sustain=1.0, amp_release=2.5, rev_size=0.9, rev_damping=0.6, rev_mix=0.25)

CANDIDATES = bc.end(_s)

if __name__ == "__main__":
    bc.write("sad1", CANDIDATES)
