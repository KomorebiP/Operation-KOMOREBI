# Paper XII: Lean theorem outline

**Komorebi P. · 8 September 2026 · v0.0.1**

The target manuscript is *Patching Support, Hecke Packets, and Conditional
Automorphic Completion*. This package outlines every internally proved claim.
It adds **zero checked Lean theorems**. No Lean compiler was run for this outline.
The exact source statements and their prose proofs are retained in
`SOURCE_PROOF_INVENTORY.md`; per-claim dependencies and proposed targets are also
machine-readable in `claim_roadmap.json`.

The source contains **49 internal claims, 8 external standard facts, 12 definitions,
10 remarks, and 3 worked examples**: 82 numbered records in total. There are 52
proof environments: 49 claim proofs and 3 example proofs. A prose proof environment
is not a Lean proof. The upstream audits are preserved as prior documents, not
endorsed as fresh independent audits.

## Recommended first implementation block

Build the ordinary support chain first. It feeds the final theorem and avoids
waiting for completed tensor products, group cohomology, or derived categories.

1. Define support by nontriviality of actual localized modules. Prove 6.2,
   (operatorname{Supp}_R M=V(operatorname{Ann}_R M)), for finite modules.
2. Prove 6.7: near faithfulness, full support, and annihilator containment in
   the nilradical are equivalent under Noetherian hypotheses. Include the reduced case.
3. Prove 6.8 by specializing to minimal primes, with the component interpretation recorded.
4. Prove 6.9 using localized quotient modules and Nakayama. Keep the two spectra typed.
5. Define the ordinary patching datum from its actual quotient identifications and
   prove 6.11, including near faithfulness and reduced-ring faithfulness.
6. Add 3.4, the independent local-idempotent lemma, as a short adjacent task.

Corollary 6.12 follows from this chain only after its reversed printed containment
is explicitly amended. That row remains flagged. A small finite-carrier block
(8.7–8.8) and the Paper X reuse wrappers (10.3, 10.9) are useful next tasks if the
support APIs take longer to connect than expected. No completion date or proof-count
gain is promised by this ordering.

For (qinoperatorname{Spec}(R/I)), use the typed quotient statement

[
qinoperatorname{Supp}_{R/I}(M/IM)quadLongleftrightarrowquad
operatorname{comap}(pi,q)inoperatorname{Supp}_R(M),
]

where (pi:R	o R/I). For the field-fiber block, with (x:R	o E), the target is
[
operatorname{Nontrivial}(Eotimes_{R,x}M)quadLongleftrightarrowquad
ker(x)inoperatorname{Supp}_R(M).
]
This uses finite generation of (M), but not Noetherianity of (R).

## Development order

| Stage | Proposed modules | Source claims | Completion requirement |
|---|---|---|---|
| A | ModuleSupport, NearFaithfulness, QuotientSupport, OrdinaryPatching, LocalIdempotents | 6.2, 6.7–6.9, 6.11; 3.4; amended 6.12 | Actual localizations, quotient action, Nakayama, full-support descent |
| B | FieldFibers, SupportTransport, FittingSupport | 6.3–6.5, 7.1–7.2, 7.4–7.5, 9.3 | Actual tensor fibers and intrinsic Fitting ideals, with all scalar maps |
| C | FiniteCarrier, StableCores, CompanionForests, FrobeniusSeparation | 8.7–8.12, 10.3–10.5, 10.9 | Nonzero vector branches and finite-set branches distinguished; companion effectivity separate |
| D | ArtinPackets | 8.2–8.4 | Actual idempotent ranges, localization, generalized eigenspaces, cast-aware trace |
| E | AuxiliaryGroupAlgebra, Coinvariants, DyadicAugmentation | 5.1–5.4, 11.1–11.2 | Actual group algebra and augmentation quotient; nonabelian dyadic scope retained |
| F | LocalQuotients, FiniteAdequacy, SupportCounterexamples | 3.1–3.3, 4.2, 7.3 and examples | Completed topology, actual adequacy certificate, power-series counterexamples |
| G | DerivedSupport | 6.16, 6.18–6.19 | Perfect models, actual derived base change, cohomological nonvanishing |
| H | GaloisRealization, CompatibleSystems, ConditionalCompletion | 9.4–9.6, 10.7, 12.2, 12.4–12.6 | Typed arithmetic inputs and genuine representation isomorphisms |

These stages are a dependency-aware sequence for implementation, not requests for
parallel agents. Fitting and completed/derived infrastructure may be subdivided once
the pinned Mathlib source has been inspected. No claimed Mathlib API availability is
inferred from a plausible theorem name.

## Confirmed reuse from our checked sources

| Existing source | Exact declaration | Intended Paper XII role | Remaining work |
|---|---|---|---|
| Paper X, Compactness | `PaperX.Compactness.finite_branch_compactness` | 10.3 | Identify the actual finite admissible levels and total reduction maps; match level 0 with manuscript level 1 |
| Paper X, Compactness | `PaperX.Compactness.empty_level_obstruction` | 10.4 | Define the reduction of a complete realization to a branch |
| Paper X, Compactness | `PaperX.Compactness.indexed_finite_completion` | 10.5, branch portion | Prove branch-to-adic-realization effectivity and local-condition preservation |
| Paper X, FiniteSeparation | `PaperX.FiniteSeparation.exists_nonsingular_samples` | 10.9 | Instantiate the actual independent Frobenius functions and retain row/column orientation |

