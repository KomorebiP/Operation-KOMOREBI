# Positive lower type and quantitative tap continuity

Checkpoint: **SF-DISCOVERY-100**, based on the definitions and entire-extension
proof in `routes/asymmetric_dilation.md`. This file strengthens that route's
order theorem. It does not alter the classification of the symmetric definition
as established, or settle historical priority for the asymmetric extension.

## 1. The exact growth exponent has positive lower type

Let

\[
F'(z)=1+\sum_{j=1}^{J}h_jF(q_jz)F(r_jz),\qquad F(0)=0,
\]

where \(h_j>0\), \(\sum_jh_j=1\), and \(0<q_j,r_j<1\).
Zero-weight channels may instead be allowed if they are removed from the
active bank before defining its growth exponent. Put

\[
\rho=\max_{j:h_j>0}\rho_j,\qquad q_j^{\rho_j}+r_j^{\rho_j}=1.
\]

The inherited coefficient recurrence gives nonnegative coefficients, entire
extension, and
\(M(R)=\max_{|z|=R}|F(z)|=F(R)\ge R\) for \(R>0\).

**Theorem 1.** There are explicit constants \(0<c_-\le c_+<\infty\) such that

\[
c_-\le\liminf_{R\to\infty}\frac{\log M(R)}{R^\rho}
\le\limsup_{R\to\infty}\frac{\log M(R)}{R^\rho}\le c_+.
\]

In particular the bank has positive lower type and finite upper type at its
exact order, including when \(0<\rho<1\). Furthermore

\[
\lim_{R\to\infty}\frac{\log\log M(R)}{\log R}=\rho.
\]

This last radial growth-exponent limit does not assert a type limit or uniform
angular growth.

### Explicit lower constants and proof

Select any active maximizing channel and abbreviate it to \((h,q,r)\), so
\(q^\rho+r^\rho=1\). Define

\[
L=\frac1h,\qquad
C=\max\left(\frac{qL}{1-q},\frac{rL}{1-r}\right),\qquad
B=L+\frac2{\min(q,r)},\qquad
c_-=\frac{\log2}{(B+C)^\rho}.
\]

We prove the stronger bound

\[
\boxed{\log M(R)\ge c_-(R+C)^\rho\quad\text{for every }R\ge2.}
\]

Write \(H(R)=\log M(R)\). On the seed interval \([2,B]\),
\(H(R)\ge\log R\ge\log2\ge c_-(R+C)^\rho\).
For \(R\ge B\), integrate the positive feedback over the fixed-width interval
\([R-L,R]\):

\[
\begin{aligned}
M(R)&\ge h\int_{R-L}^{R}M(qt)M(rt)\,dt\\
&\ge hL M(q(R-L))M(r(R-L))\\
&=M(q(R-L))M(r(R-L)).
\end{aligned}
\]

The two child radii are at least two because \(R\ge B\). Moreover

\[
q(R-L)+C\ge q(R+C),\qquad
r(R-L)+C\ge r(R+C),
\]

because respectively \((1-q)C\ge qL\) and \((1-r)C\ge rL\).
If the comparison bound is known at both child radii, it follows that

\[
\begin{aligned}
H(R)&\ge H(q(R-L))+H(r(R-L))\\
&\ge c_-\{[q(R-L)+C]^\rho+[r(R-L)+C]^\rho\}\\
&\ge c_-(q^\rho+r^\rho)(R+C)^\rho
=c_-(R+C)^\rho.
\end{aligned}
\]

For a rigorous propagation, put \(Q_* =\max(q,r)<1\) and
\(d=(1-Q_*)B+Q_*L>0\). Every child of every \(R\ge B\) is at most
\(R-d\). Induction on the intervals
\([B+kd,B+(k+1)d]\), beginning with the already controlled seed, proves the
comparison for all larger radii. Continuity deals with common endpoints.
All power comparisons use only monotonicity of \(x^\rho\) for positive \(x\);
no convexity assumption is made, so the argument also covers \(\rho<1\).

### Explicit finite upper constants

For all channels set

