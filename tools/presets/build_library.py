#!/usr/bin/env python3
"""Builds the factory preset library (presets/*.json + docs/PRESETS.md) from both preset batches.

    python3 tools/presets/build_library.py

Batch 1 = tools/presets/generate_presets.py (120 presets), batch 2 = tools/presets/generate_candidates.py
(100 candidates). The user's listening verdicts live in tools/presets/selection.json: presets marked "remove" /
rejected are left out, everything else (keep and fix) goes in. Level trims come from gain_trims.json and
candidate_trims.json. Presets are ordered by inspiration era, so the plugin's list groups them by era.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import generate_candidates as gc  # noqa: E402  (imports generate_presets as gc.gp and defines both batches)

gp = gc.gp
ERA_ORDER = ["yeezus", "graduation", "808s", "mbdtf", "donda", "homework", "discovery", "haa", "tron", "ram"]
CATEGORY_ORDER = ["Bass", "Lead", "Guitar", "Keys", "Pad", "Arp", "Brass", "FX"]


def load_json(name, default):
    path = os.path.join(HERE, name)
    return json.load(open(path)) if os.path.exists(path) else default


def library():
    sel = load_json("selection.json", {})
    removed = set(sel.get("batch1_removed", []))
    rejected = set(sel.get("candidates_rejected", []))
    trims = load_json("gain_trims.json", {})
    trims.update(load_json("candidate_trims.json", {}))
    batch1 = [p for p in gp.PRESETS[:gc.START] if p["name"] not in removed]
    batch2 = [p for p in gc.CANDIDATES if p["name"] not in rejected]
    chosen = batch1 + batch2
    names = [p["name"] for p in chosen]
    assert len(names) == len(set(names)), "duplicate preset names"
    order = {g: i for i, g in enumerate(ERA_ORDER)}
    cat = {c: i for i, c in enumerate(CATEGORY_ORDER)}
    chosen.sort(key=lambda p: (order[p["group"]], cat.get(p["category"], 99)))
    return chosen, trims, sel


def write_presets(chosen, trims):
    for f in os.listdir(gp.PRESET_DIR):
        if f.endswith(".json") and not f.startswith("000_"):
            os.remove(os.path.join(gp.PRESET_DIR, f))
    for i, p in enumerate(chosen, start=1):
        params = dict(p["params"])
        if abs(trims.get(p["name"], 0.0)) > 0.05:
            params["out_gain"] = trims[p["name"]]
        sparse = {k: (round(params[k], 5) if isinstance(params[k], float) else params[k])
                  for k in gp.DEFAULTS if k in params and params[k] != gp.DEFAULTS[k]}
        doc = {"name": p["name"], "category": p["category"], "tags": p["tags"], "description": p["description"],
               "macros": p["macros"], "version": 1, "params": sparse}
        with open(os.path.join(gp.PRESET_DIR, f"{i:03d}_{gp.slug(p['name'])}.json"), "w") as f:
            json.dump(doc, f, indent=2)
            f.write("\n")


def write_docs(chosen, sel):
    fix = set(sel.get("batch1_fix", {})) | set(sel.get("candidates_fix", {}))
    total = len(chosen) + 1
    lines = [
        "# VOLT – presety fabryczne",
        "",
        f"{total} presetów: **Init** + {len(chosen)} brzmień wybranych przez użytkownika po odsłuchu dwóch partii",
        "(pierwsza: 120 presetów, druga: 100 kandydatów z gitarami, pianinami i nowymi leadami). Presety oznaczone",
        "w kolumnie *Uwaga* jako „do poprawki” zostały wybrane do poprawienia w kolejnym kroku.",
        "",
        "*Nazwy* presetów nie zawierają nazwisk artystów, nazw albumów ani tytułów utworów – inspiracja jest zapisana",
        "wyłącznie w tagach i w tym dokumencie. Presety oddają charakter brzmień danej ery (barwa, obróbka, ruch); żaden",
        "nie odtwarza melodii. W pluginie lista jest ułożona według ery, a filtr tagów pozwala wybrać erę (np. „Yeezus”).",
        "",
        "Plik generuje `tools/presets/build_library.py`. Poziomy skorygowano rendererem offline do ok. −15 LUFS.",
        "Każdy preset ma podpięte cztery makra. Opisy są po angielsku, bo tak wyświetla je interfejs pluginu.",
        "",
        "## Init",
        "",
        "| # | Preset | Kategoria | Makra | Opis |",
        "|---|---|---|---|---|",
        "| 000 | Init | Lead | Bright / Morph / Grit / Space | Neutral starting point with one saw oscillator and the four macros pre-wired to tone, morph, grit and space. |",
        "",
    ]
    info = {k: (title, blurb) for k, title, blurb in gp.GROUP_INFO}
    for key in ERA_ORDER:
        group = [p for p in chosen if p["group"] == key]
        if not group:
            continue
        title, blurb = info[key]
        lines += [f"## {title} ({len(group)})", "", blurb, "",
                  "| # | Preset | Kategoria | Tagi | Makra | Opis | Uwaga |", "|---|---|---|---|---|---|---|"]
        for p in group:
            num = chosen.index(p) + 1
            mark = "do poprawki" if p["name"] in fix else ""
            lines.append(f"| {num:03d} | {p['name']} | {p['category']} | {', '.join(p['tags'])} | "
                         f"{' / '.join(p['macros'])} | {p['description']} | {mark} |")
        lines.append("")
    lines += ["## Liczba presetów w kategoriach", "", "| Kategoria | Presety |", "|---|---|"]
    counts = {"Lead": 1}
    for p in chosen:
        counts[p["category"]] = counts.get(p["category"], 0) + 1
    for c in CATEGORY_ORDER:
        lines.append(f"| {c} | {counts.get(c, 0)} |")
    lines.append("")
    with open(os.path.join(gp.ROOT, "docs", "PRESETS.md"), "w") as f:
        f.write("\n".join(lines))


def main():
    chosen, trims, sel = library()
    write_presets(chosen, trims)
    write_docs(chosen, sel)
    cats = {}
    for p in chosen:
        cats[p["category"]] = cats.get(p["category"], 0) + 1
    print(f"wrote Init + {len(chosen)} presets to {gp.PRESET_DIR}: {cats}")


if __name__ == "__main__":
    main()
