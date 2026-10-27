# Komorebi Space Theory: invariance under equivalent view presentations
## v0.15.0 · Komorebi P.

This extension compares genuinely different view categories, not just covers inside a fixed category. Actual pullback along a category equivalence induces an equivalence of the existing unframed cocycle gauge groupoids and a bijection of the existing coherent section types. On patches closed under isomorphism, the comparison preserves inclusion, composition covers, and restriction. A duplicated-view construction proves why arbitrary raw subsets do not enjoy the same claim.

## 1. Fixed data and orientation

Let V and W be categories, with an equivalence

\[
 e=(H:V\to W,\ L:W\to V,\ \eta:1_V\cong LH,\ \varepsilon:HL\cong1_W).
\]

Let G be the specified strict contravariant group-valued system on W. No coefficient group is assumed commutative, and restriction homomorphisms need not be invertible except where the input arrow is an isomorphism. Define the pulled-back system

\[
 (H^*G)_v=G_{Hv},\qquad (H^*G)(f)=G(Hf).
\]

The coefficient systems on the two categories are related by this actual pullback. Two unrelated systems are not silently declared equivalent. All size bounds are the universes in the Lean source.

The unframed cocycle groupoid K_G(W) is the existing `GaugeObject ∅` construction. Its objects and arrows retain their original meanings:

