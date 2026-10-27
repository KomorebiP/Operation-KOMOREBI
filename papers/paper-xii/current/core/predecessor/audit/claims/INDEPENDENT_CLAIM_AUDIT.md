# Paper XII: independent mathematical claim audit

Audit date: 6 October 2026. This audit reads the statements and proofs, reconstructs the critical implications from their definitions, and distinguishes conditional arithmetic leaves from proved algebraic deductions. It is an independent subagent review, not a second Lean compilation. Agreement with the manuscript's status files is not used as mathematical evidence.

**Normalized overall claim.** For supplied represented deformation data, finite modules or perfect complexes with full patched support, actual coefficient/control maps, a compatible Hecke point, and an applicable realization input, the paper's algebraic deductions give a nonzero specialized Hecke eigensystem and identify the specialization with the attached representation after semisimplification. Separately, finite occupied forests of actual continuous conjugacy classes over complete separated coefficient rings give actual continuous adic representations, retaining the declared integral polynomial equations. Existing compatible families with a common Frobenius spine are compared member by member.

**Primary verdict: conditional on a named input.** The final conditional automorphic conclusions are correct with the named representability, residual occupancy, patching/support, comparison-point, classicality, attached-representation, common-polynomial/density, semisimplification, and Brauer–Nesbitt inputs. The internal algebraic support, packet, finite-forest, and specified adic-effectivity deductions pass. The paper does not prove those arithmetic inputs, universal companion existence, or unrestricted reciprocity. Ambiguous contextual interfaces in the preserved revised text were made explicit in the traditional final edition; the higher Fitting proof also received its large-index boundary case.

## Authoritative sources and scope

The initial raw revised target was:

`source/latest_v0171/Paper_XII_Complete_v0.17.1_With_Visual_Appendix/formal_release/paper/Paper_XII_Revised_Formalization_Complete_v0.17.0.tex`

SHA-256: `5b1aa5b7d8919d60b53cd85fd900dc4ab98fdcd52991f1f48380535ab7243cc4`.

The original literal wording was read from:

`source/original_package/PSC_Paper_XII_Strengthened_Annals_Edition_Package/PSC_Paper_XII_Strengthened_Annals_Edition.tex`

SHA-256: `3333119951e17f30281c870eb70267a7554152d4262b4419e086aa41fa07898f`.

The publication target is `traditional/Paper_XII_Traditional_Final.tex`. Exact final hashes and statement locators are recorded in `CLAIM_OBLIGATION_MATRIX.json`; the report does not mutate raw sources or author files.

The 49 internal numbered claims consist of 27 theorems, 14 corollaries, 7 propositions, and 1 lemma. They exclude 3 worked examples, 8 standard facts, and the definitions and remarks. The three worked examples were nevertheless read and checked because they delimit the main conclusions. The preserved historical coverage reports are separate from the present mathematical review.

The relevant proof-audit obligations are general logic/typing, covariance and completion, finite group actions, computation boundaries, and exact external-source matching. No spectral-sequence, grading-sign, or homotopy-convergence claim is used to manufacture an additional conclusion.

## Dependency graph

The following list records implication order; each external leaf is explicitly marked.

