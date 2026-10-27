# Lean 0.9.0 statement coverage

35 complete, 0 partial, 52 unformalized. Counts are not difficulty weighted.

## P1. Exact realization and consistency

Status: **complete**.

Algebraic realization works on arbitrary types. Norm estimates use continuous linear maps on normed spaces. The divided lower bound explicitly assumes the observation space is nontrivial, so the synthesis norm is positive. No orthogonality is inferred.

Targets: `Komorebi.LSM.Realization.analysis_injective`, `Komorebi.LSM.Realization.projector_idempotent`, `Komorebi.LSM.Realization.projector_fixed_iff`, `Komorebi.LSM.Realization.projector_range`, `Komorebi.LSM.analysis_norm_lower`, `Komorebi.LSM.synthesis_perturbation_bound`.

## P2. Coherent transport and operator realization

Status: **complete**.

Total operations on consistent coefficient subtypes. A reference chart is explicitly supplied, making the family nonempty. Partial-map admissible-domain extensions mentioned in surrounding prose are not covered.

Targets: `Komorebi.LSM.Realization.transport_self`, `Komorebi.LSM.Realization.transport_comp`, `Komorebi.LSM.Realization.realize_natural`, `Komorebi.LSM.coherent_family_unique_realization`.

## P3. Complete refinement preserves reconstruction

Status: **complete**.

Finite rooted structural trees with nonempty finite child families, arbitrary mixed-depth selections, and the actual condition of exactly one selected node on each full root-to-leaf path. Local parent=sum(children) gives global operator/signal reconstruction. Local sibling-range orthogonality gives the squared-norm identity over real or complex inner-product spaces. A self-adjoint zero-product lemma supplies that orthogonality from projector assumptions. Antichain completeness and energy conservation are conclusions, not assumed aggregate equations. No general best-basis optimization is included.

Targets: `Komorebi.LSM.PacketTree.pathCount_zero_iff`, `Komorebi.LSM.PacketTree.completeCut_branch`, `Komorebi.LSM.PacketTree.selectedSum_eq_root`, `Komorebi.LSM.PacketTree.complete_cut_sum`, `Komorebi.LSM.PacketTree.complete_cut_operator`, `Komorebi.LSM.PacketTree.complete_cut_reconstruction`, `Komorebi.LSM.PacketTree.conservative_energy`, `Komorebi.LSM.PacketTree.complete_cut_energy`, `Komorebi.LSM.PacketTree.range_orthogonal_of_projector_products`.

## P4. Transfer reconstruction and refinement

Status: **complete**.

Actual linear maps between possibly different spaces, with explicit finite completeness and intermediate idempotence. The algebra works under weaker assumptions than orthogonality.

Targets: `Komorebi.LSM.transfer_reconstruction`, `Komorebi.LSM.transfer_refinement`, `Komorebi.LSM.transfer_composition`.

## P5. Polynomial packet interactions

Status: **complete**.

All ordered multilinear interactions, including repeated packet indices. The finite polynomial sum retains every cross term. No general nonlinear dictionary discovery is claimed.

Targets: `Komorebi.LSM.multilinear_packet_expansion`, `Komorebi.LSM.polynomial_packet_expansion`.

## P6. Exact quotient criterion

Status: **complete**.

Reduced-map existence is constructed from fiber constancy, not assumed. Uniqueness is on the actual image, and action-indexed closure is included.

Targets: `Komorebi.LSM.predictive_closure_iff`, `Komorebi.LSM.closure_on_image_iff`, `Komorebi.LSM.controlled_closure_iff`.

## P7. Closure defect and compositional defect

Status: **complete**.

Actual linear maps and continuous-linear-map operator norm. Idempotence is explicit, and orthogonality is not needed for the algebraic identity. Closure is not assumed in order to prove its criterion.

Targets: `Komorebi.LSM.retained_dynamics_split`, `Komorebi.LSM.closure_iff_zero_defect`, `Komorebi.LSM.composition_defect`, `Komorebi.LSM.closure_norm_bound`.

## P8. Minimal linear predictive completion

Status: **complete**.

Known linear dynamics on a finite-dimensional vector space over a field. Iteration adds actual dual-map images of observable row subspaces. Stabilization is proved by strict dimension growth within dim(X)-dim(W0), with persistence after equality and least common invariant extension. Evaluation and arbitrary-basis state maps, linearly independent rows, linear readout H and action transitions B are constructed. Any competing linear summary retaining the initial output and closing under the dynamics contains this completed row space. The subspace/basis construction is noncomputable Lean mathematics, not an implemented numerical row-reduction learner or a proof that new observables are measurable from the original data. The surrounding single-operator Cayley-Hamilton discussion is not an additional coverage claim.

Targets: `Komorebi.LSM.invariantSequence_dimension_growth`, `Komorebi.LSM.invariantSequence_exists_stable`, `Komorebi.LSM.invariantSequence_stays`, `Komorebi.LSM.invariantCompletion_isLeast`, `Komorebi.LSM.predictiveCompletion_stopping_bound`, `Komorebi.LSM.predictiveCompletion_isLeast`, `Komorebi.LSM.observableState_surjective`, `Komorebi.LSM.observableState_closed`, `Komorebi.LSM.observableState_retains`, `Komorebi.LSM.basisObservation_independent`, `Komorebi.LSM.basisReadout_correct`, `Komorebi.LSM.basisTransition_correct`, `Komorebi.LSM.predictiveCompletion_le_competing_summary`, `Komorebi.LSM.predictiveCompletion_coordinate_realization`.

## P9. Coarsest joint finite closure

Status: **complete**.

Finite state space with actual equivalence-relation partitions, known row-stochastic action kernels and positive observation likelihoods. The mandatory initial quotient is nontrivial for semantic minimality. The construction first splits by likelihood vectors, then by aggregate transition probabilities into current blocks. Strict refinements increase quotient cardinality, giving stabilization within card(states)-card(initial likelihood-split quotient) rounds; equality persists. Actual quotient kernels and positive likelihoods are constructed. Their prediction equation holds on all real vectors and their Bayesian equation on probability priors. Semantic JointlyClosed means existence of such stochastic quotient data, not an assumed structural condition. Its equivalence to lumpability plus likelihood constancy uses P12 and yields the unique coarsest admissible refinement. The exact real/setoid construction is noncomputable and does not implement a finite-precision partition learner or identify unknown dynamics.

