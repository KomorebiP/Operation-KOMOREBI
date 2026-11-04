# SF-LEAN-B13: exact scalar reductions, explicit functions and order surfaces

This block proves the registered ancillary Appendix F contracts for the
actual canonical coupled pair with 0<q,r,a,b<1:

\[
U=V\iff\{q,r\}=\{a,b\}
\iff(q=a\land r=b)\lor(q=b\land r=a).
\]

Equality is on the entire complex plane. On these loci the characteristic
equation is equivalent to q^rho+r^rho=1. At all four scales equal to 1/2,

\[
U(z)=V(z)=\sqrt2\sinh(z/\sqrt2),\qquad\rho=1.
\]

The exact unequal example (1/5,2/5,3/5,7/10) has order one, normalized
characteristic vector (1/2,1), and V's lower/upper types exactly twice U's
corresponding types. Its two components are different. All four printed
odd coefficients, row sums and explicit lower constants are proved, as
are the stated logarithmic lower bounds for every R>=2. Its degree-seven
polynomials P_U,P_V satisfy the stronger quantitative remainder statement

\[
|U(z)-P_U(z)|,\ |V(z)-P_V(z)|\le |z|^9/8\quad(|z|\le1).
\]

More generally, this block connects the earlier coefficient tail bound to
the actual complex function minus its finite odd polynomial, for all N
and |z|^2<2. It does not claim an arbitrary-radius numerical evaluator.

The characteristic order is invariant under fixing q,b and ar. For any
prescribed t>0 and q,r,b in (0,1) with
(1-q^t)(1-b^t)<r^t, the explicit
a=[(1-q^t)(1-b^t)]^(1/t)/r is proved to lie in (0,1) and to realize exact
radial order t in both canonical components. No integer-exponent or t>=1
restriction is introduced; the strict budget is essential.

The source `lean/CoupledScalarReduction.lean` adds **43 theorem
declarations**, including supporting lemmas, for **342 registered names**.
The accepted fresh replay has 54 passing steps across thirteen coupled
modules, 303 fresh theorem axiom audits and thirteen kernel replays, plus
four expected rejections and one positive interface fixture. The finite
core's 39-name evidence is inherited. Pinned Mathlib imports are cached,
not freshly rebuilt or replayed. Review provenance is self-review.

## Argument and exact correspondence

Authority: `monograph/sections_v11/coupled_growth_full.tex`, ancillary
section beginning at line 425, at base
`718a037fd39c0f1bbad6c66e5e1b6fa570553447`. The manuscript and reading PDFs
are preserved. The six claim-map groups bind every new theorem once.

Necessity uses coefficient equality from the actual entire expansions.
Degree three gives p=qr=ab=k. Degree five, with p>0, gives equal square
sums. The positive sums then agree, and (q-a)(q-b)=0 gives the two unordered
possibilities, including duplicate-scale cases. Product equality by itself
is weaker; a positive rational collision in the interface fixture has
p=k but different canonical components. For sufficiency, the existing
scalar T_(q,r) makes (T,T) solve either row ordering. Entire uniqueness
identifies both canonical components with T globally.

The all-half formula is proved from derivatives. A small helper derives
the complex sinh derivative from the cached exponential derivative, using
the exponential definition calculation in the pinned Mathlib source
`Analysis/SpecialFunctions/Trigonometric/DerivHyp.lean`; that module is not
an added import. The hyperbolic double-angle and square identities show
that c*sinh(c^-1*z) satisfies the half-scale equation when c^2=2. Its zero
initial values and the derivative equation hold for every complex z.
Canonical uniqueness supplies the formula with c=sqrt(2). Determinant
balance and root uniqueness give its exact order one.

For the unequal example, exact rational normalization verifies the printed
coefficients and constants. F.3's already proved type vectors specialize
to (1/2,1). F.2 and the characteristic balance at one give actual order one;
the lower comparison specializes to the manuscript's constants. The tail
identity splits a convergent series into its finite prefix and shifted
sum. The inherited geometric bound then bounds the actual remainder.
On |z|<=1 its four-term expression is at most |z|^9/8, so the printed
O(z^9) expansions have an explicit complex-disk bound.

Order invariance is the unique-positive-root theorem applied to identical
determinant data. For the order surface, the positive base
d=(1-q^t)(1-b^t) has d^(1/t)<r by strict real-power monotonicity. Dividing
by positive r gives 0<a<1, and inverse-power cancellation proves
(ar)^t=d. F.2 identifies this characteristic root with each actual radial
order. Equality in the budget would permit a=1 and is rejected.

## Evidence and limits

`declarations.json`, `CLAIM_MAP.json`, `SELF_REVIEW.md`, `IO_MANIFEST.json`
and `evidence/receipt.json` bind names, claims, review and execution.
`SOURCE_MANIFEST.json` seals immutable phase records and explicit inputs.
The replay tool is `tools/verify_coupled_scalar_reduction.py`; use the pinned
Lean/Mathlib environment and a new external work directory. It installs
nothing, makes no network call and checks input stability at the end.

The registered F.1-F.3, G.1 and guarded G.2 contracts remain complete.
This block adds the named scalar/formula/example/parameter contracts. It
does not assert exhaustive coverage of every ancillary explanatory claim,
generic ordinary type convergence, H.1 operator classification, I-J
end-to-end certificates, or the broad A-E analytic chapters. A full
manuscript-wide claim map and completion percentage remain unavailable.
`REMAINING_WORK.md` identifies the next target and retained boundaries.
