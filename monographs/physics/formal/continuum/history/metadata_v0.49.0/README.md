# Komorebi Physics Lean v0.45.0 — Block 45

This cumulative source release extends the checked v0.44 Hilbert-stability frontier with compact-time quadratic propagator bounds for fixed Fourier modes and fixed finite Fourier packets.

## New module

`KomorebiPhysics/Relativistic3DFourierCompactTime.lean`

It proves:

- Lipschitz control of the Banach-algebra exponential on closed operator-norm balls;
- an exact Hilbert generator-residual decomposition and `O(h²)` operator convergence;
- one quadratic error envelope valid for every `|t| ≤ T` on a fixed mode;
- one quadratic compact-time envelope for every fixed finite Fourier packet;
- the exact two-tail inequality required for Fourier-cutoff removal.

## Verification boundary

The release uses modular cumulative verification because the inherited root `module` target cannot import the non-module Block 44 file. The new module, its full import closure, API, axiom audit, negative controls, parent-source preservation, and clean-source replay are the release gates. The failed inherited monolithic root build is recorded rather than treated as proof evidence.

The block does not yet construct the complete Fourier-diagonal propagators on all torus `L²`, remove the finite Fourier cutoff, or formalize the full unbounded Dirac operator.

## Build

Attach the exact pinned portable Lean/Mathlib environment and run:

```bash
lake build KomorebiPhysics.Relativistic3DFourierCompactTime
lake env lean -DwarningAsError=true KomorebiPhysics/Relativistic3DFourierCompactTime.lean
```
