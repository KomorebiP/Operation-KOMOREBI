# Komorebi Space Theory: strict cocycle and gauge descent
## v0.12.0 - Komorebi P.

This continuation proves the first two strict descent components of the nonabelian Komorebi view theory. The coefficient groups remain arbitrary and need not commute. The new results do **not** yet glue local cocycle objects that are identified only up to gauge isomorphism. They prove (i) descent of gauge morphisms between already-global cocycles and (ii) descent of cocycle objects when their labels agree literally on overlap arrows.

## 1. View covers

Let \(\mathcal V\) be a category of views, let \(G_v\) be groups, and let
\[
f^*:G_w\to G_v
\qquad(f:v\to w)
\]
be the existing restriction homomorphisms. Let \((U_i)_{i\in I}\) be subsets of view objects.

The previously defined transition-cover condition is
\[
\boxed{
\forall(f:v\to w),\quad \exists i:\ v,w\in U_i.
}
\tag{1}
\]
It is sufficient to check equations attached to one arrow.

For cocycle multiplication one needs a stronger hypothesis:
\[
\boxed{
\forall\bigl(v\xrightarrow f w\xrightarrow g z\bigr),\quad
\exists i:\ v,w,z\in U_i.
}
\tag{2}
\]
Call (2) a **composition cover**. Lean proves that every composition cover is a transition cover.

## 2. Descent of gauge morphisms

A local gauge matching family consists of maps
\[
a_i(v)\in G_v\qquad(v\in U_i)
\]
which agree on common views:
\[
\boxed{a_i(v)=a_j(v)\qquad(v\in U_i\cap U_j).}
\tag{3}
\]

Under object coverage these values assemble uniquely into a global family
\[
a=(a_v)_v.
\]
For two existing global cocycles \(c,d\), assume every local gauge satisfies, on every arrow visible in its patch,
\[
\boxed{
a_i(v)c_f\,[f^*(a_i(w))]^{-1}=d_f.
}
\tag{4}
\]
Under the transition-cover condition, Lean proves that the assembled global gauge satisfies
\[
\boxed{a_vc_f[f^*(a_w)]^{-1}=d_f\qquad\forall f:v\to w,}
\tag{5}
\]
or equivalently
\[
\boxed{a\cdot c=d.}
\tag{6}
\]

If a framing domain \(B\subseteq\operatorname{Ob}(\mathcal V)\) is fixed and each local gauge is the identity on \(B\cap U_i\), the assembled gauge belongs to the already formalized subgroup \(\mathcal G_B\). Therefore the construction produces an actual morphism
\[
\boxed{c\longrightarrow d}
\]
in the existing framed cocycle groupoid.

Moreover, any global framed morphism which restricts to the prescribed local gauge values is equal to the glued morphism. Hence a fixed matching family has a unique global realization.

**Lean:** `GaugeMatching.assemble_relates`, `GaugeMatching.FramedDescent.glueHom_local`, `glueHom_unique`, `exists_unique_glued_hom` in `GaugeDescent.lean`.

## 3. Strict descent of cocycle objects

For one patch \(S\subseteq\operatorname{Ob}(\mathcal V)\), a patch cocycle consists of labels
\[
c^S_f\in G_v\qquad(f:v\to w,\ v,w\in S)
\]
with
\[
c^S_{1_v}=1,
\qquad
c^S_{g\circ f}=c^S_f\,f^*(c^S_g)
\]
whenever all relevant views lie in \(S\).

A strict matching family \((c^{(i)})_i\) satisfies equality on every overlap arrow:
\[
\boxed{
c^{(i)}_f=c^{(j)}_f
\qquad
(v,w\in U_i\cap U_j).
}
\tag{7}
\]

Choose any patch containing the endpoints of \(f\) and define
\[
\boxed{c_f:=c^{(i)}_f.}
\tag{8}
\]
Equation (7) makes this choice independent of the chosen patch. The identity law needs only object coverage. The composition law requires a patch containing all three views in a composable pair, which is exactly why (2) appears.

Lean constructs the global cocycle and proves
\[
\boxed{
c_{g\circ f}=c_f f^*(c_g).}
\tag{9}
\]

Restriction gives the reverse construction. The two are inverse, giving the explicit equivalence
\[
\boxed{
Z^1(\mathcal V;G)
\simeq
\operatorname{Match}_{\mathrm{strict}}\bigl((Z^1(U_i;G))_i\bigr)
}
\tag{10}
\]
for the formal `Cocycle` types used in the project, under a composition cover.

**Lean:** `CompositionCover.transitionCover`, `CocycleMatching.assembleEdge_local`, `glue_ofGlobal`, `ofGlobal_glue`, `descentEquiv` in `CocycleDescent.lean`.

## 4. What has and has not been reached

The new results prove both of the following strict statements:

\[
\boxed{
\text{matching local gauge morphisms}\Longleftrightarrow
\text{one global gauge morphism}
}
\]
for fixed global source and target cocycles, and
\[
\boxed{
\text{literally matching local cocycles}\Longleftrightarrow
\text{one global cocycle}.
}
\]

This is genuinely stack-like structure, but it is not yet the stack condition. A stack permits local objects to be related on overlaps by specified isomorphisms rather than by literal equality. One then needs coherence on triple overlaps and must prove those descent data are effective.

Thus the next target is a datum of the form
\[
(c_i,\ a_{ij}),
\]
where
\[
a_{ij}:c_i|_{U_{ij}}\xrightarrow{\sim}c_j|_{U_{ij}}
\]
and on triple overlaps
\[
\boxed{a_{ik}=a_{jk}\circ a_{ij}}
\tag{11}
\]
with the correct noncommutative order and restrictions. The desired theorem is that such effective descent data determine a global cocycle up to global gauge isomorphism.

That theorem is **not** asserted by v0.12.0.

## 5. Verification status

The two new modules and updated root import compile with warnings treated as errors against the separately fully replayed v0.11.0 baseline. All 76 prior proof-module sources are hash-identical to v0.11.0. The complete 845-theorem axiom request and the complete 414-construction axiom request compile in the combined build and report only `propext`, `Classical.choice`, and `Quot.sound`. The negative controls continue to reject a false statement and `sorry`, and expose an injected project axiom.

A full clean cumulative replay was also started. The host tool call reached its 300-second execution limit after 17 modules; no completed module had failed. That interrupted run is retained as evidence but is **not counted as a full-replay PASS**. The release is therefore labeled **incrementally verified against the fully verified v0.11.0 baseline**, rather than falsely claiming a completed clean replay.
