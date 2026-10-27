# Euler Lean XIII: collision coefficients, critical invariants, and certified polynomial consequences

**Operation Komorebi — 3 October 2026 — first compiled Lean tranche**

## Status

This release contains 77 named theorem/lemma declarations across eight Lean
modules. All compile with Lean 4.34.0-rc2 and the pinned mathlib cache. A transitive
axiom audit covers every declaration. No `sorryAx`, custom mathematical axiom,
or native-evaluation proof axiom appears in that audit.

The standard axiom union is `propext`, `Classical.choice`, and `Quot.sound`.
This means kernel checking in the ordinary Lean/mathlib foundational setting,
not an axiom-free foundational development. The proof statements retain their
hypotheses explicitly. A clean axiom report does not remove those hypotheses.

This is NOT an end-to-end formal proof of universal Euler simplicity, of the
terminal-514 infinite-series atlas, or of the previous digit-sum/degree coverage.
The current exact scope and remaining bridges are below. No historical-priority
claim is made for the generic algebra, calculus, or Hensel arguments.

## 1. Actual mathematical types

`D` abbreviates mathlib's `ℤ_[2]`, the actual 2-adic integers. `red`, `red4`, and
`red8` are mathlib ring homomorphisms to `ZMod 2`, `ZMod 4`, and `ZMod 8`.
The coefficient results use `PowerSeries D`; the polynomial lifting results use
`Polynomial D`. Analytic chart theorems use genuine `deriv` over a nontrivially
normed field, and apply in particular to `ℚ_[2]`.

We did not define a mock field or replace differentiation by a discrete step.
`LastOdd f d` is deliberately a coefficient predicate: coefficient d reduces to
one and every higher coefficient reduces to zero. It is not defined to mean
"all roots simple" or "Weierstrass preparation exists."

## 2. The one- and two-neighbor coefficient proofs

The exact formal ratio constructions are

    oneRatio r ε e = r (1 + 2 ε X) e(4X)
    twoRatio r e   = r (1 - 4 X²) e(4X).

The half-core identity is expressed without division:

    2 H = X(1+R) - z.

Here r is odd, ε is odd in the one-neighbor case, and e has constant coefficient
one. Using an arbitrary integral formal e records the full weighted infinite
coefficient tail, not a finite truncation of it.

Lean proves the exact coefficient formulas, for every natural n:

    [X^(n+2)] H = 4^n r (2 e_(n+1) + ε e_n)              (one neighbor)
    [X^(n+3)] H = 2·4^n r (4 e_(n+2) - e_n)              (two neighbors).

Consequences:

- One neighbor: `LastOdd H 2`.
- Two neighbors: either `LastOdd H 0`, `LastOdd H 1`, or there is an exact integral
  half F with `2F=H` and `LastOdd F 3`.
- Multiplication by an integral formal series whose entire reduction is one
  preserves this last-odd index.

The two-neighbor theorem constructs the extra integral half when all the
coefficients are even. It does not assume the desired conclusion as an input.

**Bridge still needed:** the Euler-defined ratio must be shown in Lean to have
this exact nearest-neighbor factorization, including the normalized unit and
source bounds. The manuscript supplies a mathematical proof; the present Lean
module formalizes the downstream algebraic coefficient theorem, not that whole
geometric derivation.

**Preparation still needed:** the restricted-series preparation theorem on the
closed dyadic unit disc must be connected to `LastOdd`. The available formal
power-series Weierstrass theorem over a local ring uses the *first* residue
coefficient/order, and is not silently substituted for the required restricted
last-coefficient statement. No whole-disc root-count claim is extracted from
`LastOdd` alone in this release.

## 3. Refinement budget

For a translated Hasse series A and normalized child F, the exact child identity
is

    2^c F(Z) = A(2Z).

If coefficient m of A is odd, Lean proves `c ≤ m`. Every coefficient of F above
m is even. If `LastOdd F d`, then `d ≤ m`.

