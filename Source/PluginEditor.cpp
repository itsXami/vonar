#include "PluginEditor.h"

namespace volt::ui
{
using R = juce::Rectangle<int>;

Knob& MainPanel::knob (int param, const juce::String& caption, R r, bool big)
{
    auto k = std::make_unique<Knob> (state, param, caption, big);
    k->setBounds (r);
    addAndMakeVisible (*k);
    auto& ref = *k;
    owned.push_back (std::move (k));
    return ref;
}

ParamCombo& MainPanel::combo (int param, R r)
{
    auto c = std::make_unique<ParamCombo> (state, param);
    c->setBounds (r);
    addAndMakeVisible (*c);
    auto& ref = *c;
    owned.push_back (std::move (c));
    return ref;
}

ParamToggle& MainPanel::toggle (int param, const juce::String& text, R r)
{
    auto t = std::make_unique<ParamToggle> (state, param, text);
    t->setBounds (r);
    addAndMakeVisible (*t);
    auto& ref = *t;
    owned.push_back (std::move (t));
    return ref;
}

void MainPanel::buildOsc (int o, R r)
{
    const int b = OscA_Table + o * kOscParamCount;
    section (o == 0 ? "OSC A" : "OSC B", r);
    combo (b + 0, { r.getX() + 64, r.getY() + 3, r.getWidth() - 70, 18 }).setTooltip ("Wavetable");
    wtView[o] = std::make_unique<WavetableView> (state, o);
    wtView[o]->setBounds (r.getX() + 8, r.getY() + 26, r.getWidth() - 16, 60);
    addAndMakeVisible (*wtView[o]);
    const int y0 = r.getY() + 92;
    knob (b + 1, o == 0 ? "WAVETABLE A" : "WAVETABLE B", { r.getX() + 4, y0, 74, 88 }, true);
    const int gx = r.getX() + 82, cw = 50, ch = 44;
    knob (b + 2, "OCT", { gx, y0, cw, ch });
    knob (b + 3, "SEMI", { gx + cw, y0, cw, ch });
    knob (b + 4, "FINE", { gx + 2 * cw, y0, cw, ch });
    knob (b + 5, "LEVEL", { gx, y0 + ch, cw, ch });
    knob (b + 6, "PAN", { gx + cw, y0 + ch, cw, ch });
    knob (b + 7, "UNISON", { gx + 2 * cw, y0 + ch, cw, ch });
}

void MainPanel::buildLfo (int l, R r)
{
    const int b = Lfo1_Shape + l * kLfoParamCount;
    section (l == 0 ? "LFO 1" : "LFO 2", r);
    combo (b + 0, { r.getX() + 52, r.getY() + 3, 84, 18 }).setTooltip ("LFO shape");
    toggle (b + 1, "SYNC", { r.getX() + 8, r.getY() + 28, 56, 20 });
    toggle (b + 5, "RETRIG", { r.getX() + 8, r.getY() + 54, 56, 20 });
    lfoDiv[l] = &combo (b + 3, { r.getX() + 8, r.getY() + 80, 56, 20 });
    lfoDiv[l]->setTooltip ("Synced rate");
    lfoRate[l] = &knob (b + 2, "RATE", { r.getX() + 72, r.getY() + 26, 74, 72 });
    knob (b + 4, "DEPTH", { r.getX() + 148, r.getY() + 26, 74, 72 });
    lfoSync[l] = state.getRawParameterValue (spec (b + 1).id);
}

MainPanel::MainPanel (VoltAudioProcessor& p) : presetBar (p.getPresetManager()), processor (p), state (p.apvts)
{
    addAndMakeVisible (presetBar);
    presetBar.setBounds (0, 0, kWidth, 44);

    // ---------------- row 1: oscillators, unison/sub, filter ----------------
    const int y1 = 50, h1 = 184;
    buildOsc (0, { 8, y1, 238, h1 });
    buildOsc (1, { 252, y1, 238, h1 });

    {
        const R r { 496, y1, 118, h1 };
        section ("UNISON / SUB", r);
        knob (UniDetune, "DETUNE", { r.getX() + 20, r.getY() + 24, 78, 84 }, true);
        const int y = r.getY() + 110, w = 38;
        knob (UniSpread, "SPREAD", { r.getX() + 2, y, w, 44 });
        knob (SubLevel, "SUB", { r.getX() + 2 + w, y, w, 44 });
        knob (NoiseLevel, "NOISE", { r.getX() + 2 + 2 * w, y, w, 44 });
        combo (SubShape, { r.getX() + 8, r.getY() + 158, r.getWidth() - 16, 20 }).setTooltip ("Sub oscillator shape");
    }

    {
        const R r { 620, y1, 372, h1 };
        section ("FILTER", r);
        combo (FltType, { r.getX() + 64, r.getY() + 3, 96, 18 }).setTooltip ("Filter type");
        const int y = r.getY() + 24;
        knob (FltCutoff, "CUTOFF", { r.getX() + 6, y, 80, 88 }, true);
        knob (FltRes, "RESONANCE", { r.getX() + 88, y, 80, 88 }, true);
        knob (FltDrive, "DRIVE", { r.getX() + 170, y, 80, 88 }, true);
        knob (FltKeyTrack, "KEY TRK", { r.getX() + 256, y, 54, 48 });
        knob (FltEnvAmt, "ENV AMT", { r.getX() + 312, y, 54, 48 });
        vowelKnob = &knob (FltVowel, "VOWEL", { r.getX() + 256, y + 52, 54, 48 });
        fltType = state.getRawParameterValue (spec (FltType).id);
        subLabel ("FILTER ENV", { r.getX() + 8, r.getY() + 116, 120, 12 });
        const int ey = r.getY() + 128, ew = 56;
        knob (FenvA, "ATTACK", { r.getX() + 6, ey, ew, 50 });
        knob (FenvD, "DECAY", { r.getX() + 6 + ew, ey, ew, 50 });
        knob (FenvS, "SUSTAIN", { r.getX() + 6 + 2 * ew, ey, ew, 50 });
        knob (FenvR, "RELEASE", { r.getX() + 6 + 3 * ew, ey, ew, 50 });
    }

    // ---------------- row 2: amp env, pitch env, LFOs, voice ----------------
    const int y2 = 240, h2 = 118;
    {
        const R r { 8, y2, 220, h2 };
        section ("AMP ENV", r);
        const int w = 53;
        knob (AmpA, "ATTACK", { r.getX() + 4, r.getY() + 28, w, 64 });
        knob (AmpD, "DECAY", { r.getX() + 4 + w, r.getY() + 28, w, 64 });
        knob (AmpS, "SUSTAIN", { r.getX() + 4 + 2 * w, r.getY() + 28, w, 64 });
        knob (AmpR, "RELEASE", { r.getX() + 4 + 3 * w, r.getY() + 28, w, 64 });
    }
    {
        const R r { 234, y2, 112, h2 };
        section ("PITCH ENV", r);
        knob (PenvAmt, "AMOUNT", { r.getX() + 4, r.getY() + 28, 52, 64 });
        knob (PenvDecay, "DECAY", { r.getX() + 56, r.getY() + 28, 52, 64 });
    }
    buildLfo (0, { 352, y2, 232, h2 });
    buildLfo (1, { 590, y2, 232, h2 });
    {
        const R r { 828, y2, 164, h2 };
        section ("VOICE", r);
        combo (VoiceMode, { r.getX() + 8, r.getY() + 30, 82, 20 }).setTooltip ("Poly / Mono / Legato");
        knob (Glide, "GLIDE", { r.getX() + 96, r.getY() + 26, 62, 68 });
    }

    // ---------------- row 3: macros, arp, distortion, mod fx, pump, delay ----------------
    const int y3 = 364, h3 = 128;
    {
        const R r { 8, y3, 262, h3 };
        section ("MACROS", r);
        for (int m = 0; m < kNumMacros; ++m)
        {
            auto& k = knob (Macro1 + m, processor.getPresetManager().getMacroLabel (m), { r.getX() + 4 + m * 64, r.getY() + 22, 62, 100 }, true);
            k.label.setInterceptsMouseClicks (true, false);
            k.label.setEditable (false, true, false);
            k.label.setTooltip ("Double-click to rename");
            k.label.onTextChange = [this, m, &k] {
                processor.getPresetManager().setMacroLabel (m, k.label.getText());
            };
            macroKnobs[m] = &k;
        }
    }
    {
        const R r { 276, y3, 160, h3 };
        section ("ARP", r);
        toggle (ArpOn, "ON", { r.getX() + 8, r.getY() + 28, 40, 20 });
        combo (ArpMode, { r.getX() + 54, r.getY() + 28, 98, 20 }).setTooltip ("Arp mode");
        combo (ArpRate, { r.getX() + 8, r.getY() + 58, 56, 20 }).setTooltip ("Arp rate");
        knob (ArpOct, "OCTAVES", { r.getX() + 66, r.getY() + 54, 46, 62 });
        knob (ArpGate, "GATE", { r.getX() + 112, r.getY() + 54, 46, 62 });
    }
    {
        const R r { 442, y3, 150, h3 };
        section ("DISTORTION", r);
        combo (DistType, { r.getX() + 76, r.getY() + 3, 68, 18 }).setTooltip ("Distortion type");
        knob (DistDrive, "DISTORTION", { r.getX() + 2, r.getY() + 26, 80, 90 }, true);
        knob (DistTone, "TONE", { r.getX() + 86, r.getY() + 24, 58, 48 });
        knob (DistMix, "MIX", { r.getX() + 86, r.getY() + 74, 58, 48 });
    }
    {
        const R r { 598, y3, 140, h3 };
        section ("MOD FX", r);
        combo (MfxType, { r.getX() + 60, r.getY() + 3, 74, 18 }).setTooltip ("Mod FX type");
        const int w = 44;
        knob (MfxRate, "RATE", { r.getX() + 4, r.getY() + 40, w, 60 });
        knob (MfxDepth, "DEPTH", { r.getX() + 4 + w, r.getY() + 40, w, 60 });
        knob (MfxMix, "MIX", { r.getX() + 4 + 2 * w, r.getY() + 40, w, 60 });
    }
    {
        const R r { 744, y3, 80, h3 };
        section ("PUMP", r);
        knob (PumpAmount, "PUMP", { r.getX() + 2, r.getY() + 20, 76, 82 }, true);
        combo (PumpRate, { r.getX() + 8, r.getY() + 104, r.getWidth() - 16, 18 }).setTooltip ("Pump rate (tempo synced)");
    }
    {
        const R r { 830, y3, 162, h3 };
        section ("DELAY", r);
        combo (DlyMode, { r.getX() + 60, r.getY() + 3, 96, 18 }).setTooltip ("Stereo / Ping-pong");
        knob (DlyMix, "DELAY", { r.getX() + 2, r.getY() + 26, 80, 90 }, true);
        combo (DlyTime, { r.getX() + 86, r.getY() + 30, 68, 20 }).setTooltip ("Delay time (tempo synced)");
        knob (DlyFeedback, "FEEDBACK", { r.getX() + 86, r.getY() + 56, 68, 62 });
    }

    // ---------------- row 4: mod matrix, reverb, squash, output ----------------
    const int y4 = 498, h4 = 114;
    {
        const R r { 8, y4, 520, h4 };
        section ("MODULATION", r);
        for (int m = 0; m < kNumModSlots; ++m)
        {
            const int col = m / 4, row = m % 4;
            const int x = r.getX() + 8 + col * 258, y = r.getY() + 22 + row * 22;
            const int b = Mod1_Src + m * kModSlotParamCount;
            subLabels.push_back ({ juce::String (m + 1), { x, y, 12, 20 } });
            combo (b + 0, { x + 14, y, 84, 20 }).setTooltip ("Modulation source");
            combo (b + 1, { x + 100, y, 92, 20 }).setTooltip ("Modulation target");
            auto a = std::make_unique<AmountSlider> (state, b + 2);
            a->setBounds (x + 196, y, 50, 20);
            addAndMakeVisible (*a);
            owned.push_back (std::move (a));
        }
    }
    {
        const R r { 534, y4, 160, h4 };
        section ("REVERB", r);
        knob (RevMix, "REVERB", { r.getX() + 2, r.getY() + 20, 80, 88 }, true);
        knob (RevSize, "SIZE", { r.getX() + 86, r.getY() + 18, 66, 46 });
        knob (RevDamp, "DAMPING", { r.getX() + 86, r.getY() + 64, 66, 46 });
    }
    {
        const R r { 700, y4, 70, h4 };
        section ("SQUASH", r);
        knob (Squash, "AMOUNT", { r.getX() + 4, r.getY() + 26, 62, 72 });
    }
    {
        const R r { 776, y4, 216, h4 };
        section ("OUTPUT", r);
        knob (OutGain, "OUTPUT", { r.getX() + 2, r.getY() + 20, 78, 88 }, true);
        scope.setBounds (r.getX() + 84, r.getY() + 24, r.getWidth() - 92, r.getHeight() - 32);
        scope.pull = [this] (float* dst, int n) { return processor.pullScope (dst, n); };
        addAndMakeVisible (scope);
    }

    setSize (kWidth, kHeight);
    refresh();
}

void MainPanel::refresh()
{
    for (auto& v : wtView)
        if (v != nullptr)
            v->refresh();
    scope.refresh();
    presetBar.refresh();

    for (int m = 0; m < kNumMacros; ++m)
    {
        auto* k = macroKnobs[m];
        if (k == nullptr || k->label.isBeingEdited() || k->slider.isActive())
            continue;
        const auto name = processor.getPresetManager().getMacroLabel (m);
        if (k->label.getText() != name)
            k->label.setText (name, juce::dontSendNotification);
    }
    for (int l = 0; l < 2; ++l)
    {
        const bool sync = lfoSync[l]->load() >= 0.5f;
        lfoRate[l]->setEnabled (! sync);
        lfoDiv[l]->setEnabled (sync);
    }
    if (vowelKnob != nullptr)
        vowelKnob->setEnabled (juce::roundToInt (fltType->load()) == choices::Formant);
}

void MainPanel::paint (juce::Graphics& g)
{
    g.fillAll (colours::background);
    for (const auto& s : sections)
    {
        const auto r = s.bounds.toFloat();
        g.setColour (colours::panel);
        g.fillRoundedRectangle (r, 5.0f);
        g.setColour (colours::panelBorder);
        g.drawRoundedRectangle (r.reduced (0.5f), 5.0f, 1.0f);
        g.setColour (colours::dimText);
        g.setFont (VoltLookAndFeel::font (11.5f, true));
        g.drawText (s.title, s.bounds.getX() + 10, s.bounds.getY() + 3, 120, 18, juce::Justification::centredLeft);
    }
    g.setFont (VoltLookAndFeel::font (10.0f, true));
    for (const auto& s : subLabels)
    {
        g.setColour (colours::dimText.withAlpha (0.8f));
        g.drawText (s.title, s.bounds, juce::Justification::centredLeft);
    }
}
} // namespace volt::ui

