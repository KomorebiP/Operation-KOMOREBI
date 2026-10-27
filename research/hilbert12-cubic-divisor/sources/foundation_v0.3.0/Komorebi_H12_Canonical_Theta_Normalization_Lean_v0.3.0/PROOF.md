# Canonical fifth-torsion normalization and recovery of the first-order carries

**Version 0.3.0. H12 pure-cubic continuation.**

## Status and scope

The fifth-smoothed theta normalizer is determined exactly by its elliptic fifth-torsion kernel:

\[
 q_t(z)=\frac{\theta_0(z;t)^5}{\theta_0(5z;5t)}
 =\frac{(a-b)^2}{(\wp_t(z)-a)(\wp_t(z)-b)},\qquad
 a=\wp_t(1/5),\quad b=\wp_t(2/5).
\]

Thus the previously separate eta constant is the discriminant of the monic quadratic kernel polynomial. This is an exact complex identity, not just a norm or an equality up to a root of unity. It makes the first-order signed carries, as well as the higher-order ones, rational in explicitly normalized elliptic coordinates. It does not evaluate those analytic coordinates or the resulting limits in the separate ray field.

The new formal core contains 26 additional theorem constants. Together with the unchanged 83 inherited theorem statements, all 109 compile and have their transitive axiom dependencies audited. The elliptic divisor dictionary, analytic multiplication formulas, and identification of elliptic torsion with the polynomial hypotheses remain ordinary mathematical inputs, not Lean axioms. No gamma-arithmetic power equality is proved, no interval certificate is claimed, and no literature priority claim is made.

## 1. Analytic input and conventions

Let \(t\) be any point of the upper half-plane and \(E_t=\mathbb C/(\mathbb Z+\mathbb Zt)\). The classical product convention is [1]

\[
 \theta_0(z;t)=\prod_{n\ge0}(1-e^{2\pi i(z+nt)})(1-e^{2\pi i((n+1)t-z)}).
\]

Retain from the preceding multiplication-norm proof:

\[
 \operatorname{div}(q_t)=4[0]-[P]-[-P]-[2P]-[-2P],\qquad P=1/5,
\]

and, for \(n\) prime to five,

\[
 \prod_{\eta\in E_t[n]}q_t(z+\eta)=q_t(nz).                  \tag{1.1}
\]

The scalar in (1.1) is exactly one. This is important: an unspecified norm multiplier would not suffice below. The inherited proof derives (1.1) from the theta product by finite real root-of-unity averaging and vertical residue splitting. This block also tests it at the required nonzero two- and three-torsion points independently of the rational formula.

The normalization can also be checked directly here. Finite root averaging gives

\[
 \prod_{a=0}^{n-1}\theta_0(w+a/n;t)=\theta_0(nw;nt).
\]

Next, splitting the two defining products into vertical residues gives

\[
 \prod_{b=0}^{n-1}\theta_0(nz+bt;nt)=\theta_0(nz;t).
\]

For the smoothing denominator, multiplication by five permutes the real residues modulo n; the same two steps apply with period 5t. The numerator becomes \(\theta_0(nz;t)^5\) and the denominator becomes \(\theta_0(5nz;5t)\). This proves (1.1) with no omitted multiplier and without using the unknown scalar \(c_t\).


Write

\[
 x(z)=\wp_t(z),\quad y(z)=\wp_t'(z),\quad
 f(X)=4X^3-g_2X-g_3.
\]

The classical equation is \(y(z)^2=f(x(z))\). The addition and duplication laws used below are those of this convention [2]. In particular the y-coordinate here is the full Weierstrass derivative, not its half.

Set

\[
 a=x(P),\quad b=x(2P),\quad d=a-b,\quad y_a=y(P),\quad y_b=y(2P),
\]

\[
 Q_5(X)=(X-a)(X-b).
\]

All of \(d,y_a,y_b\) are nonzero: a point of exact order five is neither two-torsion nor equal up to sign to its double. Comparing divisors yields a nonzero scalar \(c_t\) with

\[
 q_t(z)=c_t/Q_5(x(z)).                                    \tag{1.2}
\]

