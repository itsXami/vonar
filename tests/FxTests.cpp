#include "TestHelpers.h"
#include "dsp/Effects.h"
#include "dsp/Arpeggiator.h"

using namespace volt;
using namespace volt::test;

struct ArpTests final : juce::UnitTest
{
    ArpTests() : juce::UnitTest ("Arpeggiator", "VOLT") {}

    static std::vector<int> run (int mode, int octaves, std::initializer_list<int> notes, int steps)
    {
        Arpeggiator a;
        a.prepare (48000.0);
        for (int n : notes)
            a.noteOn (n, 0.8f);
        std::vector<int> seq;
        const double bps = 2.0 / 48000.0; // 120 bpm
        double beat = 0.0;
        int guard = 0;
        while ((int) seq.size() < steps && guard++ < 100000)
        {
            const int adv = a.tick (beat, false, bps, 0.25, mode, octaves, 0.5f,
                                    [&] (int n, float) { seq.push_back (n); }, [] (int) {});
            beat += adv * bps;
        }
        return seq;
    }

    void runTest() override
    {
        beginTest ("Up / Down / UpDown patterns");
        expect (run (choices::Up, 1, { 60, 64, 67 }, 6) == std::vector<int> { 60, 64, 67, 60, 64, 67 });
        expect (run (choices::Down, 1, { 60, 64, 67 }, 4) == std::vector<int> { 67, 64, 60, 67 });
        expect (run (choices::UpDown, 1, { 60, 64, 67 }, 6) == std::vector<int> { 60, 64, 67, 64, 60, 64 });
        expect (run (choices::Up, 2, { 60, 64 }, 5) == std::vector<int> { 60, 64, 72, 76, 60 });

        beginTest ("Random stays inside the pattern");
        for (int n : run (choices::Random, 2, { 48, 51 }, 32))
            expect (n == 48 || n == 51 || n == 60 || n == 63);

        beginTest ("Step timing follows tempo (1/16 at 120 bpm = 6000 samples @ 48k)");
        {
            Arpeggiator a;
            a.prepare (48000.0);
            a.noteOn (60, 0.8f);
            const double bps = 2.0 / 48000.0;
            double beat = 0.0;
            long long pos = 0;
            std::vector<long long> ons, offs;
            while (pos < 48000)
            {
                const int adv = a.tick (beat, false, bps, 0.25, choices::Up, 1, 0.5f,
                                        [&] (int, float) { ons.push_back (pos); }, [&] (int) { offs.push_back (pos); });
                pos += adv;
                beat = (double) pos * bps;
            }
            expectGreaterOrEqual ((int) ons.size(), 7);
            if (ons.size() > 2)
            {
                expect (std::llabs (ons[1] - ons[0] - 6000) <= 1);
                expect (std::llabs (offs[0] - ons[0] - 3000) <= 1);
            }
        }
    }
};

struct FxTests final : juce::UnitTest
{
    FxTests() : juce::UnitTest ("Effects", "VOLT") {}

    static FxParams quiet()
    {
        FxParams p;
        p.distMix = p.choMix = p.phaMix = p.flaMix = p.dlyMix = p.revMix = p.squash = p.pumpAmount = 0.0f;
        return p;
    }

    static void runChain (FxChain& fx, std::vector<float>& l, std::vector<float>& r, FxParams p, double sr)
    {
        const int n = (int) l.size();
        for (int pos = 0; pos < n; pos += 32)
        {
            const int k = std::min (32, n - pos);
            p.ppq = (double) pos / sr * p.bpm / 60.0;
            fx.process (l.data() + pos, r.data() + pos, k, p);
        }
    }

