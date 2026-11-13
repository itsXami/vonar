#pragma once

#include <juce_core/juce_core.h>
#include <juce_dsp/juce_dsp.h>
#include "Params.h"
#include "dsp/SynthEngine.h"

namespace volt::test
{
inline ParamSnapshot defaults()
{
    ParamSnapshot s;
    for (int p = 0; p < NumParams; ++p)
        s.v[(size_t) p] = spec (p).defaultValue;
    // Tests set an effect's mix / amount to use it: switch the classic effects on, so mix 0 = silent as before.
    for (int p : { FxDistOn, FxChorusOn, FxPhaserOn, FxFlangerOn, FxPumpOn, FxDelayOn, FxReverbOn, FxCompOn })
        s.v[(size_t) p] = 1.0f;
    s.v[ChoMix] = s.v[PhaMix] = s.v[FlaMix] = 0.0f;
    return s;
}

struct Rendered
{
    std::vector<float> L, R;
};

// Renders `seconds` of audio; noteOn at 0 for every note, noteOff at `releaseAt` seconds (if >= 0).
inline Rendered renderNotes (SynthEngine& e, const ParamSnapshot& p, std::initializer_list<int> notes, double seconds,
                             double releaseAt = -1.0, double sr = 44100.0, int block = 256, float vel = 0.8f)
{
    Rendered r;
    const int total = (int) (seconds * sr);
    r.L.assign ((size_t) total, 0.0f);
    r.R.assign ((size_t) total, 0.0f);
    const int offAt = releaseAt >= 0.0 ? (int) (releaseAt * sr) : -1;
    TransportInfo t;
    for (int pos = 0; pos < total; pos += block)
    {
        const int n = std::min (block, total - pos);
        juce::MidiBuffer midi;
        if (pos == 0)
            for (int nn : notes)
                midi.addEvent (juce::MidiMessage::noteOn (1, nn, vel), 0);
        if (offAt >= pos && offAt < pos + n)
            for (int nn : notes)
                midi.addEvent (juce::MidiMessage::noteOff (1, nn), offAt - pos);
        e.process (r.L.data() + pos, r.R.data() + pos, n, midi, p, t);
    }
    return r;
}

inline float rms (const float* x, int n)
{
    double s = 0.0;
    for (int i = 0; i < n; ++i)
        s += (double) x[i] * x[i];
    return n > 0 ? (float) std::sqrt (s / n) : 0.0f;
}

inline float peak (const std::vector<float>& x)
{
    float p = 0.0f;
    for (float v : x)
        p = std::max (p, std::abs (v));
    return p;
}

inline bool allFinite (const std::vector<float>& x)
{
    for (float v : x)
        if (! std::isfinite (v))
            return false;
    return true;
}

// Magnitude spectrum (Hann window) of 2^order samples starting at `start`.
inline std::vector<float> spectrum (const std::vector<float>& x, int start, int order)
{
    const int n = 1 << order;
    juce::dsp::FFT fft (order);
    std::vector<float> buf ((size_t) n * 2, 0.0f);
    for (int i = 0; i < n; ++i)
    {
        const float w = 0.5f - 0.5f * std::cos (6.2831853f * (float) i / (float) (n - 1));
        buf[(size_t) i] = x[(size_t) (start + i)] * w;
    }
    fft.performFrequencyOnlyForwardTransform (buf.data());
    buf.resize ((size_t) n / 2);
    return buf;
}
} // namespace volt::test
