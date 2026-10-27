# Komorebi Physics v0.46.0 — Full Fourier-Coefficient Evolution

## Result

Block 46 constructs the continuum and central-difference free Dirac evolutions on the complete square-summable Fourier coefficient Hilbert space

\[
\ell^2(\mathbb Z^3;\mathbb C^4).
\]

Both evolutions are exact linear isometric equivalences, satisfy the time-group law, and preserve the full coefficient norm.

For every coefficient field `f`, mass `m`, compact time radius `T ≥ 0`, and tolerance `ε > 0`, Lean proves

\[
\forall^{\mathrm{eventually}} h\to0^+,\quad
\forall |t|\le T,\quad
\|U_h(t)f-U(t)f\|<\varepsilon.
\]

The proof removes the finite Fourier cutoff using canonical finite truncations, the Block 45 compact-time finite-packet theorem, and exact unitary two-tail control. No global quadratic rate is claimed for arbitrary square-summable data.

## Verification classification

Checked modular cumulative, conditional on the frozen checked v0.45 parent and exact parent-source preservation. The new module, public API, theorem axiom audit, trust scan, negative controls, and clean-source replay all pass.

## Boundary

The theorem is currently stated on the canonical Fourier coefficient Hilbert space. A formal unitary Fourier transform to physical torus `L²`, the full unbounded continuum Dirac operator and its weighted domain, strong-resolvent convergence, and interacting gauge dynamics remain separate tasks.
