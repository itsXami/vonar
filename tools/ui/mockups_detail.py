#!/usr/bin/env python3
"""Round 2 of the stage B mock-ups: the chosen layout (variant 2, colour per section) drawn at higher fidelity in
two finishes. Writes docs/mockups/volt-ui-2a.svg ("technical": flat, flush panels, mono read-outs) and
volt-ui-2b.svg ("hardware": shaded caps, recessed displays, glowing traces).

    python3 tools/ui/mockups_detail.py
"""
import math
import os

from mockups import OUT_DIR, W, H, Svg, arc, pt, wave, esc, FONT

OSC, FLT, ENV, MOD, FX, MAC = "#22C3B0", "#F28A3C", "#74CC6C", "#9480F5", "#4C9BF2", "#E6B43A"
MONO = "'IBM Plex Mono', 'JetBrains Mono', Consolas, monospace"


class F:
    def __init__(self, **kw):
        self.__dict__.update(kw)


FIN_A = F(hw=False, bg="#08090B", panel="#14161A", head="#1A1D22", inset="#0B0C0F", grid="#171A1F", text="#E4E7EC",
          label="#9AA2AE", value="#C8CDD6", dim="#69717D", track="#2B3038", knob="#242830", field="#0D0F12",
          field_edge="#262A32", rx=2, valfont=MONO, bar="#101215")
FIN_B = F(hw=True, bg="#050607", panel="#17191D", head="#17191D", inset="#060709", grid="#111318", text="#ECEEF2",
          label="#A3A9B4", value="#D5D9E0", dim="#6E7580", track="#090A0C", knob="#2A2E35", field="#0B0C0F",
          field_edge="#2A2E36", rx=5, valfont=FONT, bar="#0E0F12")


class D(Svg):
    """Svg with a few extras: raw markup, radial gradients and the two filters used by the hardware finish."""
    def __init__(self, prefix, fin):
        super().__init__(prefix)
        self.f = fin
        p = prefix
        self.defs.append(
            f'<filter id="{p}glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="2.6" '
            f'result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
            f'<filter id="{p}sh" x="-40%" y="-40%" width="180%" height="200%"><feDropShadow dx="0" dy="2.5" '
            f'stdDeviation="2.5" flood-color="#000" flood-opacity="0.75"/></filter>'
            f'<radialGradient id="{p}cap" cx="0.38" cy="0.28" r="0.85"><stop offset="0" stop-color="#565C68"/>'
            f'<stop offset="0.55" stop-color="#2B2F37"/><stop offset="1" stop-color="#17191D"/></radialGradient>'
            f'<linearGradient id="{p}pan" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1D2025"/>'
            f'<stop offset="1" stop-color="#131518"/></linearGradient>'
            f'<linearGradient id="{p}btn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2A2E36"/>'
            f'<stop offset="1" stop-color="#1B1E23"/></linearGradient>'
            f'<linearGradient id="{p}ins" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" '
            f'stop-opacity="0.55"/><stop offset="1" stop-color="#000" stop-opacity="0"/></linearGradient>')

    def raw(self, t):
        self.o.append(t)

    def url(self, name):
        return f"url(#{self.prefix}{name})"

    def gpath(self, d, stroke, sw):
        """Stroked path; glows in the hardware finish."""
        flt = f' filter="{self.url("glow")}"' if self.f.hw else ""
        self.raw(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" '
                 f'stroke-linejoin="round"{flt}/>')

    def vtext(self, x, y, t, size, fill, anchor="middle", weight=500, op=1):
        self.raw(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
                 f'text-anchor="{anchor}" font-family="{self.f.valfont}" opacity="{op}" '
                 f'style="font-variant-numeric:tabular-nums">{esc(t)}</text>')


def panel(s, x, y, w, h, title, color):
    f = s.f
    if f.hw:
        s.rect(x, y, w, h, s.url("pan"), rx=f.rx, stroke="#000", sw=1)
        s.line(x + f.rx, y + 1, x + w - f.rx, y + 1, "#FFFFFF", 1, 0.07, "butt")
        s.raw(f'<circle cx="{x + 13}" cy="{y + 13}" r="3" fill="{color}" filter="{s.url("glow")}"/>')
        s.text(x + 24, y + 17, title, 10.5, f.text, 700, ls=1.1)
    else:
        s.rect(x, y, w, h, f.panel, rx=f.rx)
        s.rect(x, y, w, 24, f.head, rx=f.rx)
        s.rect(x, y + 23, w, 1, f.bg, op=0.6)
        s.rect(x + 9, y + 9, 6, 6, color, rx=1)
        s.text(x + 22, y + 16.5, title, 10.5, f.text, 700, ls=1.1)


