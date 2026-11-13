#!/usr/bin/env python3
"""Stage D: Drums batch 1 (31) - synthesised one-shots for house and hip-hop, asked for by the user:
"kicki, hi-haty, shakery, clapy, snare do house i do hip hopu".

Every drum is tuned to sound right on C3 (the render phrase plays eight hits on C3); other keys retune it, so a
kick can follow the bass line. One amp envelope per voice, so decay = release: a short gate never cuts a hit.

Recipes (all from the engine's own parts, nothing sampled):
  kick   sine (Basic Shapes, position 0) + sub, a steep Pitch Env dive, a 5-15 ms noise click from Mod Env -> Noise.
  snare  sine/triangle body that dies fast (Mod Env -> Level A) under a longer noise tail through HP / LP filters.
  clap   band-passed noise in 2-3 bursts: LFO 1 square (40 Hz, retrigger) gates the noise only while Mod Env holds
         the level down (noise = 1 + velocity + LFO - Mod Env, clamped), then the tail runs on; short room.
  hats   noise through a high-pass, plus a quiet metallic wavetable an octave or two up; closed 30-70 ms, open 0.3 s+.
  shaker band-passed noise with a few milliseconds of attack (the beads), Random -> Cutoff so no two hits match.
Every preset has an Energy macro (drive + top end, sometimes more click) so the same hit goes from soft to hard.

    python3 tools/presets/generate_batch_drums1.py [--trim report.json]
"""
import batch_common as bc

P, M = bc.P, bc.M
bc.gp.GROUP_TAGS.update({"house": ["House"], "hiphop": ["Hip-Hop"], "trap": ["Hip-Hop", "Trap"]})
_s = bc.begin()
D = "Drums"
SINE = dict(oscA_table="Basic Shapes", oscA_pos=0.0)


def kick(**kw):
    base = dict(SINE, oscA_oct=-1, oscA_level=0.9, sub_level=0.0, flt_type="LP24", flt_cutoff=6000.0, amp_attack=0.0005,
                amp_sustain=0.0, menv_attack=0.0005, menv_sustain=0.0, menv_decay=0.01, penv_amount=36.0,
                penv_decay=0.06, noise_level=0.0)
    base.update(kw)
    base.setdefault("amp_release", base.get("amp_decay", 0.3))
    return base


def noisy(**kw):
    base = dict(oscA_level=0.0, noise_level=1.0, amp_attack=0.0005, amp_sustain=0.0, menv_attack=0.0005,
                menv_sustain=0.0)
    base.update(kw)
    base.setdefault("amp_release", base.get("amp_decay", 0.3))
    return base


CLICK = ("Mod Env", "Noise Level", 0.5)

# ================================================================================================ KICKS
P("house", "Four Floor Kick", D, "Tight, punchy house kick with a short click and a round low thump.",
  M(("Energy", [("Dist Mix", 0.4), ("Cutoff", 0.25)]), ("Click", [("Noise Level", 0.3)]), ("Tune", [("Pitch", 0.15)]),
    ("Room", [("Reverb Mix", 0.2)])),
  mods=[CLICK, ("Velocity", "Level A", 0.15)], tags=["Kick", "Punchy", "Dry"], mood="Medium",
  **kick(oscA_semi=-3, amp_decay=0.32, penv_amount=34.0, penv_decay=0.05, dist_type="Soft", dist_drive=0.35,
         dist_mix=0.3, rev_size=0.2))
P("house", "Deep Thud Kick", D, "Soft, deep kick with a long round tail for deep house and late-night grooves.",
  M(("Energy", [("Dist Mix", 0.4), ("Cutoff", 0.3)]), ("Click", [("Noise Level", 0.25)]), ("Tune", [("Pitch", 0.15)]),
    ("Room", [("Reverb Mix", 0.2)])),
  mods=[("Mod Env", "Noise Level", 0.25)], tags=["Kick", "Deep", "Round"], mood="Dark",
  **kick(oscA_semi=-5, amp_decay=0.55, penv_amount=24.0, penv_decay=0.08, flt_cutoff=1800.0, menv_decay=0.006))
