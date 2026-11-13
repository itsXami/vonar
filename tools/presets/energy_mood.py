#!/usr/bin/env python3
"""Energy level (1 calm .. 5 hits hard) and a proposed mood (Soft, Medium, Sad, Dark, Aggressive) per preset.

    python3 tools/presets/energy_mood.py render/report.json [--json out.json] [--list]

Measured from the rendered audio (VOLT_Render report features), not from the settings: a distortion behind a
dark filter only warms a sound, so it scores nothing here. What counts:
  bite      share of energy between 1 and 8 kHz (absolute, in dB), the range the ear hears as aggressive;
  grit      harmonic density in that range (distortion, supersaw, noise fill it);
  punch     how steeply the notes strike (5 ms envelope rise);
  density   low crest factor (a dense wall) - only when there is bite;
  sub hit   a strong low end that strikes hard (808s, kicks);
minus what softens it: reverb wash and a slow swell. Mood is a proposal; the preset's own mood field wins.
"""
import argparse
import glob
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MOODS = ("Soft", "Medium", "Sad", "Dark", "Aggressive")
SAD_WORDS = ("lonely", "sad", "melanch", "mourn", "lament", "ballad", "grey", "gray", "winter", "cold", "tear", "sigh",
             "distant", "nocturne", "heart", "midnight", "lilting", "whisper", "rain", "regret", "empty")
DARK_WORDS = ("dark", "sinister", "menac", "doom", "ominous", "deep", "cinematic", "black", "industrial", "growl",
              "gong", "drone", "haze", "night", "shadow", "eerie", "horror", "abyss")
LEVEL_EDGES = (0.3, 1.0, 1.8, 2.6)   # energy below 0.3 = level 1 ... 2.6 and above = level 5


def _clamp(x, lo, hi):
    return max(lo, min(hi, x))


def _db(x):
    return 10.0 * math.log10(x + 1.0e-6)


def presets(preset_dir=None):
    out = {}
    for f in glob.glob(os.path.join(preset_dir or os.path.join(ROOT, "presets"), "*.json")):
        d = json.load(open(f))
        out[d["name"]] = d
    return out


def energy(feat, params):
    bite = _clamp((_db(feat["presence"]) + 30.0) / 25.0, 0.0, 1.2)
    grit = _clamp(feat.get("density", 0.0) / 0.4, 0.0, 1.2)
    e = 2.2 * bite * (0.4 + 0.6 * grit)
    e += _clamp((feat["onset_db"] - 8.0) / 24.0, 0.0, 1.0) * (0.4 + 0.6 * bite)
    e += _clamp((14.0 - feat["crest_db"]) / 8.0, 0.0, 1.0) * 0.6 * bite
    e += 0.8 if feat["low_share"] > 0.5 and feat["onset_db"] > 15.0 else 0.0
    e += min(0.4, feat["movement_oct"])
    e -= min(1.0, params.get("rev_mix", 0.0) * 2.5)
    e -= 0.6 if feat["attack_s"] > 0.15 else 0.0
    return e


def level(e):
    return 1 + sum(e >= edge for edge in LEVEL_EDGES)


def tagged_mood(p):
    """The mood stored in the preset (the "mood" field), if any."""
    return p.get("mood") if p.get("mood") in MOODS else None


def mood(p, lvl, feat):
    """Proposal only. Aggressive needs grit as well as energy: a bright clean pluck hits hard but is Medium."""
    text = " ".join([p["name"], p["description"]] + p["tags"]).lower()
    has = lambda words: any(w in text for w in words)
    grit = feat.get("density", 0.0)
    if lvl >= 4 and (grit > 0.25 or feat["noisiness"] > 0.15):
        return "Aggressive"
    if has(SAD_WORDS) and lvl <= 3:
        return "Sad"
    if has(DARK_WORDS) or feat["brightness_oct"] < -1.2:
        return "Dark"
    if lvl <= 2:
        return "Soft"
    return "Medium"


def analyse(report_path, preset_dir=None):
    rep = {p["name"]: p for p in json.load(open(report_path))["presets"]}
    out = []
    for name, p in presets(preset_dir).items():
        if name == "Init" or name not in rep:
            continue
        feat = rep[name]["features"]
        e = energy(feat, p["params"])
        lvl = level(e)
        out.append({"name": name, "category": p["category"], "energy": round(e, 2), "level": lvl,
                    "mood": tagged_mood(p) or mood(p, lvl, feat), "proposed": mood(p, lvl, feat),
                    "tags": p["tags"], "description": p["description"]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report")
    ap.add_argument("--json")
    ap.add_argument("--list", action="store_true", help="print every preset with its level and mood")
    ap.add_argument("--dir", help="preset JSON folder (default presets/), e.g. a batch folder")
    a = ap.parse_args()
    rows = sorted(analyse(a.report, a.dir), key=lambda r: r["energy"])
    n = len(rows)
    if a.list:
        for r in rows:
            print(f"{r['energy']:6.2f}  L{r['level']}  {r['mood']:<10} {r['category']:<9} {r['name']}")
    for key in ("level", "mood"):
        counts = {}
        for r in rows:
            counts[r[key]] = counts.get(r[key], 0) + 1
        print(key, {k: f"{v} ({round(100 * v / n)}%)" for k, v in sorted(counts.items())})
    if a.json:
        json.dump(rows, open(a.json, "w"), indent=1)


if __name__ == "__main__":
    main()
