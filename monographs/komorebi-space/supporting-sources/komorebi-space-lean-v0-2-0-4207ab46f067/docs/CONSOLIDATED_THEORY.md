# Komorebi Space Theory
## Consolidated formal core, v0.2.0

**Author:** Komorebi P.  
**Status:** A machine-checked core with an explicit extension boundary.  
**Conventions:** In equations, juxtaposition is ordinary right-to-left composition. In Lean, `f ≫ g` means first `f`, then `g`. Bonding maps point from finer to coarser resolution. All size and universe restrictions are those in the source declarations.

This document replaces the earlier fifty-section outline as the definition of the **checked core**. The full outline is retained as a status ledger in `OUTLINE_STATUS.md`. The core does not identify pro-objects, stacks, homotopy limits, and metric completions with one another. Those are different constructions requiring different hypotheses.

## 1. Resolution towers

Let \(\mathcal C\) be a category. Define

\[
X_\bullet=(X_n,\rho^X_n)_{n\geq0},\qquad
\rho^X_n:X_{n+1}\longrightarrow X_n.
\]

For towers \(X_\bullet,Y_\bullet\), a candidate transport is

\[
f=(f_n)_{n\geq0},\qquad f_n:X_n\longrightarrow Y_n.
\]

Define

\[
\operatorname{Exact}(f)
\iff
\forall n,\quad \rho^Y_nf_{n+1}=f_n\rho^X_n.
\tag{1.1}
\]

Identity and composition are levelwise:

\[
(1_X)_n=1_{X_n},\qquad(gf)_n=g_nf_n.
\]

### Theorem 1. Exact core

\[
\operatorname{Exact}(1_X),\qquad
\operatorname{Exact}(f)\land\operatorname{Exact}(g)
\Longrightarrow\operatorname{Exact}(gf).
\tag{1.2}
\]

Together with associativity and identities, this gives an actual category of towers and exact levelwise transports.

**Lean:** `Tower.PreHom.exact_id`, `Tower.PreHom.exact_comp`, the `Category (Tower C)` instance in `Towers.lean`.

**Boundary.** This is a fixed-schedule category. It has not been identified with \(\operatorname{Pro}(\mathcal C)\). That would require a reindexing and eventual-equality construction, followed by a comparison theorem.

## 2. The actual tower differential

Assume \(\mathcal C\) is preadditive. Set

\[
E(X,Y)=\prod_{n\geq0}\operatorname{Hom}_{\mathcal C}(X_n,Y_n),
\qquad
R(X,Y)=\prod_{n\geq0}\operatorname{Hom}_{\mathcal C}(X_{n+1},Y_n).
\]

The compatibility differential is the additive homomorphism

\[
\partial_{X,Y}:E(X,Y)\longrightarrow R(X,Y),
\qquad
(\partial f)_n=\rho^Y_nf_{n+1}-f_n\rho^X_n.
\tag{2.1}
\]

Consequently,

\[
\boxed{\operatorname{Exact}(f)\iff\partial f=0.}
\tag{2.2}
\]

For composable candidate transports,

\[
\boxed{
\partial(gf)_n=(\partial g)_nf_{n+1}+g_n(\partial f)_n.
}
\tag{2.3}
\]

This is an exact algebraic identity, not a bound. There is no additional mixed-error term in this setting.

**Lean:** `TowerCorrection.differential`, `TowerCorrection.exact_iff_differential_zero`, `Tower.PreHom.defect_comp`.

### Diagnostic: unrestricted repair is trivial

\[
\partial(f-f)=0.
\]

More generally, for any additive \(d:E\to R\),

\[
\forall f\in E,\quad\exists a\in E:\ d(f)-d(a)=0.
\]

Taking \(a=f\) proves the statement. Thus residual cancellation alone says nothing about retaining the mathematical object or observable of interest.

**Lean:** `CorrectionProblem.unrestricted_correction`, `Tower.PreHom.exact_zero`.

## 3. Semantics-preserving corrections

Let \(E,R,S\) be abelian groups and

\[
d:E\longrightarrow R,\qquad p:E\longrightarrow S
\]

be additive homomorphisms. Here \(d\) records residual, while \(p\) records the semantic information that must survive correction.

Admissible corrections are

\[
A_p=\ker p.
\]

Define the boundary subgroup and obstruction quotient by