1. **Local quotient chain.** Ordinary finite tensor quotient identity → quotient topology → completion/closed-quotient comparison → actual completed tensor quotient (3.1) → closed-kernel local-condition test (3.2) → actual global base change (3.3). Representability of the underlying arithmetic deformation functor is **external**, not obtained from a ring pushout.
2. **Ordinary support chain.** Finite-generation annihilator criterion (6.2) → Noetherian nilpotence criterion (6.7); localization and Nakayama → quotient support (6.9) → full-support descent (6.11) → corrected component occupancy (6.12). Full patched support is a **supplied patching input**.
3. **Derived support chain.** Bounded finite-projective model → tensor associativity at corresponding residue fields → faithful extension of fields → quotient derived support (6.16) → descent (6.18) → a surviving integer degree (6.19). The cited cohomological support standard fact 6.15 is **not needed** by this proof route.
4. **Hecke chain.** Ring isomorphism and actual carrier identification → support/Fitting transport (7.1) → finite-module field-fiber test (7.4) → scalar eigensystem (9.3). Alternatively, perfect-model specialization gives the derived scalar eigensystem. Artin ring decomposition (8.1) is **external algebraic input** for canonical finite Hecke packets; it does not assert occupancy.
5. **Finite occupancy chain.** Finite-dimensional descending subspaces → stabilization (8.7); finite-dimensional stable images → surjection on stable cores (8.10) → recursive nonzero inverse-limit sequence (8.11). Nonzero levels alone do not imply nonzero stable cores.
6. **Adic class chain.** Finitely generated ideal and finite residue → finite coefficient quotients → finite conjugacy orbits of frames → finite nonempty actual representative sets → branch in the finite rooted forest → compatible matrices and inverse matrices → actual adic group representation → continuity → integral Frobenius, inertia, and polynomial-ideal effectivity (10.5). No lifting of a prescribed conjugating matrix is assumed.
7. **Arithmetic identification chain.** A particular nonzero eigensystem → **supplied applicable classicality/occurrence theorem** → **supplied attached continuous semisimple representation** and common Frobenius polynomials → coefficientwise continuity and dense conjugacy union → equality for every group element → **algebraic Brauer–Nesbitt plus supplied semisimplification** → invertible linear intertwiner. Existing common-spine families are then compared at each coefficient place; their existence is **external**.

No circular dependency was found. A complete search of the raw revised paper, original paper, and production Lean sources for Paper XI references/imports found none. Production source reuses Paper X modules. The final explanatory sentence saying Paper XI's general Conjecture 66 is not assumed is a boundary statement, not a new theorem dependency.

## Claim card A: completed tensor quotient, 3.1

**Objects.** A finite family of complete Noetherian local coefficient algebras `R_i` with the common coefficient residue field `k`, closed ideals `I_i`, ordinary tensor `S = tensor_O R_i`, ideal of definition `a = m_O S + sum_i m_i S`, and relation ideal `L = sum_i I_i S`. The claimed target uses the actual Hausdorff completion of this adic ring. The closed ideal `J` is generated by the images of the `I_i` in that actual completion.

**Conclusion.** A canonical coefficient-algebra isomorphism, continuous with continuous inverse, between the completed tensor of the factor quotients and `widehat(S)/J`, commuting with every canonical factor map.

**Primary verdict: proved as written.** The fixed coefficient residue-field convention is material to locality, while the quotient comparison itself is more general.

Fresh derivation:

* Multilinearity gives the ordinary identity `S/L = tensor_O (R_i/I_i)`. Quotienting the ideal `a` gives precisely the natural scalar-plus-factor ideal on the quotient tensor.
* The Hausdorff completion of `S/L` is the quotient of the Hausdorff completion of `S` by the closed extended relation ideal. The quotient is Hausdorff because that subgroup is closed. It is complete because the adic additive uniformity is countably based: a Cauchy sequence of quotient classes can be lifted recursively, correcting each lift by a relation so that consecutive differences lie in a prescribed decreasing sequence of open ideals; the corrected representatives form a Cauchy sequence in the completion. Their limit supplies the quotient limit.
* The two natural comparison maps are inverse because their composites agree on the dense images of `S/L` and are continuous into Hausdorff targets. This proves actual inverse laws, not only an abstract universal property without object construction.
* The closure of the extended relation ideal agrees with the closure of the ordinary relation ideal's image. To see the nontrivial inclusion, approximate each completed coefficient occurring in a finite ideal sum by ordinary tensor elements; ideal multiplication preserves every adic neighborhood. Thus no extra relation ideal is silently substituted.
* The ordinary quotient identity preserves coefficients and factor maps before completion, and continuous extension retains these identities.
* The common residue maps give `S/a = k`. Finite generation of the defining ideal identifies the completion topology with the topology of the extended ideal; that ideal is the actual maximal ideal. This is what permits the completed object to enter the complete local deformation category.

