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
        const auto r = getLocalBounds().toFloat().withTrimmedBottom (1.0f);
        VoltLookAndFeel::drawDisplay (g, r);

        // The table as a surface: frames drawn back to front, each one hiding what lies behind it.
        const auto& wt = WavetableBank::get()[juce::jmax (0, lastTable)];
        const float pad = 14.0f;
        const float depthX = r.getWidth() * 0.26f, depthY = r.getHeight() * 0.44f;
        const float plotW = r.getWidth() - 2.0f * pad - depthX;
        const float amp = (r.getHeight() - 2.0f * pad - depthY) * 0.5f;
        const auto colour = lastOn ? colours::osc : colours::dimText;
        const int frames = 18, pts = 96;

        auto frame = [&] (float d, bool current) {
            const float x0 = r.getX() + pad + d * depthX;
            const float yc = r.getBottom() - pad - amp - d * depthY;
            juce::Path line;
            for (int i = 0; i <= pts; ++i)
            {
                const float ph = (float) i / (float) pts;
                const float v = wt.read (0, d * (float) (kWtFrames - 1), juce::jmin (ph, 0.9999f));
                const float x = x0 + ph * plotW, y = yc - v * amp * 0.9f;
                if (i == 0) line.startNewSubPath (x, y); else line.lineTo (x, y);
            }
            juce::Path body (line);
            body.lineTo (x0 + plotW, yc + amp + 2.0f);
            body.lineTo (x0, yc + amp + 2.0f);
            body.closeSubPath();
            g.setColour (colours::inset);
            g.fillPath (body);
            if (current)
            {
                g.setColour (colour.withAlpha (0.16f));
                g.strokePath (line, juce::PathStrokeType (6.0f, juce::PathStrokeType::curved, juce::PathStrokeType::rounded));
                g.setColour (colour);
                g.strokePath (line, juce::PathStrokeType (2.2f, juce::PathStrokeType::curved, juce::PathStrokeType::rounded));
            }
            else
            {
                const bool behind = d > lastPos;
                g.setColour (colour.withAlpha (0.2f + 0.38f * (1.0f - d) * (behind ? 0.6f : 1.0f)));
                g.strokePath (line, juce::PathStrokeType (1.0f));
            }
        };

        bool drawn = false;
        for (int k = frames - 1; k >= 0; --k)
        {
            const float d = (float) k / (float) (frames - 1);
            if (! drawn && d <= lastPos)
            {
                frame (lastPos, true);
                drawn = true;
                if (std::abs (d - lastPos) < 0.5f / (float) (frames - 1))
                    continue;
            }
            frame (d, false);
        }

        g.setFont (VoltLookAndFeel::font (11.0f));
        g.setColour (lastString ? colours::osc : colours::faint);
        const auto readout = lastString ? juce::String ("String: pluck shape")
                                        : juce::String (juce::roundToInt (lastPos * (float) (kWtFrames - 1)) + 1) + " / " + juce::String (kWtFrames);
        g.drawText (readout, getLocalBounds().reduced (9, 6), juce::Justification::topRight);
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
        const auto r = getLocalBounds().toFloat().withTrimmedBottom (1.0f);
        VoltLookAndFeel::drawDisplay (g, r);
        const auto area = r.reduced (10.0f, 8.0f).withTrimmedBottom (12.0f);
        const float minDb = -36.0f, maxDb = 24.0f;
        auto xOf = [&] (float f) { return area.getX() + area.getWidth() * std::log (f / 20.0f) / std::log (1000.0f); };
        auto yOf = [&] (float db) { return area.getY() + area.getHeight() * (maxDb - juce::jlimit (minDb, maxDb, db)) / (maxDb - minDb); };

        g.setFont (VoltLookAndFeel::font (10.0f));
        const std::pair<float, const char*> marks[] = { { 100.0f, "100" }, { 1000.0f, "1k" }, { 10000.0f, "10k" } };
        for (const auto& [f, name] : marks)
        {
            g.setColour (colours::grid);
            g.fillRect (xOf (f), area.getY(), 1.0f, area.getHeight());
            g.setColour (colours::faint);
            g.drawText (name, (int) xOf (f) - 20, (int) area.getBottom() + 1, 40, 12, juce::Justification::centred);
        }
        g.setColour (colours::grid);
        g.fillRect (area.getX(), yOf (0.0f), area.getWidth(), 1.0f);
        g.fillRect (area.getX(), yOf (-24.0f), area.getWidth(), 1.0f);
        g.setColour (colours::faint);
        g.drawText ("0 dB", (int) area.getX() + 3, (int) yOf (0.0f) - 13, 40, 12, juce::Justification::left);

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
        g.setGradientFill (juce::ColourGradient (colours::filter.withAlpha (0.30f), 0.0f, area.getY(),
                                                 colours::filter.withAlpha (0.02f), 0.0f, area.getBottom(), false));
        g.fillPath (fill);
        g.setColour (colours::filter);
        g.strokePath (curve, juce::PathStrokeType (2.0f, juce::PathStrokeType::curved, juce::PathStrokeType::rounded));
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
        const auto r = getLocalBounds().toFloat().withTrimmedBottom (1.0f);
        VoltLookAndFeel::drawDisplay (g, r);
        g.setColour (colours::grid);
        g.fillRect (r.getX() + 6.0f, r.getCentreY(), r.getWidth() - 12.0f, 1.0f);

        const int n = (int) ring.size();
        const int view = 512;
        int start = (writePos - view - 512 + n * 2) % n; // search window for a rising zero crossing
        for (int i = 0; i < 512; ++i)
        {
            const int a = (start + i) % n, b = (start + i + 1) % n;
            if (ring[(size_t) a] <= 0.0f && ring[(size_t) b] > 0.0f) { start = a; break; }
        }
        juce::Path p;
        const auto area = r.reduced (6.0f, 8.0f);
        for (int i = 0; i < view; ++i)
        {
            const float v = juce::jlimit (-1.0f, 1.0f, ring[(size_t) ((start + i) % n)]);
            const float x = area.getX() + area.getWidth() * (float) i / (float) (view - 1);
            const float y = area.getCentreY() - v * area.getHeight() * 0.5f;
            if (i == 0) p.startNewSubPath (x, y); else p.lineTo (x, y);
        }
        g.setColour (colours::value);
        g.strokePath (p, juce::PathStrokeType (1.5f, juce::PathStrokeType::curved, juce::PathStrokeType::rounded));
    }

