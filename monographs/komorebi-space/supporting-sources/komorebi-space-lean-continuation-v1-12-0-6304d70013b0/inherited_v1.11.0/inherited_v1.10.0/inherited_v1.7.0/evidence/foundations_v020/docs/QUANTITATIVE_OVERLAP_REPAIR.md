# Komorebi Space Theory: quantitative reconstruction of overlap data
## v0.17.0 · Komorebi P.

This block connects an actual additive ambient-section problem to an explicit analytic repair bound. It treats finite measured graphs and supplied linear isometric coordinate frames. It does not assert quantitative repair for arbitrary nonabelian stacks, nontrivial holonomy, or unknown frames. The path estimates and linear projections are established mathematics; the contribution here is their checked integration with the existing Komorebi residual, prescribed-observation, and exactification structures.

## 1. The model and its mathematical inputs

Let V be a finite type of views, let H be a real normed vector space, and supply real linear isometry equivalences

\[
 e_i:H\simeq_{\!L}^{\mathrm{iso}} H\qquad(i\in V).
\]

H need not be finite-dimensional or complete. The explicit finite repair does not use completeness. Define the actual coordinate transports

\[
 \boxed{\tau_{ij}=e_i e_j^{-1},\qquad
 \tau_{ii}=I,\quad \tau_{ij}\tau_{jk}=\tau_{ik}.}
 \tag{1}
\]

These are flat, globally trivialized overlaps by construction. Their flatness is not a consequence inferred from small measured errors. The frames, and hence the overlap maps, are known input.

Let G be a simple undirected graph on V. Its residual indices are directed adjacent pairs

\[
 \vec E(G)=\{(i,j):G(i,j)\}.
\]

Both directions of each edge are included. Give

\[
 \mathcal X=\prod_{i\in V}H,
 \qquad \mathcal R=\prod_{(i,j)\in\vec E(G)}H
\]

the finite-product maximum norms. Choose an anchor o and a graph walk p_i from o to every i, with p_o the empty walk. This is an explicit witness of connectedness, not an assumed inverse operator. Set

\[
 \boxed{\ell=\max_i |p_i|.}
 \tag{2}
\]

No claim is made that the selected routes are shortest. They may be replaced to improve the estimate.

**Lean:** `OverlapTransport.Frames`, `transport`, `Edges`, `Routing`, `Routing.radius`.

## 2. An actual differential and its telescoping identity

For candidate local values x=(x_i), the measured disagreement is

\[
 \boxed{(dx)_{ij}=\tau_{ij}x_j-x_i.}
 \tag{3}
\]

The sign agrees with the previous additive view differential. The code constructs a continuous linear map

\[
 d:\mathcal X\longrightarrow\mathcal R,
 \qquad \boxed{\|d\|\le2.}
 \tag{4}
\]

Normalize y_i=e_i^{-1}x_i. Then

\[
 e_i^{-1}(dx)_{ij}=y_j-y_i,
 \qquad \|(dx)_{ij}\|=\|y_j-y_i\|.
 \tag{5}
\]

For independently supplied edge data r and a walk p=(i_0,\ldots,i_m), define

\[
 \int_p r=\sum_{k<m}e_{i_k}^{-1}r_{i_ki_{k+1}}.
 \tag{6}
\]

The source-frame inverse is necessary. Summing untransported residual coordinates is not the defined operation. Lean proves

\[
 \boxed{\left\|\int_p r\right\|\le |p|\,\|r\|_\infty,}
 \tag{7}
\]

and the exact identity

\[
 \boxed{\int_p dx=y_{i_m}-y_{i_0}.}
 \tag{8}
\]

In particular, every actual residual has zero normalized integral around every closed walk.

**Lean:** `edgeDifferential`, `edgeDifferential_opNorm`, `pathIntegral_bound`, `pathIntegral_differential`, `actual_closed_walk`.

## 3. Construct the correction rather than assume it

Define the path correction

\[
 \boxed{(Ar)_i=e_i\left(\int_{p_i}r\right).}
 \tag{9}
\]

The implementation proves its linearity and constructs its continuous linear structure with the derived bound

\[
 \boxed{\|A\|\le\ell,\qquad(Ar)_o=0.}
 \tag{10}
\]

For actual residuals, (8) gives

\[
 (Adx)_i=x_i-e_i e_o^{-1}x_o.
\]

Thus the repaired realization is explicitly

\[
 \boxed{(P_ox)_i=\tau_{io}x_o,\qquad P_o=I-Ad.}
 \tag{11}
\]

The checked identities and estimates are

\[
 \boxed{
 dP_o=0,\quad P_o^2=P_o,\quad(P_ox)_o=x_o,\quad
 \|P_o\|\le1,\quad dAd=d.
 }
 \tag{12}
\]

