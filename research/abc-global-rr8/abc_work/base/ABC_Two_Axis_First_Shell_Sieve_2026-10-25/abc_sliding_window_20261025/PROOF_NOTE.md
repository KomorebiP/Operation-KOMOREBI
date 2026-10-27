# ABC: Two-Axis First-Shell Sieve and Uniform Moving-Window Bounds

**Research continuation | 25 October 2026**

**Status.** The theorems below are unconditional elementary consequences of multiplicative orders, lifting the exponent, Chebyshev's bound for primes, and the Chinese remainder theorem. The input-height and full-radical inequality required by the abc conjecture remain open. Exact finite tests accompany this note. No Lean compilation is claimed and no priority claim is made.

## 1. Motivation and notation

Let

\[
  U(h,f)=1+hq^f,\qquad q\ge2,\quad h,f\ge1.
\]

This is the primitive relation \(1+hq^f=U(h,f)\). For a prime \(p\), the weighted contribution of repeated \(p\)-power content is

\[
  (v_p(U)-1)_+\log p=\sum_{e\ge2}(\log p)\,\mathbf1_{p^e\mid U}.
\]

For real \(Y\ge2, X\ge4\), define the truncated weight

\[
  T_{Y,X}(h,f)=\sum_{\substack{p>Y,\ e\ge2\\p^e\le X}}(\log p)\,\mathbf1_{p^e\mid U(h,f)}.
\]

Let \(d_p=\operatorname{ord}_p(q)\) for primes \(p\nmid q\). An odd prime is **ordinary** if \(v_p(q^{d_p}-1)=1\). We write \(T^{\rm ord}_{Y,X}\) for the sum restricted to ordinary primes. All sums with \(p>Y\ge2\) automatically involve odd primes.

The cut-off \(p^e\le X\) is a cut-off on the *entire prime power*, not merely on \(p\). This distinction produces a square-root saving in the rounding error.

## 2. The multiplicative-order tail

**Lemma 2.1 (fixed-base tail).** For every integer \(q\ge2\) and \(Y\ge2\),

\[
\boxed{\sum_{\substack{p>Y\\p\nmid q}}\frac{\log p}{(p-1)d_p}\ll_q Y^{-1/2}.}
\]

**Proof.** Partition primes above \(Y\) into dyadic intervals \([x,2x)\). If \(d_p\le\sqrt{x}\), group by exact order \(d\). All primes in the group divide \(q^d-1\). The sum of their logarithms is at most \(\log(q^d-1)\le d\log q\). Their total weighted contribution is therefore

\[
 \le \frac{1}{x-1}\sum_{d\le\sqrt{x}}\frac{d\log q}{d}\ll_q x^{-1/2}.
\]

For \(d_p>\sqrt{x}\), the elementary Chebyshev bound \(\vartheta(2x)=\sum_{p\le2x}\log p\ll x\) gives

\[
 \sum_{x\le p<2x\atop d_p>\sqrt{x}}\frac{\log p}{(p-1)d_p}\ll x^{-1/2}.
\]

Sum geometrically over the dyadic intervals. QED.

**Lemma 2.2 (prime-power rounding budget).** For \(X\ge4\),

\[
\boxed{\sum_{e\ge2}\ \sum_{p^e\le X}\log p\ll\sqrt X.}
\]

**Proof.** Write the sum as \(\sum_{e=2}^{\lfloor\log_2 X\rfloor}\vartheta(X^{1/e})\). The term \(e=2\) is \(O(\sqrt X)\). The other terms are at most \(O(X^{1/3}\log X)=O(\sqrt X)\) by Chebyshev and the boundedness of \(\log X/X^{1/6}\) on \([4,\infty)\). QED.

## 3. Exponent-direction theorem

**Theorem 3.1 (all translated windows, ordinary primes).** Fix \(q\ge2\). For every \(h\ge1\), \(N\ge0\), \(F\ge1\), \(Y\ge2\), and \(X\ge4\),

