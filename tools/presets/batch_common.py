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
    if abs(trims.get(p["name"], 0.0)) > 0.05:
        params["out_gain"] = trims[p["name"]]
    sparse = {k: (round(params[k], 5) if isinstance(params[k], float) else params[k])
              for k in gp.DEFAULTS if k in params and params[k] != gp.DEFAULTS[k]}
    return {"name": p["name"], "category": p["category"], "tags": p["tags"], "description": p["description"],
            "macros": p["macros"], "version": 1, "params": sparse}


def other_names(exclude_batch):
    """Every preset name outside this batch (both early batches, the fixes and the other stage D batches)."""
    names = {p["name"].lower() for p in gp.PRESETS} | {p["name"].lower() for p in gc.CANDIDATES}
    for f in os.listdir(HERE):
        if f.startswith("generate_batch_") and f.endswith(".py") and f != "generate_batch_" + exclude_batch + ".py":
            mod = __import__(f[:-3])
            names |= {p["name"].lower() for p in mod.CANDIDATES}
    return names


def write(batch, candidates):
    out_dir = os.path.join(HERE, "batches", batch)
    trim_file = os.path.join(HERE, "batches", batch + "_trims.json")
    trims = json.load(open(trim_file)) if os.path.exists(trim_file) else {}
    if len(sys.argv) > 2 and sys.argv[1] == "--trim":
        report = json.load(open(sys.argv[2]))
        names = {p["name"] for p in candidates}
        for r in report["presets"]:
            if r["name"] in names:
                trims[r["name"]] = round(max(-24.0, min(12.0, trims.get(r["name"], 0.0) + TARGET_LUFS - r["loudness_lufs"])), 1)
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