Boundary obligations pass: for an empty family the ordinary tensor is `O` and the scalar term retains its adic topology; for a unary family the comparison reduces to completion of a quotient; zero factor ideals impose no relation; a unit factor ideal produces the zero ring on both sides. The zero ring is not called a local coefficient algebra with residue field `k`. Factor quotient ideals and closure are used at the actual level claimed.

## Claim card B: local-condition factorization and global base change, 3.2–3.3

**Objects.** A continuous local coefficient-algebra structural map `A = Rloc → B = R^square`, with the represented global and local rings complete Noetherian local and maximal-adic; `A/J` is the independently constructed completed tensor of the local quotients. The final 3.3 statement uses continuous local coefficient-algebra points into complete Hausdorff coefficient test rings.

**Conclusion.** The actual completed global tensor is canonically `B/closure(JB)`. Its continuous coefficient points are the global points whose original local restrictions kill every specified local ideal; quotient factors are unique, local when the original point is local, and natural in coefficient targets.

**Primary verdict: proved as written for the clarified final statement.** The preserved revised statement's context was under-specified in its first sentence; its proof invoked local-map “conventions” without a dedicated conventions section. Definition 2.1 supplied the intended local category. The final edition now states this category explicitly.

Fresh derivation:

1. The ordinary algebra identity is `B tensor_A (A/J) = B/JB`.
2. The structural local map carries `m_A` into `m_B`, so the tensor's scalar-plus-factor defining ideal corresponds to the image of `m_B` under the ordinary quotient identity. This is the exact topology comparison needed for completing the ordinary tensor identity.
3. Since `B` is already complete, the completion/closed-quotient comparison gives `R^tau = B/closure(JB)`, respecting the original global map. That map is surjective.
4. A continuous map with Hausdorff target has closed kernel. It kills `closure(JB)` iff it kills `JB`, iff its restriction to `A` kills `J`, iff all the original local restrictions kill the factor ideals. This proves the local-condition criterion without discarding closure.
5. Actual quotient maps give uniqueness and continuity. Surjectivity gives locality of a factor when locality is assumed for the original point. Composing two candidate coefficient changes and using uniqueness gives naturality.

In maximal-adic local categories continuity itself forces a ring map to be local: if an element of `m_A` mapped to a unit, none of its powers could lie in `m_B`, contradicting the continuity bound `f(m_A^N) ⊂ m_B`. Explicit locality therefore clarifies the intended context rather than repairing a counterexample in that category.

These coefficient test points must not be identified with the later characteristic-zero field-valued specializations. For example, a continuous inclusion `O → E` into its valued fraction field sends a uniformizer to a unit, hence is not a local ring map in the deformation-test-ring sense. Sections 7, 9, and 12 use algebraic/generic field points, imposing continuity of the specialized representation separately. The quotient factorization argument with a closed kernel can also be applied to such a continuous field evaluation, but it does not turn that evaluation into a local coefficient-test point.

The ring identity proves a base change of an already represented functor. It does not prove that every desired Hodge, Weil–Deligne, component, or arbitrary arithmetic condition is represented by one of the declared quotient ideals.

## Claim card C: ordinary and derived support descent

**Ordinary objects.** A finite module over a commutative Noetherian ring; a quotient by any ideal, including zero and the unit ideal; actual patched quotient and module-control identifications.

**Conclusion.** `Supp_(R/I)(M/IM) = Supp_R(M) ∩ V(I)`, and hence full patched support descends to full finite-level support. Near faithfulness is equivalent to full support under the finite/Noetherian assumptions.

**Primary verdict: proved as written.** The corrected final containment in 6.12 is required.

At a prime containing `I`, localization identifies the specialized module with `M_p / I_p M_p`. If `M_p` is nonzero, it is finite over the local ring and `I_p` lies in its maximal ideal; Nakayama excludes a zero quotient. This is the critical implication. Without finite generation it fails, for example for `R = Z_(p)`, `M = Q`, and `I = (p)`: the generic localization of `M` is nonzero but `M/pM = 0` at the closed point. The paper retains the needed finiteness.

