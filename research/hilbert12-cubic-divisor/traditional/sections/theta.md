## Analytic input and conventions

Let \(t\) be any point of the upper half-plane and \(E_t=\mathbb C/(\mathbb Z+\mathbb Zt)\). The classical product convention is \cite{BCG}

\[
 \theta_0(z;t)=\prod_{n\ge0}(1-e^{2\pi i(z+nt)})(1-e^{2\pi i((n+1)t-z)}).
\]

Retain from the preceding multiplication-norm proof:

\[
 \operatorname{div}(q_t)=4[0]-[P]-[-P]-[2P]-[-2P],\qquad P=1/5,
\]

and, for \(n\) prime to five,

\[
 \prod_{\eta\in E_t[n]}q_t(z+\eta)=q_t(nz).                  \tag{N1.1}
\]

The scalar in (N1.1) is exactly one. This is important: an unspecified norm multiplier would not suffice below. The inherited proof derives (N1.1) from the theta product by finite real root-of-unity averaging and vertical residue splitting. This block also tests it at the required nonzero two- and three-torsion points independently of the rational formula.

The normalization can also be checked directly here. Finite root averaging gives

\[
 \prod_{a=0}^{n-1}\theta_0(w+a/n;t)=\theta_0(nw;nt).
\]

Next, splitting the two defining products into vertical residues gives

\[
 \prod_{b=0}^{n-1}\theta_0(nz+bt;nt)=\theta_0(nz;t).
\]

For the smoothing denominator, multiplication by five permutes the real residues modulo n; the same two steps apply with period 5t. The numerator becomes \(\theta_0(nz;t)^5\) and the denominator becomes \(\theta_0(5nz;5t)\). This proves (N1.1) with no omitted multiplier and without using the unknown scalar \(c_t\).


Write

\[
 x(z)=\wp_t(z),\quad y(z)=\wp_t'(z),\quad
 f(X)=4X^3-g_2X-g_3.
\]

The classical equation is \(y(z)^2=f(x(z))\). The addition and duplication laws used below are those of this convention \cite{DLMFWeierstrass}. In particular the y-coordinate here is the full Weierstrass derivative, not its half.

Set

\[
 a=x(P),\quad b=x(2P),\quad d=a-b,\quad y_a=y(P),\quad y_b=y(2P),
\]

\[
 Q_5(X)=(X-a)(X-b).
\]

All of \(d,y_a,y_b\) are nonzero: a point of exact order five is neither two-torsion nor equal up to sign to its double. Comparing divisors yields a nonzero scalar \(c_t\) with

\[
 q_t(z)=c_t/Q_5(x(z)).                                    \tag{N1.2}
\]

Also \(q_t(z)\sim c_tz^4\) at zero. The problem in this development is to determine this scalar exactly without a choice of cube root or eta multiplier.

## A scalar is fixed by two coprime norm exponents

Suppose two nonzero elliptic functions with the same divisor differ by a scalar \(r\), and both satisfy the exactly normalized degree-two and degree-three multiplication laws. On the degree-four and degree-nine fibers those laws imply

\[
 r^4=r,\qquad r^9=r.
\]

Thus \(r^3=r^8=1\), and

\[
 r=(r^3)^3/r^8=1.                                       \tag{N2.1}
\]

More generally, if \(c^3=A\) and \(c^8=B\) with \(c\ne0\), then

\[
 \boxed{c=A^3/B.}                                       \tag{N2.2}
\]

This is a uniqueness and recovery statement within a fixed divisor class. It does NOT say that arbitrary functions are determined by two norms. In particular it does not contradict the nonconstant norm-one factor established in the preceding note.

The commutative-group statements (N2.1)-(N2.2), including uniqueness and the fixed-norm conditions, are formalized in `H12CoprimeNormalization`.

## The fifth-torsion ordinate identity

Since \(2P\) doubles to \(4P=-P\), let \(\ell,m\) be the full-y tangent slopes at \(P,2P\). The addition law gives

\[
 \ell^2=4(2a+b),\quad m^2=4(a+2b),
\]

\[
 \ell d=y_a+y_b,\qquad md=y_a-y_b.                       \tag{N3.1}
\]

Subtract the squares of the last two equalities:

\[
 4y_ay_b=(\ell^2-m^2)d^2=4d^3.
\]

Therefore

\[
 \boxed{y_ay_b=d^3,\qquad f(a)f(b)=d^6.}                 \tag{N3.2}
\]