// =================================================================================================
VoltAudioProcessorEditor::VoltAudioProcessorEditor (VoltAudioProcessor& p) : AudioProcessorEditor (p), proc (p), panel (p)
{
    setLookAndFeel (&lnf);
    tooltips.setLookAndFeel (&lnf);
    addAndMakeVisible (panel);

    const float scale = juce::jlimit (0.75f, 2.0f, proc.getUiScale());
    setResizable (true, true);
    setResizeLimits (750, 465, 2000, 1240);
    if (auto* c = getConstrainer())
        c->setFixedAspectRatio ((double) volt::ui::MainPanel::kWidth / (double) volt::ui::MainPanel::kHeight);

    panel.presetBar.onScaleChange = [this] (float s) {
        proc.setUiScale (s);
        setSize (juce::roundToInt (volt::ui::MainPanel::kWidth * s), juce::roundToInt (volt::ui::MainPanel::kHeight * s));
    };
    static const float steps[] = { 0.75f, 1.0f, 1.25f, 1.5f, 1.75f, 2.0f };
    int best = 1;
    for (int i = 0; i < 6; ++i)
        if (std::abs (steps[i] - scale) < std::abs (steps[best] - scale))
            best = i;
    panel.presetBar.scaleBox.setSelectedItemIndex (best, juce::dontSendNotification);

    setSize (juce::roundToInt (volt::ui::MainPanel::kWidth * scale), juce::roundToInt (volt::ui::MainPanel::kHeight * scale));
    startTimerHz (30);
}

VoltAudioProcessorEditor::~VoltAudioProcessorEditor()
{
    stopTimer();
    tooltips.setLookAndFeel (nullptr);
    setLookAndFeel (nullptr);
}

void VoltAudioProcessorEditor::paint (juce::Graphics& g)
{
    g.fillAll (volt::ui::colours::background);
}

void VoltAudioProcessorEditor::resized()
{
    const float s = (float) getWidth() / (float) volt::ui::MainPanel::kWidth;
    panel.setBounds (0, 0, volt::ui::MainPanel::kWidth, volt::ui::MainPanel::kHeight);
    panel.setTransform (juce::AffineTransform::scale (s));
}
