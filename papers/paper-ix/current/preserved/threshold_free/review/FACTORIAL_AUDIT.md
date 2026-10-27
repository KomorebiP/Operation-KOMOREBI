# Independent audit of the factorial bound for the actual N=4, j=2 packet

Audit date: 2026-10-06.

Primary verdict: **proved as written** for the all-row, all-order factorial difference bound and its mixed-step version. The proof uses finite polynomial identities and an integral moment-functional domain. It does not require a bounded measure, an infinite evaluation, or a generic divided-flat inverse theorem. The analytic interpolation conclusion also follows, with the radius terminology clarified below.

Audited source:

/workspace/scratch/052464f5391e/euler_threshold_free_2026_10_06/combinatorial/factorial_j2/FACTORIAL_J2_PROOF.md

SHA256 of the revision read and checked:

31890deede310c8e207d4322bc85f85caaadbd558d3bb82667c5cd874975442e

The source included Sections 1 through 7. Its hash was unchanged before and after the exact checks. No authored proof or status file was modified. No applicable AGENTS.md or project .mathbox ledger was present. This report is the only file written by this audit.

## 1. Normalized claim and dependency graph

Define
\[
 A(t)=2\sum_{q\ge0}\frac{t^{4q}}{(4q+2)!},\qquad
 C(n)=(4n)![t^{4n}]A(t)^{-1}.
\]
Thus C is the normalized actual j=2 packet, rather than its unnormalized multiple 2C. All indices n,k are nonnegative integers. The positive steps are ordinary natural integers, and
\[
 \Delta_u C(n)=C(n+u)-C(n).
\]
The claims audited are
\[
 v_2(\Delta_u^kC(n))
 \ge k(1+v_2(u))+v_2(k!)
\]
and, for any positive steps \(u_1,\ldots,u_k\),
\[
 v_2(\Delta_{u_1}\cdots\Delta_{u_k}C(n))
 \ge k+v_2(k!)+\sum_i v_2(u_i).
\]
Zero differences have infinite valuation. The empty difference, k=0, asserts C(n) is integral.

The dependencies are:

1. A formal Stirling identity bounds each Bernoulli number by \(2B_m\in\mathbf Z_2\).
2. A finite one-variable functional is integral on \(S^\ell U^r/r!\).
3. Its tensor product is integral on an explicitly specified module of finite polynomials.
4. The actual source factors, giving \(C(n)=\mathcal E(Y^{4n})\).
5. Seven component identities place every \(W^k/k!\) in the integral-evaluation module.
6. The exact difference stencil and Gaussian descent give the step-one factorial estimate.
7. Finite shift-polynomial expansions give arbitrary equal and mixed steps.
8. The initial-row factorial estimate gives ordinary power-series interpolation.

All these leaves are internal exact algebra. No named external theorem is needed.

## 2. Independent reconstruction of the moment-functional domain

Let \(\epsilon:\mathbf Q_2[x]\to\mathbf Q_2\) be the linear functional specified by
\[
 \epsilon(x^m)=B_m,\qquad
 \sum_{m\ge0}B_m\frac{t^m}{m!}=\frac{t}{e^t-1}.
\]
It is a linear functional, not a multiplicative evaluation homomorphism.

The exact finite coefficient identity is
\[
 B_m=\sum_{r=0}^m\frac{(-1)^r r!S(m,r)}{r+1}.
\]
It follows by expanding the formal identity
\[
 \sum_{r\ge0}\frac{(-1)^r(e^t-1)^r}{r+1}
 =\frac{\log(e^t)}{e^t-1}.
\]
For a fixed coefficient m only r at most m contributes. If \(a=v_2(r+1)>0\), then \(r\ge2^a-1\) and \(v_2(r!)\ge a-1\); for a=1 this is the zero lower bound. If a=0 the denominator is a unit. Hence \(2r!/(r+1)\) is dyadically integral and \(2B_m\in\mathbf Z_2\).