private:
    std::array<float, 4096> ring {};
    int writePos = 0;
};

// Shape of one envelope. Segment widths follow the knob positions (not a linear time axis), so short and long
// settings both stay readable.
class EnvelopeView final : public juce::Component
{
public:
    enum Mode { Amp, Filter, Mod, Pitch };

    explicit EnvelopeView (juce::AudioProcessorValueTreeState& s) : state (s)
    {
        setInterceptsMouseClicks (false, false);
        const int first[3] = { AmpA, FenvA, MenvA };
        for (int e = 0; e < 3; ++e)
            for (int k = 0; k < 4; ++k)
                adsr[e][k] = state.getParameter (spec (first[e] + k).id);
        pitch[0] = state.getParameter (spec (PenvAmt).id);
        pitch[1] = state.getParameter (spec (PenvDecay).id);
    }

    void setMode (int m) { mode = m; last[0] = -1.0f; refresh(); }

    void refresh()
    {
        float v[4] { 0.0f, 0.0f, 0.0f, 0.0f };
        if (mode == Pitch)
        {
            v[0] = pitch[0]->getValue();
            v[1] = pitch[1]->getValue();
        }
        else
            for (int k = 0; k < 4; ++k)
                v[k] = adsr[mode][k]->getValue();
        bool changed = false;
        for (int k = 0; k < 4; ++k)
            changed |= std::abs (v[k] - last[k]) > 1.0e-5f;
        if (changed)
        {
            std::copy (v, v + 4, last);
            repaint();
        }
    }

