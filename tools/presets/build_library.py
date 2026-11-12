#!/usr/bin/env python3
"""Builds the factory preset library (presets/*.json + docs/PRESETS.md) from both preset batches.

    python3 tools/presets/build_library.py

Batch 1 = tools/presets/generate_presets.py (120 presets), batch 2 = tools/presets/generate_candidates.py
(100 candidates). The user's listening verdicts live in tools/presets/selection.json: presets marked "remove" /
rejected are left out, everything else (keep and fix) goes in. Level trims come from gain_trims.json and
candidate_trims.json. Presets are ordered by sound category (same order as the plugin's category list), then by
name, so the numbered files, the plugin's preset menu and docs/PRESETS.md all follow the same order.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import generate_candidates as gc  # noqa: E402  (imports generate_presets as gc.gp and defines both batches)
import generate_fixes as gf  # noqa: E402  (reworked versions of the presets marked "fix")

gp = gc.gp
# Must match PresetManager::categories() in Source/PresetManager.cpp.
CATEGORY_ORDER = ["Bass", "Lead", "Guitar", "Pad", "Keys", "Arp", "Brass", "FX"]
CATEGORY_INFO = {
    "Bass": "Suby i 808, basy przesterowane, acid, reese, FM, funkowe i analogowe.",
    "Lead": "Leady mono i poly: supersaw, sync, formantowe, miękkie sinusy, flety i brzmienia solowe.",
    "Guitar": "Brzmienia gitarowe: przester, palm mute, czyste funkowe, slide i sustain.",
    "Pad": "Pady, chóry i smyczki – od zimnych i oszczędnych po szerokie, pompujące i ewoluujące.",
    "Keys": "Pianina, pianina elektryczne, organy, staby i klawisze perkusyjne.",
    "Arp": "Brzmienia z włączonym arpeggiatorem i sekwencje zsynchronizowane z tempem.",
    "Brass": "Sekcje dęte, fanfary, miękkie rogi i syntetyczne brassy.",
    "FX": "Efekty: zapy, przemiatania i uderzenia.",
}


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
    # Reworks replace the original only when the user picked the new version on the listening page.
    accepted = set(sel.get("fixes_accepted", []))
    fixes = {p["name"]: p for p in gf.FIXES if p["name"] in accepted}
    fix_trims = load_json("fix_trims.json", {})
    for name in fixes:
        trims[name] = fix_trims.get(name, 0.0)
    chosen = [fixes.get(p["name"], p) for p in chosen]
    names = [p["name"] for p in chosen]
    assert len(names) == len(set(names)), "duplicate preset names"
    cat = {c: i for i, c in enumerate(CATEGORY_ORDER)}
    assert all(p["category"] in cat for p in chosen), "unknown category"
    chosen.sort(key=lambda p: (cat[p["category"]], p["name"].lower()))
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
    fix = (set(sel.get("batch1_fix", {})) | set(sel.get("candidates_fix", {}))) - set(sel.get("fixes_accepted", []))
    total = len(chosen) + 1
    lines = [
        "# VOLT – presety fabryczne",
        "",
        f"{total} presetów: **Init** + {len(chosen)} brzmień wybranych po odsłuchu. Lista jest ułożona według kategorii",
        "brzmienia, a w kategorii alfabetycznie – tak samo jak w menu presetów pluginu. Presety oznaczone w kolumnie",
        "*Uwaga* jako „do poprawki” zostały wybrane do poprawienia w kolejnym kroku.",
        "",
        "Nazwy, tagi i opisy presetów opisują wyłącznie dźwięk (charakter, styl, technikę) – nie zawierają nazw artystów,",
        "albumów, utworów ani marek; pilnuje tego test jednostkowy. W pluginie filtr tagów pozwala wybrać styl",
        "(np. „Industrial”, „House”, „Cinematic”).",
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
    for num, p in enumerate(chosen, start=1):
        if num == 1 or chosen[num - 2]["category"] != p["category"]:
            count = sum(1 for q in chosen if q["category"] == p["category"])
            lines += ["" if num > 1 else None, f"## {p['category']} ({count})", "", CATEGORY_INFO[p["category"]], "",
                      "| # | Preset | Tagi | Makra | Opis | Uwaga |", "|---|---|---|---|---|---|"]
        mark = "do poprawki" if p["name"] in fix else ""
        lines.append(f"| {num:03d} | {p['name']} | {', '.join(p['tags'])} | "
                     f"{' / '.join(p['macros'])} | {p['description']} | {mark} |")
    lines = [l for l in lines if l is not None]
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
