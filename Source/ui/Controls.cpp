#include "Controls.h"

namespace volt::ui
{
void ValueText::paint (juce::Graphics& g)
{
    int split = 0;
    while (split < text.length() && juce::String ("+-0123456789.").containsChar (text[split]))
        ++split;
    const auto number = text.substring (0, split);
    const auto unit = text.substring (split).trim();
    const auto f = VoltLookAndFeel::font (size, bold);
    if (number.isEmpty() || unit.isEmpty() || unit.containsAnyOf ("0123456789/"))
    {
        g.setFont (f);
        g.setColour (colour);
        g.drawText (text, getLocalBounds(), justification);
        return;
    }
    const auto uf = VoltLookAndFeel::font (size * 0.82f, false);
    const float nw = juce::GlyphArrangement::getStringWidth (f, number);
    const float uw = juce::GlyphArrangement::getStringWidth (uf, unit);
    const float total = nw + 2.0f + uw;
    float x = justification.testFlags (juce::Justification::left) ? 0.0f
            : justification.testFlags (juce::Justification::right) ? (float) getWidth() - total
            : ((float) getWidth() - total) * 0.5f;
    const auto h = (float) getHeight();
    g.setFont (f);
    g.setColour (colour);
    g.drawText (number, juce::Rectangle<float> (x, 0.0f, nw + 1.0f, h), juce::Justification::centredLeft);
    g.setFont (uf);
    g.setColour (colours::dimText);
    g.drawText (unit, juce::Rectangle<float> (x + nw + 2.0f, size * 0.07f, uw + 1.0f, h), juce::Justification::centredLeft);
}

Knob::Knob (juce::AudioProcessorValueTreeState& state, int param, const juce::String& caption, juce::Colour accentColour,
            int knobSize)
    : size (knobSize), accent (accentColour)
{
    const auto& s = spec (param);
    slider.setSliderStyle (juce::Slider::RotaryHorizontalVerticalDrag);
    slider.setTextBoxStyle (juce::Slider::NoTextBox, false, 0, 0);
    slider.setRotaryParameters (juce::MathConstants<float>::pi * 1.25f, juce::MathConstants<float>::pi * 2.75f, true);
    slider.displayName = s.name;
    slider.getProperties().set ("bipolar", s.minValue < 0.0f && std::abs (s.minValue + s.maxValue) < 1.0e-6f);
    slider.getProperties().set ("hero", size == Hero);
    VoltLookAndFeel::setAccent (slider, accent);
    slider.setScrollWheelEnabled (true);
    addAndMakeVisible (slider);

    label.setText (caption, juce::dontSendNotification);
    label.setJustificationType (juce::Justification::centred);
    label.setFont (VoltLookAndFeel::font (size == Hero ? 13.5f : 11.5f, size == Hero));
    label.setColour (juce::Label::textColourId, size == Hero ? colours::text : colours::dimText);
    label.setInterceptsMouseClicks (false, false);
    label.setMinimumHorizontalScale (0.8f);
    label.setBorderSize ({ 0, 0, 0, 0 });
    addAndMakeVisible (label);

    value.size = size == Hero ? 13.5f : (size == Medium ? 12.0f : 11.5f);
    value.bold = size == Hero;
    addAndMakeVisible (value);

    attachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment> (state, s.id, slider);
    slider.setDoubleClickReturnValue (true, s.defaultValue);
    slider.onHover = [this] { updateValue(); };
    slider.onValueChange = [this] { updateValue(); };
    updateValue();
}

void Knob::updateValue()
{
    value.setText (slider.getTextFromValue (slider.getValue()));
    value.setTextColour (slider.isActive() ? accent : colours::value);
}

void Knob::setMacroMark (bool on)
{
    if ((bool) slider.getProperties().getWithDefault ("macroMark", false) != on)
    {
        slider.getProperties().set ("macroMark", on);
        slider.repaint();
    }
}

void Knob::resized()
{
    auto r = getLocalBounds();
    const int th = size == Hero ? 17 : 14;
    label.setBounds (r.removeFromTop (th).expanded (6, 0));
    value.setBounds (r.removeFromBottom (th).expanded (6, 0));
    const int side = juce::jmin (r.getWidth(), r.getHeight());
    slider.setBounds (r.withSizeKeepingCentre (side, side));
}

MacroCell::MacroCell (juce::AudioProcessorValueTreeState& state, int param)
{
    const auto& s = spec (param);
    slider.setSliderStyle (juce::Slider::RotaryHorizontalVerticalDrag);
    slider.setTextBoxStyle (juce::Slider::NoTextBox, false, 0, 0);
    slider.setRotaryParameters (juce::MathConstants<float>::pi * 1.25f, juce::MathConstants<float>::pi * 2.75f, true);
    slider.displayName = s.name;
    slider.getProperties().set ("hero", true);
    VoltLookAndFeel::setAccent (slider, colours::macro);
    slider.setScrollWheelEnabled (true);
    addAndMakeVisible (slider);

    name.setFont (VoltLookAndFeel::font (17.0f, true));
    name.setColour (juce::Label::textColourId, colours::text);
    name.setColour (juce::Label::textWhenEditingColourId, colours::text);
    name.setColour (juce::Label::backgroundWhenEditingColourId, colours::field);
    name.setJustificationType (juce::Justification::centredLeft);
    name.setBorderSize ({ 0, 0, 0, 0 });
    name.setMinimumHorizontalScale (0.75f);
    name.setEditable (false, true, false);
    name.setTooltip ("Double-click to rename");
    addAndMakeVisible (name);

    value.size = 13.5f;
    value.bold = true;
    value.justification = juce::Justification::centredLeft;
    value.setTextColour (colours::macro);
    addAndMakeVisible (value);

    attachment = std::make_unique<juce::AudioProcessorValueTreeState::SliderAttachment> (state, s.id, slider);
    slider.setDoubleClickReturnValue (true, s.defaultValue);
    slider.onValueChange = [this] { value.setText (slider.getTextFromValue (slider.getValue())); };
    slider.onValueChange();
}

void MacroCell::resized()
{
    const int side = juce::jmin (getHeight(), 84);
    slider.setBounds (0, (getHeight() - side) / 2, side, side);
    const int x = side + 8, cy = getHeight() / 2;
    name.setBounds (x, cy - 30, getWidth() - x, 22);
    value.setBounds (x, cy + 10, getWidth() - x, 18);
}

void MacroCell::paint (juce::Graphics& g)
{
    const int x = juce::jmin (getHeight(), 84) + 8;
    g.setFont (VoltLookAndFeel::font (11.5f));
    g.setColour (colours::dimText);
    g.drawFittedText (target.isEmpty() ? juce::String ("not assigned") : target, x, getHeight() / 2 - 7, getWidth() - x, 15,
                      juce::Justification::centredLeft, 1, 0.8f);
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
    value.setColour (juce::Label::textColourId, colours::value);
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
