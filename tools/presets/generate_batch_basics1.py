#!/usr/bin/env python3
"""Stage D: Basics batch 1 (30) - plain, everyday sounds the library was missing.

From the diagnosis of 2026-11-12: the process rewarded unusual sounds, so the ordinary ones that every producer
reaches for first (a clean sub, a plain saw lead, a simple pad, a string section, a brass section, a synth piano)
were rejected as "too close to something". This batch is exempt from the novelty rule: each preset only has to be
clean, useful and not a duplicate of another basic. Simple recipes, few effects, sensible macros (macro 1 is the
Energy macro: drive + brightness, so even a basic can be pushed).

    python3 tools/presets/generate_batch_basics1.py [--trim report.json]
"""
import batch_common as bc

P, M = bc.P, bc.M
bc.gp.GROUP_TAGS.update({"basic": ["Basic"]})
_s = bc.begin()
B = "basic"
E = ("Energy", [("Dist Mix", 0.35), ("Cutoff", 0.25)])

# ============================================================================================ BASS
P(B, "Pure Sub", "Bass", "Clean sine sub with a soft click, sits under anything without colouring it.",
  M(E, ("Click", [("Noise Level", 0.15)]), ("Warmth", [("WT Pos A", 0.25)]), ("Glide", [("Pitch A", 0.02)])),
  mods=[("Mod Env", "Noise Level", 0.08), ("Velocity", "Level A", 0.15)], tags=["Sub", "Clean", "Sine"], mood="Medium",
  voice_mode="Mono", oscA_table="Basic Shapes", oscA_pos=0.0, oscA_level=0.95, menv_decay=0.006, flt_type="LP24",
  flt_cutoff=1200.0, amp_attack=0.002, amp_release=0.08, dist_type="Soft", dist_drive=0.3)
P(B, "Clean 808", "Bass", "Plain 808: a sine with a short pitch drop and a long tail, no distortion.",
  M(E, ("Punch", [("Pitch A", 0.03)]), ("Tail", [("Sub Level", 0.3)]), ("Glide", [("Detune", 0.1)])),
  mods=[("Velocity", "Level A", 0.15)], tags=["808", "Clean", "Long"], mood="Dark",
  voice_mode="Legato", glide=0.05, oscA_table="Basic Shapes", oscA_pos=0.0, oscA_level=0.95, penv_amount=12.0,
  penv_decay=0.05, flt_type="LP24", flt_cutoff=3000.0, amp_attack=0.0005, amp_decay=2.0, amp_sustain=0.0,
  amp_release=0.4, dist_type="Soft", dist_drive=0.3)