The polynomial implication from (N3.1) to (N3.2) is formalized. The fact that the actual elliptic points satisfy (N3.1) is supplied by the ordinary group-law argument here, not by an undeclared formal assumption.

Define the third division polynomial in this convention:

\[
 \psi_3(X)=3X^4-\tfrac32g_2X^2-3g_3X-\tfrac1{16}g_2^2,
\]

and the duplication numerator

\[
 \phi_2(X)=X^4+\tfrac12g_2X^2+2g_3X+\tfrac1{16}g_2^2.
\]

The identities

\[
 Xf(X)-\phi_2(X)=\psi_3(X),\qquad
 b=\phi_2(a)/f(a),\quad a=\phi_2(b)/f(b)
\]

give

\[
 \psi_3(a)=f(a)d,\qquad \psi_3(b)=-f(b)d.
\]

Consequently

\[
 \boxed{\psi_3(a)\psi_3(b)=-d^8.}                        \tag{N3.3}
\]

The minus sign in (N3.3) is retained. It disappears only after the square used below.

## Evaluate both scalar powers without ambiguity

Let \(z\to0\) in (N1.1). The fourth-order zero gives

\[
 \boxed{\prod_{\eta\in E_t[n]\setminus\{0\}}q_t(\eta)=n^4}
 \quad(5\nmid n).                                      \tag{N4.1}
\]

### Degree two

The three x-coordinates of nonzero two-torsion are the roots of \(f(X)/4\). Hence

\[
 \prod_{\eta\in E_t[2]\setminus\{0\}}Q_5(x(\eta))
 =\frac{f(a)f(b)}{16}.
\]

Using (N4.1),

\[
 c_t^3=16\prod_{\eta\ne0}Q_5(x(\eta))=f(a)f(b)=d^6.       \tag{N4.2}
\]

Degree two alone determines \(c_t/d^2\) only up to a cube root of unity.

### Degree three

The eight nonzero three-torsion points have four x-coordinates, each repeated twice; those coordinates are the roots of \(\psi_3(X)/3\). Therefore

\[
 \prod_{\eta\in E_t[3]\setminus\{0\}}Q_5(x(\eta))
 =\left(\frac{\psi_3(a)\psi_3(b)}9\right)^2.
\]

The \(3^4=81\) in (N4.1) cancels the denominator:

\[
 c_t^8=(\psi_3(a)\psi_3(b))^2=d^{16}.                    \tag{N4.3}
\]

Combining the coprime exponents in (N4.2)-(N4.3),

\[
 \boxed{c_t=(c_t^3)^3/c_t^8=d^{18}/d^{16}=d^2.}           \tag{N4.4}
\]

This closes the scalar-normalization subproblem completely.

## Canonical theta normal form

Equations (N1.2) and (N4.4) prove

\[
 \boxed{
 q_t(z)=\frac{(a-b)^2}{(x(z)-a)(x(z)-b)}
       =\frac{\operatorname{disc}(Q_5)}{Q_5(x(z))}.
 }                                                       \tag{N5.1}
\]

Writing \(S_5=a+b\) and \(P_5=ab\), the symmetric form is

\[
 q_t(z)=\frac{S_5^2-4P_5}{x(z)^2-S_5x(z)+P_5}.            \tag{N5.2}
\]

Thus the formula depends on the unordered fifth-torsion kernel, not a choice between its two x-coordinates. Under a change of generator \(P\mapsto2P\), \(a,b\) swap and the formula is unchanged.

Define a dimensionless elliptic coordinate

\[
 \mathsf X_t(z)=\frac{x(z)-a}{a-b}.
\]

Then

\[
 \boxed{q_t(z)=\frac1{\mathsf X_t(z)(\mathsf X_t(z)+1)}.}   \tag{N5.3}
\]

Swapping \(a,b\) changes \(\mathsf X\) to \(-1-\mathsf X\), leaving (N5.3) fixed. Scaling all Weierstrass x-coordinates by the same nonzero factor also leaves the formula fixed. These field identities are formalized in `H12CanonicalTheta`.

The identities are interpreted meromorphically at their zeros and poles. Numerical pointwise evaluations and group-valued Lean applications use nonzero sampled values.

## An explicit order-five plane-curve normalization

The same calculation places the entire elliptic curve in an order-five normal form without adjoining square roots. Put

\[
 u=-y_b/y_a,\qquad \lambda=y_a/d,
\]

and for an arbitrary point \((x,y)\), define

