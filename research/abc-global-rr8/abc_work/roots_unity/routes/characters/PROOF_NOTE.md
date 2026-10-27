# Roots of unity that retain prime-power depth

Base: RR2 archive SHA-256 `f5b5e7336d5cae31502106100997cf02733b1054f62e3df39827002cfe7e9469`.

Inputs: `abc_work/LATEST.md`, SHA-256 `c764c76cb7823213358d51165b7f865c223cfbe2f5c116e079f246ce2749eff2`; and `abc_work/routes/global/PROOF_NOTE.md`, SHA-256 `f4b1c1eb8d4e52ee43634b454ea5fa3e12e88488dc148d76ea68e79a58e29bfc`.

This note proves exact character projectors, depth-sensitive period formulas, and the correlation law for simultaneous contacts. It tests specific proposed counting bounds. It does not prove ABC or a uniform bound on exceptional birth depth. All proofs are elementary. No historical priority or Lean certificate is claimed.

## 1. Full and primitive-conductor additive projectors

For q>=1 let `e_q(t)=exp(2*pi*i*t/q)` and

\[
P_q(t)=\frac1q\sum_{j=0}^{q-1}e_q(jt).
\]

The finite geometric sum gives the exact identity

\[
\boxed{P_q(t)=1_{q\mid t}.}\tag{1}
\]

For an odd prime p and e>=1, collect just primitive frequencies:

\[
c_{p^e}(t)=\sum_{j\bmod p^e\atop p\nmid j}e_{p^e}(jt).
\]

Subtract the nonprimitive frequencies from the full sum to obtain

\[
\boxed{c_{p^e}(t)=p^eP_{p^e}(t)-p^{e-1}P_{p^{e-1}}(t).}\tag{2}
\]

Here `P_1(t)=1`. Consequently

\[
c_{p^e}(t)=
\begin{cases}
p^{e-1}(p-1),&v_p(t)\ge e,\\
-p^{e-1},&v_p(t)=e-1,\\
0,&v_p(t)<e-1.
\end{cases}\tag{3}
\]

Telescoping (2), with `c_1(t)=1`, gives

\[
\boxed{p^eP_{p^e}(t)=\sum_{k=0}^{e}c_{p^k}(t).}\tag{4}
\]

Thus roots of unity can retain every prime-power depth. A primitive-conductor shell alone is not a divisibility indicator: it has the negative value in (3). Its normalized value `c_(p^e)/phi(p^e)` equals 1 at a depth-e contact, irrespective of how large e is. There is no automatic depth attenuation at that point.

For nonzero t and an integer L>=2, the truncated powerful-part valuation has the exact expansion

\[
\boxed{\min\{(v_p(t)-1)_+,L-1\}=\sum_{e=2}^{L}P_{p^e}(t)
=\sum_{e=2}^{L}\frac1{p^e}\sum_{k=0}^{e}c_{p^k}(t).}\tag{5}
\]

This is the relevant filter for `log U(t)`, rather than the depth-one projector. If `v_p(t)>=L`, every summand on the left-hand depth sum is 1. The conductor expansion reproduces L-1, including all normalization factors, rather than cancelling the contact.

More generally `qP_q(t)=sum_(d|q)c_d(t)`, by sorting a frequency according to its conductor. For coprime q and r, `P_q(t)P_r(t)=P_(qr)(t)`. These identities retain all CRT information. At the already satisfied relation `a+b-c=0`, however, every character phase is 1, so the projector is 1 and yields no additional arithmetic inequality.

## 2. Multiplicative and exponent projectors

Let A>B>=1 be coprime, let p be an odd prime not dividing AB, and put

\[
d=\operatorname{ord}_p(A/B),\qquad s=v_p(A^d-B^d)\ge1.
\]

The ratio is taken in the finite group of units. For each e>=1 its order modulo `p^e` is

\[
\boxed{d_e=d\,p^{\max\{0,e-s\}}.}\tag{6}
\]

