// VOLT offline preset renderer.
//
//   VOLT_Render [--out DIR] [--dir PRESET_DIR] [--preset TEXT] [--no-previews] [--block N]
//   VOLT_Render --snapshot FILE.png [SCALE]
//
// Loads every factory preset into the real plugin processor, plays a category-specific test phrase
// (bass note, chord or short sequence) at 48 kHz / 120 BPM with a running transport, renders the tail and
// writes report.json, report.md and short FLAC previews. Exit code 1 if any preset fails a check.
#include "PluginProcessor.h"
#include "PluginEditor.h"
#include <juce_audio_formats/juce_audio_formats.h>

namespace
{
constexpr double kSampleRate = 48000.0;
constexpr double kBpm = 120.0;
constexpr double kTailSeconds = 8.0;

// Thresholds (see docs/DECISIONS.md, stage 5)
constexpr float kSilenceDb = -40.0f;       // peak below this = silent
constexpr float kMaxPeakDb = 0.0f;         // > 0 dBFS = clipping
constexpr float kMaxDc = 0.01f;            // |mean| over the active part
constexpr float kTailEndDb = -60.0f;       // RMS of the last 0.5 s of the 8 s tail
constexpr float kMaxLimiterDb = 3.0f;      // more = bad gain staging
constexpr float kLoudnessWindow = 5.0f;    // +- LU around the median of all presets
constexpr float kMinLoudness = -24.0f, kMaxLoudness = -9.0f;

struct NoteEvent { double time; int note; bool on; float vel; };

struct Phrase
{
    juce::String name;
    std::vector<NoteEvent> events;
    double end = 0.0; // time of the last note-off
};

Phrase phraseFor (const juce::String& category)
{
    Phrase p;
    auto add = [&p] (double t0, double t1, int note, float vel = 0.85f) {
        p.events.push_back ({ t0, note, true, vel });
        p.events.push_back ({ t1, note, false, 0.0f });
        p.end = std::max (p.end, t1);
    };
    if (category == "Bass")
    {
        p.name = "bass note C2";
        add (0.0, 1.6, 36, 0.9f);
    }
    else if (category == "Lead")
    {
        p.name = "sequence C4-Eb4-G4-Bb4-C5";
        const int notes[] = { 60, 63, 67, 70, 72 };
        for (int i = 0; i < 5; ++i)
            add (i * 0.35, i * 0.35 + (i == 4 ? 0.8 : 0.315), notes[i], 0.8f + 0.04f * (float) i);
    }
    else if (category == "Arp")
    {
        p.name = "held chord Cm (arp)";
        for (int n : { 48, 55, 60, 63 })
            add (0.0, 2.6, n, 0.85f);
    }
    else if (category == "Guitar")
    {
        p.name = "strummed Em chord x2";
        const int notes[] = { 40, 47, 52, 55, 59, 64 };
        for (int k = 0; k < 2; ++k)
            for (int i = 0; i < 6; ++i)
                add (k * 1.2 + i * 0.018, k * 1.2 + 1.05, notes[i], 0.75f + 0.04f * (float) i);
    }
    else if (category == "Pluck")
    {
        p.name = "plucked melody C4-E4-G4-C5-B4-G4";
        const int notes[] = { 60, 64, 67, 72, 71, 67 };
        for (int i = 0; i < 6; ++i)
            add (i * 0.3, i * 0.3 + 0.22, notes[i], 0.78f + 0.03f * (float) (i % 3));
    }
    else if (category == "Bell")
    {
        p.name = "bell notes C5-G5-E5, then C major triad";
        add (0.0, 0.9, 72, 0.85f);
        add (0.5, 1.4, 79, 0.8f);
        add (1.0, 1.9, 76, 0.8f);
        for (int n : { 60, 64, 67 })
            add (1.6, 2.6, n, 0.75f);
    }
    else if (category == "Woodwind")
    {
        p.name = "legato line G4-A4-C5-B4-G4";
        const int notes[] = { 67, 69, 72, 71, 67 };
        for (int i = 0; i < 5; ++i)
            add (i * 0.45, i * 0.45 + (i == 4 ? 0.9 : 0.47), notes[i], 0.8f);
    }
    else if (category == "FX")
    {
        p.name = "single note C4";
        add (0.0, 2.0, 60, 0.9f);
    }
    else
    {
        p.name = "chord Cmaj7";
        for (int n : { 48, 55, 59, 64 })
            add (0.0, 2.4, n, 0.8f);
    }
    std::sort (p.events.begin(), p.events.end(), [] (const NoteEvent& a, const NoteEvent& b) {
        return a.time < b.time || (juce::exactlyEqual (a.time, b.time) && ! a.on && b.on);
    });
    return p;
}

class FixedPlayHead final : public juce::AudioPlayHead
{
public:
    juce::int64 samplePos = 0;
    juce::Optional<PositionInfo> getPosition() const override
    {
        PositionInfo info;
        info.setBpm (kBpm);
        info.setTimeInSamples (samplePos);
        info.setTimeInSeconds ((double) samplePos / kSampleRate);
        info.setPpqPosition ((double) samplePos / kSampleRate * kBpm / 60.0);
        info.setIsPlaying (true);
        info.setTimeSignature (juce::AudioPlayHead::TimeSignature { 4, 4 });
        return info;
    }
};

// ITU-R BS.1770 K-weighting at 48 kHz (ungated integrated loudness over the analysed range).
struct Biquad
{
    double b0, b1, b2, a1, a2, z1 = 0.0, z2 = 0.0;
    double process (double x)
    {
        const double y = b0 * x + z1;
        z1 = b1 * x - a1 * y + z2;
        z2 = b2 * x - a2 * y;
        return y;
    }
};

double loudness (const std::vector<float>& l, const std::vector<float>& r, size_t start, size_t end)
{
    double sum = 0.0;
    for (const auto* ch : { &l, &r })
    {
        Biquad shelf { 1.53512485958697, -2.69169618940638, 1.19839281085285, -1.69065929318241, 0.73248077421585 };
        Biquad hp { 1.0, -2.0, 1.0, -1.99004745483398, 0.99007225036621 };
        double acc = 0.0;
        for (size_t i = 0; i < end; ++i)
        {
            const double y = hp.process (shelf.process ((*ch)[i]));
            if (i >= start)
                acc += y * y;
        }
        sum += acc / (double) std::max<size_t> (1, end - start);
    }
    return -0.691 + 10.0 * std::log10 (sum + 1.0e-20);
}

double spectralCentroid (const std::vector<float>& l, const std::vector<float>& r, size_t start, size_t end)
{
    constexpr int order = 12, n = 1 << order;
    juce::dsp::FFT fft (order);
    std::vector<float> acc ((size_t) n / 2, 0.0f), buf ((size_t) n * 2);
    int frames = 0;
    for (size_t pos = start; pos + (size_t) n <= end; pos += (size_t) n / 2)
    {
        std::fill (buf.begin(), buf.end(), 0.0f);
        for (int i = 0; i < n; ++i)
        {
            const float w = 0.5f - 0.5f * std::cos (6.2831853f * (float) i / (float) (n - 1));
            buf[(size_t) i] = 0.5f * (l[pos + (size_t) i] + r[pos + (size_t) i]) * w;
        }
        fft.performFrequencyOnlyForwardTransform (buf.data());
        for (int i = 0; i < n / 2; ++i)
            acc[(size_t) i] += buf[(size_t) i];
        ++frames;
    }
    double num = 0.0, den = 0.0;
    for (int i = 1; i < n / 2; ++i)
    {
        const double f = (double) i * kSampleRate / n;
        num += f * acc[(size_t) i];
        den += acc[(size_t) i];
    }
    return den > 0.0 ? num / den : 0.0;
}

float toDb (double v) { return (float) juce::Decibels::gainToDecibels (v, -150.0); }


// Timbre fingerprint used to detect presets that sound alike (tools/presets/similarity.py).
struct Features
{
    std::vector<float> bands;   // 16 log-spaced band levels (dB, relative to their mean): spectral shape
    float brightness = 0;       // log2 of spectral centroid relative to 1 kHz
    float noisiness = 0;        // mean spectral flatness (0 tonal .. 1 noise)
    float movement = 0;         // std-dev of the per-frame centroid in octaves (how much the timbre moves)
    float attack = 0;           // seconds to reach 90 % of the loudest 23 ms frame
    float sustain = 0;          // level 1 s after the peak relative to the peak (0 .. 1)
    float width = 0;            // side / (mid + side) energy
    float low = 0;              // share of energy below 150 Hz
};

Features computeFeatures (const std::vector<float>& l, const std::vector<float>& r, size_t end)
{
    constexpr int order = 11, n = 1 << order, hop = n / 2;
    juce::dsp::FFT fft (order);
    std::vector<float> buf ((size_t) n * 2);
    Features f;
    f.bands.assign (16, 0.0f);
    std::vector<double> bandAcc (16, 0.0), frameEnergy, frameCentroid;
    double flatAcc = 0.0, lowE = 0.0, allE = 0.0, mid = 0.0, side = 0.0;
    int frames = 0;
    auto bandOf = [] (double hz) { return juce::jlimit (0, 15, (int) std::floor (std::log2 (std::max (hz, 40.0) / 40.0) * 16.0 / std::log2 (16000.0 / 40.0))); };
    for (size_t pos = 0; pos + (size_t) n <= end; pos += (size_t) hop)
    {
        std::fill (buf.begin(), buf.end(), 0.0f);
        double e = 0.0;
        for (int i = 0; i < n; ++i)
        {
            const float a = l[pos + (size_t) i], b = r[pos + (size_t) i];
            const float w = 0.5f - 0.5f * std::cos (6.2831853f * (float) i / (float) (n - 1));
            buf[(size_t) i] = 0.5f * (a + b) * w;
            e += 0.25 * (a + b) * (a + b);
            mid += 0.25 * (a + b) * (a + b);
            side += 0.25 * (a - b) * (a - b);
        }
        fft.performFrequencyOnlyForwardTransform (buf.data());
        double num = 0.0, den = 0.0, logSum = 0.0, linSum = 0.0;
        int cnt = 0;
        for (int k = 1; k < n / 2; ++k)
        {
            const double hz = (double) k * kSampleRate / n;
            const double m = (double) buf[(size_t) k] + 1.0e-9;
            const double p2 = m * m;
            bandAcc[(size_t) bandOf (hz)] += p2;
            if (hz < 150.0) lowE += p2;
            allE += p2;
            num += hz * m;
            den += m;
            logSum += std::log (m);
            linSum += m;
            ++cnt;
        }
        flatAcc += std::exp (logSum / cnt) / (linSum / cnt);
        frameEnergy.push_back (e / n);
        frameCentroid.push_back (den > 0.0 ? num / den : 1000.0);
        ++frames;
    }
    if (frames == 0)
        return f;
    double meanDb = 0.0;
    for (int b = 0; b < 16; ++b)
    {
        f.bands[(size_t) b] = (float) (10.0 * std::log10 (bandAcc[(size_t) b] / frames + 1.0e-12));
        meanDb += f.bands[(size_t) b] / 16.0;
    }
    for (auto& v : f.bands)
        v -= (float) meanDb;
    f.noisiness = (float) (flatAcc / frames);
    f.low = (float) (lowE / (allE + 1.0e-12));
    f.width = (float) (side / (mid + side + 1.0e-12));

    // Loudness-weighted centroid statistics (silent frames would dominate otherwise).
    double eSum = 0.0, cMean = 0.0;
    for (int i = 0; i < frames; ++i) { eSum += frameEnergy[(size_t) i]; cMean += frameEnergy[(size_t) i] * std::log2 (frameCentroid[(size_t) i] / 1000.0); }
    cMean /= (eSum + 1.0e-20);
    double cVar = 0.0;
    for (int i = 0; i < frames; ++i) { const double d = std::log2 (frameCentroid[(size_t) i] / 1000.0) - cMean; cVar += frameEnergy[(size_t) i] * d * d; }
    f.brightness = (float) cMean;
    f.movement = (float) std::sqrt (cVar / (eSum + 1.0e-20));

    // Envelope from short frames.
    const size_t win = (size_t) (0.023 * kSampleRate);
    std::vector<double> env;
    for (size_t pos = 0; pos + win <= end; pos += win)
    {
        double s = 0.0;
        for (size_t i = pos; i < pos + win; ++i)
            s += 0.5 * ((double) l[i] * l[i] + (double) r[i] * r[i]);
        env.push_back (std::sqrt (s / (double) win));
    }
    if (! env.empty())
    {
        const auto pk = std::max_element (env.begin(), env.end());
        size_t a = 0;
        while (a < env.size() && env[a] < 0.9 * *pk) ++a;
        f.attack = (float) ((double) a * (double) win / kSampleRate);
        const size_t later = (size_t) (pk - env.begin()) + (size_t) (1.0 / 0.023);
        f.sustain = (float) (later < env.size() ? env[later] / (*pk + 1.0e-12) : 0.0);
    }
    return f;
}

struct Result
{
    int index = 0;
    juce::String name, category, phrase, file;
    float peakDb = 0, rmsDb = 0, lufs = 0, centroid = 0, tailDb = 0, tailTime = 0, limiterDb = 0, dc = 0;
    Features features;
    int nonFinite = 0;
    juce::StringArray failures;
};

Result renderPreset (VoltAudioProcessor& proc, int index, const volt::PresetInfo& info, int block, const juce::File& previewDir)
{
    auto& pm = proc.getPresetManager();
    Result res;
    res.index = index;
    res.name = info.name;
    res.category = info.category;

    pm.applyPreset (info);
    FixedPlayHead playHead;
    proc.setPlayHead (&playHead);
    proc.prepareToPlay (kSampleRate, block);
    proc.getEngine().resetLimiterMeter();

    const auto phrase = phraseFor (info.category);
    res.phrase = phrase.name;
    const auto total = (size_t) ((phrase.end + kTailSeconds) * kSampleRate);
    std::vector<float> L (total, 0.0f), R (total, 0.0f);
    juce::AudioBuffer<float> buffer (2, block);
    juce::MidiBuffer midi;
    size_t ev = 0;

    for (size_t pos = 0; pos < total; pos += (size_t) block)
    {
        const int n = (int) std::min<size_t> ((size_t) block, total - pos);
        buffer.setSize (2, n, false, false, true);
        buffer.clear();
        midi.clear();
        while (ev < phrase.events.size() && (size_t) (phrase.events[ev].time * kSampleRate) < pos + (size_t) n)
        {
            const auto& e = phrase.events[ev];
            const int offset = (int) std::max<juce::int64> (0, (juce::int64) (e.time * kSampleRate) - (juce::int64) pos);
            midi.addEvent (e.on ? juce::MidiMessage::noteOn (1, e.note, e.vel) : juce::MidiMessage::noteOff (1, e.note), offset);
            ++ev;
        }
        playHead.samplePos = (juce::int64) pos;
        proc.processBlock (buffer, midi);
        std::copy (buffer.getReadPointer (0), buffer.getReadPointer (0) + n, L.begin() + (long) pos);
        std::copy (buffer.getReadPointer (1), buffer.getReadPointer (1) + n, R.begin() + (long) pos);
    }
    proc.setPlayHead (nullptr);

    // ---- analysis ----
    const size_t activeEnd = (size_t) (phrase.end * kSampleRate);
    double peak = 0.0, sumSq = 0.0, sumDc = 0.0;
    bool finite = true;
    for (size_t i = 0; i < total; ++i)
    {
        if (! std::isfinite (L[i]) || ! std::isfinite (R[i])) { finite = false; continue; }
        peak = std::max (peak, (double) std::max (std::abs (L[i]), std::abs (R[i])));
        if (i < activeEnd)
        {
            sumSq += 0.5 * ((double) L[i] * L[i] + (double) R[i] * R[i]);
            sumDc += 0.5 * ((double) L[i] + R[i]);
        }
    }
    res.peakDb = toDb (peak);
    res.rmsDb = toDb (std::sqrt (sumSq / (double) activeEnd));
    res.dc = (float) (sumDc / (double) activeEnd);
    res.lufs = (float) loudness (L, R, 0, activeEnd);
    res.centroid = (float) spectralCentroid (L, R, 0, activeEnd);
    res.features = computeFeatures (L, R, std::min (total, activeEnd + (size_t) (0.5 * kSampleRate)));
    res.limiterDb = proc.getEngine().getLimiterReduction();
    res.nonFinite = proc.getEngine().getNonFiniteCount() + (finite ? 0 : 1);

    const size_t win = (size_t) (0.05 * kSampleRate);
    res.tailTime = 0.0f;
    for (size_t pos = activeEnd; pos + win <= total; pos += win)
    {
        double s = 0.0;
        for (size_t i = pos; i < pos + win; ++i)
            s += 0.5 * ((double) L[i] * L[i] + (double) R[i] * R[i]);
        if (toDb (std::sqrt (s / (double) win)) > kTailEndDb)
            res.tailTime = (float) ((double) (pos + win - activeEnd) / kSampleRate);
    }
    {
        const size_t last = (size_t) (0.5 * kSampleRate);
        double s = 0.0;
        for (size_t i = total - last; i < total; ++i)
            s += 0.5 * ((double) L[i] * L[i] + (double) R[i] * R[i]);
        res.tailDb = toDb (std::sqrt (s / (double) last));
    }

    if (res.nonFinite > 0) res.failures.add ("NaN/Inf in output");
    if (res.peakDb < kSilenceDb) res.failures.add ("silent (peak " + juce::String (res.peakDb, 1) + " dBFS)");
    if (res.peakDb > kMaxPeakDb) res.failures.add ("clipping above 0 dBFS");
    if (std::abs (res.dc) > kMaxDc) res.failures.add ("DC offset " + juce::String (res.dc, 4));
    if (res.tailDb > kTailEndDb) res.failures.add ("tail does not decay (" + juce::String (res.tailDb, 1) + " dBFS after 8 s)");
    if (res.limiterDb > kMaxLimiterDb) res.failures.add ("limiter works too hard (" + juce::String (res.limiterDb, 1) + " dB)");
    if (res.lufs < kMinLoudness || res.lufs > kMaxLoudness)
        res.failures.add ("loudness " + juce::String (res.lufs, 1) + " LUFS outside [" + juce::String (kMinLoudness) + ", " + juce::String (kMaxLoudness) + "]");

    // ---- preview ----
    if (previewDir != juce::File())
    {
        const size_t len = std::min (total, (size_t) ((phrase.end + 1.6) * kSampleRate));
        const size_t fade = (size_t) (0.25 * kSampleRate);
        juce::AudioBuffer<float> out (2, (int) len);
        for (size_t i = 0; i < len; ++i)
        {
            const float g = i + fade > len ? (float) (len - i) / (float) fade : 1.0f;
            out.setSample (0, (int) i, L[i] * g);
            out.setSample (1, (int) i, R[i] * g);
        }
        res.file = juce::String (index).paddedLeft ('0', 3) + "_" + juce::File::createLegalFileName (info.name).replaceCharacter (' ', '_') + ".flac";
        auto file = previewDir.getChildFile (res.file);
        file.deleteFile();
        juce::FlacAudioFormat flac;
        std::unique_ptr<juce::OutputStream> stream = std::make_unique<juce::FileOutputStream> (file);
        if (static_cast<juce::FileOutputStream*> (stream.get())->openedOk())
        {
            auto writer = flac.createWriterFor (stream, juce::AudioFormatWriterOptions().withSampleRate (kSampleRate)
                                                                .withNumChannels (2).withBitsPerSample (16));
            if (writer != nullptr)
                writer->writeFromAudioSampleBuffer (out, 0, out.getNumSamples());
        }
    }
    return res;
}

int snapshot (const juce::File& out, float scale, int tab)
{
    VoltAudioProcessor proc;
    proc.setUiScale (scale);
    proc.prepareToPlay (48000.0, 512);
    std::unique_ptr<juce::AudioProcessorEditor> ed (proc.createEditor());
    if (auto* ve = dynamic_cast<VoltAudioProcessorEditor*> (ed.get()))
    {
        ve->getPanel().setTab (tab % 3);
        if (tab >= 3)
            ve->getPanel().showKeyboard (true); // tab 3: synth tab with the play keyboard shown
    }
    ed->setSize (juce::roundToInt (volt::ui::MainPanel::kWidth * scale), juce::roundToInt (volt::ui::MainPanel::kHeight * scale));
    auto img = ed->createComponentSnapshot (ed->getLocalBounds(), true, 1.0f);
    out.deleteFile();
    juce::FileOutputStream os (out);
    juce::PNGImageFormat png;
    return png.writeImageToStream (img, os) ? 0 : 1;
}

juce::String fmt (float v, int dp = 1) { return juce::String (v, dp); }
} // namespace

