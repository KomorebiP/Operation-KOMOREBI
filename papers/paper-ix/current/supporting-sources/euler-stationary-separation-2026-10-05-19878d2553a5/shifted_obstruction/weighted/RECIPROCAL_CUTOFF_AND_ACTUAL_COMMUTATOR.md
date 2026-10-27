# Reciprocal cutoff and actual derivative commutator

Base: `Euler-arithmetic-nonvanishing-20261005`. The base sources are unchanged.
This attempt concerns the actual admitted integers

\[
r=(17659+2^{18}T)2^{640}-161,\qquad T\geq0,
\]

with true final minimizing packet 161 and normalization \(\mu=-154\).
It targets actual nonvanishing; no additional parameter digits are sought.

## Outcome

The weighted and Riccati equations combine into a reciprocal kernel identity,
with an explicit finite cutoff remainder. Every coefficient of that remainder
continues to participate in the cancellation. The exact derivative commutator
then has a uniform, genuinely arithmetic evaluation on the terminal chart:

**At every stationary point \(x=10202+2^{15}Z\) of the actual residual,
\(v_2((T_gG_r)'(x))=158\).**

The two terms in the derivative commutator each have valuation 156; their sum
has valuation 158. Thus treating either term as uniquely dominant is false.
The transformed function has a nonzero derivative even at a hypothetical
double zero of the original function. None of the exact kernel equations
implies that this transformed derivative must vanish there. The missing
implication is stated explicitly at the end.

## 1. Exact reciprocal tail, with the whole cutoff remainder

Use \(t=z^2\),

\[
g(t)=z\coth z=\sum a_nt^n,\quad
f(t)=(z/\sinh z)^2=\sum\beta_nt^n,
\quad \beta_n=(1-2n)a_n.
\]

The previously established equations are

\[
g(t)g(4t)=f(t)+2t,\qquad f(t)=g(t)^2-t.
\]

Consequently

\[
k(t):=g(4t)-g(t)=z\tanh z,\qquad g(t)k(t)=t.       \tag{1}
\]

For an ordinary integer \(r\geq2\), set

\[
p=p_r=\sum_{n<r}a_nt^n,\quad
R=R_r=\sum_{q\geq0}a_{r+q}t^q,\quad
K_r=4^rR(4t)-R(t).
\]

Thus \(g=p+t^rR\) and \(k=p(4t)-p+t^rK_r\). Let

\[
D_r=t^{-r}\{p(t)[p(4t)-p(t)]-t\}.                         \tag{2}
\]

This is the sum \(C_r+F_r\) of the weighted and Riccati cutoff polynomials
from `arithmetic_nonvanishing/unit_identity/WEIGHTED_KERNEL_ATTEMPT.md`.
It is a polynomial of degree at most \(r-2\). The exact tail of (1) is

\[
Rk+pK_r+D_r=0,                                           \tag{3}
\]

or equivalently

\[
R(p-k)-4^rpR(4t)=D_r.                                    \tag{4}
\]

For every \(0\leq q\leq r-2\), the retained finite coefficient is

\[
[t^q]D_r=\sum_{i=q+1}^{r-1}
 (4^{r+q-i}-1)a_i a_{r+q-i}.                              \tag{5}
\]

In particular,

\[
D_r(0)=-(4^r-1)a_r.
\]

This cancels \(p(0)K_r(0)=(4^r-1)a_r\) in (3), while \(k(0)=0\).
At higher coefficients the exact statement is

\[
[t^q]D_r=-[t^q](Rk+pK_r),                                \tag{6}
\]

including every cross-boundary term. Combining the two original equations
has therefore not produced an independent nonzero remainder. It has produced
the reciprocal identity and its exact cutoff.

## 2. Keep the Newton operator and its commutator

Write

\[
P_q(x)=\prod_{i=0}^{q-1}(x-i)(2x-2i-1),\qquad
(T_a h)(x)=\sum_{q\geq0}8^qa_qP_q(x)h(x-q).
\]

The factorization \(P_i(x)P_j(x-i)=P_{i+j}(x)\) proves
\(T_aT_b=T_{ab}\) for integral coefficient kernels. If
\(Lh=8P_1(x)h(x-1)\), then \(T_g=g(L)\), and (1) gives

\[
T_gT_k=L.                                                \tag{7}
\]

This is an operator product, not multiplication of values. In particular,
translation of (3) at the Euler source \(A\) gives the exact identity

\[
T_RT_kA+T_pT_{K_r}A+T_{D_r}A=0.                          \tag{8}
\]

Ordinary differentiation \(D_x=d/dx\) obeys

\[
(T_gh)'=T_gh'+[D_x,T_g]h,\qquad
[D_x,T_g]h=\sum_{q\geq1}8^qa_qP_q'(x)h(x-q).              \tag{9}
\]

For comparison, on a domain where the source-eliminated half-shifts converge,
let \(Nh=x[h(x)-h(x-1/2)]\). Direct calculation gives

\[
[N,L]=L,\qquad
2[N,T_g]=T_g-T_g^2+L.                                    \tag{10}
\]

Equation (10) follows from \(2tg'=g-g^2+t\) and retains the half-shifted
values. It does not identify \(N\) with \(D_x\). Any exponential source term
shifted by \(1/2\) uses \(\exp(\log9/2)=-3\).

The proposed elimination at both value and argument derivative can be written
exactly. Put \(\mathcal J_xh=(h(x),h'(x))\), and let
\(B_r=\sum_{q\geq0}\beta_{r+q}t^q\). The unweighted and weighted equations are

\[
B_r=(g+p)R-F_r
    =Rg(4t)+4^rpR(4t)+C_r.
\]

At a hypothetical \(\mathcal J_xG=0\), also \(\mathcal J_xT_{B_r}A=0\),
since these functions differ by a nonzero scalar. Hence

\[
\begin{aligned}
\mathcal J_xT_{F_r}A&=\mathcal J_xT_{(g+p)R}A,\\
\mathcal J_xT_{C_r}A&=-\mathcal J_xT_{Rg(4t)+4^rpR(4t)}A.
\end{aligned}
\]

Adding eliminates the two original finite forcing terms into \(D_r=C_r+F_r\):

\[
\mathcal J_xT_{D_r}A
 =\mathcal J_xT_{R(p-k)-4^rpR(4t)}A.                       \tag{10a}
\]

But (10a) is exactly the jet of the unconditional kernel identity (4).
Thus this specified elimination loses the hypothetical-zero assumptions and
becomes an identity at every point. It cannot supply a nonzero Wronskian
forcing term at the next packet. The argument retains the complete Newton
operator at both orders.

## 3. Uniform actual derivative theorem

Let

\[
G=G_r=\sum_{q\geq0}\gamma_qP_q(x)A(x-q),\qquad
A(x)=\frac{9^{x+1}-1}{8(x+1)(2x+1)}.
\]

The actual normalized coefficients satisfy

\[
\gamma_0=2^{154},\quad v_2(\gamma_1)=153,
\quad \gamma_1/2^{153}\equiv43\pmod{64},\quad
v_2(\gamma_2)=157,
\]

and \(v_2(\gamma_q)\geq149+3q\) for \(3\leq q<161\).
For \(q=161+t\), \(1\leq t<2^{640}\), the exact digit formula gives
\(v_2(\gamma_q)=3t+s_2(t)\geq4\). All normalized packets are integral
because 161 is a true minimizer. These are actual Bernoulli coefficients;
the congruence for \(\gamma_1\) is the exact low-unit calculation in
`coupled/critical_dynamics/COUPLED_CANCELLATION_DYNAMICS.md`.

We also need the following explicit actual unit:

\[
\gamma_{161}\equiv7\pmod8.                               \tag{11}
\]

Here is a direct derivation. Put \(M=(17659+2^{18}T)2^{640}=r+161\).
The Bernoulli midpoint formula modulo 8 yields

\[
2B_n\equiv1-n+\frac23\binom n2\pmod8
\]

for the even indices \(n=2r,2M\): all terms indexed at least 4 have
valuation at least 3, and the odd terms after 1 vanish. Since
\(2r\equiv6\pmod8\) and \(2M\equiv0\pmod8\), this gives
\(2B_{2r}\equiv5\) and \(2B_{2M}\equiv1\pmod8\).
The odd part of the denominator product from \(2r+1\) through \(2M\) is

\[
-(17659+2^{18}T)\operatorname{odd}(321!)\equiv-3\cdot5
\equiv1\pmod8.
\]

Finally \((2M-1)/(2r-1)\equiv3\pmod8\). The exact Bernoulli ratio defining
\(\gamma_{161}\) now gives \(3\cdot5\cdot1=7\pmod8\).

For every \(u\in\mathbf Z_2\),

\[
v_2(G(u))\geq153,\qquad v_2(G'(u))\geq151.                \tag{12}
\]

Indeed \(P_q(u)\) has valuation at least \(v_2(q!)\), while

\[
v_2(P_q'(u))\geq v_2(q!)-\lfloor\log_2q\rfloor.
\]

For the derivative estimate, differentiate
\((1+z)^u\):
\((d/du)\binom uq=\sum_{i=1}^q(-1)^{i-1}\binom u{q-i}/i\).
Multiply by \(q!\), then by the integral odd-factor polynomial in \(P_q\).
For \(q\geq161\), the two lower bounds are at least158 and151,
respectively; the latter is nondecreasing. The lower packets give (12).

Fix \(x=10202+2^{15}Z\), and set \(y=x-1=89+128a\), where
\(a=79+256Z\) is odd. The exact low shifted jets are

\[
G(y)/2^{153}\equiv1\pmod8,
\qquad G'(y)/2^{152}\equiv3\pmod8.                       \tag{13}
\]

For the first congruence, only packets 0 and 1 contribute modulo \(2^{156}\).
Since \(y\equiv1\pmod8\), \(A(y)\equiv3\pmod4\),
\(A(y-1)\equiv1\pmod8\), and \(P_1(y)\equiv1\pmod8\), their normalized
sum is \(2\cdot3+3\cdot1=1\pmod8\). The source congruences follow from
\(A(0)=1\), \(A(1)=5/3\), and integral source coefficients.

For the second congruence, the lower-packet contribution modulo \(2^{155}\)
is just packet 1. We have \(P_1'(y)\equiv3\pmod4\) and
\(A'(y-1)\equiv A'(0)\equiv2\pmod4\). The latter follows from
\(A'(0)=9\log9/8-3\). Thus packet 1 contributes
\(2\cdot3(3+2)\equiv6\pmod8\).

In packet 161, \(v_2(P_{161}(y))=159\) and

\[
P_{161}'(y)/2^{152}\equiv3\pmod8.                         \tag{14}
\]

To check (14) without sampling, remove the unique factor \(y-89\) from
the falling product. At \(y=89\), the remaining falling product divided
by \(2^{152}\) is
\(-\operatorname{odd}(89!)\operatorname{odd}(71!)\equiv-1\pmod8\).
Moving to \(89+128a\) multiplies this unit by 5 modulo 8: the paired
differences \(\pm64\) contribute \(1-4a^2\equiv5\), the other pairs
contribute 1, and the unpaired differences 72 through 89 also contribute 1.
The logarithmic derivative correction from the removed factor is 1 modulo 8:
the \(\pm64\) pair contributes \(8a^2/(4a^2-1)\), the \(\pm32\) pair
contributes a multiple of 32, and all others a multiple of 8.
The product of the odd factors \(2y-2i-1\) is 1 modulo 8; its derivative
contribution contains the removed factor and vanishes modulo 8 after
normalization. This proves (14).

As \(A(y-161)\equiv1\pmod8\), packet 161 contributes
\(7\cdot3=5\pmod8\), using (11). Every upper packet after 161 has
derivative valuation at least 156: for \(161<q<161+2^{640}\), combine
the scalar bound 4 with the factorial derivative bound 152; later factorial
bounds alone are more than sufficient. Packets2 through160 also vanish
modulo \(2^{155}\). Thus the total is \(6+5=3\pmod8\), proving (13).

At the second shift, \(x-2\equiv88\pmod{128}\), we need only

\[
v_2(G(x-2))=154,\qquad v_2(G'(x-2))\geq153.               \tag{15}
\]

Packet0 uniquely gives the value: packet 1 has valuation 156 because
\(v_2(x-2)=3\). In the derivative, packet 1 has valuation at least 153;
packet 161 has valuation 155 because
\(v_2(88!)+v_2(72!)=85+70=155\); the other packets have larger bounds.

Now suppose \(G'(x)=0\). In (9), the \(q=0\) derivative term vanishes.
Because \(a_1=1/3\), its \(q=1\) combined term is

\[
\frac83\{P_1'(x)G(x-1)+P_1(x)G'(x-1)\}.                 \tag{16}
\]

Here \(P_1'(x)\equiv7\pmod8\) and \(P_1(x)/2\equiv7\pmod8\).
Dividing the braces by \(2^{153}\), (13) gives

\[
7\cdot1+7\cdot3\equiv4\pmod8.
\]

Therefore (16) has exact valuation 158. The \(q=2\) terms have valuation
at least 160 by (15), \(v_2(P_2(x))=1\), and integrality of \(P_2'\).
For \(q\geq3\), (12) gives derivative-term valuation at least
\(151+3q\geq160\) and commutator-term valuation at least
\(153+3q\geq162\). Hence no later packet can cancel (16), and

\[
\boxed{v_2((T_gG)'(x))=158.}                              \tag{17}
\]

The individual \(q=1\) terms in (16) have valuation 156, so the same bounds
also prove

\[
v_2((T_gG')(x))=v_2(([D_x,T_g]G)(x))=156.                 \tag{18}
\]

This theorem holds for the actual family uniformly, not just for the two
examples below. It is compatible with \(G(x)=0\), because (17) concerns
the transformed function.

## 4. Bounded actual discriminator and provenance

`check_shifted_commutator.py` separately rebuilds actual Euler packets at the
two previously fixed parameters \(T=0\) and
\(T=22831001499602523078606181325\). It uses 210 global bits, independently
solves the stationary equation through 31 local bits, and evaluates every
operator packet \(0\leq q\leq9\) at 180 output bits. The omitted derivative
and commutator tails have respective valuation bounds 181 and 183 by (12).
No parameter search occurs.

The 31-bit stationary lift changes the physical argument by a multiple of
\(2^{46}\). The two rebuilt Euler packet maxima are 233 and 250, both below 256.
For these finite packets, the binomial addition identity and its derivative
give value and derivative changes of valuation at least \(151+46=197\) and
\(144+46=190\), respectively. For the second bound, use
\(v_2(q!)-2\lfloor\log_2q\rfloor\geq144\) for \(161\leq q<256\);
the lower packets give stronger bounds. Omitted global packets are zero
coefficientwise modulo \(2^{210}\), including after ordinary differentiation.
Consequently the stored shifted jets through 180 bits are the jets at the
actual stationary point, not merely at an insufficiently accurate center.

Both cases give the following exact valuations and normalized units:

| Quantity | Valuation | Odd part modulo 65536 |
|---|---:|---:|
| \(T_gG'\) | 156 | 53791 |
| \([D_x,T_g]G\) | 156 | 53277 |
| \((T_gG)'\) | 158 | 26767 |

The complete output, pinned input hashes, runtime bounds, and successful
manifest validation are in `certified_run/`. The low congruences (13) are
also present in the stored packet records. This numerical evidence checks
the actual-coefficient interpretation of the proof; it is not its universal
quantifier.

## Exact remaining implication

For a fixed actual \(r\), the target remains

\[
\Phi_r(2^{2r-25})\ne0.
\]

The reciprocal identity (8) holds together with its argument derivative
for every point. At a hypothetical \(G=G'=0\), it still contains the full
shifted jets of \(T_RT_kA\), \(T_pT_{K_r}A\), and \(T_{D_r}A\).
Equation (6) prevents deleting the cutoff term at either order. The exact
commutator theorem proves that a natural transformed jet is nonzero; it
does not force that jet to be zero at a double zero of \(G\).

To turn (17) into a contradiction, one would have to prove from some new
arithmetic relation that \(G(x)=G'(x)=0\) implies \((T_gG)'(x)=0\), or
obtain an independently vanishing shifted-jet combination with a strict
lowest-packet valuation. Neither implication follows from the weighted,
Riccati, reciprocal, or commutator identities above. No actual
nonintersection theorem is claimed.
