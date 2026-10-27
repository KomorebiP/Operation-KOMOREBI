# Transversality for every regular lower address

Date: 2026-10-05. This continuation extends the address-one derivative exclusion theorem to every lower address that is a strict carry record. It uses the actual finite Euler prefix. It does not replace the true terminal by a smaller label, and it does not claim universal Euler simplicity.

## 1. Hypotheses and exact Euler normalization

Let

\[
\Theta(n)=3n+1+s_2(n-1).
\]

Consider an actual Euler wall with certified true terminal \(j\), outer scale \(L=\Theta(k)+\delta\), and last lower minimizing address \(a\ge1\). Let \(k=j-a\) be its first-record complement. Thus \(k\) is regular, \(t=v_2(k)\), \(a<t\), and \(t\ge L_a\). Assume in addition that **the lower address \(a\) is regular**, meaning

\[
e_a(q)=\Theta(a)-\Theta(a-q)>0\qquad(1\le q<a).
\]

Consequently \(L_a=\Theta(a)\). Set

\[
D=t-\Theta(a)\ge0,\qquad
c_{r,q}=8^q\frac{\beta_{r+q}}{\beta_r},\qquad
S(x)=\sum_{q=0}^{a-1}c_{r,q}P_q(x)\mathscr A(x-q).
\]

The carry identities give \(v_2(c_{r,q})=e_a(q)>0\) for \(1\le q<a\), and \(c_{r,0}=1\). Therefore

\[
S\in\mathbb Z_2\langle x\rangle^\times,
\qquad S\equiv1\pmod2.
\tag{1}
\]

This conclusion concerns the actual Euler coefficients. The prefix has not been replaced by an arbitrary polynomial.

The exact tail split, true-terminal inheritance, and \(\mu_r=-D-\delta\) give

\[
G_r(x)=uP_a(x)F(x-a)+2^{\delta+D}S(x),
\qquad F=G_{r+a},\quad u\in\mathbb Z_2^\times.
\tag{2}
\]

For \(\delta\ge1\), the regular complement has

\[
F(y)=P_k(y)U(y-k)+2^\delta V(y),\qquad U\equiv V\equiv1\pmod2.
\tag{3}
\]

All congruences of analytic series here are coefficientwise. Define the exact normalized coordinate

\[
Q(x)=P_a(x)/S(x).
\]

Then \(G_r/S=uQF+2^{\delta+D}\). At a zero of \(G_r\), its multiplicity is unchanged by division by \(S\), and neither \(Q\) nor \(F\) vanishes.

## 2. Two skeleton partitions

For \(0\le\ell<a\), set

\[
g_\ell=v_2(\ell!)+v_2((a-1-\ell)!),
\qquad
h_\ell=1+\lfloor\log_2\max(\ell,a-1-\ell)\rfloor,
\]

and \(C_\ell=\ell+2^{h_\ell}\mathbb Z_2\). When \(a=1\), use \(g_0=h_0=0\) and \(C_0=\mathbb Z_2\). These balls partition \(\mathbb Z_2\). For \(x\in C_\ell\) with \(x\ne\ell\), put \(s=v_2(x-\ell)\ge h_\ell\). Skeleton separation gives

\[
v_2Q(x)=g_\ell+s,
\qquad v_2Q'(x)=g_\ell.
\tag{4}
\]

For completeness, after substituting \(x=\ell+2^{h_\ell}Z\), the series \(2^{-g_\ell-h_\ell}P_a(x)\) is \(Z\) times a restricted integral unit whose reduction is a nonzero constant. Division by \(S(x)\) preserves this property. The normalized series therefore reduces to \(Z\), so its derivative is a unit. This proves both assertions, without taking a logarithmic derivative at a skeleton zero.

For \(0\le i<k\), put

\[
d_i=v_2(i!)+v_2((k-1-i)!),
\qquad
H_i=1+\lfloor\log_2\max(i,k-1-i)\rfloor,
\]

and \(B_i=i+2^{H_i}\mathbb Z_2\). Because \(2^t\mid k\), all \(H_i\ge t\). Also \(a<2^t\). Every translated complement ball \(a+B_i\) is contained in a lower skeleton ball \(C_\ell\).

The regular-wall atlas states:

* If \(\delta<d_i+H_i\), then \(v_2F(y)=\delta\) throughout \(B_i\).
* If \(\delta\ge d_i+H_i\), there is a unique simple root \(\alpha_i\in B_i\), with
  \[
  v_2F(y)=d_i+v_2(y-\alpha_i),\quad
  v_2F'(y)=d_i,\quad
  v_2(\alpha_i-i)=\delta-d_i.
  \tag{5}
  \]

