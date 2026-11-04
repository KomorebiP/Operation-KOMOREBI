# SF-LEAN-B15: arbitrary-radius exact evaluation certificates

This block proves the registered mathematical evaluation contract from
Appendix J for the actual canonical coupled entire functions under
0<q,r,a,b<1. Let Q be the maximum scale and M(x)=max(UReal(x),VReal(x)).
For every nonnegative radius the following certificate is proved:

\[
M(x)\le x(1+M(Qx)^2),\qquad
M(x)\le x/(1-x^2)\quad(0\le x<1).
\]

A fuel-indexed majorant stops at the first small radius and propagates
the recurrence backward. If Q^fuel*S<1, it bounds both actual functions
throughout the complex disk of radius S. Adequate fuel exists for every
nonnegative radius. This construction does not invoke the growth-order law.

When F_N retains odd coefficient indices 0 through N, for S>R>=0:

\[
|F(z)-F_N(z)|\le B(S)(R/S)^{2N+3}\quad(|z|\le R).
\]

No additional geometric denominator occurs. For x>=0, positivity gives
the real enclosure [F_N(x),F_N(x)+B(S)(x/S)^(2N+3)]. Zero input/radius is
included. The outer radius is strictly larger than the target radius.

The Lean model has exact rational scale parameters, a rational ordinary
coefficient recurrence, rational polynomials and a rational finite majorant.
Casting these quantities to the reals gives the existing canonical
coefficients, polynomials and majorant. The resulting interval has rational
endpoints and contains the actual real component. This certifies the Lean
rational model; it is not a proof of the Python program's full behavior.

For the manuscript's unequal pair (1/5,2/5,3/5,7/10), R=1, S=2 and N=30,
exact rational arithmetic proves a tail strictly below 1.6*10^(-13).
The actual complex error satisfies that bound on the closed unit disk.
Here last index 30 retains **31 coefficients through degree 61**, and the
first omitted degree is 63. The displayed rounded U(1),V(1) decimals are
not newly certified by this block.

`lean/CoupledEvaluation.lean` adds **36 theorem declarations**, including
supporting lemmas, for **405 registered names**. All **60 fresh replay
steps** pass across fifteen coupled modules: 366 theorem axiom audits,
fifteen kernel replays, four expected rejections and one positive fixture.
The finite core's 39-name evidence is inherited. Pinned Mathlib imports
are cached, not freshly rebuilt/replayed. Review provenance is self-review.

## Argument and source correspondence

Authority: `monograph/sections_v11/coupled_lab_full.tex`, lines 44-87 and
the worked call at lines 93-110, at base
`f5b2651f182244afd4d979d9aed386e45c898381`. Source code assessment also
binds `research/coupled_lab.py` and its imported `research/family_lab.py`;
these are assessed as remaining refinement inputs, not trusted proof leaves.
Manuscripts, reading PDFs, earlier blocks and dated guides retain their bytes.

Existing real derivative bounds and monotonicity bound each contracted
factor by M(Qx), giving the scalar max recurrence. The inherited coefficient
bound 2^(-n)<=1 and the convergent geometric series at x<1 give the source's
x/(1-x^2) seed. The finite majorant induction handles a small radius directly;
otherwise Qx is nonnegative and satisfies the child terminal condition.
The nonnegative actual max profile and its child bound allow squaring and
propagating the recurrence. Q^n*S tends to zero, proving adequate fuel exists.

For the outer tail, put beta=R/S in [0,1). For every m>=2N+3,
R^m=beta^m*S^m<=beta^(2N+3)*S^m. The actual summable complex series is
split into its finite prefix and shifted tail. Nonnegative coefficients
bound each tail norm by beta^(2N+3) times its positive term at S. The
positive omitted sum at S is at most the full F(S), giving the displayed
bound without a geometric denominator. The real partial sum lies below
the actual function; complex-to-real identification gives the upper endpoint.

The rational majorant uses the same finite recurrence, with the same stop
test, and its real cast is proved by fuel induction. Rational coefficients
use the ordinary simultaneous recurrence. Their cast is a full coefficient
solution, so the established uniqueness theorem identifies it with the
canonical real sequence for every index. Casts commute with finite sums,
powers and maximum, identifying rational polynomial and maximum-scale data.
These identities turn the real enclosure into one with exact rational
endpoints. Rational adequate fuel follows by casting the real existence
theorem. The worked tail bound is kernel-checked `norm_num` arithmetic,
not an external numerical experiment or an assumed decimal approximation.

## Evidence and boundaries

The claim map covers every new theorem once. Declarations and source hashes,
focused self-review, actual I/O and the accepted raw receipt bind the result.
The verifier `tools/verify_coupled_evaluation.py` uses a new external work
directory, installs nothing, makes no network request and checks input
stability at the end. Source and assessment I/O are separate from unaccepted
development diagnostics; root archive manifests remain historical snapshots.

The registered Appendix J **mathematical certificate** is complete. Full
Python-to-Lean refinement remains open: factorial-normalized derivative
arrays, their conversion to ordinary coefficients, the guarded while-loop
and exact dictionary endpoints need explicit correspondence. Resource errors
must not be treated as successful weaker certificates. Additional J degree,
denominator-clearing and symmetry statements need mapping before exhaustive
appendix coverage is claimed. Remaining F/H correspondence, I's resolution
mechanisms and broad A-E analytic development remain. Ordinary type
convergence is conditional, and G.2's nonzero-defect guard is retained.