\[
\boxed{\frac1F\sum_{f=N+1}^{N+F}T^{\rm ord}_{Y,X}(h,f)\ll_q Y^{-1/2}+\frac{\sqrt X}{F}.}
\]

The constant is independent of \(h,N,F,Y,X\).

**Proof.** For an ordinary odd prime \(p\nmid qh\), \(q^d\in1+p\mathbb Z_p\) with valuation exactly one above unity, where \(d=d_p\). For every \(e\ge2\), lifting the exponent shows \(q^d\) has exact order \(p^{e-1}\) in the group of principal units modulo \(p^e\). Therefore the congruence

\[
1+hq^f\equiv0\pmod{p^e}
\]

is either insoluble or selects exactly one class \(f\pmod{dp^{e-1}}\). The number of solutions in any interval of \(F\) consecutive exponents is at most \(F/(dp^{e-1})+1\). Multiply by \(\log p\), sum over \(p^e\le X\) and \(p>Y\), then apply Lemmas 2.1 and 2.2. QED.

**Corollary 3.2 (uniform sparse window).** For any fixed \(0<\alpha<\beta<1\), the number of exponents \(f\in(N,N+F]\) for which at least one ordinary prime satisfies

\[
 F^\alpha<p\le F^\beta,\qquad p^2\mid1+hq^f,
\]

is

\[
\boxed{\ll_{q,\alpha,\beta}\frac{F^{1-\alpha/2}+F^\beta}{\log F}.}
\]

**Proof.** Set \(Y=F^\alpha\), \(X=F^{2\beta}\), and note that each eligible square contributes at least \(\alpha\log F\). Apply Theorem 3.1, then multiply by \(F\). QED.

The simple balanced choice \((\alpha,\beta)=(1/2,3/4)\) yields \(O_q(F^{3/4}/\log F)\) in every translated interval.

## 4. The dual multiplier-direction theorem

The exponent direction is singular at Wieferich primes. The **multiplier direction is never singular** at primes not dividing \(q\):

\[
 \frac{\partial}{\partial h}(1+hq^f)=q^f\in\mathbb Z_p^\times.
\]

**Theorem 4.1 (all repeated primes, including Wieferich).** For all integers \(q\ge2\), \(f\ge1\), \(K\ge0\), \(H\ge1\), \(Y\ge2\), and \(X\ge4\),

\[
\boxed{\frac1H\sum_{h=K+1}^{K+H}T_{Y,X}(h,f)\ll \frac1Y+\frac{\sqrt X}{H}.}
\]

The implied constant is absolute, independent of \(q,f,K,H,Y,X\).

**Proof.** Any prime \(p\mid q\) cannot divide \(1+hq^f\). For \(p\nmid q\), the congruence \(p^e\mid1+hq^f\) determines precisely one class

\[
 h\equiv -q^{-f}\pmod{p^e}.
\]

Thus at most \(H/p^e+1\) multipliers in any length-\(H\) interval satisfy the congruence. Weighted summation gives

\[
 \frac1H\sum_h T_{Y,X}(h,f)
 \le \sum_{p>Y}\sum_{e\ge2}\frac{\log p}{p^e}
 +\frac1H\sum_{p^e\le X\atop e\ge2}\log p.
\]

The first term is \(\sum_{p>Y}\log p/(p(p-1))\ll1/Y\), by partial summation using \(\vartheta(t)\ll t\). Lemma 2.2 bounds the second. QED.

**Corollary 4.2 (two-direction rectangle).** Averaging \(T^{\rm ord}\) over the rectangle \(K<h\le K+H\), \(N<f\le N+F\) gives

\[
 \frac1{HF}\sum_{h,f}T^{\rm ord}_{Y,X}(h,f)
 \ll_q \min\left\{Y^{-1/2}+\frac{\sqrt X}{F},\quad Y^{-1}+\frac{\sqrt X}{H}\right\}.
\]

