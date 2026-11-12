#!/usr/bin/env python3
"""Energy level (1 calm .. 5 hard-hitting) and a proposed mood (Soft, Medium, Sad, Dark, Aggressive) per preset.

    python3 tools/presets/energy_mood.py render/report.json [--json out.json]

Energy comes from what the ear notices first: brightness, a hard attack, distortion, density (squash, pump),
fast movement, minus what softens a sound (long reverb, slow swell). Mood is a proposal for the listening page;
the user's choice there wins. Both are heuristics: they rank and group presets, the ear decides.
"""
import argparse
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SAD_WORDS = ("lonely", "sad", "melanch", "mourn", "lament", "ballad", "grey", "gray", "winter", "cold", "tear", "sigh",
             "distant", "nocturne", "heart", "midnight", "lilting", "whisper")
DARK_WORDS = ("dark", "sinister", "menac", "doom", "ominous", "low", "deep", "cinematic", "epic", "dramatic", "black",
              "industrial", "growl", "gong", "church", "temple", "drone", "haze")
SOFT_WORDS = ("soft", "warm", "felt", "gentle", "sweet", "dream", "velvet", "round", "lo-fi", "tape", "ambient", "airy",
              "breath", "halo", "glass")


def presets():
    out = {}
    for f in glob.glob(os.path.join(ROOT, "presets", "*.json")):
        d = json.load(open(f))
        out[d["name"]] = d
    return out


def energy(feat, params, ref_brightness=-1.0):
    """ref_brightness: median brightness of the preset's category, so a bass is judged against other basses."""
    s = 0.0
    s += max(0.0, min(2.0, feat["brightness_oct"] - ref_brightness))         # bright top (for its category)
    s += 1.5 if feat["attack_s"] < 0.01 else (0.8 if feat["attack_s"] < 0.04 else 0.0)  # hard attack
    dist = params.get("dist_mix", 0.0) * (params.get("dist_drive", 0.3) + 0.2)
    s += min(2.0, dist * 3.0)                                                 # distortion
    s += min(1.0, params.get("squash", 0.0) * 2.0)                            # density
    s += 0.5 if params.get("pump_amount", 0.0) > 0.2 else 0.0                 # pumping
    s += min(0.6, feat["movement_oct"] * 1.5)                                 # movement
    s -= min(1.5, params.get("rev_mix", 0.0) * 5.0)                           # washed out
    s -= 1.0 if params.get("amp_attack", 0.002) > 0.1 else 0.0                # slow swell
    return s


def level(e):
    return 1 if e < 0.9 else 2 if e < 1.9 else 3 if e < 2.9 else 4 if e < 3.9 else 5


def mood(p, lvl, feat):
    text = " ".join([p["name"], p["description"]] + p["tags"]).lower()
    has = lambda words: any(w in text for w in words)
    dist = p["params"].get("dist_mix", 0.0) > 0.35 and p["params"].get("dist_drive", 0.3) > 0.3
    if lvl == 5 or (dist and lvl >= 3) or has(("aggress", "rage", "scream", "riot", "smash")):
        return "Aggressive"
    if has(SAD_WORDS) and lvl <= 3:
        return "Sad"
    if lvl <= 1:
        return "Soft"
    if has(DARK_WORDS) or feat["brightness_oct"] < -0.8:
        return "Dark"
    if lvl == 2 and has(SOFT_WORDS):
        return "Soft"
    return "Medium"


def analyse(report_path):
    rep = {p["name"]: p for p in json.load(open(report_path))["presets"]}
    allp = {n: p for n, p in presets().items() if n != "Init" and n in rep}
    bycat = {}
    for n, p in allp.items():
        bycat.setdefault(p["category"], []).append(rep[n]["features"]["brightness_oct"])
    ref = {c: sorted(v)[len(v) // 2] - 1.0 for c, v in bycat.items()}  # category median sits one step up the scale
    out = []
    for name, p in allp.items():
        feat = rep[name]["features"]
        e = energy(feat, p["params"], ref[p["category"]])
        lvl = level(e)
        out.append({"name": name, "category": p["category"], "energy": round(e, 2), "level": lvl,
                    "mood": mood(p, lvl, feat), "tags": p["tags"], "description": p["description"]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report")
    ap.add_argument("--json")
    a = ap.parse_args()
    rows = analyse(a.report)
    n = len(rows)
    for key in ("level", "mood"):
        counts = {}
        for r in rows:
            counts[r[key]] = counts.get(r[key], 0) + 1
        print(key, {k: f"{v} ({round(100 * v / n)}%)" for k, v in sorted(counts.items())})
    if a.json:
        json.dump(rows, open(a.json, "w"), indent=1)


if __name__ == "__main__":
    main()
