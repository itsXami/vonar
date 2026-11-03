#pragma once

#include <juce_audio_processors/juce_audio_processors.h>
#include "VoltLookAndFeel.h"
#include "../dsp/Wavetables.h"
#include "../Params.h"
#include "../dsp/Formants.h"
#include <complex>

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
          levelParam (state.getRawParameterValue (spec (OscA_Level + oscIndex * kOscParamCount).id)),
          typeParam (state.getRawParameterValue (spec (OscA_Type + oscIndex * kOscParamCount).id))
    {
        setInterceptsMouseClicks (false, false);
    }

    void refresh()
    {
        const int t = juce::roundToInt (tableParam->load());
        const float p = posParam->load();
        const bool on = levelParam->load() > 0.0001f;
        const bool str = juce::roundToInt (typeParam->load()) == choices::String;
        if (t != lastTable || std::abs (p - lastPos) > 1.0e-4f || on != lastOn || str != lastString)
        {
            lastString = str;
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
        g.setColour (lastOn ? colours::osc : colours::dimText);
        g.strokePath (pathFor (cur, depthX * d, depthY * (1.0f - d)), juce::PathStrokeType (2.0f));
        if (lastString)
        {
            g.setFont (VoltLookAndFeel::font (11.0f, true));
            g.setColour (colours::osc);
            g.drawText ("STRING  -  pluck shape", getLocalBounds().reduced (8, 4), juce::Justification::topRight);
        }
    }

private:
    juce::AudioProcessorValueTreeState& state;
    std::atomic<float>* tableParam;
    std::atomic<float>* posParam;
    std::atomic<float>* levelParam;
    std::atomic<float>* typeParam;
    bool lastString = false;
    int lastTable = -1;
    float lastPos = -1.0f;
    bool lastOn = true;
};

// Magnitude response of the current filter settings, using the same coefficient mapping as VoiceFilter
// (analogue prototypes; drive saturation and modulation are not shown).
class FilterResponseView final : public juce::Component
{
public:
    explicit FilterResponseView (juce::AudioProcessorValueTreeState& s)
        : type (s.getRawParameterValue ("flt_type")), cutoff (s.getRawParameterValue ("flt_cutoff")),
          res (s.getRawParameterValue ("flt_res")), vowel (s.getRawParameterValue ("flt_vowel"))
    {
        setInterceptsMouseClicks (false, false);
    }

    void refresh()
    {
        const float v[4] = { type->load(), cutoff->load(), res->load(), vowel->load() };
        bool changed = false;
        for (int i = 0; i < 4; ++i)
            changed |= std::abs (v[i] - last[i]) > 1.0e-5f;
        if (changed)
        {
            std::copy (v, v + 4, last);
            repaint();
        }
    }

    static float magnitudeDb (int t, float fc, float r, float vw, float f)
    {
        using cf = std::complex<float>;
        const float q = 0.5f * std::pow (40.0f, juce::jlimit (0.0f, 1.0f, r));
        const float k = 1.0f / q;
        const cf s (0.0f, f / juce::jmax (fc, 1.0f));
        auto svfDen = [&] (cf x, float kk) { return x * x + kk * x + 1.0f; };
        cf h;
        switch (t)
        {
            case choices::LP12:  h = 1.0f / svfDen (s, k); break;
            case choices::LP24:  h = 1.0f / (svfDen (s, 1.41421356f) * svfDen (s, k)); break;
            case choices::HP:    h = s * s / svfDen (s, k); break;
            case choices::BP:    h = s * (juce::jmax (k, 0.25f) * 1.6f) / svfDen (s, k); break;
            case choices::Notch: h = (s * s + 1.0f) / svfDen (s, k); break;
            case choices::Ladder:
            {
                const float kl = 3.96f * juce::jlimit (0.0f, 1.0f, r);
                const cf p = (1.0f + s) * (1.0f + s);
                h = (1.0f + 0.35f * kl) / (p * p + kl);
                break;
            }
            case choices::CombPlus:
            case choices::CombMinus:
            {
                const float mag = 0.2f + 0.775f * std::sqrt (juce::jlimit (0.0f, 1.0f, r));
                const float fb = t == choices::CombPlus ? mag : -mag;
                const cf z = std::polar (1.0f, -juce::MathConstants<float>::twoPi * f / juce::jmax (fc, 1.0f));
                h = (1.0f - 0.85f * mag) / (1.0f - fb * z);
                break;
            }
            case choices::Formant:
            default:
            {
                const auto v = vowelAt (vw);
                const float shift = juce::jlimit (0.5f, 2.0f, fc / 1000.0f);
                const float bwScale = 2.0f * std::pow (0.25f, juce::jlimit (0.0f, 1.0f, r));
                for (size_t i = 0; i < 3; ++i)
                {
                    const float fi = v.freq[i] * shift;
                    const float kf = 1.0f / juce::jlimit (0.7f, 60.0f, fi / (v.bw[i] * bwScale));
                    const cf si (0.0f, f / fi);
                    h += std::pow (10.0f, v.gainDb[i] / 20.0f) * kf * si / svfDen (si, kf);
                }
                h *= 2.2f;
                break;
            }
        }
        return juce::Decibels::gainToDecibels (std::abs (h), -60.0f);
    }

