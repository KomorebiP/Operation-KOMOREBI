# From a reduced response to a full-model response

**Komorebi P. · Conditional extension · 13 November 2026**

The published H10-derived example certifies arithmetic in a nine-state
projection. This note supplies a precise bridge to a larger model and
lists the additional bounds that bridge would need. It does not assign
unmeasured values to those bounds.

## Objects that must refer to the same target

Let $H$ be a finite real symmetric target Hamiltonian and let
$J:\mathbb R^9\to\mathbb R^N$ be an isometry, so $J^{\mathsf T}J=I_9$.
Put $P=JJ^{\mathsf T}$, $Q=I-P$, and $A=J^{\mathsf T}HJ$.
The sector, basis signs, stored-bit conventions and energy origin must
agree in these definitions.

Let $H_{\mathrm{red}}$ be the exact reduced Hamiltonian to which the
three-query recovery theorem applies, and let $\widehat H$ be its
estimated matrix. A nine-state approximation does not automatically equal
$A$; we allow a separate mismatch bound.

For a real observed reduced source $u$, a real full source $b$, and real
energies $E$ and $\widehat E$, assume certified nonnegative caps

$$
\|H_{\mathrm{red}}-\widehat H\|_2\le r,
\qquad \|A-H_{\mathrm{red}}\|_2\le\mu,
\qquad \|QHJ\|_2\le\tau,
$$

$$
\|b-Ju\|\le\delta,
\qquad |E-\widehat E|\le\kappa.
$$

The cache's Frobenius bound $r_H$ is a valid choice of $r$. The cap
$\mu$ can include a declared symmetry-completion or block-model mismatch.
The cap $\tau$ measures coupling to discarded states. The source cap
includes both active-space source error and leakage outside the projection.
If their orthogonal components are bounded by $\delta_P$ and $\ell$,
then $\delta=\sqrt{\delta_P^2+\ell^2}$ is sufficient.

## A finite-dimensional conditional bound

Use the same positive broadening $\eta$ in both responses and define

$$
g_{\mathrm{full}}=
b^{\mathsf T}\bigl((E+i\eta)I-H\bigr)^{-1}b,
\qquad
\widehat g=
u^{\mathsf T}\bigl((\widehat E+i\eta)I-\widehat H\bigr)^{-1}u.
$$

**Proposition.** Under the stated assumptions,

$$
|g_{\mathrm{full}}-\widehat g|
\le
\|u\|^2\left(
\frac{r+\mu+\kappa}{\eta^2}+\frac{\tau^2}{\eta^3}
\right)
+\frac{\delta(2\|u\|+\delta)}{\eta}.
$$

This is a sufficient enclosure, not an optimal bound. It requires no
spectral interval beyond finite real symmetry and $\eta>0$.

### Why the discarded-space contribution is quadratic

Set $H_d=PHP+QHQ$ and $T=PHQ+QHP$. These are the block-diagonal and
off-diagonal parts of $H$, and $\|T\|_2=\|QHJ\|_2\le\tau$.
For $z=\widehat E+i\eta$, let $R=(zI-H)^{-1}$ and
$R_d=(zI-H_d)^{-1}$. Applying the resolvent identity twice gives

$$
R-R_d=R_dTR_d+R_dTRTR_d.
$$

The first term vanishes after compression on both sides by $P$, since
$R_d$ preserves the two blocks and $T$ exchanges them. Each resolvent
has norm at most $1/\eta$. Therefore

$$
\|J^{\mathsf T}RJ-(zI_9-A)^{-1}\|_2
\le\frac{\tau^2}{\eta^3}.
$$

The source $Ju$ must be supported in the retained space for this
second-order compression argument. General source leakage is accounted
for separately by $\delta$.

### Completing the error budget

Replace $b$ by $Ju$ in the full response; the source expansion costs at
most $\delta(2\|u\|+\delta)/\eta$. Changing the real evaluation energy
costs at most $\|u\|^2\kappa/\eta^2$. The compression bound then costs
$\|u\|^2\tau^2/\eta^3$. Finally, two ordinary resolvent identities
replace $A$ by $H_{\mathrm{red}}$ and then by $\widehat H$, at costs
$\|u\|^2\mu/\eta^2$ and $\|u\|^2r/\eta^2$. Adding these terms proves
the proposition.

If $\tau=0$, the retained space is invariant and its truncation term is
zero. If the energy is a chosen fixed coordinate rather than an uncertain
physical reference, take $\kappa=0$ by definition. No neutral ground-state
claim follows from doing so. Small broadening amplifies the unknown caps;
the formula does not establish a uniform zero-broadening limit.

## What has and has not been measured for H10

| Term | Present status |
|---|---|
| Numerical recovery error $r$ | Certified for the declared nine-state model and its measured action cache. |
| Block mismatch $\mu$ | Zero for the exact declared projection compared with itself; not certified against the different original stored-bit target. |
| Discarded-space coupling $\tau$ | No numerical cap has been supplied for the original full-H10 target. |
| Physical source error $\delta$ | Zero for the example's exact Slater source by definition; not certified for the original neutral-state annihilation source. |
| Neutral-reference error $\kappa$ | No ground-state reference error cap has been supplied. It is unnecessary for a deliberately fixed evaluation coordinate. |

Using a spin-conjugate sector also requires a verified isometry and the
same target-operator semantics. Integral symmetry alone does not justify
silently identifying two differently assembled stored-bit operators.

The missing caps remain open obligations. This conditional proposition
fills in the argument that would combine them; it does not turn the small
arithmetic radius into a certificate of full-molecule accuracy. Its
argument is elementary finite-dimensional resolvent algebra, and no
novelty claim is made for that general method.