Combining two such exact child identities with the explicit parent multiplicity
budget `m₀+m₁ ≤ d` yields `d₀+d₁ ≤ d` for the child degrees.

**Boundary:** this is the coefficientwise refinement step. The full analytic
translation construction, residue multiplicity accounting at both children, and
the infinite-path/termination theorem from the manuscript have not all been
formalized here. In particular, the total-parent budget is an explicit argument,
not a new theorem about every unconstructed refinement tree.

## 4. Genuine analytic chart reductions

`CriticalZero f x` means exactly

    f x = 0 ∧ deriv f x = 0.

Lean proves that this property is preserved by multiplication by a differentiable
nonzero gauge, and by a differentiable coordinate with nonzero derivative.
For a square chart,

    f(x) = u(x)(φ(x)² - ξ),

with those nonvanishing conditions,

    CriticalZero f x ↔ ξ=0 ∧ φ(x)=0.

Thus a nonzero exact scalar excludes a critical zero in that chart.
For a derivative-square representation

    f'(x) = A + 3u φ(x)²,

nonsquareness of `-A/(3u)` excludes critical points. When A=0 and φ has its only
zero at ρ, a critical zero is exactly `x=ρ` and `f(ρ)=0`.

**Boundary:** these are implications under exact chart/derivative identities.
Lean has not constructed the analytic square coordinate for every Euler residual
or proved that the exact Euler scalar is nonzero. The existence of those charts
cannot be inferred merely from a successful compilation of the implications.

## 5. Exact quadratic and cubic discriminant reduction

Over any characteristic-zero field, with nonzero leading coefficient, the new
algebraic lemmas prove both directions:

    ∃x, ax²+bx+c=0 and 2ax+b=0
      ↔ b²-4ac=0,

    ∃x, ux³+Ax+C=0 and 3ux²+A=0
      ↔ 4A³+27uC²=0.

The latter quantity is the reduced discriminant obstruction; the full cubic
discriminant is `-u(4A³+27uC²)`. If A is nonzero, a critical zero on the
vanishing locus is `-3C/(2A)`. If A=0, then C=0 and the center is zero.
Triple-jet vanishing is exactly `x=A=C=0` in these depressed coordinates.

The derivative formulas are also proved with `HasDerivAt`, connecting these
polynomial expressions to actual analytic derivatives. Nonzero discriminant
excludes a critical zero after an independently supplied invertible analytic
chart and nonzero gauge.

**Boundary:** these exact polynomial discriminants are not claimed to be the
same expressions as those obtained by discarding the higher terms of a general
restricted cubic. An exact polynomial preparation or an exact chart is required.
The v12 derivative-square normal form is distinct from a cubic-polynomial chart.
Neither family-wise nonvanishing nor integral existence of the field-theoretic
critical point follows without its additional hypotheses.

## 6. Terminal-shaped residue certificates, checked by the kernel

The finite proofs use `decide +kernel`, not native evaluation.

The terminal-161 model

    4+(2+6t)y+6y²+y³  modulo 8

has no simultaneous zero of its zeroth, first, and second Hasse jets. This is
proved universally in `t,y : ZMod 8`. The binary model `y³+y` receives the same
triple-jet exclusion.

A ring-homomorphism soundness theorem transfers such residue facts to every
polynomial over `ℤ_[2]` having the corresponding coefficient reduction.
The module also proves

    three Hasse jets vanish at x ↔ (X-C x)^3 divides p.

Thus the no-triple conclusion is an actual polynomial multiplicity statement,
not a renamed Boolean certificate.

The terminal-514 mod-4 models are checked similarly. For odd t they have no root
modulo four, so every dyadic polynomial with that coefficient reduction is
root-free. For a polynomial reducing to `X²+X` modulo two, the Hensel module proves
that it has exactly two dyadic roots, one in each residue class, and both have
nonzero polynomial derivative. This quantifies over arbitrary higher integral
polynomial coefficients, not just the displayed quadratic.