## 3. The theorem

For \(\delta\ge1\), every multiple root of \(G_r\) must belong to a root-free complement ball. If \(x\in C_\ell\) and \(x-a\in B_i\), it must satisfy all of

\[
\boxed{
\begin{aligned}
 s=v_2(x-\ell)&=D-g_\ell\ge h_\ell,\\
 \delta&=d_i+D-g_\ell,\\
 v_2(i+a-\ell)&=D-g_\ell.
\end{aligned}}
\tag{6}
\]

Every root outside these explicitly specified strata is simple. In particular, every root over every emerged complement ball is simple.

### Proof

At a root, equation (2) and (4) imply

\[
v_2F(x-a)=\delta+D-g_\ell-s.
\tag{7}
\]

If the root were multiple, differentiation of \(uQF+2^{\delta+D}\) would give \(Q'F+QF'=0\). Taking valuations of its two nonzero summands yields

\[
v_2F(x-a)=s+v_2F'(x-a).
\tag{8}
\]

Suppose first that the complement ball has emerged. Put \(\gamma=\alpha_i+a\) and \(z=v_2(x-\gamma)\ge H_i\). Equations (5) and (8) force \(z=s\). Equation (7) then gives

\[
\delta-d_i=2s+g_\ell-D.
\tag{9}
\]

Since \(D=t-\Theta(a)<t\le H_i\), and \(s=z\ge H_i\), equation (9) implies \(\delta-d_i>H_i\). Furthermore \(s\ge H_i\) means that the translated complement ball contains \(\ell\). Thus \(i+a-\ell\) is divisible by \(2^{H_i}\).

By the definition of \(H_i\), we have \(0\le i<2^{H_i}\). Also \(1\le a-\ell\le a<2^t\le2^{H_i}\). Hence

\[
0<i+a-\ell<2^{H_i+1}.
\]

Its divisibility forces \(i+a-\ell=2^{H_i}\) exactly. From the exact displacement in (5) and \(\delta-d_i>H_i\), it follows that

\[
v_2(\gamma-\ell)=H_i.
\]

If \(s>H_i\), then \(v_2(x-\gamma)=H_i<s\). If \(s=H_i\), the units \((x-\ell)/2^{H_i}\) and \((\gamma-\ell)/2^{H_i}\) have even difference, so \(v_2(x-\gamma)>H_i=s\). Both contradict \(z=s\). Therefore emerged balls contain no multiple root.

Now suppose the complement ball is root-free. Its constant valuation and (7) give \(g_\ell+s=D\). In particular \(s=D-g_\ell<t\le H_i\), proving the first and third conditions in (6).

On \(B_i\), the derivative of \(P_k(y)U(y-k)\) has valuation exactly \(d_i\). This follows from its coefficientwise affine reduction after skeleton normalization. Since \(V\equiv1\pmod2\), we have \(V'\in2\mathbb Z_2\langle y\rangle\). If \(d_i>\delta\), equation (3) would give \(v_2F'>\delta\), incompatible with (8), which requires \(v_2F'=\delta-s\le\delta\). Therefore \(d_i\le\delta\), the skeleton derivative dominates, and \(v_2F'=d_i\). Equation (8) now yields \(\delta=d_i+s\), completing (6). ∎

## 4. A new complete simplicity band

The lower skeleton thresholds obey

\[
\min_{0\le\ell<a}(g_\ell+h_\ell)=v_2(a!).
\tag{10}
\]

Indeed \(P_a(x)\) is the falling factorial \(x(x-1)\cdots(x-a+1)\) times an odd-valued factor. On \(\mathbb Z_2\), the falling factorial divided by \(a!\) is integral: this follows on nonnegative integers from binomial coefficients, and on all of \(\mathbb Z_2\) by density and continuity. Thus \(v_2P_a(x)\ge v_2(a!)\). Equality holds at \(x=a\). On each partition ball \(C_\ell\), the minimum valuation in (4) is exactly \(g_\ell+h_\ell\), including the stated convention for \(a=1\). This proves (10).

Consequently condition (6) is impossible whenever

\[
\boxed{\Theta(a)\le t<\Theta(a)+v_2(a!).}
\tag{11}
\]

Under the certified wall and regular-address hypotheses, **every dyadic root is simple, at every positive wall distance, throughout (11)**. This is a universal theorem over the actual Euler multipliers meeting those hypotheses. It is not a finite computation statement. The band is empty for \(a=1\), as it should be.