Targets: `Komorebi.LSM.FinitePartitions.strict_refinement_count`, `Komorebi.LSM.FinitePartitions.refinement_stabilizes`, `Komorebi.LSM.FinitePartitions.refinementIter_stays_fixed`, `Komorebi.LSM.FinitePartitions.stableRefinement_fixed`, `Komorebi.LSM.FinitePartitions.jointRefinement_termination`, `Komorebi.LSM.FinitePartitions.jointRefinement_coarsest`, `Komorebi.LSM.FinitePartitions.quotientKernel_stochastic`, `Komorebi.LSM.FinitePartitions.quotient_prediction_commutes`, `Komorebi.LSM.FinitePartitions.quotientLikelihood_pos`, `Komorebi.LSM.FinitePartitions.quotient_bayes_commutes`, `Komorebi.LSM.FinitePartitions.joint_closed_iff`, `Komorebi.LSM.FinitePartitions.jointRefinement_closed`, `Komorebi.LSM.FinitePartitions.jointlyClosed_refines_completion`, `Komorebi.LSM.FinitePartitions.coarsest_jointly_closed`.

## P10. Exact projected memory and a conditional tail bound

Status: **complete**.

Exact recurrence elimination, lag reindexing, actual projected blocks, continuous-map bridge, same-history geometric truncation bound and initial-term bound. Nonnegative radius/rho and rho<1 are explicit for the bound. H<=t for full-minus-truncated history; the omitted Ico tail also handles an empty interval. No recursively predicted rollout stability is inferred.

Targets: `Komorebi.LSM.unresolved_solution`, `Komorebi.LSM.exact_memory_lags`, `Komorebi.LSM.projected_memory`, `Komorebi.LSM.continuous_exact_memory_lags`, `Komorebi.LSM.memory_truncation_difference_bound`, `Komorebi.LSM.unresolved_initial_bound`.

## P11. Ideal statistical benefit of refinement

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P12. Bayesian closure and its exact defect

Status: **complete**.

Finite real probability vectors and a surjective map onto the actual coarse blocks. With at least two coarse blocks and strictly positive fine and declared coarse likelihoods, commutation for every normalized nonnegative prior is equivalent to a common positive likelihood scale. Necessity is proved using two-point priors and a cross-block bridge, not assumed as fiber constancy. The one-block exception is proved separately. The effective-likelihood and matrix-defect identities include zero-prior-mass blocks. The fixed-prior algebra assumes nonnegative prior entries and nonzero fine/coarse evidences, so in particular includes nonnegative likelihoods with positive evidences. Totalized real division at zero is not interpreted as a valid posterior. Matrix null direction for a common likelihood scale is also proved.

Targets: `Komorebi.LSM.FiniteBayes.cross_ratio_of_commutes`, `Komorebi.LSM.FiniteBayes.bayesian_coarsening_iff`, `Komorebi.LSM.FiniteBayes.likelihood_constant_on_fibers`, `Komorebi.LSM.FiniteBayes.one_block_commutes`, `Komorebi.LSM.FiniteBayes.zero_mass_weight`, `Komorebi.LSM.FiniteBayes.effectiveLikelihood_product`, `Komorebi.LSM.FiniteBayes.effectiveLikelihood_evidence`, `Komorebi.LSM.FiniteBayes.aggregate_posterior_effective`, `Komorebi.LSM.FiniteBayes.bayesian_coarsening_defect`, `Komorebi.LSM.FiniteBayes.bayesian_coarsening_matrix_defect`, `Komorebi.LSM.FiniteBayes.informationLossMatrix_scale_null`.

## P13. Strong fixed-horizon refinement limit

Status: **complete**.

Strong convergence is proved for actual continuous linear maps with a uniform operator bound. The compression estimate and fixed-power induction are derived. Actual orthogonal subspace projections provide the contractivity premise, for real or complex inner-product spaces. Each horizon is fixed; neither operator-norm convergence nor uniform-in-time accuracy is asserted. The fitted-operator extension retains its independent uniform-bound and strong-error assumptions.

Targets: `Komorebi.LSM.Stability.compression_error_bound`, `Komorebi.LSM.Stability.compression_uniform_bound`, `Komorebi.LSM.Stability.strong_fixed_powers`, `Komorebi.LSM.Stability.contractive_refinement_fixed_horizon`, `Komorebi.LSM.Stability.strong_fixed_horizon_refinement`, `Komorebi.LSM.Stability.estimated_refinement_fixed_horizon`.

## P14. Exact causal delay closure

Status: **complete**.

Positive delay length. Actual observation maps, not empirical ranks. Kernel factorization, range-valued transition, uniqueness, rank-nullity equivalence, dimension-bound stabilization and warm-up-indexed future output are derived over finite-dimensional field vector spaces. The zero-dimensional case does not license a last block for h=0.

Targets: `Komorebi.LSM.Delay.observation`, `Komorebi.LSM.Delay.observation_apply`, `Komorebi.LSM.Delay.mem_observation_kernel`, `Komorebi.LSM.Delay.kernel_antitone`, `Komorebi.LSM.Delay.kernel_closed_iff_plateau`, `Komorebi.LSM.Delay.kernel_succ`, `Komorebi.LSM.Delay.kernel_stays`, `Komorebi.LSM.Delay.transition`, `Komorebi.LSM.Delay.transition_apply`, `Komorebi.LSM.Delay.transition_unique`, `Komorebi.LSM.Delay.transition_exists_iff`, `Komorebi.LSM.Delay.transition_iterates`, `Komorebi.LSM.Delay.causal_last_block`, `Komorebi.LSM.Delay.rank_plateau_iff_kernel`, `Komorebi.LSM.Delay.dimension_closure`, `Komorebi.LSM.Delay.delay_closure_rank_iff`, `Komorebi.LSM.Delay.causal_future_output`.

## P15. Data-span identification and its boundary

Status: **complete**.

Actual sample and successor linear maps. Kernel compatibility is equivalent to ambient extension, all fits agree on the sampled span, and span invariance is equivalent to successor-image inclusion. The orthogonal Moore-Penrose inverse is constructed using quotient factorization and orthogonal projections, with all four Penrose conditions proved. A proper subspace admits distinct extensions. Classical choices support a symbolic real operator, not an executable floating-point algorithm.

