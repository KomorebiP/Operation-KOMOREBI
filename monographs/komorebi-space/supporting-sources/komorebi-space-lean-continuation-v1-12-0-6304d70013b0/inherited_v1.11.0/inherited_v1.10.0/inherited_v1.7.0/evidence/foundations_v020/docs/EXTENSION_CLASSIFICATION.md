# Komorebi Space Theory: extension fibers, exactness, and staged choices
## v0.10.0 · Komorebi P.

This extension classifies all solutions of the actual additive ambient-section extension problem. It distinguishes nonexistence, nonuniqueness, and the failure of an intermediate choice. The core is strict and set-valued, with additive fibers. No higher stack, arbitrary arithmetic correspondence, or canonical view doctrine is asserted.

## 1. Fixed view system and the two invariants

Fix a category of views \(\mathcal V\), abelian groups \(A_v\), and additive restriction maps
\[
f^*:A_w\to A_v\quad(f:v\to w),\qquad (gf)^*=f^*g^*.
\]
The universes are those of the Lean declarations. Set
\[
E=\prod_v A_v,\qquad R=\prod_{f:v\to w}A_v,
\qquad (\delta x)_f=f^*(x_w)-x_v.
\]
For a prescribed domain \(U\), let \(p_U:E\to\prod_{u\in U}A_u\) be restriction and let \(s\in\Gamma_U(A)\) be coherent partial data. The v0.9 obstruction is
\[
\mathfrak o_U(s)=[\delta\widetilde s]\in Q_U:=R/\delta(\ker p_U).
\]
Its independence from the raw extension and its vanishing criterion remain unchanged.

The new second invariant is the **ambiguity group**
\[
\boxed{H_U=\ker\delta\cap\ker p_U.}
\tag{1}
\]
This is a subgroup of actual raw families, not a group assigned by a truth flag. Its elements are coherent ambient changes invisible on the prescribed views.

The two invariants answer different questions:
\[
\mathfrak o_U(s):\text{does a global extension exist?}
\qquad H_U:\text{how can two global extensions differ?}
\]

## 2. Every nonempty extension fiber is classified

The extension set is the existing object
\[
\operatorname{Ext}_U(s)=\{x\in\Gamma(A):x|_U=s\}.
\]
For any supplied base extension \(x_0\), the maps
\[
\boxed{
H_U\longrightarrow\operatorname{Ext}_U(s),\ h\longmapsto x_0+h,
\qquad x\longmapsto x-x_0
}
\tag{2}
\]
are mutually inverse. At every view, the forward map has value \((x_0)_v+h_v\).

The generic additive fiber theorem is first proved for a correction problem \((d:E\to R,p:E\to S)\). Translation by \(\ker d\cap\ker p\) is simply transitive on each nonempty exact fiber. A separate equivalence identifies that fiber with the existing `ViewSystem.Extensions`, using the actual view differential and observations.

The code proves the simply transitive translation laws directly. It does not introduce a separate mathlib `AddTorsor` instance. The usual description as a torsor is justified by those laws. Choosing a base solution supplies coordinates, not a distinguished solution. For two bases \(x_0,y_0\), the coordinate change is
\[
h\longmapsto h+x_0-y_0.
\]

**Lean:** `CorrectionProblem.fiberParameters`, `exists_unique_translation`, `change_base`; `AdditiveViewSystem.extensionsFiberEquiv`, `extensionParameters`, `extensionParameters_coordinate`, `extensionParameters_inverse`.

## 3. Existence and uniqueness are separate

The new complete criterion is
\[
\boxed{
\exists!x\in\Gamma(A),\ x|_U=s
\quad\Longleftrightarrow\quad
\mathfrak o_U(s)=0\ \land\ H_U=\{0\}.
}
\tag{3}
\]
For a supplied extension, its extension set is a subsingleton exactly when \(H_U\) is the bottom subgroup. Existence is not assumed in (3).

For arbitrary set-valued views, a useful sufficient detection criterion is also proved. Suppose that for every view \(v\) there is \(u\in U\) and an arrow \(f:u\to v\) whose restriction function \(f^*\) is injective. Then
\[
\Gamma(F)\longrightarrow\Gamma_U(F)
\]
is injective. This is a uniqueness theorem, not an existence theorem.

