#pragma once

#include "DspUtil.h"
#include "Formants.h"
#include "../Params.h"

namespace volt
{
// Per-voice stereo filter: TPT state-variable (LP12/LP24/HP/BP/Notch), a zero-delay ladder with
// saturating feedback (acid-style resonance) and a 3-band formant bank (A-E-I-O-U morph).
// Coefficients are computed at chunk boundaries and interpolated per sample (no zipper noise).
class VoiceFilter
{
public:
    void prepare (double sr) noexcept { sampleRate = sr; reset(); }

    void reset() noexcept
    {
        for (auto& c : ch)
            c = {};
        first = true;
    }

    // Processes L/R in place; targets apply at the end of the chunk, ramped from the previous call.
    void process (int type, float* L, float* R, int n, float cutoffHz, float res, float drive, float vowel) noexcept;

private:
    struct Svf { float ic1 = 0.0f, ic2 = 0.0f; };
    struct Channel
    {
        Svf a, b;
        float lad[4] {};
        Svf f[3];
    };

    struct Coeffs
    {
        float g = 0.1f, k = 1.0f, drive = 0.0f;
        float fg[3] {}, fk[3] {}, fgain[3] {};
    };

    Coeffs computeCoeffs (int type, float cutoffHz, float res, float drive, float vowel) const noexcept;

    static inline void svf (Svf& s, float v0, float g, float k, float& lp, float& bp, float& hp) noexcept
    {
        const float a1 = 1.0f / (1.0f + g * (g + k));
        const float a2 = g * a1;
        const float a3 = g * a2;
        const float v3 = v0 - s.ic2;
        const float v1 = a1 * s.ic1 + a2 * v3;
        const float v2 = s.ic2 + a2 * s.ic1 + a3 * v3;
        s.ic1 = 2.0f * v1 - s.ic1;
        s.ic2 = 2.0f * v2 - s.ic2;
        lp = v2;
        bp = v1;
        hp = v0 - k * v1 - v2;
    }

    double sampleRate = 44100.0;
    Channel ch[2];
    Coeffs prev;
    int lastType = -1;
    bool first = true;
};

inline VoiceFilter::Coeffs VoiceFilter::computeCoeffs (int type, float cutoffHz, float res, float drive, float vowel) const noexcept
{
    Coeffs c;
    const float sr = (float) sampleRate;
    const float fc = clampf (cutoffHz, 16.0f, 0.46f * sr);
    c.g = std::tan (kPiF * fc / sr);
    res = clampf (res, 0.0f, 1.0f);
    c.drive = clampf (drive, 0.0f, 1.0f);

    if (type == choices::Ladder)
        c.k = 3.96f * res;
    else
        c.k = 1.0f / (0.5f * std::pow (40.0f, res)); // Q 0.5 .. 20

    if (type == choices::Formant)
    {
        const auto v = vowelAt (vowel);
        const float shift = clampf (cutoffHz / 1000.0f, 0.5f, 2.0f);
        const float bwScale = 2.0f * std::pow (0.25f, res); // wide .. narrow
        for (int k = 0; k < 3; ++k)
        {
            const float f = clampf (v.freq[(size_t) k] * shift, 60.0f, 0.45f * sr);
            c.fg[k] = std::tan (kPiF * f / sr);
            const float q = clampf (f / (v.bw[(size_t) k] * bwScale), 0.7f, 60.0f);
            c.fk[k] = 1.0f / q;
            c.fgain[k] = std::pow (10.0f, v.gainDb[(size_t) k] / 20.0f);
        }
    }
    return c;
}

inline void VoiceFilter::process (int type, float* L, float* R, int n, float cutoffHz, float res, float drive, float vowel) noexcept
{
    if (n <= 0)
        return;

    if (type != lastType)
    {
        for (auto& c : ch)
            c = {};
        lastType = type;
        first = true;
    }

    const Coeffs to = computeCoeffs (type, cutoffHz, res, drive, vowel);
    if (first)
    {
        prev = to;
        first = false;
    }
    const Coeffs from = prev;
    prev = to;

    const float inv = 1.0f / (float) n;
    float* bufs[2] = { L, R };

    for (int c = 0; c < 2; ++c)
    {
        Channel& st = ch[c];
        float* x = bufs[c];
        float g = from.g, k = from.k, d = from.drive;
        const float dg = (to.g - from.g) * inv, dk = (to.k - from.k) * inv, dd = (to.drive - from.drive) * inv;

        float fg[3], fk[3], fgain[3], dfg[3], dfk[3], dfgain[3];
        for (int i = 0; i < 3; ++i)
        {
            fg[i] = from.fg[i]; fk[i] = from.fk[i]; fgain[i] = from.fgain[i];
            dfg[i] = (to.fg[i] - from.fg[i]) * inv;
            dfk[i] = (to.fk[i] - from.fk[i]) * inv;
            dfgain[i] = (to.fgain[i] - from.fgain[i]) * inv;
        }

        for (int i = 0; i < n; ++i)
        {
            g += dg; k += dk; d += dd;
            float in = x[i];

            // Pre-filter drive, blended in continuously from 0.
            if (d > 1.0e-4f)
            {
                const float gain = 1.0f + 15.0f * d * d;
                const float wet = fastTanh (in * gain) / (1.0f + 1.5f * d);
                in += (wet - in) * std::min (1.0f, d * 10.0f);
            }

            float out = 0.0f, lp, bp, hp;
            switch (type)
            {
                case choices::LP12:
                    svf (st.a, in, g, k, lp, bp, hp);
                    out = lp;
                    break;
                case choices::LP24:
                {
                    svf (st.a, in, g, 1.41421356f, lp, bp, hp);
                    float lp2, bp2, hp2;
                    svf (st.b, lp, g, k, lp2, bp2, hp2);
                    out = lp2;
                    break;
                }
                case choices::HP:
                    svf (st.a, in, g, k, lp, bp, hp);
                    out = hp;
                    break;
                case choices::BP:
                    svf (st.a, in, g, k, lp, bp, hp);
                    out = bp * std::max (k, 0.25f) * 1.6f;
                    break;
                case choices::Notch:
                    svf (st.a, in, g, k, lp, bp, hp);
                    out = lp + hp;
                    break;
                case choices::Ladder:
                {
                    const float G = g / (1.0f + g);
                    const float beta = 1.0f / (1.0f + g);
                    float* s = st.lad;
                    const float S = beta * (G * G * G * s[0] + G * G * s[1] + G * s[2] + s[3]);
                    const float G4 = G * G * G * G;
                    const float y4est = (G4 * in + S) / (1.0f + k * G4);
                    const float u = fastTanh (in - k * y4est);
                    float v = (u - s[0]) * G; const float y1 = v + s[0]; s[0] = y1 + v;
                    v = (y1 - s[1]) * G; const float y2 = v + s[1]; s[1] = y2 + v;
                    v = (y2 - s[2]) * G; const float y3 = v + s[2]; s[2] = y3 + v;
                    v = (y3 - s[3]) * G; const float y4 = v + s[3]; s[3] = y4 + v;
                    out = y4 * (1.0f + 0.35f * k);
                    break;
                }
                case choices::Formant:
                default:
                {
                    float sum = 0.0f;
                    for (int f = 0; f < 3; ++f)
                    {
                        fg[f] += dfg[f]; fk[f] += dfk[f]; fgain[f] += dfgain[f];
                        svf (st.f[f], in, fg[f], fk[f], lp, bp, hp);
                        sum += fgain[f] * fk[f] * bp;
                    }
                    out = sum * 2.2f;
                    break;
                }
            }
            x[i] = out;
        }
    }
}
} // namespace volt
