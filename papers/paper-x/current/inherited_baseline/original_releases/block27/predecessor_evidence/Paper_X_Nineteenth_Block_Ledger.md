# Paper X Nineteenth-Block Claim Ledger

Original inventory: 38 numbered items, including 20 theorem/proposition/corollary claims.
Checked at stated scope: 15; partial: 5; pending: 0. These are not difficulty-weighted percentages.

| No. | Kind | Title | Status |
|---|---|---|---|
| 1.1 | definition | Residual seed system | `DEFINITION` |
| 2.1 | theorem | Residual partition | `LEAN_CHECKED_STRUCTURAL` |
| 2.2 | theorem | No crossing under positive-depth perturbation | `LEAN_CHECKED_STRUCTURAL` |
| 2.3 | corollary | Zeroth-order obstruction | `LEAN_CHECKED_STRUCTURAL` |
| 2.4 | numericalcertificate | Exact residual partition | `EXACT_FINITE_AUDIT` |
| 3.1 | classicalinput | Represented complete deformation problems | `CLASSICAL_INPUT_NOT_FORMALIZED` |
| 3.2 | theorem | Formal inverse-limit reconstruction | `LEAN_CHECKED_REPRESENTED_MAPS` |
| 3.3 | theorem | Finite-branch compactness | `LEAN_CHECKED_STRUCTURAL` |
| 3.4 | proposition | Smooth formal branch count | `LEAN_CHECKED_SMOOTH_FORMAL_MAPS` |
| 4.1 | classicalinput | Tangent and obstruction spaces | `CLASSICAL_INPUT_NOT_FORMALIZED` |
| 4.2 | theorem | Cohomology packet decomposition | `LEAN_CHECKED_COHOMOLOGY` |
| 4.3 | remark | Odd and dyadic nonlinear equations | `REMARK_NOT_FORMALIZED` |
| 4.4 | numericalcertificate | Finite packet complex | `NEW_EXACT_REALIZATION` |
| 5.1 | definition | Visibility weight | `DEFINITION` |
| 5.2 | example | The two sign branches | `LEAN_CHECKED_EXAMPLE` |
| 5.3 | proposition | Weighted smooth-chart count | `LEAN_CHECKED_COORDINATE_MODEL` |
| 6.1 | definition | Seed zeta function | `DEFINITION` |
| 6.2 | theorem | Smooth seed zeta function | `LEAN_CHECKED_SMOOTH_FORMAL_MAPS` |
| 6.3 | theorem | Weighted seed zeta function | `LEAN_CHECKED_COORDINATE_MODEL` |
| 6.4 | theorem | Singular power seed | `LEAN_CHECKED_DVR` |
| 6.5 | definition | Branching dimension | `DEFINITION` |
| 6.6 | corollary | Fractional singular dimension | `LEAN_CHECKED_DVR` |
| 7.1 | definition | Admissible residual transport | `DEFINITION` |
| 7.2 | definition | Directed seed rank | `DEFINITION` |
| 7.3 | theorem | Directed minimum-seed theorem | `LEAN_CHECKED_FINITE_DIRECTED_GRAPH` |
| 7.4 | numericalcertificate | Directed seed count | `NEW_EXACT_REALIZATION` |
| 8.1 | definition | Common arithmetic spine | `DEFINITION` |
| 8.2 | theorem | Adelic finite-depth completion | `PARTIAL_LEAN` |
| 8.3 | corollary | Residual companion obstruction | `LEAN_CHECKED_STRUCTURAL` |
| 8.4 | example | A scalar companion failure | `PARTIAL_FINITE_EXAMPLE` |
| 9.1 | theorem | Finite Frobenius separation | `PARTIAL_LEAN` |
| 9.2 | theorem | Compatible-carrier summand completion | `PARTIAL_LEAN` |
| 9.3 | numericalcertificate | Multiplicity recovery | `NEW_EXACT_REALIZATION` |
| 10.1 | theorem | Exact finite occupancy trace | `LEAN_CHECKED_SPECTRAL_OCCUPANCY` |
| 10.2 | conjecture | Universal occupancy | `CONJECTURAL` |
| 11.1 | theorem | Residual-system completion criterion | `PARTIAL_LEAN` |
| 11.2 | corollary | Exact location of the remaining existence problem | `PARTIAL_LEAN` |
| 11.3 | conjecture | Natural finite seed rank | `CONJECTURAL` |

