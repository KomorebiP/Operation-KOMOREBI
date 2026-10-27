# Research boundary after Strong Artin Lean v0.19

## Strongest closed nonlinear theorem

Let `R` be a commutative ring, `pi : R` nilpotent, `F : X -> W`, and

```text
D : X -> (X ->ₗ[R] W)
```

a state-dependent Jacobian. Fix an initial point `x₀` and suppose there are

```text
approxRightInv : W ->ₗ[R] X
E              : X -> Module.End R W
```

such that for every `x` in the residual fibre of `x₀`,

```text
(D x).comp approxRightInv = LinearMap.id + pi • E x.
```

Assume also that for every `n >= 1` and every correction `delta ∈ pi^n X`,

```text
F (x + delta) - F x - D x delta ∈ pi^(n+1) W.
```

If

```text
F x₀ ∈ pi W,
```

then Lean proves

```text
∃ x, x - x₀ ∈ pi X ∧ F x = 0.
```

It also constructs a compatible tower whose defect at stage `n` lies in `pi^(n+1) W`.

## What changed

The prior v0.17 result only solved explicitly compatible **linearized** state-transition systems. v0.19 proves an actual nonlinear lifting theorem over finite nilpotent coefficient thickenings. It allows the Jacobian to vary with the current state and derives each exact stagewise right inverse from one approximate residual right inverse.

Quadratic equation systems satisfy the required Taylor-remainder gain automatically.

## Arithmetic boundary

The theorem does not by itself prove nonlinear Strong Artin deformation lifting. The following must still be supplied for the actual arithmetic presentation:

1. identify the completed deformation/Hecke equation map `F` and its state-dependent Jacobian `D`;
2. lift the residual augmented-Jacobian right inverse to `approxRightInv`;
3. prove the error factorization
   ```text
   D x ∘ approxRightInv = id + pi • E x
   ```
   throughout the relevant residual fibre;
4. prove the Taylor remainder gains one power for the actual complete local equations;
5. prove the Selmer--Jacobian and arithmetic auxiliary-column comparisons.

Thus v0.19 closes the **abstract nonlinear Hensel mechanism**, not its number-field deformation-theoretic instantiation.

## Dominant independent global gap

Even a complete arithmetic nonlinear lifting theorem cannot act without a nonzero automorphic carrier. The principal global existence problem remains:

```text
finite-Satake cyclic descent
  -> nonzero patchable determinant-bearing residual automorphic complex.
```

Continuous local Galois/Tate comparison, Chebotarev instantiation, relative patching, twist equivariance, ramified attachment, and Strong Artin also remain open.
