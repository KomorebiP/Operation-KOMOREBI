# Block 34 proof guide

## 1. Coordinate-regular connection data

`RegularConnection3` stores three real connection components

\[
A_x,A_y,A_z:\mathbb R^3\to\mathbb R
\]

together with the six cross-coordinate derivative fields

\[
\partial_xA_y,\ \partial_yA_x,\ \partial_xA_z,\ \partial_zA_x,
\ \partial_yA_z,\ \partial_zA_y.
\]

The structure records one-dimensional derivative identities and continuity
along the coordinate lines actually used by the proofs. `CrossDerivativeBounds`
provides uniform nonnegative absolute bounds for those six derivative fields.
The theorem does not assume a stronger unformalized multivariable smoothness
class.

## 2. Exact line-integral links

The coordinate-edge angles are interval integrals, for example

\[
\theta_x(p,h)=\int_0^h A_x(p+t e_x)\,dt.
\]

The links are `Circle.exp θ`. Interval-integral additivity proves

\[
\theta_x(p,h)
=\theta_x(p,h/2)+\theta_x(p+(h/2)e_x,h/2),
\]

and hence

\[
u_x^{(2)}u_x^{(1)}=u_x.
\]

The analogous results hold in the `y` and `z` directions. The finite-site
functions `regularHalfProductLink*On` therefore equal the corresponding
`regularCoarseLink*On` exactly.

## 3. Fundamental-theorem variation bounds

For each cross direction, the one-dimensional fundamental theorem of calculus
and the recorded derivative bound give estimates such as

\[
|A_y(p+h e_x)-A_y(p)|\le B_{yx}|h|.
\]

Integrating this estimate along the transverse edge yields

\[
|\theta_y(p+h e_x,h)-\theta_y(p,h)|
\le B_{yx}|h|^2.
\]

Six such estimates are proved, one for each ordered cross-coordinate pair.

## 4. Plaquette control

The oriented plaquette angle is the difference between the two path angles.
For the `xy` face,

\[
|\Theta_{xy}(p,h)|
\le (B_{yx}+B_{xy})|h|^2.
\]

Using the checked unit-circle exponential estimate gives

\[
|\Omega_{xy}(p,h)-1|
\le (B_{yx}+B_{xy})|h|^2,
\]

with corresponding `xz` and `yz` bounds.

The quantities

\[
F_{xy}=\partial_xA_y-\partial_yA_x,
\quad
F_{xz}=\partial_xA_z-\partial_zA_x,
\quad
F_{yz}=\partial_yA_z-\partial_zA_y
\]

are defined and bounded. The present plaquette theorem uses the sum of the
absolute derivative bounds; it does not claim the sharper exact surface
integral of `F` for a general connection.

## 5. Five-face and complete Hilbert estimates

`regularCubeLinks` populates the twelve links of one cubical cell. The five
independent face terms selected by the prior Bianchi analysis satisfy

\[
\operatorname{curvatureBudget}
\le h^2\mathcal A_{\partial}(A),
\]

where

\[
\mathcal A_{\partial}(A)
=(B_{yx}+B_{xy})+2(B_{zx}+B_{xz})+2(B_{zy}+B_{yz}).
\]

Exact half-edge composition sets the straight-edge budget to zero. Inserting
the generated links into the checked Block 32 operator theorem proves

\[
\boxed{
\|D_{\mathrm{total}}(h)\|
\le h^2\mathcal A_{\partial}(A).
}
\]

## 6. Dyadic summability and global limit

For `a_n=a_0 2^{-n}`, `regularDyadicBudget` has the exact form

\[
\varepsilon_n
=a_0^2\mathcal A_{\partial}(A)(1/4)^n.
\]

The scalar sequence and the actual connection-generated operator norms are
summable. `tendsto_regularConnectionLimit` and
`dist_regularConnectionLimit_le_tail` instantiate the checked complete-metric
summable-defect theorem.

## 7. Non-affine witness

`sinusoidalYConnection` is

\[
A_x=0,\qquad A_y(x,y,z)=\sin x,\qquad A_z=0.
\]

Its curvature is

\[
F_{xy}(x,y,z)=\cos x,
\]

which has different values at `x=0` and `x=π/2`. The certified derivative
envelope is one, and therefore

\[
\|D_{\mathrm{total}}(h)\|\le h^2.
\]

This witness demonstrates that Block 34 is genuinely beyond the constant
curvature affine class.

## Boundary

The block is abelian and uses exact coordinate line integrals. It does not prove
nonabelian path ordering, a sharp general Stokes theorem, continuum `L²`
reconstruction, continuum Dirac convergence, or gauge-field dynamics.