For a finite module, the annihilator detects support because the product of finitely many denominators killing chosen generators is itself outside the prime. Full support says every annihilator element lies in every prime and is nilpotent. Over a Noetherian ring the annihilator has finitely many generators; if their nilpotence exponents are `N_i`, every product of degree greater than `sum_i(N_i-1)` is zero. Thus the whole annihilator ideal is nilpotent. Reducedness then turns near faithfulness into faithfulness.

The corrected component corollary follows because every component is a subset of the full support. The original reverse containment is false even for a fully supported node ring and its regular module: each component omits the other generic point.

**Derived objects.** An actual derived-category perfect object with a bounded finite-projective model, actual quotient coefficient ring and derived-control isomorphism, and any field-valued point.

**Conclusion.** Derived support restricts along the quotient and full support yields a nonzero derived field fiber with some nonzero integer-degree cohomology.

**Primary verdict: proved as written.** A projective model computes scalar extension, and its scalar extension remains bounded finite projective. At corresponding quotient/source primes, the residue field fibers are identified by tensor associativity; more generally a field point at kernel `p` is an extension of the residue field at `p`. A field embedding is faithfully flat, so it preserves and reflects acyclicity. This proves nonvanishing in the derived category, not merely a nonzero term of a cochain complex. A bounded acyclic complex represents zero; therefore a nonzero fiber has a nonzero cohomology object, and bounds constrain its integer degree.

No flatness of the ring quotient is assumed: the tensor is derived. The surviving cohomological degree and its classicality are not supplied by support. The cited equality of support with the union of cohomological supports is unnecessary for these direct fiber proofs.

The Fitting formulas pass for finite presentations. The final 6.4 proof now handles `r>n` separately: fiber dimension is at most presentation target rank `n`, while `Fitt_(r-1)(M)=R`; both loci are empty. For `1≤r≤n`, the rank condition is exactly vanishing of minors of size `n-r+1`. This removes a negative-minor-size expression from the original all-index argument without changing the theorem.

## Claim card D: finite packets and inverse limits

**Finite packet objects.** A finite-dimensional commutative algebra over a field and a finite module; supplied canonical Artin localization decomposition. For generalized eigenspaces, an algebraically closed coefficient field and a finite list of commuting generators are retained. For the trace criterion, characteristic zero is retained.

**Primary verdict: conditional on a named input.** The named input is the canonical Artin decomposition (external standard fact 8.1); the module packet and generalized-eigenspace deductions pass.

Orthogonal idempotents summing to one split the actual module. Localization at a selected maximal ideal kills the other idempotent factors, and identifies the selected one with its localized module. Nilpotence in the selected Artin local factor supplies a uniform positive exponent. On each other factor at least one generator-minus-eigenvalue is a unit, so a vector satisfying all nilpotence tests cannot have a nonzero coordinate there. This is valid for nilpotent Jordan packets; semisimplicity is not needed. An idempotent is diagonalizable with eigenvalues zero and one, so its trace is the dimension cast into the field. Characteristic zero is necessary for nonzero trace to detect positive dimension.

**One finite carrier.** Nested idempotent relations imply nested ranges. Positive finite dimensions cannot decrease infinitely, so the ranges eventually agree at a nonzero subspace. Primary verdict for 8.7–8.8: **proved as written**. The infinite `ell^2` tail example passes and shows why finite dimension matters.

**Changing finite carriers.** For any coherent linear inverse system, images in a fixed level form descending finite-dimensional subspaces and stabilize. Given `y` in the stable core at level `m`, the sets of preimages of `y` within successive images at level `m+1` are nonempty descending affine subspaces. Their dimensions eventually agree, and inclusion of nonempty affine spaces of the same dimension is equality. Thus a preimage lies in every image and belongs to `Y_(m+1)`. Primary verdict for 8.10–8.12: **proved as written**.

