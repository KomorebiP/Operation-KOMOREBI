# Komorebi Physics v0.30.0 — Checked Block 30

## Result

Block 30 supplies the continuous-linear operator layer required by the
corrected refinement architecture.

On every finite lattice, the Clifford directional shifts and phase-frame
embedding are packaged as continuous linear maps. For each direction, the
actual adjacent-scale operator is

\[
D_i=F_i I_r-I_r C_i.
\]

For the full palindromic walk, assuming the fine and coarse factors are
contractive and the two mass factors intertwine exactly, Lean proves

\[
\|D_{MXYZYXM}\|
\le
\|D_X\|+\|D_Y\|+\|D_Z\|+\|D_Y\|+\|D_X\|.
\]

The multiplicative ratios `edgeRatioX/Y/Z` satisfy

\[
E_i(p)=1
\iff
v_i(h_i p)v_i(p)
=
r(\widetilde\tau_i p)u_i(x(p))r(p)^{-1}.
\]

When those straight-edge contracts hold, the complete seven-factor straight
refinement defect is exactly zero. This theorem does not assume flat
plaquettes.

Path reordering and cubical gluing are kept in a separate curvature budget

\[
\varepsilon_\Omega
=
\sum_{f\in\mathcal F_{\mathrm{ind}}}|\Omega_f-1|.
\]

A general two-stage theorem then proves

\[
\|D_{\mathrm{glue}\circ\mathrm{edge}}\|
\le
\varepsilon_E+\varepsilon_\Omega.
\]

Finally, separate summability of the scale-dependent edge and curvature
budgets implies convergence to one global limit, with the explicit tail bound

\[
d(f_n,f_\infty)
\le
\sum_{m=0}^{\infty}
\bigl(\varepsilon_E(n+m)+\varepsilon_\Omega(n+m)\bigr).
\]

## Verification

- Cumulative one-worker warnings-as-errors build: **PASS, 3,788 jobs**
- Block 30 import closure: **PASS, 2,354 jobs**
- Direct warning-as-error compilation: **PASS**
- Public API compilation: **PASS**
- Declaration-level axiom audit: **PASS**
- New negative controls: **3/3 correctly rejected**
- Parent preservation: **128/128 v0.29 modules byte-identical**
- Active mathematical modules: **129**
- Cumulative theorem declarations: **2,403**
- Cumulative audited declarations: **3,022**
- New Block 30 theorem declarations: **44**
- New Block 30 audited declarations: **68**

The observed imported axioms are `Classical.choice`, `Quot.sound`, and
`propext`.

## Boundary

The straight budget currently consists of actual continuous-linear operator
norms. Block 30 does not yet derive a sharp scalar reduction to
`max_p |E_i(p)-1|`, and the ambient continuous-linear norm is not silently
identified with the separately proved half-cell Hilbert energy. No concrete
mesh-scale decay or summability law is proved for the physical walk. Therefore
this block does not establish continuum Dirac convergence, dynamical gauge
field equations, gravity, cosmology, or empirical validation.
