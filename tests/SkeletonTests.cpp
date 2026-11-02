#include "PluginProcessor.h"

struct SkeletonTests final : juce::UnitTest
{
    SkeletonTests() : juce::UnitTest ("Skeleton", "VOLT") {}
    void runTest() override
    {
        beginTest ("Processor constructs");
        VoltAudioProcessor p;
        expect (p.getParameters().size() > 0);
    }
};
static SkeletonTests skeletonTests;
