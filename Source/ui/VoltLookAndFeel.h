#pragma once

#include <juce_gui_basics/juce_gui_basics.h>

namespace volt::ui
{
namespace colours
{
    inline const juce::Colour background { 0xff111317 };
    inline const juce::Colour panel { 0xff1a1d23 };
    inline const juce::Colour panelBorder { 0xff2a2e36 };
    inline const juce::Colour track { 0xff2e333c };
    inline const juce::Colour text { 0xffe6e9ee };
    inline const juce::Colour dimText { 0xff8d95a3 };
    inline const juce::Colour field { 0xff23272e };

    // One colour per kind of section, so it is obvious at a glance what each control belongs to.
    inline const juce::Colour osc { 0xff35c9b5 };     // oscillators, unison, sub, noise
    inline const juce::Colour filter { 0xffff8a3d };  // filter
    inline const juce::Colour env { 0xff7bd66a };     // envelopes (amp, filter env, pitch env)
    inline const juce::Colour mod { 0xffa98bff };     // LFOs, modulation matrix, arp, voice
    inline const juce::Colour fx { 0xff4fa8ff };      // effects and output
    inline const juce::Colour macro { 0xffffd23f };   // macros
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

    // Inter Regular / SemiBold, embedded (SIL OFL).
    static juce::Font font (float size, bool bold = false);
    // Section colour stored on a component (falls back to the oscillator colour).
    static juce::Colour accentOf (const juce::Component& c);
    static void setAccent (juce::Component& c, juce::Colour colour);
};
} // namespace volt::ui
