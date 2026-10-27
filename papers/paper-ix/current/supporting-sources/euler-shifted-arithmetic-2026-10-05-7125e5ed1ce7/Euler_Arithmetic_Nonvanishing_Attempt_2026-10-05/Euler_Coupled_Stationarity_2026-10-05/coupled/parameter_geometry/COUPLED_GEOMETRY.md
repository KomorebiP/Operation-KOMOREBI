# Coupled stationary motion and value cancellation

Date: 2026-10-05. Base: `Euler-regular-address-critical-phases-20261005`.

The coupled equations have a unit Jacobian after the correct division of the stationary equation. Their local geometry is an ordinary quadratic fold. In the finite affine model, the stationary point moves by seven extra dyadic bits while the critical value changes isometrically in the parameter. This explains the coupling without asserting a global analytic interpolation of the actual Euler family.

## 1. Precisely which object is analytic

The inherited 629-bit uniform certificate uses

\[
B(T)=17659+2^{18}T,\qquad
r(T)=B(T)2^{640}-161,\qquad x=10202+2^{15}Z.
\]

For admissible ordinary integer \(T\), meaning positive odd \(B(T)\) and certified actual terminal 161, define the exact fixed-depth series

\[
K_T(Z)=2^{-178}G_{r(T)}(10202+2^{15}Z).
\]

The inherited coefficientwise theorem is

\[
B(T)K_T(Z)\equiv H(T,Z):=H_0(Z)+T H_1(Z)\pmod{2^{451}}.
\tag{1}
\]

Choose the stored integral polynomial representatives for \(H_0,H_1\). Their exact analytic model is used below. Changing representatives modulo \(2^{451}\) changes the far digits of its exact critical parameter, so that parameter is not identified with an exact singular member of the actual Euler family.

The stored coefficient valuations begin

\[
\begin{aligned}
v_2[Z^n]H_0&=(0,3,0,8,19,28,39,\ldots),\\
v_2[Z^n]H_1&=(0,8,25,42,58,74,90,\ldots).
\end{aligned}
\tag{2}
\]

All coefficients of \(H_0\) of degree at least three are divisible by \(2^8\); all coefficients of \(H_1\) of degree at least two are divisible by \(2^{25}\). The quadratic coefficient of \(H_0\) is 3 modulo 8. These are exact stored-model coefficient checks, reproduced by the accompanying script.

## 2. The coupled system has a unit Jacobian

Put

\[
Q(T,Z)=\frac12 H_Z(T,Z)=Q_0(Z)+TQ_1(Z).
\]

This division is coefficientwise integral. The reductions are

\[
H(T,Z)\equiv1+T+Z^2\pmod2,
\qquad Q(T,Z)\equiv Z\pmod2.
\]

The Jacobian with respect to \((T,Z)\) is

\[
J=\begin{pmatrix}
H_1&H_Z\\
H_1'/2&H_{ZZ}/2
\end{pmatrix}
\equiv
\begin{pmatrix}1&0\\0&1\end{pmatrix}\pmod2.
\tag{3}
\]

It is a unit matrix modulo two everywhere. The pair \((H,Q)\) has the unique binary zero \((1,0)\), and therefore a unique exact dyadic zero for each chosen integral model lift. In particular, a double zero in \(Z\) is not a degenerate zero of the coupled two-variable system.

Without dividing the stationary equation by two, the Jacobian determinant at a simultaneous zero has valuation one. The division in (3) removes exactly that normalization loss.

## 3. Exact stationary motion in the affine model

For every \(T\in\mathbb Z_2\), there is a unique stationary point \(c(T)\) with

\[
Q(T,c(T))=0.
\]

More strongly, \(c\in\mathbb Z_2\langle T\rangle\). To see this directly, solve the equation for its linear \(Z\) term: that coefficient is a unit of the restricted parameter algebra, all nonlinear \(Z\) coefficients are even, and its constant term lies in \(4\mathbb Z_2\langle T\rangle\). The resulting map is a strict contraction on that algebra. Thus \(c(T)\in4\mathbb Z_2\langle T\rangle\); the recorded calculation gives \(c(T)\equiv20\pmod{128}\).

