#include "Params.h"
#include "dsp/Wavetables.h"

namespace volt
{
namespace choices
{
const juce::StringArray& tempoDivisions()
{
    static const juce::StringArray d { "4/1", "2/1", "1/1", "1/2D", "1/2", "1/2T", "1/4D", "1/4", "1/4T",
                                       "1/8D", "1/8", "1/8T", "1/16D", "1/16", "1/16T", "1/32" };
    return d;
}

const juce::StringArray& arpRates()
{
    static const juce::StringArray d { "1/4", "1/8", "1/8T", "1/16", "1/16T", "1/32" };
    return d;
}

const juce::StringArray& delayTimes()
{
    static const juce::StringArray d { "1/32", "1/16T", "1/16", "1/16D", "1/8T", "1/8", "1/8D", "1/4T", "1/4",
                                       "1/4D", "1/2", "1/1" };
    return d;
}

const juce::StringArray& pumpRates()
{
    static const juce::StringArray d { "1/2", "1/4", "1/8", "1/16" };
    return d;
}

double divisionToBeats (const juce::String& name)
{
    auto s = name.trim();
    double mult = 1.0;
    if (s.endsWithChar ('D')) { mult = 1.5; s = s.dropLastCharacters (1); }
    else if (s.endsWithChar ('T')) { mult = 2.0 / 3.0; s = s.dropLastCharacters (1); }
    const auto num = s.upToFirstOccurrenceOf ("/", false, false).getDoubleValue();
    const auto den = s.fromFirstOccurrenceOf ("/", false, false).getDoubleValue();
    if (num <= 0.0 || den <= 0.0)
        return 1.0;
    return 4.0 * num / den * mult;
}
} // namespace choices

namespace
{
const juce::StringArray modSourceNames { "None", "LFO 1", "LFO 2", "Filter Env", "Velocity", "Mod Wheel",
                                         "Aftertouch", "Key Track", "Macro 1", "Macro 2", "Macro 3", "Macro 4",
                                         "Mod Env", "Random" };

const juce::StringArray modDestNames { "None", "WT Pos A", "WT Pos B", "Pitch", "Pitch A", "Pitch B", "Cutoff",
                                       "Resonance", "Filter Drive", "Formant", "Level A", "Level B", "Sub Level",
                                       "Noise Level", "Pan A", "Pan B", "Dist Drive", "Dist Mix", "Mod FX Mix",
                                       "Delay Mix", "Reverb Mix", "Warp A", "Warp B", "Detune" };

ParamSpec F (const juce::String& id, const juce::String& name, float mn, float mx, float def, float centre = 0.0f, const char* unit = "")
{
    return { id, name, ParamType::Float, mn, mx, def, centre, unit, {} };
}
ParamSpec I (const juce::String& id, const juce::String& name, int mn, int mx, int def, const char* unit = "")
{
    return { id, name, ParamType::Int, (float) mn, (float) mx, (float) def, 0.0f, unit, {} };
}
ParamSpec B (const juce::String& id, const juce::String& name, bool def)
{
    return { id, name, ParamType::Bool, 0.0f, 1.0f, def ? 1.0f : 0.0f, 0.0f, "", {} };
}
ParamSpec C (const juce::String& id, const juce::String& name, const juce::StringArray& items, int def)
{
    return { id, name, ParamType::Choice, 0.0f, (float) (items.size() - 1), (float) def, 0.0f, "", items };
}

std::array<ParamSpec, NumParams> buildSpecs()
{
    std::array<ParamSpec, NumParams> s;
    auto set = [&s] (int p, ParamSpec spec) { s[(size_t) p] = std::move (spec); };

    const auto& tables = wavetableNames();
    const auto& divs = choices::tempoDivisions();

    set (VoiceMode, C ("voice_mode", "Voice Mode", { "Poly", "Mono", "Legato" }, 0));
    set (Glide, F ("glide", "Glide", 0.0f, 2.0f, 0.0f, 0.25f, "s"));

    struct OscIds { const char* table; const char* pos; const char* oct; const char* semi; const char* fine;
                    const char* level; const char* pan; const char* voices; const char* type; const char* warp;
                    const char* warpAmt; const char* label; };
    const OscIds oscs[2] = {
        { "oscA_table", "oscA_pos", "oscA_oct", "oscA_semi", "oscA_fine", "oscA_level", "oscA_pan", "oscA_voices",
          "oscA_type", "oscA_warp", "oscA_warp_amt", "Osc A" },
        { "oscB_table", "oscB_pos", "oscB_oct", "oscB_semi", "oscB_fine", "oscB_level", "oscB_pan", "oscB_voices",
          "oscB_type", "oscB_warp", "oscB_warp_amt", "Osc B" } };

    for (int o = 0; o < 2; ++o)
    {
        const int base = OscA_Table + o * kOscParamCount;
        const juce::String l (oscs[o].label);
        set (base + 0, C (oscs[o].table, l + " Wavetable", tables, o == 0 ? wavetableIndex ("Analog Saw") : wavetableIndex ("Basic Shapes")));
        set (base + 1, F (oscs[o].pos, l + " WT Position", 0.0f, 1.0f, 0.0f));
        set (base + 2, I (oscs[o].oct, l + " Octave", -3, 3, 0));
        set (base + 3, I (oscs[o].semi, l + " Semitones", -12, 12, 0, "st"));
        set (base + 4, F (oscs[o].fine, l + " Fine", -100.0f, 100.0f, 0.0f, 0.0f, "ct"));
        set (base + 5, F (oscs[o].level, l + " Level", 0.0f, 1.0f, o == 0 ? 0.8f : 0.0f));
        set (base + 6, F (oscs[o].pan, l + " Pan", -1.0f, 1.0f, 0.0f));
        set (base + 7, I (oscs[o].voices, l + " Unison", 1, 8, 1));
        set (base + 8, C (oscs[o].type, l + " Type", { "Wavetable", "String" }, 0));
        set (base + 9, C (oscs[o].warp, l + " Warp", { "Off", "Sync", "Bend", "Squeeze", "Mirror", "Quantize", "FM", "RM" }, 0));
        set (base + 10, F (oscs[o].warpAmt, l + " Warp Amount", 0.0f, 1.0f, 0.0f));
    }

    set (StrDecay, F ("str_decay", "String Decay", 0.05f, 10.0f, 1.5f, 1.0f, "s"));
    set (StrTone, F ("str_tone", "String Tone", 0.0f, 1.0f, 0.6f));

    set (UniDetune, F ("uni_detune", "Unison Detune", 0.0f, 1.0f, 0.25f));
    set (UniSpread, F ("uni_spread", "Unison Spread", 0.0f, 1.0f, 0.5f));
    set (SubShape, C ("sub_shape", "Sub Shape", { "Sine", "Triangle" }, 0));
    set (SubLevel, F ("sub_level", "Sub Level", 0.0f, 1.0f, 0.0f));
    set (NoiseLevel, F ("noise_level", "Noise Level", 0.0f, 1.0f, 0.0f));

    set (FltType, C ("flt_type", "Filter Type", { "LP12", "LP24", "HP", "BP", "Notch", "Ladder", "Formant", "Comb+", "Comb-" }, 1));
    set (FltCutoff, F ("flt_cutoff", "Cutoff", 20.0f, 20000.0f, 20000.0f, 1000.0f, "Hz"));
    set (FltRes, F ("flt_res", "Resonance", 0.0f, 1.0f, 0.1f));
    set (FltDrive, F ("flt_drive", "Filter Drive", 0.0f, 1.0f, 0.0f));
    set (FltKeyTrack, F ("flt_keytrack", "Key Track", 0.0f, 1.0f, 0.0f));
    set (FltEnvAmt, F ("flt_envamt", "Filter Env Amount", -1.0f, 1.0f, 0.0f));
    set (FltVowel, F ("flt_vowel", "Formant Vowel", 0.0f, 1.0f, 0.0f));

    set (AmpA, F ("amp_attack", "Amp Attack", 0.0005f, 10.0f, 0.002f, 0.4f, "s"));
    set (AmpD, F ("amp_decay", "Amp Decay", 0.002f, 10.0f, 0.3f, 0.6f, "s"));
    set (AmpS, F ("amp_sustain", "Amp Sustain", 0.0f, 1.0f, 1.0f));
    set (AmpR, F ("amp_release", "Amp Release", 0.002f, 12.0f, 0.15f, 0.8f, "s"));
    set (FenvA, F ("fenv_attack", "Filter Env Attack", 0.0005f, 10.0f, 0.002f, 0.4f, "s"));
    set (FenvD, F ("fenv_decay", "Filter Env Decay", 0.002f, 10.0f, 0.4f, 0.6f, "s"));
    set (FenvS, F ("fenv_sustain", "Filter Env Sustain", 0.0f, 1.0f, 0.5f));
    set (FenvR, F ("fenv_release", "Filter Env Release", 0.002f, 12.0f, 0.3f, 0.8f, "s"));
    set (PenvAmt, F ("penv_amount", "Pitch Env Amount", -48.0f, 48.0f, 0.0f, 0.0f, "st"));
    set (PenvDecay, F ("penv_decay", "Pitch Env Decay", 0.005f, 3.0f, 0.12f, 0.25f, "s"));
    set (MenvA, F ("menv_attack", "Mod Env Attack", 0.0005f, 10.0f, 0.002f, 0.4f, "s"));
    set (MenvD, F ("menv_decay", "Mod Env Decay", 0.002f, 10.0f, 0.5f, 0.6f, "s"));
    set (MenvS, F ("menv_sustain", "Mod Env Sustain", 0.0f, 1.0f, 0.0f));
    set (MenvR, F ("menv_release", "Mod Env Release", 0.002f, 12.0f, 0.3f, 0.8f, "s"));

    const char* lfoIds[2][6] = { { "lfo1_shape", "lfo1_sync", "lfo1_rate", "lfo1_div", "lfo1_depth", "lfo1_retrig" },
                                 { "lfo2_shape", "lfo2_sync", "lfo2_rate", "lfo2_div", "lfo2_depth", "lfo2_retrig" } };
    const char* lfoNames[2][6] = { { "LFO 1 Shape", "LFO 1 Sync", "LFO 1 Rate", "LFO 1 Division", "LFO 1 Depth", "LFO 1 Retrigger" },
                                   { "LFO 2 Shape", "LFO 2 Sync", "LFO 2 Rate", "LFO 2 Division", "LFO 2 Depth", "LFO 2 Retrigger" } };
    for (int l = 0; l < 2; ++l)
    {
        const int base = Lfo1_Shape + l * kLfoParamCount;
        set (base + 0, C (lfoIds[l][0], lfoNames[l][0], { "Sine", "Triangle", "Saw", "Square", "S&H" }, 0));
        set (base + 1, B (lfoIds[l][1], lfoNames[l][1], false));
        set (base + 2, F (lfoIds[l][2], lfoNames[l][2], 0.01f, 40.0f, 2.0f, 2.0f, "Hz"));
        set (base + 3, C (lfoIds[l][3], lfoNames[l][3], divs, divs.indexOf ("1/4")));
        set (base + 4, F (lfoIds[l][4], lfoNames[l][4], 0.0f, 1.0f, 1.0f));
        set (base + 5, B (lfoIds[l][5], lfoNames[l][5], false));
    }

    for (int m = 0; m < kNumModSlots; ++m)
    {
        const int base = Mod1_Src + m * kModSlotParamCount;
        const juce::String n (m + 1);
        const juce::String src = "mod" + n + "_src", dst = "mod" + n + "_dst", amt = "mod" + n + "_amt";
        set (base + 0, C (src, "Mod " + n + " Source", modSourceNames, 0));
        set (base + 1, C (dst, "Mod " + n + " Target", modDestNames, 0));
        set (base + 2, F (amt, "Mod " + n + " Amount", -1.0f, 1.0f, 0.0f));
    }

    set (Macro1, F ("macro1", "Macro 1", 0.0f, 1.0f, 0.0f));
    set (Macro2, F ("macro2", "Macro 2", 0.0f, 1.0f, 0.0f));
    set (Macro3, F ("macro3", "Macro 3", 0.0f, 1.0f, 0.0f));
    set (Macro4, F ("macro4", "Macro 4", 0.0f, 1.0f, 0.0f));

    set (ArpOn, B ("arp_on", "Arp On", false));
    set (ArpMode, C ("arp_mode", "Arp Mode", { "Up", "Down", "UpDown", "Random" }, 0));
    set (ArpRate, C ("arp_rate", "Arp Rate", choices::arpRates(), choices::arpRates().indexOf ("1/16")));
    set (ArpOct, I ("arp_octaves", "Arp Octaves", 1, 4, 1));
    set (ArpGate, F ("arp_gate", "Arp Gate", 0.05f, 1.0f, 0.5f));

    set (DistType, C ("dist_type", "Distortion Type", { "Soft", "Tube", "Hard", "Fold", "Bitcrush" }, 0));
    set (DistDrive, F ("dist_drive", "Distortion Drive", 0.0f, 1.0f, 0.3f));
    set (DistTone, F ("dist_tone", "Distortion Tone", 0.0f, 1.0f, 0.7f));
    set (DistMix, F ("dist_mix", "Distortion Mix", 0.0f, 1.0f, 0.0f));

    set (MfxType, C ("mfx_type", "Mod FX Type", { "Chorus", "Phaser", "Flanger" }, 0));
    set (MfxRate, F ("mfx_rate", "Mod FX Rate", 0.02f, 10.0f, 0.4f, 1.0f, "Hz"));
    set (MfxDepth, F ("mfx_depth", "Mod FX Depth", 0.0f, 1.0f, 0.5f));
    set (MfxMix, F ("mfx_mix", "Mod FX Mix", 0.0f, 1.0f, 0.0f));

    set (PumpAmount, F ("pump_amount", "Pump Amount", 0.0f, 1.0f, 0.0f));
    set (PumpRate, C ("pump_rate", "Pump Rate", choices::pumpRates(), 1));

    set (DlyMode, C ("dly_mode", "Delay Mode", { "Stereo", "PingPong" }, 0));
    set (DlyTime, C ("dly_time", "Delay Time", choices::delayTimes(), choices::delayTimes().indexOf ("1/4")));
    set (DlyFeedback, F ("dly_feedback", "Delay Feedback", 0.0f, 0.95f, 0.35f));
    set (DlyMix, F ("dly_mix", "Delay Mix", 0.0f, 1.0f, 0.0f));

    set (RevSize, F ("rev_size", "Reverb Size", 0.0f, 1.0f, 0.5f));
    set (RevDamp, F ("rev_damping", "Reverb Damping", 0.0f, 1.0f, 0.5f));
    set (RevMix, F ("rev_mix", "Reverb Mix", 0.0f, 1.0f, 0.0f));

    set (Squash, F ("squash", "Squash", 0.0f, 1.0f, 0.0f));
    set (OutGain, F ("out_gain", "Output Gain", -24.0f, 12.0f, 0.0f, 0.0f, "dB"));
    set (BendRange, I ("bend_range", "Pitch Bend Range", 0, 24, 2, "st"));

    for ([[maybe_unused]] auto& p : s)
        jassert (p.id.isNotEmpty());
    return s;
}
} // namespace

const std::array<ParamSpec, NumParams>& paramSpecs()
{
    static const auto specs = buildSpecs();
    return specs;
}

static juce::String formatValue (const ParamSpec& s, float v)
{
    const juce::String unit (s.unit);
    if (unit == "Hz")
        return v >= 1000.0f ? juce::String (v / 1000.0f, 2) + " kHz" : juce::String (v, v < 10.0f ? 2 : 0) + " Hz";
    if (unit == "s")
        return v < 1.0f ? juce::String (juce::roundToInt (v * 1000.0f)) + " ms" : juce::String (v, 2) + " s";
    if (unit == "dB")
        return juce::String (v, 1) + " dB";
    if (unit == "st")
        return juce::String (v, 1) + " st";
    if (unit == "ct")
        return juce::String (juce::roundToInt (v)) + " ct";
    if (s.minValue < 0.0f)
        return juce::String (juce::roundToInt (v * 100.0f)) + "%";
    return juce::String (juce::roundToInt (v * 100.0f)) + "%";
}

juce::AudioProcessorValueTreeState::ParameterLayout createParameterLayout()
{
    juce::AudioProcessorValueTreeState::ParameterLayout layout;
    for (const auto& s : paramSpecs())
    {
        const juce::ParameterID pid { s.id, 1 };
        switch (s.type)
        {
            case ParamType::Float:
            {
                juce::NormalisableRange<float> range (s.minValue, s.maxValue);
                if (s.skewCentre > 0.0f)
                    range.setSkewForCentre (s.skewCentre);
                const ParamSpec* sp = &s;
                layout.add (std::make_unique<juce::AudioParameterFloat> (
                    pid, s.name, range, s.defaultValue,
                    juce::AudioParameterFloatAttributes()
                        .withStringFromValueFunction ([sp] (float v, int) { return formatValue (*sp, v); })));
                break;
            }
            case ParamType::Int:
                layout.add (std::make_unique<juce::AudioParameterInt> (pid, s.name, (int) s.minValue, (int) s.maxValue,
                                                                       (int) s.defaultValue));
                break;
            case ParamType::Bool:
                layout.add (std::make_unique<juce::AudioParameterBool> (pid, s.name, s.defaultValue >= 0.5f));
                break;
            case ParamType::Choice:
                layout.add (std::make_unique<juce::AudioParameterChoice> (pid, s.name, s.choices, (int) s.defaultValue));
                break;
        }
    }
    return layout;
}

void ParamReader::attach (juce::AudioProcessorValueTreeState& state)
{
    for (int p = 0; p < NumParams; ++p)
    {
        ptrs[(size_t) p] = state.getRawParameterValue (spec (p).id);
        jassert (ptrs[(size_t) p] != nullptr);
    }
}

void ParamReader::read (ParamSnapshot& out) const noexcept
{
    for (size_t p = 0; p < ptrs.size(); ++p)
        out.v[p] = ptrs[p] != nullptr ? ptrs[p]->load (std::memory_order_relaxed) : 0.0f;
}
} // namespace volt
