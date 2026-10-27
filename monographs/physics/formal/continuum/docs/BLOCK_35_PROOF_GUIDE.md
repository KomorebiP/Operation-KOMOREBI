# Block 35 proof guide

## 1. Formal reconstruction space

Block 35 is the first release in the physics program to place the finite cell
states inside a genuine continuum Hilbert space rather than an abstract complete
metric target.

Let `(Ω, μ)` be a measure space, let `I` be finite, and let `E` be a complete
complex inner-product space. A `UnitVolumePartition` consists of measurable,
pairwise-disjoint cells `C_i` satisfying

\[
\mu(C_i)=1,
\qquad
\bigcup_{i\in I}C_i=\Omega.
\]

The discrete cell space and continuum space are

\[
\mathcal H_I=\ell^2(I;E),
\qquad
\mathcal H=L^2(\Omega,\mu;E).
\]

The unit-volume convention is load-bearing. It makes one coefficient equal to
both the constant cell value and its cell integral. General non-unit cell
volumes require explicit weights and are not claimed in this block.

## 2. Step interpolation

For `ψ : CellState`, the map `stepLinear` is

\[
(J\psi)(x)=\sum_{i\in I}\mathbf 1_{C_i}(x)\psi_i.
\]

Pairwise disjointness and unit cell volume give

\[
\langle J\psi,J\phi\rangle_{L^2}
=
\sum_i\langle\psi_i,\phi_i\rangle
=
\langle\psi,\phi\rangle_{\ell^2}.
\]

`stepIsometry` packages this equality as an exact complex linear isometry into
Mathlib's `Lp E 2 μ`.

## 3. Averaging as the Hilbert adjoint

The averaging map is defined by the Hilbert adjoint

\[
R=J^*.
\]

The formal proof first establishes

\[
RJ=I_{\mathcal H_I}.
\]

It then identifies every coordinate explicitly:

\[
(Rf)_i=\int_{C_i}f(x)\,d\mu(x).
\]

This is a Bochner integral in `E`; the result is not merely an abstract
existence statement about an adjoint.

## 4. Orthogonal cell projection

The continuum cell-average projection is

\[
P=JR.
\]

Lean proves:

\[
P^2=P,
\qquad
P^*=P,
\qquad
\|Pf\|\le\|f\|.
\]

It also derives the explicit formula

\[
Pf
=
\sum_i\mathbf 1_{C_i}
\left(\int_{C_i}f\,d\mu\right).
\]

The residual is orthogonal to every cell-step state:

\[
\langle J\psi,f-Pf\rangle=0.
\]

## 5. Pythagorean and best-approximation theorems

The orthogonal decomposition is checked exactly:

\[
\|f\|^2
=
\|Pf\|^2+\|f-Pf\|^2.
\]

For every step state `J ψ`,

\[
\boxed{
\|f-Pf\|\le\|f-J\psi\|
}
\]

so `Pf` is a best approximation from the finite cell-step subspace. Fixed
points of `P` are exactly the step states.

## 6. Refining-family convergence criterion

For a sequence of finite unit-volume partitions `P_n`, suppose there are step
approximants `J_n ψ_n` satisfying

\[
J_n\psi_n\longrightarrow f
\quad\text{in }L^2.
\]

The best-approximation inequality implies

\[
\boxed{
P_nf\longrightarrow f.
}
\]

This theorem reduces strong convergence of the cell-average projections to a
concrete density/approximation theorem for the selected geometric family.

## 7. Exact boundary

Block 35 does not yet construct the physical three-dimensional dyadic cubical
family. In particular, it does not prove:

- density of dyadic step spinors in `L²(Ω, ℂ⁴)`;
- the weighted normalization for cells of volume `a_n^3`;
- compatibility of `J_n` with the checked Clifford refinement maps;
- convergence of lattice translations or multiplication operators;
- consistency of the scaled walk generator;
- convergence to the continuum Dirac propagator.

Those are separate geometric and dynamical obligations. The present block
supplies the exact Hilbert reconstruction, adjoint, projection, and optimality
machinery they require.