## Scope by source statement

### 1.1 — Residual seed system
A definition, not a proof claim.

### 2.1 — Residual partition
Disjoint-fiber decomposition for any total reduction map, including empty fibers.

Targets: `PaperX.Residual.unpack_pack`, `PaperX.Residual.pack_unpack`, `PaperX.Residual.fibers_disjoint`.

### 2.2 — No crossing under positive-depth perturbation
Finite reachability and convergent streams preserve reduction. Infinite-limit clause corrected to require explicit finite-precision convergence.

Targets: `PaperX.Residual.no_crossing_finite`, `PaperX.Residual.stream_invariant`, `PaperX.Residual.no_crossing_limit`, `PaperX.Residual.positive_depth_mod`.

### 2.3 — Zeroth-order obstruction
Different roots prevent reachability by reduction-preserving operations.

Targets: `PaperX.Residual.zeroth_order_obstruction`.

### 2.4 — Exact residual partition
New exhaustive modular tests and the general modular perturbation identity. Original Python package not rerun.

Targets: `PaperX.Residual.positive_depth_mod`.

### 3.1 — Represented complete deformation problems
Representability and Galois deformation-theoretic inputs are not proved; the coefficient-completion map theorem is now checked separately in 3.2.

### 3.2 — Formal inverse-limit reconstruction
Actual ring and coefficient-preserving algebra homomorphisms between ideal-power quotients and an adically complete target. Reconstruction, both inverses, uniqueness, locality and maximal-ideal-adic continuity are proved. Representability of the deformation functor remains an explicit classical input; no new Galois representability theorem is claimed.

Targets: `PaperX.Reconstruction.ringReconstructionEquiv`, `PaperX.Reconstruction.localReconstructionEquiv`, `PaperX.Reconstruction.represented_local_algebra_reconstruction`, `PaperX.Reconstruction.reconstruct_precompose`.

### 3.3 — Finite-branch compactness
Actual infinite compatible branch of a tower of finite nonempty sets with total transition maps. No surjectivity hypothesis.

Targets: `PaperX.Compactness.finite_branch_compactness`, `PaperX.Compactness.branch_iff_levels_nonempty`.

### 3.4 — Smooth formal branch count
All local coefficient-algebra maps on the finite-variable formal power-series model are classified by actual maximal-ideal tuples. Integral maps are classified under explicit adic completeness. The count and chosen-uniformizer/chosen-residue-section digit equivalence, including the finite-precision expansion identity, are proved. Results transport along a supplied algebra isomorphism of the representing ring. Representability and the existence of that smooth model are not asserted.

Targets: `PaperX.FormalCharts.nilpotent_hom_ext`, `PaperX.SmoothMaps.pointEquiv`, `PaperX.IntegralCharts.integralPointEquiv`, `PaperX.Digits.integralPointDigitEquiv`, `PaperX.Digits.parameter_digit_expansion`, `PaperX.SmoothModels.modelPointEquiv`, `PaperX.SmoothModels.modelDigitEquiv`, `PaperX.SmoothModels.smooth_model_count`.

### 4.1 — Tangent and obstruction spaces
Representability and Galois deformation-theoretic inputs are not proved; the coefficient-completion map theorem is now checked separately in 3.2.

### 4.2 — Cohomology packet decomposition
Actual kernel/image-quotient cohomology is split by supplied finite commuting chain projectors. Packet complexes use actual projector ranges and their own boundaries. Both inverse maps, naturality under intertwining cochain maps, boundary detection, vanishing equivalence and dimension corollary are proved. The main theorem uses genuine Mathlib graded complexes and homology on both sides. Works over commutative rings. Does not construct Galois controlling complexes or projectors and does not prove obstruction vanishing.

