# ABC: Square-Kernel Reverse Realization and Quadratic Progression Barrier

**Research checkpoint: 25 October 2026.** This note gives elementary unconditional counting theorems for restricted ABC families, exact polynomial reductions, and clearly labeled remaining problems. **It does not prove the abc conjecture.** No Lean formalization and no historical priority claim are made. Computational tests are independent finite checks, not substitutes for the general proofs.

## 1. Correct normalization and radical ceiling

For `n>=1`, let `r(n)=rad(n)` and `U(n)=n/r(n)`. Fix `Q>=1`. Let `h>=1` be squarefree with `gcd(h,Q)=1`, and set `c=1+hQ`. The triple is primitive and

\[
 R=r(hQc)=h\,r(Q)\,r(c),\qquad K=U(Q)=Q/r(Q),\qquad c=h\,r(Q)K+1.
\]

Since `r(c)` is an integer, the exact hit criterion is

\[
 \boxed{c>R\iff r(c)\le K.} \tag{1}
\]

For the more demanding bound `c>R^(1+epsilon)` and `H/2<h<=H`, `epsilon>0`, we necessarily have

\[
 r(c)<T_\epsilon(H,Q):=\frac{2(1+HQ)^{1/(1+\epsilon)}}{H\,r(Q)}. \tag{2}
\]

This inequality is strict and comes from `R=h*r(Q)*r(c)` with `h>H/2`. It is **not** equivalent to abc: it is a necessary condition in the restricted family.

## 2. Quadratic root count

Each positive integer `c` has a unique decomposition

\[
 c=m u^2,\quad m\ge1\text{ squarefree},\quad u\ge1. \tag{3}
\]

Since `m|r(c)`, if `r(c)<=T` then `m<=T`. Also `c=1+hQ` yields

\[
 \boxed{m u^2\equiv1\pmod Q.} \tag{4}
\]

Put

\[
 \rho(Q)=\#\{v\bmod Q:v^2\equiv1\pmod Q\}.
\]

With `Q=1`, let `rho(Q)=1`. For prime powers, the root counts are `rho(p^e)=2` for odd `p`, and `rho(2^e)=1,2,4` for `e=1,2,>=3`, respectively. CRT thus gives

\[
 \rho(Q)\le 2^{\omega(Q)+1}. \tag{5}
\]

If `(4)` is solvable, every solution `u mod Q` is a fixed solution times one of the `rho(Q)` roots of unity, because `m` and `u` are invertible modulo `Q`. Hence at most `rho(Q)` residue classes occur. For `c<=1+HQ`, the positive `u` satisfy

\[
 u\le\sqrt{\frac{1+HQ}{m}}.
\]

Each residue class contributes at most `1+u_max/Q` such `u`. Summing over squarefree `m<=T` and using `sum_{m<=T}1/sqrt(m)<=2sqrt(T)` proves the fully elementary bound

\[
 \boxed{\#\{1\le h\le H:(h,Q)=1,\ r(1+hQ)\le T\}\le
 \rho(Q)\left(T+\frac{2\sqrt{T(1+HQ)}}Q\right).} \tag{6}
\]

This even counts **all integer multipliers** satisfying the displayed radical condition, not merely squarefree or prime multipliers. When `T<1`, there are no solutions. Note that the radical condition itself is stronger than the squarefree-kernel condition used in the proof.

**Corollary 2.1 (ABC hit count).** Squarefree multipliers that produce an `abc` hit satisfy `(1)`, so

\[
 \boxed{\#\{h\le H:\ h\text{ squarefree},\ (h,Q)=1,\ 1+hQ>r(hQ(1+hQ))\}\le
 \rho(Q)\left(K+\frac{2\sqrt{K(1+HQ)}}Q\right).} \tag{7}
\]

**Corollary 2.2 (quality-sensitive count).** For `epsilon>0` and `H/2<h<=H` with `h` squarefree and coprime to `Q`, the number of exceptions to `c<=R^(1+epsilon)` is at most

\[
 \boxed{\rho(Q)\left(T_\epsilon+\frac{2\sqrt{T_\epsilon(1+HQ)}}Q\right).} \tag{8}
\]

If `T_epsilon<1` the count is zero. No analytic prime-counting theorem enters either corollary.

## 3. Fixed-prime-alphabet and growing-Q consequences

If all primes dividing `Q` lie in a fixed finite set `S`, then `rho(Q)<=2^(|S|+1)`.

For a *single* `Q<=H^(1-eta)`, `(7)` and `K<=Q` give

\[
 \#\{\text{squarefree }h\le H:\text{abc hit}\}\ll_S H^{1-\eta}+\sqrt H. \tag{9}
\]

There are only `O_S((log H)^|S|)` choices of `S`-smooth `Q<=H^(1-eta)`. By a union bound, the number of multipliers belonging to **any** such exceptional pair `(h,Q)` obeys

\[
 \boxed{\ll_{S,\eta}(H^{1-\eta}+\sqrt H)(\log H)^{|S|}.} \tag{10}
\]

More notably, set `Q<=H^A` with fixed `A>0`. For `H>=2`, equation `(2)` implies

