# Block 48 Proof Guide

## Namespace

`KomorebiPhysics.Relativistic3DUnboundedDirac`

## Construction order

1. `diracCoeff` applies the bounded self-adjoint mode Hamiltonian at each Fourier label.
2. `continuumDiracDomain` requires the resulting coefficient field to be square summable.
3. `continuumDiracOutput` packages that field as an element of coefficient `ℓ²`.
4. `continuumDiracPMap` packages the maximal multiplier as a `LinearPMap`.
5. Single-mode and finite-truncation lemmas establish a dense domain.
6. `continuumDiracPMap_isFormalAdjoint` sums the checked modewise symmetry identity.
7. `continuumDiracAdjoint_apply_coord` probes the adjoint with single-mode vectors.
8. The coordinate formula proves adjoint-domain inclusion and then equality with the original multiplier.
9. Self-adjointness implies closedness.
10. Exact truncation commutation plus simultaneous tail control proves the graph-core approximation theorem.

## Load-bearing declarations

- `continuumDiracDomain`
- `continuumDiracPMap`
- `continuumDiracDomain_dense`
- `continuumDiracPMap_isFormalAdjoint`
- `continuumDiracAdjoint_apply_coord`
- `continuumDiracAdjoint_domain_le`
- `continuumDiracPMap_selfAdjoint`
- `continuumDiracPMap_isClosed`
- `continuumDiracPMap_coeffTruncation`
- `exists_finite_graph_approx`

## Interpretation

The theorem is an unbounded-operator result.  The operator is not represented as a bounded continuous endomorphism.  Its maximal domain and adjoint domain are part of the formal statement.
