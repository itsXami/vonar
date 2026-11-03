#include "Voice.h"

namespace volt
{
namespace
{
constexpr float kVoiceGain = 0.3f;

inline float frac01 (float x) noexcept { return x - std::floor (x); }
}

void Voice::prepare (double sampleRate, uint32_t seed)
{
    sr = sampleRate;
    rng = XorShift (seed);
    randomRng = XorShift (seed * 2654435761u + 17u);
    amp.setSampleRate (sr);
    fenv.setSampleRate (sr);
    menv.setSampleRate (sr);
    filter.prepare (sr);
    lfo[0].reset (0.0, seed * 3u + 1u);
    lfo[1].reset (0.0, seed * 7u + 5u);
    maxStringLen = (int) (sr / 16.0) + 8;
    for (auto& o : osc)
        for (auto& s : o.strings)
            s.prepare (maxStringLen);
    reset();
}

void Voice::reset()
{
    amp.reset();
    fenv.reset();
    menv.reset();
    filter.reset();
    penv = 0.0f;
    gate = false;
    note = -1;
    for (auto& o : osc)
        o.init = false;
    subPhase = 0.0f;
    levelsInit = false;
    polyPressure = 0.0f;
    pendingExcite = false;
}

void Voice::start (int newNote, float vel, float startPitch, bool retrigger, const VoiceContext& ctx)
{
    const bool wasIdle = ! amp.isActive();
    note = newNote;
    velocity = vel;
    targetPitch = (float) newNote;
    currentPitch = startPitch;
    gate = true;
    polyPressure = 0.0f;

    if (wasIdle)
    {
        filter.reset();
        for (auto& o : osc)
            o.init = false;
        subPhase = 0.0f;
        levelsInit = false;
    }

    if (retrigger || wasIdle)
    {
        amp.noteOn();
        fenv.noteOn();
        menv.noteOn();
        penv = 1.0f;
        randomValue = randomRng.nextBipolar();
        pendingExcite = true;
        for (int l = 0; l < 2; ++l)
            if (ctx.lfoRetrig[l])
                lfo[l].reset (0.0, rng.nextU());
    }
}

void Voice::release() noexcept
{
    gate = false;
    amp.noteOff();
    fenv.noteOff();
    menv.noteOff();
}

void Voice::computeOsc (int o, const VoiceContext& ctx, float pitch, float level, float pan, float detune,
                        std::array<float, kMaxUnison>& newInc, std::array<float, kMaxUnison>& newGl,
                        std::array<float, kMaxUnison>& newGr, int& voicesOut) noexcept
{
    const auto& raw = *ctx.raw;
    const int base = OscA_Table + o * kOscParamCount;
    const int n = juce::jlimit (1, kMaxUnison, raw.i (base + 7));
    const float detuneSemis = detune * detune;
    const float spread = ctx.smooth[UniSpread];
    const float norm = level / std::sqrt ((float) n);

    for (int u = 0; u < n; ++u)
    {
        const float p = n > 1 ? (2.0f * (float) u / (float) (n - 1) - 1.0f) : 0.0f;
        const float f = pitchToHz (pitch + p * detuneSemis);
        newInc[(size_t) u] = std::min (f / (float) sr, 0.45f);
        float l, r;
        panGains (pan + spread * p, l, r);
        newGl[(size_t) u] = l * norm;
        newGr[(size_t) u] = r * norm;
    }
    voicesOut = n;
}

void Voice::renderWavetable (int o, const VoiceContext& ctx, int n, float pos, float warpAmt,
                             const std::array<float, kMaxUnison>& ni, const std::array<float, kMaxUnison>& ngl,
                             const std::array<float, kMaxUnison>& ngr) noexcept
{
    OscState& st = osc[o];
    const int nv = st.voices;
    const auto& raw = *ctx.raw;
    const int mode = raw.i (OscA_Table + o * kOscParamCount + 9);
    const float inv = 1.0f / (float) n;

    float maxInc = 0.0f;
    for (int u = 0; u < nv; ++u)
        maxInc = std::max (maxInc, std::max (st.inc[(size_t) u], ni[(size_t) u]));
    float ratio = 1.0f;
    const float wMax = std::max (st.warp, warpAmt);
    if (mode == choices::WarpSync) ratio = 1.0f + 7.0f * wMax;
    else if (mode == choices::WarpMirror) ratio = 2.0f;
    else if (mode == choices::WarpFM) ratio = 1.0f + 4.0f * wMax;

    const Wavetable& wt = *ctx.table[o];
    const int mip = Wavetable::mipForIncrement (maxInc * ratio);
    const float fromPos = st.pos * (float) (kWtFrames - 1);
    const float dPos = (pos - st.pos) * (float) (kWtFrames - 1) * inv;
    const float dWarp = (warpAmt - st.warp) * inv;

    // Modulator for FM / RM: the other oscillator's first unison voice (its own table, frame and pitch).
    float modBuf[kChunk];
    if (mode == choices::WarpFM || mode == choices::WarpRM)
    {
        const int other = 1 - o;
        const Wavetable* owt = ctx.table[other];
        float ph = modPhase[other];
        for (int i = 0; i < n; ++i)
        {
            ph += modInc[other];
            ph -= std::floor (ph);
            modBuf[i] = owt != nullptr ? owt->read (modMip[other], modPos[other], ph) : 0.0f;
        }
    }

    switch (mode)
    {
        case choices::WarpSync:     wavetableLoop<choices::WarpSync> (wt, mip, n, nv, fromPos, dPos, dWarp, modBuf, ni, ngl, ngr, st); break;
        case choices::WarpBend:     wavetableLoop<choices::WarpBend> (wt, mip, n, nv, fromPos, dPos, dWarp, modBuf, ni, ngl, ngr, st); break;
        case choices::WarpSqueeze:  wavetableLoop<choices::WarpSqueeze> (wt, mip, n, nv, fromPos, dPos, dWarp, modBuf, ni, ngl, ngr, st); break;
        case choices::WarpMirror:   wavetableLoop<choices::WarpMirror> (wt, mip, n, nv, fromPos, dPos, dWarp, modBuf, ni, ngl, ngr, st); break;
        case choices::WarpQuantize: wavetableLoop<choices::WarpQuantize> (wt, mip, n, nv, fromPos, dPos, dWarp, modBuf, ni, ngl, ngr, st); break;
        case choices::WarpFM:       wavetableLoop<choices::WarpFM> (wt, mip, n, nv, fromPos, dPos, dWarp, modBuf, ni, ngl, ngr, st); break;
        case choices::WarpRM:       wavetableLoop<choices::WarpRM> (wt, mip, n, nv, fromPos, dPos, dWarp, modBuf, ni, ngl, ngr, st); break;
        default:                    wavetableLoop<choices::WarpOff> (wt, mip, n, nv, fromPos, dPos, dWarp, modBuf, ni, ngl, ngr, st); break;
    }
}

template <int Mode>
void Voice::wavetableLoop (const Wavetable& wt, int mip, int n, int nv, float fromPos, float dPos, float dWarp, const float* modBuf,
                           const std::array<float, kMaxUnison>& ni, const std::array<float, kMaxUnison>& ngl,
                           const std::array<float, kMaxUnison>& ngr, OscState& st) noexcept
{
    const float inv = 1.0f / (float) n;
    for (int u = 0; u < nv; ++u)
    {
        const size_t uu = (size_t) u;
        float ph = st.phase[uu];
        float inc = st.inc[uu];
        const float dInc = (ni[uu] - inc) * inv;
        float gl = st.gl[uu], gr = st.gr[uu];
        const float dgl = (ngl[uu] - gl) * inv, dgr = (ngr[uu] - gr) * inv;
        float fp = fromPos;
        float a = st.warp;
        for (int i = 0; i < n; ++i)
        {
            fp += dPos;
            inc += dInc;
            gl += dgl;
            gr += dgr;
            a += dWarp;
            float smp;
            if constexpr (Mode == choices::WarpSync)
                smp = wt.read (mip, fp, frac01 (ph * (1.0f + 7.0f * a)));
            else if constexpr (Mode == choices::WarpBend)
            {
                const float k = 1.0f + 7.0f * a;
                smp = wt.read (mip, fp, ph / (ph + (1.0f - ph) * k));
            }
            else if constexpr (Mode == choices::WarpSqueeze)
            {
                const float m = 0.5f * (1.0f - 0.94f * a);
                smp = wt.read (mip, fp, ph < m ? 0.5f * ph / m : 0.5f + 0.5f * (ph - m) / (1.0f - m));
            }
            else if constexpr (Mode == choices::WarpMirror)
            {
                const float s1 = wt.read (mip, fp, ph);
                const float p2 = std::min (ph < 0.5f ? 2.0f * ph : 2.0f - 2.0f * ph, 0.99999f);
                smp = s1 + (wt.read (mip, fp, p2) - s1) * a;
            }
            else if constexpr (Mode == choices::WarpQuantize)
            {
                const float q = 1.0f - a;
                const float steps = 2.0f + q * q * 254.0f;
                smp = wt.read (mip, fp, std::floor (ph * steps) / steps);
            }
            else if constexpr (Mode == choices::WarpFM)
                smp = wt.read (mip, fp, frac01 (ph + 1.5f * a * modBuf[i]));
            else if constexpr (Mode == choices::WarpRM)
                smp = wt.read (mip, fp, ph) * (1.0f - a + a * modBuf[i]);
            else
            {
                juce::ignoreUnused (a, modBuf);
                smp = wt.read (mip, fp, ph);
            }
            bufL[i] += smp * gl;
            bufR[i] += smp * gr;
            ph += inc;
            if (ph >= 1.0f)
                ph -= 1.0f;
        }
        st.phase[uu] = ph;
    }
}

void Voice::renderString (int o, const VoiceContext& ctx, int n, const std::array<float, kMaxUnison>& ni,
                          const std::array<float, kMaxUnison>& ngl, const std::array<float, kMaxUnison>& ngr) noexcept
{
    OscState& st = osc[o];
    const auto& raw = *ctx.raw;
    const float inv = 1.0f / (float) n;
    const float tone = clampf (ctx.smooth[StrTone], 0.0f, 1.0f);
    const float c = 0.04f + 0.96f * tone * std::sqrt (tone);        // loop damping (one-pole low-pass)
    const float groupDelay = (1.0f - c) / c;
    const float decay = std::max (raw[StrDecay], 0.02f);
    const Wavetable& wt = *ctx.table[o];
    const float framePos = st.pos * (float) (kWtFrames - 1);
    const int len = maxStringLen;

    for (int u = 0; u < st.voices; ++u)
    {
        const size_t uu = (size_t) u;
        PluckString& s = st.strings[uu];
        if (s.buf.empty())
            continue;

        if (pendingExcite)
        {
            // Pluck: add one period of the current wavetable frame (plus a little noise) behind the write head.
            const int period = juce::jlimit (2, len - 4, (int) std::lround (1.0f / std::max (ni[uu], 1.0e-5f)));
            const int mip = Wavetable::mipForIncrement (ni[uu]);
            for (int k = 0; k < period; ++k)
            {
                const float ph = (float) k / (float) period;
                const float e = 0.85f * wt.read (mip, framePos, ph) + 0.15f * rng.nextBipolar();
                const int idx = (s.write - period + k + len * 2) % len;
                s.buf[(size_t) idx] += e;
            }
            s.excited = true;
        }

        float inc = st.inc[uu];
        const float dInc = (ni[uu] - inc) * inv;
        float gl = st.gl[uu], gr = st.gr[uu];
        const float dgl = (ngl[uu] - gl) * inv, dgr = (ngr[uu] - gr) * inv;
        const float freq = std::max (ni[uu] * (float) sr, 1.0f);
        const float g = std::pow (0.001f, 1.0f / (freq * decay));
        float* buf = s.buf.data();
        int w = s.write;
        float lp = s.lp;

        for (int i = 0; i < n; ++i)
        {
            inc += dInc;
            gl += dgl;
            gr += dgr;
            const float d = clampf (1.0f / std::max (inc, 1.0e-5f) - groupDelay, 2.0f, (float) (len - 3));
            float rp = (float) w - d;
            if (rp < 0.0f)
                rp += (float) len;
            const int i0 = (int) rp;
            const float fr = rp - (float) i0;
            const int i1 = i0 + 1 >= len ? 0 : i0 + 1;
            const float y = buf[i0] + fr * (buf[i1] - buf[i0]);
            lp += c * (y - lp);
            const float out = lp * g;
            buf[w] = out;
            if (++w >= len)
                w = 0;
            bufL[i] += out * gl;
            bufR[i] += out * gr;
        }
        s.write = w;
        s.lp = (std::abs (lp) < 1.0e-15f) ? 0.0f : lp;
    }
}

void Voice::render (const VoiceContext& ctx, float* outL, float* outR, int n) noexcept
{
    if (! amp.isActive() || n <= 0)
        return;

    const auto& raw = *ctx.raw;
    const float* s = ctx.smooth;

    amp.setParams (raw[AmpA], raw[AmpD], s[AmpS], raw[AmpR]);
    fenv.setParams (raw[FenvA], raw[FenvD], s[FenvS], raw[FenvR]);
    menv.setParams (raw[MenvA], raw[MenvD], s[MenvS], raw[MenvR]);
    const float fe = fenv.advance (n);
    const float me = menv.advance (n);
    penv *= std::exp (-4.6051702f * (float) n / (std::max (raw[PenvDecay], 1.0e-3f) * (float) sr));

    float lv[2];
    for (int l = 0; l < 2; ++l)
    {
        if (ctx.lfoRetrig[l])
        {
            lfo[l].setShape (ctx.lfoShape[l]);
            lv[l] = lfo[l].advance (ctx.lfoInc[l], n) * ctx.lfoDepth[l];
        }
        else
        {
            lv[l] = ctx.lfoGlobal[l];
        }
        lastLfo[l] = lv[l];
    }
    lastFenv = fe;
    lastMenv = me;

    // ---- modulation matrix ----
    float src[choices::NumModSources] {};
    src[choices::SrcLfo1] = lv[0];
    src[choices::SrcLfo2] = lv[1];
    src[choices::SrcFilterEnv] = fe;
    src[choices::SrcVelocity] = velocity;
    src[choices::SrcModWheel] = ctx.modWheel;
    src[choices::SrcAftertouch] = std::max (ctx.aftertouch, polyPressure);
    src[choices::SrcKeyTrack] = clampf ((currentPitch - 60.0f) / 60.0f, -1.0f, 1.0f);
    for (int m = 0; m < kNumMacros; ++m)
        src[choices::SrcMacro1 + m] = ctx.macros[m];
    src[choices::SrcModEnv] = me;
    src[choices::SrcRandom] = randomValue;

    float dst[choices::NumModDests] {};
    for (int i = 0; i < ctx.numSlots; ++i)
    {
        const auto& sl = ctx.slots[(size_t) i];
        dst[sl.dst] += sl.amt * src[sl.src];
    }

    // ---- pitch ----
    currentPitch += (targetPitch - currentPitch) * ctx.glideAlpha;
    const float basePitch = currentPitch + s[PenvAmt] * penv + 24.0f * dst[choices::DstPitch];
    const float detune = clampf (s[UniDetune] + dst[choices::DstDetune], 0.0f, 1.0f);

    std::fill (bufL, bufL + n, 0.0f);
    std::fill (bufR, bufR + n, 0.0f);

    // Snapshot both oscillators' first voices before rendering (FM / RM modulators).
    for (int o = 0; o < 2; ++o)
    {
        modPhase[o] = osc[o].phase[0];
        modInc[o] = osc[o].inc[0];
        modPos[o] = osc[o].pos * (float) (kWtFrames - 1);
        modMip[o] = Wavetable::mipForIncrement (modInc[o]);
    }

    const float inv = 1.0f / (float) n;
    float pitchA = basePitch;

    for (int o = 0; o < 2; ++o)
    {
        const int b = OscA_Table + o * kOscParamCount;
        const float pitch = basePitch + 12.0f * (float) raw.i (b + 2) + (float) raw.i (b + 3) + s[b + 4] * 0.01f
                          + 24.0f * dst[o == 0 ? choices::DstPitchA : choices::DstPitchB];
        if (o == 0)
            pitchA = pitch;
        const float pos = clampf (s[b + 1] + dst[o == 0 ? choices::DstPosA : choices::DstPosB], 0.0f, 1.0f);
        const float level = clampf (s[b + 5] + dst[o == 0 ? choices::DstLevelA : choices::DstLevelB], 0.0f, 1.0f);
        const float pan = clampf (s[b + 6] + dst[o == 0 ? choices::DstPanA : choices::DstPanB], -1.0f, 1.0f);
        const float warp = clampf (s[b + 10] + dst[o == 0 ? choices::DstWarpA : choices::DstWarpB], 0.0f, 1.0f);
        const bool isString = raw.i (b + 8) == choices::String;

        OscState& st = osc[o];
        std::array<float, kMaxUnison> ni {}, ngl {}, ngr {};
        int nv = 1;
        computeOsc (o, ctx, pitch, level, pan, detune, ni, ngl, ngr, nv);

        if (! st.init || st.voices != nv)
        {
            for (int u = 0; u < nv; ++u)
            {
                if (! st.init || u >= st.voices)
                {
                    st.phase[(size_t) u] = nv > 1 ? rng.next01() : 0.0f;
                    st.strings[(size_t) u].reset();
                }
                st.inc[(size_t) u] = ni[(size_t) u];
                st.gl[(size_t) u] = ngl[(size_t) u];
                st.gr[(size_t) u] = ngr[(size_t) u];
            }
            st.pos = pos;
            st.warp = warp;
            st.voices = nv;
            st.init = true;
        }

        bool silent = true;
        for (int u = 0; u < nv; ++u)
            if (st.gl[(size_t) u] + st.gr[(size_t) u] + ngl[(size_t) u] + ngr[(size_t) u] > 1.0e-6f)
                silent = false;

        if (! silent && ctx.table[o] != nullptr)
        {
            if (isString)
                renderString (o, ctx, n, ni, ngl, ngr);
            else
                renderWavetable (o, ctx, n, pos, warp, ni, ngl, ngr);
        }
        else
        {
            for (int u = 0; u < nv; ++u) // keep phases moving so re-entry is continuous
            {
                float& ph = st.phase[(size_t) u];
                ph += ni[(size_t) u] * (float) n;
                ph -= std::floor (ph);
            }
        }

        // String mode does not advance wavetable phases; keep them moving for FM / RM use by the other osc.
        if (isString)
            for (int u = 0; u < nv; ++u)
            {
                float& ph = st.phase[(size_t) u];
                ph += 0.5f * (st.inc[(size_t) u] + ni[(size_t) u]) * (float) n;
                ph -= std::floor (ph);
            }

        for (int u = 0; u < nv; ++u)
        {
            st.inc[(size_t) u] = ni[(size_t) u];
            st.gl[(size_t) u] = ngl[(size_t) u];
            st.gr[(size_t) u] = ngr[(size_t) u];
        }
        st.pos = pos;
        st.warp = warp;
    }
    pendingExcite = false;

    // ---- sub + noise ----
    {
        const float newSubInc = std::min (pitchToHz (pitchA - 12.0f) / (float) sr, 0.45f);
        const float newSub = clampf (s[SubLevel] + dst[choices::DstSubLevel], 0.0f, 1.0f);
        const float newNoise = clampf (s[NoiseLevel] + dst[choices::DstNoiseLevel], 0.0f, 1.0f);
        if (! levelsInit)
        {
            subInc = newSubInc;
            subLevel = newSub;
            noiseLevel = newNoise;
            levelsInit = true;
        }
        const bool tri = raw.i (SubShape) == choices::SubTriangle;
        if (subLevel + newSub > 1.0e-6f)
        {
            float inc = subInc, lvl = subLevel;
            const float dInc = (newSubInc - subInc) * inv, dl = (newSub - subLevel) * inv;
            for (int i = 0; i < n; ++i)
            {
                inc += dInc;
                lvl += dl;
                const float p = subPhase;
                const float v = tri ? (p < 0.25f ? 4.0f * p : (p < 0.75f ? 2.0f - 4.0f * p : 4.0f * p - 4.0f))
                                    : std::sin (kTwoPiF * p);
                bufL[i] += v * lvl;
                bufR[i] += v * lvl;
                subPhase += inc;
                if (subPhase >= 1.0f)
                    subPhase -= 1.0f;
            }
        }
        if (noiseLevel + newNoise > 1.0e-6f)
        {
            float lvl = noiseLevel;
            const float dl = (newNoise - noiseLevel) * inv;
            for (int i = 0; i < n; ++i)
            {
                lvl += dl;
                const float v = rng.nextBipolar() * lvl * 0.6f;
                bufL[i] += v;
                bufR[i] += v;
            }
        }
        subInc = newSubInc;
        subLevel = newSub;
        noiseLevel = newNoise;
    }

    // ---- filter ----
    const float cutoffPitch = ctx.cutoffPitch + s[FltKeyTrack] * (currentPitch - 60.0f) + s[FltEnvAmt] * 72.0f * fe
                            + 60.0f * dst[choices::DstCutoff];
    filter.process (raw.i (FltType), bufL, bufR, n, pitchToHz (clampf (cutoffPitch, 0.0f, 140.0f)),
                    s[FltRes] + dst[choices::DstRes], s[FltDrive] + dst[choices::DstDrive],
                    clampf (s[FltVowel] + dst[choices::DstFormant], 0.0f, 1.0f));

    // ---- amplitude ----
    for (int i = 0; i < n; ++i)
    {
        const float a = amp.next() * kVoiceGain;
        outL[i] += bufL[i] * a;
        outR[i] += bufR[i] * a;
    }

    if (! amp.isActive())
        reset();
}
} // namespace volt