    void runTest() override
    {
        const double sr = 48000.0;

        beginTest ("Limiter never exceeds -0.5 dBFS, even with +20 dB input");
        {
            FxChain fx;
            fx.prepare (sr, 512);
            std::vector<float> l (48000), r (48000);
            for (int i = 0; i < 48000; ++i)
                l[(size_t) i] = r[(size_t) i] = 10.0f * std::sin (0.05f * (float) i);
            auto p = quiet();
            p.outGainDb = 12.0f;
            runChain (fx, l, r, p, sr);
            expectLessOrEqual (peak (l), 0.9441f);
            expectGreaterThan (fx.getLimiterReductionDb(), 20.0f);
        }

        beginTest ("Bypassed chain is transparent below the ceiling");
        {
            FxChain fx;
            fx.prepare (sr, 512);
            std::vector<float> l (4800), r (4800), ref (4800);
            for (int i = 0; i < 4800; ++i)
                ref[(size_t) i] = l[(size_t) i] = r[(size_t) i] = 0.3f * std::sin (0.01f * (float) i);
            runChain (fx, l, r, quiet(), sr);
            float maxDiff = 0.0f;
            for (int i = 0; i < 4800; ++i)
                maxDiff = std::max (maxDiff, std::abs (l[(size_t) i] - ref[(size_t) i]));
            expectLessThan (maxDiff, 1.0e-5f);
        }

        beginTest ("Distortion adds harmonics for every type");
        for (int type = 0; type <= choices::Bitcrush; ++type)
        {
            FxChain fx;
            fx.prepare (sr, 512);
            const int n = 16384;
            std::vector<float> l ((size_t) n), r ((size_t) n);
            const float f0 = 375.0f; // bin-aligned for 2^14 @ 48k
            for (int i = 0; i < n; ++i)
                l[(size_t) i] = r[(size_t) i] = 0.25f * std::sin (6.2831853f * f0 * (float) i / (float) sr);
            auto p = quiet();
            p.distType = type;
            p.distDrive = 0.7f;
            p.distTone = 1.0f;
            p.distMix = 1.0f;
            runChain (fx, l, r, p, sr);
            std::vector<float> tail (l.begin() + 8192, l.end());
            tail.resize (8192);
            auto mag = spectrum (tail, 0, 13);
            const size_t b0 = (size_t) std::lround (f0 / (sr / 8192.0));
            float other = 0.0f, fund = 0.0f;
            for (size_t b = 2; b < mag.size(); ++b)
            {
                if (b + 3 >= b0 && b <= b0 + 3)
                    fund += mag[b] * mag[b];
                else
                    other += mag[b] * mag[b];
            }
            expectGreaterThan (std::sqrt (other / fund), 0.05f, "type " + juce::String (type));
            expect (allFinite (l), "type " + juce::String (type));
        }

        beginTest ("Pump ducks on the beat and recovers");
        {
            FxChain fx;
            fx.prepare (sr, 512);
            std::vector<float> l (48000, 0.5f), r (48000, 0.5f);
            auto p = quiet();
            p.pumpAmount = 0.8f;
            p.pumpBeats = 1.0;
            p.bpm = 120.0;
            runChain (fx, l, r, p, sr);
            // beat length = 24000 samples; dip right after the beat, near unity before the next one
            expectLessThan (l[24000 + 600], 0.5f * 0.35f);
            expectGreaterThan (l[24000 + 23000], 0.5f * 0.95f);
        }

        beginTest ("Delay repeats after one beat");
        {
            FxChain fx;
            fx.prepare (sr, 512);
            std::vector<float> l (60000, 0.0f), r (60000, 0.0f);
            l[100] = r[100] = 0.8f;
            auto p = quiet();
            p.dlyMix = 0.5f;
            p.dlyBeats = 1.0;
            p.dlyFeedback = 0.3f;
            p.bpm = 120.0;
            runChain (fx, l, r, p, sr);
            float echo = 0.0f;
            for (int i = 24000 + 100 - 40; i < 24000 + 100 + 40; ++i)
                echo = std::max (echo, std::abs (l[(size_t) i]));
            expectGreaterThan (echo, 0.2f);
        }

        beginTest ("Reverb tail decays");
        {
            FxChain fx;
            fx.prepare (sr, 512);
            const int n = (int) sr * 8;
            std::vector<float> l ((size_t) n, 0.0f), r ((size_t) n, 0.0f);
            for (int i = 0; i < 2400; ++i)
                l[(size_t) i] = r[(size_t) i] = 0.5f * std::sin (0.07f * (float) i);
            auto p = quiet();
            p.revMix = 0.5f;
            p.revSize = 1.0f;
            p.revDamp = 0.3f;
            runChain (fx, l, r, p, sr);
            const float early = rms (l.data() + 4800, 4800);
            const float late = rms (l.data() + n - 4800, 4800);
            expectGreaterThan (early, 0.01f);
            expectLessThan (juce::Decibels::gainToDecibels (late + 1.0e-12f), -70.0f);
        }

        beginTest ("Squash reduces dynamic range");
        {
            FxChain fx;
            fx.prepare (sr, 512);
            std::vector<float> l (96000), r (96000);
            for (int i = 0; i < 96000; ++i)
            {
                const float env = (i / 24000) % 2 == 0 ? 0.6f : 0.06f;
                l[(size_t) i] = r[(size_t) i] = env * std::sin (6.2831853f * 1000.0f * (float) i / (float) sr);
            }
            auto p = quiet();
            p.squash = 1.0f;
            runChain (fx, l, r, p, sr);
            const float loud = rms (l.data() + 48000 - 4800, 4800);
            const float soft = rms (l.data() + 72000 - 4800, 4800);
            const float rangeDb = juce::Decibels::gainToDecibels (loud / soft);
            logMessage ("squashed range: " + juce::String (rangeDb, 1) + " dB (input 20 dB)");
            expectLessThan (rangeDb, 12.0f);
        }
    }
};