def display(s, x, y, w, h):
    f = s.f
    s.rect(x, y, w, h, f.inset, rx=3 if f.hw else 2, stroke="#000" if f.hw else "#1C1F25", sw=1)
    if f.hw:
        s.rect(x + 1, y + 1, w - 2, 12, s.url("ins"), rx=3)
        s.line(x + 3, y + h + 0.5, x + w - 3, y + h + 0.5, "#FFFFFF", 1, 0.06, "butt")


def dd(s, x, y, w, h, label, color=None):
    f = s.f
    if f.hw:
        s.rect(x, y, w, h, s.url("btn"), rx=3, stroke="#000", sw=1)
        s.line(x + 2, y + 1, x + w - 2, y + 1, "#FFFFFF", 1, 0.08, "butt")
    else:
        s.rect(x, y, w, h, f.field, rx=2, stroke=f.field_edge)
    s.text(x + 8, y + h / 2 + 3.8, label, 10.5, f.text, 500)
    cx, cy = x + w - 11, y + h / 2
    s.path(f"M{cx - 3} {cy - 1.5}L{cx} {cy + 1.8}L{cx + 3} {cy - 1.5}", stroke=color or f.dim, sw=1.4)


def chip(s, x, y, w, h, label, on, color):
    f = s.f
    if on:
        if f.hw:
            s.rect(x, y, w, h, s.url("btn"), rx=3, stroke="#000")
            s.raw(f'<circle cx="{x + 8}" cy="{y + h / 2}" r="2.2" fill="{color}" filter="{s.url("glow")}"/>')
            s.text(x + w / 2 + 4, y + h / 2 + 3.4, label, 9.5, f.text, 700, "middle", 0.6)
        else:
            s.rect(x, y, w, h, color, rx=2)
            s.text(x + w / 2, y + h / 2 + 3.4, label, 9.5, "#0A0B0D", 700, "middle", 0.6)
    else:
        s.rect(x, y, w, h, f.field, rx=3 if f.hw else 2, stroke=f.field_edge if not f.hw else "#000")
        s.text(x + w / 2, y + h / 2 + 3.4, label, 9.5, f.dim, 700, "middle", 0.6)


def knob(s, cx, cy, r, v, label, val, color, bipolar=False, dim=False):
    f = s.f
    a = -135 + 270 * v
    a0 = 0 if bipolar else -135
    big = r >= 17
    if dim:
        s.raw('<g opacity="0.36">')
    if f.hw:
        ro = r + 5
        s.path(arc(cx, cy, ro, -135, 135), stroke=f.track, sw=3.4)
        s.path(arc(cx, cy, ro, -135, 135), stroke="#FFFFFF", sw=0.6, op=0.05)
        if abs(a - a0) > 1:
            s.gpath(arc(cx, cy, ro, a0, a), color, 2.6)
        s.raw(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{s.url("cap")}" stroke="#08090A" stroke-width="1" '
              f'filter="{s.url("sh")}"/>')
        s.path(arc(cx, cy, r - 1, -70, 20), stroke="#FFFFFF", sw=0.8, op=0.13)
        x0, y0 = pt(cx, cy, r * 0.42, a)
        x1, y1 = pt(cx, cy, r - 2.5, a)
        s.line(x0, y0, x1, y1, color, 2.2 if big else 1.8)
        off = 7
    else:
        ro = r + 3.5
        s.path(arc(cx, cy, ro, -135, 135), stroke=f.track, sw=2)
        if abs(a - a0) > 1:
            s.path(arc(cx, cy, ro, a0, a), stroke=color, sw=2)
        if big:
            for t in (-135, 0, 135):
                x0, y0 = pt(cx, cy, ro + 3.5, t)
                x1, y1 = pt(cx, cy, ro + 6, t)
                s.line(x0, y0, x1, y1, f.dim, 1, 0.9, "butt")
        s.circle(cx, cy, r, f.knob)
        s.path(arc(cx, cy, r - 0.5, -80, 80), stroke="#FFFFFF", sw=1, op=0.07)
        x0, y0 = pt(cx, cy, r * 0.32, a)
        x1, y1 = pt(cx, cy, r - 2, a)
        s.line(x0, y0, x1, y1, "#F2F4F7", 1.8 if big else 1.5)
        off = 6 if big else 4
    s.text(cx, cy - r - off - 6, label, 11 if big else 10, f.text if big else f.label, 600 if big else 500, "middle")
    s.vtext(cx, cy + r + off + (15 if big else 13), val, 10.5 if big else 9.5, f.value if big else f.dim)
    if dim:
        s.raw("</g>")