P("house", "Tech Kick", D, "Short, clicky tech house kick with a hard transient and almost no tail.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Click", [("Noise Level", 0.35)]), ("Tune", [("Pitch", 0.15)]),
    ("Room", [("Reverb Mix", 0.2)])),
  mods=[("Mod Env", "Noise Level", 0.7), ("Velocity", "Cutoff", 0.15)], tags=["Kick", "Tech House", "Clicky"], mood="Medium",
  **kick(oscA_semi=-2, amp_decay=0.2, penv_amount=40.0, penv_decay=0.035, flt_cutoff=9000.0, menv_decay=0.012,
         dist_type="Tube", dist_drive=0.4, dist_mix=0.45, squash=0.2))
P("house", "Hard Clipped Kick", D, "Loud, square-clipped kick for hard house and peak-time techno drops.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.3)]), ("Click", [("Noise Level", 0.3)]), ("Tune", [("Pitch", 0.15)]),
    ("Tail", [("Reverb Mix", 0.25)])),
  mods=[("Mod Env", "Noise Level", 0.6)], tags=["Kick", "Hard", "Distorted"], mood="Aggressive",
  **kick(oscA_semi=-3, amp_decay=0.38, penv_amount=44.0, penv_decay=0.05, flt_cutoff=12000.0, menv_decay=0.01,
         dist_type="Hard", dist_drive=0.75, dist_tone=0.75, dist_mix=1.0, squash=0.35))
P("hiphop", "Boom Bap Kick", D, "Thick, slightly saturated kick with a knock on top for boom bap beats.",
  M(("Energy", [("Dist Mix", 0.4), ("Cutoff", 0.3)]), ("Knock", [("Noise Level", 0.3)]), ("Tune", [("Pitch", 0.15)]),
    ("Room", [("Reverb Mix", 0.2)])),
  mods=[("Mod Env", "Noise Level", 0.65), ("Velocity", "Cutoff", 0.2)], tags=["Kick", "Boom Bap", "Knock"], mood="Medium",
  **kick(oscA_semi=-1, oscA_pos=0.2, amp_decay=0.3, penv_amount=30.0, penv_decay=0.035, flt_cutoff=4500.0,
         menv_decay=0.028, dist_type="Tube", dist_drive=0.6, dist_mix=0.7, squash=0.3))
P("hiphop", "Dusty Knock Kick", D, "Dark, short kick with a muffled thump, like it was bounced to tape.",
  M(("Energy", [("Dist Mix", 0.4), ("Cutoff", 0.35)]), ("Knock", [("Noise Level", 0.3)]), ("Tune", [("Pitch", 0.15)]),
    ("Crush", [("Dist Drive", 0.3)])),
  mods=[("Mod Env", "Noise Level", 0.35)], tags=["Kick", "Boom Bap", "Dark"], mood="Dark",
  **kick(oscA_semi=-2, amp_decay=0.3, penv_amount=22.0, penv_decay=0.04, flt_type="LP12", flt_cutoff=1200.0,
         menv_decay=0.015, dist_type="Bitcrush", dist_drive=0.25, dist_tone=0.3, dist_mix=0.35))
P("trap", "Trap Kick Punch", D, "Short, clipped trap kick that cuts through a long 808.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.3)]), ("Click", [("Noise Level", 0.3)]), ("Tune", [("Pitch", 0.15)]),
    ("Room", [("Reverb Mix", 0.2)])),
  mods=[("Mod Env", "Noise Level", 0.55)], tags=["Kick", "Trap", "Clipped"], mood="Aggressive",
  **kick(oscA_semi=0, amp_decay=0.24, penv_amount=40.0, penv_decay=0.04, flt_cutoff=10000.0, menv_decay=0.008,
         dist_type="Hard", dist_drive=0.6, dist_tone=0.7, dist_mix=0.8, squash=0.3))