On this curve, set

\[
a=H_{ZZ}(T,c(T)),\quad b=H_1'(c(T)),\quad
 d=H_{ZZZ}(T,c(T)),\quad e=H_1''(c(T)).
\]

The coefficient gaps in (2) give uniformly

\[
v_2(a)=1,\quad v_2(b)=8,\quad v_2(d)=9,\quad v_2(e)=26.
\tag{4}
\]

Implicit differentiation gives

\[
c'(T)=-b/a,\qquad v_2(c')=7.
\tag{5}
\]

There is also the stronger exact two-point law

\[
\boxed{v_2(c(T)-c(S))=7+v_2(T-S)\qquad(T\ne S).}
\tag{6}
\]

Indeed the difference quotient of \(Z\mapsto Q(T,Z)\) is always a unit, while \(Q_1(c(S))=H_1'(c(S))/2\) has valuation seven. Subtracting the two stationary equations proves (6). This avoids inferring a global isometry from a pointwise derivative claim alone.

## 4. Critical-value curvature comes from stationary motion

Define the model critical value

\[
\Psi(T)=H(T,c(T)).
\]

The chain rule simplifies because \(H_Z(T,c(T))=0\):

\[
\Psi'=H_1(c),\qquad
\Psi''=-\frac{b^2}{a},\qquad
\Psi'''=\frac{3e b^2}{a^2}-\frac{d b^3}{a^3}.
\tag{7}
\]

Consequently

\[
\boxed{v_2(\Psi')=0,\qquad v_2(\Psi'')=15,\qquad
v_2(\Psi''')=30.}
\tag{8}
\]

For the third derivative, the two terms have valuations 40 and 30, so cancellation cannot change the asserted value. Thus the curvature is not an independent cancellation effect: it is exactly the product of the source's spatial sensitivity and the moving stationary point.

Coefficientwise, \(\Psi\equiv1+T\pmod2\). Therefore \(\Psi\) is an analytic isometry:

\[
v_2(\Psi(T)-\Psi(S))=v_2(T-S).
\tag{9}
\]

It has one exact dyadic zero \(\tau\) in the chosen model. The parameter is transverse even though the spatial root there is double.

An exact 128-bit Taylor computation at \(T=0\), through order seven, gives

| Derivative order \(n\) | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| \(v_2(c^{(n)}(0))\) | 7 | 22 | 37 | 52 | 67 | 82 | 97 |
| \(v_2(\Psi^{(n)}(0))\) | 0 | 15 | 30 | 45 | 60 | 75 | 90 |

The identities (5) and (7) prove the stated low-order laws uniformly. The seven-order table is an exact bounded computation; it is not promoted to an all-order theorem. Its pattern explains why previous high-order differences suggested a 15-bit curvature scale.

