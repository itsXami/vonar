#pragma once

#include <juce_gui_basics/juce_gui_basics.h>

namespace volt::ui
{
namespace colours
{
    inline const juce::Colour background { 0xff0e1013 };
    inline const juce::Colour panel { 0xff16191e };
    inline const juce::Colour panelBorder { 0xff23272e };
    inline const juce::Colour track { 0xff2a2f37 };
    inline const juce::Colour text { 0xffd3d7de };
    inline const juce::Colour dimText { 0xff7c8490 };
    inline const juce::Colour accent { 0xffffb52e }; // the single accent colour
    inline const juce::Colour field { 0xff1d2127 };
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

    static juce::Font font (float size, bool bold = false);
};
} // namespace volt::ui
