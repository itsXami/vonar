#!/usr/bin/env python3
"""Reworked versions of the 14 presets the user marked "fix" (tools/presets/selection.json).

Each rework keeps the preset's name, category and role, and is rebuilt around one clear idea (engine v2: warp,
String, Comb, Mod Env, Random). The old versions stay in generate_presets.py / generate_candidates.py so both can
be compared; build_library.py uses a rework only when its name is listed in selection.json "fixes_accepted".

    python3 tools/presets/generate_fixes.py                      # write tools/presets/fixes/*.json
    python3 tools/presets/generate_fixes.py --trim report.json   # level-match from a render report, then write
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import generate_candidates as gc  # noqa: E402  (defines both batches; gc.gp is generate_presets)

gp = gc.gp
OUT_DIR = os.path.join(HERE, "fixes")
TRIM_FILE = os.path.join(HERE, "fix_trims.json")
TARGET_LUFS = -15.0
M = gc.M

_start = len(gp.PRESETS)
P = gp.P

# ---------------------------------------------------------------------------------------------- Bass
# User: "nothing audible". The old one sat an octave too low (C1, ~33 Hz) with almost no harmonics.
P("cold", "Long Glide 808", "Bass", "Gliding 808 with a folded upper growl that stays audible on laptop speakers.",
  M(("Drive", [("Dist Drive", 0.35)]), ("Tone", [("Cutoff", 0.4)]), ("Growl", [("WT Pos A", 0.4)]), ("Sub", [("Sub Level", 0.35)])),
  mods=[("Velocity", "Dist Drive", 0.2), ("Mod Wheel", "Cutoff", 0.3), ("Mod Env", "Cutoff", -0.25)], tags=["808", "Glide"],
  voice_mode="Legato", glide=0.22, oscA_table="Sine Drive", oscA_pos=0.3, oscA_level=0.9, sub_level=0.35,
  penv_amount=7.0, penv_decay=0.06, flt_type="LP24", flt_cutoff=3200.0, flt_keytrack=0.3, menv_decay=1.2,
  amp_decay=3.0, amp_sustain=0.75, amp_release=1.0, dist_type="Fold", dist_drive=0.4, dist_tone=0.5, dist_mix=0.55)
# User: "too quiet". It was short and its pitch-drop peak hit the limiter, so the body could not be raised.
P("cold", "Tom Drop 808", "Bass", "Round tom-like 808 whose pitch falls a full octave and rings on with a tube growl.",
  M(("Drop", [("Pitch A", 0.04)]), ("Drive", [("Dist Drive", 0.35)]), ("Tone", [("Cutoff", 0.4)]), ("Room", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Dist Drive", 0.25), ("Mod Wheel", "Cutoff", 0.3)], tags=["808", "Punch"],
  voice_mode="Legato", glide=0.05, oscA_table="Sine Drive", oscA_pos=0.35, oscA_level=0.9, penv_amount=12.0,
  penv_decay=0.16, flt_type="LP24", flt_cutoff=1800.0, amp_decay=1.4, amp_sustain=0.25, amp_release=0.35,
  dist_type="Tube", dist_drive=0.45, dist_mix=0.6, squash=0.3)

# ---------------------------------------------------------------------------------------------- Lead
P("stadium", "Neon Anthem", "Lead", "Synced saw lead whose edge snaps open at every note and settles as it holds.",
  M(("Bright", [("Cutoff", 0.4)]), ("Edge", [("Warp A", 0.35)]), ("Pulse", [("WT Pos B", 0.5)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Mod Env", "Warp A", 0.45), ("LFO 1", "Pitch", 0.004), ("Mod Wheel", "Warp A", 0.3), ("Velocity", "Cutoff", 0.15)],
  tags=["Bright", "Sync"],
  voice_mode="Legato", glide=0.06, oscA_table="Analog Saw", oscA_warp="Sync", oscA_warp_amt=0.12, oscB_table="PWM",
  oscB_pos=0.3, oscB_level=0.45, oscB_fine=6.0, menv_decay=0.6, menv_sustain=0.15, lfo1_rate=5.4,
  flt_type="LP24", flt_cutoff=5200.0, flt_res=0.15, amp_release=0.3, dly_time="1/8D", dly_mix=0.15, rev_mix=0.12)
P("discohouse", "Laser Harp", "Lead", "Plucked-string harp with a laser zap on the attack and dotted ping-pong echoes.",
  M(("Zap", [("Pitch A", 0.03)]), ("Bright", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Mod Wheel", "Pitch", 0.004), ("Random", "Pan A", 0.25)], tags=["80s", "Pluck"],
  oscA_type="String", oscA_table="PWM", oscA_pos=0.45, str_decay=1.6, str_tone=0.8, penv_amount=12.0, penv_decay=0.03,
  flt_type="LP12", flt_cutoff=7000.0, amp_sustain=1.0, amp_release=0.4,
  dly_mode="PingPong", dly_time="1/8D", dly_feedback=0.4, dly_mix=0.2, rev_mix=0.12)

# ---------------------------------------------------------------------------------------------- Guitar
P("rawhouse", "Fuzzbox Bass Guitar", "Guitar", "Plucked low string driven into a hard fuzz that spits harder the harder you play.",
  M(("Fuzz", [("Dist Drive", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Low", [("Sub Level", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Dist Drive", 0.3), ("Velocity", "Cutoff", 0.2), ("Mod Wheel", "Resonance", 0.3)], tags=["Guitar", "Fuzz"],
  oscA_type="String", oscA_table="Analog Square", oscA_pos=0.2, oscA_oct=-1, str_decay=2.2, str_tone=0.5,
  oscB_table="Analog Saw", oscB_oct=-1, oscB_level=0.2, flt_type="LP24", flt_cutoff=2400.0, flt_res=0.15,
  amp_sustain=1.0, amp_release=0.15, dist_type="Hard", dist_drive=0.6, dist_tone=0.45, dist_mix=0.9)
P("discohouse", "Muted Disco Picking", "Guitar", "Palm-muted string picking in sixteenths, chorused and pushed by the groove.",
  M(("Mute", [("Cutoff", -0.3)]), ("Grit", [("Dist Mix", 0.2)]), ("Echo", [("Delay Mix", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.25), ("Random", "Cutoff", 0.08)], tags=["Guitar", "Disco"],
  arp_on=True, arp_mode="UpDown", arp_rate="1/16", oscA_type="String", oscA_table="Analog Saw",
  oscA_pos=0.3, oscA_level=1.0, str_decay=0.5, str_tone=0.5, flt_type="LP24", flt_cutoff=2600.0, flt_res=0.2, arp_gate=0.5,
  amp_sustain=1.0, amp_release=0.06, mfx_type="Chorus", mfx_mix=0.3, pump_amount=0.35, dly_time="1/16", dly_mix=0.08)

# ---------------------------------------------------------------------------------------------- Keys
P("industrial", "Breaker Keys", "Keys", "FM stab that starts as clean glass and breaks into bit-crushed grit as it decays.",
  M(("Index", [("Warp A", 0.4)]), ("Crush", [("Dist Mix", 0.5)]), ("Tone", [("Cutoff", 0.4)]), ("Room", [("Reverb Mix", 0.3)])),
  mods=[("Mod Env", "Warp A", 0.35), ("Velocity", "Warp A", 0.2), ("Mod Wheel", "Dist Drive", 0.3)], tags=["Stab", "Digital"],
  oscA_table="Basic Shapes", oscA_warp="FM", oscA_warp_amt=0.12, oscB_table="Basic Shapes", oscB_semi=7, oscB_fine=8.0,
  oscB_level=0.0, sub_level=0.15, menv_decay=0.25, flt_type="LP24", flt_cutoff=5500.0, amp_attack=0.004,
  amp_decay=1.3, amp_sustain=0.2, amp_release=0.3, dist_type="Bitcrush", dist_drive=0.3, dist_mix=0.3, squash=0.45,
  rev_mix=0.1)
P("cinematic", "Glass Piano", "Keys", "Struck glass strings that ring like a piano and shimmer with a high bell overtone.",
  M(("Glass", [("WT Pos A", 0.4)]), ("Shimmer", [("Level B", 0.3)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Mod Env", "Level B", 0.35), ("Random", "Pan A", 0.2), ("Mod Wheel", "Mod FX Mix", 0.4)],
  tags=["Piano", "Cinematic"],
  oscA_type="String", oscA_table="Glass Harmonics", oscA_pos=0.6, str_decay=1.8, str_tone=0.95,
  oscB_table="Basic Shapes", oscB_oct=2, oscB_semi=7, oscB_level=0.08, menv_decay=0.8,
  flt_type="LP12", flt_cutoff=12000.0, amp_sustain=1.0, amp_release=0.9,
  dly_mode="PingPong", dly_time="1/8D", dly_feedback=0.45, dly_mix=0.2, rev_size=0.5, rev_mix=0.12)

# ---------------------------------------------------------------------------------------------- Arp
P("industrial", "Sawblade Arp", "Arp", "Metallic comb-filtered buzz arpeggio that rings like a spinning blade.",
  M(("Edge", [("WT Pos A", 0.4)]), ("Grind", [("Dist Drive", 0.4)]), ("Ring", [("Resonance", 0.3)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Filter Env", "Cutoff", 0.3), ("Random", "WT Pos A", 0.3), ("Mod Wheel", "Resonance", 0.3)], tags=["Arp", "Distorted"],
  arp_on=True, arp_mode="UpDown", arp_rate="1/16", arp_octaves=2, arp_gate=0.4, oscA_table="Buzz", oscA_pos=0.3,
  flt_type="Comb-", flt_cutoff=500.0, flt_res=0.6, flt_keytrack=1.0, fenv_decay=0.12, fenv_sustain=0.0,
  amp_decay=0.18, amp_sustain=0.3, dist_type="Fold", dist_drive=0.4, dist_mix=0.5,
  dly_mode="PingPong", dly_time="1/8D", dly_feedback=0.3, dly_mix=0.14)
P("stadium", "Skyline Arp", "Arp", "Short supersaw plucks racing over three octaves, with an octave layer that grows as you hold.",
  M(("Shine", [("Cutoff", 0.4)]), ("Octave", [("Level B", 0.3)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Mod Env", "Level B", 0.5), ("Filter Env", "Cutoff", 0.35), ("Mod Wheel", "Detune", 0.3)], tags=["Supersaw", "Arp"],
  arp_on=True, arp_mode="Up", arp_rate="1/16", arp_octaves=3, oscA_table="Hyper Saw", oscA_pos=0.3,
  oscA_voices=5, uni_detune=0.3, uni_spread=0.9, oscB_table="Hyper Saw", oscB_oct=1, oscB_level=0.0,
  menv_attack=2.5, menv_decay=1.0, menv_sustain=1.0, flt_type="LP24", flt_cutoff=3800.0, fenv_decay=0.08,
  fenv_sustain=0.0, amp_decay=0.12, amp_sustain=0.05, amp_release=0.1, arp_gate=0.3,
  dly_mode="PingPong", dly_time="1/8D", dly_feedback=0.45, dly_mix=0.24, rev_mix=0.12)
P("cinematic", "Pulsing String Ostinato", "Arp", "Spiccato strings bowing a tight ostinato, each stroke a little different.",
  M(("Bow", [("WT Pos A", 0.5)]), ("Tone", [("Cutoff", 0.4)]), ("Ensemble", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.2), ("Random", "Cutoff", 0.08), ("Random", "Pitch", 0.002), ("Mod Wheel", "Resonance", 0.25)],
  tags=["Strings", "Cinematic"],
  arp_on=True, arp_mode="UpDown", arp_rate="1/16", arp_gate=0.5, oscA_table="Strings", oscA_pos=0.6, oscA_voices=3,
  uni_detune=0.2, oscA_level=1.0, flt_type="LP24", flt_cutoff=2800.0, flt_res=0.3, flt_keytrack=0.4, flt_envamt=0.35,
  fenv_decay=0.1, fenv_sustain=0.1, amp_attack=0.004, amp_decay=0.25, amp_sustain=0.35, amp_release=0.12, mfx_type="Chorus",
  mfx_mix=0.25, rev_size=0.6, rev_mix=0.15)
P("cinematic", "Plucked Sequence", "Arp", "FM pluck sequence whose bell tone changes on every step.",
  M(("Index", [("Warp A", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Mod Env", "Warp A", 0.45), ("Random", "Warp A", 0.3), ("Mod Wheel", "Delay Mix", 0.3)], tags=["Sequence", "Cinematic"],
  arp_on=True, arp_mode="UpDown", arp_rate="1/16", arp_octaves=2, arp_gate=0.5, oscA_table="Basic Shapes",
  oscA_warp="FM", oscA_warp_amt=0.1, oscB_table="Basic Shapes", oscB_semi=12, oscB_fine=5.0, oscB_level=0.0,
  menv_decay=0.15, flt_type="LP24", flt_cutoff=5000.0, amp_decay=0.25, amp_sustain=0.0, amp_release=0.15,
  dly_mode="PingPong", dly_time="1/8D", dly_mix=0.18, rev_mix=0.12)

# ---------------------------------------------------------------------------------------------- FX
P("epic", "Dark Orchestra Hit", "FX", "Brass and low strings slam together with a burst of air and a deep thump.",
  M(("Brass", [("WT Pos A", 0.5)]), ("Tone", [("Cutoff", 0.4)]), ("Air", [("Noise Level", 0.2)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Mod Env", "Noise Level", 0.35), ("Mod Wheel", "Dist Drive", 0.3)], tags=["Impact", "Dramatic"],
  oscA_table="Brass", oscA_pos=0.8, oscA_voices=3, oscB_table="Strings", oscB_level=0.6, oscB_oct=-1, sub_level=0.45,
  penv_amount=7.0, penv_decay=0.06, menv_decay=0.12, flt_type="LP24", flt_cutoff=1200.0, flt_envamt=0.55,
  fenv_decay=0.18, fenv_sustain=0.0, amp_decay=0.55, amp_sustain=0.0, amp_release=0.6, dist_type="Tube", dist_drive=0.4,
  dist_mix=0.5, rev_size=0.9, rev_damping=0.8, rev_mix=0.35)
P("rawhouse", "Grinding Sweep", "FX", "Comb-filtered noise sweep that rises into a pitched metallic whine and falls back.",
  M(("Sweep", [("Cutoff", 0.35)]), ("Grind", [("Dist Drive", 0.4)]), ("Ring", [("Resonance", 0.3)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("LFO 1", "Cutoff", 0.45), ("Mod Wheel", "Resonance", 0.3)], tags=["Noise", "Sweep"],
  oscA_table="Rasp", oscA_pos=0.6, oscA_level=0.6, noise_level=0.8, flt_type="Comb+", flt_cutoff=600.0, flt_res=0.7,
  flt_keytrack=1.0, lfo1_sync=True, lfo1_div="1/1", lfo1_shape="Triangle", dist_type="Hard", dist_drive=0.35,
  dist_mix=0.5, amp_attack=0.3, amp_release=0.6, dly_time="1/8", dly_mix=0.12)

FIXES = gp.PRESETS[_start:]
del gp.PRESETS[_start:]  # keep the generators' own lists untouched for importers


def main():
    trims = json.load(open(TRIM_FILE)) if os.path.exists(TRIM_FILE) else {}
    if len(sys.argv) > 2 and sys.argv[1] == "--trim":
        report = json.load(open(sys.argv[2]))
        names = {p["name"] for p in FIXES}
        for r in report["presets"]:
            if r["name"] in names:
                trims[r["name"]] = round(max(-24.0, min(12.0, trims.get(r["name"], 0.0) + TARGET_LUFS - r["loudness_lufs"])), 1)
        json.dump(dict(sorted(trims.items())), open(TRIM_FILE, "w"), indent=1)

    sel = json.load(open(os.path.join(HERE, "selection.json")))
    wanted = set(sel.get("batch1_fix", {})) | set(sel.get("candidates_fix", {}))
    names = [p["name"] for p in FIXES]
    assert set(names) == wanted, set(names) ^ wanted
    banned = gc.banned_words("kBannedEverywhere")
    for p in FIXES:
        text = " | ".join([p["name"], p["description"]] + p["tags"] + p["macros"])
        assert not [w for w in banned if gc.contains_word(text, w)], p["name"]
        d = p["description"]
        assert d.endswith(".") and ". " not in d[:-1], p["name"]

    os.makedirs(OUT_DIR, exist_ok=True)
    for f in os.listdir(OUT_DIR):
        if f.endswith(".json"):
            os.remove(os.path.join(OUT_DIR, f))
    for i, p in enumerate(FIXES, start=1):
        with open(os.path.join(OUT_DIR, f"{i:03d}_{gp.slug(p['name'])}.json"), "w") as f:
            json.dump(preset_doc(p, trims), f, indent=2)
            f.write("\n")
    print("wrote", len(FIXES), "reworked presets to", OUT_DIR)


def preset_doc(p, trims):
    params = dict(p["params"])
    if abs(trims.get(p["name"], 0.0)) > 0.05:
        params["out_gain"] = trims[p["name"]]
    sparse = {k: (round(params[k], 5) if isinstance(params[k], float) else params[k])
              for k in gp.DEFAULTS if k in params and params[k] != gp.DEFAULTS[k]}
    return {"name": p["name"], "category": p["category"], "tags": p["tags"], "description": p["description"],
            "macros": p["macros"], "version": 1, "params": sparse}


if __name__ == "__main__":
    main()