P(B, "Simple Saw Bass", "Bass", "Classic saw bass with a filter that opens on each note, for any groove.",
  M(E, ("Env", [("Cutoff", 0.3)]), ("Res", [("Resonance", 0.3)]), ("Sub", [("Sub Level", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Saw", "Analog", "Plain"], mood="Medium",
  voice_mode="Mono", oscA_table="Analog Saw", sub_level=0.3, flt_type="LP24", flt_cutoff=500.0, flt_res=0.2,
  flt_envamt=0.45, fenv_decay=0.25, fenv_sustain=0.15, amp_attack=0.001, amp_release=0.08)

# ============================================================================================ LEADS
P(B, "Plain Saw Lead", "Lead", "A single bright saw with a touch of glide, the lead every track starts from.",
  M(E, ("Tone", [("Cutoff", 0.3)]), ("Width", [("Detune", 0.3)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.2), ("Mod Wheel", "Pitch", 0.006)], tags=["Saw", "Mono", "Plain"], mood="Medium",
  voice_mode="Legato", glide=0.03, oscA_table="Analog Saw", oscA_voices=2, uni_detune=0.06, flt_type="LP24",
  flt_cutoff=6000.0, amp_attack=0.001, amp_release=0.12)
P(B, "Square Lead", "Lead", "Hollow square lead, clean and direct, for hooks and counter-melodies.",
  M(E, ("Tone", [("Cutoff", 0.3)]), ("Pulse", [("WT Pos A", 0.3)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.2), ("LFO 1", "Pitch", 0.002)], tags=["Square", "Hollow", "Plain"], mood="Medium",
  voice_mode="Legato", glide=0.02, oscA_table="Analog Square", lfo1_rate=5.5, flt_type="LP12", flt_cutoff=5000.0,
  amp_attack=0.001, amp_release=0.1, dly_time="1/8D", dly_feedback=0.25, dly_mix=0.1)
P(B, "Supersaw Lead", "Lead", "Wide seven-voice supersaw for anthems and big hooks.",
  M(E, ("Tone", [("Cutoff", 0.3)]), ("Width", [("Detune", 0.3)]), ("Space", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.2)], tags=["Supersaw", "Wide", "Anthem"], mood="Medium",
  oscA_table="Hyper Saw", oscA_pos=0.3, oscA_voices=7, uni_detune=0.3, uni_spread=1.0, flt_type="LP12",
  flt_cutoff=9000.0, amp_attack=0.002, amp_release=0.3, squash=0.3, rev_size=0.5, rev_mix=0.12)
P(B, "Pulse Lead", "Lead", "Pulse-width lead that slowly thins and thickens as you hold it.",
  M(E, ("Width", [("WT Pos A", 0.3)]), ("Tone", [("Cutoff", 0.3)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("LFO 1", "WT Pos A", 0.25), ("Velocity", "Cutoff", 0.2)], tags=["PWM", "Analog", "Plain"], mood="Medium",
  voice_mode="Legato", glide=0.04, oscA_table="PWM", oscA_pos=0.3, lfo1_rate=0.7, flt_type="LP24", flt_cutoff=4500.0,
  amp_attack=0.002, amp_release=0.15, mfx_type="Chorus", mfx_mix=0.2)
P(B, "Glide Sine Lead", "Lead", "Soft sine lead with a slow glide and a gentle vibrato on the mod wheel.",
  M(E, ("Breath", [("Noise Level", 0.1)]), ("Vibrato", [("Pitch", 0.01)]), ("Space", [("Reverb Mix", 0.25)])),
  mods=[("Mod Wheel", "Pitch", 0.008), ("LFO 1", "Pitch", 0.002)], tags=["Sine", "Smooth", "Glide"], mood="Soft",
  voice_mode="Legato", glide=0.12, oscA_table="Basic Shapes", oscA_pos=0.08, lfo1_rate=5.0, flt_type="LP12",
  flt_cutoff=4000.0, amp_attack=0.02, amp_release=0.3, dly_mode="PingPong", dly_time="1/4", dly_feedback=0.3,
  dly_mix=0.12, rev_size=0.5, rev_mix=0.15)

# ============================================================================================ PLUCKS
P(B, "Square Pluck", "Pluck", "Short square pluck with a quick filter snap, dry enough for fast melodies.",
  M(E, ("Snap", [("Cutoff", 0.3)]), ("Tail", [("Delay Mix", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.3)], tags=["Square", "Short", "Plain"], mood="Medium",
  oscA_table="Analog Square", flt_type="LP24", flt_cutoff=700.0, flt_envamt=0.5, fenv_decay=0.12, fenv_sustain=0.0,
  amp_attack=0.0005, amp_decay=0.3, amp_sustain=0.0, amp_release=0.2)
P(B, "Round Pluck", "Pluck", "Soft, round pluck with a warm tail, for chords and gentle melodies.",
  M(E, ("Tone", [("Cutoff", 0.3)]), ("Tail", [("Delay Mix", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Round", "Warm", "Plain"], mood="Soft",
  oscA_table="Basic Shapes", oscA_pos=0.4, oscB_table="Analog Saw", oscB_level=0.25, flt_type="LP12",
  flt_cutoff=1800.0, flt_envamt=0.3, fenv_decay=0.2, fenv_sustain=0.0, amp_attack=0.001, amp_decay=0.6,
  amp_sustain=0.0, amp_release=0.4, rev_size=0.45, rev_mix=0.15)

# ============================================================================================ KEYS
P(B, "Synth Piano", "Keys", "Clean, bright synth piano for chords in any style, with velocity on the tone.",
  M(E, ("Bright", [("Cutoff", 0.3)]), ("Body", [("WT Pos A", 0.25)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.35)], tags=["Piano", "Clean", "Plain"], mood="Medium",
  oscA_table="Hammer Piano", oscA_pos=0.2, flt_type="LP12", flt_cutoff=5000.0, amp_attack=0.001, amp_decay=2.5,
  amp_sustain=0.0, amp_release=0.4, rev_size=0.4, rev_mix=0.1)
P(B, "Classic EP", "Keys", "Bell-like electric piano with a soft tremolo, the everyday tine sound.",
  M(E, ("Bell", [("Warp A", 0.3)]), ("Trem", [("Level A", -0.2)]), ("Chorus", [("Mod FX Mix", 0.4)])),
  mods=[("Velocity", "Warp A", 0.3), ("LFO 1", "Pan A", 0.3)], tags=["Electric Piano", "Tremolo", "Plain"], mood="Soft",
  oscA_table="Basic Shapes", oscA_pos=0.0, oscA_warp="FM", oscA_warp_amt=0.15, oscB_table="Glass Harmonics",
  oscB_level=0.12, oscB_oct=1, lfo1_rate=4.0, flt_type="LP12", flt_cutoff=6000.0, amp_attack=0.001, amp_decay=2.2,
  amp_sustain=0.2, amp_release=0.35, mfx_type="Chorus", mfx_mix=0.15)
P(B, "Full Drawbar Organ", "Keys", "All-drawbars-out organ with a rotary wobble, straight from the stage.",
  M(E, ("Drawbar", [("WT Pos A", 0.3)]), ("Rotor", [("Mod FX Mix", 0.4)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("LFO 1", "Pan A", 0.4)], tags=["Organ", "Drawbar", "Plain"], mood="Medium",
  oscA_table="Drawbars", oscA_pos=0.8, lfo1_rate=6.0, amp_attack=0.002, amp_sustain=1.0, amp_release=0.06,
  mfx_type="Chorus", mfx_rate=5.5, mfx_depth=0.4, mfx_mix=0.3)
P(B, "Polysynth Chords", "Keys", "Plain two-saw polysynth for chords, the sound of a hundred records.",
  M(E, ("Tone", [("Cutoff", 0.3)]), ("Width", [("Detune", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Polysynth", "Chords", "Plain"], mood="Medium",
  oscA_table="Analog Saw", oscA_voices=2, uni_detune=0.1, oscB_table="Analog Square", oscB_level=0.3,
  flt_type="LP24", flt_cutoff=2500.0, flt_envamt=0.2, fenv_decay=0.5, fenv_sustain=0.4, amp_attack=0.003,
  amp_decay=1.0, amp_sustain=0.7, amp_release=0.35, mfx_type="Chorus", mfx_mix=0.2)

# ============================================================================================ PADS
P(B, "Warm Saw Pad", "Pad", "Basic warm pad from detuned saws, slow in and slow out.",
  M(E, ("Tone", [("Cutoff", 0.3)]), ("Width", [("Detune", 0.3)]), ("Space", [("Reverb Mix", 0.25)])),
  mods=[("LFO 1", "Cutoff", 0.05)], tags=["Saw", "Warm", "Plain"], mood="Soft",
  oscA_table="Analog Saw", oscA_voices=4, uni_detune=0.2, uni_spread=0.9, lfo1_rate=0.2, flt_type="LP24",
  flt_cutoff=1600.0, amp_attack=0.6, amp_sustain=1.0, amp_release=1.5, rev_size=0.6, rev_mix=0.18)
P(B, "Bright Poly Pad", "Pad", "Open, bright pad with a fast attack, for house chords and choruses.",
  M(E, ("Tone", [("Cutoff", 0.3)]), ("Width", [("Detune", 0.3)]), ("Pump", [("Level A", -0.2)])),
  mods=[("Velocity", "Cutoff", 0.15)], tags=["Bright", "Chords", "Plain"], mood="Medium",
  oscA_table="Hyper Saw", oscA_pos=0.2, oscA_voices=5, uni_detune=0.22, uni_spread=1.0, oscB_table="Analog Square",
  oscB_level=0.2, oscB_oct=1, flt_type="LP12", flt_cutoff=7000.0, amp_attack=0.03, amp_sustain=1.0,
  amp_release=0.8, squash=0.3, rev_size=0.5, rev_mix=0.12)
P(B, "House Pump Pad", "Pad", "Deep house chord pad pumping in quarter notes, ready for a four-on-the-floor kick.",
  M(E, ("Pump", [("Level A", -0.25)]), ("Tone", [("Cutoff", 0.3)]), ("Space", [("Reverb Mix", 0.25)])),
  mods=[("LFO 1", "Cutoff", 0.06)], tags=["Deep House", "Pump", "Chords"], mood="Medium",
  oscA_table="Analog Saw", oscA_voices=3, uni_detune=0.15, oscB_table="Drawbars", oscB_pos=0.4, oscB_level=0.3,
  lfo1_sync=True, lfo1_div="2/1", flt_type="LP24", flt_cutoff=2200.0, flt_res=0.2, amp_attack=0.01,
  amp_sustain=1.0, amp_release=0.4, pump_amount=0.7, rev_size=0.45, rev_mix=0.12)
P(B, "Choir Pad", "Pad", "Simple 'aah' choir pad, wide and soft, for hooks and intros.",
  M(E, ("Vowel", [("Formant", 0.3)]), ("Width", [("Detune", 0.3)]), ("Space", [("Reverb Mix", 0.25)])),
  mods=[("Mod Wheel", "Formant", 0.3)], tags=["Choir", "Vocal", "Plain"], mood="Soft",
  oscA_table="Choir", oscA_pos=0.4, oscA_voices=4, uni_detune=0.12, uni_spread=1.0, flt_type="LP12",
  flt_cutoff=5000.0, amp_attack=0.25, amp_sustain=1.0, amp_release=1.2, rev_size=0.65, rev_mix=0.2)
P(B, "Dark Pad", "Pad", "Low, dark pad with a closed filter, a bed for night-time beats.",
  M(E, ("Open", [("Cutoff", 0.35)]), ("Motion", [("WT Pos A", 0.3)]), ("Space", [("Reverb Mix", 0.25)])),
  mods=[("LFO 1", "WT Pos A", 0.15)], tags=["Dark", "Low", "Plain"], mood="Dark",
  oscA_table="Hollow", oscA_pos=0.3, oscA_voices=3, uni_detune=0.12, sub_level=0.2, lfo1_rate=0.15,
  flt_type="LP24", flt_cutoff=650.0, flt_res=0.2, amp_attack=0.8, amp_sustain=1.0, amp_release=2.0,
  rev_size=0.75, rev_damping=0.7, rev_mix=0.2)
P(B, "Glass Pad", "Pad", "Thin, glassy pad high above the mix, airy but not dull.",
  M(E, ("Air", [("Noise Level", 0.1)]), ("Shine", [("WT Pos A", 0.3)]), ("Space", [("Reverb Mix", 0.25)])),
  mods=[("LFO 1", "WT Pos A", 0.1)], tags=["Glass", "Airy", "Bright"], mood="Soft",
  oscA_table="Glass Harmonics", oscA_pos=0.5, oscA_voices=3, uni_detune=0.1, lfo1_rate=0.3, flt_type="HP",
  flt_cutoff=350.0, amp_attack=0.4, amp_sustain=1.0, amp_release=1.6, rev_size=0.7, rev_mix=0.22)
P(B, "Filter Sweep Pad", "Pad", "Saw pad whose filter slowly sweeps open and closed over two bars.",
  M(E, ("Sweep", [("Resonance", 0.3)]), ("Width", [("Detune", 0.3)]), ("Space", [("Reverb Mix", 0.25)])),
  mods=[("LFO 1", "Cutoff", 0.3)], tags=["Sweep", "Moving", "Plain"], mood="Medium",
  oscA_table="Saw Octaves", oscA_pos=0.3, oscA_voices=4, uni_detune=0.18, lfo1_shape="Triangle", lfo1_sync=True,
  lfo1_div="2/1", flt_type="LP24", flt_cutoff=1200.0, flt_res=0.35, amp_attack=0.3, amp_sustain=1.0,
  amp_release=1.0, rev_size=0.55, rev_mix=0.15)

# ============================================================================================ STRINGS
P(B, "String Ensemble", "Strings", "Full string section with a gentle attack, for chords and swells.",
  M(E, ("Bow", [("Cutoff", 0.3)]), ("Width", [("Detune", 0.3)]), ("Hall", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.2), ("LFO 1", "Pitch", 0.0015)], tags=["Strings", "Ensemble", "Plain"], mood="Medium",
  oscA_table="Strings", oscA_pos=0.4, oscA_voices=5, uni_detune=0.12, uni_spread=1.0, lfo1_rate=5.0,
  flt_type="LP12", flt_cutoff=6000.0, amp_attack=0.15, amp_sustain=1.0, amp_release=0.6, rev_size=0.6, rev_mix=0.18)
P(B, "Low String Section", "Strings", "Cellos and basses together, a dark low line for drama.",
  M(E, ("Bow", [("Cutoff", 0.3)]), ("Weight", [("Sub Level", 0.3)]), ("Hall", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.25), ("LFO 1", "Pitch", 0.0015)], tags=["Strings", "Cello", "Low"], mood="Dark",
  oscA_table="Strings", oscA_pos=0.25, oscA_oct=-1, oscA_voices=4, uni_detune=0.1, lfo1_rate=4.5, flt_type="LP24",
  flt_cutoff=2400.0, amp_attack=0.12, amp_sustain=1.0, amp_release=0.5, rev_size=0.6, rev_mix=0.15)
P(B, "Synth Strings", "Strings", "Bright, chorused synth strings with a quick attack, the classic disco sound.",
  M(E, ("Tone", [("Cutoff", 0.3)]), ("Chorus", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.2)], tags=["Synth Strings", "Chorus", "Bright"], mood="Medium",
  oscA_table="PWM Saw", oscA_pos=0.3, oscA_voices=4, uni_detune=0.2, flt_type="LP12", flt_cutoff=7000.0,
  amp_attack=0.04, amp_sustain=1.0, amp_release=0.4, mfx_type="Chorus", mfx_depth=0.7, mfx_mix=0.4, rev_size=0.5,
  rev_mix=0.12)

# ============================================================================================ BRASS
P(B, "Brass Section", "Brass", "Punchy brass section for stabs and fanfares, opening with velocity.",
  M(E, ("Blare", [("Cutoff", 0.3)]), ("Width", [("Detune", 0.3)]), ("Hall", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.35)], tags=["Brass", "Section", "Plain"], mood="Medium",
  oscA_table="FM Brass", oscA_pos=0.5, oscA_voices=3, uni_detune=0.1, flt_type="LP24", flt_cutoff=1500.0,
  flt_envamt=0.4, fenv_attack=0.04, fenv_decay=0.3, fenv_sustain=0.5, amp_attack=0.02, amp_sustain=0.9,
  amp_release=0.25, rev_size=0.55, rev_mix=0.15)
P(B, "Synth Brass", "Brass", "Saw synth brass with the filter swelling in, for big chords.",
  M(E, ("Swell", [("Cutoff", 0.3)]), ("Width", [("Detune", 0.3)]), ("Hall", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Synth Brass", "Saw", "Plain"], mood="Medium",
  oscA_table="Analog Saw", oscA_voices=3, uni_detune=0.12, flt_type="LP24", flt_cutoff=900.0, flt_envamt=0.45,
  fenv_attack=0.08, fenv_decay=0.6, fenv_sustain=0.5, amp_attack=0.01, amp_sustain=1.0, amp_release=0.3,
  squash=0.25, rev_size=0.5, rev_mix=0.12)
P(B, "Soft Horns", "Brass", "Mellow horn section for warm backing chords.",
  M(E, ("Tone", [("Cutoff", 0.3)]), ("Breath", [("Noise Level", 0.1)]), ("Hall", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.25), ("LFO 1", "Pitch", 0.0012)], tags=["Horns", "Mellow", "Plain"], mood="Soft",
  oscA_table="Brass", oscA_pos=0.3, oscA_voices=2, uni_detune=0.08, lfo1_rate=4.8, flt_type="LP12",
  flt_cutoff=1400.0, amp_attack=0.06, amp_sustain=1.0, amp_release=0.4, rev_size=0.6, rev_mix=0.18)

# ============================================================================================ BELL, ARP
P(B, "Simple Bell", "Bell", "Clear FM bell with a medium tail, for melodies that need to ring.",
  M(E, ("Metal", [("Warp A", 0.3)]), ("Tail", [("Reverb Mix", 0.3)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Velocity", "Warp A", 0.25)], tags=["Bell", "FM", "Plain"], mood="Medium",
  oscA_table="Basic Shapes", oscA_pos=0.0, oscA_warp="FM", oscA_warp_amt=0.3, oscB_table="Basic Shapes",
  oscB_level=0.2, oscB_oct=2, oscB_semi=7, flt_type="LP12", flt_cutoff=9000.0, amp_attack=0.0005, amp_decay=1.8,
  amp_sustain=0.0, amp_release=1.5, rev_size=0.55, rev_mix=0.15)
P(B, "Simple Up Arp", "Arp", "Plain saw arpeggio going up in sixteenths, ready to drop on any chord.",
  M(E, ("Tone", [("Cutoff", 0.3)]), ("Gate", [("Resonance", 0.3)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.2)], tags=["Arp", "Saw", "Plain"], mood="Medium",
  arp_on=True, arp_mode="Up", arp_rate="1/16", arp_octaves=2, arp_gate=0.5, oscA_table="Analog Saw",
  flt_type="LP24", flt_cutoff=1800.0, flt_envamt=0.35, fenv_decay=0.1, fenv_sustain=0.1, amp_attack=0.001,
  amp_decay=0.2, amp_sustain=0.3, amp_release=0.08, dly_time="1/8D", dly_feedback=0.3, dly_mix=0.12)

CANDIDATES = bc.end(_s)

if __name__ == "__main__":
    bc.write("basics1", CANDIDATES)
