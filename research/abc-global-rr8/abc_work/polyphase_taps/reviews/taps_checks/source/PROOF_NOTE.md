# Finite taps: constructive auxiliary integers and their exact cost

Base checkpoint: RR3, archive SHA-256 `557eeb61fcd37c984884b7123e7b599b403200244786f6fb549279d6b4b05302`.

Let A>B>=1 be coprime integers and `s_n=A^n+B^n`, n>=1. This route applies finite taps to the actual common-power sequence. It constructs a nonzero auxiliary by a two-tap Bezout calculation, proves the exact ideal of all such auxiliaries, and tracks divisibility amplification, coefficient cost, and normalization. It does not prove ABC or claim historical originality.

## 1. Translation to physical convolution taps

Write E for forward shift: `E s_n=s_(n+1)`. For `T(z)=sum_(j=0)^r t_j z^j` with integer taps,

\[
\boxed{T(E)s_n=A^nT(A)+B^nT(B).}\tag{1}
\]

For stride d,

\[
\boxed{T(E^d)s_n=A^nT(A^d)+B^nT(B^d).}\tag{2}
\]

The physical convention is `y[m]=sum_k h[k]s_(Nm-k)`. For (2), set `h[(r-j)d]=t_j`, with all other coefficients zero, and take `n=Nm-rd>=1`. Then the physical output is exactly `T(E^d)s_n`. This is reversal and relabeling of the taps, with no amplitude normalization. Decimation N itself introduces no factor 1/N. A separately normalized Fourier or averaging stage does introduce a denominator and must be accounted for as in Section 7.

## 2. A constructive nonzero auxiliary from two taps

Put `Delta_d=A^d-B^d`. Subtracting the B mode gives

\[
s_{n+d}-B^d s_n=A^n\Delta_d.\tag{3}
\]

Since `gcd(s_n,A)=1`,

\[
\boxed{G_{n,d}:=\gcd(s_n,s_{n+d})=\gcd(s_n,\Delta_d).}\tag{4}
\]

The extended Euclidean algorithm constructs integers u,v satisfying

\[
\boxed{u s_n+v s_{n+d}=G_{n,d}>0,\qquad G_{n,d}\le\Delta_d<A^d.}\tag{5}
\]

One may choose `|u|<=s_(n+d)/G_(n,d)` and `|v|<=s_n/G_(n,d)`. Thus this is a genuine nonzero divisible auxiliary, rather than an unverified modular null vector. Its coefficients can be large.

This construction can lower the archimedean height from roughly `n log A` to at most `d log A` when d is much smaller than n. It is the tap version of the order budget, not a new estimate on the unknown order or its cyclotomic degree.

For an odd prime p with `d=ord_p(A/B)` even, let `s=v_p(A^d-B^d)` and suppose `p|s_n`. Then `n=(d/2)k` with k odd. The RR2 lifting identity gives `v_p(s_n)=s+v_p(n)`. The same identity for n+d and the fact `p` does not divide d show

\[
\boxed{v_p(G_{n,d})=s.}\tag{6}
\]

Indeed, n and n+d cannot both be divisible by p, so the minimum of their valuation depths is s. The two-tap auxiliary retains the entire birth depth and removes any extra ordinary exponent lifting.

## 3. Longer taps have an exact minimum nonzero value

The stride-d sequence obeys an order-two recurrence:

\[
s_{n+(j+2)d}=(A^d+B^d)s_{n+(j+1)d}-(AB)^d s_{n+jd}.\tag{7}
\]

Consequently the ideal of all integer finite-tap outputs at this base point and stride is exactly

\[
\boxed{\left\{\sum_{j=0}^r t_j s_{n+jd}:r\ge0,t_j\in\mathbb Z\right\}
=G_{n,d}\mathbb Z.}\tag{8}
\]

Inclusion in the right-hand side follows from the recurrence and (4); the reverse inclusion follows from the Bezout taps (5). Thus the smallest possible positive reconstructed integer is exactly G_(n,d). More taps cannot produce an integer strictly between zero and that value.

This has a sharp primitive-order case. If `d=2n`, then `s_n` divides `A^(2n)-B^(2n)`, so

\[
\boxed{G_{n,2n}=s_n.}\tag{9}
\]

Every finite integer tap with stride 2n produces zero or an integer of absolute value at least s_n. In the primitive-order branch, aligning shifts with the full contact order cannot lower the height at all.

The exact annihilator

\[
(E^d-A^d)(E^d-B^d)s_n=0\tag{10}
\]

also explains why a small modular coefficient vector is not automatically a nonzero auxiliary. A tap combination can vanish identically after reconstruction.

## 4. Why the half-order shift behaves differently

Let `h=d/2` and suppose `n=hk` with k odd. Then

\[
\boxed{\gcd(s_n,s_{n+h})=
\begin{cases}2,&A,B\text{ both odd},\\1,&A,B\text{ of opposite parity}.\end{cases}}\tag{11}
\]

Proof: write `X=A^h`, `Y=B^h`. If an odd prime divided both `X^k+Y^k` and `X^(k+1)+Y^(k+1)`, the ratio x=X/Y would satisfy `x^k=x^(k+1)=-1`, forcing x=1 and then 1=-1 modulo that odd prime. This is impossible. If A and B are odd, k+1 is even and `X^(k+1)+Y^(k+1)=2 mod 8`, so the common 2-adic valuation is exactly one. Otherwise both outputs are odd.