int main (int argc, char** argv)
{
    juce::ScopedJuceInitialiser_GUI gui;
    juce::StringArray args;
    for (int i = 1; i < argc; ++i)
        args.add (argv[i]);

    if (args[0] == "--snapshot")
        return snapshot (juce::File::getCurrentWorkingDirectory().getChildFile (args[1]), args.size() > 2 ? args[2].getFloatValue() : 1.0f,
                         args.size() > 3 ? args[3].getIntValue() : 0);

    juce::File outDir = juce::File::getCurrentWorkingDirectory().getChildFile ("render-out");
    juce::String filter;
    juce::File presetDir;
    bool previews = true;
    int block = 512;
    for (int i = 0; i < args.size(); ++i)
    {
        if (args[i] == "--out" && i + 1 < args.size()) outDir = juce::File::getCurrentWorkingDirectory().getChildFile (args[++i]);
        else if (args[i] == "--preset" && i + 1 < args.size()) filter = args[++i];
        else if (args[i] == "--no-previews") previews = false;
        else if (args[i] == "--dir" && i + 1 < args.size()) presetDir = juce::File::getCurrentWorkingDirectory().getChildFile (args[++i]);
        else if (args[i] == "--block" && i + 1 < args.size()) block = juce::jlimit (16, 4096, args[++i].getIntValue());
    }
    outDir.createDirectory();
    const auto previewDir = previews ? outDir.getChildFile ("previews") : juce::File();
    if (previews)
    {
        previewDir.deleteRecursively();
        previewDir.createDirectory();
    }

    VoltAudioProcessor proc;
    proc.enableAllBuses();
    proc.setPlayConfigDetails (0, 2, kSampleRate, block);
    auto& pm = proc.getPresetManager();
    const int count = pm.getNumFactoryPresets();

    // Presets to render: the embedded factory set, or every *.json in --dir (candidates under review).
    std::vector<volt::PresetInfo> list;
    if (presetDir != juce::File())
    {
        auto files = presetDir.findChildFiles (juce::File::findFiles, false, "*.json");
        files.sort();
        for (const auto& f : files)
        {
            volt::PresetInfo info;
            juce::StringArray errors;
            volt::PresetManager::parsePreset (f.loadFileAsString(), info, errors);
            for (const auto& e : errors)
                if (! e.contains ("invalid category"))
                    std::printf ("warning: %s: %s\n", f.getFileName().toRawUTF8(), e.toRawUTF8());
            list.push_back (std::move (info));
        }
    }
    else
    {
        for (int i = 0; i < count; ++i)
            list.push_back (pm.getPresets()[(size_t) i]);
    }

    std::vector<Result> results;
    for (int i = 0; i < (int) list.size(); ++i)
    {
        if (filter.isNotEmpty() && ! list[(size_t) i].name.containsIgnoreCase (filter))
            continue;
        results.push_back (renderPreset (proc, i, list[(size_t) i], block, previewDir));
        const auto& r = results.back();
        std::printf ("%3d %-28s %-6s peak %6.1f  rms %6.1f  lufs %6.1f  cent %6.0f  tail %4.1fs  lim %4.1f  %s\n", i,
                     r.name.toRawUTF8(), r.category.toRawUTF8(), r.peakDb, r.rmsDb, r.lufs, r.centroid, r.tailTime,
                     r.limiterDb, r.failures.isEmpty() ? "ok" : r.failures.joinIntoString ("; ").toRawUTF8());
    }

    // Level consistency across all rendered presets.
    std::vector<float> l;
    for (const auto& r : results)
        l.push_back (r.lufs);
    float median = 0.0f;
    if (! l.empty())
    {
        std::sort (l.begin(), l.end());
        median = l[l.size() / 2];
        if (filter.isEmpty())
            for (auto& r : results)
                if (std::abs (r.lufs - median) > kLoudnessWindow)
                    r.failures.add ("loudness " + fmt (r.lufs) + " LUFS deviates more than " + fmt (kLoudnessWindow, 0) + " LU from median " + fmt (median));
    }

    int failed = 0;
    juce::Array<juce::var> arr;
    juce::String md;
    md << "# VOLT preset render report\n\n"
       << "48 kHz, 120 BPM, block " << block << ", tail " << kTailSeconds << " s after the last note-off.\n\n"
       << "Checks: peak <= 0 dBFS, not silent (peak > " << kSilenceDb << " dBFS), no NaN/Inf, |DC| <= " << kMaxDc
       << ", RMS of the last 0.5 s of the tail < " << kTailEndDb << " dBFS, limiter reduction <= " << kMaxLimiterDb
       << " dB, loudness in [" << kMinLoudness << ", " << kMaxLoudness << "] LUFS and within +-" << kLoudnessWindow
       << " LU of the median (" << fmt (median) << " LUFS).\n\n"
       << "| # | Preset | Category | Phrase | Peak dBFS | RMS dBFS | LUFS | Centroid Hz | Tail s | Limiter dB | DC | Result |\n"
       << "|---|---|---|---|---|---|---|---|---|---|---|---|\n";
    for (const auto& r : results)
    {
        const bool ok = r.failures.isEmpty();
        failed += ok ? 0 : 1;
        md << "| " << r.index << " | " << r.name << " | " << r.category << " | " << r.phrase << " | " << fmt (r.peakDb)
           << " | " << fmt (r.rmsDb) << " | " << fmt (r.lufs) << " | " << juce::String (juce::roundToInt (r.centroid))
           << " | " << fmt (r.tailTime) << " | " << fmt (r.limiterDb) << " | " << juce::String (r.dc, 4) << " | "
           << (ok ? juce::String ("ok") : "FAIL: " + r.failures.joinIntoString ("; ")) << " |\n";

        auto* o = new juce::DynamicObject();
        o->setProperty ("index", r.index);
        o->setProperty ("name", r.name);
        o->setProperty ("category", r.category);
        o->setProperty ("phrase", r.phrase);
        o->setProperty ("peak_dbfs", r.peakDb);
        o->setProperty ("rms_dbfs", r.rmsDb);
        o->setProperty ("loudness_lufs", r.lufs);
        o->setProperty ("spectral_centroid_hz", r.centroid);
        {
            auto* fo = new juce::DynamicObject();
            juce::Array<juce::var> bands;
            for (float b : r.features.bands)
                bands.add (juce::roundToInt (b * 10.0f) / 10.0);
            fo->setProperty ("bands_db", bands);
            fo->setProperty ("brightness_oct", r.features.brightness);
            fo->setProperty ("noisiness", r.features.noisiness);
            fo->setProperty ("movement_oct", r.features.movement);
            fo->setProperty ("attack_s", r.features.attack);
            fo->setProperty ("sustain", r.features.sustain);
            fo->setProperty ("width", r.features.width);
            fo->setProperty ("low_share", r.features.low);
            o->setProperty ("features", juce::var (fo));
        }
        o->setProperty ("tail_seconds", r.tailTime);
        o->setProperty ("tail_end_dbfs", r.tailDb);
        o->setProperty ("limiter_reduction_db", r.limiterDb);
        o->setProperty ("dc_offset", r.dc);
        o->setProperty ("non_finite_samples", r.nonFinite);
        o->setProperty ("preview", r.file);
        juce::Array<juce::var> f;
        for (const auto& s : r.failures)
            f.add (s);
        o->setProperty ("failures", f);
        o->setProperty ("passed", ok);
        arr.add (juce::var (o));
    }
    md << "\n**" << (int) results.size() - failed << " / " << (int) results.size() << " presets passed.**\n";

    auto* root = new juce::DynamicObject();
    root->setProperty ("sample_rate", kSampleRate);
    root->setProperty ("bpm", kBpm);
    root->setProperty ("median_lufs", median);
    root->setProperty ("presets", arr);
    root->setProperty ("passed", (int) results.size() - failed);
    root->setProperty ("failed", failed);
    outDir.getChildFile ("report.json").replaceWithText (juce::JSON::toString (juce::var (root)));
    outDir.getChildFile ("report.md").replaceWithText (md);

    std::printf ("\n%d / %d presets passed (median loudness %.1f LUFS). Report: %s\n", (int) results.size() - failed,
                 (int) results.size(), median, outDir.getChildFile ("report.md").getFullPathName().toRawUTF8());
    return failed == 0 && ! results.empty() ? 0 : 1;
}
