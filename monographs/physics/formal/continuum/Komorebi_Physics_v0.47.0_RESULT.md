# Komorebi Physics v0.47.0 — Physical Torus Fourier Evolution

## Result

Block 47 constructs a complex linear isometric equivalence

\[
L^2(\mathbb T^3;\mathbb C^4)
\simeq
\ell^2(\mathbb Z^3;\mathbb C^4).
\]

The equivalence is built from Mathlib's normalized multivariate torus Fourier basis, with a formal surjectivity proof for four-spinor synthesis. The complete coefficient-space continuum and central-difference Dirac propagators are conjugated through this equivalence to exact linear isometric evolutions on physical torus spinor `L²`.

For every physical torus spinor `f`, mass `m`, compact time radius `T ≥ 0`, and tolerance `ε > 0`, Lean proves

\[
\forall^{\mathrm{eventually}}h\to0^+,\quad
\forall |t|\le T,\quad
\|U_h(t)f-U(t)f\|_{L^2}<\varepsilon.
\]

The theorem removes the Fourier cutoff and transports the full coefficient-space compact-time convergence theorem into physical torus `L²`.

## Verification classification

Checked modular cumulative. The Block 47 source, complete import closure, warning-as-error compilation, public API, theorem axiom audit, trust scan, three negative controls, parent-source preservation, and fresh modular replay all pass.

The inherited default root target still fails at the pre-existing Block 44 module/non-module import boundary. That root failure is recorded and is not counted as proof evidence.

## Boundary

The unbounded continuum Dirac operator, its weighted Fourier domain, self-adjoint spectral realization, strong-resolvent convergence, and interacting gauge evolution remain separate tasks.
