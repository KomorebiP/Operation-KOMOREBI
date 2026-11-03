# Focused self-review: SF-LEAN-B10

Verdict: **proved as written** for the explicit upper-comparison contract.
Provenance: self-review. Base: `2661894c45768d240e9c2fcc4524061e404a0411`.
Audited source: `lean/CoupledUpperGrowth.lean`, SHA256
`0b899b5d8639a9fe6a957af7ceffc7a3e173557c0bc7f347c92dc92fec344f1d`. Kernel replay is separate
execution evidence; this report is not independent review.

Claim card: for each tuple 0<q,r,a,b<1, every N with (1/Q)^N>=3/m, its
positive characteristic rho and normalized positive right vector w, both
actual canonical real functions satisfy log(F_i(R))<=c_plus*w_i*R^rho-log(R)-D
for every real R>=exp(1), with the manuscript's explicit constants. Such N
exists, and a least-index wrapper gives positive canonical coefficients and
two-sided growth-ratio bounds. All coefficients, powers and orders are real.
Complex norms are transported through Block08's exact embedding/norm identity.

Dependency graph: Block01 coefficient majorant + Block08 actual HasSum ->
bound at one; Block08 actual derivatives/monotonicity/origin -> full product
upper recurrence -> geometric ladder -> W_n bound -> log seed. Scale
geometry -> positive delay interval and correction-row bounds -> delayed
recurrences. Block07 characteristic rows + seed -> closed-cap propagation ->
explicit real-power upper bound. Block09 lower comparison -> two-sided ratio
wrapper. No edge uses a type object, later limit or the desired upper bound
as its own seed. All leaves are internal proofs or pinned Mathlib results.

| Obligation | Result | Evidence |
| --- | --- | --- |
| Actual functions and R=0 | passed | Mean-value bound on closed [0,R], exact origin values |
| Bound at one | passed | Termwise geometric majorant between actual HasSum expansions |
| Ladder indices and both rows | passed | p*R_(n+1)<=R_n; nonnegative product comparisons |
| W_n formula including n=0 | passed | Exact initial value and polynomial recurrence over real casts |
| N existence and seed coverage | passed | Q in (0,1), unbounded powers, exact e<3, closed seed endpoints |
| Logarithm/product hypotheses | passed | Positive real values and explicit child floor >=1 |
| D row constants and delay signs | passed | delta_p in [log(1/Q),Delta], D>=delta_p+delta_p'+log(2) |
| Weighted seed and rho<1 | passed | min(w)>0, rho>0 and exponent monotonicity; rho=1/2 fixture |
| Global induction and endpoints | passed | Translated closed-cap induction with positive minimum delay |
| Canonical constants and ratios | passed | Parameter-only least index, positive coefficients, positive R^rho |
| Norm transport and maxima | passed | Block08 real-axis norm and separately proved attained maxima |
| Type objects, radial limit, F.3 | out of scope | No such formal theorem claimed in this block |

Pinned API checks: Convex.image_sub_le_mul_sub_of_deriv_le in
Mathlib/Analysis/Calculus/Deriv/MeanValue.lean:355 requires continuity on the
closed interval, differentiability on its interior, a derivative upper bound
and ordered endpoints; these are supplied. The geometric HasSum comparison
uses hasSum_le, not an unproved summation interchange. Real.exp_sub,
Real.exp_log and Real.rpow_def_of_pos are used only with positive scale or
radius inputs. The exact rational proof of e<3 is a Lean proof, not a
load-bearing numerical experiment or an external approximation claim.

Decisive evidence: 45 fresh replay steps, exact audits of all 212 coupled
names, ten module kernel replays, four rejections and the positive fixture.
N=0 fails the worked threshold 15<=1. Omitting u,v>=1 is rejected even when
f<=R*(1+u*v) holds. The nonnegative-radius premise is kept at the origin.

Strongest safe conclusion: both explicit comparisons and positive finite
pointwise growth-ratio bounds on R>=e. Remaining gap for full F.2: formal
real liminf/limsup type bounds and the radial exponent limit. The cheapest
next check is to feed the canonical two-sided ratio theorem into the real
filter liminf/limsup APIs with eventual boundedness made explicit. No
mathematical restriction or constant correction was required by this review.