Also \(q_t(z)\sim c_tz^4\) at zero. The problem in this block is to determine this scalar exactly without a choice of cube root or eta multiplier.

## 2. A scalar is fixed by two coprime norm exponents

Suppose two nonzero elliptic functions with the same divisor differ by a scalar \(r\), and both satisfy the exactly normalized degree-two and degree-three multiplication laws. On the degree-four and degree-nine fibers those laws imply

\[
 r^4=r,\qquad r^9=r.
\]

Thus \(r^3=r^8=1\), and

\[
 r=(r^3)^3/r^8=1.                                       \tag{2.1}
\]

More generally, if \(c^3=A\) and \(c^8=B\) with \(c\ne0\), then

\[
 \boxed{c=A^3/B.}                                       \tag{2.2}
\]

This is a uniqueness and recovery statement within a fixed divisor class. It does NOT say that arbitrary functions are determined by two norms. In particular it does not contradict the nonconstant norm-one factor established in the preceding note.

The commutative-group statements (2.1)-(2.2), including uniqueness and the fixed-norm conditions, are formalized in `H12CoprimeNormalization`.

## 3. The fifth-torsion ordinate identity

Since \(2P\) doubles to \(4P=-P\), let \(\ell,m\) be the full-y tangent slopes at \(P,2P\). The addition law gives

\[
 \ell^2=4(2a+b),\quad m^2=4(a+2b),
\]

\[
 \ell d=y_a+y_b,\qquad md=y_a-y_b.                       \tag{3.1}
\]

Subtract the squares of the last two equalities:

\[
 4y_ay_b=(\ell^2-m^2)d^2=4d^3.
\]

Therefore

\[
 \boxed{y_ay_b=d^3,\qquad f(a)f(b)=d^6.}                 \tag{3.2}
\]

The polynomial implication from (3.1) to (3.2) is formalized. The fact that the actual elliptic points satisfy (3.1) is supplied by the ordinary group-law argument here, not by an undeclared formal assumption.

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
 \boxed{\psi_3(a)\psi_3(b)=-d^8.}                        \tag{3.3}
\]

The minus sign in (3.3) is retained. It disappears only after the square used below.

## 4. Evaluate both scalar powers without ambiguity

Let \(z\to0\) in (1.1). The fourth-order zero gives

\[
 \boxed{\prod_{\eta\in E_t[n]\setminus\{0\}}q_t(\eta)=n^4}
 \quad(5\nmid n).                                      \tag{4.1}
\]

### Degree two

The three x-coordinates of nonzero two-torsion are the roots of \(f(X)/4\). Hence

\[
 \prod_{\eta\in E_t[2]\setminus\{0\}}Q_5(x(\eta))
 =\frac{f(a)f(b)}{16}.
\]

Using (4.1),

\[
 c_t^3=16\prod_{\eta\ne0}Q_5(x(\eta))=f(a)f(b)=d^6.       \tag{4.2}
\]

Degree two alone determines \(c_t/d^2\) only up to a cube root of unity.

### Degree three

The eight nonzero three-torsion points have four x-coordinates, each repeated twice; those coordinates are the roots of \(\psi_3(X)/3\). Therefore

\[
 \prod_{\eta\in E_t[3]\setminus\{0\}}Q_5(x(\eta))
 =\left(\frac{\psi_3(a)\psi_3(b)}9\right)^2.
\]

The \(3^4=81\) in (4.1) cancels the denominator:

\[
 c_t^8=(\psi_3(a)\psi_3(b))^2=d^{16}.                    \tag{4.3}
\]

Combining the coprime exponents in (4.2)-(4.3),

\[
 \boxed{c_t=(c_t^3)^3/c_t^8=d^{18}/d^{16}=d^2.}           \tag{4.4}
\]

This closes the scalar-normalization subproblem completely.

## 5. Canonical theta normal form

Equations (1.2) and (4.4) prove

\[
 \boxed{
 q_t(z)=\frac{(a-b)^2}{(x(z)-a)(x(z)-b)}
       =\frac{\operatorname{disc}(Q_5)}{Q_5(x(z))}.
 }                                                       \tag{5.1}
\]

