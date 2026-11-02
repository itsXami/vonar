#include "PluginEditor.h"

namespace volt::ui
{
using R = juce::Rectangle<int>;

Knob& MainPanel::knob (int param, const juce::String& caption, R r, bool big)
{
    return knob (param, caption, r, current, big);
}

Knob& MainPanel::knob (int param, const juce::String& caption, R r, juce::Colour c, bool big)
{
    auto k = std::make_unique<Knob> (state, param, caption, c, big);
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
    VoltLookAndFeel::setAccent (*c, current);
    addAndMakeVisible (*c);
    auto& ref = *c;
    owned.push_back (std::move (c));
    return ref;
}

ParamToggle& MainPanel::toggle (int param, const juce::String& text, R r)
{
    auto t = std::make_unique<ParamToggle> (state, param, text);
    t->setBounds (r);
    VoltLookAndFeel::setAccent (*t, current);
    addAndMakeVisible (*t);
    auto& ref = *t;
    owned.push_back (std::move (t));
    return ref;
}

void MainPanel::buildOsc (int o, R r)
{
    const int b = OscA_Table + o * kOscParamCount;
    section (o == 0 ? "OSC A" : "OSC B", r, colours::osc);
    combo (b + 0, { r.getX() + 70, r.getY() + 4, r.getWidth() - 78, 20 }).setTooltip ("Wavetable");
    wtView[o] = std::make_unique<WavetableView> (state, o);
    wtView[o]->setBounds (r.getX() + 10, r.getY() + 32, r.getWidth() - 20, 64);
    addAndMakeVisible (*wtView[o]);
    const int y0 = r.getY() + 102;
    knob (b + 1, o == 0 ? "Wavetable A" : "Wavetable B", { r.getX() + 6, y0 + 10, 84, 116 }, true);
    const int gx = r.getX() + 94, cw = 68, ch = 69;
    knob (b + 2, "Octave", { gx, y0, cw, ch });
    knob (b + 3, "Semitones", { gx + cw, y0, cw, ch });
    knob (b + 4, "Fine", { gx + 2 * cw, y0, cw, ch });
    knob (b + 5, "Level", { gx, y0 + ch, cw, ch });
    knob (b + 6, "Pan", { gx + cw, y0 + ch, cw, ch });
    knob (b + 7, "Unison", { gx + 2 * cw, y0 + ch, cw, ch });
}

void MainPanel::buildLfo (int l, R r)
{
    const int b = Lfo1_Shape + l * kLfoParamCount;
    section (l == 0 ? "LFO 1" : "LFO 2", r, colours::mod);
    combo (b + 0, { r.getX() + 64, r.getY() + 4, 104, 20 }).setTooltip ("LFO shape");
    toggle (b + 1, "Sync", { r.getX() + 10, r.getY() + 34, 72, 24 });
    toggle (b + 5, "Retrigger", { r.getX() + 10, r.getY() + 64, 72, 24 });
    lfoDiv[l] = &combo (b + 3, { r.getX() + 10, r.getY() + 94, 72, 24 });
    lfoDiv[l]->setTooltip ("Synced rate (active when Sync is on)");
    lfoRate[l] = &knob (b + 2, "Rate", { r.getX() + 90, r.getY() + 30, 90, 100 }, true);
    knob (b + 4, "Depth", { r.getX() + 184, r.getY() + 30, 90, 100 }, true);
    lfoSync[l] = state.getRawParameterValue (spec (b + 1).id);
}

MainPanel::MainPanel (VoltAudioProcessor& p) : presetBar (p.getPresetManager()), processor (p), state (p.apvts)
{
    addAndMakeVisible (presetBar);
    presetBar.setBounds (0, 0, kWidth, 48);

    // ---------------- row 1: oscillators, unison/sub, filter ----------------
    const int y1 = 56, h1 = 250;
    buildOsc (0, { 8, y1, 300, h1 });
    buildOsc (1, { 314, y1, 300, h1 });
    {
        const R r { 620, y1, 150, h1 };
        section ("UNISON / SUB", r, colours::osc);
        knob (UniDetune, "Unison Detune", { r.getX() + 20, r.getY() + 30, 110, 112 }, true);
        const int y = r.getY() + 148, w = 48;
        knob (UniSpread, "Spread", { r.getX() + 3, y, w, 66 });
        knob (SubLevel, "Sub", { r.getX() + 3 + w, y, w, 66 });
        knob (NoiseLevel, "Noise", { r.getX() + 3 + 2 * w, y, w, 66 });
        combo (SubShape, { r.getX() + 10, r.getY() + 220, r.getWidth() - 20, 22 }).setTooltip ("Sub oscillator shape");
    }
    {
        const R r { 776, y1, 416, h1 };
        section ("FILTER", r, colours::filter);
        combo (FltType, { r.getX() + 70, r.getY() + 4, 110, 20 }).setTooltip ("Filter type");
        filterView = std::make_unique<FilterResponseView> (state);
        filterView->setBounds (r.getX() + 10, r.getY() + 32, 176, 112);
        addAndMakeVisible (*filterView);
        knob (FltCutoff, "Cutoff", { r.getX() + 192, r.getY() + 30, 74, 114 }, true);
        knob (FltRes, "Resonance", { r.getX() + 266, r.getY() + 30, 74, 114 }, true);
        knob (FltDrive, "Drive", { r.getX() + 340, r.getY() + 30, 74, 114 }, true);
        const int y = r.getY() + 170, w = 56;
        knob (FltKeyTrack, "Keytrack", { r.getX() + 6, y, w, 70 });
        knob (FltEnvAmt, "Env Amt", { r.getX() + 6 + w, y, w, 70 });
        vowelKnob = &knob (FltVowel, "Vowel", { r.getX() + 6 + 2 * w, y, w, 70 });
        fltType = state.getRawParameterValue (spec (FltType).id);
        subLabel ("Filter envelope", { r.getX() + 184, r.getY() + 152, 160, 14 }, colours::env);
        const int ex = r.getX() + 182, ew = 58;
        knob (FenvA, "Attack", { ex, y, ew, 70 }, colours::env);
        knob (FenvD, "Decay", { ex + ew, y, ew, 70 }, colours::env);
        knob (FenvS, "Sustain", { ex + 2 * ew, y, ew, 70 }, colours::env);
        knob (FenvR, "Release", { ex + 3 * ew, y, ew, 70 }, colours::env);
    }

    // ---------------- row 2: amp env, pitch env, LFOs, voice ----------------
    const int y2 = 312, h2 = 136;
    {
        const R r { 8, y2, 290, h2 };
        section ("AMP ENVELOPE", r, colours::env);
        const int w = 70;
        knob (AmpA, "Attack", { r.getX() + 5, r.getY() + 30, w, 100 }, true);
        knob (AmpD, "Decay", { r.getX() + 5 + w, r.getY() + 30, w, 100 }, true);
        knob (AmpS, "Sustain", { r.getX() + 5 + 2 * w, r.getY() + 30, w, 100 }, true);
        knob (AmpR, "Release", { r.getX() + 5 + 3 * w, r.getY() + 30, w, 100 }, true);
    }
    {
        const R r { 304, y2, 150, h2 };
        section ("PITCH ENVELOPE", r, colours::env);
        knob (PenvAmt, "Amount", { r.getX() + 5, r.getY() + 30, 70, 100 }, true);
        knob (PenvDecay, "Decay", { r.getX() + 75, r.getY() + 30, 70, 100 }, true);
    }
    buildLfo (0, { 460, y2, 280, h2 });
    buildLfo (1, { 746, y2, 280, h2 });
    {
        const R r { 1032, y2, 160, h2 };
        section ("VOICE", r, colours::mod);
        combo (VoiceMode, { r.getX() + 10, r.getY() + 34, r.getWidth() - 20, 24 }).setTooltip ("Poly / Mono / Legato");
        knob (Glide, "Glide", { r.getX() + 30, r.getY() + 60, 100, 74 }, true);
    }

    // ---------------- row 3: macros, arp, distortion, mod fx, pump, scope ----------------
    const int y3 = 454, h3 = 140;
    {
        const R r { 8, y3, 330, h3 };
        section ("MACROS", r, colours::macro);
        for (int m = 0; m < kNumMacros; ++m)
        {
            auto& k = knob (Macro1 + m, processor.getPresetManager().getMacroLabel (m), { r.getX() + 5 + m * 80, r.getY() + 30, 80, 104 }, true);
            k.label.setInterceptsMouseClicks (true, false);
            k.label.setEditable (false, true, false);
            k.label.setTooltip ("Double-click to rename");
            k.label.onTextChange = [this, m, &k] { processor.getPresetManager().setMacroLabel (m, k.label.getText()); };
            macroKnobs[m] = &k;
        }
    }
    {
        const R r { 344, y3, 190, h3 };
        section ("ARPEGGIATOR", r, colours::mod);
        toggle (ArpOn, "On", { r.getX() + 10, r.getY() + 34, 50, 24 });
        combo (ArpMode, { r.getX() + 66, r.getY() + 34, 114, 24 }).setTooltip ("Arp mode");
        combo (ArpRate, { r.getX() + 10, r.getY() + 66, 70, 24 }).setTooltip ("Arp rate");
        knob (ArpOct, "Octaves", { r.getX() + 84, r.getY() + 62, 50, 72 });
        knob (ArpGate, "Gate", { r.getX() + 134, r.getY() + 62, 50, 72 });
    }
    {
        const R r { 540, y3, 210, h3 };
        section ("DISTORTION", r, colours::fx);
        combo (DistType, { r.getX() + 100, r.getY() + 4, 102, 20 }).setTooltip ("Distortion type");
        knob (DistDrive, "Distortion", { r.getX() + 6, r.getY() + 30, 92, 104 }, true);
        knob (DistTone, "Tone", { r.getX() + 100, r.getY() + 40, 52, 76 });
        knob (DistMix, "Mix", { r.getX() + 152, r.getY() + 40, 52, 76 });
    }
    {
        const R r { 756, y3, 200, h3 };
        section ("MOD FX", r, colours::fx);
        combo (MfxType, { r.getX() + 80, r.getY() + 4, 112, 20 }).setTooltip ("Mod FX type");
        knob (MfxRate, "Rate", { r.getX() + 4, r.getY() + 38, 64, 84 });
        knob (MfxDepth, "Depth", { r.getX() + 68, r.getY() + 38, 64, 84 });
        knob (MfxMix, "Mix", { r.getX() + 132, r.getY() + 38, 64, 84 });
    }
    {
        const R r { 962, y3, 110, h3 };
        section ("PUMP", r, colours::fx);
        knob (PumpAmount, "Pump", { r.getX() + 10, r.getY() + 28, 90, 84 }, true);
        combo (PumpRate, { r.getX() + 10, r.getY() + 114, r.getWidth() - 20, 20 }).setTooltip ("Pump rate (tempo synced)");
    }
    {
        const R r { 1078, y3, 114, h3 };
        section ("SCOPE", r, colours::fx);
        scope.setBounds (r.getX() + 8, r.getY() + 32, r.getWidth() - 16, r.getHeight() - 42);
        scope.pull = [this] (float* dst, int n) { return processor.pullScope (dst, n); };
        addAndMakeVisible (scope);
    }

    // ---------------- row 4: modulation matrix, delay, reverb, squash, output ----------------
    const int y4 = 600, h4 = 132;
    {
        const R r { 8, y4, 604, h4 };
        section ("MODULATION", r, colours::mod);
        for (int m = 0; m < kNumModSlots; ++m)
        {
            const int col = m / 4, row = m % 4;
            const int x = r.getX() + 10 + col * 296, y = r.getY() + 32 + row * 24;
            const int b = Mod1_Src + m * kModSlotParamCount;
            subLabel (juce::String (m + 1), { x, y, 14, 21 }, colours::dimText);
            combo (b + 0, { x + 14, y, 80, 21 }).setTooltip ("Modulation source");
            combo (b + 1, { x + 97, y, 92, 21 }).setTooltip ("Modulation target");
            auto a = std::make_unique<AmountSlider> (state, b + 2, colours::mod);
            a->setBounds (x + 192, y, 100, 21);
            addAndMakeVisible (*a);
            owned.push_back (std::move (a));
        }
    }
    {
        const R r { 618, y4, 190, h4 };
        section ("DELAY", r, colours::fx);
        combo (DlyMode, { r.getX() + 64, r.getY() + 4, 118, 20 }).setTooltip ("Stereo / Ping-pong");
        knob (DlyMix, "Delay", { r.getX() + 6, r.getY() + 26, 86, 100 }, true);
        combo (DlyTime, { r.getX() + 98, r.getY() + 32, 84, 22 }).setTooltip ("Delay time (tempo synced)");
        knob (DlyFeedback, "Feedback", { r.getX() + 102, r.getY() + 58, 76, 68 });
    }
    {
        const R r { 814, y4, 190, h4 };
        section ("REVERB", r, colours::fx);
        knob (RevMix, "Reverb", { r.getX() + 4, r.getY() + 26, 82, 100 }, true);
        knob (RevSize, "Size", { r.getX() + 86, r.getY() + 40, 50, 76 });
        knob (RevDamp, "Damping", { r.getX() + 136, r.getY() + 40, 50, 76 });
    }
    {
        const R r { 1010, y4, 76, h4 };
        section ("SQUASH", r, colours::fx);
        knob (Squash, "Amount", { r.getX() + 4, r.getY() + 34, 68, 84 });
    }
    {
        const R r { 1092, y4, 100, h4 };
        section ("OUTPUT", r, colours::fx);
        knob (OutGain, "Output", { r.getX() + 5, r.getY() + 26, 90, 100 }, true);
    }

    setSize (kWidth, kHeight);
    refresh();
}

void MainPanel::refresh()
{
    for (auto& v : wtView)
        if (v != nullptr)
            v->refresh();
    if (filterView != nullptr)
        filterView->refresh();
    scope.refresh();
    presetBar.refresh();

    for (int m = 0; m < kNumMacros; ++m)
    {
        auto* k = macroKnobs[m];
        if (k == nullptr || k->label.isBeingEdited())
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
        g.fillRoundedRectangle (r, 6.0f);
        // header strip tinted with the section colour
        const auto header = r.withHeight (26.0f);
        juce::Path hp;
        hp.addRoundedRectangle (header.getX(), header.getY(), header.getWidth(), header.getHeight(), 6.0f, 6.0f, true, true, false, false);
        g.setColour (s.colour.withAlpha (0.13f));
        g.fillPath (hp);
        g.setColour (s.colour);
        g.fillRect (r.getX() + 10.0f, r.getY() + 25.0f, 24.0f, 2.0f);
        g.setColour (colours::panelBorder);
        g.drawRoundedRectangle (r.reduced (0.5f), 6.0f, 1.0f);
        g.setColour (s.colour);
        g.setFont (VoltLookAndFeel::font (12.5f, true));
        g.drawText (s.title, s.bounds.getX() + 10, s.bounds.getY() + 3, 160, 20, juce::Justification::centredLeft);
    }
    for (const auto& s : subLabels)
    {
        g.setColour (s.colour);
        g.setFont (VoltLookAndFeel::font (11.5f, true));
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
    setResizeLimits (900, 555, 2400, 1480);
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