struct ModulationTests final : juce::UnitTest
{
    ModulationTests() : juce::UnitTest ("Modulation", "VOLT") {}

    void runTest() override
    {
        beginTest ("Macro routed to cutoff opens the filter");
        {
            auto p = defaults();
            p.v[FltCutoff] = 300.0f;
            p.v[Mod1_Src] = (float) choices::SrcMacro1;
            p.v[Mod1_Dst] = (float) choices::DstCutoff;
            p.v[Mod1_Amt] = 1.0f;
            SynthEngine a, b;
            a.prepare (48000.0, 256);
            b.prepare (48000.0, 256);
            auto closed = renderNotes (a, p, { 48 }, 0.5, -1.0, 48000.0);
            p.v[Macro1] = 1.0f;
            auto open = renderNotes (b, p, { 48 }, 0.5, -1.0, 48000.0);
            auto mc = spectrum (closed.L, 8192, 13), mo = spectrum (open.L, 8192, 13);
            float hc = 0.0f, ho = 0.0f;
            for (size_t i = 200; i < 2000; ++i) { hc += mc[i]; ho += mo[i]; }
            expectGreaterThan (ho, hc * 4.0f);
        }

        beginTest ("LFO to pitch creates vibrato; Velocity to level scales output");
        {
            auto p = defaults();
            p.v[Mod1_Src] = (float) choices::SrcVelocity;
            p.v[Mod1_Dst] = (float) choices::DstLevelA;
            p.v[Mod1_Amt] = 0.6f;
            p.v[OscA_Level] = 0.2f;
            SynthEngine a, b;
            a.prepare (48000.0, 256);
            b.prepare (48000.0, 256);
            auto soft = renderNotes (a, p, { 60 }, 0.3, -1.0, 48000.0, 256, 0.1f);
            auto hard = renderNotes (b, p, { 60 }, 0.3, -1.0, 48000.0, 256, 1.0f);
            expectGreaterThan (rms (hard.L.data() + 4800, 4800), 2.0f * rms (soft.L.data() + 4800, 4800));
        }

        beginTest ("Arp through the engine plays a sequence");
        {
            auto p = defaults();
            p.v[ArpOn] = 1.0f;
            p.v[AmpR] = 0.01f;
            SynthEngine e;
            e.prepare (48000.0, 256);
            auto r = renderNotes (e, p, { 60, 64, 67 }, 1.0, -1.0, 48000.0);
            int onsets = 0;
            bool wasQuiet = true;
            for (int blk = 0; blk < 48000 / 240; ++blk)
            {
                const float lv = rms (r.L.data() + blk * 240, 240);
                if (wasQuiet && lv > 0.02f) ++onsets;
                wasQuiet = lv < 0.005f;
            }
            expectGreaterOrEqual (onsets, 6); // 1/16 at 120 bpm = 8 steps per second
        }
    }
};