Both modules are included byte for byte under `reuse/`, with provenance hashes.
Their source was inspected here and their prior release verification was available.
They were not recompiled for this outline, and they add no new proof count.
Paper X's ring reconstruction and finite-group averaging are additional design
references. They do not themselves establish companion effectivity or the full
adequacy theorem.

## Mathematical interfaces to settle before coding

- **Ordinary algebra:** commutative rings, finite versus finitely presented modules,
  ideals, prime spectra, actual localizations, residue fields, and scalar-extension
  module actions. Define `NearlyFaithful` by a power of the annihilator ideal being
  zero. Define `FullSupport` from localization support.
- **Quotient modules:** use the actual submodule (IM=Icdot	op), give (M/IM)
  its (R/I)-module structure, and prove localization and tensor identifications.
- **Fitting ideals:** use an intrinsic API when available. If a presentation-based
  implementation is needed, prove independence of presentation before labeling the
  resulting ideals intrinsic Fitting ideals.
- **Finite inverse systems:** for vector spaces use linear transition maps and
  `Nontrivial`; for finite companion sets use actual finite types and `Nonempty`.
  Stable cores are intersections of images of constructed composite maps.
- **Artin packets:** separate the external algebra decomposition from the internal
  direct-sum, localization, and generalized-eigenspace theorems.
- **Completed local algebra:** record the topology, residue-field identifications,
  closure of ideals, and the category in which the completed tensor is a pushout.
- **Derived algebra:** work with actual perfect complexes and quasi-isomorphisms.
  A logical interface assuming every desired tensor identity is only a preliminary
  interface and cannot finish the source theorem.
- **Arithmetic realization:** use actual ring maps, Hecke fibers, representations,
  Frobenius polynomials, and isomorphisms. External results are explicit theorem
  parameters with semantic contracts, not new global axioms. The realization input
  may produce an automorphic object with an attached representation and matching
  polynomials; the final comparison to the chosen deformation representation must
  still be obtained by the declared identification theorem.

## Source issues and formalization questions

1. **6.12, reversed containment.** The source says every component “contains the
   support.” From full support, the valid direction is that every component is
   contained in the support. On a reducible spectrum the literal printed direction
   is false. The original file is unchanged. The corrected target is recorded as a
   proposed amendment and must not be reported as literal coverage of that sentence.
2. **Register labels.** The old register assigned following labels to unlabelled
   remarks 6.6, 6.20, and 10.8. The new inventory reads labels only inside their own
   environments; these are not duplicate labels in the manuscript source.
3. **6.4, large r.** When r exceeds a chosen presentation target rank, prove the empty
   stratum using the proper Fitting convention. Do not use truncated subtraction in
   the minor formula without a case split.
4. **8.4, trace typing.** A scalar trace equals the natural dimension after casting
   into the coefficient field. Positive rank is an integer assertion. Nonzero trace
   detects nonzero packets only under the characteristic-zero hypothesis.
5. **8.7, stabilization.** Prove eventual constancy of the entire dimension sequence.
   One equal consecutive pair alone does not forbid a later dimension drop.
6. **10.5, effectivity.** A finite forest produces compatible finite objects. Recovering
   an actual continuous adic representation with all local conditions needs a separate
   construction. Strict compatibility or a common label must not be defined to conceal
   this obligation. No failure of the intended arithmetic instance is asserted here.
7. **9.6 and 12.4, degree applicability.** The nonzero cohomology degree is existential.
   A realization theorem confined to a chosen interval must be shown to cover the
   surviving witness, or an adequate witness-specific input must be supplied.
8. **11.2, group and module scope.** A finite two-group need not be abelian. Keep a
   noncommutative group-algebra module formulation with correct sidedness. Interpret
   the coefficient ring as the integer ring of the declared finite extension of Q2.
9. **9.2, external topology.** Freeze a precise coefficient-topology and identification
   theorem contract when this input is instantiated. This planning task has not
   verified the cited literature or proved the external facts.

## Verification and coverage rules

The next implementation uses the established candidate pin Lean 4.34.0-rc2 and
Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Before coding against
an API, inspect that pinned source locally and check its signature. Draft signatures
in `contracts/` are design text with the suffix `.lean.txt`; they are excluded from
compilation and theorem counts.

Count a source claim as complete only after every printed clause has an actual
formal counterpart, its declared assumptions match, all production modules compile,
and transitive axiom checks pass under the existing allowlist
`propext`, `Classical.choice`, `Quot.sound`. Track definitions, imported results,
supporting lemmas, test examples, and amended claims separately. Keep rejected proof
attempts outside production. A conditional arithmetic wrapper can be complete as a
conditional theorem while its explicitly supplied arithmetic inputs remain external.

Useful semantic controls for the first implementations are: a nonlocal product ring
with a nontrivial idempotent; a finite module missing a component; the failure of
Nakayama without finite generation; a nonzero vector-space tower with zero transition
maps; a finite-set tower with occupied dead ends; and an idempotent of nonzero rank
but zero trace in positive characteristic. These are proposed controls, not completed
tests. The three exact worked examples in the manuscript retain their own separate
formalization obligations.

## Per-claim outline

Every row below is **not yet formalized in Paper XII**. Names are proposed targets.
Dependencies refer to the regenerated manuscript numbers, not fresh Lean declarations.


### 3.1 · Completed tensor quotient

Source: `thm:tensor_quotient`, lines 249–262. Proposed module: `LocalQuotients`.

Proposed target: `PaperXII.LocalQuotients.completed_tensor_quotient`.

Dependencies: shared foundational APIs only.

