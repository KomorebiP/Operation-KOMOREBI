# Independent audit of the final four-address factorial route

Audit date: 2026-10-06. Primary verdict: **proved as written**.

Reviewed `measure/factorial_route.md`, including its final address-two exact-radius and power-of-two-order mixed-difference appendices. The final reviewed revision has 599 lines and SHA-256 `67e112cc0d9bceb49446ffa856f15679c1a46de3cc0a584f5cbd7284f4689b82`. The earlier full mathematical revision had hash `28df34db9b767cccd18617eb553ff82b180b99d3b3238071215bd3b8e8e4cf38`; the two subsequent scope-sentence clarifications were read and checked, with no equation or proof change.

The exact objects throughout are
\[
C_j(n)=(4n)![t^{4n}]\left(j!\sum_{q\ge0}\frac{t^{4q}}{(4q+j)!}\right)^{-1},
\qquad 0\le j\le3.
\]
All claims below hold for every natural starting row, including zero. Positive mixed steps are arbitrary natural integers. A zero step makes a nonempty mixed difference zero; empty differences assert ordinary integrality. No extra positive-order offset is asserted at order zero.

## Separately verified conclusions

Put \(S_u=\sum_{r=1}^k v_2(u_r)\) and \(L=k+v_2(k!)+S_u\), with \(k\ge1\).

| Statement | Audit result |
|---|---|
| All four lanes: \(v_2(\Delta_{u_1}\cdots\Delta_{u_k}C_j(n))\ge L+(0,0,3,1)_j\) | Proved |
| Lanes 0 and 1: equality with \(L\) if \(k\) is odd or the number of even steps is even | Proved |
| Lanes 0 and 1: at least \(L+1\) when \(k\) is even and the number of even steps is odd | Proved; no further exact value inferred |
| Lanes 0 and 1: \(v_2(\Delta_u^kC_j(n))=k+v_2(k!)+k v_2(u)\) | Proved for every positive \(u,k\) |
| Lane 2: lower bound \(2k+v_2(k!)+\lfloor k/2\rfloor+S_u\) | Proved; may be combined with \(L+3\) by taking the maximum |
| Lane 2, order 1: exact value \(4+v_2(u_1)\) | Proved |
| Lane 2, order 2: exact value \(6+v_2(u_1)+v_2(u_2)\) | Proved |
| Lane 2, \(k=2^r\ge4\): exact value \(2k+v_2(k!)+k/2+S_u\) | Proved for every positive mixed step list |
| Continuous interpolation and ordinary Taylor series for all four lanes | Proved |
| Lanes 0 and 1: Taylor radius exactly 2 at every integral center | Proved |
| Lane 2: Taylor radius exactly \(2^{5/2}\) at every integral center | Proved |
| Lane 3: Taylor radius at least 2 | Proved; maximality not asserted |

For the original coefficients \(j!C_j(n)\), every difference valuation gains \(v_2(j!)\). The audit does not infer a complete exact law at all lane-two orders or at lane three.

The lane-zero and lane-one factorial and exact-valuation conclusions depend on the verified classical Euler input. The lane-two factorial, filtration, power-of-two-order, and radius conclusions are self-contained Bernoulli calculations. The lane-three lower bound uses that lane-two result and the self-contained transfer factor; it does not depend on Frobenius.

## Dependency and primary-source verification

