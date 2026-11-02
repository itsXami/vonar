#!/usr/bin/env python3
"""Generates the VOLT factory presets (presets/*.json).

Every preset is written sparsely: only parameters that differ from the plugin defaults are stored.
Output gain trims measured by the offline renderer live in tools/presets/gain_trims.json and are applied
here, so `python3 tools/presets/generate_presets.py` always reproduces the committed files.

Usage:
    python3 tools/presets/generate_presets.py              # write presets/
    python3 tools/presets/generate_presets.py --trim report.json   # update trims from a render report, then write
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PRESET_DIR = os.path.join(ROOT, "presets")
TRIM_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gain_trims.json")
TARGET_LUFS = -15.0

TABLES = ["Basic Shapes", "Analog Saw", "Analog Square", "Hollow", "Hyper Saw", "Saw Octaves", "PWM", "PWM Saw",
          "Sync Saw", "Sync Square", "Drawbars", "Drive Organ", "Pipe Organ", "Vowels", "Choir", "Talk Box",
          "Formant Sweep", "Bell Metal", "Metal Comb", "Ring Mod", "FM Bass", "FM Bell", "FM Brass", "FM Digital",
          "Fold", "Crush", "Buzz", "Rasp", "Acid", "Brass", "Strings", "Sine Drive"]
SOURCES = ["LFO 1", "LFO 2", "Filter Env", "Velocity", "Mod Wheel", "Aftertouch", "Key Track",
           "Macro 1", "Macro 2", "Macro 3", "Macro 4"]
DESTS = ["WT Pos A", "WT Pos B", "Pitch", "Pitch A", "Pitch B", "Cutoff", "Resonance", "Filter Drive", "Formant",
         "Level A", "Level B", "Sub Level", "Noise Level", "Pan A", "Pan B", "Dist Drive", "Dist Mix", "Mod FX Mix",
         "Delay Mix", "Reverb Mix"]

# Plugin defaults (must match Source/Params.cpp); used to keep the JSON sparse.
DEFAULTS = {
    "voice_mode": "Poly", "glide": 0.0,
    "oscA_table": "Analog Saw", "oscA_pos": 0.0, "oscA_oct": 0, "oscA_semi": 0, "oscA_fine": 0.0, "oscA_level": 0.8,
    "oscA_pan": 0.0, "oscA_voices": 1,
    "oscB_table": "Basic Shapes", "oscB_pos": 0.0, "oscB_oct": 0, "oscB_semi": 0, "oscB_fine": 0.0, "oscB_level": 0.0,
    "oscB_pan": 0.0, "oscB_voices": 1,
    "uni_detune": 0.25, "uni_spread": 0.5, "sub_shape": "Sine", "sub_level": 0.0, "noise_level": 0.0,
    "flt_type": "LP24", "flt_cutoff": 20000.0, "flt_res": 0.1, "flt_drive": 0.0, "flt_keytrack": 0.0,
    "flt_envamt": 0.0, "flt_vowel": 0.0,
    "amp_attack": 0.002, "amp_decay": 0.3, "amp_sustain": 1.0, "amp_release": 0.15,
    "fenv_attack": 0.002, "fenv_decay": 0.4, "fenv_sustain": 0.5, "fenv_release": 0.3,
    "penv_amount": 0.0, "penv_decay": 0.12,
    "lfo1_shape": "Sine", "lfo1_sync": False, "lfo1_rate": 2.0, "lfo1_div": "1/4", "lfo1_depth": 1.0, "lfo1_retrig": False,
    "lfo2_shape": "Sine", "lfo2_sync": False, "lfo2_rate": 2.0, "lfo2_div": "1/4", "lfo2_depth": 1.0, "lfo2_retrig": False,
    "macro1": 0.0, "macro2": 0.0, "macro3": 0.0, "macro4": 0.0,
    "arp_on": False, "arp_mode": "Up", "arp_rate": "1/16", "arp_octaves": 1, "arp_gate": 0.5,
    "dist_type": "Soft", "dist_drive": 0.3, "dist_tone": 0.7, "dist_mix": 0.0,
    "mfx_type": "Chorus", "mfx_rate": 0.4, "mfx_depth": 0.5, "mfx_mix": 0.0,
    "pump_amount": 0.0, "pump_rate": "1/4",
    "dly_mode": "Stereo", "dly_time": "1/4", "dly_feedback": 0.35, "dly_mix": 0.0,
    "rev_size": 0.5, "rev_damping": 0.5, "rev_mix": 0.0,
    "squash": 0.0, "out_gain": 0.0,
}
for i in range(1, 9):
    DEFAULTS[f"mod{i}_src"] = "None"
    DEFAULTS[f"mod{i}_dst"] = "None"
    DEFAULTS[f"mod{i}_amt"] = 0.0

PRESETS = []
GROUP_TAGS = {
    "yeezus": ["Kanye West", "Yeezus", "Industrial"],
    "graduation": ["Kanye West", "Graduation", "Stadium"],
    "808s": ["Kanye West", "808s & Heartbreak", "Cold"],
    "mbdtf": ["Kanye West", "MBDTF", "Epic"],
    "donda": ["Kanye West", "Donda", "Gospel"],
    "homework": ["Daft Punk", "Homework", "Acid"],
    "discovery": ["Daft Punk", "Discovery", "French House"],
    "haa": ["Daft Punk", "Human After All", "Mechanical"],
    "tron": ["Daft Punk", "Tron: Legacy", "Cinematic"],
    "ram": ["Daft Punk", "Random Access Memories", "Analog"],
}


def P(group, name, category, desc, macros, mods=(), tags=(), **params):
    """macros: four (label, [(dest, amount), ...]) tuples. mods: extra (source, dest, amount) routings."""
    assert len(macros) == 4, name
    slots = []
    for i, (label, routes) in enumerate(macros):
        for dest, amt in routes:
            slots.append((f"Macro {i + 1}", dest, amt))
    slots.extend(mods)
    assert len(slots) <= 8, f"{name}: {len(slots)} modulation slots"
    for i, (src, dst, amt) in enumerate(slots):
        assert src in SOURCES and dst in DESTS, (name, src, dst)
        params[f"mod{i + 1}_src"] = src
        params[f"mod{i + 1}_dst"] = dst
        params[f"mod{i + 1}_amt"] = amt
    for k in ("oscA_table", "oscB_table"):
        if k in params:
            assert params[k] in TABLES, (name, params[k])
    for k in params:
        assert k in DEFAULTS, (name, k)
    PRESETS.append({
        "group": group, "name": name, "category": category,
        "tags": GROUP_TAGS[group] + list(tags), "description": desc,
        "macros": [m[0] for m in macros], "params": params,
    })


# =====================================================================================================
# Kanye West – Yeezus (24): distorted basses, industrial buzz and acid, screaming leads, sirens, rough 808s
# =====================================================================================================
G = "yeezus"
P(G, "Concrete Saw", "Bass", "Buzzing mono bass driven through hard clipping and a snarling ladder filter.",
  [("Grit", [("Dist Drive", 0.35)]), ("Snarl", [("Cutoff", 0.35)]), ("Sync", [("WT Pos B", 0.8)]), ("Crush", [("Resonance", 0.4)])],
  tags=["Distorted", "Aggressive"],
  voice_mode="Mono", oscA_table="Buzz", oscA_pos=0.55, oscA_oct=-1, oscB_table="Sync Saw", oscB_pos=0.2, oscB_level=0.5,
  oscB_oct=-1, sub_level=0.45, flt_type="Ladder", flt_cutoff=420.0, flt_res=0.45, flt_drive=0.5, flt_envamt=0.45,
  fenv_decay=0.28, fenv_sustain=0.2, amp_release=0.12, dist_type="Hard", dist_drive=0.55, dist_tone=0.6, dist_mix=1.0,
  squash=0.45)
P(G, "Furnace Sub", "Bass", "Saturated sub bass with a fast pitch drop and tube heat on top.",
  [("Heat", [("Dist Drive", 0.4)]), ("Body", [("Cutoff", 0.4)]), ("Growl", [("WT Pos A", 0.5)]), ("Click", [("Noise Level", 0.25)])],
  tags=["808", "Distorted"],
  voice_mode="Legato", glide=0.07, oscA_table="Sine Drive", oscA_pos=0.45, oscA_oct=-1, oscA_level=0.9,
  flt_type="LP24", flt_cutoff=1800.0, penv_amount=12.0, penv_decay=0.07, amp_decay=1.2, amp_sustain=0.6, amp_release=0.4,
  dist_type="Tube", dist_drive=0.6, dist_tone=0.45, dist_mix=0.8)
P(G, "Rivet Gun", "Bass", "Bit-crushed square bass with a metallic attack that rattles like machinery.",
  [("Bits", [("Dist Drive", 0.4)]), ("Bite", [("Cutoff", 0.4)]), ("Metal", [("WT Pos B", 0.7)]), ("Mix", [("Dist Mix", -0.5)])],
  tags=["Lo-Fi", "Aggressive"],
  voice_mode="Mono", oscA_table="Crush", oscA_pos=0.4, oscA_oct=-1, oscB_table="Metal Comb", oscB_pos=0.3, oscB_level=0.35,
  sub_level=0.4, flt_type="LP24", flt_cutoff=900.0, flt_res=0.3, flt_envamt=0.4, fenv_decay=0.15, fenv_sustain=0.15,
  dist_type="Bitcrush", dist_drive=0.45, dist_mix=0.85, squash=0.3)
P(G, "Acid Bath", "Bass", "Screaming acid line with a self-resonant ladder and a hard-driven filter stage.",
  [("Squelch", [("Resonance", 0.15)]), ("Open", [("Cutoff", 0.4)]), ("Dirt", [("Dist Drive", 0.4)]), ("Wobble", [("WT Pos A", 0.6)])],
  mods=[("Velocity", "Cutoff", 0.15)], tags=["Acid", "Aggressive"],
  voice_mode="Mono", glide=0.05, oscA_table="Acid", oscA_pos=0.25, oscA_oct=-1, flt_type="Ladder", flt_cutoff=300.0,
  flt_res=0.82, flt_drive=0.55, flt_envamt=0.6, fenv_decay=0.22, fenv_sustain=0.1, amp_release=0.1,
  dist_type="Soft", dist_drive=0.5, dist_mix=0.7)
P(G, "Static Throat", "Lead", "Fuzzy formant lead that growls through vowel shapes and folded distortion.",
  [("Vowel", [("Formant", 0.6)]), ("Fold", [("Dist Drive", 0.4)]), ("Scream", [("Cutoff", 0.4)]), ("Space", [("Reverb Mix", 0.3)])],
  mods=[("LFO 1", "Formant", 0.35)], tags=["Vocal", "Distorted"],
  voice_mode="Mono", glide=0.04, oscA_table="Buzz", oscA_pos=0.9, oscB_table="Talk Box", oscB_level=0.5, oscB_pos=0.4,
  flt_type="Formant", flt_cutoff=1100.0, flt_res=0.55, flt_vowel=0.2, lfo1_rate=1.5, lfo1_shape="Triangle",
  dist_type="Fold", dist_drive=0.35, dist_mix=0.6, rev_mix=0.12)
P(G, "Air Raid", "FX", "Wailing siren that sweeps a full octave with tube grit and a long hall.",
  [("Sweep", [("Pitch", 0.25)]), ("Grit", [("Dist Drive", 0.4)]), ("Hall", [("Reverb Mix", 0.3)]), ("Echo", [("Delay Mix", 0.35)])],
  mods=[("LFO 1", "Pitch", 0.5)], tags=["Siren"],
  voice_mode="Mono", oscA_table="Sine Drive", oscA_pos=0.6, oscA_level=0.75, lfo1_shape="Triangle", lfo1_rate=0.45,
  lfo1_retrig=True, flt_type="LP12", flt_cutoff=5000.0, amp_attack=0.08, amp_release=0.6,
  dist_type="Tube", dist_drive=0.45, dist_mix=0.7, rev_size=0.75, rev_mix=0.3)
P(G, "Alarm Pulse", "FX", "Two-tone square alarm that flips pitch on every quarter note.",
  [("Tone", [("Cutoff", 0.4)]), ("Grit", [("Dist Drive", 0.4)]), ("Width", [("Mod FX Mix", 0.5)]), ("Echo", [("Delay Mix", 0.4)])],
  mods=[("LFO 1", "Pitch", 0.125)], tags=["Siren"],
  voice_mode="Mono", oscA_table="Analog Square", oscA_pos=0.3, lfo1_shape="Square", lfo1_sync=True, lfo1_div="1/4",
  flt_type="LP24", flt_cutoff=3500.0, dist_type="Hard", dist_drive=0.35, dist_mix=0.6, dly_mode="PingPong",
  dly_time="1/8", dly_mix=0.15, amp_release=0.3)
P(G, "Chain Link Scream", "Lead", "Hard-synced lead that tears upward as the sync sweep opens.",
  [("Sync", [("WT Pos A", 0.6)]), ("Clip", [("Dist Drive", 0.4)]), ("Tone", [("Cutoff", 0.4)]), ("Slap", [("Delay Mix", 0.3)])],
  mods=[("Filter Env", "WT Pos A", 0.35), ("Mod Wheel", "Pitch", 0.02)], tags=["Distorted", "Aggressive"],
  voice_mode="Mono", glide=0.03, oscA_table="Sync Saw", oscA_pos=0.25, oscB_table="Analog Saw", oscB_level=0.4, oscB_fine=8.0,
  flt_type="LP24", flt_cutoff=6000.0, flt_res=0.2, fenv_decay=0.5, fenv_sustain=0.2,
  dist_type="Hard", dist_drive=0.45, dist_mix=0.75, squash=0.3, dly_time="1/8D", dly_mix=0.12)
P(G, "Steel Mill Drone", "Pad", "Metallic drone of ring-modulated tones and noise that slowly grinds and phases.",
  [("Grind", [("WT Pos A", 0.6)]), ("Metal", [("WT Pos B", 0.6)]), ("Noise", [("Noise Level", 0.3)]), ("Space", [("Reverb Mix", 0.3)])],
  mods=[("LFO 1", "Cutoff", 0.15), ("LFO 2", "WT Pos A", 0.25)], tags=["Dark", "Texture"],
  oscA_table="Ring Mod", oscA_pos=0.3, oscA_level=0.6, oscB_table="Metal Comb", oscB_pos=0.5, oscB_level=0.5, oscB_semi=-12,
  noise_level=0.05, flt_type="LP24", flt_cutoff=2400.0, flt_res=0.35, amp_attack=1.2, amp_release=2.0,
  lfo1_rate=0.12, lfo2_rate=0.07, lfo2_shape="Triangle", mfx_type="Phaser", mfx_rate=0.15, mfx_depth=0.8, mfx_mix=0.6,
  dist_type="Fold", dist_drive=0.25, dist_mix=0.35, rev_size=0.8, rev_mix=0.3)
P(G, "Overload 808", "Bass", "Long 808 that breaks up into a raspy, clipped tail.",
  [("Drive", [("Dist Drive", 0.4)]), ("Tone", [("Cutoff", 0.4)]), ("Rasp", [("WT Pos A", 0.5)]), ("Sub", [("Sub Level", 0.3)])],
  tags=["808", "Distorted"],
  voice_mode="Legato", glide=0.1, oscA_table="Sine Drive", oscA_pos=0.3, oscA_oct=-1, oscA_level=0.9, penv_amount=7.0,
  penv_decay=0.05, flt_type="LP24", flt_cutoff=2600.0, amp_decay=2.5, amp_sustain=0.0, amp_release=0.5,
  dist_type="Hard", dist_drive=0.6, dist_tone=0.5, dist_mix=0.75)
P(G, "Gutter Growl", "Bass", "FM bass that growls in eighth-note pulses under heavy saturation.",
  [("Growl", [("WT Pos A", 0.4)]), ("Speed", [("Cutoff", 0.3)]), ("Heat", [("Dist Drive", 0.4)]), ("Sub", [("Sub Level", 0.3)])],
  mods=[("LFO 1", "WT Pos A", 0.3)], tags=["Wobble"],
  voice_mode="Mono", oscA_table="FM Bass", oscA_pos=0.45, oscA_oct=-1, sub_level=0.35, lfo1_sync=True, lfo1_div="1/8",
  lfo1_shape="Triangle", flt_type="LP24", flt_cutoff=1400.0, flt_res=0.3, dist_type="Tube", dist_drive=0.55, dist_mix=0.8,
  squash=0.35)
P(G, "Shock Collar", "Bass", "Wavefolded bass with a bit-crushed bite that jumps out of the mix.",
  [("Fold", [("WT Pos A", 0.5)]), ("Crush", [("Dist Drive", 0.4)]), ("Bite", [("Cutoff", 0.4)]), ("Width", [("Pan B", 0.6)])],
  mods=[("Filter Env", "WT Pos A", 0.25)], tags=["Lo-Fi", "Aggressive"],
  voice_mode="Mono", oscA_table="Fold", oscA_pos=0.35, oscA_oct=-1, oscB_table="Analog Square",
  oscB_level=0.3, oscB_oct=-1, sub_level=0.3, flt_type="LP24", flt_cutoff=1200.0, flt_envamt=0.35, fenv_decay=0.18,
  fenv_sustain=0.1, dist_type="Bitcrush", dist_drive=0.35, dist_mix=0.55)
P(G, "Black Iron Lead", "Lead", "Wide stacked saw lead pushed into hard clipping for a brutal topline.",
  [("Width", [("Mod FX Mix", 0.4)]), ("Clip", [("Dist Drive", 0.4)]), ("Tone", [("Cutoff", 0.4)]), ("Hall", [("Reverb Mix", 0.25)])],
  tags=["Distorted", "Wide"],
  voice_mode="Mono", glide=0.02, oscA_table="Hyper Saw", oscA_pos=0.5, oscA_voices=5, uni_detune=0.45, uni_spread=0.8,
  oscB_table="Analog Saw", oscB_level=0.35, oscB_oct=-1, flt_type="LP24", flt_cutoff=5000.0, flt_res=0.15,
  dist_type="Hard", dist_drive=0.4, dist_mix=0.7, squash=0.35, rev_mix=0.1)
P(G, "Riot Horn", "Brass", "Blaring distorted brass stab with a nasal tube bite.",
  [("Blare", [("WT Pos A", 0.5)]), ("Bite", [("Dist Drive", 0.4)]), ("Open", [("Cutoff", 0.4)]), ("Room", [("Reverb Mix", 0.3)])],
  mods=[("Filter Env", "WT Pos A", 0.3)], tags=["Stab"],
  oscA_table="Brass", oscA_pos=0.6, oscA_voices=3, uni_detune=0.3, oscB_table="FM Brass", oscB_pos=0.5, oscB_level=0.35,
  flt_type="LP24", flt_cutoff=1800.0, flt_envamt=0.4, fenv_attack=0.02, fenv_decay=0.35, fenv_sustain=0.3,
  amp_attack=0.01, amp_release=0.25, dist_type="Tube", dist_drive=0.5, dist_mix=0.7, rev_mix=0.12)
P(G, "Feedback Choir", "Pad", "Dark choir that folds and flanges into a menacing wall of feedback.",
  [("Vowel", [("WT Pos A", 0.6)]), ("Fold", [("Dist Mix", 0.5)]), ("Flange", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("LFO 1", "Cutoff", 0.1)], tags=["Dark", "Choir"],
  oscA_table="Choir", oscA_pos=0.3, oscA_voices=4, uni_detune=0.35, oscB_table="Rasp", oscB_level=0.25, oscB_pos=0.5,
  flt_type="LP24", flt_cutoff=2200.0, amp_attack=0.8, amp_release=1.8, lfo1_rate=0.2, dist_type="Fold", dist_drive=0.3,
  dist_mix=0.3, mfx_type="Flanger", mfx_rate=0.1, mfx_depth=0.6, mfx_mix=0.35, rev_size=0.8, rev_mix=0.3)
P(G, "Sawblade Arp", "Arp", "Buzzing two-octave arpeggio that cuts like a grinder.",
  [("Edge", [("WT Pos A", 0.4)]), ("Grind", [("Dist Drive", 0.4)]), ("Tone", [("Cutoff", 0.4)]), ("Echo", [("Delay Mix", 0.3)])],
  mods=[("Filter Env", "Cutoff", 0.2)], tags=["Arp", "Distorted"],
  arp_on=True, arp_mode="UpDown", arp_rate="1/16", arp_octaves=2, arp_gate=0.45, oscA_table="Buzz", oscA_pos=0.4,
  flt_type="LP24", flt_cutoff=2500.0, flt_res=0.3, fenv_decay=0.15, fenv_sustain=0.0, amp_decay=0.2, amp_sustain=0.4,
  dist_type="Hard", dist_drive=0.35, dist_mix=0.6, dly_mode="PingPong", dly_time="1/8D", dly_feedback=0.3, dly_mix=0.15)
P(G, "Scrapyard Hit", "FX", "Clanging noise impact that drops in pitch and smashes into a dark room.",
  [("Pitch", [("Pitch", 0.2)]), ("Metal", [("WT Pos A", 0.6)]), ("Crush", [("Dist Drive", 0.4)]), ("Room", [("Reverb Mix", 0.3)])],
  tags=["Impact"],
  oscA_table="Metal Comb", oscA_pos=0.6, oscA_level=1.0, noise_level=0.6, penv_amount=-24.0, penv_decay=0.3,
  flt_type="LP24", flt_cutoff=2500.0, flt_res=0.3, flt_envamt=0.3, fenv_decay=0.3, fenv_sustain=0.0, amp_decay=1.4,
  amp_sustain=0.0,
  amp_release=0.4, dist_type="Bitcrush", dist_drive=0.4, dist_mix=0.6, rev_size=0.6, rev_damping=0.7, rev_mix=0.25)
P(G, "Klaxon Drop", "FX", "Distorted horn that dives two octaves like a warning call.",
  [("Dive", [("Pitch", -0.3)]), ("Grit", [("Dist Drive", 0.4)]), ("Tone", [("Cutoff", 0.4)]), ("Echo", [("Delay Mix", 0.3)])],
  tags=["Siren"],
  voice_mode="Mono", oscA_table="PWM Saw", oscA_pos=0.6, oscB_table="Analog Square", oscB_level=0.4, oscB_semi=7,
  penv_amount=-24.0, penv_decay=1.6, flt_type="LP24", flt_cutoff=3000.0, dist_type="Hard", dist_drive=0.45,
  dist_mix=0.65, amp_release=0.4, dly_time="1/8", dly_mix=0.1)
P(G, "Rust Bass", "Bass", "Pulse-width bass with a rusty tube edge and a quick filter pluck.",
  [("PWM", [("WT Pos A", 0.5)]), ("Rust", [("Dist Drive", 0.4)]), ("Pluck", [("Cutoff", 0.35)]), ("Sub", [("Sub Level", 0.3)])],
  mods=[("LFO 1", "WT Pos A", 0.2)], tags=["Distorted"],
  voice_mode="Mono", oscA_table="PWM", oscA_pos=0.4, oscA_oct=-1, sub_level=0.35, lfo1_rate=0.6, flt_type="Ladder",
  flt_cutoff=500.0, flt_res=0.35, flt_envamt=0.45, fenv_decay=0.2, fenv_sustain=0.15, dist_type="Tube", dist_drive=0.5,
  dist_mix=0.75)
P(G, "Kick Sub Smash", "Bass", "Punchy kick-like 808 with a steep pitch dive and clipped transient.",
  [("Punch", [("Pitch A", 0.05)]), ("Clip", [("Dist Drive", 0.4)]), ("Tone", [("Cutoff", 0.4)]), ("Tail", [("Sub Level", 0.3)])],
  tags=["808", "Punch"],
  voice_mode="Legato", oscA_table="Sine Drive", oscA_pos=0.2, oscA_oct=-1, oscA_level=0.9, penv_amount=36.0,
  penv_decay=0.035, flt_type="LP24", flt_cutoff=3000.0, amp_decay=1.4, amp_sustain=0.0, amp_release=0.3,
  dist_type="Hard", dist_drive=0.5, dist_mix=0.6)
P(G, "Panic Lead", "Lead", "Crushed square lead with a nervous fast vibrato.",
  [("Panic", [("Pitch", 0.01)]), ("Crush", [("Dist Drive", 0.4)]), ("Tone", [("Cutoff", 0.4)]), ("Echo", [("Delay Mix", 0.3)])],
  mods=[("LFO 1", "Pitch", 0.012)], tags=["Lo-Fi"],
  voice_mode="Mono", glide=0.03, oscA_table="Analog Square", oscA_pos=0.2, lfo1_rate=7.5, flt_type="LP12", flt_cutoff=4000.0,
  dist_type="Bitcrush", dist_drive=0.4, dist_mix=0.7, dly_mode="PingPong", dly_time="1/8", dly_mix=0.12)
P(G, "Pressure Drone", "Pad", "Folded, raspy drone whose filter breathes in slow waves.",
  [("Fold", [("WT Pos A", 0.5)]), ("Rasp", [("WT Pos B", 0.5)]), ("Breath", [("Cutoff", 0.35)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("LFO 1", "Cutoff", 0.2)], tags=["Dark", "Texture"],
  oscA_table="Fold", oscA_pos=0.3, oscA_level=0.6, oscB_table="Rasp", oscB_pos=0.4, oscB_level=0.45, oscB_oct=-1,
  flt_type="LP24", flt_cutoff=1500.0, flt_res=0.3, amp_attack=1.5, amp_release=2.0, lfo1_rate=0.15,
  rev_size=0.8, rev_mix=0.3, squash=0.3)
P(G, "Breaker Keys", "Keys", "Harsh digital FM stab with a bit-crushed decay.",
  [("Index", [("WT Pos A", 0.5)]), ("Crush", [("Dist Mix", 0.5)]), ("Tone", [("Cutoff", 0.4)]), ("Room", [("Reverb Mix", 0.3)])],
  mods=[("Velocity", "WT Pos A", 0.3)], tags=["Stab", "Digital"],
  oscA_table="FM Digital", oscA_pos=0.4, oscB_table="Bell Metal", oscB_level=0.3, flt_type="LP24", flt_cutoff=6000.0,
  amp_decay=1.0, amp_sustain=0.1, amp_release=0.3, squash=0.3, dist_type="Bitcrush", dist_drive=0.3, dist_mix=0.35, rev_mix=0.12)
P(G, "Smoke Signal", "FX", "Random formant chatter bouncing between ping-pong echoes.",
  [("Chatter", [("WT Pos A", 0.5)]), ("Grit", [("Dist Mix", 0.5)]), ("Echo", [("Delay Mix", 0.3)]), ("Space", [("Reverb Mix", 0.3)])],
  mods=[("LFO 1", "WT Pos A", 0.5), ("LFO 1", "Formant", 0.4)], tags=["Texture", "Vocal"],
  oscA_table="Formant Sweep", oscA_pos=0.4, flt_type="Formant", flt_cutoff=1000.0, flt_res=0.5, lfo1_shape="S&H",
  lfo1_sync=True, lfo1_div="1/16", dist_type="Soft", dist_drive=0.4, dist_mix=0.3, dly_mode="PingPong", dly_time="1/8D",
  dly_feedback=0.45, dly_mix=0.25, rev_mix=0.15, amp_release=0.5)

# =====================================================================================================
# Kanye West – Graduation (10): stadium supersaws and shiny leads
# =====================================================================================================
G = "graduation"
P(G, "Arena Saw Stack", "Lead", "Huge detuned supersaw lead with octave layer, chorus and a stadium hall.",
  [("Width", [("Mod FX Mix", 0.4)]), ("Shine", [("Cutoff", 0.4)]), ("Octave", [("Level B", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("Mod Wheel", "Pitch", 0.01), ("LFO 1", "Pitch", 0.004)], tags=["Supersaw", "Bright"],
  oscA_table="Hyper Saw", oscA_pos=0.4, oscA_voices=7, uni_detune=0.45, uni_spread=0.9, oscB_table="Saw Octaves",
  oscB_pos=0.3, oscB_oct=1, oscB_voices=5, oscB_level=0.35, flt_type="LP24", flt_cutoff=6500.0, amp_release=0.4,
  lfo1_rate=5.0, mfx_type="Chorus", mfx_mix=0.3, dly_time="1/8D", dly_mix=0.15, rev_size=0.7, rev_mix=0.25)
P(G, "Varsity Stabs", "Keys", "Bright supersaw chord stab with a short pluck and stereo delay.",
  [("Pluck", [("Cutoff", 0.35)]), ("Width", [("Mod FX Mix", 0.4)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("Velocity", "Cutoff", 0.15)], tags=["Supersaw", "Stab"],
  oscA_table="Hyper Saw", oscA_pos=0.35, oscA_voices=6, uni_detune=0.4, uni_spread=0.85, flt_type="LP24",
  flt_cutoff=1800.0, flt_envamt=0.4, fenv_decay=0.35, fenv_sustain=0.1, amp_decay=0.6, amp_sustain=0.25,
  amp_release=0.35, dly_mode="PingPong", dly_time="1/8D", dly_mix=0.18, rev_mix=0.2)
P(G, "Neon Anthem", "Lead", "Bright analog saw and pulse lead with glide and mod-wheel vibrato.",
  [("Bright", [("Cutoff", 0.4)]), ("Pulse", [("WT Pos B", 0.5)]), ("Vibrato", [("Pitch", 0.01)]), ("Echo", [("Delay Mix", 0.3)])],
  mods=[("Mod Wheel", "Pitch", 0.012)], tags=["Bright"],
  voice_mode="Legato", glide=0.06, oscA_table="Analog Saw", oscB_table="PWM", oscB_pos=0.3, oscB_level=0.5, oscB_fine=6.0,
  flt_type="LP24", flt_cutoff=4500.0, flt_res=0.2, flt_envamt=0.2, amp_release=0.3, dly_time="1/4", dly_mix=0.15,
  rev_mix=0.15)
P(G, "Gloss Pluck", "Keys", "Glassy FM pluck layered with a soft triangle for shiny chords.",
  [("Gloss", [("WT Pos A", 0.4)]), ("Body", [("Level B", 0.4)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("Velocity", "WT Pos A", 0.25)], tags=["Pluck", "Bright"],
  oscA_table="FM Bell", oscA_pos=0.35, oscB_table="Basic Shapes", oscB_pos=0.33, oscB_level=0.4, flt_type="LP12",
  flt_cutoff=9000.0, amp_decay=1.4, amp_sustain=0.1, amp_release=0.5, dly_mode="PingPong", dly_time="1/8D",
  dly_mix=0.18, rev_mix=0.2, squash=0.2)
P(G, "Skyline Arp", "Arp", "Shimmering supersaw arpeggio rising over two octaves.",
  [("Shine", [("Cutoff", 0.4)]), ("Width", [("Mod FX Mix", 0.4)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("Filter Env", "Cutoff", 0.15)], tags=["Supersaw", "Arp"],
  arp_on=True, arp_mode="Up", arp_rate="1/16", arp_octaves=2, arp_gate=0.6, oscA_table="Hyper Saw", oscA_pos=0.3,
  oscA_voices=5, uni_detune=0.35, uni_spread=0.8, flt_type="LP24", flt_cutoff=3500.0, fenv_decay=0.2, fenv_sustain=0.2,
  amp_release=0.2, dly_mode="PingPong", dly_time="1/8D", dly_mix=0.2, rev_mix=0.2)
P(G, "Victory Brass", "Brass", "Bold synth brass section with a swelling filter and warm unison.",
  [("Swell", [("Cutoff", 0.35)]), ("Brass", [("WT Pos A", 0.5)]), ("Width", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("Filter Env", "WT Pos A", 0.25), ("Velocity", "Cutoff", 0.12)], tags=["Brass", "Bright"],
  oscA_table="Brass", oscA_pos=0.45, oscA_voices=3, uni_detune=0.3, oscB_table="Analog Saw", oscB_level=0.35,
  oscB_fine=-7.0, flt_type="LP24", flt_cutoff=1400.0, flt_envamt=0.35, fenv_attack=0.08, fenv_decay=0.6, fenv_sustain=0.5,
  amp_attack=0.03, amp_release=0.35, rev_mix=0.2)
P(G, "Shine Lead", "Lead", "Synced square lead with a moving sweep that sparkles on top of a mix.",
  [("Sync", [("WT Pos A", 0.5)]), ("Sweep", [("Cutoff", 0.35)]), ("Width", [("Mod FX Mix", 0.4)]), ("Echo", [("Delay Mix", 0.3)])],
  mods=[("LFO 1", "WT Pos A", 0.2)], tags=["Bright"],
  voice_mode="Mono", glide=0.04, oscA_table="Sync Square", oscA_pos=0.3, lfo1_rate=0.8, lfo1_shape="Triangle",
  flt_type="LP24", flt_cutoff=7000.0, mfx_type="Chorus", mfx_mix=0.2, dly_time="1/8D", dly_mix=0.15, rev_mix=0.15)
P(G, "Campus Pad", "Pad", "Warm string and supersaw blend that swells in slowly.",
  [("Air", [("Cutoff", 0.35)]), ("Strings", [("WT Pos A", 0.5)]), ("Width", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("LFO 1", "Cutoff", 0.06)], tags=["Supersaw", "Warm"],
  oscA_table="Strings", oscA_pos=0.5, oscA_voices=4, uni_detune=0.35, oscB_table="Hyper Saw", oscB_pos=0.2,
  oscB_level=0.35, oscB_voices=4, flt_type="LP24", flt_cutoff=3000.0, amp_attack=0.6, amp_release=1.5, lfo1_rate=0.25,
  mfx_mix=0.3, rev_size=0.7, rev_mix=0.25)
P(G, "Big Room Saw Bass", "Bass", "Stacked saw bass with a solid sub that fills a stadium.",
  [("Bright", [("Cutoff", 0.4)]), ("Stack", [("WT Pos A", 0.5)]), ("Sub", [("Sub Level", 0.3)]), ("Drive", [("Filter Drive", 0.4)])],
  mods=[("Filter Env", "Cutoff", 0.1)], tags=["Supersaw"],
  voice_mode="Mono", oscA_table="Hyper Saw", oscA_pos=0.25, oscA_oct=-1, oscA_voices=3, uni_detune=0.2, sub_level=0.45,
  flt_type="LP24", flt_cutoff=800.0, flt_res=0.15, flt_envamt=0.25, fenv_decay=0.3, fenv_sustain=0.4, amp_release=0.15)
P(G, "Synth Choir Lift", "Pad", "Airy synthetic choir layered with saws for uplifting chords.",
  [("Vowel", [("WT Pos A", 0.5)]), ("Saw", [("Level B", 0.4)]), ("Air", [("Cutoff", 0.35)]), ("Hall", [("Reverb Mix", 0.3)])],
  tags=["Choir", "Bright"],
  oscA_table="Choir", oscA_pos=0.6, oscA_voices=4, uni_detune=0.3, oscB_table="Hyper Saw", oscB_level=0.25, oscB_voices=4,
  oscB_oct=1, flt_type="LP24", flt_cutoff=5000.0, amp_attack=0.35, amp_release=1.2, mfx_mix=0.35, rev_size=0.75,
  rev_mix=0.28)

# =====================================================================================================
# Kanye West – 808s & Heartbreak (10): cold pads, synthetic pseudo-vocals, long gliding 808s
# =====================================================================================================
G = "808s"
P(G, "Glass Heart Pad", "Pad", "Cold, hollow pad with a slow bloom and a very wide hall.",
  [("Frost", [("Cutoff", 0.35)]), ("Breath", [("Noise Level", 0.2)]), ("Width", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("LFO 1", "WT Pos A", 0.15)], tags=["Pad", "Minimal"],
  oscA_table="Hollow", oscA_pos=0.4, oscA_voices=3, uni_detune=0.2, oscB_table="Choir", oscB_pos=0.2, oscB_level=0.3,
  flt_type="LP12", flt_cutoff=2200.0, amp_attack=1.0, amp_release=2.2, lfo1_rate=0.1, mfx_mix=0.3, rev_size=0.85,
  rev_damping=0.6, rev_mix=0.32)
P(G, "Frozen Voice Box", "Lead", "Synthetic vocal lead that glides between vowels like a pitch-corrected singer.",
  [("Vowel", [("Formant", 0.5)]), ("Mouth", [("WT Pos A", 0.5)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("LFO 1", "Formant", 0.2), ("Mod Wheel", "Pitch", 0.01)], tags=["Vocal", "Glide"],
  voice_mode="Legato", glide=0.09, oscA_table="Talk Box", oscA_pos=0.4, flt_type="Formant", flt_cutoff=1000.0, flt_res=0.45,
  flt_vowel=0.25, lfo1_rate=0.7, amp_release=0.4, dly_mode="PingPong", dly_time="1/4", dly_mix=0.15, rev_mix=0.2)
P(G, "Long Glide 808", "Bass", "Deep sustained 808 with a long tail and portamento between notes.",
  [("Drive", [("Dist Drive", 0.35)]), ("Tone", [("Cutoff", 0.4)]), ("Knock", [("Pitch A", 0.04)]), ("Sub", [("Sub Level", 0.3)])],
  tags=["808", "Glide"],
  voice_mode="Legato", glide=0.22, oscA_table="Sine Drive", oscA_pos=0.15, oscA_oct=-1, oscA_level=0.9, penv_amount=7.0,
  penv_decay=0.06, flt_type="LP24", flt_cutoff=1500.0, amp_decay=3.0, amp_sustain=0.5, amp_release=1.0,
  dist_type="Tube", dist_drive=0.25, dist_mix=0.35)
P(G, "Winter Choir", "Pad", "Breathy synthetic choir drifting through vowels in the cold.",
  [("Vowel", [("Formant", 0.5)]), ("Air", [("Noise Level", 0.15)]), ("Width", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("LFO 1", "Formant", 0.25), ("LFO 2", "WT Pos A", 0.2)], tags=["Choir", "Vocal"],
  oscA_table="Choir", oscA_pos=0.4, oscA_voices=4, uni_detune=0.3, flt_type="Formant", flt_cutoff=1000.0, flt_res=0.3,
  flt_vowel=0.6, amp_attack=0.8, amp_release=2.0, lfo1_rate=0.12, lfo2_rate=0.08, mfx_mix=0.3, rev_size=0.85,
  rev_mix=0.3)
P(G, "Cold Bell Keys", "Keys", "Clear FM bell keys with a frosty decay and long reverb.",
  [("Ring", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.4)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("Velocity", "WT Pos A", 0.3)], tags=["Bell", "Minimal"],
  oscA_table="FM Bell", oscA_pos=0.3, oscB_table="Basic Shapes", oscB_level=0.25, flt_type="LP12", flt_cutoff=7000.0,
  amp_decay=1.6, amp_sustain=0.0, amp_release=1.0, dly_time="1/4D", dly_mix=0.15, rev_size=0.8, rev_mix=0.25)
P(G, "Lonely Sine Lead", "Lead", "Soft sine lead with delayed vibrato and ping-pong echoes.",
  [("Shape", [("WT Pos A", 0.4)]), ("Vibrato", [("Pitch", 0.01)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("LFO 1", "Pitch", 0.008)], tags=["Minimal", "Soft"],
  voice_mode="Legato", glide=0.08, oscA_table="Basic Shapes", oscA_pos=0.12, lfo1_rate=5.0, amp_attack=0.02,
  amp_release=0.5, dly_mode="PingPong", dly_time="1/4", dly_feedback=0.4, dly_mix=0.2, rev_mix=0.2)
P(G, "Tom Drop 808", "Bass", "Tom-like 808 with a pronounced pitch drop and a short, round tail.",
  [("Drop", [("Pitch A", 0.04)]), ("Drive", [("Dist Drive", 0.35)]), ("Tone", [("Cutoff", 0.4)]), ("Room", [("Reverb Mix", 0.3)])],
  tags=["808"],
  voice_mode="Legato", glide=0.05, oscA_table="Sine Drive", oscA_pos=0.1, oscA_oct=-1, oscA_level=0.9, penv_amount=19.0,
  penv_decay=0.12, flt_type="LP24", flt_cutoff=1200.0, amp_decay=0.9, amp_sustain=0.0, amp_release=0.3,
  dist_type="Tube", dist_drive=0.25, dist_mix=0.3)
P(G, "Synthetic Sigh", "Lead", "Vowel-shaped lead that sighs and bends like a vocoder.",
  [("Vowel", [("WT Pos A", 0.6)]), ("Bend", [("Pitch", 0.02)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("LFO 1", "WT Pos A", 0.25), ("Mod Wheel", "Pitch", 0.01)], tags=["Vocal"],
  voice_mode="Legato", glide=0.12, oscA_table="Vowels", oscA_pos=0.3, oscA_voices=2, uni_detune=0.15, lfo1_rate=0.5,
  flt_type="LP24", flt_cutoff=4000.0, amp_attack=0.05, amp_release=0.6, dly_time="1/4", dly_mix=0.15, rev_mix=0.22)
P(G, "Grey Sky Strings", "Pad", "Muted synthetic strings with a slow attack and melancholic shimmer.",
  [("Air", [("Cutoff", 0.35)]), ("Ensemble", [("Mod FX Mix", 0.4)]), ("Bow", [("WT Pos A", 0.5)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("LFO 1", "Pitch", 0.002)], tags=["Strings", "Minimal"],
  oscA_table="Strings", oscA_pos=0.35, oscA_voices=4, uni_detune=0.3, flt_type="LP12", flt_cutoff=2600.0,
  amp_attack=0.7, amp_release=1.6, lfo1_rate=4.5, mfx_mix=0.35, rev_size=0.75, rev_mix=0.28)
P(G, "Tin Croon", "Lead", "Nasal, robotic-sounding sung tone with stepped vowel changes.",
  [("Vowel", [("Formant", 0.5)]), ("Steps", [("WT Pos A", 0.5)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("LFO 1", "Formant", 0.3)], tags=["Vocal"],
  voice_mode="Mono", glide=0.05, oscA_table="Vowels", oscA_pos=0.5, oscB_table="PWM", oscB_level=0.3, oscB_pos=0.6,
  flt_type="Formant", flt_cutoff=1100.0, flt_res=0.4, lfo1_shape="S&H", lfo1_sync=True, lfo1_div="1/8",
  amp_release=0.3, dly_time="1/8D", dly_mix=0.15, rev_mix=0.18)

# =====================================================================================================
# Kanye West – MBDTF (10): dramatic brass, dark synth strings, epic basses
# =====================================================================================================
G = "mbdtf"
P(G, "Throne Brass", "Brass", "Majestic synth brass that swells with tube warmth and a long hall.",
  [("Swell", [("Cutoff", 0.35)]), ("Blare", [("WT Pos A", 0.5)]), ("Heat", [("Dist Mix", 0.5)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("Filter Env", "WT Pos A", 0.3), ("Velocity", "Cutoff", 0.12)], tags=["Brass", "Dramatic"],
  oscA_table="Brass", oscA_pos=0.5, oscA_voices=4, uni_detune=0.3, oscB_table="Saw Octaves", oscB_level=0.3,
  oscB_oct=-1, flt_type="LP24", flt_cutoff=1200.0, flt_envamt=0.4, fenv_attack=0.15, fenv_decay=0.8, fenv_sustain=0.6,
  amp_attack=0.06, amp_release=0.6, dist_type="Tube", dist_drive=0.3, dist_mix=0.25, rev_size=0.8, rev_mix=0.25)
P(G, "Velvet Doom Strings", "Pad", "Dark synthetic strings in low register with slow motion and drama.",
  [("Bow", [("WT Pos A", 0.5)]), ("Dark", [("Cutoff", -0.3)]), ("Ensemble", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("LFO 1", "Cutoff", 0.08)], tags=["Strings", "Dark"],
  oscA_table="Strings", oscA_pos=0.6, oscA_voices=5, uni_detune=0.35, oscB_table="Analog Saw", oscB_oct=-1,
  oscB_level=0.3, flt_type="LP24", flt_cutoff=1800.0, amp_attack=0.9, amp_release=1.8, lfo1_rate=0.18, mfx_mix=0.35,
  rev_size=0.8, rev_mix=0.3)
P(G, "Cathedral Low End", "Bass", "Enormous saw and sub bass with a slow-opening filter for epic drops.",
  [("Open", [("Cutoff", 0.4)]), ("Drive", [("Filter Drive", 0.4)]), ("Sub", [("Sub Level", 0.3)]), ("Hall", [("Reverb Mix", 0.2)])],
  mods=[("Filter Env", "Cutoff", 0.1)], tags=["Epic"],
  voice_mode="Mono", oscA_table="Analog Saw", oscA_oct=-1, oscA_voices=3, uni_detune=0.2, oscB_table="Analog Square",
  oscB_oct=-2, oscB_level=0.35, sub_level=0.4, flt_type="LP24", flt_cutoff=380.0, flt_res=0.2, flt_envamt=0.3,
  fenv_attack=0.3, fenv_decay=1.2, fenv_sustain=0.5, amp_release=0.3)
P(G, "Gilded Horns", "Brass", "Punchy FM horn stab with a bright, golden edge.",
  [("Gold", [("WT Pos A", 0.4)]), ("Bite", [("Cutoff", 0.35)]), ("Width", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("Velocity", "WT Pos A", 0.2), ("Filter Env", "Cutoff", 0.15)], tags=["Brass", "Stab"],
  oscA_table="FM Brass", oscA_pos=0.45, oscA_voices=2, uni_detune=0.2, oscB_table="Brass", oscB_pos=0.7, oscB_level=0.4,
  flt_type="LP24", flt_cutoff=2500.0, fenv_decay=0.3, fenv_sustain=0.4, amp_attack=0.01, amp_decay=0.5,
  amp_sustain=0.5, amp_release=0.3, rev_mix=0.2)
P(G, "Opera Synth Lead", "Lead", "Theatrical vowel lead with wide vibrato that sings over strings.",
  [("Vowel", [("WT Pos A", 0.5)]), ("Vibrato", [("Pitch", 0.015)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("LFO 1", "Pitch", 0.01), ("Mod Wheel", "Pitch", 0.01)], tags=["Vocal", "Dramatic"],
  voice_mode="Legato", glide=0.07, oscA_table="Vowels", oscA_pos=0.2, oscB_table="Analog Saw", oscB_level=0.3,
  lfo1_rate=5.5, flt_type="LP24", flt_cutoff=5000.0, amp_attack=0.04, amp_release=0.6, dly_time="1/4", dly_mix=0.12,
  rev_size=0.8, rev_mix=0.25)
P(G, "Dark Orchestra Hit", "FX", "Orchestral brass and string hit with noise air and a huge tail.",
  [("Brass", [("WT Pos A", 0.5)]), ("Tone", [("Cutoff", 0.4)]), ("Air", [("Noise Level", 0.2)]), ("Hall", [("Reverb Mix", 0.3)])],
  tags=["Impact", "Dramatic"],
  oscA_table="Brass", oscA_pos=0.7, oscA_voices=3, oscB_table="Strings", oscB_level=0.45, oscB_oct=-1, noise_level=0.08,
  flt_type="LP24", flt_cutoff=3000.0, flt_envamt=0.3, fenv_decay=0.4, fenv_sustain=0.0, amp_decay=1.2, amp_sustain=0.0,
  amp_release=0.8, rev_size=0.85, rev_mix=0.3)
P(G, "Grand Synth Keys", "Keys", "Piano-like synth keys mixing a soft bell attack and a warm square body.",
  [("Attack", [("WT Pos A", 0.4)]), ("Body", [("Level B", 0.3)]), ("Tone", [("Cutoff", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("Velocity", "Cutoff", 0.25), ("Key Track", "Cutoff", 0.15)], tags=["Keys", "Warm"],
  oscA_table="FM Bell", oscA_pos=0.2, oscB_table="Analog Square", oscB_pos=0.5, oscB_level=0.45, flt_type="LP12",
  flt_cutoff=3500.0, flt_envamt=0.25, fenv_decay=0.9, fenv_sustain=0.0, amp_decay=2.5, amp_sustain=0.0,
  amp_release=0.6, rev_mix=0.2)
P(G, "Velvet Rope Bass", "Bass", "Smooth FM bass that slides between notes with a rich low mid.",
  [("Weight", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.4)]), ("Drive", [("Filter Drive", 0.4)]), ("Sub", [("Sub Level", 0.3)])],
  mods=[("Velocity", "WT Pos A", 0.2)], tags=["Glide"],
  voice_mode="Legato", glide=0.08, oscA_table="FM Bass", oscA_pos=0.3, oscA_oct=-1, sub_level=0.3, flt_type="LP24",
  flt_cutoff=1500.0, amp_release=0.2)
P(G, "Midnight Cellos", "Pad", "Low synthetic cello section with a slow bow and dark tone.",
  [("Bow", [("WT Pos A", 0.5)]), ("Tone", [("Cutoff", 0.35)]), ("Ensemble", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("LFO 1", "Pitch", 0.002)], tags=["Strings", "Dark"],
  oscA_table="Strings", oscA_pos=0.4, oscA_oct=-1, oscA_voices=3, uni_detune=0.25, flt_type="LP24", flt_cutoff=1400.0,
  flt_res=0.15, amp_attack=0.5, amp_release=1.4, lfo1_rate=5.0, mfx_mix=0.3, rev_size=0.75, rev_mix=0.25)
P(G, "Fanfare Swell", "Brass", "Massive octave-stacked brass swell for cinematic climaxes.",
  [("Swell", [("Cutoff", 0.35)]), ("Octave", [("WT Pos A", 0.5)]), ("Width", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("Filter Env", "Cutoff", 0.15)], tags=["Brass", "Epic"],
  oscA_table="Saw Octaves", oscA_pos=0.6, oscA_voices=4, uni_detune=0.3, oscB_table="Brass", oscB_level=0.35,
  flt_type="LP24", flt_cutoff=900.0, flt_envamt=0.45, fenv_attack=0.9, fenv_decay=1.5, fenv_sustain=0.7,
  amp_attack=0.4, amp_release=0.9, rev_size=0.8, rev_mix=0.28)

# =====================================================================================================
# Kanye West – Gospel / Donda (6): organs, choral pads, powerful chords
# =====================================================================================================
G = "donda"
P(G, "Sunday Drawbars", "Keys", "Classic drawbar organ with a gentle rotary-style chorus.",
  [("Drawbars", [("WT Pos A", 0.5)]), ("Rotor", [("Mod FX Mix", 0.4)]), ("Drive", [("Dist Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])],
  tags=["Organ"],
  oscA_table="Drawbars", oscA_pos=0.25, oscA_oct=1, flt_type="LP12", flt_cutoff=9000.0, amp_attack=0.004,
  amp_release=0.08, mfx_type="Chorus", mfx_rate=0.8, mfx_depth=0.6, mfx_mix=0.35, dist_type="Tube", dist_drive=0.2,
  dist_mix=0.2, rev_mix=0.15)
P(G, "Revival Organ", "Keys", "Overdriven church organ with a swirling phaser and lots of soul.",
  [("Drawbars", [("WT Pos A", 0.5)]), ("Swirl", [("Mod FX Mix", 0.4)]), ("Grit", [("Dist Drive", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])],
  tags=["Organ", "Distorted"],
  oscA_table="Drive Organ", oscA_pos=0.5, oscA_oct=1, flt_type="LP12", flt_cutoff=7000.0, amp_attack=0.004,
  amp_release=0.1, mfx_type="Phaser", mfx_rate=0.6, mfx_depth=0.5, mfx_mix=0.35, dist_type="Tube", dist_drive=0.35,
  dist_mix=0.5, rev_mix=0.18)
P(G, "Stadium Choir", "Pad", "Massive choir pad that rises slowly into a huge hall.",
  [("Vowel", [("WT Pos A", 0.5)]), ("Choir", [("Level B", 0.3)]), ("Air", [("Cutoff", 0.35)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("LFO 1", "WT Pos A", 0.15)], tags=["Choir", "Epic"],
  oscA_table="Choir", oscA_pos=0.7, oscA_voices=6, uni_detune=0.35, uni_spread=0.9, oscB_table="Vowels", oscB_pos=0.1,
  oscB_level=0.3, oscB_voices=3, flt_type="LP24", flt_cutoff=4500.0, amp_attack=0.9, amp_release=2.0, lfo1_rate=0.15,
  mfx_mix=0.3, rev_size=0.85, rev_mix=0.3)
P(G, "Pulpit Chords", "Pad", "Huge organ-and-saw chord bed that feels like a full congregation.",
  [("Organ", [("Level B", 0.4)]), ("Bright", [("Cutoff", 0.4)]), ("Width", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])],
  tags=["Organ", "Epic"],
  oscA_table="Analog Saw", oscA_voices=4, uni_detune=0.3, oscB_table="Drawbars", oscB_pos=0.6, oscB_oct=1,
  oscB_level=0.45, flt_type="LP24", flt_cutoff=3500.0, amp_attack=0.15, amp_release=1.2, mfx_mix=0.3, rev_size=0.8,
  rev_mix=0.25)
P(G, "Holy Drone", "Pad", "Sustained pipe organ drone with a cathedral-sized reverb.",
  [("Pipes", [("WT Pos A", 0.5)]), ("Tone", [("Cutoff", 0.35)]), ("Air", [("Noise Level", 0.15)]), ("Hall", [("Reverb Mix", 0.3)])],
  tags=["Organ", "Drone"],
  oscA_table="Pipe Organ", oscA_pos=0.4, oscA_voices=2, uni_detune=0.1, oscB_table="Pipe Organ", oscB_pos=0.8,
  oscB_oct=1, oscB_level=0.25, flt_type="LP12", flt_cutoff=5000.0, amp_attack=0.4, amp_release=2.0, rev_size=0.9,
  rev_damping=0.4, rev_mix=0.3)
P(G, "Praise Bass", "Bass", "Round organ bass with a clean sub for gospel bass lines.",
  [("Drawbars", [("WT Pos A", 0.5)]), ("Tone", [("Cutoff", 0.4)]), ("Sub", [("Sub Level", 0.3)]), ("Grit", [("Dist Mix", 0.4)])],
  tags=["Organ"],
  voice_mode="Mono", oscA_table="Drawbars", oscA_pos=0.1, sub_level=0.35, flt_type="LP24", flt_cutoff=1200.0,
  amp_release=0.12, dist_type="Tube", dist_drive=0.3, dist_mix=0.15)

# =====================================================================================================
# Daft Punk – Homework (14): acid squelch, raw filtered basses and leads
# =====================================================================================================
G = "homework"
P(G, "Squelch Box", "Bass", "Classic acid squelch with a resonant ladder, accent-like envelope and slide.",
  [("Squelch", [("Resonance", 0.15)]), ("Open", [("Cutoff", 0.4)]), ("Dirt", [("Dist Mix", 0.5)]), ("Echo", [("Delay Mix", 0.3)])],
  mods=[("Velocity", "Cutoff", 0.2)], tags=["Acid"],
  voice_mode="Legato", glide=0.06, oscA_table="Analog Saw", oscA_oct=-1, flt_type="Ladder", flt_cutoff=350.0,
  flt_res=0.8, flt_drive=0.3, flt_envamt=0.55, fenv_decay=0.2, fenv_sustain=0.05, amp_release=0.08,
  dist_type="Soft", dist_drive=0.4, dist_mix=0.3)
P(G, "Rubber Acid", "Bass", "Square-wave acid bass with a rubbery resonant bounce.",
  [("Squelch", [("Resonance", 0.15)]), ("Open", [("Cutoff", 0.4)]), ("Drive", [("Filter Drive", 0.4)]), ("Echo", [("Delay Mix", 0.3)])],
  mods=[("Velocity", "Cutoff", 0.2)], tags=["Acid"],
  voice_mode="Legato", glide=0.05, oscA_table="Analog Square", oscA_oct=-1, flt_type="Ladder", flt_cutoff=280.0,
  flt_res=0.78, flt_drive=0.35, flt_envamt=0.5, fenv_decay=0.25, fenv_sustain=0.1, amp_release=0.08)
P(G, "Warehouse Filter Bass", "Bass", "Raw saw bass whose filter sweeps every two beats under a pump.",
  [("Sweep", [("Cutoff", 0.35)]), ("Grit", [("Dist Mix", 0.3)]), ("Res", [("Resonance", 0.3)]), ("Sub", [("Sub Level", 0.3)])],
  mods=[("LFO 1", "Cutoff", 0.3)], tags=["Filter House"],
  voice_mode="Mono", oscA_table="Analog Saw", oscA_oct=-1, sub_level=0.3, flt_type="LP24", flt_cutoff=600.0,
  flt_res=0.4, lfo1_sync=True, lfo1_div="1/2", lfo1_shape="Triangle", pump_amount=0.5, pump_rate="1/4",
  dist_type="Soft", dist_drive=0.3)
P(G, "Raw Filter Lead", "Lead", "Gritty square lead with a slowly moving resonant ladder.",
  [("Filter", [("Cutoff", 0.4)]), ("Res", [("Resonance", 0.3)]), ("Grit", [("Dist Drive", 0.4)]), ("Echo", [("Delay Mix", 0.3)])],
  mods=[("LFO 1", "Cutoff", 0.25)], tags=["Filter"],
  voice_mode="Mono", oscA_table="Analog Square", oscA_pos=0.2, oscB_table="Analog Saw", oscB_level=0.3, oscB_fine=-10.0,
  flt_type="Ladder", flt_cutoff=1200.0, flt_res=0.55, flt_drive=0.3, lfo1_rate=0.3, dist_type="Soft", dist_drive=0.4,
  dist_mix=0.4, dly_time="1/8D", dly_mix=0.12)
P(G, "Distorted Riff Saw", "Lead", "Overdriven saw riff tone with tube crunch and a tight filter.",
  [("Crunch", [("Dist Drive", 0.4)]), ("Tone", [("Cutoff", 0.4)]), ("Width", [("Mod FX Mix", 0.4)]), ("Echo", [("Delay Mix", 0.3)])],
  mods=[("Filter Env", "Cutoff", 0.15)], tags=["Distorted"],
  voice_mode="Mono", oscA_table="Analog Saw", oscB_table="Analog Saw", oscB_level=0.5, oscB_fine=12.0, flt_type="LP24",
  flt_cutoff=2200.0, flt_res=0.25, fenv_decay=0.25, fenv_sustain=0.3, dist_type="Tube", dist_drive=0.55, dist_mix=0.8)
P(G, "Acid Line Arp", "Arp", "Random acid arpeggio with squelching accents and slapback echo.",
  [("Squelch", [("Resonance", 0.15)]), ("Open", [("Cutoff", 0.4)]), ("Dirt", [("Dist Mix", 0.5)]), ("Echo", [("Delay Mix", 0.3)])],
  mods=[("Velocity", "Cutoff", 0.15)], tags=["Acid", "Arp"],
  arp_on=True, arp_mode="Random", arp_rate="1/16", arp_octaves=2, arp_gate=0.5, voice_mode="Mono", oscA_table="Acid",
  oscA_pos=0.2, oscA_oct=-1, flt_type="Ladder", flt_cutoff=400.0, flt_res=0.8, flt_drive=0.3, flt_envamt=0.5,
  fenv_decay=0.15, fenv_sustain=0.0, amp_release=0.05, dist_type="Soft", dist_drive=0.4, dist_mix=0.3, dly_time="1/8D",
  dly_mix=0.12)
P(G, "Chicago Organ Stab", "Keys", "Short house organ stab with a punchy decay.",
  [("Drawbars", [("WT Pos A", 0.5)]), ("Tone", [("Cutoff", 0.4)]), ("Grit", [("Dist Mix", 0.3)]), ("Room", [("Reverb Mix", 0.3)])],
  tags=["House", "Organ"],
  oscA_table="Drawbars", oscA_pos=0.75, oscA_oct=1, flt_type="LP12", flt_cutoff=6000.0, amp_decay=0.6, amp_sustain=0.2,
  amp_release=0.1, pump_amount=0.3, rev_mix=0.12)
P(G, "Phaser Sweep Bass", "Bass", "Raw saw bass smeared by a slow, deep phaser.",
  [("Phase", [("Mod FX Mix", 0.3)]), ("Tone", [("Cutoff", 0.4)]), ("Grit", [("Dist Mix", 0.4)]), ("Sub", [("Sub Level", 0.3)])],
  tags=["Filter House"],
  voice_mode="Mono", oscA_table="Analog Saw", oscA_oct=-1, sub_level=0.3, flt_type="LP24", flt_cutoff=1000.0,
  flt_res=0.3, mfx_type="Phaser", mfx_rate=0.15, mfx_depth=0.8, mfx_mix=0.6, dist_drive=0.35, dist_mix=0.2)
P(G, "Grinding Sweep", "FX", "Distorted noise sweep that rises and falls through a resonant band-pass.",
  [("Sweep", [("Cutoff", 0.35)]), ("Grind", [("Dist Drive", 0.4)]), ("Res", [("Resonance", 0.3)]), ("Echo", [("Delay Mix", 0.3)])],
  mods=[("LFO 1", "Cutoff", 0.4)], tags=["Noise", "Sweep"],
  oscA_table="Rasp", oscA_pos=0.6, oscA_level=0.9, noise_level=0.9, flt_type="BP", flt_cutoff=1200.0, flt_res=0.4,
  lfo1_sync=True, lfo1_div="1/1", lfo1_shape="Triangle", dist_type="Hard", dist_drive=0.4, dist_mix=0.6,
  amp_attack=0.3, amp_release=0.6, dly_time="1/8", dly_mix=0.12)
P(G, "Funky Filter Keys", "Keys", "Clavinet-like pulse keys with a resonant envelope wah.",
  [("Wah", [("Cutoff", 0.35)]), ("Pulse", [("WT Pos A", 0.5)]), ("Phase", [("Mod FX Mix", 0.4)]), ("Room", [("Reverb Mix", 0.3)])],
  mods=[("Velocity", "Cutoff", 0.2)], tags=["Funk"],
  oscA_table="PWM", oscA_pos=0.65, flt_type="LP24", flt_cutoff=500.0, flt_res=0.5, flt_envamt=0.5, fenv_decay=0.25,
  fenv_sustain=0.1, amp_decay=0.5, amp_sustain=0.35, amp_release=0.1, mfx_type="Phaser", mfx_rate=0.5, mfx_mix=0.2,
  squash=0.3)
P(G, "Garage Squelch Lead", "Lead", "Acid table lead with a nasal squelch that sits above the groove.",
  [("Squelch", [("WT Pos A", 0.5)]), ("Open", [("Cutoff", 0.4)]), ("Dirt", [("Dist Mix", 0.5)]), ("Echo", [("Delay Mix", 0.3)])],
  mods=[("Filter Env", "WT Pos A", 0.3)], tags=["Acid"],
  voice_mode="Mono", glide=0.04, oscA_table="Acid", oscA_pos=0.35, flt_type="LP24", flt_cutoff=3500.0, flt_res=0.3,
  fenv_decay=0.3, fenv_sustain=0.2, dist_drive=0.4, dist_mix=0.25, dly_time="1/8D", dly_mix=0.12)
P(G, "Siren Sweep", "FX", "Analog-style siren that rises and falls with a resonant filter.",
  [("Rate", [("Pitch", 0.1)]), ("Tone", [("Cutoff", 0.4)]), ("Grit", [("Dist Mix", 0.5)]), ("Echo", [("Delay Mix", 0.3)])],
  mods=[("LFO 1", "Pitch", 0.35)], tags=["Siren"],
  voice_mode="Mono", oscA_table="Analog Saw", lfo1_shape="Saw", lfo1_rate=0.8, lfo1_retrig=True, flt_type="LP24",
  flt_cutoff=2500.0, flt_res=0.5, amp_release=0.5, dly_mode="PingPong", dly_time="1/4", dly_mix=0.15)
P(G, "Fuzz Bassline", "Bass", "Buzzy fuzz bass with a short filter snap.",
  [("Fuzz", [("Dist Drive", 0.4)]), ("Tone", [("Cutoff", 0.4)]), ("Buzz", [("WT Pos A", 0.5)]), ("Sub", [("Sub Level", 0.3)])],
  mods=[("Filter Env", "Cutoff", 0.15)], tags=["Distorted"],
  voice_mode="Mono", oscA_table="Buzz", oscA_pos=0.3, oscA_oct=-1, sub_level=0.3, flt_type="LP24", flt_cutoff=900.0,
  fenv_decay=0.2, fenv_sustain=0.2, dist_type="Soft", dist_drive=0.5, dist_mix=0.6)
P(G, "Mono Wah Lead", "Lead", "Band-pass lead that opens like a wah pedal on every note.",
  [("Wah", [("Cutoff", 0.35)]), ("Res", [("Resonance", 0.3)]), ("Grit", [("Dist Mix", 0.5)]), ("Echo", [("Delay Mix", 0.3)])],
  mods=[("Velocity", "Cutoff", 0.2)], tags=["Filter"],
  voice_mode="Mono", glide=0.03, oscA_table="Analog Saw", flt_type="BP", flt_cutoff=600.0, flt_res=0.5, flt_envamt=0.5,
  fenv_attack=0.03, fenv_decay=0.35, fenv_sustain=0.2, dist_drive=0.35, dist_mix=0.3, dly_time="1/8D", dly_mix=0.12)

# =====================================================================================================
# Daft Punk – Discovery (18): filter house with Pump, talkbox, disco strings, 80s leads, sweet pads
# =====================================================================================================
G = "discovery"
P(G, "Pumping Filter Chords", "Keys", "Saw chord stack that pumps on every beat while the filter sweeps open.",
  [("Filter", [("Cutoff", 0.4)]), ("Phase", [("Mod FX Mix", 0.4)]), ("Grit", [("Dist Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("LFO 1", "Cutoff", 0.2)], tags=["Pump", "Filter House"],
  oscA_table="Analog Saw", oscA_voices=3, uni_detune=0.25, oscB_table="Analog Square", oscB_level=0.35,
  flt_type="LP24", flt_cutoff=900.0, flt_res=0.35, lfo1_sync=True, lfo1_div="2/1", lfo1_shape="Triangle",
  pump_amount=0.7, pump_rate="1/4", mfx_type="Phaser", mfx_rate=0.3, mfx_mix=0.25, amp_release=0.25, rev_mix=0.12)
P(G, "Talkbox Lead", "Lead", "Talkbox-style lead that speaks through moving vowel formants.",
  [("Vowel", [("Formant", 0.6)]), ("Mouth", [("WT Pos A", 0.5)]), ("Echo", [("Delay Mix", 0.3)]), ("Grit", [("Dist Mix", 0.4)])],
  mods=[("Filter Env", "Formant", 0.4), ("Mod Wheel", "Formant", 0.4)], tags=["Talkbox", "Vocal"],
  voice_mode="Mono", glide=0.05, oscA_table="Talk Box", oscA_pos=0.3, oscB_table="Analog Saw", oscB_level=0.35,
  flt_type="Formant", flt_cutoff=1050.0, flt_res=0.55, flt_vowel=0.1, fenv_decay=0.4, fenv_sustain=0.3,
  amp_release=0.15, dly_time="1/8D", dly_mix=0.1)
P(G, "Talk Synth Chords", "Keys", "Chords that say a vowel on every hit, like a talkbox section.",
  [("Vowel", [("Formant", 0.6)]), ("Grit", [("Dist Mix", 0.3)]), ("Width", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("Filter Env", "Formant", 0.5)], tags=["Talkbox", "Vocal"],
  oscA_table="Talk Box", oscA_pos=0.5, oscA_voices=2, uni_detune=0.15, flt_type="Formant", flt_cutoff=1000.0,
  flt_res=0.45, fenv_attack=0.02, fenv_decay=0.5, fenv_sustain=0.2, amp_release=0.25, pump_amount=0.3,
  mfx_mix=0.25, rev_mix=0.12)
P(G, "Disco Strings", "Pad", "Lush disco string section with ensemble chorus and gentle pumping.",
  [("Bow", [("WT Pos A", 0.5)]), ("Air", [("Cutoff", 0.35)]), ("Ensemble", [("Mod FX Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("LFO 1", "Pitch", 0.002)], tags=["Strings", "Disco"],
  oscA_table="Strings", oscA_pos=0.6, oscA_voices=5, uni_detune=0.35, oscB_table="Hyper Saw", oscB_level=0.25,
  oscB_oct=1, flt_type="LP24", flt_cutoff=5000.0, amp_attack=0.12, amp_release=0.8, lfo1_rate=5.5,
  pump_amount=0.3, mfx_type="Chorus", mfx_mix=0.45, rev_mix=0.2)
P(G, "Eighties Solo Lead", "Lead", "Bright synced lead with portamento and delayed vibrato for solos.",
  [("Sync", [("WT Pos A", 0.5)]), ("Vibrato", [("Pitch", 0.01)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("Mod Wheel", "Pitch", 0.012), ("Filter Env", "WT Pos A", 0.2)], tags=["80s", "Solo"],
  voice_mode="Legato", glide=0.07, oscA_table="Sync Saw", oscA_pos=0.3, oscB_table="Analog Square", oscB_level=0.3,
  oscB_fine=7.0, flt_type="LP24", flt_cutoff=5500.0, fenv_decay=0.6, amp_release=0.3, dly_mode="PingPong",
  dly_time="1/8D", dly_mix=0.18, rev_mix=0.18)
P(G, "Sweet Analog Pad", "Pad", "Soft warm pad with gently detuned saws and a glossy chorus.",
  [("Warmth", [("Cutoff", 0.35)]), ("Hollow", [("Level B", 0.3)]), ("Width", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("LFO 1", "Cutoff", 0.06)], tags=["Warm", "Sweet"],
  oscA_table="Analog Saw", oscA_pos=0.4, oscA_voices=4, uni_detune=0.3, oscB_table="Hollow", oscB_pos=0.3,
  oscB_level=0.35, flt_type="LP12", flt_cutoff=2800.0, amp_attack=0.4, amp_release=1.4, lfo1_rate=0.2,
  mfx_mix=0.4, rev_size=0.7, rev_mix=0.25)
P(G, "Filter House Bass", "Bass", "Round octave saw bass that pumps behind the kick.",
  [("Filter", [("Cutoff", 0.4)]), ("Grit", [("Dist Mix", 0.25)]), ("Res", [("Resonance", 0.3)]), ("Sub", [("Sub Level", 0.3)])],
  mods=[("Filter Env", "Cutoff", 0.12)], tags=["Pump", "Filter House"],
  voice_mode="Mono", oscA_table="Analog Saw", oscA_oct=-1, oscB_table="Analog Saw", oscB_level=0.35, sub_level=0.3,
  flt_type="LP24", flt_cutoff=700.0, flt_res=0.3, fenv_decay=0.3, fenv_sustain=0.4, pump_amount=0.55)
P(G, "Sidechain Organ", "Keys", "House organ chords breathing with a strong quarter-note pump.",
  [("Drawbars", [("WT Pos A", 0.5)]), ("Tone", [("Cutoff", 0.4)]), ("Phase", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])],
  tags=["Pump", "Organ"],
  oscA_table="Drawbars", oscA_pos=0.5, oscA_oct=1, flt_type="LP24", flt_cutoff=4000.0, amp_release=0.15,
  pump_amount=0.75, pump_rate="1/4", mfx_type="Phaser", mfx_rate=0.25, mfx_mix=0.2, rev_mix=0.12)
P(G, "Vocoded Chords", "Pad", "Vocoder-like chord pad built from vowel tables and formants.",
  [("Vowel", [("Formant", 0.5)]), ("Voice", [("WT Pos A", 0.5)]), ("Width", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("LFO 1", "Formant", 0.2)], tags=["Vocal", "Talkbox"],
  oscA_table="Vowels", oscA_pos=0.3, oscA_voices=3, uni_detune=0.2, oscB_table="Analog Saw", oscB_level=0.3,
  flt_type="Formant", flt_cutoff=1000.0, flt_res=0.35, flt_vowel=0.3, lfo1_rate=0.25, amp_attack=0.15,
  amp_release=0.8, mfx_mix=0.3, rev_mix=0.2)
P(G, "Glitter Arp", "Arp", "Sparkling FM bell arpeggio bouncing between ping-pong delays.",
  [("Sparkle", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.4)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("Velocity", "WT Pos A", 0.2)], tags=["Arp", "Bright"],
  arp_on=True, arp_mode="Up", arp_rate="1/16", arp_octaves=2, arp_gate=0.4, oscA_table="FM Bell", oscA_pos=0.3,
  flt_type="LP12", flt_cutoff=9000.0, amp_decay=0.4, amp_sustain=0.0, amp_release=0.3, dly_mode="PingPong",
  dly_time="1/8D", dly_feedback=0.45, dly_mix=0.22, rev_mix=0.18)
P(G, "Funk Riff Synth", "Lead", "Snappy phased synth riff that plays like a muted funk guitar.",
  [("Snap", [("Cutoff", 0.35)]), ("Phase", [("Mod FX Mix", 0.4)]), ("Grit", [("Dist Mix", 0.4)]), ("Echo", [("Delay Mix", 0.3)])],
  mods=[("Velocity", "Cutoff", 0.2)], tags=["Funk"],
  voice_mode="Mono", oscA_table="PWM Saw", oscA_pos=0.4, flt_type="LP24", flt_cutoff=900.0, flt_res=0.35,
  flt_envamt=0.45, fenv_decay=0.18, fenv_sustain=0.1, amp_decay=0.35, amp_sustain=0.3, amp_release=0.08,
  mfx_type="Phaser", mfx_rate=0.7, mfx_mix=0.4, dist_drive=0.3, dist_mix=0.2)
P(G, "Laser Harp", "Lead", "Pulse pluck with a zapping pitch envelope, built for melodic hooks.",
  [("Zap", [("Pitch A", 0.03)]), ("Pulse", [("WT Pos A", 0.5)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])],
  tags=["80s", "Pluck"],
  oscA_table="PWM", oscA_pos=0.45, penv_amount=12.0, penv_decay=0.04, flt_type="LP12", flt_cutoff=6000.0,
  amp_decay=0.6, amp_sustain=0.2, amp_release=0.3, dly_mode="PingPong", dly_time="1/8D", dly_mix=0.18, rev_mix=0.15)
P(G, "Sunset Pad", "Pad", "Golden warm pad with a soft swell and slow chorus.",
  [("Warmth", [("Cutoff", 0.35)]), ("Shimmer", [("Level B", 0.3)]), ("Width", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("LFO 1", "WT Pos A", 0.15)], tags=["Warm", "Sweet"],
  oscA_table="PWM Saw", oscA_pos=0.3, oscA_voices=3, uni_detune=0.25, oscB_table="Basic Shapes", oscB_pos=0.4,
  oscB_oct=1, oscB_level=0.25, flt_type="LP24", flt_cutoff=2500.0, amp_attack=0.6, amp_release=1.5, lfo1_rate=0.15,
  mfx_mix=0.4, rev_size=0.75, rev_mix=0.25)
P(G, "French Disco Bass", "Bass", "Octave-bouncing disco bass that pumps with the groove.",
  [("Tone", [("Cutoff", 0.4)]), ("Octave", [("Level B", 0.3)]), ("Grit", [("Dist Mix", 0.25)]), ("Sub", [("Sub Level", 0.3)])],
  mods=[("Filter Env", "Cutoff", 0.15)], tags=["Disco", "Pump"],
  voice_mode="Mono", oscA_table="Analog Square", oscA_pos=0.3, oscA_oct=-1, oscB_table="Analog Saw", oscB_level=0.25,
  sub_level=0.3, flt_type="LP24", flt_cutoff=1000.0, flt_res=0.2, fenv_decay=0.2, fenv_sustain=0.3,
  amp_decay=0.4, amp_sustain=0.6, amp_release=0.08, pump_amount=0.4)
P(G, "Crystal Keys", "Keys", "Bright FM keys with a crisp attack and silky tail.",
  [("Crystal", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.4)]), ("Width", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("Velocity", "WT Pos A", 0.25)], tags=["Bright", "Keys"],
  oscA_table="FM Bell", oscA_pos=0.45, oscB_table="FM Digital", oscB_pos=0.2, oscB_level=0.25, flt_type="LP12",
  flt_cutoff=8000.0, amp_decay=1.2, amp_sustain=0.0, amp_release=0.5, mfx_mix=0.25, rev_mix=0.2)
P(G, "Shuffle Pump Pad", "Pad", "Airy pad chopped into a shuffling eighth-note pump.",
  [("Air", [("Cutoff", 0.35)]), ("Grit", [("Dist Mix", 0.25)]), ("Width", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])],
  tags=["Pump", "Filter House"],
  oscA_table="Hyper Saw", oscA_pos=0.3, oscA_voices=4, uni_detune=0.3, flt_type="LP24", flt_cutoff=3000.0,
  amp_attack=0.1, amp_release=0.8, pump_amount=0.75, pump_rate="1/8", mfx_mix=0.35, rev_mix=0.2)
P(G, "Vowel Sweep FX", "FX", "Formant sweep that says a long slow word across the stereo field.",
  [("Vowel", [("Formant", 0.5)]), ("Sweep", [("WT Pos A", 0.5)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("LFO 1", "Formant", 0.5), ("LFO 2", "Pan A", 0.6)], tags=["Talkbox", "Sweep"],
  oscA_table="Formant Sweep", oscA_pos=0.2, flt_type="Formant", flt_cutoff=1000.0, flt_res=0.5, lfo1_shape="Triangle",
  lfo1_rate=0.3, lfo2_rate=0.5, amp_attack=0.2, amp_release=0.6, dly_mode="PingPong", dly_time="1/4",
  dly_mix=0.15, rev_mix=0.2)
P(G, "Metal Mouth Lead", "Lead", "Ring-modulated talkbox lead with a metallic, synthetic voice.",
  [("Vowel", [("Formant", 0.6)]), ("Metal", [("Level B", 0.3)]), ("Echo", [("Delay Mix", 0.3)]), ("Grit", [("Dist Mix", 0.4)])],
  mods=[("Filter Env", "Formant", 0.35)], tags=["Talkbox", "Vocal"],
  voice_mode="Mono", glide=0.04, oscA_table="Talk Box", oscA_pos=0.6, oscB_table="Ring Mod", oscB_pos=0.3,
  oscB_level=0.25, flt_type="Formant", flt_cutoff=1100.0, flt_res=0.5, fenv_decay=0.35, amp_release=0.15,
  dly_time="1/8D", dly_mix=0.1)

# =====================================================================================================
# Daft Punk – Human After All (8): rough, guitar-like, mechanical riffs
# =====================================================================================================
G = "haa"
P(G, "Gritty Riff Saw", "Lead", "Overdriven saw riff that chugs like a distorted guitar.",
  [("Gain", [("Dist Drive", 0.4)]), ("Tone", [("Cutoff", 0.4)]), ("Chug", [("Resonance", 0.3)]), ("Room", [("Reverb Mix", 0.3)])],
  mods=[("Filter Env", "Cutoff", 0.15)], tags=["Rock", "Distorted"],
  voice_mode="Mono", oscA_table="Analog Saw", oscB_table="Analog Saw", oscB_level=0.5, oscB_fine=-9.0, flt_type="Ladder",
  flt_cutoff=1500.0, flt_res=0.3, fenv_decay=0.2, fenv_sustain=0.4, dist_type="Hard", dist_drive=0.55, dist_tone=0.55,
  dist_mix=0.9, squash=0.3)
P(G, "Fuzz Chord Stab", "Keys", "Saw and fifth stacked into a fuzzed-out chord stab.",
  [("Fuzz", [("Dist Drive", 0.4)]), ("Tone", [("Cutoff", 0.4)]), ("Fifth", [("Level B", 0.3)]), ("Room", [("Reverb Mix", 0.3)])],
  tags=["Rock", "Distorted"],
  oscA_table="Analog Saw", oscB_table="Analog Square", oscB_semi=7, oscB_level=0.4, flt_type="LP24", flt_cutoff=2500.0,
  amp_decay=0.6, amp_sustain=0.5, amp_release=0.15, dist_type="Tube", dist_drive=0.6, dist_tone=0.5, dist_mix=0.9)
P(G, "Machine Riff", "Lead", "Bit-crushed square riff with a cold, mechanical edge.",
  [("Bits", [("Dist Drive", 0.4)]), ("Tone", [("Cutoff", 0.4)]), ("Pulse", [("WT Pos A", 0.5)]), ("Echo", [("Delay Mix", 0.3)])],
  mods=[("Filter Env", "Cutoff", 0.15)], tags=["Mechanical", "Lo-Fi"],
  voice_mode="Mono", oscA_table="Analog Square", oscA_pos=0.3, flt_type="LP24", flt_cutoff=2500.0, fenv_decay=0.15,
  fenv_sustain=0.4, dist_type="Bitcrush", dist_drive=0.35, dist_mix=0.7, dly_time="1/8", dly_mix=0.1)
P(G, "Talking Fuzz", "Lead", "Formant lead slammed into hard distortion for a talking fuzz pedal sound.",
  [("Vowel", [("Formant", 0.6)]), ("Fuzz", [("Dist Drive", 0.4)]), ("Mouth", [("WT Pos A", 0.5)]), ("Room", [("Reverb Mix", 0.3)])],
  mods=[("LFO 1", "Formant", 0.35)], tags=["Talkbox", "Distorted"],
  voice_mode="Mono", oscA_table="Talk Box", oscA_pos=0.5, flt_type="Formant", flt_cutoff=1000.0, flt_res=0.5,
  lfo1_sync=True, lfo1_div="1/4", lfo1_shape="Triangle", dist_type="Hard", dist_drive=0.5, dist_mix=0.85)
P(G, "Steel String Synth", "Keys", "Plucky pulse tone with fuzz that mimics a picked electric guitar.",
  [("Pick", [("Cutoff", 0.35)]), ("Fuzz", [("Dist Drive", 0.4)]), ("Pulse", [("WT Pos A", 0.5)]), ("Room", [("Reverb Mix", 0.3)])],
  mods=[("Velocity", "Cutoff", 0.2)], tags=["Rock", "Pluck"],
  oscA_table="PWM Saw", oscA_pos=0.5, flt_type="LP24", flt_cutoff=1600.0, flt_envamt=0.35, fenv_decay=0.3,
  fenv_sustain=0.2, amp_decay=1.0, amp_sustain=0.2, amp_release=0.2, dist_type="Tube", dist_drive=0.5, dist_mix=0.75)
P(G, "Mechanic Bass", "Bass", "Clanky buzz bass with a crunchy bite for repetitive riffs.",
  [("Crunch", [("Dist Drive", 0.4)]), ("Tone", [("Cutoff", 0.4)]), ("Buzz", [("WT Pos A", 0.5)]), ("Sub", [("Sub Level", 0.3)])],
  mods=[("Filter Env", "Cutoff", 0.15)], tags=["Mechanical"],
  voice_mode="Mono", oscA_table="Buzz", oscA_pos=0.2, oscA_oct=-1, sub_level=0.35, flt_type="LP24", flt_cutoff=800.0,
  flt_res=0.25, fenv_decay=0.15, fenv_sustain=0.3, dist_type="Hard", dist_drive=0.45, dist_mix=0.6)
P(G, "Clockwork Arp", "Arp", "Distorted square arpeggio ticking in tight eighth notes.",
  [("Tick", [("Cutoff", 0.35)]), ("Crunch", [("Dist Drive", 0.4)]), ("Pulse", [("WT Pos A", 0.5)]), ("Echo", [("Delay Mix", 0.3)])],
  mods=[("Filter Env", "Cutoff", 0.2)], tags=["Mechanical", "Arp"],
  arp_on=True, arp_mode="UpDown", arp_rate="1/8", arp_octaves=2, arp_gate=0.35, oscA_table="Analog Square",
  oscA_pos=0.4, flt_type="LP24", flt_cutoff=1800.0, fenv_decay=0.1, fenv_sustain=0.0, amp_decay=0.2, amp_sustain=0.3,
  dist_type="Hard", dist_drive=0.4, dist_mix=0.7, dly_time="1/8D", dly_mix=0.12)
P(G, "Distortion Wah", "FX", "Fuzzed saw swept by an auto-wah band-pass for gritty transitions.",
  [("Wah", [("Cutoff", 0.35)]), ("Fuzz", [("Dist Drive", 0.4)]), ("Res", [("Resonance", 0.3)]), ("Echo", [("Delay Mix", 0.3)])],
  mods=[("LFO 1", "Cutoff", 0.35)], tags=["Rock", "Sweep"],
  voice_mode="Mono", oscA_table="Analog Saw", flt_type="BP", flt_cutoff=900.0, flt_res=0.55, lfo1_sync=True,
  lfo1_div="1/8", lfo1_shape="Triangle", dist_type="Hard", dist_drive=0.55, dist_mix=0.85, amp_release=0.3,
  dly_time="1/8", dly_mix=0.1)

# =====================================================================================================
# Daft Punk – Tron: Legacy (12): monumental brass, pulsing basses, arpeggios
# =====================================================================================================
G = "tron"
P(G, "Grid Pulse Bass", "Bass", "Relentless sixteenth-note bass pulse with a cutting filter envelope.",
  [("Pulse", [("Cutoff", 0.35)]), ("Drive", [("Filter Drive", 0.4)]), ("Sub", [("Sub Level", 0.3)]), ("Hall", [("Reverb Mix", 0.2)])],
  mods=[("Filter Env", "Cutoff", 0.15)], tags=["Pulse", "Synthwave"],
  arp_on=True, arp_rate="1/16", arp_gate=0.45, voice_mode="Mono", oscA_table="Analog Saw", oscA_oct=-1, sub_level=0.35,
  flt_type="LP24", flt_cutoff=500.0, flt_res=0.25, flt_envamt=0.35, fenv_decay=0.12, fenv_sustain=0.0,
  amp_decay=0.15, amp_sustain=0.3, amp_release=0.05)
P(G, "Monolith Brass", "Brass", "Towering low brass with slow swell, octave weight and a giant hall.",
  [("Swell", [("Cutoff", 0.35)]), ("Blare", [("WT Pos A", 0.5)]), ("Weight", [("Level B", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("Filter Env", "WT Pos A", 0.3)], tags=["Brass", "Cinematic"],
  oscA_table="Brass", oscA_pos=0.5, oscA_oct=-1, oscA_voices=4, uni_detune=0.3, oscB_table="Saw Octaves",
  oscB_oct=-1, oscB_level=0.35, flt_type="LP24", flt_cutoff=700.0, flt_envamt=0.4, fenv_attack=0.6, fenv_decay=1.5,
  fenv_sustain=0.6, amp_attack=0.25, amp_release=1.0, rev_size=0.85, rev_mix=0.3)
P(G, "Light Cycle Arp", "Arp", "Glowing supersaw arpeggio racing upward with dotted echoes.",
  [("Glow", [("Cutoff", 0.4)]), ("Width", [("Mod FX Mix", 0.4)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("Filter Env", "Cutoff", 0.15)], tags=["Arp", "Synthwave"],
  arp_on=True, arp_mode="Up", arp_rate="1/16", arp_octaves=3, arp_gate=0.5, oscA_table="Hyper Saw", oscA_pos=0.4,
  oscA_voices=4, uni_detune=0.3, flt_type="LP24", flt_cutoff=2500.0, fenv_decay=0.15, fenv_sustain=0.1,
  amp_release=0.15, dly_mode="PingPong", dly_time="1/8D", dly_feedback=0.4, dly_mix=0.2, rev_mix=0.18)
P(G, "Neon Grid Pad", "Pad", "Dark pulsing pad whose filter moves on a slow tempo-synced triangle.",
  [("Glow", [("Cutoff", 0.35)]), ("Pulse", [("Level B", 0.3)]), ("Width", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("LFO 1", "Cutoff", 0.2)], tags=["Synthwave", "Dark"],
  oscA_table="Analog Saw", oscA_voices=4, uni_detune=0.3, oscB_table="PWM", oscB_pos=0.4, oscB_level=0.3,
  flt_type="LP24", flt_cutoff=1200.0, flt_res=0.3, lfo1_sync=True, lfo1_div="1/1", lfo1_shape="Triangle",
  amp_attack=0.5, amp_release=1.4, mfx_mix=0.3, rev_size=0.8, rev_mix=0.25)
P(G, "Frontier Sync Lead", "Lead", "Cinematic synced lead with long echoes for soaring themes.",
  [("Sync", [("WT Pos A", 0.5)]), ("Tone", [("Cutoff", 0.4)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("Mod Wheel", "Pitch", 0.01), ("Filter Env", "WT Pos A", 0.2)], tags=["Cinematic"],
  voice_mode="Legato", glide=0.05, oscA_table="Sync Saw", oscA_pos=0.35, oscA_voices=2, uni_detune=0.15,
  flt_type="LP24", flt_cutoff=5000.0, amp_release=0.5, dly_mode="PingPong", dly_time="1/4D", dly_mix=0.2,
  rev_size=0.8, rev_mix=0.22)
P(G, "Pulse Engine Bass", "Bass", "Bass gated by a square LFO into a driving sixteenth-note engine.",
  [("Gate", [("Cutoff", 0.35)]), ("Drive", [("Filter Drive", 0.4)]), ("Sub", [("Sub Level", 0.3)]), ("Grit", [("Dist Mix", 0.4)])],
  mods=[("LFO 1", "Cutoff", 0.35)], tags=["Pulse", "Synthwave"],
  voice_mode="Mono", oscA_table="Analog Saw", oscA_oct=-1, oscB_table="Analog Square", oscB_oct=-1, oscB_level=0.3,
  sub_level=0.3, flt_type="LP24", flt_cutoff=500.0, flt_res=0.2, lfo1_shape="Square", lfo1_sync=True, lfo1_div="1/16",
  amp_release=0.1)
P(G, "Cinematic Low Brass", "Brass", "Short, heavy low-brass stab for trailer hits.",
  [("Blare", [("WT Pos A", 0.5)]), ("Tone", [("Cutoff", 0.4)]), ("Grit", [("Dist Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("Filter Env", "Cutoff", 0.15)], tags=["Brass", "Cinematic"],
  oscA_table="FM Brass", oscA_pos=0.5, oscA_oct=-1, oscB_table="Brass", oscB_pos=0.6, oscB_oct=-1, oscB_level=0.4,
  flt_type="LP24", flt_cutoff=900.0, flt_envamt=0.35, fenv_decay=0.4, fenv_sustain=0.2, amp_decay=0.9, amp_sustain=0.3,
  amp_release=0.5, rev_size=0.8, rev_mix=0.25)
P(G, "Data Stream Arp", "Arp", "Random digital FM arpeggio flickering like scrolling code.",
  [("Index", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.4)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("LFO 1", "WT Pos A", 0.2)], tags=["Arp", "Digital"],
  arp_on=True, arp_mode="Random", arp_rate="1/16", arp_octaves=2, arp_gate=0.4, oscA_table="FM Digital", oscA_pos=0.3,
  lfo1_shape="S&H", lfo1_sync=True, lfo1_div="1/16", flt_type="LP24", flt_cutoff=6000.0, amp_decay=0.25,
  amp_sustain=0.2, dly_mode="PingPong", dly_time="1/8", dly_mix=0.15, rev_mix=0.15)
P(G, "Shutdown Hit", "FX", "System-crash impact that collapses in pitch into noise and reverb.",
  [("Collapse", [("Pitch", -0.2)]), ("Noise", [("Noise Level", 0.3)]), ("Crush", [("Dist Mix", 0.5)]), ("Hall", [("Reverb Mix", 0.3)])],
  tags=["Impact", "Cinematic"],
  oscA_table="Hyper Saw", oscA_pos=0.6, oscA_voices=4, uni_detune=0.4, noise_level=0.15, penv_amount=-36.0,
  penv_decay=0.9, flt_type="LP24", flt_cutoff=4000.0, flt_envamt=-0.3, fenv_decay=0.8, fenv_sustain=0.0,
  amp_decay=1.2, amp_sustain=0.0, amp_release=0.6, dist_type="Bitcrush", dist_drive=0.3, dist_mix=0.3,
  rev_size=0.85, rev_mix=0.3)
P(G, "Sky Bridge Pad", "Pad", "Wide luminous pad with slow movement and a long reflective tail.",
  [("Light", [("Cutoff", 0.35)]), ("Morph", [("WT Pos A", 0.5)]), ("Width", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("LFO 1", "WT Pos A", 0.2)], tags=["Cinematic", "Wide"],
  oscA_table="Hyper Saw", oscA_pos=0.2, oscA_voices=6, uni_detune=0.3, uni_spread=0.95, oscB_table="Hollow",
  oscB_level=0.3, oscB_oct=1, flt_type="LP24", flt_cutoff=2600.0, amp_attack=0.8, amp_release=1.8, lfo1_rate=0.08,
  mfx_mix=0.35, rev_size=0.85, rev_mix=0.3)
P(G, "Pulsing String Ostinato", "Arp", "Synthetic strings repeating a tight ostinato for tension.",
  [("Bow", [("WT Pos A", 0.5)]), ("Tone", [("Cutoff", 0.4)]), ("Ensemble", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])],
  mods=[("Velocity", "Cutoff", 0.15)], tags=["Strings", "Cinematic"],
  arp_on=True, arp_mode="Up", arp_rate="1/16", arp_gate=0.6, oscA_table="Strings", oscA_pos=0.5, oscA_voices=3,
  uni_detune=0.25, flt_type="LP24", flt_cutoff=3000.0, amp_attack=0.01, amp_decay=0.2, amp_sustain=0.5,
  amp_release=0.15, mfx_mix=0.3, rev_size=0.75, rev_mix=0.22)
P(G, "Circuit Bass Drone", "Bass", "Dark sustained bass drone with slowly opening resonance.",
  [("Open", [("Cutoff", 0.4)]), ("Res", [("Resonance", 0.3)]), ("Drive", [("Filter Drive", 0.4)]), ("Sub", [("Sub Level", 0.3)])],
  mods=[("LFO 1", "Cutoff", 0.15)], tags=["Dark", "Drone"],
  voice_mode="Mono", oscA_table="Saw Octaves", oscA_pos=0.2, oscA_oct=-1, oscA_voices=2, uni_detune=0.15,
  sub_level=0.35, flt_type="LP24", flt_cutoff=450.0, flt_res=0.4, lfo1_rate=0.1, amp_attack=0.05, amp_release=0.4)

# =====================================================================================================
# Daft Punk – Random Access Memories (8): warm analog polysynths, funky keys, modular basses
# =====================================================================================================
G = "ram"
P(G, "Warm Poly Brass", "Brass", "Vintage polysynth brass with a soft envelope swell.",
  [("Swell", [("Cutoff", 0.35)]), ("Warmth", [("Filter Drive", 0.4)]), ("Width", [("Mod FX Mix", 0.4)]), ("Room", [("Reverb Mix", 0.3)])],
  mods=[("Velocity", "Cutoff", 0.15), ("LFO 1", "Pitch", 0.002)], tags=["Brass", "Vintage"],
  oscA_table="Analog Saw", oscA_pos=0.3, oscA_voices=3, uni_detune=0.25, oscB_table="Analog Saw", oscB_level=0.3,
  oscB_fine=-8.0, flt_type="LP24", flt_cutoff=1100.0, flt_envamt=0.35, fenv_attack=0.06, fenv_decay=0.5,
  fenv_sustain=0.5, amp_attack=0.02, amp_release=0.4, lfo1_rate=4.5, mfx_mix=0.25, rev_mix=0.15)
P(G, "Studio Poly Pad", "Pad", "Rich warm studio pad with slow filter movement and ensemble.",
  [("Warmth", [("Cutoff", 0.35)]), ("Pulse", [("Level B", 0.3)]), ("Width", [("Mod FX Mix", 0.4)]), ("Room", [("Reverb Mix", 0.3)])],
  mods=[("LFO 1", "Cutoff", 0.08)], tags=["Warm", "Vintage"],
  oscA_table="Analog Saw", oscA_pos=0.4, oscA_voices=3, uni_detune=0.25, oscB_table="PWM", oscB_pos=0.4,
  oscB_level=0.3, flt_type="LP24", flt_cutoff=1800.0, flt_res=0.15, amp_attack=0.35, amp_release=1.2,
  lfo1_rate=0.2, mfx_mix=0.4, rev_mix=0.2)
P(G, "Funk Clav Keys", "Keys", "Tight funky clav tone with a percussive filter bite.",
  [("Bite", [("Cutoff", 0.35)]), ("Pulse", [("WT Pos A", 0.5)]), ("Phase", [("Mod FX Mix", 0.4)]), ("Room", [("Reverb Mix", 0.3)])],
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Funk", "Keys"],
  oscA_table="PWM", oscA_pos=0.75, oscB_table="Analog Saw", oscB_level=0.2, flt_type="LP24", flt_cutoff=1500.0,
  flt_res=0.3, flt_envamt=0.35, fenv_decay=0.15, fenv_sustain=0.1, amp_decay=0.5, amp_sustain=0.3, amp_release=0.06,
  mfx_type="Phaser", mfx_rate=0.4, mfx_mix=0.15, rev_mix=0.1, squash=0.35)
P(G, "Modular Pluck Bass", "Bass", "Woody modular bass pluck with a snappy ladder envelope.",
  [("Snap", [("Cutoff", 0.35)]), ("Res", [("Resonance", 0.3)]), ("Drive", [("Filter Drive", 0.4)]), ("Sub", [("Sub Level", 0.3)])],
  mods=[("Velocity", "Cutoff", 0.2)], tags=["Modular", "Funk"],
  voice_mode="Mono", oscA_table="Analog Saw", oscA_oct=-1, oscB_table="Analog Square", oscB_oct=-1, oscB_level=0.3,
  sub_level=0.25, flt_type="Ladder", flt_cutoff=350.0, flt_res=0.35, flt_envamt=0.45, fenv_decay=0.18,
  fenv_sustain=0.05, amp_decay=0.6, amp_sustain=0.4, amp_release=0.08)
P(G, "Electric Tine Keys", "Keys", "Soft electric-piano-like tines with a velocity-driven bark.",
  [("Bark", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.4)]), ("Trem", [("Mod FX Mix", 0.4)]), ("Room", [("Reverb Mix", 0.3)])],
  mods=[("Velocity", "WT Pos A", 0.35), ("LFO 1", "Pan A", 0.3)], tags=["Keys", "Vintage"],
  oscA_table="FM Bell", oscA_pos=0.15, oscB_table="Basic Shapes", oscB_level=0.35, flt_type="LP12", flt_cutoff=5000.0,
  amp_decay=2.0, amp_sustain=0.0, amp_release=0.4, lfo1_rate=4.0, mfx_mix=0.2, rev_mix=0.15)
P(G, "Seventies Solo Lead", "Lead", "Warm square lead with portamento and expressive vibrato.",
  [("Tone", [("Cutoff", 0.4)]), ("Vibrato", [("Pitch", 0.01)]), ("Echo", [("Delay Mix", 0.3)]), ("Room", [("Reverb Mix", 0.3)])],
  mods=[("Mod Wheel", "Pitch", 0.012), ("Aftertouch", "Cutoff", 0.2)], tags=["Solo", "Vintage"],
  voice_mode="Legato", glide=0.09, oscA_table="Analog Square", oscA_pos=0.4, oscB_table="Analog Saw", oscB_level=0.3,
  oscB_fine=6.0, flt_type="LP24", flt_cutoff=2800.0, flt_res=0.2, flt_envamt=0.2, amp_release=0.3, dly_time="1/4",
  dly_mix=0.12, rev_mix=0.15)
P(G, "Boogie Bass", "Bass", "Round, bouncy square bass for funky disco lines.",
  [("Tone", [("Cutoff", 0.4)]), ("Bounce", [("Resonance", 0.3)]), ("Drive", [("Filter Drive", 0.4)]), ("Sub", [("Sub Level", 0.3)])],
  mods=[("Filter Env", "Cutoff", 0.15)], tags=["Funk", "Disco"],
  voice_mode="Mono", oscA_table="Analog Square", oscA_pos=0.2, oscA_oct=-1, sub_level=0.25, flt_type="LP24",
  flt_cutoff=600.0, flt_res=0.2, flt_envamt=0.3, fenv_decay=0.25, fenv_sustain=0.2, amp_decay=0.5, amp_sustain=0.5,
  amp_release=0.08)
P(G, "Vintage String Ensemble", "Pad", "Classic string machine with thick ensemble chorus.",
  [("Bow", [("WT Pos A", 0.5)]), ("Tone", [("Cutoff", 0.35)]), ("Ensemble", [("Mod FX Mix", 0.4)]), ("Room", [("Reverb Mix", 0.3)])],
  tags=["Strings", "Vintage"],
  oscA_table="Strings", oscA_pos=0.3, oscA_voices=4, uni_detune=0.3, oscB_table="Analog Saw", oscB_oct=1,
  oscB_level=0.25, flt_type="LP12", flt_cutoff=4000.0, amp_attack=0.15, amp_release=1.0, mfx_type="Chorus",
  mfx_rate=0.6, mfx_depth=0.7, mfx_mix=0.5, rev_mix=0.18)


# =====================================================================================================
def slug(name):
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")


def main():
    trims = {}
    if os.path.exists(TRIM_FILE):
        with open(TRIM_FILE) as f:
            trims = json.load(f)

    if len(sys.argv) > 2 and sys.argv[1] == "--trim":
        with open(sys.argv[2]) as f:
            report = json.load(f)
        for r in report["presets"]:
            if r["name"] == "Init":
                continue
            delta = TARGET_LUFS - r["loudness_lufs"]
            trims[r["name"]] = round(max(-24.0, min(12.0, trims.get(r["name"], 0.0) + delta)), 1)
        with open(TRIM_FILE, "w") as f:
            json.dump(dict(sorted(trims.items())), f, indent=1)
        print(f"updated {len(trims)} trims")

    names = [p["name"] for p in PRESETS]
    assert len(names) == len(set(names)), "duplicate names"
    counts = {}
    for p in PRESETS:
        counts[p["group"]] = counts.get(p["group"], 0) + 1
    expected = {"yeezus": 24, "graduation": 10, "808s": 10, "mbdtf": 10, "donda": 6, "homework": 14,
                "discovery": 18, "haa": 8, "tron": 12, "ram": 8}
    assert counts == expected, counts

    for old in os.listdir(PRESET_DIR):
        if old.endswith(".json") and not old.startswith("000_"):
            os.remove(os.path.join(PRESET_DIR, old))

    for i, p in enumerate(PRESETS, start=1):
        params = dict(p["params"])
        trim = trims.get(p["name"], 0.0)
        if abs(trim) > 0.05:
            params["out_gain"] = trim
        sparse = {}
        for k in DEFAULTS:  # stable key order
            if k in params and params[k] != DEFAULTS[k]:
                v = params[k]
                sparse[k] = round(v, 5) if isinstance(v, float) else v
        doc = {
            "name": p["name"], "category": p["category"], "tags": p["tags"], "description": p["description"],
            "macros": p["macros"], "version": 1, "params": sparse,
        }
        path = os.path.join(PRESET_DIR, f"{i:03d}_{slug(p['name'])}.json")
        with open(path, "w") as f:
            json.dump(doc, f, indent=2)
            f.write("\n")
    print(f"wrote {len(PRESETS)} presets (+ Init) to {PRESET_DIR}")


if __name__ == "__main__":
    main()
