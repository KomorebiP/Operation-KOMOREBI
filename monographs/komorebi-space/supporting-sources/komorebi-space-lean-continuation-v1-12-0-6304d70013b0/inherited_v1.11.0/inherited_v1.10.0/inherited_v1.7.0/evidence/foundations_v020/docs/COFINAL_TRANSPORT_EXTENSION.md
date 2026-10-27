# Komorebi Space Theory: cofinal transport and finite observation
## v0.5.0 · Komorebi P.

This extension formalizes exact transport under a change of sequential resolution schedule. The new category is set-valued. The existing Banach operators enter it through an explicit forgetful bridge. Neither a full comparison with `Pro(C)` nor invariance of numerical residuals is claimed.

## 1. Resolution data

Retain the existing type `Resolution`:
\[
 X_\bullet=(X_n,\rho^X_{ij}),\qquad
 \rho^X_{ij}:X_j\to X_i\quad(i\le j),
\]
\[
 \rho^X_{ii}=I,\qquad \rho^X_{ij}\rho^X_{jk}=\rho^X_{ik}.
\]
The all-pairs maps can now be constructed from any actual adjacent bonding functions. The associated all-pairs coherent point type is equivalent to the adjacent-coherence point type, without changing coordinates.
\[
 \operatorname{Lim}X=\{x\in\prod_nX_n:\rho^X_{ij}x_j=x_i\}.
\]

**Lean:** `Resolution.Adjacent.restrict`, `restrict_trans`, `resolution`, `pointEquiv`, `map_all`.

## 2. Reindexed exact representatives

A representative \(f:X\rightsquigarrow Y\) consists of
\[
 \phi_f:\mathbb N\to\mathbb N\quad\text{monotone},\qquad
 f_n:X_{\phi_f(n)}\to Y_n,
\]
subject to
\[
 \boxed{\rho^Y_{ij}f_j=f_i\rho^X_{\phi_f(i),\phi_f(j)}\quad(i\le j).}
\]
The selected input schedule need not itself be cofinal. The identity schedule is allowed, as are maps whose outputs use a fixed input stage.

Composition is explicit:
\[
 \phi_{g\circ f}(n)=\phi_f(\phi_g(n)),\qquad
 (g\circ f)_n=g_n f_{\phi_g(n)}.
\]
Identity and associativity are proved. These are exact representatives; nonzero compatibility residuals are not quotiented here.

**Lean:** `Resolution.ReindexedMap`, `id`, `ofMap`, `comp`, `comp_assoc`.

## 3. Eventual agreement is a finite-stage relation

Define
\[
 \boxed{
 f\sim g\iff\forall n\ \exists k\ge\phi_f(n),\phi_g(n):
 f_n\rho^X_{\phi_f(n),k}=g_n\rho^X_{\phi_g(n),k}.
 }
\]
The witness \(k\) may depend on the output stage \(n\). Equality here is equality of functions on all of \(X_k\), not equality restricted to globally realizable points.

The formalization proves reflexivity, symmetry, transitivity, persistence of a witness under further refinement, and
\[
 f\sim f',\quad g\sim g'\Longrightarrow g\circ f\sim g'\circ f'.
\]
The transitivity proof passes to the maximum of two witnesses. The composition proof first takes a common intermediate stage and then a common input stage.

Define the morphism set
\[
 \boxed{\operatorname{Hom}_{K_{\rm seq}}(X,Y)=\operatorname{ReindexedMap}(X,Y)/\!\sim.}
\]
Identities and composition descend to this quotient. An actual Lean `Category` instance is constructed on the existing resolutions.

**Lean:** `ReindexedMap.EventuallyEq`, `agree_further`, `eventuallyEq_trans`, `comp_congr`, `EventualHom`, `EventualHom.comp`.

This establishes a sequential category. An equivalence with the full pro-category has not been proved.

## 4. Realization

Each representative induces
\[
 F_f:\operatorname{Lim}X\to\operatorname{Lim}Y,\qquad
 (F_f(x))_n=f_n(x_{\phi_f(n)}).
\]
Finite-stage eventual agreement implies equality of these realized functions. Consequently realization descends to the quotient and gives a functor
\[
 \boxed{\operatorname{Real}:K_{\rm seq}\to\mathbf{Set}.}
\]
Identity and composition are preserved. No unrestricted faithfulness or fullness is assumed.

