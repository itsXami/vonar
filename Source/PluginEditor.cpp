#include "PluginEditor.h"

VoltAudioProcessorEditor::VoltAudioProcessorEditor (VoltAudioProcessor& p) : AudioProcessorEditor (p)
{
    setSize (1000, 620);
}

void VoltAudioProcessorEditor::paint (juce::Graphics& g)
{
    g.fillAll (juce::Colour (0xff121417));
    g.setColour (juce::Colour (0xffffc23d));
    g.setFont (juce::FontOptions (32.0f, juce::Font::bold));
    g.drawText ("VOLT", getLocalBounds(), juce::Justification::centred);
}
