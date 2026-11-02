#include "TestHelpers.h"
#include "dsp/VoiceFilter.h"
#include "dsp/Modulators.h"

using namespace volt;
using namespace volt::test;

struct WavetableTests final : juce::UnitTest
{
    WavetableTests() : juce::UnitTest ("Wavetables", "VOLT") {}

    void runTest() override
    {
        const auto& bank = WavetableBank::get();

        beginTest ("At least 24 procedurally generated tables");
        expectGreaterOrEqual (bank.size(), 24);
        expectEquals (bank.size(), wavetableNames().size());

        beginTest ("All samples finite, mip 0 normalised to peak 1");
        for (int t = 0; t < bank.size(); ++t)
        {
            const auto& wt = bank[t];
            bool finite = true;
            for (float v : wt.data)
                finite = finite && std::isfinite (v);
            expect (finite, wt.name);
            for (int f = 0; f < kWtFrames; ++f)
            {
                const float* c = wt.cycle (0, f);
                float pk = 0.0f;
                for (int i = 0; i < wt.sizes[0]; ++i)
                    pk = std::max (pk, std::abs (c[i]));
                expectWithinAbsoluteError (pk, 1.0f, 1.0e-3f, wt.name + " frame " + juce::String (f));
                expectEquals (c[wt.sizes[0]], c[0]);
            }
        }

        beginTest ("Mipmaps are band-limited");
        for (int t = 0; t < bank.size(); ++t)
        {
            const auto& wt = bank[t];
            for (int mip : { 3, 5, 7 })
            {
                const int size = wt.sizes[(size_t) mip];
                const int limit = Wavetable::harmonicLimit (mip);
                const float* c = wt.cycle (mip, kWtFrames / 2);
                double maxAbove = 0.0, maxAll = 1.0e-12;
                for (int h = 1; h < size / 2; ++h)
                {
                    double re = 0.0, im = 0.0;
                    for (int i = 0; i < size; ++i)
                    {
                        const double a = 6.283185307179586 * h * i / size;
                        re += c[i] * std::cos (a);
                        im -= c[i] * std::sin (a);
                    }
                    const double mag = std::sqrt (re * re + im * im) * 2.0 / size;
                    maxAll = std::max (maxAll, mag);
                    if (h > limit)
                        maxAbove = std::max (maxAbove, mag);
                }
                expectLessThan (maxAbove / maxAll, 1.0e-4, wt.name + " mip " + juce::String (mip));
            }
        }

        beginTest ("Mip selection keeps harmonics under Nyquist");
        for (float inc : { 0.0001f, 0.001f, 0.01f, 0.05f, 0.2f })
        {
            const int mip = Wavetable::mipForIncrement (inc);
            expect ((float) Wavetable::harmonicLimit (mip) * inc < 0.5f || mip == kWtMips - 1);
        }
    }
};

struct FilterTests final : juce::UnitTest
{
    FilterTests() : juce::UnitTest ("Filter", "VOLT") {}

    static float toneGain (int type, float cutoff, float res, float freq, float vowel = 0.0f)
    {
        VoiceFilter f;
        const double sr = 48000.0;
        f.prepare (sr);
        const int n = 48000;
        std::vector<float> l ((size_t) n), r ((size_t) n);
        for (int i = 0; i < n; ++i)
            l[(size_t) i] = r[(size_t) i] = 0.1f * std::sin (6.2831853f * freq * (float) i / (float) sr);
        for (int pos = 0; pos < n; pos += 32)
            f.process (type, l.data() + pos, r.data() + pos, std::min (32, n - pos), cutoff, res, 0.0f, vowel);
        return rms (l.data() + n / 2, n / 2) / (0.1f / std::sqrt (2.0f));
    }

