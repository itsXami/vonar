#pragma once

#include "PluginProcessor.h"
#include "ui/Controls.h"
#include "ui/Views.h"
#include "ui/PresetBar.h"
#include "ui/FxRack.h"

namespace volt::ui
{
// One tab, or the always-visible bottom bar: flat surfaces, coloured section titles, hairlines and small notes.
class Page final : public juce::Component
{
public:
    struct Surface { juce::Rectangle<int> bounds; juce::Colour colour; };
    struct Title { juce::String text; juce::Point<int> pos; juce::Colour colour; float size; };
    struct Note { juce::String text; juce::Rectangle<int> bounds; juce::Colour colour; bool bold; };
    struct Line { juce::Rectangle<int> bounds; };

    void paint (juce::Graphics&) override;
    std::vector<Surface> surfaces;
    std::vector<Title> titles;
    std::vector<Note> notes;
    std::vector<Line> lines;
};

// 1200 x 740 logical pixels: top bar (logo, tabs, preset browser), the selected tab, and a bottom bar with macros,
// output and scope that is always visible. The editor scales the whole panel.
class MainPanel final : public juce::Component
{
public:
    static constexpr int kWidth = 1200, kHeight = 740;
    enum Tab { SynthTab, ModTab, FxTab };

    explicit MainPanel (VoltAudioProcessor& p);
    void paint (juce::Graphics&) override;
    void paintOverChildren (juce::Graphics&) override;
    void resized() override {}
    void refresh(); // called by the editor timer (30 Hz)
    void setTab (int tab);
    int getTab() const noexcept { return currentTab; }
    void setEnvelope (int env);
    FxRack* getFxRack() noexcept { return fxRack; }

    PresetBar presetBar;

private:
    Knob& knob (int param, const juce::String& caption, juce::Rectangle<int> r, int size = Knob::Small);
    Knob& knob (int param, const juce::String& caption, juce::Rectangle<int> r, juce::Colour c, int size = Knob::Small);
    ParamCombo& combo (int param, juce::Rectangle<int> r);
    ParamToggle& toggle (int param, const juce::String& text, juce::Rectangle<int> r);
    void surface (juce::Rectangle<int> r, juce::Colour fill);
    void section (const juce::String& title, juce::Rectangle<int> r, juce::Colour c);   // panel surface + title
    void group (const juce::String& title, int x, int y, juce::Colour c);               // title only (utility strip)
    void hairline (juce::Rectangle<int> r);
    void note (const juce::String& text, juce::Rectangle<int> r, juce::Colour c, bool bold = false);
    void add (std::unique_ptr<juce::Component> c, juce::Rectangle<int> r);
    void marks (int dest, Knob& k) { destKnobs[(size_t) dest].push_back (&k); }

    void buildSynthTab();
    void buildModTab();
    void buildFxTab();
    void buildBottom();
    void buildOsc (int o, int y0);
    void buildLfo (int l, juce::Rectangle<int> r);
    void buildStripLfo (int l, int gx, int y);

    VoltAudioProcessor& processor;
    juce::AudioProcessorValueTreeState& state;
    Page synthPage, modPage, fxPage, bottomPage;
    Page* target = &synthPage;
    juce::TextButton tabButtons[3];
    juce::TextButton envButtons[4];
    int currentTab = 0, currentEnv = 0;
    juce::Image grain;

    std::vector<std::unique_ptr<juce::Component>> owned;
    juce::Colour current = colours::osc;
    WavetableView* wtView[2] {};
    FilterResponseView* filterView = nullptr;
    EnvelopeView* envView = nullptr;
    std::vector<LfoView*> lfoViews;
    ScopeView* scope = nullptr;
    FxRack* fxRack = nullptr;
    LevelMeter* meter = nullptr;
    MacroCell* macroCells[kNumMacros] {};
    std::vector<Knob*> envKnobs[4];
    Knob* lfoRate[2] {};          // modulation tab: disabled while synced
    ParamCombo* lfoDiv[2] {};
    Knob* stripLfoRate[2] {};     // synth tab: rate knob and division box share one place
    ParamCombo* stripLfoDiv[2] {};
    std::atomic<float>* lfoSync[2] {};
    std::atomic<float>* fltType = nullptr;
    std::atomic<float>* oscType[2] {};
    std::atomic<float>* oscWarp[2] {};
    std::atomic<float>* modSrc[kNumModSlots] {};
    std::atomic<float>* modDst[kNumModSlots] {};
    std::atomic<float>* modAmt[kNumModSlots] {};
    std::array<std::vector<Knob*>, choices::NumModDests> destKnobs;
    Knob* vowelKnob = nullptr;
    Knob* warpKnob[2] {};
    Knob* stringKnobs[2] {};
};
} // namespace volt::ui

class VoltAudioProcessorEditor final : public juce::AudioProcessorEditor, private juce::Timer
{
public:
    explicit VoltAudioProcessorEditor (VoltAudioProcessor&);
    ~VoltAudioProcessorEditor() override;

    void paint (juce::Graphics&) override;
    void resized() override;

    volt::ui::MainPanel& getPanel() noexcept { return panel; }

private:
    void timerCallback() override { panel.refresh(); }

    VoltAudioProcessor& proc;
    volt::ui::VoltLookAndFeel lnf;
    volt::ui::MainPanel panel;
    juce::TooltipWindow tooltips { this, 500 };

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (VoltAudioProcessorEditor)
};
