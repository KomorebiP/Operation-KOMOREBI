# A Closing Test for the Pure Cubic Hilbert 12 Comparison

**Author:** Komorebi P.

**Result:** The analytic to arithmetic equality is not proved. This continuation proves an exact obstruction to inferring the missing phase from finite torsion transport, and supplies a fresh rational interval certificate that resolves the sign and branch questions conditional on an exact phase theorem.

## 1. The statement being tested

Put

\[
\omega=e^{2\pi i/3},\quad \beta=7^{1/3}\omega^2,\quad
\varepsilon=2-\beta,\quad \rho=\varepsilon^{-1}=\beta^2+2\beta+4,
\]

\[
\tau=(\beta^2+2\beta)/15,\quad t=-\tau,\quad s=-(\beta+2)/15.
\]

The independently specified analytic value is

\[
U_\Gamma=F(1/3),\qquad
F(z)=\Gamma_{\mathrm{ell}}(z;\tau,s)^5/
\Gamma_{\mathrm{ell}}(5z;5\tau,5s).
\]

The desired equality is \(U_\Gamma=U_{\mathrm{alg}}\), where the algebraic candidate below is defined without using a numerical gamma value.

The previous research supplies a modulus comparison and the normalized contracting theta equations. The present note does not independently reprove the modulus theorem. Any closing lemma using that theorem is expressly conditional on that inherited input.

The primary BCG paper distinguishes its conjectured algebraicity and complex reciprocity from its proved logarithmic modulus formula. Gray's congruence independence theorem does not assert the algebraicity of the special value. Neither theorem is being strengthened by citation alone.

## 2. Independent arithmetic target

Set \(J=2+3\omega\), \(\bar J=-1-3\omega\), and

\[
\chi(1),\ldots,\chi(6)=(1,\omega,\omega^2,\omega^2,\omega,1).
\]

Define the selected Gauss branch by

\[
\xi=\frac1\beta\sum_{a=1}^6\chi(a)e^{6\pi ia/7}.
\]

A finite polynomial calculation gives \(\xi^3=J\). Define

\[
\nu=(\xi+\beta/\xi-\beta^2)/3,\qquad
v=-\beta^2\nu-2\nu^2,
\]

\[
Y=(4\beta^2+\beta-14)v^2+(11\beta-23)v-\beta^2+3\beta-3,
\]

\[
Z=\frac{(-2\beta^2+7\beta-8)v^2+(-10\beta^2+11\beta+17)v}{3}
+7-\beta-\beta^2,
\]

\[
U_{\mathrm{alg}}=\frac{Y-(1+2\omega)Z}{2}.
\]

The attached exact polynomial certificate rechecks

\[
v^3-\beta v^2+1=0,\quad Y^2-4=-3Z^2,
\]

and

\[
R(Y)=Y^3+(6\beta^2-14\beta+2)Y^2
 +(4\beta^2-6\beta-1)Y+94\beta^2-124\beta-107=0.
\]

It also checks the original reciprocal sextic \(Q(U_{\mathrm{alg}})=0\), where \(Q(U)=U^3R(U+U^{-1})\). These are identities in finite polynomial quotients, separate from the analytic evaluation.

## 3. The weighted return is not the unweighted permutation

Retain the full ambient packet \(V=(\mathbb Z/7)^3\) with arguments

\[
z_x=\frac13+k\frac{\tau+2s+4}{7}+\ell\frac{s+2}{7}+\frac j7,
\qquad x=(k,\ell,j).
\]

The inverse unit induces

\[
T(k,\ell,j)=(4k+5\ell+j,\,4\ell+5j,\,4j)\pmod7.
\]

Thus \(T^{21}=1\), and the orbit decomposition is \(1+2\cdot3+16\cdot21\). The zero label is fixed.

The inherited theta transport has the form

\[
f_m(x)=F(\rho^m z_x),\qquad
f_m(x)=C_m(x)f_{m-1}(Tx),
\]

where \(C_m\) is an explicit finite product of theta quotients. The packet avoids the divisor, so all entries are nonzero. In particular \(f_m(x)\to\varepsilon^2\) for every label.

Let

\[
(Pg)(x)=g(Tx),\qquad D_m=\operatorname{diag}(f_m(x)),\qquad
A_m=\operatorname{diag}(C_m(x))P.
\]

