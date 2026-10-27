# Independent review of shifted Jacobi approximation and height scope

**Normalized claim.** For every ordinary shift r>=0 and truncation size m>=1,
the actual depleted Bernoulli moment ratios admit the stated finite Jacobi
model, agreeing exactly through q<2m and having error valuation at least
`h_m=4m+4v_2(m!)` for every q>=0, with equality at q=2m. On the admitted
terminal-161 chart, this gives a depleted function error of valuation at least
`L=h_m-178`, a half-derivative error of valuation at least L-1, and, for L>=9,
the claimed stationary-point and critical-value errors. The note gives a
sufficient comparison test with actual undepletion, not a proof that the test
holds for every actual index.

**Primary verdict: proved as written.** The infinite-basis passage, paired-edge
valuation, all-q estimate, packet normalization, derivative loss, and height
limitations check out. No correction was required. The actual Euler
nonintersection claim remains open.

This is an independent review by `/root/cross_cartier_review` of the raw proof,
implementation, and cited local dependencies. Author files were read-only. No
Lean compilation was performed. Exact reviewed files, dependencies, author
evidence, and replay evidence are pinned in `JACOBI_HEIGHT_REVIEW_HASHES.json`.
The main proof SHA256 is
`b721b9c512dc1aae1e9130f99f4f0300fefd3bcf45bb8aaa9d11f1d5d234bfab`.

## Dependencies and obligations

The dependency chain is:

1. The reviewed shifted Bernoulli Gram theorem gives unit norms and Gram
   congruence modulo 4 in the normalized unshifted basis.
2. Finite Gram--Schmidt gives the shifted triangular transformation, which
   extends with its inverse to c_0. Conjugation gives bounded J_r congruent
   to the identity modulo 4.
3. Symmetry and polynomial degree give tridiagonality. Norm ratios give the
   subdiagonal valuation, and finite walks give the uniform truncation error.
4. The actual carry minimum and factorial valuation give the scalar packet
   bound. Integral source packets transfer the uniform moment estimate to
   the full restricted analytic series.
5. The inherited Morse chart and undepletion isometry transfer this to the
   conditional actual nonintersection test.
6. The inherited rational approximation construction and the authenticated
   Bernoulli zeta evaluation support the limited height statements.

| Obligation | Status | Decisive reason |
|---|---|---|
| Shifted orthogonal basis has coefficients in 4Z_2 below its diagonal | Passed | Projection numerators vanish modulo 4 and the previous orthogonal norms are units |
| Infinite basis change and inverse are bounded on c_0 | Passed | Both have uniformly integral entries and finite columns, and their identities extend from finite sequences by continuity |
| J_r is tridiagonal and congruent to I modulo 4 | Passed | Integral conjugation preserves the congruence; symmetry and the degree filtration kill distant coefficients |
| Shifted edge-product valuation | Passed | Norm ratio gives `v_2(a_n)=4+4v_2(n)`; upward/downward normalized products equal a_n |
| Moment normalization by D(r) | Passed | The e_0 norm is D(r), so the normalized moment equals the matrix-power 00 entry |
| All-q truncation bound and exact first exit | Passed | Every omitted walk contains all m paired boundary edges; at length 2m only the ascending/descending path remains |
| Depleted packet scalar and convergence | Passed | Factorial valuation gives `154+lambda_r(q)>=0`, tending to infinity with q |
| Coefficientwise function error and ordinary Z derivative | Passed | The source packets are integral; division by 2 is the only additional half-derivative loss |
| Critical point and value errors | Passed | Isometry gives displacement L-1; stationarity makes value displacement quadratic |
| Passage from depleted to actual scalar | Passed in conditional form | A valuation strictly below both L and E cannot be canceled by either error |
| Height control and its limitations | Passed | The note gives an available upper bound and an actual unit-height counterexample; neither is promoted to a universal impossibility result |
| Actual critical scalar nonvanishing | Not established | The required strict valuation-versus-error inequality is still missing |

## Infinite change of basis and path reconstruction

There is no unbounded triangular inversion hidden in the proof. Inductively,
the shifted orthogonal vector of degree n has lower e-coordinates in 4Z_2.
Its norm is a unit, so each succeeding projection still divides only by a
unit. The resulting matrix S has finite columns and `S-I` uniformly divisible
by 4. The triangular inverse has the same properties. Such matrices act
contractively on finite coefficient sequences and preserve that space; they
therefore extend to bounded maps on c_0. The algebraic inverse identities hold
on a dense subspace and hence everywhere. Equivalently, the inverse follows
from the convergent operator Neumann series for S-I.

The continuous shifted bilinear form and multiplication operator retain
symmetry. Pairing U times the degree-n orthogonal polynomial with degrees
less than n-1 gives zero; multiplication cannot raise degree by more than one.
Thus conjugation really yields a tridiagonal operator. Its upward coefficient
is `c_(n+1)/c_n=4(n+1)^2`. The norm-ratio formula for the monic recurrence gives
the stated a_n valuation; the downward coefficient is `a_n/(4n^2)`.
Both directions are integral and divisible by 4.

