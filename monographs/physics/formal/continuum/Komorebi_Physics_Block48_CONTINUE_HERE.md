# Continue from Block 48

The checked frontier is the maximal self-adjoint and closed Fourier-multiplier realization of the free continuum Dirac Hamiltonian, with finite Fourier graph-core approximation.

## Target A: explicit weighted domain

Prove that the maximal domain is equivalent to a first-order momentum-weighted condition.  A natural target is

```text
f ∈ continuumDiracDomain m
↔ Summable (fun n => (m^2 + |2πn|^2) * ‖f n‖^2)
```

with the exact weight adjusted to the available `ℓ²` API.

## Target B: physical torus operator

Conjugate the coefficient `LinearPMap` through `torusFourierEquiv` and prove the resulting partial operator on

```text
L²(T³; C⁴)
```

is densely defined, closed, and self-adjoint.

## Target C: generator of the checked unitary group

Identify the Block 47 continuum unitary group with the spectral or functional-calculus exponential of the self-adjoint unbounded operator.  Do not infer this only from agreement on finite Fourier packets.

## Target D: lattice-to-continuum resolvent theory

After lattice generators and compatible domains are formalized, prove graph or strong-resolvent convergence.  Do not claim strong-resolvent convergence from propagator convergence alone without invoking and checking the required theorem and hypotheses.
