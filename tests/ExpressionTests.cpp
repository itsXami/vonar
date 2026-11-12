#include "TestHelpers.h"

using namespace volt;
using namespace volt::test;

namespace
{
// Renders blocks of `block` samples, sending the given events at the start of the listed blocks.
struct Script
{
    SynthEngine& e;
    const ParamSnapshot& p;
    double sr;
    std::vector<float> L, R;

    void run (int blocks, const std::function<void (int, juce::MidiBuffer&)>& events, int block = 256)
    {
        TransportInfo t;
        for (int b = 0; b < blocks; ++b)
        {
            juce::MidiBuffer midi;
            events (b, midi);
            const size_t at = L.size();
            L.resize (at + (size_t) block);
            R.resize (at + (size_t) block);
            e.process (L.data() + at, R.data() + at, block, midi, p, t);
        }
    }
};

// Zero crossings per second of a pure sine -> frequency.
float sineFrequency (const std::vector<float>& x, size_t start, size_t len, double sr)
{
    int crossings = 0;
    for (size_t i = start + 1; i < start + len; ++i)
        crossings += (x[i - 1] <= 0.0f && x[i] > 0.0f) ? 1 : 0;
    return (float) (crossings * sr / (double) len);
}

ParamSnapshot sinePatch()
{
    auto p = defaults();
    p.v[OscA_Table] = 0.0f;   // Basic Shapes, frame 0 = sine
    p.v[OscA_Pos] = 0.0f;
    p.v[FltCutoff] = 20000.0f;
    p.v[AmpR] = 0.01f;
    return p;
}
} // namespace

struct ExpressionTests final : juce::UnitTest
{
    ExpressionTests() : juce::UnitTest ("Pitch bend and sustain", "VOLT") {}

