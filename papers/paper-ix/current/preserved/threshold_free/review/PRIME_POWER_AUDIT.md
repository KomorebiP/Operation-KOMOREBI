# Independent audit of the sign-twisted prime-power transfer

Audit date: 2026-10-06. Primary verdict: **proved as written**.

The reviewed statement concerns a prime \(p\), \(a\ge1\), \(N=p^a\), and \(0\le j<N\), with the exact series
\[
G(t)=j!\sum_{n\ge0}\frac{t^{Nn}}{(Nn+j)!},\qquad
G(t)^{-1}=\sum_{n\ge0}C(n)\frac{t^{Nn}}{(Nn)!}.
\]
It proves ordinary mixed-difference divisibility for \(C\) when \(p=2\), ordinary mixed-difference divisibility for \(A(n)=(-1)^nC(n)\) for arbitrary primes, and the corresponding twisted-operator divisibility for the original coefficients \(E(n)=j!C(n)\). The odd-prime conclusion is not an ordinary step-one difference claim about raw \(C\).

Reviewed `GENERAL_PRIME_POWER_TRANSFER.md`, SHA-256 `cce4fb1cd2c85f4379eb49d7122e8d56f80c7065d7e88fa1c604ed34dec57422`. This report is separate from the dyadic audit so the distinct sign convention is not silently conflated. An isolated reviewer also rederived the abstract prime-power reciprocal and mixed-step statements from bare hypotheses without reading this authored proof.

## Dependencies and source construction

The proof uses the internally proved Hurwitz reciprocal and commuting-operator identities audited in `GLOBAL_PROOF_AUDIT.md`, with \(p\) replacing two. The prime-specific obligations are the source slopes, interior binomial divisibility, sign conversion, and mixed-step coefficient estimate. They all pass by direct derivation below. No external theorem or finite computational classification is needed.

Factorial scaling of the actual prescribed source gives
\[
g(n)=\frac{j!(Nn)!}{(Nn+j)!}
=\prod_{i=1}^j(1+(N/i)n)^{-1}.
\]
For every \(1\le i<N\), \(v_p(i)<a\), so \(s=N/i\in p\mathbb Z_p\). Consequently \(1+sn\) is a unit for every natural \(n\), and the exact identity
\[
\Delta_1^k(1+sn)^{-1}
=\frac{(-s)^k k!}{\prod_{h=0}^k(1+s(n+h))}
\]
gives valuation at least \(k\). The pointwise discrete product formula
\[
\Delta_1^k(fh)(n)=\sum_{r=0}^k\binom kr
\Delta_1^rf(n)\Delta_1^{k-r}h(n+r)
\]
preserves that bound for the finite product. Thus \(g(n)\in\mathbb Z_p\), \(g(0)=1\), and \(\Delta_1^kg(n)\in p^k\mathbb Z_p\) at all rows. The empty product covers \(j=0\).

## Reciprocal induction for general primes

Let \(\mathcal H_p=\{\sum h_dt^d/d!:h_d\in\mathbb Z_p\}\), \(D=d/dt\), and \(L_\lambda=(D^N-\lambda)/p\). Hurwitz multiplication is integral because its structure constants are binomial coefficients. Derivatives shift its coefficients toward higher nonnegative degrees. The triangular inverse recurrence proves \(G^{-1}\in\mathcal H_p\), with support on degrees divisible by \(N\).

In \(\mathbb F_p[X]\), \((1+X)^{p^a}=1+X^{p^a}\); hence each \(\binom Ni/p\), \(0<i<N\), is an integer. The exact product identity is
\[
L_{\lambda+\mu}(UV)
=(L_\lambda U)V+U(L_\mu V)
+\sum_{i=1}^{N-1}\frac{\binom Ni}{p}(D^iU)(D^{N-i}V).
\]
All operators on the two factors commute, so the full multinomial expansion is exact and all its scalar coefficients are integral. Setting \(U=G\), \(V=G^{-1}\), \(\lambda=1\), \(\mu=-1\), and taking order \(k>0\) makes its left side zero. The unique term with inverse \(L_{-1}\)-order \(k\) is \(G L_{-1}^kG^{-1}\), with coefficient one. Every other term has smaller inverse order and arbitrary derivatives of already integral factors. Induction, followed by multiplication by \(G^{-1}\), proves \(L_{-1}^kG^{-1}\in\mathcal H_p\) at all orders and all coefficient degrees.

