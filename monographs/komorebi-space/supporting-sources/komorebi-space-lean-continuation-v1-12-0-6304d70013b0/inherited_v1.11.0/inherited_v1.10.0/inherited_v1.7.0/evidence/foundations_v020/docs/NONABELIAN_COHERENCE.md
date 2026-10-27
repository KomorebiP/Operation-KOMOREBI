# Komorebi Space Theory: nonabelian coherence and framed extension
## v0.11.0 · Komorebi P.

This layer replaces the assumption of additive commutativity by arbitrary group coefficients. It constructs an actual groupoid of coherent cocycles and gauge changes, an independently defined pointed relative obstruction, and a classification of every nonempty twisted extension fiber. The old additive extension problem is recovered by a proved bridge.

This is not a general category-valued stack, a site-descent theorem, a higher category, or an arithmetic correspondence. The cocycles already satisfy coherence. The new obstruction measures whether a coherent transition system can be trivialized with specified local data; it is not a scalar norm of an arbitrary incoherent square.

## 1. Group-valued view data

Fix a category of views V, groups G_v, and homomorphisms
\[
f^*:G_w\longrightarrow G_v\qquad(f:v\to w)
\]
satisfying
\[
(1_v)^*=1,\qquad(g\circ f)^*=f^*g^*.
\]
No group is required to be abelian. No restriction map is required to be bijective. Universes are fixed by the declarations.

A cocycle is a family c_f in G_v with
\[
\boxed{c_{1_v}=1,\qquad c_{g\circ f}=c_f f^*(c_g).}
\tag{1}
\]
It gives an actual strict set-valued view system
\[
T_c(f)(x)=c_f f^*(x),
\qquad
T_c(f)T_c(g)=T_c(g\circ f).
\]
A twisted section is therefore a family satisfying
\[
\boxed{x_v=c_f f^*(x_w).}
\tag{2}
\]
The `ViewSystem.Ambient`, `Partial`, and `Extensions` types used here are the existing ones, not newly named substitutes.

**Lean:** `GroupViewSystem`, `Cocycle`, `twistedViews`, `twisted_coherent_iff` in `GroupViewSystems.lean`.

## 2. Gauge changes and the actual groupoid

A raw gauge is a family a in the product of the G_v. Define
\[
\boxed{(a\cdot c)_f=a_vc_f[f^*(a_w)]^{-1}.}
\tag{3}
\]
Lean proves that this is again a cocycle and that
\[
1\cdot c=c,\qquad a\cdot(b\cdot c)=(ab)\cdot c,
\qquad a^{-1}\cdot(a\cdot c)=c.
\]
It also constructs an equivalence between actual twisted section sets:
\[
\Gamma(T_c)\simeq\Gamma(T_{a\cdot c}),\qquad x\mapsto(a_vx_v)_v.
\tag{4}
\]

For a prescribed domain U define the based gauge group
\[
\boxed{\mathcal G_U=\{a\in\prod_vG_v:a_u=1\ (u\in U)\}.}
\]
The groupoid K_U(G) has cocycles as objects and arrows
\[
\operatorname{Hom}(c,d)=\{a\in\mathcal G_U:a\cdot c=d\}.
\]
Composition follows ordinary right-to-left group multiplication: an arrow a followed by b has label ba. The identity has label 1 and the inverse has label a^{-1}. All category and inverse laws are proved in a Lean `Groupoid` instance.

The orbit set is a different construction:
\[
\boxed{\mathcal H_U=Z^1(V;G)/\mathcal G_U.}
\tag{5}
\]
The notation Z^1 here refers to the explicitly defined cocycles (1); no general derived cohomology API is invoked. The distinguished point is [1]. A group operation on this orbit set is not asserted.

Lean proves
\[
[c]=[d]\iff\operatorname{Hom}(c,d)\ne\varnothing
\iff\operatorname{Iso}(c,d)\ne\varnothing.
\tag{6}
\]
Thus the orbit set classifies isomorphism classes, while the groupoid retains the actual equivalences and automorphisms.

**Lean:** `GaugeObject`, its `Groupoid` instance, `GaugeEquivalent`, `gaugeSetoid`, `Orbit`, `orbitClass_eq_iff`, `iso_nonempty_iff_class` in `CocycleGaugeGroupoid.lean`.

## 3. Automorphisms are not distinct solutions

