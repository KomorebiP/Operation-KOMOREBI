# A weak tap: compact convergence and a discontinuous growth order

Checkpoint **SF-DISCOVERY-001**. This note adds a corollary without altering the
independently audited asymmetric-family route.

For \(0\le\varepsilon\le1\), let the normalized entire function \(F_\varepsilon\)
solve

\[
F_\varepsilon'(z)=1+(1-\varepsilon)F_\varepsilon(z/4)^2
+\varepsilon F_\varepsilon(3z/4)^2,\qquad F_\varepsilon(0)=0.
\]

The two active contractions have growth orders

\[
\rho_0=\frac{\log2}{\log4}=\frac12,\qquad
\rho_1=\frac{\log2}{\log(4/3)}.
\]

Removing channels of zero weight before applying the positive feedback-bank
theorem gives exactly

\[
\rho(F_\varepsilon)=
\begin{cases}
\frac12,&\varepsilon=0,\\
\frac{\log2}{\log(4/3)},&0<\varepsilon\le1.
\end{cases}
\]

The second number is approximately \(2.409420839653209\). It is a theorem's
numerical display, not a growth order estimated from the plotted curves.

**Compact convergence.** As \(\varepsilon\downarrow0\),
\(F_\varepsilon\to f_{1/4}\) uniformly on every compact subset of the complex
plane.

**Proof.** Write \(F_\varepsilon(z)=\sum_{n\ge0}c_n(\varepsilon)z^{2n+1}\).
Its recurrence is

\[
c_0=1,\qquad
c_n(\varepsilon)=
\frac{(1-\varepsilon)4^{-2n}+\varepsilon(3/4)^{2n}}{2n+1}
\sum_{i=0}^{n-1}c_i(\varepsilon)c_{n-1-i}(\varepsilon),\qquad n\ge1.
\]

Each coefficient is a polynomial in \(\varepsilon\), by induction, and therefore
is continuous at zero. On \(0\le\varepsilon\le1\), all coefficients are
nonnegative. Let \(d_n=c_n(1)\) be the coefficients of the established
single-dilation function \(f_{3/4}\). Since

\[
0\le (1-\varepsilon)4^{-2n}+\varepsilon(3/4)^{2n}
\le(3/4)^{2n},
\]

the recurrence proves \(0\le c_n(\varepsilon)\le d_n\). For any fixed radius
\(R>0\), the entire majorant has finite sum
\(\sum_n d_nR^{2n+1}=f_{3/4}(R)\). Coefficient continuity and domination by this
summable series prove uniform convergence on the disk \(|z|\le R\).
At \(\varepsilon=0\), the equation is exactly that of \(f_{1/4}\). \(\square\)

Thus a tap of arbitrarily small fixed positive weight can alter the global
growth order while changing the function only slightly on every prescribed
bounded region. This does not give a uniform approximation over an unbounded
domain. The limits of tap removal and arbitrarily large radius behave
differently.

## Numerical figure contract

The standalone script **build_tap_figure.py** creates **figures/07_weak_tap.pdf**
and **figures/07_weak_tap.png** without importing the other figure generator.
Its left panel displays ordinary 90-digit series calculations on \(0\le z\le2\)
for \(\varepsilon=0,0.001,0.01,0.1\). Its right panel displays the theorem above.

Coefficient sums retain \(c_0,\ldots,c_{160}\), hence powers through \(z^{321}\).
The Cauchy majorant algorithm is copied from the previously validated figure
generator. Coefficientwise domination gives \(M_\varepsilon(1)\le\tan(1)<2\).
The last inequality follows from \(\sin(1)<1\) and
\(\cos(1)>1-1/2=1/2\). For larger radii, the exact rational recursion

\[
M_{3/4}(R)\le R[1+M_{3/4}(3R/4)^2]
\]

is iterated down to radius at most one. At Cauchy radius \(R=3\), this gives a
finite exact rational bound \(B\). Every omitted Taylor coefficient of degree
\(k\) is bounded by \(B/3^k\). Therefore the uniform analytic truncation bound
on \(|z|\le2\) is

\[
B\,\frac{(2/3)^{323}}{1-2/3}
<1.40\times10^{-48}.
\]

This bound is exact rational arithmetic and controls omitted analytic terms.
It is separate from rounding in the ordinary 90-digit coefficient arithmetic
and the final floating display. It does not claim a certified ball enclosure.
The first nine coefficients of each plotted member are cross-checked against
an exact rational construction, giving 36 ordinary-precision comparisons with
absolute error below \(10^{-85}\). These checks authenticate the plotting
implementation in that range; they do not replace the analytic proofs.

The detailed computation record is **evidence/tap_figure_computation.json**,
including software versions, exact majorant and tail fractions, precision,
sample domain, evaluations at \(z=2\), coefficient hashes, and output hashes.
The figure was visually inspected for readable labels and absence of clipping.
Matplotlib emitted nonfatal font timestamp warnings during PDF construction;
the PDF and PNG were produced successfully.