P("trap", "808 Boom Kick", D, "Long, booming kick that doubles as a short 808, tuned to the note you play.",
  M(("Energy", [("Dist Mix", 0.4), ("Cutoff", 0.3)]), ("Click", [("Noise Level", 0.3)]), ("Length", [("Sub Level", 0.3)]),
    ("Room", [("Reverb Mix", 0.2)])),
  mods=[("Mod Env", "Noise Level", 0.35)], tags=["Kick", "808", "Long"], mood="Dark",
  **kick(oscA_semi=0, sub_level=0.0, amp_decay=1.1, penv_amount=20.0, penv_decay=0.06, flt_cutoff=2500.0,
         menv_decay=0.008, dist_type="Soft", dist_drive=0.35, dist_mix=0.35, dist_keep_low=True))

# ================================================================================================ SNARES
SNARE_BODY = [("Mod Env", "Level A", 0.85)]
P("house", "House Snare", D, "Crisp, bright snare with a short tone body for classic house backbeats.",
  M(("Energy", [("Dist Mix", 0.35), ("Cutoff", 0.3)]), ("Body", [("Level A", 0.3)]), ("Snap", [("Noise Level", 0.2)]),
    ("Room", [("Reverb Mix", 0.3)])),
  mods=SNARE_BODY + [("Velocity", "Cutoff", 0.2)], tags=["Snare", "Bright", "Classic"], mood="Medium",
  **noisy(oscA_table="Basic Shapes", oscA_pos=0.33, oscA_semi=7, noise_level=0.55, penv_amount=12.0, penv_decay=0.03,
          menv_decay=0.07, flt_type="HP", flt_cutoff=220.0, flt_res=0.15, amp_decay=0.22, rev_size=0.25, rev_mix=0.1))
P("house", "Tight Rim Snare", D, "Short, snappy snare with a rim-like tone for tech and minimal house.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.3)]), ("Ring", [("Level A", 0.3)]), ("Snap", [("Noise Level", 0.2)]),
    ("Room", [("Reverb Mix", 0.3)])),
  mods=SNARE_BODY + [("Velocity", "Noise Level", 0.2)], tags=["Snare", "Tight", "Minimal"], mood="Medium",
  **noisy(oscA_table="Basic Shapes", oscA_pos=0.66, oscA_semi=10, noise_level=0.4, penv_amount=7.0, penv_decay=0.02,
          menv_decay=0.04, flt_type="HP", flt_cutoff=400.0, amp_decay=0.12, dist_type="Tube", dist_drive=0.4,
          dist_mix=0.35))
P("hiphop", "Boom Bap Snare", D, "Fat, cracking snare with a thick body and a dirty top for boom bap.",
  M(("Energy", [("Dist Mix", 0.35), ("Cutoff", 0.3)]), ("Body", [("Level A", 0.3)]), ("Crack", [("Noise Level", 0.2)]),
    ("Room", [("Reverb Mix", 0.3)])),
  mods=SNARE_BODY + [("Velocity", "Cutoff", 0.25)], tags=["Snare", "Boom Bap", "Fat"], mood="Medium",
  **noisy(oscA_table="Basic Shapes", oscA_pos=0.2, oscA_semi=5, noise_level=0.7, penv_amount=14.0, penv_decay=0.035,
          menv_decay=0.09, flt_type="LP12", flt_cutoff=6500.0, amp_decay=0.28, dist_type="Tube", dist_drive=0.55,
          dist_mix=0.6, squash=0.35, rev_size=0.3, rev_mix=0.12))
P("hiphop", "Dirty Crack Snare", D, "Distorted, ringing snare that hits hard and breaks up on loud notes.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.3)]), ("Body", [("Level A", 0.3)]), ("Crack", [("Noise Level", 0.2)]),
    ("Room", [("Reverb Mix", 0.3)])),
  mods=SNARE_BODY + [("Velocity", "Dist Drive", 0.3)], tags=["Snare", "Distorted", "Hard"], mood="Aggressive",
  **noisy(oscA_table="Basic Shapes", oscA_pos=0.4, oscA_semi=6, noise_level=0.75, penv_amount=16.0, penv_decay=0.03,
          menv_decay=0.1, flt_type="HP", flt_cutoff=160.0, amp_decay=0.25, dist_type="Hard", dist_drive=0.7,
          dist_tone=0.65, dist_mix=0.9, squash=0.4))