Proof route: Define the complete local algebra category, its continuous local morphisms, finite completed tensor product, and the closed generated ideal. Construct maps in both directions from the universal properties and prove inverse laws by uniqueness.

Completion requires: An algebra equivalence with continuous inverse between the actual completed tensor of quotients and the quotient of the actual completed tensor, respecting each canonical factor map.

Scope question: Do not substitute an ordinary tensor product. Verify completeness and locality of the quotient, the closure convention, and the empty finite family. Universal-property data may be a first interface, but construction of the stated completed objects remains a separately tracked obligation.


### 3.2 · Simultaneous local conditions

Source: `cor:simultaneous_local`, lines 268–270. Proposed module: `LocalQuotients`.

Proposed target: `PaperXII.LocalQuotients.factors_iff_local_factors`.

Dependencies: 3.1.

Proof route: Translate factorization through a quotient into kernel containment. Show that the closed generated ideal is killed exactly when every factor ideal is killed.

Completion requires: Existence and uniqueness of continuous local quotient maps, with the same original point and factor inclusions.

Scope question: Kernel closedness needs the specified Hausdorff target topology. Prove the closure step rather than silently removing it.


### 3.3 · Global base change for local conditions

Source: `prop:global_local_basechange`, lines 276–284. Proposed module: `LocalQuotients`.

Proposed target: `PaperXII.LocalQuotients.global_base_change`.

Dependencies: 3.1, 3.2.

Proof route: Apply the completed pushout universal property to the supplied global map and use the simultaneous-local-condition criterion.

Completion requires: A natural factorization equivalence for the actual global base change, with all local restrictions identified.

External or supplied contracts: 2.2.

Scope question: Representability of deformation functors is external. This theorem starts with supplied represented rings and maps.


### 3.4 · Idempotents in a local ring

Source: `prop:local_idempotent`, lines 290–292. Proposed module: `LocalIdempotents`.

Proposed target: `PaperXII.LocalIdempotents.eq_zero_or_one`.

Dependencies: shared foundational APIs only.

Proof route: Use that either e or 1-e is a unit in a local ring. Cancel in e*(1-e)=0.

Completion requires: For every commutative local ring and e with e*e=e, prove e=0 or e=1.


### 4.2 · Finite adequacy certificate

Source: `thm:s3_adequacy`, lines 340–354. Proposed module: `FiniteAdequacy`.

Proposed target: `PaperXII.FiniteAdequacy.standard_S3_F7`.

Dependencies: shared foundational APIs only.

Proof route: Construct the S3 action over ZMod 7, identify it with the standard representation, prove absolute irreducibility, trace-zero adjoint invariants and an actual sign-plus-standard decomposition. Prove H1 vanishing by a finite-group averaging/cochain argument. Check the two explicit eigenprojectors and nonzero trace pairings.

Completion requires: All printed cohomology, decomposition, and detection clauses plus agreement with a precisely specified adequacy definition.

External or supplied contracts: 4.1.

Scope question: Matrix identities alone are partial coverage. Character values alone are not a Lean representation equivalence. The exact adequacy convention and the imported definition need a later primary-source check.


### 5.1 · Functorial group algebra transfer

Source: `prop:group_algebra_transfer`, lines 429–438. Proposed module: `AuxiliaryGroupAlgebra`.

Proposed target: `PaperXII.AuxiliaryGroupAlgebra.transfer`.

Dependencies: shared foundational APIs only.

Proof route: Extend a group homomorphism on basis elements of the group algebra. Prove multiplicativity, augmentation compatibility, and surjectivity by lifting finite basis support.

Completion requires: An actual algebra homomorphism with the stated identities and a proof of surjectivity when the group map is surjective.


### 5.2 · Residual augmentation algebra

Source: `thm:residual_augmentation_algebra`, lines 444–461. Proposed module: `AuxiliaryGroupAlgebra`.

Proposed target: `PaperXII.AuxiliaryGroupAlgebra.truncated_polynomial_equiv`.

Dependencies: 5.1.

Proof route: For a supplied product decomposition of the finite abelian p-group, send each polynomial variable to its generator minus one. Prove the p-power relations, construct the quotient map, and prove it bijective using explicit bounded monomial bases or inverse maps. Identify the augmentation ideal and unique maximal ideal.

Completion requires: The full multivariable algebra equivalence, generator identities, augmentation ideal equality, and locality.

Scope question: Retain characteristic p and primality. Include rank-zero products and any allowed trivial cyclic factor; finite p-group order alone does not choose its generators.


### 5.3 · No residual character splitting

Source: `cor:no_residual_character_splitting`, lines 471–473. Proposed module: `AuxiliaryGroupAlgebra`.

Proposed target: `PaperXII.AuxiliaryGroupAlgebra.no_residual_splitting`.

Dependencies: 5.2, 3.4.

Proof route: Apply the local idempotent theorem to the constructed residual group algebra.

Completion requires: Every residual idempotent is zero or one, in the actual group algebra.


### 5.4 · Coinvariant recovery

Source: `thm:coinvariant_recovery`, lines 479–491. Proposed module: `Coinvariants`.

Proposed target: `PaperXII.Coinvariants.free_recovery`.

Dependencies: 5.1.

Proof route: Identify the augmentation quotient with the coefficient ring, construct the module quotient/base-change equivalence, and base change a supplied finite basis.

Completion requires: Both displayed module isomorphisms and an O-basis of size d. The basis is data; no canonical basis is claimed.