\[
Q=\max_j\max(q_j,r_j),\quad
m=\min_j\min(q_j,r_j),\quad
\Delta=\log(1/m),\quad
B_+=\max_j\log\frac1{q_jr_j}+\log2.
\]

Choose an integer \(N\ge0\) with \(Q^{-N}\ge3/m\), and put

\[
V_N=(2^{N+1}-1)\log2+
       (2^{N+1}-N-2)\log(1/Q),
\]

\[
c_+=e^{-\rho}(V_N+1+\Delta+B_+).
\]

These constants are intentionally conservative, and require no numerical
evaluation of an unknown solution. The tangent majorant gives \(M(1)<2\).
At \(R_k=Q^{-k}\), the integral equation gives

\[
M(R_k)\le R_k[1+M(R_{k-1})^2].
\]

Define \(U_0=2\), \(U_k=Q^{-k}(1+U_{k-1}^2)\). Then \(M(R_k)\le U_k\),
\(U_k\ge1\), and
\(\log U_k\le k\log(1/Q)+\log2+2\log U_{k-1}\).
Summing this elementary recurrence gives \(\log U_N\le V_N\).
Since \(e<3\), the logarithmic-radius seed
\(1\le t\le1+\Delta\) has \(e^t\le e/m<3/m\le R_N\), and therefore
\(\log M(e^t)\le V_N\).

Let \(a_j=\log(1/q_j)\), \(b_j=\log(1/r_j)\), and
\(G(t)=\log M(e^t)+t+B_+\). For \(t\ge1+\Delta\), all child moduli are at
least one, so the positive integral and weight normalization give

\[
\log M(e^t)\le t+\log2+
\max_j\{\log M(e^{t-a_j})+\log M(e^{t-b_j})\}.
\]

The definition of \(B_+\) implies

\[
G(t)\le\max_j\{G(t-a_j)+G(t-b_j)\}.
\]

On the seed, \(G(t)\le V_N+1+\Delta+B_+\le c_+e^{\rho t}\).
Each channel satisfies \(q_j^\rho+r_j^\rho\le1\). Induction in intervals of
length \(\min_j\min(a_j,b_j)>0\) therefore propagates the seed comparison,
giving the explicit upper bound

\[
\boxed{\log M(R)\le c_+R^\rho-\log R-B_+\quad(R\ge e).}
\]

Dividing the two bounds by \(R^\rho\), then taking logarithms of their positive
logarithmic-growth bounds, proves all assertions of Theorem 1. The theorem
leaves open whether \(\log M(R)/R^\rho\) has a limit. Lattice resonances or
logarithmic oscillations are possible research directions, not results here.

## 2. Joint holomorphic dependence on parameters

Fix the number \(J\) of channels. Allow complex weights \(h_j\), without
normalization, and complex contractions satisfying \(|q_j|,|r_j|<1\).
The same formal recurrence defines coefficients

\[
c_n(h,q,r)\in\mathbb Q[h_1,\ldots,h_J,q_1,r_1,\ldots,q_J,r_J].
\]

Each is homogeneous of degree \(n\) in the weights. If a parameter set has
\(|q_j|,|r_j|\le Q<1\) and \(\sum_j|h_j|\le W\), with \(W>0\), coefficient
induction gives

\[
|c_n(h,q,r)|\le W^n d_n(Q),
\]

where \(f_Q(z)=\sum d_n(Q)z^{2n+1}\) is the established diagonal function.
Consequently, on every disk \(|z|\le R\),

\[
\sum_{n\ge0}|c_n(h,q,r)|R^{2n+1}
\le W^{-1/2}f_Q(\sqrt W R)<\infty.
\]

Every compact subset of the complex parameter domain has such \(Q,W\).
The series therefore converges normally on compact sets of the joint domain,
and its sum is jointly holomorphic in the weights, contractions, and \(z\).
This proves parameter continuity at zero weights, although the growth order
can jump there. Complex or signed parameters do not inherit the positive-bank
growth theorem merely from holomorphic dependence.

## 3. A quantitative compact bound for changing tap weights