    void paint (juce::Graphics& g) override
    {
        const auto r = getLocalBounds().toFloat();
        g.setColour (colours::field);
        g.fillRoundedRectangle (r, 3.0f);
        const auto area = r.reduced (4.0f, 6.0f);
        const float minDb = -36.0f, maxDb = 24.0f;
        auto xOf = [&] (float f) { return area.getX() + area.getWidth() * std::log (f / 20.0f) / std::log (1000.0f); };
        auto yOf = [&] (float db) { return area.getY() + area.getHeight() * (maxDb - juce::jlimit (minDb, maxDb, db)) / (maxDb - minDb); };

        g.setColour (colours::track.withAlpha (0.7f));
        for (float f : { 100.0f, 1000.0f, 10000.0f })
            g.drawVerticalLine ((int) xOf (f), area.getY(), area.getBottom());
        g.drawHorizontalLine ((int) yOf (0.0f), area.getX(), area.getRight());
        g.setColour (colours::dimText.withAlpha (0.7f));
        g.setFont (VoltLookAndFeel::font (10.0f));
        g.drawText ("100", (int) xOf (100.0f) + 2, (int) area.getBottom() - 12, 30, 12, juce::Justification::left);
        g.drawText ("1k", (int) xOf (1000.0f) + 2, (int) area.getBottom() - 12, 30, 12, juce::Justification::left);
        g.drawText ("10k", (int) xOf (10000.0f) + 2, (int) area.getBottom() - 12, 30, 12, juce::Justification::left);

        const int t = juce::roundToInt (last[0]);
        juce::Path curve;
        const int pts = 160;
        for (int i = 0; i <= pts; ++i)
        {
            const float f = 20.0f * std::pow (1000.0f, (float) i / (float) pts);
            const float y = yOf (magnitudeDb (t, last[1], last[2], last[3], f));
            const float x = area.getX() + area.getWidth() * (float) i / (float) pts;
            if (i == 0) curve.startNewSubPath (x, y); else curve.lineTo (x, y);
        }
        juce::Path fill (curve);
        fill.lineTo (area.getRight(), area.getBottom());
        fill.lineTo (area.getX(), area.getBottom());
        fill.closeSubPath();
        g.setGradientFill (juce::ColourGradient (colours::filter.withAlpha (0.28f), 0.0f, area.getY(),
                                                 colours::filter.withAlpha (0.02f), 0.0f, area.getBottom(), false));
        g.fillPath (fill);
        g.setColour (colours::filter);
        g.strokePath (curve, juce::PathStrokeType (2.0f));
    }

private:
    std::atomic<float>* type;
    std::atomic<float>* cutoff;
    std::atomic<float>* res;
    std::atomic<float>* vowel;
    float last[4] { -1.0f, -1.0f, -1.0f, -1.0f };
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
        g.setColour (colours::fx);
        g.strokePath (p, juce::PathStrokeType (1.4f));
    }

private:
    std::array<float, 4096> ring {};
    int writePos = 0;
};
} // namespace volt::ui
