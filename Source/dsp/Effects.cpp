#include "Effects.h"
#include <complex>

namespace volt
{
namespace
{
inline float dryWet (float mix, float& wetGain) noexcept
{
    // Dry stays at unity until 50 %, wet reaches unity at 50 % (good for delay / reverb / distortion blends).
    wetGain = std::min (1.0f, 2.0f * mix);
    return std::min (1.0f, 2.0f * (1.0f - mix));
}
} // namespace

// =============================================================================================
void Distortion::prepare (double sr, int maxBlock)
{
    sampleRate = sr;
    os = std::make_unique<juce::dsp::Oversampling<float>> (2, 2, juce::dsp::Oversampling<float>::filterHalfBandPolyphaseIIR, true, false);
    os->initProcessing ((size_t) juce::jmax (maxBlock, 64));
    dryL.assign ((size_t) juce::jmax (maxBlock, 64), 0.0f);
    dryR.assign ((size_t) juce::jmax (maxBlock, 64), 0.0f);
    lowL.assign ((size_t) juce::jmax (maxBlock, 64), 0.0f);
    lowR.assign ((size_t) juce::jmax (maxBlock, 64), 0.0f);
    split.prepare ({ sr, (juce::uint32) juce::jmax (maxBlock, 64), 2 });
    split.setCutoffFrequency (160.0f);
    dcL.prepare (sr, 8.0f);
    dcR.prepare (sr, 8.0f);
    reset();
}

void Distortion::reset()
{
    if (os != nullptr)
        os->reset();
    toneL.reset();
    toneR.reset();
    split.reset();
    dcL.reset();
    dcR.reset();
    crushHoldL = crushHoldR = crushCount = 0.0f;
    mixRamp = {};
    driveRamp = {};
}

void Distortion::process (float* L, float* R, int n, int type, float drive, float tone, float mix, bool keepLow) noexcept
{
    float m0, dm, d0, dd;
    mixRamp.set (mix, n, m0, dm);
    driveRamp.set (drive, n, d0, dd);
    if (m0 < 1.0e-4f && mix < 1.0e-4f)
    {
        active = false;
        return;
    }
    if (! active)
    {
        reset();
        mixRamp.set (mix, n, m0, dm);
        driveRamp.set (drive, n, d0, dd);
        active = true;
    }
    if (n > (int) dryL.size())
        return;

    std::copy (L, L + n, dryL.data());
    std::copy (R, R + n, dryR.data());

    // Keep low: a Linkwitz-Riley crossover at ~160 Hz splits the signal, only the upper band is distorted and the
    // low band is added back clean (low + high sums to an all-pass, so the sub keeps its level and stays pure).
    if (keepLow)
        for (int i = 0; i < n; ++i)
        {
            float lo = 0.0f, hi = 0.0f;
            split.processSample (0, L[i], lo, hi);
            lowL[(size_t) i] = lo;
            dryL[(size_t) i] = lo + hi;   // the dry path gets the same all-pass phase, so a partial mix does not comb
            L[i] = hi;
            split.processSample (1, R[i], lo, hi);
            lowR[(size_t) i] = lo;
            dryR[(size_t) i] = lo + hi;
            R[i] = hi;
        }

    const float cut = 600.0f * std::exp2 (clampf (tone, 0.0f, 1.0f) * 5.0f);
    toneL.setCutoff (cut, sampleRate);
    toneR.setCutoff (cut, sampleRate);

    if (type == choices::Bitcrush)
    {
        float d = d0;
        for (int i = 0; i < n; ++i)
        {
            d += dd;
            const float levels = std::exp2 (12.0f - 10.0f * d); // 12 .. 2 bits
            const float hold = 1.0f + 23.0f * d * d;            // sample-rate reduction
            crushCount += 1.0f;
            if (crushCount >= hold)
            {
                crushCount -= hold;
                const float pre = 1.0f + 3.0f * d;
                crushHoldL = std::round (clampf (L[i] * pre, -1.0f, 1.0f) * levels) / levels;
                crushHoldR = std::round (clampf (R[i] * pre, -1.0f, 1.0f) * levels) / levels;
            }
            L[i] = crushHoldL;
            R[i] = crushHoldR;
        }
    }
    else
    {
        float* chans[2] = { L, R };
        juce::dsp::AudioBlock<float> block (chans, 2, (size_t) n);
        auto up = os->processSamplesUp (block);
        const int un = (int) up.getNumSamples();
        const float gStart = juce::Decibels::decibelsToGain (36.0f * d0);
        const float gEnd = juce::Decibels::decibelsToGain (36.0f * clampf (drive, 0.0f, 1.0f));
        const float cStart = 0.25f / std::tanh (0.25f * gStart), cEnd = 0.25f / std::tanh (0.25f * gEnd);
        const float invUn = 1.0f / (float) std::max (1, un);
        for (int c = 0; c < 2; ++c)
        {
            float* x = up.getChannelPointer ((size_t) c);
            float g = gStart, comp = cStart;
            const float dg = (gEnd - gStart) * invUn, dc = (cEnd - cStart) * invUn;
            for (int i = 0; i < un; ++i)
            {
                g += dg;
                comp += dc;
                const float v = x[i] * g;
                float y;
                switch (type)
                {
                    case choices::Tube: y = fastTanh (v + 0.35f) - 0.33637f; break; // asymmetric -> even harmonics
                    case choices::Hard: y = clampf (v, -1.0f, 1.0f); break;
                    case choices::Fold: y = std::sin (v * 1.5707963f); break;
                    case choices::Soft:
                    default:            y = fastTanh (v); break;
                }
                x[i] = y * comp;
            }
        }
        os->processSamplesDown (block);
    }

    float m = m0;
    for (int i = 0; i < n; ++i)
    {
        m += dm;
        float wl = dcL.process (toneL.process (L[i]));
        float wr = dcR.process (toneR.process (R[i]));
        if (keepLow)
        {
            wl += lowL[(size_t) i];
            wr += lowR[(size_t) i];
        }
        L[i] = dryL[(size_t) i] + m * (wl - dryL[(size_t) i]);
        R[i] = dryR[(size_t) i] + m * (wr - dryR[(size_t) i]);
    }
}

// =============================================================================================
void ModFx::prepare (double sr)
{
    sampleRate = sr;
    int size = 1;
    while (size < (int) (0.06 * sr))
        size <<= 1;
    bufL.assign ((size_t) size, 0.0f);
    bufR.assign ((size_t) size, 0.0f);
    mask = size - 1;
    reset();
}

void ModFx::reset()
{
    std::fill (bufL.begin(), bufL.end(), 0.0f);
    std::fill (bufR.begin(), bufR.end(), 0.0f);
    writePos = 0;
    phase = 0.0; // deterministic start (offline renders do not depend on the previously played sound)
    fbL = fbR = 0.0f;
    for (int i = 0; i < 6; ++i)
        apL[i] = apR[i] = 0.0f;
    mixRamp = {};
}

float ModFx::readDelay (const std::vector<float>& buf, float d) const noexcept
{
    const float rp = (float) writePos - d;
    const int i0 = (int) std::floor (rp);
    const float fr = rp - (float) i0;
    const float a = buf[(size_t) (i0 & mask)];
    const float b = buf[(size_t) ((i0 + 1) & mask)];
    return a + fr * (b - a);
}

void ModFx::process (float* L, float* R, int n, int type, float rate, float depth, float mix) noexcept
{
    float m0, dm;
    mixRamp.set (mix, n, m0, dm);
    if (m0 < 1.0e-4f && mix < 1.0e-4f)
    {
        active = false;
        return;
    }
    if (! active || type != lastType)
    {
        reset();
        mixRamp.set (mix, n, m0, dm);
        active = true;
        lastType = type;
    }

    const double inc = (double) rate / sampleRate;
    const float sr = (float) sampleRate;
    depth = clampf (depth, 0.0f, 1.0f);
    float m = m0;

    for (int i = 0; i < n; ++i)
    {
        m += dm;
        phase += inc;
        if (phase >= 1.0)
            phase -= 1.0;
        const float lfoL = std::sin (kTwoPiF * (float) phase);
        const float lfoR = std::sin (kTwoPiF * (float) phase + 1.5707963f);
        const float inL = L[i], inR = R[i];
        float wetL, wetR;

        if (type == choices::Phaser)
        {
            const float fmin = 180.0f, range = 1.0f + 5.0f * depth;
            const float fL = fmin * std::exp2 (range * (0.5f + 0.5f * lfoL));
            const float fR = fmin * std::exp2 (range * (0.5f + 0.5f * lfoR));
            const float tL = std::tan (kPiF * std::min (fL, 0.45f * sr) / sr);
            const float tR = std::tan (kPiF * std::min (fR, 0.45f * sr) / sr);
            const float aL = (tL - 1.0f) / (tL + 1.0f), aR = (tR - 1.0f) / (tR + 1.0f);
            float xl = inL + 0.55f * fbL, xr = inR + 0.55f * fbR;
            for (int s = 0; s < 6; ++s)
            {
                const float yl = aL * xl + apL[s];
                apL[s] = xl - aL * yl;
                xl = yl;
                const float yr = aR * xr + apR[s];
                apR[s] = xr - aR * yr;
                xr = yr;
            }
            fbL = fastTanh (xl);
            fbR = fastTanh (xr);
            wetL = xl;
            wetR = xr;
            // Phasing needs dry + wet; mix 100 % = deepest notches.
            wetL = 0.5f * (inL + wetL);
            wetR = 0.5f * (inR + wetR);
        }
        else
        {
            const bool flanger = type == choices::Flanger;
            const float base = (flanger ? 0.0012f : 0.011f) * sr;
            const float sweep = (flanger ? 0.0040f : 0.0065f) * sr * depth;
            const float dL = base + sweep * (0.5f + 0.5f * lfoL);
            const float dR = base + sweep * (0.5f + 0.5f * lfoR);
            const float fb = flanger ? 0.55f + 0.3f * depth : 0.0f;
            bufL[(size_t) writePos] = inL + fb * fbL;
            bufR[(size_t) writePos] = inR + fb * fbR;
            wetL = readDelay (bufL, dL);
            wetR = readDelay (bufR, dR);
            fbL = fastTanh (wetL);
            fbR = fastTanh (wetR);
            if (flanger)
            {
                wetL = 0.5f * (inL + wetL);
                wetR = 0.5f * (inR + wetR);
            }
            writePos = (writePos + 1) & mask;
        }

        L[i] = inL + m * (wetL - inL);
        R[i] = inR + m * (wetR - inR);
    }
}

// =============================================================================================
void FilterFx::prepare (double sr)
{
    sampleRate = sr;
    reset();
}

void FilterFx::reset()
{
    ic1[0] = ic1[1] = ic2[0] = ic2[1] = 0.0f;
    smoothCut = -1.0f;
    mixRamp = {};
}

void FilterFx::process (float* L, float* R, int n, int type, float cutoff, float res, float mix) noexcept
{
    float m0, dm;
    mixRamp.set (mix, n, m0, dm);
    if (m0 < 1.0e-4f && mix < 1.0e-4f)
    {
        active = false;
        return;
    }
    if (! active)
    {
        reset();
        mixRamp.set (mix, n, m0, dm);
        active = true;
    }
    const float target = clampf (cutoff, 20.0f, 0.45f * (float) sampleRate);
    const float start = smoothCut < 0.0f ? target : smoothCut;
    smoothCut = target;
    const float k = 2.0f - 1.9f * clampf (res, 0.0f, 1.0f);   // damping: 2 (flat) .. 0.1 (sharp peak)
    float m = m0;
    for (int i = 0; i < n; ++i)
    {
        m += dm;
        const float fc = start + (target - start) * (float) (i + 1) / (float) n;
        const float g = std::tan (kPiF * fc / (float) sampleRate);
        const float a1 = 1.0f / (1.0f + g * (g + k)), a2 = g * a1, a3 = g * a2;
        float* ch[2] = { L, R };
        for (int c = 0; c < 2; ++c)
        {
            const float x = ch[c][i];
            const float v3 = x - ic2[c];
            const float v1 = a1 * ic1[c] + a2 * v3;
            const float v2 = ic2[c] + a2 * ic1[c] + a3 * v3;
            ic1[c] = 2.0f * v1 - ic1[c];
            ic2[c] = 2.0f * v2 - ic2[c];
            float y;
            switch (type)
            {
                case choices::FxHighPass: y = x - k * v1 - v2; break;
                case choices::FxBandPass: y = k * v1; break;
                case choices::FxNotch:    y = x - k * v1; break;
                case choices::FxLowPass:
                default:                  y = v2; break;
            }
            ch[c][i] = x + m * (y - x);
        }
    }
}

// =============================================================================================
// RBJ cookbook biquads.
void Biquad::setLowShelf (double sr, double f, double gainDb)
{
    const double A = std::pow (10.0, gainDb / 40.0), w = juce::MathConstants<double>::twoPi * f / sr;
    const double cs = std::cos (w), sn = std::sin (w), al = sn / 2.0 * std::sqrt (2.0), sa = 2.0 * std::sqrt (A) * al;
    const double a0 = (A + 1) + (A - 1) * cs + sa;
    b0 = (float) (A * ((A + 1) - (A - 1) * cs + sa) / a0);
    b1 = (float) (2 * A * ((A - 1) - (A + 1) * cs) / a0);
    b2 = (float) (A * ((A + 1) - (A - 1) * cs - sa) / a0);
    a1 = (float) (-2 * ((A - 1) + (A + 1) * cs) / a0);
    a2 = (float) (((A + 1) + (A - 1) * cs - sa) / a0);
}

void Biquad::setHighShelf (double sr, double f, double gainDb)
{
    const double A = std::pow (10.0, gainDb / 40.0), w = juce::MathConstants<double>::twoPi * f / sr;
    const double cs = std::cos (w), sn = std::sin (w), al = sn / 2.0 * std::sqrt (2.0), sa = 2.0 * std::sqrt (A) * al;
    const double a0 = (A + 1) - (A - 1) * cs + sa;
    b0 = (float) (A * ((A + 1) + (A - 1) * cs + sa) / a0);
    b1 = (float) (-2 * A * ((A - 1) + (A + 1) * cs) / a0);
    b2 = (float) (A * ((A + 1) + (A - 1) * cs - sa) / a0);
    a1 = (float) (2 * ((A - 1) - (A + 1) * cs) / a0);
    a2 = (float) (((A + 1) - (A - 1) * cs - sa) / a0);
}

void Biquad::setPeak (double sr, double f, double gainDb, double q)
{
    const double A = std::pow (10.0, gainDb / 40.0), w = juce::MathConstants<double>::twoPi * f / sr;
    const double al = std::sin (w) / (2.0 * q), cs = std::cos (w), a0 = 1 + al / A;
    b0 = (float) ((1 + al * A) / a0);
    b1 = (float) (-2 * cs / a0);
    b2 = (float) ((1 - al * A) / a0);
    a1 = (float) (-2 * cs / a0);
    a2 = (float) ((1 - al / A) / a0);
}

void Biquad::setHighPass (double sr, double f)
{
    const double w = juce::MathConstants<double>::twoPi * f / sr, cs = std::cos (w), al = std::sin (w) / (2.0 * 0.7071), a0 = 1 + al;
    b0 = (float) ((1 + cs) / 2 / a0);
    b1 = (float) (-(1 + cs) / a0);
    b2 = b0;
    a1 = (float) (-2 * cs / a0);
    a2 = (float) ((1 - al) / a0);
}

void Biquad::setLowPass (double sr, double f)
{
    const double w = juce::MathConstants<double>::twoPi * f / sr, cs = std::cos (w), al = std::sin (w) / (2.0 * 0.7071), a0 = 1 + al;
    b0 = (float) ((1 - cs) / 2 / a0);
    b1 = (float) ((1 - cs) / a0);
    b2 = b0;
    a1 = (float) (-2 * cs / a0);
    a2 = (float) ((1 - al) / a0);
}

void EqFx::prepare (double sr)
{
    sampleRate = sr;
    reset();
}

void EqFx::reset()
{
    for (auto& b : band)
        b.reset();
    std::fill (last, last + 7, -1.0f);
}

void EqFx::process (float* L, float* R, int n, const FxParams& p) noexcept
{
    if (! p.eqOn)
    {
        reset();
        return;
    }
    const float nyq = 0.45f * (float) sampleRate;
    const float v[7] = { std::min (p.eqLowFreq, nyq), p.eqLowGain, std::min (p.eqMidFreq, nyq), p.eqMidGain, p.eqMidQ,
                         std::min (p.eqHighFreq, nyq), p.eqHighGain };
    bool changed = false;
    for (int i = 0; i < 7; ++i)
        changed |= std::abs (v[i] - last[i]) > 1.0e-4f;
    if (changed)
    {
        band[0].setLowShelf (sampleRate, v[0], v[1]);
        band[1].setPeak (sampleRate, v[2], v[3], std::max (0.1f, v[4]));
        band[2].setHighShelf (sampleRate, v[5], v[6]);
        std::copy (v, v + 7, last);
    }
    bandOn[0] = std::abs (v[1]) > 0.01f;
    bandOn[1] = std::abs (v[3]) > 0.01f;
    bandOn[2] = std::abs (v[6]) > 0.01f;
    for (int b = 0; b < 3; ++b)
    {
        if (! bandOn[b])
        {
            band[b].reset();
            continue;
        }
        for (int i = 0; i < n; ++i)
        {
            L[i] = band[b].process (L[i], 0);
            R[i] = band[b].process (R[i], 1);
        }
    }
}

float EqFx::responseDb (const FxParams& p, double sr, float f)
{
    Biquad b[3];
    b[0].setLowShelf (sr, p.eqLowFreq, p.eqLowGain);
    b[1].setPeak (sr, p.eqMidFreq, p.eqMidGain, std::max (0.1f, p.eqMidQ));
    b[2].setHighShelf (sr, p.eqHighFreq, p.eqHighGain);
    const std::complex<double> z = std::polar (1.0, -juce::MathConstants<double>::twoPi * (double) f / sr);
    double mag = 1.0;
    for (const auto& q : b)
    {
        const auto num = (double) q.b0 + (double) q.b1 * z + (double) q.b2 * z * z;
        const auto den = 1.0 + (double) q.a1 * z + (double) q.a2 * z * z;
        mag *= std::abs (num / den);
    }
    return (float) (20.0 * std::log10 (std::max (mag, 1.0e-6)));
}

// =============================================================================================
void CompStage::prepare (double sr)
{
    sampleRate = sr;
    reset();
}

void CompStage::reset()
{
    envDb = 0.0f;
    gainRamp = {};
}

void CompStage::process (float* L, float* R, int n, float thresholdDb, float ratio, float attack, float release,
                         float gainDb) noexcept
{
    float g0, dg;
    gainRamp.set (juce::Decibels::decibelsToGain (gainDb), n, g0, dg);
    if (ratio <= 1.001f && std::abs (gainDb) < 0.01f && std::abs (g0 - 1.0f) < 1.0e-5f)
    {
        envDb = 0.0f;
        return;
    }
    const float atk = std::exp (-1.0f / (std::max (attack, 1.0e-4f) * (float) sampleRate));
    const float rel = std::exp (-1.0f / (std::max (release, 1.0e-3f) * (float) sampleRate));
    const float slope = 1.0f - 1.0f / std::max (1.0f, ratio), knee = 6.0f;
    float g = g0;
    for (int i = 0; i < n; ++i)
    {
        g += dg;
        const float pk = std::max (std::abs (L[i]), std::abs (R[i]));
        const float inDb = pk > 1.0e-6f ? 20.0f * std::log10 (pk) : -120.0f;
        const float over = inDb - thresholdDb;
        float grDb;   // gain reduction (dB, >= 0), soft knee
        if (over <= -knee * 0.5f) grDb = 0.0f;
        else if (over >= knee * 0.5f) grDb = slope * over;
        else { const float t = over + knee * 0.5f; grDb = slope * t * t / (2.0f * knee); }
        envDb = grDb > envDb ? atk * envDb + (1.0f - atk) * grDb : rel * envDb + (1.0f - rel) * grDb;
        const float gain = g * std::pow (10.0f, -envDb / 20.0f);
        L[i] *= gain;
        R[i] *= gain;
    }
}

// =============================================================================================
void Pump::process (float* L, float* R, int n, float amount, double ppq, double beatsPerSample, double cycleBeats) noexcept
{
    float a0, da;
    amountRamp.set (amount, n, a0, da);
    if (a0 < 1.0e-4f && amount < 1.0e-4f)
        return;
    cycleBeats = std::max (cycleBeats, 1.0e-3);
    float a = a0;
    for (int i = 0; i < n; ++i)
    {
        a += da;
        const double beat = ppq + (double) i * beatsPerSample;
        const float p = (float) (beat / cycleBeats - std::floor (beat / cycleBeats));
        float duck;
        if (p < 0.02f)
            duck = p / 0.02f;
        else
        {
            const float r = std::max (0.0f, 1.0f - (p - 0.02f) / 0.62f);
            duck = r * r * (3.0f - 2.0f * r); // smooth recovery
        }
        const float g = 1.0f - clampf (a, 0.0f, 1.0f) * duck;
        L[i] *= g;
        R[i] *= g;
    }
}

// =============================================================================================
void StereoDelay::prepare (double sr)
{
    sampleRate = sr;
    size = (int) (sr * 4.1) + 8;
    bufL.assign ((size_t) size, 0.0f);
    bufR.assign ((size_t) size, 0.0f);
    lpL.setCutoff (7000.0f, sr);
    lpR.setCutoff (7000.0f, sr);
    hpL.prepare (sr, 120.0f);
    hpR.prepare (sr, 120.0f);
    reset();
}

void StereoDelay::reset()
{
    std::fill (bufL.begin(), bufL.end(), 0.0f);
    std::fill (bufR.begin(), bufR.end(), 0.0f);
    writePos = 0;
    curDelay = -1.0f;
    lpL.reset();
    lpR.reset();
    hpL.reset();
    hpR.reset();
    mixRamp = {};
}

void StereoDelay::process (float* L, float* R, int n, int mode, double delaySamples, float feedback, float mix) noexcept
{
    float m0, dm;
    mixRamp.set (mix, n, m0, dm);
    if (m0 < 1.0e-4f && mix < 1.0e-4f)
    {
        active = false;
        return;
    }
    if (! active)
    {
        reset();
        mixRamp.set (mix, n, m0, dm);
        active = true;
    }

    const float target = (float) juce::jlimit (16.0, (double) size - 8.0, delaySamples);
    if (curDelay < 0.0f)
        curDelay = target;
    const float k = 1.0f - std::exp (-1.0f / (0.08f * (float) sampleRate)); // glide delay time changes
    feedback = clampf (feedback, 0.0f, 0.95f);
    const bool ping = mode == choices::PingPong;
    float m = m0;

    for (int i = 0; i < n; ++i)
    {
        m += dm;
        curDelay += (target - curDelay) * k;
        float rp = (float) writePos - curDelay;
        if (rp < 0.0f)
            rp += (float) size;
        const int i0 = (int) rp;
        const float fr = rp - (float) i0;
        const int i1 = (i0 + 1) % size;
        const float dl = bufL[(size_t) i0] + fr * (bufL[(size_t) i1] - bufL[(size_t) i0]);
        const float dr = bufR[(size_t) i0] + fr * (bufR[(size_t) i1] - bufR[(size_t) i0]);

        const float fl = fastTanh (hpL.process (lpL.process (dl))) * feedback;
        const float fr2 = fastTanh (hpR.process (lpR.process (dr))) * feedback;
        if (ping)
        {
            bufL[(size_t) writePos] = 0.5f * (L[i] + R[i]) + fr2;
            bufR[(size_t) writePos] = fl;
        }
        else
        {
            bufL[(size_t) writePos] = L[i] + fl;
            bufR[(size_t) writePos] = R[i] + fr2;
        }
        writePos = (writePos + 1) % size;

        float wet;
        const float dry = dryWet (m, wet);
        L[i] = L[i] * dry + dl * wet;
        R[i] = R[i] * dry + dr * wet;
    }
}

// =============================================================================================
void ReverbFx::prepare (double sr)
{
    sampleRate = sr;
    reverb.setSampleRate (sr);
    wetL.assign (8192, 0.0f);
    wetR.assign (8192, 0.0f);
    reset();
}

void ReverbFx::reset()
{
    reverb.reset();
    lastSize = lastDamp = -1.0f;
    lowCutF.reset();
    highCutF.reset();
    lastLow = lastHigh = -1.0f;
    mixRamp = {};
}

void ReverbFx::process (float* L, float* R, int n, float size, float damp, float mix, float lowCut, float highCut) noexcept
{
    float m0, dm;
    mixRamp.set (mix, n, m0, dm);
    if (m0 < 1.0e-4f && mix < 1.0e-4f)
    {
        active = false;
        return;
    }
    if (! active)
    {
        reset();
        mixRamp.set (mix, n, m0, dm);
        active = true;
    }
    if (n > (int) wetL.size())
        return;

    if (std::abs (size - lastSize) > 1.0e-4f || std::abs (damp - lastDamp) > 1.0e-4f)
    {
        juce::Reverb::Parameters rp;
        rp.roomSize = 0.30f + 0.62f * clampf (size, 0.0f, 1.0f);
        rp.damping = clampf (damp, 0.0f, 1.0f);
        rp.wetLevel = 1.0f;
        rp.dryLevel = 0.0f;
        rp.width = 1.0f;
        rp.freezeMode = 0.0f;
        reverb.setParameters (rp);
        lastSize = size;
        lastDamp = damp;
    }

    std::copy (L, L + n, wetL.data());
    std::copy (R, R + n, wetR.data());
    reverb.processStereo (wetL.data(), wetR.data(), n);

    // Tone of the tail: only when moved away from the open ends, so the default reverb is unchanged.
    const bool useLow = lowCut > 20.5f, useHigh = highCut < 19900.0f;
    if (useLow && std::abs (lowCut - lastLow) > 0.01f) { lowCutF.setHighPass (sampleRate, lowCut); lastLow = lowCut; }
    if (useHigh && std::abs (highCut - lastHigh) > 0.01f) { highCutF.setLowPass (sampleRate, highCut); lastHigh = highCut; }
    if (useLow || useHigh)
        for (int i = 0; i < n; ++i)
        {
            float l = wetL[(size_t) i], r = wetR[(size_t) i];
            if (useLow) { l = lowCutF.process (l, 0); r = lowCutF.process (r, 1); }
            if (useHigh) { l = highCutF.process (l, 0); r = highCutF.process (r, 1); }
            wetL[(size_t) i] = l;
            wetR[(size_t) i] = r;
        }

    float m = m0;
    for (int i = 0; i < n; ++i)
    {
        m += dm;
        float wet;
        const float dry = dryWet (m, wet);
        L[i] = L[i] * dry + wetL[(size_t) i] * wet * 0.55f;
        R[i] = R[i] * dry + wetR[(size_t) i] * wet * 0.55f;
    }
}

// =============================================================================================
void SquashCompressor::prepare (double sr)
{
    sampleRate = sr;
    juce::dsp::ProcessSpec spec { sr, 512, 2 };
    for (auto* f : { &lp1, &hp1, &lp2, &hp2, &ap2 })
        f->prepare (spec);
    lp1.setType (juce::dsp::LinkwitzRileyFilterType::lowpass);
    hp1.setType (juce::dsp::LinkwitzRileyFilterType::highpass);
    lp2.setType (juce::dsp::LinkwitzRileyFilterType::lowpass);
    hp2.setType (juce::dsp::LinkwitzRileyFilterType::highpass);
    ap2.setType (juce::dsp::LinkwitzRileyFilterType::allpass);
    lp1.setCutoffFrequency (150.0f);
    hp1.setCutoffFrequency (150.0f);
    lp2.setCutoffFrequency (2500.0f);
    hp2.setCutoffFrequency (2500.0f);
    ap2.setCutoffFrequency (2500.0f);
    const float atkMs[3] = { 12.0f, 6.0f, 2.5f };
    const float relMs[3] = { 180.0f, 110.0f, 70.0f };
    for (int b = 0; b < 3; ++b)
    {
        atk[b] = std::exp (-1.0f / (atkMs[b] * 0.001f * (float) sr));
        rel[b] = std::exp (-1.0f / (relMs[b] * 0.001f * (float) sr));
    }
    reset();
}

void SquashCompressor::reset()
{
    for (auto* f : { &lp1, &hp1, &lp2, &hp2, &ap2 })
        f->reset();
    for (auto& e : env)
        e = 0.0f;
    amountRamp = {};
}

void SquashCompressor::process (float* L, float* R, int n, float amount) noexcept
{
    float a0, da;
    amountRamp.set (amount, n, a0, da);
    if (a0 < 1.0e-4f && amount < 1.0e-4f)
    {
        active = false;
        return;
    }
    if (! active)
    {
        reset();
        amountRamp.set (amount, n, a0, da);
        active = true;
    }

    float a = a0;
    for (int i = 0; i < n; ++i)
    {
        a += da;
        const float amt = clampf (a, 0.0f, 1.0f);
        const float thresholdDb = -8.0f - 22.0f * amt;
        const float ratio = 1.0f + 5.0f * amt;
        const float makeupDb = -thresholdDb * (1.0f - 1.0f / ratio) * 0.55f;

        float band[3][2];
        float* io[2] = { L + i, R + i };
        for (int c = 0; c < 2; ++c)
        {
            const float x = *io[c];
            const float low = lp1.processSample (c, x);
            const float rest = hp1.processSample (c, x);
            band[0][c] = ap2.processSample (c, low);
            band[1][c] = lp2.processSample (c, rest);
            band[2][c] = hp2.processSample (c, rest);
        }

        float outL = 0.0f, outR = 0.0f;
        for (int b = 0; b < 3; ++b)
        {
            const float lvl = std::max (std::abs (band[b][0]), std::abs (band[b][1]));
            const float k = lvl > env[b] ? atk[b] : rel[b];
            env[b] = lvl + k * (env[b] - lvl);
            const float levelDb = juce::Decibels::gainToDecibels (env[b] + 1.0e-9f, -120.0f);
            const float over = levelDb - thresholdDb;
            const float grDb = over > 0.0f ? -over * (1.0f - 1.0f / ratio) : 0.0f;
            const float g = juce::Decibels::decibelsToGain (grDb + makeupDb);
            outL += band[b][0] * g;
            outR += band[b][1] * g;
        }
        L[i] = outL;
        R[i] = outR;
    }
}

// =============================================================================================
void OutputStage::prepare (double sr)
{
    releaseK = std::exp (-1.0f / (0.12f * (float) sr));
    reset();
}

void OutputStage::reset()
{
    envelope = 0.0f;
    gainRamp = {};
}

void OutputStage::process (float* L, float* R, int n, float gainDb) noexcept
{
    constexpr float ceiling = 0.944f; // -0.5 dBFS
    float g0, dg;
    gainRamp.set (juce::Decibels::decibelsToGain (gainDb), n, g0, dg);
    float g = g0;
    for (int i = 0; i < n; ++i)
    {
        g += dg;
        float l = L[i] * g, r = R[i] * g;
        if (! std::isfinite (l)) { l = 0.0f; ++nonFinite; }
        if (! std::isfinite (r)) { r = 0.0f; ++nonFinite; }
        const float pk = std::max (std::abs (l), std::abs (r));
        envelope = pk > envelope ? pk : pk + releaseK * (envelope - pk);
        if (envelope > ceiling)
        {
            const float gr = ceiling / envelope;
            l *= gr;
            r *= gr;
            maxReductionDb = std::max (maxReductionDb, -juce::Decibels::gainToDecibels (gr));
        }
        L[i] = clampf (l, -ceiling, ceiling);
        R[i] = clampf (r, -ceiling, ceiling);
    }
}

// =============================================================================================
void FxChain::prepare (double sr, int maxBlock)
{
    sampleRate = sr;
    dist.prepare (sr, juce::jmax (maxBlock, 64));
    chorus.prepare (sr);
    phaser.prepare (sr);
    flanger.prepare (sr);
    filter.prepare (sr);
    eq.prepare (sr);
    comp.prepare (sr);
    delay.prepare (sr);
    reverb.prepare (sr);
    squash.prepare (sr);
    output.prepare (sr);
}

void FxChain::reset()
{
    dist.reset();
    chorus.reset();
    phaser.reset();
    flanger.reset();
    filter.reset();
    eq.reset();
    comp.reset();
    delay.reset();
    reverb.reset();
    squash.reset();
    output.reset();
}

void FxChain::process (float* L, float* R, int n, const FxParams& p) noexcept
{
    const double bpm = juce::jlimit (20.0, 999.0, p.bpm);
    const double beatsPerSample = bpm / 60.0 / sampleRate;

    for (int e : p.order)
    {
        switch (e)
        {
            case fx::Distortion:
                dist.process (L, R, n, p.distType, clampf (p.distDrive, 0.0f, 1.0f), p.distTone, clampf (p.distMix, 0.0f, 1.0f), p.distKeepLow);
                break;
            case fx::Chorus:  chorus.process (L, R, n, choices::Chorus, p.choRate, p.choDepth, clampf (p.choMix, 0.0f, 1.0f)); break;
            case fx::Phaser:  phaser.process (L, R, n, choices::Phaser, p.phaRate, p.phaDepth, clampf (p.phaMix, 0.0f, 1.0f)); break;
            case fx::Flanger: flanger.process (L, R, n, choices::Flanger, p.flaRate, p.flaDepth, clampf (p.flaMix, 0.0f, 1.0f)); break;
            case fx::Filter:  filter.process (L, R, n, p.fxfType, p.fxfCutoff, p.fxfRes, clampf (p.fxfMix, 0.0f, 1.0f)); break;
            case fx::Eq:      eq.process (L, R, n, p); break;
            case fx::Pump:    pump.process (L, R, n, p.pumpAmount, p.ppq, beatsPerSample, p.pumpBeats); break;
            case fx::Delay:
                delay.process (L, R, n, p.dlyMode, p.dlyBeats * 60.0 / bpm * sampleRate, p.dlyFeedback, clampf (p.dlyMix, 0.0f, 1.0f));
                break;
            case fx::Reverb:
                reverb.process (L, R, n, p.revSize, p.revDamp, clampf (p.revMix, 0.0f, 1.0f), p.revLowCut, p.revHighCut);
                break;
            case fx::Compressor:
                squash.process (L, R, n, p.squash);
                if (p.compOn)
                    comp.process (L, R, n, p.compThreshold, p.compRatio, p.compAttack, p.compRelease, p.compGain);
                else
                    comp.reset();
                break;
            default: break;
        }
    }
    output.process (L, R, n, p.outGainDb);
}
} // namespace volt