**Lean:** `AdditiveViewSystem.unique_extension_iff`, `extension_subsingleton_iff`; `ViewSystem.restrict_injective_of_detecting_views`.

## 4. The obstruction is an additive connecting map

The coherent global and partial families are constructed as additive subgroups, and explicit equivalences identify them with the earlier subtype-based section objects. Let
\[
\operatorname{res}_U:\Gamma(A)\longrightarrow\Gamma_U(A).
\]
Extension by zero is an additive raw lift on prescribed values. Composing that lift with \(\delta\) and quotient projection constructs
\[
\boxed{\partial_U:\Gamma_U(A)\longrightarrow Q_U.}
\tag{4}
\]
The code proves that its value on the old partial-section type is exactly \(\mathfrak o_U(s)\), rather than a different obstruction.

The exactness statements are
\[
\boxed{\ker\partial_U=\operatorname{im}(\operatorname{res}_U),}
\tag{5}
\]
and, on coherent families,
\[
\operatorname{res}_U(x)=0\iff x\in H_U.
\]
These give the familiar exact-sequence interpretation
\[
0\longrightarrow H_U\longrightarrow\Gamma(A)
\xrightarrow{\operatorname{res}_U}\Gamma_U(A)
\xrightarrow{\partial_U}Q_U.
\tag{6}
\]
The formalization records subgroup/kernel equalities and the actual homomorphisms. It does not package (6) as a chain complex or claim a terminal zero: \(\partial_U\) need not be surjective onto all of \(Q_U\).

The first isomorphism theorem is applied to give an actual additive equivalence
\[
\boxed{
\Gamma_U(A)/\operatorname{im}(\operatorname{res}_U)
\simeq_+\operatorname{im}\partial_U.
}
\tag{7}
\]
This isolates the obstruction classes arising from coherent prescribed data, excluding irrelevant elements of the larger arrow-residual quotient.

In addition,
\[
\boxed{\operatorname{res}_U\text{ is surjective}\iff\partial_U=0.}
\tag{8}
\]
The right side is a property to prove for a concrete system, not a general claim of global reconstruction.

**Lean:** `sectionGroup`, `partialGroup`, `restrictionHom`, `connectingHom`, `connecting_eq_extensionClass`, `connecting_kernel_eq_range`, `restriction_kernel_characterization`, `partialObstructionEquiv`, `partialObstructionEquiv_class`, `restriction_surjective_iff_connecting_zero`.

The additive fiber and first-isomorphism constructions are established mathematics. The pinned mathlib quotient API is used, not claimed as a new mathematical discovery. The new project layer connects those constructions to this actual view differential, its prescribed-domain quotient, and its extension objects.

## 5. Enlarging the prescribed domain

For \(U\subseteq W\), the checked inclusions are
\[
\ker p_W\subseteq\ker p_U,\qquad
\delta(\ker p_W)\subseteq\delta(\ker p_U),\qquad
\boxed{H_W\subseteq H_U.}
\tag{9}
\]
They induce a canonical surjective additive map
\[
\boxed{q_{W,U}:Q_W\twoheadrightarrow Q_U.}
\tag{10}
\]
It sends the class of a residual to the class of the same residual in the weaker quotient. The identity and composition laws are proved:
\[
q_{U,U}=I,\qquad q_{W,U}q_{Z,W}=q_{Z,U}.
\]
For every coherent partial section \(t\in\Gamma_W(A)\),
\[
\boxed{q_{W,U}(\mathfrak o_W(t))=\mathfrak o_U(t|_U).}
\tag{11}
\]
Therefore vanishing on the larger prescribed domain implies vanishing on the smaller one. Conversely, a nonzero obstruction on the smaller domain remains nonzero when retaining more specified data. The converse implications are not claimed. A concrete failure of injectivity of \(q_{W,U}\) is proved in Section 7.

**Lean:** `boundaries_antitone`, `ambiguity_antitone`, `forgetObstruction`, `forgetObstruction_surjective`, `forgetObstruction_comp`, `extensionClass_restrict`, `vanishing_restricts`, `obstruction_persists_under_prescription`.

## 6. Extension by stages retains the intermediate choice

