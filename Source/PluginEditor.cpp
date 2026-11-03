#include "PluginEditor.h"

namespace volt::ui
{
using R = juce::Rectangle<int>;

// =================================================================================================
void Page::paint (juce::Graphics& g)
{
    for (const auto& s : sections)
    {
        const auto r = s.bounds.toFloat();
        g.setColour (colours::panel);
        g.fillRoundedRectangle (r, 6.0f);
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
        g.drawText (s.title, s.bounds.getX() + 10, s.bounds.getY() + 3, 200, 20, juce::Justification::centredLeft);
    }
    for (const auto& n : notes)
    {
        g.setColour (n.colour);
        g.setFont (VoltLookAndFeel::font (n.bold ? 11.5f : 11.5f, n.bold));
        g.drawFittedText (n.text, n.bounds, juce::Justification::centredLeft, 3);
    }
}

// =================================================================================================
void MainPanel::add (std::unique_ptr<juce::Component> c, R r)
{
    c->setBounds (r);
    target->addAndMakeVisible (*c);
    owned.push_back (std::move (c));
}

Knob& MainPanel::knob (int param, const juce::String& caption, R r, bool big)
{
    return knob (param, caption, r, current, big);
}

Knob& MainPanel::knob (int param, const juce::String& caption, R r, juce::Colour c, bool big)
{
    auto k = std::make_unique<Knob> (state, param, caption, c, big);
    auto& ref = *k;
    add (std::move (k), r);
    return ref;
}

ParamCombo& MainPanel::combo (int param, R r)
{
    auto c = std::make_unique<ParamCombo> (state, param);
    VoltLookAndFeel::setAccent (*c, current);
    auto& ref = *c;
    add (std::move (c), r);
    return ref;
}

ParamToggle& MainPanel::toggle (int param, const juce::String& text, R r)
{
    auto t = std::make_unique<ParamToggle> (state, param, text);
    VoltLookAndFeel::setAccent (*t, current);
    auto& ref = *t;
    add (std::move (t), r);
    return ref;
}

void MainPanel::section (const juce::String& title, R r, juce::Colour c)
{
    target->sections.push_back ({ title, r, c });
    current = c;
}

void MainPanel::note (const juce::String& text, R r, juce::Colour c, bool bold)
{
    target->notes.push_back ({ text, r, c, bold });
}

// =================================================================================================
void MainPanel::buildOsc (int o, R r)
{
    const int b = OscA_Table + o * kOscParamCount;
    section (o == 0 ? "OSC A" : "OSC B", r, colours::osc);
    combo (b + 0, { r.getX() + 66, r.getY() + 4, 184, 20 }).setTooltip ("Wavetable (in String mode: the pluck shape)");
    combo (b + 8, { r.getX() + 256, r.getY() + 4, r.getWidth() - 264, 20 }).setTooltip ("Oscillator type: Wavetable or String (plucked string model)");
    auto view = std::make_unique<WavetableView> (state, o);
    wtView[o] = view.get();
    add (std::move (view), { r.getX() + 10, r.getY() + 32, r.getWidth() - 20, 70 });
    const int y0 = r.getY() + 108;
    posKnob[o] = &knob (b + 1, o == 0 ? "Wavetable A" : "Wavetable B", { r.getX() + 6, y0, 84, 146 }, true);
    combo (b + 9, { r.getX() + 96, y0 + 2, 84, 22 }).setTooltip ("Warp mode: Sync, Bend, Squeeze, Mirror, Quantize, FM / RM from the other oscillator");
    warpKnob[o] = &knob (b + 10, "Warp", { r.getX() + 96, y0 + 28, 84, 118 }, true);
    const int gx = r.getX() + 186, cw = 64, ch = 73;
    knob (b + 2, "Octave", { gx, y0, cw, ch });
    knob (b + 3, "Semitones", { gx + cw, y0, cw, ch });
    knob (b + 4, "Fine", { gx + 2 * cw, y0, cw, ch });
    knob (b + 5, "Level", { gx, y0 + ch, cw, ch });
    knob (b + 6, "Pan", { gx + cw, y0 + ch, cw, ch });
    knob (b + 7, "Unison", { gx + 2 * cw, y0 + ch, cw, ch });
    oscType[o] = state.getRawParameterValue (spec (b + 8).id);
    oscWarp[o] = state.getRawParameterValue (spec (b + 9).id);
}

void MainPanel::buildLfo (int l, R r)
{
    const int b = Lfo1_Shape + l * kLfoParamCount;
    section (l == 0 ? "LFO 1" : "LFO 2", r, colours::mod);
    combo (b + 0, { r.getX() + 64, r.getY() + 4, 120, 20 }).setTooltip ("LFO shape");
    toggle (b + 1, "Sync", { r.getX() + 12, r.getY() + 44, 92, 28 });
    toggle (b + 5, "Retrigger", { r.getX() + 12, r.getY() + 80, 92, 28 });
    lfoDiv[l] = &combo (b + 3, { r.getX() + 12, r.getY() + 116, 92, 28 });
    lfoDiv[l]->setTooltip ("Synced rate (active when Sync is on)");
    note ("Use LFO " + juce::String (l + 1) + " as a source in the Modulation matrix below.", { r.getX() + 12, r.getY() + 160, 100, 56 }, colours::dimText);
    lfoRate[l] = &knob (b + 2, "Rate", { r.getX() + 116, r.getY() + 34, 130, 180 }, true);
    knob (b + 4, "Depth", { r.getX() + 250, r.getY() + 34, 130, 180 }, true);
    lfoSync[l] = state.getRawParameterValue (spec (b + 1).id);
}

// =================================================================================================
void MainPanel::buildSynthTab()
{
    target = &synthPage;
    buildOsc (0, { 8, 4, 380, 262 });
    buildOsc (1, { 394, 4, 380, 262 });
    {
        const R r { 780, 4, 412, 262 };
        section ("FILTER", r, colours::filter);
        combo (FltType, { r.getX() + 70, r.getY() + 4, 110, 20 }).setTooltip ("Filter type");
        auto fv = std::make_unique<FilterResponseView> (state);
        filterView = fv.get();
        add (std::move (fv), { r.getX() + 10, r.getY() + 32, 186, 120 });
        knob (FltCutoff, "Cutoff", { r.getX() + 200, r.getY() + 30, 70, 122 }, true);
        knob (FltRes, "Resonance", { r.getX() + 270, r.getY() + 30, 70, 122 }, true);
        knob (FltDrive, "Drive", { r.getX() + 340, r.getY() + 30, 70, 122 }, true);
        const int y = r.getY() + 176, w = 58;
        knob (FltKeyTrack, "Keytrack", { r.getX() + 6, y, w, 80 });
        knob (FltEnvAmt, "Env Amt", { r.getX() + 6 + w, y, w, 80 });
        vowelKnob = &knob (FltVowel, "Vowel", { r.getX() + 6 + 2 * w, y, w, 80 });
        fltType = state.getRawParameterValue (spec (FltType).id);
        note ("Filter envelope", { r.getX() + 188, r.getY() + 158, 160, 14 }, colours::env, true);
        const int ex = r.getX() + 186, ew = 56;
        knob (FenvA, "Attack", { ex, y, ew, 80 }, colours::env);
        knob (FenvD, "Decay", { ex + ew, y, ew, 80 }, colours::env);
        knob (FenvS, "Sustain", { ex + 2 * ew, y, ew, 80 }, colours::env);
        knob (FenvR, "Release", { ex + 3 * ew, y, ew, 80 }, colours::env);
    }

    const int y = 272, h = 238;
    {
        const R r { 8, y, 232, h };
        section ("UNISON / SUB / NOISE", r, colours::osc);
        knob (UniDetune, "Unison Detune", { r.getX() + 6, r.getY() + 34, 104, 150 }, true);
        knob (UniSpread, "Spread", { r.getX() + 112, r.getY() + 32, 58, 80 });
        knob (SubLevel, "Sub", { r.getX() + 170, r.getY() + 32, 58, 80 });
        knob (NoiseLevel, "Noise", { r.getX() + 112, r.getY() + 116, 58, 80 });
        note ("Sub shape", { r.getX() + 172, r.getY() + 118, 60, 14 }, colours::dimText);
        combo (SubShape, { r.getX() + 172, r.getY() + 136, 54, 22 }).setTooltip ("Sub oscillator shape (one octave below Osc A)");
    }
    {
        const R r { 246, y, 150, h };
        section ("STRING", r, colours::osc);
        stringKnobs[0] = &knob (StrDecay, "Decay", { r.getX() + 5, r.getY() + 34, 70, 120 }, true);
        stringKnobs[1] = &knob (StrTone, "Tone", { r.getX() + 75, r.getY() + 34, 70, 120 }, true);
        note ("Used when an oscillator's type is String: a plucked string excited by its wavetable.",
              { r.getX() + 10, r.getY() + 162, r.getWidth() - 20, 60 }, colours::dimText);
    }
    {
        const R r { 402, y, 290, h };
        section ("AMP ENVELOPE", r, colours::env);
        const int w = 70;
        knob (AmpA, "Attack", { r.getX() + 5, r.getY() + 34, w, 130 }, true);
        knob (AmpD, "Decay", { r.getX() + 5 + w, r.getY() + 34, w, 130 }, true);
        knob (AmpS, "Sustain", { r.getX() + 5 + 2 * w, r.getY() + 34, w, 130 }, true);
        knob (AmpR, "Release", { r.getX() + 5 + 3 * w, r.getY() + 34, w, 130 }, true);
    }
    {
        const R r { 698, y, 150, h };
        section ("PITCH ENVELOPE", r, colours::env);
        knob (PenvAmt, "Amount", { r.getX() + 5, r.getY() + 34, 70, 130 }, true);
        knob (PenvDecay, "Decay", { r.getX() + 75, r.getY() + 34, 70, 130 }, true);
    }
    {
        const R r { 854, y, 150, h };
        section ("VOICE", r, colours::mod);
        combo (VoiceMode, { r.getX() + 10, r.getY() + 36, r.getWidth() - 20, 26 }).setTooltip ("Poly / Mono / Legato");
        knob (Glide, "Glide", { r.getX() + 20, r.getY() + 74, 110, 130 }, true);
    }
    {
        const R r { 1010, y, 182, h };
        section ("ARPEGGIATOR", r, colours::mod);
        toggle (ArpOn, "On", { r.getX() + 10, r.getY() + 36, 50, 26 });
        combo (ArpMode, { r.getX() + 66, r.getY() + 36, 106, 26 }).setTooltip ("Arp mode");
        combo (ArpRate, { r.getX() + 10, r.getY() + 70, 162, 26 }).setTooltip ("Arp rate (tempo synced)");
        knob (ArpOct, "Octaves", { r.getX() + 6, r.getY() + 106, 84, 110 }, true);
        knob (ArpGate, "Gate", { r.getX() + 92, r.getY() + 106, 84, 110 }, true);
    }
}

void MainPanel::buildModTab()
{
    target = &modPage;
    buildLfo (0, { 8, 4, 390, 226 });
    buildLfo (1, { 404, 4, 390, 226 });
    {
        const R r { 800, 4, 392, 226 };
        section ("MOD ENVELOPE", r, colours::mod);
        const int w = 92;
        knob (MenvA, "Attack", { r.getX() + 12, r.getY() + 34, w, 140 }, true);
        knob (MenvD, "Decay", { r.getX() + 12 + w, r.getY() + 34, w, 140 }, true);
        knob (MenvS, "Sustain", { r.getX() + 12 + 2 * w, r.getY() + 34, w, 140 }, true);
        knob (MenvR, "Release", { r.getX() + 12 + 3 * w, r.getY() + 34, w, 140 }, true);
        note ("A free envelope for any target: pick 'Mod Env' as a source. 'Random' gives every note its own value.",
              { r.getX() + 12, r.getY() + 180, r.getWidth() - 24, 36 }, colours::dimText);
    }
    {
        const R r { 8, 236, 1184, 274 };
        section ("MODULATION MATRIX", r, colours::mod);
        const int colW = 586;
        for (int m = 0; m < kNumModSlots; ++m)
        {
            const int col = m / 6, row = m % 6;
            const int x = r.getX() + 12 + col * colW, yy = r.getY() + 38 + row * 38;
            const int b = Mod1_Src + m * kModSlotParamCount;
            note (juce::String (m + 1), { x, yy, 24, 28 }, colours::dimText, true);
            combo (b + 0, { x + 26, yy, 150, 28 }).setTooltip ("Modulation source");
            note (">", { x + 182, yy, 14, 28 }, colours::dimText, true);
            combo (b + 1, { x + 198, yy, 170, 28 }).setTooltip ("Modulation target");
            add (std::make_unique<AmountSlider> (state, b + 2, colours::mod), { x + 378, yy, 186, 28 });
        }
    }
}

void MainPanel::buildFxTab()
{
    target = &fxPage;
    const int h = 250;
    {
        const R r { 8, 4, 390, h };
        section ("1  DISTORTION", r, colours::fx);
        combo (DistType, { r.getX() + 130, r.getY() + 4, 120, 20 }).setTooltip ("Distortion type");
        knob (DistDrive, "Drive", { r.getX() + 10, r.getY() + 40, 120, 170 }, true);
        knob (DistTone, "Tone", { r.getX() + 135, r.getY() + 40, 120, 170 }, true);
        knob (DistMix, "Mix", { r.getX() + 260, r.getY() + 40, 120, 170 }, true);
    }
    {
        const R r { 404, 4, 390, h };
        section ("2  MOD FX", r, colours::fx);
        combo (MfxType, { r.getX() + 110, r.getY() + 4, 120, 20 }).setTooltip ("Chorus / Phaser / Flanger");
        knob (MfxRate, "Rate", { r.getX() + 10, r.getY() + 40, 120, 170 }, true);
        knob (MfxDepth, "Depth", { r.getX() + 135, r.getY() + 40, 120, 170 }, true);
        knob (MfxMix, "Mix", { r.getX() + 260, r.getY() + 40, 120, 170 }, true);
    }
    {
        const R r { 800, 4, 392, h };
        section ("3  PUMP", r, colours::fx);
        knob (PumpAmount, "Pump", { r.getX() + 20, r.getY() + 40, 150, 170 }, true);
        note ("Rate (tempo synced)", { r.getX() + 200, r.getY() + 60, 170, 16 }, colours::dimText);
        combo (PumpRate, { r.getX() + 200, r.getY() + 80, 170, 28 }).setTooltip ("Pump rate");
        note ("Sidechain-style ducking locked to the host tempo, like a kick pushing the sound down on every beat.",
              { r.getX() + 200, r.getY() + 120, 175, 80 }, colours::dimText);
    }
    {
        const R r { 8, 260, 390, h };
        section ("4  DELAY", r, colours::fx);
        combo (DlyMode, { r.getX() + 100, r.getY() + 4, 120, 20 }).setTooltip ("Stereo / Ping-pong");
        knob (DlyMix, "Mix", { r.getX() + 10, r.getY() + 40, 120, 170 }, true);
        knob (DlyFeedback, "Feedback", { r.getX() + 135, r.getY() + 40, 120, 170 }, true);
        note ("Time (tempo synced)", { r.getX() + 264, r.getY() + 60, 120, 16 }, colours::dimText);
        combo (DlyTime, { r.getX() + 264, r.getY() + 80, 112, 28 }).setTooltip ("Delay time");
    }
    {
        const R r { 404, 260, 390, h };
        section ("5  REVERB", r, colours::fx);
        knob (RevMix, "Mix", { r.getX() + 10, r.getY() + 40, 120, 170 }, true);
        knob (RevSize, "Size", { r.getX() + 135, r.getY() + 40, 120, 170 }, true);
        knob (RevDamp, "Damping", { r.getX() + 260, r.getY() + 40, 120, 170 }, true);
    }
    {
        const R r { 800, 260, 392, h };
        section ("6  SQUASH", r, colours::fx);
        knob (Squash, "Amount", { r.getX() + 20, r.getY() + 40, 150, 170 }, true);
        note ("Three-band compressor on one knob: glues and thickens the sound; high values bring quiet details up.",
              { r.getX() + 190, r.getY() + 70, 185, 90 }, colours::dimText);
    }
}

void MainPanel::buildBottom()
{
    target = &bottomPage;
    {
        const R r { 8, 0, 600, 134 };
        section ("MACROS", r, colours::macro);
        for (int m = 0; m < kNumMacros; ++m)
        {
            auto& k = knob (Macro1 + m, processor.getPresetManager().getMacroLabel (m), { r.getX() + 8 + m * 146, r.getY() + 28, 140, 104 }, true);
            k.label.setInterceptsMouseClicks (true, false);
            k.label.setEditable (false, true, false);
            k.label.setTooltip ("Double-click to rename");
            k.label.onTextChange = [this, m, &k] { processor.getPresetManager().setMacroLabel (m, k.label.getText()); };
            macroKnobs[m] = &k;
        }
    }
    {
        const R r { 614, 0, 150, 134 };
        section ("OUTPUT", r, colours::fx);
        knob (OutGain, "Output", { r.getX() + 15, r.getY() + 28, 120, 104 }, true);
    }
    {
        const R r { 770, 0, 422, 134 };
        section ("SCOPE", r, colours::fx);
        auto sc = std::make_unique<ScopeView>();
        scope = sc.get();
        scope->pull = [this] (float* dst, int n) { return processor.pullScope (dst, n); };
        add (std::move (sc), { r.getX() + 10, r.getY() + 32, r.getWidth() - 20, r.getHeight() - 42 });
    }
}

MainPanel::MainPanel (VoltAudioProcessor& p) : presetBar (p.getPresetManager()), processor (p), state (p.apvts)
{
    addAndMakeVisible (presetBar);
    presetBar.setBounds (0, 0, kWidth, 48);

    const char* names[3] = { "SYNTH", "MODULATION", "EFFECTS" };
    const juce::Colour tabColours[3] = { colours::osc, colours::mod, colours::fx };
    for (int t = 0; t < 3; ++t)
    {
        auto& b = tabButtons[t];
        b.setButtonText (names[t]);
        b.setClickingTogglesState (false);
        b.setRadioGroupId (4711);
        VoltLookAndFeel::setAccent (b, tabColours[t]);
        b.setBounds (8 + t * 150, 54, 144, 26);
        b.onClick = [this, t] { setTab (t); };
        addAndMakeVisible (b);
    }

    for (auto* pg : { &synthPage, &modPage, &fxPage })
    {
        pg->setBounds (0, 86, kWidth, 514);
        addChildComponent (*pg);
    }
    bottomPage.setBounds (0, 604, kWidth, 136);
    addAndMakeVisible (bottomPage);

    buildSynthTab();
    buildModTab();
    buildFxTab();
    buildBottom();

    setSize (kWidth, kHeight);
    setTab (juce::jlimit (0, 2, (int) processor.apvts.state.getProperty ("uiTab", 0)));
    refresh();
}

void MainPanel::setTab (int tab)
{
    currentTab = juce::jlimit (0, 2, tab);
    synthPage.setVisible (currentTab == SynthTab);
    modPage.setVisible (currentTab == ModTab);
    fxPage.setVisible (currentTab == FxTab);
    for (int t = 0; t < 3; ++t)
        tabButtons[t].setToggleState (t == currentTab, juce::dontSendNotification);
    processor.apvts.state.setProperty ("uiTab", currentTab, nullptr);
}

void MainPanel::refresh()
{
    for (auto* v : wtView)
        if (v != nullptr)
            v->refresh();
    if (filterView != nullptr)
        filterView->refresh();
    if (scope != nullptr)
        scope->refresh();
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
    bool anyString = false;
    for (int o = 0; o < 2; ++o)
    {
        const bool isString = juce::roundToInt (oscType[o]->load()) == choices::String;
        anyString = anyString || isString;
        warpKnob[o]->setEnabled (! isString && juce::roundToInt (oscWarp[o]->load()) != choices::WarpOff);
    }
    for (auto* k : stringKnobs)
        if (k != nullptr)
            k->setEnabled (anyString);
}

void MainPanel::paint (juce::Graphics& g)
{
    g.fillAll (colours::background);
    g.setColour (colours::panelBorder);
    g.drawHorizontalLine (83, 8.0f, (float) kWidth - 8.0f);
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