Targets: `Komorebi.LSM.Identification.onRange`, `Komorebi.LSM.Identification.onRange_apply`, `Komorebi.LSM.Identification.fit_iff_kernel`, `Komorebi.LSM.Identification.fits_agree_on_range`, `Komorebi.LSM.Identification.fitted_range`, `Komorebi.LSM.Identification.generalized_inverse_fit`, `Komorebi.LSM.Identification.unseen_direction_not_identified`, `Komorebi.LSM.Identification.retained`, `Komorebi.LSM.Identification.retained_apply`, `Komorebi.LSM.Identification.retained_kernel`, `Komorebi.LSM.Identification.pinv`, `Komorebi.LSM.Identification.pinv_apply_image`, `Komorebi.LSM.Identification.apply_retained`, `Komorebi.LSM.Identification.pinv_apply_mem`, `Komorebi.LSM.Identification.apply_pinv`, `Komorebi.LSM.Identification.penrose_one`, `Komorebi.LSM.Identification.penrose_two`, `Komorebi.LSM.Identification.penrose_range_projection`, `Komorebi.LSM.Identification.penrose_source_projection`, `Komorebi.LSM.Identification.moore_penrose_fit`, `Komorebi.LSM.Identification.penrose_three`, `Komorebi.LSM.Identification.penrose_four`.

## P16. Fixed-space identification bound

Status: **complete**.

Finite-dimensional real Hilbert spaces, with the spectral operator norm. The smallest row singular value is represented by the infimum of adjoint norm ratios, proved equal to the infimum on unit vectors. Strict input error below this value derives surjectivity and the norm of the constructed orthogonal pseudoinverse. The full residual identity and divided bound are derived. Coordinates and dimension are fixed. No fitted-basis or statistical error is absorbed without a bound.

Targets: `Komorebi.LSM.Identification.pinvL`, `Komorebi.LSM.Identification.rowGain`, `Komorebi.LSM.Identification.rowGain_variational_unit`, `Komorebi.LSM.Identification.rowGain_lower`, `Komorebi.LSM.Identification.rowGain_perturbation`, `Komorebi.LSM.Identification.surjective_of_adjoint_lower`, `Komorebi.LSM.Identification.pinvL_right`, `Komorebi.LSM.Identification.pinvL_bound`, `Komorebi.LSM.Identification.noisy_identification_identity`, `Komorebi.LSM.Identification.noisy_identification_bound`.

## P17. Finite-prefix indistinguishability

Status: **complete**.

For every natural horizon T, two explicit rational systems on Fin (T+2) have identical outputs at all times through T and different output at T+1. Their transition powers at T+2 vanish. No bound on the unknown hidden dimension is assumed.

Targets: `Komorebi.LSM.Delay.shift`, `Komorebi.LSM.Delay.shift_power`, `Komorebi.LSM.Delay.shift_nilpotent`, `Komorebi.LSM.Delay.delayedInitial`, `Komorebi.LSM.Delay.output`, `Komorebi.LSM.Delay.delayed_output`, `Komorebi.LSM.Delay.finite_prefix_indistinguishability`.

## P18. Compositional defect propagation

Status: **complete**.

The theorem permits genuinely time-indexed normed state spaces and representations. It defines local residuals from the true transition and approximate step, derives the one-step error, and proves the manuscript suffix-product/sum bound. Lipschitz constants are nonnegative; both true and predicted inputs must lie in the declared domain. Output decoding, constant contraction and exact closure-versus-fit decomposition are separate theorems. An arbitrary changed policy is not automatically covered.

Targets: `Komorebi.LSM.Stability.errorEnvelope`, `Komorebi.LSM.Stability.recurrence_product_sum`, `Komorebi.LSM.Stability.local_error_step`, `Komorebi.LSM.Stability.compositional_defect_propagation`, `Komorebi.LSM.Stability.decoder_error_bound`, `Komorebi.LSM.Stability.constant_gain_bound`, `Komorebi.LSM.Stability.linear_defect_split`.

## P19. Uniform prediction bound for a stable finite-memory truncation

Status: **complete**.

The predictor uses its own recursively generated history, with integer time indices and an explicit initialization window. A strict norm-sum gain below one yields the actual supremum error bound. Coefficient, geometric memory-tail and initialization-forcing budgets are derived and inserted into the recursive theorem. Zero prehistory handles H=0 and t<H without natural-number subtraction artifacts. Retaining the exact forcing removes its contribution. The condition is sufficient, not necessary; failure of this certificate is not proof of instability.

Targets: `Komorebi.LSM.Stability.finiteMemory`, `Komorebi.LSM.Stability.finiteMemory_error_bound`, `Komorebi.LSM.Stability.invariant_error_radius`, `Komorebi.LSM.Stability.finite_memory_prediction_bound`, `Komorebi.LSM.Stability.finite_memory_uniform_prediction_bound`, `Komorebi.LSM.Stability.initialized_memory_split`, `Komorebi.LSM.Stability.memory_defect_identity`, `Komorebi.LSM.Stability.integer_memory_tail_bound`, `Komorebi.LSM.Stability.memory_approximation_defect_bound`, `Komorebi.LSM.Stability.discarded_initialized_forcing_bound`, `Komorebi.LSM.Stability.retained_initialized_forcing_bound`, `Komorebi.LSM.Stability.certified_memory_truncation`.

## P20. Packet-interaction truncation bound

Status: **complete**.

Continuous multilinear maps retain ordered interaction tuples and their multiplicities. Restricted product-of-packet-range norm bounds yield the exact omitted sum and its amplitude majorant. Telescoping yields the retained Lipschitz bound on the declared ball. Contractivity is explicitly derived for actual orthogonal subspace projectors. The finite-dimensional real Hilbert sector is included in a stronger normed-space algebraic theorem. A separate bound is required for an unexpanded nonpolynomial law and for keeping trajectories inside the domain.

Targets: `Komorebi.LSM.PacketApproximation.HasPacketBound`, `Komorebi.LSM.PacketApproximation.full_ordered_expansion`, `Komorebi.LSM.PacketApproximation.omitted_interaction_identity`, `Komorebi.LSM.PacketApproximation.packet_interaction_truncation_bound`, `Komorebi.LSM.PacketApproximation.packet_term_lipschitz`, `Komorebi.LSM.PacketApproximation.retained_polynomial_lipschitz_bound`, `Komorebi.LSM.PacketApproximation.orthogonal_packet_lipschitz_bound`, `Komorebi.LSM.PacketApproximation.additional_model_remainder`.

## P21. Coherent reconciliation and coordinate-stable transport

Status: **complete**.

Linear atlases act on the actual analysis-range subtype. A genuine normed additive group and normed space are constructed by pulling back synthesis; exact transports are isometries and every Lipschitz constant is equivalent to its object-space counterpart. Repaired maps are consistent and intertwine. Weighted variance and unique minimization are proved for the actual squared Frobenius objective, with a constructed orthonormal matrix coordinate equivalence in finite-dimensional real Hilbert space. The target-error inequality uses actual continuous-operator norms and nonnegative weights summing to one. Agreement is not correctness. The adjacent learned singular-value/pseudoinverse discussion is not claimed as a separate checked theorem.

