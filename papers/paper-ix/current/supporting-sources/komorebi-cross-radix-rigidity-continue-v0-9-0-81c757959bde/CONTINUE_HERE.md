# CONTINUE HERE — Certified v0.9.0 State

## 1. Authoritative checkpoint

v0.9.0 extends v0.8.0 without modifying any v0.8 source bytes.

- Lean `4.34.0-rc2`
- Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- strict gate `-DwarningAsError=true`
- source modules: 41
- theorem/lemma declarations: 287
- definitions/abbreviations/structures: 144
- new v0.9 theorem/lemma declarations: 28
- new v0.9 definitions/abbreviations/structures: 4
- placeholder scan: zero `sorry`, zero `admit`, zero custom `axiom`
- load-bearing v0.9 axiom audit: only `propext`, `Classical.choice`, `Quot.sound`

## 2. Exact affine Fourier transition closed

`CrossRadixExplicitShellJetClosure.lean` proves the exact DFT law for positive affine pullback `k ↦ m*k+r`:

`DFT(S_{m,r} Φ)(η) = Σ_{ξ : m ξ = η} χ(r ξ) • DFT(Φ)(ξ)`.

Nonunit `m` is allowed: aliases are summed rather than silently treated as a permutation.

For polynomial profiles, the Fourier-side polynomial is then transformed by the certified affine polynomial equivalence `X ↦ mX+r`.

The same module proves the coefficient/Hasse identity

`coeff_q(p(mX+r)) = hasseDeriv_q(p)(r) * m^q`,

and therefore affine substitution cannot create a nonzero jet `q` if all input jets `j ≥ q` vanish.

## 3. Sufficiency of explicit shell–jet closure closed

`CrossRadixShellJetTransition.lean` proves multiplication of a Fourier frequency can only move its divisor-shell index upward:

`gcd(T, ξ) ∣ gcd(T, m ξ)`.

Combining this with the Hasse-jet result gives the support transition theorem: any nonzero output coordinate has a source coordinate whose shell divides the output shell and whose jet is at least the output jet.

Hence for

`ExplicitShellJetClosure S = {(g',q) | ∃ (g,j)∈S, g ∣ g' ∧ q ≤ j}`

the corresponding mask is invariant under every positive affine section.

## 4. Necessity closed

`CrossRadixShellJetNecessity.lean` constructs pure Fourier/monomial atoms and proves:

- every divisor-upward shell transition can actually be realized by a positive multiplier;
- with zero translation, a pure atom survives at the target shell and same jet;
- translation by one creates every lower jet over `ℂ` because the required binomial coefficient is nonzero.

Therefore every positive-affine-invariant shell/jet mask is necessarily divisor-upward and jet-downward.

## 5. Explicit classification closed

`CrossRadixShellJetClassification.lean` combines sufficiency and necessity with the v0.8 abstract minimality theorem and proves

`InvariantShellJetSet hT H = ExplicitShellJetClosure (ActiveShellJetSet hT H)`.

Equivalently,

`(g',q) ∈ InvariantShellJetSet hT H`

iff there is an active `(g,j)` with `g ∣ g'` and `q ≤ j`.

The physical invariant shell/jet envelope is exactly the mask cut out by this explicit closure, and its finrank is exactly the number of Fourier-frequency/jet coordinates retained by that closure.

This specializes directly to `ProfileOrbitHull`.

## 6. Strongest next theorem

The remaining conceptual gap is between two distinct minimal objects:

1. `ProfileOrbitHull`: the absolute smallest positive-affine-invariant linear profile subspace;
2. the explicit invariant shell/jet zero-mask envelope just classified.

Characterize exactly when they are equal and when shell saturation is strictly larger. A useful route is to identify phase/cancellation or within-shell symmetry conditions under which each retained coordinate atom lies in the orbit hull.

A second target is an effective finite criterion for the active support of a profile orbit. After that, return to localized integral common lattices with Smith/Fitting/radix-local defect data.
