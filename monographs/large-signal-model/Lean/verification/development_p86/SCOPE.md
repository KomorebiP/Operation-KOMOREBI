P86 main marginal and rolling-window formalization

The comparison uses actual Markov kernels P,Q on one measurable state space,
a probability reference μ, the literal row-measure minorization
ofReal(ρ) • μ ≤ P(x), and a pointwise actual conditional-law TV upper budget Δ.
No Dobrushin coefficient or error recurrence is supplied as a field. The state
space is arbitrary measurable; no Standard Borel restriction is added.

MarkovMinorization derives the strict contraction of output marginal measures
by showing that every pulled-back measurable [0,1] test has oscillation at most
1−ρ. For ρ<1 its normalized pullback is another [0,1] test. For ρ=1 the pullback
is constant, and the output discrepancy is zero. This derives actual
TV(Pν,Pη) ≤ (1−ρ)TV(ν,η), rather than incorrectly applying strict contraction
to a joint record that retains its starting state.

MarkovMarginals defines literal iterates ν_(n+1)=P∘ν_n. Adding a common-P step
and changing one kernel derives e_(n+1) ≤ (1−ρ)e_n+Δ. The displayed geometric
closed form, its cap by one, and the complete-refresh ρ=1 endpoint are proved.
A same-initial-law nonnegative budget gives the all-time one-marginal Δ/ρ bound.

MarkovRecords constructs chronological joint probability measures by actual
composition products with the kernel row at the last recorded state. Prefix
consistency and the equality of the last-coordinate law with the actual
marginal iterate are proved. A record with L transitions contains L+1 states,
including its entry state. Its TV bound is min(1, entry TV+LΔ).

MarkovWindows defines a rolling window as the literal measurable segment
pushforward of the full record at t+L. The restart-at-the-time-t-marginal identity
is proved using measurable mapping of the composition product. Consequently
its TV is at most min(1,e_t+LΔ), which is the source k-observation formula with
k=L+1. Geometric entry budgets, uniform-in-start-time same-initial windows, and
the exact reference bound 2437/22320 are explicit corollaries.

The kernels are autonomous and globally defined. This does not claim stability
for arbitrary policies remembering an entire history. It does not replace a
complete-record error budget with a marginal bound.

The three semantic controls reject actual False: strict contraction without
minorization for the identity kernel; erasing the kernel discrepancy under
ρ=1; and strict contraction of a retained-entry joint record under complete
refresh. Each uses actual probability measures and kernels.

The final Bernoulli full-record TV→1 separation is authored separately in
BernoulliRecordSeparation.lean. This main-core receipt does not certify that
separate leaf or cumulative P86 release integration by itself.
