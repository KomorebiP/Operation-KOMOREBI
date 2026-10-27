# Komorebi Space Theory: ambient sections and extension obstructions
## v0.9.0 · Komorebi P.

The new layer treats a global realization as coherent data across a chosen category of views. It formalizes strict **set-valued** sections, gluing under an explicit transition-cover hypothesis, correspondence fibers, and a concrete additive obstruction to extension. It connects these constructions to the existing resolution points and repaired Banach-tower maps.

This is not a construction of an infinity category, a general moduli stack, homotopy descent, or an arithmetic correspondence. Those are extensions of the research program, not conclusions of these proofs.

## 1. View systems: one base, multiple kinds of transition

Fix a category \(\mathcal V\), with all universes fixed as in the Lean declarations. A view system consists of sets \(F_v\) and restrictions
\[
 f^*:F_w\longrightarrow F_v \qquad(f:v\to w)
\]
with
\[
 (1_v)^*=1_{F_v},\qquad (g\circ f)^*=f^*g^*.
\]
Thus it has the data and laws of a contravariant set-valued functor. The Lean record is `ViewSystem`; its laws are fields checked for every concrete instance.

The local total space and the ambient section space play different roles:
\[
 \mathcal E=\int_{\mathcal V}F
 \quad\text{organizes individual viewwise appearances},\qquad
 \Gamma(F)\quad\text{organizes coherent full families}.
\]
The category-of-elements notation in this paragraph is explanatory; the Lean layer directly implements the families and their coherence rather than a separate Grothendieck-construction category.

A view can encode both resolution and representation. The abstract category does not require a product decomposition or force all view changes to be invertible. Which arrows are admissible is still part of the mathematical input.

Define the ambient section set
\[
 \boxed{\Gamma(F)=\left\{x\in\prod_{v\in\mathcal V}F_v:
     f^*(x_w)=x_v\text{ for every }f:v\to w\right\}.}
 \tag{1}
\]
This is a subset with a coherence proof, not an unchecked list of appearances.

Evaluation is
\[
 \operatorname{ev}_v:\Gamma(F)\to F_v,\qquad x\mapsto x_v.
\]
Lean proves
\[
 \boxed{\bigl(\forall v,\operatorname{ev}_v(x)=\operatorname{ev}_v(y)\bigr)
      \Longrightarrow x=y.}
 \tag{2}
\]
Individual evaluations need not be injective or surjective. Joint determination is the proved conclusion.

**Lean:** `ViewSystem.Ambient`, `evaluate`, `evaluations_jointly_injective`, `evaluation_coherent`.

### Universal property

If a set \(T\) has maps \(c_v:T\to F_v\) with \(f^*c_w=c_v\), there is a unique map
\[
 \boxed{c:T\to\Gamma(F),\qquad\operatorname{ev}_v c=c_v.}
 \tag{3}
\]
The lift is explicit: \(c(t)_v=c_v(t)\). Natural families of maps between view systems also induce maps between ambient sections, preserving identities and composition.

**Lean:** `ViewSystem.Cone.exists_unique_lift`, `Morphism.onAmbient`, `onAmbient_comp`.

### A useful warning about including a global view

Suppose the view category has a specified terminal object \(t\), with its unique arrows \(v\to t\). Lean constructs
\[
 \boxed{\Gamma(F)\simeq F_t.}
 \tag{4}
\]
The inverse sends \(a\in F_t\) to its restrictions at every view. Including an already-global terminal fiber can therefore recover that fiber directly. It does not prove that a partial collection of local data extends to the terminal fiber.

**Lean:** `ViewSystem.terminalEvaluationEquiv`, `terminalEvaluation_coordinate`.

## 2. Partial realizations and a precise gluing condition

For \(U\subseteq\operatorname{Ob}(\mathcal V)\), define \(\Gamma_U(F)\) using the full subcategory on \(U\). A partial section contains all coherence conditions whose endpoints lie in \(U\). Restriction is defined for \(U\subseteq W\).

For \(s\in\Gamma_U(F)\), define its extension set
\[
 \boxed{\operatorname{Ext}_U(s)
   =\{x\in\Gamma(F):x|_U=s\}.}
 \tag{5}
\]
It can be empty or nonempty. No existence assertion is hidden in the definition.

For patches \((U_i)_{i\in I}\), a matching family is
\[
 (s_i),\qquad s_i\in\Gamma_{U_i}(F),\qquad
 s_i(v)=s_j(v)\quad(v\in U_i\cap U_j).
\]
Require the **transition-cover condition**
\[
 \boxed{\forall(f:v\to w),\ \exists i:\ v,w\in U_i.}
 \tag{TC}
\]
Since identity arrows are included, (TC) also covers every view object. It is a sufficient combinatorial hypothesis on full-subcategory patches, not a declared Grothendieck topology.

