#pragma once

#include "DspUtil.h"
#include "../Params.h"

#include <juce_dsp/juce_dsp.h>
#include <vector>

namespace volt
{
// Values for one chunk (already smoothed and modulated by the engine).
struct FxParams
{
    int distType = 0;
    float distDrive = 0.3f, distTone = 0.7f, distMix = 0.0f;
    int mfxType = 0;
    float mfxRate = 0.4f, mfxDepth = 0.5f, mfxMix = 0.0f;
    float pumpAmount = 0.0f;
    double pumpBeats = 1.0;
    int dlyMode = 0;
    double dlyBeats = 1.0;
    float dlyFeedback = 0.35f, dlyMix = 0.0f;
    float revSize = 0.5f, revDamp = 0.5f, revMix = 0.0f;
    float squash = 0.0f;
    float outGainDb = 0.0f;
    double ppq = 0.0;   // beat position at the first sample of the chunk
    double bpm = 120.0;
};

// Linear per-sample ramp between chunk values.
struct Ramp
{
    float cur = 0.0f;
    bool init = false;
    inline void set (float target, int n, float& start, float& step) noexcept
    {
        if (! init) { cur = target; init = true; }
        start = cur;
        step = (target - cur) / (float) std::max (1, n);
        cur = target;
    }
};

class Distortion
{
public:
    void prepare (double sr, int maxBlock);
    void reset();
    void process (float* L, float* R, int n, int type, float drive, float tone, float mix) noexcept;

private:
    std::unique_ptr<juce::dsp::Oversampling<float>> os;
    std::vector<float> dryL, dryR;
    OnePoleLP toneL, toneR;
    DcBlocker dcL, dcR;
    Ramp mixRamp, driveRamp;
    double sampleRate = 44100.0;
    float crushHoldL = 0.0f, crushHoldR = 0.0f, crushCount = 0.0f;
    bool active = false;
};

class ModFx
{
public:
    void prepare (double sr);
    void reset();
    void process (float* L, float* R, int n, int type, float rate, float depth, float mix) noexcept;

private:
    float readDelay (const std::vector<float>& buf, float delaySamples) const noexcept;
    std::vector<float> bufL, bufR;
    int writePos = 0, mask = 0;
    double phase = 0.0;
    double sampleRate = 44100.0;
    float fbL = 0.0f, fbR = 0.0f;
    float apL[6] {}, apR[6] {};
    Ramp mixRamp;
    int lastType = -1;
    bool active = false;
};

class Pump
{
public:
    void process (float* L, float* R, int n, float amount, double ppq, double beatsPerSample, double cycleBeats) noexcept;

private:
    Ramp amountRamp;
};

class StereoDelay
{
public:
    void prepare (double sr);
    void reset();
    void process (float* L, float* R, int n, int mode, double delaySamples, float feedback, float mix) noexcept;

private:
    std::vector<float> bufL, bufR;
    int writePos = 0, size = 0;
    double sampleRate = 44100.0;
    float curDelay = -1.0f;
    OnePoleLP lpL, lpR;
    DcBlocker hpL, hpR;
    Ramp mixRamp;
    bool active = false;
};

class ReverbFx
{
public:
    void prepare (double sr);
    void reset();
    void process (float* L, float* R, int n, float size, float damp, float mix) noexcept;

private:
    juce::Reverb reverb;
    std::vector<float> wetL, wetR;
    float lastSize = -1.0f, lastDamp = -1.0f;
    Ramp mixRamp;
    bool active = false;
};

// 3-band downward compressor driven by a single Amount control.
class SquashCompressor
{
public:
    void prepare (double sr);
    void reset();
    void process (float* L, float* R, int n, float amount) noexcept;

private:
    juce::dsp::LinkwitzRileyFilter<float> lp1, hp1, lp2, hp2, ap2;
    float env[3] {};
    float atk[3] {}, rel[3] {};
    Ramp amountRamp;
    double sampleRate = 44100.0;
    bool active = false;
};

// Output gain followed by a zero-latency protective peak limiter (ceiling -0.5 dBFS).
class OutputStage
{
public:
    void prepare (double sr);
    void reset();
    void process (float* L, float* R, int n, float gainDb) noexcept;
    float getMaxReductionDb() const noexcept { return maxReductionDb; }
    void resetMaxReduction() noexcept { maxReductionDb = 0.0f; }

private:
    float envelope = 0.0f, releaseK = 0.999f;
    Ramp gainRamp;
    float maxReductionDb = 0.0f;
};

class FxChain
{
public:
    void prepare (double sr, int maxBlock);
    void reset();
    void process (float* L, float* R, int n, const FxParams& p) noexcept;
    float getLimiterReductionDb() const noexcept { return output.getMaxReductionDb(); }
    void resetLimiterMeter() noexcept { output.resetMaxReduction(); }

private:
    double sampleRate = 44100.0;
    Distortion dist;
    ModFx modFx;
    Pump pump;
    StereoDelay delay;
    ReverbFx reverb;
    SquashCompressor squash;
    OutputStage output;
};
} // namespace volt
