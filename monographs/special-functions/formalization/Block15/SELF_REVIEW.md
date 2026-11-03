# Focused self-review of the Appendix J mathematical certificate

Primary verdict: **proved as written within the registered mathematical
evaluation contract**. Provenance: self-review, not independent review.
Exact production bytes and 36 theorem names are bound by declarations.json
and the accepted receipt; base is f5b2651f182244afd4d979d9aed386e45c898381.

Claim card: strict positive real contractions, actual canonical complex
entire functions, arbitrary R>=0 and outer S>R, inclusive odd index N>=0.
Finite adequate majorant fuel bounds both functions and gives complex
polynomial error B(S)*(R/S)^(2N+3). Nonnegative real inputs have exact interval
enclosures. Rational scale/coefficient/polynomial/majorant definitions cast
to these actual quantities, giving rational endpoints. The unequal worked
case at N=30 has error <1.6*10^(-13) on the closed unit disk. Python program
refinement is not part of this verdict.

Dependency graph: existing entire series, positivity and real derivatives
-> max recurrence/small-disk seed -> finite majorant induction and fuel
existence -> disk bound. Positive series at S + actual prefix decomposition
-> power comparison -> complex tail -> real ordered interval. Rational
majorant cast + coefficient-solution uniqueness + finite sum/max casts ->
rational endpoints and fuel. Exact rational worked bound -> actual error.
Earlier modules do not depend on this source. Pinned Mathlib leaves are
standard summability, geometric series, real order, power and rational casts.
No unverified Python computation supports a Lean theorem.

| Obligation | Result | Evidence |
| --- | --- | --- |
| Actual functions and global convergence | passed | Component series are the existing canonical entire sums, not surrogate numerical functions. |
| Max recurrence | passed | Both real differential inequalities, four coordinate bounds and nonnegative products are supplied. |
| Seed domain | passed | 0<=x<1; coefficient<=1 and the geometric series justify x/(1-x^2). |
| Adequate fuel and finite propagation | passed | Q^fuel*S<1; child condition is an exact power identity; Q in (0,1) gives existence. |
| Nonnegative squaring | passed | The actual child max is nonnegative before applying the square comparison. |
| Zero radius/input | passed | Seed and majorant are zero there; exponent 2N+3 is positive; no division by R occurs. |
| Outer radius | passed | S>R>=0 implies S>0 and beta in [0,1); equal radii are rejected. |
| Inclusive indexing | passed | Finset.range(N+1) retains 0..N and omitted exponents are >=2N+3. |
| Actual tail and convergence | passed | Summable complex series split at N+1; positive comparison at S has a summable shifted tail. |
| No extra denominator | passed | The omitted positive sum is bounded by the full F(S), rather than by separate Cauchy coefficient estimates. |
| Real enclosure direction | passed | Every omitted real term is nonnegative; the complex norm bound controls the upper difference. |
| Rational coefficient identification | passed | Cast sequence satisfies the full canonical recurrence; uniqueness identifies all indices. |
| Rational endpoints | passed | Finite rational polynomial and rational tail cast to the proved real interval. |
| Worked exact threshold | passed | Kernel-checked rational inequality; N=30 means 31 coefficients, degree 61 and omitted degree 63. |
| Order-law independence | passed | Mathematical proof uses entire/positive/derivative facts, not the characteristic-order or type theorem. |
| Python implementation and resource guards | not addressed | Separate source-bound refinement obligation; no equality of programs is inferred from formulas. |
| Additional J normalization/degree/denominator claims | not addressed | Retained in the source correspondence inventory. |

Accepted validation: all 60 fresh steps, fifteen compilations/audits/kernel
replays and five control files. Four invalid proof attempts are rejected.
All 366 coupled names are freshly axiom-audited; 39 finite-core names retain
inherited evidence. Only propext, Classical.choice and Quot.sound are
allowed. Mathlib imports are cached rather than freshly replayed.
No gap remains in the registered mathematical contract; no whole-book
audit or completion percentage is claimed.
