#include "TestHelpers.h"
#include "dsp/Effects.h"
#include "PluginProcessor.h"
#include "PluginEditor.h"

using namespace volt;
using namespace volt::test;
using namespace volt::ui;

namespace
{
// Test tone; the length is rounded up to whole 256-sample blocks so runChain processes every sample.
std::vector<float> sine (float hz, float amp, int n, double sr)
{
    n = (n + 255) / 256 * 256;
    std::vector<float> x ((size_t) n);
    for (int i = 0; i < n; ++i)
        x[(size_t) i] = amp * (float) std::sin (juce::MathConstants<double>::twoPi * hz * i / sr);
    return x;
}

// Runs the chain in 256-sample blocks on a copy of `in` (both channels) and returns the left channel.
std::vector<float> runChain (FxChain& fx, const std::vector<float>& in, const FxParams& p)
{
    std::vector<float> l = in, r = in;
    for (size_t pos = 0; pos + 256 <= l.size(); pos += 256)
        fx.process (l.data() + pos, r.data() + pos, 256, p);
    return l;
}

FxParams silentChain()
{
    FxParams p;
    p.distMix = p.choMix = p.phaMix = p.flaMix = p.fxfMix = p.dlyMix = p.revMix = p.squash = p.pumpAmount = 0.0f;
    p.eqOn = p.compOn = false;
    return p;
}

float rmsDb (const std::vector<float>& x, size_t from)
{
    return juce::Decibels::gainToDecibels (rms (x.data() + from, (int) (x.size() - from)), -150.0f);
}

void setRaw (juce::AudioProcessorValueTreeState& s, int param, float v)
{
    auto* p = dynamic_cast<juce::RangedAudioParameter*> (s.getParameter (spec (param).id));
    p->setValueNotifyingHost (p->convertTo0to1 (v));
}

float raw (juce::AudioProcessorValueTreeState& s, int param) { return s.getRawParameterValue (spec (param).id)->load(); }
} // namespace

struct RackTests final : juce::UnitTest
{
    RackTests() : juce::UnitTest ("Effects rack", "VOLT") {}

