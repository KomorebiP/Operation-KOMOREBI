# Strong Artin Lean v0.22.0 — Presentation–Cotangent Obstruction Exact Sequence — Checked

**Author:** Komorebi P.  
**Base checkpoint:** `Strong_Artin_Lean_v0.21.0_Completed_Formal_Presentation_Checked.zip`  
**Base SHA-256:** `97d7ae4b8bf0804af7eea942cc11d0a10b7587dcea4223cd757947fba28b8d51`  
**Status:** additive Lean checkpoint; all six new modules freshly replayed with warnings as errors.

## Purpose

v0.21 closes the abstract route from a one-prime auxiliary interface and a finite completed presentation to an exact nonlinear finite-level point. Its arithmetic instantiation still requires a comparison between a global Selmer obstruction space and the dual obstruction extracted from a chosen presentation Jacobian.

v0.22 identifies a necessary correction to that comparison. For a presentation with relation differential

```text
relationDifferentialMap : (relations →₀ S) →ₗ[S] (generators →₀ S),
```

the raw kernel of the displayed transpose Jacobian is not automatically intrinsic. It maps canonically and surjectively to the first homology of Mathlib's naive cotangent complex, and the kernel of this map is exactly the redundancy among the selected relation generators.

The checked sequence is

```text
relation syzygies
  → raw transpose-Jacobian kernel
  → cotangent H1
  → 0.
```

Under conormal independence of the chosen relations, the middle arrow is a linear equivalence.

## Main results

### 1. Jacobian coordinates

For a presentation `P`, the relation differential map is proved to be the finite-support transpose action of the evaluated Jacobian matrix:

```text
relationDifferentialMap P x i
  = x.sum (fun r a => a * relationJacobianMatrix P r i).
```

Consequently, membership in the raw presentation obstruction is exactly annihilation by every column of the displayed transpose Jacobian.

### 2. Canonical surjection to intrinsic cotangent H1

The module

```text
presentationObstructionDual P
```

is the kernel of the relation differential map. The canonical conormal map induces

```text
toH1Cotangent P : presentationObstructionDual P →ₗ[S] P.toExtension.H1Cotangent.
```

Lean proves this map is surjective.

### 3. Exact syzygy kernel

Define

```text
relationSyzygies P = ker (toH1Cotangent P).
```

Lean proves exactness:

```text
Function.Exact
  (Submodule.subtype (relationSyzygies P))
  (toH1Cotangent P).
```

Thus relation redundancy is the complete difference between the raw presentation obstruction and intrinsic cotangent H1.

### 4. Independence criterion

Lean proves the equivalence

```text
Function.Injective (toH1Cotangent P)
  ↔ Function.Injective (Algebra.Presentation.differentials.hom₁ P).
```

Equivalently,

```text
relationSyzygies P = ⊥
  ↔ the chosen relation generators are independent in the conormal module.
```

Under this hypothesis, the raw presentation obstruction is linearly equivalent to cotangent H1.

### 5. Rank correction

With the appropriate `HasRankNullity` hypothesis and universe lifts, Lean proves

```text
rank(raw presentation obstruction)
  = rank(cotangent H1) + rank(relation syzygies).
```

Therefore a redundant presentation overcounts intrinsic obstruction rank by exactly the syzygy rank.

### 6. Negative control

Two distinct relation-basis vectors having the same conormal image force a nonzero relation syzygy. In that case the canonical map from the raw Jacobian kernel to cotangent H1 cannot be injective.

### 7. Selmer comparison interface

`SelmerPresentationComparison.Datum` records an arithmetic equivalence

```text
P.toExtension.H1Cotangent ≃ₗ[S] SelmerObstruction.
```

From this datum Lean constructs a canonical surjection

```text
raw presentation obstruction → Selmer obstruction
```

whose kernel is exactly `relationSyzygies P`. It becomes an equivalence precisely under conormal independence.

A further negative theorem proves that genuine Selmer functionals annihilate every relation syzygy. Hence, if the syzygy space is nonzero, no family of arithmetic Selmer functionals can detect every nonzero vector in the raw presentation kernel.

## Consequence for the Strong Artin program

The arithmetic Selmer–Jacobian comparison must target the intrinsic cotangent obstruction, not an arbitrary raw matrix kernel. There are now two valid routes:

1. prove that the selected arithmetic relations are independent in the conormal module, so that the raw kernel is intrinsic; or
2. quotient relation syzygies before applying the Taylor–Wiles auxiliary-selection machinery.

This is a correction and sharpening of the v0.17–v0.21 arithmetic interface. It does not invalidate their abstract linear-algebra and lifting theorems; it specifies the exact obstruction space to which they must be applied.

## Boundary

v0.22 does **not** construct:

- the actual Strong Artin Selmer-to-cotangent-H1 equivalence;
- conormal independence for the arithmetic deformation/Hecke presentation;
- a quotient-level Taylor–Wiles interface when syzygies are present;
- continuous local Galois cohomology or local Tate-pairing comparison;
- Chebotarev realization;
- a patchable determinant-bearing automorphic carrier;
- relative patching, ramified attachment, solvable Strong Artin, or unrestricted Strong Artin.

## Verification

Pinned environment:

```text
Lean 4.34.0-rc2
mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06
-DwarningAsError=true
```

Fresh replay results:

- additive modules: **6**;
- theorem declarations: **29**;
- definitions: **8**;
- abbreviations: **1**;
- structures: **1**;
- source lines: **704**;
- `sorry`: **0**;
- `admit`: **0**;
- custom `axiom`: **0**;
- custom `opaque`: **0**;
- every compiler exit code: **0**;
- `sorryAx`: absent.

Representative axiom audits contain only ordinary Lean/Mathlib foundations:

```text
propext
Classical.choice
Quot.sound
```

## Replay

```bash
python3 verify.py \
  --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
```