Writing \(S_5=a+b\) and \(P_5=ab\), the symmetric form is

\[
 q_t(z)=\frac{S_5^2-4P_5}{x(z)^2-S_5x(z)+P_5}.            \tag{5.2}
\]

Thus the formula depends on the unordered fifth-torsion kernel, not a choice between its two x-coordinates. Under a change of generator \(P\mapsto2P\), \(a,b\) swap and the formula is unchanged.

Define a dimensionless elliptic coordinate

\[
 \mathsf X_t(z)=\frac{x(z)-a}{a-b}.
\]

Then

\[
 \boxed{q_t(z)=\frac1{\mathsf X_t(z)(\mathsf X_t(z)+1)}.}   \tag{5.3}
\]

Swapping \(a,b\) changes \(\mathsf X\) to \(-1-\mathsf X\), leaving (5.3) fixed. Scaling all Weierstrass x-coordinates by the same nonzero factor also leaves the formula fixed. These field identities are formalized in `H12CanonicalTheta`.

The identities are interpreted meromorphically at their zeros and poles. Numerical pointwise evaluations and group-valued Lean applications use nonzero sampled values.

## 6. An explicit order-five plane-curve normalization

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
 \boxed{Y^2+(1-u)XY-uY=X^3-uX^2,}                        \tag{6.1}
\]

with \(P=(0,0)\), \(2P=(u,u^2)\), and

\[
 \boxed{q_t(z)=\frac{u^2}{X(z)(X(z)-u)}.}                  \tag{6.2}
\]

Here is a derivation rather than an assumption of that model. From (3.2),

\[
 d=-u\lambda^2,\quad y_a=-u\lambda^3,\quad y_b=u^2\lambda^3.
\]

The first tangent slope is \((1-u)\lambda\). Equation (3.1) therefore gives

\[
 a=\lambda^2(1-6u+u^2)/12.
\]

Writing \(b_2=1-6u+u^2\), \(b_4=u^2-u\), the derivative and curve equation imply

\[
 g_2=\lambda^4(b_2^2/12-2b_4),\quad
 g_3=\lambda^6(-b_2^3/216+b_2b_4/6-u^2).
\]

Substitution proves (6.1). This coefficient calculation is independently checked symbolically over \(\mathbb Q(u)\) and numerically at the specified analytic lattices. The full geometric change-of-variables theorem is not Lean-formalized in this release.

The parameter \(u\) remains analytically defined. Calling the curve a rational normal form does not assert that \(u\) is an algebraic number at the cubic period.

## 7. The actual cubic inter-chart covariance

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
 \boxed{q_t(\rho z)=q_s(z).}                              \tag{7.1}
\]

Thus the phase-free theta covariance has a proof through the canonical fifth-torsion normal form as well as its earlier eta-multiplier proof. This statement is about two homothetic elliptic lattices, not an endomorphism of the single lattice \(\Lambda_t\).

## 8. Recovery of every signed unit carry

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

By (5.3) this now has the exact expression

\[
 \boxed{
 B_v=\prod_{j=0}^{A_v-1}
 \frac1{\mathsf X_t(w_{T^2v}+js)
             (\mathsf X_t(w_{T^2v}+js)+1)}.
 }                                                       \tag{8.1}
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
 c_t^{-36}=d^{-72}.                                      \tag{8.2}
\]

It would be false to set this factor to one. Formula (8.1) incorporates it automatically.

The same substitution works for every oriented three-step return product \(J_{n,v}\) from the predecessor. Consequently ALL seven nontrivial signed-channel limits have finite rational elliptic expressions without a separately supplied eta constant. The first-order limits still have only their guaranteed first-order local cancellation; this normalization change does not upgrade their convergence rate.

These facts use the inherited analytic return theorem. Its limit remains the actual signed gamma value; it has not been independently evaluated in the ray field.

## 9. What is, and is not, resolved

Resolved in this block:

- the exact complex theta scalar, including its root-of-unity ambiguity;
- rational normalization of the previously non-normalization-free first-order carries;
- an unordered-kernel formula and an explicit order-five curve model;
- an independent geometric route to the retained theta covariance.

