# Komorebi Physics v0.40.0 — deep progress audit

## Scientific transition

Block 39 showed that abstractly transported finite-prefix subspaces are dense in Euclidean cube `L²`. Its exact boundary was geometric: those subspaces had not been identified with the ordinary fields that are constant on Cartesian dyadic cells.

Block 40 closes that boundary. It constructs each ordinary dyadic box directly from the three coordinate bit prefixes, proves the exact side and volume laws, and identifies its decoder preimage with the matching octree cylinder modulo null boundaries. This is sufficient at the `L²` level because functions differing only on those boundaries represent the same state.

## Load-bearing theorem chain

\[
	ext{octree prefix}
	o
	ext{three coordinate codes}
	o
B_{n,a}\subset [0,1]^3,
\]

\[
\mu(B_{n,a})=8^{-n},
\qquad
C_{n,a}=_{\mathrm{a.e.}}q^{-1}(B_{n,a}),
\]

\[
U(1_{B_{n,a}}c)=1_{C_{n,a}}c,
\qquad
U^\dagger(1_{C_{n,a}}c)=1_{B_{n,a}}c,
\]

\[
V_d^{\mathrm{transport}}=V_d^{\mathrm{box}},
\qquad
\overline{igcup_dV_d^{\mathrm{box}}}=L^2([0,1]^3;E),
\]

\[
P_d^{\mathrm{box}}f	o f.
\]

## Why the equality is not pointwise

The construction uses closed dyadic boxes to obtain a direct containment theorem from binary tails. Sibling closed boxes meet on faces. The overlapping faces have cube-volume zero, so the corresponding indicator fields are equal in `L²` to any half-open partition convention. The formal claim is therefore exactly the right one: equality almost everywhere, followed by equality in `L²`.

## What is now closed

- exact Cartesian coordinates for every finite octree prefix;
- exact `2⁻ⁿ` side and `8⁻ⁿ` volume laws;
- a.e. prefix-cylinder / box-preimage identification;
- exact pullback and adjoint transport of box indicators;
- equality of the concrete and transported finite-resolution levels;
- nesting and density of ordinary dyadic-box step spaces;
- strong convergence of their orthogonal projections.

## Remaining dynamical frontier

The state-space reconstruction is now concrete enough to define dynamics directly on Euclidean dyadic fields. The next major block should select a boundary convention—most naturally the three-torus for translation invariance—define a dense trigonometric-polynomial spinor core, construct finite-difference Dirac generators, and prove generator consistency. Stability/unitarity can then be combined with that consistency to target strong propagator convergence.
