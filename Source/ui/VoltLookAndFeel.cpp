#include "VoltLookAndFeel.h"
#include "VoltFontData.h"

namespace volt::ui
{
namespace
{
juce::Typeface::Ptr typeface (bool bold)
{
    static juce::Typeface::Ptr regular = juce::Typeface::createSystemTypefaceFor (VoltFontData::InterRegular_ttf,
                                                                                VoltFontData::InterRegular_ttfSize);
    static juce::Typeface::Ptr semi = juce::Typeface::createSystemTypefaceFor (VoltFontData::InterSemiBold_ttf,
                                                                             VoltFontData::InterSemiBold_ttfSize);
    return bold ? semi : regular;
}
} // namespace

juce::Font VoltLookAndFeel::font (float size, bool bold)
{
    return juce::Font (juce::FontOptions (typeface (bold)).withHeight (size));
}

juce::Colour VoltLookAndFeel::accentOf (const juce::Component& c)
{
    const auto v = c.getProperties()["accent"];
    return v.isVoid() ? colours::osc : juce::Colour ((juce::uint32) (juce::int64) v);
}

void VoltLookAndFeel::setAccent (juce::Component& c, juce::Colour colour)
{
    c.getProperties().set ("accent", (juce::int64) colour.getARGB());
    c.setColour (juce::ComboBox::arrowColourId, colour);
    c.setColour (juce::TextButton::buttonOnColourId, colour);
}

juce::Typeface::Ptr VoltLookAndFeel::getTypefaceForFont (const juce::Font& f)
{
    if (f.getTypefaceName() == juce::Font::getDefaultSansSerifFontName())
        return typeface (f.isBold());
    return LookAndFeel_V4::getTypefaceForFont (f);
}

VoltLookAndFeel::VoltLookAndFeel()
{
    using namespace colours;
    setColour (juce::ResizableWindow::backgroundColourId, background);
    setColour (juce::Label::textColourId, text);
    setColour (juce::ComboBox::backgroundColourId, field);
    setColour (juce::ComboBox::textColourId, text);
    setColour (juce::ComboBox::outlineColourId, panelBorder);
    setColour (juce::ComboBox::arrowColourId, dimText);
    setColour (juce::PopupMenu::backgroundColourId, juce::Colour (0xff1d2026));
    setColour (juce::PopupMenu::textColourId, text);
    setColour (juce::PopupMenu::highlightedBackgroundColourId, juce::Colour (0xff2f3540));
    setColour (juce::PopupMenu::highlightedTextColourId, juce::Colours::white);
    setColour (juce::PopupMenu::headerTextColourId, dimText);
    setColour (juce::TextEditor::backgroundColourId, field);
    setColour (juce::TextEditor::textColourId, text);
    setColour (juce::TextEditor::outlineColourId, panelBorder);
    setColour (juce::TextEditor::focusedOutlineColourId, text.withAlpha (0.4f));
    setColour (juce::TextEditor::highlightColourId, text.withAlpha (0.2f));
    setColour (juce::CaretComponent::caretColourId, text);
    setColour (juce::TextButton::buttonColourId, field);
    setColour (juce::TextButton::buttonOnColourId, osc);
    setColour (juce::TextButton::textColourOffId, text);
    setColour (juce::TextButton::textColourOnId, juce::Colours::black);
    setColour (juce::TooltipWindow::backgroundColourId, juce::Colour (0xf2262a31));
    setColour (juce::TooltipWindow::textColourId, text);
    setColour (juce::TooltipWindow::outlineColourId, panelBorder.brighter (0.3f));
    setColour (juce::AlertWindow::backgroundColourId, panel);
    setColour (juce::AlertWindow::textColourId, text);
    setColour (juce::AlertWindow::outlineColourId, panelBorder.brighter (0.3f));
}

void VoltLookAndFeel::drawRotarySlider (juce::Graphics& g, int x, int y, int w, int h, float pos, float start, float end,
                                        juce::Slider& s)
{
    using namespace colours;
    const auto accent = accentOf (s);
    const auto bounds = juce::Rectangle<float> ((float) x, (float) y, (float) w, (float) h).reduced (1.5f);
    const float size = juce::jmin (bounds.getWidth(), bounds.getHeight());
    const auto c = bounds.getCentre();
    const float r = size * 0.5f;
    const float stroke = juce::jlimit (2.5f, 5.0f, r * 0.14f);
    const float arcR = r - stroke * 0.5f;
    const bool enabled = s.isEnabled();
    const float angle = start + pos * (end - start);

    juce::Path trackPath;
    trackPath.addCentredArc (c.x, c.y, arcR, arcR, 0.0f, start, end, true);
    g.setColour (track);
    g.strokePath (trackPath, juce::PathStrokeType (stroke, juce::PathStrokeType::curved, juce::PathStrokeType::butt));

    const bool bipolar = s.getProperties().getWithDefault ("bipolar", false);
    const float from = bipolar ? (start + end) * 0.5f : start;
    if (std::abs (angle - from) > 0.001f)
    {
        juce::Path valuePath;
        valuePath.addCentredArc (c.x, c.y, arcR, arcR, 0.0f, juce::jmin (from, angle), juce::jmax (from, angle), true);
        g.setColour (enabled ? accent : dimText.withAlpha (0.6f));
        g.strokePath (valuePath, juce::PathStrokeType (stroke, juce::PathStrokeType::curved, juce::PathStrokeType::butt));
    }

    // flat cap
    const float bodyR = arcR - stroke * 1.25f;
    g.setColour (s.isMouseOverOrDragging() ? juce::Colour (0xff343a44) : juce::Colour (0xff2a2f37));
    g.fillEllipse (c.x - bodyR, c.y - bodyR, bodyR * 2.0f, bodyR * 2.0f);

    const juce::Point<float> a (c.x + bodyR * 0.30f * std::sin (angle), c.y - bodyR * 0.30f * std::cos (angle));
    const juce::Point<float> b (c.x + bodyR * 0.92f * std::sin (angle), c.y - bodyR * 0.92f * std::cos (angle));
    g.setColour (enabled ? text : dimText);
    g.drawLine ({ a, b }, juce::jmax (1.6f, stroke * 0.6f));
}

void VoltLookAndFeel::drawLinearSlider (juce::Graphics& g, int x, int y, int w, int h, float pos, float, float,
                                        juce::Slider::SliderStyle, juce::Slider& s)
{
    using namespace colours;
    const auto accent = accentOf (s);
    const auto r = juce::Rectangle<float> ((float) x, (float) y, (float) w, (float) h).reduced (1.0f, (float) h * 0.34f);
    g.setColour (track);
    g.fillRoundedRectangle (r, r.getHeight() * 0.5f);
    const bool bipolar = s.getProperties().getWithDefault ("bipolar", false);
    const float centre = bipolar ? r.getCentreX() : r.getX();
    const float px = juce::jlimit (r.getX(), r.getRight(), pos);
    g.setColour (s.isEnabled() ? accent : dimText);
    g.fillRect (juce::Rectangle<float>::leftTopRightBottom (juce::jmin (centre, px), r.getY(), juce::jmax (centre, px), r.getBottom()));
    if (bipolar)
    {
        g.setColour (dimText.withAlpha (0.6f));
        g.fillRect (juce::Rectangle<float> (centre - 0.5f, r.getY() - 2.0f, 1.0f, r.getHeight() + 4.0f));
    }
    g.setColour (text);
    g.fillEllipse (juce::Rectangle<float> (7.0f, 7.0f).withCentre ({ px, r.getCentreY() }));
}

void VoltLookAndFeel::drawComboBox (juce::Graphics& g, int w, int h, bool, int, int, int, int, juce::ComboBox& box)
{
    using namespace colours;
    const auto r = juce::Rectangle<float> (0.0f, 0.0f, (float) w, (float) h).reduced (0.5f);
    g.setColour (box.isMouseOver (true) ? field.brighter (0.08f) : field);
    g.fillRoundedRectangle (r, 3.0f);
    g.setColour (panelBorder);
    g.drawRoundedRectangle (r, 3.0f, 1.0f);
    const float ax = (float) w - 10.0f, ay = (float) h * 0.5f;
    juce::Path arrow;
    arrow.startNewSubPath (ax - 3.5f, ay - 1.8f);
    arrow.lineTo (ax, ay + 1.8f);
    arrow.lineTo (ax + 3.5f, ay - 1.8f);
    g.setColour (box.isEnabled() ? box.findColour (juce::ComboBox::arrowColourId) : dimText.withAlpha (0.5f));
    g.strokePath (arrow, juce::PathStrokeType (1.6f, juce::PathStrokeType::curved, juce::PathStrokeType::rounded));
}

juce::Font VoltLookAndFeel::getComboBoxFont (juce::ComboBox& box)
{
    return font (juce::jmin (13.5f, (float) box.getHeight() * 0.62f));
}

void VoltLookAndFeel::positionComboBoxText (juce::ComboBox& box, juce::Label& label)
{
    label.setBounds (5, 0, box.getWidth() - 20, box.getHeight());
    label.setFont (getComboBoxFont (box));
}

juce::PopupMenu::Options VoltLookAndFeel::getOptionsForComboBoxPopupMenu (juce::ComboBox& box, juce::Label& label)
{
    return LookAndFeel_V4::getOptionsForComboBoxPopupMenu (box, label).withStandardItemHeight (juce::jmax (20, box.getHeight()));
}

void VoltLookAndFeel::drawButtonBackground (juce::Graphics& g, juce::Button& b, const juce::Colour&, bool over, bool down)
{
    using namespace colours;
    const auto r = b.getLocalBounds().toFloat().reduced (0.5f);
    const bool on = b.getToggleState();
    const auto accent = b.findColour (juce::TextButton::buttonOnColourId);
    g.setColour (on ? accent : (over || down ? field.brighter (0.1f) : field));
    g.fillRoundedRectangle (r, 3.0f);
    g.setColour (on ? accent : panelBorder);
    g.drawRoundedRectangle (r, 3.0f, 1.0f);
}

void VoltLookAndFeel::drawButtonText (juce::Graphics& g, juce::TextButton& b, bool, bool)
{
    g.setFont (getTextButtonFont (b, b.getHeight()));
    g.setColour (b.getToggleState() ? juce::Colour (0xff121417) : colours::text);
    g.drawFittedText (b.getButtonText(), b.getLocalBounds().reduced (4, 0), juce::Justification::centred, 1);
}

juce::Font VoltLookAndFeel::getTextButtonFont (juce::TextButton&, int h)
{
    return font (juce::jmin (13.0f, (float) h * 0.58f), true);
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
    g.drawFittedText (text, juce::Rectangle<int> (w, h).reduced (7, 2), juce::Justification::centred, 2);
}

juce::Rectangle<int> VoltLookAndFeel::getTooltipBounds (const juce::String& text, juce::Point<int> pos, juce::Rectangle<int> parent)
{
    const int w = juce::jmin (360, juce::GlyphArrangement::getStringWidthInt (font (13.0f), text) + 18);
    const int h = 24;
    return juce::Rectangle<int> (pos.x > parent.getCentreX() ? pos.x - (w + 12) : pos.x + 18,
                                 pos.y > parent.getCentreY() ? pos.y - (h + 6) : pos.y + 6, w, h)
        .constrainedWithin (parent);
}

juce::Font VoltLookAndFeel::getPopupMenuFont() { return font (14.0f); }
juce::Font VoltLookAndFeel::getLabelFont (juce::Label& l) { return l.getFont(); }
juce::Font VoltLookAndFeel::getSliderPopupFont (juce::Slider&) { return font (13.0f); }
juce::Font VoltLookAndFeel::getAlertWindowTitleFont() { return font (17.0f, true); }
juce::Font VoltLookAndFeel::getAlertWindowMessageFont() { return font (14.0f); }
juce::Font VoltLookAndFeel::getAlertWindowFont() { return font (13.0f); }
} // namespace volt::ui
