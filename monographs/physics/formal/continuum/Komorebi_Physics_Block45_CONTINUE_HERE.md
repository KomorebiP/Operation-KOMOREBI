# Continue from Block 45

The verified target is compact-time quadratic convergence for every fixed mode and fixed finite Fourier packet, plus an exact two-tail cutoff inequality.

## Next target A: full Fourier-diagonal unitary evolutions

Define on torus Fourier coefficients:

```text
(U_h(t) f)^∧(n) = exp(-i t H_{h,n}) f̂(n)
(U(t) f)^∧(n)   = exp(-i t H_n) f̂(n)
```

Prove both maps are unitary on the complete four-spinor torus `L²` space.

## Next target B: cutoff removal

Let `P_N` be the finite Fourier projection. Combine exact unitarity, Fourier density, and Block 45:

```text
‖U_h(t)f-U(t)f‖
≤ 2 ‖f-P_N f‖
  + ‖U_h(t)P_N f-U(t)P_N f‖.
```

Derive compact-time strong convergence for every `f`.

## Next target C: unbounded continuum generator

After the propagator is constructed spectrally, define the full continuum Dirac operator and its weighted Fourier domain. Prove self-adjointness and identify the spectral propagator with its functional-calculus exponential. Do not claim strong-resolvent convergence before a common-domain theorem is formalized.