    void runTest() override
    {
        const double sr = 48000.0;

        beginTest ("Pitch wheel bends by the bend range, centre returns to the note");
        {
            auto p = sinePatch();
            p.v[BendRange] = 2.0f;
            SynthEngine e;
            e.prepare (sr, 256);
            Script s { e, p, sr };
            s.run (380, [] (int b, juce::MidiBuffer& m) {
                if (b == 0) m.addEvent (juce::MidiMessage::noteOn (1, 69, 0.8f), 0);
                if (b == 120) m.addEvent (juce::MidiMessage::pitchWheel (1, 16383), 0);
                if (b == 250) m.addEvent (juce::MidiMessage::pitchWheel (1, 8192), 0);
            });
            const size_t len = 48000 / 2;
            const float f0 = sineFrequency (s.L, 256 * 40, len / 2, sr);
            const float up = sineFrequency (s.L, 256 * 140, len / 2, sr);
            const float back = sineFrequency (s.L, 256 * 270, len / 2, sr);
            const float expectedUp = 440.0f * std::pow (2.0f, (2.0f * 8191.0f / 8192.0f) / 12.0f);
            expectWithinAbsoluteError (f0, 440.0f, 6.0f);
            expectWithinAbsoluteError (up, expectedUp, 6.0f);
            expectWithinAbsoluteError (back, 440.0f, 6.0f);
        }

        beginTest ("Bend range 12 bends down an octave");
        {
            auto p = sinePatch();
            p.v[BendRange] = 12.0f;
            SynthEngine e;
            e.prepare (sr, 256);
            Script s { e, p, sr };
            s.run (200, [] (int b, juce::MidiBuffer& m) {
                if (b == 0) m.addEvent (juce::MidiMessage::noteOn (1, 69, 0.8f), 0);
                if (b == 10) m.addEvent (juce::MidiMessage::pitchWheel (1, 0), 0);
            });
            expectWithinAbsoluteError (sineFrequency (s.L, 256 * 60, 24000, sr), 220.0f, 5.0f);
        }

        beginTest ("Sustain pedal holds released notes until it is lifted");
        {
            auto p = sinePatch();
            SynthEngine e;
            e.prepare (sr, 256);
            Script s { e, p, sr };
            int duringPedal = -1, afterLift = -1;
            s.run (200, [&] (int b, juce::MidiBuffer& m) {
                if (b == 0)
                {
                    m.addEvent (juce::MidiMessage::controllerEvent (1, 64, 127), 0);
                    m.addEvent (juce::MidiMessage::noteOn (1, 60, 0.8f), 0);
                    m.addEvent (juce::MidiMessage::noteOn (1, 64, 0.8f), 0);
                }
                if (b == 20) m.addEvent (juce::MidiMessage::noteOff (1, 60), 0);
                if (b == 21) m.addEvent (juce::MidiMessage::noteOff (1, 64), 0);
                if (b == 100) duringPedal = e.getNumActiveVoices();
                if (b == 101) m.addEvent (juce::MidiMessage::controllerEvent (1, 64, 0), 0);
                if (b == 199) afterLift = e.getNumActiveVoices();
            });
            expectEquals (duringPedal, 2);
            expectEquals (afterLift, 0);
            expectGreaterThan (rms (s.L.data() + 256 * 90, 256 * 10), 0.01f);
            expectLessThan (rms (s.L.data() + 256 * 190, 256 * 9), 1.0e-4f);
        }

        beginTest ("A key still held when the pedal is lifted keeps sounding");
        {
            auto p = sinePatch();
            SynthEngine e;
            e.prepare (sr, 256);
            Script s { e, p, sr };
            int afterLift = -1;
            s.run (150, [&] (int b, juce::MidiBuffer& m) {
                if (b == 0) m.addEvent (juce::MidiMessage::controllerEvent (1, 64, 127), 0);
                if (b == 1) m.addEvent (juce::MidiMessage::noteOn (1, 60, 0.8f), 0);
                if (b == 10) m.addEvent (juce::MidiMessage::noteOff (1, 60), 0);
                if (b == 20) m.addEvent (juce::MidiMessage::noteOn (1, 60, 0.8f), 0);   // pressed again
                if (b == 40) m.addEvent (juce::MidiMessage::controllerEvent (1, 64, 0), 0);
                if (b == 149) afterLift = e.getNumActiveVoices();
            });
            expectEquals (afterLift, 1);
        }

        beginTest ("Sustain with the arpeggiator keeps the pattern running");
        {
            auto p = sinePatch();
            p.v[ArpOn] = 1.0f;
            SynthEngine e;
            e.prepare (sr, 256);
            Script s { e, p, sr };
            s.run (300, [] (int b, juce::MidiBuffer& m) {
                if (b == 0)
                {
                    m.addEvent (juce::MidiMessage::controllerEvent (1, 64, 127), 0);
                    m.addEvent (juce::MidiMessage::noteOn (1, 60, 0.8f), 0);
                    m.addEvent (juce::MidiMessage::noteOn (1, 67, 0.8f), 0);
                }
                if (b == 10)
                {
                    m.addEvent (juce::MidiMessage::noteOff (1, 60), 0);
                    m.addEvent (juce::MidiMessage::noteOff (1, 67), 0);
                }
            });
            expectGreaterThan (rms (s.L.data() + 256 * 200, 256 * 90), 0.01f);
        }

        beginTest ("All Notes Off clears sustained notes");
        {
            auto p = sinePatch();
            SynthEngine e;
            e.prepare (sr, 256);
            Script s { e, p, sr };
            int after = -1;
            s.run (120, [&] (int b, juce::MidiBuffer& m) {
                if (b == 0)
                {
                    m.addEvent (juce::MidiMessage::controllerEvent (1, 64, 127), 0);
                    m.addEvent (juce::MidiMessage::noteOn (1, 60, 0.8f), 0);
                }
                if (b == 5) m.addEvent (juce::MidiMessage::noteOff (1, 60), 0);
                if (b == 10) m.addEvent (juce::MidiMessage::allNotesOff (1), 0);
                if (b == 119) after = e.getNumActiveVoices();
            });
            expectEquals (after, 0);
        }
    }
};

static ExpressionTests expressionTests;