\[
B_{d,p}=d(\ker p)\leq R,
\qquad
\mathcal Q_{d,p}=R/B_{d,p},
\qquad
\mathfrak o_{d,p}(f)=[d(f)].
\tag{3.1}
\]

### Theorem 2. Constrained flattening

\[
\boxed{
\mathfrak o_{d,p}(f)=0
\iff
\exists a\in E:\ p(a)=0,\ d(a)=d(f)
\iff
\exists g\in E:\ d(g)=0,\ p(g)=p(f).
}
\tag{3.2}
\]

The forward construction is \(g=f-a\). The reverse construction is \(a=f-g\).

Furthermore,

\[
p(a)=0\Longrightarrow
\mathfrak o_{d,p}(f-a)=\mathfrak o_{d,p}(f).
\tag{3.3}
\]

**Lean:** `CorrectionProblem.obstruction_zero_iff`, `CorrectionProblem.flatten_iff`, `CorrectionProblem.obstruction_invariant`.

### Theorem 3. Concrete tower repair criterion

For the actual differential \(\partial_{X,Y}\) and any additive semantic observable \(p:E(X,Y)\to S\),

\[
\boxed{
[\partial f]=0\text{ in }R(X,Y)/\partial(\ker p)
\iff
\exists g:X_\bullet\longrightarrow Y_\bullet\text{ exact},\quad p(g)=p(f).
}
\tag{3.4}
\]

The right-hand side is a bundled exact tower morphism, not an untyped promise of a global map.

**Lean:** `TowerCorrection.obstruction_zero_iff_exact`, `TowerCorrection.obstruction_zero_iff_exactHom`.

### Theorem 4. Obstruction certificate

Let \(L:R\to D\) be additive. If

\[
\forall a\in\ker p,\quad L(d(a))=0,
\qquad L(d(f))\ne0,
\]

then

\[
\mathfrak o_{d,p}(f)\ne0.
\tag{3.5}
\]

**Lean:** `CorrectionProblem.nonzero_certificate`.

A nonempty obstructed model is checked with \(E=R=S=\mathbb Z\), \(d=p=\operatorname{id}\), and \(f=1\).

**Lean:** `CorrectionProblem.rigid_one_obstructed`.

## 4. Square defects and pasting

In a preadditive category, for

\[
\begin{array}{ccc}
 A&\xrightarrow{f}&B\\
 u\downarrow&&\downarrow v\\
 A'&\xrightarrow{f'}&B',
\end{array}
\]

set

