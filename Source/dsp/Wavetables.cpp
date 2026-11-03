// Procedural wavetable generation. Every table below is computed from simple maths (additive spectra,
// waveshaping, phase modulation, sync, quantisation) – no audio data is loaded from anywhere.
#include "Wavetables.h"
#include "Formants.h"

#include <complex>
#include <functional>

namespace volt
{
namespace
{
using cd = std::complex<double>;
constexpr double kPi = 3.14159265358979323846;
constexpr double kTwoPi = 2.0 * kPi;
constexpr int kTimeN = 4096; // time-domain generation resolution

using Spectrum = std::vector<cd>; // index = harmonic number, [0] unused

void fft (std::vector<cd>& a, bool inverse)
{
    const size_t n = a.size();
    for (size_t i = 1, j = 0; i < n; ++i)
    {
        size_t bit = n >> 1;
        for (; (j & bit) != 0; bit >>= 1)
            j ^= bit;
        j ^= bit;
        if (i < j)
            std::swap (a[i], a[j]);
    }
    for (size_t len = 2; len <= n; len <<= 1)
    {
        const double ang = kTwoPi / (double) len * (inverse ? 1.0 : -1.0);
        const cd wl (std::cos (ang), std::sin (ang));
        for (size_t i = 0; i < n; i += len)
        {
            cd w (1.0, 0.0);
            for (size_t k = 0; k < len / 2; ++k)
            {
                const cd u = a[i + k];
                const cd v = a[i + k + len / 2] * w;
                a[i + k] = u + v;
                a[i + k + len / 2] = u - v;
                w *= wl;
            }
        }
    }
}

double frac (double x) { return x - std::floor (x); }
double sine (double x) { return std::sin (kTwoPi * x); }
double saw (double x) { return 2.0 * frac (x + 0.5) - 1.0; }
double square (double x) { return frac (x) < 0.5 ? 1.0 : -1.0; }
double pulse (double x, double w) { return frac (x) < w ? 1.0 : -1.0; }
double tri (double x)
{
    const double p = frac (x);
    if (p < 0.25) return 4.0 * p;
    if (p < 0.75) return 2.0 - 4.0 * p;
    return 4.0 * p - 4.0;
}
double lerp (double a, double b, double f) { return a + (b - a) * f; }

// Deterministic per-table pseudo random numbers (no global state).
struct Lcg
{
    uint32_t s;
    explicit Lcg (uint32_t seed) : s (seed) {}
    double next() { s = s * 1664525u + 1013904223u; return (double) (s >> 8) / (double) (1u << 24); }
};

void addSine (Spectrum& c, int h, double amp, double phase = 0.0)
{
    if (h >= 1 && h <= kWtMaxHarmonics)
        c[(size_t) h] += amp * std::polar (1.0, phase - kPi * 0.5);
}

// Distribute a (possibly fractional) partial between its two neighbouring harmonics.
void addPartial (Spectrum& c, double h, double amp)
{
    const int h0 = (int) std::floor (h);
    const double f = h - h0;
    addSine (c, h0, amp * (1.0 - f));
    addSine (c, h0 + 1, amp * f);
}

double formantGain (const Vowel& v, double freqHz, double bwScale, int numFormants = 5)
{
    double g = 0.0;
    for (int k = 0; k < numFormants; ++k)
    {
        const double a = std::pow (10.0, v.gainDb[(size_t) k] / 20.0);
        const double d = (freqHz - v.freq[(size_t) k]) / (v.bw[(size_t) k] * bwScale);
        g += a / (1.0 + d * d);
    }
    return g + 0.01;
}

struct TableDef
{
    const char* name;
    std::function<void (double t, Spectrum&)> spectral; // either spectral ...
    std::function<double (double x, double t)> time;     // ... or time domain
};

std::vector<TableDef> definitions()
{
    std::vector<TableDef> d;

    // ---------------- classic analog ----------------
    d.push_back ({ "Basic Shapes", {}, [] (double x, double t) {
        const double u = t * 3.0;
        const int k = juce::jmin (2, (int) u);
        const double f = u - k;
        const double s[4] = { sine (x), tri (x), saw (x), square (x) };
        return lerp (s[k], s[k + 1], f);
    } });

    d.push_back ({ "Analog Saw", [] (double t, Spectrum& c) {
        const double hc = 600.0 * std::pow (1.0 - t, 3.0) + 3.0;
        Lcg r (11);
        for (int h = 1; h <= kWtMaxHarmonics; ++h)
        {
            const double roll = 1.0 / std::sqrt (1.0 + std::pow (h / hc, 2.0));
            addSine (c, h, roll / h, ((h % 2 == 0) ? kPi : 0.0) + t * 0.6 * (r.next() - 0.5));
        }
    }, {} });

    d.push_back ({ "Analog Square", [] (double t, Spectrum& c) {
        const double hc = 500.0 * std::pow (1.0 - t, 3.0) + 3.0;
        for (int h = 1; h <= kWtMaxHarmonics; ++h)
        {
            const double roll = 1.0 / std::sqrt (1.0 + std::pow (h / hc, 2.0));
            const double a = (h % 2 == 1) ? 1.0 / h : 0.04 / h; // slight asymmetry like a real circuit
            addSine (c, h, a * roll);
        }
    }, {} });

    d.push_back ({ "Hollow", [] (double t, Spectrum& c) {
        const double p = lerp (2.0, 0.75, t);
        for (int h = 1; h <= kWtMaxHarmonics; h += 2)
            addSine (c, h, 1.0 / std::pow ((double) h, p));
    }, {} });

    // ---------------- supersaw family ----------------
    d.push_back ({ "Hyper Saw", {}, [] (double x, double t) {
        static const double offs[5] = { 0.0, 0.137, 0.291, 0.413, 0.677 };
        double s = 0.0;
        for (double o : offs)
            s += saw (x + t * o);
        return s / 5.0;
    } });

    d.push_back ({ "Saw Octaves", {}, [] (double x, double t) {
        return saw (x) + 0.75 * t * saw (2.0 * x + 0.1) + 0.5 * t * t * saw (4.0 * x + 0.3);
    } });

    // ---------------- PWM ----------------
    d.push_back ({ "PWM", {}, [] (double x, double t) { return pulse (x, lerp (0.5, 0.03, t)); } });

    d.push_back ({ "PWM Saw", {}, [] (double x, double t) {
        return 0.6 * saw (x) + 0.6 * pulse (x + 0.25, lerp (0.5, 0.08, t));
    } });

    d.push_back ({ "Sync Saw", {}, [] (double x, double t) { return 2.0 * frac (x * (1.0 + 5.0 * t)) - 1.0; } });

    d.push_back ({ "Sync Square", {}, [] (double x, double t) { return frac (x * (1.0 + 4.0 * t)) < 0.5 ? 1.0 : -1.0; } });

    // ---------------- organs ----------------
    // Drawbar footages 16', 5 1/3', 8', 4', 2 2/3', 2', 1 3/5', 1 1/3', 1'  ->  harmonic numbers relative to 16'.
    static const int drawbarHarm[9] = { 1, 3, 2, 4, 6, 8, 10, 12, 16 };
    static const int registrations[5][9] = { { 8, 0, 8, 0, 0, 0, 0, 0, 0 },
                                             { 8, 8, 8, 0, 0, 0, 0, 0, 0 },
                                             { 8, 6, 8, 8, 0, 0, 0, 0, 4 },
                                             { 8, 8, 8, 8, 6, 4, 0, 0, 6 },
                                             { 8, 8, 8, 8, 8, 8, 8, 8, 8 } };
    auto drawbars = [] (double t, Spectrum& c, double leak) {
        const double u = t * 4.0;
        const int k = juce::jmin (3, (int) u);
        const double f = u - k;
        for (int b = 0; b < 9; ++b)
        {
            const double lv = lerp (registrations[k][b], registrations[k + 1][b], f);
            if (lv > 0.0)
                addSine (c, drawbarHarm[b], std::pow (10.0, (lv - 8.0) * 3.0 / 20.0) * (lv / 8.0));
        }
        for (int h = 5; h <= 24; h += 2) // tonewheel leakage
            addSine (c, h, leak / h);
    };
    d.push_back ({ "Drawbars", [drawbars] (double t, Spectrum& c) { drawbars (t, c, 0.004); }, {} });

    d.push_back ({ "Drive Organ", {}, [] (double x, double t) {
        // Additive drawbar cycle evaluated directly, then overdriven.
        double s = 0.0;
        const double u = 0.75 + 0.25 * t;
        const int k = juce::jmin (3, (int) (u * 4.0));
        const double f = u * 4.0 - k;
        for (int b = 0; b < 9; ++b)
        {
            const double lv = lerp (registrations[k][b], registrations[k + 1][b], f);
            if (lv > 0.0)
                s += std::pow (10.0, (lv - 8.0) * 3.0 / 20.0) * (lv / 8.0) * sine (drawbarHarm[b] * x);
        }
        const double g = 0.4 + 4.0 * t * t;
        return std::tanh (g * s) / std::tanh (g);
    } });

    d.push_back ({ "Pipe Organ", [] (double t, Spectrum& c) {
        const int maxH = 6 + (int) (26.0 * t);
        for (int h = 1; h <= maxH; ++h)
        {
            const double odd = (h % 2 == 1) ? 1.0 : (1.0 - 0.75 * t);
            addSine (c, h, odd / std::pow ((double) h, 1.4 - 0.5 * t));
        }
    }, {} });

    // ---------------- vocal / formant ----------------
    d.push_back ({ "Vowels", [] (double t, Spectrum& c) {
        const auto v = vowelAt ((float) t);
        for (int h = 1; h <= kWtMaxHarmonics; ++h)
            addSine (c, h, formantGain (v, 130.0 * h, 1.3) / h, (h % 2 == 0) ? kPi : 0.0);
    }, {} });

    d.push_back ({ "Choir", [] (double t, Spectrum& c) {
        const auto v = vowelAt ((float) (0.95 - 0.95 * t)); // U -> A
        for (int h = 1; h <= kWtMaxHarmonics; ++h)
            addSine (c, h, formantGain (v, 220.0 * h, 2.2, 3) / std::pow ((double) h, 1.25));
    }, {} });

    d.push_back ({ "Talk Box", [] (double t, Spectrum& c) {
        // U -> O -> A -> E -> I with narrow, strong resonances on a reedy source.
        const float order[5] = { 1.0f, 0.75f, 0.0f, 0.25f, 0.5f };
        const double u = t * 4.0;
        const int k = juce::jmin (3, (int) u);
        const double f = u - k;
        const auto v = vowelAt ((float) lerp (order[k], order[k + 1], f));
        for (int h = 1; h <= kWtMaxHarmonics; ++h)
        {
            const double src = (h % 2 == 1 ? 1.0 : 0.6) / h;
            addSine (c, h, src * formantGain (v, 110.0 * h, 0.8) * 1.5);
        }
    }, {} });

    d.push_back ({ "Formant Sweep", [] (double t, Spectrum& c) {
        const double peak = 2.0 * std::pow (32.0, t);
        for (int h = 1; h <= kWtMaxHarmonics; ++h)
        {
            const double dd = (h - peak) / (0.18 * peak + 0.8);
            addSine (c, h, (0.15 + 3.0 / (1.0 + dd * dd)) / h, (h % 2 == 0) ? kPi : 0.0);
        }
    }, {} });

    // ---------------- metallic ----------------
    d.push_back ({ "Bell Metal", [] (double t, Spectrum& c) {
        static const double base[9] = { 1.0, 2.76, 5.40, 8.93, 13.34, 18.64, 24.8, 31.9, 40.1 };
        addSine (c, 1, 1.0);
        for (int k = 1; k < 9; ++k)
            addPartial (c, base[k] * (1.0 + 0.45 * t), 0.8 / std::sqrt ((double) k + 1.0));
    }, {} });

    d.push_back ({ "Metal Comb", [] (double t, Spectrum& c) {
        const double spacing = 0.04 + 0.21 * t;
        for (int h = 1; h <= kWtMaxHarmonics; ++h)
        {
            const double comb = 0.5 + 0.5 * std::cos (kTwoPi * h * spacing);
            addSine (c, h, comb * comb / std::pow ((double) h, 0.75));
        }
    }, {} });

    d.push_back ({ "Ring Mod", [] (double t, Spectrum& c) {
        const double k = 2.0 + 14.0 * t;
        addSine (c, 1, 0.35);
        addPartial (c, k - 1.0, 0.5);
        addPartial (c, k + 1.0, 0.5);
        addPartial (c, 2.0 * k + 1.0, 0.15);
    }, {} });

    // ---------------- FM ----------------
    d.push_back ({ "FM Bass", {}, [] (double x, double t) { return std::sin (kTwoPi * x + 5.0 * t * sine (x)); } });
    d.push_back ({ "FM Bell", {}, [] (double x, double t) {
        return std::sin (kTwoPi * x + 2.2 * t * sine (3.0 * x) + 1.1 * t * sine (7.0 * x));
    } });
    d.push_back ({ "FM Brass", {}, [] (double x, double t) {
        const double i = 0.4 + 2.6 * t;
        return std::sin (kTwoPi * x + i * std::sin (kTwoPi * x + 0.5 * i * sine (x)));
    } });
    d.push_back ({ "FM Digital", {}, [] (double x, double t) { return std::sin (kTwoPi * x + 4.0 * t * sine (5.0 * x)); } });

    // ---------------- grit ----------------
    d.push_back ({ "Fold", {}, [] (double x, double t) {
        const double g = 1.0 + 7.0 * t;
        return std::sin (g * kPi * 0.5 * sine (x));
    } });

    d.push_back ({ "Crush", {}, [] (double x, double t) {
        const double steps = 2.0 + 62.0 * std::pow (1.0 - t, 2.0);
        const double sh = 4.0 + 60.0 * (1.0 - t);
        const double xq = std::floor (x * sh) / sh;
        return std::round (saw (xq) * steps) / steps;
    } });

    d.push_back ({ "Buzz", {}, [] (double x, double t) {
        const double g = 1.0 + 20.0 * t;
        return std::tanh (g * (saw (x) + 0.5 * square (x))) / std::tanh (g * 1.5);
    } });

    d.push_back ({ "Rasp", [] (double t, Spectrum& c) {
        Lcg r (77);
        for (int h = 1; h <= kWtMaxHarmonics; ++h)
        {
            const double jitter = 1.0 + t * 0.95 * (2.0 * r.next() - 1.0);
            const double ph = t * kTwoPi * r.next();
            addSine (c, h, jitter / std::pow ((double) h, 1.0 - 0.35 * t), ph);
        }
    }, {} });

    d.push_back ({ "Acid", [] (double t, Spectrum& c) {
        const double hc = 1.5 * std::pow (40.0, t);
        const double q = 7.0;
        for (int h = 1; h <= kWtMaxHarmonics; ++h)
        {
            const double r = h / hc;
            const double mag = 1.0 / std::sqrt (std::pow (1.0 - r * r, 2.0) + std::pow (r / q, 2.0));
            addSine (c, h, juce::jmin (mag, q) / (1.0 + std::pow (r, 3.0)) / h, (h % 2 == 0) ? kPi : 0.0);
        }
    }, {} });

    // ---------------- ensemble / orchestral flavours ----------------
    d.push_back ({ "Brass", [] (double t, Spectrum& c) {
        const double hb = 4.0 + 10.0 * t;
        const double hc = 6.0 + 60.0 * t * t;
        for (int h = 1; h <= kWtMaxHarmonics; ++h)
        {
            const double bump = 1.0 + 2.0 * std::exp (-std::pow ((h - hb) / 4.0, 2.0));
            const double roll = 1.0 / (1.0 + std::pow (h / hc, 2.0));
            addSine (c, h, bump * roll / h, (h % 2 == 0) ? kPi : 0.0);
        }
    }, {} });

    d.push_back ({ "Strings", [] (double t, Spectrum& c) {
        Lcg r (5);
        const double hc = 8.0 + 120.0 * t;
        for (int h = 1; h <= kWtMaxHarmonics; ++h)
        {
            const double body = 1.0 + 0.6 * std::sin (h * 0.9) + 0.4 * std::sin (h * 2.3 + 1.0);
            const double roll = 1.0 / std::sqrt (1.0 + std::pow (h / hc, 2.0));
            addSine (c, h, body * roll / h, kTwoPi * r.next());
        }
    }, {} });

    d.push_back ({ "Sine Drive", {}, [] (double x, double t) {
        const double g = 1.0 + 11.0 * t * t;
        return std::tanh (g * sine (x)) / std::tanh (g);
    } });

    // ---------------- second set: distinct acoustic-ish and textural sources ----------------
    d.push_back ({ "Pluck Body", [] (double t, Spectrum& c) {
        // Ideal plucked string: harmonic h is weighted by sin(pi * h * pickPosition) / h^2, pick moves along t.
        const double beta = 0.04 + 0.42 * t;
        for (int h = 1; h <= kWtMaxHarmonics; ++h)
            addSine (c, h, std::abs (std::sin (kPi * h * beta)) / std::pow ((double) h, 1.6));
    }, {} });

    d.push_back ({ "Hammer Piano", [] (double t, Spectrum& c) {
        // Hammer-struck string: soft roll-off, a resonance region around harmonics 4-9, brighter with t.
        const double hc = 3.0 + 40.0 * t * t;
        for (int h = 1; h <= kWtMaxHarmonics; ++h)
        {
            const double res = 1.0 + 0.8 * std::exp (-std::pow ((h - 6.0) / 3.0, 2.0));
            const double strike = std::abs (std::sin (kPi * h / 7.3)) * 0.6 + 0.4;
            addSine (c, h, res * strike / (h * (1.0 + std::pow (h / hc, 2.0))));
        }
    }, {} });

    d.push_back ({ "Reed", [] (double t, Spectrum& c) {
        // Clarinet (odd harmonics) morphing to a saxophone-like full spectrum with a formant bump.
        for (int h = 1; h <= kWtMaxHarmonics; ++h)
        {
            const double odd = (h % 2 == 1) ? 1.0 : t * 0.9;
            const double bump = 1.0 + 1.5 * std::exp (-std::pow ((h - 5.0 - 6.0 * t) / 3.0, 2.0));
            addSine (c, h, odd * bump / std::pow ((double) h, 1.3));
        }
    }, {} });

    d.push_back ({ "Glass Harmonics", [] (double t, Spectrum& c) {
        // Sparse square-number partials (1, 4, 9, 16, ...) fading in for a glassy, bell-like tone.
        addSine (c, 1, 1.0);
        for (int k = 2; k <= 12; ++k)
        {
            const int h = k * k;
            const double on = juce::jlimit (0.0, 1.0, t * 12.0 - (k - 2));
            addSine (c, h, on * 0.7 / std::sqrt ((double) k));
        }
    }, {} });

    d.push_back ({ "Vocal Fry", [] (double t, Spectrum& c) {
        // Narrow glottal pulse train shaped by a moving open vowel: raspy, buzzy voice.
        const auto v = vowelAt ((float) (0.2 + 0.6 * t));
        for (int h = 1; h <= kWtMaxHarmonics; ++h)
            addSine (c, h, formantGain (v, 95.0 * h, 1.0) * 1.2 / std::pow ((double) h, 0.55), (h % 3) * 0.7);
    }, {} });

    d.push_back ({ "Even Saturate", {}, [] (double x, double t) {
        // Asymmetric (even-harmonic) saturation of a sine, like an overdriven valve stage.
        const double g = 0.5 + 6.0 * t;
        const double v = std::tanh (g * sine (x) + 0.6 * t) - std::tanh (0.6 * t);
        return v / std::tanh (g + 0.6 * t);
    } });

    d.push_back ({ "Noise Cycle", {}, [] (double x, double t) {
        // A fixed random cycle (smoothed noise) that gets rougher with t: textured, airy loops.
        static const std::vector<double> pts = [] {
            std::vector<double> v (64);
            Lcg r (2024);
            for (auto& p : v)
                p = 2.0 * r.next() - 1.0;
            return v;
        }();
        const int segs = 4 + (int) (60.0 * t);
        const double u = frac (x) * segs;
        const int k = (int) u;
        const double f = u - k;
        const double a = pts[(size_t) (k % 64)], b = pts[(size_t) ((k + 1) % segs % 64)];
        const double sm = f * f * (3.0 - 2.0 * f);
        return lerp (a, b, sm) * 0.8 + 0.2 * sine (x);
    } });

    d.push_back ({ "Dual Formant", [] (double t, Spectrum& c) {
        // Two resonant peaks moving in opposite directions over a saw source: wah / talk-like crossings.
        const double p1 = 2.0 + 18.0 * t, p2 = 24.0 - 18.0 * t;
        for (int h = 1; h <= kWtMaxHarmonics; ++h)
        {
            const double d1 = (h - p1) / (0.15 * p1 + 0.8), d2 = (h - p2) / (0.15 * p2 + 0.8);
            addSine (c, h, (0.1 + 2.0 / (1.0 + d1 * d1) + 2.0 / (1.0 + d2 * d2)) / h, (h % 2 == 0) ? kPi : 0.0);
        }
    }, {} });

    return d;
}

Wavetable buildTable (const TableDef& def)
{
    Wavetable wt;
    wt.name = def.name;

    size_t total = 0;
    for (int m = 0; m < kWtMips; ++m)
    {
        const int size = juce::jmax (256, 2048 >> m);
        wt.sizes[(size_t) m] = size;
        wt.offsets[(size_t) m] = total;
        total += (size_t) kWtFrames * (size_t) (size + 1);
    }
    wt.data.assign (total, 0.0f);

    std::vector<cd> timeBuf ((size_t) kTimeN);
    for (int f = 0; f < kWtFrames; ++f)
    {
        const double t = (double) f / (double) (kWtFrames - 1);
        Spectrum c ((size_t) kWtMaxHarmonics + 1, cd (0.0, 0.0));

        if (def.spectral)
        {
            def.spectral (t, c);
        }
        else
        {
            for (int n = 0; n < kTimeN; ++n)
                timeBuf[(size_t) n] = cd (def.time ((double) n / kTimeN, t), 0.0);
            fft (timeBuf, false);
            for (int h = 1; h <= kWtMaxHarmonics; ++h)
                c[(size_t) h] = timeBuf[(size_t) h] * (2.0 / kTimeN);
        }

        float norm = 1.0f;
        for (int m = 0; m < kWtMips; ++m)
        {
            const int size = wt.sizes[(size_t) m];
            const int limit = Wavetable::harmonicLimit (m);
            std::vector<cd> y ((size_t) size, cd (0.0, 0.0));
            for (int h = 1; h <= limit && h < size / 2; ++h)
            {
                y[(size_t) h] = c[(size_t) h] * 0.5;
                y[(size_t) (size - h)] = std::conj (c[(size_t) h]) * 0.5;
            }
            fft (y, true);

            float* out = wt.data.data() + wt.offsets[(size_t) m] + (size_t) f * (size_t) (size + 1);
            for (int n = 0; n < size; ++n)
                out[n] = (float) y[(size_t) n].real();

            if (m == 0)
            {
                float peak = 0.0f;
                for (int n = 0; n < size; ++n)
                    peak = juce::jmax (peak, std::abs (out[n]));
                norm = peak > 1.0e-9f ? 1.0f / peak : 0.0f;
            }
            for (int n = 0; n < size; ++n)
                out[n] *= norm;
            out[size] = out[0];
        }
    }
    return wt;
}
} // namespace

WavetableBank::WavetableBank()
{
    for (const auto& def : definitions())
        tables.push_back (buildTable (def));
}

const WavetableBank& WavetableBank::get()
{
    static const WavetableBank bank;
    return bank;
}

const juce::StringArray& wavetableNames()
{
    static const juce::StringArray names = [] {
        juce::StringArray n;
        for (const auto& d : definitions())
            n.add (d.name);
        return n;
    }();
    return names;
}

int wavetableIndex (const juce::String& name)
{
    return juce::jmax (0, wavetableNames().indexOf (name));
}
} // namespace volt
