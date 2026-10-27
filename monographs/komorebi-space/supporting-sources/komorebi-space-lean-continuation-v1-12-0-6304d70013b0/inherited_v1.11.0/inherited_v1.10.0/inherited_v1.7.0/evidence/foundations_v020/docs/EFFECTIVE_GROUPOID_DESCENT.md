# Komorebi Space Theory: effective groupoid descent
## v0.13.0 · Komorebi P.

The stated v0.12 goal is closed for the existing strict group-valued coefficient system and composition-covered full view patches. Local cocycles may disagree literally on overlaps. Specified gauge isomorphisms, satisfying the triple-overlap law, are retained and glued. Restriction is proved to be an actual equivalence of groupoids. This is not a claim of arbitrary site descent, higher-stack construction, or arithmetic correspondence.

## 1. Ambient section space and the symmetry-retaining layer

For a chosen view category V and contravariant set-valued system F, the strict ambient realization space remains
\[
\mathfrak K(F)=\Gamma(F)=\{(x_v)_v: f^*x_w=x_v\text{ for every } f:v\to w\}.
\]
A view is an admissible representation/resolution context. Evaluation recovers the appearance at that view. The system and its arrows are input, not an intrinsically selected universal doctrine.

For groups G_v with homomorphisms f^*:G_w→G_v, the symmetry-retaining construction has coherent cocycles c as objects:
\[
c_{1_v}=1,\qquad c_{gf}=c_f f^*(c_g).
\]
A gauge a=(a_v)_v acts by
\[
(a\cdot c)_f=a_vc_f[f^*(a_w)]^{-1}.
\]
The existing unframed gauge groupoid is denoted K_G. Its arrows retain actual gauge witnesses and automorphisms. Its orbit set retains only isomorphism classes. This continuation uses the unframed groupoid, corresponding to the empty framing domain.

## 2. Covers and descent data

Fix subsets U_i of view objects, understood as full subcategories. Assume a composition cover:
\[
\forall(v\xrightarrow f w\xrightarrow g z),\quad
\exists i:\ v,w,z\in U_i.
\tag{1}
\]
This implies coverage of objects and individual arrows by inserting identities.

A descent datum D contains a patch cocycle c_i on each U_i and actual overlap gauges
\[
a_{ij}(v)\in G_v\quad(v\in U_i\cap U_j).
\]
They must satisfy, for overlap arrows f:v→w,
\[
c_j(f)=a_{ij}(v)c_i(f)[f^*a_{ij}(w)]^{-1},
\tag{2}
\]
and, on every triple overlap,
\[
a_{ik}(v)=a_{jk}(v)a_{ij}(v).
\tag{3}
\]
Lean derives a_ii=1 and a_ji=a_ij^{-1}; these conclusions are not separately assumed. Groups need not be abelian, and the restriction homomorphisms need not be invertible.

A morphism r:D→D' consists of local gauges r_i carrying c_i to c'_i, with
\[
r_j(v)a_{ij}(v)=a'_{ij}(v)r_i(v).
\tag{4}
\]
Composition is pointwise multiplication in the order “second times first,” and inversion is pointwise inversion. The resulting type has an actual Lean `Groupoid` instance.

**Lean:** `CocycleDescentData`, `change_self`, `change_reverse`, `CocycleDescentData.Hom`, its `Groupoid` instance.

## 3. Main theorem

Let DD(U;G) be this groupoid of descent data. The restriction functor sends a global cocycle to its restrictions with identity overlap gauges. Under (1), Lean constructs
\[
\boxed{\operatorname{Res}:K_G\simeq DD(U;G).}
\tag{5}
\]
The symbol means an equivalence of categories/groupoids, not literal equality or merely a bijection of orbit sets.

The principal Lean construction is
```
KomorebiSpace.GroupViewSystem.CocycleDescentData.descentEquivalence
```
with type
```
F.GaugeObject (∅ : Set V) ≌ F.CocycleDescentData U
```
and an explicit argument `h : CompositionCover U`.

Its forward functor is proved equal to the concrete restriction functor. Full faithfulness is proved using an explicit inverse on every Hom set. Essential surjectivity uses the constructed globalization below, rather than assuming a global object in the descent datum. The final packaging uses mathlib's standard `Functor.asEquivalence`.

## 4. Construction of the global cocycle

Choose a patch κ(v) containing each view v. Define a local frame
\[
b_i(v)=a_{\kappa(v),i}(v).
\]
Equation (3) gives
\[
b_j(v)=a_{ij}(v)b_i(v).
\tag{6}
\]
Normalize each local cocycle:
\[
\widetilde c_i(f)=b_i(v)^{-1}c_i(f)f^*(b_i(w)).
\tag{7}
\]
Substituting (2) and (6), in the written noncommutative order, proves
\[
\widetilde c_i(f)=\widetilde c_j(f)
\]
on overlap arrows. These are now *literally* matching patch cocycles. The v0.12 strict descent construction glues them to c. Composition coverage proves its multiplication law in a patch containing each composable pair.