Targets: `PaperX.PacketCohomology.cohomologyPacketEquiv`, `PaperX.ComplexCohomology.chainCohomologyPacketEquiv`, `PaperX.PacketNaturality.decomposition_natural`, `PaperX.PacketCohomology.boundary_iff_packet_boundaries`, `PaperX.PacketCohomology.vanishing_iff`, `PaperX.ComplexCohomology.dimension_sum`.

### 4.3 — Odd and dyadic nonlinear equations
No new formal result claimed for this remark.

### 4.4 — Finite packet complex
New explicitly specified complex reproduces packet dimension pattern (0,0,0)+(1,2,1). Its actual H1 isomorphism and dimension two over F5 are Lean-checked. All three degrees are independently tested under 24 field/basis realizations. Original companion implementation was not retrieved or rerun.

Targets: `PaperX.CohomologyExamples.exampleResolution`, `PaperX.CohomologyExamples.exampleCohomologyEquiv`, `PaperX.CohomologyExamples.example_h1_dimension`.

### 5.1 — Visibility weight
A definition, not a proof claim.

### 5.2 — The two sign branches
The exact two congruences are checked.

Targets: `PaperX.BoundaryExamples.signs_same_mod2`, `PaperX.BoundaryExamples.signs_different_mod4`.

### 5.3 — Weighted smooth-chart count
Weighted chart consists of actual images of P^w in O/P^m, not types defined to have the desired size. Works for any nonzero prime of a Dedekind domain with finite residue field, hence the stated DVR model. Invisible coordinates and dimension zero are included. No claim that every deformation ring has this chart.

Targets: `PaperX.Counting.coordinate_count`, `PaperX.Counting.weighted_chart_count`.

### 6.1 — Seed zeta function
A definition, not a proof claim.

### 6.2 — Smooth seed zeta function
Exact infinite series identity T/(1-q^d T) is proved for the actual cardinalities of all local coefficient-algebra maps at every positive quotient precision. Transport along a supplied formal-model algebra isomorphism is formalized. This is no longer only a tuple-chart computation.

Targets: `PaperX.SmoothMaps.smooth_point_zeta`, `PaperX.SmoothModels.smooth_model_zeta`.

### 6.3 — Weighted seed zeta function
Actual weighted-chart cardinalities define the infinite series in Q[[T]]. The finite polynomial prefix and denominator with constant term one are proved coefficientwise. Any bound M on the weights is allowed, including the empty chart; for positive d take M=max weights to recover the source formula.

Targets: `PaperX.Zeta.actual_weighted_zeta`, `PaperX.Zeta.weighted_first_tail`.

### 6.4 — Singular power seed
For every finite-residue DVR and e>=1, actual roots of x^e=0 in O/m^n are identified with the correct ideal image, counted, and their entire formal generating series is rational with the stated numerator and denominator. The valuation proof treats x=0 explicitly.

Targets: `PaperX.Singular.root_iff_coordinate`, `PaperX.Singular.singular_root_count`, `PaperX.SingularZeta.actual_singular_zeta`, `PaperX.SingularZeta.numerator_coefficients`.

### 6.5 — Branching dimension
A definition, not a proof claim.

### 6.6 — Fractional singular dimension
Actual real logarithmic limit of the root-cardinality function is proved with Filter.Tendsto. This is finite-level count growth, not the dimension or cardinality of the inverse limit. PaperX.Singular.compatible_root_family_zero separately proves every compatible nilpotent root tower is zero.

Targets: `PaperX.BranchingDimension.actual_singular_dimension`.

### 7.1 — Admissible residual transport
A definition, not a proof claim.

### 7.2 — Directed seed rank
A definition, not a proof claim.

### 7.3 — Directed minimum-seed theorem
Actual reflexive-transitive closure of a supplied directed edge relation, actual quotient by mutual reachability, and seed rank defined independently by least covering cardinality. Both optimality bounds, arbitrary representatives, empty graph and loops are covered. Uses the existing finite-preorder minimal-element theorem. Does not construct admissible arithmetic edges or initial occupancy. Infinite unique-source counterexample is also checked.

