# Komorebi Physics v0.48.0 Result

## Classification

**CHECKED MODULAR CUMULATIVE**, conditional on the production and clean-source receipts distributed with the release.

## Main result

Block 48 constructs the free continuum Dirac Hamiltonian on Fourier coefficient space

\[
\ell^2(\mathbb Z^3;\mathbb C^4)
\]

as a densely defined `LinearPMap`.  Its maximal domain is

\[
\mathcal D(H_m)=\{f:\ (H_m(n)f_n)_{n\in\mathbb Z^3}\in\ell^2\}.
\]

Lean proves:

1. finite-support coefficient fields lie in the domain;
2. the domain is dense;
3. the multiplier is symmetric;
4. its Hilbert adjoint acts by the same modewise Dirac matrices;
5. the adjoint domain is contained in the maximal multiplier domain;
6. the multiplier equals its adjoint and is self-adjoint;
7. every self-adjoint realization obtained here is closed;
8. finite Fourier truncations commute exactly with the multiplier;
9. every domain vector can be approximated simultaneously in state norm and operator-image norm by one finite truncation.

The final theorem gives the finite Fourier graph-core approximation property:

\[
\forall f\in\mathcal D(H_m),\ \forall\varepsilon>0,\ \exists S\Subset\mathbb Z^3
\]

such that

\[
\|f-P_Sf\|<\varepsilon,
\qquad
\|H_mf-H_mP_Sf\|<\varepsilon.
\]

## Nonclaims

Block 48 does not yet prove:

- an explicit equivalence of the maximal domain with a named Sobolev or momentum-weighted norm;
- the conjugated unbounded operator directly on physical torus `L²`;
- identification of the Block 47 continuum propagator with the spectral exponential of this unbounded operator;
- resolvent, graph-resolvent, or strong-resolvent convergence of lattice generators;
- gauge-covariant or interacting unbounded Dirac dynamics.