    void paint (juce::Graphics& g) override
    {
        const auto r = getLocalBounds().toFloat().withTrimmedBottom (1.0f);
        VoltLookAndFeel::drawDisplay (g, r);
        const auto area = r.reduced (12.0f, 16.0f);
        g.setColour (colours::grid);
        for (int k = 1; k < 4; ++k)
            g.fillRect (area.getX() + area.getWidth() * (float) k / 4.0f, r.getY() + 5.0f, 1.0f, r.getHeight() - 10.0f);

        juce::Path line;
        std::vector<juce::Point<float>> nodes;
        const float x0 = area.getX(), yb = area.getBottom(), yt = area.getY(), w = area.getWidth();
        if (mode == Pitch)
        {
            // amount is bipolar around the centre line; the pitch falls (or rises) back to the note
            const float yc = area.getCentreY();
            const float amount = (last[0] - 0.5f) * 2.0f;
            const float y0 = yc - amount * area.getHeight() * 0.5f;
            const float xe = x0 + w * (0.08f + 0.8f * last[1]);
            g.fillRect (x0, yc, w, 1.0f);
            line.startNewSubPath (x0, y0);
            line.quadraticTo (x0 + (xe - x0) * 0.25f, yc, xe, yc);
            line.lineTo (x0 + w, yc);
            nodes = { { x0, y0 }, { xe, yc } };
        }
        else
        {
            const float seg = w * 0.26f;
            const float xa = x0 + seg * (0.04f + 0.96f * last[0]);
            const float xd = xa + seg * (0.06f + 0.94f * last[1]);
            const float ys = yb - last[2] * (yb - yt);
            const float xr = x0 + w * 0.70f;
            const float xe = xr + seg * (0.06f + 0.94f * last[3]);
            line.startNewSubPath (x0, yb);
            line.lineTo (xa, yt);
            line.quadraticTo (xa + (xd - xa) * 0.22f, ys, xd, ys);
            line.lineTo (xr, ys);
            line.quadraticTo (xr + (xe - xr) * 0.22f, yb, xe, yb);
            nodes = { { xa, yt }, { xd, ys }, { xr, ys }, { xe, yb } };
            juce::Path fill (line);
            fill.closeSubPath();
            g.setColour (colours::env.withAlpha (0.13f));
            g.fillPath (fill);
        }
        g.setColour (colours::env);
        g.strokePath (line, juce::PathStrokeType (2.0f, juce::PathStrokeType::curved, juce::PathStrokeType::rounded));
        for (const auto& n : nodes)
        {
            const auto box = juce::Rectangle<float> (7.0f, 7.0f).withCentre (n);
            g.setColour (colours::inset);
            g.fillRect (box);
            g.setColour (colours::env);
            g.drawRect (box, 1.6f);
        }
    }

private:
    juce::AudioProcessorValueTreeState& state;
    juce::RangedAudioParameter* adsr[3][4] {};
    juce::RangedAudioParameter* pitch[2] {};
    int mode = Amp;
    float last[4] { -1.0f, -1.0f, -1.0f, -1.0f };
};

// Two cycles of the selected LFO shape.
class LfoView final : public juce::Component
{
public:
    LfoView (juce::AudioProcessorValueTreeState& s, int lfo)
        : shape (s.getRawParameterValue (spec (Lfo1_Shape + lfo * kLfoParamCount).id)),
          depth (s.getRawParameterValue (spec (Lfo1_Depth + lfo * kLfoParamCount).id))
    {
        setInterceptsMouseClicks (false, false);
    }

    void refresh()
    {
        const int sh = juce::roundToInt (shape->load());
        const float d = depth->load();
        if (sh != lastShape || std::abs (d - lastDepth) > 1.0e-4f)
        {
            lastShape = sh;
            lastDepth = d;
            repaint();
        }
    }