**Lean:** `ReindexedMap.onLimit_congr`, `EventualHom.onLimit`, `Resolution.realizationFunctor`.

## 5. Cofinal changes are actual isomorphisms

Let \(\phi:\mathbb N\to\mathbb N\) be monotone and unbounded:
\[
 \forall n\ \exists j:\ n\le\phi(j).
\]
Write \(X^\phi_n=X_{\phi(n)}\). Define
\[
 c_\phi(n)=\min\{j:n\le\phi(j)\}.
\]
The function \(c_\phi\) is proved monotone. The forward representative uses input level \(\phi(n)\) and the identity on \(X_{\phi(n)}\). The reverse representative uses sampled stage \(c_\phi(n)\) and restriction
\[
 X_{\phi(c_\phi(n))}\xrightarrow{\rho^X_{n,\phi(c_\phi(n))}}X_n.
\]
Both composite representatives agree with the appropriate identity after finite refinement. Therefore
\[
 \boxed{X\cong X^\phi\quad\text{in }K_{\rm seq}.}
\]
This is proved at the finite-stage quotient level, not inferred from a bijection of inverse limits.

For independent monotone unbounded schedules \(\phi,\psi\), conjugation yields
\[
 \boxed{\operatorname{Hom}_{K_{\rm seq}}(X,Y)
 \cong\operatorname{Hom}_{K_{\rm seq}}(X^\phi,Y^\psi).}
\]
On realized functions this is exactly conjugation by the previously checked cofinal point equivalences. For a strict same-level map and a common schedule, the new class agrees with ordinary levelwise sampling.

**Lean:** `ceilingIndex_monotone`, `sample_recover_eventually`, `recover_sample_eventually`, `cofinalIso`, `cofinalHomEquiv`, `cofinalHomEquiv_onLimit`, `Map.sample_class`.

## 6. When realization detects equality

Let
\[
 \pi_n:\operatorname{Lim}X\to X_n,\qquad \pi_n(x)=x_n.
\]
Assume every \(\pi_n\) is surjective. If two realized functions agree, take a common finite input stage and lift each of its points to a coherent input. Equality of realized functions then gives the required finite-stage witness. Thus
\[
 \boxed{f\sim g\iff F_f=F_g.}
\]
Equivalently, realization is injective on morphisms out of this source.

Surjectivity of all adjacent bonding functions is sufficient. Given a seed in \(X_k\), use restriction below level \(k\), choose right inverses of the adjacent maps, and recursively lift above \(k\). The resulting sequence is proved coherent and has the prescribed \(k\)-th coordinate.

This existence proof uses classical choice. It is not an algorithmic bound for finding lifts.

**Lean:** `ProjectionSurjective`, `ReindexedMap.eventuallyEq_iff_onLimit_eq`, `EventualHom.onLimit_injective`, `seededPoint`, `projectionSurjective_of_surjective_bonding`.

## 7. Exact description of the realized morphisms

For a function \(F:\operatorname{Lim}X\to\operatorname{Lim}Y\), define
\[
 \boxed{\operatorname{FO}(F)\iff
 \forall n\ \exists k\ \exists a_n:X_k\to Y_n:\
 \pi^Y_nF=a_n\pi^X_k.}
\]
This means that each entire output coordinate factors through one finite input coordinate. It does not merely mean pointwise dependence on a finite amount of information that can vary with the input point.

Every reindexed representative satisfies \(\operatorname{FO}\). Conversely, assume all input projections are surjective. From arbitrary factorization stages \(k_n\), form their monotone running maximum
\[
 \ell_0=k_0,\qquad\ell_{n+1}=\max(\ell_n,k_{n+1}).
\]
Define the stage maps by restricting from \(X_{\ell_n}\) to \(X_{k_n}\) and applying \(a_n\). Surjectivity of the input projections and coherence of \(F(x)\) imply their naturality on every finite input point. This constructs a representative whose realization is exactly \(F\).

Combining existence with faithfulness gives
\[
 \boxed{\operatorname{Hom}_{K_{\rm seq}}(X,Y)
 \cong\{F:\operatorname{Lim}X\to\operatorname{Lim}Y:\operatorname{FO}(F)\}.}
\]
This is an actual Lean equivalence of types. No topology, continuity theorem, or computational complexity is smuggled into \(\operatorname{FO}\).

