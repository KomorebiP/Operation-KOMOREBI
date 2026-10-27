# Research boundary after Strong Artin Lean v0.17

## Strongest closed internal pipeline

Assume:

1. a global transverse quotient `H / k·d`;
2. raw admissible local functionals whose localizations kill `d` and detect every nonzero transverse class;
3. a linear equivalence
   ```text
   H / k·d ≃ₗ[k] obstructionDual J;
   ```
4. finite dimensionality of the equation space;
5. an explicit state-transition theorem saying that a solved linearized correction yields the next valid lift state.

Then Lean constructs:

- equation-space columns representing every local functional;
- exactly `finrank k (W / range J)` admissible labels;
- a surjective augmented Jacobian;
- corrections through every prescribed finite depth.

The columns are unique modulo `range J`, and

```text
W / range J ≃ₗ[k] Dual k (obstructionDual J).
```

## Strongest closed local pairing theorem

For residual Frobenius `A`, Lean proves the trace pairing equivalence

```text
ker (1 - Ad(A))
  ≃ₗ[k]
Dual k (Matrix / range (1 - Ad(A))).
```

At residue-field norm `q = 1`, the left side is exactly the linearized tame inertia relation space. Every local quotient functional has a unique tame-relation representative. The pairing on representatives is `trace(P * X)` and equals the differential of a spectral determinant coordinate.

## Strongest closed support theorem

Flatness plus a nonzero special fibre gives a nonzero generic localization. After identification with a module over a finite split product ring, a transitive equivariant branch action propagates support to every coordinate branch.

## First open arithmetic implication

```text
v0.16 Chebotarev-ready conjugacy class
  -> number-field prime outside the bad set
  -> actual continuous local Galois cohomology classes
  -> normalized local Tate pairing
  -> the checked tame trace functional.
```

The finite-dimensional local pairing is proved; the arithmetic comparison and normalization are not.

## First open global existence implication

```text
finite-Satake cyclic descent
  -> nonzero residual packet in a determinant-bearing complex
  -> flat/MCM relative patched module or finite-depth arithmetic carrier.
```

No internal linear-algebra theorem manufactures this residual automorphic packet. This remains the dominant global gap.

## Non-claims

v0.17 does not establish Chebotarev, an arithmetic Taylor--Wiles theorem, nonlinear Hensel lifting for the actual deformation equations, residual automorphic occurrence, relative `R=T`, ramified local attachment, solvable-image Strong Artin, or unrestricted Strong Artin.