P("trap", "Trap Snare", D, "Bright, tight trap snare with a fast noise burst and a short tuned body.",
  M(("Energy", [("Dist Mix", 0.35), ("Cutoff", 0.3)]), ("Body", [("Level A", 0.3)]), ("Snap", [("Noise Level", 0.2)]),
    ("Room", [("Reverb Mix", 0.3)])),
  mods=SNARE_BODY + [("Velocity", "Cutoff", 0.2)], tags=["Snare", "Trap", "Bright"], mood="Medium",
  **noisy(oscA_table="Basic Shapes", oscA_pos=0.0, oscA_semi=9, noise_level=0.65, penv_amount=10.0, penv_decay=0.025,
          menv_decay=0.05, flt_type="HP", flt_cutoff=600.0, flt_res=0.2, amp_decay=0.17, squash=0.25, rev_size=0.2,
          rev_mix=0.08))
P("trap", "Dark Room Snare", D, "Low, heavy snare drowned in a dark room for slow, sinister beats.",
  M(("Energy", [("Dist Mix", 0.35), ("Cutoff", 0.35)]), ("Body", [("Level A", 0.3)]), ("Tail", [("Reverb Mix", 0.3)]),
    ("Snap", [("Noise Level", 0.2)])),
  mods=SNARE_BODY + [("Velocity", "Cutoff", 0.2)], tags=["Snare", "Dark", "Room"], mood="Dark",
  **noisy(oscA_table="Basic Shapes", oscA_pos=0.15, oscA_semi=2, noise_level=0.6, penv_amount=12.0, penv_decay=0.05,
          menv_decay=0.12, flt_type="LP24", flt_cutoff=2600.0, amp_decay=0.35, rev_size=0.75, rev_damping=0.8,
          rev_mix=0.3))

# ================================================================================================ CLAPS
# Noise = 1 + 2 x velocity + LFO square (90 Hz) - 3 x Mod Env, clamped to 0..1. While the Mod Env is high the
# square cuts the noise into bursts about 11 ms apart; as it falls the low half of the square climbs above 1 and the
# clamp leaves a smooth tail. Gives the 3-4 quick hits of a real clap (velocity changes how many you hear).
CLAP = [("Velocity", "Noise Level", 1.0), ("Velocity", "Noise Level", 1.0), ("LFO 1", "Noise Level", 0.5),
        ("Mod Env", "Noise Level", -1.0), ("Mod Env", "Noise Level", -1.0), ("Mod Env", "Noise Level", -1.0)]


def clap(**kw):
    return noisy(**dict(dict(noise_level=1.0, lfo1_shape="Square", lfo1_rate=90.0, lfo1_retrig=True, menv_decay=0.3,
                             flt_type="BP", flt_cutoff=1200.0, flt_res=0.3, flt_drive=0.4, squash=0.35), **kw))


P("house", "House Clap", D, "Classic layered clap with a short burst and a small bright room.",
  M(("Energy", [("Dist Mix", 0.35), ("Cutoff", 0.25)]), ("Tone", [("Cutoff", 0.3)]), ("Spread", [("Mod FX Mix", 0.4)]),
    ("Room", [("Reverb Mix", 0.3)])),
  mods=CLAP, tags=["Clap", "Classic", "Bright"], mood="Medium",
  **clap(amp_decay=0.2, rev_size=0.3, rev_mix=0.18, mfx_type="Chorus", mfx_mix=0.0))
