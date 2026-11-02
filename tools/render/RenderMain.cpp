#include "PluginProcessor.h"
#include "PluginEditor.h"

// Snapshot of the editor (development aid for checking the layout on a headless machine).
static int snapshot (const juce::File& out, float scale)
{
    VoltAudioProcessor proc;
    proc.setUiScale (scale);
    proc.prepareToPlay (48000.0, 512);
    std::unique_ptr<juce::AudioProcessorEditor> ed (proc.createEditor());
    ed->setSize (juce::roundToInt (1000 * scale), juce::roundToInt (620 * scale));
    auto img = ed->createComponentSnapshot (ed->getLocalBounds(), true, 1.0f);
    out.deleteFile();
    juce::FileOutputStream os (out);
    juce::PNGImageFormat png;
    return png.writeImageToStream (img, os) ? 0 : 1;
}

int main (int argc, char** argv)
{
    juce::ScopedJuceInitialiser_GUI gui;
    juce::StringArray args;
    for (int i = 1; i < argc; ++i)
        args.add (argv[i]);

    if (args[0] == "--snapshot")
        return snapshot (juce::File::getCurrentWorkingDirectory().getChildFile (args[1]), args.size() > 2 ? args[2].getFloatValue() : 1.0f);

    std::printf ("volt_render: render mode arrives in stage 5\n");
    return 0;
}