Scope question: Choose left/right tensor conventions explicitly. Keep a version for arbitrary finite groups so 11.2 can include nonabelian two-groups; commutative group-algebra APIs alone are insufficient for that extension.


### 6.2 · Finite module support

Source: `thm:finite_module_support`, lines 536–545. Proposed module: `ModuleSupport`.

Proposed target: `PaperXII.ModuleSupport.support_eq_zeroLocus_annihilator`.

Dependencies: shared foundational APIs only.

Proof route: Use actual localized modules. One direction inverts an annihilator outside the prime. For the other, kill a finite generating family by elements outside the prime and take their product.

Completion requires: Equality of subsets of PrimeSpectrum R, for a finite module over any commutative ring. Include the zero module.

Scope question: Support must be defined by localization nonvanishing, independently of the desired annihilator equality.


### 6.3 · Fitting support criterion

Source: `thm:fitting_support`, lines 559–568. Proposed module: `FittingSupport`.

Proposed target: `PaperXII.FittingSupport.support_eq_zeroLocus_fitting_zero`.

Dependencies: 6.2.

Proof route: Choose a finite presentation, localize its matrix, and compare cokernel vanishing with a unit maximal minor over the local ring.

Completion requires: The actual zeroth Fitting ideal and its presentation independence, followed by equality of support loci.

Scope question: Use Fitt_0(0)=top. A custom minor ideal from a chosen matrix needs a proved bridge to the intrinsic Fitting ideal.


### 6.4 · Higher Fitting strata

Source: `thm:higher_fitting_strata`, lines 579–598. Proposed module: `FittingSupport`.

Proposed target: `PaperXII.FittingSupport.generator_strata`.

Dependencies: 6.3.

Proof route: Compute the residue-field fiber dimension from a presentation. Translate its rank bound to vanishing minors and to membership in the Fitting zero locus.

Completion requires: For every positive r, the fiber-dimension-at-least-r locus equals V(Fitt_(r-1)(M)).

Scope question: Treat r greater than the presentation target rank separately; natural-number subtraction must not create a false minor-size formula.


### 6.5 · Fitting ideals and base change

Source: `prop:fitting_base_change`, lines 608–617. Proposed module: `FittingSupport`.

Proposed target: `PaperXII.FittingSupport.base_change`.

Dependencies: shared foundational APIs only.

Proof route: Tensor a finite presentation, map every minor along the coefficient homomorphism, and identify the generated ideal.

Completion requires: Ideal.map of every intrinsic Fitting ideal equals the Fitting ideal after base change, for finitely presented modules.

Scope question: Do not add a Noetherian or flatness hypothesis to the printed statement. Construction of presentation-independent Fitting ideals is shared infrastructure.


### 6.7 · Near faithfulness is full support

Source: `thm:near_faithful_full_support`, lines 627–635. Proposed module: `NearFaithfulness`.

Proposed target: `PaperXII.NearFaithfulness.iff_full_support`.

Dependencies: 6.2.

Proof route: Use support=V(Ann), the intersection-of-primes description of the nilradical, and finite generation of the annihilator in a Noetherian ring to turn nil generators into a nilpotent ideal.

Completion requires: All three equivalences and the reduced-ring equivalence with FaithfulSMul.

Scope question: Nilpotent ideal means there is one common power equal to bottom, not only pointwise nilpotence without a finite-generation argument.


### 6.8 · Support on every irreducible component

Source: `cor:every_component_support`, lines 645–647. Proposed module: `NearFaithfulness`.

Proposed target: `PaperXII.NearFaithfulness.nonzero_at_minimal_prime`.

Dependencies: 6.7.

Proof route: Specialize full support to minimal primes and connect them with generic points of irreducible components.

Completion requires: Every minimal-prime localization is nontrivial; include the geometric correspondence for full prose coverage.


### 6.9 · Support after a quotient

Source: `thm:quotient_support`, lines 653–666. Proposed module: `QuotientSupport`.

Proposed target: `PaperXII.QuotientSupport.support_quotient_iff`.

Dependencies: 6.2.

Proof route: For a prime of R/I, pull it back to R. Construct the localization/quotient comparison and apply Nakayama to the localized finite module.

Completion requires: At each q in Spec(R/I), nonvanishing of the quotient localization iff nonvanishing at its pulled-back prime. Then derive the image equality in Spec R.

Scope question: The two supports live in different spectra. State a preimage equality or an image equality through the quotient spectral map, never a raw equality between different types.


### 6.11 · Ordinary patching support descent

Source: `thm:ordinary_support_descent`, lines 691–703. Proposed module: `OrdinaryPatching`.

Proposed target: `PaperXII.OrdinaryPatching.full_support_descends`.

Dependencies: 6.9, 6.7.

Proof route: Apply quotient support to R_infinity and its augmentation ideal. Transport the quotient module and quotient ring through the supplied identifications. Apply near faithfulness and reducedness only after the descent proof.

Completion requires: Full support, near faithfulness, and the reduced-ring faithfulness conclusion for the actual finite-level module.

Scope question: The datum contains the quotient identifications and full patched support. It must not contain full finite-level support as a field.


### 6.12 · Componentwise finite level occupancy

Source: `cor:componentwise_occupancy`, lines 714–717. Proposed module: `OrdinaryPatching`.

Proposed target: `PaperXII.OrdinaryPatching.componentwise_occupancy`.

Dependencies: 6.11.

Proof route: After resolving the printed containment, specialize full finite-level support to every component or to each generic point.

Completion requires: Every irreducible component is contained in support, or equivalently here every component is wholly occupied.