P("house", "Wide Disco Clap", D, "Big, wide clap with a long bright room for disco and filter house.",
  M(("Energy", [("Dist Mix", 0.35), ("Cutoff", 0.25)]), ("Tone", [("Cutoff", 0.3)]), ("Width", [("Mod FX Mix", 0.4)]),
    ("Room", [("Reverb Mix", 0.3)])),
  mods=CLAP, tags=["Clap", "Disco", "Wide"], mood="Medium",
  **clap(flt_cutoff=1500.0, amp_decay=0.3, mfx_type="Chorus", mfx_depth=0.7, mfx_mix=0.4, rev_size=0.55, rev_mix=0.25))
P("hiphop", "Snap Clap", D, "Dry, short clap with a hard snap for rap and boom bap.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Tone", [("Cutoff", 0.3)]), ("Grit", [("Dist Mix", 0.35)]),
    ("Room", [("Reverb Mix", 0.3)])),
  mods=CLAP, tags=["Clap", "Dry", "Snappy"], mood="Medium",
  **clap(flt_cutoff=1700.0, flt_res=0.4, menv_decay=0.18, amp_decay=0.12, dist_type="Tube", dist_drive=0.35,
         dist_mix=0.3))
P("trap", "Trap Clap", D, "Loud, crunchy trap clap that sits on top of the snare.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.25)]), ("Tone", [("Cutoff", 0.3)]), ("Width", [("Mod FX Mix", 0.4)]),
    ("Room", [("Reverb Mix", 0.3)])),
  mods=CLAP, tags=["Clap", "Trap", "Crunchy"], mood="Aggressive",
  **clap(flt_cutoff=1400.0, flt_res=0.35, amp_decay=0.18, dist_type="Hard", dist_drive=0.6, dist_mix=0.7, squash=0.35,
         rev_size=0.25, rev_mix=0.1))
P("trap", "Haunted Clap", D, "Dark clap fading into a long, damped hall for eerie, slow beats.",
  M(("Energy", [("Dist Mix", 0.35), ("Cutoff", 0.3)]), ("Tone", [("Cutoff", 0.3)]), ("Echo", [("Delay Mix", 0.3)]),
    ("Hall", [("Reverb Mix", 0.3)])),
  mods=CLAP, tags=["Clap", "Dark", "Hall"], mood="Dark",
  **clap(flt_cutoff=850.0, flt_res=0.25, amp_decay=0.35, rev_size=0.85, rev_damping=0.75, rev_mix=0.35))

# ================================================================================================ HATS
def hat(**kw):
    return noisy(**dict(dict(noise_level=0.9, flt_type="HP", flt_cutoff=7500.0, flt_res=0.15, oscB_table="Metal Comb",
                             oscB_oct=2), **kw))


HAT_MODS = [("Velocity", "Cutoff", 0.2), ("Random", "Cutoff", 0.05)]
P("house", "Closed Hat Tick", D, "Tight, crisp closed hat for sixteenth-note house grooves.",
  M(("Energy", [("Dist Mix", 0.35), ("Cutoff", 0.2)]), ("Tone", [("Cutoff", 0.3)]), ("Metal", [("Level B", 0.3)]),
    ("Room", [("Reverb Mix", 0.25)])),
  mods=HAT_MODS, tags=["Hi-Hat", "Closed", "Crisp"], mood="Medium",
  **hat(oscB_level=0.12, amp_decay=0.045))
P("house", "Open Hat Shimmer", D, "Bright open hat on the offbeat, the classic house lift.",
  M(("Energy", [("Dist Mix", 0.35), ("Cutoff", 0.2)]), ("Tone", [("Cutoff", 0.3)]), ("Metal", [("Level B", 0.3)]),
    ("Room", [("Reverb Mix", 0.25)])),
  mods=HAT_MODS, tags=["Hi-Hat", "Open", "Offbeat"], mood="Medium",
  **hat(oscB_level=0.15, flt_cutoff=6500.0, amp_decay=0.32, rev_size=0.3, rev_mix=0.08))
