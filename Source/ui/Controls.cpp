#include "Controls.h"

namespace volt::ui
{
Knob::Knob (juce::AudioProcessorValueTreeState& state, int param, const juce::String& caption, bool big)
    : isBig (big), captionText (caption)
{
    const auto& s = spec (param);
    slider.setSliderStyle (juce::Slider::RotaryHorizontalVerticalDrag);
    slider.setTextBoxStyle (juce::Slider::NoTextBox, false, 0, 0);
    slider.setRotaryParameters (juce::MathConstants<float>::pi * 1.25f, juce::MathConstants<float>::pi * 2.75f, true);
    slider.displayName = s.name;
    slider.getProperties().set ("bipolar", s.minValue < 0.0f && std::abs (s.minValue + s.maxValue) < 1.0e-6f);
    slider.setScrollWheelEnabled (true);
    addAndMakeVisible (slider);

    label.setJustificationType (juce::Justification::centred);
    label.setFont (VoltLookAndFeel::font (big ? 12.5f : 11.0f, big));
    label.setColour (juce::Label::textColourId, big ? colours::text : colours::dimText);
    label.setInterceptsMouseClicks (false, false);
    label.setMinimumHorizontalScale (0.7f);
    addAndMakeVisible (label);

    attachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment> (state, s.id, slider);
    slider.setDoubleClickReturnValue (true, s.defaultValue);
    slider.onHover = [this] { updateCaption(); };
    slider.onValueChange = [this] { if (slider.isActive()) updateCaption(); };
    updateCaption();
}

void Knob::updateCaption()
{
    if (slider.isActive())
    {
        label.setText (slider.getTextFromValue (slider.getValue()), juce::dontSendNotification);
        label.setColour (juce::Label::textColourId, colours::accent);
    }
    else
    {
        label.setText (captionText, juce::dontSendNotification);
        label.setColour (juce::Label::textColourId, isBig ? colours::text : colours::dimText);
    }
}

void Knob::resized()
{
    auto r = getLocalBounds();
    const int labelH = isBig ? 16 : 13;
    label.setBounds (r.removeFromBottom (labelH).expanded (isBig ? 2 : 6, 0));
    const int side = juce::jmin (r.getWidth(), r.getHeight());
    slider.setBounds (r.withSizeKeepingCentre (side, side));
}

ParamCombo::ParamCombo (juce::AudioProcessorValueTreeState& state, int param) : paramIndex (param)
{
    const auto& s = spec (param);
    addItemList (s.choices, 1);
    setJustificationType (juce::Justification::centredLeft);
    attachment = std::make_unique<juce::AudioProcessorValueTreeState::ComboBoxAttachment> (state, s.id, *this);
}

ParamToggle::ParamToggle (juce::AudioProcessorValueTreeState& state, int param, const juce::String& buttonText)
{
    setButtonText (buttonText);
    setClickingTogglesState (true);
    setTooltip (spec (param).name);
    attachment = std::make_unique<juce::AudioProcessorValueTreeState::ButtonAttachment> (state, spec (param).id, *this);
}

AmountSlider::AmountSlider (juce::AudioProcessorValueTreeState& state, int param)
{
    const auto& s = spec (param);
    slider.setSliderStyle (juce::Slider::LinearHorizontal);
    slider.setTextBoxStyle (juce::Slider::NoTextBox, false, 0, 0);
    slider.getProperties().set ("bipolar", true);
    slider.displayName = s.name;
    addAndMakeVisible (slider);
    attachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment> (state, s.id, slider);
    slider.setDoubleClickReturnValue (true, s.defaultValue);
}
} // namespace volt::ui