Targets: `PaperX.DirectedSeeds.directed_minimum_seed`, `PaperX.DirectedSeeds.minimum_seed_set`, `PaperX.DirectedSeeds.covers_iff_meets_sources`, `PaperX.SeedConsequences.arbitrary_representatives`, `PaperX.DirectedSeeds.source_iff_no_external_edge`.

### 7.4 — Directed seed count
A new explicit seven-root directed graph has the manuscript component/source pattern. Complete finite-path closure and equivalence to the actual SCC quotient are certified; rank three and all four minimum sets are Lean-checked. Independent graph census checks 66067 graphs. Original companion implementation was not retrieved or rerun.

Targets: `PaperX.SeedExamples.closure_closed`, `PaperX.SeedExamples.component_count`, `PaperX.SeedExamples.source_count`, `PaperX.SeedExamples.rank_three`, `PaperX.SeedExamples.minimumSeedSets_exact`, `PaperX.SeedExamples.minimumSeedSets_iff`.

### 8.1 — Common arithmetic spine
A definition, not a proof claim.

### 8.2 — Adelic finite-depth completion
**Still PARTIAL_LEAN at full arithmetic scope.** The coherent-framing and conditional common-polynomial core from Block 14 is extended by simultaneous reconstruction of actual local comparison matrices. Finite augmented nodes contain the actual representation and finitely many intertwiners, with determinant nonzero at fixed detecting depths. Compactness selects all data together. Their limits satisfy the actual equations, and injective coefficient change makes each comparison a genuine matrix unit. The finite criterion has a checked converse. Neither compatible witness choices nor matrix inverses are assumed.

The unframed positive-depth theorem derives finite framed levels, depth-zero occupancy, and continuity from one continuous representative in every allowed class. The common-spine version gives whole common polynomials and the prescribed local representation isomorphisms without a generic Local/stable premise for that specific certificate property. It retains fixed detectors, templates and occupancy of augmented levels as substantive assumptions. Cross-coefficient compatibility of the templates is not inferred.

There is now an actual G_Q/G_Qp specialization using the field-induced continuous maps between absolute Galois groups. A nontrivial continuous quadratic character of G_Q supplies a Z_2 example with determinant-two comparison detected modulo four: the representations are isomorphic over Q_2 but not integrally conjugate. The actual Z_3 example invokes simultaneous completion and reconstructs a nonunit comparison which is a field unit.

The fixed-depth condition is essential. Lean proves det P=pi^n*(P_11)^2 for every integral comparison in the unipotent degenerating family, ruling out every uniform detector although each field-valued approximant has the same rational isomorphism type.

The source already assumes inverse-limit closure. The new certificate theorem is a concrete sufficient condition for a particular actual comparison problem, not a proof that every intended arithmetic packet satisfies it. Full arithmetic status remains partial: actual common weight/Hodge–Tate/Weil–Deligne invariants, their finite-level interpretations and coefficient comparisons are not yet identified with the required formal inputs. Exact prescribed local Galois action is stronger than a packet label. No universal occupancy or unconditional local closure is claimed.

New targets: `PaperX.ComparisonCertificates.comparison_realization_iff`, `exists_continuous_comparison_realization`; `PaperX.CertificateIsomorphisms.exists_conjugating_unit`; `PaperX.LocalComparisonCompletion.certified_common_spine_completion`; `PaperX.GaloisComparisonCompletion.rational_galois_comparison_completion`; `PaperX.CertificateBoundary.no_uniform_detecting_depth`; `PaperX.CertificateExamples.completed_comparison_is_nonunit`; `PaperX.ArithmeticCertificateExample.quadraticCharacter_continuous`, `field_conjugacy`, `not_integrally_conjugate`. All predecessor targets remain valid.