### Gluing theorem

Under (TC), Lean constructs
\[
 \boxed{\Gamma(F)\simeq\operatorname{Match}(F,(U_i)).}
 \tag{6}
\]
In particular, each fixed matching family has a unique global extension.

**Proof.** At each view choose a patch containing it and take that patch's value. Agreement on overlaps makes this choice irrelevant. For each arrow, choose a patch containing both endpoints; coherence inside that patch proves global coherence. Covering the objects alone suffices for uniqueness, but not for this existence argument.

**Lean:** `ViewSystem.gluingEquiv`, `Matching.exists_unique_glue`, `restrict_jointly_injective`.

### Checked failure of an object-only cover

Take two views \(0\to1\) and constant Boolean fibers with identity restriction. The singleton patches \(\{0\}\), \(\{1\}\) cover all objects. The local value false at 0 and true at 1 agree on their empty overlap, but a global section would require the two values to be equal. Lean proves that this matching family has no glue and that the patches fail (TC).

**Lean:** `ViewBoundaryExamples.singleton_objectCover`, `singleton_matching_not_gluable`, `singleton_not_transitionCover`.

## 3. Correspondences as coherent bridge sections

Fix natural maps of view systems
\[
 F\xleftarrow{p}M\xrightarrow{q}G
\]
and ambient sections \(a\in\Gamma(F)\), \(b\in\Gamma(G)\). At view \(v\), let
\[
 B_{a,b}(v)=\{m\in M_v:p_v(m)=a_v,\ q_v(m)=b_v\}.
\]
Naturality of \(p,q\) and coherence of \(a,b\) give actual restriction maps for \(B_{a,b}\).

Define the global bridge set
\[
 \mathfrak B(a,b)=\{z\in\Gamma(M):\Gamma(p)(z)=a,\ \Gamma(q)(z)=b\}.
\]
Lean constructs the explicit equivalence
\[
 \boxed{\Gamma(B_{a,b})\simeq\mathfrak B(a,b).}
 \tag{7}
\]
One direction forgets the local fiber-membership proofs and retains the coherent underlying family. The other attaches the coordinatewise consequences of the global projection equations. These constructions are inverse.

**Lean:** `ViewSystem.bridgeSystem`, `GlobalBridge`, `bridgeEquiv`, `bridgeEquiv_coordinate`.

Combining (6) and (7), under (TC),
\[
 \boxed{\mathfrak B(a,b)\ne\varnothing
   \iff\operatorname{Match}(B_{a,b},(U_i))\ne\varnothing.}
 \tag{8}
\]
A fixed matching family determines its global bridge uniquely. The matching **correspondence objects** themselves are glued, with both projected ambient sections unchanged.

**Lean:** `glueBridge`, `glueBridge_left`, `glueBridge_right`, `bridge_exists_iff_matching`, `bridge_glue_unique`.

These are ordinary set-theoretic fibers, not homotopy fibers. Multiple bridges may exist for the same pair if different matching families are allowed.

## 4. Nonempty fibers and invertible transports need not give a section

Construct a one-object category whose arrows form \(C_2\). Let its nonidentity arrow act on \(\{\mathrm{false},\mathrm{true}\}\) by negation. The pullback functors satisfy identity and composition exactly.

The fiber is nonempty and every transport is bijective. Nevertheless,
\[
 \Gamma(F)=\{x:x=\neg x\}=\varnothing.
\]
The same example, with both projections to the terminal one-point system, has nonempty local bridge fibers but no global bridge.

Lean also proves that the nonidentity transport is bijective and is not the identity map.

**Lean:** `ViewBoundaryExamples.swap_fibers_nonempty`, `swap_transports_bijective`, `swap_no_ambient`, `bijective_not_identity`, `local_bridges_nonempty`, `no_global_bridge`.

This separates three statements:
\[
 \boxed{\text{fiberwise existence}\ne\text{invertible transport}\ne
 \text{existence of a coherent choice}.}
\]
It also warns against conflating equivalence with trivial holonomy.

## 5. An independently defined additive extension obstruction