At a prime of birth order d, the phase at the half step is negative: `A^h/B^h=-1 mod p^s`. Thus shifting by h changes the contact sum into the other phase. The half-step two-tap gcd loses every odd birth prime. Taking a full-order step preserves those primes but pays the larger period, exactly as (8) records.

One can transport to the difference phase `a_n=A^n-B^n` and mix the two phases:

\[
a_{n+h}+B^h s_n=A^n(A^h+B^h).\tag{12}
\]

This retains the birth contact in the half-order factor. It requires access to the difference phase, rather than only taps on the original sum sequence. Equivalently, the sequence `w_j=A^(n+jh)+(-1)^j B^(n+jh)` has B-mode eigenvalue `-B^h`, and `w_1+B^h w_0=A^n(A^h+B^h)`. The auxiliary is still the existing cyclotomic half-order factor, whose size must be bounded.

## 5. Vanishing moments amplify depth and height together

For r>=1, use the rth difference tap about the B mode:

\[
\boxed{(E^d-B^d)^r s_n=A^n\Delta_d^r.}\tag{13}
\]

Its coefficients are `binom(r,j)(-B^d)^(r-j)`, at forward shifts jd. Their l1 norm is `(1+B^d)^r`; the largest index shift is rd. At an odd birth prime,

\[
v_p((E^d-B^d)^r s_n)=rs.\tag{14}
\]

After removing the known unit factor A^n, the auxiliary is the nonzero integer `Delta_d^r`. Divisibility gives only

\[
rs\log p\le r\log\Delta_d<rd\log A.\tag{15}
\]

The factor r cancels. Vanishing moments increase prime-power depth but do not improve its ratio to the degree-height budget.

For B=1 these are ordinary binomial difference taps `(E^d-1)^r`, with l1 norm 2^r. This particularly small coefficient norm does not remove the index-height cost rd. For general B, applying ordinary differences to the normalized sequence `(A/B)^n+1` requires clearing the denominator `B^(n+rd)`, recovering (13).

## 6. General short taps: an exact preservation criterion

Let p be an odd prime with `p^s|s_n`, and `p` not dividing AB. Formula (1) gives

\[
T(E)s_n\equiv B^n[T(B)-T(A)]\pmod {p^s}.\tag{16}
\]

Thus the tap preserves that birth depth if and only if

\[
\boxed{T(A)\equiv T(B)\pmod {p^s}.}\tag{17}
\]

For distinct exceptional output primes define `P=prod_p p^(s_p)`. To preserve every listed birth depth, the exact condition is `P|T(A)-T(B)`. For degree r>=1 and tap norm `L=sum_j|t_j|`, there are two cases.

If `T(A)!=T(B)`, the nonzero auxiliary `T(A)-T(B)` gives the genuine bound

\[
\boxed{P\le|T(A)-T(B)|\le L(A^r+B^r).}\tag{18}
\]

This is a sufficient arithmetic certificate if a low-cost preserving tap is constructed. It does not prove that such a tap exists.

If `T(A)=T(B)=C`, then `T(z)=C+(z-A)(z-B)Q(z)` with `Q in Z[z]`, and the reconstructed output is exactly

\[
\boxed{T(E)s_n=C s_n.}\tag{19}
\]

It either vanishes or retains the full original height. The factorization follows by monic polynomial division after subtracting the integer C.

There is also an exact minimum for the nonzero difference in (18). Every `T(A)-T(B)` is divisible by A-B, and every multiple of A-B occurs by taking a linear tap. Since every listed birth prime has even order at least two, it does not divide A-B. Therefore `gcd(P,A-B)=1`, and

\[
\boxed{\min\{|T(A)-T(B)|>0:P\mid T(A)-T(B)\}=P(A-B).}\tag{20}
\]

The minimum is attained by `T(z)=Pz`. More tap coefficients can redistribute this cost between degree and coefficient size, but cannot erase it. A pigeonhole argument in coefficient space must exclude the exact kernel `T(A)=T(B)` before claiming a useful nonzero auxiliary.

The statement is constructive in two directions: Bezout supplies the smallest positive reconstructed stride auxiliary (5), and linear taps supply the smallest possible positive preserving difference (20). Neither supplies the missing ABC-strength upper bound for the primitive birth mass.

## 7. Rational normalization

If physical or Fourier taps have a common positive integer denominator D, write `y=Y/D` with Y an integer finite-tap output. Then

\[
v_p(y)=v_p(Y)-v_p(D).\tag{21}
\]

A size-divisibility argument must be applied to the reconstructed nonzero numerator Y and its actual divisibility. A factor 1/N from an averaged root-of-unity projector loses `v_p(N)` valuation when p divides N. It is not present in plain decimation. In particular, reducing the real height by a denominator does not preserve the previous integral-divisibility assertion without this correction.

## 8. Result and limitation

Finite taps do produce a smaller nonzero auxiliary when the contact order is small relative to n. The exact best unrestricted integer output is `gcd(s_n,A^d-B^d)`. The primitive stride `d=2n` has best positive output s_n itself. Half-order shifts access a different phase and lose the original odd contact unless the corresponding difference sequence is transported as in (12).

The positive continuation is precise: construct a preserving tap with `T(A)!=T(B)` and `r log A+log L=o(n log A)`, uniformly across the required exceptional primes, or an auxiliary outside this two-exponential linear span with a separately proved nonzero value. Existing tap orthogonality and moment amplification do not prove that construction. ABC remains unresolved.
