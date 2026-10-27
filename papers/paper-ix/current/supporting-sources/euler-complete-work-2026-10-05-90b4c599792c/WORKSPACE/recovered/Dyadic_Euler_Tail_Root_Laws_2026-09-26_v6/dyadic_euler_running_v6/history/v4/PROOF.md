# Exact cancellation laws for binary-edge dyadic Euler tails

Research continuation, 26 September 2026.

**Status.** The results below have an explicit mathematical proof and an executed exact-arithmetic audit. They have not been compiled in Lean in this run. No historical-priority claim is made. The existing optimal uniform truncation theorem is an input, not a new result of this continuation.

## 1. Definitions and existing identities

Use signed Euler numbers, with E_0=1, E_2=-1, E_4=5, and

\[
\operatorname{sech}t=\sum_{n\ge0}E_n t^n/n!.
\]

Index a row by N, so its target is E_(2N). Set

\[
A(N)=\frac{3^{2N+2}-1}{4(2N+1)(2N+2)},\qquad
\left(\frac z{\sinh z}\right)^2=\sum_{m\ge0}\beta_mz^{2m},
\]

\[
\kappa_m=2^{2m}(2m)!\beta_m,\qquad \kappa_0=1.
\]

The existing reconstruction is

\[
E_{2N}=\sum_{m=0}^N\kappa_m\binom{2N}{2m}A(N-m).
\]

For m>=1,

\[
\beta_m=-\frac{2^{2m}(2m-1)B_{2m}}{(2m)!},\quad
v_2(\beta_m)=s_2(m)-1,\quad v_2(\kappa_m)=4m-1.
\]

Here s_2 is binary digit sum. The Bernoulli valuation follows from von Staudt--Clausen; the factorial identity is Legendre's formula. Every nonnegative integral A(N) is a dyadic unit. Consequently the exact summand weight is

\[
w_m(N)=4m-1+v_2\binom{2N}{2m}=4m-1+v_2\binom Nm.
\]

The equality between these two binomial valuations does not assert equality of the binomial coefficients.

Define the whole tail after depth M by

\[
\mathcal T_M(N)=E_{2N}-\sum_{m=0}^{\min(M,N)}\kappa_m\binom{2N}{2m}A(N-m).
\]

For M>=N this is zero exactly. Use v_2(0)=infinity throughout. The existing optimal uniform lower bound is 4M+3, attained at N=M+1.

## 2. The analytic source, including its removable point

Extend A to the dyadic integers by

\[
\mathscr A(x)=\frac{9^{x+1}-1}{8(x+1)(2x+1)},\qquad
\mathscr A(-1)=-\log(9)/8.
\]

Let l=log(9), so v_2(l)=3. Then

\[
\mathscr A(x)=\frac{l/8}{1+2x}
\sum_{k\ge0}\frac{l^k}{(k+1)!}(x+1)^k.
\]

The coefficient valuations 3k-v_2((k+1)!) tend to infinity. For k>=1 they are positive. Also (1+2x)^(-1)=sum_k(-2x)^k. It follows that A is a restricted power series with integral dyadic coefficients and

\[
\mathscr A\in\mathbb Z_2\langle x\rangle,\qquad
\mathscr A\equiv1\pmod2
\]

**coefficientwise**. This is stronger than just saying its integer values are odd. Integer translations preserve its integral Gauss norm.

## 3. Factor the entire omitted tail

Fix r>=1, put M=r-1, and write x=N-r. For j>=0 let

\[
P_j(x)=x^{\underline j}\prod_{i=0}^{j-1}(2x-2i-1),\qquad P_0=1.
\]

An exact factorial cancellation gives

\[
\mathcal T_{r-1}(N)=\kappa_r\binom{2N}{2r}H_r(N-r),
\]

where

\[
H_r(x)=\sum_{j\ge0}8^j\frac{\beta_{r+j}}{\beta_r}P_j(x)\mathscr A(x-j).
\]

