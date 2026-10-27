# Komorebi Space Theory: holonomy-sensitive reconstruction
## v0.18.0 · Komorebi P.

The new layer removes the v0.17 requirement that overlap transports come from a globally compatible family of coordinate frames. It permits nontrivial loop transport. Exact realizations are classified by the common fixed space of actual rooted loop operators. The old protected-data obstruction quotient is connected to this classification and to a graph-derived error bound. A reflection triangle supplies a nonzero exact core, an obstructed anchor, and a constructed repair with sharp gain 3/2.

The connection maps remain known real linear isometries. The theorem does not estimate unknown transports, alter the connection, repair arbitrary nonlinear cocycles, or assert uniform conditioning over all loop systems.

## 1. Data and conventions

Let \(\mathcal G\) be a finite connected simple graph on the view set \(V\). Let \(H\) be a real normed vector space. A connection supplies linear isometry equivalences
\[
\tau_{ij}:H\longrightarrow H,\qquad \tau_{ii}=I,\qquad \tau_{ij}\tau_{ji}=I.
\]
Only adjacent pairs enter the differential. Maps are oriented contravariantly: \(\tau_{ij}\) takes values at view \(j\) to view \(i\). No equation \(\tau_{ij}\tau_{jk}=\tau_{ik}\) is assumed.

The raw candidate and measured residual spaces use maximum norms:
\[
 E=\prod_{i\in V}H,\qquad R=\prod_{(i,j)\in\vec E(\mathcal G)}H,
 \qquad (dx)_{ij}=\tau_{ij}x_j-x_i.
\]
Both directions of each graph edge are present. The code constructs the continuous linear differential and proves \(\|d\|\le2\).

The implementation supplies maps on all vertex pairs, with inverse consistency, and measures only graph edges. This does not impose composition consistency on unmeasured pairs. The previous globally framed transport is embedded by \(\tau_{ij}=e_ie_j^{-1}\), and its differential is proved identical to the earlier one.

**Lean:** `HolonomyTransport.Connection`, `Connection.differential`, `differential_opNorm`, `ofFrames_differential`.

## 2. Actual walk transport

For a walk \(q=(i_0,\ldots,i_m)\), define
\[
 T_q=\tau_{i_0i_1}\cdots\tau_{i_{m-1}i_m}.
\]
Thus \(T_q\) maps the last fiber to the first. The empty walk has identity transport. The formalization proves
\[
 T_{pq}=T_pT_q,\qquad T_{\bar q}=T_q^{-1}.
\]
For a candidate family,
\[
 \boxed{\|T_qx_{i_m}-x_{i_0}\|\le |q|\,\|dx\|_\infty.}
\]
The proof adds one edge at a time, transports the remaining error by an isometry, and applies the triangle inequality. It does not assume a spectral gap or a bounded inverse.

Exactness means \(dx=0\). This is equivalent to coherence along every graph walk, not merely along a chosen route.

**Lean:** `walkTransport_append`, `walkTransport_reverse`, `parallel_iff_all_walks`, `walk_error`.

## 3. Rooted loops and the admissible anchor space

Choose an anchor \(o\) and actual graph walks \(p_i:o\leadsto i\), with \(p_o\) empty. These are the existing `OverlapTransport.Routing` data. They witness connectedness. Put
\[
 T_i=T_{p_i},\qquad e_i=T_i^{-1},\qquad \ell=\max_i|p_i|.
\]
These \(e_i\) are constructed route frames. They are not asserted to trivialize every graph edge.

For each directed edge, define an operator on the anchor fiber:
\[
 \boxed{K_{ij}=T_i\tau_{ij}T_j^{-1}.}
\]
Lean proves that it is the transport around the actual closed walk
\[
 p_i\cdot(i,j)\cdot\overline{p_j}.
\]
Define the linear subspace
\[
 \boxed{H_{\mathrm{hol}}=\bigcap_{(i,j)}\ker(K_{ij}-I).}
\]
The finite rooted edge-loop test is equivalent to the complete closed-walk test:
\[
 z\in H_{\mathrm{hol}}
 \iff T_qz=z\text{ for every closed walk }q:o\leadsto o.
\]
This is a finite family of operators, not a claim that finding their common fixed space is algorithmically easy in arbitrary \(H\).

**Lean:** `Rooted.holonomy`, `fixedSpace`, `holonomy_is_loop`, `fixed_iff_all_loops`.

## 4. Classification theorem