**Lean:** `FinitelyObserved`, `levelEnvelope_monotone`, `observedPresentation`, `realization_image_iff`, `finiteObservationEquiv`.

## 8. Bridge to the existing Banach transport space

For a Banach tower, forget norms only after retaining its actual coordinate spaces and bonding functions. Construct all-pairs restrictions from the adjacent functions. The resulting limit point type is equivalent to the existing Banach-tower point type, with unchanged coordinates.

If a bounded candidate satisfies
\[
 (df)_n=\rho^Y_nf_{n+1}-f_n\rho^X_n=0,
\]
it determines a strict map, an eventual class, and a resampled class. Their realizations agree with the prior `BanachTower.onLimit`.

In particular, for the already constructed repair \(g=P_Lf\), the resampled output is
\[
 \boxed{(F_g^{\phi,\psi}(x))_n
 =g_{\psi(n)}\bigl((e_\phi^{-1}x)_{\psi(n)}\bigr),}
\]
where \(e_\phi\) is the cofinal point equivalence.

This is transport of an already repaired map. It does not assert that rerunning a different correction scheme on a coarser tower gives that same repair.

If the source has bounded target-style sections, its underlying bonding functions are surjective. The finite-observation equivalence therefore applies. It describes all set-valued eventual maps between the underlying resolutions, not only their continuous linear subset.

**Lean:** `BanachTower.underlyingResolution`, `resolutionPointEquiv`, `exactEventualHom_onLimit`, `sampledRepair_coordinate`, `underlying_projection_surjective`, `underlyingFiniteObservationEquiv`.

## 9. Three checked limits on the invariance statements

### 9.1 Strict presentation information can disappear

Use \(X_0=\{0,1\}\), \(X_{n+1}=\{*\}\), and the map \(*\mapsto0\) at the initial bond. The identity strict transport and the transport erasing the Boolean coordinate differ. Sampling \(n+1\) makes them literally equal. Their eventual classes were already equal.
\[
 \boxed{\text{Cofinal sampling need not be injective on strict presentations.}}
\]

### 9.2 Realized functions need not detect eventual classes

Let \(X_n=\{m\in\mathbb N:m\ge n\}\), with inclusions as restrictions. Every stage is nonempty but \(\operatorname{Lim}X=\varnothing\). The constant-false and constant-true transports into a constant Boolean tower are not eventually equal, since every possible witness stage has a point. Their realized functions have empty domain and are equal.
\[
 \boxed{\text{Realization need not be faithful without an additional hypothesis.}}
\]

### 9.3 Exact transport does not make the sup norm intrinsic

On constant real stages set
\[
 \rho^X_n=\tfrac12 I,\qquad\rho^Y_n=I,\qquad f_n=2^{-n}I.
\]
Both bonding maps are surjective and \(f\) is exact. Lean proves
\[
 \|f\|_\infty=1,\qquad\|(f_{n+1})_n\|_\infty=\tfrac12.
\]
The shifted family is itself exact, and its coordinates are proved to be the actual subsequence, not a merely analogous scaling.
\[
 \boxed{\text{Cofinal exact-class invariance does not imply sup-norm invariance.}}
\]

**Lean:** `ReindexingExamples.strict_reindexing_not_injective`, `distinct_classes_same_realization`, `ScheduleNormObstruction.cofinal_sampling_changes_norm`.

## 10. Scope and next obligations

Proved: finite-stage eventual equivalence, its composition congruence, a category, a realization functor, cofinal isomorphisms and Hom equivalences, a finite-observation characterization under surjective projections, and a bridge to actual repaired Banach transports. The three boundary examples are universal Lean proofs, not finite extrapolations.

Not proved: a comparison with the unrestricted pro-category; reindexed residual-valued morphisms; norm-independent or isometric presentation change; a topology on the quotient; arbitrary stack/descent constructions; unrestricted arithmetic correspondence; or a novel theorem relative to the literature. The next structural task is comparison with an established sequential pro-object model. The next quantitative task is identifying which residual norms admit controlled reindexing bounds, rather than declaring them invariant.
