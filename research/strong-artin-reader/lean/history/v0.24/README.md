# Strong Artin Lean v0.24 — Compatible targets and syzygy-aware Hensel lifting

Author: Komorebi P.

## Exact outcome

This checkpoint continues the **intrinsic syzygy-corrected** v0.23 branch. It proves
that an augmented linear map whose dual kernel is the retained syzygy space has
image exactly the annihilator of those syzygies. It connects this identity directly
to v0.23's presentation-level auxiliary selection.

It also gives two sufficient nonlinear repairs:

1. Lift within an **integrally split compatible equation target**, with explicit
   nonlinear compatibility and projected-Jacobian right-inverse hypotheses.
2. Remove **known exact variable-dependent redundant equations** by a triangular
   row operation, then apply the existing nonlinear Hensel theorem to the retained
   subsystem.

Two exact Lean counterexamples show why neither repair follows merely from the
residual syzygy space. These are counterexamples to proposed auxiliary implications,
not to Strong Artin.

## Main formulas

For a linear map J over a field and a dual syzygy subspace S,

    ker J.dualMap = S  ->  range J = S.dualCoannihilator.

Thus

    exists u, J u + error = 0
      iff every syzygy vanishes on error.

Algebraic dual separation makes this valid even without finite dimensionality.
The finite-dimensional hypothesis remains relevant to finite auxiliary selection.

For a split integral target C <= W with retraction r : W -> C, the nonlinear
lifting theorem assumes, on the residual fibre of x0,

    F(x) belongs to C,
    (r o D_x) o R0 = identity + pi E_x,
    pi is nilpotent,
    F(x0) belongs to pi W,
    Taylor remainder at depth n belongs to pi^(n+1) W.

It concludes an exact solution of the **original ambient equation** F(x)=0,
with x congruent to x0. It does not merely solve the projected equation r(F(x))=0.

For exact redundant equations, the invertible transformation

    (w,z) -> (w,z-B(x)w)

sends (F(x),B(x)F(x)) to (F(x),0). The extra derivative term from varying B is
retained in the derivative-block identity, not silently dropped.

## Boundary controls

- F(x)=(x,x^2) has DF(0)(delta)=(delta,0). Yet over Z/8Z, F(2)=(2,4),
  which is not in the horizontal derivative image. The exact syzygy is (-x,1),
  not its value (0,1) at the origin.
- For R=Z/4Z and C=2R, the element 2 is in C and in 2R, but is not in 2C.
  Thus ambient power-divisibility cannot be transferred into an arbitrary
  submodule without an additional strictness/splitting argument.

## Formal scope and ancestry

The additive sources contain 36 theorems, 11 definitions and 1 structure in
7 modules (648 lines). The verifier compiles 13 unchanged direct dependency
modules plus all 7 additive modules, then audits all 47 new theorem/definition
constants. This is not a replay or recount of the entire Strong Artin lineage.

The exact v0.23, v0.19 and v0.16 base archives are retained in `base/`.
`MANIFEST.json` records their SHA-256 values and the precise nested archive
member for every copied dependency. No sibling release is silently substituted.
The portable Lean runtime is not included.

Pinned environment:

    Lean 4.34.0-rc2
    mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06
    -DwarningAsError=true

## Replay

Start from a fresh output tree:

    python3 verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --max-modules 6

Continue the same replay, repeating until PASS:

    python3 verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --resume --max-modules 6

A bounded batch prints INCOMPLETE until every module and the axiom audit finishes.
`RESULT.json` is written as PASS only at that point. Resume verifies source hashes
and previously completed object hashes. All allowed axiom dependencies are limited
to propext, Classical.choice and Quot.sound.

## Arithmetic work not completed

The arithmetic cotangent/Selmer comparison and one-prime interface remain inputs.
No integral compatible target, exact redundant-equation reduction, automorphic
carrier, arithmetic Taylor-Wiles construction, local Tate comparison, Chebotarev
instantiation, patching, ramified comparison, or Strong Artin theorem is constructed.

In particular, solving an arbitrary augmented system F(x)+C y=0 does not imply
F(x)=0 after forgetting y. Arithmetic descent/specialization needs its own theorem.
