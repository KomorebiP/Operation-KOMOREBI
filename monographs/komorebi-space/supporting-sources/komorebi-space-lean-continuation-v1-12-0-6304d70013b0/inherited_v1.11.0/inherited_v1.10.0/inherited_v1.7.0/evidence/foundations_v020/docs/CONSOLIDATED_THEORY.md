# Current continuation: v0.20.0

The nonisometric connection model replaces unit transport gains by recursive path amplification. Its exact core is continuously linearly equivalent to the actual holonomy-fixed anchor space, and finite-dimensional inner-product fibers admit a constructed exact ambient repair with a derived bound that includes normalization, restoration, and holonomy conditioning. A nonzero anchored scalar chain has unit residual and repair error 2^n-1, disproving both length-only bounds and unconditional nonexpansiveness. See `AMPLIFIED_TRANSPORT_RECONSTRUCTION.md`. Earlier entries retain their historical hypotheses.

---

# Current continuation: v0.19.0

Finite-dimensional real inner-product fibers now admit a constructed orthogonal anchor correction and a derived optimal residual-to-distance gain. The actual edge and vertex product norms remain maximum norms. The correction yields an exact ambient realization for every candidate, retaining the feasible anchor component, with the proved graph bound \(\ell+\kappa_\infty(2\ell+1)\). A Cayley-rotation family on a fixed triangle rules out a universal gain over connections. This does not preserve an infeasible full anchor, assert infinite-dimensional stability, or compute a numerical singular value.

The complete development is `HOLONOMY_PROJECTION_STABILITY.md`. Current inventory: 117 proof modules, 1,207 named theorems, 654 indexed constructions. Verification uses a freshly rebuilt full v0.18 baseline and fresh compilation/audits of every v0.19 addition, with the reuse scope explicitly recorded. Earlier entries below retain their historical hypotheses and status.

---

# Current continuation: v0.18.0

The quantitative theory now permits nontrivial holonomy. Known inverse-consistent isometric edge maps define an actual graph-walk view system. Its exact ambient sections are classified by the common fixed space of rooted loop operators, with an explicit linear isometric equivalence. A prescribed anchor extends precisely when it lies in that fixed space. The existing protected-data obstruction is connected to a route-length error estimate. A reflection triangle has a nonzero one-dimensional exact core and an explicit repair with sharp gain 3/2. See `HOLONOMY_RECONSTRUCTION.md`. Counts: 112 modules, 1,134 named theorems, 636 indexed constructions. These are declaration counts, not novelty claims. See the delivery receipt for the exact current verification and fresh-replay boundary.

---

# Current continuation: v0.17.0

The new layer is **quantitative reconstruction from actual overlap data** on finite root-connected measured graphs with supplied linear isometric frames. It constructs a continuous linear path correction with norm bounded by the maximal route length, proves a unique anchor-preserving exact repair, and connects it to the old additive view obstruction and ambient section objects. Star overlap graphs admit a size-independent bound of one; a chain of n edges has sharp constant n, ruling out a universal graph-independent bound. Independent edge residuals are checked by a separate image projector, with a triangle obstruction. Isometric changes of coordinates commute with repair. No arbitrary nonabelian stack repair or unknown-frame reconstruction is claimed.

Five new modules add 78 named theorems and 42 indexed constructions. Current cumulative counts: 107 proof modules, 1,071 named theorems, and 601 indexed constructions. All 102 prior proof modules are unchanged. See `QUANTITATIVE_OVERLAP_REPAIR.md` for exact hypotheses, formulas, and the computational/verification boundary. Older entries retain their original version labels.

---

# Current continuation: v0.16.0

The new block is **relative realization invariance**: equivalence of actual prescribed section-extension sets, multiplicative equivalence of their ambiguity groups, and equivalence of identified-boundary realization groupoids on saturated patches. The actual full-framing pullback is proved not full in a duplicated-view counterexample. See `RELATIVE_REALIZATION_INVARIANCE.md`. The cumulative sources have 102 proof modules, 993 named theorems, and 559 indexed constructions. These are declaration counts, not novelty counts. Earlier sections retain their historical hypotheses and status.

---

# Current continuation: v0.15.0

The new layer is **invariance under equivalent view presentations**. Actual pullback along a category equivalence induces an equivalence of the existing unframed cocycle gauge groupoids and an equivalence of coherent section types, including twisted sections. It preserves and reflects unframed neutral orbit classes. On patches closed under isomorphism, inverse image is an order isomorphism, preserves and reflects composition covers, and gives actual patchwise cocycle equivalences commuting with restriction. A duplicated-view example proves failure of faithfulness on a raw nonsaturated patch. This is not a claim of arbitrary functor, norm, raw-site, or universal-doctrine invariance. See `VIEW_PRESENTATION_INVARIANCE.md` for statements and source names. Current counts: 95 proof modules, 959 named theorems, 524 indexed constructions. Historical sections retain their original hypotheses and scope.

---

# Current continuation: v0.14.0

The cocycle view theory now has an actual composition Grothendieck topology on the poset of full view patches, a restriction pseudofunctor, and a theorem using mathlib's standard `Pseudofunctor.IsStack` predicate. The topology axioms and the comparison to standard descent data are proved. This is an ordinary groupoid-valued stack on this specified site, not an arbitrary higher stack or arithmetic correspondence. The six new modules contain 43 named theorems and 30 indexed constructions. The cumulative project has 89 proof modules, 923 named theorems and 485 indexed constructions. See `COMPOSITION_SITE_STACK.md` and the exact `GroupViewSystem.patch_isStack` statement. Earlier sections retain their historical hypotheses and verification scope.

---

# Current continuation: v0.13.0

The new layer proves effective descent of local nonabelian cocycles related by specified overlap gauge isomorphisms. Under a composition cover, the actual restriction functor from global gauge objects to the constructed descent-data groupoid is an equivalence. Globalization is constructed, its compatible comparison is unique, and noncommuting overlap examples are checked. This does not assert arbitrary site or higher-stack descent. See `EFFECTIVE_GROUPOID_DESCENT.md`.

---

# Current continuation: v0.12.0

The new layer proves **strict groupoid descent in two complementary directions**. First, local gauge transformations which agree on view-overlaps glue uniquely to a global framed gauge morphism between already-global cocycles whenever the patches cover every transition. Second, local cocycle objects whose edge labels agree literally on overlap arrows glue to a unique global cocycle whenever every composable pair is contained in one patch. This yields an explicit equivalence between global cocycles and strictly matching local cocycles under the composition-cover hypothesis. These results establish descent of morphisms and strict descent of objects, but not yet effective descent for local objects related only up to gauge isomorphism. See `STRICT_GROUPOID_DESCENT.md`. Current counts: 78 proof modules, 845 named theorems, and 414 indexed constructions. Verification is incremental against the separately fully replayed v0.11.0 baseline; the attempted full clean cumulative replay hit the host 300-second tool limit and is not counted as a pass.

---

# Current continuation: v0.11.0

The new layer is **nonabelian cocycle groupoids and framed extension**. Arbitrary group coefficients support actual gauge arrows, stabilizer groups, a pointed orbit obstruction, and a proved neutrality criterion for extending prescribed twisted sections. Nonempty extension fibers are parametrized by invisible coherent group elements. A direct bridge recovers the actual additive differential and its earlier vanishing criterion. An exhaustive S3 loop model distinguishes two isomorphism classes and retains noncommuting automorphisms. This is not a full higher stack or a site-descent theorem. Current source counts: 76 modules, 831 named theorems, 399 indexed constructions. Verification evidence is separately documented.

See `NONABELIAN_COHERENCE.md`. Earlier entries below retain their historical hypotheses and scope.

---

# Current continuation: v0.10.0

The new layer classifies all additive ambient extensions. A nonempty extension fiber is parametrized by coherent changes vanishing on the prescribed views. Uniqueness is equivalent to vanishing of that ambiguity group, separately from vanishing of the existence obstruction. An additive connecting homomorphism has kernel exactly equal to the global-restriction image. Obstruction quotient maps respect restriction of prescribed domains and satisfy composition laws. Extension-by-stages is a dependent-sum equivalence retaining the intermediate choice. A three-view integer model has infinitely many completions of a nonzero seed and a coherent intermediate choice that is obstructed. See `EXTENSION_CLASSIFICATION.md` for the full development. Current counts: 70 modules, 775 named theorems, 358 indexed constructions. Older entries retain their historical hypotheses and status.

---

# Current continuation: v0.9.0

The new layer is **coherent ambient sections and concrete extension obstructions**. It constructs a strict set-valued view system, an ambient limit universal property, gluing on transition-covered full subcategories, a fiber/section theorem for correspondences, and an additive relative obstruction whose vanishing is equivalent to extending a prescribed partial section. A two-view integer example extends precisely for even seeds. The constructions agree with the old resolution point types and the old repaired Banach-tower maps. Higher stacks, homotopy fibers, general site descent, and arithmetic essential-surjectivity statements remain separate targets. Current counts are 64 proof modules, 718 named theorems, and 327 indexed constructions. Earlier entries below retain their historical hypotheses and status.

---

# Current continuation: v0.8.0

The new layer is **infinite-depth reconstruction with topology made explicit**. On actual dyadic tower residuals, all retained details are injective and every fixed coordinate is recovered exactly at finite depth. Uniform-norm convergence is separate: it holds precisely when the lifted coarse remainder vanishes, with density, summability, and gain criteria proved. Two fully constructed model families verify the distinction. The complete new development appears below and in `INFINITE_RECONSTRUCTION_EXTENSION.md`. Current counts are 56 modules, 656 named theorems, and 271 indexed constructions. Older entries retain historical hypotheses and status.

---

# Current continuation: v0.7.0

The current layer is **lossless dyadic residual detail**: a constructed section of the actual block coarsener, explicit independent hidden channels, bounded linear residual coordinates, a fine-exactness criterion, and a finite-depth hierarchy on the actual towers. The new development is appended below and is also in `LOSSLESS_RESIDUAL_EXTENSION.md`. There are 50 modules and 559 named theorems. Historical sections below retain their own hypotheses and release status.

---

# Current continuation: v0.6.0

The current verified layer is **controlled residual reindexing**: actual continuous linear maps \(S_\phi,C_\phi\), the identity \(d_\phi S_\phi=C_\phi d\), gap-dependent bounds, repair mismatch, and checked aliasing/sharpness examples. The full new development is appended below and is also available as `RESIDUAL_REINDEXING_EXTENSION.md`. The checked cumulative library has 44 modules and 480 named theorems. Earlier sections remain historical records with their original hypotheses.

---

# Current continuation: v0.5.0

The cumulative theory now includes `COFINAL_TRANSPORT_EXTENSION.md`: an exact set-valued category of reindexed transports modulo finite-stage eventual equality, cofinal Hom equivalences, a finite-observation characterization under surjective projections, and a bridge to the previous Banach repairs. Numerical norm invariance is explicitly refuted. Earlier sections below remain historical development with their original hypotheses.

# Komorebi Space Theory
## Consolidated formal core, v0.4.0

**Author:** Komorebi P.  
**Status:** A machine-checked core with an explicit extension boundary.  
**Conventions:** In equations, juxtaposition is ordinary right-to-left composition. In Lean, `f ≫ g` means first `f`, then `g`. Bonding maps point from finer to coarser resolution. All size and universe restrictions are those in the source declarations.

This document replaces the earlier fifty-section outline as the definition of the **checked core**. The full outline is retained as a status ledger in `OUTLINE_STATUS.md`. The core does not identify pro-objects, stacks, homotopy limits, and metric completions with one another. Those are different constructions requiring different hypotheses.

## 1. Resolution towers

Let \(\mathcal C\) be a category. Define

\[
X_\bullet=(X_n,\rho^X_n)_{n\geq0},\qquad
\rho^X_n:X_{n+1}\longrightarrow X_n.
\]

For towers \(X_\bullet,Y_\bullet\), a candidate transport is

\[
f=(f_n)_{n\geq0},\qquad f_n:X_n\longrightarrow Y_n.
\]

Define

\[
\operatorname{Exact}(f)
\iff
\forall n,\quad \rho^Y_nf_{n+1}=f_n\rho^X_n.
\tag{1.1}
\]

Identity and composition are levelwise:

\[
(1_X)_n=1_{X_n},\qquad(gf)_n=g_nf_n.
\]

### Theorem 1. Exact core

\[
\operatorname{Exact}(1_X),\qquad
\operatorname{Exact}(f)\land\operatorname{Exact}(g)
\Longrightarrow\operatorname{Exact}(gf).
\tag{1.2}
\]

Together with associativity and identities, this gives an actual category of towers and exact levelwise transports.

**Lean:** `Tower.PreHom.exact_id`, `Tower.PreHom.exact_comp`, the `Category (Tower C)` instance in `Towers.lean`.

**Boundary.** This is a fixed-schedule category. It has not been identified with \(\operatorname{Pro}(\mathcal C)\). That would require a reindexing and eventual-equality construction, followed by a comparison theorem.

## 2. The actual tower differential

Assume \(\mathcal C\) is preadditive. Set

\[
E(X,Y)=\prod_{n\geq0}\operatorname{Hom}_{\mathcal C}(X_n,Y_n),
\qquad
R(X,Y)=\prod_{n\geq0}\operatorname{Hom}_{\mathcal C}(X_{n+1},Y_n).
\]

The compatibility differential is the additive homomorphism

\[
\partial_{X,Y}:E(X,Y)\longrightarrow R(X,Y),
\qquad
(\partial f)_n=\rho^Y_nf_{n+1}-f_n\rho^X_n.
\tag{2.1}
\]

Consequently,

\[
\boxed{\operatorname{Exact}(f)\iff\partial f=0.}
\tag{2.2}
\]

For composable candidate transports,

\[
\boxed{
\partial(gf)_n=(\partial g)_nf_{n+1}+g_n(\partial f)_n.
}
\tag{2.3}
\]

This is an exact algebraic identity, not a bound. There is no additional mixed-error term in this setting.