**Critical boundary:** this does not derive the residue congruences from the
infinite Euler source. Nor does polynomial soundness alone prove analytic
residue soundness for every restricted series. Those must be connected formally.
The resulting residue-shape theorems are ready for that bridge; they are not an
end-to-end formalization of either complete Euler family.

## 7. Negative controls preserve the research boundary

The exact finite skeleton is defined recursively as

    P_(j+1)=P_j (X-j)(2X-2j-1).

Lean checks the synthetic, non-Euler example

    P_5 + 4(-162+117X-18X²)

is divisible by `(X-2)^3` and is NOT divisible by `(X-2)^4`. The quotient at 2 is
1025. Its lower reduction really is the simple residue X.

The synthetic double-root factorization of `P_4+30(X-1)` is also checked, with
quadratic quotient value 47 at 1. Finite residue indistinguishability and an
analytic cubic critical-zero control are retained.

These checks do not refute any claimed Euler-family theorem. They show why a
proof of generic collision structure cannot substitute for Euler-specific
critical-value nonvanishing.

## 8. What is actually left

The formalization queue has four distinct items:

1. Define the Euler source/kernel/tail over the selected p-adic analytic types,
   prove convergence, and prove the normalization and nearest-neighbor identities.
2. Connect coefficientwise error bounds, polynomial residue certificates, and
   restricted analytic evaluation/Hasse jets. Prove the full-disc preparation or
   use a direct analytic Hensel construction without an invalid formal-unit step.
3. Derive the exact Euler chart or prepared polynomial from those constructions,
   with all scaling and derivative hypotheses discharged.
4. Prove or otherwise settle exact nonvanishing of the surviving Euler critical
   scalars for the open terminal-129 and terminal-161 multiplier families.

Items 1–3 are formal bridges for mathematical arguments in the existing record.
Item 4 is still a mathematical research obstruction. Kernel checking does not
supply that missing nonvanishing argument automatically.

The prior consecutive terminal-degree and binary-complexity bounds remain
manuscript/computer-assisted results, not newly established end-to-end Lean
corollaries. No numeric coverage bound is increased in this release.

## 9. Executed checking and failures

The v12 input integrity checker reported 1039 matching entries. No v12 scientific
atlas generator or scientific checker is claimed to have been rerun in this turn.

The portable Lean kit was restored from the five visible Compact archives.
Its version and the pinned mathlib manifest were checked. Two clean project
compilations are retained, each using a fresh output directory and one worker.
Warnings were treated as errors. Every indexed theorem/lemma was included in a
transitive axiom audit; the checker rejects any unapproved axiom.

During proof development, normal compiler errors exposed wrong theorem names,
rewrite orientation/type mismatches, and linter issues. They were corrected and
all affected files were recompiled. The first preliminary declaration-index
script also mistook two words inside comments for theorem names; the corrected
nested-comment-aware index contains 77 actual declarations and the complete
axiom audit passes. These failed diagnostics are retained separately from the
clean replay evidence. They are not counted as mathematical counterexamples.

The ordinary local-ring formal-power-series preparation theorem was inspected
and deliberately not used as a substitute for a restricted unit-disc theorem.
This leaves an explicit bridge rather than introducing a false semantic shortcut.

No custom mathematical axioms, unfinished proofs, or native-evaluation proof
axioms were added. The full environment and the multi-gigabyte runtime are not
included in the deliverable.

## 10. Provenance and attribution

The mathematical target is the unchanged v12 proof note in `reference/`.
`PROVENANCE.json` records its source archive hash and integrity replay.
`THEOREM_INDEX.json` and `PROOF_BOUNDARY.json` record the current formal scope.
The new Lean source is the evidence for the statements marked compiled.

Mathlib supplies actual p-adic rings, polynomial/Hasse calculus, analytic
Deriv APIs, and the polynomial Hensel theorem. The official Lean reference
explains the transitive axiom audit:
https://lean-lang.org/doc/reference/latest/Axioms/ .