Keep fixed real contractions \(0<q_j,r_j\le Q<1\), and let \(h,g\) be
nonnegative normalized weight vectors. Zero weights are permitted. Let
\(d=\|h-g\|_1\). Then for every \(R\ge0\),

\[
\boxed{\sup_{|z|\le R}|F_h(z)-F_g(z)|
\le\frac d4\{R f_Q'(R)-f_Q(R)\}.}
\]

**Proof.** Regard \(c_n\) as a polynomial in the real weight variables with
the contractions fixed. Its coefficients are nonnegative. Induction in the
recurrence gives the coefficientwise polynomial bound

\[
0\preceq c_n(h)\preceq d_n(Q)\Bigl(\sum_jh_j\Bigr)^n.
\]

Here \(\preceq\) compares every monomial coefficient. Differentiation preserves
this comparison, so on the normalized nonnegative simplex

\[
0\le\partial_{h_j}c_n\le n d_n(Q).
\]

Put \(v=h-g\). Its positive and negative parts both have sum \(d/2\), since
\(\sum_jv_j=0\). At every point of the segment between \(g\) and \(h\), all
partial derivatives lie in the interval \([0,n d_n(Q)]\). Hence

\[
|v\cdot\nabla c_n|\le\frac d2 n d_n(Q),\qquad
|c_n(h)-c_n(g)|\le\frac d2 n d_n(Q).
\]

Multiply by \(R^{2n+1}\) and sum. Entire convergence justifies the sum, and
\(R f_Q'(R)-f_Q(R)=2\sum_{n\ge0}n d_n(Q)R^{2n+1}\), proving the claim.
The same argument applies to the closed simplex and needs no positive minimum
weight.

### A vanishing tap and discontinuous order

Take the two diagonal channels \((q,r)=(1/4,1/4)\) and \((3/4,3/4)\), with
weights \(1-\varepsilon\) and \(\varepsilon\), respectively. For
\(0\le\varepsilon\le1\), write the resulting function as \(F_\varepsilon\).
The quantitative bound gives

\[
\sup_{|z|\le R}|F_\varepsilon(z)-f_{1/4}(z)|
\le\frac{\varepsilon}{2}\{R f_{3/4}'(R)-f_{3/4}(R)\}.
\]

Thus convergence to \(f_{1/4}\) is uniform on every fixed disk, at an explicit
linear rate in \(\varepsilon\). Yet

\[
\rho(F_0)=\frac12,\qquad
\rho(F_\varepsilon)=\frac{\log2}{\log(4/3)}
\quad(0<\varepsilon\le1).
\]

For the faster active channel the lower constants become
\(L=1/\varepsilon\), \(C=3/\varepsilon\),
\(B=1/\varepsilon+8/3\). Its certified lower-type constant is

\[
c_-(\varepsilon)=\frac{\log2}{(4/\varepsilon+8/3)^{\log2/\log(4/3)}}>0.
\]

It tends to zero as the faster tap vanishes. These are proved growth and
compact-convergence statements. They do not determine an actual crossover
radius or leading asymptotic constant.

## 4. Computational contract and limitations

`checks/dilation_type.py` uses exact `fractions.Fraction` arithmetic for its
finite assertions. It checks the algebraic fixed-width and interval-propagation
conditions for rational scales and weights, the positive homogeneous
weight-polynomial majorant, derivative bounds on a normalized simplex, the
improved total-variation coefficient bound, and a distinct ordered-tree
evaluation against the recurrence. Scalar examples and the explicit real type
constants are displayed at high precision separately from exact assertions.

The finite checks do not prove a universal analytic theorem, normal convergence,
or historical novelty. Those depend on the proofs above. No numerical type-limit
fit is presented as evidence that a limit exists.

The earlier moving-width lower argument used a fixed \(\alpha<1\); it proved
orders below \(\rho\) and then recovered the order by \(\alpha\uparrow1\), but
did not establish positive lower type at \(\rho\). This is a limitation of that
argument, not a counterexample. The fixed-width comparison closes precisely
that missing implication. Any execution failure of the new finite checks is
recorded with its cause and retained run metadata rather than erased.
