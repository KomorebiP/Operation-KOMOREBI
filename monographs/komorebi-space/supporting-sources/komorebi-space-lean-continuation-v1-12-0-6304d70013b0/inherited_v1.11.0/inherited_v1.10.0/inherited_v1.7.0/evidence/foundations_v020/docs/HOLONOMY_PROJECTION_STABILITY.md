# Komorebi Space Theory: derived holonomy projection and stability
## v0.19.0 · Komorebi P.

This block discharges the anchor-correction estimate left as a hypothesis in v0.18, for finite-dimensional real inner-product fibers. It constructs the orthogonal anchor projection, derives a finite optimal gain for the existing maximum residual norm, and applies the result to actual graph transports and ambient sections. An exact Cayley-rotation family proves that a common gain over all connections is impossible, even on a fixed triangle with real fiber dimension two.

## 1. The precise advance and its hypotheses

Retain the finite graph, root, routing, known inverse-consistent linear isometric transports, edge differential, and ambient walk-view system of v0.18. The new fiber assumption is
\[
H\text{ is a finite-dimensional real inner-product space.}
\]
No flatness is assumed. The graph is supplied with routes from a fixed anchor, witnessing connectedness. Vertex and directed-edge families retain their **maximum norms**. Only the individual fiber has its inner-product norm. In particular, this theorem is not obtained by treating a product maximum norm as a Hilbert norm.

The older reflection example used a maximum norm on its two-dimensional fiber. Its earlier theorem remains valid under its own assumptions; it is not silently replaced by this new inner-product specialization.

## 2. Generic kernel projection with a derived gain

Let \(E\) be a finite-dimensional real inner-product space, let \(R\) be any real normed vector space, and let
\[
d:E\to R
\]
be continuous linear. Define
\[
K=\ker d,\qquad q=P_K:E\to E,
\]
where \(P_K\) is the orthogonal projection. Its existence follows from finite dimensionality, rather than being an additional repair hypothesis. Lean constructs it using the standard `Submodule.starProjection`.

The restricted map
\[
D=d|_{K^\perp}:K^\perp\to \operatorname{im}D
\]
is injective and surjective onto its specified range. Finite dimensionality supplies a continuous inverse. Set
\[
\boxed{\kappa(d)=\|D^{-1}\|.}
\tag{1}
\]
The range carries the norm inherited from \(R\). The construction does not demand surjectivity of \(d\) onto all of \(R\).

For every \(z\in E\),
\[
z-qz\in K^\perp,\qquad d(z-qz)=dz.
\]
Applying the inverse bound gives
\[
\boxed{\|z-qz\|\le\kappa(d)\|dz\|.}
\tag{2}
\]
No spectral lower bound, right inverse, or anchor estimate is assumed in this theorem.

Lean also proves
\[
q^2=q,\quad dq=0,\quad q|_K=I,\quad\|q\|\le1,
\]
and the best-approximation inequality
\[
\|z-qz\|\le\|z-w\|\qquad(w\in K).
\tag{3}
\]
For every nonnegative \(C\),
\[
\boxed{[\forall z,\ \|z-qz\|\le C\|dz\|]\iff\kappa(d)\le C.}
\tag{4}
\]
Thus (1) is the optimal gain for these specified norms, not an arbitrary existential bound.

The all-exact case is handled without an undefined smallest positive singular value:
\[
\boxed{\kappa(d)=0\iff d=0.}
\tag{5}
\]
The definition is classical and noncomputable. It does not implement an executable singular-value decomposition.

**Lean:** `KernelProjection.projection`, `reducedEquiv`, `gain`, `error_bound`, `projection_best`, `gain_characterization`, `gain_eq_zero_iff`.

## 3. Application to the actual holonomy operator

For the existing rooted graph connection, write
\[
K_a=T_i\tau_{ij}T_j^{-1},\qquad a=(i,j),
\]
and define the same root residual as v0.18, now bundled as a continuous linear map:
\[
\mathcal H:H\to\prod_{a\in\vec E(G)}H,
\qquad (\mathcal H z)_a=K_a z-z.
\tag{6}
\]
The formalization proves
\[
\ker\mathcal H=H_{\rm hol}
\]
for the existing `fixedSpace`, not a replacement notion of feasible anchors. Define
\[
q=P_{H_{\rm hol}},\qquad\kappa_\infty=\kappa(\mathcal H).
\]
Then
\[
\boxed{\|z-qz\|\le\kappa_\infty\max_a\|K_a z-z\|.}
\tag{7}
\]
The maximum over an empty edge set is handled by the formal product-space conventions; the zero differential has gain zero. No nontrivial kernel or nonempty complementary space is required.