**Lean:** `TowerCorrection.differential`, `TowerCorrection.exact_iff_differential_zero`, `Tower.PreHom.defect_comp`.

### Diagnostic: unrestricted repair is trivial

\[
\partial(f-f)=0.
\]

More generally, for any additive \(d:E\to R\),

\[
\forall f\in E,\quad\exists a\in E:\ d(f)-d(a)=0.
\]

Taking \(a=f\) proves the statement. Thus residual cancellation alone says nothing about retaining the mathematical object or observable of interest.

**Lean:** `CorrectionProblem.unrestricted_correction`, `Tower.PreHom.exact_zero`.

## 3. Semantics-preserving corrections

Let \(E,R,S\) be abelian groups and

\[
d:E\longrightarrow R,\qquad p:E\longrightarrow S
\]

be additive homomorphisms. Here \(d\) records residual, while \(p\) records the semantic information that must survive correction.

Admissible corrections are

\[
A_p=\ker p.
\]

Define the boundary subgroup and obstruction quotient by

\[
B_{d,p}=d(\ker p)\leq R,
\qquad
\mathcal Q_{d,p}=R/B_{d,p},
\qquad
\mathfrak o_{d,p}(f)=[d(f)].
\tag{3.1}
\]

### Theorem 2. Constrained flattening

\[
\boxed{
\mathfrak o_{d,p}(f)=0
\iff
\exists a\in E:\ p(a)=0,\ d(a)=d(f)
\iff
\exists g\in E:\ d(g)=0,\ p(g)=p(f).
}
\tag{3.2}
\]

The forward construction is \(g=f-a\). The reverse construction is \(a=f-g\).

Furthermore,

\[
p(a)=0\Longrightarrow
\mathfrak o_{d,p}(f-a)=\mathfrak o_{d,p}(f).
\tag{3.3}
\]

**Lean:** `CorrectionProblem.obstruction_zero_iff`, `CorrectionProblem.flatten_iff`, `CorrectionProblem.obstruction_invariant`.

### Theorem 3. Concrete tower repair criterion

For the actual differential \(\partial_{X,Y}\) and any additive semantic observable \(p:E(X,Y)\to S\),

\[
\boxed{
[\partial f]=0\text{ in }R(X,Y)/\partial(\ker p)
\iff
\exists g:X_\bullet\longrightarrow Y_\bullet\text{ exact},\quad p(g)=p(f).
}
\tag{3.4}
\]

The right-hand side is a bundled exact tower morphism, not an untyped promise of a global map.

**Lean:** `TowerCorrection.obstruction_zero_iff_exact`, `TowerCorrection.obstruction_zero_iff_exactHom`.

### Theorem 4. Obstruction certificate

Let \(L:R\to D\) be additive. If

\[
\forall a\in\ker p,\quad L(d(a))=0,
\qquad L(d(f))\ne0,
\]

then

\[
\mathfrak o_{d,p}(f)\ne0.
\tag{3.5}
\]

**Lean:** `CorrectionProblem.nonzero_certificate`.

A nonempty obstructed model is checked with \(E=R=S=\mathbb Z\), \(d=p=\operatorname{id}\), and \(f=1\).

**Lean:** `CorrectionProblem.rigid_one_obstructed`.

## 4. Square defects and pasting

In a preadditive category, for

\[
\begin{array}{ccc}
 A&\xrightarrow{f}&B\\
 u\downarrow&&\downarrow v\\
 A'&\xrightarrow{f'}&B',
\end{array}
\]

set

