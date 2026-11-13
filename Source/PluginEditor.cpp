#include "PluginEditor.h"

namespace volt::ui
{
using R = juce::Rectangle<int>;

// =================================================================================================
void Page::paint (juce::Graphics& g)
{
    for (const auto& s : surfaces)
        VoltLookAndFeel::drawSurface (g, s.bounds.toFloat(), s.colour);
    g.setColour (colours::panelBorder);
    for (const auto& l : lines)
        g.fillRect (l.bounds);
    for (const auto& t : titles)
    {
        g.setColour (t.colour);
        g.setFont (VoltLookAndFeel::titleFont (t.size));
        g.drawText (t.text, t.pos.x, t.pos.y, 260, 20, juce::Justification::centredLeft);
    }
    for (const auto& n : notes)
    {
        g.setColour (n.colour);
        g.setFont (VoltLookAndFeel::font (11.5f, n.bold));
        g.drawFittedText (n.text, n.bounds, juce::Justification::centredLeft, 4);
    }
}

// =================================================================================================
void MainPanel::add (std::unique_ptr<juce::Component> c, R r)
{
    c->setBounds (r);
    target->addAndMakeVisible (*c);
    owned.push_back (std::move (c));
}

Knob& MainPanel::knob (int param, const juce::String& caption, R r, int size)
{
    return knob (param, caption, r, current, size);
}

Knob& MainPanel::knob (int param, const juce::String& caption, R r, juce::Colour c, int size)
{
    auto k = std::make_unique<Knob> (state, param, caption, c, size);
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

void MainPanel::surface (R r, juce::Colour fill) { target->surfaces.push_back ({ r, fill }); }

void MainPanel::section (const juce::String& title, R r, juce::Colour c)
{
    surface (r, colours::panel);
    target->titles.push_back ({ title, { r.getX() + 14, r.getY() + 7 }, c, 12.5f });
    current = c;
}

void MainPanel::group (const juce::String& title, int x, int y, juce::Colour c)
{
    target->titles.push_back ({ title, { x, y }, c, 11.5f });
    current = c;
}

void MainPanel::hairline (R r) { target->lines.push_back ({ r }); }

void MainPanel::note (const juce::String& text, R r, juce::Colour c, bool bold)
{
    target->notes.push_back ({ text, r, c, bold });
}

// =================================================================================================
// Knob boxes: label + dial + value. Hero 90 x 109, medium 64 x 76, small 46..64 x 58.
void MainPanel::buildOsc (int o, int y0)
{
    const int b = OscA_Table + o * kOscParamCount;
    group (o == 0 ? "OSC A" : "OSC B", 20, y0 + 11, colours::osc);
    target->titles.back().size = 12.5f;
    combo (b + 0, { 80, y0 + 10, 184, 22 }).setTooltip ("Wavetable (in String mode: the pluck shape)");
    combo (b + 8, { 270, y0 + 10, 104, 22 }).setTooltip ("Oscillator type: Wavetable or String (plucked string model)");
    auto view = std::make_unique<WavetableView> (state, o);
    wtView[o] = view.get();
    add (std::move (view), { 16, y0 + 40, 280, 161 });

    auto& pos = knob (b + 1, "Position", { 307, y0 + 37, 90, 109 }, Knob::Hero);
    marks (o == 0 ? choices::DstPosA : choices::DstPosB, pos);
    warpKnob[o] = &knob (b + 10, "Warp", { 402, y0 + 56, 64, 76 }, Knob::Medium);
    marks (o == 0 ? choices::DstWarpA : choices::DstWarpB, *warpKnob[o]);
    note ("Warp mode", { 478, y0 + 70, 100, 14 }, colours::dimText);
    combo (b + 9, { 478, y0 + 88, 108, 22 }).setTooltip ("Warp mode: Sync, Bend, Squeeze, Mirror, Quantize, FM / RM from the other oscillator");

    const int x = 311, y = y0 + 147, w = 46, h = 58;
    knob (b + 2, "Octave", { x, y, w, h });
    knob (b + 3, "Semi", { x + w, y, w, h });
    knob (b + 4, "Fine", { x + 2 * w, y, w, h });
    marks (o == 0 ? choices::DstLevelA : choices::DstLevelB, knob (b + 5, "Level", { x + 3 * w, y, w, h }));
    marks (o == 0 ? choices::DstPanA : choices::DstPanB, knob (b + 6, "Pan", { x + 4 * w, y, w, h }));
    knob (b + 7, "Unison", { x + 5 * w, y, w, h });
    oscType[o] = state.getRawParameterValue (spec (b + 8).id);
    oscWarp[o] = state.getRawParameterValue (spec (b + 9).id);
}

void MainPanel::buildStripLfo (int l, int gx, int y)
{
    const int b = Lfo1_Shape + l * kLfoParamCount;
    group (l == 0 ? "LFO 1" : "LFO 2", gx + 14, y + 6, colours::mod);
    combo (b + 0, { gx + 62, y + 6, 92, 20 }).setTooltip ("LFO shape");
    auto& sync = toggle (b + 1, "SYNC", { gx + 160, y + 6, 56, 20 });
    VoltLookAndFeel::setStyle (sync, "seg");
    auto view = std::make_unique<LfoView> (state, l);
    lfoViews.push_back (view.get());
    add (std::move (view), { gx + 14, y + 34, 96, 63 });
    stripLfoRate[l] = &knob (b + 2, "Rate", { gx + 114, y + 36, 54, 58 });
    stripLfoDiv[l] = &combo (b + 3, { gx + 114, y + 56, 54, 22 });
    stripLfoDiv[l]->setTooltip ("Synced rate");
    knob (b + 4, "Depth", { gx + 170, y + 36, 54, 58 });
}

void MainPanel::buildLfo (int l, R r)
{
    const int b = Lfo1_Shape + l * kLfoParamCount;
    section (l == 0 ? "LFO 1" : "LFO 2", r, colours::mod);
    combo (b + 0, { r.getX() + 70, r.getY() + 7, 120, 22 }).setTooltip ("LFO shape");
    auto view = std::make_unique<LfoView> (state, l);
    lfoViews.push_back (view.get());
    add (std::move (view), { r.getX() + 12, r.getY() + 40, 122, 81 });
    toggle (b + 1, "Sync", { r.getX() + 12, r.getY() + 132, 58, 26 });
    toggle (b + 5, "Retrigger", { r.getX() + 76, r.getY() + 132, 58, 26 });
    lfoDiv[l] = &combo (b + 3, { r.getX() + 12, r.getY() + 166, 122, 26 });
    lfoDiv[l]->setTooltip ("Synced rate (active when Sync is on)");
    note ("Pick LFO " + juce::String (l + 1) + " as a source in the matrix below.", { r.getX() + 12, r.getY() + 196, 124, 30 }, colours::faint);
    lfoRate[l] = &knob (b + 2, "Rate", { r.getX() + 150, r.getY() + 54, 108, 134 }, Knob::Hero);
    knob (b + 4, "Depth", { r.getX() + 266, r.getY() + 54, 108, 134 }, Knob::Hero);
    lfoSync[l] = state.getRawParameterValue (spec (b + 1).id);
}

// =================================================================================================
void MainPanel::buildSynthTab()
{
    target = &synthPage;

    // Oscillators: one surface, two rows.
    surface ({ 6, 2, 590, 420 }, colours::panel);
    hairline ({ 20, 212, 562, 1 });
    buildOsc (0, 2);
    buildOsc (1, 212);

    {   // Filter: cutoff is the hero control.
        const R r { 598, 2, 596, 212 };
        section ("FILTER", r, colours::filter);
        target->titles.back().pos.y = r.getY() + 11;
        combo (FltType, { 684, 12, 112, 22 }).setTooltip ("Filter type");
        auto fv = std::make_unique<FilterResponseView> (state);
        filterView = fv.get();
        add (std::move (fv), { 608, 42, 280, 163 });
        marks (choices::DstCutoff, knob (FltCutoff, "Cutoff", { 913, 39, 90, 109 }, Knob::Hero));
        marks (choices::DstRes, knob (FltRes, "Resonance", { 1018, 60, 72, 76 }, Knob::Medium));
        marks (choices::DstDrive, knob (FltDrive, "Drive", { 1104, 60, 64, 76 }, Knob::Medium));
        knob (FltKeyTrack, "Keytrack", { 926, 151, 64, 58 });
        knob (FltEnvAmt, "Env amount", { 1018, 151, 72, 58 });
        vowelKnob = &knob (FltVowel, "Vowel", { 1104, 151, 64, 58 });
        marks (choices::DstFormant, *vowelKnob);
        fltType = state.getRawParameterValue (spec (FltType).id);
    }
    {   // Envelopes: one graph, four switchable sets of controls.
        const R r { 598, 216, 596, 206 };
        section ("ENVELOPES", r, colours::env);
        target->titles.back().pos.y = r.getY() + 11;
        const char* names[4] = { "AMP", "FILTER", "MOD", "PITCH" };
        for (int e = 0; e < 4; ++e)
        {
            auto& b = envButtons[e];
            b.setButtonText (names[e]);
            b.setConnectedEdges ((e > 0 ? juce::Button::ConnectedOnLeft : 0) | (e < 3 ? juce::Button::ConnectedOnRight : 0));
            VoltLookAndFeel::setStyle (b, "seg");
            VoltLookAndFeel::setAccent (b, colours::env);
            b.setBounds (716 + e * 56, 226, 56, 22);
            b.onClick = [this, e] { setEnvelope (e); };
            synthPage.addAndMakeVisible (b);
        }
        auto ev = std::make_unique<EnvelopeView> (state);
        envView = ev.get();
        add (std::move (ev), { 608, 256, 364, 157 });
        const R slots[4] = { { 994, 258, 84, 72 }, { 1094, 258, 84, 72 }, { 994, 342, 84, 72 }, { 1094, 342, 84, 72 } };
        const char* adsr[4] = { "Attack", "Decay", "Sustain", "Release" };
        const int first[3] = { AmpA, FenvA, MenvA };
        for (int e = 0; e < 3; ++e)
            for (int k = 0; k < 4; ++k)
                envKnobs[e].push_back (&knob (first[e] + k, adsr[k], slots[k], Knob::Medium));
        envKnobs[3].push_back (&knob (PenvAmt, "Amount", slots[0], Knob::Medium));
        envKnobs[3].push_back (&knob (PenvDecay, "Decay", slots[1], Knob::Medium));
    }

    // Utility strip: darker, no boxes, groups separated by space and hairlines.
    const int y = 424;
    surface ({ 6, y, 1188, 108 }, colours::strip);
    for (int x : { 136, 316, 446, 676, 906, 1036 })
        hairline ({ x, y + 14, 1, 80 });

    group ("UNISON", 20, y + 6, colours::osc);
    marks (choices::DstDetune, knob (UniDetune, "Detune", { 16, y + 36, 54, 58 }));
    knob (UniSpread, "Spread", { 72, y + 36, 54, 58 });

    group ("SUB / NOISE", 150, y + 6, colours::osc);
    marks (choices::DstSubLevel, knob (SubLevel, "Sub", { 146, y + 36, 54, 58 }));
    marks (choices::DstNoiseLevel, knob (NoiseLevel, "Noise", { 200, y + 36, 54, 58 }));
    note ("Sub shape", { 258, y + 36, 56, 14 }, colours::dimText);
    combo (SubShape, { 256, y + 56, 54, 22 }).setTooltip ("Sub oscillator shape (one octave below Osc A)");

    group ("STRING", 330, y + 6, colours::osc);
    stringKnobs[0] = &knob (StrDecay, "Decay", { 326, y + 36, 54, 58 });
    stringKnobs[1] = &knob (StrTone, "Tone", { 382, y + 36, 54, 58 });

    buildStripLfo (0, 446, y);
    buildStripLfo (1, 676, y);

    group ("VOICE", 920, y + 6, colours::mod);
    combo (VoiceMode, { 968, y + 6, 62, 20 }).setTooltip ("Poly / Mono / Legato");
    knob (Glide, "Glide", { 914, y + 36, 54, 58 });
    knob (BendRange, "Bend", { 972, y + 36, 54, 58 }).slider.setTooltip ("Pitch wheel range in semitones");

    group ("ARP", 1050, y + 6, colours::mod);
    VoltLookAndFeel::setStyle (toggle (ArpOn, "ON", { 1092, y + 6, 40, 20 }), "seg");
    combo (ArpMode, { 1048, y + 36, 66, 22 }).setTooltip ("Arp mode");
    combo (ArpRate, { 1048, y + 64, 66, 22 }).setTooltip ("Arp rate (tempo synced)");
    knob (ArpOct, "Oct", { 1116, y + 36, 38, 58 });
    knob (ArpGate, "Gate", { 1154, y + 36, 38, 58 });
}

void MainPanel::buildModTab()
{
    target = &modPage;
    buildLfo (0, { 6, 2, 392, 236 });
    buildLfo (1, { 400, 2, 392, 236 });
    {
        const R r { 794, 2, 400, 236 };
        section ("MOD ENVELOPE", r, colours::mod);
        const int w = 94;
        knob (MenvA, "Attack", { r.getX() + 12, r.getY() + 60, w, 76 }, Knob::Medium);
        knob (MenvD, "Decay", { r.getX() + 12 + w, r.getY() + 60, w, 76 }, Knob::Medium);
        knob (MenvS, "Sustain", { r.getX() + 12 + 2 * w, r.getY() + 60, w, 76 }, Knob::Medium);
        knob (MenvR, "Release", { r.getX() + 12 + 3 * w, r.getY() + 60, w, 76 }, Knob::Medium);
        note ("A free envelope for any target: pick 'Mod Env' as a source. 'Random' gives every note its own value.",
              { r.getX() + 14, r.getY() + 176, r.getWidth() - 28, 44 }, colours::faint);
    }
    {
        const R r { 6, 240, 1188, 292 };
        section ("MODULATION MATRIX", r, colours::mod);
        const int colW = 590;
        for (int m = 0; m < kNumModSlots; ++m)
        {
            const int col = m / 6, row = m % 6;
            const int x = r.getX() + 14 + col * colW, yy = r.getY() + 44 + row * 40;
            const int b = Mod1_Src + m * kModSlotParamCount;
            note (juce::String (m + 1), { x, yy, 24, 28 }, colours::faint, true);
            combo (b + 0, { x + 26, yy, 150, 28 }).setTooltip ("Modulation source");
            note (">", { x + 183, yy, 14, 28 }, colours::faint, true);
            combo (b + 1, { x + 198, yy, 170, 28 }).setTooltip ("Modulation target");
            add (std::make_unique<AmountSlider> (state, b + 2, colours::mod), { x + 378, yy, 186, 28 });
        }
    }
}

void MainPanel::buildFxTab()
{
    target = &fxPage;
    auto rack = std::make_unique<FxRack> (state);
    fxRack = rack.get();
    for (auto* p : fxRack->panels())
        for (auto& [dest, k] : p->macroTargets)
            marks (dest, *k);
    add (std::move (rack), { 0, 0, kWidth, 534 });
}

void MainPanel::buildBottom()
{
    target = &bottomPage;
    // Macro bar: the performance area. Each macro shows what it controls.
    surface ({ 6, 0, 740, 148 }, colours::macroBar);
    group ("MACROS", 20, 7, colours::macro);
    target->titles.back().size = 12.5f;
    for (int m = 0; m < kNumMacros; ++m)
    {
        auto cell = std::make_unique<MacroCell> (state, Macro1 + m);
        auto* c = cell.get();
        c->name.setText (processor.getPresetManager().getMacroLabel (m), juce::dontSendNotification);
        c->name.onTextChange = [this, m, c] { processor.getPresetManager().setMacroLabel (m, c->name.getText()); };
        macroCells[m] = c;
        add (std::move (cell), { 18 + m * 181, 40, 176, 96 });
    }

    // Output and scope carry no section colour.
    surface ({ 748, 0, 446, 148 }, colours::panel);
    group ("OUTPUT", 762, 7, colours::dimText);
    target->titles.back().size = 12.5f;
    knob (OutGain, "Level", { 762, 48, 64, 76 }, colours::value, Knob::Medium);
    auto lm = std::make_unique<LevelMeter>();
    meter = lm.get();
    meter->pull = [this] (int ch) { return processor.takeOutputPeak (ch); };
    add (std::move (lm), { 836, 38, 20, 99 });
    auto sc = std::make_unique<ScopeView>();
    scope = sc.get();
    scope->pull = [this] (float* dst, int n) { return processor.pullScope (dst, n); };
    add (std::move (sc), { 872, 38, 312, 99 });
}

MainPanel::MainPanel (VoltAudioProcessor& p) : presetBar (p.getPresetManager()), processor (p), state (p.apvts)
{
    addAndMakeVisible (presetBar);
    presetBar.setBounds (0, 0, kWidth, 48);

    const char* names[3] = { "SYNTH", "MODULATION", "EFFECTS" };
    const int tabX[4] = { 118, 196, 318, 412 };
    for (int t = 0; t < 3; ++t)
    {
        auto& b = tabButtons[t];
        b.setButtonText (names[t]);
        VoltLookAndFeel::setStyle (b, "tab");
        b.setBounds (tabX[t], 0, tabX[t + 1] - tabX[t], 48);
        b.onClick = [this, t] { setTab (t); };
        addAndMakeVisible (b);
    }

    for (auto* pg : { &synthPage, &modPage, &fxPage })
    {
        pg->setBounds (0, 52, kWidth, 534);
        addChildComponent (*pg);
    }
    bottomPage.setBounds (0, 586, kWidth, 154);
    addAndMakeVisible (bottomPage);

    for (int m = 0; m < kNumModSlots; ++m)
    {
        modSrc[m] = state.getRawParameterValue (spec (Mod1_Src + m * kModSlotParamCount).id);
        modDst[m] = state.getRawParameterValue (spec (Mod1_Dst + m * kModSlotParamCount).id);
        modAmt[m] = state.getRawParameterValue (spec (Mod1_Amt + m * kModSlotParamCount).id);
    }

    buildSynthTab();
    buildModTab();
    buildFxTab();
    buildBottom();

    // Fine grain over every surface, so the flat colours do not look printed.
    grain = juce::Image (juce::Image::ARGB, 160, 160, true);
    juce::Random rng (7);
    for (int y = 0; y < grain.getHeight(); ++y)
        for (int x = 0; x < grain.getWidth(); ++x)
            grain.setPixelAt (x, y, juce::Colour (0xfffff4e6).withAlpha (rng.nextFloat() * 0.042f));

    setSize (kWidth, kHeight);
    setTab (juce::jlimit (0, 2, (int) processor.apvts.state.getProperty ("uiTab", 0)));
    setEnvelope (0);
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

void MainPanel::setEnvelope (int env)
{
    currentEnv = juce::jlimit (0, 3, env);
    for (int e = 0; e < 4; ++e)
    {
        envButtons[e].setToggleState (e == currentEnv, juce::dontSendNotification);
        for (auto* k : envKnobs[e])
            k->setVisible (e == currentEnv);
    }
    if (envView != nullptr)
        envView->setMode (currentEnv);
}

void MainPanel::refresh()
{
    for (auto* v : wtView)
        if (v != nullptr)
            v->refresh();
    if (filterView != nullptr)
        filterView->refresh();
    if (envView != nullptr)
        envView->refresh();
    for (auto* v : lfoViews)
        v->refresh();
    if (scope != nullptr)
        scope->refresh();
    if (fxRack != nullptr && fxPage.isVisible())
        fxRack->refresh();
    if (meter != nullptr)
        meter->refresh();
    presetBar.refresh();

    // Modulation matrix -> what each macro controls, and which knobs a macro moves.
    juce::StringArray targets[kNumMacros];
    std::array<bool, choices::NumModDests> marked {};
    const auto& destNames = spec (Mod1_Dst).choices;
    for (int m = 0; m < kNumModSlots; ++m)
    {
        const int src = juce::roundToInt (modSrc[m]->load());
        const int dst = juce::roundToInt (modDst[m]->load());
        if (src < choices::SrcMacro1 || src > choices::SrcMacro4 || dst <= choices::DstNone || dst >= choices::NumModDests
            || std::abs (modAmt[m]->load()) < 1.0e-4f)
            continue;
        targets[src - choices::SrcMacro1].addIfNotAlreadyThere (destNames[dst]);
        marked[(size_t) dst] = true;
    }
    for (size_t d = 0; d < destKnobs.size(); ++d)
        for (auto* k : destKnobs[d])
            k->setMacroMark (marked[d]);

    for (int m = 0; m < kNumMacros; ++m)
    {
        auto* c = macroCells[m];
        if (c == nullptr)
            continue;
        c->setTarget (targets[m].joinIntoString (", "));
        if (c->name.isBeingEdited())
            continue;
        const auto name = processor.getPresetManager().getMacroLabel (m);
        if (c->name.getText() != name)
            c->name.setText (name, juce::dontSendNotification);
    }
    for (int l = 0; l < 2; ++l)
    {
        const bool sync = lfoSync[l]->load() >= 0.5f;
        lfoRate[l]->setEnabled (! sync);
        lfoDiv[l]->setEnabled (sync);
        stripLfoRate[l]->setVisible (! sync);
        stripLfoDiv[l]->setVisible (sync);
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
}

void MainPanel::paintOverChildren (juce::Graphics& g)
{
    g.setTiledImageFill (grain, 0, 0, 1.0f);
    g.fillAll();
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