A prescribed nonzero vector in `Y_1` can be lifted recursively, and every lift remains nonzero because it maps to that vector. The hypothesis that every core is nonzero is sufficient; the proof really starts from nonzero `Y_1`. There is no false inference from nonzero levels to nonzero cores: an inverse system with `V_m=E` and all transitions zero has nonzero levels but zero inverse limit. Finite-dimensional systems automatically satisfy stabilization of images; nonzero stable images are the additional occupancy requirement.

**Finite sets.** Nonempty finite levels with total reduction maps and one residual root admit a branch. Every finite-depth path is obtained by starting at a vertex of that depth and reducing, so the finite path constraints have the finite intersection property. Equivalently König's lemma applies to the locally finite rooted tree. Transition surjectivity is unnecessary. Primary verdict for 10.3–10.4 with the final declared-admissibility clarification: **proved as written**. An empty admissible level obstructs only complete realizations whose reductions are required to lie in these particular admissible sets. If the levels are merely selected subsets of all possible realizations of a spine, an empty selected level cannot exclude a complete realization outside those sets. The final forest wording therefore makes the reduction-membership contract explicit; unrestricted nonexistence would require exhaustive coverage of all admissible reductions.

## Claim card E: class reconstruction and polynomial effectivity, 10.5

**Objects.** For each coefficient index `lambda`, a commutative ring `O_lambda`, complete and separated for a finitely generated ideal `I_lambda`, finite residue ring, finite matrix index set, finite nonempty admissible class sets of actual continuous representations to `GL_D(O/I^n)`, downward closure under reduction, and a unique declared residual class. The characteristic polynomials have supplied integral coefficient lifts matching the algebraic spine after the supplied coefficient map. Every admissible frame kills each declared polynomial ideal.

**Conclusion.** Actual continuous integral representations with all required reduction classes, residual class, prescribed integral/evaluated Frobenius polynomials, triviality on the declared subgroup, and actual quotient-ideal factorization.

**Primary verdict: proved as written for the revised and final statement.** Original 10.5 is incomplete at the effectivity implication; a bare finite forest only proves a branch of its labels.

Fresh derivation of the critical representative step:

1. Let `I` have `q` generators. Every `I^r/I^(r+1)` is generated over the finite ring `O/I` by the finitely many monomials of degree `r` in those generators. Therefore it is a finite set. Induction on the extension `0 → I^r/I^(r+1) → O/I^(r+1) → O/I^r → 0` proves every coefficient quotient finite. No Noetherian assumption on `O` is needed here.
2. A conjugacy class of actual quotient representations is one orbit under the finite group `GL_D(O/I^n)`. Thus it contains only finitely many actual matrix functions, even if the source group is infinite. A finite admissible union of such orbits is a finite set of actual representatives.
3. Conjugation preserves continuity, and the class admissibility predicate is pulled back to every actual representative. Reduction of any admissible representative has a class in the previous admissible set. Consequently actual reduction gives a total map between these finite nonempty actual sets. It need not be surjective.
4. Applying the finite-set branch argument to these actual sets selects strictly compatible representatives, not merely compatible classes. This avoids any claim that an arbitrarily prescribed conjugating matrix lifts through a quotient.
5. Reconstruct each matrix entry using `O = lim O/I^n`. Reconstruct inverse entries in the same way. The matrix/inverse identities hold modulo every power and hence hold integrally by separatedness. Thus the reconstruction lies in the actual general linear group. The representation product and identity equations likewise hold modulo every power, hence integrally.
6. The adic topology is the inverse-limit topology on entries. Every quotient coordinate of the reconstructed group function is continuous, so the function is continuous. Inverse coordinates are treated identically. Applying the supplied continuous coefficient map gives a continuous map to the declared coefficient target with its matrix topology.
7. Characteristic polynomial coefficients are finite polynomial expressions in matrix entries; evaluation commutes with reduction. Their differences from the supplied integral coefficients lie in every `I^n`, so separatedness makes them zero. The same entrywise argument retains subgroup triviality.
8. A polynomial in the ideal `J_(lambda,u)` involves only finitely many of the possibly infinitely many variables `x_(g,a,b)`. Its evaluation commutes with reduction, and every admissible finite frame kills it. Its integral value is therefore in every ideal power and is zero. The actual evaluation homomorphism kills the entire ideal and factors through the actual ring quotient.

