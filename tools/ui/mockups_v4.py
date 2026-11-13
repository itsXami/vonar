#!/usr/bin/env python3
"""Round 4 of the stage B mock-ups: 3B (Oxanium) with a "made by hand" pass. Writes docs/mockups/volt-ui-4.svg.

Against round 3: warm charcoal surfaces and off-white text instead of blue-black and cool grey, slightly muted
section colours, fine grain on the surfaces, shaded knob caps with a rim, a tick scale on the hero knobs, units set
smaller than the numbers, shape icons, a mark on knobs that a macro moves, bevel lines on panels and displays.

    python3 tools/ui/mockups_v4.py
"""
import math
import os
import re

from mockups import OUT_DIR, W, H, Svg, arc, pt, wave, esc

OSC, FLT, ENV, MOD, MAC = "#3DB8A6", "#E8893F", "#86C26A", "#9C8BE8", "#E4B54A"
BG, S1, S2, S3 = "#0B0A09", "#191817", "#11100F", "#211F1D"       # window, main panels, utility strip, macro bar
INSET, HAIR, GRID = "#090808", "#2D2A27", "#191816"
TEXT, VALUE, LABEL, DIM = "#F0EBE3", "#E3DED5", "#999188", "#655F58"
TRACK, KNOB, FIELD = "#35322E", "#2B2927", "#0E0D0C"


class V(Svg):
    def __init__(self, prefix, font):
        super().__init__(prefix)
        self.font = font

    def num(self, x, y, t, size=11.5, fill=VALUE, anchor="middle", weight=500, op=1):
        m = re.match(r"^([+\-]?[\d.]+)\s?(%|[A-Za-z]+)$", str(t))
        body = (f'{esc(m.group(1))}<tspan font-size="{size * 0.8:.1f}" fill="{LABEL}" dx="1.5">{esc(m.group(2))}</tspan>'
                if m else esc(t))
        self.o.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
                      f'text-anchor="{anchor}" opacity="{op}" style="font-variant-numeric:tabular-nums">{body}</text>')

    def url(self, name):
        return f"url(#{self.prefix}{name})"

    def group(self, op):
        self.o.append(f'<g opacity="{op}">')

    def end(self):
        self.o.append("</g>")

    def out(self, title):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="{self.font}" role="img" '
                f'aria-label="{esc(title)}"><title>{esc(title)}</title><defs>{"".join(self.defs)}</defs>'
                + "".join(self.o) + "</svg>")


def title(s, x, y, t, color, size=12.5):
    s.text(x, y, t, size, color, 600, ls=1.4)


def knob(s, cx, cy, r, v, label, val, color, bipolar=False, dim=False, labels=True, mark=None, scale=None):
    a = -135 + 270 * v
    a0 = 0 if bipolar else -135
    hero = r >= 24
    big = r >= 16
    if dim:
        s.group(0.34)
    ro = r + (4.5 if hero else 3.5)
    sw = 3 if hero else 2
    s.path(arc(cx, cy, ro, -135, 135), stroke=TRACK, sw=sw)
    if abs(a - a0) > 1:
        s.path(arc(cx, cy, ro, a0, a), stroke=color, sw=sw)
    if hero:
        for k in range(11):
            t = -135 + 27 * k
            x0, y0 = pt(cx, cy, ro + 4.5, t)
            x1, y1 = pt(cx, cy, ro + (8.5 if k in (0, 5, 10) else 6.5), t)
            s.line(x0, y0, x1, y1, LABEL if k in (0, 5, 10) else DIM, 1, 1, "butt")
        if scale:
            for t, lab, anc in ((-135, scale[0], "end"), (135, scale[1], "start")):
                tx, ty = pt(cx, cy, ro + 13, t)
                s.text(tx, ty + 6, lab, 9.5, DIM, 500, anc)
    s.circle(cx, cy + 1.5, r + 0.5, "#000000", op=0.55)
    s.circle(cx, cy, r, s.url("kn"), stroke="#0A0908", sw=1)
    s.path(arc(cx, cy, r - 1, -62, 62), stroke="#FFFFFF", sw=1, op=0.11)
    if mark:
        s.circle(cx, cy + ro, 2.4, mark)
    x0, y0 = pt(cx, cy, r * 0.3, a)
    x1, y1 = pt(cx, cy, r - 2.5, a)
    s.line(x0, y0, x1, y1, TEXT, 2.4 if hero else 1.8 if big else 1.5)
    if labels:
        s.text(cx, cy - ro - 7, label, 12.5 if hero else 11.5, TEXT if hero else LABEL, 600 if hero else 500, "middle")
        s.num(cx, cy + ro + (17 if hero else 15), val, 13 if hero else 11.5 if big else 11, VALUE,
              weight=600 if hero else 500)
    if dim:
        s.end()


