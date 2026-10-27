# Critical independent audit of the factorial route

**Verdict: proved as written**, under the expressly permitted classical Euler divided-power moment input. No mathematical gap or counterexample was found.

Audited final source: measure/factorial_route.md, 599 lines.

SHA256: 67e112cc0d9bceb49446ffa856f15679c1a46de3cc0a584f5cbd7284f4689b82

The full mathematical revision was read before the final two scope-only wording changes; those changes were also read. This report is the only file written in this audit. The previous FACTORIAL_AUDIT.md and authored proof/status files remain unchanged. External Frobenius source verification is outside this independent pass and is covered by the complementary main audit.

## Central-factorial Bernoulli lemma

For \(X=Z(Z+1)\), define \(P_r(X)=\prod_{a<r}(X-a(a+1))\). Direct substitution gives \(P_r(X)=(2r)!\binom{Z+r}{2r}\). The defining Bernoulli transform gives \(L(\binom Zj)=(-1)^j/(j+1)\); finite Vandermonde expansion therefore gives
\[
L(P_r(X))=(-1)^r(r!)^2/(2r+1).
\]
The recurrence for \(X^m=\sum_rT(m,r)P_r(X)\) is
\[
T(m+1,r)=T(m,r-1)+r(r+1)T(m,r).
\]
It proves \(2^{m-r}\mid T(m,r)\), including the boundaries. For \(m>0\), the r=0 term vanishes. Every evaluated summand divided by m! has valuation at least
\[
r+s_2(m)-2s_2(r)\ge s_2(m)-1\ge0.
\]
Thus \(L(X^m/m!)\) is integral. All evaluations are finite; no measure assumption enters.

## Integral algebra and address-zero parity

The divided-power algebra, with the stated quadratic relations, consists of finite expressions. Its functional maps it into \(R=\mathbf Z_2[i]\), by independence and the permitted integral moments; an odd Euler factor has zero moment. Divided powers of arbitrary integral elements are not assumed integral.

With \(X=P+Q,\ \tau=iEF,\ \epsilon=1+\tau\), direct expansion gives
\[
H=\gamma_2(X)+\epsilon X+2G,\quad
G=PQ-\gamma_2(P)-\gamma_2(Q)-\tau Q.
\]
Every component of G has integral divided powers: the quadratic component uses \((2r-1)!!\gamma_{2r}(P)\), the PQ component uses \(r!\gamma_r(P)\gamma_r(Q)\), and the last uses \((-\tau)^r\gamma_r(Q)\). Addition is finite. Since \(\epsilon^2=2(\tau-P-Q-2PQ)\), the exact divided-power expansion yields, for \(k\ge1\),
\[
\gamma_k(H)\equiv\gamma_{2k}(X)+\epsilon\gamma_{2k-1}(X)\pmod{2\mathcal A}.
\]
The double-factorial and multiplication coefficients are odd. The permitted odd moments give \(L(\gamma_m(X))\equiv m+1\); tau-weighted moments vanish. Hence \(L(\gamma_k(H))\) is odd, including k=0. The base-index corrections are even after normalization, proving the all-row exact unit-step valuation. The extra-bit transfer proves the same for address one.

For mixed steps, only the all-one multi-index and, when k is even, a single two associated to an even step can affect normalized parity. Thus the leading parity is \(1+(k+1)e\), where e counts even steps. Baseline equality holds exactly when k is odd or e is even. The remaining class has at least one extra bit; no further equality is claimed. Homogeneous steps always attain the baseline.

## Address-two filtration and exact power orders

The Bernoulli lemma validates the address-two integral algebra. Its exact expression
\[
H_2=\epsilon X+2G,\quad
G=-\gamma_2(P)-\gamma_2(Q)+3PQ-\tau Q,\quad
\epsilon^2=2V,\quad V=\tau-2X-8PQ
\]
has integral component divided powers. Therefore
\[
\gamma_k(H_2)\in2^{\lfloor k/2\rfloor}\mathcal A.
\]
Applying L and rational descent proves the claimed stronger unit and mixed bounds. Descent is legitimate: \(L(2^h\mathcal A)\subset2^hR\), and \(R\cap\mathbf Q_2=\mathbf Z_2\) by linear independence of 1,i.

For \(\mu_m=L(\gamma_m(P))\), the central estimate proves evenness off powers of two. At powers, only r=1,3 can contribute odd residues. The first is odd; for \(m\ge4\) the second is even because
\[
T(m,3)/2^{m-3}=h_{m-3}(1,3,6)\equiv m-2=0.
\]
At powers \(m=1,2\), the r=3 term is absent. Thus \(\mu_m\) is odd exactly for m=0 or a power of two.

For \(k=2q\ge4\) a power of two, normalize the exact expansion before reduction. Only auxiliary indices zero and one survive:
\[
\gamma_k(H_2)/2^q\equiv\gamma_k(X)+\epsilon G\gamma_{k-1}(X)\pmod{2\mathcal A}.
\]
The first evaluated term is \(\mu_q=1\) modulo two. The second reduces to the \(\gamma_2(X)\) product with even coefficient \(\binom{k+1}{2}\), and the Q product, whose parity is \(\mu_{k-1}=0\). The normalized moment is therefore a unit. Base-index tails and every higher mixed multi-index have strictly higher valuation. The low-order checks separately prove the stated exact orders one and two.

## Radii, checks, and remaining gap

Stirling conversion is uniformly summable. Unique leading terms prove radius exactly 2 for addresses zero/one and, along the power-of-two subsequence, exactly \(2^{5/2}\) for address two, at every integral center. Boundary divergence concerns these Taylor expansions.

Exact Fraction checks passed: central moments/parities through 32; address-zero parity through 12; address-two filtration through 20; 2,720 mixed parity checks; 1,360 stronger address-two checks; and 2,436 exact address-two low/power-order checks. These are bounded corroboration, not the universal proof.

All critical obligations pass. No remaining gap, conjectural repair, complete address-two valuation pattern, or new Lean verification is asserted.