The second bound also applies to \(T_{Y,X}\) including every Wieferich prime. Neither estimate is pointwise for an individual arithmetic triple.

## 5. Prime-input theorem by Brun–Titchmarsh

The previous multiplier estimate averages over all integer multipliers, including those with many prime factors. It is therefore important to prove a result that applies to the **prime multiplier family** \(a=1,b=hq^f\) with \(h\) prime. A standard theorem on primes in arithmetic progressions supplies the required estimate.

Let \(\pi(H)\) be the number of primes \(h\le H\). For a fixed \(0<\delta<1\), assume \(H\) is sufficiently large and \(X\le H^{1-\delta}\).

**Theorem 5.1 (prime multipliers, including all Wieferich primes).** Uniformly in \(q\ge2\), \(f\ge1\), \(Y\ge2\), and \(4\le X\le H^{1-\delta}\),

\[
\boxed{
\frac1{\pi(H)}\sum_{\substack{h\le H\\h\text{ prime}}}T_{Y,X}(h,f)
\ll_\delta\frac1Y.
}
\]

No condition about the order or Wieferich status of an output prime is necessary.

**Proof.** For each \(p\nmid q\) and each \(e\ge2\), the congruence \(p^e\mid1+hq^f\) selects the unique reduced residue class

\[
 h\equiv -q^{-f}\pmod{p^e}.
\]

The Brun–Titchmarsh inequality for primes \(h\le H\) in this progression reads

\[
 \pi(H;p^e,-q^{-f})\le \frac{2H}{\varphi(p^e)\log(H/p^e)}.
\]

As \(p^e\le X\le H^{1-\delta}\), the denominator logarithm is at least \(\delta\log H\). Since \(\pi(H)\gg H/\log H\) by elementary prime-counting bounds, the proportion of prime multipliers satisfying that one congruence is

\[
 \ll_\delta\frac1{\varphi(p^e)}.
\]

Sum over prime powers and use

\[
 \sum_{e\ge2}\frac1{\varphi(p^e)}
 =\sum_{e\ge2}\frac1{p^{e-1}(p-1)}=\frac1{(p-1)^2},
\]

and then \(\sum_{p>Y}(\log p)/(p-1)^2\ll1/Y\), by partial summation and \(\vartheta(t)\ll t\). QED.

**Corollary 5.2 (prime-supported sparsity).** Under the same hypotheses, the fraction of prime multipliers \(h\le H\) for which there is any output prime \(p>Y\) and exponent \(e\ge2\) with \(p^e\le X\) and \(p^e\mid1+hq^f\) is

\[
\boxed{\ll_\delta\frac1{Y\log Y}.}
\]

For example, if \(0<\alpha<(1-\delta)/2\), then all but \(O_{\alpha,\delta}(\pi(H)/(H^\alpha\log H))\) prime multipliers have **no squared output prime** in the interval

\[
 H^\alpha<p\le H^{(1-\delta)/2}.
\]

**Corollary 5.3 (many exponents simultaneously).** Let \(\mathcal F\) be any finite set of \(F\) positive exponents, possibly astronomically large. All but

\[
 \boxed{O_\delta\left(\frac{F\pi(H)}{Y\log Y}\right)}
\]

prime multipliers \(h\le H\) avoid every event \(p^e\mid1+hq^f\) with \(f\in\mathcal F\), \(p>Y\), \(e\ge2\), and \(p^e\le X\). This is a direct union bound and is uniform in the positions of the exponents. In particular, if \(F=o(Y\log Y)\), a density-one subset of prime multipliers avoids all the designated contacts simultaneously.

The theorem uses the classical Brun–Titchmarsh inequality, not a new distribution theorem for primes. It applies directly to genuine inputs with two prime factors when \(q\) itself is prime and \(h\ne q\). The remaining weakness is that it is still **an average over prime \(h\)**, not a bound for each prime multiplier.

