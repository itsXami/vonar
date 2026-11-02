#pragma once

namespace volt
{
// Stage 2 placeholder: hard ceiling only; full chain implemented in stage 3.
class FxChain
{
public:
    void prepare (double, int) {}
    void reset() {}
    void process (float* L, float* R, int n) noexcept
    {
        for (int i = 0; i < n; ++i)
        {
            L[i] = L[i] > 0.98f ? 0.98f : (L[i] < -0.98f ? -0.98f : L[i]);
            R[i] = R[i] > 0.98f ? 0.98f : (R[i] < -0.98f ? -0.98f : R[i]);
        }
    }
    float getLimiterReductionDb() const noexcept { return 0.0f; }
};
} // namespace volt