Define route reconstruction by
\[
 (\mathcal R_pz)_i=e_i z.
\]
Then
\[
 \boxed{d\mathcal R_pz=0\iff z\in H_{\mathrm{hol}}.}
\]
Indeed, normalizing each reconstructed edge defect gives
\[
 e_i^{-1}(d\mathcal R_pz)_{ij}=K_{ij}z-z.
\]
Conversely, if \(dx=0\), coherence along \(p_i\) implies
\[
 x_i=e_i x_o.
\]
Therefore
\[
 \boxed{H_{\mathrm{hol}}\simeq_{\mathrm{lin,iso}}\ker d.}
\]
This is an actual Lean linear isometry equivalence. It sends \(z\) to \(\mathcal R_pz\), with inverse evaluation at the anchor. The norm equality follows from \(\|e_i z\|=\|z\|\), and the anchor coordinate attains that norm.

Equivalently,
\[
 \boxed{\exists!x:\ dx=0,\ x_o=z\iff z\in H_{\mathrm{hol}}.}
\]
The common fixed subspace is independent of the chosen routes. Reconstructed families are also route-independent on admissible anchors. No route-independence claim is made for the reconstruction of an inadmissible anchor.

**Lean:** `Rooted.parameterEquiv`, `anchor_unique_extension_iff`, `fixedSpace_route_independent`, `reconstruction_route_independent`.

## 5. Quantitative reconstruction

For every candidate, even one with an inadmissible anchor,
\[
 \boxed{\|x-\mathcal R_p(x_o)\|_\infty\le\ell\,\|dx\|_\infty.}
\]
Without anchor feasibility, the route reconstruction need not be exact. If \(x_o\in H_{\mathrm{hol}}\), it is the unique exact realization preserving the full anchor and satisfies the displayed bound.

For any replacement anchor \(z\),
\[
 \|x-\mathcal R_pz\|_\infty\le\ell\,\|dx\|_\infty+\|x_o-z\|.
\]
Writing \(h(z)=(K_{ij}z-z)_{ij}\), the anchor discrepancy obeys
\[
 \boxed{\|h(x_o)\|_\infty\le(2\ell+1)\|dx\|_\infty.}
\]
This follows by applying \(\|d\|\le2\) to the route-reconstruction error.

If a separate anchor correction \(q:H\to H_{\mathrm{hol}}\) satisfies
\[
 \|z-qz\|\le C\|h(z)\|_\infty,
\]
then the formalization proves
\[
 \|x-\mathcal R_pq(x_o)\|_\infty
 \le[\ell+C(2\ell+1)]\|dx\|_\infty.
\]
The existence of such a uniformly controlled anchor correction is **not** asserted for every connection. The next example derives a stronger constant directly for a specified system.

**Lean:** `anchored_approximation_bound`, `anchored_quantitative_repair`, `changed_anchor_error`, `rootResidual_anchor_bound`, `repair_from_anchor_estimate`.

## 6. The existing prescribed-data obstruction

For \(U\subseteq V\) containing \(o\), let \(p_Ux=x|_U\). Use the actual earlier `CorrectionProblem` quotient:
\[
 \mathfrak o_U(x)=[dx]\in R/d(\ker p_U).
\]
Lean proves
\[
 \boxed{\mathfrak o_U(x)=0\iff
 x_o\in H_{\mathrm{hol}}\ \text{and}\ (\mathcal R_p x_o)_i=x_i\quad(i\in U).}
\]
Thus the quotient checks both loop feasibility and compatibility of the remaining prescribed observations.

Vanishing produces a unique exact family retaining all prescribed values and satisfying
\[
 \boxed{\|x-y\|_\infty\le\ell\|dx\|_\infty.}
\]
The obstruction is the earlier algebraic quotient, not a new flag defined to mean solvability.

**Lean:** `Rooted.problem`, `obstruction_criterion`, `quantitative_prescribed_repair`.

## 7. An actual ambient view system, with paths retained

The globally framed v0.17 model used a thin comparison category. That would incorrectly identify distinct routes in the present setting. Instead construct a category with vertices as objects and graph walks as morphisms. Composition is concatenation. The coefficient functor restricts along a walk by \(T_q\).

The existing strict `ViewSystem.Ambient` is instantiated on this category. The formalization constructs
\[
 \boxed{\Gamma(F_T)\simeq\{x:dx=0\}\simeq H_{\mathrm{hol}}.}
\]
It also returns an actual ambient section in the quantitative prescribed-reconstruction theorem.

The walk category is not separately localized by cancellation of backtracking. Reverse consistency is proved at the transport level, and every closed-walk constraint remains visible. No new topology or arbitrary stack-level norm is asserted.

