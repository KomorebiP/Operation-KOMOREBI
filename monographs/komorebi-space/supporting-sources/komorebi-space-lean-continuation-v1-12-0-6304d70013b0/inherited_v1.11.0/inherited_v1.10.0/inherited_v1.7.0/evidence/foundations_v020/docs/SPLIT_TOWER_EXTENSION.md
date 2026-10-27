# Komorebi Space Theory: split-tower coordinates
## v0.3.0 · Komorebi P.

This extension constructs the correction operator left as a hypothesis in v0.2.0, for sequential Banach towers with bounded target splittings and a strict propagation gap. It then derives a continuous linear coordinate system and an explicit, dimension-growing model. It does not prove a splitting or a gap for arbitrary towers.

## 1. Ambient spaces and hypotheses

Fix a nontrivially normed field \(\mathbb K\) and towers of complete normed spaces
\[
X_{n+1}\xrightarrow{\rho^X_n}X_n,
\qquad Y_{n+1}\xrightarrow{\rho^Y_n}Y_n,
\qquad n\in\mathbb N.
\]
Assume supplied finite uniform bounds
\[
\|\rho^X_n\|\le B_X,\qquad \|\rho^Y_n\|\le B_Y.
\]
The existing complete candidate and residual spaces are
\[
E=\ell^\infty_n\mathcal L_{\mathbb K}(X_n,Y_n),
\qquad R=\ell^\infty_n\mathcal L_{\mathbb K}(X_{n+1},Y_n),
\]
with the continuous linear differential
\[
\boxed{(df)_n=\rho^Y_nf_{n+1}-f_n\rho^X_n.}
\tag{1}
\]
Thus \(df=0\) is exact tower compatibility, with no replacement of the actual bonding maps by abstract residual data.

Choose continuous linear target sections
\[
s_n:Y_n\to Y_{n+1},\qquad
\rho^Y_ns_n=I_{Y_n},\qquad \|s_n\|\le S.
\]
The central quantitative hypothesis is
\[
\boxed{SB_X<1.}
\tag{2}
\]
Set
\[
\boxed{K=\frac{S}{1-SB_X}.}
\tag{3}
\]
A splitting is mathematical input, not intrinsic structure inferred from an object. Its bound and the norms are also part of the input.

**Lean data:** `BanachTower.Splitting`. The gap is an explicit argument, not an axiom or a field assuming the desired correction.

## 2. Constructed correction: a right inverse of the actual differential

For \(r\in R\), recursively define
\[
\boxed{(Ar)_0=0,\qquad
(Ar)_{n+1}=s_n\bigl(r_n+(Ar)_n\rho^X_n\bigr).}
\tag{4}
\]
All maps in (4) have domain \(X_{n+1}\) at stage \(n+1\). The recurrence preserves linearity in \(r\).

### Bound

Inductively,
\[
\begin{aligned}
\|(Ar)_{n+1}\|
&\le S\bigl(\|r\|_\infty+B_X\|(Ar)_n\|\bigr)\\
&\le S(1+B_XK)\|r\|_\infty
=K\|r\|_\infty.
\end{aligned}
\]
The base case is zero. The identity \(S(1+B_XK)=K\) uses (2). Therefore
\[
\boxed{A:R\to E\text{ is continuous linear},\qquad
\|Ar\|_\infty\le K\|r\|_\infty,\quad \|A\|\le K.}
\tag{5}
\]

### Exact right inverse

Using \(\rho^Y_ns_n=I\),
\[
\begin{aligned}
(dAr)_n
&=\rho^Y_ns_n\bigl(r_n+(Ar)_n\rho^X_n\bigr)
 -(Ar)_n\rho^X_n\\
&=r_n.
\end{aligned}
\]
Hence
\[
\boxed{dA=I_R,\qquad (Ar)_0=0.}
\tag{6}
\]
This is surjectivity onto *all bounded residual families*, not just residuals already known to equal \(df\).

**Lean:** `Splitting.rawCorrection_bound`, `correction`, `correction_bound`, `correction_opNorm`, `differential_correction`.

## 3. One-step exactification

Define
\[
\boxed{P=I_E-Ad.}
\tag{7}
\]
Equations (6) give
\[
\boxed{dP=0,\qquad P^2=P,\qquad \operatorname{im}P=\ker d,\qquad (Pf)_0=f_0.}
\tag{8}
\]
Moreover,
\[
\boxed{\|f-Pf\|_\infty\le K\|df\|_\infty.}
\tag{9}
\]
The existing iterative exactification engine has a constructed scheme with residual contraction rate zero. Its limiting projection is proved to equal (7). There is no remaining assumption that a global correction operator exists within this class.

