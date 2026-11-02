#include "PluginProcessor.h"
#include "PluginEditor.h"

VoltAudioProcessor::VoltAudioProcessor()
    : AudioProcessor (BusesProperties().withOutput ("Output", juce::AudioChannelSet::stereo(), true)),
      apvts (*this, nullptr, "VOLT", volt::createParameterLayout())
{
    reader.attach (apvts);
    volt::WavetableBank::get(); // build the shared tables off the audio thread
}

void VoltAudioProcessor::prepareToPlay (double sampleRate, int samplesPerBlock)
{
    engine.prepare (sampleRate, juce::jmax (1, samplesPerBlock));
}

bool VoltAudioProcessor::isBusesLayoutSupported (const BusesLayout& layouts) const
{
    return layouts.getMainOutputChannelSet() == juce::AudioChannelSet::stereo()
        && layouts.getMainInputChannelSet().isDisabled();
}

void VoltAudioProcessor::processBlock (juce::AudioBuffer<float>& buffer, juce::MidiBuffer& midi)
{
    juce::ScopedNoDenormals noDenormals;
    const int n = buffer.getNumSamples();
    if (buffer.getNumChannels() < 2)
    {
        buffer.clear();
        return;
    }

    volt::TransportInfo t;
    if (auto* ph = getPlayHead())
    {
        if (auto pos = ph->getPosition())
        {
            if (auto bpm = pos->getBpm())
                t.bpm = *bpm;
            if (auto ppq = pos->getPpqPosition())
                t.ppq = *ppq;
            t.playing = pos->getIsPlaying() && pos->getPpqPosition().hasValue();
        }
    }

    reader.read (snapshot);
    engine.process (buffer.getWritePointer (0), buffer.getWritePointer (1), n, midi, snapshot, t);
    for (int c = 2; c < buffer.getNumChannels(); ++c)
        buffer.clear (c, 0, n);
}

juce::AudioProcessorEditor* VoltAudioProcessor::createEditor() { return new VoltAudioProcessorEditor (*this); }

void VoltAudioProcessor::getStateInformation (juce::MemoryBlock& destData)
{
    if (auto xml = apvts.copyState().createXml())
        copyXmlToBinary (*xml, destData);
}

void VoltAudioProcessor::setStateInformation (const void* data, int sizeInBytes)
{
    if (auto xml = getXmlFromBinary (data, sizeInBytes))
        if (xml->hasTagName (apvts.state.getType()))
            apvts.replaceState (juce::ValueTree::fromXml (*xml));
}

juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter() { return new VoltAudioProcessor(); }