Put
\[
 S=2x+1,\qquad U=2x(x+1)=\frac{S^2-1}{2}.
\]
Ordinary S moments are integral directly:
\[
 \epsilon(S^\ell)=\sum_{j=0}^\ell\binom\ell j2^jB_j.
\]
The j=0 term is 1 and each j at least 1 term is integral by the preceding denominator bound. This argument does not require the additional even-moment formula.

For r positive,
\[
 \epsilon\left(S^\ell\frac{U^r}{r!}\right)
 =\frac{2^r}{r!}
   \epsilon\bigl((2x+1)^\ell x^r(x+1)^r\bigr).
\]
The polynomial inside epsilon has integral coefficients, so its value lies in \(\frac12\mathbf Z_2\). Also
\[
 v_2(2^r/r!)=r-v_2(r!)=s_2(r)\ge1.
\]
Therefore the displayed finite evaluation is integral. The r=0 case is the ordinary-moment case above. This treats the divisions by 2 and r! inside their actual finite polynomial domain; no limiting or measure argument is involved.

Now introduce a second independent polynomial variable z, with
\[
 T=2z+1,\qquad V=2z(z+1),
\]
and use the tensor-product functional \(\mathcal E=\epsilon_x\otimes\epsilon_z\), extended linearly to \(K=\mathbf Q_2(i)\). It satisfies
\[
 \mathcal E\left(S^\ell T^m\gamma_r(U)\gamma_s(V)\right)
 =\epsilon(S^\ell\gamma_r(U))\epsilon(T^m\gamma_s(V))
 \in\mathbf Z_2,
\]
where \(\gamma_r(Z)=Z^r/r!\).

Let M be the \(\mathbf Z_2[i]\)-module of **finite linear combinations** of these displayed monomials inside \(K[x,z]\). The displayed generator family is infinite. No finite-generation assertion is made or needed.

M is an algebra because multiplication of divided powers has integral coefficient:
\[
 \gamma_r(U)\gamma_s(U)=\binom{r+s}{r}\gamma_{r+s}(U),
\]
and likewise for V, while powers of S and T add their nonnegative exponents. Its finite tensor-product evaluation lies in \(\mathbf Z_2[i]\).

## 3. Actual factorization and the decisive divided-power implication

Set
\[
 a=(1+i)/2,\qquad b=(1-i)/2,\qquad Y=aS+bT.
\]
The formal factorization is exact:
\[
 A(t)=\frac{\cosh t-\cos t}{t^2}
 =\frac{\sinh(at)}{at}\frac{\sinh(bt)}{bt}.
\]
Indeed \(a+b=1,\ a-b=i,\ ab=1/2\), and the product-to-sum identity gives the displayed equality. The constant terms are 1, so formal reciprocals are well-defined.

Since
\[
 \epsilon(e^{St})=e^t\frac{2t}{e^{2t}-1}
 =\frac{t}{\sinh t},
\]
the tensor-product EGF gives
\[
 A(t)^{-1}=\mathcal E(e^{Yt}),\qquad
 C(n)=\mathcal E(Y^{4n}).
\]
Every equality here is coefficientwise, with finitely many polynomial terms at each coefficient. The inverse has only degrees divisible by 4, matching the actual packed normalization.

Independently expanding with \(a^2=i/2,\ b^2=-i/2,\ 2ab=1\) gives
\[
 Y^2=ST+i(U-V)
\]
and
\[
 Y^4=1+2U+2V+6UV-U^2-V^2+2iST(U-V).
\]
Consequently
\[
 W=(Y^4-1)/2
 =U+V+3UV-U^2/2-V^2/2+iSTU-iSTV.
\]

The potentially delicate implication is \(\gamma_k(W)\in M\). It follows from the following exact component formulas:

| Component Z | Its divided power \(\gamma_k(Z)\) |
|---|---|
| U or V | \(\gamma_k(U)\) or \(\gamma_k(V)\) |
| 3UV | \(3^k k!\gamma_k(U)\gamma_k(V)\) |
| \(-U^2/2\) | \((-1)^k(2k-1)!!\gamma_{2k}(U)\) |
| \(-V^2/2\) | \((-1)^k(2k-1)!!\gamma_{2k}(V)\) |
| iSTU | \(i^kS^kT^k\gamma_k(U)\) |
| \(-iSTV\) | \((-i)^kS^kT^k\gamma_k(V)\) |

