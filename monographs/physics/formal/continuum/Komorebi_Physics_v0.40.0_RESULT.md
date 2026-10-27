# Komorebi Physics v0.40.0 — Checked Block 40

## Status

**PASS — modular cumulative verification with an exact frozen-source replay.**

Block 40 identifies the transported Euclidean finite-resolution spaces from Block 39 with the closed spans of concrete Cartesian dyadic-box indicator fields, modulo null boundaries.

## Central results

For an octree prefix `a` of depth `n`, the ordinary closed box `dyadicBox n a` has coordinate side length `2⁻ⁿ` and cube-volume

\[
\mu(B_{n,a})=8^{-n}.
\]

The octree prefix cylinder and the pullback of that Euclidean box agree almost everywhere:

\[
C_{n,a}=_{\mathrm{a.e.}}\operatorname{octreeCubeCode}^{-1}(B_{n,a}).
\]

Consequently the Euclidean box indicator pulls back to the octree prefix indicator, and the Hilbert adjoint transports the octree prefix indicator back to the Euclidean box indicator.

At Block 39 level `d` (which records the first `d+1` octree digits), the concrete dyadic level equals the previously transported level:

\[
V_d^{\mathrm{box}}=V_d^{\mathrm{transport}}.
\]

Therefore the concrete box-step hierarchy is nested, its algebraic union is dense in cube `L²`, and its orthogonal projections converge strongly:

\[
P_d^{\mathrm{box}}f\longrightarrow f.
\]

## Counts

- active mathematical modules: **139**
- cumulative named declarations: **3,598**
- cumulative theorem declarations: **2,761**
- new Block 40 named declarations: **63**
- new Block 40 theorem declarations: **37**
- preserved v0.39 mathematical modules: **138 / 138**
- new negative controls: **3 / 3 correctly rejected**

## Trust boundary

The new module compiles with warnings treated as errors. The theorem-level axiom audit reports only:

- `Classical.choice`
- `Quot.sound`
- `propext`

No active Block 40 source contains `sorry`, `admit`, a custom `axiom`, `native_decide`, or `unsafe`.

The pinned Lean and Mathlib binaries/caches were used; they were not rebuilt from compiler source.

## Nonclaims

Block 40 does not prove convergence of finite translations, consistency of the discrete Dirac generator, strong propagator convergence, dynamical gauge equations, gravity, cosmology, or empirical adequacy.