Block16 adds complete restricted rigidity theorems. `FiniteGroupAveraging.conjugacy_iff_residue` lifts any residual isomorphism for a fixed finite group of unit order. `AveragingCompletion.finite_group_completion_iff` and `continuous_fixed_quotient_completion` derive depth-one comparisons from ordinary finite-level occupancy and residual type. `MatrixSpanBound.uniform_detector_for_conjugates` derives one detector uniformly across the fixed full-span field-isomorphism class. `SplitTemplateRigidity.uniform_detector_of_split_irreducible` derives the span from actual irreducibility and a scalar commutant. `MatrixSpanCompletion.full_span_completion` uses integral finite-condition approximants to preserve the actual field-isomorphism type after completion. No full arithmetic status promotion is made.

Block 17 removes the unit-order restriction in the finite-group sector when the group order is nonzero. `PrecisionAveraging.exists_isomorphism_lift` lifts an actual comparison at depth e+k while retaining depth k, for |Γ| dividing π^e. `OrderPrecision.uniform_detection_precision` derives e=v_π(|Γ|), uniformly before all ranks and representation pairs. Reduction at e+1 is injective on integral classes, giving `finite_integral_classes` when coefficient quotients are finite. `PrecisionCompletion.finite_group_completion_iff` and `continuous_fixed_quotient_completion` reconstruct the required integral type from every-level occupancy and the single-depth type condition. The actual Z_2 example calls these constructions and proves the precision loss necessary. No full arithmetic status promotion is made.

### 8.3 — Residual companion obstruction
Structural companion obstruction, strengthened to any empty level in any required coefficient-indexed tower. No arithmetic companion is constructed.

Targets: `PaperX.Compactness.empty_level_obstruction`, `PaperX.Compactness.indexed_empty_level_obstruction`.

### 8.4 — A scalar companion failure
Displayed root failures and selected positive finite levels are checked; infinite 5-adic/13-adic simple branches are not proved in this checkpoint.

Targets: `PaperX.BoundaryExamples.roots_mod2`, `PaperX.BoundaryExamples.roots_mod4`, `PaperX.BoundaryExamples.roots_mod3`, `PaperX.BoundaryExamples.roots_mod7`, `PaperX.BoundaryExamples.roots_mod5`, `PaperX.BoundaryExamples.roots_mod25`.

### 9.1 — Finite Frobenius separation
General characteristic-zero irreducible character independence is now proved for actual representations of arbitrary monoids, including infinite groups and varying constituent dimensions; no algebraic-closedness hypothesis or assumed independence is used. Joint continuity of coordinate actions implies character continuity. Coverage of every open normal quotient implies conjugacy-saturated sample density in the compact totally disconnected setting, hence exactly r distinct nonsingular trace evaluations. The common-field matrix argument remains checked. The arithmetic Frobenius coverage input and the bridge from nonisomorphic systems to nonisomorphic members at a fixed coefficient prime remain unformalized. Permitted-place exclusions remain explicit. Full arithmetic status remains partial.

New targets: `PaperX.SimpleModuleSeparation.exists_selecting_element`, `PaperX.GeneralCharacters.independent_irreducible_characters`, `PaperX.GeneralCharacters.continuous_character_of_action`, `PaperX.ProfiniteSeparation.dense_of_quotient_coverage`, `PaperX.ProfiniteSeparation.irreducible_separator_of_quotient_coverage`.

### 9.2 — Compatible-carrier summand completion
**Still PARTIAL_LEAN at full arithmetic scope.** The previous actual finite-copy, recovery, inertia and monodromy results are extended by a finite-exponential reconstruction from a supplied twisted scalar cocycle. Its actual representation law, inverse group actions, finite-copy equality, equivariant splits and joint continuity under explicit hypotheses are checked. Twisting by the negative cocycle recovers the original datum with N still supplied. The independently defined monodromy/inertia fixed kernel and its restricted actions and Euler polynomial are preserved.

An actual logarithmic inverse is now checked on N^3=0: the quadratic logarithm recovers N from one nonzero sample and gives both inverse identities on the cubic nilpotent/unipotent loci. If both original actions are identity at a supplied common nonzero-parameter sample, any reconstructed-action intertwiner recovers both original group equivariance and monodromy equivariance. General nilpotence reconstruction and cubic extracted recovery are different scopes. A length-four counterexample refutes using this quadratic logarithm without its cubic hypothesis; a zero sample loses N.