Examples:

| Regular address \(a\) | \(\Theta(a)\) | \(v_2(a!)\) | Complement valuations \(t\) closed for every wall distance |
|---:|---:|---:|---|
| 2 | 8 | 1 | 8 |
| 3 | 11 | 1 | 11 |
| 4 | 15 | 3 | 15, 16, 17 |
| 5 | 17 | 3 | 17, 18, 19 |
| 6 | 21 | 4 | 21, 22, 23, 24 |
| 7 | 24 | 4 | 24, 25, 26, 27 |
| 8 | 28 | 7 | 28 through 34 |

For example \(k=256\), \(a=2\), \(j=258\), \(t=8\) gives a genuinely higher-address universal simplicity family. Its outer record scale is \(\Theta(256)=777\). Every certified wall with this true terminal and every \(L\ge777\) is simple at all dyadic roots. The same statement at equality uses the boundary argument below.

## 5. Exact surviving outer scales

Write \(k=2^tc\) with \(c\) odd, and write \(i=2^tb+\rho\), where \(0\le b<c\), \(0\le\rho<2^t\). Then

\[
d_i=k-1-t-s_2(b)-s_2(c-1-b).
\]

Adding \(\Theta(k)=3k+1+t+s_2(c-1)\) to the critical distance in (6), and using the binary valuation of a binomial coefficient, yields

\[
\boxed{
L=4k+t-\Theta(a)-g_\ell-v_2\binom{c-1}{b}.
}
\tag{12}
\]

This is necessary, together with the disc and root-valuation conditions in (6). It does not assert the existence of a root or tangency.

For address \(2\), \((g_0,g_1)=(0,0)\) and \((h_0,h_1)=(1,1)\). Thus the only possible critical scales are

\[
L=4k+t-8-v_2\binom{c-1}{b},\qquad
v_2(x-\ell)=t-8\ge1,\quad\ell\in\{0,1\}.
\]

For address \(3\), the pairs \((g_\ell,h_\ell)\) are \((1,2),(0,1),(1,2)\). The odd lower branch \(\ell=1\) can become critical only for \(t\ge12\), with scale \(L=4k+t-11-v_2\binom{c-1}{b}\). The two even lower branches can become critical only for \(t\ge14\), with scale \(L=4k+t-12-v_2\binom{c-1}{b}\).

For a power-of-two complement, \(c=1\), so the binomial valuation vanishes. The previous counterexample to combinatorial descent, \(k=4096\), \(a=3\), \(t=12\), therefore has just one possible critical scale:

\[
L=16385,\qquad \ell=1,\qquad v_2(x-1)=1.
\]

Its double lower residue does not produce an unresolved analytic problem at all other scales. In particular the previously displayed example \(L=12302\) lies far outside this sole critical scale, and all of its dyadic roots are simple by the present theorem.

## 6. Equality wall

At \(\delta=0\), the regular complement satisfies \(F\equiv1+X^{\underline{k}}\pmod2\). Because \(k\) is divisible by \(2^t\), with \(t\ge\Theta(a)\ge4\), the falling polynomial is zero at both binary residues and its derivative is the zero polynomial modulo two. Therefore \(F(y)\) is always a unit and \(F'(y)\) is always even.

On a lower skeleton ball, equation (4) gives

\[
v_2(Q'F)=g_\ell,
\qquad v_2(QF')\ge g_\ell+s+1>g_\ell.
\]

The derivative of the source-normalized root equation cannot vanish. **Every equality-wall root is simple for every regular lower address**, without the additional band (11).

## 7. What this closes and what it leaves

The actual finite prefix gives a valid extension beyond address one. It closes all emerged complement discs for every regular lower address. It proves a complete simplicity theorem in the explicit factorial-width band (11), including genuinely higher-address examples. Outside that band it leaves only the exact critical scales (12) and the local conditions (6).

It does not close the remaining unit cancellation on those critical strata. It does not cover irregular lower addresses, for which the finite prefix need not be a unit and must itself be resolved. No Lean verification is claimed. The accompanying finite checker audits the combinatorial and polynomial identities used here in its declared bounded ranges. The proof above, rather than those bounded checks, establishes the universal statements.

## Self-review

Reviewed all new notation, normalization signs, derivative exponents, branch thresholds, and displayed examples. Routine edits: notation disambiguated between lower scales \(h_\ell\) and complement scales \(H_i\). Mathematical-token corrections during proofreading: none. Residual obligations are stated in Section 7. Independent proof audit is requested separately.
