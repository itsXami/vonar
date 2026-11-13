#!/usr/bin/env python3
"""Finds presets that sound alike, using the timbre fingerprints written by VOLT_Render (report.json "features").

    VOLT_Render --out render-lib --no-previews                       # the current library
    VOLT_Render --dir tools/presets/candidates --out render-new --no-previews
    python3 tools/presets/similarity.py render-lib/report.json                     # duplicates inside the library
    python3 tools/presets/similarity.py render-lib/report.json render-new/report.json   # candidates vs library

Each preset becomes a vector: spectral shape (16 bands), brightness, movement of the timbre, attack, sustain,
noisiness, stereo width and low-end share. Every dimension is scaled by its spread across all presets in the
reports, so the distance is roughly "how many typical differences apart" two sounds are. Pairs closer than
--threshold are reported as too similar; candidates too close to the library or to each other are listed as
"reject" so they never reach the listening page.
"""
import argparse
import json
import math
import statistics

WEIGHTS = {"bands": 1.0, "brightness_oct": 1.5, "movement_oct": 1.5, "attack": 1.0, "sustain": 1.0,
           "noisiness": 1.0, "width": 0.7, "low_share": 0.7}


def vectorise(p):
    f = p["features"]
    v = [("band%d" % i, b, WEIGHTS["bands"] / 4.0) for i, b in enumerate(f["bands_db"])]  # 16 bands ~ weight 4 total
    v += [("brightness_oct", f["brightness_oct"], WEIGHTS["brightness_oct"]),
          ("movement_oct", f["movement_oct"], WEIGHTS["movement_oct"]),
          ("attack", math.log10(f["attack_s"] + 0.005), WEIGHTS["attack"]),
          ("sustain", f["sustain"], WEIGHTS["sustain"]),
          ("noisiness", f["noisiness"], WEIGHTS["noisiness"]),
          ("width", f["width"], WEIGHTS["width"]),
          ("low_share", f["low_share"], WEIGHTS["low_share"])]
    return v


def load(path, origin):
    data = json.load(open(path))
    out = []
    for p in data["presets"]:
        if "features" not in p:
            raise SystemExit(f"{path}: no 'features' – render it again with the current VOLT_Render")
        out.append({"name": p["name"], "category": p["category"], "origin": origin, "vec": vectorise(p)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("library")
    ap.add_argument("candidates", nargs="?")
    ap.add_argument("--threshold", type=float, default=1.2, help="distance below which two presets count as alike")
    ap.add_argument("--json", help="write the verdicts to this file")
    args = ap.parse_args()

    lib = load(args.library, "library")
    cand = load(args.candidates, "candidate") if args.candidates else []
    allp = lib + cand
    dims = len(allp[0]["vec"])
    spread = []
    for d in range(dims):
        vals = [p["vec"][d][1] for p in allp]
        s = statistics.pstdev(vals)
        spread.append(s if s > 1e-9 else 1.0)

    def dist(a, b):
        return math.sqrt(sum(a["vec"][d][2] * ((a["vec"][d][1] - b["vec"][d][1]) / spread[d]) ** 2 for d in range(dims)))

    def nearest(p, pool):
        best = None
        for q in pool:
            if q is p:
                continue
            d = dist(p, q)
            if best is None or d < best[1]:
                best = (q, d)
        return best

    report = {"threshold": args.threshold, "library_pairs": [], "candidates": []}
    pairs = []
    for i, a in enumerate(lib):
        for b in lib[i + 1:]:
            d = dist(a, b)
            if d < args.threshold:
                pairs.append((d, a, b))
    pairs.sort(key=lambda t: t[0])
    print(f"Library: {len(lib)} presets, {len(pairs)} pairs closer than {args.threshold}")
    for d, a, b in pairs[:40]:
        print(f"  {d:4.2f}  {a['name']} ({a['category']})  ~  {b['name']} ({b['category']})")
        report["library_pairs"].append({"distance": round(d, 3), "a": a["name"], "b": b["name"]})

    nn = [nearest(p, lib)[1] for p in lib]
    print(f"Median distance to the nearest other preset: {statistics.median(nn):.2f} (higher = more varied library)")
    cats = sorted({p["category"] for p in lib})
    for c in cats:
        vals = [nearest(p, lib)[1] for p in lib if p["category"] == c]
        print(f"  {c:7s} {len(vals):3d} presets, median nearest distance {statistics.median(vals):.2f}")

    if cand:
        print(f"\nCandidates: {len(cand)}")
        accepted = []
        for p in cand:
            near_lib = nearest(p, lib)
            near_new = nearest(p, accepted) if accepted else None
            verdict = "ok"
            reason = ""
            if near_lib[1] < args.threshold:
                verdict, reason = "reject", f"too close to library preset '{near_lib[0]['name']}' ({near_lib[1]:.2f})"
            elif near_new and near_new[1] < args.threshold:
                verdict, reason = "reject", f"too close to candidate '{near_new[0]['name']}' ({near_new[1]:.2f})"
            else:
                accepted.append(p)
            print(f"  {verdict:6s} {p['name']:28s} nearest library: {near_lib[0]['name']} ({near_lib[1]:.2f}) {reason}")
            report["candidates"].append({"name": p["name"], "verdict": verdict, "reason": reason,
                                         "nearest_library": near_lib[0]["name"], "distance": round(near_lib[1], 3)})
        print(f"{len(accepted)} / {len(cand)} candidates are different enough")

    if args.json:
        json.dump(report, open(args.json, "w"), indent=1)


if __name__ == "__main__":
    main()