Indeed, the ratio of the (r+j)th coefficient to the factored coefficient is

\[
4^j\frac{\beta_{r+j}}{\beta_r}(2x)^{\underline{2j}}
=8^j\frac{\beta_{r+j}}{\beta_r}P_j(x).
\]

At a nonnegative integer x all terms j>x vanish. Thus the infinite analytic expression agrees with the original finite tail. For fixed r, its polynomial coefficient valuations are bounded below by

\[
3j+s_2(r+j)-s_2(r)\ge3j+1-s_2(r),
\]

which tend to infinity. Hence it defines an element of Q_2<x>.

## 4. Binary-edge root theorem

**Theorem.** Let a>=4, r=2^a-1, and M=2^a-2. There is a unique alpha_a in Z_2 such that, on putting rho_a=r+alpha_a,

\[
\boxed{
 v_2\mathcal T_{2^a-2}(N)
 =4(2^a-1)+3-a+v_2\binom{N}{2^a-1}+v_2(N-\rho_a)
}
\]

for every integer N>=2^a-1. The convention at a zero tail is v_2(0)=infinity. In addition,

\[
v_2(\alpha_a)=a-4.
\]

**Proof.** Since s_2(r)=a, define

\[
G_a(x)=2^{a-4}H_r(x)
 =\sum_{j\ge0}\gamma_{a,j}P_j(x)\mathscr A(x-j),
\quad
\gamma_{a,j}=2^{a-4}8^j\beta_{r+j}/\beta_r.
\]

The first coefficient is gamma_(a,0)=2^(a-4). The second is a unit because r+1=2^a and

\[
v_2(\gamma_{a,1})=(a-4)+3-(a-1)=0.
\]

For every j>=2,

\[
v_2(\gamma_{a,j})=3j+s_2(r+j)-4\ge3j-3\ge3.
\]

Thus G_a belongs to Z_2<x>, and, coefficientwise,

\[
G_a(x)\equiv
\begin{cases}1+x,&a=4,\\x,&a>4\end{cases}\pmod2.
\]

Here P_1=x(2x-1), which reduces to x modulo 2. It follows directly that for distinct x,y in Z_2,

\[
\frac{G_a(x)-G_a(y)}{x-y}\in1+2\mathbb Z_2.
\]

Therefore G_a is an isometry. The coefficientwise congruence also gives one root modulo 2. At each subsequent precision exactly one of its two lifts remains a root, because shifting by 2^k changes G_a by 2^k times a unit modulo 2^(k+1). Completeness constructs a unique root alpha_a, and

\[
v_2G_a(x)=v_2(x-\alpha_a).
\]

Since G_a(0)=2^(a-4), isometry gives v_2(alpha_a)=a-4. Finally, the factorization in Section 3 and the known kappa valuation give

\[
v_2\mathcal T_{r-1}(N)
=4r-1+v_2\binom Nr+4-a+v_2(N-r-\alpha_a),
\]

which is the claimed formula. QED.

**Consequences.** The root controls the *whole* tail, not merely the first two terms. Approaching rho_a through integer residue classes gives arbitrarily large additional cancellation at one fixed truncation depth. This does not improve the uniform bound: at N=r the formula gives 4r-1=4M+3 exactly.

## 5. A second exact family: low binary digit sum

If s_2(r)<=4 and r!=15, then for every N>=r,

\[
\boxed{v_2\mathcal T_{r-1}(N)=4r-1+v_2\binom Nr.}
\]

For j>=2, the coefficient in H_r has valuation at least 3j+1-s_2(r)>=3. For j=1 its exact valuation is 4-v_2(r+1). Under the stated condition v_2(r+1)<=3: four trailing ones with no other one bits would be precisely r=15. Therefore all positive-j terms vanish coefficientwise modulo 2 and H_r is congruent to A, hence to 1. Its value is a unit. In particular this proves the first-omitted-term valuation for all depths M=0,...,13, at every admissible row, not only in a bounded scan.

