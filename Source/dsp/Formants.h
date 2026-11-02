#pragma once

#include <array>
#include <cmath>

namespace volt
{
// Reference vowel formants (bass voice, textbook phonetics values): frequency [Hz], gain [dB], bandwidth [Hz].
struct Vowel
{
    std::array<float, 5> freq, gainDb, bw;
};

inline const std::array<Vowel, 5>& vowelTable() noexcept
{
    static const std::array<Vowel, 5> v { {
        { { 600.f, 1040.f, 2250.f, 2450.f, 2750.f }, { 0.f, -7.f, -9.f, -9.f, -20.f }, { 60.f, 70.f, 110.f, 120.f, 130.f } },     // A
        { { 400.f, 1620.f, 2400.f, 2800.f, 3100.f }, { 0.f, -12.f, -9.f, -12.f, -18.f }, { 40.f, 80.f, 100.f, 120.f, 120.f } },   // E
        { { 250.f, 1750.f, 2600.f, 3050.f, 3340.f }, { 0.f, -30.f, -16.f, -22.f, -28.f }, { 60.f, 90.f, 100.f, 120.f, 120.f } },  // I
        { { 400.f, 750.f, 2400.f, 2600.f, 2900.f }, { 0.f, -11.f, -21.f, -20.f, -40.f }, { 40.f, 80.f, 100.f, 120.f, 120.f } },   // O
        { { 350.f, 600.f, 2400.f, 2675.f, 2950.f }, { 0.f, -20.f, -32.f, -28.f, -36.f }, { 40.f, 80.f, 100.f, 120.f, 120.f } },   // U
    } };
    return v;
}

// Interpolated vowel for morph position 0..1 across A-E-I-O-U.
inline Vowel vowelAt (float morph) noexcept
{
    const auto& t = vowelTable();
    const float p = std::fmin (std::fmax (morph, 0.0f), 1.0f) * 4.0f;
    const int i0 = (int) p;
    const int i1 = i0 < 4 ? i0 + 1 : 4;
    const float f = p - (float) i0;
    Vowel out;
    for (size_t k = 0; k < 5; ++k)
    {
        out.freq[k] = t[(size_t) i0].freq[k] + f * (t[(size_t) i1].freq[k] - t[(size_t) i0].freq[k]);
        out.gainDb[k] = t[(size_t) i0].gainDb[k] + f * (t[(size_t) i1].gainDb[k] - t[(size_t) i0].gainDb[k]);
        out.bw[k] = t[(size_t) i0].bw[k] + f * (t[(size_t) i1].bw[k] - t[(size_t) i0].bw[k]);
    }
    return out;
}
} // namespace volt
