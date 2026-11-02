#include "VoltLookAndFeel.h"

namespace volt::ui
{
VoltLookAndFeel::VoltLookAndFeel()
{
    using namespace colours;
    setColour (juce::ResizableWindow::backgroundColourId, background);
    setColour (juce::Label::textColourId, text);
    setColour (juce::ComboBox::backgroundColourId, field);
    setColour (juce::ComboBox::textColourId, text);
    setColour (juce::ComboBox::outlineColourId, panelBorder);
    setColour (juce::ComboBox::arrowColourId, accent);
    setColour (juce::PopupMenu::backgroundColourId, juce::Colour (0xff1a1d22));
    setColour (juce::PopupMenu::textColourId, text);
    setColour (juce::PopupMenu::highlightedBackgroundColourId, accent.withAlpha (0.85f));
    setColour (juce::PopupMenu::highlightedTextColourId, juce::Colours::black);
    setColour (juce::PopupMenu::headerTextColourId, accent);
    setColour (juce::TextEditor::backgroundColourId, field);
    setColour (juce::TextEditor::textColourId, text);
    setColour (juce::TextEditor::outlineColourId, panelBorder);
    setColour (juce::TextEditor::focusedOutlineColourId, accent.withAlpha (0.7f));
    setColour (juce::TextEditor::highlightColourId, accent.withAlpha (0.35f));
    setColour (juce::CaretComponent::caretColourId, accent);
    setColour (juce::TextButton::buttonColourId, field);
    setColour (juce::TextButton::buttonOnColourId, accent);
    setColour (juce::TextButton::textColourOffId, text);
    setColour (juce::TextButton::textColourOnId, juce::Colours::black);
    setColour (juce::Slider::textBoxTextColourId, text);
    setColour (juce::Slider::textBoxBackgroundColourId, field);
    setColour (juce::Slider::textBoxOutlineColourId, panelBorder);
    setColour (juce::BubbleComponent::backgroundColourId, juce::Colour (0xf0202429));
    setColour (juce::BubbleComponent::outlineColourId, accent.withAlpha (0.6f));
    setColour (juce::TooltipWindow::backgroundColourId, juce::Colour (0xf0202429));
    setColour (juce::TooltipWindow::textColourId, text);
    setColour (juce::TooltipWindow::outlineColourId, accent.withAlpha (0.6f));
    setColour (juce::AlertWindow::backgroundColourId, panel);
    setColour (juce::AlertWindow::textColourId, text);
    setColour (juce::AlertWindow::outlineColourId, accent.withAlpha (0.5f));
}

juce::Font VoltLookAndFeel::font (float size, bool bold)
{
    return juce::Font (juce::FontOptions (size, bold ? juce::Font::bold : juce::Font::plain));
}

void VoltLookAndFeel::drawRotarySlider (juce::Graphics& g, int x, int y, int w, int h, float pos, float start, float end,
                                        juce::Slider& s)
{
    using namespace colours;
    const auto bounds = juce::Rectangle<float> ((float) x, (float) y, (float) w, (float) h).reduced (2.0f);
    const float size = juce::jmin (bounds.getWidth(), bounds.getHeight());
    const auto c = bounds.getCentre();
    const float r = size * 0.5f;
    const float stroke = juce::jmax (2.5f, r * 0.13f);
    const float arcR = r - stroke * 0.5f;
    const bool enabled = s.isEnabled();
    const float angle = start + pos * (end - start);

    // background track
    juce::Path trackPath;
    trackPath.addCentredArc (c.x, c.y, arcR, arcR, 0.0f, start, end, true);
    g.setColour (track);
    g.strokePath (trackPath, juce::PathStrokeType (stroke, juce::PathStrokeType::curved, juce::PathStrokeType::rounded));

    // value arc: from the centre for bipolar parameters, else from the start
    const bool bipolar = s.getProperties().getWithDefault ("bipolar", false);
    const float from = bipolar ? (start + end) * 0.5f : start;
    if (std::abs (angle - from) > 0.001f)
    {
        juce::Path valuePath;
        valuePath.addCentredArc (c.x, c.y, arcR, arcR, 0.0f, juce::jmin (from, angle), juce::jmax (from, angle), true);
        g.setColour (enabled ? accent : dimText);
        g.strokePath (valuePath, juce::PathStrokeType (stroke, juce::PathStrokeType::curved, juce::PathStrokeType::rounded));
    }

    // body
    const float bodyR = arcR - stroke * 1.1f;
    g.setColour (juce::Colour (0xff1f2329));
    g.fillEllipse (c.x - bodyR, c.y - bodyR, bodyR * 2.0f, bodyR * 2.0f);
    g.setColour (panelBorder.brighter (0.15f));
    g.drawEllipse (c.x - bodyR, c.y - bodyR, bodyR * 2.0f, bodyR * 2.0f, 1.0f);

    // pointer
    const float p0 = bodyR * 0.25f, p1 = bodyR * 0.85f;
    const juce::Point<float> a (c.x + p0 * std::sin (angle), c.y - p0 * std::cos (angle));
    const juce::Point<float> b (c.x + p1 * std::sin (angle), c.y - p1 * std::cos (angle));
    g.setColour (enabled ? text : dimText);
    g.drawLine ({ a, b }, juce::jmax (1.5f, stroke * 0.55f));
}

void VoltLookAndFeel::drawLinearSlider (juce::Graphics& g, int x, int y, int w, int h, float pos, float, float,
                                        juce::Slider::SliderStyle, juce::Slider& s)
{
    using namespace colours;
    const auto r = juce::Rectangle<float> ((float) x, (float) y, (float) w, (float) h).reduced (1.0f, (float) h * 0.28f);
    g.setColour (track);
    g.fillRoundedRectangle (r, 2.0f);
    const bool bipolar = s.getProperties().getWithDefault ("bipolar", false);
    const float centre = bipolar ? r.getCentreX() : r.getX();
    const float px = juce::jlimit (r.getX(), r.getRight(), pos);
    g.setColour (s.isEnabled() ? accent : dimText);
    g.fillRoundedRectangle (juce::Rectangle<float>::leftTopRightBottom (juce::jmin (centre, px), r.getY(), juce::jmax (centre, px), r.getBottom()), 2.0f);
    g.setColour (text);
    g.fillRect (juce::Rectangle<float> (px - 1.0f, r.getY() - 2.0f, 2.0f, r.getHeight() + 4.0f));
}

void VoltLookAndFeel::drawComboBox (juce::Graphics& g, int w, int h, bool, int, int, int, int, juce::ComboBox& box)
{
    using namespace colours;
    const auto r = juce::Rectangle<float> (0.0f, 0.0f, (float) w, (float) h).reduced (0.5f);
    g.setColour (field);
    g.fillRoundedRectangle (r, 3.0f);
    g.setColour (box.hasKeyboardFocus (false) ? accent.withAlpha (0.6f) : panelBorder);
    g.drawRoundedRectangle (r, 3.0f, 1.0f);
    const float ax = (float) w - 10.0f, ay = (float) h * 0.5f;
    juce::Path arrow;
    arrow.addTriangle (ax - 3.5f, ay - 1.5f, ax + 3.5f, ay - 1.5f, ax, ay + 2.5f);
    g.setColour (box.isEnabled() ? accent : dimText);
    g.fillPath (arrow);
}

juce::Font VoltLookAndFeel::getComboBoxFont (juce::ComboBox& box)
{
    return font (juce::jmin (13.0f, (float) box.getHeight() * 0.62f));
}

void VoltLookAndFeel::positionComboBoxText (juce::ComboBox& box, juce::Label& label)
{
    label.setBounds (4, 0, box.getWidth() - 18, box.getHeight());
    label.setFont (getComboBoxFont (box));
}

juce::PopupMenu::Options VoltLookAndFeel::getOptionsForComboBoxPopupMenu (juce::ComboBox& box, juce::Label& label)
{
    return LookAndFeel_V4::getOptionsForComboBoxPopupMenu (box, label).withStandardItemHeight (juce::jmax (18, box.getHeight()));
}

void VoltLookAndFeel::drawButtonBackground (juce::Graphics& g, juce::Button& b, const juce::Colour&, bool over, bool down)
{
    using namespace colours;
    const auto r = b.getLocalBounds().toFloat().reduced (0.5f);
    const bool on = b.getToggleState();
    g.setColour (on ? accent : (over || down ? field.brighter (0.12f) : field));
    g.fillRoundedRectangle (r, 3.0f);
    g.setColour (on ? accent : panelBorder);
    g.drawRoundedRectangle (r, 3.0f, 1.0f);
}

void VoltLookAndFeel::drawButtonText (juce::Graphics& g, juce::TextButton& b, bool, bool)
{
    g.setFont (getTextButtonFont (b, b.getHeight()));
    g.setColour (b.getToggleState() ? juce::Colours::black : colours::text);
    g.drawFittedText (b.getButtonText(), b.getLocalBounds().reduced (3, 0), juce::Justification::centred, 1);
}

juce::Font VoltLookAndFeel::getTextButtonFont (juce::TextButton&, int h)
{
    return font (juce::jmin (13.0f, (float) h * 0.6f), true);
}

void VoltLookAndFeel::drawTooltip (juce::Graphics& g, const juce::String& text, int w, int h)
{
    const auto r = juce::Rectangle<float> (0.0f, 0.0f, (float) w, (float) h);
    g.setColour (findColour (juce::TooltipWindow::backgroundColourId));
    g.fillRoundedRectangle (r, 3.0f);
    g.setColour (findColour (juce::TooltipWindow::outlineColourId));
    g.drawRoundedRectangle (r.reduced (0.5f), 3.0f, 1.0f);
    g.setColour (findColour (juce::TooltipWindow::textColourId));
    g.setFont (font (13.0f));
    g.drawFittedText (text, juce::Rectangle<int> (w, h).reduced (6, 2), juce::Justification::centred, 2);
}

juce::Rectangle<int> VoltLookAndFeel::getTooltipBounds (const juce::String& text, juce::Point<int> pos, juce::Rectangle<int> parent)
{
    const int w = juce::jmin (320, juce::GlyphArrangement::getStringWidthInt (font (13.0f), text) + 16);
    const int h = 22;
    return juce::Rectangle<int> (pos.x > parent.getCentreX() ? pos.x - (w + 12) : pos.x + 18,
                                 pos.y > parent.getCentreY() ? pos.y - (h + 6) : pos.y + 6, w, h)
        .constrainedWithin (parent);
}

juce::Font VoltLookAndFeel::getPopupMenuFont() { return font (14.0f); }
juce::Font VoltLookAndFeel::getLabelFont (juce::Label& l) { return l.getFont(); }
juce::Font VoltLookAndFeel::getSliderPopupFont (juce::Slider&) { return font (13.0f); }
} // namespace volt::ui