Packing identifies this conclusion with
\[
(S+1)^kC(n)\in p^k\mathbb Z_p,
\quad S C(n)=C(n+1).
\]
All derivative corrections and row-zero coefficients are included in that induction. There is no hidden positive starting index or order restriction.

## Sign convention and precision

For \(p=2\),
\((S-1)^k=((S+1)-2)^k\) shows \(\Delta_1^kC\in2^k\mathbb Z_2\). Equivalently, \(L_1=L_{-1}-1\). This conversion would require division of two by \(p\) for odd primes and is not used there.

For arbitrary \(p\), put \(A(n)=(-1)^nC(n)\). Exact expansion gives
\[
\Delta_1^kA(n)=(-1)^{n+k}(S+1)^kC(n),
\]
so \(A\) has ordinary \(p^k\) higher-difference divisibility.

For any sequence \(X\) with that property, let \(H>0\). The finite shift identity is
\[
\Delta_H=\sum_{i=1}^H\binom Hi\Delta_1^i.
\]
Because \(i\binom Hi=H\binom{H-1}{i-1}\),
\[
v_p(p^i\binom Hi)\ge i+v_p(H)-v_p(i)
\ge1+v_p(H).
\]
The last inequality holds for every prime and every positive \(i\), since \(i-v_p(i)\ge1\). Multiplying these finite polynomial identities and applying global divisibility of \(\Delta_1^mX\) proves
\[
v_p(\Delta_{H_1}\cdots\Delta_{H_k}X(n))
\ge\sum_{\nu=1}^k(1+v_p(H_\nu))
\]
for every base row and positive natural steps. This bound needs no modification for odd primes after twisting.

For raw \(C\), set \(T_H=S^H-(-1)^H\). The full sign conversion, including mixed steps, is
\[
\Delta_{H_1}\cdots\Delta_{H_k}A(n)
=(-1)^{n+\sum H_\nu}T_{H_1}\cdots T_{H_k}C(n).
\]
Thus multiplication by \(j!\) gives exactly the manuscript's bound
\[
v_p(T_{H_1}\cdots T_{H_k}E(n))
\ge v_p(j!)+\sum_{\nu=1}^k(1+v_p(H_\nu)).
\]
When \(p=2\), the stronger ordinary mixed-difference statement applies directly to \(E\). Empty products give integrality with the factorial normalization. A zero ordinary step gives the zero operator; the same is true of the twisted step \(T_0\). Zero values have infinite valuation.

## Boundaries and independent checks

The odd-prime twist is essential. For the actual \(j=0\) kernel, \(g(n)=1\), the inverse recurrence gives \(C(0)=1\), \(C(1)=-1\), so the ordinary step-one difference is \(-2\), a unit at every odd prime. This confirms rather than contradicts the proof's explicit boundary. No transfer to arbitrary non-prime-power \(N\) is claimed.

Although the file assumes \(a\ge1\), the same abstract algebra works at \(N=p^0=1\): the correction family is empty. This is a checked boundary extension, not an additional assumption needed for the stated claim.

Exact Python 3.12.14 `Fraction` arithmetic independently reconstructed the ordinary series inverse from \(j!/(Nq+j)!\), scaled by \((Nn)!\), and verified 8,232 assertions across \((p,N)=(2,4),(3,3),(3,9),(5,5)\), every permitted lane, \(0\le k\le3\), \(1\le H_i\le3\), and all rows satisfying \(n+\sum H_i\le9\). Both the raw twisted differences and the corresponding ordinary differences of \(C\) or \((-1)^nC\) were checked. These samples are supplementary; the theorem follows from the universal algebraic proof above.

## Obligation matrix

| Obligation | Status |
|---|---|
| Exact source and normalization | Passed |
| Unit source factors for every permitted lane | Passed |
| Complete source higher-difference hypothesis | Passed |
| Interior binomial divisibility at prime-power order | Passed |
| Full reciprocal induction, including all derivatives | Passed |
| Odd-prime sign twist | Passed |
| Mixed-step signs and valuation sum | Passed |
| Original \(j!\) normalization | Passed |
| Row zero, order zero, and zero operators | Passed |
| Ordinary raw odd-prime first-difference theorem | Not claimed; false in the stated example |
| Arbitrary non-prime-power section order | Out of scope |

No mathematical gap remains in the reviewed prime-power statement. Its conclusion should continue to be reported separately from the ordinary dyadic theorem, preserving the operator \(T_H\) and the sign-twisted sequence for odd primes.
