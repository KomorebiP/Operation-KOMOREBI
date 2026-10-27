# Strong Artin Lean v0.16.0 — Jacobian Completion and Chebotarev-Class Algebra — Checked

**Author:** Komorebi P.  
**Base checkpoint:** `Strong_Artin_Lean_v0.15.0_Adaptive_Auxiliary_Set_Checked.zip`  
**Base SHA-256:** `77b0988d26f5a61d02028339697942e3863457074a1682124c7a4b538817ab4e`  
**Status:** additive Lean checkpoint; fresh replay with warnings treated as errors.

## Purpose

v0.14 constructed an abstract projector-detected pre-Chebotarev element. v0.15 proved that a one-prime detection interface selects an exact finite auxiliary set. v0.16 closes three internal bridges between those results and a future arithmetic Taylor--Wiles argument:

1. **dual detection completes the Jacobian:** the columns selected by v0.15 make the augmented linearized deformation map surjective;
2. **finite quotient and conjugacy packaging:** cocycles form affine semidirect-product quotients, prime-power splitting labels preserve every prime-to-characteristic residual class, and projector detection survives passage to the whole conjugacy class;
3. **local linear interface:** a commuting spectral projector kills Frobenius coboundaries, hence defines a functional on the local cocycle quotient, and this functional is exactly the first derivative of a block-determinant coordinate.

The checkpoint does **not** invoke Chebotarev, prove a local Tate-duality normalization, produce residual automorphic occurrence, prove patching, or prove Strong Artin.

## Main results

### 1. Auxiliary columns complete the obstruction Jacobian

For a linear map

```text
J : U →ₗ[k] W
```

define the dual obstruction space

```text
obstructionDual J = ker J.dualMap.
```

For auxiliary columns `column : Aux → W`, the associated scalar detector is

```text
φ ↦ φ (column a).
```

If selected columns jointly detect every nonzero element of `obstructionDual J`, Lean proves that

```text
augmentedMap J column Q : U × (Q → k) →ₗ[k] W
```

is surjective.

The v0.15 capstone then gives:

```text
exists_exact_admissible_columns_making_augmentedMap_surjective
```

If every nonzero dual obstruction is detected by one admissible auxiliary column, there is a set `Q` with

```text
Q.card = finrank k (obstructionDual J)
```

all labels admissible, and the augmented Jacobian surjective.

### 2. Prime-power splitting labels preserve the residual spectrum

Let `q : G →* Γ` be surjective and `a : G →* P`. If `Γ` and `P` have coprime finite orders, Lean proves

```text
a.ker.map q = ⊤.
```

In particular, if `P` is a finite `p`-group and `p ∤ Nat.card Γ`, every `γ : Γ` has a lift `g : G` satisfying

```text
q g = γ

a g = 1.
```

Thus all splitting-in-`E`, cyclotomic-level, and other prime-power labels may be imposed simultaneously without losing any residual Frobenius class, in the stated prime-to-`p` regime.

### 3. Cocycles define finite affine quotients

For an additive `Γ`-module `V`, Lean constructs the affine semidirect product

```text
AffineExtension Γ V
```

with multiplication

```text
(v,g) * (w,h) = (v + g • w, g*h).
```

A normalized cocycle is packaged as a homomorphism

```text
G →* AffineExtension Γ V.
```

Together with a finite cyclotomic/splitting label this gives one homomorphism into a finite product. The actual quotient is defined as its range, is finite, and the range-restricted map is surjective by construction.

### 4. The detector is stable on a finite conjugacy class

For a matrix-valued conjugation cocycle, Lean proves the exact affine formula

```text
f(h*g*h⁻¹)
  = Ad(q h)(f g)
    + (f h - Ad(q(h*g*h⁻¹))(f h)).
```

If `P` commutes with the residual matrix of `g`, the second term is a Frobenius coboundary and has zero `P`-trace. After transporting `P` by `q h`,

```text
traceProbe (Ad(q h) P) (f(h*g*h⁻¹)) = traceProbe P (f g).
```

The indexed capstone first chooses an actual projector detecting a deep common-kernel cocycle value, uses the residual element attached to that same projector, lifts it through every finite `p`-group label, applies the two-candidate selector, and proves nonvanishing on the full conjugacy class.

### 5. Local Frobenius quotient and determinant differential

For an invertible residual Frobenius matrix `A`, define

```text
frobeniusCoboundaryMap A (Y) = Y - A*Y*A⁻¹.
```

If `P` commutes with `A`, Lean proves

```text
range (frobeniusCoboundaryMap A) ≤ ker (traceProbeLinear P).
```

Therefore `trace(PX)` descends to

```text
Matrix n n k ⧸ range (1 - Ad A).
```

It is exactly the linear coefficient, equivalently the derivative at zero, of

```text
det(1 + T * (P*X)).
```

This is the algebraic cotangent calculation needed by the intended local Taylor--Wiles condition. The theorem deliberately does not identify it with the fully normalized local Tate pairing.

## Verification

The verifier checks:

- Lean `4.34.0-rc2`;
- mathlib commit `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`;
- exact v0.15 base archive hash;
- absence of `sorry`, `admit`, and custom `axiom` declarations in active v0.16 sources;
- fresh compilation of the three direct v0.15 source dependencies and all ten v0.16 modules with `-DwarningAsError=true`;
- no `sorryAx` in compiler/axiom output.

Run from the extracted checkpoint:

```bash
python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

## Exact boundary

Still open:

1. instantiate the finite affine quotient with the actual continuous Galois cocycle and finite extension used for Chebotarev;
2. apply Chebotarev outside a prescribed bad set and decode splitting and norm congruences;
3. identify the quotient trace functional with the exact local Tate-duality quotient and Taylor--Wiles deformation condition;
4. prove the arithmetic local columns are the columns of the global deformation/Hecke Jacobian;
5. produce residual occurrence of the finite-Satake descent in determinant-bearing cohomology;
6. construct relative patching/full support or a finite-depth carrier through the explicit threshold;
7. prove ramified local attachment and complete the solvable Clifford recursion;
8. address non-solvable finite images.