The stabilizer is a genuine subgroup
\[
\operatorname{Stab}_U(c)=\{a\in\mathcal G_U:a\cdot c=c\}.
\]
Its membership condition is proved equivalent to
\[
\boxed{a_v=c_f f^*(a_w)c_f^{-1}.}
\tag{7}
\]
At the trivial cocycle this reduces to ordinary coherence, f^*(a_w)=a_v, together with a|_U=1.

Given one arrow a:c to d, there is an explicit equivalence
\[
\boxed{\operatorname{Stab}_U(c)\simeq\operatorname{Hom}(c,d),
\qquad h\mapsto ah,\qquad b\mapsto a^{-1}b.}
\tag{8}
\]
The Hom set is a torsor for the source stabilizer whenever nonempty. This is a standard groupoid principle, applied here to the actual gauge arrows. In particular, a unique isomorphism class does not imply a unique isomorphism witness.

**Lean:** `stabilizer`, `stabilizer_characterization`, `trivial_stabilizer_iff`, `morphismParameters`, `morphism_unique_iff_stabilizer`.

## 4. A relative pointed obstruction defined before solvability

Let s be a coherent partial section of T_c on U. Choose a raw family q with q|_U=s. Identity outside U gives one such raw family, without assuming global coherence.

Normalize by
\[
\boxed{c^q_f=q_v^{-1}c_f f^*(q_w).}
\tag{9}
\]
This is gauge transformation by q^{-1}. Its labels are 1 on every arrow with both endpoints in U, by the coherence of s.

Define
\[
\boxed{\mathfrak o_U(c,s)=[c^q]\in\mathcal H_U.}
\tag{10}
\]
If t is a second raw lift of s, then t^{-1}q belongs to the based gauge group and
\[
(t^{-1}q)\cdot c^q=c^t.
\]
Consequently (10) is independent of the raw lift.

### Nonabelian extension theorem
\[
\boxed{\mathfrak o_U(c,s)=[1]
\iff\operatorname{Ext}_U^{T_c}(s)\ne\varnothing.}
\tag{11}
\]

**Proof.** If b is based and b acts on c^q to give 1, then
\[
x_v=q_vb_v^{-1}
\]
satisfies (2) and agrees with s on U. Conversely, an extension x gives the based gauge b=x^{-1}q and trivializes c^q. Multiplication order is retained throughout; no commutativity is used.

This is an obstruction orbit built from actual labels and an actual equivalence relation. It is not a Boolean flag defined by whether a solution exists. The theorem does not supply a procedure for deciding orbit membership in an arbitrary infinite group.

**Lean:** `normalize`, `normalization_independent`, `normalized_class_neutral_iff`, `extensionOrbit`, `extensionOrbit_neutral_iff`, `extensionOrbit_independent`, `normalized_internal_edge` in `NonabelianExtension.lean`.

## 5. Classification of twisted extension fibers

Define the group of invisible coherent changes
\[
\boxed{H_U=\{h:f^*(h_w)=h_v\ \forall f,\quad h|_U=1\}.}
\tag{12}
\]
This group is not assumed abelian. It is explicitly identified with the stabilizer of the trivial cocycle.

Given one extension x_0 of s,
\[
\boxed{H_U\simeq\operatorname{Ext}_U^{T_c}(s),
\qquad h\mapsto x_0h,
\qquad x\mapsto x_0^{-1}x.}
\tag{13}
\]
All formulas are pointwise. For example,
\[
(x_0)_v^{-1}x_v
= [c_f f^*((x_0)_w)]^{-1}[c_f f^*(x_w)]
=f^*((x_0)_w^{-1}x_w).
\]
This cancellation is valid without commuting any factors.

The corresponding uniqueness criterion is
\[
\boxed{\exists!x\in\Gamma(T_c),\ x|_U=s
\iff\mathfrak o_U(c,s)=[1]\ \land\ H_U=\{1\}.}
\tag{14}
\]
The Lean statement uses `Subsingleton H_U`, equivalent to triviality because H_U is a group. Enlarging U reduces H_U.

Two different symmetry questions must not be conflated. Equation (13) parametrizes global trivializations of a fixed cocycle. Equation (8) parametrizes isomorphism witnesses between cocycles. The underlying cocycle may have nontrivial automorphisms even when its orbit is a single point in the coarse moduli set.

**Lean:** `invisible`, `invisibleStabilizerEquiv`, `extensionParameters`, `extensionParameters_coordinate`, `extensionParameters_inverse`, `unique_extension_iff`, `invisible_antitone` in `NonabelianExtensionFibers.lean`.

## 6. Exact comparison with the additive core

Let A be the previous `AdditiveViewSystem`. Replace each A_v by its multiplicative type tag and retain the same homomorphisms. Use the trivial cocycle.

