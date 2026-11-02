#pragma once

#include "Voice.h"
#include "Arpeggiator.h"
#include "Effects.h"

#include <juce_audio_basics/juce_audio_basics.h>

namespace volt
{
struct TransportInfo
{
    double bpm = 120.0;
    double ppq = 0.0;      // quarter notes at the first sample of the block
    bool playing = false;
};

// Complete synth: MIDI handling, arpeggiator, voice allocation, modulation and the global FX chain.
// Real-time safe: no allocation, locks or I/O inside process().
class SynthEngine
{
public:
    SynthEngine();

    void prepare (double sampleRate, int maxBlockSize);
    void reset();

    void process (float* outL, float* outR, int numSamples, const juce::MidiBuffer& midi, const ParamSnapshot& params,
                  const TransportInfo& transport) noexcept;

    int getNumActiveVoices() const noexcept;
    float getLimiterReduction() const noexcept { return fx.getLimiterReductionDb(); }
    void resetLimiterMeter() noexcept { fx.resetLimiterMeter(); }
    int getNonFiniteCount() const noexcept { return fx.getNonFiniteCount(); }

private:
    void handleMidi (const juce::MidiMessage& m) noexcept;
    void midiNoteOn (int note, float velocity) noexcept;  // before the arpeggiator
    void midiNoteOff (int note) noexcept;
    void noteOn (int note, float velocity) noexcept;      // after the arpeggiator
    void noteOff (int note) noexcept;
    void allNotesOff (bool hard) noexcept;
    void beginChunk (int n) noexcept;
    void renderChunk (float* L, float* R, int n) noexcept;
    void computeGlobalMods (float* dst) const noexcept;

    double sampleRate = 44100.0;
    std::array<Voice, kMaxVoices> voices;
    VoiceContext ctx;
    ParamSnapshot raw;
    std::array<float, NumParams> sm {};
    std::vector<int> floatParams;   // indices of smoothable params (built in prepare)
    float smCutoffPitch = 135.0f;
    bool smInit = false;

    Lfo globalLfo[2];
    std::array<double, 16> lfoDivBeats {};
    std::array<double, 8> arpRateBeats {};
    std::array<double, 16> delayBeats {};
    std::array<double, 4> pumpBeats {};

    // Mono / legato note stack (most recent last).
    std::array<int, 32> stackNotes {};
    std::array<float, 32> stackVel {};
    int stackSize = 0;

    uint64_t ageCounter = 0;
    float modWheel = 0.0f, aftertouch = 0.0f;
    int lastMode = -1;
    float lastNotePitch = -1.0f;
    bool lastArpOn = false;

    TransportInfo transport;
    double chunkPpq = 0.0;
    double freePpq = 0.0; // free-running beat clock when the host is stopped

    Arpeggiator arp;
    FxChain fx;
};
} // namespace volt
