#!/usr/bin/env python3
"""Draws the three UI direction mock-ups for stage B (docs/mockups/volt-ui-*.svg).

    python3 tools/ui/mockups.py                 # write the three SVG files
    python3 tools/ui/mockups.py --html out.html # also write a comparison page fragment

The mock-ups are static vector drawings of the 1200x740 editor window. They show layout, colour and the kind of
graphics each direction needs; they are not screenshots of the plugin.
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.join(ROOT, "docs", "mockups")
FONT = "Inter, 'Segoe UI', system-ui, sans-serif"
W, H = 1200, 740


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Theme:
    def __init__(self, **kw):
        self.__dict__.update(kw)


class Svg:
    def __init__(self, prefix):
        self.o, self.defs, self.prefix, self.n = [], [], prefix, 0

    def rect(self, x, y, w, h, fill, rx=0, stroke=None, sw=1, op=1):
        s = f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"'
        if stroke:
            s += f' stroke="{stroke}" stroke-width="{sw}"'
        if op != 1:
            s += f' opacity="{op}"'
        self.o.append(s + "/>")

    def line(self, x1, y1, x2, y2, stroke, sw=1, op=1, cap="round"):
        self.o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" '
                      f'stroke-width="{sw}" stroke-linecap="{cap}" opacity="{op}"/>')

    def text(self, x, y, t, size=11, fill="#fff", weight=400, anchor="start", ls=0, op=1):
        self.o.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
                      f'text-anchor="{anchor}" letter-spacing="{ls}" opacity="{op}">{esc(t)}</text>')

    def path(self, d, fill="none", stroke=None, sw=1.0, op=1):
        s = f'<path d="{d}" fill="{fill}" opacity="{op}"'
        if stroke:
            s += f' stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"'
        self.o.append(s + "/>")

    def circle(self, cx, cy, r, fill, stroke=None, sw=1, op=1):
        s = f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" opacity="{op}"'
        if stroke:
            s += f' stroke="{stroke}" stroke-width="{sw}"'
        self.o.append(s + "/>")

    def grad(self, color, o1=0.35, o2=0.0):
        self.n += 1
        gid = f"{self.prefix}g{self.n}"
        self.defs.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{color}" '
                         f'stop-opacity="{o1}"/><stop offset="1" stop-color="{color}" stop-opacity="{o2}"/></linearGradient>')
        return f"url(#{gid})"

    def out(self, title):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="{FONT}" role="img" '
                f'aria-label="{esc(title)}"><title>{esc(title)}</title><defs>{"".join(self.defs)}</defs>'
                + "".join(self.o) + "</svg>")


# ----------------------------------------------------------------------------------------------- widgets
def pt(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.sin(a), cy - r * math.cos(a)


def arc(cx, cy, r, a0, a1):
    if a1 < a0:
        a0, a1 = a1, a0
    x0, y0 = pt(cx, cy, r, a0)
    x1, y1 = pt(cx, cy, r, a1)
    return f"M{x0:.2f} {y0:.2f}A{r:.2f} {r:.2f} 0 {1 if a1 - a0 > 180 else 0} 1 {x1:.2f} {y1:.2f}"


def knob(s, T, cx, cy, r, v, label, val, color=None, bipolar=False, dim=False):
    color = color or T.accent
    a = -135 + 270 * v
    op = 0.38 if dim else 1
    if T.knob_style == "disc":
        s.path(arc(cx, cy, r + 4, -135, 135), stroke=T.track, sw=2.4, op=op)
        if abs(a - (0 if bipolar else -135)) > 1:
            s.path(arc(cx, cy, r + 4, 0 if bipolar else -135, a), stroke=color, sw=2.4, op=op)
        s.circle(cx, cy, r, T.knob, op=op)
        x0, y0 = pt(cx, cy, r * 0.42, a)
        x1, y1 = pt(cx, cy, r * 0.84, a)
        s.line(x0, y0, x1, y1, T.text, 2, op)
    elif T.knob_style == "ring":
        sw = 4.2 if r > 18 else 3.2
        s.circle(cx, cy, r - sw - 1.5, T.knob, op=op)
        s.path(arc(cx, cy, r, -135, 135), stroke=T.track, sw=sw, op=op)
        if abs(a - (0 if bipolar else -135)) > 1:
            s.path(arc(cx, cy, r, 0 if bipolar else -135, a), stroke=color, sw=sw, op=op)
        x, y = pt(cx, cy, r - sw - 6.5 if r > 18 else r - sw - 4.5, a)
        s.circle(x, y, 2.2 if r > 18 else 1.7, T.text, op=op)
    else:  # cap
        s.path(arc(cx, cy, r + 5, -135, 135), stroke=T.track, sw=1.6, op=op)
        if abs(a - (0 if bipolar else -135)) > 1:
            s.path(arc(cx, cy, r + 5, 0 if bipolar else -135, a), stroke=color, sw=2.6, op=op)
        s.circle(cx, cy, r, T.knob, stroke=T.knob_edge, sw=1, op=op)
        x0, y0 = pt(cx, cy, r * 0.5, a)
        x1, y1 = pt(cx, cy, r - 2, a)
        s.line(x0, y0, x1, y1, color, 2.4, op)
    big = r >= 20
    off = 5 if T.knob_style != "ring" else 0
    s.text(cx, cy - r - off - 7, label, 11 if big else 10, T.text if big else T.dim, 600 if big else 500, "middle", op=op)
    s.text(cx, cy + r + off + (16 if big else 14), val, 11 if big else 10, T.dim if not big else T.text, 500, "middle", op=op)


def dropdown(s, T, x, y, w, h, label, color=None):
    s.rect(x, y, w, h, T.field, rx=T.rx_small, stroke=T.field_edge)
    s.text(x + 9, y + h / 2 + 4, label, 11, T.text, 500)
    cx, cy = x + w - 12, y + h / 2
    s.path(f"M{cx - 3.5} {cy - 1.5}L{cx} {cy + 2}L{cx + 3.5} {cy - 1.5}", stroke=color or T.dim, sw=1.5)


def pill(s, T, x, y, w, h, label, on=False, color=None):
    color = color or T.accent
    s.rect(x, y, w, h, color if on else T.field, rx=h / 2 if T.rx_small > 3 else T.rx_small,
           stroke=None if on else T.field_edge, op=1)
    s.text(x + w / 2, y + h / 2 + 3.6, label, 10, T.on_accent if on else T.dim, 600, "middle", 0.4)


def panel(s, T, x, y, w, h, title=None, color=None, note=None):
    s.rect(x, y, w, h, T.panel, rx=T.rx, stroke=T.panel_edge)
    if title:
        s.text(x + 12, y + 20, title, 10.5, color or T.title, 700, ls=0.9)
    if note:
        s.text(x + w - 12, y + 20, note, 10, T.dim, 500, "end")


def wave(kind, t, m):
    """One cycle of a morphing table: t = phase 0..1, m = frame 0..1."""
    if kind == "saw":
        saw = 1 - 2 * t
        sq = math.tanh(6 * math.sin(2 * math.pi * t)) * 0.9
        return (1 - m) * saw + m * (0.6 * sq + 0.4 * math.sin(6 * math.pi * t + 1.2 * m))
    if kind == "bell":
        return math.sin(2 * math.pi * t + (0.3 + 3.2 * m) * math.sin(4 * math.pi * t)) * (1 - 0.25 * m)
    return math.sin(2 * math.pi * t) * (1 - 0.5 * m) + m * 0.5 * math.sin(6 * math.pi * t)


def wavetable(s, T, x, y, w, h, color, kind="saw", pos=0.3, frames=13, pad=14, depth=(0.22, 0.42)):
    s.rect(x, y, w, h, T.inset, rx=T.rx_small, stroke=T.inset_edge)
    dx_tot, dy_tot = w * depth[0], h * depth[1]
    ww = w - 2 * pad - dx_tot
    amp = (h - 2 * pad - dy_tot) / 2
    cur = round(pos * (frames - 1))
    n = 96
    for i in range(frames - 1, -1, -1):
        d = i / (frames - 1)
        x0 = x + pad + d * dx_tot
        yc = y + h - pad - amp - d * dy_tot
        pts = [(x0 + ww * k / n, yc - amp * 0.92 * wave(kind, k / n, d)) for k in range(n + 1)]
        dpath = "M" + "L".join(f"{px:.1f} {py:.1f}" for px, py in pts)
        if i == cur:
            base = yc + amp
            s.path(dpath + f"L{pts[-1][0]:.1f} {base:.1f}L{pts[0][0]:.1f} {base:.1f}Z", fill=s.grad(color, 0.30, 0.02))
            s.path(dpath, stroke=color, sw=2.2)
        else:
            s.path(dpath, stroke=color if T.wt_tint else T.dim, sw=1, op=0.16 + 0.34 * (1 - abs(i - cur) / frames))


def env_graph(s, T, x, y, w, h, color, a=0.12, d=0.25, sus=0.6, r=0.25, nodes=True, grid=True):
    s.rect(x, y, w, h, T.inset, rx=T.rx_small, stroke=T.inset_edge)
    px, py = 8, 9
    x0, yb, yt = x + px, y + h - py, y + py
    ww = w - 2 * px
    xa = x0 + a * ww
    xd = xa + d * ww
    ys = yb - sus * (yb - yt)
    xr0 = x0 + ww * 0.72
    xe = min(x0 + ww, xr0 + r * ww)
    if grid:
        for k in range(1, 4):
            s.line(x0 + ww * k / 4, yt, x0 + ww * k / 4, yb, T.grid, 1, 1, "butt")
    dpath = (f"M{x0:.1f} {yb:.1f}L{xa:.1f} {yt:.1f}Q{xa + (xd - xa) * 0.25:.1f} {ys:.1f} {xd:.1f} {ys:.1f}"
             f"L{xr0:.1f} {ys:.1f}Q{xr0 + (xe - xr0) * 0.25:.1f} {yb:.1f} {xe:.1f} {yb:.1f}")
    s.path(dpath + "Z", fill=s.grad(color, 0.30, 0.03))
    s.path(dpath, stroke=color, sw=2)
    if nodes:
        for nx, ny in ((xa, yt), (xd, ys), (xr0, ys), (xe, yb)):
            s.circle(nx, ny, 3, T.inset, stroke=color, sw=1.6)


def lfo_graph(s, T, x, y, w, h, color, shape="sine", cycles=2.0, phase=0.3):
    s.rect(x, y, w, h, T.inset, rx=T.rx_small, stroke=T.inset_edge)
    px, py = 8, 10
    x0, ww = x + px, w - 2 * px
    yc, amp = y + h / 2, h / 2 - py
    s.line(x0, yc, x0 + ww, yc, T.grid, 1, 1, "butt")

    def f(t):
        ph = (t * cycles) % 1
        if shape == "tri":
            return 1 - 4 * abs(ph - 0.5)
        if shape == "saw":
            return 1 - 2 * ph
        return math.sin(2 * math.pi * ph)
    n = 120
    pts = [(x0 + ww * k / n, yc - amp * f(k / n)) for k in range(n + 1)]
    dpath = "M" + "L".join(f"{a:.1f} {b:.1f}" for a, b in pts)
    s.path(dpath + f"L{x0 + ww:.1f} {yc:.1f}L{x0:.1f} {yc:.1f}Z", fill=s.grad(color, 0.22, 0.04))
    s.path(dpath, stroke=color, sw=2)
    k = int(phase * n)
    s.line(pts[k][0], y + 5, pts[k][0], y + h - 5, T.text, 1, 0.35, "butt")
    s.circle(pts[k][0], pts[k][1], 3.2, T.text)


def filter_graph(s, T, x, y, w, h, color, cut=0.62, res=0.45, labels=True):
    s.rect(x, y, w, h, T.inset, rx=T.rx_small, stroke=T.inset_edge)
    px = 8
    x0, ww = x + px, w - 2 * px
    ytop, ybot = y + 8, y + h - (16 if labels else 8)
    fmin, fmax = 20.0, 20000.0
    fc = fmin * (fmax / fmin) ** cut
    q = 0.6 + res * 6

    def ypos(db):
        return ytop + (18 - db) / 66 * (ybot - ytop)
    for f, lab in ((100, "100"), (1000, "1k"), (10000, "10k")):
        gx = x0 + ww * math.log(f / fmin) / math.log(fmax / fmin)
        s.line(gx, ytop, gx, ybot, T.grid, 1, 1, "butt")
        if labels:
            s.text(gx, y + h - 5, lab, 9, T.dim, 500, "middle")
    s.line(x0, ypos(0), x0 + ww, ypos(0), T.grid, 1, 1, "butt")
    pts = []
    n = 140
    for k in range(n + 1):
        f = fmin * (fmax / fmin) ** (k / n)
        rr = f / fc
        mag = 1 / math.sqrt((1 - rr * rr) ** 2 + (rr / q) ** 2)
        db = 20 * math.log10(mag) + (-12 * math.log2(rr) if rr > 1 else 0)
        pts.append((x0 + ww * k / n, min(ybot, ypos(max(-48, db)))))
    dpath = "M" + "L".join(f"{a:.1f} {b:.1f}" for a, b in pts)
    s.path(dpath + f"L{x0 + ww:.1f} {ybot:.1f}L{x0:.1f} {ybot:.1f}Z", fill=s.grad(color, 0.30, 0.03))
    s.path(dpath, stroke=color, sw=2)


def scope(s, T, x, y, w, h, color):
    s.rect(x, y, w, h, T.inset, rx=T.rx_small, stroke=T.inset_edge)
    yc, amp = y + h / 2, h / 2 - 9
    s.line(x + 6, yc, x + w - 6, yc, T.grid, 1, 1, "butt")
    n = 200
    pts = []
    for k in range(n + 1):
        t = k / n * 3.2
        v = 0.62 * math.sin(2 * math.pi * t) + 0.25 * math.sin(4 * math.pi * t + 0.6) + 0.12 * math.sin(10 * math.pi * t)
        pts.append((x + 6 + (w - 12) * k / n, yc - amp * v))
    s.path("M" + "L".join(f"{a:.1f} {b:.1f}" for a, b in pts), stroke=color, sw=1.6)


def bolt(s, x, y, color, k=1.0):
    p = [(7, 0), (0, 11), (5, 11), (3, 20), (11, 8), (6, 8)]
    s.path("M" + "L".join(f"{x + a * k:.1f} {y + b * k:.1f}" for a, b in p) + "Z", fill=color)


def topbar(s, T, h, tabs, active, tab_style):
    s.rect(0, 0, W, h, T.bar)
    s.line(0, h, W, h, T.panel_edge or T.track, 1, 1, "butt")
    cy = h / 2
    bolt(s, 18, cy - 10, T.accent)
    s.text(36, cy + 6, "VOLT", 17, T.text, 800, ls=2.4)
    x = 116
    for i, t in enumerate(tabs):
        tw = len(t) * 7.4 + 26
        if tab_style == "pill":
            s.rect(x, cy - 13, tw, 26, T.accent if i == active else "none", rx=13,
                   stroke=None if i == active else T.field_edge)
            s.text(x + tw / 2, cy + 4, t, 10.5, T.on_accent if i == active else T.dim, 700, "middle", 0.8)
            x += tw + 6
        else:
            s.text(x + tw / 2, cy + 4, t, 10.5, T.text if i == active else T.dim, 700, "middle", 0.9)
            if i == active:
                s.rect(x + 8, h - 3, tw - 16, 3, T.accent, rx=1.5)
            x += tw + 2
    for i, ch in enumerate("‹›"):
        bx = 462 + i * 30
        s.rect(bx, cy - 13, 26, 26, T.field, rx=T.rx_small, stroke=T.field_edge)
        s.text(bx + 13, cy + 5, ch, 15, T.text, 500, "middle")
    s.rect(524, cy - 13, 318, 26, T.field, rx=T.rx_small, stroke=T.field_edge)
    s.text(536, cy + 4, "KEYS", 9.5, T.accent, 700, ls=1)
    s.text(574, cy + 4.5, "Autopan Electric Piano", 12.5, T.text, 600)
    s.path(f"M{826 - 3.5} {cy - 1.5}L826 {cy + 2}L{826 + 3.5} {cy - 1.5}", stroke=T.dim, sw=1.5)
    dropdown(s, T, 850, cy - 13, 104, 26, "All tags")
    s.rect(962, cy - 13, 112, 26, T.field, rx=T.rx_small, stroke=T.field_edge)
    s.text(972, cy + 4, "Search…", 11, T.dim, 400)
    s.rect(1082, cy - 13, 50, 26, "none", rx=T.rx_small, stroke=T.accent, sw=1.2)
    s.text(1107, cy + 4, "SAVE", 10, T.accent, 700, "middle", 0.8)
    s.text(1166, cy + 4, "100%", 10.5, T.dim, 500, "middle")


# ----------------------------------------------------------------------------------------------- variant 1
def variant1():
    T = Theme(bg="#0D0F13", bar="#12151A", panel="#161A20", panel_edge=None, inset="#0A0C0F", inset_edge="#1C222A",
              text="#E8ECF2", dim="#7F8A98", title="#AEB8C6", accent="#45C8FF", on_accent="#04202E",
              track="#2A313B", knob="#232A33", knob_edge="#2F3742", field="#1D232B", field_edge="#2A313B",
              grid="#171C23", rx=10, rx_small=6, knob_style="disc", wt_tint=True)
    s = Svg("a")
    s.rect(0, 0, W, H, T.bg)
    topbar(s, T, 52, ["SYNTH", "MATRIX", "ARP", "EFFECTS"], 0, "underline")
    A = T.accent
    for i, (name, table, kind, pos, vals) in enumerate((
            ("OSC A", "Glass Harmonics", "bell", 0.33, (0.33, 0.4, 0.5, 0.5, 0.5, 0.8, 0.5, 0.45)),
            ("OSC B", "Analog Saw", "saw", 0.17, (0.17, 0.0, 0.62, 0.5, 0.56, 0.45, 0.5, 0.15)))):
        x = 12 + i * 384
        panel(s, T, x, 62, 372, 292, name)
        dropdown(s, T, x + 76, 70, 176, 22, table)
        dropdown(s, T, x + 260, 70, 100, 22, "Wavetable")
        wavetable(s, T, x + 12, 100, 348, 118, A, kind, pos)
        knob(s, T, x + 50, 272, 24, vals[0], "Position", f"{round(vals[0] * 100)}%")
        knob(s, T, x + 132, 272, 24, vals[1], "Warp · Sync" if i == 0 else "Warp · Off", f"{round(vals[1] * 100)}%",
             dim=(i == 1))
        small = [("Octave", "0" if i == 0 else "+1", vals[2], True), ("Semi", "0", vals[3], True),
                 ("Fine", "0 ct" if i == 0 else "+7 ct", vals[4], True),
                 ("Level", f"{round(vals[5] * 100)}%", vals[5], False), ("Pan", "0%", vals[6], True),
                 ("Unison", "4" if i == 0 else "2", vals[7], False)]
        for k, (lab, val, v, bi) in enumerate(small):
            knob(s, T, x + 214 + (k % 3) * 58, 244 + (k // 3) * 70, 12, v, lab, val, bipolar=bi)
    x = 780
    panel(s, T, x, 62, 408, 292, "FILTER")
    dropdown(s, T, x + 70, 70, 110, 22, "LP24")
    s.text(x + 396, 85, "2.40 kHz", 11, T.text, 600, "end")
    filter_graph(s, T, x + 12, 100, 384, 118, A)
    for k, (lab, val, v) in enumerate((("Cutoff", "2.40 kHz", 0.62), ("Resonance", "32%", 0.32), ("Drive", "18%", 0.18))):
        knob(s, T, x + 52 + k * 78, 272, 24, v, lab, val)
    for k, (lab, val, v, bi) in enumerate((("Keytrack", "40%", 0.4, False), ("Env Amt", "+35%", 0.68, True),
                                            ("Vowel", "0%", 0.0, False))):
        knob(s, T, x + 274 + k * 52, 272, 12, v, lab, val, bipolar=bi, dim=(k == 2))
    # modulation strip
    pw = 227.2
    mods = [("ENV 1", "Amp", "env", (0.04, 0.3, 0.55, 0.22)), ("ENV 2", "Filter", "env", (0.02, 0.2, 0.3, 0.3)),
            ("ENV 3", "Mod  ·  Pitch", "env", (0.3, 0.3, 0.0, 0.1)), ("LFO 1", "Sine", "sine", None),
            ("LFO 2", "Triangle", "tri", None)]
    for i, (name, note, kind, e) in enumerate(mods):
        x = 12 + i * (pw + 10)
        panel(s, T, x, 364, pw, 206, name, note=note)
        if kind == "env":
            env_graph(s, T, x + 10, 394, pw - 20, 92, A, *e)
            labs = (("Attack", "12 ms"), ("Decay", "480 ms"), ("Sustain", f"{round(e[2] * 100)}%"), ("Release", "260 ms"))
            vs = (e[0] * 2, e[1] * 1.6, e[2], e[3] * 1.8)
            for k in range(4):
                knob(s, T, x + pw / 8 * (2 * k + 1), 528, 12, min(1, vs[k]), labs[k][0], labs[k][1])
        else:
            lfo_graph(s, T, x + 10, 394, pw - 20, 92, A, kind, 2.0 if kind == "sine" else 3.0, 0.3)
            knob(s, T, x + pw / 8, 528, 12, 0.45 if i == 3 else 0.6, "Rate", "1/4" if i == 3 else "3.2 Hz")
            knob(s, T, x + pw / 8 * 3, 528, 12, 0.7, "Depth", "70%")
            pill(s, T, x + pw / 2 + 10, 510, 92, 18, "SYNC", on=(i == 3))
            pill(s, T, x + pw / 2 + 10, 534, 92, 18, "RETRIGGER", on=(i == 4))
    # bottom row
    y = 580
    panel(s, T, 12, y, 300, 148, "UNISON · SUB · NOISE")
    for k, (lab, val, v) in enumerate((("Detune", "25%", 0.25), ("Spread", "50%", 0.5), ("Sub", "30%", 0.3),
                                       ("Noise", "0%", 0.0))):
        knob(s, T, 12 + 300 / 8 * (2 * k + 1), y + 86, 14, v, lab, val)
    panel(s, T, 322, y, 420, 148, "MACROS")
    for k, (lab, v) in enumerate((("Bark", 0.35), ("Tone", 0.5), ("Tremolo", 0.0), ("Room", 0.2))):
        knob(s, T, 322 + 420 / 8 * (2 * k + 1), y + 84, 22, v, lab, f"{round(v * 100)}%")
    panel(s, T, 752, y, 150, 148, "VOICE")
    dropdown(s, T, 764, y + 32, 126, 22, "Poly")
    knob(s, T, 827, y + 100, 13, 0.0, "Glide", "0 ms")
    panel(s, T, 912, y, 276, 148, "OUTPUT")
    scope(s, T, 924, y + 32, 168, 104, A)
    knob(s, T, 1142, y + 84, 20, 0.66, "Output", "0.0 dB")
    return s.out("Makieta 1: jeden akcent, pasek modulacji zawsze widoczny"), T


# ----------------------------------------------------------------------------------------------- variant 2
def variant2():
    T = Theme(bg="#101216", bar="#101216", panel="#171A20", panel_edge="#262B35", inset="#0C0E12", inset_edge="#20252E",
              text="#ECEEF2", dim="#878E9B", title="#ECEEF2", accent="#ECEEF2", on_accent="#101216",
              track="#2B303A", knob="#1F232B", knob_edge="#343A46", field="#1E222A", field_edge="#2E3440",
              grid="#191D24", rx=8, rx_small=5, knob_style="ring", wt_tint=True)
    OSC, FLT, ENV, MOD, FX, MAC = "#2ED3BE", "#FF9548", "#7FE08A", "#A98BFF", "#5AA9FF", "#F5C63C"
    s = Svg("b")
    s.rect(0, 0, W, H, T.bg)
    topbar(s, T, 56, ["SYNTH", "MODULATION", "EFFECTS"], 0, "pill")

    def head(x, y, title, color):
        s.rect(x + 12, y + 12, 3, 12, color, rx=1.5)
        s.text(x + 22, y + 22, title, 10.5, T.title, 700, ls=0.9)

    for i, (name, table, kind, pos, mode) in enumerate((("OSC A", "Glass Harmonics", "bell", 0.33, "Sync"),
                                                        ("OSC B", "Analog Saw", "saw", 0.17, "Off"))):
        y = 66 + i * 214
        panel(s, T, 12, y, 560, 204)
        head(12, y, name, OSC)
        wavetable(s, T, 24, y + 34, 236, 158, OSC, kind, pos, pad=12)
        dropdown(s, T, 272, y + 10, 176, 22, table, OSC)
        dropdown(s, T, 456, y + 10, 104, 22, "Wavetable", OSC)
        knob(s, T, 312, y + 88, 24, pos, "Position", f"{round(pos * 100)}%", OSC)
        knob(s, T, 396, y + 88, 24, 0.4 if i == 0 else 0, "Warp", "40%" if i == 0 else "0%", OSC, dim=(i == 1))
        s.text(444, y + 72, "Warp mode", 10, T.dim, 500)
        dropdown(s, T, 444, y + 78, 116, 22, mode, OSC)
        small = [("Octave", "0" if i == 0 else "+1", 0.5 if i == 0 else 0.62, True), ("Semi", "0", 0.5, True),
                 ("Fine", "0 ct" if i == 0 else "+7 ct", 0.5 if i == 0 else 0.56, True),
                 ("Level", "80%" if i == 0 else "45%", 0.8 if i == 0 else 0.45, False), ("Pan", "0%", 0.5, True),
                 ("Unison", "4" if i == 0 else "2", 0.45 if i == 0 else 0.15, False)]
        for k, (lab, val, v, bi) in enumerate(small):
            knob(s, T, 294 + k * 49, y + 164, 12, v, lab, val, OSC, bipolar=bi)
    y = 494
    panel(s, T, 12, y, 560, 106)
    head(12, y, "UNISON · SUB · NOISE · STRING", OSC)
    for k, (lab, val, v, dim) in enumerate((("Detune", "25%", 0.25, False), ("Spread", "50%", 0.5, False),
                                            ("Sub", "30%", 0.3, False), ("Noise", "0%", 0.0, False),
                                            ("Str Decay", "1.50 s", 0.4, True), ("Str Tone", "60%", 0.6, True))):
        knob(s, T, 12 + 560 / 12 * (2 * k + 1), y + 64, 12, v, lab, val, OSC, dim=dim)
    # right column
    panel(s, T, 584, 66, 604, 204)
    head(584, 66, "FILTER", FLT)
    filter_graph(s, T, 596, 100, 250, 158, FLT)
    dropdown(s, T, 858, 76, 120, 22, "LP24", FLT)
    for k, (lab, val, v) in enumerate((("Cutoff", "2.40 kHz", 0.62), ("Resonance", "32%", 0.32), ("Drive", "18%", 0.18))):
        knob(s, T, 911 + k * 106, 154, 24, v, lab, val, FLT)
    for k, (lab, val, v, bi) in enumerate((("Keytrack", "40%", 0.4, False), ("Env Amt", "+35%", 0.68, True),
                                            ("Vowel", "0%", 0.0, False))):
        knob(s, T, 911 + k * 106, 230, 12, v, lab, val, FLT, bipolar=bi, dim=(k == 2))
    y = 280
    panel(s, T, 584, y, 604, 204)
    head(584, y, "ENVELOPES", ENV)
    tx = 700
    for k, t in enumerate(("AMP", "FILTER", "MOD", "PITCH")):
        tw = len(t) * 7 + 22
        s.rect(tx, y + 9, tw, 22, ENV if k == 0 else "none", rx=11, stroke=None if k == 0 else T.field_edge)
        s.text(tx + tw / 2, y + 24, t, 10, T.on_accent if k == 0 else T.dim, 700, "middle", 0.6)
        tx += tw + 6
    env_graph(s, T, 596, y + 40, 330, 152, ENV, 0.04, 0.3, 0.55, 0.22)
    for k, (lab, val, v) in enumerate((("Attack", "12 ms", 0.1), ("Decay", "480 ms", 0.45), ("Sustain", "55%", 0.55),
                                       ("Release", "260 ms", 0.4))):
        knob(s, T, 1000 + (k % 2) * 110, y + 76 + (k // 2) * 78, 19, v, lab, val, ENV)
    y = 494
    for i, (name, shape) in enumerate((("LFO 1", "sine"), ("LFO 2", "tri"))):
        x = 584 + i * 158
        panel(s, T, x, y, 150, 106)
        head(x, y, name, MOD)
        lfo_graph(s, T, x + 10, y + 32, 84, 64, MOD, shape, 1.0 if i == 0 else 2.0, 0.3)
        knob(s, T, x + 122, y + 60, 11, 0.45 + i * 0.15, "Rate", "1/4" if i == 0 else "3.2 Hz", MOD)
    panel(s, T, 900, y, 130, 106)
    head(900, y, "VOICE", MOD)
    dropdown(s, T, 910, y + 34, 110, 22, "Poly", MOD)
    s.text(910, y + 82, "Glide", 10, T.dim, 500)
    s.text(1020, y + 82, "0 ms", 10, T.text, 500, "end")
    s.rect(910, y + 88, 110, 3, T.track, rx=1.5)
    panel(s, T, 1038, y, 150, 106)
    head(1038, y, "ARP", MOD)
    pill(s, T, 1144, y + 10, 34, 18, "ON", on=True, color=MOD)
    dropdown(s, T, 1048, y + 34, 130, 22, "Up · 2 oct", MOD)
    dropdown(s, T, 1048, y + 64, 130, 22, "1/16 · gate 50%", MOD)
    y = 610
    panel(s, T, 12, y, 560, 118)
    head(12, y, "MACROS", MAC)
    for k, (lab, v) in enumerate((("Bark", 0.35), ("Tone", 0.5), ("Tremolo", 0.0), ("Room", 0.2))):
        knob(s, T, 12 + 560 / 8 * (2 * k + 1), y + 68, 21, v, lab, f"{round(v * 100)}%", MAC)
    panel(s, T, 584, y, 150, 118)
    head(584, y, "OUTPUT", FX)
    knob(s, T, 659, y + 68, 21, 0.66, "Output", "0.0 dB", FX)
    panel(s, T, 742, y, 446, 118)
    head(742, y, "SCOPE", FX)
    scope(s, T, 754, y + 32, 422, 74, FX)
    return s.out("Makieta 2: kolor na sekcję, obwiednie i LFO jako wykresy"), T


# ----------------------------------------------------------------------------------------------- variant 3
def variant3():
    T = Theme(bg="#0C0B0A", bar="#0C0B0A", panel="#161412", panel_edge=None, inset="#080706", inset_edge="#25211D",
              text="#F3EEE7", dim="#93897D", title="#F3EEE7", accent="#FF7A45", on_accent="#200B02",
              track="#322C26", knob="#2A2520", knob_edge="#40382F", field="#1A1714", field_edge="#322C26",
              grid="#15120F", rx=4, rx_small=3, knob_style="cap", wt_tint=False)
    A = T.accent
    s = Svg("c")
    s.rect(0, 0, W, H, T.bg)
    topbar(s, T, 48, ["SYNTH", "MODULATION", "EFFECTS"], 0, "underline")
    # hero display
    s.rect(12, 58, 1176, 236, T.inset, rx=6, stroke=T.inset_edge)
    tx = 28
    for k, t in enumerate(("OSC A", "OSC B", "FILTER", "ENVELOPES", "LFO", "SCOPE")):
        tw = len(t) * 7.2 + 20
        s.text(tx + tw / 2, 82, t, 10.5, T.text if k == 0 else T.dim, 700, "middle", 0.9)
        if k == 0:
            s.rect(tx + 4, 89, tw - 8, 2, A)
        tx += tw + 4
    inner = Theme(**T.__dict__)
    inner.inset, inner.inset_edge = "none", None
    wavetable(s, inner, 20, 96, 840, 192, A, "bell", 0.33, frames=22, pad=16, depth=(0.30, 0.5))
    s.line(872, 100, 872, 282, T.inset_edge, 1, 1, "butt")
    rows = (("Table", "Glass Harmonics"), ("Position", "33 %"), ("Warp", "Sync  ·  40 %"), ("Pitch", "0 st  ·  0 ct"),
            ("Unison", "4 voices  ·  25 %"), ("Level", "80 %"), ("Pan", "C"))
    for k, (lab, val) in enumerate(rows):
        yy = 116 + k * 25
        s.text(892, yy, lab.upper(), 9.5, T.dim, 600, ls=0.9)
        s.text(1170, yy, val, 12 if k else 12.5, A if k == 0 else T.text, 600, "end")
        if k < len(rows) - 1:
            s.line(892, yy + 9, 1170, yy + 9, T.inset_edge, 1, 0.7, "butt")

    def col(x, w, title):
        s.text(x + 12, 326, title, 10.5, T.title, 700, ls=0.9)
        s.line(x + 12, 336, x + w - 12, 336, T.track, 1, 1, "butt")

    for i, (name, table, vals) in enumerate((("OSC A", "Glass Harmonics", (0.33, 0.4, 0.5, 0.5, 0.5, 0.8, 0.5, 0.45)),
                                             ("OSC B", "Analog Saw", (0.17, 0.0, 0.62, 0.5, 0.56, 0.45, 0.5, 0.15)))):
        x = 12 + i * 282
        col(x, 270, name)
        dropdown(s, T, x + 98, 310, 160, 20, table)
        knob(s, T, x + 78, 394, 27, vals[0], "Position", f"{round(vals[0] * 100)}%")
        knob(s, T, x + 192, 394, 27, vals[1], "Warp · Sync" if i == 0 else "Warp · Off", f"{round(vals[1] * 100)}%",
             dim=(i == 1))
        small = [("Octave", "0" if i == 0 else "+1", vals[2], True), ("Semi", "0", vals[3], True),
                 ("Fine", "0 ct" if i == 0 else "+7 ct", vals[4], True),
                 ("Level", f"{round(vals[5] * 100)}%", vals[5], False), ("Pan", "0%", vals[6], True),
                 ("Unison", "4" if i == 0 else "2", vals[7], False)]
        for k, (lab, val, v, bi) in enumerate(small):
            knob(s, T, x + 48 + (k % 3) * 87, 482 + (k // 3) * 74, 11, v, lab, val, bipolar=bi)
        s.line(x + 276, 316, x + 276, 590, T.track, 1, 0.6, "butt")
    x = 576
    col(x, 290, "FILTER")
    dropdown(s, T, x + 168, 310, 110, 20, "LP24")
    for k, (lab, val, v) in enumerate((("Cutoff", "2.40 kHz", 0.62), ("Resonance", "32%", 0.32), ("Drive", "18%", 0.18))):
        knob(s, T, x + 56 + k * 89, 394, 24, v, lab, val)
    for k, (lab, val, v, bi, dim) in enumerate((("Keytrack", "40%", 0.4, False, False), ("Env Amt", "+35%", 0.68, True, False),
                                                 ("Vowel", "0%", 0.0, False, True), ("Pitch Env", "0.0 st", 0.5, True, False),
                                                 ("P. Decay", "120 ms", 0.3, False, False), ("Glide", "0 ms", 0.0, False, False))):
        knob(s, T, x + 56 + (k % 3) * 89, 482 + (k // 3) * 74, 11, v, lab, val, bipolar=bi, dim=dim)
    s.line(x + 296, 316, x + 296, 590, T.track, 1, 0.6, "butt")
    x = 878
    col(x, 310, "ENVELOPES")
    for i, (name, e, vals) in enumerate((("AMP", (0.05, 0.3, 0.55, 0.22), ("12 ms", "480 ms", "55%", "260 ms")),
                                         ("FILTER", (0.03, 0.2, 0.3, 0.3), ("2 ms", "300 ms", "30%", "300 ms")),
                                         ("MOD", (0.3, 0.3, 0.0, 0.1), ("400 ms", "500 ms", "0%", "100 ms")))):
        yy = 346 + i * 84
        s.text(x + 12, yy + 12, name, 9.5, T.dim, 700, ls=0.9)
        env_graph(s, T, x + 12, yy + 18, 104, 52, A, *e, nodes=False, grid=False)
        for k, lab in enumerate(("A", "D", "S", "R")):
            v = (e[0] * 2, e[1] * 1.6, e[2], e[3] * 1.8)[k]
            knob(s, T, x + 146 + k * 46, yy + 42, 10, min(1, v), lab, vals[k])
    # bottom deck
    y = 608
    s.rect(12, y, 1176, 120, T.panel, rx=6)
    s.text(28, y + 22, "MACROS", 10.5, T.title, 700, ls=0.9)
    for k, (lab, v) in enumerate((("Bark", 0.35), ("Tone", 0.5), ("Tremolo", 0.0), ("Room", 0.2))):
        knob(s, T, 150 + k * 92, y + 62, 20, v, lab, f"{round(v * 100)}%")
    s.line(488, y + 14, 488, y + 106, T.track, 1, 1, "butt")
    s.text(504, y + 22, "MIX", 10.5, T.title, 700, ls=0.9)
    for k, (lab, val, v) in enumerate((("Detune", "25%", 0.25), ("Spread", "50%", 0.5), ("Sub", "30%", 0.3),
                                       ("Noise", "0%", 0.0))):
        knob(s, T, 572 + k * 62, y + 66, 12, v, lab, val)
    s.line(806, y + 14, 806, y + 106, T.track, 1, 1, "butt")
    s.text(822, y + 22, "VOICE", 10.5, T.title, 700, ls=0.9)
    dropdown(s, T, 822, y + 38, 120, 22, "Poly")
    pill(s, T, 822, y + 72, 120, 20, "ARP  ·  OFF", on=False)
    s.line(960, y + 14, 960, y + 106, T.track, 1, 1, "butt")
    s.text(976, y + 22, "OUTPUT", 10.5, T.title, 700, ls=0.9)
    knob(s, T, 1066, y + 62, 20, 0.66, "Output", "0.0 dB")
    for k in range(2):
        s.rect(1132 + k * 14, y + 22, 8, 80, T.inset, rx=2, stroke=T.inset_edge)
        s.rect(1132 + k * 14, y + 22 + 80 - (52 - k * 6), 8, 52 - k * 6, A, rx=2)
    return s.out("Makieta 3: duży ekran kontekstowy i pulpit pokręteł"), T


VARIANTS = [("volt-ui-1", variant1), ("volt-ui-2", variant2), ("volt-ui-3", variant3)]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    svgs = []
    for name, fn in VARIANTS:
        svg, _ = fn()
        with open(os.path.join(OUT_DIR, name + ".svg"), "w") as f:
            f.write(svg + "\n")
        svgs.append(svg)
    print("wrote", len(svgs), "mock-ups to", OUT_DIR)
    if len(sys.argv) > 2 and sys.argv[1] == "--html":
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import mockups_detail
        import mockups_page
        detail = mockups_detail.build()
        for name, svg in zip(("volt-ui-2a", "volt-ui-2b"), detail):
            with open(os.path.join(OUT_DIR, name + ".svg"), "w") as f:
                f.write(svg + "\n")
        import mockups_final
        final = mockups_final.build()
        for (name, *_), svg in zip(mockups_final.FONTS, final):
            with open(os.path.join(OUT_DIR, name + ".svg"), "w") as f:
                f.write(svg + "\n")
        with open(sys.argv[2], "w") as f:
            f.write(mockups_page.render(svgs, detail, final))
        print("wrote", sys.argv[2])


if __name__ == "__main__":
    main()