This result requires only strict set-valued views. For \(U\subseteq W\), define
\[
\operatorname{Int}_{U,W}(s)
=\{t\in\Gamma_W(F):t|_U=s\}.
\]
There is an explicitly constructed equivalence
\[
\boxed{
\operatorname{Ext}_U(s)
\simeq
\coprod_{t\in\operatorname{Int}_{U,W}(s)}\operatorname{Ext}_W(t).
}
\tag{12}
\]
The forward map records the intermediate restriction of the same global object. The reverse map retains that global object, using the intermediate restriction equation. Both inverse identities are checked.

In particular,
\[
\operatorname{Ext}_U(s)\ne\varnothing
\iff
\exists t\in\operatorname{Int}_{U,W}(s),\ \operatorname{Ext}_W(t)\ne\varnothing.
\]
The existential quantifier is essential. Not every coherent intermediate choice must extend. No infinite choice, limit, or search-termination assertion follows from (12).

**Lean:** `ViewSystem.Intermediate`, `extensionStages`, `extensionStages_global`, `extensionStages_intermediate`, `extension_nonempty_iff_intermediate`.

## 7. One nonzero seed, infinitely many completions, and a failed intermediate choice

Use the three-view chain \(0\to1\to2\), with every fiber \(\mathbb Z^2\). Define
\[
\rho_{01}(a,b)=(a,0),\qquad
\rho_{12}(a,b)=(a,2b),\qquad
\rho_{02}(a,b)=(a,0).
\tag{13}
\]
All identity and composition laws are checked. Prescribe \(s_k=(k,0)\) at view 0. For each integer \(n\), the complete coherent family is
\[
\boxed{x^{(n)}=((k,0),(k,2n),(k,n)).}
\tag{14}
\]
Lean proves these are **all** extensions, giving
\[
\boxed{\mathbb Z\simeq\operatorname{Ext}_{\{0\}}(s_k).}
\tag{15}
\]
This holds for every \(k\), in particular the nonzero initial value \((7,0)\).

Now prescribe the intermediate family
\[
t_{k,m}=((k,0),(k,m))\quad\text{on }\{0,1\}.
\]
Every such family is internally coherent and restricts to \(s_k\). Nevertheless,
\[
\boxed{
\mathfrak o_{\{0,1\}}(t_{k,m})=0
\iff
\exists n\in\mathbb Z,\ m=2n.
}
\tag{16}
\]
Thus \(t_{7,1}\) has no global extension, although \(s_7\) does. The obstruction of \(t_{7,1}\) is nonzero and maps to zero under \(q_{\{0,1\},\{0\}}\). The actual quotient homomorphism is therefore proved not injective.

This refutes three possible shortcuts: zero obstruction does not imply uniqueness; extendable initial data do not make every intermediate choice safe; and forgetting observations need not preserve a nonzero obstruction.

**Lean:** `ExtensionChoiceExample.initialExtensionsEquiv`, `initial_extension_formula`, `initial_extensions_not_unique`, `middle_obstruction_iff_even`, `odd_middle_obstructed`, `obstruction_forgotten`, `forgetting_not_injective`, `nonzero_seed_dead_end`.

## 8. Computation and proof boundary

Six new modules add 57 named theorems and 31 indexed constructions. The cumulative project has 70 modules, 775 named theorems, and 358 indexed constructions. All 64 v0.9 proof-module sources are unchanged. Counts include auxiliary declarations, not discoveries.

The supplementary Python audit enumerates all scalar linear residual/observation pairs on \(\mathbb F_q^n\) for \(q=2,3\) and \(1\le n\le3\): 903 linear problems. It checks 35 nested-observation problems, 231 integer global examples and 209 integer intermediate examples, with 63,891 assertions. Kernel cardinalities are independently compared with modular Gaussian elimination. Three false-claim controls are rejected. These finite computations do not replace the universal Lean proofs.

Not proved: a canonical base extension when the ambiguity group is nonzero; an algorithm deciding arbitrary obstruction-quotient membership; convergence of infinite extension choices; category-valued or higher descent; equivalence with all intended mathematical objects; unrestricted arithmetic or automorphic correspondence. The results are relative to the specified view system and restriction maps.
