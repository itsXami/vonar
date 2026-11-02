#pragma once

#include "VoltLookAndFeel.h"
#include "../PresetManager.h"

namespace volt::ui
{
// Top bar: logo, previous / next, preset menu, category + tag filters, search, save, UI scale.
class PresetBar final : public juce::Component, private juce::ChangeListener
{
public:
    explicit PresetBar (PresetManager& pm);
    ~PresetBar() override;

    void paint (juce::Graphics&) override;
    void resized() override;
    void refresh(); // update the displayed preset name

    juce::ComboBox scaleBox;
    std::function<void (float)> onScaleChange;

private:
    void changeListenerCallback (juce::ChangeBroadcaster*) override { rebuildFilters(); refresh(); }
    std::vector<int> filtered() const;
    void step (int delta);
    void showMenu();
    void showSaveDialog();
    void rebuildFilters();

    PresetManager& presets;
    juce::TextButton prevButton { "<" }, nextButton { ">" }, nameButton, saveButton { "SAVE" };
    juce::ComboBox categoryBox, tagBox;
    juce::TextEditor search;
    std::unique_ptr<juce::AlertWindow> saveWindow;
    juce::String shownName;
};
} // namespace volt::ui