The anchor is preserved as a full vector, not merely as a norm or scalar truth value. The repaired family is the unique exact candidate with that anchor value:

\[
 \boxed{\exists!z:\ dz=0,\quad z_o=x_o.}
 \tag{13}
\]

Most importantly,

\[
 \boxed{\|x-P_ox\|_\infty\le\ell\,\|dx\|_\infty.}
 \tag{14}
\]

This is a bound derived from the graph and the isometry hypotheses. It does not assume a singular-value estimate, a bounded right inverse, or a contraction rate as an unproved property of the model.

Different chosen routes yield the same correction on actual residuals dx, since both equal x-P_ox. This does not require the route operators to agree on arbitrary independent edge assignments. P_o depends on the protected anchor and the overlap system. It is not claimed to be an orthogonal projection or a best approximation without the anchor constraint.

**Lean:** `Routing.correction`, `correction_opNorm`, `correction_differential`, `differential_correction_differential`, `repair_error`, `unique_exact_repair`, `routes_agree_on_actual_residual`; `repair_opNorm`.

## 4. Connection to the existing ambient-section and obstruction theory

Construct the complete thin comparison category on V, with exactly one arrow between every ordered pair. On this category, the old `AdditiveViewSystem` is instantiated with restrictions (1). The root-connected measured graph is sufficient to test its full coherence. The formal equivalence is

\[
 \boxed{d_Gx=0\iff\delta_{\mathrm{views}}x=0.}
 \tag{15}
\]

This is not a definition that replaces the old ambient coherence condition. The differential comparison and both implications are proved. There is also an explicit equivalence with the independently specified reference vector space:

\[
 \boxed{
 \Gamma(F_e)\simeq H,\qquad
 s\mapsto e_o^{-1}s_o,\qquad
 z\mapsto(e_i z)_i.
 }
 \tag{16}
\]

This is an equivalence of the existing section type with H. No new topology on the section subtype is asserted by (16).

Let U be any prescribed vertex set containing o. In the actual old obstruction quotient, Lean proves

\[
 \boxed{
 [\delta\widetilde x]=0\pmod{\delta(\ker p_U)}
 \iff
 e_i^{-1}x_i=e_o^{-1}x_o\quad(i\in U).
 }
 \tag{17}
\]

Here the implementation uses the actual raw family x, and its class under the existing `CorrectionProblem` definitions; it does not substitute a Boolean compatibility flag. The right side says that all prescribed local values describe the same reference vector.

Combining this with (14) gives the quantitative realization theorem:

\[
 \boxed{
 \mathfrak o_U(x)=0\Longrightarrow
 \exists s\in\Gamma(F_e):\quad
 s|_U=x|_U,\quad
 \|x-s\|_\infty\le\ell\|d_Gx\|_\infty.
 }
 \tag{18}
\]

The construction is s=P_ox. It is already unique among exact realizations preserving the anchor. Incompatible prescriptions cannot all be retained.

Finally, A supplies the correction operator for the previous `RepairDynamics.Scheme`, with contraction rate zero. Its preservation and contraction obligations are proved from (12). When H is complete, the old limiting projector is proved equal to the explicit P_o. Completeness is used only for invoking that older analytic interface, not for constructing the finite path repair itself.

**Lean:** `viewSystem`, `view_differential`, `ambientEquiv`, `edge_exact_iff_view_exact`, `obstruction_zero_iff_boundary`, `quantitative_realization`, `Routing.scheme`, `scheme_step`, `scheme_projection`.

## 5. Integrability of arbitrary edge data is a separate question

A is not claimed to satisfy dA=I on every element of the independent residual space. Define

\[
 \Pi=dA,\qquad O_{\mathcal P}=I-\Pi.
 \tag{19}
\]

Lean proves

\[
 \boxed{
 \Pi^2=\Pi,\quad O_{\mathcal P}^2=O_{\mathcal P},\quad
 A O_{\mathcal P}=0,
 }
 \tag{20}
\]

and

\[
 \boxed{
 O_{\mathcal P}r=0
 \iff r\in\operatorname{im}d,
 \qquad
 \|O_{\mathcal P}r\|\le(1+2\ell)\|r\|.
 }
 \tag{21}
\]

The diagnostic representative depends on routes, but its zero condition is the intrinsic image condition for the fixed differential. It measures an integrability question distinct from the prescribed-domain obstruction (17).

On the three-vertex complete graph with identity frames, set

\[
 r_{01}=1,\quad r_{12}=1,\quad r_{02}=0,
 \qquad r_{ji}=-r_{ij}.
\]

