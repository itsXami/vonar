#include "TestHelpers.h"
#include "PluginProcessor.h"
#include "VoltPresetData.h"

using namespace volt;

namespace
{
// Artist, album and track names that must never appear in preset names (inspiration goes to tags/docs only).
const char* const kBannedInNames[] = {
    "kanye", "west", "yeezus", "yeezy", "daft", "bangalter", "homem-christo", "thomas", "guy-manuel",
    "graduation", "heartbreak", "808s", "dark twisted", "fantasy", "mbdtf", "donda", "jesus is king", "pablo",
    "late registration", "college dropout", "homework", "discovery", "human after all", "tron", "legacy",
    "random access", "memories", "alive", "stronger", "harder", "better", "faster", "one more time",
    "around the world", "da funk", "digital love", "aerodynamic", "get lucky", "instant crush", "lose yourself",
    "contact", "derezzed", "end of line", "black skinhead", "blood on the leaves", "bound", "new slaves", "on sight",
    "i am a god", "send it up", "hold my liquor", "guilt trip", "flashing lights", "good life", "love lockdown",
    "heartless", "paranoid", "amazing", "robocop", "runaway", "power", "monster", "all of the lights", "lost in the world",
    "ultralight", "father stretch", "jail", "hurricane", "off the grid", "moon", "robot rock", "technologic",
    "television", "something about us", "veridis", "voyager", "superheroes", "revolution 909", "rinzler",
    "solar sailer", "the grid", "giorgio", "doin it right", "touch", "motherboard", "fragments of time", "within",
    "beyond", "teachers", "emotion", "make love", "prime time", "indo silver", "fresh", "phoenix", "high fidelity",
    "crescendolls", "nightvision", "face to face", "too long", "steam machine", "brainwasher", "on/off", "aerodynamik",
    "short circuit", "burnin", "rollin", "flynn", "clu", "sea of simulation", "adagio for tron", "armory", "recognizer",
    "the son of flynn", "nuclear", "c'mon", "coldest winter", "welcome to heartbreak", "street lights", "pinocchio",
    "say you will", "robot", "blame game", "devil in a new dress", "hell of a life", "gorgeous", "so appalled",
    "on god", "jesus walks", "gold digger", "touch the sky", "homecoming", "champion", "i wonder", "glory", "drunk and hot",
    "barry bonds", "everything i am", "big brother", "flashing", "lights"
};

bool containsWord (const juce::String& hay, const juce::String& word)
{
    const auto h = " " + hay.toLowerCase().replaceCharacters ("-_.,!?()'", "         ") + " ";
    const auto w = " " + word.toLowerCase().replaceCharacters ("-_.,!?()'", "         ") + " ";
    return h.contains (w);
}
}

struct PresetTests final : juce::UnitTest
{
    PresetTests() : juce::UnitTest ("Presets", "VOLT") {}

