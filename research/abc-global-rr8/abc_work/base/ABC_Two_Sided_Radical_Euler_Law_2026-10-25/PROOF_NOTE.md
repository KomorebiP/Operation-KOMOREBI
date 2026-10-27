# ABC continuation: exact two-sided radical ceiling and prime-multiplier Euler laws

**Research checkpoint — 25 October 2026**  
**Status:** Elementary exact identities; a stronger conditional-range uniform moment theorem from Brun–Titchmarsh; a uniform Euler-product law from Siegel–Walfisz; elementary deterministic exceptional-set bounds; independent exact verification. **ABC remains open.** No Lean compilation and no priority claim.

## 1. Notation and the exact two-sided relation

For an integer `n>=1` put `r(n)=rad(n)` and `U(n)=n/r(n)`; `r(1)=U(1)=1`.

For `gcd(a,b)=1` and `a+b=c`, the three integers are pairwise coprime, and therefore

\[
 R=r(abc)=r(a)r(b)r(c)=\frac{abc}{U(a)U(b)U(c)}.
\]

Consequently, for any `delta>=0` and `gamma=delta/(1+delta)`,

\[
\boxed{c>R^{1+\delta}\iff U(a)U(b)U(c)>ab\,c^\gamma.}\tag{1}
\]

In particular an ABC hit, `c>R`, is equivalent to `U(a)U(b)U(c)>ab`.

For `a=1`, write `b=D K` with `D=r(b)` and `K=U(b)`. Since `c=b+1=DK+1`,

\[
 c>r(bc)=D r(c)\iff r(c)<K+1/D\iff\boxed{r(b+1)\le U(b)}.\tag{2}
\]

The last equivalence uses that the right-hand side and `r(c)` are integers, including `D=1`.

For `b=hQ` with `h` prime and `h` not dividing `Q`, `U(b)=U(Q)`. Therefore

\[
\boxed{1+hQ>r(hQ(1+hQ))\iff r(1+hQ)\le U(Q).}\tag{3}
\]

This criterion is exact, not an estimate or a statement about typical cases. If `U(Q)=1`, there are **no** ABC hits for primes `h` not dividing `Q`. If `U(Q)=2`, then `Q` is even, `1+hQ` is odd, and again there are no such hits (its radical is at least 3).

## 2. A deterministic exceptional-set bound, uniform for moderately growing powerful part

Let `S(x,y)={n<=x : rad(n)<=y}`. Every such `n` is supported on primes `p<=y`, and hence

\[
 \#S(x,y)\le\prod_{p\le y}\left(1+\left\lfloor\frac{\log x}{\log p}\right\rfloor\right)
 \le\left(1+\frac{\log x}{\log2}\right)^{\pi(y)}.\tag{4}
\]

By (2), the same bound counts all ABC hits `1+b=b+1<=x` with `U(b)<=y`. Thus for every fixed `0<theta<1`, using the prime number theorem in the elementary auxiliary count `pi(theta log x)~theta log x/loglog x`,

