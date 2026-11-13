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
    // Effect chain order (message thread writes, audio thread reads; 4 bits per slot).
    void setFxOrder (const fx::Order& o) noexcept
    {
        uint64_t packed = 0;
        for (int i = 0; i < fx::NumEffects; ++i)
            packed |= (uint64_t) (o[(size_t) i] & 0xF) << (4 * i);
        fxOrderPacked.store (packed, std::memory_order_relaxed);
    }
    int getNonFiniteCount() const noexcept { return fx.getNonFiniteCount(); }

private:
    void handleMidi (const juce::MidiMessage& m) noexcept;
    void midiNoteOn (int note, float velocity) noexcept;  // before the arpeggiator
    void midiNoteOff (int note) noexcept;
    void noteOn (int note, float velocity) noexcept;      // after the arpeggiator
    void noteOff (int note) noexcept;
    void allNotesOff (bool hard) noexcept;
    void setSustain (bool down) noexcept;
    void beginChunk (int n) noexcept;
    void renderChunk (float* L, float* R, int n) noexcept;
public:
    bool isIdleAsleep() const noexcept { return fxAsleep; }
private:
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
    float pitchWheel = 0.0f;   // -1..1 from the MIDI pitch wheel
    float bendSmooth = 0.0f;   // semitones, smoothed per chunk

    // Sustain pedal (CC64): keys released while the pedal is down keep sounding until it is lifted.
    bool sustainDown = false;
    std::array<bool, 128> keyHeld {};
    std::array<bool, 128> keySustained {};
    int lastMode = -1;
    float lastNotePitch = -1.0f;
    bool lastArpOn = false;

    TransportInfo transport;
    double chunkPpq = 0.0;
    double freePpq = 0.0; // free-running beat clock when the host is stopped
    // Idle sleep: with no voice sounding and the effects' output below -100 dB for longer than the delay could
    // still answer, the effect chain is skipped (an idle instance in a project costs almost nothing).
    std::atomic<uint64_t> fxOrderPacked { 0xFEDCBA9876543210ull & 0xFFFFFFFFFFull };
    int fxSilentSamples = 0;
    bool fxAsleep = false;

    Arpeggiator arp;
    FxChain fx;
};
} // namespace volt