Proof: if `(A/B)^m=1 mod p^e`, then `d|m`. Write m=dk. The elementary odd-prime lifting identity gives

\[
v_p(A^{dk}-B^{dk})=s+v_p(k).
\]

Because `d|p-1`, the smallest positive k reaching depth e is `p^[max(0,e-s)]`. This proves (6).

The contact `p^e|A^n+B^n` is impossible when d is odd. When d is even it is equivalent to

\[
\boxed{n\equiv d_e/2\pmod {d_e}.}\tag{7}
\]

Indeed, a power of the ratio equals -1 precisely halfway around its cyclic subgroup. The only element of order two among units modulo an odd prime power is -1: factor `(z-1)(z+1)=0 mod p^e`, noting that the two factors have gcd dividing 2. This proves (7) without presuming independence or equidistribution.

Formula (7) has an exact roots-of-unity representation in exponent space:

\[
\boxed{1_{p^e\mid A^n+B^n}
=\frac1{d_e}\sum_{j=0}^{d_e-1}
\exp\!\left(2\pi i j\frac{n-d_e/2}{d_e}\right).}\tag{8}
\]

Equivalently, if `G_e=(Z/p^e Z)^*` and `G_e^hat` is its full character group,

\[
1_{p^e\mid A^n+B^n}
=\frac1{|G_e|}\sum_{\chi\in\widehat G_e}
\chi((A/B)^n)\overline{\chi(-1)}.\tag{9}
\]

Character orthogonality proves (9). Both formulas retain prime-power depth exactly, but their normalization reflects the true contact set. In particular,

\[
\boxed{d_e=d\quad\text{for every }1\le e\le s.}\tag{10}
\]

There is a birth-depth plateau. Requiring p^2, ..., p^s contact imposes no additional exponent condition beyond p contact. Only at depths above s does the period grow by a factor p for each new depth.

## 3. A concrete false bound and arbitrary plateaus

A tempting proposed saving is

\[
\#\{1\le n\le N:p^e\mid A^n+B^n\}
\stackrel{?}{\le}\frac N{d p^{e-1}}+1.\tag{11}
\]

It is false. For A=2, B=1, p=1093, one has d=364 and s=2. Set e=2 and N=728. Both n=182 and n=546 have p^2 contact. The right side of (11) is `1+2/1093<2`. The exact count from (7) is

\[
\boxed{\#\{1\le n\le N:p^e\mid A^n+B^n\}
=\left\lfloor\frac{N+d_e/2}{d_e}\right\rfloor}\tag{12}
\]

when d is even. This supplies the corrected uniform statement.

Arbitrarily deep plateaus are possible within the coprime-base domain. For an odd prime p and L>=1, take `A=p^L-1`, B=1. Then d=2 and s=L, since `v_p(A+1)=L` and `p` does not divide `A-1`. Every odd n has

\[
v_p(A^n+1)=L+v_p(n).
\]

The density of p^L contacts in exponent space is exactly 1/2, independently of L. This example does not refute ABC: A grows with L and its radical still has to be included. It refutes a purported depth penalty inferred from orthogonality alone.

## 4. Simultaneous filters synchronize through a least common multiple

Consider distinct odd primes p_i not dividing AB, with birth data d_i,s_i, and prescribed depths e_i>=1. Put

\[
q_i=d_i p_i^{\max\{0,e_i-s_i\}}.
\]

If any d_i is odd, there are no simultaneous contacts. Otherwise let `D=lcm_i(q_i)`.

**Exact correlation law.** The simultaneous contact set is empty unless all `v_2(q_i)` are equal. If they are equal, then

\[
\boxed{p_i^{e_i}\mid A^n+B^n\ \text{for every i}
\iff n\equiv D/2\pmod D.}\tag{13}
\]

To prove this, write `q_i=2^r m_i` with m_i odd when the common 2-adic valuation r exists. The ith half-order condition is precisely `n=2^(r-1)m_i*k_i` with k_i odd. All these hold iff `n=2^(r-1)lcm_i(m_i)*k` with k odd, which is (13). Different 2-adic valuations prescribe incompatible values of `v_2(n)`.

