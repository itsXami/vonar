#pragma once

#include "DspUtil.h"
#include "../Params.h"

namespace volt
{
// Analog-style ADSR: linear attack, exponential decay/release (times are to -40 dB).
// Retriggering starts the attack from the current level, so voice reuse never clicks.
class Adsr
{
public:
    enum Stage { Idle, Attack, Decay, Release };

    void setSampleRate (double sr) noexcept { sampleRate = sr; }

    void setParams (float attack, float decay, float sustain, float release) noexcept
    {
        attackInc = 1.0f / (std::max (attack, 1.0e-4f) * (float) sampleRate);
        decayK = decayCoef (decay, sampleRate);
        releaseK = decayCoef (release, sampleRate);
        sustainLevel = clampf (sustain, 0.0f, 1.0f);
    }

    void noteOn() noexcept { stage = Attack; }
    void noteOff() noexcept { if (stage != Idle) stage = Release; }
    void reset() noexcept { stage = Idle; level = 0.0f; }

    inline float next() noexcept
    {
        switch (stage)
        {
            case Attack:
                level += attackInc;
                if (level >= 1.0f) { level = 1.0f; stage = Decay; }
                break;
            case Decay:
                level = sustainLevel + (level - sustainLevel) * decayK;
                break;
            case Release:
                level *= releaseK;
                if (level < 1.0e-5f) { level = 0.0f; stage = Idle; }
                break;
            case Idle:
            default:
                break;
        }
        return level;
    }

    float advance (int n) noexcept
    {
        for (int i = 0; i < n; ++i)
            next();
        return level;
    }

    bool isActive() const noexcept { return stage != Idle; }
    bool isReleasing() const noexcept { return stage == Release; }
    float getLevel() const noexcept { return level; }
    Stage getStage() const noexcept { return stage; }

private:
    double sampleRate = 44100.0;
    Stage stage = Idle;
    float level = 0.0f, attackInc = 0.01f, decayK = 0.999f, releaseK = 0.999f, sustainLevel = 1.0f;
};

// Bipolar LFO, phase in cycles.
class Lfo
{
public:
    void reset (double startPhase, uint32_t seed) noexcept
    {
        phase = startPhase - std::floor (startPhase);
        rng = XorShift (seed);
        sh = rng.nextBipolar();
    }

    void setPhase (double p) noexcept
    {
        const double np = p - std::floor (p);
        if (np < phase - 0.5) // wrapped forward
            sh = rng.nextBipolar();
        phase = np;
    }

    float advance (double incPerSample, int n) noexcept
    {
        phase += incPerSample * n;
        if (phase >= 1.0)
        {
            phase -= std::floor (phase);
            sh = rng.nextBipolar();
        }
        return value();
    }

    void setShape (int s) noexcept { shape = s; }

    float value() const noexcept
    {
        const float p = (float) phase;
        switch (shape)
        {
            case choices::Sine:     return std::sin (kTwoPiF * p);
            case choices::Triangle: return p < 0.25f ? 4.0f * p : (p < 0.75f ? 2.0f - 4.0f * p : 4.0f * p - 4.0f);
            case choices::Saw:      return 2.0f * p - 1.0f;
            case choices::Square:   return p < 0.5f ? 1.0f : -1.0f;
            case choices::SampleHold:
            default:                return sh;
        }
    }

    double getPhase() const noexcept { return phase; }
    float getHeld() const noexcept { return sh; }
    void copyFrom (const Lfo& o) noexcept { phase = o.phase; sh = o.sh; shape = o.shape; }

private:
    double phase = 0.0;
    float sh = 0.0f;
    int shape = 0;
    XorShift rng;
};
} // namespace volt