## 5. Exact negative control: five large squared primes at one exponent

The failure of any putative pointwise statement uniform over input prime \(h\) is explicit. Take

\[
 q=3,\quad f=23,\quad h=1452595321237\quad(\text{prime}).
\]

Then

\[
 \begin{aligned}
 1+h3^{23}&=136751941090478401849000\\
 &=2^3\cdot5^3\cdot7^2\cdot17^2\cdot19^2\cdot23^2\cdot911\cdot2593\cdot21407.
 \end{aligned}
\]

All prime factorizations and the primality of \(h\) are independently checked in `verify.py` using a deterministic Miller–Rabin test for 64-bit inputs. The input radical is \(3h=4357785963711\). The full radical is

\[
 R=114596405860108132732260752130>c.
\]

Hence this is not an ABC exception. It shows why the density statements do not bound a prescribed exceptional realization, and illustrates that the input radical can pay for an arbitrarily high collection of local conditions.

More generally, fix \(q\ge2\), \(f\ge1\), and any finite set of primes \(P\) not dividing \(q\). By the Chinese remainder theorem there is a unique class \(h\pmod{\prod_{p\in P}p^2}\) for which all \(p^2\mid1+hq^f\). That class is coprime to the modulus, so Dirichlet's theorem supplies infinitely many **prime** choices of \(h\) with all those simultaneous square divisibilities. Consequently no bound depending only on the fixed base \(q\) and on a chosen exponent \(f\) can limit the number of such channels without paying for the size of \(h\).

## 7. What is still missing for abc

The direction-dependent average estimates are not estimates at an individual point \((h,f)\). The elementary horizontal theorem averages over **all positive multipliers**; Theorem 5.1 also handles prime multipliers, but only after averaging over primes \(h\le H\) and only for prime powers \(p^e\le H^{1-\delta}\). Neither bound is pointwise for a chosen prime \(h\). The vertical theorem excludes Wieferich channels and becomes weak once \(p^2\) is larger than the square of the exponent-window length.

For \(a=1\), \(b=hq^f\), the ABC conjecture requires the pointwise inequality

\[
 \log\operatorname{rad}(1+hq^f)\ge
 \frac{\log(1+hq^f)}{1+\varepsilon}
 -\log\operatorname{rad}(hq)-O_\varepsilon(1).
\]

Neither theorem proves this. A successful new result would have to control exceptional sparse multipliers and moving output primes with prime-square sizes far beyond the available averaging window, with a quantitative connection to the actual input height. This is the proper remaining arithmetic target.

## 8. Verification

The standard-library program `verify.py` checks the unique lifted classes in the exponent direction, direct modular evaluation independently of progression counting, unique multiplier classes at every prime power, two distant exponent windows, two distant multiplier windows, three prime-multiplier cases, exact CRT congruences, and a fully factored explicit spike. The program produces `results.json`. The tests are finite, not a substitute for the proofs above. No Lean verification was performed.

## References

* P. Chebyshev, classical estimates for the prime-counting functions \(\vartheta(x)\) and \(\pi(x)\).
* The standard lifting-the-exponent lemma for odd primes.
* Dirichlet's theorem on primes in arithmetic progressions.
* H. L. Montgomery and R. C. Vaughan, *The large sieve*, Mathematika 20 (1973), 119–134. The Brun–Titchmarsh inequality is used only for Theorem 5.1 and its corollaries; see also https://encyclopediaofmath.org/wiki/Brun%E2%80%93Titchmarsh_theorem.
* K. C. Chim, *Lower bounds for linear forms in two p-adic logarithms*, Journal of Number Theory 266 (2025), 295–349, https://doi.org/10.1016/j.jnt.2024.07.012. Context for the complementary fixed-prime pointwise method; it is **not** used in these sieve proofs.
