# Independent audit of the threshold-free dyadic reciprocal theorem

Audit date: 2026-10-06. Primary verdict: **proved as written**.

The exact requested objects are
\[
F_j(t)=j!\sum_{n\ge0}\frac{t^{4n}}{(4n+j)!},\qquad
f_j(t)=F_j(t)^{-1},\qquad
C_j(n)=(4n)![t^{4n}]f_j(t),\quad 0\le j\le3.
\]
For every natural \(n,k,u\), the conclusion
\[
\Delta_u^k C_j(n)\in2^k\mathbb Z_2
\]
is valid, including \(n=0\), \(k>n\), \(k=0\), and \(u=0\). No starting-row restriction remains. The stronger step-sensitive and all-dyadic-order conclusions in the appended sections are also valid. The proof is algebraic in formal power series; it requires neither convergence in \(t\) nor a computational exhaustion of rows.

## Reviewed artifact and scope

Reviewed `combinatorial/THRESHOLD_FREE_EIGENFLAT_PROOF.md`. The initial five-section version had SHA-256 `c192591e7ff9b293064b805f85f598491fa8356dcacd26964320210fa3464325`; the expanded version through section 8 had SHA-256 `903f63bb027a4586d04ce94dc88578044acd60c7f180d1dab1d06f783c2b2e3b` at review. The core proof was read before an author's verdict was supplied to this auditor. An isolated additional reviewer derived the inverse lemma from its bare hypotheses, without the authored proof, and returned the same induction. Agreement is supplementary; the derivation below is the evidence.

No applicable `AGENTS.md` or project `.mathbox` ledger was found in this workspace branch. The audit changes only audit reports, not the proof or its status. The unnamed “checked completion” in section 5 is not needed as an external input: its source lemma is established directly below.

## Dependency graph

1. Exact generating function → Hurwitz source coefficients \(g_j(n)\).
2. Explicit affine reciprocal difference identity and discrete product identity → source divisibility at every row and order.
3. Hurwitz product/inverse recurrences and derivative shifts → integral lattice operations.
4. Even interior binomial coefficients for \(N=2^a\) → exact integral commuting product operator.
5. Its full multinomial expansion and induction → reciprocal changes flatness type \(\lambda\) to \(-\lambda\).
6. \(L_1=L_{-1}-1\) → ordinary step-one divisibility of the actual reciprocal coefficients.
7. Integral shift polynomials → arbitrary steps, step-sensitive precision, and mixed-step precision.

Every leaf is proved internally. There is no external theorem or finite-computation leaf needed for the universal claim.

## Independent reconstruction of the source

Factorial scaling gives, directly from the specified series,
\[
g_j(n)=\frac{j!(4n)!}{(4n+j)!}.
\]
Thus
\[
g_0=1,\quad g_1(n)=\frac1{4n+1},\quad
g_2(n)=\frac1{(4n+1)(2n+1)},\quad
g_3(n)=\frac3{(4n+1)(2n+1)(4n+3)}.
\]
All have \(g_j(0)=1\); all denominators are odd. These are the coefficients of the series being inverted, not the coefficients of a pointwise-inverted surrogate.

For \(b\in2\mathbb Z_2\), odd \(c\in\mathbb Z_2\), and \(x=bn+c\), direct induction gives
\[
\Delta_1^k\frac1{bn+c}
=\frac{(-1)^k k!b^k}{\prod_{r=0}^k(b(n+r)+c)}.
\]
Every denominator is a unit, so its valuation is at least \(k\). The induction subtracts two adjacent reciprocal products; their numerator difference is \(-(k+1)b\). The constant case is immediate.

For arbitrary sequences \(A,B\), the exact discrete Leibniz identity is
\[
\Delta_1^k(AB)(n)
=\sum_{i=0}^k\binom ki\Delta_1^iA(n)\,
\Delta_1^{k-i}B(n+i).
\]
If both factors have order-\(i\) differences divisible by \(2^i\) at every row, each summand has valuation at least \(k\). Applying this repeatedly to the displayed kernels proves the complete source hypothesis with no cutoff.

## Hurwitz lattice and the decisive induction

Write \(\mathcal H_R=\{\sum a_dt^d/d!:a_d\in\mathbb Z_2\}\). Its product satisfies
\[
[t^d/d!](AB)=\sum_{r=0}^d\binom dr a_rb_{d-r}.
\]
Differentiation satisfies \([t^d/d!]D^iA=a_{d+i}\). Both operations therefore preserve the entire lattice. If \(a_0\) is a unit, the inverse coefficients obey
\[
h_0=a_0^{-1},\qquad
h_d=-a_0^{-1}\sum_{r=1}^d\binom dr a_rh_{d-r},
\]
which proves inverse integrality by induction on \(d\). If \(A\) is supported in degrees divisible by \(N\), the same recurrence proves that its inverse is supported there too.