Targets: `Komorebi.LSM.Reconciliation.LinearAtlas.repaired_consistent`, `Komorebi.LSM.Reconciliation.LinearAtlas.repaired_intertwines`, `Komorebi.LSM.Reconciliation.reconciledOperator`, `Komorebi.LSM.Reconciliation.coherent_reconciled_family`, `Komorebi.LSM.Reconciliation.weighted_variance_identity`, `Komorebi.LSM.Reconciliation.weighted_unique_minimizer`, `Komorebi.LSM.Reconciliation.frobenius_variance_identity`, `Komorebi.LSM.Reconciliation.operator_unique_frobenius_minimizer`, `Komorebi.LSM.Reconciliation.orthonormalOperatorCoordinates`, `Komorebi.LSM.Reconciliation.hilbert_operator_unique_minimizer`, `Komorebi.LSM.Reconciliation.reconciled_target_error`, `Komorebi.LSM.Reconciliation.LinearAtlas.coeffNormed`, `Komorebi.LSM.Reconciliation.LinearAtlas.coeffNormedSpace`, `Komorebi.LSM.Reconciliation.LinearAtlas.pullback_norm`, `Komorebi.LSM.Reconciliation.LinearAtlas.transport_isometry`, `Komorebi.LSM.Reconciliation.LinearAtlas.represented_lipschitz_iff`.

## P22. The upward-lift obstruction

Status: **complete**.

Existence/uniqueness between actual images, the linear kernel criterion, and the half-distance worst-case norm lower bound. An onto hypothesis in the linear-map construction means that its codomain is the true coarse state space.

Targets: `Komorebi.LSM.factor_on_images_iff`, `Komorebi.LSM.linear_fiber_iff_kernel`, `Komorebi.LSM.linear_factor_iff_kernel`, `Komorebi.LSM.refinement_worst_case_lower`.

## P23. Exact accounting for an enumerated grammar

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P24. Prior-preserving program refinement

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P25. Observationally grounded finite linear realization

Status: **complete**.

Conditional finite observable realization. A covering table and true successors recover the unique map by the data-only pseudoinverse formula. Delay-range identification, every iterate, causal future output, lossless atlas recoding and complete packet synthesis are linked. The actual noisy fitted predictor feeds the product-sum error envelope, a contraction radius, and a decoder bound. Coverage and model assumptions remain supplied. No unrestricted hidden-state discovery or executable production-code verification.

Targets: `Komorebi.LSM.Delay.observation`, `Komorebi.LSM.Delay.observation_apply`, `Komorebi.LSM.Delay.mem_observation_kernel`, `Komorebi.LSM.Delay.kernel_antitone`, `Komorebi.LSM.Delay.kernel_closed_iff_plateau`, `Komorebi.LSM.Delay.kernel_succ`, `Komorebi.LSM.Delay.kernel_stays`, `Komorebi.LSM.Delay.transition`, `Komorebi.LSM.Delay.transition_apply`, `Komorebi.LSM.Delay.transition_unique`, `Komorebi.LSM.Delay.transition_exists_iff`, `Komorebi.LSM.Delay.transition_iterates`, `Komorebi.LSM.Delay.causal_last_block`, `Komorebi.LSM.Delay.rank_plateau_iff_kernel`, `Komorebi.LSM.Delay.dimension_closure`, `Komorebi.LSM.Delay.delay_closure_rank_iff`, `Komorebi.LSM.Delay.causal_future_output`, `Komorebi.LSM.Identification.pinvL`, `Komorebi.LSM.Identification.rowGain`, `Komorebi.LSM.Identification.rowGain_variational_unit`, `Komorebi.LSM.Identification.rowGain_lower`, `Komorebi.LSM.Identification.rowGain_perturbation`, `Komorebi.LSM.Identification.surjective_of_adjoint_lower`, `Komorebi.LSM.Identification.pinvL_right`, `Komorebi.LSM.Identification.pinvL_bound`, `Komorebi.LSM.Identification.noisy_identification_identity`, `Komorebi.LSM.Identification.noisy_identification_bound`, `Komorebi.LSM.Identification.learned`, `Komorebi.LSM.Identification.learned_eq_true`, `Komorebi.LSM.Identification.learned_all_horizons`, `Komorebi.LSM.Identification.learned_packet_output`, `Komorebi.LSM.Identification.learned_atlas_iterates`, `Komorebi.LSM.Identification.delay_table_identifies`, `Komorebi.LSM.Identification.fitted_rollout`, `Komorebi.LSM.Identification.rollout_uniform_bound`, `Komorebi.LSM.Identification.contracting_rollout`, `Komorebi.LSM.Identification.decoded_rollout_bound`.

## P26. Finite instrument closure

Status: **complete**.

Known instrument on a finite nonempty hidden state type with finitely many outcomes. Actual nonnegative matrices obey exact per-action column-mass conservation. The P8 iteration from the nonzero mass row stabilizes within card(hidden)-1 steps and is proved equal to the span of all chronological word tests. A finite basis is extended/reindexed to place mass literally in its first coordinate. Its observation map has independent rows, is surjective onto the full coordinate space, has precisely the completed row space, and supplies unique reduced transitions. Word probabilities agree for every initial vector; probability and posterior meaning are restricted to realizableBeliefs and positive evidence. Minimality is against every linear summary with linear readouts of all words on every prior. All constructions using arbitrary real bases are noncomputable. This is not observable-data learning, minimum dimension for one fixed initialization, or a general cone-search theorem.

Targets: `Komorebi.LSM.FiniteInstruments.Instrument.instrument_mass`, `Komorebi.LSM.FiniteInstruments.Instrument.word_probability`, `Komorebi.LSM.FiniteInstruments.Instrument.observationTreeMass_eq`, `Komorebi.LSM.FiniteInstruments.instrumentCompletion_eq_wordSpan`, `Komorebi.LSM.FiniteInstruments.finite_instrument_stopping_bound`, `Komorebi.LSM.invariantSequence_stays`, `Komorebi.LSM.FiniteInstruments.exists_basis_first`, `Komorebi.LSM.FiniteInstruments.finite_instrument_coordinates`, `Komorebi.LSM.FiniteInstruments.closed_operator_unique`, `Komorebi.LSM.FiniteInstruments.finite_instrument_closure`, `Komorebi.LSM.FiniteInstruments.completion_le_word_reading_summary`, `Komorebi.LSM.FiniteInstruments.reduced_likelihood`, `Komorebi.LSM.FiniteInstruments.reduced_posterior`, `Komorebi.LSM.FiniteInstruments.reduced_likelihood_prior`, `Komorebi.LSM.FiniteInstruments.reduced_posterior_realizable`, `Komorebi.LSM.FiniteInstruments.reduced_word_probability`, `Komorebi.LSM.FiniteInstruments.reduced_mass_identity`.