In the quadratic component formula,
\[
 \frac{(2k)!}{2^kk!}=(2k-1)!!
\]
is an integer; at k=0 it is 1. Thus these formulas include the nullary case and introduce no nonintegral scalars. The divided-power addition formula is a finite sum over the seven nonnegative component indices adding to k, with coefficient 1. M being an algebra, it proves \(\gamma_k(W)\in M\).

For every nonnegative n, \(Y^{4n}=(1+2W)^n\) is in M, and so
\[
 \mathcal E(Y^{4n}\gamma_k(W))\in\mathbf Z_2[i]
\]
for every n,k. Equivalently, the source proof's formula
\[
 W^q\gamma_k(W)=\frac{(k+q)!}{k!}\gamma_{k+q}(W)
\]
is exact and has integral coefficient. Both ways prove the same implication without asserting general divided-power closure for arbitrary elements of M.

## 4. Difference stencil, division by k!, and Gaussian descent

The finite exact stencil gives
\[
 \Delta_1^kC(n)
 =\mathcal E\bigl(Y^{4n}(Y^4-1)^k\bigr)
 =2^kk!\mathcal E(Y^{4n}\gamma_k(W)).
\]
Thus the quotient by \(2^kk!\) is the evaluation of a specific finite polynomial whose membership in M was proved above. Division is not inferred merely from ordinary-moment integrality.

The quotient is in \(\mathbf Q\subset\mathbf Q_2\), because A has rational coefficients. Also
\[
 \mathbf Z_2[i]\cap\mathbf Q_2=\mathbf Z_2.
\]
A direct check avoids any unverified assertion about rings of integers: \(i\notin\mathbf Q_2\), since a 2-adic square root of -1 would be a unit whose square is 1 modulo 4 rather than 3. Hence 1,i are linearly independent over \(\mathbf Q_2\). Every element of \(\mathbf Z_2[i]\) has the form a+bi with a,b in \(\mathbf Z_2\); if it lies in \(\mathbf Q_2\), then b=0. Therefore
\[
 \frac{\Delta_1^kC(n)}{2^kk!}\in\mathbf Z_2.
\]
This proves the step-one all-n, all-k factorial bound. For k=0 it proves ordinary integrality.

## 5. Arbitrary steps, including mixed steps

This implication can be checked internally, without relying on the cited earlier global theorem. For positive u and \(1\le j\le u\),
\[
 j\binom uj=u\binom{u-1}{j-1}
\]
implies
\[
 v_2\left(2^j\binom uj\right)
 \ge v_2(u)+j-v_2(j)
 \ge1+v_2(u).
\]
Now expand the finite polynomial
\[
 \prod_{i=1}^k\bigl((1+X)^{u_i}-1\bigr)=\sum_m b_mX^m.
\]
Every product contributing to \(2^mb_m\) has valuation at least
\[
 k+\sum_i v_2(u_i).
\]
Its degree is at least k. Since \(E=1+\Delta_1\), applying this polynomial to C gives
\[
 \Delta_{u_1}\cdots\Delta_{u_k}C(n)
 =\sum_{m\ge k}b_m\Delta_1^mC(n).
\]
The already proved factorial estimate shows each summand has valuation at least
\[
 v_2(2^mb_m)+v_2(m!)
 \ge k+\sum_i v_2(u_i)+v_2(k!).
\]
All sums are finite. Equal steps follow by taking every \(u_i=u\). A zero step makes the difference zero, and the empty product is the k=0 case. Multiplication by 2 gives the stated one-bit gain for the unnormalized actual packet.

## 6. Analytic interpolation

Let \(a_m=\Delta_1^mC(0)\). The proved bound gives
\[
 a_m/m!\in2^m\mathbf Z_2.
\]
The exact finite Newton identity on natural rows is
\[
 C(n)=\sum_{m=0}^n(a_m/m!)(n)_m.
\]
For \(x\in\mathbf Z_2\), every \((x)_m\) is integral. Thus the Newton series converges uniformly with its mth term having valuation at least m.

