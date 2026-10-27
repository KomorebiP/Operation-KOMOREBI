# Nonlinear dilation tangent: established family, worked analytic results

Checkpoint: **SF-DISCOVERY-001**. The normalized function definition is known
verbatim in Miguel A. Méndez's 2024 paper, Example 2.4, as verified in the
third search pass below. The local statements here are mathematical results,
with proofs. Their priority has not been established, and no analytic Lean
certificate is claimed.

## Definition and exact initial coefficients

For a real parameter \(0\le q\le1\), define the normalized germ \(f_q\) by

\[
f_q'(z)=1+f_q(qz)^2,\qquad f_q(0)=0.
\]

This replaces tangent's instantaneous quadratic feedback with feedback from a
contracted argument. It is an ordinary derivative coupled to a dilation. It is
not a Jackson derivative definition.

There is one formal solution, and it is odd:

\[
f_q(z)=\sum_{n\ge0}c_n(q)z^{2n+1},\qquad c_0=1,
\]

\[
\boxed{c_n(q)=\frac{q^{2n}}{2n+1}
\sum_{i=0}^{n-1}c_i(q)c_{n-1-i}(q),\qquad n\ge1.}
\]

Indeed, in a general Taylor series the coefficient of degree \(j+1\) is
determined by the coefficients through degree \(j\). The equation is preserved
by \(f(z)\mapsto-f(-z)\), so uniqueness forces oddness. Matching the coefficient
of \(z^{2n}\) then gives the displayed recurrence. Every \(c_n\) is a polynomial
in \(q\) with nonnegative rational coefficients. For \(q>0\), every coefficient
\(c_n(q)\) is strictly positive.

The first terms are

\[
\begin{aligned}
f_q(z)={}&z+\frac{q^2}{3}z^3+\frac{2q^6}{15}z^5
 +\frac{5q^{10}+12q^{12}}{315}z^7\\
 &+\frac{28q^{16}+10q^{18}+24q^{20}}{2835}z^9+O(z^{11}).
\end{aligned}
\]

The mixed powers of \(q\) at \(z^7\) already record different branching shapes.
This is more structure than multiplying each tangent coefficient by one common
geometric factor.

## Existence, entire extension, and classical points

Let \(t_n=c_n(1)\), the positive Taylor coefficients of \(\tan z\). The recurrence
gives \(0\le c_n(q)\le t_n\) for \(0\le q\le1\). Consequently the germ converges
at least on \(|z|<\pi/2\), where it solves the equation term by term.

**Entire extension theorem.** For each \(0\le q<1\), \(f_q\) extends uniquely to
an entire function.

**Proof.** The case \(q=0\) gives \(f_0(z)=z\). For \(0<q<1\), suppose the germ
has been constructed on the disk \(|z|<R\). On the larger disk \(|z|<R/q\), set

\[
\widetilde f(z)=\int_0^z\bigl[1+f_q(qw)^2\bigr]\,dw.
\]

The integrand is holomorphic throughout the larger disk. Its integral is
independent of the path within that disk. On the original disk it equals the
existing solution by its derivative and its value at zero. Iteration extends
the solution to disks of radii \(Rq^{-k}\), which exhaust the complex plane.
Formal uniqueness gives uniqueness on every extension. \(\square\)

There are three exact classical points, including an intermediate one that
must not be advertised as a new function:

| Parameter | Exact function | Global analytic behavior |
|---|---|---|
| \(q=0\) | \(f_0(z)=z\) | Polynomial |
| \(q=1/2\) | \(f_{1/2}(z)=\sqrt2\sinh(z/\sqrt2)\) | Entire of order \(1\) |
| \(q=1\) | \(f_1(z)=\tan z\) as a germ | Meromorphic, with poles |

For the middle identity, direct substitution gives

\[
1+2\sinh^2\!\left(\frac{z}{2\sqrt2}\right)
=\cosh\!\left(\frac{z}{\sqrt2}\right)
=\frac{d}{dz}\left[\sqrt2\sinh\!\left(\frac{z}{\sqrt2}\right)\right].
\]

The normalization at zero is correct, so uniqueness proves the identity.
Equivalently,

\[
c_n(1/2)=\frac1{2^n(2n+1)!}.
\]

This reduction was discovered in the exact coefficient check and then proved
at the function level. It is a productive exclusion of a false novelty claim.

## The growth order is a structural invariant

For an entire function let

\[
M_q(r)=\max_{|z|=r}|f_q(z)|,\qquad
\rho(f_q)=\limsup_{r\to\infty}
\frac{\log\log M_q(r)}{\log r}.
\]

**Exact order theorem.** For every real \(0<q<1\),

\[
\boxed{\rho(f_q)=\frac{\log2}{\log(1/q)}.}
\]

