#include "SynthEngine.h"

namespace volt
{
SynthEngine::SynthEngine()
{
    for (int p = 0; p < NumParams; ++p)
        if (spec (p).type == ParamType::Float)
            floatParams.push_back (p);

    const auto& divs = choices::tempoDivisions();
    for (int i = 0; i < divs.size() && i < (int) lfoDivBeats.size(); ++i)
        lfoDivBeats[(size_t) i] = choices::divisionToBeats (divs[i]);
    const auto& ar = choices::arpRates();
    for (int i = 0; i < ar.size() && i < (int) arpRateBeats.size(); ++i)
        arpRateBeats[(size_t) i] = choices::divisionToBeats (ar[i]);
    const auto& dt = choices::delayTimes();
    for (int i = 0; i < dt.size() && i < (int) delayBeats.size(); ++i)
        delayBeats[(size_t) i] = choices::divisionToBeats (dt[i]);
    const auto& pr = choices::pumpRates();
    for (int i = 0; i < pr.size() && i < (int) pumpBeats.size(); ++i)
        pumpBeats[(size_t) i] = choices::divisionToBeats (pr[i]);

    for (int p = 0; p < NumParams; ++p)
        raw.v[(size_t) p] = spec (p).defaultValue;
}

void SynthEngine::prepare (double sr, int maxBlockSize)
{
    sampleRate = sr;
    ctx.sampleRate = sr;
    for (int i = 0; i < kMaxVoices; ++i)
        voices[(size_t) i].prepare (sr, 0x1234567u + (uint32_t) i * 7919u);
    globalLfo[0].reset (0.0, 99u);
    globalLfo[1].reset (0.25, 199u);
    arp.prepare (sr);
    fx.prepare (sr, maxBlockSize);
    reset();
}

void SynthEngine::reset()
{
    for (auto& v : voices)
        v.reset();
    stackSize = 0;
    modWheel = aftertouch = 0.0f;
    lastNotePitch = -1.0f;
    smInit = false;
    freePpq = 0.0;
    arp.reset();
    fx.reset();
}

int SynthEngine::getNumActiveVoices() const noexcept
{
    int n = 0;
    for (const auto& v : voices)
        n += v.isActive() ? 1 : 0;
    return n;
}

// ---------------------------------------------------------------------------------------------
void SynthEngine::handleMidi (const juce::MidiMessage& m) noexcept
{
    if (m.isNoteOn())
    {
        midiNoteOn (m.getNoteNumber(), m.getFloatVelocity());
    }
    else if (m.isNoteOff())
    {
        midiNoteOff (m.getNoteNumber());
    }
    else if (m.isController())
    {
        const int cc = m.getControllerNumber();
        if (cc == 1)
            modWheel = (float) m.getControllerValue() / 127.0f;
        else if (cc == 120)
            allNotesOff (true);
        else if (cc == 123)
            allNotesOff (false);
    }
    else if (m.isChannelPressure())
    {
        aftertouch = (float) m.getChannelPressureValue() / 127.0f;
    }
    else if (m.isAftertouch())
    {
        for (auto& v : voices)
            if (v.isActive() && v.note == m.getNoteNumber())
                v.polyPressure = (float) m.getAfterTouchValue() / 127.0f;
    }
    else if (m.isAllNotesOff() || m.isAllSoundOff())
    {
        allNotesOff (m.isAllSoundOff());
    }
}

void SynthEngine::midiNoteOn (int note, float velocity) noexcept
{
    if (raw.b (ArpOn))
        arp.noteOn (note, velocity);
    else
        noteOn (note, velocity);
}

void SynthEngine::midiNoteOff (int note) noexcept
{
    if (raw.b (ArpOn))
        arp.noteOff (note);
    else
        noteOff (note);
}

void SynthEngine::allNotesOff (bool hard) noexcept
{
    arp.reset();
    for (auto& v : voices)
    {
        if (hard)
            v.kill();
        else if (v.isActive())
            v.release();
    }
    stackSize = 0;
}

void SynthEngine::noteOn (int note, float velocity) noexcept
{
    const int mode = raw.i (VoiceMode);
    const bool glideOn = raw[Glide] > 1.0e-3f;

    if (mode == choices::Poly)
    {
        Voice* target = nullptr;
        for (auto& v : voices) // same note already sounding: retrigger it
            if (v.isActive() && v.note == note) { target = &v; break; }

        if (target == nullptr)
            for (auto& v : voices)
                if (! v.isActive()) { target = &v; break; }

        if (target == nullptr) // steal: oldest released voice, otherwise the oldest voice
        {
            for (auto& v : voices)
                if (v.isReleasing() && (target == nullptr || v.age < target->age))
                    target = &v;
            if (target == nullptr)
                for (auto& v : voices)
                    if (target == nullptr || v.age < target->age)
                        target = &v;
        }

        const float startPitch = (glideOn && lastNotePitch >= 0.0f) ? lastNotePitch : (float) note;
        target->age = ++ageCounter;
        target->start (note, velocity, target->isActive() && glideOn ? target->currentPitch : startPitch, true, ctx);
        if (! glideOn)
            target->currentPitch = (float) note;
    }
    else
    {
        // Mono / Legato: one voice, last-note priority.
        for (int i = 0; i < stackSize; ++i)
            if (stackNotes[(size_t) i] == note)
            {
                for (int j = i; j < stackSize - 1; ++j)
                {
                    stackNotes[(size_t) j] = stackNotes[(size_t) j + 1];
                    stackVel[(size_t) j] = stackVel[(size_t) j + 1];
                }
                --stackSize;
                break;
            }
        const bool othersHeld = stackSize > 0;
        if (stackSize < (int) stackNotes.size())
        {
            stackNotes[(size_t) stackSize] = note;
            stackVel[(size_t) stackSize] = velocity;
            ++stackSize;
        }

        Voice& v = voices[0];
        v.age = ++ageCounter;
        if (mode == choices::Legato && othersHeld && v.isActive())
        {
            v.glideTo (note);
            if (! glideOn)
                v.currentPitch = (float) note;
        }
        else
        {
            const bool canGlide = glideOn && v.isActive() && (mode == choices::Mono);
            const float from = canGlide ? v.currentPitch : (float) note;
            v.start (note, velocity, from, true, ctx);
        }
    }
    lastNotePitch = (float) note;
}

void SynthEngine::noteOff (int note) noexcept
{
    const int mode = raw.i (VoiceMode);
    if (mode == choices::Poly)
    {
        for (auto& v : voices)
            if (v.isGateOn() && v.note == note)
                v.release();
        return;
    }

    int idx = -1;
    for (int i = 0; i < stackSize; ++i)
        if (stackNotes[(size_t) i] == note) { idx = i; break; }
    if (idx < 0)
        return;
    for (int j = idx; j < stackSize - 1; ++j)
    {
        stackNotes[(size_t) j] = stackNotes[(size_t) j + 1];
        stackVel[(size_t) j] = stackVel[(size_t) j + 1];
    }
    --stackSize;

    Voice& v = voices[0];
    if (v.note != note)
        return;

    if (stackSize > 0)
    {
        const int back = stackNotes[(size_t) stackSize - 1];
        if (mode == choices::Legato)
        {
            v.glideTo (back);
            if (raw[Glide] <= 1.0e-3f)
                v.currentPitch = (float) back;
        }
        else
        {
            v.start (back, stackVel[(size_t) stackSize - 1], raw[Glide] > 1.0e-3f ? v.currentPitch : (float) back, true, ctx);
        }
        lastNotePitch = (float) back;
    }
    else
    {
        v.release();
    }
}

// ---------------------------------------------------------------------------------------------
void SynthEngine::beginChunk (int n) noexcept
{
    const float alpha = smInit ? smoothAlpha (n, sampleRate, 0.012f) : 1.0f;
    for (int p : floatParams)
        sm[(size_t) p] += (raw.v[(size_t) p] - sm[(size_t) p]) * alpha;
    const float cutPitch = hzToPitch (raw[FltCutoff]);
    smCutoffPitch += (cutPitch - smCutoffPitch) * alpha;
    if (! smInit)
    {
        for (int p = 0; p < NumParams; ++p)
            if (spec (p).type != ParamType::Float)
                sm[(size_t) p] = raw.v[(size_t) p];
        smCutoffPitch = cutPitch;
        smInit = true;
    }

    ctx.raw = &raw;
    ctx.smooth = sm.data();
    ctx.cutoffPitch = smCutoffPitch;

    const auto& bank = WavetableBank::get();
    ctx.table[0] = &bank[raw.i (OscA_Table)];
    ctx.table[1] = &bank[raw.i (OscB_Table)];
    ctx.modWheel = modWheel;
    ctx.aftertouch = aftertouch;
    for (int m = 0; m < kNumMacros; ++m)
        ctx.macros[m] = sm[(size_t) (Macro1 + m)];

    const double bpm = juce::jlimit (20.0, 999.0, transport.bpm);
    for (int l = 0; l < 2; ++l)
    {
        const int b = Lfo1_Shape + l * kLfoParamCount;
        const bool sync = raw.b (b + 1);
        double inc;
        double beats = 1.0;
        if (sync)
        {
            beats = lfoDivBeats[(size_t) juce::jlimit (0, (int) lfoDivBeats.size() - 1, raw.i (b + 3))];
            inc = (bpm / 60.0) / beats / sampleRate;
        }
        else
        {
            inc = (double) raw[b + 2] / sampleRate;
        }
        ctx.lfoInc[l] = inc;
        ctx.lfoRetrig[l] = raw.b (b + 5);
        ctx.lfoShape[l] = raw.i (b + 0);
        ctx.lfoDepth[l] = sm[(size_t) (b + 4)];
        globalLfo[l].setShape (ctx.lfoShape[l]);
        if (sync)
            globalLfo[l].setPhase (chunkPpq / beats);
        else
            globalLfo[l].advance (inc, n);
        ctx.lfoGlobal[l] = globalLfo[l].value() * ctx.lfoDepth[l];
    }

    ctx.numSlots = 0;
    for (int m = 0; m < kNumModSlots; ++m)
    {
        const int b = Mod1_Src + m * kModSlotParamCount;
        const int src = raw.i (b), dst = raw.i (b + 1);
        const float amt = sm[(size_t) (b + 2)];
        if (src > 0 && dst > 0 && src < choices::NumModSources && dst < choices::NumModDests && std::abs (amt) > 1.0e-5f)
            ctx.slots[(size_t) ctx.numSlots++] = { src, dst, amt };
    }

    const float glide = raw[Glide];
    ctx.glideAlpha = glide > 1.0e-3f ? 1.0f - std::exp (-4.6051702f * (float) n / (glide * (float) sampleRate)) : 1.0f;
}

void SynthEngine::computeGlobalMods (float* dst) const noexcept
{
    // Global targets use free-running LFOs, controllers, macros and the newest sounding voice.
    const Voice* newest = nullptr;
    for (const auto& v : voices)
        if (v.isActive() && (newest == nullptr || v.age > newest->age))
            newest = &v;

    float src[choices::NumModSources] {};
    src[choices::SrcLfo1] = ctx.lfoGlobal[0];
    src[choices::SrcLfo2] = ctx.lfoGlobal[1];
    src[choices::SrcFilterEnv] = newest != nullptr ? newest->lastFenv : 0.0f;
    src[choices::SrcVelocity] = newest != nullptr ? newest->velocity : 0.0f;
    src[choices::SrcModWheel] = modWheel;
    src[choices::SrcAftertouch] = aftertouch;
    src[choices::SrcKeyTrack] = newest != nullptr ? clampf ((newest->currentPitch - 60.0f) / 60.0f, -1.0f, 1.0f) : 0.0f;
    for (int m = 0; m < kNumMacros; ++m)
        src[choices::SrcMacro1 + m] = ctx.macros[m];

    for (int i = 0; i < ctx.numSlots; ++i)
        dst[ctx.slots[(size_t) i].dst] += ctx.slots[(size_t) i].amt * src[ctx.slots[(size_t) i].src];
}

void SynthEngine::renderChunk (float* L, float* R, int n) noexcept
{
    beginChunk (n);
    std::fill (L, L + n, 0.0f);
    std::fill (R, R + n, 0.0f);
    for (auto& v : voices)
        v.render (ctx, L, R, n);

    float gdst[choices::NumModDests] {};
    computeGlobalMods (gdst);

    FxParams fp;
    fp.distType = raw.i (DistType);
    fp.distDrive = sm[DistDrive] + gdst[choices::DstDistDrive];
    fp.distTone = sm[DistTone];
    fp.distMix = sm[DistMix] + gdst[choices::DstDistMix];
    fp.mfxType = raw.i (MfxType);
    fp.mfxRate = sm[MfxRate];
    fp.mfxDepth = sm[MfxDepth];
    fp.mfxMix = sm[MfxMix] + gdst[choices::DstModFxMix];
    fp.pumpAmount = sm[PumpAmount];
    fp.pumpBeats = pumpBeats[(size_t) juce::jlimit (0, (int) pumpBeats.size() - 1, raw.i (PumpRate))];
    fp.dlyMode = raw.i (DlyMode);
    fp.dlyBeats = delayBeats[(size_t) juce::jlimit (0, choices::delayTimes().size() - 1, raw.i (DlyTime))];
    fp.dlyFeedback = sm[DlyFeedback];
    fp.dlyMix = sm[DlyMix] + gdst[choices::DstDelayMix];
    fp.revSize = sm[RevSize];
    fp.revDamp = sm[RevDamp];
    fp.revMix = sm[RevMix] + gdst[choices::DstReverbMix];
    fp.squash = sm[Squash];
    fp.outGainDb = sm[OutGain];
    fp.ppq = chunkPpq;
    fp.bpm = transport.bpm;
    fx.process (L, R, n, fp);

    chunkPpq += (double) n / sampleRate * (transport.bpm / 60.0);
}

void SynthEngine::process (float* outL, float* outR, int numSamples, const juce::MidiBuffer& midi,
                           const ParamSnapshot& params, const TransportInfo& t) noexcept
{
    raw = params;
    transport = t;
    if (transport.playing)
    {
        chunkPpq = transport.ppq;
    }
    else
    {
        chunkPpq = freePpq;
        freePpq += (double) numSamples / sampleRate * (transport.bpm / 60.0);
    }

    const int mode = raw.i (VoiceMode);
    if (mode != lastMode)
    {
        if (lastMode >= 0)
            allNotesOff (false);
        lastMode = mode;
    }
    const bool arpOn = raw.b (ArpOn);
    if (arpOn != lastArpOn)
    {
        allNotesOff (false);
        lastArpOn = arpOn;
    }

    const double bpm = juce::jlimit (20.0, 999.0, transport.bpm);
    const double beatsPerSample = bpm / 60.0 / sampleRate;
    const double blockBeat = chunkPpq;
    const double arpStep = arpRateBeats[(size_t) juce::jlimit (0, choices::arpRates().size() - 1, raw.i (ArpRate))];
    const int arpMode = raw.i (ArpMode), arpOct = raw.i (ArpOct);
    const float arpGate = raw[ArpGate];

    auto it = midi.begin();
    const auto end = midi.end();
    int pos = 0;
    while (pos < numSamples)
    {
        while (it != end && (*it).samplePosition <= pos)
        {
            handleMidi ((*it).getMessage());
            ++it;
        }
        int next = numSamples;
        if (it != end)
            next = std::min (next, std::max ((*it).samplePosition, pos + 1));
        if (arpOn)
        {
            const int a = arp.tick (blockBeat + (double) pos * beatsPerSample, transport.playing, beatsPerSample, arpStep,
                                    arpMode, arpOct, arpGate,
                                    [this] (int nn, float v) { noteOn (nn, v); },
                                    [this] (int nn) { noteOff (nn); });
            if (a < numSamples)
                next = std::min (next, pos + a);
        }
        const int n = std::min (kChunk, next - pos);
        renderChunk (outL + pos, outR + pos, n);
        pos += n;
    }
    while (it != end) // events stamped past the block end
    {
        handleMidi ((*it).getMessage());
        ++it;
    }
}
} // namespace volt
