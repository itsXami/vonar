#pragma once

#include "PluginProcessor.h"

class VoltAudioProcessorEditor final : public juce::AudioProcessorEditor
{
public:
    explicit VoltAudioProcessorEditor (VoltAudioProcessor&);
    void paint (juce::Graphics&) override;

private:
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (VoltAudioProcessorEditor)
};