The constructed equivalences identify its global and prescribed extension types with the existing additive types. Moreover,
\[
\boxed{\operatorname{toAdd}((1^q)_f)=f^*(q_w)-q_v=(\delta q)_f.}
\tag{15}
\]
Consequently,
\[
\boxed{\mathfrak o_U^{\rm nonab}(1,s)=[1]
\iff\mathfrak o_U^{\rm additive}(s)=0.}
\tag{16}
\]
This compares actual vanishing criteria. It does not claim that the entire nonabelian pointed orbit set is the old larger additive arrow-residual quotient.

**Lean:** `AdditiveViewSystem.multiplicativeViews`, `multiplicativeAmbientEquiv`, `multiplicativeExtensionsEquiv`, `normalization_is_additive_defect`, `orbit_neutral_iff_additive_zero` in `AdditiveCocycleBridge.lean`.

## 7. An exhaustive noncommutative loop model

Use the existing one-view category with C2 arrows, and constant group coefficients H. Every cocycle is determined by an involution p in H:
\[
c_1=1,\qquad c_\sigma=p,\qquad p^2=1.
\]
Lean constructs the equivalence between all these cocycles and the involutions of H. It proves
\[
\boxed{[c_p]=[c_q]\iff\exists a\in H:\ apa^{-1}=q,}
\tag{17}
\]
and identifies automorphism labels with the centralizer of p:
\[
a\in\operatorname{Stab}(c_p)\iff ap=pa.
\tag{18}
\]
Also,
\[
[c_p]=[1]\iff p=1.
\]
For p not equal to 1, the cocycle is valid coherent data, but its associated regular twisted set system has no global section: p x=x would force p=1. Nontrivial descent data and the absence of a global trivialization are therefore compatible statements.

Specialize to H=S3. The Lean proofs enumerate its involutions and establish exactly two orbit classes: the identity class and the transposition class. They are not isomorphic, despite having the same underlying local coefficient fibers. Automorphism arrows at the identity cocycle are explicitly parametrized by S3, and two of those arrows are proved not to commute. Framing the only view forces all allowed gauge changes to be identity.

**Lean:** `CocycleExamples.loopCocycleEquiv`, `loop_class_eq_iff_conjugate`, `loop_stabilizer_iff`, `involution_trivial_iff`, `trivialAutEquiv`, `actual_automorphisms_noncommute`, `same_local_fibers_inequivalent`, `s3_orbit_dichotomy`, `full_framing_gauge_unique`.

The finite S3 proofs use ordinary Lean `decide`, not `native_decide`, external computation axioms, or numerical extrapolation. The generic classification and obstruction theorems quantify over arbitrary group coefficients.

## 8. Independent computation

`checks/computation/nonabelian_cocycles_exact.py` is a separate implementation using exact permutation tables. It checks all four C2-to-S3 loop cocycles, 864 composable gauge triples, all 16 pairs of four listed S3 endomorphisms on a three-view chain, all 576 resulting generator-label cocycles, and all 24,768 coherent partial seeds over every subset of the three views.

It compares brute-force extension enumeration with based-gauge neutrality, independently checks fiber cardinalities and parametrizations, and checks raw-lift independence. It records 195,787 assertions and four rejected mutations. This is finite implementation evidence, not the source of the universal conclusions.

## 9. Status and limits

Six new modules contain 56 named theorem declarations and 41 indexed constructions. The cumulative sources contain 76 proof modules, 831 named theorems, and 399 indexed constructions. Counts include elementary and auxiliary lemmas, not discoveries.

The exact scope is strict group-valued view coefficients, a groupoid of coherent cocycles, relative gauge orbits, twisted set-valued extension fibers, and the stated additive bridge. Not established: arbitrary category-valued coherent sections, descent over a site, stackification, higher homotopies, a universal view doctrine, general nonabelian obstruction algorithms, topological or normed gauge estimates, or unrestricted arithmetic correspondences.

The new groupoid is one step beyond coarse sets of equivalence classes. It is not being called the complete higher Komorebi space.

## 10. Established background

The groupoid Hom-torsor principle in Section 3 is standard; see the Stacks Project, Lemma 39.17.4, tag 04Q2. The distinction between an action groupoid and a quotient stack is also standard; see the Stacks Project, Definition 78.20.1, tag 044Q. No novelty claim is made for those general constructions or for involutions classified up to conjugacy.

The contribution of this continuation is the explicit, kernel-checked integration with the project's view systems, relative extension questions, and earlier additive obstruction.