"One step" means one application of the bounded operator \(A\). The infinite family is defined mathematically by a level recurrence. This is not a constant-time computational claim.

**Lean:** `Splitting.scheme`, `repair`, `repair_exact`, `repair_idempotent`, `repair_image_iff`, `repair_error`, `scheme_projection_eq`.

## 4. Protected observable: seed plus new output components

The initial level alone need not distinguish exact transports when target dimensions grow. Define
\[
N_n(f)=\bigl(I_{Y_{n+1}}-s_n\rho^Y_n\bigr)f_{n+1}.
\tag{10}
\]
Then
\[
\rho^Y_nN_n(f)=0,
\]
so this operator takes values in the newly exposed target kernel.

Package the initial level and all these components as
\[
\boxed{
(p_Lf)_0=f_0,\qquad (p_Lf)_{n+1}=N_n(f).
}
\tag{11}
\]
This is a continuous linear map \(p_L:E\to E\), satisfying
\[
\boxed{
\|p_L\|\le1+SB_Y,\quad p_L^2=p_L,\quad p_LA=0,\quad p_LP=p_L.
}
\tag{12}
\]
The name "semantic" refers to this specified protected mathematical observable. No claim is made that it captures every possible meaning or invariant of an arbitrary representation.

### Separation is derived

Every exact family obeys
\[
\boxed{f_{n+1}=s_nf_n\rho^X_n+N_n(f).}
\tag{13}
\]
Induction using its initial value and (13) gives
\[
\boxed{df=dg=0,\quad p_Lf=p_Lg\quad\Longrightarrow\quad f=g.}
\tag{14}
\]
Applying (14) to a difference yields the stronger injectivity statement
\[
\boxed{df=dg,\quad p_Lf=p_Lg\quad\Longrightarrow\quad f=g.}
\tag{15}
\]
Consequently
\[
\boxed{\forall f\in E,\quad\exists!g\in E:
 dg=0\ \land\ p_Lg=p_Lf.}
\tag{16}
\]
The unique \(g\) is \(Pf\). Any valid repair scheme for this *same* protected observable has the same projection. This is canonicity relative to the chosen splitting, not independence from changing the splitting, norms, schedule, or ambient doctrine.

**Lean:** `Splitting.innovation_down`, `observable`, `observable_idempotent`, `observable_correction`, `exact_reconstruction`, `exact_eq_of_observable`, `residual_observable_injective`, `unique_exact_repair`, `any_scheme_projection_eq`.

## 5. Continuous linear coordinate theorem

Let the semantic coordinate space be the normed submodule
\[
\boxed{\mathcal S_L=\{s\in E:p_Ls=s\}=\ker(p_L-I_E).}
\tag{17}
\]
The coordinate map and its inverse are explicit:
\[
\boxed{
\begin{aligned}
\Phi:E&\longrightarrow\mathcal S_L\times R,&
\Phi(f)&=(p_Lf,df),\\
\Phi^{-1}(s,r)&=Ps+Ar.
\end{aligned}}
\tag{18}
\]
Equations (6), (12), and (15) prove both inverse identities. Both maps are linear. The formalization also proves
\[
\|\Phi f\|\le
\max(1+SB_Y,B_X+B_Y)\|f\|,
\tag{19}
\]
\[
\|\Phi^{-1}(s,r)\|
\le(\|P\|+\|A\|)\|(s,r)\|.
\tag{20}
\]
Therefore the result is an actual continuous linear equivalence:
\[
\boxed{E_\infty(X,Y)\simeq_L\mathcal S_L\times R_\infty(X,Y).}
\tag{21}
\]
Here \(\simeq_L\) denotes a bounded linear isomorphism with continuous inverse, not an isometry.

In these coordinates,
\[
\boxed{
\Phi(Pf)=((\Phi f)_1,0),\qquad
\Phi(Ar)=(0,r),\qquad
f\text{ exact}\iff(\Phi f)_2=0.
}
\tag{22}
\]
Thus this class of Komorebi transport spaces has a proved separation into protected information and compatibility residual. This is a concrete analytic class, not a claim that the entire speculative stack/pro-object outline has been constructed.

**Lean:** `Splitting.semanticSpace`, `coordinateEquiv`, `coordinate_bound`, `coordinate_inverse_bound`, `coordinates`, `coordinates_repair`, `coordinates_correction`, `exact_iff_zero_residual_coordinate`.

## 6. A genuinely dimension-growing realization

