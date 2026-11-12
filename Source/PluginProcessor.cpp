#include "PluginProcessor.h"
#include "PluginEditor.h"

VoltAudioProcessor::VoltAudioProcessor()
    : AudioProcessor (BusesProperties().withOutput ("Output", juce::AudioChannelSet::stereo(), true)),
      apvts (*this, nullptr, "VOLT", volt::createParameterLayout())
{
    reader.attach (apvts);
    volt::WavetableBank::get(); // build the shared tables off the audio thread
    presetManager = std::make_unique<volt::PresetManager> (apvts);
    presetManager->loadPresetByName ("Init");
}

int VoltAudioProcessor::pullScope (float* dest, int maxSamples)
{
    int start1, size1, start2, size2;
    scopeFifo.prepareToRead (maxSamples, start1, size1, start2, size2);
    if (size1 > 0) std::copy (scopeData.begin() + start1, scopeData.begin() + start1 + size1, dest);
    if (size2 > 0) std::copy (scopeData.begin() + start2, scopeData.begin() + start2 + size2, dest + size1);
    scopeFifo.finishedRead (size1 + size2);
    return size1 + size2;
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

    for (int c = 0; c < 2; ++c)
    {
        const float peak = buffer.getMagnitude (c, 0, n);
        if (peak > outputPeak[c].load (std::memory_order_relaxed))
            outputPeak[c].store (peak, std::memory_order_relaxed);
    }

    // Oscilloscope: mono sum, dropped when the UI is not reading.
    int start1, size1, start2, size2;
    scopeFifo.prepareToWrite (n, start1, size1, start2, size2);
    const float* l = buffer.getReadPointer (0);
    const float* r = buffer.getReadPointer (1);
    for (int i = 0; i < size1; ++i)
        scopeData[(size_t) (start1 + i)] = 0.5f * (l[i] + r[i]);
    for (int i = 0; i < size2; ++i)
        scopeData[(size_t) (start2 + i)] = 0.5f * (l[size1 + i] + r[size1 + i]);
    scopeFifo.finishedWrite (size1 + size2);
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