For a fixed root and inner product, \(q\) is independent of the selected root routes, because the common fixed space was already proved route-independent. The numerical gain and route radius may depend on the selected finite presentation of loop tests. No route-invariance theorem for the gain is asserted.

**Lean:** `Rooted.rootResidualMap_kernel`, `anchorProjection`, `holonomyGain`, `anchorProjection_error`, `holonomyGain_optimal`, `anchorProjection_route_independent`.

## 4. Unconditional candidate repair within this finite-dimensional class

Let \(\mathcal R_pz=(e_i z)_i\) be the existing route reconstruction, and let \(o\) be the anchor. Define
\[
\boxed{(Px)_i=e_iq(x_o).}
\tag{8}
\]
The map is continuous linear into the existing vertex maximum-norm space. The code proves
\[
\boxed{dP=0,\quad P^2=P,\quad P|_{\ker d}=I,\quad\|P\|\le1.}
\tag{9}
\]
It preserves exactly the feasible component of the anchor:
\[
q((Px)_o)=q(x_o).
\]
It is the unique exact family with that protected component:
\[
\boxed{\exists!y:\ dy=0\ \land\ q(y_o)=q(x_o).}
\tag{10}
\]
An already feasible full anchor remains unchanged. An impossible full anchor is not claimed to survive.

With \(\ell=\max_i|p_i|\), the old path estimates and the newly derived (7) give
\[
\boxed{\|x-Px\|_\infty\le
[\ell+\kappa_\infty(2\ell+1)]\|dx\|_\infty.}
\tag{11}
\]
This holds for **every candidate** of each fixed system. The separate anchor-estimate assumption has been removed in this finite-dimensional inner-product class.

The repair is independent of the chosen root routes. It can still depend on the selected anchor and inner product. Orthogonal best approximation is proved for the anchor \(qz\). The global \(P\) is not claimed to be a nearest-point projection in the vertex maximum norm, and the constant in (11) is not claimed sharp.

The construction returns an actual prior `ViewSystem.Ambient` object, not only a numerical vector family:
\[
\exists s\in\Gamma(F_T):\ q(s_o)=q(x_o),\quad
\|x-s\|_\infty\le[\ell+\kappa_\infty(2\ell+1)]\|dx\|_\infty.
\tag{12}
\]

**Lean:** `Rooted.orthogonalRepair`, `orthogonalRepair_error`, `orthogonalRepair_unique`, `orthogonalRepair_route_independent`, `orthogonalAmbient`, `finite_dimensional_ambient_repair`, `finite_dimensional_stability`.

## 5. Certified numerical upper bounds with the correct product norm

The existence theorem above does not need a supplied spectral gap. To certify an explicit upper bound in a concrete model, one may additionally establish a positive number \(\lambda\) satisfying
\[
\lambda\|u\|^2\le\sum_{a\in\vec E(G)}\|(K_a-I)u\|^2
\quad\text{for all }u\in H_{\rm hol}^\perp.
\tag{13}
\]
Let \(m=|\vec E(G)|\), counting the directed edges used in the actual residual type. Lean proves
\[
\boxed{\kappa_\infty\le\sqrt{m/\lambda}.}
\tag{14}
\]
Consequently,
\[
\boxed{\|x-Px\|_\infty\le
[\ell+\sqrt{m/\lambda}(2\ell+1)]\|dx\|_\infty.}
\tag{15}
\]
The factor \(\sqrt m\) is present because the squared sum in (13) is bounded by \(m\) times the squared maximum norm. A least-positive-singular-value argument with a Euclidean stacked residual cannot silently reuse its constant for the maximum residual norm.

The Lean certificate theorem takes a proof of (13). It does not certify floating-point eigenvalues. The supplementary rational auditor uses exact matrix positivity certificates and conservative rational constants instead of approximate square roots.

**Lean:** `KernelProjection.QuadraticGap`, `error_of_quadratic_gap`, `gain_le_of_quadratic_gap`; `Rooted.holonomyGain_certificate`, `certified_orthogonalRepair_error`.

## 6. No universal conditioning bound, even on a fixed triangle