Use real sup-norm spaces
\[
X_n=Y_n=\mathbb R^{n+1}.
\]
Let \(\pi_n\) delete the final coordinate and \(s_n\) append zero. Set
\[
\boxed{\rho^X_n=\tfrac12\pi_n,\qquad
\rho^Y_n=\pi_n,\qquad s_n(y)=(y,0).}
\tag{23}
\]
All dimensions, maps, bounds, and right-inverse laws are defined and checked in Lean. Here
\[
B_X=\tfrac12,\qquad B_Y=S=1,\qquad K=2.
\]
Thus every bounded candidate has an exact repair with
\[
\boxed{\|f-Pf\|_\infty\le2\|df\|_\infty.}
\tag{24}
\]
Its initial operator and every new final output row remain unchanged. For inherited output coordinates,
\[
(Pf)_{n+1}(x)_i=\tfrac12(Pf)_n(\pi_nx)_i,
\quad 0\le i\le n.
\]
For the new row,
\[
(Pf)_{n+1}(x)_{n+1}=f_{n+1}(x)_{n+1}.
\]

Take the bounded but nonexact candidate \(f_n=I_{\mathbb R^{n+1}}\). The formalization proves, for **every** \(n\) and \(0\le i\le n\),
\[
\boxed{(PI)_n(x)_i=2^{-(n-i)}x_i.}
\tag{25}
\]
For example,
\[
(PI)_3=\operatorname{diag}(1/8,1/4,1/2,1).
\]
The repaired family is nonzero and induces an actual map of the coherent inverse-limit point types. Its coordinate formula is (25). No unnamed original space is silently identified with either inverse limit, and no topology on the point types is asserted beyond what the code constructs.

**Lean:** `GrowingTower.source`, `target`, `targetSplitting`, `propagation_gap`, `gain_eq_two`, `identityCandidate_not_exact`, `identityRepair_nonzero`, `identityRepair_formula`, `realizedIdentity_coordinate`.

The factor \(1/2\) in the source bonding maps is substantive. This example does not establish the same bounded right inverse for unweighted truncation towers.

## 7. The threshold cannot be discarded indiscriminately

Take constant real towers with identity bonding maps. Then
\[
(df)_n=f_{n+1}-f_n,
\qquad S=B_X=1.
\]
The bounded residual family \(r_n=I_{\mathbb R}\) has no bounded primitive. Indeed, if \(df=r\), evaluating at 1 gives
\[
f_n(1)=f_0(1)+n,
\]
contradicting \(\sup_n\|f_n\|<\infty\).

Lean proves
\[
\boxed{\nexists f\in E:\ df=r,\qquad
\nexists A:R\to E:\ \forall r,\ d(Ar)=r.}
\tag{26}
\]
The second statement rules out even an arbitrary right-inverse function, not only a bounded linear one. Meanwhile the earlier constant-tower theorem still gives unique exact repair preserving level zero. Therefore
\[
\boxed{
\text{exact repair of candidates}\ \not\Longrightarrow\
\text{surjectivity onto every bounded residual}.
}
\tag{27}
\]
This is a checked counterexample at the threshold, not a theorem that the numerical gap condition is necessary for every tower.

**Lean:** `IdentityTowerObstruction.primitive_growth`, `no_bounded_primitive`, `no_right_inverse`, `repair_exists_but_right_inverse_does_not`.

## 8. Independent finite audit

`checks/computation/split_tower_exact.py` uses exact rational arithmetic. It checks 360 deterministic candidate cases with source factors 0, 1/4, 1/2, 3/4, and 7/8, depths 1 through 12, and six input families. It checks separately generated residuals, a nonrecursive finite Green-sum implementation, right inversion, exact repair, preservation, coordinate reconstruction, idempotence, and the gain bound. The identity formula is also checked through level 32.

There are 2,564 positive assertions and two deliberately faulty implementations which must be rejected. These bounded tests audit a second implementation. The universal results above are Lean proof terms, not an inference from the finite tests.

## 9. Scope ledger

Proved here: a constructed bounded right inverse under explicit split/gap hypotheses; exact repair; protected-profile separation; a continuous linear coordinate equivalence; an all-level dimension-growing model; and a threshold counterexample.

Not proved here: bounded splitting existence for arbitrary bonding maps; arbitrary schedule reindexing; unrestricted pro-category comparison; an invariant-independent canonical resolution doctrine; descent, stacks, higher obstruction theory, or any unrestricted arithmetic correspondence. Orthogonality, best approximation, computational complexity, and novelty relative to the literature are not asserted.