The source supplies the compatible carrier, its decomposition and constituent systems. Remaining work is the actual arithmetic identification/attachment: G, norm and tame cocycle; existence and comparison of all intended attached Weil–Deligne data, including coefficient comparisons and Hodge–Tate/period data. The present explicit class is not shown to contain every intended arithmetic representation. The general logarithmic inverse is still unformalized. No finite/open inertia preservation is asserted for the reconstructed rho; that earlier preservation result concerns finite sums of the supplied local r-data. Arithmetic Frobenius separation in 9.1 remains partial.

New targets: `PaperX.NilpotentExponential.expN_polynomial`, `expN_intertwines`; `PaperX.MonodromyReconstruction.reconstruct`, `twist_cancel`, `twist_fixedKernel`; `PaperX.ReconstructionSummands.reconstruct_copies`, `twist_copies`, `reconstructed_inclusion`, `reconstructed_retraction`, `reconstructed_projector`; `PaperX.ReconstructionTopology.continuous_reconstruct`; `PaperX.ReconstructionLocal.twist_euler`; `PaperX.UnipotentLogarithm.cubeEquiv`, `recoverN_expN`, `expN_intertwines_iff`, `kernel_expN_sub_one`; `PaperX.ReconstructionRecovery.reconstruct_intertwiner_iff`, `datum_eq_of_reconstruct_eq`; `PaperX.ReconstructionBoundary.actual_monodromy_recovery`, `quadratic_log_fails_beyond_cube`, `zero_parameter_recovery_fails`.


Block 19 adds complete simultaneous finite-group family lifting at e+k→k, with loss independent of the number of labels. Actual images give the full equivariant decomposition. Under local coefficients and positive retained depth, congruent complete labeled families are conjugate by the explicit equivariant unit sum_i F_i E_i, congruent to identity at the same depth. The existence theorem permits empty label sets and requires no local coefficient hypothesis; rigidity does not require a finite group or completeness. The fixed carrier and sufficiently deep family remain inputs. Arithmetic attachment and interpretation remain unproved.

New targets: `PaperX.OrthogonalLifting.exists_family_lift`; `PaperX.OrthogonalProjectors.Family.decomposition`, `decomposition_equivariant`; `PaperX.FamilyRigidity.exists_conjugating_unit_of_reduction`, `imageEquiv_equivariant`; `PaperX.FamilyClassification.exists_family_unique_up_to_conjugacy`; `PaperX.FamilyExamples.actual_three_summand_lift`, `no_exact_family_retains_mod_four`; `PaperX.FamilyBoundary.independent_lifts_not_orthogonal`, `generic_rigidity_on_distinct_families`.

### 9.3 — Multiplicity recovery
A new actual one-dimensional representation family of the Klein four-group gives matrix [[1,1,1],[1,-1,1],[1,1,-1]], determinant four, and observed trace (3,3,1) recovering multiplicities (2,0,1). Fractional and over-capacity targets are rejected. This does not claim the original companion matrix was retrieved, and no Galois carrier is asserted.

Targets: `PaperX.TraceExamples.actual_trace_matrix`, `PaperX.TraceExamples.determinant_four`, `PaperX.TraceExamples.exact_recovery`, `PaperX.TraceExamples.only_natural_solution`, `PaperX.TraceExamples.fractional_not_natural`, `PaperX.TraceExamples.no_admissible_excessive_trace`.

### 10.1 — Exact finite occupancy trace
Actual finite eigenvalue sets, Lagrange polynomials and evaluation at actual operators. For commuting split operators the product is idempotent with actual joint-eigenspace image, and trace equals the cast of its dimension. Characteristic zero gives unique natural trace/rank and occupancy iff nonzero trace. Order independence, intertwiners and basis changes are proved. The rank sequence 3,2,1,0, individually occupied but jointly empty packets, and exact Jordan/noncommuting failures are checked. No positive occupancy, arithmetic carrier, or numerical stability guarantee is inferred.

