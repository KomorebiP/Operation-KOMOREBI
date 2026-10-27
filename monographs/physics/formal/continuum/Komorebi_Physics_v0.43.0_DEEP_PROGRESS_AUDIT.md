# Komorebi Physics v0.43.0 — Deep progress audit

## Executive result

Block 43 advances the checked program from generator consistency to finite-cutoff exponential evolution.  For every fixed torus Fourier mode, the central-difference Dirac generator converges to the continuum generator in operator norm with quadratic mesh error.  Analyticity of the Banach-algebra exponential transfers that estimate to `exp(-itH)` for every fixed physical time.  Exact Fourier orthogonality then gives strong torus-`L²` convergence for every fixed finite packet.

## 1. Operator-level upgrade

Block 42 controlled `H_h ψ - H ψ` for finite packets.  Block 43 packages the four Clifford generators as bounded continuous endomorphisms and proves

\[
\|H_h(n)-H(n)\|_{\mathrm{op}}=O(h^2)
\]

for every fixed Fourier label `n`.  The mass term cancels exactly; only the three sine-quotient residuals remain.

This operator theorem is stronger than pointwise convergence on a chosen amplitude.  It allows the error estimate to be composed with nonlinear analytic functional calculus.

## 2. Exponential evolution

The mode evolutions are defined by

\[
U_{h,n}(t)=\exp(-itH_h(n)),
\qquad
U_n(t)=\exp(-itH(n)).
\]

The endomorphism algebra is complete.  The generic Banach-algebra exponential is analytic, hence locally Lipschitz in the asymptotic sense used by Lean.  Composition with the operator residual yields

\[
\|U_{h,n}(t)-U_n(t)\|_{\mathrm{op}}=O(h^2)
\]

for every fixed `t`.

The block also proves exact algebraic identities

\[
U(0)=I,
\qquad
U(s+t)=U(s)U(t),
\qquad
U(-t)U(t)=I.
\]

These identities hold for both lattice and continuum mode evolutions.

## 3. Torus Hilbert-space assembly

For fixed finite support `S`, the propagated packet is

\[
\Psi_h(t)=\sum_{n\in S}E_n U_{h,n}(t)a_n.
\]

The residual decomposes exactly by mode, and Parseval gives

\[
\|\Psi_h(t)-\Psi(t)\|_{L^2}^2
=
\sum_{n\in S}
\|U_{h,n}(t)a_n-U_n(t)a_n\|^2.
\]

Finite closure of the mode estimates proves

\[
\|\Psi_h(t)-\Psi(t)\|_{L^2}=O(h^2),
\]

and therefore strong convergence at fixed time.

## 4. Why this matters

The checked discrete-to-continuum chain now contains:

1. concrete Euclidean `L²` state-space reconstruction;
2. dense finite-resolution subspaces and strong projection convergence;
3. generator consistency on finite Fourier packets;
4. exponential evolution convergence on fixed finite Fourier cutoffs.

This is the first formal propagation theorem in the continuum program.  The finite cutoff keeps every generator bounded and avoids unsupported claims about domains of unbounded operators.

## 5. Exact boundary

The current exponential is defined in the Banach algebra of continuous endomorphisms of the finite spinor space.  The source does not yet prove that the generator is self-adjoint in the Euclidean spinor inner product or that the exponential is Hilbert-unitary.  The algebraic inverse and group laws are proved, but norm preservation remains a separate theorem.

The theorem is also fixed in:

- Fourier support;
- physical time;
- mass and mode amplitudes.

There is no compact-time uniform estimate and no cutoff-removal theorem.  No full unbounded Dirac operator, self-adjoint domain, strong-resolvent limit, or interacting gauge propagator is claimed.

## 6. Verification contract

The production contract requires:

- full cumulative `lake build KomorebiPhysics`;
- direct warning-as-error compilation of the new source;
- API elaboration of every new named declaration;
- axiom audit of every new theorem;
- rejection of three deliberately false controls;
- byte preservation of predecessor mathematical sources;
- source trust scan;
- exact source archive CRC, path-safety, and internal hash validation;
- a clean extraction and rebuild of the complete Block 43 import closure;
- repetition of all focused gates in the extracted tree.

A build exit code establishes kernel acceptance of the compiled source.  It does not rebuild Lean or Mathlib from compiler source.

## 7. Next block

The next load-bearing layer is Hilbert stability:

1. transport the mode generators to Euclidean-spinor continuous endomorphisms;
2. prove the Clifford linear combination is self-adjoint;
3. prove `-itH` is skew-adjoint;
4. deduce exact unitary evolution;
5. obtain a bound uniform for `|t| ≤ T`;
6. remove the finite cutoff by Fourier density and unitary stability.