static ArpTests arpTests;
static FxTests fxTests;
static ModulationTests modulationTests;

struct PerformanceTests final : juce::UnitTest
{
    PerformanceTests() : juce::UnitTest ("Performance", "VOLT") {}

    void runTest() override
    {
        beginTest ("Worst case (16 voices x 2 osc x 8 unison, all FX) renders faster than real time");
        auto p = defaults();
        p.v[OscA_Voices] = p.v[OscB_Voices] = 8.0f;
        p.v[OscB_Level] = 0.6f;
        p.v[SubLevel] = 0.3f;
        p.v[NoiseLevel] = 0.1f;
        p.v[FltType] = (float) choices::Ladder;
        p.v[DistMix] = p.v[ChoMix] = p.v[PhaMix] = p.v[FlaMix] = p.v[DlyMix] = p.v[RevMix] = 0.5f;
        p.v[FxFilterOn] = p.v[FxEqOn] = 1.0f;
        p.v[EqLowGain] = 3.0f;
        p.v[EqMidGain] = -4.0f;
        p.v[EqHighGain] = 2.0f;
        p.v[CompRatio] = 4.0f;
        p.v[CompThreshold] = -18.0f;
        p.v[PumpAmount] = 0.5f;
        p.v[Squash] = 0.5f;
        SynthEngine e;
        e.prepare (48000.0, 512);
        const auto t0 = juce::Time::getMillisecondCounterHiRes();
        renderNotes (e, p, { 36, 40, 43, 47, 48, 52, 55, 59, 60, 64, 67, 71, 72, 76, 79, 83 }, 5.0, -1.0, 48000.0, 512);
        const double ms = juce::Time::getMillisecondCounterHiRes() - t0;
        const double rt = ms / 5000.0;
        logMessage ("worst-case CPU: " + juce::String (rt * 100.0, 1) + " % of one core in real time");
        expectLessThan (rt, 1.0);

        beginTest ("Distortion Keep Low leaves the sub clean");
        {
            const double sr = 48000.0;
            auto measure = [&] (bool keep) {
                Distortion d;
                d.prepare (sr, 512);
                std::vector<float> L (48128), R (48128);   // whole 512-sample blocks
                for (size_t i = 0; i < L.size(); ++i)
                    L[i] = R[i] = 0.5f * std::sin (6.2831853f * 50.0f * (float) i / (float) sr);
                for (size_t pos = 0; pos < L.size(); pos += 512)
                    d.process (L.data() + pos, R.data() + pos, 512, choices::Hard, 1.0f, 1.0f, 1.0f, keep);
                // energy outside the 50 Hz fundamental = harmonics added by the distortion
                auto mag = volt::test::spectrum (L, 16384, 14);
                const float bin = (float) sr / 16384.0f;
                double fund = 0.0, rest = 0.0;
                for (size_t b = 1; b < mag.size(); ++b)
                {
                    const double e = (double) mag[b] * mag[b];
                    if (std::abs ((float) b * bin - 50.0f) < 6.0f) fund += e; else rest += e;
                }
                return rest / (fund + 1.0e-12);
            };
            const double full = measure (false), keep = measure (true);
            logMessage ("50 Hz sine, hard clip: harmonic/fundamental energy full " + juce::String (full, 4) + ", keep low " + juce::String (keep, 4));
            expectGreaterThan (full, 0.05);
            expectLessThan (keep, full * 0.1);
        }
    }
};
static PerformanceTests performanceTests;
