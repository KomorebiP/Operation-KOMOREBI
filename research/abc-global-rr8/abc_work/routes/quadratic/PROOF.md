# Full-radical counting and the remaining height obstruction

Base checkpoint: the archive `ABC_Square_Kernel_Reverse_Realization_2026-10-25.zip`, SHA-256 `f9e5f22f454acf335f7267e6b69d0ee7c06394bf8744c3c3652fb9dec8ac9b59`.

All statements below concern positive integers. Write `r(n)=rad(n)` and `U(n)=n/r(n)`, including `r(1)=U(1)=1`. These are elementary proofs, not a Lean certificate. No originality claim is made.

## 1. A full-radical bound

For every real delta>0 define

\[
C_\delta=\prod_p\left(1+\frac1{p(p^\delta-1)}\right).
\]

This product converges. For sufficiently large p, `p^delta-1 >= p^delta/2`, so its local excess is at most `2p^(-1-delta)` and the sum converges even when summed over all integers instead of primes.

For X,T>=1,

\[
\boxed{\#\{n\le X:r(n)\le T\}\le C_\delta T X^\delta.}\tag{A}
\]

Indeed, if `n<=X` and `r(n)<=T`, then `1 <= T X^delta/[r(n)n^delta]`. Sum this inequality over the indicated integers and then over all positive integers. The resulting positive series factors absolutely as

\[
\sum_{n\ge1}\frac1{r(n)n^\delta}
=\prod_p\left(1+\sum_{e\ge1}\frac1{p^{1+e\delta}}\right)=C_\delta.
\]

This counts the complete radical, including primes appearing only in the square factor `u` of `n=m u^2`. The square-kernel proof had discarded that information. Formula (A) has no congruence saving and should be combined with, rather than confused with, the existing quadratic-root bound.

## 2. Application to the prior restricted ABC family

Let h be squarefree, `(h,Q)=1`, and `c=1+hQ`. Let H>=2, `H/2<h<=H`, epsilon>0, and `gamma=epsilon/(1+epsilon)`. An exception means

\[
c>R^{1+\epsilon},\qquad R=h\,r(Q)r(c).
\]

The preceding checkpoint proves the necessary radical ceiling

\[
r(c)<T_\epsilon=\frac{2(1+HQ)^{1/(1+\epsilon)}}{H r(Q)}.
\]

Apply (A) with `X=1+HQ`. For any delta>0 the number of exceptional h at this Q is at most

\[
\boxed{2C_\delta\frac{(1+HQ)^{1/(1+\epsilon)+\delta}}{H r(Q)}.}\tag{B}
\]

Fix a finite nonempty prime alphabet S and A>epsilon. Summing over S-smooth `Q<=H^A`, or simply using their number `O_S((log H)^|S|)`, yields, for every eta>0,

\[
\boxed{\#\{(h,Q)\text{ exceptional}:Q\le H^A,\ Q\text{ S-smooth}\}
\ll_{S,A,\epsilon,\eta}
H^{(A-\epsilon)/(1+\epsilon)+\eta}(\log H)^{|S|}.}\tag{C}
\]

Choose `delta=eta/(1+A)` in (B), and use `1+HQ<=2H^(1+A)`. This removes the separate `H^[1/(2(1+epsilon))]` term in the previous square-kernel estimate. The bound counts pairs and therefore also bounds the number of distinct exceptional multipliers.

There is a simple improvement at the lower endpoint. If `Q<=H^epsilon`, then no exceptions exist in this dyadic interval. Indeed `Q<(2h)^epsilon`, `r(c)>=2`, and `R>=2h`. Consequently

\[
c=1+hQ<1+h(2h)^\epsilon\le2h(2h)^\epsilon\le R^{1+\epsilon}.
\]

The middle inequality uses `h(2h)^epsilon>=1`. This endpoint observation does not require S to be fixed.

## 3. Optional sharper logarithmic and explicit exponent refinement

The previous checkpoint already proves the following elementary moment estimate. For `0<t<1`, put

\[
D_t=\prod_p\left(1+\frac{(p^t-1)p^{-2}}{1-p^{t-1}}\right)<\infty.
\]

Then

\[
\sum_{n\le X}U(n)^t\le D_t X.\tag{D}
\]

For completeness, define the nonnegative multiplicative coefficients by `b_t(1)=1`, `b_t(p)=0`, and `b_t(p^e)=p^[t(e-1)]-p^[t(e-2)]` for e>=2. Telescoping proves `U(n)^t=sum_(d|n)b_t(d)`. Thus the sum in (D) is at most `X sum_d b_t(d)/d =D_tX`. The Euler factors converge since their excess is `O_t(p^(t-2))` for large p.

The exception inequality is exactly

\[
U(c)>h r(Q)c^\gamma.
\]

Since `h>H/2` and `c>HQ/2`, an exceptional output satisfies

\[
U(c)>(H/2)r(Q)(HQ/2)^\gamma.
\]

The map `h -> c` is injective. Apply (D) to every integer `c<=1+HQ<=2HQ` to obtain

\[
\boxed{\#\{h\text{ exceptional at }Q\}
\le2^{1+t(1+\gamma)}D_t
H^{1-t(1+\gamma)}\frac{Q^{1-\gamma t}}{r(Q)^t}.}\tag{E}
\]

For fixed nonempty S and b>0,

\[
\sum_{Q\le Y\atop Q\text{ S-smooth}}Q^b
\ll_{S,b}Y^b(1+\log Y)^{|S|-1}.\tag{F}
\]

To prove (F), choose one prime `p_1 in S`. Fix the exponents of the remaining primes, whose product is L<=Y. The sum over `p_1^e<=Y/L` is geometric and at most `p_1^b/(p_1^b-1) Y^b`. There are `O_S((1+log Y)^(|S|-1))` choices of the other exponents. This proves (F), including the single-prime case.

Discarding `r(Q)^(-t)<=1` and applying (F) with `b=1-gamma t>0` proves

\[
\#\{(h,Q)\text{ exceptional}:Q\le H^A,Q\text{ S-smooth}\}
\ll_{S,A,\epsilon,t}
H^{1+A-t[1+\gamma(1+A)]}(1+\log H)^{|S|-1}.\tag{G}
\]

The limiting exponent as t approaches 1 is `(A-epsilon)/(1+epsilon)`. For example `epsilon=1/10`, `A=1/2`, `t=99/100` gives precisely

\[
\boxed{O_S\bigl(H^{3/8}(1+\log H)^{|S|-1}\bigr).}\tag{H}
\]

This is a valid refinement of the former `H^(5/11)` term in that regime. Constants may be large as t approaches 1. Neither (A) nor the refinements claim a best known estimate.

## 4. Higher perfect powers

Let k>=2, let h be prime, `(h,Q)=1`, and suppose `1+hQ=u^k` with u>=2. Then

\[
\boxed{h\le\frac{(Q+1)^k-1}{Q}.}\tag{I}
\]

Write `A=u-1` and `B=1+u+...+u^(k-1)`, so `AB=hQ` and `gcd(A,B)|k`. If h divides both factors, then h divides k, hence `h<=k<=((Q+1)^k-1)/Q`. If h divides exactly one factor, the other divides Q and is at most Q. If `A<=Q`, then `u<=Q+1`, proving (I). If `B<=Q`, then `u-1<=B<=Q`, giving the same conclusion. This includes k=2 and recovers the old `h<=Q+2` bound.

The result excludes the split perfect-power branch beyond a Q-dependent cutoff. General `c=m u^k` retains an unrestricted coefficient m. For k>2, the unique kth-powerfree m can be as large as `r(c)^(k-1)`, so merely replacing squares by kth powers worsens the discarded-coefficient budget. It cannot establish the ABC inequality on its own.

## 5. Exact proof boundary

The new estimates establish sparsity, with a stronger exponent than the square-kernel bound in some regimes. They do not bound the largest exceptional h or the height of the last exception. For example a bound `O(H^beta)` with beta>0 remains compatible with an infinite sparse sequence.

The arithmetic obstruction that survives is the height of simultaneous solutions `m u^2-1=hQ` with the complete radical `r(mu)` small, while Q and its prime alphabet are allowed to vary. No uniform pointwise height bound is proved. The unrestricted ABC conjecture is not solved, and the prime-multiplier restriction does not cover all primitive triples.

Continuation: exploit both the congruence `m u^2=1 mod Q` and the full radical restriction in an estimate that forces eventual emptiness, rather than another sublinear counting bound. The estimates above alone cannot supply that step.