Boundary checks: an empty matrix index set gives the trivial group and characteristic polynomial one; a zero ideal gives a discrete constant coefficient tower; the unit ideal together with separatedness forces the coefficient ring to be zero, so with a unital map to a nonzero field the hypotheses have no instance. Precision zero is the trivial quotient, not an extra occupied residual level. An empty index set of coefficient places is vacuous; simultaneous choices over an arbitrary supplied index set use ordinary choice.

This result retains a residual **conjugacy class**, not a prescribed matrix frame. It asserts no uniqueness under integral conjugacy. Its finite class occupancy and continuity assumptions must be established arithmetically. A polynomial condition imposed only in a special finite-level frame does not satisfy the stated every-frame hypothesis. Nor are arbitrary Hodge or Weil–Deligne conditions automatically ideals in this matrix-entry polynomial ring. Those effectivity questions remain separate.

## Claim card F: conditional automorphic realization and propagation

**Objects.** A finite or perfect automorphic Hecke carrier, actual full-support/control data, a ring comparison and compatible coefficient-field point, a particular nonzero scalar Hecke eigensystem, and a declared realization theorem applying to that eigensystem. The coefficient field is Hausdorff with continuous ring operations; the specialization and attached comparison representation are continuous. A semisimplification and the general Brauer–Nesbitt contract are supplied. The two representations share characteristic polynomials on the same dense Frobenius conjugacy union, using one geometric Frobenius and attached-representation normalization.

**Conclusion.** An actual coefficient-field linear representation isomorphism after semisimplification, and directly before semisimplification when the specialization is irreducible. For propagation, two existing compatible families with the same algebraic spine are identified member by member.

**Primary verdict: conditional on a named input.** The named inputs are the declared classicality/attached-representation and common-polynomial/density data, plus algebraic semisimplification and Brauer–Nesbitt. They are not proved by support or the formal gate composition.

The support step gives a nonzero actual tensor fiber by finite generation and Nakayama, or a nonzero derived field fiber by faithful field extension. The balancing relation forces each Hecke element to act by its specialized scalar, so a nonzero vector in an ordinary fiber, or in surviving derived cohomology, is an actual scalar eigensystem. This is a quotient fiber; it need not claim an eigenvector already lying in the original unspecialized carrier.

For derived realization, the final 9.6 statement uses a model interval contained in the classicality range. For final 12.4 the weaker pointwise requirement that realization applies to the selected surviving eigensystem is sufficient. The earlier blanket cohomological conclusion does not establish classicality in an unrelated degree.

The coefficient functions of the characteristic polynomial are continuous polynomial functions. Their equalizers are closed in a Hausdorff field. Equality on the dense union of the declared Frobenius conjugacy classes therefore gives equality on the entire profinite group. An algebraic semisimplification preserves characteristic polynomials. General Brauer–Nesbitt then gives the actual linear intertwiner over the coefficient field, without replacing that field by an algebraic closure in the conclusion.

The literature audit located Gee, *Modularity Lifting Theorems*, Fact 2.5, as the exact coefficient-field Brauer–Nesbitt contract. Arithmetic Chebotarev gives the required dense conjugacy union outside a finite ramification set and a density-zero exception set, by testing each conjugacy class in each finite quotient. Finiteness of `S` is now stated at the start of the final manuscript. Pointwise theorems also directly require a dense set, which is the minimal formal input actually used.

The final ordinary completion datum now explicitly supplies all pointwise realization inputs, especially the equality of the **universal specialization's** polynomials with the same specialized Hecke polynomials used by the attached representation. Classicality alone, or occurrence of some automorphic object in a nonzero fiber, would not imply this equality. This closes the implicit interface in the preserved revised 12.1/12.2 wording. The patched carrier's `R`-action must be the restriction of its Hecke `T`-action along the comparison isomorphism; the derived carrier requires the corresponding scalar transport/identification. An isomorphism of rings by itself does not compare unrelated module structures. These are the same carrier-compatibility hypotheses explicitly used in 7.1 and in the final five-gate support comparison.