def dd(s, x, y, w, h, label, color=None):
    s.rect(x, y, w, h, FIELD, rx=2, stroke=HAIR)
    s.text(x + 8, y + h / 2 + 4.2, label, 12, TEXT, 500)
    cx, cy = x + w - 11, y + h / 2
    s.path(f"M{cx - 3} {cy - 1.5}L{cx} {cy + 1.8}L{cx + 3} {cy - 1.5}", stroke=color or DIM, sw=1.4)


def shape_icon(s, x, y, shape, color):
    if shape == "tri":
        s.path(f"M{x} {y + 4}L{x + 4} {y - 4}L{x + 12} {y + 4}L{x + 16} {y - 4}", stroke=color, sw=1.5)
    elif shape == "lp":
        s.path(f"M{x} {y - 3}H{x + 8}Q{x + 12} {y - 3} {x + 16} {y + 4}", stroke=color, sw=1.5)
    else:
        s.path(f"M{x} {y}Q{x + 4} {y - 9} {x + 8} {y}T{x + 16} {y}", stroke=color, sw=1.5)


def seg(s, x, y, labels, active, color, w=56, h=22):
    s.rect(x, y, w * len(labels), h, FIELD, rx=2, stroke=HAIR)
    for k, t in enumerate(labels):
        if k == active:
            s.rect(x + k * w, y, w, h, color, rx=2)
        elif k:
            s.line(x + k * w, y + 5, x + k * w, y + h - 5, HAIR, 1, 1, "butt")
        s.text(x + k * w + w / 2, y + h / 2 + 4, t, 11, "#0B0C0E" if k == active else LABEL, 600, "middle", 0.8)


def display(s, x, y, w, h):
    s.rect(x, y, w, h, INSET, rx=2, stroke="#000000")
    s.line(x + 2, y + h + 1, x + w - 2, y + h + 1, "#FFFFFF", 1, 0.06, "butt")


def wavetable(s, x, y, w, h, color, kind, pos, frames=18):
    display(s, x, y, w, h)
    pad = 14
    dx_tot, dy_tot = w * 0.26, h * 0.44
    ww = w - 2 * pad - dx_tot
    amp = (h - 2 * pad - dy_tot) / 2
    cur = round(pos * (frames - 1))
    n = 110
    for i in range(frames - 1, -1, -1):
        d = i / (frames - 1)
        x0 = x + pad + d * dx_tot
        yc = y + h - pad - amp - d * dy_tot
        base = yc + amp + 2
        pts = [(x0 + ww * k / n, yc - amp * 0.9 * wave(kind, k / n, d)) for k in range(n + 1)]
        line = "M" + "L".join(f"{a:.1f} {b:.1f}" for a, b in pts)
        closed = line + f"L{pts[-1][0]:.1f} {base:.1f}L{pts[0][0]:.1f} {base:.1f}Z"
        s.path(closed, fill=INSET)
        if i == cur:
            s.path(line, stroke=color, sw=6, op=0.16)
            s.path(line, stroke=color, sw=2.2)
        else:
            s.path(line, stroke=color, sw=1, op=0.2 + 0.38 * (1 - d) * (0.6 if i > cur else 1))
    s.num(x + w - 9, y + 17, f"{cur + 1} / {frames}", 11, DIM, "end")


