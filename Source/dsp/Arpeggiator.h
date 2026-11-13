#pragma once

#include "DspUtil.h"
#include "../Params.h"

#include <array>
#include <cmath>
#include <limits>

namespace volt
{
// Tempo-synced arpeggiator (Up, Down, UpDown, Random; 1-4 octaves; gate).
// The engine calls tick() at every render position; tick() fires due events and reports how many samples
// remain until the next one, so steps and gate-offs land sample-accurately.
class Arpeggiator
{
public:
    static constexpr int kMaxHeld = 32;

    void prepare (double sr) noexcept { sampleRate = sr; reset(); }

    void reset() noexcept
    {
        numHeld = 0;
        playing = -1;
        lastStep = std::numeric_limits<long long>::min();
        patternPos = -1;
        pendingStart = false;
    }

    bool hasHeldNotes() const noexcept { return numHeld > 0; }
    int getPlayingNote() const noexcept { return playing; }

    void noteOn (int note, float vel) noexcept
    {
        for (int i = 0; i < numHeld; ++i)
            if (held[(size_t) i] == note)
                return;
        if (numHeld >= kMaxHeld)
            return;
        int pos = numHeld;
        while (pos > 0 && held[(size_t) pos - 1] > note) // keep sorted ascending
        {
            held[(size_t) pos] = held[(size_t) pos - 1];
            heldVel[(size_t) pos] = heldVel[(size_t) pos - 1];
            --pos;
        }
        held[(size_t) pos] = note;
        heldVel[(size_t) pos] = vel;
        if (numHeld == 0)
        {
            pendingStart = true;
            patternPos = -1;
        }
        ++numHeld;
    }

    void noteOff (int note) noexcept
    {
        for (int i = 0; i < numHeld; ++i)
            if (held[(size_t) i] == note)
            {
                for (int j = i; j < numHeld - 1; ++j)
                {
                    held[(size_t) j] = held[(size_t) j + 1];
                    heldVel[(size_t) j] = heldVel[(size_t) j + 1];
                }
                --numHeld;
                return;
            }
    }

    // beat: position in quarter notes at this sample; beatsPerSample: tempo; returns samples until next event.
    // When the host transport is stopped (synced == false) the grid is anchored at the first key press.
    template <typename OnFn, typename OffFn>
    int tick (double hostBeat, bool synced, double beatsPerSample, double stepBeats, int mode, int octaves, float gate, OnFn&& on, OffFn&& off) noexcept
    {
        if (numHeld == 0)
        {
            if (playing >= 0) { off (playing); playing = -1; }
            lastStep = std::numeric_limits<long long>::min();
            return std::numeric_limits<int>::max();
        }

        stepBeats = std::max (stepBeats, 1.0e-3);
        if (pendingStart && ! synced)
            anchor = hostBeat;
        const double beat = synced ? hostBeat : hostBeat - anchor;
        const long long idx = (long long) std::floor (beat / stepBeats + 1.0e-9);
        if (pendingStart || idx != lastStep)
        {
            if (playing >= 0) { off (playing); playing = -1; }
            const int n = nextNote (mode, octaves);
            on (n, currentVel);
            playing = n;
            stepStartBeat = beat;
            lastStep = idx;
            pendingStart = false;
        }

        const double gateEnd = stepStartBeat + juce::jlimit (0.05, 1.0, (double) gate) * stepBeats;
        if (playing >= 0 && gate < 0.999f && beat >= gateEnd - 1.0e-9)
        {
            off (playing);
            playing = -1;
        }

        const double nextBoundary = (double) (idx + 1) * stepBeats;
        double untilBeats = nextBoundary - beat;
        if (playing >= 0 && gate < 0.999f)
            untilBeats = std::min (untilBeats, gateEnd - beat);
        const double samples = std::ceil (untilBeats / std::max (beatsPerSample, 1.0e-12));
        return (int) juce::jlimit (1.0, 1.0e9, samples);
    }

private:
    int nextNote (int mode, int octaves) noexcept
    {
        octaves = juce::jlimit (1, 4, octaves);
        const int len = numHeld * octaves;
        int index = 0;
        switch (mode)
        {
            case choices::Down:
                patternPos = (patternPos + 1) % len;
                index = len - 1 - patternPos;
                break;
            case choices::UpDown:
            {
                const int cycle = len > 1 ? 2 * (len - 1) : 1;
                patternPos = (patternPos + 1) % cycle;
                index = patternPos < len ? patternPos : cycle - patternPos;
                break;
            }
            case choices::Random:
                index = (int) (rng.next01() * (float) len) % len;
                break;
            case choices::Up:
            default:
                patternPos = (patternPos + 1) % len;
                index = patternPos;
                break;
        }
        const int noteIdx = index % numHeld;
        const int oct = index / numHeld;
        currentVel = heldVel[(size_t) noteIdx];
        return juce::jlimit (0, 127, held[(size_t) noteIdx] + 12 * oct);
    }

    double sampleRate = 44100.0;
    std::array<int, kMaxHeld> held {};
    std::array<float, kMaxHeld> heldVel {};
    int numHeld = 0;
    int playing = -1;
    int patternPos = -1;
    float currentVel = 0.8f;
    long long lastStep = 0;
    double stepStartBeat = 0.0;
    double anchor = 0.0;
    bool pendingStart = false;
    XorShift rng { 0xA5A5u };
};
} // namespace volt