## P27. Minimal finite behavior realization

Status: **complete**.

The behavior space is the actual real linear span of history/test columns on finite chronological words. Branch operators are constructed by restriction of test shifts, rather than postulated well-defined coordinate maps. Rank means finite dimension of this full column space, not a sampled matrix rank. Every finite linear realization has at least that dimension. Reachable and observable realizations are explicitly isomorphic, intertwining the initial vector, all operators and mass; the intertwiner is unique. Conditional predictions use the true word/history ratio on positive histories. Nonnegativity and causal normalization are separate supplied word-law assumptions. Infinite-record probability measures and the auxiliary supremum-of-finite-submatrix characterization are not additional claims of this mapping. No model is learned from a finite noisy sample here.

Targets: `Komorebi.LSM.Behavior.space`, `Komorebi.LSM.Behavior.branch`, `Komorebi.LSM.Behavior.branch_history`, `Komorebi.LSM.Behavior.word_probability`, `Komorebi.LSM.Behavior.test_evaluation`, `Komorebi.LSM.Behavior.conditional_test`, `Komorebi.LSM.Behavior.conditional_mass`, `Komorebi.LSM.Behavior.conditional_equivalence`, `Komorebi.LSM.Behavior.Realization.toBehavior_surjective`, `Komorebi.LSM.Behavior.Realization.behavior_dimension_le`, `Komorebi.LSM.Behavior.Realization.behavior_finite`, `Komorebi.LSM.Behavior.canonical_reachable`, `Komorebi.LSM.Behavior.canonical_observable`, `Komorebi.LSM.Behavior.Realization.minimal_dimension`, `Komorebi.LSM.Behavior.Realization.minimal_realizations_similar`, `Komorebi.LSM.Behavior.Realization.intertwiner_unique`, `Komorebi.LSM.Behavior.CausalLaw.canonical_conditional_probability`.

## P28. Observable table reconstruction

Status: **complete**.

Finite core coordinates are actual selected test evaluations. An invertible square population matrix gives surjectivity and a lower rank bound; an explicit global finite behavior-rank upper bound supplies injectivity and full coverage. The formula G_s H^{-1} is an actual matrix expression using the correct inverse side. It yields the full chronological state, mass and probability for every word, a reachable observable model and minimal dimension against every finite linear realization. A distinguished selected empty test is the literal mass coordinate (index zero in Fin r). Normalized updates require positive evidence for probabilistic interpretation. Finding the core, deriving an unknown global rank bound and statistical estimation of table entries are not claimed. Noncomputable inverse/space constructions do not amount to an executed numerical data learner.

Targets: `Komorebi.LSM.Behavior.core`, `Komorebi.LSM.Behavior.shiftedCore`, `Komorebi.LSM.Behavior.evaluate_surjective`, `Komorebi.LSM.Behavior.core_rank_exact`, `Komorebi.LSM.Behavior.evaluate_bijective`, `Komorebi.LSM.Behavior.synthesize_surjective`, `Komorebi.LSM.Behavior.coreEquiv`, `Komorebi.LSM.Behavior.reconstructed`, `Komorebi.LSM.Behavior.reconstructed_intertwines`, `Komorebi.LSM.Behavior.reconstructed_unique`, `Komorebi.LSM.Behavior.reconstructed_state`, `Komorebi.LSM.Behavior.reconstructed_probability`, `Komorebi.LSM.Behavior.reconstructed_conditional_update`, `Komorebi.LSM.Behavior.reconstructed_likelihood_pos`, `Komorebi.LSM.Behavior.tableModel`, `Komorebi.LSM.Behavior.tableModel_minimal`, `Komorebi.LSM.Behavior.observable_table_reconstruction`.

## P29. Canonical probability cone

Status: **complete**.

The actual canonical behavior space is the submodule span of history/test functions from P27. Causal consistency and nonnegative behavior are supplied as CausalLaw. The all-test cone is defined by every finite test, not by finitely sampled trajectories. Cone closure under addition and nonnegative scaling, convexity, pointedness, generation by history columns, branch invariance, strict positive mass, the per-action mass identity, normalized posterior closure, and test-coordinate bounds are proved. Closedness and compact normalized-base results use the actual inherited Hausdorff function-space topology and an explicit finite-dimensional behavior-space assumption. Compactness follows through a proved closed embedding into the compact all-test unit cube; boundedness of the desired base is not assumed. The selected empty test is the literal mass-one coordinate. No finite inequality description or learned cone algorithm is claimed for the general canonical space.

Targets: `Komorebi.LSM.TestDomains.allTests_closed`, `Komorebi.LSM.TestDomains.testLevel_closed`, `Komorebi.LSM.TestDomains.base_closed`, `Komorebi.LSM.TestDomains.observe_closedEmbedding`, `Komorebi.LSM.TestDomains.base_compact`, `Komorebi.LSM.Behavior.probabilityCone`, `Komorebi.LSM.Behavior.probabilityBase`, `Komorebi.LSM.Behavior.probabilityCone_eq_tests`, `Komorebi.LSM.Behavior.probabilityBase_eq_tests`, `Komorebi.LSM.Behavior.probability_observe_injective`, `Komorebi.LSM.Behavior.probabilityCone_convex`, `Komorebi.LSM.Behavior.probabilityCone_pointed`, `Komorebi.LSM.Behavior.probabilityCone_closed`, `Komorebi.LSM.Behavior.probabilityCone_invariant`, `Komorebi.LSM.Behavior.probabilityCone_smul`, `Komorebi.LSM.Behavior.probabilityCone_add`, `Komorebi.LSM.Behavior.history_mem_probabilityCone`, `Komorebi.LSM.Behavior.probabilityCone_spans`, `Komorebi.LSM.Behavior.probabilityCone_strict_mass`, `Komorebi.LSM.Behavior.probabilityBase_test_bounds`, `Komorebi.LSM.Behavior.probabilityBase_compact`, `Komorebi.LSM.Behavior.probabilityBase_convex`, `Komorebi.LSM.Behavior.initial_mem_probabilityBase`, `Komorebi.LSM.Behavior.probabilityBase_posterior`, `Komorebi.LSM.Behavior.probabilityBase_core_bounds`, `Komorebi.LSM.Behavior.canonical_probability_cone`.

## P30. Positive packet decomposition and its boundary

Status: **complete**.