### Weighted return theorem

For any positive integer \(n\),

\[
\boxed{A_nA_{n-1}\cdots A_1=D_nP^nD_0^{-1}.}
\]

In particular,

\[
\boxed{A_{21}\cdots A_1=D_{21}D_0^{-1}.}
\]

**Proof.** The defining transport identity gives
\(A_m=D_mPD_{m-1}^{-1}\). Adjacent diagonal matrices cancel in the product. At 21 steps, \(P^{21}=I\). This proves both formulas. No arithmetic evaluation of \(F\) is used.

The distinguished diagonal entry of the 21 step return is therefore

\[
\boxed{\frac{F(\rho^{21}/3)}{F(1/3)},}
\]

not one. At 21 times an increasing integer, it tends to

\[
\frac{\varepsilon^2}{U_\Gamma}.
\]

The contracting return retains the unknown initial value. The finite order of the label permutation does not make the weighted return finite order and does not put \(U_\Gamma/U_{\mathrm{alg}}\) in a group of roots of unity.

For a single step, the characteristic polynomial also makes the dependence explicit:

\[
\det(\lambda I-A_m)
=(\lambda-C_m(0))
\prod_{|\mathcal O|=3}\left(\lambda^3-\prod_{x\in\mathcal O}C_m(x)\right)
\prod_{|\mathcal O|=21}\left(\lambda^{21}-\prod_{x\in\mathcal O}C_m(x)\right).
\]

The cycle weights are analytic theta products, not automatically one or algebraic numbers.

## 4. Fourier transformation does not remove the fixed block

Let \(E_0\) be the projector onto the zero label. Because \(T0=0\),

\[
\boxed{E_0A_m=A_mE_0=C_m(0)E_0.}
\]

Consequently the target obeys its own scalar recurrence:

\[
\boxed{f_m(0)=C_m(0)f_{m-1}(0).}
\]

In the Fourier coordinates

\[
\widehat f(a)=\sum_{x\in V}\zeta_7^{a\cdot x}f(x),
\]

this projector is the averaging projector onto constant vectors. Summing the exact Fourier convolution equation gives

\[
\boxed{
\frac1{343}\sum_a\widehat f_m(a)
=C_m(0)\frac1{343}\sum_a\widehat f_{m-1}(a).
}
\]

**Proof.** The sum \(\sum_a\zeta_7^{a\cdot x}\) is 343 at \(x=0\) and zero otherwise. Equivalently, \(\sum_a\widehat C_m(a-b)=343 C_m(0)\) for every \(b\). Apply this to the convolution formula.

Thus apparent coupling of Fourier coordinates does not create a new relation between the target fixed label and the moving torsion labels. Each arithmetic orbit is an invariant block before the change of basis. Relations between those blocks would require an additional identity, not merely their reexpression in Fourier coordinates.

This is a restriction on this particular transport argument. It is not a claim that the full geometric gamma construction has no further identities.

## 5. What the endpoint does and does not fix

For the *prescribed* theta multipliers, the common endpoint fixes the solution uniquely.

### Uniqueness lemma

Suppose \(f_m\) and \(g_m\) are nonzero solutions with identical \(C_m\), and both tend to the same nonzero constant. Then \(f_0=g_0\).

**Proof.** Their quotient satisfies \(r_m(x)=r_{m-1}(Tx)\), so \(r_{21q}(x)=r_0(x)\). Its limit is one. Hence \(r_0(x)=1\) for all \(x\).

There is therefore no arbitrary analytic phase once all the actual theta data and the endpoint are fixed. The unresolved task is to identify that unique analytic answer with the independent arithmetic value.

Conversely, the finite order and endpoint *without* the actual theta weights do not force a root of unity. For a countermodel, choose real \(\theta\) and set

\[
f_m(0)=e^{i\theta2^{-m}},\qquad f_m(x)=1\quad(x\ne0).
\]

Define \(C_m(x)=f_m(x)/f_{m-1}(Tx)\). All entries converge to one, the same order 21 permutation acts, and the product over all nonzero labels is one. Every entry has modulus one. Yet \(f_0(0)=e^{i\theta}\) can have infinite order, for example with \(\theta=\pi\sqrt2/10^{100}\). This example also makes the initial phase arbitrarily close to one without making it a root of unity.

