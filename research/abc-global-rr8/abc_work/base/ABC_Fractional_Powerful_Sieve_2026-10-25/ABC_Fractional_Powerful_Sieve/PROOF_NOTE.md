# ABC continuation — fractional powerful-part moments over prime multipliers

**Research checkpoint, 25 October 2026.** Mathematics: a self-contained derivation from the classical Brun–Titchmarsh inequality and elementary counting of powerful integers. All statements concern restricted families and/or density-one sets. This does **not** prove the unrestricted abc conjecture. No Lean compilation or claim of historical priority.

## 1. Notation

Write \(\operatorname{rad}(n)=\prod_{p\mid n}p\) and \(M(n)=n/\operatorname{rad}(n)\). Let \(H\) grow, \(0<\eta<1\), and \(Q\) be a positive integer with \(Q\le H^{1-\eta}\). The variable \(h\) ranges over primes \(h\le H\).

A primitive triple \((1,hQ,1+hQ)\) is an *ABC hit* if \(1+hQ>\operatorname{rad}(hQ(1+hQ))\). An ABC hit necessarily has \(M(1+hQ)>\operatorname{rad}(hQ)\ge h\).

## 2. Exact positive powerful-divisor expansion

**Lemma 2.1.** Let \(0<\sigma<1/2\). Define the multiplicative arithmetic function \(b_\sigma\) by

\[
 b_\sigma(1)=1,\quad b_\sigma(p)=0,\quad b_\sigma(p^e)=p^{\sigma(e-1)}-p^{\sigma(e-2)}\quad(e\ge2).
\]

Then \(b_\sigma(d)\ge0\), it vanishes unless \(d\) is powerful (all nonzero prime exponents at least two), and

\[
 \boxed{ M(n)^\sigma=\sum_{d\mid n}b_\sigma(d). }
\]

**Proof.** For \(p^k\parallel n\) with \(k\ge1\), the local sum is
\(1+\sum_{e=2}^k(p^{\sigma(e-1)}-p^{\sigma(e-2)})=p^{\sigma(k-1)}\).
For \(k=0\) it is 1. Multiply the local identities. Moreover, \(0\le b_\sigma(d)\le d^\sigma\).

**Lemma 2.2 (powerful-number estimates).** The number of powerful integers up to \(X\) is \(O(\sqrt X)\). Consequently, for any \(0<\sigma<1/2\),

\[
 \sum_{\substack{d>T\\d\text{ powerful}}}\frac{b_\sigma(d)}d\ll_\sigma T^{\sigma-1/2},
 \quad \sum_{\substack{d\le X\\d\text{ powerful}}}b_\sigma(d)\ll_\sigma X^{\sigma+1/2},
 \quad \sum_{d\text{ powerful}}\frac{b_\sigma(d)}{\varphi(d)}<\infty.
\]

**Proof.** Every powerful integer has a representation \(d=a^2b^3\) with squarefree \(b\), obtained separately at each prime. Thus the count is at most \(\sum_{b\le X^{1/3}}\sqrt{X/b^3}\ll\sqrt X\). The first two bounds follow by dyadic summation and \(b_\sigma(d)\le d^\sigma\). For the third, apply the elementary inequality \(d/\varphi(d)\ll_\epsilon d^\epsilon\) with \(\epsilon<1/2-\sigma\), followed by dyadic summation.

## 3. Uniform prime-input fractional moment

**Theorem 3.1.** Fix \(0<\eta<1\) and

\[
 0<\sigma<\frac{\eta}{2(2-\eta)}.
\]

There exists \(C_{\eta,\sigma}>0\) such that, for all sufficiently large \(H\), uniformly for all integers \(1\le Q\le H^{1-\eta}\),

\[
 \boxed{ \frac1{\pi(H)}\sum_{h\le H\atop h\text{ prime}}M(1+Qh)^\sigma\le C_{\eta,\sigma}. }
\]

**Proof.** Put \(X=1+HQ\) and \(T=H^{1/2}\). Expand by Lemma 2.1 and reverse the nonnegative sums:

\[
 \sum_{h\le H\atop h\text{ prime}}M(1+Qh)^\sigma
 =\sum_{\substack{d\le X\ d\text{ powerful}\\(d,Q)=1}}b_\sigma(d)\pi(H;d,-Q^{-1}),
\]

where the \(d=1\) term is interpreted as \(\pi(H)\). If \((d,Q)>1\), then \(d\nmid 1+Qh\), so omitting it is exact.

For \(2\le d\le T\), the residue class is reduced. Brun–Titchmarsh yields
\(\pi(H;d,-Q^{-1})\le2H/[\varphi(d)\log(H/d)]\ll H/[\varphi(d)\log H]\).
Since \(\pi(H)\gg H/\log H\), Lemma 2.2 shows that the small-modulus sum contributes \(O_\sigma(1)\) to the normalized average.

