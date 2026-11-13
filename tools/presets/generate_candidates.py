#!/usr/bin/env python3
"""Second batch of VOLT presets: 100 candidates for listening review (guitars, pianos, creative leads, ...).

The candidates are written to tools/presets/candidates/ (NOT embedded in the plugin). After the review the chosen
ones get merged into presets/.

    python3 tools/presets/generate_candidates.py                         # write candidates/
    python3 tools/presets/generate_candidates.py --trim report.json      # level-match from a render report, then write
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_presets as gp  # noqa: E402  (defaults, tables, validation helper P)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "candidates")
TRIM_FILE = os.path.join(HERE, "candidate_trims.json")
TARGET_LUFS = -15.0

START = len(gp.PRESETS)
P = gp.P

# Common macro sets (labels are what the musician sees on the four macro knobs).
def M(*pairs):
    return [(label, routes) for label, routes in pairs]

# =====================================================================================================
# GUITARS (20) – synthesised guitar-like tones: plucks, riffs, chugs, clean funk, slide, feedback
# =====================================================================================================
P("mechanical", "Overdrive Rhythm Guitar", "Guitar", "Two detuned saws through a tube amp stage for crunchy rhythm chords.",
  M(("Gain", [("Dist Drive", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Bite", [("Resonance", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.25), ("Key Track", "Cutoff", 0.15)], tags=["Guitar", "Rock"],
  oscA_table="Analog Saw", oscB_table="Analog Square", oscB_level=0.45, oscB_fine=-9.0, flt_type="LP24", flt_cutoff=2400.0,
  flt_res=0.2, flt_envamt=0.2, fenv_decay=0.5, fenv_sustain=0.4, amp_decay=1.3, amp_sustain=0.45, amp_release=0.18,
  dist_type="Tube", dist_drive=0.6, dist_tone=0.55, dist_mix=0.9, squash=0.25, rev_mix=0.1)
P("industrial", "Palm Mute Chug", "Guitar", "Tight palm-muted chug with a hard-clipped bite for industrial riffs.",
  M(("Gain", [("Dist Drive", 0.35)]), ("Mute", [("Cutoff", -0.35)]), ("Low", [("Sub Level", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.3)], tags=["Guitar", "Distorted"],
  oscA_table="Buzz", oscA_pos=0.2, oscB_table="Analog Saw", oscB_level=0.4, oscB_oct=-1, sub_level=0.15, flt_type="LP24",
  flt_cutoff=850.0, flt_envamt=0.4, fenv_decay=0.12, fenv_sustain=0.0, amp_decay=0.22, amp_sustain=0.12, amp_release=0.08,
  dist_type="Hard", dist_drive=0.55, dist_tone=0.5, dist_mix=0.85, squash=0.35)
P("mechanical", "Fuzz Lead Guitar", "Guitar", "Singing fuzz lead with slight sync edge, slide and mod-wheel vibrato.",
  M(("Fuzz", [("Dist Drive", 0.35)]), ("Edge", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Mod Wheel", "Pitch", 0.012), ("LFO 1", "Pitch", 0.003)], tags=["Guitar", "Lead"],
  voice_mode="Legato", glide=0.04, oscA_table="Sync Saw", oscA_pos=0.12, oscB_table="Analog Saw", oscB_level=0.4,
  oscB_fine=7.0, lfo1_rate=5.5, flt_type="LP24", flt_cutoff=3200.0, flt_res=0.25, amp_release=0.25,
  dist_type="Hard", dist_drive=0.7, dist_tone=0.5, dist_mix=0.95, dly_time="1/8D", dly_mix=0.12)
P("analog", "Clean Funk Chop", "Guitar", "Quacky muted single-coil chop with a fast filter snap for funk strums.",
  M(("Quack", [("Resonance", 0.3)]), ("Snap", [("Cutoff", 0.35)]), ("Chorus", [("Mod FX Mix", 0.4)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.3)], tags=["Guitar", "Funk"],
  oscA_table="PWM", oscA_pos=0.6, oscB_table="Analog Saw", oscB_level=0.25, flt_type="LP24", flt_cutoff=700.0, flt_res=0.5,
  flt_envamt=0.5, fenv_decay=0.12, fenv_sustain=0.0, amp_decay=0.4, amp_sustain=0.2, amp_release=0.06,
  mfx_type="Chorus", mfx_mix=0.25, squash=0.45)
P("cold", "Nylon Pluck", "Guitar", "Soft nylon-string pluck with a woody body and short room.",
  M(("Body", [("Level B", 0.3)]), ("Pick", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Key Track", "Cutoff", 0.2)], tags=["Guitar", "Acoustic"],
  oscA_table="FM Bell", oscA_pos=0.08, oscB_table="Basic Shapes", oscB_pos=0.3, oscB_level=0.5, flt_type="LP12",
  flt_cutoff=2600.0, flt_envamt=0.25, fenv_decay=0.15, fenv_sustain=0.0, amp_decay=1.6, amp_sustain=0.0, amp_release=0.3,
  rev_size=0.4, rev_mix=0.14)
P("stadium", "Twelve String Shimmer", "Guitar", "Jangly octave-doubled strum with chorus and stereo echoes.",
  M(("Octave", [("Level B", 0.3)]), ("Shimmer", [("Mod FX Mix", 0.4)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Guitar", "Bright"],
  oscA_table="Analog Saw", oscA_voices=2, uni_detune=0.15, oscB_table="Saw Octaves", oscB_oct=1, oscB_level=0.35,
  flt_type="LP24", flt_cutoff=4200.0, flt_envamt=0.2, fenv_decay=0.3, fenv_sustain=0.1, amp_decay=2.0, amp_sustain=0.15,
  amp_release=0.4, mfx_type="Chorus", mfx_depth=0.6, mfx_mix=0.4, dly_mode="PingPong", dly_time="1/8D", dly_mix=0.14,
  rev_mix=0.15)
P("discohouse", "Auto Wah Guitar", "Guitar", "Overdriven guitar swept by a tempo-synced wah that opens on every eighth note.",
  M(("Wah", [("Formant", 0.4)]), ("Gain", [("Dist Drive", 0.35)]), ("Peak", [("Resonance", 0.25)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("LFO 1", "Formant", 0.45)], tags=["Guitar", "Wah"],
  oscA_table="Analog Saw", oscB_table="Analog Square", oscB_level=0.3, flt_type="Formant", flt_cutoff=1150.0, flt_res=0.5,
  flt_vowel=0.4, lfo1_shape="Triangle", lfo1_sync=True, lfo1_div="1/8", lfo1_retrig=True, amp_decay=1.0, amp_sustain=0.5,
  amp_release=0.2, dist_type="Tube", dist_drive=0.5, dist_mix=0.8, dly_time="1/8", dly_mix=0.08)
P("analog", "Surf Tremolo Guitar", "Guitar", "Twangy square pluck with tempo tremolo and a splashy spring-like reverb.",
  M(("Soft", [("Level A", -0.3)]), ("Twang", [("Cutoff", 0.35)]), ("Spring", [("Reverb Mix", 0.3)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("LFO 1", "Level A", 0.35)], tags=["Guitar", "Vintage"],
  oscA_table="Analog Square", oscA_pos=0.35, oscA_level=0.55, flt_type="LP24", flt_cutoff=3000.0, flt_envamt=0.3,
  fenv_decay=0.2, fenv_sustain=0.2, amp_decay=1.8, amp_sustain=0.2, amp_release=0.4, lfo1_shape="Sine", lfo1_sync=True,
  lfo1_div="1/16", rev_size=0.55, rev_damping=0.2, rev_mix=0.3)
P("industrial", "Industrial Guitar Wall", "Guitar", "Wide wall of buzzing, raspy saws crushed by clipping and multiband squash.",
  M(("Wall", [("Mod FX Mix", 0.4)]), ("Gain", [("Dist Drive", 0.35)]), ("Rasp", [("WT Pos B", 0.5)]), ("Tone", [("Cutoff", 0.35)])),
  tags=["Guitar", "Distorted"],
  oscA_table="Buzz", oscA_pos=0.5, oscA_voices=3, uni_detune=0.3, uni_spread=0.9, oscB_table="Rasp", oscB_pos=0.4,
  oscB_level=0.4, flt_type="LP24", flt_cutoff=3000.0, amp_attack=0.004, amp_decay=1.0, amp_sustain=0.7, amp_release=0.2,
  dist_type="Hard", dist_drive=0.65, dist_tone=0.5, dist_mix=0.95, squash=0.55)
P("discohouse", "Muted Disco Picking", "Guitar", "Short muted sixteenth-note picking that pumps with the groove.",
  M(("Mute", [("Cutoff", -0.3)]), ("Grit", [("Dist Mix", 0.2)]), ("Echo", [("Delay Mix", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Guitar", "Disco"],
  arp_on=True, arp_mode="UpDown", arp_rate="1/16", arp_gate=0.4, oscA_table="PWM Saw", oscA_pos=0.4, flt_type="LP24",
  flt_cutoff=1600.0, flt_res=0.25, flt_envamt=0.3, fenv_decay=0.08, fenv_sustain=0.0, amp_decay=0.15, amp_sustain=0.0,
  amp_release=0.05, pump_amount=0.4, dly_time="1/16", dly_mix=0.1)
P("mechanical", "Feedback Sustain Guitar", "Guitar", "Endless sustaining guitar that blooms into a resonant feedback whine.",
  M(("Feedback", [("Resonance", 0.25)]), ("Gain", [("Dist Drive", 0.35)]), ("Bloom", [("WT Pos A", 0.5)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Filter Env", "WT Pos A", 0.4), ("LFO 2", "Pitch A", 0.003)], tags=["Guitar", "Lead"],
  voice_mode="Legato", glide=0.05, oscA_table="Sine Drive", oscA_pos=0.6, oscB_table="Sync Saw", oscB_level=0.4,
  oscB_pos=0.2, flt_type="Ladder", flt_cutoff=1400.0, flt_res=0.65, fenv_attack=0.6, fenv_decay=2.0, fenv_sustain=0.8,
  lfo2_rate=4.8, dist_type="Fold", dist_drive=0.4, dist_mix=0.7, dly_time="1/4", dly_mix=0.12)
P("gospel", "Gospel Slide Guitar", "Guitar", "Warm sliding lead guitar for church-style fills with expressive vibrato.",
  M(("Slide", [("Pitch", 0.02)]), ("Warm", [("Cutoff", 0.35)]), ("Gain", [("Dist Drive", 0.35)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("LFO 1", "Pitch", 0.004), ("Aftertouch", "Pitch", 0.01)], tags=["Guitar", "Slide"],
  voice_mode="Legato", glide=0.18, oscA_table="Analog Saw", oscB_table="Hollow", oscB_level=0.4, lfo1_rate=5.0,
  flt_type="LP24", flt_cutoff=2600.0, flt_res=0.2, amp_attack=0.01, amp_release=0.35, dist_type="Tube", dist_drive=0.45,
  dist_mix=0.7, rev_mix=0.18)
P("stadium", "Jangle Arp Guitar", "Guitar", "Bright plucked guitar arpeggio rolling over two octaves.",
  M(("Pick", [("Cutoff", 0.35)]), ("Chorus", [("Mod FX Mix", 0.4)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.2)], tags=["Guitar", "Arp"],
  arp_on=True, arp_mode="UpDown", arp_rate="1/16", arp_octaves=2, arp_gate=0.7, oscA_table="Analog Saw", oscB_table="PWM",
  oscB_pos=0.5, oscB_level=0.35, flt_type="LP24", flt_cutoff=2200.0, flt_envamt=0.35, fenv_decay=0.15, fenv_sustain=0.0,
  amp_decay=0.6, amp_sustain=0.0, amp_release=0.25, mfx_mix=0.3, dly_mode="PingPong", dly_time="1/8D", dly_mix=0.15)
P("cold", "Acoustic Strum", "Guitar", "Steel-string acoustic strum with bright attack and natural decay.",
  M(("Bright", [("Cutoff", 0.35)]), ("Body", [("WT Pos A", 0.4)]), ("Width", [("Mod FX Mix", 0.4)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.25), ("Key Track", "Cutoff", 0.15)], tags=["Guitar", "Acoustic"],
  oscA_table="Strings", oscA_pos=0.15, oscB_table="FM Bell", oscB_pos=0.25, oscB_level=0.45, flt_type="LP12",
  flt_cutoff=4500.0, flt_envamt=0.2, fenv_decay=0.25, fenv_sustain=0.1, amp_decay=2.4, amp_sustain=0.0, amp_release=0.4,
  mfx_mix=0.15, rev_size=0.45, rev_mix=0.15)
P("industrial", "Bit Crushed Riff", "Guitar", "Lo-fi riff guitar chewed by a bitcrusher for gritty loops.",
  M(("Bits", [("Dist Drive", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Crush", [("WT Pos A", 0.5)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Guitar", "Lo-Fi"],
  oscA_table="Crush", oscA_pos=0.3, oscB_table="Analog Saw", oscB_level=0.4, flt_type="LP24", flt_cutoff=1800.0,
  flt_envamt=0.3, fenv_decay=0.2, fenv_sustain=0.2, amp_decay=0.7, amp_sustain=0.35, amp_release=0.1,
  dist_type="Bitcrush", dist_drive=0.35, dist_mix=0.6)
P("cinematic", "Space Echo Guitar", "Guitar", "Clean pluck thrown into long dotted ping-pong echoes and a dark hall.",
  M(("Echo", [("Delay Mix", 0.3)]), ("Tone", [("Cutoff", 0.35)]), ("Hall", [("Reverb Mix", 0.3)]), ("Grit", [("Dist Mix", 0.4)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Guitar", "Ambient"],
  oscA_table="Analog Saw", oscB_table="Basic Shapes", oscB_pos=0.33, oscB_level=0.35, flt_type="LP24", flt_cutoff=2600.0,
  flt_envamt=0.3, fenv_decay=0.2, fenv_sustain=0.1, amp_decay=1.2, amp_sustain=0.1, amp_release=0.4, dly_mode="PingPong",
  dly_time="1/4D", dly_feedback=0.5, dly_mix=0.3, rev_size=0.75, rev_damping=0.6, rev_mix=0.22)
P("analog", "Phaser Rhythm Guitar", "Guitar", "Seventies rhythm guitar swirling through a slow phaser.",
  M(("Phase", [("Mod FX Mix", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Gain", [("Dist Drive", 0.35)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Guitar", "Funk"],
  oscA_table="Analog Square", oscA_pos=0.25, oscB_table="Analog Saw", oscB_level=0.35, flt_type="LP24", flt_cutoff=2200.0,
  flt_envamt=0.25, fenv_decay=0.25, fenv_sustain=0.2, amp_decay=1.0, amp_sustain=0.4, amp_release=0.15, mfx_type="Phaser",
  mfx_rate=0.25, mfx_depth=0.7, mfx_mix=0.55, dist_type="Tube", dist_drive=0.3, dist_mix=0.5)
P("epic", "Ebow Swell Guitar", "Guitar", "Bowed-sounding guitar that swells in without a pick attack.",
  M(("Swell", [("Cutoff", 0.35)]), ("Edge", [("WT Pos A", 0.4)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Pitch", 0.002)], tags=["Guitar", "Cinematic"],
  voice_mode="Legato", glide=0.06, oscA_table="Sync Saw", oscA_pos=0.08, oscB_table="Hollow", oscB_level=0.4,
  lfo1_rate=5.0, flt_type="LP24", flt_cutoff=2400.0, amp_attack=0.45, amp_release=0.9, dist_type="Tube", dist_drive=0.4,
  dist_mix=0.6, dly_time="1/4", dly_feedback=0.45, dly_mix=0.18, rev_size=0.8, rev_mix=0.25)
P("mechanical", "Octave Rock Lead", "Guitar", "Hard-driven octave-doubled guitar lead for big riff hooks.",
  M(("Octave", [("Level B", 0.3)]), ("Gain", [("Dist Drive", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Mod Wheel", "Pitch", 0.012)], tags=["Guitar", "Rock"],
  voice_mode="Mono", glide=0.02, oscA_table="Analog Saw", oscB_table="Analog Saw", oscB_oct=1, oscB_level=0.45,
  flt_type="LP24", flt_cutoff=3000.0, flt_res=0.2, amp_release=0.2, dist_type="Hard", dist_drive=0.6, dist_mix=0.9,
  dly_time="1/8", dly_mix=0.1)
P("rawhouse", "Fuzzbox Bass Guitar", "Guitar", "Fuzzed low guitar riff tone between bass and baritone guitar.",
  M(("Fuzz", [("Dist Drive", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Low", [("Sub Level", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Guitar", "Fuzz"],
  oscA_table="Analog Square", oscA_pos=0.15, oscA_oct=-1, oscB_table="Analog Saw", oscB_level=0.4, flt_type="LP24",
  flt_cutoff=1600.0, flt_envamt=0.25, fenv_decay=0.3, fenv_sustain=0.3, amp_decay=0.9, amp_sustain=0.5, amp_release=0.12,
  dist_type="Fold", dist_drive=0.45, dist_tone=0.5, dist_mix=0.8)

# =====================================================================================================
# PIANOS & KEYS (20)
# =====================================================================================================
P("cold", "Felt Grand", "Keys", "Soft felt piano with a muted hammer and gentle room.",
  M(("Felt", [("Cutoff", -0.3)]), ("Hammer", [("WT Pos A", 0.4)]), ("Body", [("Level B", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Key Track", "Cutoff", 0.2), ("Velocity", "Level A", 0.2)], tags=["Piano", "Soft"],
  oscA_table="FM Bell", oscA_pos=0.06, oscA_level=0.6, oscB_table="Basic Shapes", oscB_pos=0.2, oscB_level=0.5,
  flt_type="LP12", flt_cutoff=1800.0, flt_envamt=0.2, fenv_decay=0.6, fenv_sustain=0.0, amp_decay=3.5, amp_sustain=0.0,
  amp_release=0.5, rev_size=0.5, rev_mix=0.2)
P("stadium", "Bright Concert Piano", "Keys", "Bright stage piano with a clear attack for pop chords.",
  M(("Bright", [("Cutoff", 0.35)]), ("Hammer", [("WT Pos A", 0.4)]), ("Width", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.35), ("Key Track", "Cutoff", 0.2)], tags=["Piano", "Bright"],
  oscA_table="FM Bell", oscA_pos=0.22, oscB_table="Analog Square", oscB_pos=0.6, oscB_level=0.25, flt_type="LP24",
  flt_cutoff=4500.0, flt_envamt=0.25, fenv_decay=1.0, fenv_sustain=0.0, amp_decay=4.0, amp_sustain=0.0, amp_release=0.5,
  rev_size=0.6, rev_mix=0.2)
P("gospel", "Gospel Upright", "Keys", "Slightly detuned upright piano for church chords and runs.",
  M(("Detune", [("Pitch B", 0.004)]), ("Bright", [("Cutoff", 0.35)]), ("Body", [("Level B", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Key Track", "Cutoff", 0.15)], tags=["Piano", "Gospel"],
  oscA_table="FM Bell", oscA_pos=0.18, oscB_table="Analog Saw", oscB_pos=0.3, oscB_level=0.3, oscB_fine=6.0,
  flt_type="LP24", flt_cutoff=3000.0, flt_envamt=0.25, fenv_decay=0.8, fenv_sustain=0.0, amp_decay=3.0, amp_sustain=0.0,
  amp_release=0.45, rev_size=0.45, rev_mix=0.16)
P("gospel", "Honky Tonk Bar", "Keys", "Out-of-tune saloon piano with two strings per note beating against each other.",
  M(("Detune", [("Pitch B", 0.006)]), ("Bright", [("Cutoff", 0.35)]), ("Room", [("Reverb Mix", 0.25)]), ("Grit", [("Dist Mix", 0.4)])),
  mods=[("Velocity", "Cutoff", 0.3)], tags=["Piano", "Vintage"],
  oscA_table="FM Bell", oscA_pos=0.25, oscB_table="FM Bell", oscB_pos=0.25, oscB_level=0.7, oscB_fine=18.0,
  flt_type="LP24", flt_cutoff=4000.0, amp_decay=2.5, amp_sustain=0.0, amp_release=0.3, dist_type="Tube", dist_drive=0.2,
  rev_mix=0.12)
P("analog", "Autopan Electric Piano", "Keys", "Bell-toned electric piano with stereo auto-pan and velocity bark.",
  M(("Bark", [("WT Pos A", 0.4)]), ("Pan", [("Pan A", 0.3)]), ("Phase", [("Mod FX Mix", 0.4)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "WT Pos A", 0.4), ("LFO 1", "Pan A", 0.6)], tags=["Electric Piano", "Vintage"],
  oscA_table="FM Bell", oscA_pos=0.1, oscB_table="Basic Shapes", oscB_level=0.4, lfo1_sync=True, lfo1_div="1/4",
  flt_type="LP12", flt_cutoff=5000.0, amp_decay=2.6, amp_sustain=0.15, amp_release=0.4, mfx_type="Phaser", mfx_rate=0.3,
  mfx_mix=0.15, rev_mix=0.14)
P("analog", "Reed Electric Piano", "Keys", "Reedy, slightly barking electric piano with tube grit when played hard.",
  M(("Bark", [("Dist Drive", 0.35)]), ("Reed", [("WT Pos A", 0.4)]), ("Soft", [("Level A", -0.2)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Dist Drive", 0.4), ("Velocity", "Cutoff", 0.25)], tags=["Electric Piano", "Vintage"],
  oscA_table="Hollow", oscA_pos=0.45, oscB_table="Sine Drive", oscB_pos=0.3, oscB_level=0.4, flt_type="LP24",
  flt_cutoff=3200.0, amp_decay=2.0, amp_sustain=0.2, amp_release=0.3, dist_type="Tube", dist_drive=0.3, dist_mix=0.5,
  rev_mix=0.12)
P("epic", "Dark Ballad Piano", "Keys", "Dark, distant piano with a cathedral tail for dramatic intros.",
  M(("Dark", [("Cutoff", -0.3)]), ("Hammer", [("WT Pos A", 0.4)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.3), ("Key Track", "Cutoff", 0.2)], tags=["Piano", "Dramatic"],
  oscA_table="FM Bell", oscA_pos=0.12, oscB_table="Hollow", oscB_pos=0.2, oscB_level=0.3, flt_type="LP24",
  flt_cutoff=1500.0, amp_decay=4.0, amp_sustain=0.0, amp_release=1.0, rev_size=0.85, rev_damping=0.6, rev_mix=0.32)
P("cold", "Lo-Fi Wobble Piano", "Keys", "Tape-wobbly, bit-reduced piano for lonely late-night beats.",
  M(("Wobble", [("Pitch", 0.006)]), ("Bits", [("Dist Mix", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("LFO 1", "Pitch", 0.004), ("Velocity", "Cutoff", 0.2)], tags=["Piano", "Lo-Fi"],
  oscA_table="FM Bell", oscA_pos=0.15, oscB_table="Basic Shapes", oscB_pos=0.25, oscB_level=0.4, lfo1_rate=0.7,
  flt_type="LP24", flt_cutoff=2400.0, amp_decay=3.0, amp_sustain=0.0, amp_release=0.4, dist_type="Bitcrush",
  dist_drive=0.15, dist_tone=0.45, dist_mix=0.45, rev_mix=0.15)
P("discohouse", "Toy Piano", "Keys", "Tiny metallic toy piano for playful high melodies.",
  M(("Metal", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "WT Pos A", 0.3)], tags=["Piano", "Playful"],
  oscA_table="FM Digital", oscA_pos=0.3, oscA_oct=1, oscB_table="Bell Metal", oscB_oct=1, oscB_level=0.3,
  flt_type="LP12", flt_cutoff=8000.0, amp_decay=0.9, amp_sustain=0.0, amp_release=0.3, dly_mode="PingPong",
  dly_time="1/8", dly_mix=0.12, rev_mix=0.12)
P("rawhouse", "House Piano Stab", "Keys", "Bright stacked house piano that cuts through a dance mix and pumps.",
  M(("Bright", [("Cutoff", 0.35)]), ("Grit", [("Dist Mix", 0.2)]), ("Width", [("Mod FX Mix", 0.4)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.3)], tags=["Piano", "House"],
  oscA_table="FM Bell", oscA_pos=0.35, oscB_table="Analog Square", oscB_pos=0.4, oscB_level=0.35, flt_type="LP24",
  flt_cutoff=5000.0, amp_decay=1.2, amp_sustain=0.15, amp_release=0.25, pump_amount=0.35, squash=0.3, rev_mix=0.12)
P("epic", "Baroque Harpsichord", "Keys", "Plucky harpsichord-like keys with a nasal synced edge.",
  M(("Quill", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Width", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "WT Pos A", 0.2)], tags=["Harpsichord", "Dramatic"],
  oscA_table="Sync Square", oscA_pos=0.3, oscB_table="Analog Saw", oscB_oct=1, oscB_level=0.25, flt_type="HP",
  flt_cutoff=300.0, flt_res=0.2, amp_decay=1.8, amp_sustain=0.1, amp_release=0.3, rev_size=0.6, rev_mix=0.2, squash=0.3)
P("cinematic", "Glass Piano", "Keys", "Crystalline glass-like piano with icy delay trails.",
  M(("Glass", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "WT Pos A", 0.3)], tags=["Piano", "Cinematic"],
  oscA_table="Bell Metal", oscA_pos=0.2, oscB_table="FM Bell", oscB_pos=0.3, oscB_level=0.5, flt_type="LP12",
  flt_cutoff=7000.0, amp_decay=3.0, amp_sustain=0.0, amp_release=0.8, dly_mode="PingPong", dly_time="1/4D",
  dly_mix=0.16, rev_size=0.8, rev_mix=0.25)
P("industrial", "Prepared Piano", "Keys", "Piano with objects on the strings: clanky, metallic and slightly folded.",
  M(("Clank", [("WT Pos A", 0.4)]), ("Fold", [("Dist Mix", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "WT Pos A", 0.3)], tags=["Piano", "Experimental"],
  oscA_table="Metal Comb", oscA_pos=0.3, oscB_table="FM Bell", oscB_pos=0.4, oscB_level=0.5, flt_type="Notch",
  flt_cutoff=1200.0, flt_res=0.3, amp_decay=1.4, amp_sustain=0.0, amp_release=0.3, dist_type="Fold", dist_drive=0.25,
  dist_mix=0.25, rev_size=0.4, rev_mix=0.15)
P("cold", "Celeste Box", "Keys", "Soft music-box celeste ringing an octave up.",
  M(("Ring", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  tags=["Celeste", "Soft"],
  oscA_table="FM Bell", oscA_pos=0.4, oscA_oct=1, oscB_table="Basic Shapes", oscB_pos=0.33, oscB_oct=1, oscB_level=0.35,
  flt_type="LP12", flt_cutoff=6000.0, amp_decay=1.8, amp_sustain=0.0, amp_release=0.6, dly_time="1/4", dly_mix=0.12,
  rev_size=0.7, rev_mix=0.25)
P("gospel", "Organ Piano Hybrid", "Keys", "Piano attack that blooms into a sustained drawbar organ tail.",
  M(("Organ", [("Level B", 0.3)]), ("Bright", [("Cutoff", 0.35)]), ("Rotor", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Piano", "Organ"],
  oscA_table="FM Bell", oscA_pos=0.2, oscB_table="Drawbars", oscB_pos=0.5, oscB_oct=1, oscB_level=0.4, flt_type="LP24",
  flt_cutoff=5000.0, amp_decay=1.5, amp_sustain=0.45, amp_release=0.4, mfx_type="Chorus", mfx_rate=0.8, mfx_mix=0.25,
  rev_mix=0.18)
P("stadium", "Marimba Keys", "Keys", "Woody mallet keys with a quick knock and short ring.",
  M(("Knock", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "WT Pos A", 0.3)], tags=["Mallet", "Bright"],
  oscA_table="Basic Shapes", oscA_pos=0.03, oscB_table="FM Bell", oscB_pos=0.15, oscB_level=0.4, penv_amount=7.0,
  penv_decay=0.01, flt_type="LP12", flt_cutoff=5000.0, amp_decay=0.9, amp_sustain=0.1, amp_release=0.2, squash=0.35,
  dly_mode="PingPong", dly_time="1/8D", dly_mix=0.12, rev_mix=0.12)
P("analog", "Motor Vibraphone", "Keys", "Vibraphone with a spinning-fan tremolo and long ring.",
  M(("Soft", [("Level A", -0.2)]), ("Tone", [("Cutoff", 0.35)]), ("Width", [("Mod FX Mix", 0.4)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("LFO 1", "Level A", 0.3), ("Velocity", "WT Pos A", 0.2)], tags=["Mallet", "Vintage"],
  oscA_table="FM Bell", oscA_pos=0.08, oscA_level=0.6, oscB_table="Basic Shapes", oscB_level=0.3, lfo1_rate=5.5,
  flt_type="LP12", flt_cutoff=6000.0, amp_decay=3.2, amp_sustain=0.0, amp_release=0.8, rev_mix=0.18)
P("industrial", "Saturated Keys Stab", "Keys", "Overdriven brassy key stab that hits like a slap.",
  M(("Drive", [("Dist Drive", 0.35)]), ("Bite", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Dist Drive", 0.3)], tags=["Stab", "Distorted"],
  oscA_table="FM Brass", oscA_pos=0.5, oscB_table="Analog Saw", oscB_level=0.35, flt_type="LP24", flt_cutoff=3500.0,
  amp_decay=0.6, amp_sustain=0.2, amp_release=0.15, dist_type="Hard", dist_drive=0.5, dist_mix=0.7, squash=0.3)
P("rawhouse", "Chord Memory Stab", "Keys", "Classic house chord stab with a snappy filter and a dub echo.",
  M(("Snap", [("Cutoff", 0.35)]), ("Res", [("Resonance", 0.25)]), ("Dub", [("Delay Mix", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Stab", "House"],
  oscA_table="Analog Saw", oscB_table="Analog Square", oscB_level=0.4, oscB_fine=-8.0, flt_type="LP24", flt_cutoff=800.0,
  flt_res=0.35, flt_envamt=0.45, fenv_decay=0.22, fenv_sustain=0.0, amp_decay=0.6, amp_sustain=0.25, amp_release=0.15,
  squash=0.3,
  dly_mode="PingPong", dly_time="1/4D", dly_feedback=0.45, dly_mix=0.2)
P("discohouse", "Dream Keys", "Keys", "Hazy, sweet keys smeared with chorus and ping-pong echoes.",
  M(("Haze", [("Mod FX Mix", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.25)], tags=["Keys", "Sweet"],
  oscA_table="Hollow", oscA_pos=0.3, oscB_table="FM Bell", oscB_pos=0.2, oscB_level=0.45, flt_type="LP24",
  flt_cutoff=3500.0, amp_attack=0.015, amp_decay=2.0, amp_sustain=0.3, amp_release=0.6, mfx_mix=0.45,
  dly_mode="PingPong", dly_time="1/8D", dly_mix=0.15, rev_mix=0.2)

# =====================================================================================================
# LEADS (25) – each built around a different idea (movement, rhythm, pitch tricks, layering)
# =====================================================================================================
P("cold", "Morphing Vowel Lead", "Lead", "Lead that slowly morphs between vowel shapes every two beats.",
  M(("Morph", [("WT Pos A", 0.4)]), ("Glide", [("Pitch", 0.01)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "WT Pos A", 0.45)], tags=["Vocal", "Movement"],
  voice_mode="Legato", glide=0.08, oscA_table="Vowels", oscA_pos=0.5, lfo1_sync=True, lfo1_div="1/2", lfo1_shape="Triangle",
  flt_type="LP24", flt_cutoff=5000.0, amp_release=0.4, dly_time="1/4", dly_mix=0.12, rev_mix=0.15)
P("discohouse", "Trance Gate Lead", "Lead", "Saw lead chopped into a sixteenth-note gate for rhythmic hooks.",
  M(("Soft", [("Level A", -0.3)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Level A", 0.6)], tags=["Gated", "Rhythmic"],
  oscA_table="Hyper Saw", oscA_pos=0.3, oscA_level=0.5, oscA_voices=3, uni_detune=0.3, lfo1_shape="Square",
  lfo1_sync=True, lfo1_div="1/16", lfo1_retrig=True, flt_type="LP24", flt_cutoff=4500.0, amp_release=0.2,
  dly_mode="PingPong", dly_time="1/8D", dly_mix=0.15)
P("cinematic", "Ring Bell Lead", "Lead", "Ring-modulated bell lead with an inharmonic shimmer.",
  M(("Ring", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Filter Env", "WT Pos A", 0.25)], tags=["Metallic", "Cinematic"],
  voice_mode="Mono", glide=0.03, oscA_table="Ring Mod", oscA_pos=0.35, oscB_table="Basic Shapes", oscB_level=0.35,
  flt_type="LP24", flt_cutoff=6000.0, amp_decay=1.0, amp_sustain=0.6, amp_release=0.4, dly_time="1/8D", dly_mix=0.15,
  rev_mix=0.18)
P("discohouse", "Chiptune Square Lead", "Lead", "Eight-bit square lead with a pitch blip and fast vibrato.",
  M(("Pulse", [("WT Pos A", 0.4)]), ("Bits", [("Dist Mix", 0.4)]), ("Vibrato", [("Pitch", 0.01)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("LFO 1", "Pitch", 0.006)], tags=["8-bit", "Playful"],
  voice_mode="Mono", oscA_table="PWM", oscA_pos=0.45, penv_amount=12.0, penv_decay=0.03, lfo1_rate=7.0,
  flt_type="LP12", flt_cutoff=9000.0, amp_release=0.08, dist_type="Bitcrush", dist_drive=0.2, dist_mix=0.3,
  dly_time="1/8", dly_mix=0.1)
P("industrial", "Portamento Scream", "Lead", "Screaming synced lead that slides between notes with heavy clipping.",
  M(("Scream", [("WT Pos A", 0.4)]), ("Clip", [("Dist Drive", 0.35)]), ("Slide", [("Resonance", 0.25)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("LFO 2", "WT Pos A", 0.2)], tags=["Distorted", "Glide"],
  voice_mode="Legato", glide=0.15, oscA_table="Sync Saw", oscA_pos=0.3, lfo2_rate=0.6, flt_type="Ladder",
  flt_cutoff=2600.0, flt_res=0.4, amp_release=0.2, dist_type="Hard", dist_drive=0.55, dist_mix=0.85, squash=0.3)
P("cold", "Formant Whistle", "Lead", "Airy whistle lead shaped by an 'oo' formant with gentle vibrato.",
  M(("Air", [("Noise Level", 0.2)]), ("Vowel", [("Formant", 0.4)]), ("Vibrato", [("Pitch", 0.01)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Pitch", 0.005)], tags=["Whistle", "Soft"],
  voice_mode="Legato", glide=0.06, oscA_table="Basic Shapes", oscA_pos=0.05, oscA_oct=1, noise_level=0.08,
  flt_type="Formant", flt_cutoff=1700.0, flt_res=0.6, flt_vowel=0.95, lfo1_rate=5.2, amp_attack=0.03, amp_release=0.3,
  rev_size=0.7, rev_mix=0.22)
P("rawhouse", "Acid Glide Lead", "Lead", "Acid lead with sliding notes and a squelchy ladder accent.",
  M(("Squelch", [("Resonance", 0.15)]), ("Open", [("Cutoff", 0.35)]), ("Dirt", [("Dist Mix", 0.4)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.2)], tags=["Acid", "Glide"],
  voice_mode="Legato", glide=0.07, oscA_table="Acid", oscA_pos=0.3, flt_type="Ladder", flt_cutoff=900.0, flt_res=0.72,
  flt_drive=0.3, flt_envamt=0.45, fenv_decay=0.25, fenv_sustain=0.15, amp_release=0.12, dist_drive=0.4, dist_mix=0.3,
  dly_time="1/8D", dly_mix=0.12)
P("industrial", "Random Morph Lead", "Lead", "Digital lead whose timbre jumps randomly on every sixteenth note.",
  M(("Chaos", [("WT Pos A", 0.4)]), ("Grit", [("Dist Mix", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("LFO 1", "WT Pos A", 0.5)], tags=["Glitch", "Movement"],
  voice_mode="Mono", oscA_table="FM Digital", oscA_pos=0.4, lfo1_shape="S&H", lfo1_sync=True, lfo1_div="1/16",
  flt_type="LP24", flt_cutoff=5000.0, amp_release=0.15, dist_type="Soft", dist_drive=0.5, dist_mix=0.5, dly_time="1/16",
  dly_mix=0.1)
P("stadium", "Octave Bounce Lead", "Lead", "Lead that bounces between two octaves in sixteenths when you hold a note.",
  M(("Bright", [("Cutoff", 0.35)]), ("Width", [("Mod FX Mix", 0.4)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  tags=["Arp Lead", "Bright"],
  arp_on=True, arp_mode="Up", arp_rate="1/16", arp_octaves=2, arp_gate=0.85, voice_mode="Mono", oscA_table="Hyper Saw",
  oscA_pos=0.3, oscA_voices=3, uni_detune=0.3, flt_type="LP24", flt_cutoff=5000.0, amp_release=0.1, mfx_mix=0.2,
  dly_mode="PingPong", dly_time="1/8D", dly_mix=0.12)
P("cinematic", "Bell Sync Lead", "Lead", "Synced square layered with a metallic bell for a laser-sharp theme.",
  M(("Sync", [("WT Pos A", 0.4)]), ("Bell", [("Level B", 0.3)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Filter Env", "WT Pos A", 0.3)], tags=["Cinematic", "Bright"],
  voice_mode="Mono", glide=0.03, oscA_table="Sync Square", oscA_pos=0.2, oscB_table="Bell Metal", oscB_pos=0.3,
  oscB_level=0.3, oscB_oct=1, flt_type="LP24", flt_cutoff=6000.0, fenv_decay=0.5, amp_release=0.3, dly_mode="PingPong",
  dly_time="1/8D", dly_mix=0.15, rev_mix=0.15)
P("industrial", "Zap Drop Lead", "Lead", "Buzz lead whose every note starts with a laser-like downward zap.",
  M(("Zap", [("Pitch A", 0.02)]), ("Buzz", [("WT Pos A", 0.4)]), ("Grit", [("Dist Drive", 0.35)]), ("Echo", [("Delay Mix", 0.3)])),
  tags=["Distorted", "Zap"],
  voice_mode="Mono", oscA_table="Buzz", oscA_pos=0.4, penv_amount=24.0, penv_decay=0.06, flt_type="LP24",
  flt_cutoff=4000.0, amp_release=0.15, dist_type="Soft", dist_drive=0.5, dist_mix=0.6, dly_time="1/8", dly_mix=0.1)
P("stadium", "Fifth Stack Lead", "Lead", "Huge supersaw lead with a parallel fifth for anthem melodies.",
  M(("Fifth", [("Level B", 0.3)]), ("Bright", [("Cutoff", 0.35)]), ("Width", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Mod Wheel", "Pitch", 0.01)], tags=["Supersaw", "Anthem"],
  voice_mode="Legato", glide=0.05, oscA_table="Hyper Saw", oscA_pos=0.35, oscA_voices=5, uni_detune=0.4, uni_spread=0.8,
  oscB_table="Analog Saw", oscB_semi=7, oscB_level=0.4, oscB_voices=3, flt_type="LP24", flt_cutoff=5500.0,
  amp_release=0.3, rev_size=0.7, rev_mix=0.2)
P("epic", "Breathy Flute Lead", "Lead", "Breathy flute-like sine lead with chiff and soft vibrato.",
  M(("Breath", [("Noise Level", 0.2)]), ("Tone", [("Cutoff", 0.35)]), ("Vibrato", [("Pitch", 0.01)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Pitch", 0.004), ("Velocity", "Noise Level", 0.1)], tags=["Flute", "Soft"],
  voice_mode="Legato", glide=0.05, oscA_table="Basic Shapes", oscA_pos=0.1, noise_level=0.06, penv_amount=1.0,
  penv_decay=0.05, flt_type="LP12", flt_cutoff=3500.0, lfo1_rate=5.0, amp_attack=0.05, amp_release=0.25,
  rev_size=0.75, rev_mix=0.25)
P("epic", "Hollow Clarinet Lead", "Lead", "Woody odd-harmonic lead in the clarinet register.",
  M(("Reed", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Vibrato", [("Pitch", 0.01)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.25), ("Aftertouch", "Pitch", 0.006)], tags=["Woodwind", "Soft"],
  voice_mode="Legato", glide=0.04, oscA_table="Hollow", oscA_pos=0.35, flt_type="LP24", flt_cutoff=3000.0,
  amp_attack=0.025, amp_release=0.2, rev_mix=0.2)
P("analog", "Phase Mod Lead", "Lead", "FM lead whose brightness breathes slowly through a phaser.",
  M(("Index", [("WT Pos A", 0.4)]), ("Phase", [("Mod FX Mix", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("LFO 1", "WT Pos A", 0.25)], tags=["FM", "Movement"],
  voice_mode="Mono", glide=0.04, oscA_table="FM Brass", oscA_pos=0.3, lfo1_rate=0.3, lfo1_shape="Triangle",
  flt_type="LP24", flt_cutoff=5000.0, amp_release=0.25, mfx_type="Phaser", mfx_rate=0.2, mfx_mix=0.45, dly_time="1/4",
  dly_mix=0.1)
P("discohouse", "Pumped Pluck Lead", "Lead", "Short pluck lead that ducks on every beat for French-house hooks.",
  M(("Pluck", [("Cutoff", 0.35)]), ("Grit", [("Dist Mix", 0.2)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.2)], tags=["Pump", "Pluck"],
  oscA_table="Analog Saw", oscB_table="PWM", oscB_pos=0.4, oscB_level=0.4, flt_type="LP24", flt_cutoff=1500.0,
  flt_envamt=0.45, fenv_decay=0.18, fenv_sustain=0.1, amp_decay=0.5, amp_sustain=0.3, amp_release=0.15,
  pump_amount=0.6, dly_mode="PingPong", dly_time="1/8D", dly_mix=0.15)
P("cinematic", "Reese Lead", "Lead", "Thick, phasing two-saw lead with slowly drifting filter.",
  M(("Drift", [("Cutoff", 0.35)]), ("Phase", [("Mod FX Mix", 0.4)]), ("Grit", [("Dist Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Cutoff", 0.15)], tags=["Dark", "Wide"],
  voice_mode="Mono", glide=0.04, oscA_table="Analog Saw", oscA_voices=2, uni_detune=0.6, uni_spread=0.6,
  oscB_table="Analog Saw", oscB_oct=-1, oscB_level=0.35, flt_type="LP24", flt_cutoff=2200.0, flt_res=0.2,
  lfo1_rate=0.2, amp_release=0.2, rev_mix=0.12)
P("industrial", "Glitch S&H Lead", "Lead", "Stuttering lead with random filter jumps and crushed edges.",
  M(("Glitch", [("Cutoff", 0.35)]), ("Bits", [("Dist Drive", 0.35)]), ("Chaos", [("Resonance", 0.25)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("LFO 1", "Cutoff", 0.35), ("LFO 1", "Pitch A", 0.005)], tags=["Glitch", "Lo-Fi"],
  voice_mode="Mono", oscA_table="PWM Saw", oscA_pos=0.4, lfo1_shape="S&H", lfo1_sync=True, lfo1_div="1/16",
  flt_type="LP24", flt_cutoff=2500.0, flt_res=0.4, amp_release=0.12, dist_type="Bitcrush", dist_drive=0.3, dist_mix=0.5,
  dly_time="1/16", dly_mix=0.1)
P("stadium", "Crystal Saw Lead", "Lead", "Glossy wide saw lead with a pitch flick on every note.",
  M(("Flick", [("Pitch A", 0.01)]), ("Bright", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  tags=["Supersaw", "Bright"],
  voice_mode="Mono", glide=0.03, oscA_table="Hyper Saw", oscA_pos=0.45, oscA_voices=7, uni_detune=0.45, uni_spread=0.9,
  penv_amount=5.0, penv_decay=0.04, flt_type="LP24", flt_cutoff=7000.0, amp_release=0.3, dly_mode="PingPong",
  dly_time="1/8D", dly_mix=0.15, rev_mix=0.18)
P("industrial", "Comb Sweep Lead", "Lead", "Metallic comb lead whose notch sweeps like a jet.",
  M(("Comb", [("WT Pos A", 0.4)]), ("Jet", [("Cutoff", 0.35)]), ("Grit", [("Dist Mix", 0.4)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("LFO 1", "WT Pos A", 0.35), ("LFO 2", "Cutoff", 0.25)], tags=["Metallic", "Movement"],
  voice_mode="Mono", oscA_table="Metal Comb", oscA_pos=0.4, lfo1_rate=0.4, lfo1_shape="Triangle", lfo2_rate=0.9,
  flt_type="Notch", flt_cutoff=1500.0, flt_res=0.3, amp_release=0.15, dist_drive=0.4, dist_mix=0.3, dly_time="1/8",
  dly_mix=0.1)
P("analog", "Smooth Mono Synth Lead", "Lead", "Round vintage mono lead with portamento and pressure vibrato.",
  M(("Tone", [("Cutoff", 0.35)]), ("Res", [("Resonance", 0.25)]), ("Vibrato", [("Pitch", 0.01)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Aftertouch", "Pitch", 0.01), ("Velocity", "Cutoff", 0.2)], tags=["Vintage", "Solo"],
  voice_mode="Legato", glide=0.1, oscA_table="Analog Square", oscA_pos=0.3, oscB_table="Analog Saw", oscB_level=0.45,
  oscB_fine=5.0, flt_type="Ladder", flt_cutoff=1800.0, flt_res=0.3, flt_envamt=0.3, fenv_decay=0.4, fenv_sustain=0.4,
  amp_release=0.25, rev_mix=0.12)
P("industrial", "Fold Growl Lead", "Lead", "Wavefolded lead that growls as the fold depth wobbles.",
  M(("Fold", [("WT Pos A", 0.4)]), ("Growl", [("Dist Drive", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("LFO 1", "WT Pos A", 0.3)], tags=["Distorted", "Wobble"],
  voice_mode="Mono", glide=0.03, oscA_table="Fold", oscA_pos=0.4, lfo1_sync=True, lfo1_div="1/8", lfo1_shape="Triangle",
  flt_type="LP24", flt_cutoff=3500.0, amp_release=0.15, dist_type="Soft", dist_drive=0.5, dist_mix=0.6)
P("discohouse", "Stepped Vocoder Lead", "Lead", "Talking lead with stepped vowels that change with the sixteenths.",
  M(("Vowel", [("Formant", 0.4)]), ("Steps", [("WT Pos A", 0.4)]), ("Echo", [("Delay Mix", 0.3)]), ("Grit", [("Dist Mix", 0.4)])),
  mods=[("LFO 1", "Formant", 0.4)], tags=["Vocal", "Rhythmic"],
  voice_mode="Mono", glide=0.03, oscA_table="Vowels", oscA_pos=0.4, oscB_table="Analog Saw", oscB_level=0.35,
  flt_type="Formant", flt_cutoff=1000.0, flt_res=0.45, lfo1_shape="S&H", lfo1_sync=True, lfo1_div="1/16",
  amp_release=0.15, dly_time="1/8", dly_mix=0.1)
P("rawhouse", "Filter Sweep Lead", "Lead", "Raw saw lead whose resonant filter opens over a whole bar.",
  M(("Sweep", [("Cutoff", 0.35)]), ("Res", [("Resonance", 0.25)]), ("Grit", [("Dist Mix", 0.4)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("LFO 1", "Cutoff", 0.35)], tags=["Filter", "Movement"],
  voice_mode="Mono", oscA_table="Analog Saw", oscB_table="Analog Saw", oscB_level=0.4, oscB_fine=-10.0, flt_type="LP24",
  flt_cutoff=1000.0, flt_res=0.5, lfo1_shape="Saw", lfo1_sync=True, lfo1_div="1/1", amp_release=0.15, dist_drive=0.35,
  dist_mix=0.3)
P("epic", "Choir Solo Lead", "Lead", "Solo choir voice lead with expressive vibrato for dramatic toplines.",
  M(("Vowel", [("WT Pos A", 0.4)]), ("Vibrato", [("Pitch", 0.01)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Pitch", 0.005), ("Mod Wheel", "WT Pos A", 0.4)], tags=["Choir", "Dramatic"],
  voice_mode="Legato", glide=0.06, oscA_table="Choir", oscA_pos=0.6, oscA_voices=2, uni_detune=0.12, lfo1_rate=5.2,
  flt_type="LP24", flt_cutoff=5000.0, amp_attack=0.04, amp_release=0.5, rev_size=0.8, rev_mix=0.25)

# =====================================================================================================
# BASS (10)
# =====================================================================================================
P("industrial", "Distorted Reese", "Bass", "Dark detuned reese bass torn by tube distortion.",
  M(("Detune", [("Pitch B", 0.004)]), ("Tone", [("Cutoff", 0.35)]), ("Heat", [("Dist Drive", 0.35)]), ("Sub", [("Sub Level", 0.3)])),
  mods=[("LFO 1", "Cutoff", 0.12)], tags=["Reese", "Distorted"],
  voice_mode="Mono", oscA_table="Analog Saw", oscA_oct=-1, oscA_voices=2, uni_detune=0.55, oscB_table="Analog Saw",
  oscB_oct=-1, oscB_level=0.4, oscB_fine=-14.0, sub_level=0.3, flt_type="LP24", flt_cutoff=900.0, lfo1_rate=0.25,
  amp_release=0.15, dist_type="Tube", dist_drive=0.5, dist_mix=0.7)
P("industrial", "Formant Growl Bass", "Bass", "Buzz bass that growls 'yah-yow' through moving vowels.",
  M(("Vowel", [("Formant", 0.4)]), ("Growl", [("Dist Drive", 0.35)]), ("Buzz", [("WT Pos A", 0.4)]), ("Sub", [("Sub Level", 0.3)])),
  mods=[("LFO 1", "Formant", 0.45)], tags=["Growl", "Distorted"],
  voice_mode="Mono", oscA_table="Buzz", oscA_pos=0.4, oscA_oct=-1, sub_level=0.35, flt_type="Formant", flt_cutoff=900.0,
  flt_res=0.45, lfo1_sync=True, lfo1_div="1/8", lfo1_shape="Triangle", amp_release=0.12, dist_type="Soft",
  dist_drive=0.55, dist_mix=0.7)
P("cold", "Audible 808 Glide", "Bass", "Long gliding 808 with added harmonics so it stays audible on small speakers.",
  M(("Grit", [("Dist Drive", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Harm", [("WT Pos A", 0.4)]), ("Sub", [("Sub Level", 0.3)])),
  tags=["808", "Glide"],
  voice_mode="Legato", glide=0.2, oscA_table="Sine Drive", oscA_pos=0.65, oscA_oct=-1, oscA_level=0.9, penv_amount=7.0,
  penv_decay=0.05, flt_type="LP24", flt_cutoff=2500.0, amp_decay=2.6, amp_sustain=0.55, amp_release=0.8,
  dist_type="Tube", dist_drive=0.45, dist_mix=0.6)
P("analog", "Funk Slap Bass", "Bass", "Snappy slap bass with a pitch pop and percussive ladder.",
  M(("Pop", [("Pitch A", 0.02)]), ("Snap", [("Cutoff", 0.35)]), ("Thump", [("Sub Level", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Velocity", "Cutoff", 0.3)], tags=["Funk", "Slap"],
  voice_mode="Mono", oscA_table="Analog Square", oscA_pos=0.2, oscA_oct=-1, oscB_table="Analog Saw", oscB_level=0.3,
  penv_amount=12.0, penv_decay=0.015, sub_level=0.2, flt_type="Ladder", flt_cutoff=500.0, flt_res=0.3, flt_envamt=0.45,
  fenv_decay=0.12, fenv_sustain=0.1, amp_decay=0.6, amp_sustain=0.4, amp_release=0.06)
P("discohouse", "Octave Pump Bass", "Bass", "Bass that jumps octaves in eighths and pumps with the kick.",
  M(("Tone", [("Cutoff", 0.35)]), ("Grit", [("Dist Mix", 0.2)]), ("Res", [("Resonance", 0.25)]), ("Sub", [("Sub Level", 0.3)])),
  tags=["Octave", "Pump"],
  arp_on=True, arp_mode="Up", arp_rate="1/8", arp_octaves=2, arp_gate=0.6, voice_mode="Mono", oscA_table="Analog Saw",
  oscA_oct=-1, sub_level=0.25, flt_type="LP24", flt_cutoff=1000.0, flt_res=0.25, flt_envamt=0.25, fenv_decay=0.15,
  fenv_sustain=0.2, amp_release=0.06, pump_amount=0.45)
P("rawhouse", "Rubber Square Line", "Bass", "Bouncy resonant square bassline with gentle slide.",
  M(("Squelch", [("Resonance", 0.15)]), ("Open", [("Cutoff", 0.35)]), ("Drive", [("Filter Drive", 0.35)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.2)], tags=["Acid", "Bouncy"],
  voice_mode="Legato", glide=0.04, oscA_table="Analog Square", oscA_pos=0.1, oscA_oct=-1, oscB_table="Analog Saw",
  oscB_oct=-1, oscB_level=0.3, flt_type="Ladder", flt_cutoff=380.0, flt_res=0.6, flt_envamt=0.4, fenv_decay=0.18,
  fenv_sustain=0.1, amp_release=0.08)
P("cinematic", "Grid FM Pulse", "Bass", "Pulsing FM bass ticking in tight sixteenths.",
  M(("Index", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Drive", [("Filter Drive", 0.35)]), ("Hall", [("Reverb Mix", 0.2)])),
  mods=[("Filter Env", "WT Pos A", 0.2)], tags=["Pulse", "FM"],
  arp_on=True, arp_rate="1/16", arp_gate=0.35, voice_mode="Mono", oscA_table="FM Bass", oscA_pos=0.35, oscA_oct=-1,
  sub_level=0.3, flt_type="LP24", flt_cutoff=1400.0, fenv_decay=0.1, fenv_sustain=0.0, amp_decay=0.12, amp_sustain=0.3,
  amp_release=0.05)
P("analog", "Round Analog Bass", "Bass", "Warm round analog bass with a soft ladder pluck.",
  M(("Tone", [("Cutoff", 0.35)]), ("Res", [("Resonance", 0.25)]), ("Drive", [("Filter Drive", 0.35)]), ("Sub", [("Sub Level", 0.3)])),
  mods=[("Velocity", "Cutoff", 0.2)], tags=["Analog", "Warm"],
  voice_mode="Mono", oscA_table="Analog Saw", oscA_oct=-1, oscB_table="Analog Square", oscB_oct=-2, oscB_level=0.4,
  flt_type="Ladder", flt_cutoff=420.0, flt_res=0.2, flt_envamt=0.3, fenv_decay=0.3, fenv_sustain=0.3, amp_release=0.1)
P("industrial", "Bitcrush Sub", "Bass", "Sub bass broken into crunchy bits for lo-fi aggression.",
  M(("Bits", [("Dist Drive", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Harm", [("WT Pos A", 0.4)]), ("Mix", [("Dist Mix", 0.3)])),
  tags=["Lo-Fi", "808"],
  voice_mode="Legato", glide=0.05, oscA_table="Sine Drive", oscA_pos=0.4, oscA_oct=-1, oscA_level=0.9, flt_type="LP24",
  flt_cutoff=3000.0, amp_decay=1.5, amp_sustain=0.5, amp_release=0.3, dist_type="Bitcrush", dist_drive=0.35, dist_mix=0.55)
P("stadium", "Stadium Saw Bass", "Bass", "Wide stacked saw bass that pumps under big chords.",
  M(("Bright", [("Cutoff", 0.35)]), ("Width", [("Mod FX Mix", 0.4)]), ("Grit", [("Dist Mix", 0.2)]), ("Sub", [("Sub Level", 0.3)])),
  tags=["Supersaw", "Pump"],
  voice_mode="Mono", oscA_table="Hyper Saw", oscA_pos=0.3, oscA_oct=-1, oscA_voices=3, uni_detune=0.25, sub_level=0.4,
  flt_type="LP24", flt_cutoff=1100.0, flt_envamt=0.2, fenv_decay=0.25, fenv_sustain=0.4, amp_release=0.12,
  pump_amount=0.4)

# =====================================================================================================
# PADS (8) – every pad is built around a different kind of motion
# =====================================================================================================
P("cinematic", "Wavetable Drift Pad", "Pad", "Pad whose formant peak drifts slowly through the spectrum.",
  M(("Drift", [("WT Pos A", 0.4)]), ("Phase", [("Mod FX Mix", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "WT Pos A", 0.4)], tags=["Movement", "Cinematic"],
  oscA_table="Formant Sweep", oscA_pos=0.3, oscA_voices=3, uni_detune=0.25, lfo1_shape="Triangle", lfo1_sync=True,
  lfo1_div="2/1", flt_type="LP24", flt_cutoff=5000.0, amp_attack=0.5, amp_release=1.5, mfx_type="Phaser",
  mfx_rate=0.12, mfx_depth=0.7, mfx_mix=0.4, rev_size=0.8, rev_mix=0.25)
P("discohouse", "Pulse Pump Pad", "Pad", "Pulse-width pad that breathes in quarter notes like a sidechained synth.",
  M(("PWM", [("WT Pos A", 0.4)]), ("Grit", [("Dist Mix", 0.2)]), ("Tone", [("Cutoff", 0.35)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "WT Pos A", 0.3)], tags=["Pump", "Movement"],
  oscA_table="PWM", oscA_pos=0.4, oscA_voices=3, uni_detune=0.25, lfo1_rate=0.35, lfo1_shape="Triangle",
  flt_type="LP24", flt_cutoff=3000.0, amp_attack=0.08, amp_release=0.8, pump_amount=0.8, pump_rate="1/4", rev_mix=0.18)
P("cold", "Shimmer Grain Pad", "Pad", "Glittering pad with its timbre jumping randomly in sixteenths under a big hall.",
  M(("Grain", [("WT Pos A", 0.4)]), ("Air", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "WT Pos A", 0.35)], tags=["Texture", "Shimmer"],
  oscA_table="Bell Metal", oscA_pos=0.3, oscA_oct=1, oscB_table="Hollow", oscB_level=0.4, lfo1_shape="S&H",
  lfo1_sync=True, lfo1_div="1/16", flt_type="LP12", flt_cutoff=6000.0, amp_attack=0.6, amp_release=1.8,
  dly_mode="PingPong", dly_time="1/8D", dly_mix=0.2, rev_size=0.9, rev_mix=0.32)
P("rawhouse", "Notch Phaser Pad", "Pad", "Saw pad carved by a sweeping notch filter for a hollow jet motion.",
  M(("Sweep", [("Cutoff", 0.35)]), ("Width", [("Mod FX Mix", 0.4)]), ("Res", [("Resonance", 0.25)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Cutoff", 0.4)], tags=["Movement", "Filter"],
  oscA_table="Analog Saw", oscA_voices=3, uni_detune=0.3, flt_type="Notch", flt_cutoff=1200.0, flt_res=0.35,
  lfo1_sync=True, lfo1_div="1/1", lfo1_shape="Triangle", amp_attack=0.3, amp_release=1.2, mfx_mix=0.3, rev_mix=0.2)
P("gospel", "Choir Vowel Pad", "Pad", "Choir pad that slowly sings through vowels like a congregation.",
  M(("Vowel", [("Formant", 0.4)]), ("Choir", [("WT Pos A", 0.4)]), ("Width", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Formant", 0.4)], tags=["Choir", "Movement"],
  oscA_table="Choir", oscA_pos=0.5, oscA_voices=5, uni_detune=0.3, flt_type="Formant", flt_cutoff=1000.0, flt_res=0.3,
  flt_vowel=0.5, lfo1_rate=0.08, amp_attack=0.7, amp_release=2.0, mfx_mix=0.3, rev_size=0.85, rev_mix=0.3)
P("stadium", "Arp Shimmer Pad", "Pad", "Held chords turn into a fast random shimmer of notes across three octaves.",
  M(("Sparkle", [("Cutoff", 0.35)]), ("Width", [("Mod FX Mix", 0.4)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  tags=["Arp", "Shimmer"],
  arp_on=True, arp_mode="Random", arp_rate="1/16", arp_octaves=3, arp_gate=0.9, oscA_table="Hyper Saw", oscA_pos=0.2,
  oscA_voices=3, uni_detune=0.25, flt_type="LP24", flt_cutoff=4000.0, amp_attack=0.02, amp_release=1.2,
  dly_mode="PingPong", dly_time="1/8D", dly_mix=0.2, rev_size=0.85, rev_mix=0.3)
P("epic", "Bell String Pad", "Pad", "Strings that bloom out of a bell attack for haunting chords.",
  M(("Bell", [("Level B", 0.3)]), ("Bow", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Pitch", 0.002)], tags=["Strings", "Bell"],
  oscA_table="Strings", oscA_pos=0.4, oscA_voices=3, uni_detune=0.25, oscB_table="Bell Metal", oscB_pos=0.2,
  oscB_level=0.45, lfo1_rate=4.5, flt_type="LP24", flt_cutoff=3500.0, amp_attack=0.02, amp_decay=1.5, amp_sustain=0.6,
  amp_release=1.4, rev_size=0.8, rev_mix=0.25)
P("analog", "Vinyl Warm Pad", "Pad", "Dusty warm pad with tape drift, a little grit and noise.",
  M(("Drift", [("Pitch", 0.006)]), ("Dust", [("Noise Level", 0.2)]), ("Bits", [("Dist Mix", 0.4)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("LFO 1", "Pitch", 0.004)], tags=["Lo-Fi", "Warm"],
  oscA_table="Analog Saw", oscA_pos=0.5, oscA_voices=2, uni_detune=0.2, noise_level=0.04, lfo1_rate=0.5,
  flt_type="LP12", flt_cutoff=1800.0, amp_attack=0.25, amp_release=1.0, dist_type="Bitcrush", dist_drive=0.1,
  dist_tone=0.4, dist_mix=0.35, rev_mix=0.18)

# =====================================================================================================
# ARP (7)
# =====================================================================================================
P("cinematic", "Plucked Sequence", "Arp", "Up-down FM pluck sequence with dotted echoes.",
  M(("Index", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Filter Env", "WT Pos A", 0.25)], tags=["Sequence", "Cinematic"],
  arp_on=True, arp_mode="UpDown", arp_rate="1/16", arp_octaves=2, arp_gate=0.5, oscA_table="FM Bass", oscA_pos=0.4,
  flt_type="LP24", flt_cutoff=3000.0, fenv_decay=0.12, fenv_sustain=0.0, amp_decay=0.25, amp_sustain=0.0,
  amp_release=0.15, dly_mode="PingPong", dly_time="1/8D", dly_mix=0.18, rev_mix=0.15)
P("discohouse", "Triplet Bell Arp", "Arp", "Sparkling bell arpeggio in sixteenth-note triplets over three octaves.",
  M(("Bell", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  tags=["Bell", "Triplet"],
  arp_on=True, arp_mode="Up", arp_rate="1/16T", arp_octaves=3, arp_gate=0.4, oscA_table="FM Bell", oscA_pos=0.3,
  flt_type="LP12", flt_cutoff=8000.0, amp_decay=0.4, amp_sustain=0.0, amp_release=0.3, dly_mode="PingPong",
  dly_time="1/8", dly_mix=0.15, rev_mix=0.18)
P("mechanical", "Gated Guitar Arp", "Arp", "Distorted guitar notes picked in tight eighths across two octaves.",
  M(("Gain", [("Dist Drive", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Filter Env", "Cutoff", 0.15)], tags=["Guitar", "Rock"],
  arp_on=True, arp_mode="Up", arp_rate="1/8", arp_octaves=2, arp_gate=0.55, oscA_table="Analog Saw",
  oscB_table="Analog Square", oscB_level=0.35, flt_type="LP24", flt_cutoff=2400.0, fenv_decay=0.15, fenv_sustain=0.2,
  amp_decay=0.3, amp_sustain=0.4, amp_release=0.08, dist_type="Tube", dist_drive=0.55, dist_mix=0.85)
P("gospel", "Organ Arp", "Arp", "Drawbar organ rolling in up-down eighths like a gospel run.",
  M(("Drawbars", [("WT Pos A", 0.4)]), ("Rotor", [("Mod FX Mix", 0.4)]), ("Drive", [("Dist Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])),
  tags=["Organ", "Gospel"],
  arp_on=True, arp_mode="UpDown", arp_rate="1/8T", arp_octaves=2, arp_gate=0.8, oscA_table="Drawbars", oscA_pos=0.5,
  oscA_oct=1, flt_type="LP12", flt_cutoff=7000.0, amp_release=0.08, mfx_type="Chorus", mfx_rate=0.8, mfx_mix=0.3,
  dist_type="Tube", dist_drive=0.3, dist_mix=0.3, rev_mix=0.18)
P("cold", "Vowel Step Arp", "Arp", "Random arpeggio whose vowel changes with every note.",
  M(("Vowel", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "WT Pos A", 0.4)], tags=["Vocal", "Random"],
  arp_on=True, arp_mode="Random", arp_rate="1/16", arp_octaves=2, arp_gate=0.6, oscA_table="Vowels", oscA_pos=0.4,
  lfo1_shape="S&H", lfo1_sync=True, lfo1_div="1/16", flt_type="LP24", flt_cutoff=5000.0, amp_release=0.15,
  dly_mode="PingPong", dly_time="1/8D", dly_mix=0.15, rev_mix=0.18)
P("industrial", "Industrial Pump Arp", "Arp", "Crushed metallic arpeggio pumping hard against the kick.",
  M(("Crush", [("Dist Drive", 0.35)]), ("Metal", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)])),
  tags=["Pump", "Distorted"],
  arp_on=True, arp_mode="Up", arp_rate="1/16", arp_octaves=2, arp_gate=0.5, oscA_table="Crush", oscA_pos=0.4,
  oscB_table="Metal Comb", oscB_level=0.3, flt_type="LP24", flt_cutoff=3000.0, amp_decay=0.2, amp_sustain=0.3,
  amp_release=0.06, pump_amount=0.6, dist_type="Bitcrush", dist_drive=0.35, dist_mix=0.5)
P("discohouse", "Disco Octave Arp", "Arp", "Phased saw arpeggio bouncing octaves for disco breakdowns.",
  M(("Phase", [("Mod FX Mix", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Res", [("Resonance", 0.25)]), ("Echo", [("Delay Mix", 0.3)])),
  mods=[("Filter Env", "Cutoff", 0.15)], tags=["Disco", "Octave"],
  arp_on=True, arp_mode="Up", arp_rate="1/16", arp_octaves=2, arp_gate=0.5, oscA_table="Analog Saw", flt_type="LP24",
  flt_cutoff=1800.0, flt_res=0.35, fenv_decay=0.12, fenv_sustain=0.1, amp_release=0.06, mfx_type="Phaser",
  mfx_rate=0.3, mfx_mix=0.4, pump_amount=0.3)

# =====================================================================================================
# BRASS (5)
# =====================================================================================================
P("stadium", "Horn Section Stab", "Brass", "Punchy horn-section stab for victory hits.",
  M(("Blare", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Width", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Filter Env", "WT Pos A", 0.3), ("Velocity", "Cutoff", 0.15)], tags=["Brass", "Stab"],
  oscA_table="Brass", oscA_pos=0.6, oscA_voices=4, uni_detune=0.25, flt_type="LP24", flt_cutoff=2000.0, flt_envamt=0.35,
  fenv_attack=0.01, fenv_decay=0.3, fenv_sustain=0.2, amp_attack=0.008, amp_decay=0.5, amp_sustain=0.3,
  amp_release=0.25, rev_mix=0.18)
P("epic", "Soft French Horn", "Brass", "Mellow distant horn with a slow, warm swell.",
  M(("Swell", [("Cutoff", 0.35)]), ("Warm", [("WT Pos A", 0.4)]), ("Width", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("LFO 1", "Pitch", 0.002)], tags=["Brass", "Soft"],
  oscA_table="Brass", oscA_pos=0.25, oscA_voices=2, uni_detune=0.15, oscB_table="Hollow", oscB_level=0.3,
  lfo1_rate=4.8, flt_type="LP24", flt_cutoff=1100.0, flt_envamt=0.2, fenv_attack=0.2, fenv_decay=1.0, fenv_sustain=0.6,
  amp_attack=0.15, amp_release=0.6, rev_size=0.8, rev_mix=0.25)
P("industrial", "Distorted Fanfare", "Brass", "Brass fanfare smashed through hard clipping and squash.",
  M(("Clip", [("Dist Drive", 0.35)]), ("Blare", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Hall", [("Reverb Mix", 0.3)])),
  mods=[("Filter Env", "WT Pos A", 0.25)], tags=["Brass", "Distorted"],
  oscA_table="Brass", oscA_pos=0.7, oscA_voices=3, uni_detune=0.3, oscB_table="FM Brass", oscB_pos=0.6, oscB_level=0.35,
  flt_type="LP24", flt_cutoff=2500.0, fenv_decay=0.4, fenv_sustain=0.4, amp_attack=0.01, amp_release=0.25,
  dist_type="Hard", dist_drive=0.55, dist_mix=0.8, squash=0.4)
P("analog", "Synth Trumpet Lead", "Brass", "Expressive mono trumpet with breathy attack and pressure vibrato.",
  M(("Brass", [("WT Pos A", 0.4)]), ("Tone", [("Cutoff", 0.35)]), ("Vibrato", [("Pitch", 0.01)]), ("Room", [("Reverb Mix", 0.25)])),
  mods=[("Aftertouch", "Pitch", 0.01), ("Velocity", "Cutoff", 0.2)], tags=["Brass", "Solo"],
  voice_mode="Legato", glide=0.05, oscA_table="Brass", oscA_pos=0.65, noise_level=0.03, flt_type="LP24",
  flt_cutoff=1600.0, flt_envamt=0.3, fenv_attack=0.03, fenv_decay=0.4, fenv_sustain=0.5, amp_attack=0.03,
  amp_release=0.2, rev_mix=0.14)
P("gospel", "Brass Choir Swell", "Brass", "Brass and choir swelling together into a huge gospel chord.",
  M(("Choir", [("Level B", 0.3)]), ("Swell", [("Cutoff", 0.35)]), ("Width", [("Mod FX Mix", 0.4)]), ("Hall", [("Reverb Mix", 0.3)])),
  tags=["Brass", "Choir"],
  oscA_table="Brass", oscA_pos=0.45, oscA_voices=3, uni_detune=0.25, oscB_table="Choir", oscB_pos=0.6, oscB_level=0.45,
  flt_type="LP24", flt_cutoff=900.0, flt_envamt=0.4, fenv_attack=0.8, fenv_decay=1.5, fenv_sustain=0.7, amp_attack=0.4,
  amp_release=1.0, rev_size=0.85, rev_mix=0.28)

# =====================================================================================================
# FX (5)
# =====================================================================================================
P("stadium", "Noise Riser", "FX", "White-noise riser that opens up over two seconds for build-ups.",
  M(("Rise", [("Cutoff", 0.35)]), ("Tone", [("Resonance", 0.25)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  tags=["Riser", "Build-up"],
  oscA_level=0.0, noise_level=0.9, flt_type="BP", flt_cutoff=300.0, flt_res=0.4, flt_envamt=0.8, fenv_attack=2.0,
  fenv_decay=1.0, fenv_sustain=1.0, amp_attack=1.0, amp_release=0.8, rev_size=0.7, rev_mix=0.25)
P("cinematic", "Laser Zap", "FX", "Classic laser zap diving four octaves in a split second.",
  M(("Zap", [("Pitch A", 0.05)]), ("Tone", [("Cutoff", 0.35)]), ("Echo", [("Delay Mix", 0.3)]), ("Hall", [("Reverb Mix", 0.3)])),
  tags=["Zap", "Sci-Fi"],
  oscA_table="Sine Drive", oscA_pos=0.6, oscA_oct=1, penv_amount=-48.0, penv_decay=0.25, amp_decay=0.5, amp_sustain=0.0,
  amp_release=0.3, dly_mode="PingPong", dly_time="1/8", dly_feedback=0.4, dly_mix=0.2)
P("industrial", "Tape Stop Drop", "FX", "Distorted note that slows to a halt like a stopping tape machine.",
  M(("Stop", [("Pitch", -0.2)]), ("Grit", [("Dist Drive", 0.35)]), ("Tone", [("Cutoff", 0.35)]), ("Room", [("Reverb Mix", 0.25)])),
  tags=["Transition", "Distorted"],
  oscA_table="Analog Saw", oscB_table="Analog Square", oscB_level=0.4, penv_amount=-36.0, penv_decay=1.2,
  flt_type="LP24", flt_cutoff=3000.0, flt_envamt=-0.3, fenv_decay=1.0, fenv_sustain=0.0, amp_decay=1.5, amp_sustain=0.0,
  amp_release=0.3, dist_type="Tube", dist_drive=0.5, dist_mix=0.7)
P("discohouse", "Filter Downsweep", "FX", "Pumping noise-and-saw sweep that closes down for drops.",
  M(("Sweep", [("Cutoff", 0.35)]), ("Grit", [("Dist Mix", 0.2)]), ("Res", [("Resonance", 0.25)]), ("Hall", [("Reverb Mix", 0.3)])),
  tags=["Transition", "Pump"],
  oscA_table="Hyper Saw", oscA_voices=3, uni_detune=0.3, oscA_level=0.5, noise_level=0.4, flt_type="LP24",
  flt_cutoff=200.0, flt_res=0.4, flt_envamt=0.75, fenv_attack=0.01, fenv_decay=2.0, fenv_sustain=0.0, amp_release=0.5,
  pump_amount=0.5, rev_mix=0.2)
P("epic", "Cinematic Boom", "FX", "Deep sub boom with a noise crack and a long dark tail.",
  M(("Boom", [("Sub Level", 0.3)]), ("Crack", [("Noise Level", 0.3)]), ("Tone", [("Cutoff", 0.35)]), ("Hall", [("Reverb Mix", 0.3)])),
  tags=["Impact", "Cinematic"],
  oscA_table="Sine Drive", oscA_pos=0.5, oscA_oct=-1, oscA_level=0.9, noise_level=0.25, penv_amount=24.0,
  penv_decay=0.15, flt_type="LP24", flt_cutoff=1500.0, amp_decay=1.8, amp_sustain=0.0, amp_release=0.5,
  dist_type="Tube", dist_drive=0.4, dist_mix=0.5, rev_size=0.85, rev_damping=0.7, rev_mix=0.3)


# =====================================================================================================
CANDIDATES = gp.PRESETS[START:]


def banned_words(array="kBannedInNames"):
    """Reads a banned-word list from tests/PresetTests.cpp, so the generators and the unit test share one source."""
    src = open(os.path.join(gp.ROOT, "tests", "PresetTests.cpp")).read()
    block = src[src.index(array + "[]"):src.index("};", src.index(array + "[]"))]
    return re.findall(r'"([^"]+)"', block)


def contains_word(hay, word):
    norm = lambda s: " " + re.sub(r"[-_.,!?()']", " ", s.lower()) + " "
    return norm(word) in norm(hay)


def main():
    trims = {}
    if os.path.exists(TRIM_FILE):
        trims = json.load(open(TRIM_FILE))
    if len(sys.argv) > 2 and sys.argv[1] == "--trim":
        report = json.load(open(sys.argv[2]))
        for r in report["presets"]:
            trims[r["name"]] = round(max(-24.0, min(12.0, trims.get(r["name"], 0.0) + TARGET_LUFS - r["loudness_lufs"])), 1)
        json.dump(dict(sorted(trims.items())), open(TRIM_FILE, "w"), indent=1)

    names = [p["name"] for p in CANDIDATES]
    old = {p["name"].lower() for p in gp.PRESETS[:START]}
    assert len(CANDIDATES) == 100, len(CANDIDATES)
    assert len(set(names)) == 100, "duplicate candidate names"
    clash = [n for n in names if n.lower() in old]
    assert not clash, clash
    bad = [(n, w) for n in names for w in banned_words() if contains_word(n, w)]
    assert not bad, bad
    bad = [(p["name"], w) for p in gp.PRESETS for w in banned_words("kBannedEverywhere")
           if contains_word(" | ".join([p["name"], p["description"]] + p["tags"] + p["macros"]), w)]
    assert not bad, bad
    for p in CANDIDATES:
        d = p["description"]
        assert d.endswith(".") and ". " not in d[:-1], p["name"]

    os.makedirs(OUT_DIR, exist_ok=True)
    for f in os.listdir(OUT_DIR):
        if f.endswith(".json"):
            os.remove(os.path.join(OUT_DIR, f))
    for i, p in enumerate(CANDIDATES, start=1):
        params = dict(p["params"])
        if abs(trims.get(p["name"], 0.0)) > 0.05:
            params["out_gain"] = trims[p["name"]]
        sparse = {k: (round(params[k], 5) if isinstance(params[k], float) else params[k])
                  for k in gp.DEFAULTS if k in params and params[k] != gp.DEFAULTS[k]}
        doc = {"name": p["name"], "category": p["category"], "tags": p["tags"], "description": p["description"],
               "macros": p["macros"], "version": 1, "params": sparse}
        with open(os.path.join(OUT_DIR, f"{i:03d}_{gp.slug(p['name'])}.json"), "w") as f:
            json.dump(doc, f, indent=2)
            f.write("\n")
    cats = {}
    for p in CANDIDATES:
        cats[p["category"]] = cats.get(p["category"], 0) + 1
    print("wrote", len(CANDIDATES), "candidates:", cats)


if __name__ == "__main__":
    main()
