#include "PresetManager.h"
#include "VoltPresetData.h"

namespace volt
{
const juce::StringArray& PresetManager::categories()
{
    static const juce::StringArray c { "Bass", "Lead", "Pad", "Keys", "Arp", "Brass", "FX" };
    return c;
}

PresetManager::PresetManager (juce::AudioProcessorValueTreeState& state) : apvts (state)
{
    rescan();
}

juce::File PresetManager::getUserPresetDirectory()
{
    return juce::File::getSpecialLocation (juce::File::userApplicationDataDirectory)
        .getChildFile ("VOLT")
        .getChildFile ("Presets");
}

bool PresetManager::parsePreset (const juce::String& json, PresetInfo& out, juce::StringArray& errors)
{
    juce::var root;
    const auto result = juce::JSON::parse (json, root);
    if (result.failed() || ! root.isObject())
    {
        errors.add ("invalid JSON: " + result.getErrorMessage());
        return false;
    }

    out.name = root["name"].toString().trim();
    out.category = root["category"].toString().trim();
    out.description = root["description"].toString().trim();
    out.tags.clear();
    if (auto* t = root["tags"].getArray())
        for (const auto& v : *t)
            out.tags.add (v.toString());
    out.macroLabels.clear();
    if (auto* m = root["macros"].getArray())
        for (const auto& v : *m)
            out.macroLabels.add (v.toString());
    while (out.macroLabels.size() < kNumMacros)
        out.macroLabels.add ("Macro " + juce::String (out.macroLabels.size() + 1));
    out.params = root["params"];

    if (out.name.isEmpty())
        errors.add ("missing name");
    if (! categories().contains (out.category))
        errors.add (out.name + ": invalid category '" + out.category + "'");
    if (out.description.isEmpty())
        errors.add (out.name + ": missing description");
    if (! out.params.isObject())
    {
        errors.add (out.name + ": params must be an object");
        out.params = juce::var (new juce::DynamicObject());
    }

    if (auto* obj = out.params.getDynamicObject())
    {
        for (const auto& prop : obj->getProperties())
        {
            const auto id = prop.name.toString();
            int index = -1;
            for (int p = 0; p < NumParams; ++p)
                if (id == spec (p).id) { index = p; break; }
            if (index < 0)
            {
                errors.add (out.name + ": unknown parameter '" + id + "'");
                continue;
            }
            const auto& s = spec (index);
            const auto& v = prop.value;
            if (s.type == ParamType::Choice)
            {
                if (! v.isString() || ! s.choices.contains (v.toString()))
                    errors.add (out.name + ": invalid value '" + v.toString() + "' for " + id);
            }
            else if (s.type == ParamType::Bool)
            {
                if (! v.isBool())
                    errors.add (out.name + ": " + id + " must be true/false");
            }
            else
            {
                const double d = (double) v;
                if (! (v.isDouble() || v.isInt() || v.isInt64()) || d < s.minValue - 1.0e-6 || d > s.maxValue + 1.0e-6)
                    errors.add (out.name + ": value out of range for " + id + " (" + v.toString() + ")");
            }
        }
    }
    return errors.isEmpty();
}

void PresetManager::rescan()
{
    presets.clear();

    std::vector<PresetInfo> factory;
    for (int i = 0; i < VoltPresetData::namedResourceListSize; ++i)
    {
        int size = 0;
        const char* data = VoltPresetData::getNamedResource (VoltPresetData::namedResourceList[i], size);
        if (data == nullptr || size <= 0)
            continue;
        PresetInfo info;
        juce::StringArray errors;
        parsePreset (juce::String::fromUTF8 (data, size), info, errors);
        jassert (errors.isEmpty());
        if (info.name.isNotEmpty())
        {
            info.isFactory = true;
            factory.push_back (std::move (info));
        }
    }
    // Resource order follows file names (numbered); keep Init first.
    std::stable_sort (factory.begin(), factory.end(), [] (const PresetInfo& a, const PresetInfo& b) {
        if (a.name == "Init") return b.name != "Init";
        if (b.name == "Init") return false;
        return false;
    });
    numFactory = (int) factory.size();
    presets = std::move (factory);

    const auto dir = getUserPresetDirectory();
    if (dir.isDirectory())
    {
        auto files = dir.findChildFiles (juce::File::findFiles, false, "*.json");
        files.sort();
        for (const auto& f : files)
        {
            PresetInfo info;
            juce::StringArray errors;
            parsePreset (f.loadFileAsString(), info, errors);
            if (info.name.isEmpty())
                continue;
            info.isFactory = false;
            info.file = f;
            presets.push_back (std::move (info));
        }
    }
    sendChangeMessage();
}

int PresetManager::indexOf (const juce::String& name) const
{
    for (size_t i = 0; i < presets.size(); ++i)
        if (presets[i].name == name)
            return (int) i;
    return -1;
}

void PresetManager::applyPreset (const PresetInfo& p)
{
    for (int i = 0; i < NumParams; ++i)
    {
        const auto& s = spec (i);
        auto* param = apvts.getParameter (s.id);
        if (param == nullptr)
            continue;
        float value = s.defaultValue;
        if (p.params.hasProperty (s.id))
        {
            const auto& v = p.params[juce::Identifier (s.id)];
            switch (s.type)
            {
                case ParamType::Choice:
                {
                    const int idx = v.isString() ? s.choices.indexOf (v.toString()) : (int) v;
                    if (idx >= 0 && idx < s.choices.size())
                        value = (float) idx;
                    break;
                }
                case ParamType::Bool:
                    value = (bool) v ? 1.0f : 0.0f;
                    break;
                case ParamType::Int:
                    value = (float) juce::roundToInt ((double) v);
                    break;
                case ParamType::Float:
                default:
                    value = (float) (double) v;
                    break;
            }
            value = juce::jlimit (s.minValue, s.maxValue, value);
        }
        if (auto* ranged = dynamic_cast<juce::RangedAudioParameter*> (param))
            ranged->setValueNotifyingHost (ranged->convertTo0to1 (value));
    }

    apvts.state.setProperty (kPresetNameProp, p.name, nullptr);
    apvts.state.setProperty (kPresetCategoryProp, p.category, nullptr);
    for (int m = 0; m < kNumMacros; ++m)
        apvts.state.setProperty (macroLabelProp (m), p.macroLabels[m], nullptr);
    sendChangeMessage();
}

bool PresetManager::loadPreset (int index)
{
    if (index < 0 || index >= (int) presets.size())
        return false;
    applyPreset (presets[(size_t) index]);
    return true;
}

juce::String PresetManager::getCurrentPresetName() const
{
    return apvts.state.getProperty (kPresetNameProp, "Init").toString();
}

juce::String PresetManager::getMacroLabel (int i) const
{
    return apvts.state.getProperty (macroLabelProp (i), "Macro " + juce::String (i + 1)).toString();
}

void PresetManager::setMacroLabel (int i, const juce::String& label)
{
    apvts.state.setProperty (macroLabelProp (i), label.substring (0, 24), nullptr);
}

juce::var PresetManager::currentStateToJson (const juce::String& name, const juce::String& category,
                                             const juce::StringArray& tags, const juce::String& description) const
{
    auto* root = new juce::DynamicObject();
    root->setProperty ("name", name);
    root->setProperty ("category", category);
    juce::Array<juce::var> tagArr;
    for (const auto& t : tags)
        tagArr.add (t);
    root->setProperty ("tags", tagArr);
    root->setProperty ("description", description);
    juce::Array<juce::var> macroArr;
    for (int m = 0; m < kNumMacros; ++m)
        macroArr.add (getMacroLabel (m));
    root->setProperty ("macros", macroArr);
    root->setProperty ("version", 1);

    auto* params = new juce::DynamicObject();
    for (int i = 0; i < NumParams; ++i) // user presets store every parameter explicitly
    {
        const auto& s = spec (i);
        const float v = apvts.getRawParameterValue (s.id)->load();
        switch (s.type)
        {
            case ParamType::Choice: params->setProperty (s.id, s.choices[juce::jlimit (0, s.choices.size() - 1, juce::roundToInt (v))]); break;
            case ParamType::Bool:   params->setProperty (s.id, v >= 0.5f); break;
            case ParamType::Int:    params->setProperty (s.id, juce::roundToInt (v)); break;
            case ParamType::Float:
            default:                params->setProperty (s.id, (double) v); break;
        }
    }
    root->setProperty ("params", juce::var (params));
    return juce::var (root);
}

juce::String PresetManager::saveUserPreset (const juce::String& rawName, const juce::String& category,
                                            const juce::StringArray& tags, const juce::String& description)
{
    const auto name = rawName.trim();
    if (name.isEmpty())
        return "Preset name is empty.";
    if (! categories().contains (category))
        return "Invalid category.";
    for (int i = 0; i < numFactory; ++i)
        if (presets[(size_t) i].name.equalsIgnoreCase (name))
            return "A factory preset with this name already exists.";

    const auto dir = getUserPresetDirectory();
    if (! dir.createDirectory())
        return "Cannot create " + dir.getFullPathName();

    const auto file = dir.getChildFile (juce::File::createLegalFileName (name) + ".json");
    const auto json = juce::JSON::toString (currentStateToJson (name, category, tags,
                                                                description.isNotEmpty() ? description : "User preset."));
    if (! file.replaceWithText (json))
        return "Cannot write " + file.getFullPathName();

    apvts.state.setProperty (kPresetNameProp, name, nullptr);
    apvts.state.setProperty (kPresetCategoryProp, category, nullptr);
    rescan();
    return {};
}
} // namespace volt
