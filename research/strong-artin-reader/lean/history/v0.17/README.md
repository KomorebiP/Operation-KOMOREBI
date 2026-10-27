# Strong Artin Lean v0.17.0 — Local Pairing, Finite-Depth Linearization, and Generic Support — Checked

**Author:** Komorebi P.  
**Base checkpoint:** `Strong_Artin_Lean_v0.16.0_Jacobian_Chebotarev_Algebra_Checked.zip`  
**Base SHA-256:** `9bc4144969d6917d6cc40a761049b2576788694b5f3506b3272e24e144661530`  
**Status:** additive Lean checkpoint; full v0.15/v0.16/v0.17 direct source closure replayed with warnings as errors.

## Purpose

This checkpoint closes several internal bridges that previously separated the local Taylor--Wiles model, the finite auxiliary-set theorem, the Jacobian obstruction calculation, finite-depth linearized correction, and generic branch support.

It does **not** prove Strong Artin, Chebotarev, arithmetic local Tate duality, residual packet occurrence, an arithmetic automorphy-lifting theorem, or the existence and flatness of the required patched module.

## 1. Perfect local Frobenius pairing

For an invertible residual Frobenius matrix `A`, let

```text
C_A = ker (1 - Ad(A))
B_A = range (1 - Ad(A)).
```

Lean constructs an exact linear equivalence

```text
C_A ≃ₗ[k] Dual k (Matrix / B_A)
```

whose value is the trace pairing

```text
(P, [X]) |-> trace(P * X).
```

Consequences checked in Lean:

- every quotient functional has a unique Frobenius-centralizing matrix representative;
- every nonzero centralizing direction detects an unramified quotient class;
- every nonzero quotient class is detected by a centralizing direction;
- the linearized tame relation `Ad(A) P = q P` becomes exactly the centralizer condition at `q = 1`;
- the trace functional is the first derivative of the selected spectral determinant coordinate.

This is the complete finite-dimensional algebraic model. The comparison with continuous local Galois cohomology and the normalization of local Tate duality remain arithmetic inputs.

## 2. Auxiliary conditions complete the linearized Jacobian

For a Jacobian

```text
J : U -> W,
```

write

```text
obstructionDual J = ker J.dualMap.
```

The checkpoint proves:

1. every scalar functional on `obstructionDual J` is represented by evaluation at an equation-space column `w : W`;
2. the representing column is unique modulo `range J`;
3. the evaluation-column map has kernel exactly `range J`;
4. in finite dimension there is a canonical equivalence

```text
W / range J ≃ₗ[k] Dual k (obstructionDual J);
```

5. the exact number of scalar auxiliary conditions selected by v0.15 is

```text
finrank k (W / range J),
```

the coordinate-free codimension of the original Jacobian image;
6. the selected columns make the augmented Jacobian surjective;
7. every surjective auxiliary completion uses at least this many columns, so the selected set is cardinality-minimal.

## 3. Finite-depth linearized correction

A surjective augmented Jacobian solves every affine square-zero correction equation. Lean proves this for:

- one error term;
- arbitrary indexed finite families of error terms;
- state-dependent lift systems at every prescribed finite depth.

The last theorem is conditional on an explicit `step_valid` implication saying that solving the linearized equation produces a valid next state. It does not prove the nonlinear Taylor expansion, uniform arithmetic Jacobian hypothesis, or inverse-limit compatibility.

## 4. Split-prime transverse pipeline

If a localization map kills the canonical cyclic class `d`, every raw local functional factors canonically through

```text
H / span{k}{d}.
```

Lean then combines:

- split-prime raw one-class detection;
- a linear equivalence between the global transverse quotient and `obstructionDual J`;
- v0.15 adaptive auxiliary selection;
- finite-dimensional double duality;
- augmented-Jacobian surjectivity;
- repeated finite-depth linearized correction.

The capstone constructs the compatible equation-space columns automatically. No preselected columns or separate local-column compatibility hypothesis remains.

## 5. Residual occurrence to generic branch support

Let `pi` be a coefficient nonzerodivisor. Lean proves:

- a nonzero special fibre implies the integral module is nonzero;
- regularity of multiplication by `pi` makes localization at its powers injective;
- flatness implies this regularity;
- a nonzero class modulo `pi M` survives in the generic localization;
- a nonzero module over a finite split product ring has at least one supported coordinate branch;
- faithfulness supports every branch directly;
- a transitive equivariant automorphism propagates one supported branch to all branches.

The integrated support capstone shows that a flat module with nonzero special fibre, a split generic-fibre model, and transitive twist equivariance supports every generic branch.

This makes the proposed route

```text
residual Smith/Tate occurrence
  + relative flatness
  + split generic cyclic action
  -> all generic branches supported
```

formally valid at the module-theoretic level. Constructing those arithmetic inputs remains open.

## Verification

Pinned environment:

```text
Lean 4.34.0-rc2
mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06
-DwarningAsError=true
```

The verifier:

- checks the exact v0.16 base archive hash;
- recursively restores the direct v0.15 and v0.16 source dependencies;
- scans all v0.17 source for `sorry`, `admit`, custom `axiom`, and `opaque` declarations;
- freshly compiles the complete 33-module direct dependency closure;
- rejects any compiler failure or `sorryAx` occurrence;
- records source hashes and per-module exit codes.

The new v0.17 source contains:

- 20 modules;
- 80 theorem declarations;
- 23 definitions;
- 4 abbreviations;
- 0 `sorry`;
- 0 `admit`;
- 0 custom `axiom` declarations;
- 0 custom `opaque` declarations.

See `RESULT.json`, `verification/final_release_result.json`, and `verification/final_release_replay/logs/` for the authoritative packaged replay record.

## Replay

```bash
python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

## Boundary

The dominant remaining gaps are arithmetic:

1. realize the v0.16 finite conjugacy datum by Chebotarev outside the bad set;
2. identify the checked trace pairing with the exact normalized local Tate pairing and Taylor--Wiles local deformation quotient;
3. prove the global transverse Selmer--Jacobian comparison and realize the abstract columns as arithmetic local variables;
4. upgrade the checked linearized finite-depth theorem to the actual nonlinear deformation/Hecke equations;
5. establish residual occurrence of the finite-Satake descent in a determinant-bearing complex;
6. construct a flat or maximal Cohen--Macaulay relative patched module with the required generic splitting and twist equivariance;
7. complete ramified local attachment and the solvable Clifford recursion.
