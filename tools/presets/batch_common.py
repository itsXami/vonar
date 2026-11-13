"""Shared plumbing for the stage D batch generators (tools/presets/generate_batch_<name>.py).

A batch module calls `begin()`, defines its presets with `P(...)`, then `CANDIDATES = end(start)`, and its
`main()` calls `write(name, CANDIDATES)`. JSON goes to tools/presets/batches/<name>/, level trims to
batches/<name>_trims.json (`--trim report.json` updates them from a VOLT_Render report).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import generate_candidates as gc  # noqa: E402

gp = gc.gp
M = gc.M
P = gp.P
TARGET_LUFS = -15.0
# Loudness follows the mood: a hard preset may be louder than a calm one (docs/DIAGNOZA_2026-11-12.md, step 2).
# Trims stay mood-neutral (relative to -15 LUFS); the offset is added when the JSON is written.
MOOD_OFFSET_DB = {"Aggressive": 2.5, "Medium": 0.5, "Dark": 0.0, "Sad": -1.0, "Soft": -2.0}


def mood_offset(mood):
    return MOOD_OFFSET_DB.get(mood or "", 0.0)


DRUM_PEAK_DB = -1.0   # drums are trimmed by peak, like one-shot samples (VOLT_Render checks the peak instead of LUFS)


def level_offset(p):
    """Mood loudness offset, none for drums (peak-normalised)."""
    return 0.0 if p.get("category") == "Drums" else mood_offset(p.get("mood"))


def clamp_gain(db):
    """out_gain range of the plugin (-24 .. +12 dB)."""
    return max(-24.0, min(12.0, db))

gp.GROUP_TAGS.update({
    "warm": ["Warm"], "lofi": ["Lo-Fi"], "organ": ["Organ"], "vintage": ["Vintage"], "acoustic": ["Acoustic"],
    "orchestral": ["Orchestral"], "ambient": ["Ambient"], "metallic": ["Metallic"], "electronic": ["Electronic"],
})


def begin():
    return len(gp.PRESETS)


def end(start):
    out = gp.PRESETS[start:]
    del gp.PRESETS[start:]
    return out


def preset_doc(p, trims):
    params = dict(p["params"])
    gain = clamp_gain(trims.get(p["name"], 0.0) + level_offset(p))
    if abs(gain) > 0.05:
        params["out_gain"] = round(gain, 1)
    sparse = {k: (round(params[k], 5) if isinstance(params[k], float) else params[k])
              for k in gp.DEFAULTS if k in params and params[k] != gp.DEFAULTS[k]}
    doc = {"name": p["name"], "category": p["category"], "tags": p["tags"], "description": p["description"]}
    if p.get("mood"):
        doc["mood"] = p["mood"]
    return dict(doc, macros=p["macros"], version=1, params=sparse)


def other_names(exclude_batch):
    """Every preset name outside this batch (both early batches, the fixes and the other stage D batches)."""
    names = {p["name"].lower() for p in gp.PRESETS} | {p["name"].lower() for p in gc.CANDIDATES}
    for f in os.listdir(HERE):
        if f.startswith("generate_batch_") and f.endswith(".py") and f != "generate_batch_" + exclude_batch + ".py":
            mod = __import__(f[:-3])
            names |= {p["name"].lower() for p in mod.CANDIDATES}
    return names


def param_ranges():
    """Numeric ranges of the plugin parameters, read from Source/Params.cpp (F / I specs and the oscillator block)."""
    import re
    src = open(os.path.join(gp.ROOT, "Source", "Params.cpp")).read()
    out = {m.group(2): (float(m.group(3)), float(m.group(4)))
           for m in re.finditer(r'(F|I)\s*\(\s*"([A-Za-z0-9_]+)"\s*,\s*"[^"]*"\s*,\s*(-?[\d.]+)f?\s*,\s*(-?[\d.]+)f?', src)}
    for o in "AB":
        for k, r in {"pos": (0, 1), "oct": (-3, 3), "semi": (-12, 12), "fine": (-100, 100), "level": (0, 1),
                     "pan": (-1, 1), "voices": (1, 8), "warp_amt": (0, 1)}.items():
            out[f"osc{o}_{k}"] = r
    return out


def write(batch, candidates):
    out_dir = os.path.join(HERE, "batches", batch)
    trim_file = os.path.join(HERE, "batches", batch + "_trims.json")
    trims = json.load(open(trim_file)) if os.path.exists(trim_file) else {}
    if len(sys.argv) > 2 and sys.argv[1] == "--trim":
        report = json.load(open(sys.argv[2]))
        by_name = {p["name"]: p for p in candidates}
        for r in report["presets"]:
            if r["name"] in by_name:
                p = by_name[r["name"]]
                if p["category"] == "Drums":
                    delta = DRUM_PEAK_DB - r["peak_dbfs"]
                else:
                    delta = TARGET_LUFS + mood_offset(p.get("mood")) - r["loudness_lufs"]
                trims[r["name"]] = round(max(-24.0, min(12.0, trims.get(r["name"], 0.0) + delta)), 1)
        os.makedirs(os.path.dirname(trim_file), exist_ok=True)
        json.dump(dict(sorted(trims.items())), open(trim_file, "w"), indent=1)

    names = [p["name"] for p in candidates]
    assert len(names) == len(set(names)), "duplicate names in batch"
    clash = [n for n in names if n.lower() in other_names(batch)]
    assert not clash, clash
    bad = [(n, w) for n in names for w in gc.banned_words() if gc.contains_word(n, w)]
    assert not bad, bad
    banned = gc.banned_words("kBannedEverywhere")
    for p in candidates:
        text = " | ".join([p["name"], p["description"]] + p["tags"] + p["macros"])
        assert not [w for w in banned if gc.contains_word(text, w)], p["name"]
        d = p["description"]
        assert d.endswith(".") and ". " not in d[:-1], p["name"]
    ranges = param_ranges()
    for p in candidates:
        for k, v in p["params"].items():
            if k in ranges and isinstance(v, (int, float)) and not isinstance(v, bool):
                lo, hi = ranges[k]
                assert lo - 1e-6 <= v <= hi + 1e-6, (p["name"], k, v, (lo, hi))
    tables = {}
    for p in candidates:
        t = "String" if p["params"].get("oscA_type") == "String" else p["params"].get("oscA_table", "Analog Saw")
        tables[t] = tables.get(t, 0) + 1
    print("oscA sources:", dict(sorted(tables.items(), key=lambda kv: -kv[1])))

    os.makedirs(out_dir, exist_ok=True)
    for f in os.listdir(out_dir):
        if f.endswith(".json"):
            os.remove(os.path.join(out_dir, f))
    for i, p in enumerate(candidates, start=1):
        with open(os.path.join(out_dir, f"{i:03d}_{gp.slug(p['name'])}.json"), "w") as f:
            json.dump(preset_doc(p, trims), f, indent=2)
            f.write("\n")
    print("wrote", len(candidates), "candidates to", out_dir)