Still unresolved:

\[
 \lim_m D_m=\epsilon^6/U_{\mathrm{alg}}^3,
\]

as an independent arithmetic evaluation. The inherited analytic theorem supplies \(\lim D_m=\epsilon^6/U_\Gamma^3\), not the displayed arithmetic identity. Nor have the seven signed-channel limits been evaluated in that arithmetic realization.

The two-norm scalar argument cannot be applied to \(U_\Gamma/U_{\mathrm{alg}}\) without establishing the corresponding functional comparison. Here it applies to two elliptic functions with the same divisor and two exact norm laws. A comparison to a proposed gamma special value does not yet satisfy those hypotheses.

The preceding phase deformation remains a valid demonstration that a selected set of finite snapshot constraints is insufficient. This block adds exact theta normalization data; it does not construct an arithmetic packet satisfying every actual carried identity and the common zero anchor.

## 10. Formal verification boundary

New modules:

| Module | Theorems | Scope |
|---|---:|---|
| H12CoprimeNormalization | 8 | Scalar recovery from powers 3 and 8; fixed norm equations; uniqueness |
| H12FifthTorsionAlgebra | 8 | Explicit tangent/ordinate and division-polynomial implications over fields |
| H12CanonicalTheta | 10 | Field normalizer, canonical coordinate, symmetry and scale identities |

The 83 inherited theorem statements and proofs are unchanged. All 109 are recompiled with Lean 4.34.0-rc2 and pinned Mathlib, using one worker and warnings as errors. Their transitive axiom reports are checked against `propext`, `Classical.choice`, and `Quot.sound`. No project axioms, admitted proofs, native decision escape, or unsafe declarations are used. A false integer equality must be rejected.

The formal sources keep the torsion and norm polynomial equalities as explicit hypotheses. The analytic argument establishing them is the ordinary proof above. There is no claim of a formalized theory of elliptic gamma, meromorphic divisors, or the missing arithmetic comparison.

## 11. Computational verification

`checks/exact_checks.py` verifies the displayed polynomial identities, resultants, an independent universal order-five family over \(\mathbb Q(u)\), the normalization gains, and finite carry regressions. Infinite quantifiers about the inherited carry recurrence remain covered by its Lean induction, not by bounded tests.

`checks/numerical_checks.py` uses direct Jacobi theta derivatives for \(\wp,\wp'\), independently summed Eisenstein series for \(g_2,g_3\), and direct theta products. It checks two generic lattices and the actual cubic lattice. The actual gamma carry is evaluated through the unchanged guarded predecessor series and continuation. No \(U_{\mathrm{alg}}\) is evaluated or fitted.

Numerical checks use requested precisions 40 and 70, each with 25 guard digits. Their normalized equality tolerance is \(10^{-d+8}\). They are floating-point regressions, not directed-rounding enclosures. Negative controls retain a spurious cube-root normalization, omit the known first-order scalar, change its sign, and erase its complex phase.

Commands, exact counts, failures, runtimes, hashes, and clean-extraction replay results are recorded in `evidence/` and `MANIFEST.json`.

## References and inherited sources

[1] Bergeron, Charollois, Garcia, *Elliptic units for complex cubic fields (On Eisenstein's Jugendtraum)*, arXiv:2311.04110v2. Product and continuation conventions and the original cubic example. https://arxiv.org/html/2311.04110v2

[2] NIST DLMF, sections 23.2 and 23.10. Weierstrass equation, periodicity, addition and duplication. https://dlmf.nist.gov/23.2 and https://dlmf.nist.gov/23.10

[3] The retained Signed Unit Transport v0.2.0 proof, copied under `prior/`, and its cited Norm Projector and Doubling Norm Descent notes. They provide the normalized multiplication laws and actual carried gamma return used here. The predecessor archive and unchanged source hashes are recorded.

[4] Lean language reference, Elaboration and Compilation. https://lean-lang.org/doc/reference/latest/Elaboration-and-Compilation/

The elementary algebraic normalization argument is proved above. Its role in this research continuation is asserted; a claim of historical novelty is not.
