#pragma once

#include "PluginProcessor.h"
#include "ui/Controls.h"
#include "ui/Views.h"
#include "ui/PresetBar.h"

namespace volt::ui
{
// The single 1000 x 620 screen. Everything is laid out in logical pixels; the editor scales it.
class MainPanel final : public juce::Component
{
public:
    static constexpr int kWidth = 1000, kHeight = 620;

    explicit MainPanel (VoltAudioProcessor& p);
    void paint (juce::Graphics&) override;
    void resized() override {}
    void refresh(); // called by the editor timer (30 Hz)

    PresetBar presetBar;

private:
    struct Section { juce::String title; juce::Rectangle<int> bounds; };

    Knob& knob (int param, const juce::String& caption, juce::Rectangle<int> r, bool big = false);
    ParamCombo& combo (int param, juce::Rectangle<int> r);
    ParamToggle& toggle (int param, const juce::String& text, juce::Rectangle<int> r);
    void section (const juce::String& title, juce::Rectangle<int> r) { sections.push_back ({ title, r }); }
    void subLabel (const juce::String& text, juce::Rectangle<int> r) { subLabels.push_back ({ text, r }); }
    void buildOsc (int o, juce::Rectangle<int> r);
    void buildLfo (int l, juce::Rectangle<int> r);

    VoltAudioProcessor& processor;
    juce::AudioProcessorValueTreeState& state;
    std::vector<std::unique_ptr<juce::Component>> owned;
    std::vector<Section> sections;
    std::vector<Section> subLabels;
    std::unique_ptr<WavetableView> wtView[2];
    ScopeView scope;
    Knob* macroKnobs[kNumMacros] {};
    Knob* lfoRate[2] {};
    ParamCombo* lfoDiv[2] {};
    std::atomic<float>* lfoSync[2] {};
    std::atomic<float>* fltType = nullptr;
    Knob* vowelKnob = nullptr;
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