\[
\Omega(f,f';u,v)=vf-f'u\in\operatorname{Hom}(A,B').
\tag{4.1}
\]

For a horizontal pair of squares,

\[
\boxed{\Omega_{\mathrm{outer}}=\Omega_2 f+g'\Omega_1.}
\tag{4.2}
\]

For a vertical pair, with lower vertical arrows \(u',v'\),

\[
\boxed{\Omega_{\mathrm{outer}}=v'\Omega_1+\Omega_2u.}
\tag{4.3}
\]

Zero defects paste to zero defects in either direction.

**Lean:** `Squares.lean`.

The word “curvature” is only an interpretation of this defect. A connection, a nonabelian holonomy theory, and Bianchi identities do not follow without additional structure.

## 5. Quantitative pasting and transported Stokes

In a normed ring,

\[
\|\Omega_{\mathrm{outer}}\|
\leq
\|\Omega_2\|\,\|f\|+\|g'\|\,\|\Omega_1\|.
\tag{5.1}
\]

If \(\|f\|,\|g'\|\leq1\), then

\[
\|\Omega_{\mathrm{outer}}\|\leq\|\Omega_1\|+\|\Omega_2\|.
\tag{5.2}
\]

Let a finite sequence of path swaps have a certified difference

\[
T_{k+1}-T_k=A_k\Omega_kB_k.
\]

Then

\[
\boxed{T_N-T_0=\sum_{k=0}^{N-1}A_k\Omega_kB_k.}
\tag{5.3}
\]

If \(\|A_k\|,\|B_k\|\leq1\),

\[
\boxed{\|T_N-T_0\|\leq\sum_{k=0}^{N-1}\|\Omega_k\|.}
\tag{5.4}
\]

The transporting factors \(A_k,B_k\) are essential. Arbitrary defects in different Hom spaces cannot simply be added.

**Lean:** `NormedDefects.horizontal_norm`, `horizontal_contractive`, `transported_telescope`, `transported_stokes_bound`.

**Boundary.** The package verifies this theorem for a supplied sequence of certified swaps. It does not construct arbitrary cubical surfaces or prove a topological Stokes theorem for an unspecified complex.

## 6. Exact inverse-limit realization

A concrete resolution has types \(X_n\) and restriction maps

\[
\rho^X_{j,i}:X_j\to X_i\quad(i\leq j),
\qquad
\rho^X_{i,i}=1,
\qquad
\rho^X_{j,i}\rho^X_{k,j}=\rho^X_{k,i}.
\]

Define the limit **as a type of coherent coordinates**:

\[
\boxed{
\operatorname{Lim}(X)=
\left\{(x_n)\in\prod_nX_n:
\rho^X_{j,i}(x_j)=x_i\text{ for all }i\leq j\right\}.
}
\tag{6.1}
\]

For an exact family \(f_n:X_n\to Y_n\), define

\[
\operatorname{Lim}(f)(x)_n=f_n(x_n).
\tag{6.2}
\]

### Theorem 5. Realization and universal property

This produces an actual function

\[
\operatorname{Lim}(f):\operatorname{Lim}(X)\to\operatorname{Lim}(Y),
\]

preserves identities and composition, and is uniquely specified by (6.2).

For every compatible cone \(c_n:S\to X_n\),

\[
\exists!\,\ell:S\to\operatorname{Lim}(X),
\qquad \operatorname{pr}_n\ell=c_n.
\tag{6.3}
\]

**Lean:** `Resolution.Map.onLimit`, `onLimit_comp`, `onLimit_unique`, `Resolution.Cone.exists_unique_lift`.

To realize in already named objects \(S,T\), explicit equivalences

\[
e_X:S\simeq\operatorname{Lim}(X),\qquad e_Y:T\simeq\operatorname{Lim}(Y)
\]

are supplied. The resulting map is

\[
e_Y^{-1}\operatorname{Lim}(f)e_X:S\to T.
\tag{6.4}
\]

**Lean:** `Resolution.realize`, `Resolution.realize_coordinate`.

## 7. Canonicity under cofinal sampling

Let \(\phi:\mathbb N\to\mathbb N\) be nondecreasing and unbounded:

\[
\forall n\,\exists j:\ n\leq\phi(j).
\]

Define \((X\circ\phi)_j=X_{\phi(j)}\). Sampling yields

\[
S_\phi:\operatorname{Lim}(X)\to\operatorname{Lim}(X\circ\phi),
\qquad S_\phi(x)_j=x_{\phi(j)}.
\]

### Theorem 6. Exact cofinal invariance

\[
\boxed{\operatorname{Lim}(X)\simeq\operatorname{Lim}(X\circ\phi).}
\tag{7.1}
\]

The inverse recovers coordinate \(n\) by choosing \(j\) with \(n\leq\phi(j)\) and restricting \(y_j\) to level \(n\). The result is proved independent of that choice.

**Lean:** `Resolution.recoveredCoordinate_eq`, `extend_sample`, `sample_extend`, `cofinalEquiv`.

### Theorem 7. Quantitative cofinal invariance, restricted form

If \(\eta_n\geq0\) and \(\eta\) is nonincreasing, then

\[
\boxed{\eta_n\to0\iff\eta_{\phi(n)}\to0.}
\tag{7.2}
\]

**Lean:** `Profiles.cofinal_vanish_iff`.

Without monotonicity, define

\[
a_n=\begin{cases}0&n\text{ even},\\1&n\text{ odd}.\end{cases}
\]

Then

\[
a_{2n}\to0,\qquad a_n\not\to0.
\tag{7.3}
\]

Both assertions and cofinality of \(2n\) are checked. No general invariance of residual norms, rates, or cohomology is asserted.

**Lean:** `Profiles.sampled_alternating_vanishes`, `Profiles.alternating_does_not_vanish`.

## 8. Additive cohomology, when a complex is supplied

Let

\[
C^1\xrightarrow{\delta_1}C^2\xrightarrow{\delta_2}C^3,
\qquad \delta_2\delta_1=0
\]

be an explicit complex of abelian groups. Put

\[
Z^2=\ker\delta_2,
\qquad B^2=\operatorname{im}(C^1\xrightarrow{\delta_1}Z^2),
\qquad H^2=Z^2/B^2.
\]

### Theorem 8. Cohomological correction

For \(\Omega\in Z^2\),

\[
\boxed{[\Omega]=0\iff\exists\alpha:\Omega-\delta_1\alpha=0.}
\tag{8.1}
\]

The class is unchanged by such correction. In particular,

\[
[\delta_1\alpha]=0.
\tag{8.2}
\]

Thus an obstruction defined globally as \(\delta\tau\) is **already a coboundary**. It cannot serve as a nonzero intrinsic cohomology class without a restriction on corrections, local rather than global data, or another additional structure.

**Lean:** `ObstructionComplex.flatten_iff`, `correction_invariant`, `primary_defect_class_zero`, `obstruction_certificate`.

### Differential sign convention

For additive endomorphisms \(d,e\) satisfying

\[
d^2=e^2=0,\qquad de+ed=0,
\]

we prove

\[
\boxed{(d+e)^2=0.}
\tag{8.3}
\]

A commuting bicomplex instead needs the appropriate degree sign. The earlier outline mixed these conventions; it is not retained.

**Lean:** `Differential.anticommuting_sum_square_zero`.

## 9. Obstruction magnitude and closedness

For an additive subgroup \(B\) of a normed abelian group \(R\), define

\[
\eta_B(\Omega)=\inf_{b\in B}\|\Omega-b\|.
\tag{9.1}
\]

Then

\[
0\leq\eta_B(\Omega)\leq\|\Omega-b\|\quad(b\in B),
\]

and

\[
\boxed{\eta_B(\Omega)=0\iff\Omega\in\overline B.}
\tag{9.2}
\]

Only if \(B\) is closed may \(\overline B\) be replaced by \(B\).

**Lean:** `ObstructionFloor.lower_bound`, `zero_iff_closure`, `zero_iff_mem_of_closed`.

### Theorem 9. Persistent obstruction

If \(a_n\in B_n\) and for some \(c>0\), eventually

\[
c\leq\eta_{B_n}(\Omega_n),
\]

then

\[
\boxed{\|\Omega_n-a_n\|\not\longrightarrow0.}
\tag{9.3}
\]

**Lean:** `ObstructionFloor.persistent_obstruction`.

## 10. Completion and exactification

Let \((M,d_M)\) be a complete pseudometric space and

\[
\omega:M\to\mathbb R_{\geq0}
\]

be lower semicontinuous. In Lean, \(\omega\) is real-valued and nonnegativity is an explicit hypothesis.

### Theorem 10. Summable exactification

Suppose

\[
d_M(f_n,f_{n+1})\leq b_n,\qquad
\sum_nb_n\text{ converges},\qquad
\omega(f_n)\to0.
\]

Then

\[
\boxed{
\exists f_\infty:\quad
f_n\to f_\infty,\quad
\omega(f_\infty)=0,\quad
 d_M(f_n,f_\infty)\leq\sum_{k=0}^{\infty}b_{n+k}.
}
\tag{10.1}
\]

**Lean:** `Exactification.summable_exactification`.

### Theorem 11. Variable cancellation rates

Let \(q_n,C_n\geq0\),

\[
Q_0=1,\qquad Q_{n+1}=q_nQ_n,
\]

and assume

\[
\omega(f_{n+1})\leq q_n\omega(f_n),\qquad
 d_M(f_n,f_{n+1})\leq C_n\omega(f_n),
\]

\[
Q_n\to0,\qquad \sum_nC_nQ_n<\infty.
\]

Then an exact limit exists and

\[
d_M(f_n,f_\infty)
\leq\omega(f_0)\sum_{k=0}^{\infty}C_{n+k}Q_{n+k}.
\tag{10.2}
\]

**Lean:** `Exactification.variable_exactification`.

### Theorem 12. Geometric exactification

For \(0\leq q<1\), \(C\geq0\),

\[
\omega(f_{n+1})\leq q\omega(f_n),\qquad
 d_M(f_n,f_{n+1})\leq C\omega(f_n),
\]

we obtain

\[
\boxed{
\exists f_\infty:\quad f_n\to f_\infty,\quad\omega(f_\infty)=0,\quad
 d_M(f_n,f_\infty)\leq\frac{C}{1-q}\omega(f_n).
}
\tag{10.3}
\]

**Lean:** `Exactification.geometric_exactification`.

These are universal conditional theorems. They do not construct a cancellation algorithm satisfying their hypotheses for every input.

## 11. Semantic exactification in a complete linear model

Let \(E\) be a complete normed space over a nontrivially normed field \(\mathbb K\), and let \(R,S\) be normed \(\mathbb K\)-spaces. Take continuous linear maps

\[
d:E\to R,\qquad p:E\to S.
\]

Suppose \(p(f_n)=p(f_0)\) for every \(n\).

### Theorem 13. Exactification preserving meaning

If

\[
\|d(f_{n+1})\|\leq q\|d(f_n)\|,\qquad
\|f_{n+1}-f_n\|\leq C\|d(f_n)\|,
\qquad0\leq q<1,\quad C\geq0,
\]

then

\[
\boxed{
\begin{gathered}
\exists f_\infty\in E,\qquad f_n\to f_\infty,\\
d(f_\infty)=0,\qquad p(f_\infty)=p(f_0),\\
\|f_n-f_\infty\|\leq\frac{C}{1-q}\|d(f_n)\|.
\end{gathered}
}
\tag{11.1}
\]

The corresponding summable-movement theorem is also proved. Consequently,

\[
\boxed{[d(f_0)]=0\quad\text{in }R/d(\ker p).}
\tag{11.2}
\]

**Lean:** `LinearExactification.geometric_semantic_exactification`, `summable_semantic_exactification`, `controlled_obstruction_vanishes`.

This joins the obstruction and convergence sectors. For a particular infinite-dimensional tower representation, one must still supply its complete normed candidate space and prove continuity of its differential and semantics.

## 12. Path independence, with its missing hypothesis restored

In a metric space, suppose

\[
f_n\to x,\quad g_n\to y,\quad d_M(f_n,g_n)\leq K_n,\quad K_n\to0.
\]

Then

\[
\boxed{x=y.}
\tag{12.1}
\]

**Lean:** `PathIndependence.limits_equal_of_budget`.

Zero residual alone does not imply uniqueness. A vanishing pairwise path-comparison budget is required. In a merely pseudometric space one obtains zero distance, not necessarily equality.

## 13. Optional transport-cost geometry

For a category \(\mathcal D\), supply a cost

\[
w(f)\in[0,\infty],\qquad w(1_A)=0,\qquad w(gf)\leq w(f)+w(g).
\]

Define

\[
d_w(A,B)=\inf_{f:A\to B}w(f).
\]

Then

\[
d_w(A,A)=0,\qquad d_w(A,C)\leq d_w(A,B)+d_w(B,C).
\tag{13.1}
\]

The symmetrization

\[
d_w^{\mathrm{sym}}(A,B)=\max\{d_w(A,B),d_w(B,A)\}
\]

is symmetric and satisfies the triangle inequality. Zero symmetric distance defines an equivalence relation.

**Lean:** `TransportCost.distance_triangle`, `symDistance_triangle`, `zeroDistanceSetoid`.

If zero arrows exist and every zero arrow has zero cost, then

\[
\boxed{d_w(A,B)=0\quad\text{for every }A,B.}
\tag{13.2}
\]

**Lean:** `TransportCost.collapse_of_zero_arrows`.

Thus compatibility residual, information fidelity, and transport cost are three different notions. This package does not assert that every zero-distance class is an isomorphism class, or that an infimum of zero is attained.

## 14. Nontrivial finite obstruction model

Let

\[
G=(\mathbb Z/2\mathbb Z)^2,\qquad c(x,y)=x_2y_1.
\]

Then

\[
c(0,y)=c(x,0)=0,
\]

\[
\boxed{c(x,y)+c(x+y,z)=c(y,z)+c(x,y+z).}
\tag{14.1}
\]

Every scalar coboundary

\[
(\delta a)(x,y)=a(x)+a(y)-a(x+y)
\]

is symmetric, whereas \(c\) is not. Therefore

\[
\boxed{\neg\exists a:G\to\mathbb Z/2\mathbb Z,\quad c=\delta a.}
\tag{14.2}
\]

**Lean:** `ProjectiveExample.cocycle`, `no_scalar_flattening`.

This is an exact finite cocycle model. It is not a formal identification with a Galois group, a proof of a Langlands correspondence, or a general nonabelian obstruction theory.

## 15. Algebraic operator-compression identity

In a ring, if \(P^2=P\) and \(QP=P\), then

\[
\boxed{(QTQ)P-P(PTP)=(Q-P)TP.}
\tag{15.1}
\]

**Lean:** `NormedDefects.compression_shell`.

The Hilbert-space theorem \(\|T-P_nTP_n\|\to0\) for compact \(T\) is not proved in this release. The checked statement is the exact algebraic shell identity with its projection hypotheses.

## 16. Original v0.1.0 boundary and v0.2.0 extension

The release proves a **resolution–transport core**, a **semantics-constrained obstruction quotient**, a **concrete inverse-limit realization**, and **controlled exactification theorems**.

It does not yet define and verify a universal stack of all mathematical representations. It does not prove general pro-category equivalence, arbitrary cofinal invariance of residual norms, nonabelian Bianchi identities, higher-obstruction towers, spectral sequences, unrestricted local-to-global descent, or a canonical grammar generated solely by an underlying object.

The checked thesis is:

\[
\boxed{
\text{actual compatibility defect}
+\text{protected semantics}
+\text{admissible corrections}
+\text{controlled convergence}
\Longrightarrow
\text{exact structure with the protected semantics unchanged},
}
\]

with each term instantiated and each hypothesis stated in its corresponding Lean theorem.


---

## 17. Banach tower and projection extension

The following extends the core rather than replacing the preceding proofs. All 14 original proof modules are unchanged. The Banach-space construction and its actual differential, the correction dynamics, and the projection/realization theorems are new in v0.2.0.

## A. Actual complete transport spaces

Let \(\mathbb K\) be a nontrivially normed field. Let
\[
X_\bullet=(X_n,\rho^X_n),\qquad Y_\bullet=(Y_n,\rho^Y_n)
\]
be sequential towers of complete normed \(\mathbb K\)-spaces, with continuous linear bonding maps
\[
\rho^X_n:X_{n+1}\to X_n,\qquad \rho^Y_n:Y_{n+1}\to Y_n,
\]
and supplied finite uniform bounds
\[
\|\rho^X_n\|\le B_X,\qquad \|\rho^Y_n\|\le B_Y.
\]

Define
\[
\boxed{E_\infty(X,Y)=\ell^\infty_{n\ge0}\mathcal L_\mathbb K(X_n,Y_n)}
\]
and
\[
\boxed{R_\infty(X,Y)=\ell^\infty_{n\ge0}\mathcal L_\mathbb K(X_{n+1},Y_n).}
\]
Both are equipped with the sup norm. Completeness of the candidate space is obtained from the existing completeness instances for the operator spaces and their bounded product. It is not introduced as a new axiom.

The actual compatibility differential is
\[
(\partial f)_n=\rho^Y_nf_{n+1}-f_n\rho^X_n.
\]
The component estimate is
\[
\begin{aligned}
\|(\partial f)_n\|
&\le \|\rho^Y_n\|\,\|f_{n+1}\|+\|f_n\|\,\|\rho^X_n\|\\
&\le (B_X+B_Y)\|f\|_\infty.
\end{aligned}
\]
Consequently the family is bounded, the differential is continuous linear, and
\[
\boxed{\|\partial\|\le B_X+B_Y.}
\tag{A1}
\]

The level observable
\[
p_k:E_\infty(X,Y)\to\mathcal L_\mathbb K(X_k,Y_k),\qquad p_k(f)=f_k
\]
is continuous linear with
\[
\|p_k(f)\|\le\|f\|_\infty.
\tag{A2}
\]
Thus keeping \(p_k\) fixed preserves a complete finite-resolution operator, not merely its norm or a user-supplied truth flag.

**Lean:** `BanachTower.candidates_complete`, `rawDefect_mem`, `differential`, `differential_opNorm`, `evaluation`, `evaluation_bound`.

## B. Agreement with the algebraic tower core

Forget topology and norms using the category of modules:
\[
\mathsf U(X_\bullet)_n=X_n,\qquad\mathsf U(\rho^X_n)=\rho^X_n.
\]
For the same family \(f\), Lean proves
\[
\boxed{
\partial f=0
\iff
\forall n,\ \rho^Y_nf_{n+1}=f_n\rho^X_n
\iff
\mathsf U(f)\text{ is an exact tower morphism}.
}
\tag{B1}
\]
The new normed definition and the existing `Tower.PreHom.Exact` therefore refer to the same bonding maps and candidate operators.

**Lean:** `BanachTower.exact_iff_differential_zero`, `exact_iff_algebraic`, `exactHom`.

This is a fixed sequential schedule. It does not prove an equivalence with the entire pro-category or identify arbitrary Banach spaces with inverse limits of finite-dimensional truncations.

## C. Constructed repair dynamics

For a complete normed candidate space \(E\), let
\[
d:E\to R,\qquad p:E\to S,\qquad A:R\to E
\]
be continuous linear maps. The map \(A\) is a correction operator. Assume
\[
pA=0,
\tag{C1}
\]
and, for some \(0\le q<1\),
\[
\boxed{\|df-dA(df)\|\le q\|df\|\qquad(f\in E).}
\tag{C2}
\]
The contraction hypothesis is imposed only on residuals of actual candidates. It need not hold on all of \(R\).

Construct, rather than postulate, the sequence
\[
f^{(0)}=f,\qquad f^{(m+1)}=f^{(m)}-A(df^{(m)}).
\tag{C3}
\]
Then
\[
p(f^{(m)})=p(f),\qquad
\|df^{(m+1)}\|\le q\|df^{(m)}\|,
\]
\[
\operatorname{dist}(f^{(m)},f^{(m+1)})
\le\|A\|\,\|df^{(m)}\|.
\tag{C4}
\]
The previous geometric exactification theorem now applies with the derived movement constant \(C=\|A\|\). It gives
\[
\boxed{
\begin{gathered}
f^{(m)}\to P_Af,\qquad d(P_Af)=0,\qquad p(P_Af)=p(f),\\
\operatorname{dist}(f^{(m)},P_Af)
\le\frac{\|A\|}{1-q}\,\|df^{(m)}\|.
\end{gathered}}
\tag{C5}
\]

**Lean:** `RepairDynamics.exactification_from_correction_operator`, `repair_exists`.

The theorem supplies an iteration and its limit **from** a suitable correction operator. It does not supply such an operator for every tower or solve every protected residual problem.

## D. The limit is a bounded projection

The iterates in (C3) are linear in \(f\). Uniqueness of limits gives linearity of \(P_A\). Its norm satisfies
\[
\begin{aligned}
\|P_Af\|
&\le\|f\|+\operatorname{dist}(f,P_Af)\\
&\le\left(1+\frac{\|A\|\,\|d\|}{1-q}\right)\|f\|.
\end{aligned}
\]
Thus
\[
\boxed{P_A:E\to E\text{ is continuous linear},\qquad
\|P_A\|\le1+\frac{\|A\|\,\|d\|}{1-q}.}
\tag{D1}
\]
Every exact candidate is fixed by every iterate, and hence by the limit. Therefore
\[
\boxed{P_A^2=P_A,\qquad \operatorname{im}P_A=\ker d,\qquad pP_A=p.}
\tag{D2}
\]
Every candidate has the decomposition
\[
\boxed{f=P_Af+(f-P_Af)}
\]
with
\[
d(P_Af)=0,\qquad p(f-P_Af)=0,\qquad
 d(f-P_Af)=df,\qquad P_A(f-P_Af)=0.
\tag{D3}
\]
The second summand is an admissible correction carrying precisely the original residual.

**Lean:** `RepairDynamics.Scheme.projection`, `projection_bound`, `projection_idempotent`, `projection_image_iff`, `exact_residual_splitting`.

Although `limit` uses classical choice to package the existence theorem, its value is the unique limit of the specified iteration. This is a formal analytic construction, not executable floating-point code or a claimed runtime complexity bound.

## E. When the repair is canonical

For a **fixed** correction scheme, the sequence and its limit are determined. Independence of the scheme needs more.

Assume the observable separates exact candidates:
\[
\boxed{da=db=0\ \land\ p(a)=p(b)\ \Longrightarrow\ a=b.}
\tag{E1}
\]
Then any two schemes satisfying (C1)–(C2) have the same projection:
\[
P_A=P_{A'}.
\tag{E2}
\]
There is a unique exact candidate with protected semantics \(p(f)\).

**Lean:** `RepairDynamics.unique_repair`, `RepairDynamics.Scheme.scheme_independent`, `BanachTower.unique_repair_of_separation`.

Without separation, even a nonzero protected semantic coordinate does not ensure uniqueness. In
\[
E=\mathbb R^3,\qquad d(a,b,c)=c,\qquad p(a,b,c)=a,
\]
both \((1,0,0)\) and \((1,1,0)\) are exact and have the same protected value. Their inequality is checked.

**Lean:** `RepairExamples.semantics_alone_not_unique`.

## F. Specialization to actual tower transports

Use
\[
E=E_\infty(X,Y),\quad R=R_\infty(X,Y),\quad d=\partial,\quad p=p_k.
\]
A scheme now has the explicit obligations
\[
(A r)_k=0,
\qquad
\|\partial f-\partial A(\partial f)\|_\infty\le q\|\partial f\|_\infty.
\]
Its repaired map \(g=P_Af\) is an actual exact tower transport, preserves \(g_k=f_k\), and satisfies the uniform error estimate (C5). At every level \(n\),
\[
\|f^{(m)}_n-g_n\|\le\|f^{(m)}-g\|_\infty.
\tag{F1}
\]
The constructed tower projector satisfies
\[
\boxed{\|P_A\|\le1+\frac{\|A\|}{1-q}(B_X+B_Y).}
\tag{F2}
\]

**Lean:** `BanachTower.geometric_exactification`, `repair_by_operator`, `coordinate_dist_le`, `exactificationProjection`, `projection_exact_preserving_idempotent`, `projection_stability_bound`.

Define the realized point types
\[
\operatorname{Lim}X=\{(x_n):\rho^X_nx_{n+1}=x_n\text{ for all }n\},
\]
and analogously for \(Y\). Exactness constructs
\[
\boxed{F:\operatorname{Lim}X\to\operatorname{Lim}Y,\qquad F(x)_n=g_nx_n.}
\tag{F3}
\]
At the protected level,
\[
F(x)_k=f_kx_k.
\]
This map is unique **given its coordinate maps**. It is not a claim that the repaired candidate is unique without (E1), nor a claim that an unspecified original object is equivalent to this inverse limit.

**Lean:** `BanachTower.onLimit`, `onLimit_unique`, `repair_and_realize`.

## G. Two explicit models

### G1. A supplied correction operator with nonzero preserved information

For arbitrary complete normed spaces \(S,R\), take
\[
E=S\times R,\quad d(s,r)=r,\quad p(s,r)=s,\quad A(r)=(0,r).
\]
All scheme assumptions are verified with \(q=0\). The iteration reaches its exact limit in one step:
\[
(s,r)-A(d(s,r))=(s,0),\qquad P_A(s,r)=(s,0).
\]
If \(s\ne0\), the result is nonzero.

**Lean:** `RepairExamples.splitScheme`, `split_step`, `split_projection`, `split_nonzero`.

### G2. Identity bonding maps and a canonical tower repair

Let every \(X_n=E\), every \(Y_n=F\), and all bonding maps be identities. Then
\[
\operatorname{Exact}(g)\iff g_{n+1}=g_n\ (\forall n)
\iff g_n=g_0\ (\forall n).
\]
Every bounded candidate has a unique exact repair preserving level zero:
\[
\boxed{g_n=f_0\quad(n\ge0).}
\]
The coherent inverse limits are explicitly equivalent to \(E\) and \(F\), and the realized map is exactly \(f_0:E\to F\).

**Lean:** `BanachTower.constant_exact_iff`, `constant_unique_repair`, `constantPointEquiv`, `constant_realization`.

This model proves genuine canonical repair and realization. It does **not** establish a residual-proportional sup-norm error bound or exhibit a bounded contraction operator for all identity-tower candidates. Those are stronger statements than the unique-repair conclusion.

## H. Extension boundary

The original algebraic and analytic cores are now joined for uniformly bounded **sequential Banach towers on a common schedule**. The six new modules contain 60 named theorem declarations, including auxiliary lemmas. The full project has 20 modules and 156 named theorems. These counts are not novelty claims.

Not proved here: existence of a suitable correction operator for arbitrary towers, reindexed pro-morphism comparison, arbitrary cofinal norm invariance, sheaf/stack descent, higher obstruction complexes, or unrestricted arithmetic/global correspondence. The next structural task is reindexed transports with a proved eventual-equality quotient. The next analytic task is constructing correction operators in a genuinely nonconstant tower model while preserving specified semantic data.


---

# v0.3.0: constructed split-tower coordinates

The following extension removes the correction-operator existence hypothesis for a precisely specified class of towers. The preceding conditional theory remains valid without assuming these additional hypotheses.

This extension constructs the correction operator left as a hypothesis in v0.2.0, for sequential Banach towers with bounded target splittings and a strict propagation gap. It then derives a continuous linear coordinate system and an explicit, dimension-growing model. It does not prove a splitting or a gap for arbitrary towers.

## 1. Ambient spaces and hypotheses

Fix a nontrivially normed field \(\mathbb K\) and towers of complete normed spaces
\[
X_{n+1}\xrightarrow{\rho^X_n}X_n,
\qquad Y_{n+1}\xrightarrow{\rho^Y_n}Y_n,
\qquad n\in\mathbb N.
\]
Assume supplied finite uniform bounds
\[
\|\rho^X_n\|\le B_X,\qquad \|\rho^Y_n\|\le B_Y.
\]
The existing complete candidate and residual spaces are
\[
E=\ell^\infty_n\mathcal L_{\mathbb K}(X_n,Y_n),
\qquad R=\ell^\infty_n\mathcal L_{\mathbb K}(X_{n+1},Y_n),
\]
with the continuous linear differential
\[
\boxed{(df)_n=\rho^Y_nf_{n+1}-f_n\rho^X_n.}
\tag{1}
\]
Thus \(df=0\) is exact tower compatibility, with no replacement of the actual bonding maps by abstract residual data.

Choose continuous linear target sections
\[
s_n:Y_n\to Y_{n+1},\qquad
\rho^Y_ns_n=I_{Y_n},\qquad \|s_n\|\le S.
\]
The central quantitative hypothesis is
\[
\boxed{SB_X<1.}
\tag{2}
\]
Set
\[
\boxed{K=\frac{S}{1-SB_X}.}
\tag{3}
\]
A splitting is mathematical input, not intrinsic structure inferred from an object. Its bound and the norms are also part of the input.

**Lean data:** `BanachTower.Splitting`. The gap is an explicit argument, not an axiom or a field assuming the desired correction.

## 2. Constructed correction: a right inverse of the actual differential

For \(r\in R\), recursively define
\[
\boxed{(Ar)_0=0,\qquad
(Ar)_{n+1}=s_n\bigl(r_n+(Ar)_n\rho^X_n\bigr).}
\tag{4}
\]
All maps in (4) have domain \(X_{n+1}\) at stage \(n+1\). The recurrence preserves linearity in \(r\).

### Bound

Inductively,
\[
\begin{aligned}
\|(Ar)_{n+1}\|
&\le S\bigl(\|r\|_\infty+B_X\|(Ar)_n\|\bigr)\\
&\le S(1+B_XK)\|r\|_\infty
=K\|r\|_\infty.
\end{aligned}
\]
The base case is zero. The identity \(S(1+B_XK)=K\) uses (2). Therefore
\[
\boxed{A:R\to E\text{ is continuous linear},\qquad
\|Ar\|_\infty\le K\|r\|_\infty,\quad \|A\|\le K.}
\tag{5}
\]

### Exact right inverse

Using \(\rho^Y_ns_n=I\),
\[
\begin{aligned}
(dAr)_n
&=\rho^Y_ns_n\bigl(r_n+(Ar)_n\rho^X_n\bigr)
 -(Ar)_n\rho^X_n\\
&=r_n.
\end{aligned}
\]
Hence
\[
\boxed{dA=I_R,\qquad (Ar)_0=0.}
\tag{6}
\]
This is surjectivity onto *all bounded residual families*, not just residuals already known to equal \(df\).

**Lean:** `Splitting.rawCorrection_bound`, `correction`, `correction_bound`, `correction_opNorm`, `differential_correction`.

## 3. One-step exactification

Define
\[
\boxed{P=I_E-Ad.}
\tag{7}
\]
Equations (6) give
\[
\boxed{dP=0,\qquad P^2=P,\qquad \operatorname{im}P=\ker d,\qquad (Pf)_0=f_0.}
\tag{8}
\]
Moreover,
\[
\boxed{\|f-Pf\|_\infty\le K\|df\|_\infty.}
\tag{9}
\]
The existing iterative exactification engine has a constructed scheme with residual contraction rate zero. Its limiting projection is proved to equal (7). There is no remaining assumption that a global correction operator exists within this class.

"One step" means one application of the bounded operator \(A\). The infinite family is defined mathematically by a level recurrence. This is not a constant-time computational claim.

**Lean:** `Splitting.scheme`, `repair`, `repair_exact`, `repair_idempotent`, `repair_image_iff`, `repair_error`, `scheme_projection_eq`.

## 4. Protected observable: seed plus new output components

The initial level alone need not distinguish exact transports when target dimensions grow. Define
\[
N_n(f)=\bigl(I_{Y_{n+1}}-s_n\rho^Y_n\bigr)f_{n+1}.
\tag{10}
\]
Then
\[
\rho^Y_nN_n(f)=0,
\]
so this operator takes values in the newly exposed target kernel.

Package the initial level and all these components as
\[
\boxed{
(p_Lf)_0=f_0,\qquad (p_Lf)_{n+1}=N_n(f).
}
\tag{11}
\]
This is a continuous linear map \(p_L:E\to E\), satisfying
\[
\boxed{
\|p_L\|\le1+SB_Y,\quad p_L^2=p_L,\quad p_LA=0,\quad p_LP=p_L.
}
\tag{12}
\]
The name "semantic" refers to this specified protected mathematical observable. No claim is made that it captures every possible meaning or invariant of an arbitrary representation.

### Separation is derived

Every exact family obeys
\[
\boxed{f_{n+1}=s_nf_n\rho^X_n+N_n(f).}
\tag{13}
\]
Induction using its initial value and (13) gives
\[
\boxed{df=dg=0,\quad p_Lf=p_Lg\quad\Longrightarrow\quad f=g.}
\tag{14}
\]
Applying (14) to a difference yields the stronger injectivity statement
\[
\boxed{df=dg,\quad p_Lf=p_Lg\quad\Longrightarrow\quad f=g.}
\tag{15}
\]
Consequently
\[
\boxed{\forall f\in E,\quad\exists!g\in E:
 dg=0\ \land\ p_Lg=p_Lf.}
\tag{16}
\]
The unique \(g\) is \(Pf\). Any valid repair scheme for this *same* protected observable has the same projection. This is canonicity relative to the chosen splitting, not independence from changing the splitting, norms, schedule, or ambient doctrine.

**Lean:** `Splitting.innovation_down`, `observable`, `observable_idempotent`, `observable_correction`, `exact_reconstruction`, `exact_eq_of_observable`, `residual_observable_injective`, `unique_exact_repair`, `any_scheme_projection_eq`.

## 5. Continuous linear coordinate theorem

Let the semantic coordinate space be the normed submodule
\[
\boxed{\mathcal S_L=\{s\in E:p_Ls=s\}=\ker(p_L-I_E).}
\tag{17}
\]
The coordinate map and its inverse are explicit:
\[
\boxed{
\begin{aligned}
\Phi:E&\longrightarrow\mathcal S_L\times R,&
\Phi(f)&=(p_Lf,df),\\
\Phi^{-1}(s,r)&=Ps+Ar.
\end{aligned}}
\tag{18}
\]
Equations (6), (12), and (15) prove both inverse identities. Both maps are linear. The formalization also proves
\[
\|\Phi f\|\le
\max(1+SB_Y,B_X+B_Y)\|f\|,
\tag{19}
\]
\[
\|\Phi^{-1}(s,r)\|
\le(\|P\|+\|A\|)\|(s,r)\|.
\tag{20}
\]
Therefore the result is an actual continuous linear equivalence:
\[
\boxed{E_\infty(X,Y)\simeq_L\mathcal S_L\times R_\infty(X,Y).}
\tag{21}
\]
Here \(\simeq_L\) denotes a bounded linear isomorphism with continuous inverse, not an isometry.

In these coordinates,
\[
\boxed{
\Phi(Pf)=((\Phi f)_1,0),\qquad
\Phi(Ar)=(0,r),\qquad
f\text{ exact}\iff(\Phi f)_2=0.
}
\tag{22}
\]
Thus this class of Komorebi transport spaces has a proved separation into protected information and compatibility residual. This is a concrete analytic class, not a claim that the entire speculative stack/pro-object outline has been constructed.

**Lean:** `Splitting.semanticSpace`, `coordinateEquiv`, `coordinate_bound`, `coordinate_inverse_bound`, `coordinates`, `coordinates_repair`, `coordinates_correction`, `exact_iff_zero_residual_coordinate`.

## 6. A genuinely dimension-growing realization

Use real sup-norm spaces
\[
X_n=Y_n=\mathbb R^{n+1}.
\]
Let \(\pi_n\) delete the final coordinate and \(s_n\) append zero. Set
\[
\boxed{\rho^X_n=\tfrac12\pi_n,\qquad
\rho^Y_n=\pi_n,\qquad s_n(y)=(y,0).}
\tag{23}
\]
All dimensions, maps, bounds, and right-inverse laws are defined and checked in Lean. Here
\[
B_X=\tfrac12,\qquad B_Y=S=1,\qquad K=2.
\]
Thus every bounded candidate has an exact repair with
\[
\boxed{\|f-Pf\|_\infty\le2\|df\|_\infty.}
\tag{24}
\]
Its initial operator and every new final output row remain unchanged. For inherited output coordinates,
\[
(Pf)_{n+1}(x)_i=\tfrac12(Pf)_n(\pi_nx)_i,
\quad 0\le i\le n.
\]
For the new row,
\[
(Pf)_{n+1}(x)_{n+1}=f_{n+1}(x)_{n+1}.
\]

Take the bounded but nonexact candidate \(f_n=I_{\mathbb R^{n+1}}\). The formalization proves, for **every** \(n\) and \(0\le i\le n\),
\[
\boxed{(PI)_n(x)_i=2^{-(n-i)}x_i.}
\tag{25}
\]
For example,
\[
(PI)_3=\operatorname{diag}(1/8,1/4,1/2,1).
\]
The repaired family is nonzero and induces an actual map of the coherent inverse-limit point types. Its coordinate formula is (25). No unnamed original space is silently identified with either inverse limit, and no topology on the point types is asserted beyond what the code constructs.

**Lean:** `GrowingTower.source`, `target`, `targetSplitting`, `propagation_gap`, `gain_eq_two`, `identityCandidate_not_exact`, `identityRepair_nonzero`, `identityRepair_formula`, `realizedIdentity_coordinate`.

The factor \(1/2\) in the source bonding maps is substantive. This example does not establish the same bounded right inverse for unweighted truncation towers.

## 7. The threshold cannot be discarded indiscriminately

Take constant real towers with identity bonding maps. Then
\[
(df)_n=f_{n+1}-f_n,
\qquad S=B_X=1.
\]
The bounded residual family \(r_n=I_{\mathbb R}\) has no bounded primitive. Indeed, if \(df=r\), evaluating at 1 gives
\[
f_n(1)=f_0(1)+n,
\]
contradicting \(\sup_n\|f_n\|<\infty\).

Lean proves
\[
\boxed{\nexists f\in E:\ df=r,\qquad
\nexists A:R\to E:\ \forall r,\ d(Ar)=r.}
\tag{26}
\]
The second statement rules out even an arbitrary right-inverse function, not only a bounded linear one. Meanwhile the earlier constant-tower theorem still gives unique exact repair preserving level zero. Therefore
\[
\boxed{
\text{exact repair of candidates}\ \not\Longrightarrow\
\text{surjectivity onto every bounded residual}.
}
\tag{27}
\]
This is a checked counterexample at the threshold, not a theorem that the numerical gap condition is necessary for every tower.

**Lean:** `IdentityTowerObstruction.primitive_growth`, `no_bounded_primitive`, `no_right_inverse`, `repair_exists_but_right_inverse_does_not`.

## 8. Independent finite audit

`checks/computation/split_tower_exact.py` uses exact rational arithmetic. It checks 360 deterministic candidate cases with source factors 0, 1/4, 1/2, 3/4, and 7/8, depths 1 through 12, and six input families. It checks separately generated residuals, a nonrecursive finite Green-sum implementation, right inversion, exact repair, preservation, coordinate reconstruction, idempotence, and the gain bound. The identity formula is also checked through level 32.

There are 2,564 positive assertions and two deliberately faulty implementations which must be rejected. These bounded tests audit a second implementation. The universal results above are Lean proof terms, not an inference from the finite tests.

## 9. Scope ledger

Proved here: a constructed bounded right inverse under explicit split/gap hypotheses; exact repair; protected-profile separation; a continuous linear coordinate equivalence; an all-level dimension-growing model; and a threshold counterexample.

Not proved here: bounded splitting existence for arbitrary bonding maps; arbitrary schedule reindexing; unrestricted pro-category comparison; an invariant-independent canonical resolution doctrine; descent, stacks, higher obstruction theory, or any unrestricted arithmetic correspondence. Orthogonality, best approximation, computational complexity, and novelty relative to the literature are not asserted.


---

# Komorebi Space Theory: intrinsic core and splitting changes
## v0.4.0 · Komorebi P.

This extension distinguishes the invariant spaces attached to a fixed differential from the nonunique choices of correction and protected coordinates. It constructs and compares the coordinate maps, proves their cocycle and norm bounds, and exhibits two distinct repairs on the same dimension-growing towers. It does not select an intrinsic resolution doctrine.

## 1. Fixed differential, variable section

Let \(\mathbb K\) be a nontrivially normed field. Let \(E,R\) be normed \(\mathbb K\)-spaces and let
\[
 d:E\longrightarrow R
\]
be continuous linear. Define
\[
 \boxed{E^0=\ker d.}
\]
A section is a continuous linear map
\[
 A:R\longrightarrow E,\qquad dA=I_R.
\]
Neither \(E^0\) nor \(R\) depends on \(A\). A section is additional data. Existence of a section is not inferred from the notation.

Define
\[
 \boxed{P_A=I_E-Ad.}
\]
Then
\[
 dP_A=0,\qquad P_A^2=P_A,\qquad P_A|_{E^0}=I_{E^0},\qquad P_AA=0.
\]
Completeness is not required for these statements or for the coordinate equivalence below.

**Lean:** `SplitDefect.Section`, `Core`, `Section.project`, `project_exact`, `project_idempotent`, `project_fixes`, `project_lift`.

## 2. Coordinates on a fixed product

For each section define
\[
 \boxed{
 \begin{aligned}
 \Psi_A:E&\longrightarrow E^0\times R,&
 \Psi_A(f)&=(P_Af,df),\\
 \Psi_A^{-1}(e,r)&=e+Ar.
 \end{aligned}}
\]
The identities
\[
 (f-Adf)+Adf=f,\quad d(e+Ar)=r,\quad P_A(e+Ar)=e
\]
prove that these maps are inverse. They are linear and satisfy
\[
 \|\Psi_Af\|\le\max(\|P_A\|,\|d\|)\|f\|,
\]
\[
 \|\Psi_A^{-1}(e,r)\|\le(1+\|A\|)\|(e,r)\|.
\]
Thus
\[
 \boxed{E\simeq_L E^0\times R.}
\]
The product uses the maximum norm. This is a continuous linear equivalence, not an isometry. The factors are fixed, but the coordinate map depends on the section.

**Lean:** `Section.chartLinear`, `chart_bound`, `chart_inverse_bound`, `chart`, `chart_exact_component`, `chart_residual`, `chart_inverse`.

## 3. Exact change-of-chart law

Let \(A,B\) be two sections. Since
\[
 d(A-B)=0,
\]
the map \(A-B\) takes values in \(E^0\). Define
\[
 T_{A\to B}=\Psi_B\Psi_A^{-1}.
\]
Direct substitution yields
\[
 \boxed{T_{A\to B}(e,r)=(e+(A-B)r,r).}
\]
In particular,
\[
 T_{A\to B}(e,0)=(e,0).
\]
The exact slice is fixed pointwise, and every residual coordinate is unchanged. For three sections,
\[
 \boxed{T_{B\to C}T_{A\to B}=T_{A\to C},\qquad T_{A\to A}=I.}
\]
This follows from \((A-B)+(B-C)=A-C\). The transition maps are actual continuous linear equivalences and obey
\[
 \boxed{\|T_{A\to B}(e,r)\|\le(1+\|A-B\|)\|(e,r)\|.}
\]
These are triangular shear maps. Calling them coordinate changes does not assert manifold charts, a stack, or curvature classes beyond this defined linear system.

**Lean:** `Section.difference`, `difference_exact`, `difference_add`, `transition`, `transition_formula`, `transition_residual`, `transition_exact_slice`, `transition_cocycle`, `transition_norm`.

## 4. All sections and all retractions

Fix one section \(A\). For each bounded linear map \(T:R\to E^0\), let \(\iota:E^0\hookrightarrow E\) be inclusion and define
\[
 A_T=A+\iota T.
\]
Then \(dA_T=I\). Conversely, every section \(B\) has the unique form
\[
 B=A+\iota T,\qquad T=B-A\in\mathcal L(R,E^0).
\]
The package constructs the bijection
\[
 \boxed{\mathcal L(R,E^0)\simeq\{B\in\mathcal L(R,E):dB=I\}.}
\]
This parametrizes sections relative to a chosen base section. It does not designate a preferred one.

For the corresponding retractions,
\[
 \boxed{P_Bf-P_Af=(A-B)df.}
\]
Therefore
\[
 \|P_Bf-P_Af\|\le\|A-B\|\|df\|.
\]
Also
\[
 P_AP_B=P_B,\qquad P_BP_A=P_A,
\]
so
\[
 \boxed{P_AP_B=P_BP_A\iff P_A=P_B\iff A=B.}
\]
All sections give identical repair on exact inputs. On nonexact inputs, the repairs can differ by a nonzero exact element.

**Lean:** `Section.translate`, `sectionParameters`, `project_change`, `project_change_norm`, `project_other`, `projects_commute_iff`, `projects_equal_iff_lifts_equal`.

## 5. Application to the actual resolution towers

Retain the v0.3.0 towers and differential
\[
 E=\ell^\infty_n\mathcal L(X_n,Y_n),\quad
 R=\ell^\infty_n\mathcal L(X_{n+1},Y_n),
\]
\[
 (df)_n=\rho^Y_nf_{n+1}-f_n\rho^X_n.
\]
Let \(L=(s_n^L)\), \(M=(s_n^M)\) be two uniformly bounded target splittings, with
\[
 \rho^Y_ns_n^L=I=\rho^Y_ns_n^M,
\]
\[
 \|s_n^L\|\le S_L,\quad\|s_n^M\|\le S_M,\quad
 \|\rho^X_n\|\le B,
\]
and
\[
 S_LB<1,\qquad S_MB<1.
\]
The already constructed causal corrections \(A_L,A_M\) are sections of this actual differential. All results in Sections 1–4 apply to them. In particular,
\[
 \boxed{P_Mf-P_Lf=(A_L-A_M)df.}
\]
The generic exact core is proved to be the existing tower-compatibility kernel, rather than an unrelated abstract space.

**Lean:** `Splitting.defectSection`, `coreCoordinates`, `coreTransition`, `coreTransition_formula`, `coreTransition_cocycle`, `correction_difference_exact`, `repair_change`, `repair_change_norm`, `repair_change_gain_bound`, `repair_cross`, `repairs_commute_iff`, `repairs_agree_on_exact`.

## 6. The protected-profile space is also splitting-independent

The v0.3.0 protected observable is
\[
 (p_Lf)_0=f_0,\qquad
 (p_Lf)_{n+1}=(I-s_n^L\rho^Y_n)f_{n+1}.
\]
Define its fixed-point subspace \(\mathcal S_L=\{f:p_Lf=f\}\). Then
\[
 \boxed{f\in\mathcal S_L\iff
   \forall n,\ \rho^Y_nf_{n+1}=0.}
\]
Indeed, the forward direction follows by applying \(\rho^Y_n\) to the innovation expression. Conversely, each profile with values in the indicated kernels is fixed by every \(p_L\). The initial coordinate is unrestricted.

Consequently,
\[
 \boxed{\mathcal S_L=\mathcal S_M,\qquad p_Lp_M=p_M.}
\]
This is literal equality of submodules inside the same bounded candidate space. It does not imply \(p_Lf=p_Mf\) for arbitrary \(f\). The possible profile values are invariant, while the profile assigned to a candidate can change.

**Lean:** `Splitting.semanticSpace_characterization`, `semanticSpace_eq`, `observable_cross`.

## 7. Quantitative splitting stability

Assume also
\[
 \|s_n^L-s_n^M\|\le\varepsilon\quad(\forall n),\qquad\varepsilon\ge0.
\]
Define
\[
 \boxed{C_{L,M}(\varepsilon)=
 \frac{\varepsilon}{(1-S_LB)(1-S_MB)}.}
\]
Then
\[
 \boxed{\|A_L-A_M\|\le C_{L,M}(\varepsilon).}
\]
In consequence,
\[
 \boxed{\|P_Mf-P_Lf\|\le C_{L,M}(\varepsilon)\|df\|,}
\]
\[
 \|P_M-P_L\|\le C_{L,M}(\varepsilon)(B+B_Y).
\]
The gap factors are positive by hypothesis. The bound can deteriorate near a propagation threshold. No sharpness claim is made.

### Proof

Write \(a_n=(A_Lr)_n\), \(b_n=(A_Mr)_n\). The exact recurrence is
\[
 a_{n+1}-b_{n+1}
 =s_n^L(a_n-b_n)\rho^X_n
 +(s_n^L-s_n^M)(r_n+b_n\rho^X_n).
\]
Using \(\|b_n\|\le K_M\|r\|\), with \(K_M=S_M/(1-S_MB)\), induction gives
\[
 \|a_{n+1}-b_{n+1}\|
 \le S_LB C_{L,M}\|r\|
   +\varepsilon(1+BK_M)\|r\|
 =C_{L,M}\|r\|.
\]
The initial difference is zero. Taking the supremum and then the operator norm proves the result. The repair bound follows from Section 5.

**Lean:** `Splitting.perturbationGain`, `perturbationGain_balance`, `rawCorrection_difference_succ`, `rawCorrection_perturbation`, `correction_perturbation`, `correction_perturbation_opNorm`, `repair_perturbation`, `repair_perturbation_opNorm`.

## 8. Two splittings, one tower, different exact repairs

Use the same checked dimension-growing towers
\[
 X_n=Y_n=\mathbb R^{n+1},\quad
 \rho^X_n=\tfrac12\pi_n,\quad \rho^Y_n=\pi_n.
\]
Here \(\pi_n\) deletes the last coordinate. Compare
\[
 s_n^0(y)=(y,0),\qquad s_n^1(y)=(y,y_0).
\]
Both have norm at most one under the sup norms, both are right inverses, and both satisfy the propagation gap \(1\cdot\tfrac12<1\).

For the candidate \(f_n=I\), the repaired stage-one operators are
\[
 \boxed{
 (P_0f)_1=\begin{pmatrix}1/2&0\\0&1\end{pmatrix},\qquad
 (P_1f)_1=\begin{pmatrix}1/2&0\\-1/2&1\end{pmatrix}.}
\]
The proof checks both coordinate formulas for arbitrary inputs, not only sampled vectors. The full infinite families are exact and have the same initial operator, but they are unequal. The corresponding retraction operators do not commute. The protected profile subspaces are equal, but the protected values of the original candidate differ.

**Lean:** `SplittingDependence.skewSplitting`, `skew_gap`, `skewRepair_exact`, `skew_identity_first_new`, `skew_identity_first_old`, `exact_repairs_differ`, `profile_spaces_equal`, `protected_profiles_differ`, `repair_operators_do_not_commute`, `same_seed_distinct_exact_repairs`.

## 9. What is canonical here?

For fixed towers, bonding maps and norms:
\[
 \boxed{E,\ R,\ d,\ \ker d,\ \mathcal S}
\]
are independent of the chosen target splitting. In contrast,
\[
 \boxed{A_L,\ P_L,\ p_L,\ \Psi_L}
\]
can depend on that choice. The dependency is described by proved continuous linear changes of coordinates and quantitative estimates.

This is not canonicity under arbitrary replacement of the towers, reindexing, changes of norm, semantic doctrine, or ambient category. It is not a construction of the earlier proposed stack or unrestricted pro-category theory.

## 10. Verification boundary and established mathematics

The abstract decomposition is a bounded splitting of the exact sequence
\[
 0\longrightarrow\ker d\longrightarrow E\xrightarrow{d}R\longrightarrow0.
\]
Such splitting constructions are established mathematics. The pinned mathlib contains `ContinuousLinearEquiv.equivOfRightInverse` in `Mathlib/Topology/Algebra/Module/Equiv.lean`; the current module constructs the kernel-first chart explicitly to expose its bounds and change-of-chart laws. No novelty claim is made for the abstract splitting argument.

The extension's role is to connect these facts to the actual tower correction, distinguish the invariant and choice-dependent pieces, derive the two-gap stability estimate, and verify the same-tower counterexample.

The supplementary rational script checks 144 deterministic finite cases, 1,876 positive assertions, and two rejected mutations. It is an independent implementation audit, not a substitute for the universally quantified Lean proofs.


---

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


---

# Komorebi Space Theory: controlled residual reindexing
## v0.6.0 · Komorebi P.

This extension constructs a bounded change of residual coordinates for common-schedule resampling of contractive sequential Banach towers. It distinguishes preservation of exactness from detection of exactness, quantifies the dependence on the length of skipped blocks, and compares the two orders of resampling and repair.

**Scope:** fixed source and target towers, actual bonding operators, a common monotone schedule, contractive bonds, and a finite gap bound for the quantitative operator. The previous exact eventual category remains unchanged. No quotient of arbitrary nonexact premorphisms is constructed.

## 1. Towers and the actual differential

Fix a nontrivially normed field \(\mathbb K\). Let
\[
 X_{n+1}\xrightarrow{\rho^X_n}X_n,
 \qquad Y_{n+1}\xrightarrow{\rho^Y_n}Y_n
\]
be the existing sequential Banach towers. Write
\[
 E=\ell^\infty_n\mathcal L(X_n,Y_n),
 \qquad R=\ell^\infty_n\mathcal L(X_{n+1},Y_n),
\]
\[
 \boxed{(df)_n=\rho^Y_nf_{n+1}-f_n\rho^X_n.}
\]
For the new norm estimates assume
\[
 \boxed{\|\rho^X_n\|\le1,\qquad\|\rho^Y_n\|\le1\quad(\forall n).}
\]
These hypotheses are explicit. The general uniformly bounded tower definitions from previous releases are not silently changed.

## 2. Finite-block restriction and defect

For \(i\le j\), construct
\[
 \rho^X_{i,j}:X_j\to X_i,
 \quad \rho^X_{i,i}=I,
 \quad \rho^X_{i,j+1}=\rho^X_{i,j}\rho^X_j.
\]
The analogous target maps satisfy the same equations. Lean verifies
\[
 \rho_{i,j}\rho_{j,k}=\rho_{i,k},
 \qquad\|\rho_{i,j}\|\le1.
\]
It also verifies agreement with the actual all-pairs functions used in the earlier finite-stage category.

Define the block defect
\[
 \boxed{D_{i,j}(f)=\rho^Y_{i,j}f_j-f_i\rho^X_{i,j}.}
\]
Its exact concatenation law is
\[
 \boxed{D_{i,k}(f)=\rho^Y_{i,j}D_{j,k}(f)+D_{i,j}(f)\rho^X_{j,k}.}
\]
The terms are transported into the same Hom space. Adding arbitrary untransported defects would not even be well typed for varying dimensions.

**Lean:** `BanachTower.restriction`, `restriction_trans`, `restriction_underlying`, `restriction_contractive`, `blockDefect_concat`.

## 3. Accumulation of arbitrary residuals

For any adjacent residual family \(r_n:X_{n+1}\to Y_n\), define recursively
\[
 B_{i,i}(r)=0,
\]
\[
 \boxed{B_{i,j+1}(r)=\rho^Y_{i,j}r_j+B_{i,j}(r)\rho^X_j.}
\]
This transported recursion is the formal definition of the block sum. It is linear in \(r\). For an actual candidate residual, Lean proves the telescope
\[
 \boxed{B_{i,j}(df)=D_{i,j}(f).}
\]
The local and uniform bounds are
\[
 \boxed{\|B_{i,j}(r)\|\le\sum_{k=i}^{j-1}\|r_k\|,}
\]
\[
 \boxed{\|B_{i,j}(r)\|\le(j-i)\|r\|_\infty\quad(r\in R).}
\]
These inequalities discard cancellation only when taking norms. The block sum itself retains signs, operator order, and cancellation.

**Lean:** `blockSum`, `blockSum_succ`, `blockSum_differential`, `blockSum_add`, `blockSum_smul`, `blockSum_norm`, `blockSum_uniform_bound`.

## 4. The resampled tower and candidate map

Let \(\phi:\mathbb N\to\mathbb N\) be monotone. Define
\[
 X^\phi_n=X_{\phi(n)},
 \qquad(\rho^{X^\phi})_n=\rho^X_{\phi(n),\phi(n+1)},
\]
and analogously for \(Y^\phi\).

The sampled tower is an actual `BanachTower`, with the composite bonding maps and a proved bound of one. Define the bounded candidate map
\[
 \boxed{S_\phi:E\to E_\phi,
 \qquad(S_\phi f)_n=f_{\phi(n)}.}
\]
Then
\[
 \|S_\phi f\|_\infty\le\|f\|_\infty,
 \qquad\|S_\phi\|\le1.
\]
Neither these definitions nor the preservation of exactness require cofinality or a finite gap bound. Repeated schedule indices are allowed.

**Lean:** `resample`, `sampleCLM`, `sampleCLM_apply`, `sampleCLM_bound`, `sampleCLM_opNorm`, `sample_exact`.

## 5. A bounded residual map and a commuting square

Suppose additionally
\[
 \boxed{\phi(n+1)-\phi(n)\le M\quad(\forall n),\qquad M\in\mathbb N.}
\]
Define
\[
 \boxed{C_\phi:R\to R_\phi,
 \qquad(C_\phi r)_n=B_{\phi(n),\phi(n+1)}(r).}
\]
This is constructed as a continuous linear map, with
\[
 \boxed{\|C_\phi r\|_\infty\le M\|r\|_\infty,
 \qquad\|C_\phi\|\le M.}
\]
The central identity is
\[
 \boxed{d_\phi S_\phi=C_\phi d.}
\]
Therefore
\[
 \boxed{\|d_\phi S_\phi f\|_\infty\le M\|df\|_\infty.}
\]
This is controlled reindexing, not invariance of the number \(\|df\|\). Notice that \(C_\phi\) is a transported accumulation, not the componentwise sample \(r\mapsto(r_{\phi(n)})\).

**Lean:** `residualSampleCLM`, `residualSampleCLM_opNorm`, `resampling_chain`, `sampled_residual_bound`.

## 6. Two different convergence statements

### 6.1 Sequences in the candidate Banach space

For fixed \(\phi,M\),
\[
 df^{(k)}\longrightarrow0\text{ in }R
 \quad\Longrightarrow\quad
 d_\phi S_\phi f^{(k)}\longrightarrow0\text{ in }R_\phi.
\]
This follows from continuity of the constructed \(C_\phi\).

**Lean:** `sampled_residual_tendsto_zero`.

### 6.2 A single candidate at increasing resolution

Assume also that \(\phi\) is unbounded. If
\[
 \|r_n\|\longrightarrow0,
\]
then the local sum bound and the bounded gaps imply
\[
 \boxed{\|B_{\phi(n),\phi(n+1)}(r)\|\longrightarrow0.}
\]
In particular,
\[
 \| (df)_n\|\longrightarrow0
 \quad\Longrightarrow\quad
 \|(d_\phi S_\phi f)_n\|\longrightarrow0.
\]
The two results have different quantifiers. Neither asserts a converse.

**Lean:** `blockSum_local_bound`, `blockSum_cofinal_vanish`, `sampled_levelwise_residual_vanish`.

## 7. Abstract presentation change and repair mismatch

Let \(d:E\to R\), \(D:F\to T\) be continuous linear maps. A bounded defect map consists of
\[
 S:E\to F,\qquad C:R\to T,\qquad DS=Cd.
\]
It induces a bounded map \(\ker d\to\ker D\) and composes with other such maps.

Let \(A:R\to E\) and \(B:T\to F\) be chosen bounded sections,
\[
 dA=I,\qquad DB=I,
\]
with projectors \(P_A=I-Ad\), \(P_B=I-BD\). Define
\[
 \boxed{H=SA-BC.}
\]
Then Lean proves
\[
 \boxed{DH=0,\qquad P_BS-SP_A=Hd.}
\]
Thus the discrepancy is exact-valued and vanishes on exact inputs. The estimates are
\[
 \|(P_BS-SP_A)f\|\le\|H\|\,\|df\|,
\]
\[
 \|H\|\le\|S\|\|A\|+\|B\|\|C\|.
\]
Since \(d\) has a section, it is surjective. Consequently
\[
 \boxed{P_BS=SP_A\quad\Longleftrightarrow\quad SA=BC.}
\]
Repair is natural precisely when the selected sections are compatible with the presentation change. Exactness of the repaired outputs alone does not give this equality.

**Lean:** `SplitDefect.DefectMap`, `coreMap`, `comp`, `mismatch`, `mismatch_exact`, `repair_change`, `repair_change_bound`, `repair_natural_iff`.

## 8. Triangular coordinates and composition

Using the already checked section charts
\[
 \Psi_A:E\simeq_L\ker d\times R,
 \qquad\Psi_B:F\simeq_L\ker D\times T,
\]
the presentation change has the exact form
\[
 \boxed{\Psi_BS\Psi_A^{-1}(e,r)=(S_0e+Hr,Cr),}
\]
where \(S_0\) is the restriction of \(S\) to the exact kernel.

For a second defect map \((S_2,C_2)\) and a third section, the mismatches satisfy
\[
 \boxed{H_{21}=S_2H_1+H_2C_1.}
\]
This is a proved composition law, not an assumption of path independence.

**Lean:** `DefectMap.chart_formula`, `DefectMap.mismatch_comp`.

## 9. Application to actual tower sampling

Instantiate \((S,C,D)=(S_\phi,C_\phi,d_\phi)\). Given sections \(A\) and \(B\) of the actual fine and sampled differentials,
\[
 \boxed{P_BS_\phi f-S_\phi P_Af=(S_\phi A-BC_\phi)df,}
\]
\[
 \boxed{\|P_BS_\phi f-S_\phi P_Af\|
 \le(\|A\|+M\|B\|)\|df\|.}
\]
If a sequence of fine residuals tends to zero, this discrepancy tends to zero. Equality at every finite stage still requires the section-compatibility condition.

The sections in this comparison are explicit inputs. Previous releases construct sections under their own split/gap assumptions. This release does not assert section existence for every contractive resampled tower or identify independently chosen repair procedures.

**Lean:** `samplingDefectMap`, `samplingMismatch`, `sampling_repair_formula`, `samplingMismatch_opNorm`, `sampling_repair_bound`, `sampling_repair_natural_iff`, `sampling_repair_discrepancy_tendsto_zero`.

## 10. Exactness can be hidden by coarsening

On constant real towers with identity bonding maps take
\[
 f_{2n}=I,\qquad f_{2n+1}=2I.
\]
This is a bounded nonzero candidate with
\[
 (df)_{2n}=I,\qquad(df)_{2n+1}=-I,
 \qquad\|df\|_\infty=1.
\]
For the cofinal schedule \(\phi(n)=2n\),
\[
 S_\phi f=(I,I,I,\ldots),\qquad d_\phi S_\phi f=0.
\]
Lean proves all these statements for the full infinite families. It follows that \(C_\phi\) is not injective and
\[
 \boxed{\nexists c>0\;\forall f:
 c\|df\|\le\|d_\phi S_\phi f\|.}
\]
The failure already occurs on residuals of actual bounded candidates, not just on arbitrary residual families.

This does not contradict exact-class invariance from v0.5.0. A nonexact fine candidate was not a morphism in its exact transport category. Coarsening removed the constraints that detected its incompatibility.

**Lean:** `ResidualAliasing.fine_residual_norm`, `sampled_residual_zero`, `coarsening_hides_nonzero_residual`, `coarsen_not_injective`, `no_positive_reverse_bound`.

## 11. The dependence on gap length is sharp

On the same identity real towers, sample every \(M\) levels:
\[
 \phi_M(n)=Mn.
\]
The bounded unit residual \(r_n=I\) satisfies
\[
 \|r\|_\infty=1,\qquad (C_{\phi_M}r)_n=MI.
\]
Therefore Lean proves, for every natural \(M\),
\[
 \boxed{\|C_{\phi_M}\|=M.}
\]
For \(M>0\) this schedule is cofinal. The \(M=0\) case is the constant schedule and the zero block map.

This sharpness statement is about the map on **all bounded residual families**. The unit residual is not asserted to have a bounded primitive; the earlier identity-tower obstruction rules out such a primitive.

**Lean:** `stride_cofinal`, `blockSum_unit`, `coarsen_unit_norm`, `coarsen_opNorm`.

## 12. Verification and remaining boundary

Six modules add 84 named theorem declarations, including auxiliary lemmas. The cumulative project has 44 proof modules, 480 named theorems, and 203 indexed non-theorem declarations. All 38 previous proof modules are unchanged.

The exact rational audit separately tests 120 variable-dimension candidate configurations, 24 section/cochain-map configurations, and 32 sharp-gain values. It compares a recurrence implementation against independently formed products and transported finite sums. These finite tests do not prove infinite convergence or universal statements.

Not established: unrestricted source/output reindexing of nonexact premorphisms; a residual-valued localization; a full comparison with `Pro(C)`; unrestricted weighted/noncontractive estimates; automatic compatibility or existence of fine/coarse sections; stack descent; higher obstruction theory; an unrestricted arithmetic correspondence; a novelty claim.

The next precise issue is to characterize the information in \(\ker C_\phi\), or retain suitable within-block data, so that coarsening does not hide relevant incompatibility. That is a research target, not an additional theorem in this release.


---

# Komorebi Space Theory: lossless dyadic residual detail
## v0.7.0 · Komorebi P.

This extension characterizes the information erased by the actual dyadic residual coarsener and constructs bounded coordinates retaining it. It then iterates the construction through every finite number of coarsening levels. The splitting of a bounded surjection is established mathematics. The content here is its explicit realization for the existing, transported tower residual, the independent detail channels, the exactness criterion, and the connected finite-depth hierarchy.

## 1. Fixed towers and scope

Let \(\mathbb K\) be a nontrivially normed field. Retain the sequential Banach towers
\[
 X_{n+1}\xrightarrow{\rho^X_n}X_n,
 \qquad Y_{n+1}\xrightarrow{\rho^Y_n}Y_n,
\]
and their bounded transport and residual spaces
\[
 E=\ell^\infty_n\mathcal L(X_n,Y_n),\qquad
 R=\ell^\infty_n\mathcal L(X_{n+1},Y_n).
\]
The actual compatibility differential is unchanged:
\[
 \boxed{(df)_n=\rho^Y_nf_{n+1}-f_n\rho^X_n.}
\]
Assume contractive bonding maps and specified uniformly bounded target sections:
\[
 \|\rho^X_n\|\le1,\quad \|\rho^Y_n\|\le1,\qquad
 s_n:Y_n\to Y_{n+1},\quad\rho^Y_ns_n=I,\quad\|s_n\|\le S.
\]
All maps in these equations are continuous linear. The sections are supplied input. The existence of bounded sections for arbitrary bonding maps is not asserted.

The schedule is specifically \(\phi(n)=2n\). Write
\[
 R'=\ell^\infty_n\mathcal L(X_{2n+2},Y_{2n}).
\]
The v0.6 coarsening operator, specialized to this schedule, is
\[
 \boxed{(Cr)_n=\rho^Y_{2n}r_{2n+1}+r_{2n}\rho^X_{2n+1}.}
 \tag{1}
\]
It has \(\|C\|\le2\). It is a transported pair sum, not a componentwise sample. Source and target maps can have varying dimensions.

**Lean:** `DyadicResidual.coarsen`, `coarsen_pair`. These use the actual `BanachTower.residualSampleCLM` from v0.6.

## 2. A constructed section of coarsening

For every bounded coarse residual \(c\in R'\), define
\[
 \boxed{(Jc)_{2n}=0,\qquad(Jc)_{2n+1}=s_{2n}c_n.}
 \tag{2}
\]
Parity interleaving is formalized for dependent bounded families. Even and odd coordinates need not have the same types. The interleaving and its inverse preserve the maximum norm.

Using (1),
\[
 (CJc)_n=\rho^Y_{2n}s_{2n}c_n+0=c_n.
\]
Hence
\[
 \boxed{CJ=I_{R'},\qquad\|Jc\|\le S\|c\|,\qquad\|J\|\le S.}
 \tag{3}
\]
This construction needs no propagation gap \(SB_X<1\). It is a section of **coarsening \(C\)**, not a section of the compatibility differential \(d\). It therefore does not contradict the earlier identity-tower obstruction to \(d\) having a right inverse on all bounded residuals.

**Lean:** `BoundedParity.split`, `split_norm`; `DyadicResidual.lift`, `lift_even`, `lift_odd`, `lift_bound`, `lift_opNorm`, `coarsen_lift`, `sectionC`.

## 3. Hidden residual and kernel characterization

Define
\[
 \boxed{H=I_R-JC.}
 \tag{4}
\]
The formalization proves
\[
 CH=0,\qquad H^2=H,\qquad r=Hr+JCr.
 \tag{5}
\]
Its coordinates are
\[
 (Hr)_{2n}=r_{2n},\qquad
 (Hr)_{2n+1}=r_{2n+1}-s_{2n}(Cr)_n.
\]
The complete kernel criterion is
\[
 \boxed{Cr=0\iff
  \forall n,\ \rho^Y_{2n}r_{2n+1}=-r_{2n}\rho^X_{2n+1}.}
 \tag{6}
\]
The continuous linear coordinate equivalence is
\[
 \boxed{
 R\simeq_L\ker C\times R',\qquad
 r\longmapsto(Hr,Cr),\qquad
 (h,c)\longmapsto h+Jc.
 }
 \tag{7}
\]
Here \(\simeq_L\) means a linear bijection continuous in both directions, not an isometry. The kernel of \(C\) is fixed by the tower data. The section \(J\), projection \(H\), and chosen coordinates may depend on the target splitting.

The checked quantitative bounds are
\[
 \boxed{\|Hr\|\le(1+2S)\|r\|,\qquad
 \|r\|\le\|Hr\|+S\|Cr\|.}
 \tag{8}
\]
These are sufficient bounds; no sharpness is asserted.

**Lean:** `hidden`, `hidden_coarsen`, `hidden_idempotent`, `reconstruction`, `kernel_iff`, `coordinates`, `hidden_bound`, `reconstruction_bound` in `DyadicResidual`.

## 4. The two independent hidden channels

The kernel condition (6) contains both transported cancellation and target-kernel information. Define
\[
 a_n=r_{2n},\qquad
 \boxed{\nu_n=r_{2n+1}-s_{2n}\rho^Y_{2n}r_{2n+1}.}
 \tag{9}
\]
Then
\[
 \rho^Y_{2n}\nu_n=0.
\]
With \(c=Cr\), exact reconstruction is
\[
 \boxed{
 r_{2n}=a_n,\qquad
 r_{2n+1}=\nu_n+s_{2n}
   \bigl(c_n-a_n\rho^X_{2n+1}\bigr).
 }
 \tag{10}
\]
For a hidden residual, \(c=0\), so the odd edge is
\[
 r_{2n+1}=\nu_n-s_{2n}a_n\rho^X_{2n+1}.
\]
Thus the kernel is not represented by adjacent scalar cancellation alone. The term \(\nu_n\) can be nonzero while both the even edge and the coarse residual vanish.

Define the normed submodule
\[
 V=\left\{\nu\in\ell^\infty_n\mathcal L(X_{2n+2},Y_{2n+1}):
       \rho^Y_{2n}\nu_n=0\text{ for all }n\right\}
\]
and
\[
 R_{\mathrm{even}}=\ell^\infty_n\mathcal L(X_{2n+1},Y_{2n}).
\]
Every independent bounded triple \((a,\nu,c)\in R_{\mathrm{even}}\times V\times R'\) has a unique bounded synthesis by (10). The package constructs the continuous linear equivalence
\[
 \boxed{
 R\simeq_L(R_{\mathrm{even}}\times V)\times R',
 \qquad r\longmapsto((a,\nu),c).
 }
 \tag{11}
\]
The forward and inverse bounds, with product maximum norms, are
\[
 \|\Phi r\|\le\max(1+S,2)\|r\|,
 \qquad
 \|\Phi^{-1}z\|\le(1+3S)\|z\|.
 \tag{12}
\]
The inverse is a formal mathematical construction. There is no algorithmic complexity or data-compression claim.

**Lean:** `innovation`, `innovation_down`, `reconstruct_odd`, `channels_injective`, `synthesize`, `synthesize_odd`, `unique_synthesis`, `verticalSpace`, `channelsLinear`, `channels_bound`, `channels_inverse_bound`, `channels`.

## 5. Fine exactness is recoverable from retained data

Let \(S_\phi\) sample candidate transports and \(d_\phi\) be the actual sampled differential. The existing identity is
\[
 d_\phi S_\phi=Cd.
\]
Combining it with (5) gives
\[
 \boxed{
 df=0\iff
 d_\phi S_\phi f=0\quad\text{and}\quad Hdf=0.
 }
 \tag{13}
\]
The theorem is stated in Lean using the actual `BanachTower.Exact` predicates. It is not a replacement of fine exactness by a new definition of exactness.

Merely retaining coarse residuals remains insufficient. Equation (13) succeeds because the previously discarded data are retained, not because cancellation has ceased to occur.

**Lean:** `DyadicResidual.exactness_detected`.

## 6. Two checked witnesses

### 6.1 All-level alternating candidate

On the existing real identity towers, retain the candidate
\[
 f_{2n}=I,\qquad f_{2n+1}=2I.
\]
Its residual satisfies
\[
 r_{2n}=I,\qquad r_{2n+1}=-I,\qquad\|r\|=1.
\]
For the identity target splitting, Lean proves
\[
 \boxed{Cr=0,\qquad Hr=r,\qquad\|Hr\|=1,\qquad\nu_n=0.}
 \tag{14}
\]
The nonzero incompatibility is fully visible in the retained detail despite zero coarse residual.

**Lean:** `DyadicDetailExamples.alternating_coarse_zero`, `alternating_hidden_full`, `alternating_hidden_norm`, `alternating_vertical_zero`, `alternating_detected`.

### 6.2 A separate finite target-kernel block

Let
\[
 q(x,y)=x,\qquad s(x)=(x,0),\qquad b(x)=(0,x).
\]
Lean proves
\[
 qs=I,\qquad qb=0,\qquad b\ne0,\qquad b-sqb=b.
\]
This is explicitly a finite block witness, not an additional constructed infinite tower. It shows why deleting the target-kernel channel from (10) would be unsound in general.

**Lean:** `DyadicDetailExamples.BlockKernelWitness.down_up`, `down_vertical`, `vertical_nonzero`, `vertical_is_its_innovation`, `coarse_even_insufficient`.

## 7. Finite multiscale reconstruction

For normed spaces \(R_j\), suppose coarsenings and selected sections satisfy
\[
 C_j:R_j\to R_{j+1},\qquad J_j:R_{j+1}\to R_j,
 \qquad C_jJ_j=I.
\]
Starting from \(r_0=r\), define
\[
 r_{j+1}=C_jr_j,\qquad h_j=(I-J_jC_j)r_j,
\]
\[
 L_0=I,\qquad L_{j+1}=L_jJ_j.
\]
Then, for every finite \(N\in\mathbb N\), including \(N=0\),
\[
 \boxed{r=\sum_{j=0}^{N-1}L_jh_j+L_Nr_N.}
 \tag{15}
\]
Equality of all details below level \(N\) and the final coarse datum is equivalent to equality of the original data. In particular,
\[
 \boxed{r=0\iff (h_j=0\text{ for every }j<N)\text{ and }r_N=0.}
 \tag{16}
\]
These are proved by a finite transported telescoping identity. Completeness or convergence is not needed.

**Lean:** `CoarseningCascade`, `one_layer`, `reconstruction`, `equal_iff`, `zero_iff`.

### Instantiation on the actual towers

After pairing, the target sections are constructed by composition:
\[
 s^{\mathrm{coarse}}_n=s_{2n+1}s_{2n},\qquad
 \|s^{\mathrm{coarse}}_n\|\le S^2.
\]
The corresponding coarse bonding maps remain contractive. This constructs an actual next system and, by recursion, all finite levels. The resulting cascade uses the actual transported residual coarsening at each stage.

For every candidate and every finite \(N\), Lean proves fine exactness iff all retained residual details below \(N\) and the final coarse residual vanish.

**Lean:** `DyadicResidual.sampledSplitting`, `System.next`, `System.stage`, `System.cascade`, `System.residual_reconstruction`, `System.exactness_iff_hierarchy`.

The final term \(L_Nr_N\) is retained. No claim is made that it tends to zero as \(N\to\infty\). Section bounds can grow under repeated composition, so finite-level existence does not imply a uniform infinite-depth bound.

## 8. Verification and limits

Six new modules contain 79 named theorem declarations and 45 indexed non-theorem declarations. The cumulative project contains 50 proof modules, 559 named theorems and 248 indexed non-theorems. Counts include auxiliary declarations, not mathematical discoveries. All 44 prior proof modules are unchanged.

`checks/computation/dyadic_details_exact.py` is a second implementation over exact rational matrices. It checks 216 variable-dimension pair configurations and 24 finite cascade configurations, with 4,260 explicit positive assertions and three false-claim rejection controls. Its norm is the exact induced infinity norm, computed by absolute row sums. The all-level and universally quantified results come from Lean proof terms, not extrapolation from these tests.

This release does not prove arbitrary bounded target splittings, general unbounded/independent schedules, noncontractive norm estimates, an invariant-independent repair doctrine, a nonexact eventual quotient, the full pro-category comparison, higher obstruction theory, or unrestricted descent. It does not establish infinite-depth convergence, orthogonality, optimal compression, optimal conditioning, or novelty relative to the literature.

The next extension is to retain analogous detail for variable-length blocks and compare the resulting coordinate systems under changes of grouping. The present theorem concerns actual repeated dyadic grouping with explicitly selected sections.


---

# Komorebi Space Theory: infinite-depth residual reconstruction
## v0.8.0 · Komorebi P.

The finite retained-detail identity now has an infinite-depth theory. Three assertions are distinguished throughout:

\[
\boxed{\text{uniqueness from all details}\quad\neq\quad
\text{coordinatewise reconstruction}\quad\neq\quad
\text{reconstruction in the uniform norm}.}
\]

For the actual dyadic tower construction, the first two hold for every bounded residual. Uniform-norm reconstruction has separate necessary and sufficient conditions. Abstract split cascades can also carry a nonzero persistent coarse component. The statements below use the existing objects and maps, rather than replacing the tower residual by a scalar surrogate.

## 1. Split coarsening cascades and lifted remainders

Let \(\mathbb K\) be a nontrivially normed field. Let \(R_j\) be normed \(\mathbb K\)-spaces, with continuous linear maps
\[
C_j:R_j\to R_{j+1},\qquad J_j:R_{j+1}\to R_j,
\qquad C_jJ_j=I.
\]
For \(x\in R_0\), set
\[
x_0=x,\qquad x_{j+1}=C_jx_j,
\qquad h_j(x)=(I-J_jC_j)x_j,
\]
\[
L_0=I,\qquad L_{j+1}=L_jJ_j.
\]
The old finite identity is
\[
x=\sum_{j<N}L_jh_j(x)+L_Nx_N.
\]
Define continuous linear maps on the original space:
\[
\boxed{Q_Nx=L_Nx_N,\qquad S_Nx=x-Q_Nx.}
\tag{1}
\]
Thus \(Q_N\) is the **lifted** coarse remainder, not the raw coarse coordinate \(x_N\). Lean proves
\[
Q_N^2=Q_N,\qquad S_N^2=S_N,\qquad Q_NS_N=0,
\]
\[
\boxed{Q_mQ_n=Q_nQ_m=Q_n\quad(m\le n),}
\tag{2}
\]
\[
\boxed{L_nh_n(x)=Q_nx-Q_{n+1}x,\qquad
S_Nx=\sum_{n<N}L_nh_n(x).}
\tag{3}
\]
These are nested, not necessarily orthogonal, projections. No completeness is needed here.

**Lean:** `CoarseningCascade.levelMap`, `remainder`, `reconstructed`, `level_restore`, `remainder_idempotent`, `remainder_nested_left`, `remainder_nested_right`, `detailTerm_eq_remainder_sub`, `partial_eq_sum`.

## 2. What an infinite detail record may omit

Define the persistent coarse submodule
\[
\boxed{\mathcal P_\infty=\{x\in R_0:\forall N,\ Q_Nx=x\}.}
\tag{4}
\]
Lean proves
\[
\boxed{x\in\mathcal P_\infty\iff\forall n,\ h_n(x)=0,}
\tag{5}
\]
\[
\boxed{\bigl(\forall n,\ h_n(x)=h_n(y)\bigr)
\iff x-y\in\mathcal P_\infty.}
\tag{6}
\]
For (5), zero details make consecutive remainders equal by (3), and \(Q_0=I\). Conversely, a persistent input has every transported detail zero; the restoration maps are injective because coarse observation is their left inverse.

Therefore all details determine a general cascade input only modulo \(\mathcal P_\infty\). Its disappearance must be proved in a concrete model, not assumed from the word "resolution."

**Lean:** `persistent`, `persistent_iff_details_zero`, `equal_details_iff_persistent_difference`, `restore_injective`.

## 3. The exact criterion for norm reconstruction

The error identity is
\[
\boxed{\|x-S_Nx\|=\|Q_Nx\|.}
\tag{7}
\]
Consequently,
\[
\boxed{S_Nx\longrightarrow x\iff Q_Nx\longrightarrow0,}
\tag{8}
\]
where both limits are in the original norm of \(R_0\). Equivalently,
\[
\lim_{N\to\infty}\sum_{n<N}L_nh_n(x)=x
\iff \lim_{N\to\infty}L_Nx_N=0.
\]
Define the recoverable submodule
\[
\boxed{\mathcal D=\{x:Q_Nx\to0\}.}
\tag{9}
\]
Its linear-submodule structure is constructed. The formalization proves
\[
\mathcal D\cap\mathcal P_\infty=\{0\},
\]
and the detail record is injective on \(\mathcal D\).

These are statements about natural-order partial sums. They do not infer an unconditional `HasSum` statement from ordered convergence alone.

**Lean:** `partial_error`, `partial_tendsto_iff`, `ordered_reconstruction_iff`, `recoverable`, `persistent_recoverable_zero`, `details_injective_on_recoverable`.

## 4. A convergent boundary is necessarily persistent

If \(Q_Nx\to z\), continuity of \(Q_m\) and (2) give
\[
Q_mz=\lim_NQ_mQ_Nx=\lim_NQ_Nx=z.
\]
Hence
\[
\boxed{Q_Nx\to z\Longrightarrow z\in\mathcal P_\infty,
\qquad S_Nx\to x-z.}
\tag{10}
\]
Under completeness of \(R_0\), absolute summability of the transported details implies
\[
\sum_n\|L_nh_n(x)\|<\infty
\Longrightarrow
x-\sum_n L_nh_n(x)\in\mathcal P_\infty.
\tag{11}
\]
If also \(\mathcal P_\infty=0\), then
\[
\boxed{x=\sum_n L_nh_n(x).}
\tag{12}
\]
The last sum is supported by the absolute-summability theorem, not merely notation for an unproved infinite series.

**Lean:** `remainder_limit_persistent`, `reconstruction_with_boundary`, `absolutely_summable_boundary`, `tsum_reconstruction`.

## 5. A density characterization, rather than a circular hypothesis

Define the finite-core set
\[
\boxed{\mathcal F=\bigcup_{N\ge0}\ker Q_N.}
\tag{13}
\]
These are inputs eliminated by some finite coarse depth. Nesting implies they remain eliminated at every greater depth. Each finite reconstructed approximant satisfies
\[
S_Nx\in\mathcal F.
\]
It follows without a uniform operator bound that
\[
\mathcal D\subseteq\overline{\mathcal F}.
\]
Assume additionally
\[
\boxed{\sup_N\|Q_N\|\le K<\infty.}
\tag{14}
\]
Lean proves the converse, and therefore
\[
\boxed{\mathcal D=\overline{\mathcal F}.}
\tag{15}
\]
In particular,
\[
\boxed{\forall x,\ S_Nx\to x
\iff\overline{\mathcal F}=R_0}
\tag{16}
\]
under (14).

For the nontrivial implication, approximate \(x\) by \(y\in\ker Q_M\). For \(N\ge M\),
\[
\|Q_Nx\|=\|Q_N(x-y)\|\le K\|x-y\|.
\]
This proves convergence by choosing the approximation before choosing the depth. No density or uniform bound is inferred automatically from the existence of sections.

**Lean:** `finiteCore`, `finiteCore_recoverable`, `partial_mem_finiteCore`, `recoverable_mem_closure_finiteCore`, `recoverable_iff_closure_finiteCore`, `all_recoverable_iff_dense`, `ordered_reconstruction_of_dense`.

## 6. Quantitative decay must include restoration gain

Define
\[
\boxed{G_N=\prod_{j<N}\|J_j\|.}
\tag{17}
\]
The checked estimate is
\[
\boxed{\|x-S_Nx\|\le G_N\|x_N\|.}
\tag{18}
\]
Therefore
\[
G_N\|x_N\|\to0\Longrightarrow x\in\mathcal D.
\]
For nonnegative constants \(B,C,a,b\), if
\[
G_N\le Ba^N,\qquad\|x_N\|\le Cb^N,\qquad ab<1,
\]
then
\[
\boxed{\|x-S_Nx\|\le BC(ab)^N\longrightarrow0.}
\tag{19}
\]
Contractive lifts give \(G_N\le1\), in which case raw coarse decay suffices. Without that control it need not suffice.

**Lean:** `liftGain`, `restore_gain_bound`, `reconstruction_error_bound`, `recoverable_of_weighted_coarse_decay`, `recoverable_of_geometric_bounds`, `recoverable_of_coarse_decay`.

## 7. The actual dyadic residual hierarchy has no persistent component

Now specialize to the existing `DyadicResidual.System`, with its actual sequential Banach towers, contractive bonds, supplied bounded target sections, transported coarsener, and parity lift:
\[
(Cr)_n=\rho^Y_{2n}r_{2n+1}+r_{2n}\rho^X_{2n+1},
\]
\[
(Jc)_{2n}=0,\qquad(Jc)_{2n+1}=s_{2n}c_n.
\]
All coarsening levels are the previously constructed actual dyadic systems. They are not arbitrary copies of a scalar example.

Lean proves
\[
\boxed{\mathcal P_\infty=0}
\tag{20}
\]
for every such system, without a convergence hypothesis.

The proof uses strong induction on the coordinate index, uniformly over the scale. Zero hidden detail reveals every even coordinate directly. An odd coordinate reduces to a coordinate at the next scale with index \(\lfloor k/2\rfloor<k\). Every fixed coordinate is therefore forced to zero.

Consequences:
\[
\boxed{\forall j,\ h_j(r)=h_j(s)\Longrightarrow r=s,}
\tag{21}
\]
\[
\boxed{\operatorname{Exact}(f)
\iff\forall j,\ h_j(df)=0.}
\tag{22}
\]
Here \(d\) and `Exact` are the existing compatibility differential and predicate. This does not define exactness in a new way.

**Lean:** `DyadicResidual.System.all_details_zero_implies_zero`, `persistent_residual_eq_bot`, `infinite_details_injective`, `exactness_iff_all_details`.

## 8. Every coordinate is reconstructed at finite depth

There is a stronger actual-dyadic support statement:
\[
\boxed{k+1<2^N\Longrightarrow (Q_Nr)_k=0.}
\tag{23}
\]
Thus
\[
\boxed{k+1<2^N\Longrightarrow (S_Nr)_k=r_k.}
\tag{24}
\]
In particular, for every bounded residual \(r\) and every fixed coordinate \(k\),
\[
\boxed{(S_Nr)_k\longrightarrow r_k.}
\tag{25}
\]
The equality is eventually exact, not just an approximation. Convergence here is in the operator norm at the fixed coordinate. No uniform bound over all \(k\) follows from this statement.

The finite threshold is strict. For the identity-tower pair sum, a remainder can be nonzero at the last coordinate \(k=2^N-1\) of a block.

**Lean:** `finite_details_zero_coordinate`, `remainder_coordinate_zero`, `reconstruction_coordinate`, `coordinatewise_reconstruction`. Typed wrappers `residualLevel`, `reconstructedResidual`, and `residualRemainder` expose the actual dependent operator types.

## 9. Sufficient norm-reconstruction conditions on the actual towers

The original residual space is complete by the existing bounded-product and continuous-linear-map instances. Since (20) was proved, absolute summability is sufficient:
\[
\boxed{\sum_j\|L_jh_j(r)\|<\infty
\Longrightarrow r=\sum_jL_jh_j(r).}
\tag{26}
\]
Any norm-convergent sequence \(Q_Nr\) must converge to zero. This does not prove that it converges.

If the supplied target-section bound is at most one, that bound remains at most one under every actual dyadic section composition. Thus all cascade lifts are contractive and
\[
\boxed{\|r-S_Nr\|\le\|r_N\|.}
\tag{27}
\]
Consequently \(\|r_N\|\to0\) gives norm reconstruction in this case.

**Lean:** `cascade_zero_complete`, `absolute_residual_reconstruction`, `convergent_remainder_zero`, `stage_section_bound_le_one`, `cascade_lifts_contractive`, `residual_error_le_coarse`, `residual_reconstruction_of_coarse_decay`.

The theorem does not assert that all bounded residuals satisfy these analytic hypotheses. Nor does it identify arbitrary sequences of detail values with the image of the full detail map.

## 10. A fully specified recovery domain: bounded sequences

As a separate model, take \(R_j=\ell^\infty(\mathbb N,\mathbb R)\) at every scale and
\[
(Cx)_k=x_{k+1},\qquad Jx=(0,x_0,x_1,\ldots).
\]
Then \(CJ=I\), and Lean proves
\[
(Q_Nx)_k=\begin{cases}0&k<N,\\x_k&k\ge N.\end{cases}
\tag{28}
\]
The exact characterization is
\[
\boxed{x\in\mathcal D\iff x_k\to0.}
\tag{29}
\]
Thus \(\mathcal D=c_0\) inside the bounded-sequence space, in the ordinary meaning of sequences tending to zero. This is a theorem relating the actual remainder to coordinate decay, not the definition of recoverability.

Here
\[
\|Q_N\|\le1,\qquad\mathcal P_\infty=0,
\]
but for \(\mathbf1=(1,1,\ldots)\),
\[
\boxed{\|Q_N\mathbf1\|=1\quad\text{for all }N.}
\tag{30}
\]
Therefore uniform boundedness plus a trivial persistent submodule does not imply norm reconstruction for every input. Density is a separate obligation.

For \(x_k=q^k\), \(0\le q<1\), the package constructs the actual bounded sequence and proves
\[
\boxed{\|x-S_Nx\|=q^N.}
\tag{31}
\]
This provides an all-depth positive reconstruction example with an exact error rate.

**Lean:** `SequenceCascade.recoverable_iff_vanishes`, `persistent_eq_bot`, `ones_remainder_norm`, `stability_and_separation_not_enough`, `geometric_recoverable`, `geometric_reconstruction_error`.

## 11. A coarse-decay counterexample with a persistent boundary

Take \(R_j=\mathbb R\), \(C_j=\tfrac12I\), \(J_j=2I\). Then
\[
C_jJ_j=I,\qquad x_N=2^{-N}x,\qquad L_N=2^NI,
\]
so
\[
\boxed{x_N\to0,\qquad Q_Nx=x,\qquad h_j(x)=0.}
\tag{32}
\]
For \(x=1\), raw coarse data tend to zero and the transported details are absolutely summable because they are all zero, yet reconstruction from those details gives zero, not one. The entire input is persistent coarse information.

This is a counterexample in the explicitly constructed scalar split cascade, not a claim that the actual dyadic hierarchy has a nonzero persistent subspace. The latter is ruled out by (20).

**Lean:** `CascadeBoundaryExamples.coarse_tends_zero`, `remainder_identity`, `every_detail_zero`, `coarse_decay_and_summability_not_enough`.

## 12. Verification and boundaries

The release adds six proof modules: `CascadeProjections`, `CascadeLimits`, `CascadeDensity`, `SequenceCascade`, `CascadeBoundaryExamples`, and `DyadicInfiniteReconstruction`. They add 97 named theorems and 23 indexed non-theorem declarations. The cumulative project has 56 modules, 656 named theorems, and 271 indexed constructions. Counts include auxiliary declarations, not discoveries.

The complete clean build and complete theorem and construction axiom audits passed. Original v0.7 proof modules remain byte-identical. The delivery receipt separately records fresh-extraction replay and source/compiled hash comparisons.

The independent exact-rational computation covers 36 variable-dimension finite cascades, 48 dyadic configurations, and 230 sequence/scalar cases, with 8,778 explicit assertions. Three deliberately false variants are rejected. It compares recursive dyadic remainders with independent block-sum formulas, checks nested projections, reconstruction and gain bounds, and tests the strict finite-coordinate threshold. Finite checks do not establish infinite convergence; the universal statements above have Lean proof terms.

Not proved: universal sup-norm recovery of all dyadic bounded residuals, unconditional summability without an absolute-summability hypothesis, uniform norm bounds on every hierarchy, orthogonality, a basis/Riesz-basis theorem, surjectivity onto arbitrary infinite detail sequences, arbitrary-block lossless coordinates, grouping-independent conditioning, full pro-category comparison, stacks, higher obstruction theory, unrestricted arithmetic correspondence, data compression or computational complexity. No novelty claim is made relative to the literature.


---

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


---

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


---

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
