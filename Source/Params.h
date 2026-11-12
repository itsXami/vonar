#pragma once

#include <juce_audio_processors/juce_audio_processors.h>
#include <array>

namespace volt
{
// Every automatable parameter. The order of this enum is internal only; hosts and presets
// address parameters through the stable string IDs in the spec table (Params.cpp).
enum P : int
{
    VoiceMode, Glide,

    // Oscillator A (block of kOscParamCount), then oscillator B with identical layout.
    OscA_Table, OscA_Pos, OscA_Oct, OscA_Semi, OscA_Fine, OscA_Level, OscA_Pan, OscA_Voices, OscA_Type, OscA_Warp, OscA_WarpAmt,
    OscB_Table, OscB_Pos, OscB_Oct, OscB_Semi, OscB_Fine, OscB_Level, OscB_Pan, OscB_Voices, OscB_Type, OscB_Warp, OscB_WarpAmt,

    StrDecay, StrTone,

    UniDetune, UniSpread,
    SubShape, SubLevel, NoiseLevel,

    FltType, FltCutoff, FltRes, FltDrive, FltKeyTrack, FltEnvAmt, FltVowel,

    AmpA, AmpD, AmpS, AmpR,
    FenvA, FenvD, FenvS, FenvR,
    PenvAmt, PenvDecay,
    MenvA, MenvD, MenvS, MenvR,

    Lfo1_Shape, Lfo1_Sync, Lfo1_Rate, Lfo1_Div, Lfo1_Depth, Lfo1_Retrig,
    Lfo2_Shape, Lfo2_Sync, Lfo2_Rate, Lfo2_Div, Lfo2_Depth, Lfo2_Retrig,

    Mod1_Src, Mod1_Dst, Mod1_Amt,
    Mod2_Src, Mod2_Dst, Mod2_Amt,
    Mod3_Src, Mod3_Dst, Mod3_Amt,
    Mod4_Src, Mod4_Dst, Mod4_Amt,
    Mod5_Src, Mod5_Dst, Mod5_Amt,
    Mod6_Src, Mod6_Dst, Mod6_Amt,
    Mod7_Src, Mod7_Dst, Mod7_Amt,
    Mod8_Src, Mod8_Dst, Mod8_Amt,
    Mod9_Src, Mod9_Dst, Mod9_Amt,
    Mod10_Src, Mod10_Dst, Mod10_Amt,
    Mod11_Src, Mod11_Dst, Mod11_Amt,
    Mod12_Src, Mod12_Dst, Mod12_Amt,

    Macro1, Macro2, Macro3, Macro4,

    ArpOn, ArpMode, ArpRate, ArpOct, ArpGate,

    DistType, DistDrive, DistTone, DistMix,
    MfxType, MfxRate, MfxDepth, MfxMix,
    PumpAmount, PumpRate,
    DlyMode, DlyTime, DlyFeedback, DlyMix,
    RevSize, RevDamp, RevMix,
    Squash,
    OutGain,
    BendRange,

    NumParams
};

constexpr int kOscParamCount = OscB_Table - OscA_Table;
constexpr int kLfoParamCount = Lfo2_Shape - Lfo1_Shape;
constexpr int kModSlotParamCount = 3;
constexpr int kNumModSlots = 12;
constexpr int kNumMacros = 4;

enum class ParamType { Float, Int, Bool, Choice };

struct ParamSpec
{
    juce::String id;
    juce::String name;
    ParamType type;
    float minValue, maxValue, defaultValue;
    float skewCentre;            // <= 0: linear
    const char* unit;
    juce::StringArray choices;   // for Choice
};

const std::array<ParamSpec, NumParams>& paramSpecs();
inline const ParamSpec& spec (int p) { return paramSpecs()[(size_t) p]; }

juce::AudioProcessorValueTreeState::ParameterLayout createParameterLayout();

// Choice lists that the engine interprets by index.
namespace choices
{
    enum VoiceModes { Poly, Mono, Legato };
    enum FilterTypes { LP12, LP24, HP, BP, Notch, Ladder, Formant, CombPlus, CombMinus };
    enum OscTypes { Wavetable, String };
    enum WarpModes { WarpOff, WarpSync, WarpBend, WarpSqueeze, WarpMirror, WarpQuantize, WarpFM, WarpRM };
    enum LfoShapes { Sine, Triangle, Saw, Square, SampleHold };
    enum SubShapes { SubSine, SubTriangle };
    enum ArpModes { Up, Down, UpDown, Random };
    enum DistTypes { Soft, Tube, Hard, Fold, Bitcrush };
    enum ModFxTypes { Chorus, Phaser, Flanger };
    enum DelayModes { Stereo, PingPong };

    enum ModSources { SrcNone, SrcLfo1, SrcLfo2, SrcFilterEnv, SrcVelocity, SrcModWheel, SrcAftertouch,
                      SrcKeyTrack, SrcMacro1, SrcMacro2, SrcMacro3, SrcMacro4, SrcModEnv, SrcRandom, NumModSources };

    enum ModDests { DstNone, DstPosA, DstPosB, DstPitch, DstPitchA, DstPitchB, DstCutoff, DstRes, DstDrive,
                    DstFormant, DstLevelA, DstLevelB, DstSubLevel, DstNoiseLevel, DstPanA, DstPanB,
                    DstDistDrive, DstDistMix, DstModFxMix, DstDelayMix, DstReverbMix, DstWarpA, DstWarpB, DstDetune,
                    NumModDests };

    const juce::StringArray& tempoDivisions();  // LFO sync divisions
    double divisionToBeats (const juce::String& name);
    const juce::StringArray& arpRates();
    const juce::StringArray& delayTimes();
    const juce::StringArray& pumpRates();
}

// Real-time safe snapshot of all parameter values (plain units) for one audio block.
struct ParamSnapshot
{
    std::array<float, NumParams> v {};
    float operator[] (int p) const noexcept { return v[(size_t) p]; }
    int i (int p) const noexcept { return (int) std::lround (v[(size_t) p]); }
    bool b (int p) const noexcept { return v[(size_t) p] >= 0.5f; }
};

// Holds the APVTS raw-value pointers so the audio thread can take a snapshot without locks.
class ParamReader
{
public:
    void attach (juce::AudioProcessorValueTreeState& state);
    void read (ParamSnapshot& out) const noexcept;

private:
    std::array<std::atomic<float>*, NumParams> ptrs {};
};
} // namespace volt
