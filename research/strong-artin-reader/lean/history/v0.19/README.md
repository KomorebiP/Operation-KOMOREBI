# Strong Artin Lean v0.19.0 — Relative Nonlinear Hensel Lifting — Checked

**Author:** Komorebi P.  
**Base checkpoint:** `Strong_Artin_Lean_v0.18.0_Cyclic_H1_Tate_Normalization_Checked.zip`  
**Base SHA-256:** `70301451298b50e554c8ef517dd7b013f82810681711e0f3d032ea59019cd8bf`  
**Status:** additive Lean checkpoint; all seven new modules freshly replayed with warnings as errors.

## Purpose

v0.17 completed finite-depth **linearized** correction once Taylor--Wiles columns make the augmented Jacobian surjective. The remaining abstract lifting question was whether this can produce genuine solutions of nonlinear equations over a finite nilpotent coefficient thickening.

v0.19 proves such a theorem under explicit hypotheses. It separates three requirements:

1. a lifted approximate right inverse whose error is divisible by a nilpotent parameter;
2. stability of that approximate inverse throughout the residual fibre; and
3. a first-order Taylor remainder which gains at least one filtration power.

Under these hypotheses, a solution modulo the parameter lifts through every depth and becomes an exact solution when the parameter is nilpotent.

## Main fixed-Jacobian theorem

Let `R` be a commutative ring, `pi : R`, `F : X -> W`, and `J : X ->ₗ[R] W`. Suppose there are maps

```text
approxRightInv : W ->ₗ[R] X
E              : Module.End R W
```

such that

```text
J.comp approxRightInv = LinearMap.id + pi • E.
```

If `pi` is nilpotent, Lean proves that the nilpotent endomorphism error can be inverted in the endomorphism ring and produces an exact right inverse

```text
rightInv : W ->ₗ[R] X
J.comp rightInv = LinearMap.id.
```

Assume also that corrections `delta` divisible by `pi^n`, for `n >= 1`, satisfy

```text
F (x + delta) - F x - J delta ∈ pi^(n+1) W.
```

Then every solution modulo `pi` produces a compatible tower

```text
x 0, x 1, x 2, ...
```

with

```text
F (x n) ∈ pi^(n+1) W
x (n+1) - x n ∈ pi^(n+1) X.
```

If `pi^(N) = 0`, the tower reaches an exact root `F x = 0`.

The principal capstone is

```text
Komorebi.StrongArtin.RelativeNonlinearHenselCapstone.
  exists_exact_solution_of_nilpotent_approx_rightInverse
```

## State-dependent Jacobian theorem

The stronger theorem allows a Jacobian

```text
D : X -> (X ->ₗ[R] W)
```

which changes with the current point. One fixed lifted residual right inverse may be used provided that for every point `x` in the residual fibre of `x₀`,

```text
(D x).comp approxRightInv = LinearMap.id + pi • E x.
```

If the state-dependent Taylor remainder gains one power, Lean constructs a compatible tower staying in the same residual fibre and an exact root when `pi` is nilpotent:

```text
Komorebi.StrongArtin.VariableJacobianHensel.
  exists_exact_solution_variableJacobian
```

This is the relative formal-smoothness form most relevant to deformation and Hecke equations.

## Quadratic equations

For

```text
F x = constant + linear x + bilinear x x,
```

Lean defines the derivative

```text
D x delta = linear delta + bilinear x delta + bilinear delta x
```

and proves the exact remainder identity

```text
F (x + delta) - F x - D x delta = bilinear delta delta.
```

Therefore a correction of depth `n >= 1` has remainder of depth at least `n+1`. The full quadratic capstone is

```text
Komorebi.StrongArtin.QuadraticRemainderGain.
  exists_exact_quadratic_solution
```

This confirms that the nonlinear lifting hypothesis is nonvacuous and applies automatically to affine-quadratic systems.

## Relationship to the Strong Artin pipeline

The checked implication is now:

```text
arithmetic auxiliary variables complete the residual Jacobian
  + a lifted approximate right inverse exists modulo pi
  + Jacobians remain congruent throughout the residual fibre
  + the nonlinear remainder gains one power
  -> genuine finite-depth nonlinear lifting
  -> exact solution over a finite nilpotent quotient.
```

This is the abstract nonlinear bridge missing after v0.17.

It does **not** prove that the actual Strong Artin deformation or Hecke equations satisfy those hypotheses. In particular, the arithmetic Selmer--Jacobian comparison, construction of the lifted approximate right inverse, local Tate comparison, Chebotarev instantiation, and residual automorphic carrier remain open.

## New source

- `PowerDivisibility.lean`
- `NilpotentRightInverse.lean`
- `NonlinearHenselStep.lean`
- `NonlinearHenselTower.lean`
- `RelativeNonlinearHenselCapstone.lean`
- `VariableJacobianHensel.lean`
- `QuadraticRemainderGain.lean`

## Verification

Pinned environment:

```text
Lean 4.34.0-rc2
mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06
-DwarningAsError=true
```

The verifier checks the exact v0.18 base archive hash, scans active source for proof escapes, checks declaration counts, and freshly compiles all seven v0.19 modules in dependency order.

Run:

```bash
python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

A resumable path is available if an outer execution wrapper interrupts the final module:

```bash
python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --resume
```
