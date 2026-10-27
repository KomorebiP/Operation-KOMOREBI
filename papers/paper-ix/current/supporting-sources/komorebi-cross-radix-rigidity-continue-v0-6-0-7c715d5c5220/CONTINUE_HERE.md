# CONTINUE HERE — Certified v0.6.0 State

## 1. Authoritative checkpoint

The authoritative persisted checkpoint is now **v0.6.0**, extending v0.5.0 without modifying any v0.5.0 source bytes.

- Lean: `4.34.0-rc2`
- Lean commit: `6a10ac8c22beadecabdbb0919c2b50214762f91d`
- Mathlib commit: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- strict gate: `-DwarningAsError=true`
- source modules: **29**
- theorem/lemma declarations: **209**
- definitions/abbreviations/structures: **110**
- new v0.6 theorem/lemma declarations: **13**
- new v0.6 definitions/abbreviations/structures: **10**
- placeholder scan: **0** `sorry`, **0** `admit`, **0** custom `axiom`
- load-bearing `#print axioms`: only `propext`, `Classical.choice`, `Quot.sound`

Treat `AUDIT.json`, the strict logs, and source files as authoritative if prose conflicts.

## 2. Rank/nullity block closed

`CrossRadixRankNullity.lean` introduces the finite degree-bounded polynomial fiber

`Polynomial.degreeLT ℂ (d+1)`

and the corresponding residue profile on `ZMod T`.

It proves:

- affine substitution by a nonzero slope preserves the degree bound and is a linear equivalence;
- the retained width support `{k : ZMod T // g | k.val}` is explicitly equivalent to `Fin (T/g)`;
- therefore that support has cardinality `T/g`;
- the degree-bounded polynomial fiber has finrank `d+1`;
- the full profile has finrank `T(d+1)`;
- the width projector has range finrank `(T/g)(d+1)`;
- DFT conjugation preserves that range dimension;
- composition with reversible affine bookkeeping has exactly the same range as the projector.

Consequently, for `g = gcd(T,m)` and `m>0`, Lean proves

`finrank Range(A_(m,r)) = (T/g) * (d+1)`

and

`finrank Ker(A_(m,r)) = (T - T/g) * (d+1)`.

The translation parameter `r` therefore does not enter the rank or nullity formula.

## 3. Characteristic-positive obstruction isolated

The same module proves a generic field theorem. If `[CharP K p]` and `p | m`, then

`f.comp (C m * X + C r) = C (f.eval r)`.

Thus the affine polynomial component collapses to evaluation when the coefficient characteristic divides the radix. Conversely, if `p ∤ m`, the scalar `(m : K)` is nonzero.

This isolates the failure mode rather than hiding it in a characteristic-zero assumption.

## 4. Proof boundary retained

The rank/nullity theorem is for the **saved projector-factorized affine section normal form**, now restricted to a finite degree-bounded profile space. It does not identify that normal form with any stronger unsaved root-aggregation operator. The theorem is proved over the finite complex/DFT realization. No theorem here claims a DFT/Reynolds realization over every characteristic-zero field.

## 5. Previously closed v0.5 layer remains closed

The Reynolds average, DFT mask, lcm projector/intersection laws, finite-family intersection, affine generalized inverse, raw-radix gcd reduction, and DFT/Möbius shell agreement remain exactly as certified in v0.5.0.

## 6. Strongest next theorem

Do **not** spend the next block re-proving rank/nullity. The next target is:

1. Define an explicit Lean structure or predicate containing exactly the downstream conclusion imported from Bell's generalized Cobham theorem. Bell itself remains external.
2. From that interface, prove a single finite common hull controls every positive radix simultaneously.
3. Then sharpen the coarse hull dimension using active spectral shell and polynomial-jet support.
4. Only after the field-level common hull is stable, return to localized integral lattices with Smith/Fitting/radix-local defect data.
