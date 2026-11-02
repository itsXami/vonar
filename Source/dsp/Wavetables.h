#pragma once

#include <juce_core/juce_core.h>
#include <array>
#include <vector>

namespace volt
{
constexpr int kWtFrames = 32;        // morph positions per table
constexpr int kWtMips = 10;          // band-limited copies, harmonic limit halves per level
constexpr int kWtMaxHarmonics = 512; // harmonics kept in mip 0

// One wavetable: kWtFrames single-cycle frames, each stored as kWtMips band-limited copies.
// Every stored cycle has one guard sample appended (copy of sample 0) for branch-free interpolation.
struct Wavetable
{
    juce::String name;
    std::array<int, kWtMips> sizes {};
    std::array<size_t, kWtMips> offsets {};
    std::vector<float> data;

    const float* cycle (int mip, int frame) const noexcept
    {
        return data.data() + offsets[(size_t) mip] + (size_t) frame * (size_t) (sizes[(size_t) mip] + 1);
    }

    static constexpr int harmonicLimit (int mip) noexcept { return kWtMaxHarmonics >> mip; }

    // Smallest mip whose highest harmonic stays below Nyquist for the given phase increment (cycles/sample).
    static int mipForIncrement (float inc) noexcept
    {
        int mip = 0;
        while (mip < kWtMips - 1 && (float) harmonicLimit (mip) * inc >= 0.5f)
            ++mip;
        return mip;
    }

    // Bilinear read: linear between samples and between neighbouring frames.
    inline float read (int mip, float framePos, float phase) const noexcept
    {
        const int size = sizes[(size_t) mip];
        const int f0 = juce::jlimit (0, kWtFrames - 1, (int) framePos);
        const int f1 = juce::jmin (f0 + 1, kWtFrames - 1);
        const float ff = framePos - (float) f0;
        const float* a = cycle (mip, f0);
        const float* b = cycle (mip, f1);
        const float idx = phase * (float) size;
        int i = (int) idx;
        if (i >= size) i = size - 1;
        if (i < 0) i = 0;
        const float fr = idx - (float) i;
        const float sa = a[i] + fr * (a[i + 1] - a[i]);
        const float sb = b[i] + fr * (b[i + 1] - b[i]);
        return sa + ff * (sb - sa);
    }
};

// All factory wavetables, generated procedurally once per process (thread-safe static init).
class WavetableBank
{
public:
    static const WavetableBank& get();

    int size() const noexcept { return (int) tables.size(); }
    const Wavetable& operator[] (int i) const noexcept { return tables[(size_t) juce::jlimit (0, size() - 1, i)]; }

private:
    WavetableBank();
    std::vector<Wavetable> tables;
};

const juce::StringArray& wavetableNames();
int wavetableIndex (const juce::String& name);
} // namespace volt
