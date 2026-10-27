# AVOC v0.6.0 development failures and repairs

These are development failures, not accepted theorem failures.

1. `Finset.sum_div` was initially used without its field big-operator import. The proof was replaced by an explicit inverse-factor sum, avoiding a broader import.
2. A first pointwise Bayes proof attempted `field_simp`, but that tactic module was not present in the prebuilt lightweight cache. The final proof uses `div_mul_cancel₀`.
3. The first law-of-total-expectation proof tried to reorganize nested sums directly and became brittle. The final proof factors through the already-checked equality between posterior-policy value and Blackwell decision value.
4. An explicit duplicated finite maximum for `bestBayesianDecisionValue` created proof-dependent `Finset.max'` elaboration friction. The final definition canonically reuses `bestStochasticDecisionValue`; equality of each Bayesian policy value with the Blackwell score proves the interpretation, and a best posterior policy is separately shown to exist.
5. A direct theorem rewriting nested channel-specific `bayesUpdate` terms in opposite orders failed because the positivity proof arguments depend on the posterior being rewritten. This route is not counted. The final theorem is stated and proved at the generic likelihood-conditioning level, where sequential composition and commutativity are exact.
6. Initial concrete posterior examples unfolded named belief/channel structures inside dependent terms, causing proof-term mismatch. The final examples leave the posterior opaque and evaluate only scalar predictive and likelihood factors.
7. Initial concrete sequential-evidence positivity checks unfolded normalized posteriors too aggressively. The final examples derive positivity from the proved evidence-normalizer composition identity.
8. Clean aggregate builds require resumable slices because host execution calls are bounded. Build slices are resumed only after the prior child has exited; timeout itself is not treated as a Lean failure.