Scope question: SOURCE ISSUE: the printed statement says every component contains the support. That direction is reversed for a reducible spectrum. Keep this claim flagged pending an explicit manuscript amendment; do not call the corrected target a literal proof of the original sentence.


### 6.16 · Derived quotient support

Source: `thm:derived_quotient_support`, lines 786–799. Proposed module: `DerivedSupport`.

Proposed target: `PaperXII.DerivedSupport.quotient_support`.

Dependencies: shared foundational APIs only.

Proof route: Represent a perfect complex by a bounded complex of finite projectives. Construct derived scalar base change and the residue-field fiber associator; prove invariance under the choice of model.

Completion requires: The support pullback equality for the actual derived quotient. No Noetherian hypothesis is required by the printed theorem.

Scope question: Ordinary tensor of cohomology is not derived base change. An abstract associativity hypothesis can support an interface lemma only, until the actual derived associator is constructed.


### 6.18 · Derived patching support descent

Source: `thm:derived_support_descent`, lines 827–843. Proposed module: `DerivedSupport`.

Proposed target: `PaperXII.DerivedSupport.full_support_descends`.

Dependencies: 6.16.

Proof route: Transport the derived quotient equality through the supplied patching equivalences. Factor an arbitrary field point through the residue field and prove faithful scalar extension preserves a nonzero perfect fiber.

Completion requires: Full finite-level derived support and nonzero derived fiber at every field-valued point.


### 6.19 · A nonzero cohomological degree survives

Source: `cor:derived_degree_survives`, lines 850–859. Proposed module: `DerivedSupport`.

Proposed target: `PaperXII.DerivedSupport.exists_nonzero_fiber_cohomology`.

Dependencies: 6.18.

Proof route: Apply the acyclicity/zero-object criterion to the bounded field complex, preserving the actual specialized complex.

Completion requires: Existence of an integer cohomological degree with nontrivial cohomology.

External or supplied contracts: 6.15.

Scope question: No prescribed degree or classicality follows. The needed standard derived facts must be tracked separately.


### 7.1 · Support and Fitting transport

Source: `thm:rt_support_transport`, lines 873–897. Proposed module: `SupportTransport`.

Proposed target: `PaperXII.SupportTransport.ring_equiv_support_and_fitting`.

Dependencies: 6.2, 6.5.

Proof route: Restrict scalars along the ring equivalence, construct corresponding localization equivalences, and map finite presentations and their minors.

Completion requires: Both the spectral support-image equality and Ideal.map equality for every Fitting ideal.

Scope question: A proof of support transport alone leaves the Fitting clause partial.


### 7.2 · Full support is invariant under \texorpdfstring{\(R\cong\TT\)}{R equals T}

Source: `cor:rt_full_support`, lines 903–905. Proposed module: `SupportTransport`.

Proposed target: `PaperXII.SupportTransport.full_support_iff`.

Dependencies: 7.1.

Proof route: Use bijectivity of the spectral homeomorphism.

Completion requires: Full support over R iff full support over T for the same transported module.


### 7.3 · A quotient can erase a component

Source: `prop:quotient_erases_component`, lines 911–921. Proposed module: `SupportCounterexamples`.

Proposed target: `PaperXII.SupportCounterexamples.node_quotient_misses_component`.

Dependencies: 6.2.

Proof route: Construct the actual two-variable formal power-series quotient and its quotient by x. Identify its annihilator, its two minimal primes, and the missing localization.

Completion requires: The printed k[[x,y]]/(xy) example including its k[[y]] quotient and the excluded generic point.

Scope question: A polynomial-ring or finite matrix example may be a useful preliminary control but does not finish this formal power-series example.


### 7.4 · Field fiber criterion

Source: `thm:field_fiber_criterion`, lines 927–937. Proposed module: `FieldFibers`.

Proposed target: `PaperXII.FieldFibers.nontrivial_iff_support`.

Dependencies: 6.2.

Proof route: Factor the field point through localization and its residue field. Apply local Nakayama and faithful field extension.

Completion requires: Nontriviality of E tensor_R M iff ker(x) belongs to localization-defined support, for finite M over a commutative ring.

Scope question: Use Nontrivial of the module type, not Nonempty. No Noetherian assumption is needed here. Document the tensor symmetry used to match the printed factor order.


### 7.5 · Supported deformation points give nonzero Hecke fibers

Source: `cor:supported_hecke_fiber`, lines 949–956. Proposed module: `FieldFibers`.

Proposed target: `PaperXII.FieldFibers.supported_hecke_fiber`.

Dependencies: 7.1, 7.4.

Proof route: Define the Hecke point as x composed with the inverse ring equivalence; apply support transport and the field-fiber criterion.

Completion requires: An explicit nonzero vector in the Hecke scalar-extension module at that same point.


### 8.2 · Canonical Hecke packet decomposition

Source: `thm:canonical_hecke_packets`, lines 994–1009. Proposed module: `ArtinPackets`.

Proposed target: `PaperXII.ArtinPackets.decomposition_and_localization`.

Dependencies: shared foundational APIs only.

Proof route: From the supplied canonical Artin-local decomposition, define idempotent ranges, build synthesis and analysis maps, prove they are inverse, and identify each packet with actual localization.

Completion requires: Direct-sum equivalence, canonical localization equivalence, and occupancy/support equivalence.

External or supplied contracts: 8.1.

Scope question: Fact 8.1 is an explicit external algebraic input unless separately formalized. Do not assume semisimplicity or identify a packet with a one-dimensional eigenspace.


