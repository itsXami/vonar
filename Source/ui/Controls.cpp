#include "Controls.h"

namespace volt::ui
{
Knob::Knob (juce::AudioProcessorValueTreeState& state, int param, const juce::String& caption, juce::Colour accentColour,
            bool big)
    : isBig (big), accent (accentColour)
{
    const auto& s = spec (param);
    slider.setSliderStyle (juce::Slider::RotaryHorizontalVerticalDrag);
    slider.setTextBoxStyle (juce::Slider::NoTextBox, false, 0, 0);
    slider.setRotaryParameters (juce::MathConstants<float>::pi * 1.25f, juce::MathConstants<float>::pi * 2.75f, true);
    slider.displayName = s.name;
    slider.getProperties().set ("bipolar", s.minValue < 0.0f && std::abs (s.minValue + s.maxValue) < 1.0e-6f);
    VoltLookAndFeel::setAccent (slider, accent);
    slider.setScrollWheelEnabled (true);
    addAndMakeVisible (slider);

    label.setText (caption, juce::dontSendNotification);
    label.setJustificationType (juce::Justification::centred);
    label.setFont (VoltLookAndFeel::font (big ? 13.5f : 12.0f, big));
    label.setColour (juce::Label::textColourId, big ? colours::text : colours::dimText.brighter (0.25f));
    label.setInterceptsMouseClicks (false, false);
    label.setMinimumHorizontalScale (0.75f);
    label.setBorderSize ({ 0, 0, 0, 0 });
    addAndMakeVisible (label);

    value.setJustificationType (juce::Justification::centred);
    value.setFont (VoltLookAndFeel::font (big ? 13.0f : 11.5f));
    value.setColour (juce::Label::textColourId, colours::text);
    value.setInterceptsMouseClicks (false, false);
    value.setMinimumHorizontalScale (0.7f);
    value.setBorderSize ({ 0, 0, 0, 0 });
    addAndMakeVisible (value);

    attachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment> (state, s.id, slider);
    slider.setDoubleClickReturnValue (true, s.defaultValue);
    slider.onHover = [this] { updateValue(); };
    slider.onValueChange = [this] { updateValue(); };
    updateValue();
}

void Knob::updateValue()
{
    value.setText (slider.getTextFromValue (slider.getValue()), juce::dontSendNotification);
    value.setColour (juce::Label::textColourId, slider.isActive() ? accent : colours::text.withAlpha (0.85f));
}

void Knob::resized()
{
    auto r = getLocalBounds();
    label.setBounds (r.removeFromTop (isBig ? 17 : 14).expanded (4, 0));
    value.setBounds (r.removeFromBottom (isBig ? 17 : 14).expanded (4, 0));
    r.removeFromBottom (1);
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

AmountSlider::AmountSlider (juce::AudioProcessorValueTreeState& state, int param, juce::Colour accent)
{
    const auto& s = spec (param);
    slider.setSliderStyle (juce::Slider::LinearHorizontal);
    slider.setTextBoxStyle (juce::Slider::NoTextBox, false, 0, 0);
    slider.getProperties().set ("bipolar", true);
    VoltLookAndFeel::setAccent (slider, accent);
    slider.displayName = s.name;
    addAndMakeVisible (slider);
    value.setFont (VoltLookAndFeel::font (12.0f));
    value.setJustificationType (juce::Justification::centredRight);
    value.setColour (juce::Label::textColourId, colours::text.withAlpha (0.85f));
    value.setBorderSize ({ 0, 0, 0, 2 });
    value.setInterceptsMouseClicks (false, false);
    addAndMakeVisible (value);
    attachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment> (state, s.id, slider);
    slider.setDoubleClickReturnValue (true, s.defaultValue);
    slider.onValueChange = [this] {
        const int pct = juce::roundToInt (slider.getValue() * 100.0);
        value.setText ((pct > 0 ? "+" : "") + juce::String (pct) + "%", juce::dontSendNotification);
    };
    slider.onValueChange();
}

void AmountSlider::resized()
{
    auto r = getLocalBounds();
    value.setBounds (r.removeFromRight (38));
    slider.setBounds (r);
}
} // namespace volt::ui