The mixture theorem works over real modules, a cone closed under nonnegative scaling, a strictly positive mass functional on nonzero cone elements, and complete linear packet maps preserving that cone. Weight nonnegativity, their unit sum, normalized component membership and mass, vanishing zero-weight components and the positive-weight finite mixture identity are proved separately. The orthant result uses actual finite real matrices: preservation of all nonnegative vectors is equivalent to entrywise nonnegativity; completeness forces zero off-diagonals; idempotence forces diagonal entries 0 or 1; every coordinate has exactly one selected packet. Reconstruction or orthogonality alone does not imply positivity. This theorem does not supply a learned cone or formalize the compactness theorem of P29.

Targets: `Komorebi.LSM.PositivePackets.StrictMass`, `Komorebi.LSM.PositivePackets.mass_nonnegative`, `Komorebi.LSM.PositivePackets.mass_zero_iff`, `Komorebi.LSM.PositivePackets.packet_weights_sum`, `Komorebi.LSM.PositivePackets.normalized_packet`, `Komorebi.LSM.PositivePackets.positive_packet_mixture`, `Komorebi.LSM.PositivePackets.orthant_preserving_iff`, `Komorebi.LSM.PositivePackets.off_diagonal_zero`, `Komorebi.LSM.PositivePackets.matrix_eq_diagonal`, `Komorebi.LSM.PositivePackets.diagonal_boolean`, `Komorebi.LSM.PositivePackets.unique_selected_packet`, `Komorebi.LSM.PositivePackets.positive_idempotents_are_coordinate_selections`.

## P31. Missing-intervention nonidentifiability

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P32. Finite-table rank separation and subspace stability

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P33. Noisy core-block realization

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P34. Normalization-aware filtering stability

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P35. Reset-experiment probability certificate

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P36. Exact normalized closure defect

Status: **complete**.

The vector identity is on real coordinate functions with an actual linear summary and mass-preservation law; the fine and proposed branch evidences are strictly positive. The separate likelihood identity holds without division. The oblique map is an actual rank-one correction of the identity. The converse requires a nonzero entrywise-nonnegative fine branch and agreement of likelihoods AND normalized posteriors on every strictly positive prior. Explicit uniform and perturbed-uniform priors prove that this interior family spans the fine space. No equality of unnormalized operators is assumed in that converse. A one-state instrument counterexample proves that posterior agreement alone is insufficient. The idempotent-projector specialization gives the omitted-to-retained block. The statements do not certify a fitted probability domain or control statistical error.

Targets: `Komorebi.LSM.FiniteInstruments.oblique`, `Komorebi.LSM.FiniteInstruments.oblique_null`, `Komorebi.LSM.FiniteInstruments.oblique_mass_zero`, `Komorebi.LSM.FiniteInstruments.oblique_idempotent`, `Komorebi.LSM.FiniteInstruments.likelihood_defect`, `Komorebi.LSM.FiniteInstruments.normalized_closure_defect`, `Komorebi.LSM.FiniteInstruments.nonnegative_branch_mass_pos`, `Komorebi.LSM.FiniteInstruments.linearMap_eq_of_strict_priors`, `Komorebi.LSM.FiniteInstruments.closure_of_likelihood_and_posterior`, `Komorebi.LSM.FiniteInstruments.closureDefect_projected`, `Komorebi.LSM.Block4Examples.posterior_alone_does_not_imply_closure`, `Komorebi.LSM.Block4Examples.example_satisfies_general_defect`.

## P37. Conditional observation-based stochastic completion

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P38. Test-cone hierarchy and a finite stopping certificate

Status: **complete**.

The finite-level cones are actual inequalities for all words of length at most h. Their successor/preimage identity, antitonicity, intersection, largest invariant-set property and exact adjacent-level stopping implication are proved. A noncomputable finite set of linear halfspaces is constructed at every level for finite symbol types, establishing the polyhedral description rather than assuming it. An observability row-span hypothesis is connected to injectivity of all-test evaluation. With the explicit per-action mass law, injectivity yields pointedness and strictly positive mass; membership of reachable vectors and their full span yields generation. Finite stabilization is sufficient, not asserted for every family. A one-step acceptance test is not treated as invariance. The cone may be improper without the stated observability/reachability conditions.

Targets: `Komorebi.LSM.TestDomains.observe`, `Komorebi.LSM.TestDomains.observe_apply`, `Komorebi.LSM.TestDomains.testLevel`, `Komorebi.LSM.TestDomains.allTests`, `Komorebi.LSM.TestDomains.base`, `Komorebi.LSM.TestDomains.allTests_zero`, `Komorebi.LSM.TestDomains.allTests_add`, `Komorebi.LSM.TestDomains.allTests_smul`, `Komorebi.LSM.TestDomains.allTests_convex`, `Komorebi.LSM.TestDomains.base_convex`, `Komorebi.LSM.TestDomains.allTests_invariant`, `Komorebi.LSM.TestDomains.allTests_word`, `Komorebi.LSM.TestDomains.allTests_mass_nonneg`, `Komorebi.LSM.TestDomains.testLevel_zero`, `Komorebi.LSM.TestDomains.testLevel_succ`, `Komorebi.LSM.TestDomains.testLevel_antitone`, `Komorebi.LSM.TestDomains.allTests_eq_inter`, `Komorebi.LSM.TestDomains.allTests_greatest`, `Komorebi.LSM.TestDomains.testLevel_stopping`, `Komorebi.LSM.TestDomains.allTests_pointed`, `Komorebi.LSM.TestDomains.allTests_spans`, `Komorebi.LSM.TestDomains.test_sum_next`, `Komorebi.LSM.TestDomains.test_next_le`, `Komorebi.LSM.TestDomains.test_extension_le`, `Komorebi.LSM.TestDomains.test_le_mass`, `Komorebi.LSM.TestDomains.allTests_strict_mass`, `Komorebi.LSM.TestDomains.base_test_bounds`, `Komorebi.LSM.TestDomains.base_posterior`, `Komorebi.LSM.TestDomains.finite_test_halfspaces`, `Komorebi.LSM.TestDomains.finite_stopping_certificate`, `Komorebi.LSM.TestDomains.observe_injective_of_row_span`.

## P39. Finite positive-lift certificate

Status: **complete**.

The cone is the actual image of nonnegative finite coefficient vectors under V. Normalization is lambda composed with V equals the coefficient-sum functional; surjectivity is the full-row-rank condition when generation is asserted. Cone closedness, convexity, pointedness, strict mass and generation are derived, including for redundant generators. The normalized base is proved equal to the image of the finite probability simplex and to the actual convex hull of the generators, and is compact. Invariance is equivalent to existence of an entrywise nonnegative matrix A with B V = V A, with the necessity witness constructed from the generator images by classical choice. Lifted mass conservation, the actual hidden instrument, intertwining for every chronological word and word probabilities follow from the finite witness and a nonnegative normalized initial coefficient vector. No unique lift is claimed for redundant V. The adjacent Farkas dual-certificate discussion is not claimed as an additional formal theorem.

