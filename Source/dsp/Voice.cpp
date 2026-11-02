#include "Voice.h"

namespace volt
{
namespace
{
constexpr float kVoiceGain = 0.3f;
}

void Voice::prepare (double sampleRate, uint32_t seed)
{
    sr = sampleRate;
    rng = XorShift (seed);
    amp.setSampleRate (sr);
    fenv.setSampleRate (sr);
    filter.prepare (sr);
    lfo[0].reset (0.0, seed * 3u + 1u);
    lfo[1].reset (0.0, seed * 7u + 5u);
    reset();
}

void Voice::reset()
{
    amp.reset();
    fenv.reset();
    filter.reset();
    penv = 0.0f;
    gate = false;
    note = -1;
    for (auto& o : osc)
        o.init = false;
    subPhase = 0.0f;
    levelsInit = false;
    polyPressure = 0.0f;
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
        penv = 1.0f;
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
}

void Voice::computeOsc (int o, const VoiceContext& ctx, float pitch, float pos, float level, float pan, OscState& st,
                        std::array<float, kMaxUnison>& newInc, std::array<float, kMaxUnison>& newGl,
                        std::array<float, kMaxUnison>& newGr, int& voicesOut) noexcept
{
    juce::ignoreUnused (st, pos);
    const auto& raw = *ctx.raw;
    const int base = OscA_Table + o * kOscParamCount;
    const int n = juce::jlimit (1, kMaxUnison, raw.i (base + 7));
    const float det = ctx.smooth[UniDetune];
    const float detuneSemis = det * det;
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

void Voice::render (const VoiceContext& ctx, float* outL, float* outR, int n) noexcept
{
    if (! amp.isActive() || n <= 0)
        return;

    const auto& raw = *ctx.raw;
    const float* s = ctx.smooth;

    amp.setParams (raw[AmpA], raw[AmpD], s[AmpS], raw[AmpR]);
    fenv.setParams (raw[FenvA], raw[FenvD], s[FenvS], raw[FenvR]);
    const float fe = fenv.advance (n);
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

    float dst[choices::NumModDests] {};
    for (int i = 0; i < ctx.numSlots; ++i)
    {
        const auto& sl = ctx.slots[(size_t) i];
        dst[sl.dst] += sl.amt * src[sl.src];
    }

    // ---- pitch ----
    currentPitch += (targetPitch - currentPitch) * ctx.glideAlpha;
    const float basePitch = currentPitch + s[PenvAmt] * penv + 24.0f * dst[choices::DstPitch];

    std::fill (bufL, bufL + n, 0.0f);
    std::fill (bufR, bufR + n, 0.0f);

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

        OscState& st = osc[o];
        std::array<float, kMaxUnison> ni {}, ngl {}, ngr {};
        int nv = 1;
        computeOsc (o, ctx, pitch, pos, level, pan, st, ni, ngl, ngr, nv);

        if (! st.init || st.voices != nv)
        {
            for (int u = 0; u < nv; ++u)
            {
                if (! st.init || u >= st.voices)
                    st.phase[(size_t) u] = nv > 1 ? rng.next01() : 0.0f;
                st.inc[(size_t) u] = ni[(size_t) u];
                st.gl[(size_t) u] = ngl[(size_t) u];
                st.gr[(size_t) u] = ngr[(size_t) u];
            }
            st.pos = pos;
            st.voices = nv;
            st.init = true;
        }

        bool silent = true;
        float maxInc = 0.0f;
        for (int u = 0; u < nv; ++u)
        {
            if (st.gl[(size_t) u] + st.gr[(size_t) u] + ngl[(size_t) u] + ngr[(size_t) u] > 1.0e-6f)
                silent = false;
            maxInc = std::max (maxInc, std::max (st.inc[(size_t) u], ni[(size_t) u]));
        }

        if (! silent && ctx.table[o] != nullptr)
        {
            const Wavetable& wt = *ctx.table[o];
            const int mip = Wavetable::mipForIncrement (maxInc);
            const float fromPos = st.pos * (float) (kWtFrames - 1);
            const float dPos = (pos - st.pos) * (float) (kWtFrames - 1) * inv;

            for (int u = 0; u < nv; ++u)
            {
                const size_t uu = (size_t) u;
                float ph = st.phase[uu];
                float inc = st.inc[uu];
                const float dInc = (ni[uu] - inc) * inv;
                float gl = st.gl[uu], gr = st.gr[uu];
                const float dgl = (ngl[uu] - gl) * inv, dgr = (ngr[uu] - gr) * inv;
                float fp = fromPos;
                for (int i = 0; i < n; ++i)
                {
                    fp += dPos;
                    inc += dInc;
                    gl += dgl;
                    gr += dgr;
                    const float smp = wt.read (mip, fp, ph);
                    bufL[i] += smp * gl;
                    bufR[i] += smp * gr;
                    ph += inc;
                    if (ph >= 1.0f)
                        ph -= 1.0f;
                }
                st.phase[uu] = ph;
            }
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

        for (int u = 0; u < nv; ++u)
        {
            st.inc[(size_t) u] = ni[(size_t) u];
            st.gl[(size_t) u] = ngl[(size_t) u];
            st.gr[(size_t) u] = ngr[(size_t) u];
        }
        st.pos = pos;
    }

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