\[
 X=\frac{x-a}{\lambda^2},\qquad
 Y=\frac{y-y_a-(1-u)\lambda(x-a)}{2\lambda^3}.
\]

Then

\[
 \boxed{Y^2+(1-u)XY-uY=X^3-uX^2,}                        \tag{N6.1}
\]

with \(P=(0,0)\), \(2P=(u,u^2)\), and

\[
 \boxed{q_t(z)=\frac{u^2}{X(z)(X(z)-u)}.}                  \tag{N6.2}
\]

Here is a derivation rather than an assumption of that model. From (N3.2),

\[
 d=-u\lambda^2,\quad y_a=-u\lambda^3,\quad y_b=u^2\lambda^3.
\]

The first tangent slope is \((1-u)\lambda\). Equation (N3.1) therefore gives

\[
 a=\lambda^2(1-6u+u^2)/12.
\]

Writing \(b_2=1-6u+u^2\), \(b_4=u^2-u\), the derivative and curve equation imply

\[
 g_2=\lambda^4(b_2^2/12-2b_4),\quad
 g_3=\lambda^6(-b_2^3/216+b_2b_4/6-u^2).
\]

Substitution proves (N6.1). This coefficient calculation is independently checked symbolically over \(\mathbb Q(u)\) and numerically at the specified analytic lattices. The full geometric change-of-variables theorem is not Lean-formalized in the corresponding source checkpoint.

The parameter \(u\) remains analytically defined. Calling the curve a rational normal form does not assert that \(u\) is an algebraic number at the cubic period.

## The actual cubic inter-chart covariance

Return to

\[
 \beta^3=7,\quad\epsilon=2-\beta,\quad\rho=\epsilon^{-1},
 \quad t=-(\beta^2+2\beta)/15,\quad s=-(\beta+2)/15.
\]

The retained modular relation gives \(\rho\Lambda_s=\Lambda_t\). Since

\[
 \rho=4-15t,\quad\rho/5\equiv-1/5\pmod{\Lambda_t},
\]

scaling of the Weierstrass function gives

\[
 a_s=\rho^2a_t,\quad b_s=\rho^2b_t,\quad c_s=\rho^4c_t,
\]

and hence

\[
 \mathsf X_t(\rho z)=\mathsf X_s(z),\qquad
 \boxed{q_t(\rho z)=q_s(z).}                              \tag{N7.1}
\]

Thus the phase-free theta covariance has a proof through the canonical fifth-torsion normal form as well as its earlier eta-multiplier proof. This statement is about two homothetic elliptic lattices, not an endomorphism of the single lattice \(\Lambda_t\).

## Recovery of every signed unit carry

Use the predecessor's conventions

\[
 w_v=\tfrac13+(b\tau+cs+a)/2,\quad v=(b,c,a)\in\{0,1\}^3,
 \quad T(b,c,a)=(a,b,c),\quad \tau=-t.
\]

Its proved unit carry is

\[
 F(\rho w_v)=F(w_{Tv})B_v,\qquad
 B_v=\prod_{j=0}^{A_v-1}q_t(w_{T^2v}+js),
 \quad A_v=5+4b-2c+7a.
\]

By (N5.3) this now has the exact expression

\[
 \boxed{
 B_v=\prod_{j=0}^{A_v-1}
 \frac1{\mathsf X_t(w_{T^2v}+js)
             (\mathsf X_t(w_{T^2v}+js)+1)}.
 }                                                       \tag{N8.1}
\]

This includes the full normalization of every factor. It does not discard the scalar.

The predecessor's signed gains were, in bit-index order,

\[
 (76,-28,8,0,-16,0,0,0).
\]

When written with the unnormalized denominators \(Q_5\), the corresponding known powers of \(d=a-b\) are

\[
 (152,-56,16,0,-32,0,0,0).
\]

In particular, the aggregate of the three first-order carries retains the factor

\[
 c_t^{-36}=d^{-72}.                                      \tag{N8.2}
\]

It would be false to set this factor to one. Formula (N8.1) incorporates it automatically.

The same substitution works for every oriented three-step return product \(J_{n,v}\) from the predecessor. Consequently ALL seven nontrivial signed-channel limits have finite rational elliptic expressions without a separately supplied eta constant. The first-order limits still have only their guaranteed first-order local cancellation; this normalization change does not upgrade their convergence rate.

These facts use the inherited analytic return theorem. Its limit remains the actual signed gamma value; it has not been independently evaluated in the ray field.