If r=dx, the first two equations require x_2-x_0=2, while the third requires x_2-x_0=0. Lean proves that no primitive exists. Antisymmetry alone is insufficient; loop consistency matters.

**Lean:** `Routing.residualProjection`, `residualProjection_idempotent`, `routeObstruction_zero_iff`, `routeObstruction_idempotent`, `correction_obstruction_zero`, `routeObstruction_bound`, `CycleBoundary.triangle_no_primitive`.

## 6. Uniform control and sharp failure across growing graphs

### Star overlaps

On a star centered at the protected anchor, every selected route has length at most one. The verified bound is

\[
 \boxed{\|x-P_ox\|_\infty\le\|d_Gx\|_\infty,}
 \tag{22}
\]

independently of the number of vertices.

### Chains

For the path with n edges and n+1 vertices, the selected root-to-i route has length i and the radius is n. With real values and identity frames, the candidate x_i=i satisfies

\[
 \boxed{\|dx\|_\infty=1,\qquad\|x-P_0x\|_\infty=n\quad(n>0).}
 \tag{23}
\]

The general upper bound is n, and this candidate attains it. Lean proves the statement for every natural n, not by testing a finite list of graph sizes. It also proves

\[
 \boxed{\nexists C\ge0:\ \forall n,x,\quad
 \|x-P_0x\|_\infty\le C\|d_nx\|_\infty.}
 \tag{24}
\]

Thus exact existence and uniqueness at every finite level do not imply a uniformly bounded residual-to-correction estimate across arbitrary growing overlap graphs.

### Nontrivial charts and a nonzero protected value

On two real views, use e_0=I and e_1=-I. The candidate (7,-9) repairs to (7,-7). Its residual is nonzero, while the protected value 7 remains unchanged. The chart change is genuine, not simply an all-zero example.

**Lean:** `Examples.star_error`, `chain_radius`, `chain_bound_sharp`, `no_uniform_chain_constant`, `signed_repair_formula`, `signed_residual_nonzero`.

## 7. Isometric coordinate changes are compatible with repair

Let a_i be another family of linear isometry equivalences, change the frames and observations simultaneously by

\[
 e'_i=a_i e_i,\qquad x'_i=a_i x_i.
\]

Lean proves

\[
 \boxed{d'_{ij}x'=a_i(d_{ij}x),\qquad
 \|d'_{ij}x'\|=\|d_{ij}x\|,}
 \tag{25}
\]

and

\[
 \boxed{P'_o x'=a(P_o x).}
 \tag{26}
\]

These are actual coordinate formulas, not an invocation of abstract categorical equivalence to infer numerical isometry. Arbitrary category equivalences and nonisometric coordinate changes do not receive a blanket norm-invariance claim.

**Lean:** `reframe_defect`, `reframe_defect_norm`, `reframe_repair`.

## 8. Computation, formal scope, and open boundaries

Five new proof modules add 78 named theorems and 42 indexed constructions. The cumulative library contains 107 proof modules, 1,071 named theorems, and 601 indexed constructions. All 102 v0.16 proof modules are unchanged. Counts include elementary and auxiliary declarations, not claimed discoveries.

The separate rational audit uses signed permutation frames and checks 1,080 deterministic graph/frame/candidate configurations, 2,160 independent edge residual assignments, and 40 chain lengths. It records 41,301 assertions and five rejected false-claim controls. An independent Gaussian-elimination test is compared with the route integrability criterion. These tests do not enumerate all graphs or frames and are not the proof of the universal conclusions.

The executable audit initially failed because integer entries divided by integer pivots introduced floating-point values into the Gaussian checker. Every matrix entry and right-hand side is now explicitly converted to `Fraction` before elimination. The failed attempt is retained and not counted as evidence of correctness. Lean development errors and the interrupted first baseline launcher are separately recorded.

Closed within this model: actual continuous linear residual and correction operators; a graph-derived sharp-in-chains error bound; preservation of compatible prescribed values; explicit ambient reconstruction; connection to the old correction scheme; an image/integrability diagnostic; and isometric coordinate covariance.

Not proved: existence of globally trivializing isometric frames for arbitrary local systems; repair of nonflat or nonlinear cocycles; a numerical structure on arbitrary stacks; uniform conditioning on arbitrary growing graphs; spectral/optimal estimates on general graphs; orthogonal or unanchored best approximation; nonisometric presentation-independent norms; infinite-graph estimates; executable extraction or complexity of the Lean noncomputable definitions; or unrestricted arithmetic correspondence.

The Lean compiler/kernel, pinned imported caches, and `propext`, `Classical.choice`, `Quot.sound` remain trusted. The current and fresh build reports control verification status. The archive does not include the multi-gigabyte runtime.
