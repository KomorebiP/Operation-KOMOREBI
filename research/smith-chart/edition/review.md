# Mathematical and editorial review

**Base:** `f8dbf83bb2a67139be7800768ce9a8be2109b28a`.  
**Review provenance:** self-review, 11 November 2026. No independent reviewer
or whole-manuscript formalization is claimed.

## Singular block criterion

**Claim:** for finite Hermitian `P >= 0`, the block `[P b; b* d]` is positive
semidefinite exactly when `b` annihilates `ker P` and
`d >= b* P-dagger b`.

**Verdict: proved as written.** The first implication follows by varying the
complex scalar on a null vector. Range/kernel orthogonality for a finite
Hermitian matrix then permits completing the square. Taking `u=-P-dagger b`
and `v=1` proves the remaining necessary inequality. The zero matrix is
included: its range condition forces `b=0`, after which `d>=0` is sufficient.
No inverse of a singular matrix is used.

## Complex prediction and two real packets

**Verdict: proved as written in the stated scalar domains.** At the nodes
`+/-1/2` with values equal to the nodes, the Pick matrix is all ones. Its
null vector forces the value at `i/3` to equal `i/3`. The response `F(t)=t`
proves feasibility. The wrong-value witness has exact quadratic value
`-435/4736`.

For real packets, the diagonal conditions, factored determinant, and lower
quadratic root give the stated closed feasible region. The proof explicitly
handles `p1=0`, `|p0|=1`, signs of both packets, and the discarded larger
quadratic root. The scalar interpolation bridge is Theorem 1, page 36 of
McCarthy's author-hosted 2003 article, checked directly. The constant
unimodular endpoints are supplied separately. There is no implication for
complex packet pairs or general noisy incomplete multiport synthesis.

The exact SymPy check and selected six-declaration Lean replay agree. Lean
proves the real zero-corner lemma, determinant identities, saturated case,
and two rational examples. It does not prove the full Hermitian or
Nevanlinna–Pick theorem, the square-root equivalence, or the complex example.

## Class 142

**Verdict: exact polynomial formulation verified; feasibility unresolved.**
The edge order, reactive placements, and target coefficients are bound to the
retained archive. The clearing factor is `s^3`: there are three inductive
admittances. Direct permutation expansions of the four-by-four grounded
matrix and its three-by-three port minor agree symbolically with the
125-tree and 50-forest formulas. The reactive union contains a spanning tree,
so strictly positive reactive parameters give a nonsingular matrix for real
`s>0`, even when some resistor conductances are zero. Vanishing of all 13
cross-multiplied coefficients is therefore equivalent to the rational target
identity for this placement. This is an encoding, not a feasibility witness
or an exclusion, and it does not cover other placements or node counts.

## Archived arbitrary-order argument

The displayed geometric-series identity, sharp equality point for either sign
of `a`, strict closed-disk convexity argument, noncanceling distinct poles,
and normalized passivity/pole-gap inequalities were reviewed. No additional
gap was found in those steps under `0<|a|<1`, `0<rho<1/2`, `N>=4`. The
degree-to-storage implication still uses the stated ideal independent-component
model. This pass adds no general-`N` Lean theorem or historical novelty claim.

## Language and graphics

The registered edits preserve all 1,668 archived mathematical spans and all
stable section identifiers. They clarify exposition and verification wording.
The vector drawings are illustrations; no plot establishes passivity,
minimality, exact cancellation, or infeasibility on its own. Figure 39's
resistor correction follows the exact nodal generator, and the mobile
versions rearrange the same component information.

The subsequent schematic redesign preserves the electrical connections in
figures 11, 18, 26, 27, 30 and 37. The cubic graph uses a planar embedding of
the same four-node, seven-component network. Figures 8 and 31 receive clearer
certificate and status layouts. Figure 8's original three collinear vertices
overlap the 1–3 edge with the 1–2 and 2–3 edges; the new triangle gives each
pair its own edge. Its three minors and full determinant are checked from the
archived rational kernel, using exact fractions and two determinant formulas.
This finite check covers the all-positive coupling branch only. No new
mathematical claim is inferred from the drawings.