### 8.3 · Simultaneous generalized eigenspaces

Source: `cor:simultaneous_generalized_eigenspaces`, lines 1015–1035. Proposed module: `ArtinPackets`.

Proposed target: `PaperXII.ArtinPackets.simultaneous_generalized_eigenspace`.

Dependencies: 8.2.

Proof route: Use nilpotence of the local maximal ideal for a common exponent. On other factors at least one generator difference is a unit. Alternatively use the multiindex bound d*(N-1)+1.

Completion requires: Equality of the actual packet with the simultaneous generalized eigenspace for the supplied generating operators.

External or supplied contracts: 8.1.

Scope question: Retain algebraic closedness, finite generation of the algebra by those operators, and N>=1. Handle an empty generator list consistently.


### 8.4 · Rank and trace detection in characteristic zero

Source: `cor:rank_trace_detection`, lines 1043–1055. Proposed module: `ArtinPackets`.

Proposed target: `PaperXII.ArtinPackets.trace_eq_cast_finrank`.

Dependencies: 8.2.

Proof route: Split the vector space into the image and kernel of the idempotent and compute its matrix trace. Use characteristic zero to turn positive dimension into nonzero scalar trace.

Completion requires: Rank=image dimension over any field; trace=(dimension cast to E); nonzero trace iff nonzero packet in characteristic zero.

External or supplied contracts: 8.1.

Scope question: The displayed trace and integer dimension have different types. Insert the natural-number cast. Do not order an arbitrary characteristic-zero field to express positive trace.


### 8.7 · Nested packets in one finite carrier

Source: `thm:nested_finite_carrier`, lines 1101–1113. Proposed module: `FiniteCarrier`.

Proposed target: `PaperXII.FiniteCarrier.eventually_constant_nonzero_ranges`.

Dependencies: shared foundational APIs only.

Proof route: Deduce antitonicity of ranges from the absorption laws. Prove eventual constancy of their natural-number dimensions, then use inclusion and equal finite rank to identify all sufficiently late ranges.

Completion requires: There exists N such that every later range equals range(e_N), and the intersection is nonzero when all ranges are nonzero.

Scope question: One pair of equal consecutive dimensions does not by itself rule out a later drop. The proof must obtain eventual constancy of the whole sequence.


### 8.8 · Finite witness of incompatibility

Source: `cor:finite_witness_incompatibility`, lines 1123–1129. Proposed module: `FiniteCarrier`.

Proposed target: `PaperXII.FiniteCarrier.empty_intersection_finite_witness`.

Dependencies: 8.7.

Proof route: Take the contrapositive of the nonzero intersection theorem, with the same finite carrier and nesting assumptions.

Completion requires: If the intersection is bottom, some finite-level range is bottom.

Scope question: Read “under the hypotheses” as the structural finite-dimensional and nesting assumptions; retaining the all-nonzero premise makes this implication merely contradictory.


### 8.10 · Surjectivity on stable cores

Source: `lem:stable_core_surjectivity`, lines 1156–1163. Proposed module: `StableCores`.

Proposed target: `PaperXII.StableCores.transition_surjective`.

Dependencies: shared foundational APIs only.

Proof route: Construct composites of the actual adjacent linear maps. For y in Y_m, use the nonempty descending affine fibers inside V_(m+1), whose dimensions stabilize, to find a preimage in every eventual image.

Completion requires: A well-defined linear map Y_(m+1) -> Y_m and its surjectivity, without assuming ambient transition surjectivity.

Scope question: Finite dimensionality is required separately at each level; no uniform dimension bound is assumed.


### 8.11 · Nonzero stable core criterion

Source: `thm:nonzero_stable_core`, lines 1179–1192. Proposed module: `StableCores`.

Proposed target: `PaperXII.StableCores.branch_with_prescribed_first`.

Dependencies: 8.10.

Proof route: Recursively choose preimages within stable cores, beginning with the prescribed nonzero element. Prove compatibility and that every coordinate maps to that first element.

Completion requires: An actual compatible vector family with the requested first coordinate, and nontriviality of the inverse-limit module.

Scope question: Nonempty would be vacuous for a vector-space limit because the zero branch exists. Preserve a nonzero coordinate witness.


### 8.12 · Surjective systems

Source: `cor:surjective_inverse_system`, lines 1199–1201. Proposed module: `StableCores`.

Proposed target: `PaperXII.StableCores.surjective_system_nontrivial_limit`.

Dependencies: 8.11.

Proof route: Prove every composite transition surjective, hence every stable core equals the full level, and instantiate the preceding theorem.

Completion requires: Nontrivial inverse limit for nontrivial finite-dimensional levels and surjective adjacent maps.


### 9.3 · Support gives a Hecke eigensystem

Source: `thm:support_gives_hecke_system`, lines 1269–1282. Proposed module: `FieldFibers`.

Proposed target: `PaperXII.FieldFibers.support_gives_scalar_eigensystem`.

Dependencies: 7.5.

Proof route: Use nontriviality of the actual field fiber and the tensor balancing relation to show each Hecke element acts by its point value.

Completion requires: Nonzero fiber and the scalar-action identity on every tensor, not only on pure tensors.

Scope question: For phi:R equiv T and x:R->E, the Hecke scalar is (x composed with phi inverse)(t).


### 9.4 · Pointwise Galois realization

Source: `thm:pointwise_galois_realization`, lines 1292–1322. Proposed module: `GaloisRealization`.

Proposed target: `PaperXII.GaloisRealization.pointwise_semisimple_identification`.