def wavetable(s, x, y, w, h, color, kind, pos, frames=18):
    f = s.f
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
        s.path(closed, fill=f.inset)
        if i == cur:
            s.path(closed, fill=s.grad(color, 0.42, 0.06))
            s.gpath(line, color, 2)
        else:
            s.path(line, stroke=color, sw=1, op=0.22 + 0.4 * (1 - d) * (0.6 if i > cur else 1))
    s.vtext(x + w - 8, y + 15, f"frame {cur + 1} / {frames}", 9, f.dim, "end")


def env_graph(s, x, y, w, h, color, a, d, sus, r):
    f = s.f
    display(s, x, y, w, h)
    px, py = 10, 14
    x0, yb, yt = x + px, y + h - py - 6, y + py
    ww = w - 2 * px
    for k in range(1, 8):
        gx = x0 + ww * k / 8
        s.line(gx, y + 4, gx, y + h - 4, f.grid, 1, 1, "butt")
    for k, lab in enumerate(("0", "0.5 s", "1 s", "1.5 s")):
        s.vtext(x0 + ww * k / 4 + 3, y + h - 6, lab, 8.5, f.dim, "start")
    xa = x0 + a * ww
    xd = xa + d * ww
    ys = yb - sus * (yb - yt)
    xr0 = x0 + ww * 0.68
    xe = min(x0 + ww, xr0 + r * ww)
    line = (f"M{x0:.1f} {yb:.1f}L{xa:.1f} {yt:.1f}Q{xa + (xd - xa) * 0.22:.1f} {ys:.1f} {xd:.1f} {ys:.1f}"
            f"L{xr0:.1f} {ys:.1f}Q{xr0 + (xe - xr0) * 0.22:.1f} {yb:.1f} {xe:.1f} {yb:.1f}")
    s.path(line + "Z", fill=s.grad(color, 0.36, 0.04))
    s.gpath(line, color, 2)
    for nx, ny in ((xa, yt), (xd, ys), (xr0, ys), (xe, yb)):
        s.circle(nx, ny, 3.2, f.inset, stroke=color, sw=1.6)


def lfo_graph(s, x, y, w, h, color, shape, cycles, phase):
    f = s.f
    display(s, x, y, w, h)
    px, py = 7, 10
    x0, ww = x + px, w - 2 * px
    yc, amp = y + h / 2, h / 2 - py
    for k in range(1, 4):
        s.line(x0 + ww * k / 4, y + 4, x0 + ww * k / 4, y + h - 4, f.grid, 1, 1, "butt")
    s.line(x0, yc, x0 + ww, yc, f.grid, 1, 1, "butt")

    def fn(t):
        ph = (t * cycles) % 1
        return 1 - 4 * abs(ph - 0.5) if shape == "tri" else math.sin(2 * math.pi * ph)
    n = 120
    pts = [(x0 + ww * k / n, yc - amp * fn(k / n)) for k in range(n + 1)]
    line = "M" + "L".join(f"{a:.1f} {b:.1f}" for a, b in pts)
    s.path(line + f"L{x0 + ww:.1f} {yc:.1f}L{x0:.1f} {yc:.1f}Z", fill=s.grad(color, 0.26, 0.05))
    s.gpath(line, color, 1.8)
    k = int(phase * n)
    s.line(pts[k][0], y + 4, pts[k][0], y + h - 4, "#FFFFFF", 1, 0.25, "butt")
    s.circle(pts[k][0], pts[k][1], 2.8, "#FFFFFF")


