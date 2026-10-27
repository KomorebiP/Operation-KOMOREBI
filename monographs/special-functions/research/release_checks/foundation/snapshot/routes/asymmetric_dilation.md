# Asymmetric dilation functions with intrinsic feedback taps

Checkpoint: **SF-DISCOVERY-001**. The symmetric definition is established in
Méndez's path-length construction. The route here develops two independent
child contractions and then a finite feedback bank. A bounded search has not
settled historical priority for this extension. The local results below have
explicit proofs, and the final finite run passes 1,811 exact assertions.

## Definition, recurrence, and first terms

For real \(0<q,r<1\), define \(T_{q,r}\) by

\[
\boxed{T_{q,r}'(z)=1+T_{q,r}(qz)T_{q,r}(rz),\qquad T_{q,r}(0)=0.}
\]

There is a unique formal solution, which is odd. Write

\[
T_{q,r}(z)=\sum_{n\ge0}c_n(q,r)z^{2n+1},\qquad c_0=1.
\]

Matching coefficients gives

\[
\boxed{c_n=\frac1{2n+1}\sum_{i=0}^{n-1}
q^{2i+1}r^{2(n-1-i)+1}c_i c_{n-1-i}.}
\]

The recurrence applies for \(n\ge1\).

The coefficients are positive on the parameter domain and are polynomials
over \(\mathbb{Q}[q,r]\). Commutativity of the defining product gives
\(T_{q,r}=T_{r,q}\). The first terms are

\[
\begin{aligned}
T_{q,r}(z)={}&z+\frac{qr}{3}z^3
 +\frac{q^2r^2(q^2+r^2)}{15}z^5\\
 &+q^3r^3\left[
 \frac{(q^2+r^2)(q^4+r^4)}{105}+\frac{q^2r^2}{63}
 \right]z^7+O(z^9).
\end{aligned}
\]

When \(q=r\), this is exactly the established one-dilation function \(f_q\).
Thus the diagonal is a classical boundary inside the extension, and is not
counted as a new function definition. If either contraction is zero, the
normalized solution degenerates to \(z\); those points are excluded from the
positive growth theorem but included as finite-code negative controls.

The parameters are identifiable, up to their unavoidable swap, from the first
two nontrivial Taylor coefficients. Set

\[
p=3c_1=qr,\qquad u=\frac{15c_2}{p^2}=q^2+r^2.
\]

Then \(q+r=\sqrt{u+2p}\), and \(q,r\) are the roots of

\[
x^2-\sqrt{u+2p}\,x+p=0.
\]

So the two scales are visible in the function itself, rather than only in an
external representation.

## Entire extension

Let \(Q=\max(q,r)<1\), and let \(t_n\) denote the tangent coefficients. The
recurrence gives \(0<c_n(q,r)\le Q^{2n}t_n\le t_n\), by induction followed by
the recurrence once more with \(c_i\le t_i\). Thus the germ converges at least
on \(|z|<\pi/2\).

If the solution is known on \(|z|<R\), the integral

\[
\int_0^z\left[1+T_{q,r}(qw)T_{q,r}(rw)\right]\,dw
\]

defines a holomorphic extension on \(|z|<R/Q\), agrees with the old solution,
and satisfies the same equation. Iteration exhausts the plane. Hence every
member in the positive contraction domain is an entire function.

Nonnegative coefficients give \(M(x)=T_{q,r}(x)\) for the maximum modulus on
\(|z|=x\), \(x>0\). The function is strictly increasing on the real line and
strictly convex for positive real arguments. These statements follow directly
from the equation, positivity, and oddness.

## Exact order from two competing scales

Let \(\rho>0\) be the unique solution of

\[
\boxed{q^\rho+r^\rho=1.}
\]

The root exists and is unique since the left side decreases continuously from
\(2\) to \(0\) as \(\rho\) ranges from \(0\) to infinity.

**Theorem.** The entire function \(T_{q,r}\) has exactly this order. It has
finite upper type at that order:

\[
\boxed{\rho(T_{q,r})=\rho,\qquad\log M(x)=O(x^\rho).}
\]

For \(q=r\), the characteristic equation reduces to
\(\rho=\log2/\log(1/q)\). For \(q+r=1\), every member has order \(1\), despite
having different Taylor coefficients.

The complete proof is included in the feedback-bank theorem below, with one
channel of weight one. The two core estimates are

\[
M(x)\le x[1+M(qx)M(rx)],
\]

\[
M(x)\ge(1-\alpha)xM(\alpha qx)M(\alpha rx),\qquad0<\alpha<1.
\]

The first comes from the whole integral and monotonicity; the second integrates
only over \([\alpha x,x]\). The additive logarithm of \(x\) changes the type estimates,
but does not change the characteristic equation for the order.

| Parameters | Order |
|---|---|
| \(q=r=1/4\) | \(1/2\) |
| \(q=1/3,r=1/2\) | Root of \(3^{-\rho}+2^{-\rho}=1\), about \(0.7878849110\) |
| \(q=1/3,r=2/3\) | \(1\) |
| \(q=1/4,r=3/4\) | \(1\) |
| \(q=r=1/\sqrt2\) | \(2\) |

The positive order root is the same type of scale-balance equation that appears
in self-similar dimension calculations. That shared equation does not imply an
identification of this entire function with a fractal measure.

## Exact separation from the established one-dilation family

**Nonrescaling theorem.** If \(q\ne r\), then \(T_{q,r}\) is not an amplitude
and argument rescaling of any \(f_s\) with \(0<s<1\).

**Proof.** Suppose \(T_{q,r}(z)=A f_s(Bz)\) with \(A,B\ne0\). Differentiating
at zero forces \(AB=1\), so write \(T_{q,r}(z)=B^{-1}f_s(Bz)\). Put \(p=qr\),
\(u=q^2+r^2\), and let \(\rho\) be the order of \(T_{q,r}\). Orders are unchanged by
these nonzero rescalings, so

\[
2s^\rho=1=q^\rho+r^\rho.
\]

Comparing \(z^3\) and \(z^5\) coefficients gives

\[
B^2s^2=p,\qquad s^2=\frac{u}{2}.
\]

In particular \(B^2>0\); allowing complex \(A,B\) supplies no further exception.
Consequently

\[
2\left(\frac{q^2+r^2}{2}\right)^{\rho/2}=q^\rho+r^\rho.
\]

When \(\rho\ne2\), strict convexity or strict concavity of \(x\mapsto x^{\rho/2}\)
forces \(q^2=r^2\), hence \(q=r\), a contradiction.

For the exceptional order \(\rho=2\), one has \(u=1\), \(s^2=1/2\), and \(B^2=2p\).
The two \(z^7\) coefficients then are

\[
c_3(T)=\frac{p^3(3-p^2)}{315},\qquad
c_3(B^{-1}f_s(Bz))=\frac{11p^3}{1260}.
\]

Their equality forces \(p^2=1/4\), so \(p=1/2\). Together with \(u=1\), this
gives \((q-r)^2=u-2p=0\), again a contradiction. \(\square\)

This proves a real distinction from the already authenticated diagonal
family. It is a scoped nonreduction result, not exclusion of every established
special function or a historical novelty theorem.

In particular, the only normalized scaled-sinh member is the diagonal point
\(q=r=1/2\). A scaled sinh has order one, forcing \(q+r=1\). Matching \(z^3\)
sets its scale squared to \(2qr\); matching \(z^5\) then requires
\(q^2+r^2=1/2\), which forces \(q=r=1/2\). All positive contraction members are
entire, so none is a nonconstant scaled tangent with its uncancelled poles.

## Intrinsic nonlinear taps

Choose a finite bank

\[
\Theta=\{(h_j,q_j,r_j):j=1,\ldots,J\},\qquad
h_j>0,\quad\sum_jh_j=1,\quad0<q_j,r_j<1.
\]

Define

\[
\boxed{F_\Theta'(z)=1+\sum_{j=1}^J h_j
F_\Theta(q_jz)F_\Theta(r_jz),\qquad F_\Theta(0)=0.}
\]

Here the taps enter the defining nonlinear feedback. They determine the
function's coefficients before any external filter is applied. This is a
branch of the same asymmetric dilation family, not a second independent
discovery counted solely because it has more parameters.

For \(F_\Theta(z)=\sum c_nz^{2n+1}\), the exact recurrence is

\[
c_n=\frac1{2n+1}\sum_jh_j\sum_{i=0}^{n-1}
q_j^{2i+1}r_j^{2(n-1-i)+1}c_i c_{n-1-i}.
\]

Here \(c_0=1\), and the recurrence applies for \(n\ge1\).

Put

\[
\mu_1=\sum_jh_jq_jr_j,\qquad
\mu_2=\sum_jh_jq_jr_j(q_j^2+r_j^2).
\]

The first coefficients are

\[
F_\Theta(z)=z+\frac{\mu_1}{3}z^3+
\frac{\mu_1\mu_2}{15}z^5+O(z^7).
\]

The bank is invariant under swapping the two scales within any channel,
permuting channels, and merging duplicate scale pairs by adding their weights.
Those changes do not produce new functions.

Let \(Q=\max_j\max(q_j,r_j)<1\). The same positive-coefficient majorant and
radius bootstrap prove that \(F_\Theta\) is entire. Let \(\rho_j\) be the unique positive
root of \(q_j^{\rho_j}+r_j^{\rho_j}=1\).

**Tap-bank growth theorem.**

\[
\boxed{\rho(F_\Theta)=\max_j\rho_j,\qquad
\log M_\Theta(x)=O\bigl(x^{\max_j\rho_j}\bigr).}
\]

The fixed positive weights affect coefficients and finite-scale behavior but
do not change the asymptotic order. The characteristic equation must not be
averaged across channels. A zero-weight channel is inactive and must be removed
before taking the maximum.

**Upper-bound proof.** Put \(H(t)=\log M_\Theta(e^t)\),
\(a_j=\log(1/q_j)>0\), \(b_j=\log(1/r_j)>0\),
\(\Delta=\max_j\max(a_j,b_j)\), and \(\delta=\min_j\min(a_j,b_j)>0\).
Choose \(T\ge1\). For \(t\ge T+\Delta\), every child radius has maximum modulus at
least one because \(F_\Theta(x)\ge x\). Monotonicity, the integral equation, and the
weight normalization give

\[
H(t)\le t+\log2+\max_j[H(t-a_j)+H(t-b_j)].
\]

Choose a constant \(B\ge\max_j(a_j+b_j)+\log2\), and define

\[
G(t)=H(t)+t+B.
\]

The preceding estimate becomes

\[
G(t)\le\max_j[G(t-a_j)+G(t-b_j)].
\]

Let \(\rho=\max_j\rho_j\). Then \(q_j^\rho+r_j^\rho\le1\) for every channel. Choose
\(C>0\) so \(G(t)\le Ce^{\rho t}\) throughout the compact seed interval
\([T,T+\Delta]\). Induct over intervals of length \(\delta\) starting at \(T+\Delta\).
Each predecessor \(t-a_j,t-b_j\) lies in the seed interval or an already
controlled earlier interval, and

\[
G(t)\le Ce^{\rho t}\max_j(q_j^\rho+r_j^\rho)\le Ce^{\rho t}.
\]

This proves \(H(t)\le Ce^{\rho t}-t-B\) for large \(t\), hence order at most
\(\rho\) and finite upper type.

**Lower-bound proof.** Select a channel \(j_*\) with \(\rho_{j_*}=\rho\). For
\(0<\alpha<1\), positivity and the partial integral give

\[
M_\Theta(x)\ge h_{j_*}(1-\alpha)x
M_\Theta(\alpha q_{j_*}x)M_\Theta(\alpha r_{j_*}x).
\]

Let \(s_\alpha>0\) solve
\((\alpha q_{j_*})^{s_\alpha}+(\alpha r_{j_*})^{s_\alpha}=1\), and let \(A,D>0\) be the two
logarithmic contraction lengths. Choose \(T_\alpha\ge1\) with
\(e^{T_\alpha}\ge1/[h_{j_*}(1-\alpha)]\). For \(t\ge T_\alpha+\max(A,D)\), the prefactor
is at least one, so

\[
H(t)\ge H(t-A)+H(t-D).
\]

Since \(H(t)\ge t>0\), choose \(c>0\) such that
\(H(t)\ge ce^{s_\alpha t}\) on \([T_\alpha,T_\alpha+\max(A,D)]\). The same interval
induction, now using the equality of the two contracted powers, propagates
this bound to all larger \(t\). Thus the order is at least \(s_\alpha\).
As \(\alpha\uparrow1\), continuity and monotonicity of the root give
\(s_\alpha\uparrow\rho\). This matches the upper bound. \(\square\)

## Address-weighted tree formula

For the single asymmetric channel, sum over full ordered binary trees with
\(n\) internal vertices. An internal vertex \(v\), with left and right subtrees
containing \(i_v\) and \(j_v\) internal vertices, contributes

\[
\frac{q^{2i_v+1}r^{2j_v+1}}{2(i_v+j_v+1)+1}.
\]

Multiplying these factors and summing over trees gives \(c_n(q,r)\). Root
splitting proves the formula by the coefficient recurrence. The total
\(q\)-exponent counts, over all vertices including leaves, the number of left
edges in each vertex's root path. The total \(r\)-exponent counts the analogous
right edges. Unequal contractions therefore retain left/right address geometry
inside the function.

For a bank, assign a channel color independently to each internal vertex and
multiply its factor by \(h_j\). Sum over these colors and tree shapes. This is
an exact coefficient formula for \(F_\Theta\), not a stochastic approximation.
The finite positive tap weights can also be interpreted as probabilities for
the vertex colors because they sum to one.

## Worked coefficients and finite checks

For \(q=1/3,r=2/3\), an off-diagonal order-one member,

\[
T_{1/3,2/3}(z)=z+\frac2{27}z^3+\frac4{2187}z^5+
\frac{232}{11160261}z^7+O(z^9),
\]

and \(T_{1/3,2/3}(1)\approx1.0759239897408248\). It is neither the scaled-sinh
point nor a rescaled one-dilation member, by the theorems above.

For the bank with channels

\[
(h_1,q_1,r_1)=(1/4,1/4,1/4),\qquad
(h_2,q_2,r_2)=(3/4,3/4,3/4),
\]

one obtains

\[
F_\Theta(z)=z+\frac7{48}z^3+\frac{427}{30720}z^5+
\frac{176681}{188743680}z^7+O(z^9).
\]

Its order is \(\log2/\log(4/3)\approx2.4094208397\), determined by the active
second channel, and \(F_\Theta(1)\approx1.1607208608458885\).

For an equal-weight bank with pairs \((1/3,2/3)\) and \((1/4,3/4)\), both
channels have order one, but its Taylor coefficients differ from either seed:

\[
F_\Theta(z)=z+\frac{59}{864}z^3+\frac{29441}{17915904}z^5+O(z^7),
\]

with \(F_\Theta(1)\approx1.0699488188635053\). It still has order one.

Regenerate with `python checks/asymmetric_dilation.py`. The script uses exact
rational arithmetic and bivariate polynomial dictionaries. It checks a
distinct Picard integration construction through degree \(61\), all even
coefficients, recurrence residuals, swapping invariance, tangent domination,
the first bank moments, diagonal agreement with the authenticated family,
off-diagonal scaled-sinh exclusion on \(q+r=1\), and the exceptional-order
nonrescaling obstruction at \((q,r)=(3/5,4/5)\). Bivariate polynomials are
checked through \(c_8\). There are seven rational scale pairs and two two-channel
banks, yielding **1,811 exact assertions** in Python 3.12.14.

For \(|z|\le1\), the degree-\(61\) analytic truncation error obeys

\[
\left|F_\Theta(z)-\sum_{n=0}^{30}c_nz^{2n+1}\right|
\le\frac{(Q^2/2)^{31}}{1-Q^2/2},
\]

because \(c_n\le Q^{2n}t_n\le(Q^2/2)^n\). The three displayed evaluations have
analytic tail bounds respectively below \(7.24\times10^{-21}\),
\(1.17\times10^{-17}\), and \(1.17\times10^{-17}\). Decimal conversion is a
separate floating display of the exact rational partial sum. A passing finite
run does not establish the analytic theorems or historical novelty.

## Literature boundary and interpretation

The diagonal overlaps exactly with Miguel A. Méndez's *Combinatorial differential
operators in: Faà di Bruno formula, enumeration of ballot paths, enriched rooted
trees and increasing rooted trees*, Australasian Journal of Combinatorics 89(3)
(2024), Example 2.4 and Theorem 2.1,
[verified journal PDF](https://ajc.maths.uq.edu.au/pdf/89/ajc_v89_p350.pdf).
Its general scalar nonlinearity also covers changing the degree at a single
common contraction. This is why the off-diagonal nonrescaling theorem is a
material separator rather than merely a new name for its formal family.

A bounded two-strategy search on 2026-10-08 UTC used exact equation variants
`"y'(x)" "y(qx)y(rx)"`, `"f'(z)" "f(qz)" "f(rz)"`,
`"pantograph" "two delays" "product" entire`,
`"binary trees" "left path length" "right path length" generating`, and
related nonlinear pantograph and multitype tree terminology. This search did
not authenticate the exact asymmetric normalized equation in a prior source.
That is not a global novelty conclusion.

Charles Knessl and Wojciech Szpankowski's *Binary Trees, Left and Right Paths,
WKB Expansions, and Painlevé Transcendents*, ANALCO 2006, 198–204,
[DOI:10.1137/1.9781611972962.2](https://doi.org/10.1137/1.9781611972962.2),
was found as a close combinatorial lead. Its publisher page authenticates its
metadata and its study of joint left/right path lengths. The author-hosted
full PDF could not be retrieved by the web tool, and the publisher exposed an
access wall. Its detailed hypotheses and possible exact-family overlap are
therefore **unverified** here. No theorem from that paper is used in this route.

The established nonlinear alpha-Riccati literature is also adjacent, including
[arXiv:2411.00629v2](https://arxiv.org/html/2411.00629v2), equation (1.8),
\(u'=-u+u(\alpha t)^2\); its exact equation differs from this normalization.
General multitype increasing-tree constructions, older delay-differential
books, and full citation chains need further comparison. The tap-bank
definition particularly needs that broader follow-up before claiming priority.

Classification: an explicitly developed extension with proved local analytic
structure and a proved nonrescaling boundary against one authenticated prior
family. Historical novelty remains open. The next analytic targets are zeros,
leading growth asymptotics, connection formulas, parameter sensitivity, and
signed tap banks, where positivity-based order arguments can fail.
