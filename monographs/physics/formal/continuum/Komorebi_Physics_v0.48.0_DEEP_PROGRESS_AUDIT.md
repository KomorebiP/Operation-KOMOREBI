# Komorebi Physics v0.48.0 Deep Progress Audit

## 1. Scientific role of Block 48

Blocks 41–47 established modewise generator consistency, finite-packet and full-space propagator convergence, exact Hilbert stability, Fourier cutoff removal, and transport to physical torus `L²`.  Those results used bounded mode operators and their coordinatewise exponentials.  The missing object was the actual unbounded continuum generator whose Fourier symbol grows with momentum.

Block 48 supplies that object.

## 2. Operator and domain

For mass `m`, the modewise coefficient action is

\[
(\widehat H_m f)(n)=H_m(n)f(n),
\]

where `H_m(n)` is the checked self-adjoint four-spinor Dirac matrix from the earlier Fourier-Hilbert blocks.

The maximal domain is defined by output square summability:

\[
\mathcal D(H_m)
=
\{f\in\ell^2:\ n\mapsto H_m(n)f(n)\in\ell^2\}.
\]

This is a linear subspace because the mode multiplier is linear and `Memℓp` is closed under addition and scalar multiplication.

The operator is represented by a Mathlib `LinearPMap`, which carries its domain as part of the object rather than pretending the unbounded generator is a bounded endomorphism.

## 3. Density

A single Fourier coefficient has finite support and therefore lies in the maximal domain.  Finite sums of such coefficients also lie in the domain.

Canonical coefficient truncations converge to every `ℓ²` field.  This proves that the maximal domain is dense in coefficient Hilbert space.

## 4. Symmetry and adjoint calculation

Modewise self-adjointness gives

\[
\langle H_m(n)f_n,g_n\rangle
=
\langle f_n,H_m(n)g_n\rangle.
\]

Summing over modes proves that the partial multiplier is a formal adjoint of itself.

The Hilbert adjoint exists because the domain is dense.  Testing the adjoint against single-mode fields proves the coordinate formula

\[
(H_m^*f)(n)=H_m(n)f(n).
\]

Since the adjoint output is square summable, every adjoint-domain vector belongs to the maximal multiplier domain.  Thus

\[
H_m^*\le H_m.
\]

Symmetry gives the reverse inclusion

\[
H_m\le H_m^*.
\]

Therefore

\[
\boxed{H_m^*=H_m}.
\]

The operator is self-adjoint and consequently closed.

## 5. Finite Fourier graph core

For every finite mode set `S`, truncation commutes exactly with the diagonal multiplier:

\[
H_mP_Sf=P_SH_mf.
\]

For a domain vector `f`, both the coefficient series for `f` and the coefficient series for `H_mf` converge.  Intersecting the two eventual finite-set conditions yields one finite `S` satisfying

\[
\|f-P_Sf\|<\varepsilon,
\qquad
\|H_mf-H_mP_Sf\|<\varepsilon.
\]

This is the operative graph-core approximation statement.  The release does not introduce a separate Mathlib `IsCore` wrapper, so the claim is stated at the exact epsilon-theorem level actually checked.

## 6. Verification boundary

The accepted evidence consists of:

- byte-for-byte preservation of every predecessor Lean file;
- warning-as-error compilation of the final Block 48 source;
- a complete build of the new module and import closure;
- public API checks for every new named declaration;
- theorem-level axiom audits;
- three deliberately false negative controls;
- an independent clean-source extraction and replay;
- archive CRC, path-safety, and checksum audits.

The permitted imported logical dependencies are the standard Lean/Mathlib foundations `Classical.choice`, `Quot.sound`, and `propext`.

Lean, Mathlib, and the compiler were used from the pinned portable environment.  They were not rebuilt from compiler source.

## 7. Remaining mathematical frontier

The next load-bearing results are:

1. prove an explicit weighted Fourier characterization of the domain, equivalent to the natural first-order Sobolev condition;
2. conjugate the `LinearPMap` through the checked torus Fourier equivalence to obtain a physical-space self-adjoint Dirac Hamiltonian;
3. identify the Block 47 unitary group with the spectral or functional-calculus exponential of that operator;
4. formulate lattice generators on compatible domains and prove graph or strong-resolvent convergence.