def env_graph(s, x, y, w, h, color, a, d, sus, r):
    display(s, x, y, w, h)
    px, py = 12, 16
    x0, yb, yt = x + px, y + h - py - 8, y + py
    ww = w - 2 * px
    for k in range(1, 4):
        s.line(x0 + ww * k / 4, y + 5, x0 + ww * k / 4, y + h - 5, GRID, 1, 1, "butt")
    for k, lab in enumerate(("0", "0.5 s", "1 s", "1.5 s")):
        s.num(x0 + ww * k / 4 + 4, y + h - 7, lab, 10, DIM, "start")
    xa = x0 + a * ww
    xd = xa + d * ww
    ys = yb - sus * (yb - yt)
    xr0 = x0 + ww * 0.68
    xe = min(x0 + ww, xr0 + r * ww)
    line = (f"M{x0:.1f} {yb:.1f}L{xa:.1f} {yt:.1f}Q{xa + (xd - xa) * 0.22:.1f} {ys:.1f} {xd:.1f} {ys:.1f}"
            f"L{xr0:.1f} {ys:.1f}Q{xr0 + (xe - xr0) * 0.22:.1f} {yb:.1f} {xe:.1f} {yb:.1f}")
    s.path(line + "Z", fill=color, op=0.13)
    s.path(line, stroke=color, sw=2)
    for nx, ny in ((xa, yt), (xd, ys), (xr0, ys), (xe, yb)):
        s.rect(nx - 3.5, ny - 3.5, 7, 7, INSET, rx=1, stroke=color, sw=1.6)


def lfo_graph(s, x, y, w, h, color, shape, cycles, phase):
    display(s, x, y, w, h)
    px, py = 7, 10
    x0, ww = x + px, w - 2 * px
    yc, amp = y + h / 2, h / 2 - py
    s.line(x0, yc, x0 + ww, yc, GRID, 1, 1, "butt")

    def fn(t):
        ph = (t * cycles) % 1
        return 1 - 4 * abs(ph - 0.5) if shape == "tri" else math.sin(2 * math.pi * ph)
    n = 120
    pts = [(x0 + ww * k / n, yc - amp * fn(k / n)) for k in range(n + 1)]
    s.path("M" + "L".join(f"{a:.1f} {b:.1f}" for a, b in pts), stroke=color, sw=1.8)
    k = int(phase * n)
    s.line(pts[k][0], y + 4, pts[k][0], y + h - 4, TEXT, 1, 0.22, "butt")
    s.circle(pts[k][0], pts[k][1], 2.8, TEXT)


def filter_graph(s, x, y, w, h, color, cut, res):
    display(s, x, y, w, h)
    px = 12
    x0, ww = x + px, w - 2 * px
    ytop, ybot = y + 12, y + h - 20
    fmin, fmax = 20.0, 20000.0
    fc = fmin * (fmax / fmin) ** cut
    q = 0.6 + res * 6

    def ypos(db):
        return ytop + (18 - db) / 66 * (ybot - ytop)
    for fr, lab in ((100, "100"), (1000, "1k"), (10000, "10k")):
        gx = x0 + ww * math.log(fr / fmin) / math.log(fmax / fmin)
        s.line(gx, ytop - 5, gx, ybot, GRID, 1, 1, "butt")
        s.num(gx, y + h - 7, lab, 10, DIM)
    for db in (0, -24):
        s.line(x0, ypos(db), x0 + ww, ypos(db), GRID, 1, 1, "butt")
    s.num(x0 + 3, ypos(0) - 4, "0 dB", 10, DIM, "start")
    pts = []
    n = 150
    for k in range(n + 1):
        fr = fmin * (fmax / fmin) ** (k / n)
        rr = fr / fc
        mag = 1 / math.sqrt((1 - rr * rr) ** 2 + (rr / q) ** 2)
        db = 20 * math.log10(mag) + (-12 * math.log2(rr) if rr > 1 else 0)
        pts.append((x0 + ww * k / n, min(ybot, ypos(max(-48, db)))))
    line = "M" + "L".join(f"{a:.1f} {b:.1f}" for a, b in pts)
    s.path(line + f"L{x0 + ww:.1f} {ybot:.1f}L{x0:.1f} {ybot:.1f}Z", fill=s.grad(color, 0.30, 0.02))
    s.path(line, stroke=color, sw=2)


def scope(s, x, y, w, h):
    display(s, x, y, w, h)
    yc, amp = y + h / 2, h / 2 - 12
    s.line(x + 6, yc, x + w - 6, yc, GRID, 1, 1, "butt")
    n = 220
    pts = []
    for k in range(n + 1):
        t = k / n * 3.2
        v = 0.6 * math.sin(2 * math.pi * t) + 0.26 * math.sin(4 * math.pi * t + 0.6) + 0.1 * math.sin(10 * math.pi * t)
        pts.append((x + 6 + (w - 12) * k / n, yc - amp * v))
    s.path("M" + "L".join(f"{a:.1f} {b:.1f}" for a, b in pts), stroke=VALUE, sw=1.5)