The sole external arithmetic input is ordinary Euler Frobenius congruence. It was independently checked here against Ira M. Gessel, *Applications of the classical umbral calculus*, arXiv:math/0108121v3, dated 22 November 2001. The PDF header authenticates that version. Printed page 26 states the exact valuation for the forward stencil of even-index Euler numbers at every even starting index; printed pages 29–30 derive it from Theorem 9.2. The source uses the same \(\operatorname{sech}(t)\) normalization. Its statement translates to
\[
v_2\left(\sum_{r=0}^m(-1)^{m-r}\binom mr\operatorname{Euler}_{2r+2n}\right)
=m+v_2(m!).
\]
Consequently the functional on \(P=(E^2-1)/2\) has \(L(\gamma_m(P))\) an odd dyadic integer for every \(m\). This extraction and its application were verified, rather than inferred from an abstract or a reference list. [Primary PDF, exact version](https://arxiv.org/pdf/math/0108121v3).

The source was checked through the primary PDF's retrieved content; no local PDF copy or PDF content hash is claimed. The generic threshold-free theorem, separately audited in `GLOBAL_PROOF_AUDIT.md`, supplies continuous interpolation for the shifted transfer sums. Its weaker bound is not used as a substitute for the factorial theorem. The Bernoulli denominator, central-factorial, Gaussian-algebra, transfer, and parity arguments are internal. `FACTORIAL_ROUTE_CRITICAL_AUDIT.md` provides a second isolated derivation of the central and divided-power implications; its use of the classical input is explicitly separated from the primary-source check here.

## Integral functional and exact algebra

The Euler source factorization
\[
F_0(t)=\frac2{\cosh t+\cos t}
=\operatorname{sech}(at)\operatorname{sech}(bt),
\quad a=(1+i)/2, b=(1-i)/2,
\]
is exact, with \(a+b=1,a-b=i,ab=1/2\). Two independent Euler variables give \(C_0(n)=L((aE+bF)^{4n})\). Substitution of \(E^2=1+2P,F^2=1+2Q\) removes the Gaussian denominators and yields the stated seven-component polynomial
\[
H=\frac{(aE+bF)^4-1}{2}
=P+Q-\frac{P^2}2-\frac{Q^2}2+3PQ+iEF(P-Q).
\]

The relevant ring is the algebra of finite polynomials generated over \(R=\mathbb Z_2[i]\) by the divided powers of \(P,Q\), adjoining \(E,F\) with their monic quadratic relations. It is spanned over the divided-power subalgebra by \(1,E,F,EF\). The evaluation functional maps its finite elements to \(R\): pure divided-power moments factor by independence, and any term with an odd \(E\) or \(F\) exponent has zero moment. Evaluation is linear, not a multiplicative homomorphism.

Each component has integral divided powers. In particular,
\[
\gamma_m(P^2/2)=(2m-1)!!\gamma_{2m}(P),\qquad
\gamma_m(3PQ)=3^m m!\gamma_m(P)\gamma_m(Q).
\]
The mixed component is \((iEF)^m\gamma_m(P-Q)\), with integral reduction of powers of \(E,F\). Finite divided-power addition proves \(\gamma_k(H)\) belongs to this algebra at every order. No division by \(k!\) is inferred from ordinary-moment integrality alone.

The quotient moment is rational. Gaussian descent is valid directly: \(1,i\) are independent over \(\mathbb Q_2\), so
\(\mathbb Z_2[i]\cap\mathbb Q_2=\mathbb Z_2\), and likewise after multiplying by any power of two. This also justifies later descent of filtered ideals. The fact that \(R/2R\) is not a field causes no problem: all congruences are algebra/module congruences, followed by the integral linear functional.

## Transfer factors, scaled binomials, and shifted uniform sums

The address-one factor satisfies
\[
A_1F_0=\frac12\left(\frac{\tanh(at)}{at}+\frac{\tanh(bt)}{bt}\right),
\quad A_1=\frac{\sinh t+\sin t}{2t}.
\]
Its packet coefficients are exactly
\[
d_i=(-1/4)^i\frac{2^{4i+2}(2^{4i+2}-1)B_{4i+2}}{(4i+2)(4i+1)}.
\]
The address-three factor satisfies
\[
A_3F_2=\frac32\left(\frac{\coth(at)}{at}+\frac{\coth(bt)}{bt}\right),
\quad A_3=3\frac{\sinh t-\sin t}{t^3},
\]
with
\[
d_i=3(-1/4)^i\frac{2^{4i+2}B_{4i+2}}{(4i+2)(4i+1)}.
\]
In the latter Laurent expression, the polar coefficients cancel because \(a^{-2}+b^{-2}=0\). In both cases the constant is one and the other residue classes cancel. These formulas follow by direct formal expansion of the Bernoulli generating series. The self-contained Stirling bound \(2B_m\in\mathbb Z_2\) gives \(v_2(d_i)\ge2i\), which is exactly the inequality required. No von Staudt–Clausen input remains necessary.

Hurwitz inversion then gives \(v_2(h_i)\ge2i\). The exact transfer sum has terms
\(h_i\binom{4x}{4i}C(x-i)\). For natural \(x=n\), all \(i>n\) terms are exactly zero. On \(\mathbb Z_2\), the integral-valued factors \(\binom{4x}{4i}\) and \(C(x-i)\) are bounded, so \(h_i\) forces uniform convergence. Negative shifted arguments are in the already defined continuous interpolation domain, and its factorial estimates extend to them by approximating with natural starting rows. Finite difference operators preserve these uniform limits.

For \(P_i(x)=4^i\binom{4x}{4i}\), the degree-\(d\) coefficient is
\[
\frac{4^i4^ds(4i,d)}{(4i)!}.
\]
The constant is zero. For \(d\ge1\), each product in the Stirling coefficient omits at most \(d-1\) of the \(2i-1\) even numbers, so
\(v_2(s(4i,d))\ge\max(0,2i-d)\). Since
\(v_2((4i)!)=4i-s_2(i)\), the coefficient has valuation at least \(d+s_2(i)\ge d+1\). This argument includes \(d>2i\) correctly.

The polynomial \(\Delta_1^k x^d\) is divisible by \(k!\) and vanishes for \(d<k\), giving \(\Delta_1^kP_i(x)\in2^{k+1}k!\mathbb Z_2\), also at \(k=0\). The discrete product rule contributes
\(\binom kr r!(k-r)!=k!\), so multiplying by a basic factorial sequence preserves the extra bit. Uniformly summing proves the required estimates for \(C_1-C_0\) and \(C_3-C_2\), with all shifts and rows covered.

## Central-factorial Bernoulli argument

For the Bernoulli variable \(Z\), put \(P=Z(Z+1)\) and
\(P_r(P)=\prod_{a=0}^{r-1}(P-a(a+1))\). Direct substitution gives
\(P_r(P)=(2r)!\binom{Z+r}{2r}\). The formal identity
\(L((1+t)^Z)=\log(1+t)/t\), Vandermonde, and a finite rational beta-integral identity yield
\[
L(P_r(P))=(-1)^r\frac{(r!)^2}{2r+1}.
\]
The central coefficients in \(P^m=\sum_rT(m,r)P_r(P)\) satisfy
\(T(m+1,r)=T(m,r-1)+r(r+1)T(m,r)\). Induction gives \(2^{m-r}\mid T(m,r)\). For \(m>0,r\ge1\), each divided evaluated term has valuation at least
\[
m-r+2v_2(r!)-v_2(m!)
=r+s_2(m)-2s_2(r)\ge0.
\]
The last inequality uses \(r\ge2s_2(r)-1\) and \(s_2(m)\ge1\). The \(r=0\) term vanishes for \(m>0\). This establishes finite moment integrality at every order, with no sampled-order inference.

For \(B=2Z+1\), \(P=(B^2-1)/4\), odd weighted moments vanish and the same finite integral algebra applies with \(B^2=1+4P\). The exact factorization of \(F_2\) yields
\[
H_2=\frac{(aB+bD)^4-1}{4}
=P+Q-P^2-Q^2+6PQ+iBD(P-Q).
\]
Its integral divided powers give the basic \(2k+v_2(k!)\) bound. The initial Newton coefficients \(-16/15\) and \(64/45\) have valuations 4 and 6. Newton's shifted identity supplies the additional-three-bit estimate at orders one and two; for \(k\ge3\), \(2k\ge k+3\). Thus the positive-order offset three is valid at every row.

## Leading parity, filtration, and exact subsequences

The detailed parity derivations are also given in `FACTORIAL_ROUTE_CRITICAL_AUDIT.md`. Their decisive steps were independently checked here.

At lane zero, with \(X=P+Q\), \(\tau=iEF\), \(\epsilon=1+\tau\),
\[
H=\gamma_2(X)+\epsilon X+2G,
\quad G=-\gamma_2(P)-\gamma_2(Q)+PQ-\tau Q,
\quad \epsilon^2=2(\tau-P-Q-2PQ).
\]
The polynomial \(G\) has integral divided powers componentwise. Thus only zero and first powers of \(\epsilon\) survive modulo two in the divided-power expansion, giving
\[
\gamma_k(H)\equiv\gamma_{2k}(X)+\epsilon\gamma_{2k-1}(X)\pmod{2\mathcal A}.
\]
Classical odd divided-power moments and independence give \(L(\gamma_m(X))\equiv m+1\pmod2\); the \(\tau\)-weighted even-polynomial part evaluates to zero. Therefore \(L(\gamma_k(H))\) is odd. Base-index corrections have strictly larger valuation. The extra-bit transfer gives the same exact unit-step valuation for lane one.

In the mixed step expansion, the only possible additional terms of baseline valuation have exactly one local exponent two, all others one, with even \(k\) and an even step in that position. Exponents at least three give a strict gain, and two local twos make the intervening factorial interval contain an even number. Every surviving normalized baseline term is one modulo two. The resulting parity is one for odd \(k\), and \(1+e\) for even \(k\), where \(e\) counts even steps. This proves the reported classification and explains why homogeneous steps always have exact baseline valuation.

At lane two,
\[
H_2=\epsilon X+2G,\quad
G=-\gamma_2(P)-\gamma_2(Q)+3PQ-\tau Q,\quad
\epsilon^2=2(\tau-2P-2Q-8PQ).
\]
Again every divided power of \(G\) is integral. The \(r\)-th expansion term in \(\gamma_k(H_2)\) has ideal valuation at least
\(r+\lfloor(k-r)/2\rfloor\ge\lfloor k/2\rfloor\). Applying the integral linear functional and rational Gaussian descent proves the stronger filtered bound. The finite mixed-step expansion uses
\(2m+v_2\binom um\ge2+v_2(u)\), and total order at least \(k\), giving the claimed precision for every mixed step list.

The central-factorial estimate sharpens to \(v_2(\mu_m)\ge s_2(m)-1\), where \(\mu_m=L(\gamma_m(P))\). Its parity is one precisely for \(m=0\) or a power of two. At a positive power of two, only central indices one and three can be units; index one is odd and index three is even because its normalized recurrence coefficient has generating series \(1/((1-t)(1-3t)(1-6t))\), whose relevant coefficient modulo two is \(m-2\).

For \(k=2^r\ge4\), exact normalization of \(\gamma_k(H_2)\) by \(2^{k/2}\) leaves only auxiliary expansion indices zero and one modulo two. Their evaluated residues are respectively one and zero: the first follows by squaring the parity series \(1+t+t^2+t^4+\cdots\); the second reduces to
\(L((\gamma_2(X)+Q)\gamma_{k-1}(X))\), which is even by the integral multiplication coefficient and the just-proved \(\mu\) parity. Thus the normalized moment is a unit. Base-index corrections are strictly higher. For mixed steps of higher total order \(M>k\), the excess valuation is at least \(M-k\ge1\), so only the leading term remains. The two low orders are handled by the exact coefficients and their strictly higher tails. This proves all the stated power-of-two-order equalities, without asserting other orders exact.

## Taylor radii

Writing \(a_m=\Delta_1^mC_j(0)\), the ordinary coefficients are
\[
d_{j,\ell}=\sum_{m\ge\ell}\frac{a_m}{m!}s(m,\ell).
\]
All coefficient sums and the interchange with Newton interpolation are justified by uniformly geometric row bounds. This gives
\(v_2(d_{j,\ell})\ge\ell+(0,0,3,1)_j\). For lanes zero and one, the exact Newton valuation makes the term \(m=\ell\) uniquely smallest, so \(v_2(d_{j,\ell})=\ell\). For lane two, the filtration gives
\(v_2(d_{2,\ell})\ge\max(2\ell+\lfloor\ell/2\rfloor,\ell+3)\); at every \(\ell=2^r\ge4\), its unique leading term has valuation \(5\ell/2\). These infinite exact subsequences prove, rather than numerically suggest, the stated exact radii.

Translation to any \(x_0\in\mathbb Z_2\) uses the convergent integral-binomial coefficient sum
\(\sum_{m\ge\ell}d_{j,m}\binom m\ell x_0^{m-\ell}\); the same unique leading terms remain. At the indicated boundaries in suitable complete extension fields, the exact coefficient subsequences make terms fail to tend to zero, proving divergence of those Taylor expansions. This does not rule out unrelated analytic continuation. On \(\mathbb Q_2\)-valued points, open disc terminology should be interpreted with the discrete value group; the coefficient radii are the precise analytic statements.

## Supplemental exact checks and final scope

An independent ordinary-series inverse in Python 3.12.14 `Fraction` arithmetic gave 2,044 successful assertions: the mixed classification and all four lower bounds for \(1\le k\le4\), steps in \(\{1,2,3\}\), and rows 0 through 3; homogeneous exact laws at orders 1,2,4,8,16 with steps 1 and 2 and rows 0 through 2; and Bernoulli divided-power integrality/parity through order 16. Required actual coefficients were retained through row 36. No floating precision or probabilistic test was used.

The minimal illustrated mixed cancellation is
\(\Delta_1\Delta_2C_0(0)=-33728\), of valuation six, while its baseline is four. Lane-two initial Newton valuations at orders 1,2,4,8,16 are 4,6,13,27,55. These checks agree with the proof but are not the justification of any infinite family.

No mathematical gap remains in the final reviewed statements. External dependence is confined to the primary-verified classical Euler Frobenius result. The complete scope is the claim table at the start of this report; no universal exact valuation at every lane-two order, no exact lane-three radius, no historical-priority claim, and no new Lean compilation follow from this audit.