Use the integral signed Stirling coefficients
\[
 (x)_m=\sum_{\ell=0}^ms(m,\ell)x^\ell,\qquad
 b_\ell=\sum_{m\ge\ell}(a_m/m!)s(m,\ell).
\]
The defining sum for \(b_\ell\) converges, and \(b_\ell\in2^\ell\mathbf Z_2\). Every term in the finite polynomial row m has valuation at least m uniformly on \(\mathbf Z_2\). Consequently the double family is uniformly summable: after row M, every remaining term has valuation at least M, and each preceding row is finite. Exchanging the two sums is justified and gives
\[
 C(x)=\sum_{\ell\ge0}b_\ell x^\ell.
\]
It agrees with the packet on all natural rows. These rows are dense in \(\mathbf Z_2\), so the continuous interpolation is unique.

The ordinary-series radius is at least 2, and the series converges whenever \(|x|_2<2\), including in complete extension fields. Scope clarification: on \(\mathbf Q_2\)-valued points alone, the condition \(|x|_2<2\) equals \(x\in\mathbf Z_2\), by the discrete value group. Thus a “larger disc” means a larger analytic/geometric radius, not additional \(\mathbf Q_2\)-valued points. This wording point does not affect the factorial bound or the analytic power-series conclusion.

## 7. Obligation matrix

| Obligation | Status | Decisive check |
|---|---|---|
| Actual packet and factorial normalization | Passed | Exact source factorization and independent coefficient reconstruction |
| Bernoulli denominator bound | Passed | Finite Stirling identity and valuation bound for \(2r!/(r+1)\) |
| Finite evaluation after division by 2 and r! | Passed | Explicit \(2^r/r!\) factor against a value in \(\frac12\mathbf Z_2\) |
| Tensor-product evaluation domain | Passed | Separate-variable factorization on every displayed generator |
| Algebra closure of M | Passed | Integral binomial coefficients in divided-power products |
| All seven component formulas | Passed | Direct factorial identities, including k=0 |
| \(\gamma_k(W)\) for every k | Passed | Finite divided-power addition formula |
| Every row n and every order k | Passed | \(Y^{4n}=(1+2W)^n\), with no truncation in n or k |
| Descent from \(\mathbf Z_2[i]\) | Passed | Direct basis argument using \(i\notin\mathbf Q_2\) |
| Equal and mixed positive steps | Passed | Finite weighted coefficient estimate and \(m\ge k\) |
| Nullary case and zero differences | Passed | \(\gamma_0=1\), C(n) integral, and exact zero stencils |
| Ordinary power-series interpolation | Passed | Uniformly summable Stirling conversion and \(b_\ell\in2^\ell\mathbf Z_2\) |
| External dependencies | None | All load-bearing implications reconstructed internally |
| Generic reciprocal theorem, j=1 claim, root program, Lean compilation | Out of scope | Not asserted by this proof |

## 8. Exact computational spot checks

The checks used Python 3.12.14 and exact Fraction arithmetic, with Gaussian numbers represented by pairs of rational numbers. No floating-point approximation, modular precision cap, random seed, or inherited computation code was used.

The finite assertion was:

* Construct actual inverse coefficients C(0) through C(20) from the exact Hurwitz recurrence using source coefficients \(g(j)=1/((4j+1)(2j+1))\).
* Independently construct Bernoulli moments by their defining rational recurrence, and compare \(\mathcal E((aS+bT)^{4n})\) to C(n) for n=0 through 4.
* Check 49 finite evaluations \(\epsilon(S^\ell U^r/r!)\), for \(\ell,r=0,\ldots,6\), by the independent formula
  \[
   \frac1{2^rr!}\sum_{j=0}^r(-1)^{r-j}\binom rj\epsilon(S^{\ell+2j}).
  \]
* Check 80 equal-step bounds for n=0 through 3, k=0 through 4, and u=1 through 4.
* Check 336 mixed-step bounds for n=0 through 3 and all ordered step lists of lengths 1 through 3 with entries 1 through 4.

