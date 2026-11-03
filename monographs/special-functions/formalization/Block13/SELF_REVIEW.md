# Focused self-review of the ancillary scalar and parameter contracts

Primary verdict: **proved as written within the registered Block13 scope**.
Provenance: self-review, not independent review. Exact production bytes
and theorem names are bound by declarations.json and the replay receipt;
base revision is 718a037fd39c0f1bbad6c66e5e1b6fa570553447.

Claim card: actual canonical complex U,V for all positive strict contraction
quadruples; global equality iff unordered rows coincide; scalar determinant
reduction; exact normalized half-scale sinh formula and order; exact unequal
example types, coefficients, lower bounds and complex polynomial remainder;
invariant determinant data and explicit positive order surfaces. Ordinary
types are the existing real liminf/limsup definitions. No unconditional
generic convergence or full analytic monograph certificate is asserted.

Dependency graph: canonical entire expansions -> coefficient identities
-> positive product/square-sum algebra -> necessary row alternatives.
Existing scalar solution + entire uniqueness -> global sufficiency.
Cached exponential derivative + hyperbolic identities -> exact half-scale
solution -> uniqueness -> formula. Characteristic uniqueness + F.2/F.3 ->
orders/types/example. Absolute summability + finite-prefix identity +
geometric coefficient majorant -> actual complex remainder. Positive real
power monotonicity/cancellation -> parameter budget -> exact order surface.
No dependency points from an earlier module back to this source.

| Obligation | Result | Evidence |
| --- | --- | --- |
| Entire equality rather than jet equality | passed | Coefficients only prove necessity; the converse uses actual global derivative equations and entire uniqueness. |
| Product and square-sum cancellation | passed | p>0 is proved from positive q,r; positive total sums rule out the wrong square-root sign. |
| Swapped rows and duplicate scales | passed | Both disjuncts are constructed; Set.pair_eq_pair_iff also handles repeated entries. |
| Scalar characteristic equation | passed | Same-row expansion or crossed-row positive factor cancellation; t>0 and q<1 retained. |
| Hyperbolic normalization | passed | c^2=2, hence c!=0; derivative chain cancels c*c^-1, and the double-angle identity gives the exact RHS. |
| Initial values and global domain | passed | Both functions vanish at zero and satisfy HasDerivAt equations at every complex z. |
| Unequal example type convention | passed | rho=1 proved; real types agree with actual maxima by Block11; F.3 gives V=2U for both extremal types. |
| Exact coefficients and remainder indexing | passed | Ordinary odd powers 2n+1; N=4 retains degrees 1,3,5,7 and leaves degree at least 9. |
| Actual function minus polynomial | passed | Absolute summability justifies finite-prefix splitting before using the inherited shifted-tail norm bound. |
| Closed unit-disk endpoints | passed | |z|<=1 gives |z|^2<2 and denominator>=1/2; z=0 is included. |
| Explicit lower-growth range | passed | R>=2 inherited unchanged; constants and shift specialize exactly. |
| Real power domain and prescribed orders | passed | d,r,t positive; inverse-exponent identities have nonzero t; strict budget gives a<1, including t<1. |
| Preservation of other scopes | passed | G.2 guard retained; no operator theorem, arbitrary-radius evaluator or full A-E claim introduced. |
| Expository scalar-row-order comparisons and general function variation | not addressed as new named theorems | Exact row sums/order are certified, but a full ancillary correspondence audit remains separate. |

Four rejection fixtures test product-only reduction, wrong sinh normalization,
the closed budget endpoint and placeholders. The positive fixture includes
swapped rows, a positive equal-product counterexample to the weaker claim,
zero input, actual complex polynomial error and the general order surface.
The 54-step source-bound replay compiles and audits all thirteen modules and
replays their kernel objects; only propext, Classical.choice and Quot.sound
are allowed. The cached Mathlib imports are not independently rebuilt.

No missing implication remains in this registered target. Remaining
manuscript coverage and provenance limits are listed separately.
