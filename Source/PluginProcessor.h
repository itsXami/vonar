#pragma once

#include <juce_audio_processors/juce_audio_processors.h>
#include "Params.h"
#include "dsp/SynthEngine.h"
#include "PresetManager.h"

class VoltAudioProcessor final : public juce::AudioProcessor
{
public:
    VoltAudioProcessor();
    ~VoltAudioProcessor() override = default;

    void prepareToPlay (double sampleRate, int samplesPerBlock) override;
    void releaseResources() override {}
    bool isBusesLayoutSupported (const BusesLayout& layouts) const override;
    void processBlock (juce::AudioBuffer<float>&, juce::MidiBuffer&) override;
    using AudioProcessor::processBlock;

    juce::AudioProcessorEditor* createEditor() override;
    bool hasEditor() const override { return true; }

    const juce::String getName() const override { return "VOLT"; }
    bool acceptsMidi() const override { return true; }
    bool producesMidi() const override { return false; }
    bool isMidiEffect() const override { return false; }
    double getTailLengthSeconds() const override { return 2.0; }

    int getNumPrograms() override { return 1; }
    int getCurrentProgram() override { return 0; }
    void setCurrentProgram (int) override {}
    const juce::String getProgramName (int) override { return "Default"; } // VST3 program lists need a name
    void changeProgramName (int, const juce::String&) override {}

    void getStateInformation (juce::MemoryBlock& destData) override;
    void setStateInformation (const void* data, int sizeInBytes) override;

    juce::AudioProcessorValueTreeState apvts;

    volt::PresetManager& getPresetManager() noexcept { return *presetManager; }

    // Oscilloscope feed (audio thread pushes, UI pulls; lock-free single producer / single consumer).
    int pullScope (float* dest, int maxSamples);

    float getUiScale() const { return (float) (double) apvts.state.getProperty ("uiScale", 1.0); }
    void setUiScale (float s) { apvts.state.setProperty ("uiScale", (double) s, nullptr); }

    // Debug / test access
    volt::SynthEngine& getEngine() noexcept { return engine; }

private:
    std::unique_ptr<volt::PresetManager> presetManager;
    juce::AbstractFifo scopeFifo { 8192 };
    std::vector<float> scopeData = std::vector<float> (8192, 0.0f);

    volt::ParamReader reader;
    volt::ParamSnapshot snapshot;
    volt::SynthEngine engine;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (VoltAudioProcessor)
};