\[
 c_{1_w}=1,\qquad c_{gf}=c_f f^*(c_g),
\]
\[
 (a\cdot c)_f=a_wc_f[f^*(a_{w'})]^{-1}.
\]

## 2. Pullback retains actual gauge witnesses

For any functor H, not necessarily an equivalence, define

\[
 (H^*c)_f=c_{Hf},\qquad (H^*a)_v=a_{Hv}.
\]

These formulas define an actual functor

\[
 H^*:K_G(W)\longrightarrow K_{H^*G}(V).
\]

Identity labels, cocycle multiplication, gauge targets, and functor identity/composition laws are checked. The normalized trivial cocycle is preserved.

**Lean:** `GroupViewSystem.reindex`, `reindexCocycle`, `reindexFunctor`, `reindex_trivial` in `ViewPullback.lean`.

## 3. Equivalence theorem, with the inverse constructed

For the supplied equivalence e, put

\[
 t_w=\varepsilon_w^{-1}:w\longrightarrow HLw.
\]

For a cocycle k on V with coefficients H*G, construct its return to W by

\[
 (Qk)_f=t_w^*(k_{Lf}),\qquad
 (Qb)_w=t_w^*(b_{Lw}).
\]

The coefficient transport t_w* is essential: k_{Lf} initially lies in G_{HLw}, not in G_w. Naturality supplies

\[
 t_w^*( (HLf)^*x)=f^*(t_{w'}^*x),
\]

which proves the returned cocycle and gauge equations.

The comparison QH*c -> c has gauge labels c_{t_w}. The comparison H*Qk -> k has gauge labels k_{eta_v}. The triangle law H(eta_v)=epsilon_{Hv}^{-1} identifies the actual coefficient transports in the second comparison. Both comparisons are proved natural on all gauge arrows.

The constructed result is

\[
 \boxed{K_G(W)\simeq K_{H^*G}(V).}
\]

This is an actual Lean equivalence of categories/groupoids. Its forward functor is proved equal to the explicit pullback functor. It is not merely a bijection of isomorphism classes.

**Lean:** `returnCocycle`, `returnFunctor`, `globalComparisonIso`, `localComparisonIso`, `reindexEquivalence`, `reindex_isEquivalence` in `ViewEquivalence.lean`.

## 4. Isomorphisms, automorphisms, and unframed obstruction

For every two cocycles c,d, Lean constructs

\[
 \operatorname{Hom}(c,d)\cong\operatorname{Hom}(H^*c,H^*d),
\]

whose forward map is actual pullback of the gauge values. The functor preserves identities and composition. Thus automorphisms are retained, not discarded by an orbit quotient.

In the already defined unframed orbit sets,

\[
 \boxed{[H^*c]=[H^*d]\iff[c]=[d].}
\]

In particular,

\[
 \boxed{[H^*c]=[1]\iff[c]=[1].}
\]

This is invariance of the unframed obstruction to trivialization. It is not a new theorem about every prescribed framing domain: those would require correspondingly transported partial data and additional comparison statements.

**Lean:** `reindexHomEquiv`, `reindexHomEquiv_apply`, `reindex_class_eq_iff`, `reindex_neutral_iff`.

## 5. The strict ambient section space is invariant too

For any set-valued view system F on W, retain the actual definition

\[
 \Gamma(F)=\{x\in\prod_wF_w:\ f^*x_{w'}=x_w\}.
\]

Pullback reads the same coordinates:

\[
 (H^*x)_v=x_{Hv}.
\]

The inverse is explicit:

\[
 (Ry)_w=F(t_w)(y_{Lw}).
\]

The first inverse identity is section coherence along t_w. The second is section coherence along eta_v, together with the triangle identity. Hence

\[
 \boxed{\Gamma(F)\cong\Gamma(H^*F).}
\]

Existence and the subsingleton property are both preserved and reflected. The same equivalence is instantiated for the existing twisted systems T_c, retaining their actual section types and evaluations.

**Lean:** `ViewSystem.viewEquivalence`, `recover_reindex`, `reindex_recover`, `ambient_nonempty_iff`, `ambient_subsingleton_iff`; `GroupViewSystem.reindexTwistedSections` in `SectionViewEquivalence.lean`.

## 6. Patches require an explicit representational condition

For a raw subset S of objects, categorical equivalence does not imply that inverse image captures every representative in S. Define

\[
 \operatorname{IsoClosed}(S)\iff
 (a\cong b\ \land\ a\in S)\Longrightarrow b\in S.
\]

Such a patch includes all isomorphic representatives of every view it contains. This is a sufficient condition for the comparisons below, not a claim of necessity in every individual example.

Let P_sat(V) be the inclusion poset of these patches. The construction is an actual order isomorphism

\[
 \boxed{H^{-1}:P_{\mathrm{sat}}(W)\cong_o P_{\mathrm{sat}}(V),}
\]

with inverse L^{-1}. Both inverse equations use the unit/counit isomorphisms and closure under isomorphism.

For the actual composition-cover predicate from v0.14,

\[
 \operatorname{Cov}_W(S,(U_i))\iff
 \forall(w\xrightarrow f w'\xrightarrow g w''),\
 \{w,w',w''\}\subseteq S\Longrightarrow
 \exists i:\{w,w',w''\}\subseteq U_i.
\]

Any view functor preserves covers by inverse image. If S and all U_i are isomorphism-closed and H belongs to the supplied equivalence, Lean proves reflection too:

\[
 \boxed{\operatorname{Cov}_V(H^{-1}S,(H^{-1}U_i))
 \iff\operatorname{Cov}_W(S,(U_i)).}
\]

No assertion of cover reflection for arbitrary subsets is used.

**Lean:** `CompositionSite.familyCovers_preimage`, `familyCovers_reflect`, `familyCovers_preimage_iff`, `saturatedPatchEquiv` in `ViewSiteTransport.lean`.

## 7. Actual stack values and restrictions agree on these patches

For an isomorphism-closed S, the functor between full subcategories

\[
 H_S:V|_{H^{-1}S}\longrightarrow W|_S
\]

is given an explicit inverse, unit, and counit. The inverse representative Lw lies in H^{-1}S because HLw is isomorphic to w. The coefficient systems in this restriction are definitionally the original restricted/pulled-back systems.

Applying the global groupoid theorem gives

\[
 \boxed{\mathfrak K_G(S)\simeq\mathfrak K_{H^*G}(H^{-1}S).}
\]

For S subset T, the forward comparison strictly commutes with patch restriction:

\[
 H_S^*\operatorname{res}_{T,S}
 =\operatorname{res}_{H^{-1}T,H^{-1}S}H_T^*.
\]

The existing v0.14 stack theorem applies to each of these coefficient systems on its own composition site. The new proof compares their values, restrictions, and covering families on the isomorphism-closed patch part. It does not package a standard morphism of sites or a global pseudonatural equivalence over both entire raw-subset sites. Those stronger interface constructions are not claimed to have been completed.

**Lean:** `ViewChange.patchEquivalence`, `GroupViewSystem.patchPullback_restrict`, `saturatedPatchCocycleEquivalence` in `PatchViewEquivalence.lean`.

## 8. An arbitrary-category duplication example and a real failure

Construct V^dup with objects (v,b), b in {false,true}, and

\[
 \operatorname{Hom}_{V^{\mathrm{dup}}}((v,b),(w,c))
 =\operatorname{Hom}_V(v,w).
\]

The functor v -> (v,false) is an equivalence, with inverse forgetting b. If V is nonempty, the forward map is not surjective on objects: it omits every (v,true). Nevertheless the proved cocycle and section equivalences apply to the entire system.

Now take the raw patch

\[
 S=\{(v,\mathrm{true}):v\in V\}.
\]

It is nonempty when V is, but its inverse image under the representative inclusion is empty. It is not closed under isomorphism, since (v,true) is isomorphic to (v,false).

This is not just a set-theoretic mismatch. For constant coefficients in any group H with an element a not equal to 1, the trivial cocycle on S has distinct constant gauge automorphisms labelled a and 1. Pullback to the empty patch identifies those arrows. Lean proves that this raw-patch pullback is **not faithful**, even though the original functor of whole view categories is an equivalence.

**Lean:** `ViewDuplication.equivalence`, `embed_not_surjective`, `missedPatch_preimage`, `missedPatch_not_isoClosed`, `raw_patch_pullback_not_faithful`, `cocycleEquivalence`, `sectionEquivalence`.

## 9. Evidence and exact boundary

Six new proof modules add 36 named theorems and 39 indexed constructions. The cumulative project contains 95 proof modules, 959 named theorems, and 524 indexed constructions. Counts include auxiliary statements; they are not novelty counts. All 89 v0.14 proof-module sources are retained unchanged.

The supplementary exact script `checks/computation/view_equivalence_exact.py` uses S3 permutation tables and finite relations. It checks four distinct inner-action coefficient systems over C2, 16 base cocycles, 96 duplicated cocycles, all 3,456 gauge actions, 2,304 Hom comparisons, 20,736 gauge-composition cases, and 3,456 candidate section pairs. It additionally tests every labelled preorder on at most three views, with 207 saturated patches and 6,374 covering-family comparisons. There are 46,160 assertions and four rejected stronger variants. This is finite implementation evidence, not the source of the arbitrary-category theorems.

**Established:** equivalence-relative invariance of the strict ambient section space and unframed nonabelian cocycle groupoid; explicit transported inverse; preservation and reflection of neutral classes; cover and restriction compatibility on isomorphism-closed patches; an actual gauge-level counterexample without saturation.

**Not established here:** invariance under all cofinal or arbitrary functors; an equivalence of the raw patch posets/sites; arbitrary independent coefficient changes; framed extension comparison under all domain choices; numerical isometry; a universal view doctrine; infinity-stacks; or an arithmetic correspondence.

The equivalence-of-categories machinery is standard. The pinned `Mathlib/CategoryTheory/Equivalence.lean` supplies the category-equivalence constructor, triangle law, and fully faithful interface. The project supplies the actual cocycle/gauge/section transports and patch comparisons for its existing model. No novelty claim is made for invariance of standard categorical constructions under equivalence.

The Lean compiler/kernel, pinned imported dependency cache, and standard axioms `propext`, `Classical.choice`, `Quot.sound` remain trusted. The verification receipt records the actual completed build status. No finite computation or declaration count replaces a universal proof.
