#pragma once

#include <juce_audio_processors/juce_audio_processors.h>
#include "VoltLookAndFeel.h"
#include "../dsp/Wavetables.h"
#include "../Params.h"

namespace volt::ui
{
// Shows the selected wavetable: a few faint neighbouring frames for depth and the current frame in the accent colour.
class WavetableView final : public juce::Component
{
public:
    WavetableView (juce::AudioProcessorValueTreeState& s, int oscIndex)
        : state (s),
          tableParam (state.getRawParameterValue (spec (OscA_Table + oscIndex * kOscParamCount).id)),
          posParam (state.getRawParameterValue (spec (OscA_Pos + oscIndex * kOscParamCount).id)),
          levelParam (state.getRawParameterValue (spec (OscA_Level + oscIndex * kOscParamCount).id))
    {
        setInterceptsMouseClicks (false, false);
    }

    void refresh()
    {
        const int t = juce::roundToInt (tableParam->load());
        const float p = posParam->load();
        const bool on = levelParam->load() > 0.0001f;
        if (t != lastTable || std::abs (p - lastPos) > 1.0e-4f || on != lastOn)
        {
            lastTable = t;
            lastPos = p;
            lastOn = on;
            repaint();
        }
    }

    void paint (juce::Graphics& g) override
    {
        const auto r = getLocalBounds().toFloat();
        g.setColour (colours::field);
        g.fillRoundedRectangle (r, 3.0f);
        g.setColour (colours::panelBorder);
        g.drawRoundedRectangle (r.reduced (0.5f), 3.0f, 1.0f);

        const auto& bank = WavetableBank::get();
        const auto& wt = bank[juce::jmax (0, lastTable)];
        const auto area = r.reduced (8.0f, 6.0f);
        const int ghosts = 7;
        const float depthX = 18.0f, depthY = 10.0f;
        const auto plotW = area.getWidth() - depthX;
        const auto plotH = area.getHeight() - depthY;

        auto pathFor = [&] (float framePos, float ox, float oy) {
            juce::Path p;
            const int pts = 96;
            for (int i = 0; i <= pts; ++i)
            {
                const float ph = (float) i / (float) pts;
                const float v = wt.read (0, framePos, juce::jmin (ph, 0.9999f));
                const float x = area.getX() + ox + ph * plotW;
                const float y = area.getY() + oy + plotH * 0.5f - v * plotH * 0.45f;
                if (i == 0) p.startNewSubPath (x, y); else p.lineTo (x, y);
            }
            return p;
        };

        for (int k = ghosts; k >= 1; --k)
        {
            const float fp = (float) (k - 1) / (float) (ghosts - 1) * (float) (kWtFrames - 1);
            const float d = (float) k / (float) ghosts;
            g.setColour (colours::dimText.withAlpha (0.10f + 0.08f * (1.0f - d)));
            g.strokePath (pathFor (fp, depthX * d, depthY * (1.0f - d)), juce::PathStrokeType (1.0f));
        }
        const float cur = lastPos * (float) (kWtFrames - 1);
        const float d = lastPos;
        g.setColour (lastOn ? colours::accent : colours::dimText);
        g.strokePath (pathFor (cur, depthX * d, depthY * (1.0f - d)), juce::PathStrokeType (2.0f));
    }

private:
    juce::AudioProcessorValueTreeState& state;
    std::atomic<float>* tableParam;
    std::atomic<float>* posParam;
    std::atomic<float>* levelParam;
    int lastTable = -1;
    float lastPos = -1.0f;
    bool lastOn = true;
};

// Simple triggered oscilloscope of the plugin output.
class ScopeView final : public juce::Component
{
public:
    std::function<int (float*, int)> pull; // fills up to n samples, returns count

    void refresh()
    {
        if (! pull)
            return;
        float tmp[2048];
        const int got = pull (tmp, 2048);
        for (int i = 0; i < got; ++i)
        {
            ring[(size_t) writePos] = tmp[i];
            writePos = (writePos + 1) % (int) ring.size();
        }
        if (got > 0)
            repaint();
    }

    void paint (juce::Graphics& g) override
    {
        const auto r = getLocalBounds().toFloat();
        g.setColour (colours::field);
        g.fillRoundedRectangle (r, 3.0f);
        g.setColour (colours::panelBorder);
        g.drawRoundedRectangle (r.reduced (0.5f), 3.0f, 1.0f);
        g.setColour (colours::track);
        g.drawHorizontalLine ((int) r.getCentreY(), r.getX() + 4.0f, r.getRight() - 4.0f);

        const int n = (int) ring.size();
        const int view = 512;
        int start = (writePos - view - 512 + n * 2) % n; // search window for a rising zero crossing
        for (int i = 0; i < 512; ++i)
        {
            const int a = (start + i) % n, b = (start + i + 1) % n;
            if (ring[(size_t) a] <= 0.0f && ring[(size_t) b] > 0.0f) { start = a; break; }
        }
        juce::Path p;
        const auto area = r.reduced (4.0f, 4.0f);
        for (int i = 0; i < view; ++i)
        {
            const float v = juce::jlimit (-1.0f, 1.0f, ring[(size_t) ((start + i) % n)]);
            const float x = area.getX() + area.getWidth() * (float) i / (float) (view - 1);
            const float y = area.getCentreY() - v * area.getHeight() * 0.5f;
            if (i == 0) p.startNewSubPath (x, y); else p.lineTo (x, y);
        }
        g.setColour (colours::accent);
        g.strokePath (p, juce::PathStrokeType (1.4f));
    }

private:
    std::array<float, 4096> ring {};
    int writePos = 0;
};
} // namespace volt::ui