\[
 T_\epsilon(H,Q)\ll_\epsilon\frac{Q^{1/(1+\epsilon)}}{r(Q)H^{\epsilon/(1+\epsilon)}}.
\]

The second term of `(8)` satisfies the sharper estimate

\[
 \frac{\sqrt{T_\epsilon(1+HQ)}}Q
 \ll_\epsilon\frac{H^{1/[2(1+\epsilon)]}}{Q^{\epsilon/[2(1+\epsilon)]}\sqrt{r(Q)}}
 \le H^{1/[2(1+\epsilon)]}. \tag{11}
\]

Consequently, for fixed `S` and `A>=epsilon`, the number of squarefree multipliers `h in(H/2,H]` with `Q<=H^A` and `c>R^(1+epsilon)` is at most

\[
 \boxed{O_{S,A,\epsilon}\left[(H^{(A-\epsilon)/(1+\epsilon)}+H^{1/[2(1+\epsilon)]})(\log H)^{|S|}\right].} \tag{12}
\]

When `A<epsilon`, `(2)` yields `T_epsilon<1` uniformly for sufficiently large `H`; no such violations occur. For `epsilon<A<1+2epsilon`, the bound `(12)` is power-saving relative to `H` even if the input `Q` is larger than `H`. The result applies to all *squarefree* multipliers, so in particular to primes `h` coprime to `Q`.

These are exceptional-set results, **not** pointwise ABC for every `(h,Q)`.

## 4. Exact quadratic progression and the perfect-square branch

For fixed `Q`, squarefree `m`, and a solution `u_0` to `m*u_0^2==1 (mod Q)`, every integer `u=u_0+Qt` in that class produces an integer

\[
 h(t)=\frac{m(u_0+Qt)^2-1}{Q}
 =mQt^2+2mu_0t+\frac{mu_0^2-1}{Q}. \tag{13}
\]

**The discriminant is exactly**

\[
 \boxed{\operatorname{disc}h=4m,} \tag{14}
\]

regardless of `Q` or the chosen root. Thus for squarefree `m>1`, `h(t)` is irreducible over the rationals, whereas `m=1` gives a split quadratic.

**Perfect-square classification.** If `h` is a prime not dividing `Q` and `1+hQ=u^2`, then

\[
 \boxed{h\le Q+2.} \tag{15}
\]

Indeed, suppose `h>Q+2`. Then `u>Q+1`, so both `u-1` and `u+1` exceed `Q`. They multiply to `hQ`. Since `h>Q+2>=3`, the odd prime `h` divides exactly one of these two factors (`gcd(u-1,u+1)|2`). The other must divide `Q`, impossible because it is already larger than `Q`. This proves `(15)`.

Therefore for `h>Q+2`, every ABC hit in the prime-multiplier family is forced into an **irreducible quadratic progression** with squarefree `m>1`. This is a structural restriction, not a claim that quadratic prime values are impossible.

## 5. Why quadratic congruence is not yet the full obstruction

The squarefree kernel `m` does **not** determine `rad(c)` because

\[
 r(c)=r(m u).
\]

Thus `m<=K` is necessary but insufficient for an ABC hit. The extra radical of `u` must also be paid.

A concrete example is `Q=243`, `m=10`, and `u_0=125`. The quadratic is

\[
 \boxed{h(t)=2430t^2+2500t+643}\qquad(\operatorname{disc}=40).
\]

At `t=0`, `h=643` is prime and `c=10*125^2=156250` with `rad(c)=10<=81=U(243)`: an ABC hit. At `t=1`, `h=5573` is also prime, while `c=10*368^2=1354240` has `rad(c)=230>81`: **not** an ABC hit. The same quadratic residue class retains the squarefree kernel but the square factor acquires a new prime, changing the radical decisively.

This isolates a remaining genuinely global problem: bound the frequency and height of prime values of the irreducible quadratic polynomials `(13)` **while** `r(m u)` stays below the input powerful-part budget. Merely counting square roots modulo `Q` cannot achieve the pointwise ABC inequality.

## 6. General fixed offset

Let `a>=1`, `(a,Q)=1`, and let `h` be squarefree with `(a,hQ)=1`. Put `c=a+hQ`, `K=U(Q)`, `A_0=U(a)`. If `c>rad(a h Q c)`, then the exact normalization gives

\[
 r(c)<\frac K{r(a)}+\frac{A_0}{h r(Q)}\le K+A_0.
\]

With `T=K+A_0`, the congruence becomes `m u^2==a (mod Q)`, again having either zero or `rho(Q)` roots. Thus the number of such `h<=H` is at most

\[
 \boxed{\rho(Q)\left(T+\frac{2\sqrt{T(a+HQ)}}Q\right).} \tag{16}
\]

## 7. Verification and status

The accompanying `verify.py` uses only Python's standard library. It independently verifies the radical criteria, the root-count formula and its cosets, exact quadratic discriminants, the perfect-square bound, the quality-`1/10` case by integer powers, and a number of fixed-offset examples. The finite checks are recorded in `verification_results.json`.

**Open target:** An arithmetic estimate ruling out sufficiently many solutions to `(13)` with a simultaneously small radical `r(m u)` relative to input height. This remains the ABC-strength step; our results are valid restricted counting theorems but **do not solve abc**.