    void runTest() override
    {
        VoltAudioProcessor proc;
        auto& pm = proc.getPresetManager();
        const int count = pm.getNumFactoryPresets();

        beginTest ("Every factory preset parses without errors");
        juce::StringArray names;
        for (int i = 0; i < VoltPresetData::namedResourceListSize; ++i)
        {
            int size = 0;
            const char* data = VoltPresetData::getNamedResource (VoltPresetData::namedResourceList[i], size);
            PresetInfo info;
            juce::StringArray errors;
            const bool ok = PresetManager::parsePreset (juce::String::fromUTF8 (data, size), info, errors);
            expect (ok, VoltPresetData::originalFilenames[i] + juce::String (": ") + errors.joinIntoString ("; "));
        }

        beginTest ("Exactly 121 factory presets: Init + 60 + 60 in the specified groups");
        expectEquals (count, 121);
        auto countTag = [&] (const juce::String& tag) {
            int n = 0;
            for (int i = 0; i < count; ++i)
                n += pm.getPresets()[(size_t) i].tags.contains (tag) ? 1 : 0;
            return n;
        };
        expectEquals (countTag ("Kanye West"), 60);
        expectEquals (countTag ("Daft Punk"), 60);
        const std::pair<const char*, int> groups[] = { { "Yeezus", 24 }, { "Graduation", 10 }, { "808s & Heartbreak", 10 },
                                                       { "MBDTF", 10 }, { "Donda", 6 }, { "Homework", 14 }, { "Discovery", 18 },
                                                       { "Human After All", 8 }, { "Tron: Legacy", 12 },
                                                       { "Random Access Memories", 8 } };
        for (const auto& [tag, n] : groups)
            expectEquals (countTag (tag), n, tag);

        beginTest ("Names unique, Init first, no artist / album / track names");
        expectGreaterThan (count, 0);
        expectEquals (pm.getPresets()[0].name, juce::String ("Init"));
        for (int i = 0; i < count; ++i)
        {
            const auto& p = pm.getPresets()[(size_t) i];
            expect (! names.contains (p.name), "duplicate name " + p.name);
            names.add (p.name);
            for (auto* banned : kBannedInNames)
                expect (! containsWord (p.name, banned), "preset name '" + p.name + "' contains '" + banned + "'");
        }

        beginTest ("Metadata: category, tags, one-sentence description, four routed and labelled macros");
        for (int i = 0; i < count; ++i)
        {
            const auto& p = pm.getPresets()[(size_t) i];
            expect (PresetManager::categories().contains (p.category), p.name);
            expect (p.tags.size() > 0, p.name + ": no tags");
            expect (p.description.endsWithChar ('.') && ! p.description.dropLastCharacters (1).contains (". "),
                    p.name + ": description must be one sentence");
            for (int m = 0; m < kNumMacros; ++m)
            {
                bool routed = false;
                for (int s = 0; s < kNumModSlots; ++s)
                {
                    const auto src = p.params[juce::Identifier (spec (Mod1_Src + s * kModSlotParamCount).id)].toString();
                    const double amt = (double) p.params.getProperty (spec (Mod1_Amt + s * kModSlotParamCount).id, 0.0);
                    if (src == "Macro " + juce::String (m + 1) && std::abs (amt) > 1.0e-4)
                        routed = true;
                }
                expect (routed, p.name + ": macro " + juce::String (m + 1) + " is not routed");
                expect (p.macroLabels[m].isNotEmpty() && p.macroLabels[m] != "Macro " + juce::String (m + 1),
                        p.name + ": macro " + juce::String (m + 1) + " has no label");
            }
        }

        beginTest ("Loading a preset sets every parameter and the preset name");
        if (count > 1)
        {
            pm.loadPreset (count - 1);
            expectEquals (pm.getCurrentPresetName(), pm.getPresets()[(size_t) count - 1].name);
            pm.loadPreset (0);
            for (int p = 0; p < NumParams; ++p)
            {
                const auto& s = spec (p);
                if (pm.getPresets()[0].params.hasProperty (s.id))
                    continue;
                expectWithinAbsoluteError (proc.apvts.getRawParameterValue (s.id)->load(), s.defaultValue,
                                           (s.maxValue - s.minValue) * 1.0e-4f + 1.0e-6f, s.id);
            }
        }
    }
};

struct StateTests final : juce::UnitTest
{
    StateTests() : juce::UnitTest ("State", "VOLT") {}

    void runTest() override
    {
        beginTest ("Session state restores all parameters, preset name and macro labels");
        VoltAudioProcessor a;
        auto& pm = a.getPresetManager();
        pm.loadPreset (pm.getNumFactoryPresets() - 1);
        juce::Random rnd (7);
        for (auto* param : a.getParameters())
            param->setValueNotifyingHost (rnd.nextFloat());
        pm.setMacroLabel (2, "Grit");
        a.apvts.state.setProperty (PresetManager::kPresetNameProp, "Session Sound", nullptr);

        juce::MemoryBlock blob;
        a.getStateInformation (blob);

        VoltAudioProcessor b;
        b.setStateInformation (blob.getData(), (int) blob.getSize());
        for (int p = 0; p < NumParams; ++p)
            expectWithinAbsoluteError (b.apvts.getRawParameterValue (spec (p).id)->load(),
                                       a.apvts.getRawParameterValue (spec (p).id)->load(),
                                       (spec (p).maxValue - spec (p).minValue) * 1.0e-5f, spec (p).id);
        expectEquals (b.getPresetManager().getCurrentPresetName(), juce::String ("Session Sound"));
        expectEquals (b.getPresetManager().getMacroLabel (2), juce::String ("Grit"));

        beginTest ("Parameter IDs are unique and stable");
        juce::StringArray ids;
        for (int p = 0; p < NumParams; ++p)
        {
            expect (! ids.contains (spec (p).id), spec (p).id);
            ids.add (spec (p).id);
        }
        expectEquals (ids.size(), (int) NumParams);
        expectEquals (a.getParameters().size(), (int) NumParams);

        beginTest ("User preset save / reload round trip");
        {
            const auto dir = PresetManager::getUserPresetDirectory();
            const auto file = dir.getChildFile ("Unit Test Preset.json");
            file.deleteFile();
            a.apvts.getParameter ("flt_cutoff")->setValueNotifyingHost (0.25f);
            const auto err = pm.saveUserPreset ("Unit Test Preset", "Pad", { "Test" }, "Created by the unit tests.");
            expect (err.isEmpty(), err);
            const int idx = pm.indexOf ("Unit Test Preset");
            expect (idx >= pm.getNumFactoryPresets());
            a.apvts.getParameter ("flt_cutoff")->setValueNotifyingHost (0.9f);
            pm.loadPreset (idx);
            expectWithinAbsoluteError (a.apvts.getParameter ("flt_cutoff")->getValue(), 0.25f, 1.0e-4f);
            file.deleteFile();
            pm.rescan();
        }
    }
};

static PresetTests presetTests;
static StateTests stateTests;
