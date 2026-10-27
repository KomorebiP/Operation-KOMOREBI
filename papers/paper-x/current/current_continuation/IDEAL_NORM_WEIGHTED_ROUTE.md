# Exact norm-weighted attachment to actual ideal sums

This module upgrades the predecessor's norm-filtered cardinality identity to
an identity of complex weighted sums. Let `J` be the supplied nonzero integral
ideal in the inverse of the ordinary class `C`, and write `N_J = absNorm J` and
`w_K = torsionOrder K`.

For any weight `f : ℕ → ℂ`, define `G_J(f,Y)` as the sum over actual generators
in the fundamental ideal cone with real norm at most `Y`. Its weight is
`f(absNorm(span {a}))`, using the represented algebraic integer. Define
`A_C(f,X)` as the sum over actual nonzero integral ideals in class `C` with
absolute norm at most `X`.

The proved identity is

\[
G_J(f,XN_J)=w_K\,A_C\bigl(n\mapsto f(nN_J),X\bigr)
\]

for every real `X`, including nonpositive thresholds. The source proves the
bounded domains finite. Its use of `finsum` therefore does not rely on the
convention for functions of infinite support.

The proof has two exact steps:

1. The explicit generator-to-principal-ideal-times-torsion equivalence preserves
   the actual absolute norm. Transporting the finite sum contributes `w_K`.
2. Multiplication by `J` gives an explicit bounded class-to-principal-ideal
   equivalence. Its norm-preservation theorem states `N(IJ) = NI·NJ`, so it
   transports arbitrary norm weights, not just indicator functions.

For `χ : ZMod m →*₀ ℂ`, this gives

\[
G_J(\chi,XN_J)=w_K\chi(N_J)A_C(\chi,X).
\]

The recovery formula divides by `w_K χ(N_J)` only under the explicit condition
`χ(N_J) ≠ 0`. Nontriviality of `χ` alone does not supply that condition.

This is an exact arithmetic attachment. It does not identify a generator count
with an ideal character sum without the norm scaling and torsion factors. It
does not establish an Euler product or remove the remaining finite-mean and
representative conditions in later counting applications.

Source: `lean/PaperX/IdealNormWeightedAttachment.lean`. Compiler outcomes and
hashes are recorded in `privatechecks/ideal_norm_weighted_verification.json`.
The first compiler attempt exposed a coercion ambiguity, missing explicit
finite enumerations, and a definitional-equality obstruction caused by rewriting
an equivalence's whole type. The latter was replaced by an explicit
predicate-preserving equivalence with the same mathematical map.

The corrected module passed the strict compiler (attempt two, exit zero),
including all six theorem declarations, four definitions, two abbreviations,
and three finite-domain instances.

`IdealNormCharacterBound.lean` transfers a supplied bound on this actual
generator sum,

\[
\|G_J(\chi,Y)\|\le B(Y^{1-1/d}+1)\qquad(Y\ge1),
\]

to a bound `‖A_C(χ,X)‖ ≤ M X^(1−1/d)` for every `X ≥ 1`. Its explicit
constant is

\[
M=\frac{B}{\|w_K\chi(N_J)\|}(N_J^{1-1/d}+1).
\]

This transfer assumes no estimate for the ideal sum itself. It uses the exact
weighted attachment, `N_J ≥ 1`, and the nonzero representative factor. Its
compiler result is recorded separately in
`privatechecks/ideal_norm_character_bound_verification.json`.
Its first compiler attempt failed on an unavailable name for the elementary
inequality `1 ≤ X·N_J`; the explicit ordered-ring proof replaces that name.
The corrected transfer module passed the strict compiler (attempt two, exit
zero), adding three theorem declarations. Both source modules are frozen.