Dependencies: 9.3.

Proof route: Retain the supplied classical automorphic object, its attached semisimple representation, and matching Frobenius polynomials. Apply a typed, explicitly external Chebotarev/Brauer–Nesbitt identification input. Handle the irreducible case separately.

Completion requires: An isomorphism between rho_x semisimplified and the attached representation, with the exact coefficient field and Frobenius set.

External or supplied contracts: 9.1, 9.2.

Scope question: This is conditional. Do not replace the external input by a custom global axiom or assume the final isomorphism itself. Specify coefficient topology and the precise dense-set identification contract before claiming arithmetic coverage.


### 9.5 · Full support gives pointwise automorphy on the realized locus

Source: `cor:full_support_pointwise_automorphy`, lines 1328–1334. Proposed module: `GaloisRealization`.

Proposed target: `PaperXII.GaloisRealization.full_support_realized_locus`.

Dependencies: 9.3, 9.4.

Proof route: For each point whose kernel lies in U, apply full support, the fiber theorem, and the realization contract supplied at that point.

Completion requires: Pointwise semisimplified automorphy only on the declared realization locus U.

External or supplied contracts: 9.1, 9.2.


### 9.6 · Derived pointwise realization

Source: `thm:derived_pointwise_realization`, lines 1340–1350. Proposed module: `GaloisRealization`.

Proposed target: `PaperXII.GaloisRealization.derived_pointwise`.

Dependencies: 6.19, 9.4.

Proof route: Extract a nonzero specialized cohomology degree and its scalar Hecke character, then apply the supplied realization input for that degree.

Completion requires: Nonzero fiber cohomology and conditional semisimplified realization.

External or supplied contracts: 6.15, 9.1, 9.2.

Scope question: Prove the surviving degree lies in the range to which classicality applies, or supply an explicit hypothesis for the witness degree. An existential degree does not automatically lie in a preselected interval.


### 10.3 · Companion branch criterion

Source: `thm:companion_branch_criterion`, lines 1392–1400. Proposed module: `CompanionForests`.

Proposed target: `PaperXII.CompanionForests.branch_exists`.

Dependencies: shared foundational APIs only.

Proof route: Instantiate PaperX.Compactness.Tower with actual admissible finite levels and total reduction maps. Reuse finite_branch_compactness after matching the first-residual-level indexing.

Completion requires: A compatible branch for the supplied finite nonempty forest, retaining its fixed residual root.

Scope question: The source theorem in Paper X is already checked; a wrapper is reuse, not new mathematics. Finite-dimensional vector spaces over infinite fields are not finite sets.


### 10.4 · Empty finite companion obstruction

Source: `cor:empty_companion_obstruction`, lines 1406–1408. Proposed module: `CompanionForests`.

Proposed target: `PaperXII.CompanionForests.empty_level_obstruction`.

Dependencies: 10.3.

Proof route: A branch would evaluate to an element of the empty level. To rule out an actual complete representation, compose its proved reduction-to-branch map.

Completion requires: No branch at an empty level, and no complete realization once its reduction map is part of the concrete realization model.


### 10.5 · Simultaneous companion completion

Source: `thm:simultaneous_companion_completion`, lines 1414–1416. Proposed module: `CompanionForests`.

Proposed target: `PaperXII.CompanionForests.simultaneous_realization`.

Dependencies: 10.3.

Proof route: Use indexed_finite_completion to choose one branch per coefficient place. Then apply the independently proved branch-to-realization construction, preserving every Frobenius polynomial and local label.

Completion requires: Actual complete local representations with a common fixed spine, or a clearly labeled preliminary theorem producing only branches.

Scope question: EFFECTIVITY OBLIGATION: finite sets and reduction maps alone give branches. Topology, continuity, polynomial limits, quotient representatives, and closure of local conditions must connect those branches to the intended adic representations. Paper X reconstruction may help, but does not settle every arithmetic local condition.


### 10.7 · One member propagation in a fixed system

Source: `thm:one_member_propagation`, lines 1427–1440. Proposed module: `CompatibleSystems`.

Proposed target: `PaperXII.CompatibleSystems.one_member_propagation`.

Dependencies: 9.4.

Proof route: At each coefficient place compare the two existing systems using their supplied common polynomial spine and the external identification theorem.

Completion requires: An isomorphism for every existing member, retaining existence of both systems and equality of their spines.

External or supplied contracts: 9.2, 10.6.

Scope question: The agreement of attached-system polynomials is a separate printed hypothesis, not inferred solely from one identified member.


### 10.9 · Finite Frobenius separator

Source: `prop:finite_frobenius_separator`, lines 1450–1457. Proposed module: `FrobeniusSeparation`.

Proposed target: `PaperXII.FrobeniusSeparation.exists_nonsingular_samples`.

Dependencies: shared foundational APIs only.

Proof route: Reuse PaperX.FiniteSeparation.exists_nonsingular_samples for the actual family of independent functions, and specialize Omega to the declared Frobenius sample set.

Completion requires: Existence of an invertible evaluation matrix with entry (j,i)=t_i(omega_j), followed by uniqueness of multiplicity recovery.

Scope question: Functional linear independence on the permitted Frobenius set is assumed. Pointwise distinctness does not suffice. The algebraic theorem is an existing Paper X result.


### 11.1 · Failure of integral sign projectors

Source: `prop:dyadic_sign_projectors`, lines 1484–1504. Proposed module: `DyadicAugmentation`.

Proposed target: `PaperXII.DyadicAugmentation.sign_projectors_boundary`.

