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
    bool distKeepLow = false;   // distort only above ~160 Hz, the sub passes clean
    float choRate = 0.4f, choDepth = 0.5f, choMix = 0.0f;
    float phaRate = 0.3f, phaDepth = 0.6f, phaMix = 0.0f;
    float flaRate = 0.2f, flaDepth = 0.5f, flaMix = 0.0f;
    int fxfType = 0;
    float fxfCutoff = 2000.0f, fxfRes = 0.2f, fxfMix = 0.0f;
    float eqLowFreq = 120.0f, eqLowGain = 0.0f, eqMidFreq = 1000.0f, eqMidGain = 0.0f, eqMidQ = 1.0f,
          eqHighFreq = 6000.0f, eqHighGain = 0.0f;
    bool eqOn = false;
    float revLowCut = 20.0f, revHighCut = 20000.0f;
    float compThreshold = 0.0f, compRatio = 1.0f, compAttack = 0.01f, compRelease = 0.15f, compGain = 0.0f;
    bool compOn = false;
    fx::Order order = fx::defaultOrder();
    // Effects that are switched off get their mix / amount forced to zero by the engine, so they fade out
    // smoothly and cost nothing once silent.
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
    void process (float* L, float* R, int n, int type, float drive, float tone, float mix, bool keepLow = false) noexcept;

private:
    std::unique_ptr<juce::dsp::Oversampling<float>> os;
    std::vector<float> dryL, dryR, lowL, lowR;
    juce::dsp::LinkwitzRileyFilter<float> split;    // 24 dB/oct crossover for "keep low": low + high = all-pass
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

// State-variable filter (12 dB/oct, TPT) as an effect: low-pass, high-pass, band-pass or notch, with dry/wet mix.
class FilterFx
{
public:
    void prepare (double sr);
    void reset();
    void process (float* L, float* R, int n, int type, float cutoff, float res, float mix) noexcept;

private:
    float ic1[2] {}, ic2[2] {};
    Ramp mixRamp;
    float smoothCut = -1.0f;
    double sampleRate = 44100.0;
    bool active = false;
};

// Three-band EQ: low shelf, peak (with Q), high shelf. Bands at 0 dB are skipped.
struct Biquad
{
    float b0 = 1, b1 = 0, b2 = 0, a1 = 0, a2 = 0;
    float z1[2] {}, z2[2] {};
    inline float process (float x, int c) noexcept
    {
        const float y = b0 * x + z1[c];
        z1[c] = b1 * x - a1 * y + z2[c];
        z2[c] = b2 * x - a2 * y;
        return y;
    }
    void reset() { z1[0] = z1[1] = z2[0] = z2[1] = 0.0f; }
    void setLowShelf (double sr, double f, double gainDb);
    void setHighShelf (double sr, double f, double gainDb);
    void setPeak (double sr, double f, double gainDb, double q);
    void setHighPass (double sr, double f);
    void setLowPass (double sr, double f);
};

class EqFx
{
public:
    void prepare (double sr);
    void reset();
    void process (float* L, float* R, int n, const FxParams& p) noexcept;
    // Magnitude response in dB of the three bands at frequency f (used by the interface curve).
    static float responseDb (const FxParams& p, double sampleRate, float f);

private:
    Biquad band[3];
    float last[7] { -1, -1, -1, -1, -1, -1, -1 };
    bool bandOn[3] {};
    double sampleRate = 44100.0;
};

// Feed-forward compressor with a soft knee; ratio 1:1 and 0 dB gain = bypass.
class CompStage
{
public:
    void prepare (double sr);
    void reset();
    void process (float* L, float* R, int n, float thresholdDb, float ratio, float attack, float release, float gainDb) noexcept;

private:
    float envDb = 0.0f;
    Ramp gainRamp;
    double sampleRate = 44100.0;
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
    void process (float* L, float* R, int n, float size, float damp, float mix, float lowCut = 20.0f,
                  float highCut = 20000.0f) noexcept;

private:
    juce::Reverb reverb;
    Biquad lowCutF, highCutF;     // tone of the reverb tail (wet only); bypassed at 20 Hz / 20 kHz
    float lastLow = -1.0f, lastHigh = -1.0f;
    double sampleRate = 44100.0;
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
    void resetMaxReduction() noexcept { maxReductionDb = 0.0f; nonFinite = 0; }
    int getNonFiniteCount() const noexcept { return nonFinite; }

private:
    float envelope = 0.0f, releaseK = 0.999f;
    Ramp gainRamp;
    float maxReductionDb = 0.0f;
    int nonFinite = 0;
};

class FxChain
{
public:
    void prepare (double sr, int maxBlock);
    void reset();
    void process (float* L, float* R, int n, const FxParams& p) noexcept;
    float getLimiterReductionDb() const noexcept { return output.getMaxReductionDb(); }
    int getNonFiniteCount() const noexcept { return output.getNonFiniteCount(); }
    void resetLimiterMeter() noexcept { output.resetMaxReduction(); }

private:
    double sampleRate = 44100.0;
    Distortion dist;
    ModFx chorus, phaser, flanger;
    FilterFx filter;
    EqFx eq;
    Pump pump;
    StereoDelay delay;
    ReverbFx reverb;
    SquashCompressor squash;
    CompStage comp;
    OutputStage output;
};
} // namespace volt
