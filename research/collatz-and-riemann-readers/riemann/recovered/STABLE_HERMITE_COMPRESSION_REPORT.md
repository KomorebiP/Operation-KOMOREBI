# Komorebi RH — stable Hermite compression construction

## Result

A stable heat-resolution compression can be constructed.

For the normalized Gaussian
\[
g_{t,a}(u)=(2\pi t)^{-1/4}
\exp\left(-\frac{(u-a)^2}{4t}\right),
\]
let \(\psi_{r,t,c}\) be the scaled Hermite basis centered at \(c\). The exact
coherent-state expansion is
\[
g_{t,a}
=
e^{-\lambda/2}
\sum_{r\ge0}\frac{\sigma^r}{\sqrt{r!}}\psi_{r,t,c},
\qquad
\sigma=\frac{a-c}{2\sqrt t},
\qquad
\lambda=\sigma^2.
\]
Consequently,
\[
\left\|(I-P_R)g_{t,a}\right\|_2^2
=
e^{-\lambda}\sum_{r>R}\frac{\lambda^r}{r!}
=
\Pr\{\operatorname{Pois}(\lambda)>R\}.
\]

For a shell
\[
|a-c_j|\le C\sqrt j+O(1),\qquad t\ge t_0,
\]
one has
\[
\lambda\le \alpha j+O(\sqrt j),
\qquad
\alpha=\frac{C^2}{4t_0}.
\]
Taking \(R_j=\lceil qj\rceil\), \(q>\alpha\), gives the Chernoff rate
\[
I(q\mid\alpha)=q\log(q/\alpha)-q+\alpha.
\]
The projection error is
\[
\exp\left[-\frac12 I(q\mid\alpha)j+o(j)\right].
\]

The positive prime-packet coefficient mass through
\(X_j=\exp(j+O(\sqrt j))\) is at most
\[
\sum_{n\le X_j}\frac{\Lambda(n)}{\sqrt n}
\le 2\sqrt{X_j}\log X_j
=
\exp\left(\frac j2+o(j)\right).
\]
Therefore any \(q\) satisfying
\[
I(q\mid\alpha)>1
\]
gives exponentially small aggregate compression error. The pole-annihilator
only inserts a quadratic Hermite-ladder factor, so it changes the estimate by
a polynomial in \(j\), not its exponential rate.

For the representative legal parameters
\[
t_0=0.5,\quad T=1.0,\quad C=2.2,\quad q=6.0,
\]
the computed rate is
\[
I=1.867951574357,
\qquad
\frac I2-\frac12=0.433975787178>0.
\]
Thus \(R_j=\lceil 6.0j\rceil\) is a condition-one compression with an
exponentially small reconstruction defect.

## What this closes

The exponential ill-conditioning of the raw integer-indexed Gaussian frame is
not intrinsic to the physical heat field. It is an overresolution artifact.
Fiberwise projection onto the first \(O(j)\) Hermite modes gives an orthogonal,
energy-stable physical quotient.

## What remains

The lowest Hermite coefficient is not harmless. The exact overlap identity is
\[
\langle g_{t,a},g_{s,c}\rangle
=
\left(\frac{2\sqrt{ts}}{t+s}\right)^{1/2}
\exp\left(-\frac{(a-c)^2}{4(t+s)}\right).
\]
Hence the ground Hermite coefficient of a heat packet is another Gaussian heat
packet at a larger heat time. It retains the same zero front. Compression
therefore does not remove the RH obstruction; it places it in finitely many
stable coefficient functions.

The unresolved theorem is now a finite-dimensional arithmetic estimate for
those compressed coefficients:
\[
\sum_p \operatorname{Inf}^{\rm Hermite}_p(F_j)
\ge \delta_j E_j-B_j,
\qquad
\delta_j^{-1},B_j=e^{o(j)},
\]
or an equivalent signed-collision saving. The \(r=0\) channel already contains
a smoothed prime-counting discrepancy, so ordinary sieve estimates cannot
supply this bound without overcoming the parity/zero obstruction.

## Computation audit

- Coherent-state identity cases: 144
- Maximum quadrature-versus-Poisson residual: `3.331e-16`
- Ground-mode overlap cases: 27
- Maximum overlap residual: `2.220e-16`
- Status: `PASS`

These computations audit formulas and constants only. They do not test an
asymptotic prime-cancellation theorem and do not constitute evidence of RH.
