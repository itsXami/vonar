#include "VoltLookAndFeel.h"
#include "VoltFontData.h"

namespace volt::ui
{
namespace
{
juce::Typeface::Ptr typeface (bool bold)
{
    static juce::Typeface::Ptr medium = juce::Typeface::createSystemTypefaceFor (VoltFontData::OxaniumMedium_ttf,
                                                                               VoltFontData::OxaniumMedium_ttfSize);
    static juce::Typeface::Ptr semi = juce::Typeface::createSystemTypefaceFor (VoltFontData::OxaniumSemiBold_ttf,
                                                                             VoltFontData::OxaniumSemiBold_ttfSize);
    return bold ? semi : medium;
}

juce::String styleOf (const juce::Component& c) { return c.getProperties()["style"].toString(); }
} // namespace

juce::Font VoltLookAndFeel::font (float size, bool bold)
{
    return juce::Font (juce::FontOptions (typeface (bold)).withHeight (size));
}

juce::Font VoltLookAndFeel::titleFont (float size)
{
    return font (size, true).withExtraKerningFactor (0.11f);
}

void VoltLookAndFeel::drawDisplay (juce::Graphics& g, juce::Rectangle<float> r)
{
    g.setColour (colours::inset);
    g.fillRoundedRectangle (r, 2.0f);
    g.setColour (juce::Colours::black);
    g.drawRoundedRectangle (r.reduced (0.5f), 2.0f, 1.0f);
    g.setColour (juce::Colours::white.withAlpha (0.06f));
    g.fillRect (r.getX() + 2.0f, r.getBottom(), r.getWidth() - 4.0f, 1.0f);
}

void VoltLookAndFeel::drawSurface (juce::Graphics& g, juce::Rectangle<float> r, juce::Colour fill)
{
    g.setColour (fill);
    g.fillRoundedRectangle (r, 3.0f);
    g.setColour (juce::Colours::white.withAlpha (0.055f));
    g.fillRect (r.getX() + 3.0f, r.getY(), r.getWidth() - 6.0f, 1.0f);
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
    setColour (juce::PopupMenu::backgroundColourId, juce::Colour (0xff1c1a18));
    setColour (juce::PopupMenu::textColourId, text);
    setColour (juce::PopupMenu::highlightedBackgroundColourId, juce::Colour (0xff35312c));
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
    setColour (juce::TooltipWindow::backgroundColourId, juce::Colour (0xf2262321));
    setColour (juce::TooltipWindow::textColourId, text);
    setColour (juce::TooltipWindow::outlineColourId, panelBorder.brighter (0.3f));
    setColour (juce::AlertWindow::backgroundColourId, macroBar);
    setColour (juce::AlertWindow::textColourId, text);
    setColour (juce::AlertWindow::outlineColourId, panelBorder.brighter (0.3f));
}

void VoltLookAndFeel::drawRotarySlider (juce::Graphics& g, int x, int y, int w, int h, float pos, float start, float end,
                                        juce::Slider& s)
{
    using namespace colours;
    const auto accent = accentOf (s);
    const auto bounds = juce::Rectangle<float> ((float) x, (float) y, (float) w, (float) h);
    const float size = juce::jmin (bounds.getWidth(), bounds.getHeight());
    const auto c = bounds.getCentre();
    const bool hero = s.getProperties().getWithDefault ("hero", false);
    const bool enabled = s.isEnabled();
    const float stroke = hero ? 3.0f : 2.0f;
    const float arcR = size * 0.5f - (hero ? 10.0f : 1.5f) - stroke * 0.5f;
    const float capR = arcR - (hero ? 4.5f : 3.5f);
    const float angle = start + pos * (end - start);
    auto polar = [&] (float radius, float a) { return juce::Point<float> (c.x + radius * std::sin (a), c.y - radius * std::cos (a)); };

    if (! enabled)
        g.beginTransparencyLayer (0.34f);

    juce::Path trackPath;
    trackPath.addCentredArc (c.x, c.y, arcR, arcR, 0.0f, start, end, true);
    g.setColour (track);
    g.strokePath (trackPath, juce::PathStrokeType (stroke, juce::PathStrokeType::curved, juce::PathStrokeType::rounded));

    const bool bipolar = s.getProperties().getWithDefault ("bipolar", false);
    const float from = bipolar ? (start + end) * 0.5f : start;
    if (std::abs (angle - from) > 0.001f)
    {
        juce::Path valuePath;
        valuePath.addCentredArc (c.x, c.y, arcR, arcR, 0.0f, juce::jmin (from, angle), juce::jmax (from, angle), true);
        g.setColour (accent);
        g.strokePath (valuePath, juce::PathStrokeType (stroke, juce::PathStrokeType::curved, juce::PathStrokeType::rounded));
    }

    if (hero) // scale: eleven ticks, the ends and the middle a little longer
        for (int k = 0; k <= 10; ++k)
        {
            const float a = start + (end - start) * (float) k / 10.0f;
            const bool major = k == 0 || k == 5 || k == 10;
            g.setColour (major ? dimText : faint);
            g.drawLine ({ polar (arcR + 4.5f, a), polar (arcR + (major ? 8.5f : 6.5f), a) }, 1.0f);
        }

    // shaded cap with a rim and a light edge
    g.setColour (juce::Colours::black.withAlpha (0.55f));
    g.fillEllipse (c.x - capR - 0.5f, c.y - capR + 1.0f, capR * 2.0f + 1.0f, capR * 2.0f + 1.0f);
    const bool lit = s.isMouseOverOrDragging();
    g.setGradientFill (juce::ColourGradient (juce::Colour (lit ? 0xff45413d : 0xff3a3734), c.x, c.y - capR,
                                             juce::Colour (lit ? 0xff282523 : 0xff201e1c), c.x, c.y + capR, false));
    g.fillEllipse (c.x - capR, c.y - capR, capR * 2.0f, capR * 2.0f);
    g.setColour (juce::Colour (0xff0a0908));
    g.drawEllipse (c.x - capR, c.y - capR, capR * 2.0f, capR * 2.0f, 1.0f);
    juce::Path edge;
    edge.addCentredArc (c.x, c.y, capR - 1.0f, capR - 1.0f, 0.0f, -1.08f, 1.08f, true);
    g.setColour (juce::Colours::white.withAlpha (0.11f));
    g.strokePath (edge, juce::PathStrokeType (1.0f));

    g.setColour (text);
    g.drawLine ({ polar (capR * 0.30f, angle), polar (capR - 2.5f, angle) }, hero ? 2.4f : (capR > 13.0f ? 1.8f : 1.5f));

    if (s.getProperties().getWithDefault ("macroMark", false)) // a macro moves this control
    {
        g.setColour (macro);
        g.fillEllipse (juce::Rectangle<float> (4.8f, 4.8f).withCentre ({ c.x, c.y + arcR }));
    }

    if (! enabled)
        g.endTransparencyLayer();
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
    g.setColour (box.isMouseOver (true) ? field.brighter (0.06f) : field);
    g.fillRoundedRectangle (r, 2.0f);
    g.setColour (panelBorder);
    g.drawRoundedRectangle (r, 2.0f, 1.0f);
    const float ax = (float) w - 10.0f, ay = (float) h * 0.5f;
    juce::Path arrow;
    arrow.startNewSubPath (ax - 3.0f, ay - 1.5f);
    arrow.lineTo (ax, ay + 1.8f);
    arrow.lineTo (ax + 3.0f, ay - 1.5f);
    g.setColour (box.isEnabled() ? box.findColour (juce::ComboBox::arrowColourId) : faint);
    g.strokePath (arrow, juce::PathStrokeType (1.4f, juce::PathStrokeType::curved, juce::PathStrokeType::rounded));
}

juce::Font VoltLookAndFeel::getComboBoxFont (juce::ComboBox& box)
{
    return font (juce::jmin (13.0f, (float) box.getHeight() * 0.6f));
}

void VoltLookAndFeel::positionComboBoxText (juce::ComboBox& box, juce::Label& label)
{
    label.setBounds (5, 0, box.getWidth() - 19, box.getHeight());
    label.setFont (getComboBoxFont (box));
}

juce::PopupMenu::Options VoltLookAndFeel::getOptionsForComboBoxPopupMenu (juce::ComboBox& box, juce::Label& label)
{
    return LookAndFeel_V4::getOptionsForComboBoxPopupMenu (box, label).withStandardItemHeight (juce::jmax (20, box.getHeight()));
}

void VoltLookAndFeel::drawButtonBackground (juce::Graphics& g, juce::Button& b, const juce::Colour&, bool over, bool down)
{
    using namespace colours;
    const auto style = styleOf (b);
    const auto r = b.getLocalBounds().toFloat().reduced (0.5f);
    const bool on = b.getToggleState();
    const auto accent = b.findColour (juce::TextButton::buttonOnColourId);
    if (style == "ghost" || style == "arrow")
        return;
    if (style == "tab")
    {
        if (on)
        {
            g.setColour (text);
            g.fillRect (8.0f, (float) b.getHeight() - 3.0f, (float) b.getWidth() - 16.0f, 2.0f);
        }
        return;
    }
    if (style == "seg")
    {
        juce::Path p;
        p.addRoundedRectangle (r.getX(), r.getY(), r.getWidth(), r.getHeight(), 2.0f, 2.0f,
                               ! b.isConnectedOnLeft(), ! b.isConnectedOnRight(), ! b.isConnectedOnLeft(), ! b.isConnectedOnRight());
        g.setColour (on ? accent : (over ? field.brighter (0.08f) : field));
        g.fillPath (p);
        g.setColour (on ? accent : panelBorder);
        g.strokePath (p, juce::PathStrokeType (1.0f));
        return;
    }
    if (style == "preset")
    {
        g.setColour (over || down ? field.brighter (0.06f) : field);
        g.fillRoundedRectangle (r, 2.0f);
        g.setColour (panelBorder);
        g.drawRoundedRectangle (r, 2.0f, 1.0f);
        return;
    }
    g.setColour (on ? accent : (over || down ? field.brighter (0.1f) : field));
    g.fillRoundedRectangle (r, 2.0f);
    g.setColour (on ? accent : (over ? dimText : panelBorder.brighter (0.25f)));
    g.drawRoundedRectangle (r, 2.0f, 1.0f);
}

void VoltLookAndFeel::drawButtonText (juce::Graphics& g, juce::TextButton& b, bool over, bool)
{
    using namespace colours;
    const auto style = styleOf (b);
    const auto area = b.getLocalBounds();
    if (style == "ghost")
        return;
    if (style == "arrow")
    {
        const float cx = (float) area.getCentreX(), cy = (float) area.getCentreY();
        const float d = b.getButtonText() == "<" ? 1.0f : -1.0f;
        juce::Path p;
        p.startNewSubPath (cx + 3.0f * d, cy - 5.5f);
        p.lineTo (cx - 3.0f * d, cy);
        p.lineTo (cx + 3.0f * d, cy + 5.5f);
        g.setColour (over ? text : dimText);
        g.strokePath (p, juce::PathStrokeType (1.8f, juce::PathStrokeType::mitered, juce::PathStrokeType::butt));
        return;
    }
    if (style == "tab")
    {
        g.setFont (titleFont (12.5f));
        g.setColour (b.getToggleState() ? text : (over ? dimText : faint));
        g.drawText (b.getButtonText(), area, juce::Justification::centred);
        return;
    }
    if (style == "seg")
    {
        g.setFont (titleFont (11.0f));
        g.setColour (b.getToggleState() ? juce::Colour (0xff0b0a09) : dimText);
        g.drawText (b.getButtonText(), area, juce::Justification::centred);
        return;
    }
    if (style == "preset")
    {
        const auto cat = b.getProperties()["category"].toString();
        int x = 12;
        if (cat.isNotEmpty())
        {
            g.setFont (titleFont (11.0f));
            g.setColour (dimText);
            const int cw = juce::GlyphArrangement::getStringWidthInt (g.getCurrentFont(), cat) + 2;
            g.drawText (cat, x, 0, cw, area.getHeight(), juce::Justification::centredLeft);
            x += cw + 9;
            g.setColour (panelBorder);
            g.fillRect (x, 7, 1, area.getHeight() - 14);
            x += 11;
        }
        g.setFont (font (15.5f, true));
        g.setColour (text);
        g.drawFittedText (b.getButtonText(), x, 0, area.getWidth() - x - 8, area.getHeight(), juce::Justification::centredLeft, 1);
        return;
    }
    g.setFont (titleFont (juce::jmin (11.5f, (float) b.getHeight() * 0.52f)));
    g.setColour (b.getToggleState() ? juce::Colour (0xff0b0a09) : text);
    g.drawFittedText (b.getButtonText(), area.reduced (3, 0), juce::Justification::centred, 1);
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
