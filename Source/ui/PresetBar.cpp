#include "PresetBar.h"

namespace volt::ui
{
PresetBar::PresetBar (PresetManager& pm) : presets (pm)
{
    for (auto* b : { &prevButton, &nextButton, &nameButton, &saveButton })
        addAndMakeVisible (*b);
    prevButton.setTooltip ("Previous preset (in the current filter)");
    nextButton.setTooltip ("Next preset (in the current filter)");
    nameButton.setTooltip ("Browse presets");
    saveButton.setTooltip ("Save the current sound as a user preset");
    prevButton.onClick = [this] { step (-1); };
    nextButton.onClick = [this] { step (1); };
    nameButton.onClick = [this] { showMenu(); };
    saveButton.onClick = [this] { showSaveDialog(); };

    addAndMakeVisible (categoryBox);
    addAndMakeVisible (tagBox);
    categoryBox.setTooltip ("Filter by category");
    tagBox.setTooltip ("Filter by tag");
    categoryBox.onChange = [this] { refresh(); };
    tagBox.onChange = [this] { refresh(); };

    search.setTextToShowWhenEmpty ("Search...", colours::dimText);
    search.setFont (VoltLookAndFeel::font (13.0f));
    search.setIndents (6, 4);
    search.onTextChange = [this] { refresh(); };
    search.setTooltip ("Search names, tags and descriptions");
    addAndMakeVisible (search);

    scaleBox.addItemList ({ "75%", "100%", "125%", "150%", "175%", "200%" }, 1);
    scaleBox.setTooltip ("Interface size");
    scaleBox.onChange = [this] {
        static const float s[] = { 0.75f, 1.0f, 1.25f, 1.5f, 1.75f, 2.0f };
        const int i = scaleBox.getSelectedItemIndex();
        if (i >= 0 && onScaleChange)
            onScaleChange (s[i]);
    };
    addAndMakeVisible (scaleBox);

    rebuildFilters();
    presets.addChangeListener (this);
    refresh();
}

PresetBar::~PresetBar()
{
    presets.removeChangeListener (this);
}

void PresetBar::rebuildFilters()
{
    const auto cat = categoryBox.getText();
    const auto tag = tagBox.getText();
    categoryBox.clear (juce::dontSendNotification);
    categoryBox.addItem ("All", 1);
    categoryBox.addItemList (PresetManager::categories(), 2);
    juce::StringArray tags;
    for (const auto& p : presets.getPresets())
        for (const auto& t : p.tags)
            tags.addIfNotAlreadyThere (t);
    tags.sortNatural();
    tagBox.clear (juce::dontSendNotification);
    tagBox.addItem ("All tags", 1);
    tagBox.addItemList (tags, 2);

    const int ci = PresetManager::categories().indexOf (cat);
    categoryBox.setSelectedId (ci >= 0 ? ci + 2 : 1, juce::dontSendNotification);
    const int ti = tags.indexOf (tag);
    tagBox.setSelectedId (ti >= 0 ? ti + 2 : 1, juce::dontSendNotification);
}

std::vector<int> PresetBar::filtered() const
{
    std::vector<int> out;
    const auto cat = categoryBox.getSelectedId() > 1 ? categoryBox.getText() : juce::String();
    const auto tag = tagBox.getSelectedId() > 1 ? tagBox.getText() : juce::String();
    const auto q = search.getText().trim().toLowerCase();
    const auto& all = presets.getPresets();
    for (size_t i = 0; i < all.size(); ++i)
    {
        const auto& p = all[i];
        if (cat.isNotEmpty() && p.category != cat) continue;
        if (tag.isNotEmpty() && ! p.tags.contains (tag)) continue;
        if (q.isNotEmpty())
        {
            const auto hay = (p.name + " " + p.tags.joinIntoString (" ") + " " + p.description + " " + p.category).toLowerCase();
            if (! hay.contains (q)) continue;
        }
        out.push_back ((int) i);
    }
    return out;
}

void PresetBar::step (int delta)
{
    const auto list = filtered();
    if (list.empty())
        return;
    const int cur = presets.getCurrentIndex();
    auto it = std::find (list.begin(), list.end(), cur);
    int pos = 0;
    if (it == list.end())
        pos = delta > 0 ? 0 : (int) list.size() - 1;
    else
        pos = ((int) (it - list.begin()) + delta + (int) list.size()) % (int) list.size();
    presets.loadPreset (list[(size_t) pos]);
    refresh();
}

void PresetBar::showMenu()
{
    const auto list = filtered();
    juce::PopupMenu menu;
    const auto& all = presets.getPresets();
    const int cur = presets.getCurrentIndex();
    for (const auto& cat : PresetManager::categories())
    {
        juce::PopupMenu sub;
        int count = 0;
        for (int idx : list)
        {
            const auto& p = all[(size_t) idx];
            if (p.category != cat) continue;
            sub.addItem (idx + 1, p.isFactory ? p.name : p.name + "  (user)", true, idx == cur);
            ++count;
        }
        if (count > 0)
            menu.addSubMenu (cat + "  (" + juce::String (count) + ")", sub);
    }
    if (list.empty())
        menu.addItem (-1, "No presets match the filter", false);
    menu.addSeparator();
    menu.addItem (100000, "Rescan user presets");
    menu.showMenuAsync (juce::PopupMenu::Options().withTargetComponent (nameButton).withMinimumWidth (nameButton.getWidth()),
                        [this] (int result) {
                            if (result == 100000)
                                presets.rescan();
                            else if (result > 0)
                                presets.loadPreset (result - 1);
                            refresh();
                        });
}

void PresetBar::showSaveDialog()
{
    saveWindow = std::make_unique<juce::AlertWindow> ("Save preset", "Stores the current sound in " + PresetManager::getUserPresetDirectory().getFullPathName(),
                                                      juce::MessageBoxIconType::NoIcon, this);
    const auto current = presets.getCurrentPresetName();
    saveWindow->addTextEditor ("name", current == "Init" ? juce::String ("My Preset") : current, "Name");
    saveWindow->addComboBox ("category", PresetManager::categories(), "Category");
    if (auto* c = saveWindow->getComboBoxComponent ("category"))
    {
        const int idx = presets.getCurrentIndex();
        const auto cat = idx >= 0 ? presets.getPresets()[(size_t) idx].category : juce::String ("Lead");
        c->setSelectedItemIndex (juce::jmax (0, PresetManager::categories().indexOf (cat)), juce::dontSendNotification);
    }
    saveWindow->addTextEditor ("tags", "User", "Tags (comma separated)");
    saveWindow->addTextEditor ("description", "", "Description (one sentence)");
    saveWindow->addButton ("Save", 1, juce::KeyPress (juce::KeyPress::returnKey));
    saveWindow->addButton ("Cancel", 0, juce::KeyPress (juce::KeyPress::escapeKey));

    if (auto* top = getTopLevelComponent())
    {
        top->addAndMakeVisible (*saveWindow);
        saveWindow->centreAroundComponent (top, saveWindow->getWidth(), saveWindow->getHeight());
    }
    saveWindow->enterModalState (true, juce::ModalCallbackFunction::create ([this] (int result) {
        if (saveWindow == nullptr)
            return;
        if (result == 1)
        {
            juce::StringArray tags;
            tags.addTokens (saveWindow->getTextEditorContents ("tags"), ",", "\"");
            tags.trim();
            tags.removeEmptyStrings();
            const auto* c = saveWindow->getComboBoxComponent ("category");
            const auto error = presets.saveUserPreset (saveWindow->getTextEditorContents ("name"),
                                                       c != nullptr ? c->getText() : juce::String ("Lead"), tags,
                                                       saveWindow->getTextEditorContents ("description"));
            if (error.isNotEmpty())
                juce::AlertWindow::showAsync (juce::MessageBoxOptions().withTitle ("Save preset").withMessage (error).withButton ("OK")
                                                  .withAssociatedComponent (this), nullptr);
        }
        juce::MessageManager::callAsync ([safe = juce::Component::SafePointer<PresetBar> (this)] {
            if (safe != nullptr) { safe->saveWindow.reset(); safe->refresh(); }
        });
    }), false);
}

void PresetBar::refresh()
{
    const auto name = presets.getCurrentPresetName();
    const int idx = presets.getCurrentIndex();
    juce::String text = name;
    if (idx >= 0)
        text = presets.getPresets()[(size_t) idx].category.toUpperCase() + "  |  " + name;
    nameButton.setButtonText (text);
    if (idx >= 0)
        nameButton.setTooltip (presets.getPresets()[(size_t) idx].description);
}

void PresetBar::paint (juce::Graphics& g)
{
    g.setColour (colours::panel);
    g.fillRect (getLocalBounds());
    g.setColour (colours::panelBorder);
    g.drawHorizontalLine (getHeight() - 1, 0.0f, (float) getWidth());
    g.setColour (colours::accent);
    g.setFont (VoltLookAndFeel::font (26.0f, true));
    g.drawText ("VOLT", 14, 0, 80, getHeight(), juce::Justification::centredLeft);
    g.setColour (colours::dimText);
    g.setFont (VoltLookAndFeel::font (10.0f));
    g.drawText ("WAVETABLE SYNTH", 14, getHeight() - 14, 120, 12, juce::Justification::centredLeft);
}

void PresetBar::resized()
{
    const int y = 9, h = 26;
    prevButton.setBounds (132, y, 26, h);
    nextButton.setBounds (160, y, 26, h);
    nameButton.setBounds (190, y, 270, h);
    categoryBox.setBounds (468, y, 96, h);
    tagBox.setBounds (570, y, 130, h);
    search.setBounds (706, y, 140, h);
    saveButton.setBounds (852, y, 56, h);
    scaleBox.setBounds (914, y, 74, h);
}
} // namespace volt::ui
