# Komorebi Space Theory — Banach tower extension
## v0.2.0 · Komorebi P.

The extension connects the algebraic tower differential to the analytic exactification theorem. It also constructs a repair sequence from a bounded correction operator and proves that its limit is a bounded projection. The operator and its contraction estimate remain explicit hypotheses.

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