Every check passed. Runtime was approximately 0.016 seconds. The unchanged source hash is recorded above. These tests are bounded sanity checks; the universal result comes from Sections 2 through 6 of this audit.

The first exact coefficients were
\[
 C(0),\ldots,C(4)
 =1,\ -1/15,\ 13/45,\ -4009/455,\ 151129/153.
\]
The first divided U-moments were
\[
 \epsilon(\gamma_0(U)),\ldots,\epsilon(\gamma_3(U))
 =1,\ -2/3,\ 4/15,\ -32/315.
\]
The first initial-row factorial quotients were:

| k | \(\Delta_1^kC(0)\) | \(\Delta_1^kC(0)/(2^kk!)\) | Quotient valuation |
|---|---|---|---|
| 1 | \(-16/15\) | \(-8/15\) | 3 |
| 2 | \(64/45\) | \(8/45\) | 3 |
| 3 | \(-14848/1365\) | \(-928/4095\) | 5 |
| 4 | \(71426048/69615\) | \(558016/208845\) | 6 |

The following standalone read-only Python program regenerates the substantive finite checks. It writes no files:

~~~python
from fractions import Fraction as F
from math import comb, factorial
from itertools import product

def v2(x):
    x = F(x)
    if not x:
        return float("inf")
    def v(n):
        n, z = abs(n), 0
        while n % 2 == 0:
            z += 1
            n //= 2
        return z
    return v(x.numerator) - v(x.denominator)

C = [F(1)]
for n in range(1, 21):
    C.append(-sum(
        F(comb(4*n, 4*j), (4*j+1)*(2*j+1))*C[n-j]
        for j in range(1, n+1)))

B = [F(1)]
for m in range(1, 25):
    B.append(-sum(F(comb(m+1, j))*B[j]
                  for j in range(m))/(m+1))
mu = [sum(F(comb(ell, j)*2**j)*B[j]
          for j in range(ell+1)) for ell in range(25)]

def gm(x, y):
    return (x[0]*y[0]-x[1]*y[1],
            x[0]*y[1]+x[1]*y[0])

def gp(x, n):
    out = (F(1), F(0))
    for _ in range(n):
        out = gm(out, x)
    return out

a, b = (F(1, 2), F(1, 2)), (F(1, 2), F(-1, 2))
for n in range(5):
    d, out = 4*n, (F(0), F(0))
    for j in range(d+1):
        z = gm(gp(a, j), gp(b, d-j))
        scalar = comb(d, j)*mu[j]*mu[d-j]
        out = (out[0]+scalar*z[0], out[1]+scalar*z[1])
    assert out == (C[n], F(0))

for ell in range(7):
    for r in range(7):
        val = sum(F((-1)**(r-j)*comb(r, j))*mu[ell+2*j]
                  for j in range(r+1))/(2**r*factorial(r))
        assert v2(val) >= 0

def diff(n, steps):
    out = F(0)
    for mask in range(1 << len(steps)):
        shift = sum(u for i, u in enumerate(steps)
                    if (mask >> i) & 1)
        out += (-1)**(len(steps)-mask.bit_count())*C[n+shift]
    return out

for n in range(4):
    for k in range(5):
        for u in range(1, 5):
            assert v2(diff(n, (u,)*k)) >= (
                k*(1+v2(u))+v2(factorial(k)))
    for k in range(1, 4):
        for steps in product(range(1, 5), repeat=k):
            assert v2(diff(n, steps)) >= (
                k+v2(factorial(k))+sum(v2(u) for u in steps))

print("All independent exact spot checks passed.")
print([str(x) for x in C[:5]])
~~~

## 9. Remaining gap and strongest justified statement

There is no remaining mathematical gap in the claimed factorial or mixed-step bound. The proof establishes these bounds for the actual normalized j=2 packet at every natural row, every order, and every positive natural step list. It also supplies the stated analytic interpolation with power-series radius at least 2.

The argument does not establish an extra uniform three-bit gain, an exact valuation law, the analogous j=1 factorial estimate, or a generic factorial inverse-closure theorem. The bounded checks do not assert those extensions. No further finite check is necessary to validate the present theorem.
