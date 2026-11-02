#include "Effects.h"

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
    dcL.reset();
    dcR.reset();
    crushHoldL = crushHoldR = crushCount = 0.0f;
    mixRamp = {};
    driveRamp = {};
}

void Distortion::process (float* L, float* R, int n, int type, float drive, float tone, float mix) noexcept
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
        const float wl = dcL.process (toneL.process (L[i]));
        const float wr = dcR.process (toneR.process (R[i]));
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
    reverb.setSampleRate (sr);
    wetL.assign (8192, 0.0f);
    wetR.assign (8192, 0.0f);
    reset();
}

void ReverbFx::reset()
{
    reverb.reset();
    lastSize = lastDamp = -1.0f;
    mixRamp = {};
}

void ReverbFx::process (float* L, float* R, int n, float size, float damp, float mix) noexcept
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
        if (! std::isfinite (l)) l = 0.0f;
        if (! std::isfinite (r)) r = 0.0f;
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
    modFx.prepare (sr);
    delay.prepare (sr);
    reverb.prepare (sr);
    squash.prepare (sr);
    output.prepare (sr);
}

void FxChain::reset()
{
    dist.reset();
    modFx.reset();
    delay.reset();
    reverb.reset();
    squash.reset();
    output.reset();
}

void FxChain::process (float* L, float* R, int n, const FxParams& p) noexcept
{
    const double bpm = juce::jlimit (20.0, 999.0, p.bpm);
    const double beatsPerSample = bpm / 60.0 / sampleRate;

    dist.process (L, R, n, p.distType, clampf (p.distDrive, 0.0f, 1.0f), p.distTone, clampf (p.distMix, 0.0f, 1.0f));
    modFx.process (L, R, n, p.mfxType, p.mfxRate, p.mfxDepth, clampf (p.mfxMix, 0.0f, 1.0f));
    pump.process (L, R, n, p.pumpAmount, p.ppq, beatsPerSample, p.pumpBeats);
    delay.process (L, R, n, p.dlyMode, p.dlyBeats * 60.0 / bpm * sampleRate, p.dlyFeedback, clampf (p.dlyMix, 0.0f, 1.0f));
    reverb.process (L, R, n, p.revSize, p.revDamp, clampf (p.revMix, 0.0f, 1.0f));
    squash.process (L, R, n, p.squash);
    output.process (L, R, n, p.outGainDb);
}
} // namespace volt
