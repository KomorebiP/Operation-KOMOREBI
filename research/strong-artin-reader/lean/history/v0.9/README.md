# Strong Artin Lean v0.9.0 — Checked

This release continues the finite exact Lean normalization of the Strong Artin cyclic-descent papers.
It does **not** claim Strong Artin.

## Verification

- Lean/Lake: `leanprover/lean4:v4.34.0-rc2`
- Lean commit: `6a10ac8c22beadecabdbb0919c2b50214762f91d`
- mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- full source checked with warnings as errors: **RC = 0**
- theorem declarations: **160**
- lemma declarations: **1**
- definitions/abbreviations: **67**
- structures: **1**
- `sorry`: **0**
- `admit`: **0**
- custom `axiom` declarations: **0**

Representative `#print axioms` checks use only the ordinary Lean/Mathlib foundations
`propext`, `Classical.choice`, and `Quot.sound` (some theorems use a subset).

## New in v0.9

### Prime-field characteristic-polynomial propagation

Lean now proves that for a finite-dimensional endomorphism over `ZMod p`,

`charpoly (f^p) = charpoly f`.

Using this and the quotient relation `G/H ~= C_p`, Lean proves:

> If two `F_p` representations have equivalent restrictions to a normal subgroup `H`,
> then their characteristic polynomials agree on **every** element of `G`.

The proof is exact:

1. `g^p` lies in `H` because the quotient has exponent `p`.
2. restriction equivalence gives conjugacy/equal characteristic polynomials at `g^p`;
3. representation multiplicativity gives `rho(g^p)=rho(g)^p` and similarly for `sigma`;
4. Mathlib's finite-field characteristic-polynomial theorem cancels the `p`th power.

No eigenvalue enumeration or Jordan-form assumption is used.

### Machine-visible residual-collapse boundary

The source now defines `SemisimpleCharpolyRigidityFp`, the precise semisimple
Brauer--Nesbitt property still needed to turn the preceding characteristic-polynomial
equality into equivalence of arbitrary semisimple representations.

It also proves `semisimple_residual_collapse_of_charpoly_rigidity`: supplying that
property immediately yields the manuscript's semisimple quotient-prime residual collapse.

`SemisimpleCharpolyRigidityFp` is a **property/hypothesis interface**, not an axiom,
and no instance asserting it is installed.

## Major previously checked blocks retained

- quotient-character extension torsor, including uniqueness on isomorphism classes;
- representation-level determinant selector for `p ∤ dim`;
- end-to-end Galois degree-one trace separator separating all `p` twists;
- cyclic spectrum rotation/alignment/Fourier criteria;
- coefficient rotation and characteristic-polynomial separator;
- irreducible and semisimple `C_p` collapse in characteristic `p`;
- moving induced-block twist invariance;
- modular Clifford semisimplicity of irreducible restrictions;
- nonzero restricted intertwiner rigidity for irreducible ambient modules;
- finite trace-image bound `|Gamma| <= t^(n^2)`;
- bounded cyclotomic polynomial alphabets;
- Dedekind separating-prime existence;
- quotient-prime root-power/Frobenius polynomial cancellation;
- post-Brauer large-residual recovery funnel;
- finite-index image theorem used in local Artin descent.

## Remaining boundary

The most important remaining internal finite representation-theory theorem is:

> **Semisimple Brauer--Nesbitt over the residual field:** semisimple finite-group
> representations with identical characteristic polynomials on all group elements are equivalent.

The pinned mathlib revision does not expose such a theorem. v0.9 does not introduce it as an axiom.

External/global inputs remain external: cross-characteristic Brauer lifting, Chebotarev,
cyclic base change, automorphic induction, local Langlands, unrestricted Galois realization,
automorphy lifting, global attachment, and Strong Artin itself.