For \(d>T\), bound the number of primes by the number of integers in the class:
\(\pi(H;d,-Q^{-1})\le H/d+1\). Dividing by \(\pi(H)\gg H/\log H\) and invoking Lemma 2.2 bounds the remaining average by

\[
 \ll_\sigma (\log H)\left(T^{\sigma-1/2}+\frac{X^{\sigma+1/2}}H\right).
\]

With \(T=H^{1/2}\) and \(X\le1+H^{2-\eta}\), this is

\[
 \ll_{\eta,\sigma}(\log H)\left(H^{(\sigma-1/2)/2}+H^{(2-\eta)(\sigma+1/2)-1}\right)=o(1),
\]

because both exponents are negative precisely in the indicated range. This proves the theorem. No independence assumption between different prime-square divisibility events is used.

**Safe explicit exponent.** Choosing \(\sigma=\eta/8\) is valid for every \(0<\eta<1\).

## 4. Simultaneous ABC non-hit theorem for bounded input alphabets

Let \(S\) be a fixed finite nonempty set of primes. An \(S\)-unit positive integer is \(Q=\prod_{q\in S}q^{f_q}\) with \(f_q\ge0\).

**Theorem 4.1.** Fix \(S\), \(0<\eta<1\), and \(0<\sigma<\eta/[2(2-\eta)]\). All but

\[
 \boxed{O_{S,\eta,\sigma}\bigl(H^{1-\sigma}(\log H)^{|S|-1}\bigr)}
\]

primes \(h\in(H/2,H]\) have the following property simultaneously for **every** positive \(S\)-unit \(Q\le H^{1-\eta}\):

\[
 \boxed{1+hQ\le \operatorname{rad}\bigl(hQ(1+hQ)\bigr).}
\]

**Proof.** If the displayed inequality fails, then \(M(1+hQ)>\operatorname{rad}(hQ)\ge h>H/2\). By Markov's inequality and Theorem 3.1, for each eligible \(Q\), the number of bad primes \(h\in(H/2,H]\) is
\(\ll_{\eta,\sigma}\pi(H)H^{-\sigma}\ll H^{1-\sigma}/\log H\).
The number of positive \(S\)-units \(Q\le H^{1-\eta}\) is \(O_S((\log H)^{|S|})\), since each exponent satisfies \(f_q\le\log H/\log q\). Take the union bound.

For the single-prime alphabet \(S=\{q\}\) and \(\sigma=\eta/8\), the exceptional count is \(O_\eta(H^{1-\eta/8})\), uniform in the fixed prime \(q\). Since the prime count in the interval is \(\asymp H/\log H\), the exceptional density tends to zero.

### What the theorem does NOT assert

- It makes no statement about **each** prime multiplier \(h\).
- It does not cover \(Q\) growing as fast as \(H\) or faster.
- It does not control an adversarial \(S\) that grows with \(H\).
- It is not the full abc conjecture and does not assert historical originality.

## 5. A genuine exception inside the allowed range

\[
 \boxed{1+643\cdot3^5=156250=2\cdot5^7.}
\]

The input radical is \(3\cdot643\), the full radical is \(R=2\cdot3\cdot5\cdot643=19290\), and \(156250/R\approx8.10>1\). For \(H=700\), \(h=643\in(H/2,H]\), and \(Q=3^5=243\le H^{0.9}\), this is a bona fide ABC hit in the counted family. The theorem allows finitely many such exceptions and bounds their total number, not their individual sizes.

## 6. Why this is relevant to Realization Calculus

Earlier fixed-support CRT examples demonstrated arbitrary local prime-power contact by letting the exponent height grow. The present theorem shows that, when the multiplier's exponent height stays substantially below the magnitude of the new prime input, the set of genuine global ABC hits is power-saving sparse. This quantifies a **realization-height tradeoff** without claiming a pointwise global coherence inequality.

The key new bridge relative to the predecessor two-axis sieve is a positive *multiplicative* expansion over all powerful divisors; it gives bounded fractional moments of the **complete** output powerful part without cutting off large prime powers.

## 7. Verification and external dependencies

The bundled `verify.py` computes exact radical and powerful parts for bounded samples, checks the exact divisor expansion at integer exponent 1, and verifies the explicit exceptional triple. Finite checks are not used to prove the general theorem.

External dependencies: Montgomery–Vaughan's Brun–Titchmarsh inequality, elementary prime-counting bounds \(\pi(H)\asymp H/\log H\), and the elementary estimate \(d/\varphi(d)\ll_\varepsilon d^\varepsilon\). The powerful-number counting and divisor expansion are proved above.

Primary expository source for Brun–Titchmarsh: https://encyclopediaofmath.org/wiki/Brun%E2%80%93Titchmarsh_theorem

No new Lean module was compiled in this run. The claim classification is: unconditional mathematical implication from established external theorems, exact finite checks, and an explicit open boundary. 