def filter_graph(s, x, y, w, h, color, cut, res):
    f = s.f
    display(s, x, y, w, h)
    px = 10
    x0, ww = x + px, w - 2 * px
    ytop, ybot = y + 10, y + h - 18
    fmin, fmax = 20.0, 20000.0
    fc = fmin * (fmax / fmin) ** cut
    q = 0.6 + res * 6

    def ypos(db):
        return ytop + (18 - db) / 66 * (ybot - ytop)
    for fr in (50, 100, 200, 500, 1000, 2000, 5000, 10000):
        gx = x0 + ww * math.log(fr / fmin) / math.log(fmax / fmin)
        s.line(gx, ytop - 4, gx, ybot, f.grid, 1, 1, "butt")
        if fr in (100, 1000, 10000):
            s.vtext(gx, y + h - 6, {100: "100", 1000: "1k", 10000: "10k"}[fr], 8.5, f.dim)
    for db in (12, 0, -12, -24, -36):
        s.line(x0, ypos(db), x0 + ww, ypos(db), f.grid, 1, 1, "butt")
    s.vtext(x0 + 2, ypos(0) - 3, "0 dB", 8.5, f.dim, "start")
    pts = []
    n = 150
    for k in range(n + 1):
        fr = fmin * (fmax / fmin) ** (k / n)
        rr = fr / fc
        mag = 1 / math.sqrt((1 - rr * rr) ** 2 + (rr / q) ** 2)
        db = 20 * math.log10(mag) + (-12 * math.log2(rr) if rr > 1 else 0)
        pts.append((x0 + ww * k / n, min(ybot, ypos(max(-48, db)))))
    line = "M" + "L".join(f"{a:.1f} {b:.1f}" for a, b in pts)
    s.path(line + f"L{x0 + ww:.1f} {ybot:.1f}L{x0:.1f} {ybot:.1f}Z", fill=s.grad(color, 0.36, 0.04))
    s.gpath(line, color, 2)
    gx = x0 + ww * cut
    s.line(gx, ytop - 4, gx, ybot, color, 1, 0.5, "butt")


def scope(s, x, y, w, h, color):
    f = s.f
    display(s, x, y, w, h)
    yc, amp = y + h / 2, h / 2 - 12
    for k in range(1, 8):
        s.line(x + w * k / 8, y + 4, x + w * k / 8, y + h - 4, f.grid, 1, 1, "butt")
    s.line(x + 6, yc, x + w - 6, yc, f.grid, 1, 1, "butt")
    n = 260
    pts = []
    for k in range(n + 1):
        t = k / n * 4.2
        v = 0.6 * math.sin(2 * math.pi * t) + 0.26 * math.sin(4 * math.pi * t + 0.6) + 0.1 * math.sin(10 * math.pi * t)
        pts.append((x + 6 + (w - 12) * k / n, yc - amp * v))
    s.gpath("M" + "L".join(f"{a:.1f} {b:.1f}" for a, b in pts), color, 1.6)


def topbar(s):
    f = s.f
    s.rect(0, 0, W, 44, f.bar)
    s.rect(0, 43, W, 1, "#000")
    # wordmark: the O is a small knob
    s.text(16, 28.5, "V", 18, f.text, 800)
    s.path(arc(38.5, 22, 6.6, -135, 135), stroke=f.text, sw=2.7)
    s.circle(38.5, 22, 1.7, f.text)
    s.text(50, 28.5, "LT", 18, f.text, 800, ls=2.6)
    x = 106
    for i, t in enumerate(("SYNTH", "MODULATION", "EFFECTS")):
        tw = len(t) * 7.3 + 24
        s.text(x + tw / 2, 26.5, t, 10.5, f.text if i == 0 else f.dim, 700, "middle", 1)
        if i == 0:
            s.rect(x + 6, 41, tw - 12, 2, f.text)
        x += tw
    s.rect(430, 9, 372, 26, f.inset if f.hw else f.field, rx=3 if f.hw else 2, stroke="#000" if f.hw else f.field_edge)
    s.text(442, 26, "KEYS", 9.5, f.dim, 700, ls=1.1)
    s.rect(478, 15, 1, 14, f.field_edge)
    s.text(490, 26.5, "Autopan Electric Piano", 12.5, f.text, 600)
    s.text(764, 27.5, "‹", 15, f.label, 500, "middle")
    s.text(786, 27.5, "›", 15, f.label, 500, "middle")
    dd(s, 810, 11, 86, 22, "Browse")
    dd(s, 902, 11, 96, 22, "All tags")
    s.rect(1004, 11, 96, 22, f.field, rx=3 if f.hw else 2, stroke="#000" if f.hw else f.field_edge)
    s.text(1012, 26, "Search…", 10.5, f.dim, 400)
    chip(s, 1106, 11, 44, 22, "SAVE", False, FX)
    s.vtext(1172, 26, "100%", 10, f.dim)


