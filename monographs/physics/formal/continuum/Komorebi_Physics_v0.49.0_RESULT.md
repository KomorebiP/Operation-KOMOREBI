# Komorebi Physics v0.49.0 — Result

## Classification

`CHECKED_MODULAR_CUMULATIVE`

## Main result

The maximal free Dirac Fourier-multiplier domain is exactly the inhomogeneous first-order Fourier domain:

```text
f ∈ D(H_m)
↔ Summable (fun n => (1 + |k_n|²) * ‖f n‖²).
```

The exact modal energy identity is also proved:

```text
‖H_m(n) ψ‖² = (m² + |k_n|²) * ‖ψ‖².
```

Consequently the maximal domain is independent of the mass. Conjugating through the checked torus Fourier equivalence gives a densely defined physical-space partial operator on `L²(T³; C⁴)`. That operator is proved symmetric, self-adjoint, and closed, with the same weighted Fourier-domain characterization.

## Exact boundary

This release does not identify the previously checked continuum unitary group with the unbounded functional-calculus exponential, and it does not prove graph or strong-resolvent convergence of lattice generators.
