# Exactly three action queries, with certified error bounds

**Komorebi P. · Reviewed reading edition · 13 November 2026**

The [normal form](normal-form.md) defines the real, 21-dimensional family
$L$ on nine determinant states. An action query chooses a known real
vector $v\in\mathbb R^9$ and receives the complete vector $Hv$ for a fixed
unknown $H\in L$. This is a classical full-vector oracle model.

## Exact recovery theorem

**Theorem.** Three fixed real probes identify every $H\in L$. Fewer
than three cannot identify every family member, even if a deterministic
strategy chooses later probes from earlier outputs. The same minimum
holds for the positive-integral relaxation $C\succeq0$ with unrestricted
one-body terms.

This theorem includes the energy shift. It does not concern recovery
from three scalar expectations, physical quantum measurement counts, or
the original integral decomposition.

### Why two probes cannot suffice

At most two probes impose at most 18 real linear constraints on 21
independent coefficients. Fix the probes selected along an adaptive
strategy's path at one operator $H$. A nonzero family perturbation
$\Delta H$ annihilates both probes. For sufficiently small nonzero $t$,
$H+t\Delta H$ produces the same first output, hence the same second
probe, and then the same second output. The strategy cannot distinguish
the two operators.

For the positive-integral relaxation, start at $C\succ0$. Positivity is
preserved by a sufficiently small perturbation, so the indistinguishable
pair remains admissible. This interior argument does not automatically
apply to the smaller, uncharacterized set of Coulomb-realizable tensors.

### The fixed three-probe design

Use the determinant order in the normal-form note and the columns of

$$
V=\begin{pmatrix}
-1&0&0\\0&1&0\\0&0&1\\-1&0&0\\0&0&1\\0&-1&0\\
1&0&0\\0&1&0\\0&0&1
\end{pmatrix},\qquad V^{\mathsf T}V=3I_3.
$$

For a text alternative, the following table lists each entry directly.

| Determinant row | Probe 1 | Probe 2 | Probe 3 |
|---|---|---|---|
| 0 | −1 | 0 | 0 |
| 1 | 0 | 1 | 0 |
| 2 | 0 | 0 | 1 |
| 3 | −1 | 0 | 0 |
| 4 | 0 | 0 | 1 |
| 5 | 0 | −1 | 0 |
| 6 | 1 | 0 | 0 |
| 7 | 0 | 1 | 0 |
| 8 | 0 | 0 | 1 |

Each probe has three signed unit entries and norm $\sqrt3$. The columns
are fixed; an input cache must use exactly this row and column order.

Let $D_a(X)=[T_a,X]$. The 21 normal-form basis operators consist of
$I_9$, the five $D_a$, and the products indexed lexicographically by
$a\le b$: $D_a^2$ when $a=b$, and $D_aD_b+D_bD_a$ otherwise.
Transform them to determinant coordinates and call them $H_k$.

Let $M$ have column $\operatorname{vec}_r(H_kV)$. Listing an observed
9-by-3 cache by rows gives observation index $3i+j$, where determinant
row $i$ and probe column $j$ are numbered from zero. Define

$$
G_{kl}=\langle H_k,H_l\rangle_F,\qquad B=M^{\mathsf T}M.
$$

Here $B$ is the 21-by-21 action Gram matrix; it is distinct from the
3-by-3 one-body parameter $K$ in the normal form. The code calls this
Gram matrix `model["K"]`.

The selected minor uses zero-based observation rows
$0,1,\ldots,18,22,23$ and all 21 columns. Its exact determinant is
$-2054739197952$. In addition, the rational factorization of $20B-G$
has zero reconstruction residual and strictly positive LDL pivots.
Thus $M$ has full column rank. These certificates concern explicit
integer matrices and prove sufficiency for every real coefficient vector.
The finite numerical search used to choose the probes is not used as a
rank proof.

## Stability and normalization

Since $20B-G\succ0$ and $V^{\mathsf T}V=3I_3$,

$$
\frac{\|H\|_F}{\sqrt{20}}\le\|HV\|_F\le\sqrt3\|H\|_F,
\qquad H\in L.
$$

The upper bound follows from $VV^{\mathsf T}\preceq3I_9$. The lower
bound follows by writing $H=\sum_k\theta_kH_k$ and comparing
$\theta^{\mathsf T}G\theta$ with $\theta^{\mathsf T}B\theta$.

| Probe convention | Probe norm | Sufficient inverse-noise constant |
|---|---|---|
| Raw columns of $V$ | $\sqrt3$ | $\sqrt{20}$ |
| Unit columns of $Q=V/\sqrt3$ | 1 | $\sqrt{60}$ |

The condition number is at most $\sqrt{60}$. These are sufficient
bounds, not claims of sharp constants or globally optimal probe design.
Scaling the same observations from $V$ to $Q$ scales their aggregate
error cap by $1/\sqrt3$; independently supplied caps cannot be compared
without fixing that convention.

## Least squares, consistency and boundary cases

For a real observed cache $Y$, compute