This countermodel is **not** a deformation of the prescribed elliptic gamma function or its fixed theta multipliers. It disproves only the inference from finite permutation order, unit modulus, the untwisted norm, and a normalized endpoint to a finite phase ambiguity.

## 6. A fresh rational interval certificate

The analytic and algebraic values were enclosed independently using exact integer endpoint intervals with common denominator \(S=2^{224}\). There is no binary floating point in the certified calculation. Timing output alone uses ordinary floating point.

The certificate proves

\[
\boxed{\left|\frac{U_\Gamma}{U_{\mathrm{alg}}}-1\right|<10^{-60},}
\]

and

\[
\boxed{\operatorname{Re}\left[\left(\frac{U_\Gamma}{U_{\mathrm{alg}}}\right)^3\right]>\frac12.}
\]

The latter formula means the real part of the complex cube. The imaginary part of that cube is enclosed in an interval containing zero. It is **not** proved equal to zero.

### 6.1 Exact elementary function enclosures

For each real arithmetic operation the endpoints are rounded outwards using integer floor and ceiling division. Rectangular complex operations are assembled from these intervals.

The real cube root of seven is enclosed by integer bisection: if \(a=\lfloor(7S^3)^{1/3}\rfloor\), its enclosure is \([a/S,(a+1)/S]\). The square root of three is enclosed by integer square roots. This gives \(\omega=-1/2+i\sqrt3/2\) and the specified \(\beta\).

Pi is enclosed using Machin's identity

\[
\pi=16\arctan(1/5)-4\arctan(1/239).
\]

Each arctangent uses 130 terms of its alternating rational series, with the next term bounding the remainder. All coefficients and endpoints are rational.

For a complex exponential, scale the argument by a power of two until its real and imaginary interval bounds give \(|z|\le1/2\). Sum through degree 72 and pad both components by

\[
\frac{2}{73!}.
\]

This bound is valid because the complex Taylor remainder is at most
\(e^{1/2}(1/2)^{73}/73!<2/73!\). Repeated interval squaring reverses the scaling. Thus exponential values are enclosed, not rounded to nearest and then treated as exact.

### 6.2 Infinite gamma series

Put \(P=e^{2\pi it}\) and \(Q=e^{2\pi is}\). The series at the fixed point is

\[
\log U_\Gamma=-5\sum_{\substack{n\ge1\\5\nmid n}}
\frac{P^n\omega^n-Q^n\omega^{-n}}{n(1-P^n)(1-Q^n)}.
\]

The interval computation establishes

\[
|P|<471/500,\qquad |Q|<1/2.
\]

For \(r=471/500\), \(q=1/2\), and a truncation after \(N\) terms, an absolute tail bound is

\[
\boxed{\frac{10r^{N+1}}{(N+1)(1-r)^2(1-q)}.}
\]

Indeed, bound the two numerator terms by \(2r^n\), the denominator factors below by \((1-r)(1-q)\), replace \(1/n\) by \(1/(N+1)\), and sum the geometric tail. Omitting the exclusion of multiples of five only enlarges this bound.

The accepted run used \(N=3000\). A separate replay used \(N=3400\). Both prove the displayed \(10^{-60}\) bound.

### 6.3 A directly checkable integer inequality

In the first certificate the real endpoints of \(U_\Gamma/U_{\mathrm{alg}}\), multiplied by \(S\), are

```
26959946667150639794667015087019630673637144422540572481103607072375
26959946667150639794667015087019630673637144422540572481103613415907
```

The imaginary endpoints, multiplied by the same \(S\), are

```
-1997471
 1991305
```

The common denominator is

```
26959946667150639794667015087019630673637144422540572481103610249216
```

The squared distance from one is therefore at most

\[
\frac{14082209135122}{S^2}<10^{-120}.
\]

The certificate records these integers and the factorized exact series tail. The second run independently encloses the ratio with a slightly different interval and proves the same bound.

### 6.4 Negative control

Repeating the analytic interval computation at \(z=1/4\) gives

\[
\left|F(1/4)/U_{\mathrm{alg}}-1\right|>1/100.
\]

Thus the comparison routine does not return the algebraic target at an arbitrary nearby rational argument. This is a certified separation, not a decimal residual test.

## 7. The exact closing lemma

Let

