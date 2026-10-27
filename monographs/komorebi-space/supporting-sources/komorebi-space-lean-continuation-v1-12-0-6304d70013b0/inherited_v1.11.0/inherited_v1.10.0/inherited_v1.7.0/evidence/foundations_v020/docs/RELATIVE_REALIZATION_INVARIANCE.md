# Komorebi Space Theory: invariant relative realizations
## v0.16.0 · Komorebi P.

This extension transports a prescribed reconstruction problem across equivalent view presentations. It proves equivalence of the existing section-extension sets, a multiplicative equivalence of the existing nonabelian ambiguity groups, and equivalence of newly defined identified-boundary realization groupoids. A counterexample shows why the old operation of freezing every representative's gauge value is not itself presentation-independent.

The seven new modules are a continuation of the actual v0.15 constructions. No normed stability theorem, arbitrary change of view doctrine, or higher-stack comparison is asserted here. The results below are relative to the explicit coefficient system, restriction functors, equivalence, and domain hypotheses.

## 1. Equivalent views and prescribed section data

Let \(e=(H:\mathcal V\to\mathcal W,L,\eta,\varepsilon)\) be a category equivalence, and let \(F:\mathcal W^{op}\to\mathbf{Set}\) be the existing strict view system. Let \(U\subseteq\operatorname{Ob}\mathcal W\) be closed under isomorphism:
\[
 w\in U,\quad w\cong w'\quad\Longrightarrow\quad w'\in U.
\]
Put \(U'=H^{-1}U\). For a coherent partial section \(s\in\Gamma_U(F)\), its pullback is
\[
 (H^*s)_v=s_{Hv}\qquad(v\in U').
\]
The formalization uses the original `ViewSystem.Partial` and `ViewSystem.Extensions`, not replacement notions of solutions. It constructs
\[
 \boxed{\operatorname{Ext}^{F}_U(s)\simeq
 \operatorname{Ext}^{H^*F}_{U'}(H^*s).}
 \tag{1}
\]
The forward map is \(x\mapsto(x_{Hv})_v\). The inverse uses the actual inverse-counit arrow
\[
 t_w=\varepsilon_w^{-1}:w\longrightarrow HLw,
 \qquad (Ry)_w=F(t_w)(y_{Lw}).
\]
If \(w\in U\), isomorphism closure gives \(HLw\in U\), so the prescribed equation for \(y\) applies at \(Lw\). Coherence of \(s\) along \(t_w\) then proves \((Ry)_w=s_w\). The previously proved section inverse identities establish both inverse identities of (1).

Existence and the subsingleton property are separately preserved and reflected. Saturation is a sufficient general hypothesis here, not a claim that every unsaturated domain fails.

**Lean:** `ViewSystem.reindexPartial`, `reindexExtension`, `recoverExtension`, `relativeViewEquivalence`, `relative_nonempty_iff`, `relative_subsingleton_iff`.

## 2. Nonabelian feasibility and ambiguity are both retained

Let \(G\) be the existing strict system of groups. Its restriction homomorphisms need not be invertible, and the groups need not be abelian. Fix a coherent cocycle \(c\) and its actual twisted view system
\[
 T_c(f)(x)=c_f f^*(x).
\]
Equation (1) is instantiated on this system, producing an equivalence of its prescribed extension sets. By the old independently defined extension-orbit theorem,
\[
 \boxed{
 \mathfrak o_U(c,s)=[1]
 \iff
 \mathfrak o_{U'}(H^*c,H^*s)=[1].}
 \tag{2}
\]
This is a comparison of the relative feasibility criterion for the transported problem. It is **not** an equivalence of all based-gauge orbit sets.

The existing ambiguity group is
\[
 \mathcal H_U=
 \{h\in\prod_w G_w:\ f^*(h_{w'})=h_w,\ h|_U=1\}.
\]
The extension constructs an actual multiplicative equivalence
\[
 \boxed{\mathcal H_U\simeq_*\mathcal H_{U'}^{H^*G}.}
 \tag{3}
\]
Its maps are \(h\mapsto(h_{Hv})_v\) and \(a\mapsto(t_w^*a_{Lw})_w\). Both inverse identities, boundary identities, and the multiplication law are proved.

If one extension \(x_0\) is chosen, the old parametrization \(h\mapsto x_0h\) commutes with pullback:
\[
 H^*(x_0h)=(H^*x_0)(H^*h).
\]
Consequently the entire existence-and-uniqueness statement is invariant, rather than only a count of solutions. This supplies no distinguished extension when the ambiguity group is nontrivial.

**Lean:** `GroupViewSystem.relativeTwistedEquivalence`, `relative_neutral_iff`, `invisibleViewEquivalence`, `extensionParameters_reindex`, `relative_unique_iff`.

## 3. A boundary must include its comparison isomorphism

For groupoids \(\mathcal C,\mathcal D\), a functor \(R:\mathcal C\to\mathcal D\), and a fixed object \(b\in\mathcal D\), define
\[
 \boxed{\mathcal E_b(R)=\{(x,\phi):x\in\mathcal C,\ \phi:Rx\xrightarrow{\sim}b\}.}
 \tag{4}
\]
A morphism from \((x,\phi)\) to \((y,\psi)\) is an actual arrow \(a:x\to y\) such that
\[
 \boxed{\psi\,R(a)=\phi.}
 \tag{5}
\]
The Lean record `MarkedRealization` stores an arrow `identify`; this is automatically an isomorphism because the target is a groupoid. The full groupoid instance is constructed, including inverses. The source does not invoke or assume a higher-category interface.

This is the usual explicit identified-boundary, or groupoid homotopy-fiber, construction. Its ordinary groupoid structure and comparison theorems are proved here. A general bicategorical universal-property interface is not additionally claimed.

Nonemptiness is characterized by actual essential-image membership:
\[
 \mathcal E_b(R)\ne\varnothing
 \iff \exists x\in\mathcal C:\ Rx\cong b.
\]
For an endomorphism of \((x,\phi)\), condition (5) is equivalent to
\[
 R(a)=1_{Rx}.
\]
Thus these automorphisms are precisely the ones invisible at the identified boundary. They need not be trivial for a general restriction functor.

**Lean:** `MarkedRealization`, its `Groupoid` instance, `nonempty_iff`, `endomorphism_condition`, `homEquiv`.

## 4. Weakly commuting squares transport the whole realization groupoid

Suppose
\[
 \begin{array}{ccc}
 \mathcal C&\xrightarrow{E}&\mathcal C'\\
 R\downarrow&&\downarrow R'\\
 \mathcal D&\xrightarrow{K}&\mathcal D'
 \end{array}
 \qquad
 \sigma:KR\xRightarrow{\sim}R'E.
\]
The square need not commute literally. Define
\[
 \boxed{
 (x,\phi)\longmapsto
 (Ex,\ K(\phi)\sigma_x^{-1}),
 \qquad a\longmapsto E(a).}
 \tag{6}
\]
Naturality of \(\sigma\) proves the boundary equation. Lean constructs this functor and proves that it is an equivalence whenever \(E\) and \(K\) are equivalences:
\[
 \boxed{\mathcal E_b(R)\simeq\mathcal E_{Kb}(R').}
 \tag{7}
\]

### Proof obligations are derived

Full faithfulness is proved by lifting an arrow through \(E\), then reflecting its boundary equation through faithful \(K\). Essential surjectivity starts from \((y,\psi)\), chooses \(x\) and \(i:Ex\cong y\), and lifts
\[
 \psi\,R'(i)\,\sigma_x:KRx\longrightarrow Kb
\]
through full \(K\). The lifted arrow supplies \(\phi\). The arrow \(i\) then gives an isomorphism from the image of \((x,\phi)\) to \((y,\psi)\). No preimage in the realization groupoid is assumed.

The final equivalence is packaged using mathlib's `Functor.asEquivalence`. The forward functor is proved to be (6). An explicit Hom equivalence retains boundary-preserving automorphisms and all comparison witnesses. This is not a bijection of raw object types.

**Lean:** `MarkedRealization.transport`, `transportFullyFaithful`, `chosenPreimage`, `chosenComparison`, `transport_essentially_surjective`, `transportEquivalence`, `transportHomEquiv`.

## 5. Application to the actual Komorebi patch restriction functors

For full patches \(U\subseteq T\) and a boundary cocycle object \(b\in\mathfrak K_G(U)\), use the actual v0.14 restriction functor:
\[
 \operatorname{res}_{T,U}:\mathfrak K_G(T)\to\mathfrak K_G(U).
\]
Define
\[
 \mathcal E_{U,T}^{G}(b)
 =\mathcal E_b(\operatorname{res}_{T,U}).
\]
The v0.15 patch pullback comparison strictly commutes with restriction. For isomorphism-closed \(U,T\), both horizontal functors in that square are the previously constructed equivalences. Applying (7) proves
\[
 \boxed{
 \mathcal E_{U,T}^{G}(b)
 \simeq
 \mathcal E_{H^{-1}U,H^{-1}T}^{H^*G}(H^*b).}
 \tag{8}
\]
The image of a realization is its actual pulled-back cocycle and actual pulled-back boundary identification. Nonemptiness is preserved and reflected. Every Hom set has the corresponding bijection. The coefficient systems are actually pulled back, not independently chosen and declared equivalent.

**Lean:** `GroupViewSystem.RelativeRealization`, `relativeSquare`, `relativePullback`, `relativePullback_identification`, `relativeCocycleEquivalence`, `relative_cocycle_nonempty_iff`, `relativeCocycleHomEquiv`.

## 6. The boundary object itself may be replaced by an isomorphic one

For \(j:b\cong b'\), composition with \(j\) gives
\[
 (x,\phi)\longmapsto(x,j\phi),
 \qquad
 \boxed{\mathcal E_b(R)\simeq\mathcal E_{b'}(R).}
\]
The inverse and natural round-trip isomorphisms are constructed. For \(R=1_{\mathcal D}\), the realization groupoid has the center \((b,1_b)\). Between any two objects \((x,\phi),(y,\psi)\) there is exactly one compatible arrow:
\[
 a=\psi^{-1}\phi.
\]
Thus this identity fiber is contractible as a groupoid, even if it contains many raw object representatives. It is not asserted to be a singleton as a Lean type.

**Lean:** `MarkedRealization.changeBoundary`, `boundaryEquivalence`, `identityCenter`, `identityFiberArrow_unique`, `identityFiber_unique_hom`.

## 7. Checked failure of literal full-framing invariance

For an arbitrary nonempty view category \(\mathcal V\), duplicate each view into \((v,0),(v,1)\), retaining the original morphisms. The embedding \(H(v)=(v,0)\) is the existing categorical equivalence.

Use constant coefficients in any group containing \(g\ne1\). Give copy 0 frame 1 and copy 1 frame \(g\), and let \(c^g\) be the gauge transform of the trivial cocycle by these frames. Its label on the isomorphism from \((v,1)\) to \((v,0)\) is \(g\), so
\[
 c^g\ne1.
\]
Its pullback along \(H\) is the trivial cocycle.

Now use the old based-gauge groupoids with **every view framed**. All allowed gauges are pointwise identity. Therefore distinct cocycles cannot be connected by an arrow. Nevertheless their pulled-back objects have an identity arrow between them. The actual framed pullback is proved not full, and hence not an equivalence:
\[
 \boxed{H^*_{\mathrm{fully\ framed}}\text{ need not be an equivalence}.}
\]
Both domains are the whole category and hence saturated. The failure is not caused by an unsaturated patch; it is caused by retaining independent frozen trivializations at redundant representatives.

This does not invalidate the old based-gauge definitions. It identifies extra representative-dependent information in that problem. The identified-boundary construction is a different, precisely stated relative problem, for which (8) is proved. It does not silently equate the two notions.

**Lean:** `GroupViewSystem.reindexFramedFunctor`, `fully_framed_equivalent_iff`, `FramingBoundaryExamples.copyCocycle_ne_trivial`, `copyCocycle_pullback`, `full_framing_not_full`, `full_framing_not_equivalence`.

## 8. Independent finite audit

`checks/computation/relative_realizations_exact.py` uses exact S3 permutation tables. It checks 72 duplicated two-view twisted systems using three selected coefficient homomorphisms, including a noninvertible trivial homomorphism. It enumerates all coherent partial seeds over all four saturated domains of these fixtures, comparing direct extension enumeration with independently enumerated based-gauge neutrality.

A second suite checks 108 weakly commuting squares and 3,888 marked Hom comparisons. A third checks all four C2-to-S3 loop labels, all six second-copy boundary frames, 864 marked objects, and 31,104 full-boundary comparisons. Negative controls cover the inverse in the comparison formula, full-framing invariance, nonuniqueness, and the loss of an unsaturated prescription. All arithmetic is exact; no random sampling or floating-point tolerance is used.

These are supplementary bounded implementation checks. The universally quantified conclusions come from the Lean proof terms. The fixtures do not enumerate every possible finite coefficient system or every possible frame.

## 9. Exact scope and standard background

Closed in this block: relative section-extension invariance on saturated prescribed domains; invariance of the nonabelian ambiguity group and its extension action; identified-boundary groupoids and their equivalence under weakly commuting equivalence squares; instantiation on the actual Komorebi patch restrictions; boundary-representative invariance; and a counterexample for literal full framing.

Not closed: a complete standard pseudonatural equivalence of relative stacks over sites; an isomorphism of the entire old additive raw-residual quotients; invariance under arbitrary or merely cofinal functors; quantitative stability of descent; arbitrary infinite-detail synthesis; a universal view doctrine; higher stacks; or unrestricted arithmetic correspondence. No topology or norm is added to the new realization groupoids.

The identified-boundary groupoid and its invariance under equivalence are established category theory. Background: Stacks Project, Categories, Section 4.31 (2-fibre products), and Section 4.32, tag 02XG. The project contribution here is their explicit implementation and connection to the existing Komorebi patch groupoids and prescribed section problems, together with the precise framing boundary. No novelty claim is made for the general category-theoretic principle.

Formal scope is governed by the Lean statements and their hypotheses. The compiler/kernel, pinned imported cache, and standard axioms `propext`, `Classical.choice`, and `Quot.sound` remain in the trust boundary. The current and fresh build records govern verification status; declaration counts do not establish mathematical truth or novelty.
