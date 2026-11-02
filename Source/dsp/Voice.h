#pragma once

#include "DspUtil.h"
#include "Modulators.h"
#include "VoiceFilter.h"
#include "Wavetables.h"
#include "../Params.h"

#include <array>

namespace volt
{
constexpr int kMaxVoices = 16;
constexpr int kMaxUnison = 8;
constexpr int kChunk = 32; // control-rate sub-block

struct ModSlot
{
    int src = 0, dst = 0;
    float amt = 0.0f;
};

// Everything a voice needs for one chunk; filled by the engine (no allocation, plain data).
struct VoiceContext
{
    double sampleRate = 44100.0;
    const ParamSnapshot* raw = nullptr;   // un-smoothed values (choices, ints, bools, times)
    const float* smooth = nullptr;        // smoothed float values indexed by P
    float cutoffPitch = 0.0f;             // smoothed base cutoff as MIDI pitch
    const Wavetable* table[2] {};
    float modWheel = 0.0f, aftertouch = 0.0f;
    float macros[kNumMacros] {};
    double lfoInc[2] {};                  // cycles per sample
    bool lfoRetrig[2] {};
    float lfoGlobal[2] {};                // free-running LFO values (already scaled by depth)
    float lfoDepth[2] {};
    int lfoShape[2] {};
    std::array<ModSlot, kNumModSlots> slots {};
    int numSlots = 0;
    float glideAlpha = 1.0f;              // per-chunk glide smoothing coefficient
};

class Voice
{
public:
    void prepare (double sampleRate, uint32_t seed);
    void reset();

    // retrigger: (re)start the envelopes. resetOsc: voice was idle, start oscillator phases fresh.
    void start (int note, float velocity, float startPitch, bool retrigger, const VoiceContext& ctx);
    void glideTo (int newNote) noexcept { note = newNote; targetPitch = (float) newNote; }
    void release() noexcept;
    void kill() noexcept { reset(); }

    // Renders one chunk (n <= kChunk) and adds into outL/outR.
    void render (const VoiceContext& ctx, float* outL, float* outR, int n) noexcept;

    bool isActive() const noexcept { return amp.isActive(); }
    bool isGateOn() const noexcept { return gate; }
    bool isReleasing() const noexcept { return amp.isReleasing(); }
    float getAmpLevel() const noexcept { return amp.getLevel(); }

    int note = -1;
    float velocity = 0.0f;
    float polyPressure = 0.0f;
    uint64_t age = 0;
    float currentPitch = 60.0f;

    // Last per-voice modulation source values (used for global FX targets).
    float lastFenv = 0.0f, lastLfo[2] {};

private:
    struct OscState
    {
        std::array<float, kMaxUnison> phase {}, inc {}, gl {}, gr {};
        float pos = 0.0f;
        int voices = 0;
        bool init = false;
    };

    void computeOsc (int o, const VoiceContext& ctx, float pitch, float pos, float level, float pan, OscState& st,
                     std::array<float, kMaxUnison>& newInc, std::array<float, kMaxUnison>& newGl,
                     std::array<float, kMaxUnison>& newGr, int& voicesOut) noexcept;

    double sr = 44100.0;
    XorShift rng;
    Adsr amp, fenv;
    float penv = 0.0f;
    Lfo lfo[2];
    VoiceFilter filter;
    OscState osc[2];
    float subPhase = 0.0f, subInc = 0.0f, subLevel = 0.0f, noiseLevel = 0.0f;
    bool gate = false;
    float targetPitch = 60.0f;
    bool levelsInit = false;

    float bufL[kChunk] {}, bufR[kChunk] {};
};
} // namespace volt
