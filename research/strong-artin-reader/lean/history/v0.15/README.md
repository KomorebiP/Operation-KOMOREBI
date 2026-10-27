# Strong Artin Lean v0.15.0 — Adaptive Relative Auxiliary-Set Selection — Checked

**Author:** Komorebi P.  
**Base checkpoint:** `Strong_Artin_Lean_v0.14.0_Cyclotomic_Depth_PreChebotarev_Checked.zip`  
**Base SHA-256:** `fba7ddb9c2dfd2a13351a36fccd9d274e26108ca32952f955a5e79bae2331868`  
**Status:** additive Lean checkpoint; all new modules freshly replayed with warnings as errors.

## Purpose

v0.14 constructs, under explicit residual/cohomological hypotheses, a pre-Chebotarev element detecting one nonzero transverse class. v0.15 closes the finite-dimensional iteration that follows once arithmetic Chebotarev realization and the local Taylor--Wiles pairing provide a scalar local functional for every nonzero active class.

The active space after selecting auxiliary labels `Q` is formalized as

```text
selectedKernel probe Q = {x | every selected local functional kills x}.
```

This exactly models successive intersections of transverse dual-Selmer kernels in the scalar local-condition abstraction.

## Main results

### Fresh strict drop

If the current selected kernel is nonzero and every nonzero vector is detected by some probe, then there is a probe label not already in `Q` such that

```text
selectedKernel probe (insert i Q) < selectedKernel probe Q.
```

The finite-dimensional version gives strict finrank decrease.

### Adaptive termination from an existing set

Starting with any finite `Q₀`, one can extend it to `Q` satisfying

```text
Q₀ ⊆ Q
Q.card ≤ Q₀.card + finrank k (selectedKernel probe Q₀)
selectedKernel probe Q = ⊥.
```

Thus no more than the current active dimension many new scalar auxiliary conditions are required.

### Exact cardinality and injective localization

From the empty set, one can select `Q` with

```text
Q.card = finrank k V
Function.Injective (evaluationMap probe Q).
```

The equality is exact: injectivity gives the lower bound `finrank k V ≤ Q.card`, while adaptive termination gives the upper bound.

### Arithmetic-constrained selection

A predicate `Good : Aux → Prop` may encode fixed arithmetic constraints such as:

- exclusion of a prescribed bad set;
- unramifiedness;
- `q_v ≡ 1 mod p^N`;
- a residual eigenvalue/projector condition.

If every nonzero active class is detected by some good label, v0.15 selects only good labels, preserves a pre-existing good set, and gives the same dimension bound.

### Relative Taylor--Wiles interface

`OnePrimeSelectionInterface` isolates the exact remaining input:

```text
admissible : Aux → Prop
localFunctional : Aux → Dual k H
detects : every nonzero h is detected by an admissible auxiliary label.
```

The capstone theorem

```text
exists_relative_TaylorWiles_set_exact
```

produces exactly `finrank k H` admissible labels, zero final selected kernel, and an injective simultaneous local-evaluation map.

## Boundary

This checkpoint proves the **abstract finite selection/iteration theorem**. It does not prove that number-field primes instantiate `OnePrimeSelectionInterface`.

Still required:

1. finite Galois quotient packaging of the v0.14 selected element;
2. Chebotarev realization outside the bad set;
3. identification of the centered projector trace with the actual local Tate-duality quotient;
4. verification that the resulting local functional is linear on the relevant dual-Selmer space;
5. relative patching or finite-depth carrier construction;
6. residual packet occurrence in determinant-bearing cohomology;
7. ramified local attachment and recursive solvable completion.

Accordingly, v0.15 does **not** prove a Taylor--Wiles theorem, automorphy lifting, solvable Strong Artin, or unrestricted Strong Artin.

## Verification

The verifier checks:

- Lean `4.34.0-rc2`;
- mathlib commit `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`;
- exact v0.14 base archive hash;
- absence of `sorry`, `admit`, and custom `axiom` declarations;
- fresh compilation of all three additive modules with warnings as errors;
- axiom output free of `sorryAx`.

Run:

```bash
python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
```
