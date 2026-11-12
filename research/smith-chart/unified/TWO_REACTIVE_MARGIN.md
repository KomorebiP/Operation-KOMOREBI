# A usable margin for the entire two-reactive class

For the fixed Hughes target

$$Z_H(s)=\frac{6s^2+3s+4}{6s^2+2s+9},\qquad
 h(s)=\frac{Z_H(s)-1}{Z_H(s)+1},$$

every finite positive ordinary uncoupled transformer-free network with at most
two reactive branches and any number of resistors satisfies

$$\max_{s\in\{1/2,3/4,1,3/2,2\}}|\Gamma(s)-h(s)|>10^{-6}.$$

These are positive-real Laplace samples, with reference resistance one. The
result supplies a useful subclass margin within the seven-sample framework;
it is not an imaginary-axis matching specification. It uses classical
two-reactive network classification, with exact matrix and interval arithmetic
that can be replayed without a numerical solver.

## From physical graphs to a compact coefficient box

Discard floating components. For a connected port, the grounded Laplacian
determinant is a spanning-tree sum, and the port diagonal cofactor is a
rooted-forest sum. Each term is a product of branch admittances. Resistors
contribute a positive constant, capacitors a positive multiple of $s$, and
inductors a positive multiple of $s^{-1}$. Multiplying numerator and denominator
by $s^{n_L}$ gives nonnegative coefficient polynomials $P,Q$ of degree at most
$n_L+n_C\le2$. Hence

$$Z=P/Q,\qquad \Gamma=(P-Q)/(P+Q),\qquad
 P=As^2+Bs+C,\quad Q=Ds^2+Es+F.$$

The common positive scale is chosen so that $A+B+C+D+E+F=1$. Constant and
lower-degree responses and possible common factors are allowed at this step.
An open port is the separate constant response $\Gamma=1$ and immediately
fails the displayed error budget. A short is likewise separated by
$\Gamma=-1$. Thus the number and size of resistors do not enter the coefficient
bound.

For the five displayed samples, let $M$ have rows

$$\bigl((1-h)s^2,(1-h)s,1-h,-(1+h)s^2,-(1+h)s,-(1+h)\bigr),$$

followed by the all-ones normalization row. The exact certificate prints a
rational inverse. With

$$x_H=(6,3,4,6,2,9)/30,$$

it checks $Mx_H=(0,0,0,0,0,1)^T$ and both matrix products for the inverse.
If every sample error is at most $\delta$, each of the first five entries of
$M(x-x_H)$ has magnitude at most $\delta\max(1,s^2)$, because the normalized
nonnegative denominator $P(s)+Q(s)$ is at most $\max(1,s^2)$. The last entry is
zero. Taking the weighted row sums of the exact inverse therefore proves

$$\|x-x_H\|_\infty\le\frac{439774}{507}\delta.$$

At $\delta=10^{-6}$ this is strictly less than $1/1000$. All six coefficients
then lie in the positive rational box $x_H+[-1/1000,1/1000]^6$.

## The classical obstruction and its two exceptions

Write

$$t=AF-CD,\qquad K=t^2-(AE-BD)(BF-CE),$$
$$\lambda_1=E(BF-CE)-Ft,\qquad
 \lambda_2=B(AE-BD)-At,\qquad
 \mu_1=K-4CD(2t-BE).$$

The exact rational monomial enclosure over that entire box proves

$$t>0,\qquad K>0,\qquad
 \lambda_1<0,\qquad\lambda_2<0,\qquad\mu_1<0.$$

The nonzero resultant $K$ also excludes a cancellation to lower degree.
For positive biquadratic coefficients with $t>0$, classical regularity requires
$\lambda_1\ge0$ or $\lambda_2\ge0$. Reichert's theorem reduces every
two-reactive realization with arbitrary resistor count to two reactive elements
and three resistors. The only nonregular possibilities in that catalogue are
the two exceptional bridges. The bridge with $t>0$ requires $\mu_1\ge0$;
the other requires $t<0$. All possibilities contradict the box signs.

The source leaves are [Morelli's institutional dissertation](https://api.repository.cam.ac.uk/server/api/core/bitstreams/0008b1b9-9d58-4813-8e97-1db41532cc8c/content):
Section 3.1.1, Theorem 3.1, Table 5.9, Table 5.10 and Theorem A.9. The
classification is an external classical theorem, not a new result claimed
here. The full institutional PDF, its version and inspected formulas are bound
in the source audit. Its Figure A.11 caption incorrectly says that the bridge
is always regular; the theorem, formulas and nonregular physical control are
used instead of that caption. The source's explicit Reichert statement is
used as a theorem leaf; its original proof is not independently regenerated.

The same strict separating box excludes limits of physical two-reactive
responses: use normalized coefficients in the compact simplex, pass to a
subsequence, and replace the exceptional bridge's strict $t$ sign by its weak
version. The resulting finite union of necessary polynomial conditions is
closed and still misses this box. This addresses open/short component limits
without assuming that a limiting circuit retains positive component values.

## What the certificate closes

The producer rebuilds the inverse and every polynomial enclosure exactly.
Its controls include all 64 coefficient-box corners, 320 enclosure comparisons,
four corrupt-certificate rejections and eight independent physical evaluations
of the exceptional bridge. With $L=C=R_1=R_3=1$ and $R_2=2$, that bridge has

$$Z(s)=\frac{5s^2+4s+4}{3s^2+4s+4},\qquad
 (t,K,\lambda_1,\lambda_2,\mu_1)=(8,64,-32,-8,64).$$

It is nonregular and physically realizable, so it rejects the tempting but
false shortcut that every two-reactive network is regular. Finite controls
validate the arithmetic and translation; the universal conclusion rests on
the written coefficient argument and the stated classical leaves.

This closes the nineteen previously uncovered budget-two mixed representatives.
Together with the two terminal-shunt certificates, 138 of the 2,130 canonical
mixed representatives are covered. The remaining 1,992 split as 220 at budget
three and 1,772 at budget four. No useful all-topology four-reactive margin or
complete Lean proof of this new separator is claimed.