Now let every fiber \(A_v\) be an abelian group and every \(f^*:A_w\to A_v\) an additive homomorphism. Set
\[
 E=\prod_v A_v,\qquad
 R=\prod_{(f:v\to w)} A_v.
\]
Define the actual compatibility differential
\[
 \boxed{(\delta x)_f=f^*(x_w)-x_v.}
 \tag{9}
\]
Lean proves additivity and
\[
 (\delta x)_{1_v}=0,
\]
\[
 \boxed{(\delta x)_{g\circ f}
   =f^*((\delta x)_g)+(\delta x)_f.}
 \tag{10}
\]
Furthermore,
\[
 \delta x=0\iff x\in\Gamma(A).
\]
No norm, convergence, or putative universal cohomology group is used.

For a prescribed domain \(U\), define
\[
 p_U:E\to\prod_{v\in U}A_v,\qquad p_U(x)=x|_U.
\]
Corrections must vanish on \(U\), so their possible defects form
\[
 \delta(\ker p_U)\subseteq R.
\]
For \(s\in\Gamma_U(A)\), choose any raw extension \(\widetilde s\in E\); the implementation uses zero outside \(U\). Define
\[
 \boxed{\mathfrak o_U(s)=[\delta\widetilde s]
   \in R/\delta(\ker p_U).}
 \tag{11}
\]
If \(\widetilde s'\) is another extension, then
\[
 p_U(\widetilde s-\widetilde s')=0,
 \qquad \delta\widetilde s-\delta\widetilde s'
    \in\delta(\ker p_U).
\]
Hence (11) is independent of the raw extension. The quotient is defined algebraically before testing extension existence.

### Extension theorem

Lean proves
\[
 \boxed{\mathfrak o_U(s)=0
    \iff\operatorname{Ext}_U(s)\ne\varnothing.}
 \tag{12}
\]

**Proof.** Vanishing means \(\delta\widetilde s=\delta h\) for some \(h\in\ker p_U\). Then \(x=\widetilde s-h\) is coherent and still restricts to \(s\). Conversely, if coherent \(x\) extends \(s\), the correction \(h=\widetilde s-x\) is in \(\ker p_U\) and has the required differential.

**Lean:** `AdditiveViewSystem.differential`, `differential_comp`, `extensionClass`, `extensionClass_independent`, `extensionClass_zero_iff`.

This theorem instantiates the old constrained-correction quotient with an actual view-coherence differential. It is not the circular definition "obstruction vanishes exactly when extension exists." It also supplies no general decision procedure for quotient membership. Calling this quotient \(H^2\) without a specified complex and degree convention would be unjustified.

## 6. A nontrivial prescribed section: exactly the even integers extend

Take the two-view category \(0\to1\), with
\[
 A_0=A_1=\mathbb Z,\qquad f^*(m)=2m.
\]
Prescribe \(s_0=k\) at \(U=\{0\}\). A coherent global extension is exactly a pair
\[
 (k,m),\qquad k=2m.
\]
Through the actual quotient (11), Lean proves, for every integer \(k\),
\[
 \boxed{\mathfrak o_{\{0\}}(k)=0
    \iff\exists m\in\mathbb Z,\ k=2m.}
 \tag{13}
\]
In particular, the seed 1 is obstructed, while the nonzero seed 2 extends as \((2,1)\).

**Lean:** `SectionExtensionExample.extensionClass_zero_iff_even`, `odd_seed_obstructed`, `nonzero_seed_extends`.

The universal statement is a Lean proof. Checking a bounded interval of integers is only a supplementary test.

## 7. Agreement with the previous resolution and Banach-tower core

For an existing sequential resolution \(X\), use the view category \(\mathbb N\) with arrows \(i\to j\) when \(i\le j\), and
\[
 F_X(n)=X_n,\qquad (i\to j)^*=\rho^X_{i,j}.
\]
The new construction satisfies an explicit coordinate-preserving equivalence
\[
 \boxed{\Gamma(F_X)\simeq\operatorname{Point}(X).}
 \tag{14}
\]
Old strict maps become natural maps of view systems, and their ambient actions agree with the previous inverse-limit maps. The existing cofinal point equivalence gives a cofinal ambient equivalence.

The finite prefixes
\[
 U_N=\{n:n\le N\}
\]
cover all transitions: both endpoints of any arrow lie in \(U_{\max(i,j)}\). Applying (6) gives
\[
 \boxed{\operatorname{Point}(X)
   \simeq\operatorname{Match}(F_X,(U_N)).}
 \tag{15}
\]
These are compatible **prefix sections**, not merely compatible choices of one point in each fiber.

**Lean:** `Resolution.ambientEquiv`, `Map.viewMorphism_onAmbient`, `cofinalAmbientEquiv`, `prefixViews_transitionCover`, `prefixSectionEquiv`.

For an existing Banach tower, the view system is built from its actual adjacent bonding functions and their previously checked composite restrictions. The old coherent point type is equivalent to the ambient section set with coordinates unchanged.

An exact bounded candidate \(g\) induces a natural map of view systems, and its map on ambient sections is the old coordinatewise map
\[
 x\longmapsto(g_nx_n)_n.
\]
In particular, the old constructed repair \(g=P_Lf\), under its original target-splitting and propagation-gap hypotheses, induces this same ambient map. No new existence hypothesis is silently dropped.

**Lean:** `BanachTower.ambientPointEquiv`, `exactAmbientMorphism`, `exactAmbient_agrees`, `repairedAmbientMorphism`, `repairedAmbient_coordinate`, `repairedAmbient_agrees`, `prefixAmbientEquiv`.

This bridge forgets topology only at the specified point-set interface. It does not promote coordinatewise convergence to uniform convergence or alter any v0.8 analytic theorem.

## 8. Higher refinement: proposed target, not checked by this release

A suitable next-level doctrine may consist of
\[
 (\mathcal V,\mathscr C,J,\mathscr R),\qquad
 \mathscr C:\mathcal V^{op}\to\mathrm{Cat}_\infty,
\]
where \(J\) specifies covers and \(\mathscr R\) specifies residual/correction data. Proposed ambient realizations are coherent cartesian sections of the associated fibration. Several distinctions must be maintained.

**Cartesian versus lax.** A cartesian section supplies equivalences between the selected objects and their prescribed pullbacks. Allowing arbitrary noninvertible comparison maps is a different, lax/noncartesian construction. The coherence of the indexing functor is supplied structure; failure of candidate data to obey that coherence is a separate defect.

**Equivalence versus identity.** An invertible comparison need not be the identity or have trivial holonomy. A stable-category cofiber can detect whether a comparison is an equivalence, but not distinguish that equivalence from a nontrivial automorphism. The Boolean loop example verifies the corresponding elementary distinction. Stable cofibers themselves are not formalized here.

**Sections versus stackhood.** Defining a section category does not establish effective descent for an arbitrary site. Standard stackhood requires a fibred structure, descent of morphisms, and effectiveness of object descent. The present transition-cover theorem is one explicit strict gluing theorem, not all those conditions for a proposed site.

**Internal ambient construction versus semantic realization.** If a separate category of intended semantic objects is given, a comparison functor into coherent ambient realizations must be constructed. Its full faithfulness and essential image are new mathematical questions. Equation (4) also prevents claiming nontrivial reconstruction merely by inserting an already-global terminal view.

**Bridge structure versus depth.** A homotopy fiber would retain components, automorphisms, and higher coherence. These are structural invariants, not an automatic numerical or qualitative measure of the depth of a relationship. A unique canonical correspondence can have a contractible bridge space.

**Arithmetic specialization.** No global/local arithmetic comparison, equality of support and occupancy, or essential surjectivity of an arithmetic correspondence stack follows from this abstract layer. Those require defined arithmetic categories and actual comparison theorems. Local fiberwise nonemptiness is explicitly insufficient even in the elementary checked model.

Primary reference anchors for this roadmap are the Stacks Project, Section 4.33 (Tag 02XJ), Section 8.3 (Tag 02ZC), and Section 8.4 (Tag 0268). These are established definitions and constructions, not novelty claims. The current Lean sources prove only the strict and additive statements identified above.

## 9. Verification contract and boundaries

Eight new modules contain 62 explicit named theorems and 56 indexed constructions. The cumulative project contains 64 modules, 718 named theorem declarations, and 327 indexed constructions. These counts include structural and auxiliary declarations, not mathematical discoveries. All 56 baseline proof modules are unchanged.

The mathematical proof obligations are the universally quantified declarations in the eight source modules. The theorem and construction audits must be read alongside their actual source hypotheses. The permitted standard axioms are `propext`, `Classical.choice`, and `Quot.sound`. The compiler/kernel and imported cached dependencies remain trusted and were not independently rebuilt.

The supplementary script `checks/computation/ambient_sections_exact.py` uses exact Boolean, integer, and rational arithmetic. It checks 340 Boolean view diagrams, 16,956 rational extension problems, 63 integer seeds, and two group actions, with 41,180 assertions and four false-claim rejection controls. It compares independent constructions of sections, coherent bridges, additive quotient membership, and extension solutions. It does not prove the arbitrary-category assertions or any higher descent theorem.

The new core is summarized by
\[
 \boxed{\text{views and restrictions}
   \longrightarrow\text{coherent ambient sections}
   \longrightarrow\text{partial-extension problems}
   \longrightarrow\text{actual relative obstructions and gluing}.}
\]