P("house", "Metal Hat", D, "Ringing, metallic hat with a clear pitch, for tech and minimal grooves.",
  M(("Energy", [("Dist Mix", 0.35), ("Cutoff", 0.2)]), ("Tone", [("Cutoff", 0.3)]), ("Ring", [("Level B", 0.3)]),
    ("Room", [("Reverb Mix", 0.25)])),
  mods=HAT_MODS + [("Mod Env", "Warp B", 0.3)], tags=["Hi-Hat", "Metallic", "Tech House"], mood="Medium",
  **hat(oscB_table="Ring Mod", oscB_level=0.45, oscB_oct=3, oscB_semi=5, oscB_warp="FM", oscB_warp_amt=0.4,
        noise_level=0.5, flt_cutoff=5500.0, amp_decay=0.09, menv_decay=0.05))
P("hiphop", "Dusty Closed Hat", D, "Soft, dark closed hat with a gritty edge, like an old drum machine.",
  M(("Energy", [("Dist Mix", 0.35), ("Cutoff", 0.25)]), ("Tone", [("Cutoff", 0.3)]), ("Grit", [("Dist Drive", 0.3)]),
    ("Room", [("Reverb Mix", 0.25)])),
  mods=HAT_MODS, tags=["Hi-Hat", "Closed", "Boom Bap"], mood="Dark",
  **hat(oscB_level=0.1, flt_type="BP", flt_cutoff=5200.0, flt_res=0.2, amp_decay=0.06, dist_type="Bitcrush",
        dist_drive=0.3, dist_tone=0.4, dist_mix=0.3))
P("trap", "Trap Hat Roll", D, "Short, bright hat that stays clean in fast rolls and triplets.",
  M(("Energy", [("Dist Mix", 0.35), ("Cutoff", 0.2)]), ("Tone", [("Cutoff", 0.3)]), ("Metal", [("Level B", 0.3)]),
    ("Room", [("Reverb Mix", 0.25)])),
  mods=HAT_MODS, tags=["Hi-Hat", "Trap", "Roll"], mood="Medium",
  **hat(oscB_level=0.0, flt_cutoff=10500.0, flt_res=0.45, amp_decay=0.025))
P("trap", "Trap Open Hat", D, "Sizzling open hat with a hard top, for trap bounces and fills.",
  M(("Energy", [("Dist Drive", 0.35), ("Cutoff", 0.2)]), ("Tone", [("Cutoff", 0.3)]), ("Metal", [("Level B", 0.3)]),
    ("Room", [("Reverb Mix", 0.25)])),
  mods=HAT_MODS, tags=["Hi-Hat", "Open", "Trap"], mood="Aggressive",
  **hat(oscB_level=0.2, flt_cutoff=7000.0, flt_res=0.25, amp_decay=0.42, dist_type="Hard", dist_drive=0.5,
        dist_mix=0.6))
P("hiphop", "Pedal Hat Chick", D, "Soft, closed pedal hat with a short chick sound for laid-back beats.",
  M(("Energy", [("Dist Mix", 0.35), ("Cutoff", 0.25)]), ("Tone", [("Cutoff", 0.3)]), ("Body", [("Level B", 0.3)]),
    ("Room", [("Reverb Mix", 0.25)])),
  mods=HAT_MODS, tags=["Hi-Hat", "Pedal", "Soft"], mood="Soft",
  **hat(oscB_level=0.18, flt_type="BP", flt_cutoff=3800.0, flt_res=0.3, amp_attack=0.003, amp_decay=0.05))

# ================================================================================================ SHAKERS
def shaker(**kw):
    return noisy(**dict(dict(flt_type="BP", flt_cutoff=6000.0, flt_res=0.25), **kw))


SHAKE_MODS = [("Velocity", "Cutoff", 0.15), ("Random", "Cutoff", 0.1)]
P("house", "Groove Shaker", D, "Bright, quick shaker that keeps sixteenths moving in a house groove.",
  M(("Energy", [("Dist Mix", 0.3), ("Cutoff", 0.2)]), ("Tone", [("Cutoff", 0.3)]), ("Width", [("Pan A", 0.3)]),
    ("Room", [("Reverb Mix", 0.25)])),
  mods=SHAKE_MODS + [("Random", "Pan A", 0.3)], tags=["Shaker", "Groove", "Bright"], mood="Medium",
  **shaker(amp_attack=0.012, amp_decay=0.07))
