#include "PresetBar.h"

namespace volt::ui
{
PresetBar::PresetBar (PresetManager& pm) : presets (pm)
{
    for (auto* b : { &prevButton, &nextButton, &nameButton, &saveButton, &aboutButton })
        addAndMakeVisible (*b);
    VoltLookAndFeel::setStyle (prevButton, "arrow");
    VoltLookAndFeel::setStyle (nextButton, "arrow");
    VoltLookAndFeel::setStyle (nameButton, "preset");
    VoltLookAndFeel::setStyle (aboutButton, "ghost");
    aboutButton.setTooltip ("About VOLT");
    aboutButton.onClick = [this] { showAbout(); };
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

    search.setTextToShowWhenEmpty ("Search", colours::faint);
    search.setFont (VoltLookAndFeel::font (12.5f));
    search.setIndents (6, 3);
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

void PresetBar::showAbout()
{
    juce::AlertWindow::showAsync (
        juce::MessageBoxOptions()
            .withTitle ("VOLT " VOLT_VERSION_STRING)
            .withMessage ("Wavetable synthesizer.\n\n"
                          "Free software under the GNU Affero General Public License, version 3. "
                          "You may use, study, share and change it under that licence; it comes with no warranty. "
                          "The name and logo are not covered by the licence.\n\n"
                          "Built with JUCE (AGPLv3). Interface typeface: Oxanium (SIL Open Font License 1.1).")
            .withButton ("OK")
            .withAssociatedComponent (this),
        nullptr);
}

void PresetBar::refresh()
{
    const auto name = presets.getCurrentPresetName();
    const int idx = presets.getCurrentIndex();
    const auto category = idx >= 0 ? presets.getPresets()[(size_t) idx].category.toUpperCase() : juce::String();
    if (nameButton.getButtonText() != name || nameButton.getProperties()["category"].toString() != category)
    {
        nameButton.getProperties().set ("category", category);
        nameButton.setButtonText (name);
        nameButton.repaint();
    }
    if (idx >= 0)
        nameButton.setTooltip (presets.getPresets()[(size_t) idx].description);
}

void PresetBar::paint (juce::Graphics& g)
{
    g.setColour (colours::bar);
    g.fillRect (getLocalBounds());
    g.setColour (juce::Colours::black);
    g.fillRect (0, getHeight() - 1, getWidth(), 1);

    // Wordmark drawn from strokes; the O is a knob.
    const float x = 18.0f, y = 15.0f, h = 18.0f, sw = 3.4f;
    const juce::PathStrokeType stroke (sw, juce::PathStrokeType::mitered, juce::PathStrokeType::butt);
    juce::Path mark;
    mark.startNewSubPath (x, y);
    mark.lineTo (x + 8.5f, y + h);
    mark.lineTo (x + 17.0f, y);
    const float cx = x + 33.0f, cy = y + h * 0.5f, r = h * 0.5f - sw * 0.5f + 0.6f;
    mark.addCentredArc (cx, cy, r, r, 0.0f, -2.41f, 2.41f, true);
    mark.startNewSubPath (x + 49.0f, y);
    mark.lineTo (x + 49.0f, y + h - sw * 0.5f);
    mark.lineTo (x + 61.0f, y + h - sw * 0.5f);
    mark.startNewSubPath (x + 64.0f, y + sw * 0.5f);
    mark.lineTo (x + 82.0f, y + sw * 0.5f);
    mark.startNewSubPath (x + 73.0f, y + sw * 0.5f);
    mark.lineTo (x + 73.0f, y + h);
    g.setColour (colours::text);
    g.strokePath (mark, stroke);
    g.setColour (colours::macro);
    g.drawLine (cx, cy, cx + (r - 1.0f) * std::sin (0.733f), cy - (r - 1.0f) * std::cos (0.733f), 2.6f);
}

void PresetBar::resized()
{
    const int y = 11, h = 26;
    aboutButton.setBounds (10, 6, 100, 36);
    nameButton.setBounds (424, 9, 296, 30);
    prevButton.setBounds (724, y, 24, h);
    nextButton.setBounds (748, y, 24, h);
    categoryBox.setBounds (782, y + 2, 88, 22);
    tagBox.setBounds (874, y + 2, 100, 22);
    search.setBounds (978, y + 2, 84, 22);
    saveButton.setBounds (1068, y + 2, 52, 22);
    scaleBox.setBounds (1126, y + 2, 66, 22);
}
} // namespace volt::ui