def draw(prefix, fin, title):
    s = D(prefix, fin)
    f = fin
    s.rect(0, 0, W, H, f.bg)
    topbar(s)
    # oscillators
    for i, (name, table, kind, pos, mode) in enumerate((("OSC A", "Glass Harmonics", "bell", 0.33, "Sync"),
                                                        ("OSC B", "Analog Saw", "saw", 0.17, "Off"))):
        x, y = 6, 50 + i * 208
        panel(s, x, y, 590, 206, name, OSC)
        dd(s, x + 76, y + 3, 190, 18, table, OSC)
        dd(s, x + 272, y + 3, 96, 18, "Wavetable", OSC)
        wavetable(s, x + 8, y + 32, 262, 166, OSC, kind, pos)
        xr = x + 282
        knob(s, xr + 44, y + 84, 23, pos, "Position", f"{round(pos * 100)}%", OSC)
        knob(s, xr + 128, y + 84, 23, 0.4 if i == 0 else 0, "Warp", "40%" if i == 0 else "0%", OSC, dim=(i == 1))
        s.text(xr + 184, y + 70, "Warp mode", 10, f.label, 500)
        dd(s, xr + 184, y + 76, 116, 22, mode, OSC)
        small = [("Octave", "0" if i == 0 else "+1", 0.5 if i == 0 else 0.62, True), ("Semi", "0", 0.5, True),
                 ("Fine", "0 ct" if i == 0 else "+7 ct", 0.5 if i == 0 else 0.56, True),
                 ("Level", "80%" if i == 0 else "45%", 0.8 if i == 0 else 0.45, False), ("Pan", "C", 0.5, True),
                 ("Unison", "4" if i == 0 else "2", 0.45 if i == 0 else 0.15, False)]
        for k, (lab, val, v, bi) in enumerate(small):
            knob(s, xr + 26 + k * 50, y + 172, 11, v, lab, val, OSC, bipolar=bi)
    x, y = 6, 466
    panel(s, x, y, 590, 118, "UNISON  ·  SUB  ·  NOISE  ·  STRING", OSC)
    for k, (lab, val, v, dim) in enumerate((("Detune", "25%", 0.25, False), ("Spread", "50%", 0.5, False),
                                            ("Sub", "30%", 0.3, False), ("Noise", "0%", 0.0, False),
                                            ("String decay", "1.50 s", 0.4, True), ("String tone", "60%", 0.6, True))):
        knob(s, x + 590 / 12 * (2 * k + 1), y + 74, 13, v, lab, val, OSC, dim=dim)
    # filter
    x, y = 598, 50
    panel(s, x, y, 596, 206, "FILTER", FLT)
    dd(s, x + 76, y + 3, 110, 18, "LP24", FLT)
    filter_graph(s, x + 8, y + 32, 262, 166, FLT, 0.62, 0.32)
    xr = x + 282
    for k, (lab, val, v) in enumerate((("Cutoff", "2.40 kHz", 0.62), ("Resonance", "32%", 0.32), ("Drive", "18%", 0.18))):
        knob(s, xr + 51 + k * 102, y + 84, 23, v, lab, val, FLT)
    for k, (lab, val, v, bi) in enumerate((("Keytrack", "40%", 0.4, False), ("Env amount", "+35%", 0.68, True),
                                            ("Vowel", "0%", 0.0, False))):
        knob(s, xr + 51 + k * 102, y + 172, 11, v, lab, val, FLT, bipolar=bi, dim=(k == 2))
    # envelopes
    x, y = 598, 258
    panel(s, x, y, 596, 206, "ENVELOPES", ENV)
    for k, t in enumerate(("AMP", "FILTER", "MOD", "PITCH")):
        chip(s, x + 112 + k * 60, y + 3, 58, 18, t, k == 0, ENV)
    env_graph(s, x + 8, y + 32, 352, 166, ENV, 0.04, 0.3, 0.55, 0.22)
    xr = x + 372
    for k, (lab, val, v) in enumerate((("Attack", "12 ms", 0.1), ("Decay", "480 ms", 0.45), ("Sustain", "55%", 0.55),
                                       ("Release", "260 ms", 0.4))):
        knob(s, xr + 56 + (k % 2) * 106, y + 70 + (k // 2) * 90, 18, v, lab, val, ENV)
    # lfo, voice, arp
    y = 466
    for i, (name, shape, label) in enumerate((("LFO 1", "sine", "Sine"), ("LFO 2", "tri", "Triangle"))):
        x = 598 + i * 202
        panel(s, x, y, 200, 118, name, MOD)
        dd(s, x + 64, y + 3, 78, 18, label, MOD)
        chip(s, x + 148, y + 3, 46, 18, "SYNC", i == 0, MOD)
        lfo_graph(s, x + 8, y + 32, 100, 78, MOD, shape, 1.0 if i == 0 else 2.0, 0.3)
        knob(s, x + 134, y + 74, 11, 0.45 + i * 0.15, "Rate", "1/4" if i == 0 else "3.2 Hz", MOD)
        knob(s, x + 174, y + 74, 11, 0.7, "Depth", "70%", MOD)
    x = 1002
    panel(s, x, y, 94, 118, "VOICE", MOD)
    dd(s, x + 8, y + 34, 78, 22, "Poly", MOD)
    s.text(x + 8, y + 82, "Glide", 10, f.label, 500)
    s.vtext(x + 86, y + 82, "0 ms", 9.5, f.dim, "end")
    s.rect(x + 8, y + 92, 78, 4, f.track, rx=2)
    s.circle(x + 10, y + 94, 4, f.value)
    x = 1098
    panel(s, x, y, 96, 118, "ARP", MOD)
    chip(s, x + 56, y + 3, 34, 18, "ON", True, MOD)
    dd(s, x + 8, y + 34, 80, 22, "Up", MOD)
    dd(s, x + 8, y + 60, 80, 22, "1/16", MOD)
    s.vtext(x + 48, y + 102, "2 oct · 50%", 9.5, f.dim)
    # bottom row
    x, y = 6, 586
    panel(s, x, y, 590, 148, "MACROS", MAC)
    for k, (lab, v) in enumerate((("Bark", 0.35), ("Tone", 0.5), ("Tremolo", 0.0), ("Room", 0.2))):
        knob(s, x + 590 / 8 * (2 * k + 1), y + 88, 24, v, lab, f"{round(v * 100)}%", MAC)
    x = 598
    panel(s, x, y, 150, 148, "OUTPUT", FX)
    knob(s, x + 56, y + 88, 22, 0.66, "Output", "0.0 dB", FX)
    for k in range(2):
        mx = x + 112 + k * 12
        s.rect(mx, y + 36, 8, 100, f.inset, rx=1.5, stroke="#000" if f.hw else "#1C1F25")
        lvl = 64 - k * 7
        s.rect(mx + 1.5, y + 36 + 100 - lvl, 5, lvl - 1.5, FX, rx=1)
        s.rect(mx + 1.5, y + 36 + 100 - lvl - 12, 5, 1.5, f.text, op=0.8)
    x = 750
    panel(s, x, y, 444, 148, "SCOPE", FX)
    scope(s, x + 8, y + 32, 428, 108, FX)
    return s.out(title)


def build():
    return [draw("d", FIN_A, "Makieta 2A: wykończenie techniczne"), draw("e", FIN_B, "Makieta 2B: wykończenie sprzętowe")]


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, svg in zip(("volt-ui-2a", "volt-ui-2b"), build()):
        with open(os.path.join(OUT_DIR, name + ".svg"), "w") as fh:
            fh.write(svg + "\n")
    print("wrote volt-ui-2a.svg and volt-ui-2b.svg")
