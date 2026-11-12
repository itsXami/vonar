#pragma once

#include "DspUtil.h"
#include "Modulators.h"
#include "VoiceFilter.h"
#include "Wavetables.h"
#include "../Params.h"

#include <array>
#include <vector>

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
    float bendSemis = 0.0f;               // pitch wheel x bend range, smoothed per chunk
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

// Karplus-Strong string: a delay line excited by one cycle of the oscillator's wavetable, with a damping
// low-pass and a decay gain in the loop. One per unison voice.
struct PluckString
{
    std::vector<float> buf;
    int write = 0;
    float lp = 0.0f;
    bool excited = false;

    void prepare (int maxLen) { buf.assign ((size_t) maxLen, 0.0f); reset(); }
    void reset() noexcept { std::fill (buf.begin(), buf.end(), 0.0f); write = 0; lp = 0.0f; excited = false; }
};

class Voice
{
public:
    void prepare (double sampleRate, uint32_t seed);
    void reset();

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
    float lastFenv = 0.0f, lastMenv = 0.0f, lastLfo[2] {}, randomValue = 0.0f;

private:
    struct OscState
    {
        std::array<float, kMaxUnison> phase {}, inc {}, gl {}, gr {};
        float pos = 0.0f, warp = 0.0f;
        int voices = 0;
        bool init = false;
        std::array<PluckString, kMaxUnison> strings;
    };

    void computeOsc (int o, const VoiceContext& ctx, float pitch, float level, float pan, float detune,
                     std::array<float, kMaxUnison>& newInc, std::array<float, kMaxUnison>& newGl,
                     std::array<float, kMaxUnison>& newGr, int& voicesOut) noexcept;
    void exciteStrings (int o, const VoiceContext& ctx) noexcept;
    template <int Mode>
    void wavetableLoop (const Wavetable& wt, int mip, int n, int nv, float fromPos, float dPos, float dWarp, const float* modBuf,
                        const std::array<float, kMaxUnison>& ni, const std::array<float, kMaxUnison>& ngl,
                        const std::array<float, kMaxUnison>& ngr, OscState& st) noexcept;
    void renderWavetable (int o, const VoiceContext& ctx, int n, float pos, float warpAmt, const std::array<float, kMaxUnison>& ni,
                          const std::array<float, kMaxUnison>& ngl, const std::array<float, kMaxUnison>& ngr) noexcept;
    void renderString (int o, const VoiceContext& ctx, int n, const std::array<float, kMaxUnison>& ni,
                       const std::array<float, kMaxUnison>& ngl, const std::array<float, kMaxUnison>& ngr) noexcept;

    double sr = 44100.0;
    XorShift rng, randomRng;
    Adsr amp, fenv, menv;
    float penv = 0.0f;
    Lfo lfo[2];
    VoiceFilter filter;
    OscState osc[2];
    // Chunk-start snapshot of each oscillator's first unison voice (modulator for FM / RM warps).
    float modPhase[2] {}, modInc[2] {}, modPos[2] {};
    int modMip[2] {};
    float subPhase = 0.0f, subInc = 0.0f, subLevel = 0.0f, noiseLevel = 0.0f;
    bool gate = false;
    bool pendingExcite = false;
    float targetPitch = 60.0f;
    bool levelsInit = false;
    int maxStringLen = 0;

    float bufL[kChunk] {}, bufR[kChunk] {};
};
} // namespace volt
