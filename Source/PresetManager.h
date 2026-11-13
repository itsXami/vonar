#pragma once

#include <juce_audio_processors/juce_audio_processors.h>
#include "Params.h"

namespace volt
{
struct PresetInfo
{
    juce::String name, category, description;
    juce::String mood;         // one of PresetManager::moods(), empty for old user presets
    juce::StringArray tags;
    juce::StringArray macroLabels;
    juce::var params;          // object: param id -> value (plain units, choices by name)
    bool isFactory = true;
    juce::File file;           // user presets only
};

// Factory presets come from BinaryData (presets/*.json embedded at build time),
// user presets live in <user app data>/VOLT/Presets/*.json. All loading happens on the message thread.
class PresetManager : public juce::ChangeBroadcaster
{
public:
    static const juce::StringArray& categories();   // Bass, Lead, Guitar, Pluck, Keys, Bell, Pad, Strings, Brass, Woodwind, Arp, Drums, FX
    static const juce::StringArray& moods();        // Soft, Medium, Sad, Dark, Aggressive
    static constexpr const char* kPresetNameProp = "presetName";
    static constexpr const char* kPresetCategoryProp = "presetCategory";
    static juce::String macroLabelProp (int i) { return "macroLabel" + juce::String (i + 1); }

    explicit PresetManager (juce::AudioProcessorValueTreeState& state);

    void rescan();
    const std::vector<PresetInfo>& getPresets() const noexcept { return presets; }
    int getNumFactoryPresets() const noexcept { return numFactory; }
    int indexOf (const juce::String& name) const;

    bool loadPreset (int index);
    bool loadPresetByName (const juce::String& name) { return loadPreset (indexOf (name)); }
    void applyPreset (const PresetInfo& p);   // sets every parameter (missing ones -> default)

    juce::String getCurrentPresetName() const;
    int getCurrentIndex() const { return indexOf (getCurrentPresetName()); }
    juce::String getMacroLabel (int i) const;
    void setMacroLabel (int i, const juce::String& label);

    // Saves the current state as a user preset. Returns an empty string on success, or an error message.
    juce::String saveUserPreset (const juce::String& name, const juce::String& category, const juce::StringArray& tags,
                                 const juce::String& description, const juce::String& mood = {});

    static juce::File getUserPresetDirectory();

    // Parses and validates JSON. Problems (unknown ids, bad choice names, missing fields) go to `errors`.
    static bool parsePreset (const juce::String& json, PresetInfo& out, juce::StringArray& errors);
    juce::var currentStateToJson (const juce::String& name, const juce::String& category, const juce::StringArray& tags,
                                  const juce::String& description, const juce::String& mood = {}) const;

private:
    juce::AudioProcessorValueTreeState& apvts;
    std::vector<PresetInfo> presets;
    int numFactory = 0;
};
} // namespace volt
