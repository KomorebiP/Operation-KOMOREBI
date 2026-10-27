# Komorebi Space Theory: nonisometric transport and amplified reconstruction
## v0.20.0 · Komorebi P.

This continuation replaces isometric edge maps by bounded linear equivalences. It retains the exact holonomy classification and the existing walk-view ambient-section construction, but replaces route length and nonexpansiveness by explicit transport gains. The anchor fiber is required to be finite-dimensional and real inner-product only when constructing the unconditional orthogonal-anchor repair. The earlier source modules are unchanged.

## 1. Connection, norms and actual differential

Let G be a finite simple graph on V, supplied with a root o and walks p_i:o→i, with p_o empty. The routes witness connectedness. Let H initially be any real normed vector space. Supply continuous linear equivalences

\[
\tau_{ij}:H\simeq_L H,\qquad \tau_{ii}=I,\qquad \tau_{ij}\tau_{ji}=I.
\]

Maps are specified on all vertex pairs, as in the preceding connection record, but only graph edges enter the measured differential. No flatness law and no preservation of norms is assumed. The convention is that τ_ij maps the value at j into the coordinates at i.

Use the original maximum norms on finite products:

\[
E=\prod_{i\in V}H,\quad R=\prod_{(i,j)\in\vec E(G)}H,
\qquad (dx)_{ij}=\tau_{ij}x_j-x_i.
\]

The map d is constructed as a continuous linear map. With M the maximum operator norm over measured directed edges (zero for an empty edge set),

\[
\|d\|\le M+1.
\]

`Connection.ofIsometric` embeds the old isometric connection, and `ofIsometric_differential` proves agreement of the actual differentials. This is not a replacement scalar residual.

## 2. Path amplification is derived from transported residuals

For q=(i_0,...,i_m), write T_q=τ_{i_0i_1}...τ_{i_{m-1}i_m}. Transport concatenates in this order, and reversal supplies the inverse. The exact telescoping identity is

\[
T_qx_{i_m}-x_{i_0}
=\sum_{k=0}^{m-1}(\tau_{i_0i_1}\cdots\tau_{i_{k-1}i_k})(dx)_{i_ki_{k+1}}.
\]

The empty prefix product is identity. Define the path gain recursively by

\[
\gamma(\varnothing)=0,\qquad
\gamma((i,j)q)=1+\|\tau_{ij}\|\gamma(q).
\]

Equivalently, it is the sum of the products of preceding edge norms. The code constructs the transported residual sum and proves its identity with the walk defect, then derives

\[
\|T_qx_j-x_i\|\le\gamma(q)\|dx\|_\infty.
\]

The exact gain-concatenation law is

\[
\gamma(pq)=\gamma(p)+\left(\prod_{e\in p}\|\tau_e\|\right)\gamma(q).
\]

If measured edge maps are contractive, γ(q)≤|q|. Without that hypothesis, path length cannot replace γ. These gain bounds need no inner product or finite-dimensional assumption on H.

**Lean:** `AmplifiedTransport.Connection.walkSum_defect`, `walkSum_bound`, `walk_error`, `walkGain_append`, `walkGain_le_length`.

## 3. Holonomy classification survives, but not its isometry claim

Set T_i=T_{p_i}, e_i=T_i^{-1}, and define

\[
K_{ij}=T_i\tau_{ij}T_j^{-1},\qquad
K=\bigcap_{(i,j)}\ker(K_{ij}-I).
\]

Each K_ij is proved to be the transport around an actual rooted graph loop. The common fixed space equals the vectors fixed by every closed walk. Define R_pz=(e_i z)_i. Then

\[
dR_pz=0\iff z\in K,\qquad
x\in\ker d\Longrightarrow x=R_p(x_o).
\]

The code constructs

\[
K\simeq_L\ker d.
\]

This is a continuous linear equivalence, not generally an isometry. Its inverse is anchor evaluation. The checked inequalities include

\[
\|z\|\le\|R_pz\|_\infty\le\|R_p\|\|z\|.
\]

The fixed subspace is independent of the chosen root routes. Reconstruction is route-independent on that subspace.

**Lean:** `AmplifiedTransport.Rooted.fixed_iff_all_loops`, `parameterEquiv`, `anchor_unique_extension_iff`, `fixedSpace_route_independent`.

## 4. Reverse routes give the anchor-preserving error bound

Let

\[
A_p=\max_i\gamma(\overline{p_i}).
\]

The reverse walks are deliberate: they place the reconstructed error in the destination view's own norm. The derived estimate is

\[
\|x-R_p(x_o)\|_\infty\le A_p\|dx\|_\infty.
\]

If the anchor is in K, this reconstruction is exact and is the unique exact family preserving it. Otherwise it need not be exact. For any replacement anchor z,

\[
\|x-R_pz\|_\infty
\le A_p\|dx\|_\infty+\|R_p\|\,\|x_o-z\|.
\]

The existing `CorrectionProblem` is instantiated with this d and observation p_Ux=x|_U. For U containing o,

\[
[dx]=0\text{ in }R/d(\ker p_U)
\iff x_o\in K\ \land\ (R_px_o)|_U=x|_U.
\]

Vanishing produces a unique exact family preserving U, with the A_p error bound. The algebraic obstruction is not redefined by solvability.