Let \(N=2^a\), \(L_\lambda=(D^N-\lambda)/2\), and
\(c_i=\binom Ni/2\), \(1\le i<N\). The \(c_i\) are integers because \((1+X)^N=1+X^N\) in \(\mathbb F_2[X]\). The exact product identity is
\[
L_{\lambda+\mu}(AB)
=(L_\lambda A)B+A(L_\mu B)
+\sum_{i=1}^{N-1}c_i(D^iA)(D^{N-i}B).
\]
All constituent operators commute on the two factors. If multiplication is \(m\) and
\[
T=L_\lambda\otimes1+1\otimes L_\mu
+\sum_{i=1}^{N-1}c_iD^i\otimes D^{N-i},
\]
the product identity is the operator identity \(L_{\lambda+\mu}m=mT\), and hence \(L_{\lambda+\mu}^km=mT^k\). This justifies iteration without assuming away correction terms.

With \(A=F\), \(B=H=F^{-1}\), \(\mu=-\lambda\), and \(k>0\), expansion gives
\[
0=L_0^k(FH)=
\sum_{r+s+\sum e_i=k}
\frac{k!}{r!s!\prod e_i!}\prod c_i^{e_i}
\bigl(D^\alpha L_\lambda^rF\bigr)
\bigl(D^\beta L_{-\lambda}^sH\bigr),
\]
where \(\alpha=\sum i e_i\) and \(\beta=\sum(N-i)e_i\).

There is exactly one term with \(s=k\): \(F L_{-\lambda}^kH\), with coefficient one. Every other term has \(s<k\). Under the induction hypothesis each of these terms is integral: the first factor is integral by the assumed flatness of \(F\), the second by lower-order flatness of \(H\), and arbitrary derivatives preserve integrality. The multinomial and correction coefficients are integral. Therefore \(F L_{-\lambda}^kH\in\mathcal H_R\). Multiplying by the already integral \(H\) proves \(L_{-\lambda}^kH\in\mathcal H_R\). The base \(k=0\) is inverse integrality.

For \(N=4\) the correction coefficients are exactly \((2,3,2)\). Their higher-order products are all included in the expansion. For \(N=1\) the correction family is empty; the same induction uses just the binomial expansion of the two factor operators. Thus the minimum dyadic section order is covered.

## Arbitrary derivative shifts and boundary rows

The proof establishes lattice membership simultaneously at every degree, not just at degree zero. For example,
\[
[t^d/d!]D^\alpha L_1^rF
=2^{-r}\sum_{i=0}^r(-1)^{r-i}\binom ri f_{d+\alpha+Ni}.
\]
If \(d+\alpha\) is divisible by \(N\), this is
\(2^{-r}\Delta_1^rg((d+\alpha)/N)\); otherwise it is zero. All the accessed indices are nonnegative. Arbitrary derivative corrections therefore do not demand an unproved negative row or a positive starting row.

Packing identifies \([t^{Nn}/(Nn)!]L_1^kF\) with \(\Delta_1^kg(n)/2^k\). Inversion yields \(-1\)-flatness of \(H\); the identity \(L_1=L_{-1}-1\) transfers this to \(1\)-flatness. Reading its coefficient proves \(\Delta_1^kC(n)\in2^k\mathbb Z_2\) for every \(n\). Since forward differences use \(n,n+1,\ldots,n+k\), \(k>n\) is not an exceptional case.

For positive \(u\), \(E^u-1=(E-1)(1+E+\cdots+E^{u-1})\) gives arbitrary-step divisibility. For \(u=0,k>0\), the difference is zero. For \(k=0\), including \(u=0\), the claim is coefficient integrality. Valuation of zero is interpreted as infinity.

## Appended all-order and precision claims

For \(N=2^a\) and \(0\le j<N\), direct reconstruction gives
\[
g_{N,j}(n)=\frac{j!(Nn)!}{(Nn+j)!}
=\prod_{i=1}^j(1+(N/i)n)^{-1}.
\]
Here \(v_2(N/i)=a-v_2(i)\ge1\) for \(i<N\), even when \(N/i\) is not an ordinary integer. The affine reciprocal identity above applies in \(\mathbb Z_2\), so every source factor has the required divisibility. The empty product covers \(N=1,j=0\). This proves the stated extension to all dyadic orders and all their permitted addresses.

