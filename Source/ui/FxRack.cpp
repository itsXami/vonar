#include "FxRack.h"
#include "../PresetManager.h"
#include "../dsp/Effects.h"

#include <complex>

namespace volt::ui
{
namespace
{
using cf = std::complex<float>;
constexpr float kPi = juce::MathConstants<float>::pi;

void flipBool (juce::AudioProcessorValueTreeState& state, int param)
{
    if (auto* p = state.getParameter (spec (param).id))
    {
        p->beginChangeGesture();
        p->setValueNotifyingHost (p->getValue() >= 0.5f ? 0.0f : 1.0f);
        p->endChangeGesture();
    }
}

bool isOnParam (juce::AudioProcessorValueTreeState& state, int effect)
{
    return state.getRawParameterValue (spec (fx::onParam (effect)).id)->load() >= 0.5f;
}

std::vector<int> watchedParams (int effect)
{
    switch (effect)
    {
        case fx::Distortion: return { DistType, DistDrive, DistTone, DistMix, DistKeepLow };
        case fx::Chorus:     return { ChoRate, ChoDepth, ChoMix };
        case fx::Phaser:     return { PhaRate, PhaDepth, PhaMix };
        case fx::Flanger:    return { FlaRate, FlaDepth, FlaMix };
        case fx::Filter:     return { FxfType, FxfCutoff, FxfRes, FxfMix };
        case fx::Eq:         return { EqLowFreq, EqLowGain, EqMidFreq, EqMidGain, EqMidQ, EqHighFreq, EqHighGain };
        case fx::Pump:       return { PumpAmount, PumpRate };
        case fx::Delay:      return { DlyMode, DlyTime, DlyFeedback, DlyMix };
        case fx::Reverb:     return { RevSize, RevDamp, RevMix, RevLowCut, RevHighCut };
        case fx::Compressor: return { Squash, CompThreshold, CompRatio, CompGain };
        default:             return {};
    }
}

// Frequency graphs share one axis and dB range per effect.
bool isFrequencyGraph (int e) { return e == fx::Filter || e == fx::Eq || e == fx::Reverb || e == fx::Phaser || e == fx::Flanger; }
void dbRange (int e, float& lo, float& hi)
{
    if (e == fx::Eq) { lo = -18.0f; hi = 18.0f; }
    else if (e == fx::Filter) { lo = -30.0f; hi = 18.0f; }
    else { lo = -30.0f; hi = 6.0f; }
}

juce::String hzText (float hz) { return hz >= 1000.0f ? juce::String (hz / 1000.0f, hz >= 10000.0f ? 1 : 2) + " kHz" : juce::String (juce::roundToInt (hz)) + " Hz"; }
juce::String dbText (float db) { return (db > 0.05f ? "+" : "") + juce::String (db, 1) + " dB"; }
} // namespace

juce::Colour fxColour (int effect)
{
    static const juce::uint32 c[fx::NumEffects] = { 0xffe8763a, 0xff3db8a6, 0xff6aa5e0, 0xffb39ae8, 0xff86c26a,
                                                    0xffcfc6b6, 0xffd9a05b, 0xff5bc0de, 0xff8a8ff0, 0xffe2678f };
    return juce::Colour (c[juce::jlimit (0, fx::NumEffects - 1, effect)]);
}

// =================================================================================================
FxGraph::FxGraph (juce::AudioProcessorValueTreeState& s, int e, bool isMini) : state (s), effect (e), mini (isMini)
{
    watched = watchedParams (effect);
    watched.push_back (fx::onParam (effect));
    lastValues.assign (watched.size(), -1.0e9f);
    setInterceptsMouseClicks (! mini, false);
    if (! mini)
        setRepaintsOnMouseActivity (false);
}

float FxGraph::get (int p) const { return state.getRawParameterValue (spec (p).id)->load(); }

void FxGraph::setParam (int p, float v)
{
    if (auto* r = dynamic_cast<juce::RangedAudioParameter*> (state.getParameter (spec (p).id)))
        r->setValueNotifyingHost (r->convertTo0to1 (juce::jlimit (spec (p).minValue, spec (p).maxValue, v)));
}

void FxGraph::refresh()
{
    bool changed = false;
    for (size_t i = 0; i < watched.size(); ++i)
    {
        const float v = get (watched[i]);
        if (std::abs (v - lastValues[i]) > 1.0e-6f)
        {
            lastValues[i] = v;
            changed = true;
        }
    }
    if (changed)
        repaint();
}

juce::Rectangle<float> FxGraph::plotArea() const
{
    return mini ? getLocalBounds().toFloat().reduced (1.0f, 2.0f) : getLocalBounds().toFloat().reduced (8.0f, 8.0f);
}

float FxGraph::xOfHz (float hz) const
{
    const auto a = plotArea();
    return a.getX() + a.getWidth() * std::log (juce::jlimit (20.0f, 20000.0f, hz) / 20.0f) / std::log (1000.0f);
}

float FxGraph::hzOfX (float x) const
{
    const auto a = plotArea();
    return 20.0f * std::pow (1000.0f, juce::jlimit (0.0f, 1.0f, (x - a.getX()) / a.getWidth()));
}

// The shape every graph draws, as y in 0 (top) .. 1 (bottom) for x in 0 .. 1.
juce::Path FxGraph::curvePath() const
{
    const auto a = plotArea();
    const int pts = mini ? 48 : 160;
    float lo = 0.0f, hi = 0.0f;
    dbRange (effect, lo, hi);
    auto yOfDb = [&] (float db) { return (hi - juce::jlimit (lo, hi, db)) / (hi - lo); };

    FxParams eqp;
    if (effect == fx::Eq)
    {
        eqp.eqLowFreq = get (EqLowFreq); eqp.eqLowGain = get (EqLowGain);
        eqp.eqMidFreq = get (EqMidFreq); eqp.eqMidGain = get (EqMidGain); eqp.eqMidQ = get (EqMidQ);
        eqp.eqHighFreq = get (EqHighFreq); eqp.eqHighGain = get (EqHighGain);
    }

    juce::Path path;
    for (int i = 0; i <= pts; ++i)
    {
        const float x = (float) i / (float) pts;
        const float hz = 20.0f * std::pow (1000.0f, x);
        float y = 0.5f;
        switch (effect)
        {
            case fx::Distortion:
            {
                const float t = x * 2.0f - 1.0f, drive = get (DistDrive), mix = get (DistMix);
                const float g = 1.0f + drive * 12.0f;
                float f;
                switch (juce::roundToInt (get (DistType)))
                {
                    case choices::Tube:     f = (std::tanh (g * t + 0.35f) - std::tanh (0.35f)) / (1.0f + std::tanh (0.35f)); break;
                    case choices::Hard:     f = juce::jlimit (-1.0f, 1.0f, g * t * 0.6f); break;
                    case choices::Fold:     f = std::sin (g * t * kPi * 0.25f); break;
                    case choices::Bitcrush: { const float lv = 2.0f + (1.0f - drive) * 14.0f; f = std::round (t * lv) / lv; break; }
                    case choices::Soft:
                    default:                f = std::tanh (g * t) / std::tanh (g); break;
                }
                y = 0.5f - 0.45f * (t + mix * (f - t));
                break;
            }
            case fx::Chorus:
            {
                const float cycles = juce::jlimit (0.5f, 8.0f, get (ChoRate) * 2.0f);
                y = 0.5f - 0.4f * juce::jmax (0.05f, get (ChoDepth)) * std::sin (2.0f * kPi * x * cycles);
                break;
            }
            case fx::Phaser:
            {
                const float depth = get (PhaDepth), m = get (PhaMix);
                const float fc = 180.0f * std::exp2 ((1.0f + 5.0f * depth) * 0.5f);
                const float phi = -2.0f * std::atan (hz / fc);
                const cf h = (1.0f - 0.5f * m) + 0.5f * m * std::polar (1.0f, 6.0f * phi);
                y = yOfDb (juce::Decibels::gainToDecibels (std::abs (h), -60.0f));
                break;
            }
            case fx::Flanger:
            {
                const float depth = get (FlaDepth), m = get (FlaMix);
                const float d = 0.0012f + 0.004f * depth * 0.5f, fb = 0.55f + 0.3f * depth;
                const cf z = std::polar (1.0f, -2.0f * kPi * hz * d);
                const cf delayed = z / (1.0f - fb * z);
                const cf h = 1.0f + m * (0.5f * (1.0f + delayed) - 1.0f);
                y = yOfDb (juce::Decibels::gainToDecibels (std::abs (h) * 0.6f, -60.0f));
                break;
            }
            case fx::Filter:
            {
                const float fc = get (FxfCutoff), k = 2.0f - 1.9f * get (FxfRes), m = get (FxfMix);
                const cf s (0.0f, hz / juce::jmax (fc, 1.0f));
                const cf den = s * s + k * s + 1.0f;
                cf h;
                switch (juce::roundToInt (get (FxfType)))
                {
                    case choices::FxHighPass: h = s * s / den; break;
                    case choices::FxBandPass: h = k * s / den; break;
                    case choices::FxNotch:    h = (s * s + 1.0f) / den; break;
                    default:                  h = 1.0f / den; break;
                }
                h = 1.0f + m * (h - 1.0f);
                y = yOfDb (juce::Decibels::gainToDecibels (std::abs (h), -60.0f));
                break;
            }
            case fx::Eq:
                y = yOfDb (EqFx::responseDb (eqp, 48000.0, hz));
                break;
            case fx::Reverb:
            {
                const float lc = get (RevLowCut), hc = get (RevHighCut);
                const cf sl (0.0f, hz / lc), sh (0.0f, hz / hc);
                const cf hp = lc > 20.5f ? sl * sl / (sl * sl + 1.41421f * sl + 1.0f) : cf (1.0f);
                const cf lp = hc < 19900.0f ? 1.0f / (sh * sh + 1.41421f * sh + 1.0f) : cf (1.0f);
                y = yOfDb (juce::Decibels::gainToDecibels (std::abs (hp * lp), -60.0f));
                break;
            }
            case fx::Pump:
            {
                static const double beats[] = { 2.0, 1.0, 0.5, 0.25 };
                const double cyc = beats[juce::jlimit (0, 3, juce::roundToInt (get (PumpRate)))];
                const double beat = x * 4.0;
                const float p = (float) (beat / cyc - std::floor (beat / cyc));
                float duck;
                if (p < 0.02f) duck = p / 0.02f;
                else { const float r = juce::jmax (0.0f, 1.0f - (p - 0.02f) / 0.62f); duck = r * r * (3.0f - 2.0f * r); }
                y = 0.1f + 0.8f * get (PumpAmount) * duck;
                break;
            }
            case fx::Compressor:
            {
                const float in = -60.0f + 60.0f * x, th = get (CompThreshold), ratio = juce::jmax (1.0f, get (CompRatio));
                const float out = (in < th ? in : th + (in - th) / ratio) + get (CompGain);
                y = (6.0f - juce::jlimit (-60.0f, 6.0f, out)) / 66.0f;
                break;
            }
            default: break;
        }
        const float px = a.getX() + a.getWidth() * x, py = a.getY() + a.getHeight() * juce::jlimit (0.0f, 1.0f, y);
        if (i == 0) path.startNewSubPath (px, py); else path.lineTo (px, py);
    }
    return path;
}

std::vector<FxGraph::Handle> FxGraph::handles() const
{
    if (mini)
        return {};
    switch (effect)
    {
        case fx::Eq:         return { { EqLowFreq, EqLowGain, "Low" }, { EqMidFreq, EqMidGain, "Mid" }, { EqHighFreq, EqHighGain, "High" } };
        case fx::Filter:     return { { FxfCutoff, FxfRes, "Cutoff" } };
        case fx::Reverb:     return { { RevLowCut, -1, "Low cut" }, { RevHighCut, -1, "High cut" } };
        case fx::Compressor: return { { CompThreshold, CompRatio, "Threshold" } };
        default:             return {};
    }
}

juce::Point<float> FxGraph::handlePosition (int index) const
{
    const auto a = plotArea();
    const auto hs = handles();
    if (index < 0 || index >= (int) hs.size())
        return {};
    const auto& h = hs[(size_t) index];
    float lo = 0.0f, hi = 0.0f;
    dbRange (effect, lo, hi);
    if (effect == fx::Eq)
        return { xOfHz (get (h.xParam)), a.getY() + a.getHeight() * (hi - get (h.yParam)) / (hi - lo) };
    if (effect == fx::Compressor)
    {
        const float th = get (CompThreshold);
        return { a.getX() + a.getWidth() * (th + 60.0f) / 60.0f,
                 a.getY() + a.getHeight() * (6.0f - juce::jlimit (-60.0f, 6.0f, th + get (CompGain))) / 66.0f };
    }
    // Filter and reverb: the point sits on the curve at its frequency (-3 dB for the reverb cuts).
    const float x = xOfHz (get (h.xParam));
    if (effect == fx::Reverb)
        return { x, a.getY() + a.getHeight() * (hi + 3.0f) / (hi - lo) };
    const float fc = get (FxfCutoff), k = 2.0f - 1.9f * get (FxfRes);
    const float peakDb = juce::Decibels::gainToDecibels (1.0f / juce::jmax (0.05f, k), -60.0f);
    const int t = juce::roundToInt (get (FxfType));
    const float db = t == choices::FxBandPass ? 0.0f : (t == choices::FxNotch ? -30.0f : peakDb);
    juce::ignoreUnused (fc);
    return { x, a.getY() + a.getHeight() * (hi - juce::jlimit (lo, hi, db)) / (hi - lo) };
}

void FxGraph::dragHandleTo (int index, juce::Point<float> pos)
{
    const auto hs = handles();
    if (index < 0 || index >= (int) hs.size())
        return;
    const auto a = plotArea();
    const auto& h = hs[(size_t) index];
    float lo = 0.0f, hi = 0.0f;
    dbRange (effect, lo, hi);
    switch (effect)
    {
        case fx::Eq:
            setParam (h.xParam, hzOfX (pos.x));
            setParam (h.yParam, hi - (hi - lo) * (pos.y - a.getY()) / a.getHeight());
            break;
        case fx::Filter:
            setParam (FxfCutoff, hzOfX (pos.x));
            setParam (FxfRes, startY - (pos.y - dragStart.y) / 140.0f);   // drag up = more resonance
            break;
        case fx::Reverb:
            setParam (h.xParam, hzOfX (pos.x));
            break;
        case fx::Compressor:
            setParam (CompThreshold, -60.0f + 60.0f * (pos.x - a.getX()) / a.getWidth());
            setParam (CompRatio, startY - (pos.y - dragStart.y) / 8.0f);   // drag up = higher ratio
            break;
        default: break;
    }
}

int FxGraph::hitHandle (juce::Point<float> p) const
{
    int best = -1;
    float bestD = 11.0f;
    for (int i = 0; i < (int) handles().size(); ++i)
    {
        const float d = handlePosition (i).getDistanceFrom (p);
        if (d < bestD) { bestD = d; best = i; }
    }
    return best;
}

juce::String FxGraph::valueTag (int index) const
{
    const auto hs = handles();
    if (index < 0 || index >= (int) hs.size())
        return {};
    const auto& h = hs[(size_t) index];
    switch (effect)
    {
        case fx::Eq:
            return h.name + ": " + hzText (get (h.xParam)) + "  " + dbText (get (h.yParam))
                   + (index == 1 ? "  Q " + juce::String (get (EqMidQ), 2) : juce::String());
        case fx::Filter:     return "Cutoff " + hzText (get (FxfCutoff)) + "  Res " + juce::String (juce::roundToInt (get (FxfRes) * 100.0f)) + " %";
        case fx::Reverb:     return h.name + ": " + hzText (get (h.xParam));
        case fx::Compressor: return "Threshold " + dbText (get (CompThreshold)) + "  Ratio " + juce::String (get (CompRatio), 1) + ":1";
        default:             return {};
    }
}

void FxGraph::mouseDown (const juce::MouseEvent& e)
{
    active = hitHandle (e.position);
    if (active < 0)
        return;
    dragStart = e.position;
    startY = effect == fx::Filter ? get (FxfRes) : (effect == fx::Compressor ? get (CompRatio) : 0.0f);
    const auto h = handles()[(size_t) active];
    for (int p : { h.xParam, h.yParam })
        if (p >= 0)
            state.getParameter (spec (p).id)->beginChangeGesture();
    repaint();
}

void FxGraph::mouseDrag (const juce::MouseEvent& e)
{
    if (active >= 0)
    {
        dragHandleTo (active, e.position);
        repaint();
    }
}

void FxGraph::mouseUp (const juce::MouseEvent&)
{
    if (active >= 0)
    {
        const auto h = handles()[(size_t) active];
        for (int p : { h.xParam, h.yParam })
            if (p >= 0)
                state.getParameter (spec (p).id)->endChangeGesture();
    }
    hover = active;
    active = -1;
    repaint();
}

void FxGraph::mouseMove (const juce::MouseEvent& e)
{
    const int h = hitHandle (e.position);
    if (h != hover)
    {
        hover = h;
        setMouseCursor (h >= 0 ? juce::MouseCursor::DraggingHandCursor : juce::MouseCursor::NormalCursor);
        repaint();
    }
}

void FxGraph::mouseExit (const juce::MouseEvent&)
{
    if (hover >= 0) { hover = -1; repaint(); }
}

void FxGraph::mouseDoubleClick (const juce::MouseEvent& e)
{
    const int i = hitHandle (e.position);
    if (i < 0)
        return;
    const auto h = handles()[(size_t) i];
    for (int p : { h.xParam, h.yParam })
        if (p >= 0)
        {
            auto* par = state.getParameter (spec (p).id);
            par->beginChangeGesture();
            par->setValueNotifyingHost (par->getDefaultValue());
            par->endChangeGesture();
        }
    repaint();
}

void FxGraph::mouseWheelMove (const juce::MouseEvent& e, const juce::MouseWheelDetails& w)
{
    const int i = hitHandle (e.position);
    const int p = effect == fx::Eq && i == 1 ? EqMidQ : (effect == fx::Filter && i == 0 ? FxfRes : -1);
    if (p < 0)
        return;
    const float step = p == EqMidQ ? 0.25f * get (EqMidQ) : 0.05f;
    auto* par = state.getParameter (spec (p).id);
    par->beginChangeGesture();
    setParam (p, get (p) + (w.deltaY > 0 ? step : -step));
    par->endChangeGesture();
    hover = i;
    repaint();
}

void FxGraph::paint (juce::Graphics& g)
{
    const bool on = isOnParam (state, effect);
    const auto colour = on ? fxColour (effect) : colours::faint;
    const auto r = getLocalBounds().toFloat();
    if (! mini)
        VoltLookAndFeel::drawDisplay (g, r);
    const auto a = plotArea();

    if (! mini)
    {
        g.setColour (colours::grid);
        if (isFrequencyGraph (effect))
        {
            g.setFont (VoltLookAndFeel::font (9.5f));
            for (auto [f, name] : { std::pair<float, const char*> { 100.0f, "100" }, { 1000.0f, "1k" }, { 10000.0f, "10k" } })
            {
                g.setColour (colours::grid);
                g.fillRect (xOfHz (f), a.getY(), 1.0f, a.getHeight());
                g.setColour (colours::faint.withAlpha (0.8f));
                g.drawText (name, (int) xOfHz (f) + 3, (int) a.getBottom() - 12, 30, 11, juce::Justification::left);
            }
            float lo = 0.0f, hi = 0.0f;
            dbRange (effect, lo, hi);
            g.setColour (colours::grid);
            g.fillRect (a.getX(), a.getY() + a.getHeight() * hi / (hi - lo), a.getWidth(), 1.0f);   // 0 dB
        }
        else
        {
            for (float f : { 0.25f, 0.5f, 0.75f })
                g.fillRect (a.getX(), a.getY() + a.getHeight() * f, a.getWidth(), 1.0f);
        }
    }

    if (effect == fx::Delay)
    {
        // Echoes: one bar per repeat, height from the feedback; ping-pong alternates sides.
        static const std::array<double, 12> beats = [] {
            std::array<double, 12> b {};
            for (int i = 0; i < 12; ++i)
                b[(size_t) i] = choices::divisionToBeats (choices::delayTimes()[i]);
            return b;
        }();
        const double step = beats[(size_t) juce::jlimit (0, 11, juce::roundToInt (get (DlyTime)))];
        const float fb = get (DlyFeedback), mix = juce::jmax (0.15f, get (DlyMix));
        const bool ping = juce::roundToInt (get (DlyMode)) == choices::PingPong;
        const float spacing = (float) juce::jlimit (0.04, 0.3, step / 4.0) * a.getWidth();
        float level = 1.0f;
        for (int i = 0; i < 14 && level > 0.03f; ++i)
        {
            const float x = a.getX() + 2.0f + spacing * (float) i;
            if (x > a.getRight() - 3.0f) break;
            const float h = a.getHeight() * 0.9f * level * (i == 0 ? 1.0f : mix);
            const float w = mini ? 2.0f : juce::jmax (3.0f, spacing * 0.28f);
            const bool rightSide = ping && i % 2 == 0 && i > 0;   // ping-pong: every other echo on the other side
            g.setColour (colour.withAlpha (i == 0 ? 0.55f : (rightSide ? 0.6f : 1.0f)));
            g.fillRect (x, a.getBottom() - h, w, h);
            if (i > 0)
                level *= fb;
        }
        return;
    }

    const auto path = curvePath();
    if (! mini && effect != fx::Distortion && effect != fx::Chorus && effect != fx::Compressor)
    {
        juce::Path fill (path);
        fill.lineTo (a.getRight(), a.getBottom());
        fill.lineTo (a.getX(), a.getBottom());
        fill.closeSubPath();
        g.setGradientFill (juce::ColourGradient (colour.withAlpha (0.28f), 0.0f, a.getY(), colour.withAlpha (0.03f), 0.0f,
                                                 a.getBottom(), false));
        g.fillPath (fill);
    }
    if (effect == fx::Chorus && ! mini)
    {
        // Right channel, a quarter cycle later.
        juce::Path right;
        const float cycles = juce::jlimit (0.5f, 8.0f, get (ChoRate) * 2.0f), depth = juce::jmax (0.05f, get (ChoDepth));
        for (int i = 0; i <= 160; ++i)
        {
            const float x = (float) i / 160.0f;
            const float y = 0.5f - 0.4f * depth * std::sin (2.0f * kPi * x * cycles + kPi * 0.5f);
            const juce::Point<float> p (a.getX() + a.getWidth() * x, a.getY() + a.getHeight() * y);
            if (i == 0) right.startNewSubPath (p); else right.lineTo (p);
        }
        g.setColour (colour.withAlpha (0.35f));
        g.strokePath (right, juce::PathStrokeType (1.5f));
    }
    g.setColour (colour);
    g.strokePath (path, juce::PathStrokeType (mini ? 1.4f : 2.0f, juce::PathStrokeType::curved, juce::PathStrokeType::rounded));

    if (effect == fx::Compressor && ! mini && get (Squash) > 0.005f)
    {
        g.setColour (colours::dimText);
        g.setFont (VoltLookAndFeel::font (10.5f));
        g.drawText ("+ Squash " + juce::String (juce::roundToInt (get (Squash) * 100.0f)) + " %", a.toNearestInt().removeFromBottom (14).withTrimmedLeft (4),
                    juce::Justification::left);
    }

    // Draggable points.
    const auto hs = handles();
    const int shown = active >= 0 ? active : hover;
    for (int i = 0; i < (int) hs.size(); ++i)
    {
        const auto p = handlePosition (i);
        const bool sel = i == shown;
        const float rad = sel ? 7.0f : 6.0f;
        g.setColour (sel ? colour : colours::inset);
        g.fillEllipse (p.x - rad, p.y - rad, rad * 2.0f, rad * 2.0f);
        g.setColour (colour);
        g.drawEllipse (p.x - rad, p.y - rad, rad * 2.0f, rad * 2.0f, 2.0f);
        if (! sel)
            g.fillEllipse (p.x - 2.0f, p.y - 2.0f, 4.0f, 4.0f);
    }
    if (shown >= 0)
    {
        const auto text = valueTag (shown);
        g.setFont (VoltLookAndFeel::font (11.0f));
        const int w = juce::GlyphArrangement::getStringWidthInt (g.getCurrentFont(), text) + 14;
        const auto p = handlePosition (shown);
        const bool left = p.x > a.getCentreX();
        const juce::Rectangle<float> box (left ? a.getX() + 2.0f : a.getRight() - (float) w - 2.0f, a.getY() + 2.0f, (float) w, 18.0f);
        g.setColour (colours::inset.withAlpha (0.92f));
        g.fillRoundedRectangle (box, 2.0f);
        g.setColour (colour.withAlpha (0.6f));
        g.drawRoundedRectangle (box, 2.0f, 1.0f);
        g.setColour (colours::text);
        g.drawText (text, box.toNearestInt(), juce::Justification::centred);
    }
}

// =================================================================================================
FxRow::FxRow (FxRack& r, juce::AudioProcessorValueTreeState& s, int e) : effect (e), rack (r), state (s), mini (s, e, true)
{
    addAndMakeVisible (mini);
    setTooltip (fx::names()[effect] + ": click the dot to switch on / off, click the name to show the panel, drag the grip to reorder");
}

void FxRow::resized() { mini.setBounds (getWidth() - 58, 13, 50, 18); }

void FxRow::refresh()
{
    mini.refresh();
    const bool on = isOnParam (state, effect);
    if (on != lastOn) { lastOn = on; repaint(); }
}

void FxRow::paint (juce::Graphics& g)
{
    const bool on = isOnParam (state, effect);
    const auto c = fxColour (effect);
    const auto r = getLocalBounds().toFloat();
    VoltLookAndFeel::drawSurface (g, r, dragging ? colours::macroBar : colours::panel);
    if (on)
    {
        g.setColour (c);
        g.fillRect (r.getX(), r.getY(), 3.0f, r.getHeight());
    }
    // Grip.
    g.setColour (colours::faint);
    for (int i = 0; i < 3; ++i)
        for (int j = 0; j < 2; ++j)
            g.fillEllipse (9.0f + 4.0f * (float) j, r.getCentreY() - 5.0f + 4.5f * (float) i, 2.0f, 2.0f);
    // Switch.
    const juce::Rectangle<float> dot (24.0f, r.getCentreY() - 6.0f, 12.0f, 12.0f);
    if (on) { g.setColour (c); g.fillEllipse (dot); }
    else { g.setColour (colours::track); g.drawEllipse (dot.reduced (1.0f), 2.0f); }
    g.setColour (on ? c : colours::faint);
    g.setFont (VoltLookAndFeel::font (13.0f, true));
    g.drawText (fx::names()[effect], 44, 0, getWidth() - 106, getHeight(), juce::Justification::centredLeft);
}

void FxRow::mouseDown (const juce::MouseEvent& e)
{
    dragging = e.x < 20;
    if (dragging) { setMouseCursor (juce::MouseCursor::DraggingHandCursor); repaint(); return; }
    if (e.x < 42) rack.toggle (effect);
    else rack.showPanel (effect);
}

void FxRow::mouseDrag (const juce::MouseEvent& e)
{
    if (dragging)
        rack.dragRow (effect, (int) e.getEventRelativeTo (&rack).position.y);
}

void FxRow::mouseUp (const juce::MouseEvent&)
{
    if (dragging) { dragging = false; setMouseCursor (juce::MouseCursor::NormalCursor); repaint(); }
}

// =================================================================================================
FxPanel::FxPanel (juce::AudioProcessorValueTreeState& s, int e) : effect (e), graph (s, e, false), state (s)
{
    addAndMakeVisible (graph);
    const auto c = fxColour (effect);
    auto combo = [&] (int param, const juce::String& tip) {
        auto cb = std::make_unique<ParamCombo> (state, param);
        VoltLookAndFeel::setAccent (*cb, c);
        cb->setTooltip (tip);
        controls.push_back (std::move (cb));
    };
    switch (effect)
    {
        case fx::Distortion:
        {
            combo (DistType, "Distortion type");
            auto t = std::make_unique<ParamToggle> (state, DistKeepLow, "KEEP LOW");
            VoltLookAndFeel::setAccent (*t, c);
            VoltLookAndFeel::setStyle (*t, "seg");
            t->setTooltip ("Distort only above ~160 Hz: the sub stays clean and solid");
            controls.push_back (std::move (t));
            macroTargets.push_back ({ choices::DstDistDrive, &addKnob (DistDrive, "Drive") });
            addKnob (DistTone, "Tone");
            macroTargets.push_back ({ choices::DstDistMix, &addKnob (DistMix, "Mix") });
            break;
        }
        case fx::Chorus:
            addKnob (ChoRate, "Rate"); addKnob (ChoDepth, "Depth");
            macroTargets.push_back ({ choices::DstModFxMix, &addKnob (ChoMix, "Mix") });
            break;
        case fx::Phaser:
            addKnob (PhaRate, "Rate"); addKnob (PhaDepth, "Depth");
            macroTargets.push_back ({ choices::DstModFxMix, &addKnob (PhaMix, "Mix") });
            break;
        case fx::Flanger:
            addKnob (FlaRate, "Rate"); addKnob (FlaDepth, "Depth");
            macroTargets.push_back ({ choices::DstModFxMix, &addKnob (FlaMix, "Mix") });
            break;
        case fx::Filter:
            combo (FxfType, "Filter type");
            addKnob (FxfCutoff, "Cutoff"); addKnob (FxfRes, "Resonance"); addKnob (FxfMix, "Mix");
            break;
        case fx::Eq:
            addKnob (EqLowFreq, "Low Hz", Knob::Small); addKnob (EqLowGain, "Low", Knob::Small);
            addKnob (EqMidFreq, "Mid Hz", Knob::Small); addKnob (EqMidGain, "Mid", Knob::Small);
            addKnob (EqMidQ, "Q", Knob::Small);
            addKnob (EqHighFreq, "High Hz", Knob::Small); addKnob (EqHighGain, "High", Knob::Small);
            break;
        case fx::Pump:
            combo (PumpRate, "Pump rate (tempo synced)");
            addKnob (PumpAmount, "Amount");
            break;
        case fx::Delay:
            combo (DlyMode, "Stereo / Ping-pong");
            combo (DlyTime, "Delay time (tempo synced)");
            addKnob (DlyFeedback, "Feedback");
            macroTargets.push_back ({ choices::DstDelayMix, &addKnob (DlyMix, "Mix") });
            break;
        case fx::Reverb:
            addKnob (RevSize, "Size"); addKnob (RevDamp, "Damping");
            addKnob (RevLowCut, "Low Cut"); addKnob (RevHighCut, "High Cut");
            macroTargets.push_back ({ choices::DstReverbMix, &addKnob (RevMix, "Mix") });
            break;
        case fx::Compressor:
            addKnob (Squash, "Squash"); addKnob (CompThreshold, "Threshold"); addKnob (CompRatio, "Ratio");
            addKnob (CompAttack, "Attack"); addKnob (CompRelease, "Release"); addKnob (CompGain, "Gain");
            break;
        default: break;
    }
    for (auto& c2 : controls)
        addAndMakeVisible (*c2);
    lastOn = isOn();
}

Knob& FxPanel::addKnob (int param, const juce::String& caption, int size)
{
    knobs.push_back (std::make_unique<Knob> (state, param, caption, fxColour (effect), size));
    addAndMakeVisible (*knobs.back());
    return *knobs.back();
}

bool FxPanel::isOn() const { return isOnParam (state, effect); }

void FxPanel::resized()
{
    const bool on = isOn();
    graph.setVisible (on);
    for (auto& c : controls) c->setVisible (on);
    for (auto& k : knobs) k->setVisible (on);
    if (! on)
        return;
    int y = 40;
    for (auto& c : controls)
    {
        c->setBounds (14, y, 136, 24);
        y += 30;
    }
    graph.setBounds (162, 10, 380, getHeight() - 20);
    const bool small = knobs.size() > 6;
    const int kw = small ? 56 : 64, kh = small ? 70 : 78;
    int x = 556;
    for (auto& k : knobs)
    {
        k->setBounds (x, (getHeight() - kh) / 2, kw, kh);
        x += kw + (small ? 0 : 2);
    }
}

void FxPanel::paint (juce::Graphics& g)
{
    const bool on = isOn();
    const auto c = fxColour (effect);
    const auto r = getLocalBounds().toFloat();
    VoltLookAndFeel::drawSurface (g, r, colours::panel);
    g.setColour (on ? c : colours::track);
    g.fillRect (r.getX(), r.getY(), r.getWidth(), 2.0f);
    const juce::Rectangle<float> dot (14.0f, 12.0f, 12.0f, 12.0f);
    if (on) { g.setColour (c); g.fillEllipse (dot); }
    else { g.setColour (colours::track); g.drawEllipse (dot.reduced (1.0f), 2.0f); }
    g.setColour (on ? c : colours::faint);
    g.setFont (VoltLookAndFeel::titleFont (13.0f));
    g.drawText (fx::names()[effect].toUpperCase(), 34, 8, 200, 20, juce::Justification::centredLeft);
    if (! on)
    {
        g.setColour (colours::faint);
        g.setFont (VoltLookAndFeel::font (11.0f));
        g.drawText ("off - click the dot to switch on", 200, 8, 300, 20, juce::Justification::centredLeft);
    }
}

void FxPanel::mouseDown (const juce::MouseEvent& e)
{
    if (e.y < 34 && e.x < 180)
        flipBool (state, fx::onParam (effect));
}

void FxPanel::refresh()
{
    graph.refresh();
    const bool on = isOn();
    if (on != lastOn)
    {
        lastOn = on;
        resized();
        repaint();
    }
}

// =================================================================================================
FxRack::FxRack (juce::AudioProcessorValueTreeState& s) : state (s)
{
    for (int e = 0; e < fx::NumEffects; ++e)
    {
        rows.push_back (std::make_unique<FxRow> (*this, state, e));
        addAndMakeVisible (*rows.back());
        panelList.push_back (std::make_unique<FxPanel> (state, e));
        content.addAndMakeVisible (*panelList.back());
    }
    viewport.setViewedComponent (&content, false);
    viewport.setScrollBarsShown (true, false);
    viewport.setScrollBarThickness (8);
    addAndMakeVisible (viewport);
    shownOrder.fill (-1);
}

fx::Order FxRack::order() const { return PresetManager::getFxOrder (state); }

std::vector<FxPanel*> FxRack::panels() const
{
    std::vector<FxPanel*> out;
    for (auto& p : panelList) out.push_back (p.get());
    return out;
}

void FxRack::paint (juce::Graphics& g)
{
    g.setColour (colours::dimText);
    g.setFont (VoltLookAndFeel::titleFont (11.5f));
    g.drawText ("SIGNAL CHAIN", 14, 4, 200, 20, juce::Justification::centredLeft);
    g.setColour (colours::faint);
    g.setFont (VoltLookAndFeel::font (10.5f));
    g.drawText ("drag the grip to reorder", 14, getHeight() - 22, 210, 16, juce::Justification::centredLeft);
}

void FxRack::resized()
{
    viewport.setBounds (232, 2, getWidth() - 238, getHeight() - 4);
    shownOrder.fill (-1);
    layout();
}

void FxRack::layout()
{
    const auto o = order();
    for (int i = 0; i < fx::NumEffects; ++i)
        rows[(size_t) o[(size_t) i]]->setBounds (6, 28 + i * 47, 220, 43);
    const int w = viewport.getWidth() - viewport.getScrollBarThickness() - 2;
    int y = 0;
    for (int e : o)
    {
        auto& p = *panelList[(size_t) e];
        p.setBounds (0, y, w, p.preferredHeight());
        y += p.preferredHeight() + 6;
    }
    content.setSize (w, juce::jmax (y, viewport.getHeight()));
    shownOrder = o;
    for (int e = 0; e < fx::NumEffects; ++e)
        shownOn[(size_t) e] = isOnParam (state, e);
}

void FxRack::refresh()
{
    bool relayout = order() != shownOrder;
    for (int e = 0; e < fx::NumEffects; ++e)
        relayout = relayout || isOnParam (state, e) != shownOn[(size_t) e];
    if (relayout)
        layout();
    for (auto& r : rows) r->refresh();
    for (auto& p : panelList) p->refresh();
}

void FxRack::toggle (int effect)
{
    flipBool (state, fx::onParam (effect));
    refresh();
}

void FxRack::showPanel (int effect)
{
    if (effect < 0 || effect >= fx::NumEffects)
        return;
    refresh();
    viewport.setViewPosition (0, panelList[(size_t) effect]->getY());
}

void FxRack::dragRow (int effect, int y)
{
    auto o = order();
    const int target = juce::jlimit (0, fx::NumEffects - 1, (y - 28) / 47);
    const auto it = std::find (o.begin(), o.end(), effect);
    const int from = (int) (it - o.begin());
    if (from == target)
        return;
    std::vector<int> v (o.begin(), o.end());
    v.erase (v.begin() + from);
    v.insert (v.begin() + target, effect);
    std::copy (v.begin(), v.end(), o.begin());
    PresetManager::setFxOrder (state, o);
    refresh();
}
} // namespace volt::ui