Targets: `PaperX.SpectralProjectors.spectral_isProj`, `PaperX.JointOccupancy.finite_occupancy`, `PaperX.JointOccupancy.joint_range`, `PaperX.JointOccupancy.trace_eq_dimension`, `PaperX.JointOccupancy.occupied_iff_trace_ne_zero`, `PaperX.JointOccupancy.trace_integer_unique`, `PaperX.JointOccupancy.joint_perm`, `PaperX.OccupancyTransport.joint_conjugate`.

### 10.2 — Universal occupancy
No axiom or placeholder is introduced for this statement.

### 11.1 — Residual-system completion criterion
The conditional existence core now includes positive depths and continuity after mapping into coefficient fields, with exact common polynomials and the supplied local closure implication. The source already assumes this closure. Block 14 constructs the actual representatives from unframed finite levels. Block 15 additionally constructs actual local isomorphisms from fixed-depth comparison certificates, with an actual G_Q/G_Qp specialization. Its remaining arithmetic interpretation inherits 8.2's obligations; the stated horizontal-transport identification must be expressed in that interpretation. The additional finite-trace recovery clause inherits the still-partial arithmetic inputs of 9.1 and 9.2. No missing hypothesis has been promoted to a theorem.

Targets: `PaperX.CompletionAssembly.conditional_common_spine_completion` and the unchanged system-completion, carrier and recovery results.

### 11.2 — Exact location of the remaining existence problem
The full conditional matrix equivalence now quantifies **every required supplied packet**, not just one. An arbitrary packet index is allowed; each packet has finitely many split commuting conditions over characteristic zero. Existence of an actual realizing continuous system with all prescribed local conditions and all packets occupied is equivalent to residual nonemptiness at every coefficient, nonemptiness at every higher depth, and nonzero projector trace for every packet. The conditional core is checked. Full arithmetic status remains partial until the manuscript's required arithmetic packets and admissible objects are identified with these data. No carrier construction or positive occupancy is promised. The inherited dying-node and non-stable-local-property counterexamples remain checked.

New target: `PaperX.IndexedExistenceBoundary.all_required_packets_iff`; helpers `PaperX.CompletionAssembly.residual_and_higher_iff_all`, `positive_levels_iff_all`, `positive_finite_levels`.

### 11.3 — Natural finite seed rank
Conjectural finite seed rank. The one-seed wording now requires reachability of all required objects, not merely one source in an infinite condensation.



## Block 18: actual finite-group carrier summands

No source claim is promoted to fully arithmetic checked status. Totals remain 15 checked, 5 partial, 0 pending.

| Module | New checked scope |
|---|---|
| IdempotentNewton | Integral polynomial correction, squared defect, and preservation of intertwiners |
| AdicIdempotent | Actual idempotent over a complete coefficient ring from an approximate idempotent, preserving retained precision and every commutant |
| PrecisionIdempotent | Equivariant projector lifting from depth e+k to retained depth k>0 inside the supplied finite-group carrier |
| ProjectorSummands | Actual invariant image and kernel, equivariant inclusion/retraction, direct decomposition, and image characterization |
| MatrixProjector | Matrix-to-linear representation bridge and exact reduced image/kernel surjectivity |
| FiniteCarrierSummands | End-to-end construction of the summand with image and kernel reductions, plus algebraic pullback |
| SummandBoundary | Insufficient-depth obstruction, necessary loss of prescribed precision, and averaging that destroys idempotence |
| SummandExamples | Application of the general theorem to a nonzero proper Z₂ projector supplied modulo 4 |

Claim 9.2 gains a finite-group construction that no longer assumes the integral summand decomposition: a deep quotient projector is enough. The ambient integral carrier is still supplied. This does not construct arbitrary quotient representations, attach Weil–Deligne objects, or identify period invariants. The result lifts a single projector and its complement; arbitrary simultaneous orthogonal projector families were not asserted in Block 18.

Precise arithmetic gaps remain in FIVE_PARTIALS_STATUS.md. Kernel compilation, transitive public-declaration axiom audit, independent source review, finite computations, and fresh archive replay are recorded separately. Private helper lemmas are covered transitively by the public proofs that use them.