    void paint (juce::Graphics& g) override
    {
        const auto r = getLocalBounds().toFloat().withTrimmedBottom (1.0f);
        VoltLookAndFeel::drawDisplay (g, r);
        const auto area = r.reduced (7.0f, 9.0f);
        g.setColour (colours::grid);
        g.fillRect (area.getX(), area.getCentreY(), area.getWidth(), 1.0f);
        static const float steps[8] = { 0.3f, -0.7f, 0.9f, -0.2f, 0.55f, -0.95f, 0.1f, 0.75f };
        auto valueAt = [&] (float t) {
            const float ph = t - std::floor (t);
            switch (lastShape)
            {
                case choices::Triangle:   return 1.0f - 4.0f * std::abs (ph - 0.5f);
                case choices::Saw:        return 1.0f - 2.0f * ph;
                case choices::Square:     return ph < 0.5f ? 1.0f : -1.0f;
                case choices::SampleHold: return steps[juce::jlimit (0, 7, (int) (t * 4.0f))];
                default:                  return std::sin (juce::MathConstants<float>::twoPi * ph);
            }
        };
        juce::Path p;
        const int pts = 160;
        const float amp = area.getHeight() * 0.5f * (0.25f + 0.75f * juce::jlimit (0.0f, 1.0f, lastDepth));
        for (int i = 0; i <= pts; ++i)
        {
            const float t = 2.0f * (float) i / (float) pts;
            const float x = area.getX() + area.getWidth() * (float) i / (float) pts;
            const float y = area.getCentreY() - amp * valueAt (juce::jmin (t, 1.9999f));
            if (i == 0) p.startNewSubPath (x, y); else p.lineTo (x, y);
        }
        g.setColour (colours::mod);
        g.strokePath (p, juce::PathStrokeType (1.8f, juce::PathStrokeType::mitered, juce::PathStrokeType::rounded));
    }

private:
    std::atomic<float>* shape;
    std::atomic<float>* depth;
    int lastShape = -1;
    float lastDepth = -1.0f;
};

// Stereo output peak meter with a short peak hold.
class LevelMeter final : public juce::Component
{
public:
    std::function<float (int)> pull; // peak of one channel since the last call

    void refresh()
    {
        if (! pull)
            return;
        bool changed = false;
        for (int c = 0; c < 2; ++c)
        {
            const float db = juce::Decibels::gainToDecibels (pull (c), -60.0f);
            const float next = juce::jmax (db, level[c] - 1.6f);          // about 48 dB per second fall at 30 Hz
            if (db >= hold[c]) { hold[c] = db; holdTime[c] = 30; }
            else if (--holdTime[c] < 0) hold[c] = juce::jmax (-60.0f, hold[c] - 1.0f);
            changed |= std::abs (next - level[c]) > 0.05f || holdTime[c] > -40;
            level[c] = next;
        }
        if (changed)
            repaint();
    }

    void paint (juce::Graphics& g) override
    {
        const float w = ((float) getWidth() - 4.0f) * 0.5f;
        for (int c = 0; c < 2; ++c)
        {
            const auto bar = juce::Rectangle<float> ((float) c * (w + 4.0f), 0.0f, w, (float) getHeight() - 1.0f);
            VoltLookAndFeel::drawDisplay (g, bar);
            const auto in = bar.reduced (1.5f);
            auto yOf = [&] (float db) { return in.getBottom() - in.getHeight() * juce::jlimit (0.0f, 1.0f, (db + 48.0f) / 48.0f); };
            if (level[c] > -48.0f)
            {
                g.setColour (level[c] > -0.6f ? colours::filter : colours::value);
                g.fillRect (juce::Rectangle<float>::leftTopRightBottom (in.getX(), yOf (level[c]), in.getRight(), in.getBottom()));
            }
            if (hold[c] > -48.0f)
            {
                g.setColour (colours::macro);
                g.fillRect (in.getX(), yOf (hold[c]), in.getWidth(), 1.5f);
            }
        }
    }

private:
    float level[2] { -60.0f, -60.0f }, hold[2] { -60.0f, -60.0f };
    int holdTime[2] { 0, 0 };
};
} // namespace volt::ui