The result includes the local identifications:
\[
b_i(v)c_f[f^*(b_i(w))]^{-1}=c_i(f),\qquad b_j=a_{ij}b_i.
\tag{8}
\]
They implement the specified overlap gauges, not just some unspecified equivalences.

**Lean:** `frame`, `frame_overlap`, `strictify`, `effectuate`, `effective`.

## 5. Correct uniqueness statement

An effectuation consists of a global cocycle c and the comparison gauges b_i satisfying (8). For two effectuations (c,b) and (c',b'), put
\[
g_v=b_i'(v)^{-1}b_i(v)
\tag{9}
\]
in any patch containing v. The overlap equations prove independence of the patch. This yields a global gauge c→c' satisfying
\[
b_i'g=b_i.
\tag{10}
\]
Every compatible comparison must satisfy (9), so it is unique. Comparisons compose coherently and the comparison of an effectuation with itself is the identity.

This does **not** mean that a global cocycle has no automorphisms, or that a representative is independent of all choices as a literal object. Uniqueness includes the condition that the comparison respect the fixed local identifications. Forgetting those identifications retains the usual automorphisms.

**Lean:** `Effectuation.exists_unique_comparison`, `comparisonIso`, `orbit_independent`, `comparisonHom_comp`, `effective_descent`.

## 6. Why all morphisms are retained

Between restrictions of global cocycles, the overlap gauges are identities. Equation (4) becomes r_j=r_i on intersections. The earlier gauge-descent theorem therefore gives a unique global gauge. The new code proves both inverse equations, hence an explicit Hom equivalence. This proves full faithfulness.

Conversely, (8) gives a morphism from the restricted globalization to D. Since the descent-data category is a groupoid, this is an isomorphism. Every D is consequently in the essential image. Full faithfulness and essential surjectivity yield (5).

**Lean:** `restrictedMatching`, `liftRestrictedHom`, `restrict_lift`, `lift_restrict`, `restrictionFullyFaithful`, `restrictionHomEquiv`, `restriction_essentially_surjective`, `restriction_isEquivalence`.

## 7. Noncommutative example and boundary test

Use four ordered views 0≤1≤2≤3, constant coefficients S3, and four proper patches U_i={0,1,2,3}\\{i}. Every composable triple is in a patch, although no patch contains all views. Local changes of frame are chosen so that on the overlap arrow 1→2:
\[
c_0(1\to2)=(01),\qquad c_3(1\to2)=(12).
\]
These labels are unequal. At view 1, with an intermediate patch 2, the overlap product obeys the required order; reversing it fails because (01) and (12) do not commute. The general gluing construction applies to these genuinely non-strict data. Its answer is compared by an actual isomorphism with an independently supplied benchmark.

A separate exact group-theoretic example shows why pairwise arrows are not enough. Let t=(01), and ask for frames b0,b1,b2 satisfying
\[
b_1=tb_0,\qquad b_2=tb_1,\qquad b_2=tb_0.
\]
The first two imply b2=b0, while the third would force t=1. Lean proves no such frames exist. The three proposed overlap gauges are individually invertible, but violate triple coherence.

**Lean:** `EffectiveDescentExamples.local_labels_differ`, `overlap_order_matters`, `exampleEquivalence`, `inconsistent_triple_no_frames`.

## 8. Verification contract

Five modules extend the v0.12 source tree. All 78 prior proof-module sources are unchanged. The new statements quantify over their actual arbitrary categories, group fibers, covers, and descent data; no finite computation replaces those quantifiers. The proof source contains no `sorry`, `admit`, or project-specific axiom.

The exact finite script `checks/computation/effective_descent_exact.py` independently enumerates all 216 constant-S3 chain cocycles and reconstructs each using all 81 reference choices. Its local frames are deterministic fixtures, not all possible frames. It checks noncommutative overlap laws, global cocycle laws, local identifications, independence and composition of comparison gauges, and four false-claim controls. One additional finite control shows that covering individual arrows need not cover a missing composition relation. The finite tests are supplementary implementation evidence.

See the delivery receipt and the current/fresh replay records for the completed compilation status. Lean's kernel/compiler, the pinned imported dependency cache, and the standard axioms `propext`, `Classical.choice`, `Quot.sound` remain in the trust boundary.

## 9. Scope

**Closed goal:** effective gluing up to specified coherent gauge isomorphisms, with a proved equivalence of the global and descent-data groupoids for composition covers.

**Not asserted:** a chosen Grothendieck topology with all axioms checked, arbitrary site descent or stackification, category-valued or infinity-categorical coefficients, normed descent estimates, a universal view doctrine, or any unrestricted local-global arithmetic correspondence. Earlier additive and analytic theories retain their own hypotheses.

The concepts of descent data, effective descent, and the full/faithful/essentially-surjective criterion are established mathematics. The Stacks Project, tags 02ZC and 0268, supplies the background definitions. This continuation is a checked integration with the concrete Komorebi cocycle groupoids; no novelty claim is made for the abstract descent principle.