Thus the joint density over a complete exponent period is

\[
\boxed{1/D,\quad\text{not generally }\prod_i1/q_i.}\tag{14}
\]

For example A=2, B=1, p_1=3 and p_2=11 have d_1=2, d_2=10. Their depth-one intersection is `n=5 mod 10`, of density 1/10, while the product of marginal densities is 1/20. With p_1=3 and p_2=5, the respective orders 2 and 4 have different 2-adic valuations and the intersection is empty.

A stronger exact synchronized family is obtained by choosing finitely many odd primes and setting

\[
A=(\prod_i p_i)^L-1,\qquad B=1.
\]

Each d_i=2 and s_i=L. All depth-L filters coincide with the odd-exponent projector. The joint density is 1/2 even though the product of marginal densities is `2^(-#i)`.

This directly addresses the RR2 primitive-prime obstruction. At a fixed odd prime exponent ell, every primitive output prime has `d_i=2ell`. For all depths `e_i<=s_i`, their exponent projectors coincide. Multiplying those projectors retains one condition `n=ell mod 2ell`; it does not supply one independent small factor for each exceptional prime. Birth-prime size is absent from that shared exponent modulus.

## 5. Exact positive birth mass in averaged character coefficients

Let d be even. Average over one complete period d_L, where L>=max(2,s). By (7), the normalized average of the depth-e contact projector is exactly `1/d_e`. Hence (5) gives

\[
\frac1{d_L}\sum_{n=1}^{d_L}
\min\{(v_p(A^n+B^n)-1)_+,L-1\}
=\frac1d\left(s-1+\sum_{k=1}^{L-s}p^{-k}\right).\tag{15}
\]

The limit as L increases is

\[
\boxed{\frac1d\left(s-1+\frac1{p-1}\right).}\tag{16}
\]

Multiplying by log p gives the exact local mean logarithmic powerful-part mass. The entire birth-depth contribution `(s-1)log(p)/d` is in the principal Fourier coefficient. Nonprincipal characters cancel in a complete average, leaving this positive term. A new argument is needed to bound its size or its sum over moving primes.

For the truncated local powerful factor, and any real sigma>0, the corresponding exact mean is

\[
1+\sum_{e=2}^{L}
\frac{p^{\sigma(e-1)}-p^{\sigma(e-2)}}{d_e}.\tag{17}
\]

At e<=s the sum telescopes to `(p^[sigma(s-1)]-1)/d`. Thus replacing logarithms by positive fractional moments does not remove exceptional birth mass either. No product law across primes is claimed.

Finally, use the RR2 definition

\[
W_n=\prod_{p\text{ odd},\ p\mid A^n+B^n}p^{s_p-1}.
\]

For a fixed N, only finitely many primes occur, all dividing `prod_(n<=N)(A^n+B^n)`. Formula (12) gives the exact finite identity

\[
\boxed{\sum_{n=1}^N\log W_n
=\sum_{p\text{ odd},\ d_p\text{ even},\ d_p\le2N}
(s_p-1)\log p\,
\left\lfloor\frac{N+d_p/2}{d_p}\right\rfloor.}\tag{18}
\]

The sum is over the finite set of primes with the displayed order condition for these fixed bases; each such prime divides at least one output with n<=N. This makes the remaining weighted quantity explicit. Orthogonality has not bounded `s_p`, the weighted birth sum, or its last exceptional height.

## 6. Result and remaining obligation

Roots of unity do generalize to complete conductor and exponent projectors. They preserve depth exactly and yield explicit formulas for all local and joint contacts. Two potentially useful but false shortcuts have been isolated: an automatic factor p for every extra contact depth, and multiplication of marginal contact densities across primes.

The surviving obligation is arithmetic: control the weighted birth depths at large exceptional primes, or transfer their cost to the input radical. The character formulas alone provide exact representations and correlation laws, not the missing uniform inequality. ABC remains unresolved.