Let \(u>0\), \(s=v_2(u)\), and \(P_u(W)=(1+2W)^u-1\). For \(1\le m\le u\),
\[
v_2(2^m\binom um)\ge m+s-v_2(m)\ge s+1.
\]
Thus \(P_u\) has all coefficients in \(2^{s+1}\mathbb Z_2\). Global divisibility of \(\Delta_1^mC\) permits applying every finite polynomial in \(W=\Delta_1/2\) to \(C\) with integral outputs. Consequently
\[
v_2(\Delta_u^k C(n))\ge k(1+v_2(u)).
\]
More generally, the same proof with \(\prod_{i=1}^kP_{u_i}(W)\) proves the independently checked mixed-step consequence
\[
v_2(\Delta_{u_1}\cdots\Delta_{u_k}C(n))
\ge\sum_{i=1}^k(1+v_2(u_i))
\]
for positive natural steps. A zero step makes a nonempty product zero; the empty product is integrality. Multiplication by \(j!\) adds \(v_2(j!)\). This also validates section 8's sufficient periods; it makes no claim of sharpness for all dyadic lanes.

## Obligation matrix

| Obligation | Status | Reason |
|---|---|---|
| Actual series and factorial normalization | Passed | Reconstructed directly above |
| Complete source hypothesis | Passed | Exact reciprocal and product identities |
| Reciprocal integrality and packed support | Passed | Triangular coefficient recurrence |
| All mixed derivative corrections | Passed | Exact commuting operator identity and multinomial expansion |
| Noncircular inverse induction | Passed | Unique highest inverse order; all other orders smaller |
| Arbitrary lower derivative shifts | Passed | Global lattice membership at all degrees |
| Row zero, orders larger than row, order zero | Passed | No lower-index demand; separate base case |
| Step zero and arbitrary positive steps | Passed | Zero operator or integral shift polynomial |
| All \(N=2^a\), including \(N=1\) | Passed | Integral corrections and valid source factors |
| Step-sensitive and mixed-step precision | Passed | Finite normalized-difference polynomials |
| Odd-prime unchanged conclusion | Out of scope; false if asserted | Separate counterexample below |
| Formal Lean compilation | Not addressed | Not claimed by the proof |

## Independent finite checks

These checks supplement the proof and do not establish its infinite quantifiers. Exact Python 3.12.14 `Fraction` arithmetic, with no rounding or truncation of valuation, gave:

* 3,772 assertions of \(v_2(\Delta_u^kC_j(n))\ge k\), for all \(j=0,1,2,3\), \(0\le u\le4\), and all \(n,k\ge0\) with \(k\le20\) and \(n+uk\le20\).
* 39 checks of the entire multinomial inverse product identity for \(N=4,j=3\), \(1\le k\le3\), and every degree \(0\le d\le12\), including nonpacked degrees. The required source and inverse coefficients were retained through degree 24, so derivative shifts were not silently truncated.

Small directly reconstructed values are

| \(j\) | \(C_j(0)\) | \(C_j(1)\) | \(C_j(2)\) | \(\Delta C_j(0)\) |
|---|---:|---:|---:|---:|
| 0 | 1 | −1 | 69 | −2 |
| 1 | 1 | −1/5 | 121/45 | −6/5 |
| 2 | 1 | −1/15 | 13/45 | −16/15 |
| 3 | 1 | −1/35 | 59/1155 | −36/35 |

The source checks used `sha256sum` and direct reads of the reviewed proof. Arithmetic checks were bounded inline Python, independently reconstructed from the specified factorial coefficients. The universal conclusion rests on the displayed identities and induction, not these samples or the generic example script.

## Separate odd-prime boundary

The reviewed document claims only \(R=\mathbb Z_2\), \(N=2^a\). Replacing these with \(R=\mathbb Z_p\), \(N=p^a\) for an odd prime, while retaining the conclusion \(\Delta C\in pR\), would be false. Take \(g(n)=1\). Its positive-order differences vanish and \(g(0)=1\), but the actual reciprocal has \(C(0)=1\), \(C(1)=-1\). Hence \(\Delta C(0)=-2\notin p\mathbb Z_p\). The inverse-flatness lemma still changes eigenvalue \(1\) to \(-1\); the dyadic translation back to \(1\) is what fails for odd primes.

## Remaining gap and safe conclusion

There is no remaining mathematical gap in the stated dyadic reciprocal theorem, its actual four kernels, or its appended all-dyadic-order and precision consequences. Adding the explicit affine reciprocal identity to the source section would improve self-containment but would not change the proof or its scope. Exact first-difference valuations and minimal periods require additional input and are audited separately in `SHARP_PERIOD_AUDIT.md`.