    void runTest() override
    {
        const double sr = 48000.0;

        beginTest ("Effect order: names round-trip, missing or unknown entries fall back to the default order");
        {
            fx::Order o { fx::Reverb, fx::Delay, fx::Distortion, fx::Chorus, fx::Phaser, fx::Flanger, fx::Filter, fx::Eq, fx::Pump, fx::Compressor };
            expect (fx::orderFromString (fx::orderToString (o)) == o);
            expect (fx::orderFromString ("") == fx::defaultOrder());
            const auto partial = fx::orderFromString ("reverb, nonsense, delay, reverb");
            expectEquals (partial[0], (int) fx::Reverb);
            expectEquals (partial[1], (int) fx::Delay);
            expectEquals (partial[2], (int) fx::Distortion);   // the rest in default order
            std::array<bool, fx::NumEffects> seen {};
            for (int e : partial) seen[(size_t) e] = true;
            for (bool b : seen) expect (b, "every effect appears once");
        }

        beginTest ("Chain order changes the sound (distortion before vs after the filter)");
        {
            auto in = sine (110.0f, 0.5f, 48000, sr);
            FxParams p = silentChain();
            p.distMix = 1.0f; p.distDrive = 1.0f; p.distType = choices::Hard;
            p.fxfMix = 1.0f; p.fxfCutoff = 300.0f; p.fxfType = choices::FxLowPass;
            FxChain a, b;
            a.prepare (sr, 256); b.prepare (sr, 256);
            const auto first = runChain (a, in, p);   // default: distortion, then filter
            p.order = fx::orderFromString ("filter,distortion");
            const auto second = runChain (b, in, p);
            // Distortion after the low-pass adds bright harmonics again: more energy above 1 kHz.
            auto hf = [&] (const std::vector<float>& x) {
                auto mag = spectrum (x, 24000, 14);
                double e = 0.0;
                for (size_t k = (size_t) (1000.0 * 16384 / sr); k < mag.size(); ++k) e += (double) mag[k] * mag[k];
                return e;
            };
            expectGreaterThan (hf (second), hf (first) * 10.0, "filter -> distortion is brighter than distortion -> filter");
        }

        beginTest ("EQ: flat bands pass the signal unchanged, a +6 dB peak lifts its frequency by 6 dB");
        {
            auto in = sine (1000.0f, 0.25f, 48000, sr);
            FxParams p = silentChain();
            p.eqOn = true;
            FxChain flat;
            flat.prepare (sr, 256);
            const auto out = runChain (flat, in, p);
            float maxDiff = 0.0f;
            for (size_t i = 0; i < in.size(); ++i) maxDiff = std::max (maxDiff, std::abs (out[i] - in[i]));
            expectLessThan (maxDiff, 1.0e-6f, "all gains at 0 dB = bypass");
            p.eqMidFreq = 1000.0f; p.eqMidGain = 6.0f; p.eqMidQ = 1.0f;
            FxChain peaked;
            peaked.prepare (sr, 256);
            const auto lifted = runChain (peaked, in, p);
            expectWithinAbsoluteError (rmsDb (lifted, 24000) - rmsDb (in, 24000), 6.0f, 0.3f);
            expectWithinAbsoluteError (EqFx::responseDb (p, sr, 1000.0f), 6.0f, 0.05f, "graph matches the sound");
        }

        beginTest ("Filter effect on its own: 12 dB/oct low-pass, 5 kHz tone 3.3 octaves above 500 Hz is ~40 dB down");
        {
            auto l = sine (5000.0f, 0.25f, 48000, sr), r = l;
            FilterFx f;
            f.prepare (sr);
            for (size_t pos = 0; pos < l.size(); pos += 256)
                f.process (l.data() + pos, r.data() + pos, 256, choices::FxLowPass, 500.0f, 0.0f, 1.0f);
            logMessage ("filter alone: " + juce::String (rmsDb (l, 24000) - rmsDb (sine (5000.0f, 0.25f, 48000, sr), 24000), 1) + " dB");
            expectLessThan (rmsDb (l, 24000) - rmsDb (sine (5000.0f, 0.25f, 48000, sr), 24000), -36.0f);
        }

        beginTest ("Filter effect: low-pass at 500 Hz cuts a 5 kHz tone, mix 0 leaves it alone");
        {
            auto in = sine (5000.0f, 0.25f, 48000, sr);
            FxParams p = silentChain();
            p.fxfMix = 1.0f; p.fxfCutoff = 500.0f; p.fxfRes = 0.0f; p.fxfType = choices::FxLowPass;
            FxChain f;
            f.prepare (sr, 256);
            expectLessThan (rmsDb (runChain (f, in, p), 24000) - rmsDb (in, 24000), -30.0f);
            p.fxfType = choices::FxHighPass;
            FxChain h;
            h.prepare (sr, 256);
            expectWithinAbsoluteError (rmsDb (runChain (h, in, p), 24000) - rmsDb (in, 24000), 0.0f, 0.5f, "high-pass keeps it");
        }

        beginTest ("Compressor: threshold -20 dB, ratio 4:1 turns a 0 dBFS tone into about -15 dBFS; 1:1 = bypass");
        {
            auto in = sine (200.0f, 1.0f, 48000, sr);
            FxParams p = silentChain();
            p.compOn = true; p.compThreshold = -20.0f; p.compRatio = 4.0f; p.compAttack = 0.002f; p.compRelease = 0.1f;
            FxChain c;
            c.prepare (sr, 256);
            const auto out = runChain (c, in, p);
            float pk = 0.0f;
            for (size_t i = 24000; i < out.size(); ++i) pk = std::max (pk, std::abs (out[i]));
            expectWithinAbsoluteError (juce::Decibels::gainToDecibels (pk), -15.0f, 1.5f);
            p.compRatio = 1.0f;
            FxChain b;
            b.prepare (sr, 256);
            const auto same = runChain (b, sine (200.0f, 0.5f, 48000, sr), p);
            expectWithinAbsoluteError (rmsDb (same, 1000), rmsDb (sine (200.0f, 0.5f, 48000, sr), 1000), 0.01f);
        }

        beginTest ("Reverb tone: open cuts change nothing, a 2 kHz high cut darkens the tail");
        {
            std::vector<float> in (96000 + 256, 0.0f);
            juce::Random rnd (3);
            for (int i = 0; i < 4800; ++i) in[(size_t) i] = rnd.nextFloat() * 0.5f - 0.25f;
            FxParams p = silentChain();
            p.revMix = 1.0f;
            FxChain a, b, c;
            a.prepare (sr, 256); b.prepare (sr, 256); c.prepare (sr, 256);
            const auto plain = runChain (a, in, p);
            p.revLowCut = 20.0f; p.revHighCut = 20000.0f;
            const auto open = runChain (b, in, p);
            float d = 0.0f;
            for (size_t i = 0; i < plain.size(); ++i) d = std::max (d, std::abs (plain[i] - open[i]));
            expectEquals (d, 0.0f, "default cut-offs are bypassed exactly");
            p.revHighCut = 2000.0f;
            const auto dark = runChain (c, in, p);
            auto centroid = [&] (const std::vector<float>& x) {
                auto mag = spectrum (x, 12000, 14);
                double num = 0.0, den = 0.0;
                for (size_t k = 1; k < mag.size(); ++k) { num += (double) k * mag[k]; den += mag[k]; }
                return num / den * sr / 16384.0;
            };
            expectLessThan (centroid (dark), centroid (plain) * 0.6, "tail centroid drops");
        }

        beginTest ("Switching an effect off silences it even with its mix up");
        {
            auto p = defaults();
            p.v[DistMix] = 1.0f; p.v[DistDrive] = 1.0f; p.v[DistType] = (float) choices::Hard;
            p.v[OscA_Table] = 0.0f;   // sine: harmonics only come from the distortion
            p.v[OscA_Pos] = 0.0f;
            SynthEngine on, off;
            on.prepare (sr, 256); off.prepare (sr, 256);
            const auto loud = renderNotes (on, p, { 57 }, 0.5, -1.0, sr);
            p.v[FxDistOn] = 0.0f;
            const auto clean = renderNotes (off, p, { 57 }, 0.5, -1.0, sr);
            auto harmonics = [&] (const std::vector<float>& x) {
                auto mag = spectrum (x, 8192, 14);
                double e = 0.0;
                for (size_t k = (size_t) (1500.0 * 16384 / sr); k < mag.size(); ++k) e += (double) mag[k] * mag[k];
                return e;
            };
            expectGreaterThan (harmonics (loud.L), harmonics (clean.L) * 100.0);
        }

        beginTest ("Old presets (version 1) are migrated; new ones (version 2) are never touched");
        {
            VoltAudioProcessor proc;
            auto& pm = proc.getPresetManager();
            PresetInfo legacy;
            juce::StringArray errors;
            PresetManager::parsePreset (R"({"name":"Old","category":"Pad","tags":["x"],"description":"Old preset.","version":1,
                "params":{"mfx_type":"Phaser","mfx_rate":1.5,"mfx_depth":0.8,"mfx_mix":0.4,"rev_mix":0.2,
                          "mod1_src":"Macro 1","mod1_dst":"Delay Mix","mod1_amt":0.5}})", legacy, errors);
            expect (errors.isEmpty(), errors.joinIntoString ("; "));
            pm.applyPreset (legacy);
            auto& s = proc.apvts;
            expectEquals (raw (s, FxPhaserOn), 1.0f, "phaser switched on");
            expectEquals (raw (s, FxChorusOn), 0.0f);
            expectWithinAbsoluteError (raw (s, PhaRate), 1.5f, 1.0e-4f);
            expectWithinAbsoluteError (raw (s, PhaDepth), 0.8f, 1.0e-4f);
            expectWithinAbsoluteError (raw (s, PhaMix), 0.4f, 1.0e-4f);
            expectEquals (raw (s, FxReverbOn), 1.0f, "reverb with mix > 0 is on");
            expectEquals (raw (s, FxDelayOn), 1.0f, "delay moved by a macro is on");
            expectEquals (raw (s, FxDistOn), 0.0f, "unused distortion stays off");
            expectEquals (raw (s, FxCompOn), 0.0f);

            // Regression (found 2026-11-13): a new preset whose distortion is off has no "fx_dist_on" key;
            // it must not be mistaken for an old one.
            PresetInfo modern;
            PresetManager::parsePreset (R"({"name":"New","category":"Pad","tags":["x"],"description":"New preset.","version":2,
                "params":{"fx_chorus_on":true,"chorus_mix":0.55,"chorus_rate":0.25}})", modern, errors);
            pm.applyPreset (modern);
            expectEquals (raw (s, FxChorusOn), 1.0f, "chorus stays on");
            expectWithinAbsoluteError (raw (s, ChoMix), 0.55f, 1.0e-4f);
        }

        beginTest ("Projects saved before the effects rack are migrated on load; the order is saved with the project");
        {
            VoltAudioProcessor a;
            setRaw (a.apvts, FxReverbOn, 1.0f);
            setRaw (a.apvts, RevMix, 0.3f);
            PresetManager::setFxOrder (a.apvts, fx::orderFromString ("reverb,delay"));
            juce::MemoryBlock blob;
            a.getStateInformation (blob);
            VoltAudioProcessor b;
            b.setStateInformation (blob.getData(), (int) blob.getSize());
            expectEquals (PresetManager::getFxOrder (b.apvts)[0], (int) fx::Reverb, "order restored");
            expectEquals (raw (b.apvts, FxReverbOn), 1.0f);

            // Remove the new parameters to fake an old project: Mod FX chorus at 50 %, delay at 20 %.
            auto xml = a.apvts.copyState().createXml();
            for (auto* c = xml->getFirstChildElement(); c != nullptr;)
            {
                auto* next = c->getNextElement();
                const auto id = c->getStringAttribute ("id");
                if (id.startsWith ("fx_") || id.startsWith ("chorus_"))
                    xml->removeChildElement (c, true);
                else if (id == "mfx_mix") c->setAttribute ("value", 0.5);
                else if (id == "dly_mix") c->setAttribute ("value", 0.2);
                c = next;
            }
            xml->removeAttribute (PresetManager::kFxOrderProp);
            juce::MemoryBlock old;
            juce::AudioProcessor::copyXmlToBinary (*xml, old);
            VoltAudioProcessor c;
            c.setStateInformation (old.getData(), (int) old.getSize());
            expectEquals (raw (c.apvts, FxChorusOn), 1.0f, "old Mod FX became the chorus");
            expectWithinAbsoluteError (raw (c.apvts, ChoMix), 0.5f, 1.0e-4f);
            expectEquals (raw (c.apvts, FxDelayOn), 1.0f);
            expect (PresetManager::getFxOrder (c.apvts) == fx::defaultOrder());
        }

        beginTest ("User presets keep the effect order");
        {
            VoltAudioProcessor a;
            PresetManager::setFxOrder (a.apvts, fx::orderFromString ("compressor,reverb"));
            const auto json = juce::JSON::toString (a.getPresetManager().currentStateToJson ("Order Test", "Pad", { "Test" }, "Test."));
            PresetInfo info;
            juce::StringArray errors;
            PresetManager::parsePreset (json, info, errors);
            VoltAudioProcessor b;
            b.getPresetManager().applyPreset (info);
            const auto o = PresetManager::getFxOrder (b.apvts);
            expectEquals (o[0], (int) fx::Compressor);
            expectEquals (o[1], (int) fx::Reverb);
        }

        // Interface: needs a display on Linux (CI runs the tests under xvfb).
        if (juce::SystemStats::getEnvironmentVariable ("DISPLAY", {}).isEmpty() && (juce::SystemStats::getOperatingSystemType() & juce::SystemStats::Linux) != 0)
        {
            logMessage ("no display: interface tests skipped");
            return;
        }
        juce::ScopedJuceInitialiser_GUI gui;

        beginTest ("Interface: dragging the EQ mid point sets frequency and gain; the dot switches; the grip reorders");
        {
            VoltAudioProcessor proc;
            std::unique_ptr<juce::AudioProcessorEditor> ed (proc.createEditor());
            auto* ve = dynamic_cast<VoltAudioProcessorEditor*> (ed.get());
            expect (ve != nullptr);
            auto* rack = ve->getPanel().getFxRack();
            expect (rack != nullptr);
            auto& s = proc.apvts;

            rack->toggle (fx::Eq);
            expectEquals (raw (s, FxEqOn), 1.0f, "clicking the dot switches the EQ on");
            rack->refresh();
            FxPanel* eq = nullptr;
            for (auto* p : rack->panels())
                if (p->effect == fx::Eq) eq = p;
            expect (eq != nullptr && eq->isVisible() && eq->graph.isVisible());
            auto& g = eq->graph;
            const auto handles = g.handles();
            expectEquals ((int) handles.size(), 3);
            const auto area = g.getLocalBounds().toFloat().reduced (8.0f);
            // Mid point to 2 kHz and +9 dB (y: +18 at the top, -18 at the bottom).
            const float x2k = area.getX() + area.getWidth() * std::log (2000.0f / 20.0f) / std::log (1000.0f);
            g.dragHandleTo (1, { x2k, area.getY() + area.getHeight() * (18.0f - 9.0f) / 36.0f });
            expectWithinAbsoluteError (raw (s, EqMidFreq), 2000.0f, 30.0f);
            expectWithinAbsoluteError (raw (s, EqMidGain), 9.0f, 0.2f);
            const auto pos = g.handlePosition (1);
            expectWithinAbsoluteError (pos.x, x2k, 1.0f, "the point is drawn where it was dropped");

            // The filter point: right = higher cutoff.
            rack->toggle (fx::Filter);
            rack->refresh();
            for (auto* p : rack->panels())
                if (p->effect == fx::Filter)
                {
                    const float before = raw (s, FxfCutoff);
                    const auto hp = p->graph.handlePosition (0);
                    p->graph.dragHandleTo (0, hp.translated (60.0f, 0.0f));
                    expectGreaterThan (raw (s, FxfCutoff), before * 1.5f);
                }

            // Drag the reverb row to the top of the list.
            rack->dragRow (fx::Reverb, 30);
            expectEquals (rack->order()[0], (int) fx::Reverb);
            expectEquals (PresetManager::getFxOrder (s)[0], (int) fx::Reverb, "order stored in the state");
            ve->getPanel().setTab (volt::ui::MainPanel::FxTab);
            ve->getPanel().refresh();
        }
    }
};

static RackTests rackTests;
