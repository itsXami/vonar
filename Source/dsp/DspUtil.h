#pragma once

#include <cmath>
#include <cstdint>
#include <algorithm>

namespace volt
{
constexpr float kPiF = 3.14159265358979f;
constexpr float kTwoPiF = 6.28318530717959f;

inline float clampf (float x, float lo, float hi) noexcept { return std::min (hi, std::max (lo, x)); }

// Rational tanh approximation, exact limits at +-1 beyond |x| >= 3.
inline float fastTanh (float x) noexcept
{
    if (x > 3.0f) return 1.0f;
    if (x < -3.0f) return -1.0f;
    const float x2 = x * x;
    return x * (27.0f + x2) / (27.0f + 9.0f * x2);
}

inline float pitchToHz (float midiPitch) noexcept { return 440.0f * std::exp2 ((midiPitch - 69.0f) * (1.0f / 12.0f)); }
inline float hzToPitch (float hz) noexcept { return 69.0f + 12.0f * std::log2 (std::max (hz, 1.0e-3f) / 440.0f); }

// Per-chunk exponential smoothing coefficient for a time constant in seconds.
inline float smoothAlpha (int numSamples, double sampleRate, float tauSeconds) noexcept
{
    if (tauSeconds <= 0.0f) return 1.0f;
    return 1.0f - std::exp (-(float) numSamples / (tauSeconds * (float) sampleRate));
}

// Per-sample multiplier so that a decaying exponential reaches -40 dB after `seconds`.
inline float decayCoef (float seconds, double sampleRate) noexcept
{
    return std::exp (-4.6051702f / (std::max (seconds, 1.0e-4f) * (float) sampleRate));
}

struct XorShift
{
    uint32_t s = 0x9E3779B9u;
    explicit XorShift (uint32_t seed = 0x9E3779B9u) : s (seed == 0 ? 1u : seed) {}
    inline uint32_t nextU() noexcept { s ^= s << 13; s ^= s >> 17; s ^= s << 5; return s; }
    inline float next01() noexcept { return (float) (nextU() >> 8) * (1.0f / 16777216.0f); }
    inline float nextBipolar() noexcept { return next01() * 2.0f - 1.0f; }
};

// Constant-power pan, p in [-1, 1], normalised so that the centre position gives 1.0 on both sides.
inline void panGains (float p, float& l, float& r) noexcept
{
    const float a = (clampf (p, -1.0f, 1.0f) + 1.0f) * (kPiF * 0.25f);
    l = std::cos (a) * 1.41421356f;
    r = std::sin (a) * 1.41421356f;
}

// DC blocking one-pole high-pass (~5-20 Hz).
struct DcBlocker
{
    float x1 = 0.0f, y1 = 0.0f, r = 0.999f;
    void prepare (double sr, float hz = 10.0f) noexcept { r = std::exp (-kTwoPiF * hz / (float) sr); x1 = y1 = 0.0f; }
    inline float process (float x) noexcept { const float y = x - x1 + r * y1; x1 = x; y1 = y; return y; }
    void reset() noexcept { x1 = y1 = 0.0f; }
};

// One-pole low-pass (TPT form).
struct OnePoleLP
{
    float s = 0.0f, g = 0.5f;
    void setCutoff (float hz, double sr) noexcept
    {
        const float wc = std::tan (kPiF * clampf (hz, 5.0f, 0.49f * (float) sr) / (float) sr);
        g = wc / (1.0f + wc);
    }
    inline float process (float x) noexcept { const float v = (x - s) * g; const float y = v + s; s = y + v; return y; }
    void reset() noexcept { s = 0.0f; }
};
} // namespace volt