## 6. Explicit M=14 example and root digits

For a=4, r=15, the root law is

\[
v_2\mathcal T_{14}(N)=59+v_2\binom N{15}+v_2(N-\rho_4).
\]

Certified residues from the implemented lift include

| q | rho_4 modulo 2^q |
|---:|---:|
|5|16|
|6|48|
|7|48|
|8|176|
|10|176|
|12|1200|
|16|9392|
|32|2083857584|
|64|4183939833681749168|

The 128-bit residue is 181803547360506310314536504063203550384, hexadecimal 88c616ef1758fccb3a10571c7c3524b0. These are compatible residues of a dyadic number, not a claim of an ordinary real limit.

At N=16 the two omitted terms are

\[
S_{15}=\kappa_{15}\binom{32}{30}A(1),\qquad S_{16}=\kappa_{16},
\quad A(1)=5/3.
\]

Both have valuation 63. Their normalized residues modulo 64 are respectively 63 and 33. Their sum is 32 modulo 64, so the tail has valuation 63+5=68. Exactly,

\[
\mathcal T_{14}(16)=-2^{68}\frac{1593243617206459}{58905}.
\]

Both the displayed numerator and denominator are odd.

## 7. The suggested two-minimum pattern is not universal

A finite scan showing at most two minimum-weight terms must not be extrapolated. Take

\[
N=2^{68},\qquad M=N-18.
\]

The omitted indices are m=N-d with 0<=d<=17. For 1<=d<=17,

\[
v_2\binom{N}{N-d}=68-v_2(d),
\]

so the weight above 4N-1 is 68-4d-v_2(d). It vanishes at d=16 and d=17 and is positive at d=1,...,15. The endpoint d=0 also has weight 4N-1. Thus there are exactly **three** minimum-weight terms, at N-17, N-16, N. Three units sum to a unit modulo two, so the full tail has exact valuation 4N-1. The audit checks all 18 weights by exact integer arithmetic. It does not compute this enormous Euler number.

## 8. Computational contract and interpretation

Run `python3 check_dyadic_tail.py`. Python's standard library is sufficient. The script uses Fraction and arbitrary-precision integers; no floating approximation enters any mathematical assertion.

Independent checks include inverse-series coefficients against a Bernoulli recurrence, full reconstruction against the Euler recurrence, source valuations, all nonempty tails with 1<=N<=512, and root-law predictions for a=4,...,8. Root values are generated from the analytic remainder, not fitted to the finite tail table. Each digit lift verifies both the chosen branch and rejection of the alternative branch.

The normalized root-series calculation omits only j for which the proved Gauss valuation 3j-3 reaches the requested precision. A second modular method uses the original, unfactored summands and omits only m with 4m-1 at least the modulus exponent. It agrees with rational tails for N=15,...,512 and separately checks three large rows modulo 2^220.

`RESULTS.json` records exact counts and outputs. `MANIFEST.json` records command, environment, duration, conventions and hashes. The manifest follows the available version-1 template; its fields and hashes are checked locally. The separate bundled skill validator was not located in the working filesystem and was not run.

The numerical tests support the implementation. The universal statements depend on the explicit proofs in Sections 4, 5, and 7. General depths not covered by those theorems are not classified here.

## Sources and provenance

The source/kernel reconstruction, exact coefficient weights, optimal 4M+3 bound, and analytic source are retained formulas from the supplied Komorebi materials, including the Local Polyphase edition and Paper IX consolidated edition. The consolidated edition's arithmetic-refinements section explicitly separates exact individual weights from the not-yet-classified whole-tail valuation. This continuation studies that distinction.

For the classical Bernoulli denominator input, see NIST DLMF 24.10.1, https://dlmf.nist.gov/24.10.E1. The hyperbolic series conventions agree with NIST DLMF 4.33, https://dlmf.nist.gov/4.33. No claim that the root-law formulation is absent from the external literature has been established.