\[
\boxed{\#\{b\le x: b+1>r(b(b+1)),\ U(b)\le\theta\log x\}\le x^{\theta+o(1)}.}\tag{5}
\]

If `U(b)=o(log x)` uniformly across a family, the count is `x^{o(1)}`. The exponent is only a coarse elementary upper bound, not claimed optimal.

For fixed `Q`, let `K=U(Q)` and `kappa(K)=max{omega(d): d<=K, d squarefree}`. Every output `1+hQ` with radical at most `K` has one of finitely many prime supports of size at most `kappa(K)`. Counting exponent tuples gives the sharper estimate

\[
\boxed{\#\{h\le H:\ h\text{ prime},\ 1+hQ>r(hQ(1+hQ))\}\ll_Q(1+\log H)^{\kappa(K)}.}\tag{6}
\]

Primes `h|Q`, which do not satisfy the classification (3), are finite and absorbed into the implied constant. For `Q=243`, `K=81`, `kappa(K)=3`; `1+643*243=156250=2*5^7` is one of the exceptions.

More generally, fix `A>0`, `0<theta<1`. Uniformly for integers `1<=Q<=H^A` with `U(Q)<=theta log H`, the number of exceptional primes `h<=H` is

\[
\boxed{\le H^{\theta+o_{A,\theta}(1)}.}\tag{7}
\]

The contribution from primes `h|Q` is at most `omega(Q)<=O_A(log H)`. For the others, (3) and (4) apply with `x=1+HQ<=2H^{A+1}` and `y=theta log H`. This uniform theorem does **not** require a sieve estimate for prime progressions. It works for `Q` comparable to or considerably larger than `H`, provided its powerful part remains small.

## 3. The weighted powerful-divisor series

For `0<sigma<1` define multiplicative `b_sigma` by

\[
 b_\sigma(1)=1,\quad b_\sigma(p)=0,\quad
 b_\sigma(p^e)=p^{\sigma(e-1)}-p^{\sigma(e-2)}\quad(e\ge2).
\]

These coefficients are nonnegative, supported on powerful integers, and satisfy the exact divisor identity

\[
\boxed{U(n)^\sigma=\sum_{d\mid n}b_\sigma(d).}\tag{8}
\]

Their Dirichlet generating function is

\[
 \boxed{\mathcal D_\sigma(s):=\sum_{d\ge1}\frac{b_\sigma(d)}{d^s}
 =\prod_p\left(1+\frac{(p^\sigma-1)p^{-2s}}{1-p^{\sigma-s}}\right).}\tag{9}
\]

For real `s>(1+sigma)/2`, this Euler product converges absolutely: `s>sigma` and `2s-sigma>1`, so the local excess is `O(p^{sigma-2s})`. Positivity immediately gives, for any `s` in `((1+sigma)/2,1)`,

\[
 \sum_{d\le X}b_\sigma(d)\le\mathcal D_\sigma(s)X^s,
 \qquad
 \sum_{d>T}\frac{b_\sigma(d)}d\le \mathcal D_\sigma(s)T^{s-1}.\tag{10}
\]

Also `sum_d b_sigma(d)/phi(d)<infinity` for `sigma<1`, by `d/phi(d)<<_epsilon d^epsilon`, choosing `epsilon` so that `s+epsilon<1`. This is much sharper than bounding each coefficient by `d^sigma` and then counting powerful integers, which gave an artificial abscissa `sigma+1/2`.

## 4. Improved bounded moment for prime multipliers

**Theorem.** Fix `0<eta<1`, `0<sigma<eta/(2-eta)`. There is `C_eta,sigma` such that, uniformly for all sufficiently large `H` and integers `1<=Q<=H^(1-eta)`, 

\[
\boxed{\frac1{\pi(H)}\sum_{h\le H\atop h\text{ prime}}U(1+hQ)^\sigma\le C_{\eta,\sigma}.}\tag{11}
\]

**Proof.** By (8),

\[
 \sum_{h\le H\atop h\text{ prime}}U(1+hQ)^\sigma
 =\sum_{\substack{d\le1+HQ\\(d,Q)=1}}b_\sigma(d)\pi(H;d,-Q^{-1}).
\]

Choose `s` with `(1+sigma)/2<s<1/(2-eta)<1`; such `s` exists exactly under the asserted inequality for `sigma`. For `d<=H^(1/2)`, Brun–Titchmarsh and `pi(H)>>H/log H` imply the normalized contribution is at most `C sum_d b_sigma(d)/phi(d)<infinity`. For `d>H^(1/2)` use the elementary class bound `pi(H;d,a)<=H/d+1`; after dividing by `pi(H)`, (10) bounds this tail by

\[
 O_{\eta,\sigma}\!\left((\log H)\left[H^{(s-1)/2}+\frac{(1+HQ)^s}{H}\right]\right)=o(1),
\]

because `(2-eta)s<1`. QED.

This improves the previous exponent restriction `sigma<eta/[2(2-eta)]` to

\[
\boxed{\sigma<\frac{\eta}{2-\eta}},
\]

as a theorem of the same method, without any extra Diophantine assumption. For `eta=1/2`, any `sigma<1/3` is admissible (previously `<1/6`).

**Corollary (simultaneous sparse-input nonhits).** Fix a finite prime alphabet `S`. Among primes `h in(H/2,H]`, all but

\[
 O_{S,\eta,\sigma}\bigl(H^{1-\sigma}(\log H)^{|S|-1}\bigr)
\]

satisfy `1+hQ<=rad(hQ(1+hQ))` for every `S`-unit `Q<=H^(1-eta)`. Indeed, a hit has `U(1+hQ)>rad(hQ)>=h>H/2`. Apply Markov and the number `O_S((log H)^{|S|})` of candidate `Q`. In the concrete case `eta=1/2`, `sigma=1/4`, this gives `O_S(H^(3/4)(log H)^{|S|-1})` exceptions, while taking `sigma` near `1/3` approaches `H^(2/3+epsilon)`.

## 5. Uniform Euler-product expectation and squarefree law

The bounded moment has an explicit limiting constant. Put

\[
\boxed{\mathcal C_\sigma(Q)=\prod_{p\nmid Q}
\left(1+\frac{p^\sigma-1}{p(p-1)(1-p^{\sigma-1})}\right).}\tag{12}
\]

**Theorem.** For fixed `0<eta<1`, `0<sigma<eta/(2-eta)`,

\[
\boxed{\sup_{Q\le H^{1-\eta}}
\left|\frac1{\pi(H)}\sum_{h\le H\atop h\text{ prime}}U(1+hQ)^\sigma-\mathcal C_\sigma(Q)\right|\to0.}\tag{13}
\]

**Proof sketch with all boundary estimates.** Use the exact divisor series. For `d<=T=(log H)^B`, the Siegel–Walfisz theorem gives `pi(H;d,a)/pi(H)=1/phi(d)+O_A((log H)^(-A))`, uniformly in the reduced class and `d`, for any fixed `A,B` after an appropriate choice of `A`. By (10), the sum of coefficients over `d<=T` is `O(T^s)` and so the total small-modulus error tends to zero. On `T<d<=sqrt H`, Brun–Titchmarsh bounds the contribution by `C sum_{d>T} b_sigma(d)/phi(d)=o(1)`. On `sqrt H<d<=1+HQ`, use exactly the power-saving tail in Theorem (11). The limiting arithmetic sum `sum_{(d,Q)=1}b_sigma(d)/phi(d)` factorizes as (12), since

\[
\sum_{e\ge2}\frac{b_\sigma(p^e)}{\phi(p^e)}=
\frac{p^\sigma-1}{p(p-1)(1-p^{\sigma-1})}.
\]

The tails are uniform in `Q`, because omitting local Euler factors cannot increase the positive error bounds. QED. The same argument allows arbitrary fixed logarithmic-power error after adjusting `A,B`, but constants from Siegel–Walfisz may be ineffective.

**Squarefree corollary.** Uniformly over the same range of `Q`,

\[
\boxed{\frac1{\pi(H)}\#\{h\le H:\ h\text{ prime},\ 1+hQ\text{ squarefree}\}
=\mathfrak S(Q)+o(1),}
\]

where

\[
 \boxed{\mathfrak S(Q)=\prod_{p\nmid Q}\left(1-\frac1{p(p-1)}\right).}\tag{14}
\]

This follows directly from `1_{n squarefree}=sum_{d^2|n}mu(d)`, Siegel–Walfisz for `d<=(log H)^B`, Brun–Titchmarsh for `(log H)^B<d<=H^(1/4)`, and the elementary `H/d^2+1` bound for `H^(1/4)<d<=sqrt(1+HQ)`. The final normalized large-square error is `O(H^(-1/4)logH+H^(-eta/2)logH)`.

The baseline product for `Q=1` is numerically `0.3739558136...` (the same Euler product traditionally called Artin's constant); it has a different origin here and no assumption about primitive roots. For `Q=2^f`, the density is `2*0.3739558136...`; for `Q=3^f`, it is `(6/5)*0.3739558136...`.

**Interpretation.** Both the entire limiting powerful-part moment and the limiting squarefree density depend on `Q` only through its **prime support**, not the exponents of those primes. This is a population-level decoupling and does not bound an exceptional specified `h`.

## 6. A completely elementary count for general ABC hits

From (8) and (9) with `s=1` (which converges whenever `0<t<1`),

\[
\boxed{\sum_{n\le X}U(n)^t\ll_t X\qquad(0<t<1).}\tag{15}
\]

Set `gamma=delta/(1+delta)` for `delta>=0`, and consider primitive triples `a+b=c<=X` with `a<=b`. By (1), if `c>rad(abc)^(1+delta)`, then

\[
 U(b)U(a+b)>b\,r(a)\,(a+b)^\gamma.
\]

Choose `0<sigma<1/2` and restrict `B<b<=2B`, `a<=b`. Since `b>=B` and `a+b>=B`, use Markov and Cauchy–Schwarz, with (15) at exponent `2sigma`, to bound the number of eligible `b` for each fixed `a<=2B` by

\[
\frac{\sum_{B<b\le2B}U(b)^\sigma U(a+b)^\sigma}{B^{\sigma(1+\gamma)}r(a)^\sigma}
\ll_{\sigma}B^{1-\sigma(1+\gamma)}r(a)^{-\sigma}.
\]

Also `r(a)^(-sigma)=a^(-sigma)U(a)^sigma` and (15) on dyadic intervals gives `sum_{a<=2B}r(a)^(-sigma)<<_sigma B^(1-sigma)`. Therefore the total in this dyadic region is

\[
 \ll_{\sigma,\delta}B^{2-\sigma(2+\gamma)}.
\]

Sum the dyadic regions. Let `sigma` approach `1/2` from below to obtain

\[
\boxed{\#\{\text{primitive }a+b=c\le X:\ c>r(abc)^{1+\delta}\}
\ll_{\delta,\varepsilon}X^{1-\gamma/2+\varepsilon}.}\tag{16}
\]

For `delta=0`, this gives `O_epsilon(X^(1+epsilon))` for all ordinary ABC hits. For `delta>0`, it gives a power-saving bound below `X`, but it is **weaker** than the refined published exceptional-set estimate (reported as `O(X^(3/5))` in Lichtman's August 2026 article for the usual `c>rad(abc)^(1+delta)` setting). Formula (16) is included as a transparent elementary consistency check, **not** as a claim of a new state-of-the-art theorem.

## 7. Verification, limits, and the next hard block

The bundled standard-library Python program checks (8) for 10,000 integers both at exponent `sigma=1` with exact integer arithmetic and at `sigma=1/4` numerically; it checks classification (3) for 51,320 prime-multiplier pairs. It counts all unordered primitive triples `c<=10,000`, recovering 121 ABC hits and 22 triples with `c^5>R^6`. It also compares prime-multiplier sample moments and squarefree densities to the Euler products (truncated at prime 299,993). No finite computation is used to prove the asymptotic results.

The two developments should not be conflated: (i) the radical-ceiling classification is exact and applies pointwise; (ii) the Euler distribution and fractional moments are statistical and do not control an arbitrarily selected exceptional prime multiplier. **ABC is still open.** The next genuinely hard step is a uniform constraint on the extremely sparse simultaneous prime-exponent realizations which fall outside these distributional bounds. In other words, strong global arithmetic height, not another local valuation identity, is required.

## Sources (external ingredients; historical priority not claimed)

- Montgomery–Vaughan / Brun–Titchmarsh inequality: https://www.math.tau.ac.il/~rudnick/courses/sieves2015/BrunTitchmarsh.pdf
- Siegel–Walfisz uniform PNT in arithmetic progressions: https://kskedlaya.org/ant/chapter-11.html
- Artin's constant Euler product: https://mathworld.wolfram.com/ArtinsConstant.html
- J. D. Lichtman, *The abc Conjecture is True Almost Always*, 2026: https://www.tandfonline.com/doi/full/10.1080/00029890.2026.2702867
- Bernert, Browning, Lichtman, Teräväinen, *Bounds on the exceptional set in the abc conjecture*: https://arxiv.org/abs/2410.12234
