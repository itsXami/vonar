#pragma once

#include "PluginProcessor.h"
#include "ui/Controls.h"
#include "ui/Views.h"
#include "ui/PresetBar.h"

namespace volt::ui
{
// A group of colour-coded sections (one tab, or the always-visible bottom strip).
class Page final : public juce::Component
{
public:
    struct Section { juce::String title; juce::Rectangle<int> bounds; juce::Colour colour; };
    struct Note { juce::String text; juce::Rectangle<int> bounds; juce::Colour colour; bool bold; };

    void paint (juce::Graphics&) override;
    std::vector<Section> sections;
    std::vector<Note> notes;
};

// 1200 x 740 logical pixels: preset bar, tab bar (SYNTH / MODULATION / EFFECTS), the selected tab, and a bottom
// strip with macros, output and scope that is always visible. The editor scales the whole panel.
class MainPanel final : public juce::Component
{
public:
    static constexpr int kWidth = 1200, kHeight = 740;
    enum Tab { SynthTab, ModTab, FxTab };

    explicit MainPanel (VoltAudioProcessor& p);
    void paint (juce::Graphics&) override;
    void resized() override {}
    void refresh(); // called by the editor timer (30 Hz)
    void setTab (int tab);
    int getTab() const noexcept { return currentTab; }

    PresetBar presetBar;

private:
    Knob& knob (int param, const juce::String& caption, juce::Rectangle<int> r, bool big = false);
    Knob& knob (int param, const juce::String& caption, juce::Rectangle<int> r, juce::Colour c, bool big = false);
    ParamCombo& combo (int param, juce::Rectangle<int> r);
    ParamToggle& toggle (int param, const juce::String& text, juce::Rectangle<int> r);
    void section (const juce::String& title, juce::Rectangle<int> r, juce::Colour c);
    void note (const juce::String& text, juce::Rectangle<int> r, juce::Colour c, bool bold = false);
    void add (std::unique_ptr<juce::Component> c, juce::Rectangle<int> r);

    void buildSynthTab();
    void buildModTab();
    void buildFxTab();
    void buildBottom();
    void buildOsc (int o, juce::Rectangle<int> r);
    void buildLfo (int l, juce::Rectangle<int> r);

    VoltAudioProcessor& processor;
    juce::AudioProcessorValueTreeState& state;
    Page synthPage, modPage, fxPage, bottomPage;
    Page* target = &synthPage;
    juce::TextButton tabButtons[3];
    int currentTab = 0;

    std::vector<std::unique_ptr<juce::Component>> owned;
    juce::Colour current = colours::osc;
    WavetableView* wtView[2] {};
    FilterResponseView* filterView = nullptr;
    ScopeView* scope = nullptr;
    Knob* macroKnobs[kNumMacros] {};
    Knob* lfoRate[2] {};
    ParamCombo* lfoDiv[2] {};
    std::atomic<float>* lfoSync[2] {};
    std::atomic<float>* fltType = nullptr;
    std::atomic<float>* oscType[2] {};
    std::atomic<float>* oscWarp[2] {};
    Knob* vowelKnob = nullptr;
    Knob* warpKnob[2] {};
    Knob* posKnob[2] {};
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
