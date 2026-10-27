# Block 33 proof guide

## 1. Affine abelian connection

`Point3` is a local Euclidean chart and `AffineForm3` represents a real affine
scalar field. `AffineConnection3` stores the three coordinate components
`A_x`, `A_y`, and `A_z`.

The closed coordinate-edge formulas are

\[
\theta_x(p,h)
=
hA_x(p)+\frac{h^2}{2}\partial_xA_x,
\]

with analogous definitions in the other two directions. The associated link
is the unit-circle element `Circle.exp θ`.

## 2. Exact straight-edge reconstruction

For an affine function, the integral across an edge is exactly the sum of its
two half-edge integrals. Theorems

- `edgeAngleX_half_add`,
- `edgeAngleY_half_add`,
- `edgeAngleZ_half_add`

prove the additive identities. Exponentiating gives

- `linkX_half_product`,
- `linkY_half_product`,
- `linkZ_half_product`.

The finite-site definitions `affineHalfProductLink*On` and
`affineCoarseLink*On` connect these local formulas directly to the link triples
used by the Block 32 Hilbert defect theorem. Their equality theorems show that
the straight-edge budget vanishes for the actual generated links.

## 3. Exact affine Stokes formulas

The constant curvature components are

\[
F_{xy}=\partial_xA_y-\partial_yA_x,
\quad
F_{xz}=\partial_xA_z-\partial_zA_x,
\quad
F_{yz}=\partial_yA_z-\partial_zA_y.
\]

Theorems `plaquetteXY_eq_exp_curvature`,
`plaquetteXZ_eq_exp_curvature`, and `plaquetteYZ_eq_exp_curvature` prove

\[
\Omega_{ij}(p,h)=\exp(i h^2F_{ij})
\]

exactly. No truncated Taylor expansion is used.

## 4. Quadratic curvature estimate

`norm_circleExp_sub_one_le` proves

\[
|e^{it}-1|\le |t|.
\]

The six elementary faces of the affine cube have constant holonomy. Inserting
the five independent faces selected by Block 32 yields

\[
\operatorname{curvatureBudget}
\le
h^2\mathcal A(C),
\]

where

\[
\mathcal A(C)=|F_{xy}|+2|F_{xz}|+2|F_{yz}|.
\]

This is `curvatureBudget_affineCubeLinks_le`.

## 5. Complete operator theorem

`norm_affineGeneratedCombinedHilbertDefect_le` applies the Block 32 two-budget
operator theorem to the actual affine line-integral links. Exact half-edge
composition kills the entire straight-edge budget, leaving

\[
\boxed{
\|D_{\mathrm{total}}(h)\|
\le h^2\mathcal A(C).
}
\]

If all three curvature components vanish, the generated cube is flat and the
complete operator defect is exactly zero.

## 6. Dyadic summability

`affineDyadicBudget` specializes the bound to

\[
a_n=a_0 2^{-n}.
\]

The exact closed form is

\[
\varepsilon_n
=
a_0^2\mathcal A(C)\left(\frac14\right)^n.
\]

Theorems `summable_affineDyadicBudget` and
`summable_norm_affineGeneratedCombinedHilbertDefect_dyadic` establish
summability of the scalar budget and of the actual connection-generated
operator norms.

## 7. Global limit and witness

`tendsto_affineConnectionLimit` and
`dist_affineConnectionLimit_le_tail` instantiate the checked complete-metric
summable-defect theorem.

`uniformBzConnection B` realizes the gauge potential `A_y=Bx`. It has
`F_xy=B` and the exact plaquette phase

\[
\Omega_{xy}=\exp(i h^2B).
\]

At `B=π` and `h=1`, the plaquette is formally proved nontrivial.

## Boundary

The exact formulas rely on affine connection components and an abelian phase
group. They do not establish the corresponding remainder estimates for a
general regular connection, nonabelian path ordering, continuum `L²`
reconstruction, continuum Dirac convergence, or dynamical gauge equations.