\[
\Omega(f,f';u,v)=vf-f'u\in\operatorname{Hom}(A,B').
\tag{4.1}
\]

For a horizontal pair of squares,

\[
\boxed{\Omega_{\mathrm{outer}}=\Omega_2 f+g'\Omega_1.}
\tag{4.2}
\]

For a vertical pair, with lower vertical arrows \(u',v'\),

\[
\boxed{\Omega_{\mathrm{outer}}=v'\Omega_1+\Omega_2u.}
\tag{4.3}
\]

Zero defects paste to zero defects in either direction.

**Lean:** `Squares.lean`.

The word “curvature” is only an interpretation of this defect. A connection, a nonabelian holonomy theory, and Bianchi identities do not follow without additional structure.

## 5. Quantitative pasting and transported Stokes

In a normed ring,

\[
\|\Omega_{\mathrm{outer}}\|
\leq
\|\Omega_2\|\,\|f\|+\|g'\|\,\|\Omega_1\|.
\tag{5.1}
\]

If \(\|f\|,\|g'\|\leq1\), then

\[
\|\Omega_{\mathrm{outer}}\|\leq\|\Omega_1\|+\|\Omega_2\|.
\tag{5.2}
\]

Let a finite sequence of path swaps have a certified difference

\[
T_{k+1}-T_k=A_k\Omega_kB_k.
\]

Then

\[
\boxed{T_N-T_0=\sum_{k=0}^{N-1}A_k\Omega_kB_k.}
\tag{5.3}
\]

If \(\|A_k\|,\|B_k\|\leq1\),

\[
\boxed{\|T_N-T_0\|\leq\sum_{k=0}^{N-1}\|\Omega_k\|.}
\tag{5.4}
\]

The transporting factors \(A_k,B_k\) are essential. Arbitrary defects in different Hom spaces cannot simply be added.

**Lean:** `NormedDefects.horizontal_norm`, `horizontal_contractive`, `transported_telescope`, `transported_stokes_bound`.

**Boundary.** The package verifies this theorem for a supplied sequence of certified swaps. It does not construct arbitrary cubical surfaces or prove a topological Stokes theorem for an unspecified complex.

## 6. Exact inverse-limit realization

A concrete resolution has types \(X_n\) and restriction maps

\[
\rho^X_{j,i}:X_j\to X_i\quad(i\leq j),
\qquad
\rho^X_{i,i}=1,
\qquad
\rho^X_{j,i}\rho^X_{k,j}=\rho^X_{k,i}.
\]

Define the limit **as a type of coherent coordinates**:

\[
\boxed{
\operatorname{Lim}(X)=
\left\{(x_n)\in\prod_nX_n:
\rho^X_{j,i}(x_j)=x_i\text{ for all }i\leq j\right\}.
}
\tag{6.1}
\]

For an exact family \(f_n:X_n\to Y_n\), define

\[
\operatorname{Lim}(f)(x)_n=f_n(x_n).
\tag{6.2}
\]

### Theorem 5. Realization and universal property

This produces an actual function

\[
\operatorname{Lim}(f):\operatorname{Lim}(X)\to\operatorname{Lim}(Y),
\]

preserves identities and composition, and is uniquely specified by (6.2).

For every compatible cone \(c_n:S\to X_n\),

\[
\exists!\,\ell:S\to\operatorname{Lim}(X),
\qquad \operatorname{pr}_n\ell=c_n.
\tag{6.3}
\]

**Lean:** `Resolution.Map.onLimit`, `onLimit_comp`, `onLimit_unique`, `Resolution.Cone.exists_unique_lift`.

To realize in already named objects \(S,T\), explicit equivalences

\[
e_X:S\simeq\operatorname{Lim}(X),\qquad e_Y:T\simeq\operatorname{Lim}(Y)
\]

are supplied. The resulting map is

\[
e_Y^{-1}\operatorname{Lim}(f)e_X:S\to T.
\tag{6.4}
\]

**Lean:** `Resolution.realize`, `Resolution.realize_coordinate`.

## 7. Canonicity under cofinal sampling

Let \(\phi:\mathbb N\to\mathbb N\) be nondecreasing and unbounded:

\[
\forall n\,\exists j:\ n\leq\phi(j).
\]

Define \((X\circ\phi)_j=X_{\phi(j)}\). Sampling yields

\[
S_\phi:\operatorname{Lim}(X)\to\operatorname{Lim}(X\circ\phi),
\qquad S_\phi(x)_j=x_{\phi(j)}.
\]

### Theorem 6. Exact cofinal invariance

\[
\boxed{\operatorname{Lim}(X)\simeq\operatorname{Lim}(X\circ\phi).}
\tag{7.1}
\]

The inverse recovers coordinate \(n\) by choosing \(j\) with \(n\leq\phi(j)\) and restricting \(y_j\) to level \(n\). The result is proved independent of that choice.

**Lean:** `Resolution.recoveredCoordinate_eq`, `extend_sample`, `sample_extend`, `cofinalEquiv`.

### Theorem 7. Quantitative cofinal invariance, restricted form

If \(\eta_n\geq0\) and \(\eta\) is nonincreasing, then

\[
\boxed{\eta_n\to0\iff\eta_{\phi(n)}\to0.}
\tag{7.2}
\]

**Lean:** `Profiles.cofinal_vanish_iff`.

Without monotonicity, define

\[
a_n=\begin{cases}0&n\text{ even},\\1&n\text{ odd}.\end{cases}
\]

Then

\[
a_{2n}\to0,\qquad a_n\not\to0.
\tag{7.3}
\]

Both assertions and cofinality of \(2n\) are checked. No general invariance of residual norms, rates, or cohomology is asserted.

**Lean:** `Profiles.sampled_alternating_vanishes`, `Profiles.alternating_does_not_vanish`.

## 8. Additive cohomology, when a complex is supplied

Let

\[
C^1\xrightarrow{\delta_1}C^2\xrightarrow{\delta_2}C^3,
\qquad \delta_2\delta_1=0
\]

be an explicit complex of abelian groups. Put

\[
Z^2=\ker\delta_2,
\qquad B^2=\operatorname{im}(C^1\xrightarrow{\delta_1}Z^2),
\qquad H^2=Z^2/B^2.
\]

### Theorem 8. Cohomological correction

For \(\Omega\in Z^2\),

\[
\boxed{[\Omega]=0\iff\exists\alpha:\Omega-\delta_1\alpha=0.}
\tag{8.1}
\]

The class is unchanged by such correction. In particular,

\[
[\delta_1\alpha]=0.
\tag{8.2}
\]

Thus an obstruction defined globally as \(\delta\tau\) is **already a coboundary**. It cannot serve as a nonzero intrinsic cohomology class without a restriction on corrections, local rather than global data, or another additional structure.

**Lean:** `ObstructionComplex.flatten_iff`, `correction_invariant`, `primary_defect_class_zero`, `obstruction_certificate`.

### Differential sign convention

For additive endomorphisms \(d,e\) satisfying

\[
d^2=e^2=0,\qquad de+ed=0,
\]

we prove

\[
\boxed{(d+e)^2=0.}
\tag{8.3}
\]

A commuting bicomplex instead needs the appropriate degree sign. The earlier outline mixed these conventions; it is not retained.

**Lean:** `Differential.anticommuting_sum_square_zero`.

## 9. Obstruction magnitude and closedness

For an additive subgroup \(B\) of a normed abelian group \(R\), define

\[
\eta_B(\Omega)=\inf_{b\in B}\|\Omega-b\|.
\tag{9.1}
\]

Then

\[
0\leq\eta_B(\Omega)\leq\|\Omega-b\|\quad(b\in B),
\]

and

\[
\boxed{\eta_B(\Omega)=0\iff\Omega\in\overline B.}
\tag{9.2}
\]

Only if \(B\) is closed may \(\overline B\) be replaced by \(B\).

**Lean:** `ObstructionFloor.lower_bound`, `zero_iff_closure`, `zero_iff_mem_of_closed`.

### Theorem 9. Persistent obstruction

If \(a_n\in B_n\) and for some \(c>0\), eventually

\[
c\leq\eta_{B_n}(\Omega_n),
\]

then

\[
\boxed{\|\Omega_n-a_n\|\not\longrightarrow0.}
\tag{9.3}
\]

**Lean:** `ObstructionFloor.persistent_obstruction`.

## 10. Completion and exactification

Let \((M,d_M)\) be a complete pseudometric space and

\[
\omega:M\to\mathbb R_{\geq0}
\]

be lower semicontinuous. In Lean, \(\omega\) is real-valued and nonnegativity is an explicit hypothesis.

### Theorem 10. Summable exactification

Suppose

\[
d_M(f_n,f_{n+1})\leq b_n,\qquad
\sum_nb_n\text{ converges},\qquad
\omega(f_n)\to0.
\]

Then

\[
\boxed{
\exists f_\infty:\quad
f_n\to f_\infty,\quad
\omega(f_\infty)=0,\quad
 d_M(f_n,f_\infty)\leq\sum_{k=0}^{\infty}b_{n+k}.
}
\tag{10.1}
\]

**Lean:** `Exactification.summable_exactification`.

### Theorem 11. Variable cancellation rates

Let \(q_n,C_n\geq0\),

\[
Q_0=1,\qquad Q_{n+1}=q_nQ_n,
\]

and assume

\[
\omega(f_{n+1})\leq q_n\omega(f_n),\qquad
 d_M(f_n,f_{n+1})\leq C_n\omega(f_n),
\]

\[
Q_n\to0,\qquad \sum_nC_nQ_n<\infty.
\]

Then an exact limit exists and

\[
d_M(f_n,f_\infty)
\leq\omega(f_0)\sum_{k=0}^{\infty}C_{n+k}Q_{n+k}.
\tag{10.2}
\]

**Lean:** `Exactification.variable_exactification`.

### Theorem 12. Geometric exactification

For \(0\leq q<1\), \(C\geq0\),

\[
\omega(f_{n+1})\leq q\omega(f_n),\qquad
 d_M(f_n,f_{n+1})\leq C\omega(f_n),
\]

we obtain

\[
\boxed{
\exists f_\infty:\quad f_n\to f_\infty,\quad\omega(f_\infty)=0,\quad
 d_M(f_n,f_\infty)\leq\frac{C}{1-q}\omega(f_n).
}
\tag{10.3}
\]

**Lean:** `Exactification.geometric_exactification`.

These are universal conditional theorems. They do not construct a cancellation algorithm satisfying their hypotheses for every input.

## 11. Semantic exactification in a complete linear model

Let \(E\) be a complete normed space over a nontrivially normed field \(\mathbb K\), and let \(R,S\) be normed \(\mathbb K\)-spaces. Take continuous linear maps

\[
d:E\to R,\qquad p:E\to S.
\]

Suppose \(p(f_n)=p(f_0)\) for every \(n\).

### Theorem 13. Exactification preserving meaning

If

\[
\|d(f_{n+1})\|\leq q\|d(f_n)\|,\qquad
\|f_{n+1}-f_n\|\leq C\|d(f_n)\|,
\qquad0\leq q<1,\quad C\geq0,
\]

then

\[
\boxed{
\begin{gathered}
\exists f_\infty\in E,\qquad f_n\to f_\infty,\\
d(f_\infty)=0,\qquad p(f_\infty)=p(f_0),\\
\|f_n-f_\infty\|\leq\frac{C}{1-q}\|d(f_n)\|.
\end{gathered}
}
\tag{11.1}
\]

The corresponding summable-movement theorem is also proved. Consequently,

\[
\boxed{[d(f_0)]=0\quad\text{in }R/d(\ker p).}
\tag{11.2}
\]

**Lean:** `LinearExactification.geometric_semantic_exactification`, `summable_semantic_exactification`, `controlled_obstruction_vanishes`.

This joins the obstruction and convergence sectors. For a particular infinite-dimensional tower representation, one must still supply its complete normed candidate space and prove continuity of its differential and semantics.

## 12. Path independence, with its missing hypothesis restored

In a metric space, suppose

\[
f_n\to x,\quad g_n\to y,\quad d_M(f_n,g_n)\leq K_n,\quad K_n\to0.
\]

Then

\[
\boxed{x=y.}
\tag{12.1}
\]

**Lean:** `PathIndependence.limits_equal_of_budget`.

Zero residual alone does not imply uniqueness. A vanishing pairwise path-comparison budget is required. In a merely pseudometric space one obtains zero distance, not necessarily equality.

## 13. Optional transport-cost geometry

For a category \(\mathcal D\), supply a cost

\[
w(f)\in[0,\infty],\qquad w(1_A)=0,\qquad w(gf)\leq w(f)+w(g).
\]

Define

\[
d_w(A,B)=\inf_{f:A\to B}w(f).
\]

Then

\[
d_w(A,A)=0,\qquad d_w(A,C)\leq d_w(A,B)+d_w(B,C).
\tag{13.1}
\]

The symmetrization

\[
d_w^{\mathrm{sym}}(A,B)=\max\{d_w(A,B),d_w(B,A)\}
\]

is symmetric and satisfies the triangle inequality. Zero symmetric distance defines an equivalence relation.

**Lean:** `TransportCost.distance_triangle`, `symDistance_triangle`, `zeroDistanceSetoid`.

If zero arrows exist and every zero arrow has zero cost, then

\[
\boxed{d_w(A,B)=0\quad\text{for every }A,B.}
\tag{13.2}
\]

**Lean:** `TransportCost.collapse_of_zero_arrows`.

Thus compatibility residual, information fidelity, and transport cost are three different notions. This package does not assert that every zero-distance class is an isomorphism class, or that an infimum of zero is attained.

## 14. Nontrivial finite obstruction model

Let

\[
G=(\mathbb Z/2\mathbb Z)^2,\qquad c(x,y)=x_2y_1.
\]

Then

\[
c(0,y)=c(x,0)=0,
\]

\[
\boxed{c(x,y)+c(x+y,z)=c(y,z)+c(x,y+z).}
\tag{14.1}
\]

Every scalar coboundary

\[
(\delta a)(x,y)=a(x)+a(y)-a(x+y)
\]

is symmetric, whereas \(c\) is not. Therefore

\[
\boxed{\neg\exists a:G\to\mathbb Z/2\mathbb Z,\quad c=\delta a.}
\tag{14.2}
\]

**Lean:** `ProjectiveExample.cocycle`, `no_scalar_flattening`.

This is an exact finite cocycle model. It is not a formal identification with a Galois group, a proof of a Langlands correspondence, or a general nonabelian obstruction theory.

## 15. Algebraic operator-compression identity

In a ring, if \(P^2=P\) and \(QP=P\), then

\[
\boxed{(QTQ)P-P(PTP)=(Q-P)TP.}
\tag{15.1}
\]

**Lean:** `NormedDefects.compression_shell`.

The Hilbert-space theorem \(\|T-P_nTP_n\|\to0\) for compact \(T\) is not proved in this release. The checked statement is the exact algebraic shell identity with its projection hypotheses.

## 16. Original v0.1.0 boundary and v0.2.0 extension

The release proves a **resolution–transport core**, a **semantics-constrained obstruction quotient**, a **concrete inverse-limit realization**, and **controlled exactification theorems**.

It does not yet define and verify a universal stack of all mathematical representations. It does not prove general pro-category equivalence, arbitrary cofinal invariance of residual norms, nonabelian Bianchi identities, higher-obstruction towers, spectral sequences, unrestricted local-to-global descent, or a canonical grammar generated solely by an underlying object.

The checked thesis is:

\[
\boxed{
\text{actual compatibility defect}
+\text{protected semantics}
+\text{admissible corrections}
+\text{controlled convergence}
\Longrightarrow
\text{exact structure with the protected semantics unchanged},
}
\]

with each term instantiated and each hypothesis stated in its corresponding Lean theorem.


---

## 17. Banach tower and projection extension

The following extends the core rather than replacing the preceding proofs. All 14 original proof modules are unchanged. The Banach-space construction and its actual differential, the correction dynamics, and the projection/realization theorems are new in v0.2.0.

## A. Actual complete transport spaces

Let \(\mathbb K\) be a nontrivially normed field. Let
\[
X_\bullet=(X_n,\rho^X_n),\qquad Y_\bullet=(Y_n,\rho^Y_n)
\]
be sequential towers of complete normed \(\mathbb K\)-spaces, with continuous linear bonding maps
\[
\rho^X_n:X_{n+1}\to X_n,\qquad \rho^Y_n:Y_{n+1}\to Y_n,
\]
and supplied finite uniform bounds
\[
\|\rho^X_n\|\le B_X,\qquad \|\rho^Y_n\|\le B_Y.
\]

Define
\[
\boxed{E_\infty(X,Y)=\ell^\infty_{n\ge0}\mathcal L_\mathbb K(X_n,Y_n)}
\]
and
\[
\boxed{R_\infty(X,Y)=\ell^\infty_{n\ge0}\mathcal L_\mathbb K(X_{n+1},Y_n).}
\]
Both are equipped with the sup norm. Completeness of the candidate space is obtained from the existing completeness instances for the operator spaces and their bounded product. It is not introduced as a new axiom.

The actual compatibility differential is
\[
(\partial f)_n=\rho^Y_nf_{n+1}-f_n\rho^X_n.
\]
The component estimate is
\[
\begin{aligned}
\|(\partial f)_n\|
&\le \|\rho^Y_n\|\,\|f_{n+1}\|+\|f_n\|\,\|\rho^X_n\|\\
&\le (B_X+B_Y)\|f\|_\infty.
\end{aligned}
\]
Consequently the family is bounded, the differential is continuous linear, and
\[
\boxed{\|\partial\|\le B_X+B_Y.}
\tag{A1}
\]

The level observable
\[
p_k:E_\infty(X,Y)\to\mathcal L_\mathbb K(X_k,Y_k),\qquad p_k(f)=f_k
\]
is continuous linear with
\[
\|p_k(f)\|\le\|f\|_\infty.
\tag{A2}
\]
Thus keeping \(p_k\) fixed preserves a complete finite-resolution operator, not merely its norm or a user-supplied truth flag.

**Lean:** `BanachTower.candidates_complete`, `rawDefect_mem`, `differential`, `differential_opNorm`, `evaluation`, `evaluation_bound`.

## B. Agreement with the algebraic tower core

Forget topology and norms using the category of modules:
\[
\mathsf U(X_\bullet)_n=X_n,\qquad\mathsf U(\rho^X_n)=\rho^X_n.
\]
For the same family \(f\), Lean proves
\[
\boxed{
\partial f=0
\iff
\forall n,\ \rho^Y_nf_{n+1}=f_n\rho^X_n
\iff
\mathsf U(f)\text{ is an exact tower morphism}.
}
\tag{B1}
\]
The new normed definition and the existing `Tower.PreHom.Exact` therefore refer to the same bonding maps and candidate operators.

**Lean:** `BanachTower.exact_iff_differential_zero`, `exact_iff_algebraic`, `exactHom`.

This is a fixed sequential schedule. It does not prove an equivalence with the entire pro-category or identify arbitrary Banach spaces with inverse limits of finite-dimensional truncations.

## C. Constructed repair dynamics

For a complete normed candidate space \(E\), let
\[
d:E\to R,\qquad p:E\to S,\qquad A:R\to E
\]
be continuous linear maps. The map \(A\) is a correction operator. Assume
\[
pA=0,
\tag{C1}
\]
and, for some \(0\le q<1\),
\[
\boxed{\|df-dA(df)\|\le q\|df\|\qquad(f\in E).}
\tag{C2}
\]
The contraction hypothesis is imposed only on residuals of actual candidates. It need not hold on all of \(R\).

Construct, rather than postulate, the sequence
\[
f^{(0)}=f,\qquad f^{(m+1)}=f^{(m)}-A(df^{(m)}).
\tag{C3}
\]
Then
\[
p(f^{(m)})=p(f),\qquad
\|df^{(m+1)}\|\le q\|df^{(m)}\|,
\]
\[
\operatorname{dist}(f^{(m)},f^{(m+1)})
\le\|A\|\,\|df^{(m)}\|.
\tag{C4}
\]
The previous geometric exactification theorem now applies with the derived movement constant \(C=\|A\|\). It gives
\[
\boxed{
\begin{gathered}
f^{(m)}\to P_Af,\qquad d(P_Af)=0,\qquad p(P_Af)=p(f),\\
\operatorname{dist}(f^{(m)},P_Af)
\le\frac{\|A\|}{1-q}\,\|df^{(m)}\|.
\end{gathered}}
\tag{C5}
\]

**Lean:** `RepairDynamics.exactification_from_correction_operator`, `repair_exists`.

The theorem supplies an iteration and its limit **from** a suitable correction operator. It does not supply such an operator for every tower or solve every protected residual problem.

## D. The limit is a bounded projection

The iterates in (C3) are linear in \(f\). Uniqueness of limits gives linearity of \(P_A\). Its norm satisfies
\[
\begin{aligned}
\|P_Af\|
&\le\|f\|+\operatorname{dist}(f,P_Af)\\
&\le\left(1+\frac{\|A\|\,\|d\|}{1-q}\right)\|f\|.
\end{aligned}
\]
Thus
\[
\boxed{P_A:E\to E\text{ is continuous linear},\qquad
\|P_A\|\le1+\frac{\|A\|\,\|d\|}{1-q}.}
\tag{D1}
\]
Every exact candidate is fixed by every iterate, and hence by the limit. Therefore
\[
\boxed{P_A^2=P_A,\qquad \operatorname{im}P_A=\ker d,\qquad pP_A=p.}
\tag{D2}
\]
Every candidate has the decomposition
\[
\boxed{f=P_Af+(f-P_Af)}
\]
with
\[
d(P_Af)=0,\qquad p(f-P_Af)=0,\qquad
 d(f-P_Af)=df,\qquad P_A(f-P_Af)=0.
\tag{D3}
\]
The second summand is an admissible correction carrying precisely the original residual.

**Lean:** `RepairDynamics.Scheme.projection`, `projection_bound`, `projection_idempotent`, `projection_image_iff`, `exact_residual_splitting`.

Although `limit` uses classical choice to package the existence theorem, its value is the unique limit of the specified iteration. This is a formal analytic construction, not executable floating-point code or a claimed runtime complexity bound.

## E. When the repair is canonical

For a **fixed** correction scheme, the sequence and its limit are determined. Independence of the scheme needs more.

Assume the observable separates exact candidates:
\[
\boxed{da=db=0\ \land\ p(a)=p(b)\ \Longrightarrow\ a=b.}
\tag{E1}
\]
Then any two schemes satisfying (C1)–(C2) have the same projection:
\[
P_A=P_{A'}.
\tag{E2}
\]
There is a unique exact candidate with protected semantics \(p(f)\).

**Lean:** `RepairDynamics.unique_repair`, `RepairDynamics.Scheme.scheme_independent`, `BanachTower.unique_repair_of_separation`.

Without separation, even a nonzero protected semantic coordinate does not ensure uniqueness. In
\[
E=\mathbb R^3,\qquad d(a,b,c)=c,\qquad p(a,b,c)=a,
\]
both \((1,0,0)\) and \((1,1,0)\) are exact and have the same protected value. Their inequality is checked.

**Lean:** `RepairExamples.semantics_alone_not_unique`.

## F. Specialization to actual tower transports

Use
\[
E=E_\infty(X,Y),\quad R=R_\infty(X,Y),\quad d=\partial,\quad p=p_k.
\]
A scheme now has the explicit obligations
\[
(A r)_k=0,
\qquad
\|\partial f-\partial A(\partial f)\|_\infty\le q\|\partial f\|_\infty.
\]
Its repaired map \(g=P_Af\) is an actual exact tower transport, preserves \(g_k=f_k\), and satisfies the uniform error estimate (C5). At every level \(n\),
\[
\|f^{(m)}_n-g_n\|\le\|f^{(m)}-g\|_\infty.
\tag{F1}
\]
The constructed tower projector satisfies
\[
\boxed{\|P_A\|\le1+\frac{\|A\|}{1-q}(B_X+B_Y).}
\tag{F2}
\]

**Lean:** `BanachTower.geometric_exactification`, `repair_by_operator`, `coordinate_dist_le`, `exactificationProjection`, `projection_exact_preserving_idempotent`, `projection_stability_bound`.

Define the realized point types
\[
\operatorname{Lim}X=\{(x_n):\rho^X_nx_{n+1}=x_n\text{ for all }n\},
\]
and analogously for \(Y\). Exactness constructs
\[
\boxed{F:\operatorname{Lim}X\to\operatorname{Lim}Y,\qquad F(x)_n=g_nx_n.}
\tag{F3}
\]
At the protected level,
\[
F(x)_k=f_kx_k.
\]
This map is unique **given its coordinate maps**. It is not a claim that the repaired candidate is unique without (E1), nor a claim that an unspecified original object is equivalent to this inverse limit.

**Lean:** `BanachTower.onLimit`, `onLimit_unique`, `repair_and_realize`.

## G. Two explicit models

### G1. A supplied correction operator with nonzero preserved information

For arbitrary complete normed spaces \(S,R\), take
\[
E=S\times R,\quad d(s,r)=r,\quad p(s,r)=s,\quad A(r)=(0,r).
\]
All scheme assumptions are verified with \(q=0\). The iteration reaches its exact limit in one step:
\[
(s,r)-A(d(s,r))=(s,0),\qquad P_A(s,r)=(s,0).
\]
If \(s\ne0\), the result is nonzero.

**Lean:** `RepairExamples.splitScheme`, `split_step`, `split_projection`, `split_nonzero`.

### G2. Identity bonding maps and a canonical tower repair

Let every \(X_n=E\), every \(Y_n=F\), and all bonding maps be identities. Then
\[
\operatorname{Exact}(g)\iff g_{n+1}=g_n\ (\forall n)
\iff g_n=g_0\ (\forall n).
\]
Every bounded candidate has a unique exact repair preserving level zero:
\[
\boxed{g_n=f_0\quad(n\ge0).}
\]
The coherent inverse limits are explicitly equivalent to \(E\) and \(F\), and the realized map is exactly \(f_0:E\to F\).

**Lean:** `BanachTower.constant_exact_iff`, `constant_unique_repair`, `constantPointEquiv`, `constant_realization`.

This model proves genuine canonical repair and realization. It does **not** establish a residual-proportional sup-norm error bound or exhibit a bounded contraction operator for all identity-tower candidates. Those are stronger statements than the unique-repair conclusion.

## H. Extension boundary

The original algebraic and analytic cores are now joined for uniformly bounded **sequential Banach towers on a common schedule**. The six new modules contain 60 named theorem declarations, including auxiliary lemmas. The full project has 20 modules and 156 named theorems. These counts are not novelty claims.

Not proved here: existence of a suitable correction operator for arbitrary towers, reindexed pro-morphism comparison, arbitrary cofinal norm invariance, sheaf/stack descent, higher obstruction complexes, or unrestricted arithmetic/global correspondence. The next structural task is reindexed transports with a proved eventual-equality quotient. The next analytic task is constructing correction operators in a genuinely nonconstant tower model while preserving specified semantic data.