Multiplication by \(B(T)\) matters. The critical value of the divided model is \(\phi(T)=\Psi(T)/B(T)\), not \(\Psi(T)\). The spatial stationary point is unchanged. Since \(B'=2^{18}\), quotient-rule corrections to the second and third derivatives have strictly larger valuations than 15 and 30, respectively, so these low-order curvature valuations also hold for \(\phi\).

## 5. Exact quadratic fold in the chosen model

Let \(u=Z-c(T)\). Taylor expansion at the stationary point gives

\[
H(T,c(T)+u)=\Psi(T)+A(T)u^2+u^3 R(T,u),
\]

where

\[
A(T)=H_{ZZ}(T,c(T))/2\equiv3\pmod8,
\qquad R\in2^8\mathbb Z_2\langle T,u\rangle.
\]

Both square roots in

\[
U=u\sqrt{A(T)/3}\sqrt{1+uR(T,u)/A(T)}
\tag{10}
\]

converge in the restricted integral algebra. The first radicand is 1 modulo 8; the second is 1 modulo \(2^8\). For fixed \(T\), (10) is an analytic isometry in \(u\), with analytic inverse. It gives the exact identity

\[
\boxed{H(T,Z)=\Psi(T)+3U^2.}
\tag{11}
\]

Finally \(V=-\Psi(T)/3\) is an analytic parameter isometry, so the full two-variable change of coordinates gives

\[
\boxed{H=3(U^2-V).}
\tag{12}
\]

This is the coupled normal form. Simultaneous value and derivative cancellation is exactly \(U=V=0\). Nearby roots are governed by whether \(V\) is a dyadic square; the singular member has multiplicity exactly two. The same description can be phrased through the branch \(B_s(Y)=-C(Y)/A(Y)\) in the shallow finite model: its folds are the zeros of \(A C'-C A'\). Equation (12) exhibits the resulting fold after the deep chart's correct scaling.

## 6. What transfers to actual pairs of integer parameters

The exact curves above belong to the chosen affine model. Nevertheless (1) gives rigorous finite-separation laws for pairs of actual admissible ordinary integer parameters.

For each such \(T\), let \(c_T\) be the unique stationary point of the exact fixed-depth series \(K_T\), and let \(\Phi_T=K_T(c_T)\). The coefficient reductions inherited from (1) make \(K_T'/2\) an isometry, so \(c_T\) exists uniquely. Differentiating (1) and dividing by two loses one bit, yielding

\[
c_T\equiv c(T)\pmod{2^{450}},
\qquad
\Phi_T\equiv\Psi(T)/B(T)\pmod{2^{451}}.
\tag{13}
\]

For the value congruence, substituting \(c_T\) instead of \(c(T)\) costs at least 900 bits in the model because its first derivative vanishes and its quadratic coefficient is integral. The original 451-bit model error is therefore the limiting error.

For two distinct actual parameters \(T,S\), set \(e_0=v_2(T-S)\). Then

\[
\boxed{e_0<443\ \Longrightarrow\
v_2(c_T-c_S)=e_0+7.}
\tag{14}
\]

Also

\[
\boxed{e_0<451\ \Longrightarrow\
v_2(\Phi_T-\Phi_S)=e_0.}
\tag{15}
\]

To prove (15), the divided-model difference has numerator

\[
B(S)(\Psi(T)-\Psi(S))-(B(T)-B(S))\Psi(S).
\]

Its first term has valuation \(e_0\), while the second has valuation at least \(e_0+18\). Hence it has exact valuation \(e_0\), and (13) transfers it whenever \(e_0<451\).

The exact fixed-depth Taylor expansion at \(c_T\) has a unit quadratic coefficient and higher coefficients divisible by \(2^8\). Therefore there is also the exact motion-cost identity in valuation form

\[
\boxed{e_0<443\ \Longrightarrow\
v_2\bigl(K_T(c_S)-K_T(c_T)\bigr)=2e_0+14.}
\tag{16}
\]

Thus the actual critical value changes at parameter order \(e_0\), while moving its critical point incurs a quadratic cost of order \(2e_0+14\). These are genuine statements about pairs of actual Euler depths within the stated separation precision. They do not define an all-precision analytic interpolation of the undepleted family.

## What remains

The coupled cancellation geometry is nondegenerate and locally resolved: one parameter direction crosses the singular value, and the spatial direction is quadratic. This does not establish that the exact exceptional parameter is absent from the ordinary positive integers. A dyadic isometry can have an ordinary integer zero. Finite model coefficients and the fold's square-class condition do not supply the missing arithmetic nonintersection theorem.

No new Wronskian lifting, large multiplier search, or Lean compilation was performed. The computation checks the stored coefficient hypotheses, unit Jacobian, and seven Taylor orders, with explicit 128-bit precision. The universal model statements and the bounded-separation actual-pair statements have separate proofs above.