Targets: `Komorebi.LSM.PositiveLift.hull`, `Komorebi.LSM.PositiveLift.generator`, `Komorebi.LSM.PositiveLift.normalizedHull`, `Komorebi.LSM.PositiveLift.normalized_mass`, `Komorebi.LSM.PositiveLift.mass_generator`, `Komorebi.LSM.PositiveLift.generator_mem`, `Komorebi.LSM.PositiveLift.hull_zero`, `Komorebi.LSM.PositiveLift.hull_add`, `Komorebi.LSM.PositiveLift.hull_smul`, `Komorebi.LSM.PositiveLift.hull_convex`, `Komorebi.LSM.PositiveLift.hull_mass_nonneg`, `Komorebi.LSM.PositiveLift.hull_mass_zero`, `Komorebi.LSM.PositiveLift.hull_strict_mass`, `Komorebi.LSM.PositiveLift.hull_pointed`, `Komorebi.LSM.PositiveLift.synthesis_sum`, `Komorebi.LSM.PositiveLift.hull_spans`, `Komorebi.LSM.PositiveLift.normalizedHull_eq_prior_image`, `Komorebi.LSM.PositiveLift.invariant_iff_generators`, `Komorebi.LSM.PositiveLift.positive_lift_iff`, `Komorebi.LSM.PositiveLift.lifted_mass`, `Komorebi.LSM.PositiveLift.liftedInstrument`, `Komorebi.LSM.PositiveLift.lifted_word`, `Komorebi.LSM.PositiveLift.lifted_word_probability`, `Komorebi.LSM.PositiveLift.finite_positive_lift_certificate`, `Komorebi.LSM.PositiveLift.prior_box`, `Komorebi.LSM.PositiveLift.priors_compact`, `Komorebi.LSM.PositiveLift.normalizedHull_compact`, `Komorebi.LSM.PositiveLift.normalizedHull_convex`, `Komorebi.LSM.PositiveLift.hull_closed`, `Komorebi.LSM.PositiveLift.normalizedHull_eq_convexHull`.

## P40. Robust finite-domain certificate

Status: **complete**.

The uncertainty set is the actual convex hull of complete operator families with shared convex coefficients across all branches. Nonnegative vertex lifts and exact mass conservation imply every family in that hull preserves the fixed generator cone and mass. Explicit mixed lifts are constructed. History-dependent selection of a family is handled through an actual adaptive word recursion and finite observation-tree mass recursion under any deterministic history-based action policy. Cone membership, nonnegative word likelihood, the unit upper bound and tree normalization are proved for arbitrary finite horizons. A separate theorem uses actual continuous linear operators, their operator norms and a complete facet description of the same cone to prove the stated norm-ball margin implies perturbed invariance and existence of a positive lift. The normed statement specializes to Euclidean coordinates. Exact mass constraints remain separate; independently mixing branches is not inferred to conserve mass. No statistical coverage of the uncertainty hull is asserted.

Targets: `Komorebi.LSM.RobustDomains.ValidFamily`, `Komorebi.LSM.RobustDomains.validFamily_convex`, `Komorebi.LSM.RobustDomains.robust_convex_hull`, `Komorebi.LSM.RobustDomains.robust_positive_lift`, `Komorebi.LSM.RobustDomains.mixed_lift`, `Komorebi.LSM.RobustDomains.mixed_entries_nonnegative`, `Komorebi.LSM.RobustDomains.adaptiveWord`, `Komorebi.LSM.RobustDomains.adaptiveWord_in_cone`, `Komorebi.LSM.RobustDomains.adaptiveWord_nonnegative`, `Komorebi.LSM.RobustDomains.adaptiveWord_mass_le`, `Komorebi.LSM.RobustDomains.adaptiveTreeMass`, `Komorebi.LSM.RobustDomains.adaptiveTreeMass_eq`, `Komorebi.LSM.RobustDomains.facet_error_bound`, `Komorebi.LSM.RobustDomains.facet_margin_robust`, `Komorebi.LSM.RobustDomains.facet_norm_ball_invariant`, `Komorebi.LSM.RobustDomains.facet_norm_ball_lift`.

## P41. Certified correction and its error budget

Status: **complete**.

A FeasiblePoint records the actual finite nonnegative-lift, intertwining, per-action mass and initial-prior constraints. Internal family validity, normalized initial membership and every finite-word probability are derived from those constraints and normalized generators, not included as assumed conclusions. An actual true member of a confidence set with a fixed-domain witness constructs a feasible point in that set. The two-center bound norm(corrected-truth) <= 2 epsilon is proved for an arbitrary seminormed additive group, hence applies both to continuous linear operators and to initial states in their specified norms. No optimizer, empirical confidence set, or implication from one feasible point to coverage/validity of every point is supplied. Fixed-domain witness construction is classical and noncomputable. The adjacent explicit mixing-repair formula is outside this numbered proposition's mapping.

Targets: `Komorebi.LSM.CertifiedCorrection.FeasiblePoint`, `Komorebi.LSM.CertifiedCorrection.FeasiblePoint.valid_family`, `Komorebi.LSM.CertifiedCorrection.FeasiblePoint.initial_mem`, `Komorebi.LSM.CertifiedCorrection.FeasiblePoint.all_word_probabilities`, `Komorebi.LSM.CertifiedCorrection.feasible_of_certified_member`, `Komorebi.LSM.CertifiedCorrection.two_center_error`.

## P42. Instrument contraction before normalization

Status: **complete**.

The base norm is the actual infimum over decompositions x=u-v with u,v in the declared closed, generating cone. Nonnegative mass, existence of decompositions, the infimum bounds, triangle inequality, negation invariance and absolute scalar homogeneity are proved. In finite-dimensional real normed spaces, compactness of the normalized base and a bound by the ambient norm are derived from cone closedness and strict mass; nondegeneracy supplies an actual AddGroupNorm, not an assumed norm. Instrument means cone preservation and exact total mass, not assumed contraction. Summed contraction is proved by the positive-decomposition infimum. For a normalized base equal to a nonempty finite convex hull, the discrepancy supremum is attained at a generator. For two valid instruments it is at most two. The finite positive-lift domains of the previous block instantiate this construction. Invertible synthesis gives the inverse-coordinate l1 formula; redundant synthesis gives only an upper bound for any chosen signed coefficients. The adjacent convex-hull unit-ball identity and general LP minimum-attainment assertion are not separately mapped as additional results. These are noncomputable exact real constructions, not a numerical norm minimizer.