Moreover \(\log M_q(r)=O(r^{\rho(f_q)})\), so the function has finite upper
type at its order. A strictly positive type or a full asymptotic equivalent
is not asserted here.

**Proof of the upper bound.** Nonnegative coefficients imply

\[
M_q(r)=f_q(r).
\]

The integral equation and monotonicity on the positive real axis give

\[
M_q(r)\le r\,[1+M_q(qr)^2].
\]

Put \(L=\log(1/q)>0\) and \(h(t)=\log M_q(e^t)\). Choose \(T\ge0\). Since
\(M_q(r)\ge r\), for \(t\ge T+L\), \(M_q(qe^t)\ge1\), and hence

\[
h(t)\le2h(t-L)+t+\log2.
\]

Write \(t=T+s+kL\), with \(0\le s<L\). Iterating \(k\) times yields

\[
h(t)\le2^k h(T+s)+
2^k\sum_{\ell=1}^{k}2^{-\ell}(T+s+\ell L+\log2).
\]

The function \(h\) is bounded on the compact interval \([T,T+L]\), and the
infinite sum with the same summand converges. Thus \(h(t)\le C2^k\), uniformly
in \(s\). Since \(2^k\le C' e^{(\log2/L)t}\), this proves the upper bound and
the finite upper type statement.

**Proof of the lower bound.** Fix \(0<\alpha<1\). Integrating only over
\([\alpha r,r]\) gives

\[
M_q(r)=f_q(r)\ge(1-\alpha)r\,M_q(q\alpha r)^2.
\]

Choose \(R>1\) large enough that \((1-\alpha)R\ge1\), and put
\(\beta=q\alpha\). Then

\[
\log M_q(R\beta^{-k})\ge 2^k\log M_q(R).
\]

The seed logarithm is positive because \(M_q(R)\ge R>1\). On this sequence,
the definition of order therefore gives

\[
\rho(f_q)\ge\frac{\log2}{\log(1/\beta)}.
\]

Letting \(\alpha\uparrow1\) proves the lower bound matching the upper bound. \(\square\)

| \(q\) | Exact order |
|---|---|
| \(1/4\) | \(1/2\) |
| \(1/3\) | \(\log2/\log3\) |
| \(1/2\) | \(1\) |
| \(1/\sqrt2\) | \(2\) |
| \(2^{-1/\sqrt2}\) | \(\sqrt2\) |
| \(q\uparrow1\) | Order tends to infinity |

This continuum of growth orders is a useful classification target. It does
not by itself exclude every established named-function class. In particular,
no blanket claim about Fox \(H\), Wright, or other broad classes is made.

## Confluence and positivity

**Confluence theorem.** As \(q\uparrow1\), \(f_q\to\tan\) locally uniformly on
\(|z|<\pi/2\). For each fixed coefficient, the polynomial \(c_n(q)\) converges
to \(t_n\). On a closed disk of radius \(R<\pi/2\), the summable majorant
\(t_nR^{2n+1}\) proves uniform convergence. The same reasoning shows
\(f_q\to z\) locally uniformly on every fixed compact subset of the plane as
\(q\downarrow0\): fix any \(q_0<1\), dominate by the convergent entire series
for \(f_{q_0}\), and use \(c_n(q)\to0\) for \(n\ge1\).

For real \(0<q<1\), \(f_q\) is odd, strictly increasing on the real axis, and
\(f_q'(x)=1+f_q(qx)^2\ge1\). Its only real zero is zero. On \(x>0\), it is
strictly convex since

\[
f_q''(x)=2qf_q(qx)f_q'(qx)>0.
\]

Also \(f_{q_1}(r)<f_{q_2}(r)\) for \(r>0\) and \(0\le q_1<q_2\le1\) wherever
both series converge, with no disk restriction if \(q_2<1\). This follows
coefficientwise, with strictness already supplied by \(c_1=q^2/3\).

The rotation \(g_q(z)=-i f_q(iz)\) is entire for \(q<1\) and satisfies

\[
g_q'(z)=1-g_q(qz)^2,\qquad g_q(0)=0.
\]

Its classical points are \(g_0(z)=z\),
\(g_{1/2}(z)=\sqrt2\sin(z/\sqrt2)\), and \(g_1(z)=\tanh z\) as a germ.
This is a rotated member of the same family, not a separately counted
discovery. Global real boundedness of \(g_q\) for generic \(q\) has not been
proved here.

## Tree formula and the packet connection

Let \(\mathcal T_n\) be the set of full ordered binary trees with \(n\) internal
vertices. For an internal vertex \(v\), let \(n_v\) be the number of internal
vertices in its rooted subtree. Then the recurrence gives the exact formula

\[
\boxed{
c_n(q)=\sum_{T\in\mathcal T_n}
\frac{q^{2\sum_{v\text{ internal}} n_v}}
{\prod_{v\text{ internal}}(2n_v+1)}.}
\]

The tree with no internal vertex has weight one. Splitting a nonempty tree at
the root gives subtrees with \(i\) and \(n-1-i\) internal vertices. The root
contributes \(q^{2n}/(2n+1)\); the two subtree factors give the recurrence, which
proves the formula by induction.

Since

\[
\sum_{v\text{ internal}}n_v
=n+\sum_{v\text{ internal}}\operatorname{depth}(v),
\]

the parameter weights the actual branching depths. At \(n=3\), the balanced
tree contributes \(q^{10}/63\), while the four unbalanced trees together
contribute \(4q^{12}/105\). Thus addresses and branching geometry enter the
coefficients, rather than being added afterward as plotting coordinates.

## Degree generalization, also contained in the established construction

For an integer \(m\ge2\), define

\[
F_{q,m}'(z)=1+F_{q,m}(qz)^m,\qquad F_{q,m}(0)=0.
\]

The formal series has powers \(mn+1\), with

\[
F_{q,m}(z)=\sum_{n\ge0}d_n z^{mn+1},\quad d_0=1,
\]

\[
d_n=\frac{q^{mn}}{mn+1}
\sum_{i_1+\cdots+i_m=n-1}d_{i_1}\cdots d_{i_m}.
\]

The recurrence applies for \(n\ge1\).

The classical germ at \(q=1\) is the local inverse of

\[
w\longmapsto\int_0^w\frac{dt}{1+t^m}.
\]

It supplies a positive-coefficient majorant on some neighborhood of zero.
The same disk-radius bootstrap proves that \(F_{q,m}\) is entire for \(q<1\).
The maximum-modulus upper and lower estimates replace the square by the
\(m\)th power. The preceding proof, with \(2\) replaced by \(m\), therefore gives

\[
\rho(F_{q,m})=\frac{\log m}{\log(1/q)},\qquad0<q<1.
\]

The first three terms are

\[
F_{q,m}(z)=z+\frac{q^m}{m+1}z^{m+1}
 +\frac{m q^{3m}}{(m+1)(2m+1)}z^{2m+1}+O(z^{3m+1}).
\]

Méndez's Theorem 2.1 already constructs the formal family with general
nonlinearity \(\phi\), which includes \(\phi(w)=1+w^m\). Thus changing the degree does
not rescue a new-definition claim for this route. The entire extension and
growth calculations remain substantive analytic questions.

Adding a constant coefficient \(λ>0\) to the nonlinear term does not supply
an independent family: the normalized solution of
\(H'=1+\lambda H(qz)^m\) is

\[
H(z)=\lambda^{-1/m}F_{q,m}(\lambda^{1/m}z).
\]

The degree generalization is proved by the same argument but has not been
included in the binary numerical check's 1,218 assertion count.

## Exact finite computation and worked values

Regenerate with

```bash
python checks/nonlinear_dilation.py
```

The script uses only Python's standard library. Its **1,218 exact assertions**
check coefficient recurrence and a distinct repeated Picard-polynomial
construction through degree \(61\), all even coefficients, nonnegativity,
coefficient bounds, endpoint tangent coefficients obtained independently from
Bernoulli numbers, the scaled-sinh point, and symbolic polynomial evaluation
through \(c_{12}\). Rational test parameters are
\(0,1/3,1/2,3/4,1\). Python at the author run was 3.12.14.

For rigorous truncation control, the tangent recurrence implies
\(t_n\le2^{-n}\): assuming the bound below index \(n\),

\[
t_n\le\frac{n,2^{-(n-1)}}{2n+1}<2^{-n}.
\]

Also \(c_n(q)\le q^{2n}t_n\) follows by using \(c_i(q)\le t_i\) in the
recurrence. Therefore, for \(|z|\le1\), the degree-\(61\) truncation error obeys

\[
\left|f_q(z)-\sum_{n=0}^{30}c_n(q)z^{2n+1}\right|
\le\frac{(q^2/2)^{31}}{1-q^2/2}.
\]

| \(q\) | \(f_q(1)\), decimal approximation | Absolute analytic truncation bound |
|---|---|---|
| \(0\) | \(1\) exactly | \(0\) |
| \(1/3\) | \(1.0372202767202585\) | less than \(2\times10^{-39}\) |
| \(1/2\) | \(1.085441641272607\) | less than \(2\times10^{-28}\) |
| \(3/4\) | \(1.2134856167378945\) | less than \(1.17\times10^{-17}\) |
| \(1\) | \(1.5574077246539582\) | less than \(9.32\times10^{-10}\) |

The decimals are floating displays of exact rational partial sums. The stated
bounds control analytic truncation, separately from floating conversion.
Finite checks authenticate the implemented formulas in the specified range.
The entire-extension and growth-order conclusions rest on the proofs above.

## Bounded primary-source comparison

Search question: is the normalized equation \(f'=1+f(qz)^2, f(0)=0\), or its
growth-order theorem, already present under nonlinear pantograph, delayed
Riccati, dilated tangent, or generalized \(q\)-tangent terminology?

Two web search strategies were used on 2026-10-08 UTC. Queries included
`"pantograph" "tangent" nonlinear differential equation`,
`"nonlinear pantograph" "growth" entire order`,
`"pantograph" "entire" "nonlinear" growth`,
`"q-tangent" pantograph`, `"pantograph Riccati" equation`,
`"nonlinear functional differential" "order" "log 2"`, and exact equation
variants such as `"y'(x)=1+y" pantograph`.

The closest primary source inspected in the first two passes was Radu Dascaliuc, Tuan N.
Pham, Enrique Thomann, and Edward C. Waymire, *Transformation of Stochastic
Recursions and Critical Phenomena in the Analysis of the Aldous-Shields-Athreya
Cascade and Related Mean Flow Equations*,
[arXiv:2411.00629v2](https://arxiv.org/html/2411.00629v2), revised 2 May 2025.
Its equation (1.8) is

\[
u'(t)=-u(t)+u(\alpha t)^2.
\]

This verifies **adjacent established nonlinear pantograph/Riccati structure**.
It is not the candidate's normalized equation: it includes a current-state
linear term and no constant forcing. An affine change \(u=af+b\) instead gives
a linear term in \(u(qz)\), not in \(u(z)\), for \(q\ne1\). Its principal
nonuniqueness investigations also concern parameter regimes different from
the candidate's positive contraction and holomorphic-germ setting. No
theorem from that source is needed for the proofs above.

Changgui Zhang's [arXiv:1202.0423](https://arxiv.org/abs/1202.0423), *Analytic
continuation of solutions of the pantograph equation by means of theta-modular
formula*, submitted 2 February 2012, was also inspected. Its equation is linear,
\(y'=ay(qx)+by(x)\), so it authenticates nearby terminology and the existing
connection-problem literature, not an identification of this nonlinear family.

A primary 2023 page on degenerate \(q\)-tangent polynomials was found but direct
retrieval failed with HTTP 429. Its full content was not authenticated and is
not used as a mathematical dependency. The usual \(q\)-tangent naming therefore
needs a more complete comparison before adopting a permanent name.

The initial two search passes classified the inspected sources as adjacent.
That was an interim search result, not a novelty conclusion. A third strategy,
searching `"q-tangent" "binary trees" depth` and
`"tangent numbers" "path length" trees q`, found an exact match.

**Correction from the third search pass.** Miguel A. Méndez, *Combinatorial
differential operators in: Faà di Bruno formula, enumeration of ballot paths,
enriched rooted trees and increasing rooted trees*, Australasian Journal of
Combinatorics **89(3)** (2024), 350–384,
[official journal PDF](https://ajc.maths.uq.edu.au/pdf/89/ajc_v89_p350.pdf),
was opened and its full text inspected. Example 2.4, printed page 356, gives
exactly \(\partial_tP_\beta(t,q)=1+P_\beta(tq,q)^2\), with the zero normalization supplied by
Theorem 2.1 on page 354. The notation translation is simply

\[
f_q(z)=P_\beta(z,q),\qquad
c_n(q)=\frac{p^\beta_{2n+1}(q)}{(2n+1)!}.
\]

Classification of the definition: **known verbatim**. Its path-length
interpretation and arbitrary-degree formal construction are also established
in that source. The exact growth-order result is not stated in the inspected
paper; its wider historical status remains unverified. The two earlier search
passes missed the match because the effective vocabulary was combinatorial
tree path length rather than only nonlinear pantograph analysis.

Book chapters, older nonindexed functional-differential literature, other
languages, and full citation chains remain unchecked. The same author performed
all three discovery strategies. These limitations apply particularly to any
future priority claim for the analytic growth theorem.

## What has been achieved and what remains open

This route develops an established normalized analytic family, unique entire members for
every positive contraction, an exact growth-order invariant, a branching
formula, rigorous classical confluence, three explicit classical points,
a degree generalization, and reproducible finite arithmetic.

The unresolved research questions are precise: check prior analytic growth
results; determine generic reduction or nonreduction to specified function
classes; classify complex zeros and imaginary-axis dynamics; determine
positive type, leading asymptotics, and connection formulas; and find transfer
or arithmetic properties that make the family useful. None of these open
questions retracts the proved analytic statements.
