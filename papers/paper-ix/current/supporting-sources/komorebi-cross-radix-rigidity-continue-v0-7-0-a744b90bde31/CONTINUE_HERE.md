# CONTINUE HERE — Certified v0.7.0 State

## 1. Authoritative checkpoint

v0.7.0 extends v0.6.0 without modifying any v0.6 source bytes.

- Lean `4.34.0-rc2`
- Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- strict gate `-DwarningAsError=true`
- source modules: 31
- theorem/lemma declarations: 220
- definitions/abbreviations/structures: 120
- new v0.7 theorem/lemma declarations: 11
- new v0.7 definitions/abbreviations/structures: 10
- placeholder scan: zero `sorry`, zero `admit`, zero custom `axiom`
- load-bearing new theorem axiom audit: only `propext`, `Classical.choice`, `Quot.sound`

## 2. Bell-downstream interface closed

`BellDownstreamInterface a` stores exactly the normalized tail data consumed by the internal theory: `N,T,d`, `T>0`, a bounded quasi-polynomial residue profile, and agreement from `N` onward.

It is not Bell's theorem. See `BELL_EXTERNAL_INTERFACE.md`.

## 3. Uniform common hull closed

`CrossRadixBellCommonHull.lean` defines a fixed finite coordinate source

`(Fin N → ℂ) × DegreeBoundedProfile T d`

with dimension `N + T*(d+1)`, and a linear synthesis map into sequences. Its range is `CommonHull N T d`.

Lean proves every positive affine section and every positive-radix depth/address section of a sequence satisfying the interface lies in this same hull. The hull does not depend on the radix, depth, or address.

Lean also proves the stronger structural statement that `CommonHull N T d` is closed under every positive affine section.

## 4. Previous v0.6 block remains closed

The exact rank/nullity formula remains certified for the finite complex projector-factorized affine normal form:

`rank = (T/gcd(T,m))*(d+1)`,

`nullity = (T-T/gcd(T,m))*(d+1)`.

## 5. Strongest next theorem

1. Define active spectral-shell support for a common-hull element/profile.
2. Couple shell support to polynomial jet depth.
3. Prove the section-closure of the shell-jet support closure.
4. Use it to replace the coarse `N + T(d+1)` bound by a canonical/minimal active shell-jet bound where justified.
5. Only after the field-level minimal hull is stable, return to localized integral lattices with Smith/Fitting/radix-local defect data.
