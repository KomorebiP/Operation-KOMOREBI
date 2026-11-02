# Focused self-review: SF-LEAN-B09

Verdict: **proved as written** for the lower-comparison contract, under the
stated positive strict contraction hypotheses. Review provenance: self-review.
Base: `b672123ad852de103130420565a6c1e9645b63f5`. Audited source: `lean/CoupledLowerGrowth.lean`, SHA256
`17b055c76799ed380374f2834d47cdf461d52ee95fab0babd9151f602e1c540f`. This review is separate from the
kernel evidence and makes no independent-review claim.

Claim card: for every tuple 0<q,r,a,b<1, its canonical real functions,
positive characteristic rho and max-normalized positive right vector w,
both inequalities log(F_i(R))>=c_minus*w_i*(R+C)^rho hold for all real R>=2.
The same coefficients are positive and uniformly bound the growth ratios
below. Definitions and coefficient domain are real; complex norm conclusions
use an explicit embedding identity. There is no assertion about R<2.

Dependency graph: canonical convergent real series and real derivative
equations (Block08) -> linear lower seed and log recurrences (Block08);
characteristic root/vector (Block07) -> normalized row equations;
shift/descent geometry + seed + row propagation -> closed-cap induction ->
global lower comparison -> positive coefficient and ratio/norm wrappers.
No edge depends on a later upper bound, type object or limit. All leaves are
internal Lean proofs or pinned Mathlib real-power/order/Archimedean results;
there is no numerical or unchecked literature input.

Pinned API checks: Mathlib/Analysis/SpecialFunctions/Pow/Real.lean,
Real.mul_rpow (line 477) requires both factors nonnegative, and
Real.rpow_le_rpow (line 550) requires a nonnegative lower base, ordered bases
and nonnegative exponent. Each is supplied explicitly in the propagation.
These are checks against the local pinned source, not a current-release API
or external attribution claim. The compiler checks the Archimedean theorem's
instantiation in the real-radius induction.

| Obligation | Result | Evidence |
| --- | --- | --- |
| Constants and all denominators | passed | Q in (0,1), B>1, C,d,c_minus>0; positive bases for real powers |
| Seed range and normalized weights | passed | Closed [2,B], w_i<=1; F_i(R)>=R and monotonic log |
| Shift sign and scale maximum | passed | (1-Q)C=Q and (Q-p)(1+C)>=0 |
| Finite descent and children | passed | Positive d and every child in [2,R-d] above B |
| Both coupled rows | passed | U at q,a children, V at r,b children, and the exact two eigenvector rows |
| Fractional exponents | passed | Only real-power monotonicity for rho>0; exact rho=1/2 fixture |
| Shared endpoints and global quantifier | passed | Closed caps, seed includes B, step above B, Archimedean cover |
| Canonical coefficient positivity | passed | c_minus>0 and strict positivity of both selected weights |
| Ratio division and complex transport | passed | R^rho>0 at R>=2 and Block08 norm equality |
| Actual liminf/limsup types or upper bound | out of scope | No such formal conclusion claimed |
| Full manuscript/independent review | out of scope | Bounded source addition and self-review only |

Decisive check: the fresh receipt passes all 42 steps, including nine module
kernel replays, exact axiom audits, four expected rejections and the positive
interfaces. The zero-descent control makes the recursive premise circular
and is rejected at 0<0. The shift control is arithmetically false for the
worked tuple. R=0 is rejected by the explicit seed premise 2<=R. These
controls are interface rejections; they are not universal theorems about all
possible variants with omitted hypotheses.

The strongest safe conclusion is the pointwise lower comparison and positive
uniform growth-ratio lower bounds. The smallest next missing implication for
full F.2 is a certified upper comparison; begin with the full-radius product
upper recurrence and geometric seed ladder. Real liminf/type claims are left
open pending the needed boundedness proofs. No correction to the mathematical
contract was required during this review.
