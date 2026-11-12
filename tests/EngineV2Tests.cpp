#include "TestHelpers.h"
#include "dsp/VoiceFilter.h"

using namespace volt;
using namespace volt::test;

namespace
{
float estimateF0 (const std::vector<float>& x, int start, int len, double sr, float fmin, float fmax)
{
    const int minLag = (int) (sr / fmax), maxLag = (int) (sr / fmin);
    double best = -1.0;
    int bestLag = minLag;
    for (int lag = minLag; lag <= maxLag; ++lag)
    {
        double num = 0.0, e0 = 0.0, e1 = 0.0;
        for (int i = start; i < start + len; ++i)
        {
            num += (double) x[(size_t) i] * x[(size_t) (i + lag)];
            e0 += (double) x[(size_t) i] * x[(size_t) i];
            e1 += (double) x[(size_t) (i + lag)] * x[(size_t) (i + lag)];
        }
        const double r = num / std::sqrt (e0 * e1 + 1.0e-20);
        if (r > best) { best = r; bestLag = lag; }
    }
    // parabolic refinement is unnecessary for a 1 % tolerance at these lags
    return (float) (sr / bestLag);
}

float centroid (const std::vector<float>& x, int start, double sr)
{
    auto mag = spectrum (x, start, 13);
    double num = 0.0, den = 0.0;
    for (size_t b = 1; b < mag.size(); ++b)
    {
        num += (double) b * sr / 8192.0 * mag[b];
        den += mag[b];
    }
    return (float) (num / (den + 1.0e-12));
}
} // namespace

struct EngineV2Tests final : juce::UnitTest
{
    EngineV2Tests() : juce::UnitTest ("Engine v2", "VOLT") {}