The final five-gate statement has a genuine support inclusion in prime spectra and requires an actual Hecke point `y` with `y∘f=x`. Support-preserving scalar extension does not guarantee an extension of a point into the same coefficient field. The simple example `Q → Q(i)` with `x=id_Q` shows the missing implication: support is full on both sides but there is no compatible `Q(i) → Q` point. The final statement explicitly includes this point.

Existing-system propagation is correct once both families and their common spine exist. It does not construct a missing coefficient-place member, prove that a completed companion is semisimple, or show that an automorphic object has an attached family outside its supplied hypotheses. Matching normalizations are necessary: substituting arithmetic Frobenius for geometric Frobenius can invert eigenvalues, and an attached-system twist can change the characteristic polynomials.

## Worked-example and small-case checks

The auxiliary-freeness counterexample passes: the principal quotient of `k[[t,x]]` by `x(x-t)` is reduced because `x` and `x-t` are distinct prime factors, while its module quotient by `x` is `k[[t]]` and omits the other generic point. The node quotient `k[[x,y]]/(xy) → k[[y]]` has annihilator `(x)` and support `V(x)`, and omits the generic point `(y)`. Meeting of the two components is not mistaken for disjointness.

For the finite adequacy certificate, an exact modular calculation recomputed the printed matrices directly: the determinant of the four endomorphism columns is 4 modulo 7; the adjoint constituent basis determinant is 3; the four projector trace functionals have determinant 3; the printed witness traces are 3 and 6; and all four displayed projectors are idempotent. The sign conjugation equations also hold. These finite computations support the printed elementary identities. The general conclusion uses the determinant argument (which detects every nonzero endomorphism), Maschke/averaging at group order 6 invertible modulo 7, and the supplied adequacy convention, not an extrapolation from sampled residual groups. The audit's initial attempt to use SymPy was unavailable; the completed exact modular check uses pure Python and no numerical tolerances.

Nullary and zero-rank cases do not change the conclusions: an empty tensor family retains coefficient topology, a rank-zero free module has rank-zero coinvariants, a zero-dimensional carrier has no nonzero packet hypothesis, and a zero-length list of linearly independent functions is separated by the invertible empty matrix. The finite Frobenius separator only recovers multiplicities in a **known** semisimple carrier whose listed trace functions are independent; it does not classify arbitrary representations by an arbitrarily preselected finite set of primes.

## Remaining gaps, restrictions, and next checks

There is no remaining internal mathematical blocker in the reviewed final wording. The external arithmetic leaves remain conditional by design. An actual automorphy application must name and verify its particular representability, residual image, patching, classicality, attached-system, normalization, and local-global compatibility theorem. The current article's broad external “package” facts are contextual summaries rather than a single universally applicable lifting theorem.

The original eight statement amendments must retain their separate literal-wording verdicts; they cannot be retrospectively labeled complete by the revised statement. The final contextual clarifications must also be reported separately from the preserved compiler census. A compiler check certifies its quantified Lean contract, not a vague stronger reading of prose.

The cheapest meaningful future check is application-specific: instantiate the declared gates with one exact published arithmetic theorem and verify its hypotheses, normalizations, and realized locus. Broadening the present formal proof or inventing a new global reciprocity argument is outside this audit.

## Commands and reproducibility

The audit used `rg --files` and `rg -n` to resolve manuscript, source, import, and claim locators; sequential `sed` reads covered the entire raw revised manuscript and the relevant original statements. `sha256sum` pinned the raw source revisions. A direct environment census independently recovered the 49-claim partition. `verify_printed_adequacy.py` reproduces the exact finite arithmetic without third-party packages. `build_claim_matrix.py` records authoritative statement hashes and the independently assigned verdicts; it does not import status claims as proof.

No raw source, production Lean module, or traditional manuscript was edited by this auditor. Author-requested clarifications were communicated before final inspection. The final delta pass is recorded in `FINAL_DELTA_AUDIT.md`.