    void runTest() override
    {
        beginTest ("LP24 slope");
        {
            const float pass = toneGain (choices::LP24, 1000.0f, 0.0f, 200.0f);
            const float stop = toneGain (choices::LP24, 1000.0f, 0.0f, 4000.0f);
            expectWithinAbsoluteError (pass, 1.0f, 0.15f);
            expectLessThan (juce::Decibels::gainToDecibels (stop), -40.0f);
        }
        beginTest ("LP12 / HP / BP / Notch shapes");
        {
            expectLessThan (juce::Decibels::gainToDecibels (toneGain (choices::LP12, 1000.0f, 0.0f, 8000.0f)), -30.0f);
            expectLessThan (juce::Decibels::gainToDecibels (toneGain (choices::HP, 1000.0f, 0.0f, 125.0f)), -30.0f);
            expectWithinAbsoluteError (toneGain (choices::HP, 1000.0f, 0.0f, 8000.0f), 1.0f, 0.15f);
            expectGreaterThan (toneGain (choices::BP, 1000.0f, 0.3f, 1000.0f), 0.5f);
            expectLessThan (toneGain (choices::BP, 1000.0f, 0.3f, 100.0f), 0.2f);
            expectLessThan (toneGain (choices::Notch, 1000.0f, 0.2f, 1000.0f), 0.1f);
        }
        beginTest ("Ladder resonates at cutoff");
        {
            const float atCut = toneGain (choices::Ladder, 1000.0f, 0.9f, 1000.0f);
            const float low = toneGain (choices::Ladder, 1000.0f, 0.9f, 150.0f);
            expectGreaterThan (atCut, low * 1.5f);
            expectLessThan (juce::Decibels::gainToDecibels (toneGain (choices::Ladder, 500.0f, 0.0f, 8000.0f)), -40.0f);
        }
        beginTest ("Formant vowels differ");
        {
            const float a = toneGain (choices::Formant, 1000.0f, 0.5f, 600.0f, 0.0f);   // A: F1 600 Hz
            const float i = toneGain (choices::Formant, 1000.0f, 0.5f, 600.0f, 0.5f);   // I: F1 250 Hz
            expectGreaterThan (a, i * 2.0f);
        }
        beginTest ("All types stable at max resonance and drive with modulated cutoff");
        for (int type = 0; type <= choices::Formant; ++type)
        {
            VoiceFilter f;
            f.prepare (44100.0);
            XorShift rng (42);
            float l[32], r[32];
            float maxAbs = 0.0f;
            bool finite = true;
            for (int blk = 0; blk < 4000; ++blk)
            {
                for (int i = 0; i < 32; ++i)
                    l[i] = r[i] = rng.nextBipolar() * 2.0f;
                const float cut = 20.0f * std::pow (1000.0f, 0.5f + 0.5f * std::sin ((float) blk * 0.05f));
                f.process (type, l, r, 32, cut, 1.0f, 1.0f, rng.next01());
                for (int i = 0; i < 32; ++i)
                {
                    finite = finite && std::isfinite (l[i]) && std::isfinite (r[i]);
                    maxAbs = std::max (maxAbs, std::abs (l[i]));
                }
            }
            expect (finite, "type " + juce::String (type));
            expectLessThan (maxAbs, 50.0f, "type " + juce::String (type));
        }
    }
};

struct EnvelopeTests final : juce::UnitTest
{
    EnvelopeTests() : juce::UnitTest ("Envelopes", "VOLT") {}

    void runTest() override
    {
        beginTest ("ADSR timing");
        Adsr env;
        const double sr = 48000.0;
        env.setSampleRate (sr);
        env.setParams (0.010f, 0.1f, 0.5f, 0.1f);
        env.noteOn();
        float lvl = 0.0f;
        for (int i = 0; i < 480; ++i)
            lvl = env.next();
        expectWithinAbsoluteError (lvl, 1.0f, 0.01f);
        for (int i = 0; i < 48000; ++i)
            lvl = env.next();
        expectWithinAbsoluteError (lvl, 0.5f, 0.01f);
        env.noteOff();
        for (int i = 0; i < 4800; ++i)
            lvl = env.next();
        expectWithinAbsoluteError (lvl, 0.005f, 0.002f); // -40 dB of 0.5 after release time
        for (int i = 0; i < 48000; ++i)
            env.next();
        expect (! env.isActive());

        beginTest ("Retrigger starts from current level (no click)");
        env.noteOn();
        for (int i = 0; i < 100; ++i)
            env.next();
        const float before = env.getLevel();
        env.noteOn();
        const float after = env.next();
        expectLessThan (std::abs (after - before), 0.01f);
    }
};