Since the first basis vector is 1, its shifted norm is D(r). Therefore
`D(r+q)/D(r)=(J_r^q)_(0,0)`. For a fixed ordinary q, this entry is a finite
sum of walks, despite the matrix being infinite. Comparing it with the
leading m-by-m truncation deletes precisely the walks visiting m. Any such
walk returns to 0 and hence traverses every edge between 0 and m both ways.
The product of one selected up/down pair for each edge is exactly
`a_1 ... a_m`. Additional weights are integral. This proves the lower bound
for every q, without a cancellation assumption or unproved estimate on a
recurrence after its fitted prefix. For q<2m there is no deleted path; for
q=2m there is exactly one. Its nonzero weight proves exact valuation h_m.

The checker uses the monic basis, whose upward coefficient is 1. This is
legitimate: finite diagonal conjugation does not alter the 00 entry of a
matrix power. The claim `J=I mod4` belongs to the normalized basis, and was
not mistakenly applied to the checker's monic matrix.

## Full source transfer and the actual/depleted boundary

For the focused family, direct factorial valuation gives

    v_2((2r+2q)!/(2r)!)
      =2q-s_2(r+q)+s_2(r).

The displayed scalar R consequently has valuation
`154+3q+s_2(r+q)-s_2(r)=154+lambda_r(q)`. The true terminal and mu=-154
hypothesis makes this nonnegative for every q. Its growth also proves
restricted convergence after replacing the moment ratios by unit model
moments.

The scalar uses the **depleted** ratio `D(r+q)/D(r)`. It does not silently
replace the actual Bernoulli ratio at all precision. In the independent
undepletion family, this is exactly the eta=0 normalization. The subsequent
actual correction is handled separately through E=2r-25.

The polynomial P_q and the translated source A have integral restricted
coefficients, also after substituting `x=10202+2^15 Z`. The uniform error
bound h_m therefore survives every q-th packet, and the global normalization
loses 178 bits. Convergence passes this ideal membership to the infinite sum.
Ordinary differentiation in Z is bounded in the integral restricted algebra;
division by 2 loses one bit. No physical-x derivative scaling is omitted:
the comparison at this stage explicitly uses Z derivatives on both sides.

For L>=9 the half derivatives retain the inherited isometry and unique
critical point. Evaluating the model half derivative at the true depleted
critical point gives the displacement bound L-1. The exact function is
stationary there, so translation by that displacement changes its value by
an element of valuation at least 2L-2. Since this is at least L, the direct
function error dominates the resulting critical-value comparison. The identity
`h_m=8m-4s_2(m)` is the usual factorial valuation identity.

Finally, if the model critical value has valuation strictly smaller than
`min(L,E)`, both the depleted approximation error and the actual undepletion
correction have strictly larger valuation. The actual critical scalar then
has the same finite valuation. This is a sufficient criterion, not a statement
that every model eventually satisfies it without an independent nonvanishing
argument.

## Height scope

The inherited source-polynomial construction also applies to the depleted
packets because the depleted moment ratios remain units and retain the same
scalar valuation bounds. The cutoffs and the 178-bit normalization loss match
the cited local arithmetic certificate. A critical lift through ceil(P/2)
bits gives P bits of stationary-value accuracy. The direct rational-height
upper bound still contains degree times lift length; a basis change in the
separate moment variable U does not change that rational value or automatically
cancel its reduced height.

The actual height control is correctly normalized. The recorded DLMF identity
gives

    |D(r)|=2(1-2/4^r)(2r)! zeta(2r)/pi^(2r).

For r>=40 this exceeds `(r/pi^2)^r`, which is strictly greater than 4^r.
Reduced rational height is at least absolute value. Thus a dyadic unit moment
can indeed have height above the undepletion scale. This does not rule out
cancellation or sharper height bounds for a specially constructed critical
expression. The note explicitly preserves that distinction.

The recurrence and Bernoulli evaluation are authenticated in the existing
`SOURCE_CHECK.md` and companion Hankel record. This review checked their
normalization and use; it does not claim a new primary PDF cache or a fresh
independent source authentication.

## Computation replay and exact remaining implication

Both the checker and its imported rational Bernoulli helper were read. The
checker constructs Bernoulli moments independently, performs exact rational
Gram--Schmidt, and compares finite matrix-power moments against those inputs.
The 0,...,24 range includes values beyond the matched prefix for every tested
size. The output's null valuations mean exact rational zero, not modular
uncertainty.

The independent replay in `review/jacobi_replay` is byte-identical to the
author result. Author and replay manifests validate with project-root artifact
checks. It repeats 42 recurrence-coefficient checks, 875 moment comparisons,
35 first-exit checks, and the five actual height controls. No stationary scalar
is computed by this checker; the Euler source/critical transfer is a proof
obligation checked above rather than a claimed numerical experiment.

The smallest missing implication is the strict comparison (4.1), or another
Bernoulli-specific certificate implying the same actual nonvanishing. The
Jacobi construction now supplies all-q approximation and convergence control;
it does not supply a nonzero critical value or a proved low-height algebraic
description of that value. The strongest safe conclusion is the exact
approximation theorem together with its conditional nonintersection test.

Self-review: the complete new report was conservatively proofread. No
mathematical-token correction or unresolved local notation issue remains.
