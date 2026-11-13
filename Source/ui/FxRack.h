#pragma once

#include "Controls.h"
#include "../Params.h"

namespace volt::ui
{
// The EFFECTS tab: a list of the ten effects in chain order on the left (switch, name, small curve, drag handle to
// reorder) and a scrolling column of panels on the right, one per effect, expanded when the effect is on.
// Every panel has a live graph; EQ, Filter, Reverb and Compressor graphs have points you drag with the mouse.

// Colour of each effect (fx::Id order).
juce::Colour fxColour (int effect);

// Live graph of one effect. Reads the parameters straight from the state; points change them with host gestures.
class FxGraph final : public juce::Component
{
public:
    FxGraph (juce::AudioProcessorValueTreeState& state, int effect, bool mini);
    void paint (juce::Graphics&) override;
    void refresh();   // repaint when a parameter it shows has changed
    void mouseDown (const juce::MouseEvent&) override;
    void mouseDrag (const juce::MouseEvent&) override;
    void mouseUp (const juce::MouseEvent&) override;
    void mouseMove (const juce::MouseEvent&) override;
    void mouseExit (const juce::MouseEvent&) override;
    void mouseDoubleClick (const juce::MouseEvent&) override;
    void mouseWheelMove (const juce::MouseEvent&, const juce::MouseWheelDetails&) override;

    struct Handle { int xParam = -1, yParam = -1; juce::String name; };
    std::vector<Handle> handles() const;                    // the draggable points of this graph
    juce::Point<float> handlePosition (int index) const;    // in component coordinates (also used by the tests)
    void dragHandleTo (int index, juce::Point<float> pos);  // move a point (as a mouse drag would)

private:
    float get (int param) const;
    void setParam (int param, float value);
    juce::Rectangle<float> plotArea() const;
    float xOfHz (float hz) const;
    float hzOfX (float x) const;
    int hitHandle (juce::Point<float> p) const;
    juce::String valueTag (int index) const;
    juce::Path curvePath() const;

    juce::AudioProcessorValueTreeState& state;
    const int effect;
    const bool mini;
    std::vector<float> lastValues;
    std::vector<int> watched;
    int active = -1, hover = -1;
    juce::Point<float> dragStart;
    float startY = 0.0f;
};

class FxRack;

// One row of the list.
class FxRow final : public juce::Component, public juce::SettableTooltipClient
{
public:
    FxRow (FxRack& rack, juce::AudioProcessorValueTreeState& state, int effect);
    void paint (juce::Graphics&) override;
    void resized() override;
    void mouseDown (const juce::MouseEvent&) override;
    void mouseDrag (const juce::MouseEvent&) override;
    void mouseUp (const juce::MouseEvent&) override;
    void refresh();
    const int effect;

private:
    FxRack& rack;
    juce::AudioProcessorValueTreeState& state;
    FxGraph mini;
    bool dragging = false, lastOn = false;
};

// One effect panel: header (switch, name, type boxes), graph, knobs.
class FxPanel final : public juce::Component
{
public:
    FxPanel (juce::AudioProcessorValueTreeState& state, int effect);
    void paint (juce::Graphics&) override;
    void resized() override;
    void mouseDown (const juce::MouseEvent&) override;
    void refresh();
    bool isOn() const;
    int preferredHeight() const { return isOn() ? 128 : 36; }

    const int effect;
    std::vector<std::pair<int, Knob*>> macroTargets;   // mod destination -> knob (for the macro marks)
    FxGraph graph;

private:
    Knob& addKnob (int param, const juce::String& caption, int size = Knob::Medium);
    juce::AudioProcessorValueTreeState& state;
    std::vector<std::unique_ptr<juce::Component>> controls;   // header boxes and toggles
    std::vector<std::unique_ptr<Knob>> knobs;
    bool lastOn = false;
};

class FxRack final : public juce::Component
{
public:
    explicit FxRack (juce::AudioProcessorValueTreeState& state);
    void resized() override;
    void paint (juce::Graphics&) override;
    void refresh();   // 30 Hz from the editor

    // List interaction (rows call these).
    void toggle (int effect);
    void showPanel (int effect);
    void dragRow (int effect, int yInList);   // reorder while dragging a row's handle
    fx::Order order() const;

    std::vector<FxPanel*> panels() const;

private:
    void layout();
    juce::AudioProcessorValueTreeState& state;
    std::vector<std::unique_ptr<FxRow>> rows;
    std::vector<std::unique_ptr<FxPanel>> panelList;
    juce::Viewport viewport;
    juce::Component content;
    fx::Order shownOrder {};
    std::array<bool, fx::NumEffects> shownOn {};
};
} // namespace volt::ui
