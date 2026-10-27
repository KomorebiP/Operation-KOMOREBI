# Komorebi Physics v0.43.0 — Result

## Classification

**Checked Block 43: fixed-cutoff Fourier exponential evolution converges strongly in torus `L²` at every fixed time, with quadratic mesh error.**

Production verification and a clean frozen-source replay both passed. The final archive replay record verifies the release after its metadata refresh.

## Main theorem

For a fixed finite set `S` of torus Fourier modes, amplitudes `aₙ ∈ ℂ⁴`, mass `m`, and fixed physical time `t`, let

\[
U_{h,n}(t)=\exp(-itH_{h,n}),
\qquad
U_n(t)=\exp(-itH_n),
\]

where `H_{h,n}` is the central-difference Dirac mode generator and `H_n` is its continuum counterpart. The checked development proves

\[
\left\|
\sum_{n\in S}E_n\bigl(U_{h,n}(t)a_n-U_n(t)a_n\bigr)
\right\|_{L^2}
=O(h^2)
\qquad(h\to0^+).
\]

Consequently the finite-cutoff evolved packet converges strongly in the four-spinor torus Hilbert space.

## Exact identities

- Mode generators are continuous linear endomorphisms.
- Their operator-norm difference is `O(h²)`.
- The Banach-algebra exponential inherits the `O(h²)` rate at fixed time.
- Both lattice and continuum exponentials satisfy exact zero-time, time-addition, and opposite-time inverse identities.
- The finite-packet propagator residual decomposes exactly into orthogonal mode residuals.
- Its norm square is exactly the sum of the mode-residual norm squares.

## Boundary

This block does not prove Hilbert unitarity of the exponentials, a time-uniform estimate on compact intervals, removal of the finite Fourier cutoff, self-adjointness of the full unbounded continuum Dirac operator, strong-resolvent convergence, or interacting/gauge-covariant propagator convergence.