For real \(t\), use \(\mathbb C\) as a real two-dimensional inner-product space and define
\[
u_t=\frac{t+i}{t-i},\qquad U_tz=u_tz.
\]
The denominator is nonzero, \(|u_t|=1\), and \(u_t\ne1\). Lean constructs \(U_t\) as an actual real linear isometry equivalence, with
\[
\operatorname{Fix}(U_t)=\{0\}.
\]
Since
\[
u_t-1=\frac{2i}{t-i},
\]
the checked exact identity is
\[
\boxed{\|z\|=\frac{|t-i|}{2}\|U_tz-z\|.}
\tag{16}
\]
The sharp gain \(|t-i|/2\) is unbounded as \(t\) varies. These maps remain isometries throughout. The instability concerns recovery from their increasingly weak defect signal, not amplification of the transports themselves.

Instantiate the connection on the same complete three-vertex graph for every \(t\). All edges except one inverse pair have identity transport. The exceptional pair carries \(U_t\) and \(U_t^{-1}\). Exact vertex families are zero. For a constant candidate \(x_i=z\),
\[
\|dx\|_\infty=\|U_tz-z\|,\qquad \|x-Px\|_\infty=\|z\|.
\]
Every all-input graph repair constant must therefore be at least \(|t-i|/2\). Lean proves
\[
\boxed{\nexists C\in\mathbb R\ \forall t\ \forall x:
\|x-P_tx\|_\infty\le C\|d_tx\|_\infty.}
\tag{17}
\]
The graph size and fiber dimension do not change. In particular, finite-dimensional existence of a gain does not yield a gain uniform over all connections.

**Lean:** `CayleyHolonomy.sharp_gain_identity`, `gain_unbounded`, `no_uniform_holonomy_gain`; `ConditioningTriangle.necessary_global_gain`, `no_uniform_global_gain`.

## 7. Verification and supplementary computation

Five new modules add 73 explicitly named theorems and 18 indexed constructions. The cumulative project has 117 proof modules, 1,207 named theorems, and 654 indexed constructions. Every one of the 112 v0.18 proof-module sources is unchanged. Counts include auxiliary lemmas, not mathematical discoveries.

Verification proceeds in two stages. This session first rebuilt the complete v0.18 baseline from source: all 112 modules and its root, the full theorem axiom audit, and three negative controls passed. The v0.19 verifier then checked every inherited source and compiled hash, reused those freshly rebuilt baseline objects, and freshly compiled all five additions and the new cumulative root. It ran the complete 1,207-theorem audit, the complete 654-construction audit, and all three negative controls. The final ZIP replay follows the same explicitly recorded baseline-reuse strategy. This is not described as two independent full v0.19 builds.

`checks/computation/holonomy_projection_exact.py` is an independent exact-rational implementation. It checks 72 connection fixtures, 432 candidate families, and 44 Cayley vectors, with 5,447 assertions and five rejected false-claim controls. Fiber dimensions range from one to four. Exact kernel and row-space projection formulas agree, independent global-kernel elimination agrees with holonomy classification, and exact LDL positivity certificates yield valid gap bounds. Matrix comparisons use squared Euclidean fiber norms and maximum vertex/edge norms. The tests are deterministic fixtures, not an exhaustive family or a substitute for Lean.

The supplied gain may be conservative in the rational audit. The optimal-gain statement is proved by the generic Lean inverse-norm argument, not inferred from those finite cases. The finite output also records zero-core and all-exact cases separately.

## 8. Established mathematics and the remaining boundary

Orthogonal projection, finite-dimensional inverse continuity, and operator-norm characterizations are established functional analysis. The pinned mathlib sources used here include:

- `Mathlib/Analysis/InnerProductSpace/Projection/Basic.lean`
- `Mathlib/Analysis/Normed/Module/FiniteDimension.lean`

The new project contribution is the checked integration with the actual rooted holonomy map, old maximum norms, route reconstruction, protected anchor component, ambient sections, and the fixed-graph conditioning counterexample. No novelty claim is made for the underlying finite-dimensional argument.

Closed in this class: constructed anchor projection; finite optimal max-residual gain; stable exact repair of every candidate preserving the feasible anchor component; route independence; an explicit quadratic-certificate interface; and failure of universal conditioning over connections.

Not closed: infinite-dimensional estimates without additional range hypotheses; a constant uniform over arbitrary connection families; nonisometric or nonlinear repair; estimation or correction of unknown connection maps; arbitrary protected values known to be infeasible; an executable SVD or formally verified eigenvalue-certification algorithm; global best approximation in the vertex maximum norm; a norm on an arbitrary Komorebi stack; or an unrestricted arithmetic correspondence.

The projection is canonical for the fixed inner product and kernel. The global repair additionally uses the fixed anchor. Universes and all hypotheses are those in the Lean source. Compiler/kernel, pinned imported dependencies, and the standard axioms `propext`, `Classical.choice`, and `Quot.sound` remain trusted.