    void runTest() override
    {
        const double sr = 48000.0;

        beginTest ("Defaults keep the original sound (new features are off)");
        {
            const auto p = defaults();
            expectEquals (p.i (OscA_Type), (int) choices::Wavetable);
            expectEquals (p.i (OscA_Warp), (int) choices::WarpOff);
            expectEquals (p.i (OscB_Warp), (int) choices::WarpOff);
        }

        beginTest ("Every warp mode changes the timbre and stays bounded");
        {
            SynthEngine ref;
            ref.prepare (sr, 256);
            auto base = defaults();
            base.v[OscA_Table] = (float) wavetableIndex ("Basic Shapes");
            base.v[OscA_Pos] = 0.0f; // pure sine: every warp must add harmonics
            base.v[OscB_Level] = 0.0f;
            base.v[OscB_Semi] = 7.0f; // silent modulator for FM / RM
            const auto offOut = renderNotes (ref, base, { 48 }, 0.6, -1.0, sr);
            const float offC = centroid (offOut.L, 8192, sr);
            for (int mode = choices::WarpSync; mode <= choices::WarpRM; ++mode)
            {
                SynthEngine e;
                e.prepare (sr, 256);
                auto p = base;
                p.v[OscA_Warp] = (float) mode;
                p.v[OscA_WarpAmt] = 0.7f;
                const auto r = renderNotes (e, p, { 48 }, 0.6, -1.0, sr);
                expect (allFinite (r.L), "mode " + juce::String (mode));
                expectLessThan (peak (r.L), 1.0f, "mode " + juce::String (mode));
                expectGreaterThan (peak (r.L), 0.02f, "mode " + juce::String (mode));
                const float c = centroid (r.L, 8192, sr);
                expectGreaterThan (std::abs (c - offC) / offC, 0.25f, "mode " + juce::String (mode) + " centroid "
                                   + juce::String (c) + " vs " + juce::String (offC));
            }
        }

        beginTest ("String oscillator is in tune, decays, and Tone controls brightness");
        {
            auto p = defaults();
            p.v[OscA_Type] = (float) choices::String;
            p.v[OscA_Table] = (float) wavetableIndex ("Analog Saw");
            p.v[StrDecay] = 1.0f;
            p.v[StrTone] = 0.7f;
            p.v[AmpS] = 1.0f;
            for (int note : { 40, 57, 69 })
            {
                SynthEngine e;
                e.prepare (sr, 256);
                const auto r = renderNotes (e, p, { note }, 1.5, -1.0, sr);
                const float f = estimateF0 (r.L, 4800, 4800, sr, 50.0f, 1000.0f);
                const float want = pitchToHz ((float) note);
                expectWithinAbsoluteError (f / want, 1.0f, 0.012f, "note " + juce::String (note) + ": " + juce::String (f) + " Hz");
                const float early = rms (r.L.data() + 2400, 4800);
                const float late = rms (r.L.data() + (int) (1.3 * sr), 4800);
                expectGreaterThan (early, 0.01f);
                expectLessThan (late, early * 0.25f, "decay note " + juce::String (note));
                expect (allFinite (r.L));
            }
            SynthEngine dark, bright;
            dark.prepare (sr, 256);
            bright.prepare (sr, 256);
            p.v[StrTone] = 0.15f;
            const auto d = renderNotes (dark, p, { 57 }, 0.6, -1.0, sr);
            p.v[StrTone] = 0.95f;
            const auto b = renderNotes (bright, p, { 57 }, 0.6, -1.0, sr);
            expectGreaterThan (centroid (b.L, 4096, sr), centroid (d.L, 4096, sr) * 1.3f);
        }

        beginTest ("Comb filters resonate at the cutoff frequency and its harmonics");
        for (int type : { (int) choices::CombPlus, (int) choices::CombMinus })
        {
            VoiceFilter f;
            f.prepare (sr);
            XorShift rng (3);
            const int n = 32768;
            std::vector<float> l ((size_t) n), r ((size_t) n);
            for (int i = 0; i < n; ++i)
                l[(size_t) i] = r[(size_t) i] = 0.2f * rng.nextBipolar();
            for (int pos = 0; pos < n; pos += 32)
                f.process (type, l.data() + pos, r.data() + pos, 32, 750.0f, 0.9f, 0.0f, 0.0f);
            expect (allFinite (l));
            auto mag = spectrum (l, 8192, 14);
            const double binHz = sr / 16384.0;
            auto band = [&] (double hz) { double s = 0; for (int k = -2; k <= 2; ++k) s += mag[(size_t) (hz / binHz) + (size_t) (k + 2) - 2]; return s; };
            const double peakHz = type == choices::CombPlus ? 1500.0 : 1125.0;  // harmonic vs odd-half-harmonic
            const double valleyHz = type == choices::CombPlus ? 1125.0 : 1500.0;
            expectGreaterThan (band (peakHz), band (valleyHz) * 3.0, "comb type " + juce::String (type));
        }

        beginTest ("Random and Mod Env sources, 12th modulation slot");
        {
            auto p = defaults();
            p.v[FltCutoff] = 800.0f;
            p.v[Mod12_Src] = (float) choices::SrcRandom;
            p.v[Mod12_Dst] = (float) choices::DstCutoff;
            p.v[Mod12_Amt] = 0.8f;
            SynthEngine e;
            e.prepare (sr, 256);
            // Two consecutive notes get different random values -> different brightness.
            const auto a = renderNotes (e, p, { 60 }, 0.4, 0.2, sr);
            const auto b = renderNotes (e, p, { 60 }, 0.4, 0.2, sr);
            const float ca = centroid (a.L, 0, sr), cb = centroid (b.L, 0, sr);
            expectGreaterThan (std::abs (ca - cb), 30.0f, juce::String (ca) + " vs " + juce::String (cb));

            auto q = defaults();
            q.v[MenvA] = 0.2f;
            q.v[MenvD] = 1.0f;
            q.v[MenvS] = 1.0f;
            q.v[Mod1_Src] = (float) choices::SrcModEnv;
            q.v[Mod1_Dst] = (float) choices::DstPitch;
            q.v[Mod1_Amt] = 0.5f; // +12 semitones at full envelope
            SynthEngine m;
            m.prepare (sr, 256);
            const auto r = renderNotes (m, q, { 57 }, 0.8, -1.0, sr);
            const float early = estimateF0 (r.L, 240, 1200, sr, 100.0f, 1000.0f);
            const float late = estimateF0 (r.L, (int) (0.6 * sr), 2400, sr, 100.0f, 1000.0f);
            expectWithinAbsoluteError (late / early, 2.0f, 0.15f);
        }

        beginTest ("String mode with unison 8 and all voices is real-time safe and fast");
        {
            auto p = defaults();
            p.v[OscA_Type] = p.v[OscB_Type] = (float) choices::String;
            p.v[OscA_Voices] = p.v[OscB_Voices] = 8.0f;
            p.v[OscB_Level] = 0.6f;
            SynthEngine e;
            e.prepare (sr, 512);
            const auto t0 = juce::Time::getMillisecondCounterHiRes();
            const auto r = renderNotes (e, p, { 36, 40, 43, 47, 48, 52, 55, 59, 60, 64, 67, 71, 72, 76, 79, 83 }, 3.0, -1.0, sr, 512);
            const double rt = (juce::Time::getMillisecondCounterHiRes() - t0) / 3000.0;
            logMessage ("string worst-case CPU: " + juce::String (rt * 100.0, 1) + " %");
            expect (allFinite (r.L));
            expectLessThan (rt, 1.0);
        }

        beginTest ("Phase-shaping warps leave no DC offset");
        for (int mode : { (int) choices::WarpSqueeze, (int) choices::WarpBend })
        {
            auto p = defaults();
            p.v[OscA_Table] = (float) wavetableIndex ("Reed");
            p.v[OscA_Pos] = 0.3f;
            p.v[OscA_Warp] = (float) mode;
            p.v[OscA_WarpAmt] = 0.6f;
            SynthEngine e;
            e.prepare (sr, 512);
            const auto r = renderNotes (e, p, { 48, 55, 60 }, 2.0, -1.0, sr, 512);
            double mean = 0.0;
            for (size_t i = (size_t) sr; i < r.L.size(); ++i)
                mean += r.L[i];
            mean /= (double) (r.L.size() - (size_t) sr);
            expectLessThan (std::abs (mean), 0.003, "warp mode " + juce::String (mode));
        }
    }
};

static EngineV2Tests engineV2Tests;
