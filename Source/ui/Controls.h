#pragma once

#include <juce_audio_processors/juce_audio_processors.h>
#include "VoltLookAndFeel.h"
#include "../Params.h"

namespace volt::ui
{
// Slider with relative dragging, Shift for fine adjustment, double-click reset and a value tooltip.
class FineSlider final : public juce::Slider
{
public:
    FineSlider() = default;

    void mouseDown (const juce::MouseEvent& e) override
    {
        lastPos = e.position;
        dragging = true;
        juce::Slider::mouseDown (e);
        if (onHover) onHover();
    }

    void mouseDrag (const juce::MouseEvent& e) override
    {
        if (! isEnabled() || e.mods.isPopupMenu())
            return;
        const auto delta = e.position - lastPos;
        lastPos = e.position;
        const bool horizontal = isHorizontal();
        const float px = horizontal ? delta.x : (delta.x - delta.y);
        const double speed = e.mods.isShiftDown() ? (1.0 / 1500.0) : (horizontal ? 1.0 / (double) juce::jmax (40, getWidth()) : 1.0 / 220.0);
        const double prop = juce::jlimit (0.0, 1.0, valueToProportionOfLength (getValue()) + px * speed);
        setValue (proportionOfLengthToValue (prop), juce::sendNotificationSync);
    }

    void mouseUp (const juce::MouseEvent& e) override
    {
        dragging = false;
        juce::Slider::mouseUp (e);
        if (onHover) onHover();
    }

    void mouseEnter (const juce::MouseEvent& e) override { hovering = true; juce::Slider::mouseEnter (e); if (onHover) onHover(); }
    void mouseExit (const juce::MouseEvent& e) override { hovering = false; juce::Slider::mouseExit (e); if (onHover) onHover(); }

    juce::String getTooltip() override
    {
        return displayName + ": " + getTextFromValue (getValue()) + "   (Shift: fine, double-click: reset)";
    }

    bool isActive() const noexcept { return hovering || dragging; }

    juce::String displayName;
    std::function<void()> onHover;

private:
    juce::Point<float> lastPos;
    bool dragging = false, hovering = false;
};

class Knob final : public juce::Component
{
public:
    Knob (juce::AudioProcessorValueTreeState& state, int param, const juce::String& caption, bool big = false);

    void resized() override;
    void paint (juce::Graphics&) override {}
    void updateCaption();

    FineSlider slider;
    juce::Label label;
    bool isBig;

private:
    juce::String captionText;
    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> attachment;
};

class ParamCombo final : public juce::ComboBox
{
public:
    ParamCombo (juce::AudioProcessorValueTreeState& state, int param);
    juce::String getTooltip() override { return spec (paramIndex).name + ": " + getText(); }

private:
    int paramIndex;
    std::unique_ptr<juce::AudioProcessorValueTreeState::ComboBoxAttachment> attachment;
};

class ParamToggle final : public juce::TextButton
{
public:
    ParamToggle (juce::AudioProcessorValueTreeState& state, int param, const juce::String& buttonText);

private:
    std::unique_ptr<juce::AudioProcessorValueTreeState::ButtonAttachment> attachment;
};

// Compact horizontal bipolar slider used for modulation amounts.
class AmountSlider final : public juce::Component
{
public:
    AmountSlider (juce::AudioProcessorValueTreeState& state, int param);
    void resized() override { slider.setBounds (getLocalBounds()); }
    FineSlider slider;

private:
    std::unique_ptr<juce::AudioProcessorValueTreeState::SliderAttachment> attachment;
};
} // namespace volt::ui
