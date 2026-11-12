#pragma once

#include <juce_gui_basics/juce_gui_basics.h>

namespace volt::ui
{
namespace colours
{
    // Warm charcoal surfaces and off-white text.
    inline const juce::Colour background { 0xff0b0a09 };
    inline const juce::Colour bar { 0xff100f0e };          // top bar
    inline const juce::Colour panel { 0xff191817 };        // main panels
    inline const juce::Colour strip { 0xff11100f };        // utility strip (recedes)
    inline const juce::Colour macroBar { 0xff211f1d };     // macro bar (comes forward)
    inline const juce::Colour inset { 0xff090808 };        // displays
    inline const juce::Colour panelBorder { 0xff2d2a27 };  // hairlines and field outlines
    inline const juce::Colour grid { 0xff1b1a18 };
    inline const juce::Colour track { 0xff35322e };
    inline const juce::Colour text { 0xfff0ebe3 };
    inline const juce::Colour value { 0xffe3ded5 };
    inline const juce::Colour dimText { 0xff999188 };      // parameter names
    inline const juce::Colour faint { 0xff655f58 };        // scales, inactive tabs
    inline const juce::Colour field { 0xff0e0d0c };

    // One colour per kind of section, so it is obvious at a glance what each control belongs to.
    inline const juce::Colour osc { 0xff3db8a6 };     // oscillators, unison, sub, noise, string
    inline const juce::Colour filter { 0xffe8893f };  // filter
    inline const juce::Colour env { 0xff86c26a };     // envelopes
    inline const juce::Colour mod { 0xff9c8be8 };     // LFOs, modulation matrix, arp, voice
    inline const juce::Colour fx { 0xff6aa5e0 };      // effects tab
    inline const juce::Colour macro { 0xffe4b54a };   // macros
}

class VoltLookAndFeel final : public juce::LookAndFeel_V4
{
public:
    VoltLookAndFeel();

    void drawRotarySlider (juce::Graphics&, int x, int y, int w, int h, float pos, float start, float end, juce::Slider&) override;
    void drawLinearSlider (juce::Graphics&, int x, int y, int w, int h, float pos, float minPos, float maxPos,
                           juce::Slider::SliderStyle, juce::Slider&) override;
    void drawComboBox (juce::Graphics&, int w, int h, bool down, int bx, int by, int bw, int bh, juce::ComboBox&) override;
    juce::Font getComboBoxFont (juce::ComboBox&) override;
    void positionComboBoxText (juce::ComboBox&, juce::Label&) override;
    juce::PopupMenu::Options getOptionsForComboBoxPopupMenu (juce::ComboBox&, juce::Label&) override;
    void drawButtonBackground (juce::Graphics&, juce::Button&, const juce::Colour&, bool over, bool down) override;
    void drawButtonText (juce::Graphics&, juce::TextButton&, bool over, bool down) override;
    juce::Font getTextButtonFont (juce::TextButton&, int h) override;
    void drawTooltip (juce::Graphics&, const juce::String& text, int w, int h) override;
    juce::Rectangle<int> getTooltipBounds (const juce::String& text, juce::Point<int> pos, juce::Rectangle<int> parent) override;
    juce::Font getPopupMenuFont() override;
    juce::Font getLabelFont (juce::Label&) override;
    juce::Font getSliderPopupFont (juce::Slider&) override;
    juce::Font getAlertWindowTitleFont() override;
    juce::Font getAlertWindowMessageFont() override;
    juce::Font getAlertWindowFont() override;
    juce::Typeface::Ptr getTypefaceForFont (const juce::Font&) override;

    // Oxanium Medium / SemiBold, embedded (SIL OFL).
    static juce::Font font (float size, bool bold = false);
    // Section titles and tabs: semibold capitals with a little tracking.
    static juce::Font titleFont (float size);
    // Section colour stored on a component (falls back to the oscillator colour).
    static juce::Colour accentOf (const juce::Component& c);
    static void setAccent (juce::Component& c, juce::Colour colour);
    // Button looks: "tab" (text + underline), "seg" (segmented switch), "preset" (preset name field),
    // "arrow" (bare chevron), "ghost" (invisible hit area). Anything else is a plain outlined button.
    static void setStyle (juce::Button& b, const juce::String& style) { b.getProperties().set ("style", style); }

    // Recessed display background shared by the wavetable, filter, envelope, LFO and scope views.
    static void drawDisplay (juce::Graphics&, juce::Rectangle<float> r);
    // Flat surface with a faint light edge at the top.
    static void drawSurface (juce::Graphics&, juce::Rectangle<float> r, juce::Colour fill);
};
} // namespace volt::ui
