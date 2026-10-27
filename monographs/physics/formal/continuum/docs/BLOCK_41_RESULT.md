# Block 41 result

**Komorebi Physics Lean v0.41.0 — Fourier-mode generator consistency**

## Checked mathematical result

For the central finite-difference Dirac symbol

\[
H_h(k)=
\alpha_x\frac{\sin(k_xh)}h+
\alpha_y\frac{\sin(k_yh)}h+
\alpha_z\frac{\sin(k_zh)}h+m\beta,
\]

with removable values inserted at `h = 0`, Lean proves

\[
H_h(k)\psi-H(k)\psi=O(h^2)
\qquad(h\to0^+)
\]

for every fixed momentum and four-spinor. Hence `H_h(k)ψ → H(k)ψ`.

The central-difference multiplier is derived exactly from translation phases:

\[
\frac{e^{ikh}-e^{-ikh}}{2h}
=i\frac{\sin(kh)}h.
\]

The exact Clifford mass-shell identities are

\[
H(k)^2=(m^2+|k|^2)I
\]

and

\[
H_h(k)^2=
\left(m^2+\sum_j\left(\frac{\sin(k_jh)}h\right)^2\right)I.
\]

For every fixed finite integer-mode Fourier packet, the symbol action has
pointwise `O(h²)` error and converges to the continuum symbol action.

## Scope boundary

This block proves Fourier-symbol and finite-packet consistency. It does not yet
prove an `L²` operator limit, self-adjoint generator convergence, resolvent
convergence, or convergence of unitary propagators.