struct EngineTests final : juce::UnitTest
{
    EngineTests() : juce::UnitTest ("Engine", "VOLT") {}

    void runTest() override
    {
        beginTest ("Silence without notes");
        {
            SynthEngine e;
            e.prepare (44100.0, 256);
            auto r = renderNotes (e, defaults(), {}, 0.5);
            expectEquals (peak (r.L) + peak (r.R), 0.0f);
        }

        beginTest ("Default patch produces bounded audio and releases");
        {
            SynthEngine e;
            e.prepare (44100.0, 256);
            auto r = renderNotes (e, defaults(), { 60 }, 2.0, 0.5);
            expect (allFinite (r.L) && allFinite (r.R));
            expectGreaterThan (peak (r.L), 0.05f);
            expectLessThan (peak (r.L), 1.0f);
            expectEquals (e.getNumActiveVoices(), 0);
        }

        beginTest ("Polyphony limited to 16 voices");
        {
            SynthEngine e;
            e.prepare (44100.0, 256);
            renderNotes (e, defaults(), { 40, 42, 44, 46, 48, 50, 52, 54, 56, 58, 60, 62, 64, 66, 68, 70, 72, 74, 76, 78 }, 0.2);
            expectEquals (e.getNumActiveVoices(), 16);
        }

        beginTest ("Mono and Legato use one voice");
        for (int mode : { (int) choices::Mono, (int) choices::Legato })
        {
            SynthEngine e;
            e.prepare (44100.0, 256);
            auto p = defaults();
            p.v[VoiceMode] = (float) mode;
            renderNotes (e, p, { 48, 52, 55 }, 0.2);
            expectEquals (e.getNumActiveVoices(), 1);
        }

        beginTest ("High notes are free of strong aliasing");
        {
            SynthEngine e;
            const double sr = 44100.0;
            e.prepare (sr, 256);
            auto p = defaults();
            p.v[OscA_Level] = 0.5f;
            auto r = renderNotes (e, p, { 100 }, 1.0, -1.0, sr); // ~2637 Hz saw
            const int order = 14;
            auto mag = spectrum (r.L, 8192, order);
            const float binHz = (float) sr / (float) (1 << order);
            const float f0 = pitchToHz (100.0f);
            float fund = 0.0f, worstAlias = 0.0f;
            for (size_t b = 2; b < mag.size(); ++b)
            {
                const float f = (float) b * binHz;
                const float h = f / f0;
                const float dist = std::abs (h - std::round (h)) * f0;
                if (std::abs (f - f0) < 3.0f * binHz)
                    fund = std::max (fund, mag[b]);
                else if (dist > 6.0f * binHz && f > 30.0f)
                    worstAlias = std::max (worstAlias, mag[b]);
            }
            const float db = juce::Decibels::gainToDecibels (worstAlias / fund);
            logMessage ("worst alias component: " + juce::String (db, 1) + " dB");
            expectLessThan (db, -50.0f);
        }

        beginTest ("Random parameter fuzz stays finite");
        {
            juce::Random rnd (1234);
            for (int iter = 0; iter < 30; ++iter)
            {
                SynthEngine e;
                e.prepare (48000.0, 512);
                ParamSnapshot p = defaults();
                for (int k = 0; k < NumParams; ++k)
                {
                    const auto& s = spec (k);
                    float v = s.minValue + rnd.nextFloat() * (s.maxValue - s.minValue);
                    if (s.type != ParamType::Float)
                        v = std::round (v);
                    p.v[(size_t) k] = v;
                }
                p.v[OutGain] = 0.0f;
                auto r = renderNotes (e, p, { 36, 60, 67 }, 0.6, 0.3, 48000.0, 512);
                expect (allFinite (r.L) && allFinite (r.R), "iteration " + juce::String (iter));
            }
        }
    }
};

static WavetableTests wavetableTests;
static FilterTests filterTests;
static EnvelopeTests envelopeTests;
static EngineTests engineTests;