## 5. Every candidate can be repaired in finite-dimensional inner-product fibers

Now assume H is finite-dimensional over the reals with a specified inner product. Only the fiber has that inner-product norm: the vertex and edge norms remain maximum norms.

Let

\[
\mathcal H z=(K_{ij}z-z)_{ij},\qquad q=P_{\ker\mathcal H},
\qquad \kappa=\operatorname{gain}(\mathcal H).
\]

Here `gain` is the previously proved inverse norm on the orthogonal complement of the kernel. It is finite for each fixed system, and zero in the all-exact case. The preceding generic theorem applies to this actual, nonisometric loop map:

\[
\|z-qz\|\le\kappa\|\mathcal H z\|_\infty.
\]

Define the normalization operator N_p:R→R by

\[
(N_pr)_{ij}=T_i r_{ij}.
\]

The code proves the exact identity

\[
\mathcal H=N_p dR_p.
\]

Consequently,

\[
\|\mathcal H(x_o)\|_\infty
\le\|N_p\|\bigl(\|d\|A_p+1\bigr)\|dx\|_\infty.
\]

Define the actual continuous linear repair

\[
(Px)_i=e_iq(x_o).
\]

It satisfies

\[
dP=0,\qquad P^2=P,\qquad P|_{\ker d}=I,
\qquad \|Px\|_\infty\le\|R_p\|\|x\|_\infty,
\]

and the new global error estimate is

\[
\boxed{
\|x-Px\|_\infty\le
\left[A_p+\|R_p\|\kappa\|N_p\|(\|d\|A_p+1)\right]\|dx\|_\infty.
}
\]

Every factor is defined from the actual connection, routes, and norms. No separate anchor correction or repair bound is assumed. This constant is a sufficient bound, not claimed optimal.

The repair is unique among exact families preserving q(x_o), and is route-independent for the fixed anchor and inner product. It need not preserve an inadmissible full anchor. Unlike the isometric model, it need not be nonexpansive in the global norm. It is not asserted to be a nearest-point projection in that maximum norm.

**Lean:** `AmplifiedTransport.Rooted.normalized_reconstruction`, `rootResidual_anchor_bound`, `orthogonalRepair_error`, `orthogonalRepair_unique`, `orthogonalRepair_route_independent`.

## 6. Actual ambient realization

The implementation reuses the existing graph-walk view category. Its pullback along a walk is the new continuous linear transport T_q. Thus all distinct routes, including nontrivial loop transports, remain represented.

The existing `ViewSystem.Ambient` is identified with the exact vertex families. `finite_dimensional_ambient_repair` returns an actual ambient section with the preceding error bound and protected projected anchor. It does not introduce a norm on an arbitrary categorical stack.

## 7. A scalar chain disproves two stronger bounds

For every n, use the existing n-edge chain on n+1 vertices. Let

\[
e_i(z)=2^i z,\qquad \tau_{ij}=e_i e_j^{-1}.
\]

The connection is flat but nonisometric. Each forward adjacent transport is multiplication by 1/2, and each reverse transport is multiplication by 2. Define

\[
x_i=8\cdot2^i-1,\qquad y_i=7\cdot2^i.
\]

Lean proves for every n>0 that x_o=7, y is the actual general repair P(x), and

\[
\|dx\|_\infty=1,\qquad \|x-Px\|_\infty=2^n-1.
\]

The forward residual is 1/2 and the reverse residual is -1. At n=3, the error is 7, so the old length-only bound 3 fails. On the one-edge chain, input (7,7) repairs to (7,14), proving that the global repair is not nonexpansive. These are Lean statements about the actual general projector, not only a separately proposed formula.

This is amplification even with trivial holonomy. It is distinct from v0.19's small-holonomy-defect conditioning failure, where all transports remained isometric.

**Lean:** `AmplifiedTransport.Examples.chainRepair_is_constructed`, `exponential_amplification`, `length_only_bound_false`, `repair_not_nonexpansive`.

## 8. Formal and computational scope

Five modules are added. The inherited 117 proof modules are retained byte-for-byte. The complete v0.19 source baseline was rebuilt during this continuation before reusing any project proof objects. Consult the current verification receipt for the subsequent cumulative v0.20 build and fresh-archive replay strategy.

The supplementary exact-rational script tests 54 nonisometric connection fixtures, 270 candidate families, and 40 scalar chain lengths. It checks inverse transports, ordered telescoping, fixed-space and global-kernel dimensions by independent matrix elimination, orthogonal projection, residual and repair estimates, and three explicit false-claim examples. Its conservative rational operator bounds are not the optimal Lean-defined gain. Finite fixtures do not establish the universal conclusions.

The path, inverse-operator, and finite-dimensional projection principles are established analysis. The contribution of this continuation is the checked integration with the actual Komorebi residual, holonomy, prescribed-observation, and ambient-realization constructions. No novelty claim is made for the underlying operator-norm principles.

Not established: infinite-dimensional kernel stability without further hypotheses, estimates uniform over arbitrary connections, unknown-transport estimation, alteration of the connection to remove holonomy, nonlinear repair, arbitrary-stack normed descent, optimal global maximum-norm approximation, or an arithmetic correspondence. The projection is classical, not an executable certified SVD.
