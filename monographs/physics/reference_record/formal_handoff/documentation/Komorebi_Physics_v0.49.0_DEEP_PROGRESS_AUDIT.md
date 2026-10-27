# Komorebi Physics v0.49.0 — Deep Progress Audit

## Executive result

Block 49 converts the abstract maximal-domain definition from Block 48 into an explicit first-order Fourier regularity theorem and then moves the complete unbounded Hamiltonian to physical torus `L²`.

## Coefficient-space result

For mode momentum `k_n = 2π n`, the checked Clifford identity gives

```text
H_m(n)^2 = (m² + |k_n|²) I.
```

Using modewise symmetry, Lean proves

```text
‖H_m(n) ψ‖² = (m² + |k_n|²) ‖ψ‖².
```

The maximal domain is therefore equivalent to summability of these modal energies. Since coefficient fields already lie in `ℓ²`, the mass term is always summable. Hence

```text
D(H_m) = {f : Σ (1 + |k_n|²) ‖f_n‖² < ∞}.
```

The domain is independent of `m`, although the operator action is not.

## Physical torus result

The checked Fourier equivalence

```text
L²(T³; C⁴) ≃ₗᵢ[ℂ] ℓ²(Z³; C⁴)
```

is used to pull back the maximal domain and conjugate the coefficient partial operator. The resulting physical Hamiltonian has:

- a dense domain;
- the explicit first-order Fourier characterization;
- exact Fourier intertwining;
- symmetry;
- equality with its Hilbert adjoint;
- self-adjointness;
- closedness.

The proof of reverse adjoint-domain inclusion is not inferred abstractly from prose. An adjoint-domain vector is Fourier transformed, shown to lie in the coefficient adjoint domain, placed in the maximal coefficient domain by Block 48, and then transported back.

## Exact energy formulas

For domain vectors, Lean proves

```text
‖H_m f‖² = Σ (m² + |k_n|²) ‖f_n‖²
```

both in coefficient space and after transport to physical torus `L²`.

## Scientific meaning

The free continuum matter sector now has a physically located self-adjoint Hamiltonian with a concrete first-order domain. This closes the distinction between a formally self-adjoint coefficient multiplier and an unbounded Hamiltonian acting on physical continuum spinor fields.

## Remaining boundary

Not proved in this block:

- spectral-functional-calculus identification of the checked propagator;
- Stone-theorem uniqueness of that unitary group;
- lattice graph or strong-resolvent convergence;
- a gauge-covariant unbounded Hamiltonian;
- dynamical gauge fields, geometry, gravity, cosmology, or empirical predictions.