Dependencies: 5.2, 5.3.

Proof route: Construct the Q2 group algebra projectors and compare coefficients with the image of the integral group algebra. Specialize the residual truncated-polynomial equivalence to C2 over F2.

Completion requires: Both rational primitive idempotents, their nonintegrality, the residual dual-number equivalence, locality, and no residual idempotents.

Scope question: Keep the integral embedding explicit. Nilpotence of g-1 alone does not prove the whole residual algebra equivalence.


### 11.2 · Dyadic coinvariant recovery

Source: `cor:dyadic_coinvariant_recovery`, lines 1514–1524. Proposed module: `DyadicAugmentation`.

Proposed target: `PaperXII.DyadicAugmentation.coinvariant_recovery`.

Dependencies: 5.4.

Proof route: Apply the arbitrary-group augmentation/base-change theorem to the valuation ring in the coefficient-two setting.

Completion requires: The quotient/tensor identification and preservation of finite free rank for every finite two-group.

Scope question: Specify O as the ring of integers of a finite extension of Q2. The printed finite two-group need not be abelian, so track noncommutative module sidedness.


### 12.2 · Ordinary conditional automorphic completion

Source: `thm:ordinary_conditional_completion`, lines 1567–1579. Proposed module: `ConditionalCompletion`.

Proposed target: `PaperXII.ConditionalCompletion.ordinary`.

Dependencies: 6.11, 7.1, 9.3, 9.4.

Proof route: Compose actual support descent, support transport, the nonzero scalar Hecke fiber, and the declared arithmetic realization contract.

Completion requires: The nonzero field fiber and semisimplified representation isomorphism; add the irreducible refinement.

External or supplied contracts: 2.2, 2.3, 9.1, 9.2.

Scope question: Full patched support and arithmetic realization are legitimate explicit inputs. Full finite-level support and the final automorphy conclusion are outputs, not fields of the datum.


### 12.4 · Derived conditional automorphic completion

Source: `thm:derived_conditional_completion`, lines 1599–1608. Proposed module: `ConditionalCompletion`.

Proposed target: `PaperXII.ConditionalCompletion.derived`.

Dependencies: 6.18, 6.19, 9.6.

Proof route: Descend derived support, extract a nonzero cohomology witness, and apply the declared realization theorem for that witness.

Completion requires: A nonzero actual derived fiber, some nonzero Hecke cohomology eigensystem, and conditional semisimplified realization.

External or supplied contracts: 2.2, 2.3, 6.15, 9.1, 9.2.

Scope question: Retain the surviving-degree applicability issue from 9.6.


### 12.5 · Compatible system completion from one automorphic member

Source: `thm:system_completion`, lines 1614–1629. Proposed module: `ConditionalCompletion`.

Proposed target: `PaperXII.ConditionalCompletion.system`.

Dependencies: 12.2, 12.4, 10.7.

Proof route: Use the appropriate pointwise completion result at lambda0, then apply one-member propagation to the already supplied systems.

Completion requires: Memberwise isomorphisms at all declared coefficient places, assuming matching attached-system spine.

External or supplied contracts: 9.2, 10.6.

Scope question: Do not infer companion existence from a single occupied member.


### 12.6 · Five gate formulation

Source: `thm:five_gate_completion`, lines 1635–1645. Proposed module: `ConditionalCompletion`.

Proposed target: `PaperXII.ConditionalCompletion.five_gates`.

Dependencies: 12.2, 12.4, 10.7.

Proof route: Assemble a typed ordinary/derived alternative from supplied residual, patching, comparison, and realization data. Derive the fiber gate through the relevant support theorem.

Completion requires: An explicit conditional realization theorem whose dependency report exposes every arithmetic input.

External or supplied contracts: 2.2, 2.3, 9.1, 9.2, 10.6.

Scope question: If a comparison weaker than a ring isomorphism is used, define and prove its exact support/fiber preservation property. Arbitrary propositions named Gate1,...,Gate5 do not provide manuscript coverage.


## External standard facts

These eight entries remain separate from the 49 internal claims.


- **2.2:** Representability and deformation/cohomology foundations. Rings and universal representations must be supplied; a general theorem is not encoded by a field named Representable without semantics.


- **2.3:** The applicable automorphy lifting package. Exact arithmetic hypotheses are instance-specific and must remain explicit.


- **4.1:** Adequacy convention. Freeze the published definition before proving that the finite S3 calculation meets it.


- **5.5:** The Iwasawa/group-algebra limit identification. Optional for the first support block; not needed merely to prove finite coinvariants.


- **6.15:** Perfect-complex support through cohomology and acyclicity. Track actual complex and derived-category semantics.


- **8.1:** Canonical Artin-local decomposition, maximal-ideal indexing, and its localization comparison.


- **9.2:** Chebotarev and Brauer–Nesbitt identification with specified coefficient topology, Frobenius set, continuity, and semisimplicity.


- **10.6:** Strict compatibility and determination inside an already existing system. This does not construct companions.


## Current checklist

- [x] Source-backed outline for all 49 internal claims.
- [x] All 8 external inputs and all 3 worked examples distinguished.
- [x] Exact source statements, proofs, numbers, and labels inventoried.
- [x] First support block and two existing reuse modules identified.
- [x] Source wording and typing questions recorded.
- [ ] Pinned Mathlib API inspection and signature elaboration.
- [ ] First new Paper XII Lean theorem compiled and axiom-audited.
- [ ] Full 49-claim scoped formalization.