P("house", "Soft Egg Shaker", D, "Gentle, round shaker with a slow swell, for deep and organic house.",
  M(("Energy", [("Dist Mix", 0.3), ("Cutoff", 0.25)]), ("Tone", [("Cutoff", 0.3)]), ("Swell", [("Noise Level", -0.2)]),
    ("Room", [("Reverb Mix", 0.25)])),
  mods=SHAKE_MODS, tags=["Shaker", "Soft", "Organic"], mood="Soft",
  **shaker(flt_cutoff=4200.0, flt_res=0.15, amp_attack=0.025, amp_decay=0.1, rev_size=0.3, rev_mix=0.1))
P("hiphop", "Dry Tambourine", D, "Jingly tambourine hit with metal rings over a short shake.",
  M(("Energy", [("Dist Mix", 0.3), ("Cutoff", 0.2)]), ("Tone", [("Cutoff", 0.3)]), ("Jingle", [("Level B", 0.3)]),
    ("Room", [("Reverb Mix", 0.25)])),
  mods=SHAKE_MODS + [("LFO 1", "Level B", 0.3)], tags=["Tambourine", "Jingle", "Soul"], mood="Medium",
  **shaker(oscB_table="Metal Comb", oscB_oct=3, oscB_level=0.25, flt_type="HP", flt_cutoff=5000.0, amp_attack=0.004,
           amp_decay=0.16, lfo1_shape="Square", lfo1_rate=28.0, lfo1_retrig=True))
P("trap", "Crunchy Shaker", D, "Gritty, clipped shaker for trap and drill hi-hat patterns.",
  M(("Energy", [("Dist Drive", 0.3), ("Cutoff", 0.2)]), ("Tone", [("Cutoff", 0.3)]), ("Grit", [("Dist Mix", 0.3)]),
    ("Room", [("Reverb Mix", 0.25)])),
  mods=SHAKE_MODS, tags=["Shaker", "Trap", "Gritty"], mood="Aggressive",
  **shaker(flt_cutoff=7000.0, flt_res=0.3, amp_attack=0.006, amp_decay=0.06, dist_type="Hard", dist_drive=0.55,
           dist_mix=0.65))

# ================================================================================================ WOOD AND SNAPS
P("house", "Wood Block Knock", D, "Short, hollow wood block knock for syncopated house and afro grooves.",
  M(("Energy", [("Dist Mix", 0.35), ("Cutoff", 0.25)]), ("Tone", [("Cutoff", 0.3)]), ("Click", [("Noise Level", 0.2)]),
    ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Mod Env", "Noise Level", 0.6), ("Velocity", "Cutoff", 0.2)], tags=["Wood Block", "Wood", "Percussion"], mood="Medium",
  **noisy(oscA_table="Basic Shapes", oscA_pos=0.33, oscA_level=1.0, oscA_oct=1, oscA_semi=9, noise_level=0.0,
          penv_amount=5.0, penv_decay=0.01, menv_decay=0.006, flt_type="BP", flt_cutoff=700.0, flt_res=0.3,
          amp_decay=0.06))
P("hiphop", "Finger Snap", D, "Dry, close finger snap for slow rap and r&b beats.",
  M(("Energy", [("Dist Mix", 0.35), ("Cutoff", 0.25)]), ("Tone", [("Cutoff", 0.3)]), ("Body", [("Level A", 0.3)]),
    ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.2), ("Mod Env", "Level A", 0.5)], tags=["Snap", "Dry", "R&B"], mood="Soft",
  **noisy(oscA_table="Basic Shapes", oscA_pos=0.0, oscA_oct=1, oscA_semi=7, noise_level=0.8, menv_decay=0.01,
          flt_type="BP", flt_cutoff=2600.0, flt_res=0.35, amp_decay=0.07, rev_size=0.2, rev_mix=0.1))

CANDIDATES = bc.end(_s)

if __name__ == "__main__":
    bc.write("drums1", CANDIDATES)