\[
\mathcal R=U_\Gamma/U_{\mathrm{alg}}.
\]

Assume the inherited exact modulus comparison, so \(|\mathcal R|=1\). Then the newly certified branch and sign bounds show that the single identity

\[
\boxed{\operatorname{Im}(\mathcal R^3)=0}
\]

would finish the comparison.

**Proof.** Reality and \(\operatorname{Re}(\mathcal R^3)>1/2\) make \(\mathcal R^3\) positive real. Since it has modulus one, it equals one. The two nontrivial cube roots of unity have distance \(\sqrt3\) from one, while the interval certificate places \(\mathcal R\) within \(10^{-60}\). Hence \(\mathcal R=1\).

The unresolved identity is exactly the phase assertion. Neither an interval containing zero nor the 21 step permutation order proves it.

A valid future use of the uniqueness lemma would be to construct, independently from the arithmetic candidate, a family satisfying the **same actual theta multipliers** and the **same endpoint**. Merely defining that family from the gamma product and then attaching the candidate's name would be circular.

## 8. A check on a second tempting route

The earlier ambient cyclic cubic uses

\[
d(X)=\frac{X^3-\beta X^2+1}{(\beta^2X-4)(\beta^2X-5)},
\qquad v_\Gamma(z)=h(F(z)+F(z)^{-1}).
\]

The desired arithmetic fiber is \(d_\Gamma(1/3)=0\). At the contracting endpoint, however,

\[
F(0)=\varepsilon^2,\qquad
Y(0)=\varepsilon^2+\rho^2=13\beta^2+19\beta+48,
\]

and exact reduction gives

\[
\boxed{
d_\Gamma(0)=
-\frac{6740317537\beta^2+84451919479\beta-314492957513}
{2858923851828}\ne0.
}
\]

The numerator is a nonzero polynomial of degree at most two in a degree three generator. Thus bare contraction does not select the required zero fiber. The Möbius orbit invariance established in the earlier note is not invariance under the analytic argument change \(z\mapsto\rho z\). Confusing those two actions would be a false closing step.

## 9. Verification scope and failed attempts

The inherited seven packet, full torsion, and ambient cubic symbolic verifiers were replayed in exact mode. The new arithmetic certificate checks the independently specified target, including its original sextic. The new transport audit checks all 343 return positions, all 343 fixed projector tests, and all 343 finite Fourier orthogonality relations. General proofs are given above and are not replaced by these tests.

The interval engine uses standard library integer and rational arithmetic, with 71 elementary arithmetic selftests. It has not been formally verified in Lean or independently audited by a separate reviewer. Its certification claim is a reproducible computer assisted enclosure using the explicitly proved error bounds, not a formal kernel certificate.

Two implementation attempts failed before the accepted runs. An optional python-flint installation could not proceed because the environment could not resolve the package server. It is not a dependency of the accepted calculation. The first interval report used a fixed denominator to round the squared error, producing an unnecessarily coarse \(10^{-33}\) bound and failing the requested precision assertion. Computing the endpoint distance with exact integer squares over \(S^2\) removed that artificial loss. The accepted runs and certificates use the corrected method.

The mathematical closing attempt failed at a separate and substantive step: the weighted 21 step return is an endpoint ratio, not finite monodromy of the scalar value. The sign and branch are now bounded directly, but the exact phase identity has not been obtained.

## Sources

1. Nicolas Bergeron, Pierre Charollois, and Luis E. Garcia, *Elliptic units for complex cubic fields*, arXiv:2311.04110v2. Product conventions, pure cubic special value, conjectural algebraicity, and the logarithmic modulus formula.
2. Teymour Gray, *Cocycle Relations and Elliptic Gamma Values*, arXiv:2610.10365v2, 19 October 2026. Congruence independence under the stated hypotheses. No scalar algebraicity assertion is imported.
3. Komorebi P., *Contracting Arithmetic Torsion and Theta Transport in the Pure Cubic Hilbert 12 Test*, retained source attachment. Full packet, carries, and theta recurrence.
4. Komorebi P., *An Ambient Cyclic Cubic and the Elliptic Gamma Fourier Obstruction*, retained source attachment. Rational coordinate, invariant, and algebraic model.

No claim of literature novelty is made for weighted permutation identities, Fourier projectors, or the interval methodology.