Targets: `Komorebi.LSM.BaseNorm.ProbabilityCone`, `Komorebi.LSM.BaseNorm.ProbabilityCone.value`, `Komorebi.LSM.BaseNorm.ProbabilityCone.exists_decomposition`, `Komorebi.LSM.BaseNorm.ProbabilityCone.value_on_cone`, `Komorebi.LSM.BaseNorm.ProbabilityCone.abs_mass_le`, `Komorebi.LSM.BaseNorm.ProbabilityCone.base_compact`, `Komorebi.LSM.BaseNorm.ProbabilityCone.base_norm_laws`, `Komorebi.LSM.BaseNorm.ProbabilityCone.seminorm`, `Komorebi.LSM.BaseNorm.ProbabilityCone.groupNorm`, `Komorebi.LSM.BaseNorm.ProbabilityCone.instrument_contraction`, `Komorebi.LSM.BaseNorm.ProbabilityCone.discrepancy_max_generator`, `Komorebi.LSM.BaseNorm.ProbabilityCone.instrumentError_le_two`, `Komorebi.LSM.BaseNorm.finiteCone`, `Komorebi.LSM.BaseNorm.value_invertible_synthesis`.

## P43. Observation-tree total-variation bound

Status: **complete**.

The record space, chronological history update, unnormalized record states, record probabilities and total mass are constructed explicitly for each finite horizon. The summed base-norm error is proved by induction, not assumed as a recurrence conclusion. The actual finite total variation is half the sum of absolute probability differences. Arbitrary shared history-dependent branch families, and shared deterministic or randomized history-dependent action policies over finite alphabets, are covered. Complete per-action instruments are multiplied by the same policy probabilities in the two compared models. Joint action/observation laws are proved normalized; observation-only laws are their actual aggregation and inherit the bound. The P42 all-state discrepancy supremum supplies the pointwise budget. The bound retains the initial-state discrepancy and sum of per-time budgets, with min(1, ...) clipping. No positive lower branch likelihood or action propensity is assumed. The norm, cone, mass row, observation alphabet and policy are common. No comparison of separately optimized or different policies, infinite-horizon accuracy, continuous observations or learned statistical coverage is claimed.

Targets: `Komorebi.LSM.ObservationTree.Record`, `Komorebi.LSM.ObservationTree.recordState`, `Komorebi.LSM.ObservationTree.record_prior`, `Komorebi.LSM.ObservationTree.record_state_error`, `Komorebi.LSM.ObservationTree.observation_tree_tv_bound`, `Komorebi.LSM.ObservationTree.policy_instrument`, `Komorebi.LSM.ObservationTree.shared_randomized_policy_tv_bound`, `Komorebi.LSM.ObservationTree.shared_policy_observation_tv_bound`, `Komorebi.LSM.ObservationTree.shared_policy_instrumentError_bounds`, `Komorebi.LSM.ObservationTree.deterministicPolicy_prior`, `Komorebi.LSM.FiniteTV.distance_aggregate_le`.

## P44. Sharp event-probability dependence of conditioning

Status: **complete**.

Finite distributions are actual nonnegative normalized real vectors. Event restriction, event mass and normalized conditional distribution are defined by finite sums. The exact restriction/complement budget and event-mass difference bound are proved. For strictly positive event masses in both laws, conditioning has total variation at most min(1, delta/true_event_mass). If delta is strictly below the true event mass, positivity in the comparison law is derived, not assumed. Aggregating conditional records also obeys the bound. The factor is sharp for every 0<r<=1 and 0<=d<=r, using explicit three-state priors with common event mass r, unconditional distance d and conditional distance d/r. A concrete impossible-event expression is not treated as a prior. No bound independent of event mass or general measure-theoretic conditioning is claimed.

Targets: `Komorebi.LSM.FiniteTV.conditional`, `Komorebi.LSM.FiniteTV.restriction_budget`, `Komorebi.LSM.FiniteTV.event_difference_le_distance`, `Komorebi.LSM.FiniteTV.normalized_l1_bound`, `Komorebi.LSM.FiniteTV.comparison_event_positive`, `Komorebi.LSM.FiniteTV.conditioning_tv_bound`, `Komorebi.LSM.FiniteTV.conditioning_tv_bound_of_margin`, `Komorebi.LSM.FiniteTV.conditional_readout_bound`, `Komorebi.LSM.FiniteTV.sharp_conditioning`, `Komorebi.LSM.FiniteTV.sharp_conditional_distance`.

## P45. Rational finite-certificate search

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P46. A rational rank-three model with no polyhedral probability-domain certificate

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P47. Polyhedral approximation of the rotation model

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P48. Sequential confidence accounting for certified proposals

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P49. Conditional learning with an all-horizon probability certificate

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P50. Matrix-embedding probability certificate

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P51. Exact rational matrix witness for the rotation model

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P52. Continuous-observation instrument semantics

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P53. Polynomial Gram certificate for interval observations

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P54. Conditional finite-moment identification

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P55. A valid continuous counterexample to finite-moment identification

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P56. Exact bin coarsening and its posterior

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P57. Exact covariance correction for an averaged congruence

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P58. Positive cell-average approximation

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P59. Continuous-record total-variation bound

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P60. Exact recognition of a fixed certified template

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P61. Conditional continuous realization with a finite domain certificate

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P62. Oriented quadratic probability certificate

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P63. Conditional operator-only ellipsoid discovery

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P64. Valid positive polynomial approximation

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P65. Certified coefficient error and approximation bias

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P66. Time-uniform predictable-residual certificate

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P67. Covered adaptive-action evidence

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P68. Sequential evidence gives a lower error certificate

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P69. Observation-law error without a shared state space

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P70. Separate structural acceptance, approximation control and sequential rejection

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P71. Robust oriented margin

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P72. Boundary fragility under mass preserving perturbations

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P73. Interior repair with an explicit error budget

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P74. A posteriori proposal error

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P75. Rational semicircle and Bernstein certificate

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P76. Coefficient boxes and convex uncertainty

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P77. Conditional search for strict rational curved certificates

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P78. Data-selected geometry with honest coverage

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P79. Certified repair with a retained comparison budget

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P80. Convex repair bracketing

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P81. Time-uniform regression confidence

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P82. Sequential observable-moment operator sets

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P83. Structured curved-domain certificate

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P84. Exact rational outer confidence intervals

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P85. Parameter-to-law error without a state-estimation term

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P86. Uniform marginal and rolling-window stability

Status: **not_formalized**.

No Lean result for this proposition is included in this release.

## P87. Observable structured learning with a covered domain

Status: **not_formalized**.

No Lean result for this proposition is included in this release.