$$
\widehat\theta=B^{-1}M^{\mathsf T}\operatorname{vec}_r(Y),
\qquad \widehat H=\sum_k\widehat\theta_kH_k,
\qquad d=\|Y-\widehat HV\|_F.
$$

Suppose the true family member satisfies the aggregate raw error cap
$\|Y-HV\|_F\le\epsilon$. The residual is orthogonal to the action
range, so

$$
\|Y-HV\|_F^2=d^2+\|(H-\widehat H)V\|_F^2.
$$

Therefore the full linear family is consistent if and only if
$d\le\epsilon$, and every compatible operator obeys

$$
\|H-\widehat H\|_F\le r_H,
\qquad r_H=\sqrt{20(\epsilon^2-d^2)}.
$$

If $d>\epsilon$, no such operator exists and the decoder returns no
response enclosure. If $d=\epsilon$, the compatible set is the singleton
$\{\widehat H\}$. In particular, noiseless consistent data recover the
operator exactly. Separate column bounds $\epsilon_j$ may be combined
as $\epsilon^2=\sum_j\epsilon_j^2$; that gives an outer enclosure of
the separate-ball problem.

The displayed $r_H$ is an upper bound on the operator uncertainty radius.
It is not asserted to be the exact minimax radius. A small residual alone
does not establish either the error cap or membership of the true operator
in $L$.

## Positivity: existence and an all-compatible guarantee

The normal-form estimate has a matrix $\widehat C$. The coefficient bound
gives $\|C-\widehat C\|_2\le r_H/4$. Hence

$$
\widehat C-\frac{r_H}{4}I_5\succeq0
$$

is sufficient for **every** compatible operator to have a positive-integral
representative. Failure of this sufficient test does not settle that
all-compatible question, and it does not imply infeasibility.

| Case | What is established |
|---|---|
| $d>\epsilon$ | The full linear family, and therefore its positive subclass, is infeasible. |
| $d\le\epsilon$ and $\widehat C\succeq0$ | A positive-integral solution exists: the estimate itself is compatible. |
| $d=\epsilon$ and $\widehat C$ is not positive semidefinite | The compatible singleton has no positive-integral representative. |
| An estimate that is not positive semidefinite, with nonzero remaining uncertainty | Feasibility is not decided by this decoder alone. |
| The sufficient margin above passes | Every compatible operator has a positive-integral representative. |

For example, $Y=0$ and $\epsilon>0$ give a feasible estimate
$\widehat C=0$, although the sufficient all-compatible margin fails.
This corrects an overbroad sentence in the retained source note; the
original decoder already distinguishes these cases correctly.

The general remaining feasibility question is to find $\theta$ such that
$C(\theta)\succeq0$ and
$\|M\theta-\operatorname{vec}_r(Y)\|_2\le\epsilon$. This is a finite
convex feasibility problem. The present decoder does not certify a
floating-point cone solver's answer; it reports `null` when its own
exact tests do not decide the question.

## Response disk and density of states

Let $z=E+i\eta$ with $E$ real and $\eta>0$. For real source vectors,
assume $\|b-\widehat b\|\le\delta$ and define

$$
g=b^{\mathsf T}(zI-H)^{-1}b,
\qquad \widehat g=\widehat b^{\mathsf T}(zI-\widehat H)^{-1}\widehat b.
$$

Real symmetry gives $\|(zI-H)^{-1}\|_2\le1/\eta$, and the resolvent
identity gives an operator-change bound $r_H/\eta^2$. Expanding the
source error $e=b-\widehat b$ adds at most
$(2\|\widehat b\|\|e\|+\|e\|^2)/\eta$. Thus

$$
|g-\widehat g|\le R_g,
\qquad
R_g=\frac{\|\widehat b\|^2r_H}{\eta^2}
+\frac{\delta(2\|\widehat b\|+\delta)}{\eta}.
$$

No global spectral interval is required for this inequality. The least-squares
estimate may lie outside an optional physical subclass and still gives a
valid Hermitian resolvent center under these assumptions.

For a normalized source, the broadened source-resolved density of states is
$\rho_b(E;\eta)=-\operatorname{Im}(g)/\pi$. We call
$\ell_b=\pi\rho_b=-\operatorname{Im}(g)$ the **pi-scaled** quantity.
The disk gives an interval of half-width $R_g$ for $\ell_b$, or
$R_g/\pi$ for $\rho_b$. It is not the total density of states obtained
by tracing over all sources.

If $\widehat b=0$, the source term becomes $\delta^2/\eta$; if also
$\delta=0$, the response is zero regardless of the Hamiltonian. The
three-query lower bound concerns recovery of every operator, not the
cost of every individual observable. The theorem excludes $\eta=0$.

With dimensionless state vectors and Hamiltonian energies in Hartree,
$Y$, $\epsilon$, $d$ and $r_H$ have energy units; $g$, $R_g$ and
$\rho_b$ have inverse-energy units. The source error $\delta$ is
dimensionless.

[The exact comparison](spin-comparison.md) illustrates the additional
information supplied by the model. [The full-model bridge](model-error.md)
separates numerical error from physical truncation and source errors.