**Lean:** `PathView`, `Connection.pathViews`, `ambientParallelEquiv`, `Rooted.ambientParameters`, `quantitative_ambient_realization`.

## 8. Reflection triangle: a fully constructed nontrivial example

Use three views, the complete graph, and \(H=\mathbb R^2\) with the maximum norm. Let
\[
 \tau_{01}=\tau_{12}=I,\qquad
 \tau_{02}=\tau_{20}=\begin{pmatrix}1&0\\0&-1\end{pmatrix},
\]
with inverse transports on the other reverse edges. The loop \(0\to1\to2\to0\) acts by the displayed nonidentity reflection.

The exact families are proved to be precisely
\[
 \boxed{x_0=x_1=x_2=(a,0),\qquad a\in\mathbb R.}
\]
Thus the fixed core is a line, not all of \(H\) and not zero. In particular, \((7,0)\) is an admissible nonzero anchor, whereas \((7,1)\) cannot be the anchor of any exact family.

Define the explicit repair
\[
 (Px)_i=((x_0)_1,0).
\]
It is exact, idempotent, and the unique exact family preserving the first coordinate of the anchor. It does not preserve an impossible vertical anchor component.

Let \(\varepsilon=\|dx\|_\infty\), and write the three vertical coordinates as \(a,b,c\). The edge estimates imply
\[
 |b-a|\le\varepsilon,\qquad|-c-a|\le\varepsilon,\qquad|c-b|\le\varepsilon.
\]
Combining these inequalities gives
\[
 |a|,|b|,|c|\le\tfrac32\varepsilon.
\]
The horizontal differences from the anchor are at most \(\varepsilon\), hence
\[
 \boxed{\|x-Px\|_\infty\le\tfrac32\|dx\|_\infty.}
\]
Lean proves this for every input and proves sharpness using
\[
 x=((7,3/2),(7,1/2),(7,-1/2)).
\]
Its residual norm is exactly \(1\), its repair is the nonzero constant horizontal family \((7,0)\), and its error is exactly \(3/2\).

**Lean:** `ReflectionTriangle.loop_nontrivial`, `parallel_iff`, `fixedSpace_iff`, `nonzero_exact_section`, `inadmissible_anchor`, `repair_unique`, `repair_error`, `repair_bound_sharp`.

## 9. Verification and scope

Five modules add 63 explicitly named theorems and 35 indexed constructions. The cumulative project has 112 proof modules, 1,134 named theorems, and 636 indexed constructions. All 107 previous proof-module sources are byte-identical to v0.17. Counts include auxiliary declarations, not discoveries.

The finite exact-rational audit uses signed permutation connections and independent Gaussian elimination. It checks 120 connection systems on graphs with 3 through 7 vertices, 960 candidate fixtures, and 375 reflection-triangle candidates. It records 11,641 assertions and four rejected stronger claims. Fixed spaces of dimensions 0, 1, and 2 occur. These fixtures are not exhaustive; universal conclusions come from the Lean proofs.

Seven development compile attempts failed before correction. A first finite-audit run failed when writing its report because an argument variable was shadowed; the corrected script reran all checks. An initial container call returned a transport error; subsequent ordinary execution succeeded. A separate fresh-replay harness initially failed because Lean selected the first package directory without falling through to the baseline directory. Copying hash-validated baseline modules into the fresh build root corrected the harness, and its rerun passed. These failures are retained and are not counted as successful verification.

The delivery receipt and audit logs distinguish the current cumulative clean build from the fresh extension replay against the independently rebuilt v0.17 baseline. The latter does not recompile the unchanged 107 modules a second time. The compiler, imported pinned dependency cache, and standard axioms `propext`, `Classical.choice`, and `Quot.sound` remain trusted.

Not established: unknown-transport estimation, a universally bounded projection onto every holonomy fixed space, nonisometric amplification estimates, nonlinear repair, an arbitrary norm on the cocycle stack, infinite-graph bounds, or unrestricted arithmetic correspondence. This extends quantitative reconstruction to known isometric connections with genuine loop transport. It does not make inconsistent boundary values extendable and does not repair the connection itself.

The fixed-vector characterization is standard holonomy mathematics. This release makes no novelty claim for that general principle. Its role is the explicit kernel-checked integration with the existing Komorebi section, obstruction, route, and quantitative-repair structures.

Implementation references: the pinned `Mathlib.Combinatorics.SimpleGraph.Walk.Operations` and `Mathlib.Analysis.Normed.Operator.LinearIsometry` APIs. The source declarations, rather than explanatory terminology, determine the formal scope.