def wordmark(s, x, y, hgt=18):
    """Custom-drawn VOLT: straight strokes, and a knob for the O."""
    sw = 3.4
    st = f'fill="none" stroke="{TEXT}" stroke-width="{sw}" stroke-linecap="butt" stroke-linejoin="miter"'
    s.o.append(f'<path d="M{x} {y}L{x + 8.5} {y + hgt}L{x + 17} {y}" {st}/>')
    cx, cy, r = x + 33, y + hgt / 2, hgt / 2 - sw / 2 + 0.6
    s.o.append(f'<path d="{arc(cx, cy, r, -138, 138)}" {st}/>')
    px, py = pt(cx, cy, r - 1, 42)
    s.line(cx, cy, px, py, MAC, 2.6, 1, "butt")
    s.o.append(f'<path d="M{x + 49} {y - 0.2}V{y + hgt - sw / 2}H{x + 61}" {st}/>')
    s.o.append(f'<path d="M{x + 64} {y + sw / 2}H{x + 82}M{x + 73} {y + sw / 2}V{y + hgt}" {st}/>')


def topbar(s):
    s.rect(0, 0, W, 48, "#100F0E")
    s.rect(0, 47, W, 1, "#000")
    wordmark(s, 18, 15)
    x = 130
    for i, t in enumerate(("SYNTH", "MODULATION", "EFFECTS")):
        tw = len(t) * 7.6 + 26
        s.text(x + tw / 2, 29, t, 12, TEXT if i == 0 else DIM, 600, "middle", 1.4)
        if i == 0:
            s.rect(x + 8, 45, tw - 16, 2, TEXT)
        x += tw
    s.rect(446, 9, 380, 30, FIELD, rx=2, stroke=HAIR)
    s.text(460, 29, "KEYS", 11, LABEL, 600, ls=1.4)
    s.line(500, 16, 500, 32, HAIR, 1, 1, "butt")
    s.text(512, 29.5, "Autopan Electric Piano", 15.5, TEXT, 600)
    for k, ch in enumerate("‹›"):
        s.text(782 + k * 24, 31.5, ch, 21, VALUE, 500, "middle")
    dd(s, 838, 13, 96, 22, "All tags")
    s.rect(940, 13, 110, 22, FIELD, rx=2, stroke=HAIR)
    s.text(949, 28.2, "Search", 12, DIM, 400)
    s.rect(1056, 13, 54, 22, "none", rx=2, stroke=LABEL)
    s.text(1083, 28.2, "SAVE", 11, TEXT, 600, "middle", 1.2)
    s.num(1160, 28.2, "100%", 11.5, DIM)


def draw(prefix, font, label):
    s = V(prefix, font)
    s.defs.append(
        f'<linearGradient id="{prefix}kn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3A3734"/>'
        f'<stop offset="1" stop-color="#201E1C"/></linearGradient>'
        f'<filter id="{prefix}grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" '
        f'baseFrequency="0.85" numOctaves="2" seed="7"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 0.96  0 0 0 0 0.9  '
        f'0 0 0 0.075 0"/></filter>')
    s.rect(0, 0, W, H, BG)
    topbar(s)
    # ---- oscillators: one surface, two rows, no header strips
    s.rect(6, 54, 590, 420, S1, rx=3)
    s.line(20, 264, 582, 264, HAIR, 1, 1, "butt")
    for i, (name, table, kind, pos, mode) in enumerate((("OSC A", "Glass Harmonics", "bell", 0.33, "Sync"),
                                                        ("OSC B", "Analog Saw", "saw", 0.17, "Off"))):
        x, y = 6, 54 + i * 210
        title(s, x + 14, y + 25, name, OSC)
        dd(s, x + 74, y + 10, 184, 22, table, OSC)
        dd(s, x + 264, y + 10, 104, 22, "Wavetable", OSC)
        wavetable(s, x + 10, y + 40, 280, 160, OSC, kind, pos)
        xr = x + 306
        knob(s, xr + 40, y + 88, 26, pos, "Position", f"{round(pos * 100)}%", OSC, mark=MAC if i == 0 else None)
        knob(s, xr + 122, y + 94, 18, 0.4 if i == 0 else 0, "Warp", "40%" if i == 0 else "0%", OSC, dim=(i == 1))
        s.text(xr + 166, y + 82, "Warp mode", 11.5, LABEL, 500)
        dd(s, xr + 166, y + 89, 108, 22, mode, OSC)
        small = [("Octave", "0" if i == 0 else "+1", 0.5 if i == 0 else 0.62, True), ("Semi", "0", 0.5, True),
                 ("Fine", "0 ct" if i == 0 else "+7 ct", 0.5 if i == 0 else 0.56, True),
                 ("Level", "80%" if i == 0 else "45%", 0.8 if i == 0 else 0.45, False), ("Pan", "C", 0.5, True),
                 ("Unison", "4" if i == 0 else "2", 0.45 if i == 0 else 0.15, False)]
        for k, (lab, val, v, bi) in enumerate(small):
            knob(s, xr + 22 + k * 46, y + 176, 10, v, lab, val, OSC, bipolar=bi)
    # ---- filter: cutoff is the hero control
    x, y = 598, 54
    s.rect(x, y, 596, 212, S1, rx=3)
    title(s, x + 14, y + 25, "FILTER", FLT)
    dd(s, x + 86, y + 10, 112, 22, "", FLT)
    shape_icon(s, x + 95, y + 21, "lp", FLT)
    s.text(x + 120, y + 25.2, "LP24", 12, TEXT, 500)
    filter_graph(s, x + 10, y + 40, 280, 162, FLT, 0.62, 0.32)
    xr = x + 306
    knob(s, xr + 54, y + 88, 29, 0.62, "Cutoff", "2.40 kHz", FLT, mark=MAC, scale=("20", "20k"))
    knob(s, xr + 150, y + 96, 18, 0.32, "Resonance", "32%", FLT)
    knob(s, xr + 232, y + 96, 18, 0.18, "Drive", "18%", FLT)
    for k, (lab, val, v, bi, cx) in enumerate((("Keytrack", "40%", 0.4, False, 54), ("Env amount", "+35%", 0.68, True, 150),
                                                ("Vowel", "0%", 0.0, False, 232))):
        knob(s, xr + cx, y + 182, 10, v, lab, val, FLT, bipolar=bi, dim=(k == 2))
    # ---- envelopes
    x, y = 598, 268
    s.rect(x, y, 596, 206, S1, rx=3)
    title(s, x + 14, y + 25, "ENVELOPES", ENV)
    seg(s, x + 118, y + 10, ("AMP", "FILTER", "MOD", "PITCH"), 0, ENV)
    env_graph(s, x + 10, y + 40, 364, 156, ENV, 0.04, 0.3, 0.55, 0.22)
    xr = x + 388
    for k, (lab, val, v) in enumerate((("Attack", "12 ms", 0.1), ("Decay", "480 ms", 0.45), ("Sustain", "55%", 0.55),
                                       ("Release", "260 ms", 0.4))):
        knob(s, xr + 50 + (k % 2) * 100, y + 78 + (k // 2) * 84, 16, v, lab, val, ENV)
    # ---- utility strip: darker, unboxed, grouped by proximity
    y = 476
    s.rect(6, y, 1188, 108, S2, rx=3)
    groups = (("UNISON", OSC, 6, (("Detune", "25%", 0.25, False), ("Spread", "50%", 0.5, False))),
              ("SUB · NOISE", OSC, 150, (("Sub", "30%", 0.3, False), ("Noise", "0%", 0.0, False))),
              ("STRING", OSC, 294, (("Decay", "1.50 s", 0.4, True), ("Tone", "60%", 0.6, True))))
    for name, color, gx, knobs in groups:
        title(s, gx + 14, y + 22, name, color, 11.5)
        for k, (lab, val, v, dim) in enumerate(knobs):
            knob(s, gx + 44 + k * 58, y + 66, 11, v, lab, val, color, dim=dim)
        s.line(gx + 144, y + 14, gx + 144, y + 94, HAIR, 1, 1, "butt")
    for i, (name, shape, lab) in enumerate((("LFO 1", "sine", "Sine"), ("LFO 2", "tri", "Triangle"))):
        gx = 438 + i * 262
        title(s, gx + 14, y + 22, name, MOD, 11.5)
        shape_icon(s, gx + 64, y + 18, shape, MOD)
        s.text(gx + 88, y + 22, lab, 12, TEXT, 500)
        s.text(gx + 248, y + 22, "SYNC" if i == 0 else "FREE", 11, MOD if i == 0 else DIM, 600, "end", 1)
        lfo_graph(s, gx + 14, y + 34, 118, 62, MOD, shape, 1.0 if i == 0 else 2.0, 0.3)
        knob(s, gx + 168, y + 66, 11, 0.45 + i * 0.15, "Rate", "1/4" if i == 0 else "3.2 Hz", MOD)
        knob(s, gx + 222, y + 66, 11, 0.7, "Depth", "70%", MOD)
        s.line(gx + 262, y + 14, gx + 262, y + 94, HAIR, 1, 1, "butt")
    gx = 962
    title(s, gx + 14, y + 22, "VOICE", MOD, 11.5)
    dd(s, gx + 14, y + 34, 86, 22, "Poly", MOD)
    s.text(gx + 14, y + 80, "Glide", 11.5, LABEL, 500)
    s.num(gx + 100, y + 80, "0 ms", 11.5, VALUE, "end")
    s.rect(gx + 14, y + 89, 86, 3, TRACK, rx=1.5)
    s.rect(gx + 14, y + 85, 3, 11, TEXT, rx=1)
    s.line(gx + 114, y + 14, gx + 114, y + 94, HAIR, 1, 1, "butt")
    gx = 1076
    title(s, gx + 14, y + 22, "ARP", MOD, 11.5)
    s.text(gx + 106, y + 22, "ON", 11, MOD, 600, "end", 1)
    dd(s, gx + 14, y + 34, 92, 22, "Up", MOD)
    dd(s, gx + 14, y + 62, 92, 22, "1/16", MOD)
    # ---- macro bar: the performance area, lighter surface, knob + what it controls
    y = 586
    s.rect(6, y, 740, 148, S3, rx=3)
    title(s, 20, y + 25, "MACROS", MAC)
    macros = (("Bark", 0.35, "WT Pos A"), ("Tone", 0.5, "Cutoff"), ("Tremolo", 0.0, "Mod FX Mix"), ("Room", 0.2, "Reverb Mix"))
    for k, (name, v, target) in enumerate(macros):
        cx = 58 + k * 180
        knob(s, cx, y + 90, 27, v, "", "", MAC, labels=False)
        s.text(cx + 46, y + 80, name, 17, TEXT, 600)
        s.text(cx + 46, y + 98, target, 11.5, LABEL, 500)
        s.num(cx + 46, y + 117, f"{round(v * 100)}%", 13, MAC, "start", 600)
    # ---- output and scope: neutral, no hue
    s.rect(748, y, 446, 148, S1, rx=3)
    title(s, 762, y + 25, "OUTPUT", LABEL)
    knob(s, 800, y + 90, 20, 0.66, "", "", VALUE, labels=False)
    s.num(800, y + 134, "0.0 dB", 12, VALUE)
    for k in range(2):
        mx = 846 + k * 11
        s.rect(mx, y + 40, 7, 96, INSET, rx=1, stroke="#000000")
        lvl = 60 - k * 7
        s.rect(mx + 1.5, y + 40 + 96 - lvl, 4, lvl - 1.5, VALUE, rx=0.5)
        s.rect(mx + 1.5, y + 40 + 96 - lvl - 11, 4, 1.5, MAC)
    scope(s, 884, y + 40, 300, 96)
    for px, py, pw in ((6, 54, 590), (598, 54, 596), (598, 268, 596), (6, 586, 740), (748, 586, 446)):
        s.line(px + 3, py + 0.5, px + pw - 3, py + 0.5, "#FFFFFF", 1, 0.06, "butt")
    s.o.append(f'<rect x="0" y="0" width="{W}" height="{H}" filter="{s.url("grain")}" pointer-events="none"/>')
    return s.out(label)


FONT = "Oxanium, 'Trebuchet MS', sans-serif"


def build():
    return draw("k", FONT, "Makieta 4: Oxanium, wersja dopracowana")


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "volt-ui-4.svg"), "w") as fh:
        fh.write(build() + "\n")
    print("wrote volt-ui-4.svg")
