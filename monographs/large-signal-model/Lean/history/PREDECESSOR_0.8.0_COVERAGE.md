# Coverage — Lean 0.8.0

Frozen Foundations 1.0.0: **30 complete, no partial, 57 unformalized**. The full 87-proposition volume remains the Lean 1.0 target.

Kernel acceptance checks the Lean statements. Their correspondence with the written propositions is separately reviewed. Supporting or example declarations are not counted as additional manuscript propositions.

## P1. Exact realization and consistency — complete

Algebraic realization works on arbitrary types. Norm estimates use continuous linear maps on normed spaces. The divided lower bound explicitly assumes the observation space is nontrivial, so the synthesis norm is positive. No orthogonality is inferred.

Frozen statement/proof SHA-256: `76f7343decf4bd4f6e95facc639c15a89be208ef9986541b608a60353a1a951b`.

- `Komorebi.LSM.Realization.analysis_injective` — `KomorebiLSM/Realization.lean:30` (theorem).

- `Komorebi.LSM.Realization.projector_idempotent` — `KomorebiLSM/Realization.lean:35` (theorem).

- `Komorebi.LSM.Realization.projector_fixed_iff` — `KomorebiLSM/Realization.lean:42` (theorem).

- `Komorebi.LSM.Realization.projector_range` — `KomorebiLSM/Realization.lean:50` (theorem).

- `Komorebi.LSM.analysis_norm_lower` — `KomorebiLSM/Normed.lean:34` (theorem).

- `Komorebi.LSM.synthesis_perturbation_bound` — `KomorebiLSM/Normed.lean:40` (theorem).

## P2. Coherent transport and operator realization — complete

Total operations on consistent coefficient subtypes. A reference chart is explicitly supplied, making the family nonempty. Partial-map admissible-domain extensions mentioned in surrounding prose are not covered.

Frozen statement/proof SHA-256: `bf19d2371abeca3059ff670db877aefe8da0dbe4f801883ce99d3dcd87d894c1`.

- `Komorebi.LSM.Realization.transport_self` — `KomorebiLSM/Realization.lean:75` (theorem).

- `Komorebi.LSM.Realization.transport_comp` — `KomorebiLSM/Realization.lean:78` (theorem).

- `Komorebi.LSM.Realization.realize_natural` — `KomorebiLSM/Realization.lean:86` (theorem).

- `Komorebi.LSM.coherent_family_unique_realization` — `KomorebiLSM/Realization.lean:108` (theorem).

## P3. Complete refinement preserves reconstruction — complete

Finite rooted structural trees with nonempty finite child families, arbitrary mixed-depth selections, and the actual condition of exactly one selected node on each full root-to-leaf path. Local parent=sum(children) gives global operator/signal reconstruction. Local sibling-range orthogonality gives the squared-norm identity over real or complex inner-product spaces. A self-adjoint zero-product lemma supplies that orthogonality from projector assumptions. Antichain completeness and energy conservation are conclusions, not assumed aggregate equations. No general best-basis optimization is included.

Frozen statement/proof SHA-256: `062bbb2bb5f1d910f4ffac708ecc91b94208019276a90f7ae1bd47cccb34563b`.

- `Komorebi.LSM.PacketTree.pathCount_zero_iff` — `KomorebiLSM/PacketTree.lean:73` (theorem).

- `Komorebi.LSM.PacketTree.completeCut_branch` — `KomorebiLSM/PacketTree.lean:107` (theorem).

- `Komorebi.LSM.PacketTree.selectedSum_eq_root` — `KomorebiLSM/PacketTree.lean:135` (theorem).

- `Komorebi.LSM.PacketTree.complete_cut_sum` — `KomorebiLSM/PacketTree.lean:178` (theorem).

- `Komorebi.LSM.PacketTree.complete_cut_operator` — `KomorebiLSM/TreeEnergy.lean:62` (theorem).

- `Komorebi.LSM.PacketTree.complete_cut_reconstruction` — `KomorebiLSM/TreeEnergy.lean:69` (theorem).

- `Komorebi.LSM.PacketTree.conservative_energy` — `KomorebiLSM/TreeEnergy.lean:49` (theorem).

- `Komorebi.LSM.PacketTree.complete_cut_energy` — `KomorebiLSM/TreeEnergy.lean:77` (theorem).

- `Komorebi.LSM.PacketTree.range_orthogonal_of_projector_products` — `KomorebiLSM/TreeEnergy.lean:86` (theorem).

## P4. Transfer reconstruction and refinement — complete

Actual linear maps between possibly different spaces, with explicit finite completeness and intermediate idempotence. The algebra works under weaker assumptions than orthogonality.

Frozen statement/proof SHA-256: `c66769a8d30ee8679436e27ab89249f860e2c5ceef31149a2fbbbbb06f80f40c`.

- `Komorebi.LSM.transfer_reconstruction` — `KomorebiLSM/Transfer.lean:21` (theorem).

- `Komorebi.LSM.transfer_refinement` — `KomorebiLSM/Transfer.lean:32` (theorem).

- `Komorebi.LSM.transfer_composition` — `KomorebiLSM/Transfer.lean:42` (theorem).

## P5. Polynomial packet interactions — complete

All ordered multilinear interactions, including repeated packet indices. The finite polynomial sum retains every cross term. No general nonlinear dictionary discovery is claimed.

Frozen statement/proof SHA-256: `2c77e4ac640d5efb0f5299f93c97dd5549d0549666ad1dc544fc673686eba5bf`.

- `Komorebi.LSM.multilinear_packet_expansion` — `KomorebiLSM/Polynomial.lean:14` (theorem).

- `Komorebi.LSM.polynomial_packet_expansion` — `KomorebiLSM/Polynomial.lean:22` (theorem).

## P6. Exact quotient criterion — complete

Reduced-map existence is constructed from fiber constancy, not assumed. Uniqueness is on the actual image, and action-indexed closure is included.

Frozen statement/proof SHA-256: `aa3bd645880bddcc3fae70218819f1bf71aff8d74995075be3668234a1b7eb9b`.

- `Komorebi.LSM.predictive_closure_iff` — `KomorebiLSM/PredictiveClosure.lean:37` (theorem).

- `Komorebi.LSM.closure_on_image_iff` — `KomorebiLSM/PredictiveClosure.lean:55` (theorem).

- `Komorebi.LSM.controlled_closure_iff` — `KomorebiLSM/PredictiveClosure.lean:86` (theorem).

## P7. Closure defect and compositional defect — complete

Actual linear maps and continuous-linear-map operator norm. Idempotence is explicit, and orthogonality is not needed for the algebraic identity. Closure is not assumed in order to prove its criterion.

Frozen statement/proof SHA-256: `887ae4a7406045d6a74d7463f408dbd1637d03edc4d7f0ad7f19bbb0af040ae1`.

- `Komorebi.LSM.retained_dynamics_split` — `KomorebiLSM/LinearClosure.lean:30` (theorem).

- `Komorebi.LSM.closure_iff_zero_defect` — `KomorebiLSM/LinearClosure.lean:35` (theorem).

- `Komorebi.LSM.composition_defect` — `KomorebiLSM/LinearClosure.lean:50` (theorem).

- `Komorebi.LSM.closure_norm_bound` — `KomorebiLSM/Normed.lean:46` (theorem).

## P8. Minimal linear predictive completion — complete

Known linear dynamics on a finite-dimensional vector space over a field. Iteration adds actual dual-map images of observable row subspaces. Stabilization is proved by strict dimension growth within dim(X)-dim(W0), with persistence after equality and least common invariant extension. Evaluation and arbitrary-basis state maps, linearly independent rows, linear readout H and action transitions B are constructed. Any competing linear summary retaining the initial output and closing under the dynamics contains this completed row space. The subspace/basis construction is noncomputable Lean mathematics, not an implemented numerical row-reduction learner or a proof that new observables are measurable from the original data. The surrounding single-operator Cayley-Hamilton discussion is not an additional coverage claim.

Frozen statement/proof SHA-256: `2e4e47323eab1c70602e8aa5b2992f89077d7b507ba1eeb130cf7c5b7e7ba643`.

- `Komorebi.LSM.invariantSequence_dimension_growth` — `KomorebiLSM/InvariantCompletion.lean:80` (theorem).

- `Komorebi.LSM.invariantSequence_exists_stable` — `KomorebiLSM/InvariantCompletion.lean:94` (theorem).

- `Komorebi.LSM.invariantSequence_stays` — `KomorebiLSM/InvariantCompletion.lean:68` (theorem).

- `Komorebi.LSM.invariantCompletion_isLeast` — `KomorebiLSM/InvariantCompletion.lean:136` (theorem).

- `Komorebi.LSM.predictiveCompletion_stopping_bound` — `KomorebiLSM/PredictiveCompletion.lean:75` (theorem).

- `Komorebi.LSM.predictiveCompletion_isLeast` — `KomorebiLSM/PredictiveCompletion.lean:68` (theorem).

- `Komorebi.LSM.observableState_surjective` — `KomorebiLSM/PredictiveCompletion.lean:48` (theorem).

- `Komorebi.LSM.observableState_closed` — `KomorebiLSM/PredictiveCompletion.lean:34` (theorem).

- `Komorebi.LSM.observableState_retains` — `KomorebiLSM/PredictiveCompletion.lean:42` (theorem).

- `Komorebi.LSM.basisObservation_independent` — `KomorebiLSM/PredictiveCompletion.lean:127` (theorem).

- `Komorebi.LSM.basisReadout_correct` — `KomorebiLSM/PredictiveCompletion.lean:119` (theorem).

- `Komorebi.LSM.basisTransition_correct` — `KomorebiLSM/PredictiveCompletion.lean:110` (theorem).

- `Komorebi.LSM.predictiveCompletion_le_competing_summary` — `KomorebiLSM/PredictiveCompletion.lean:164` (theorem).

- `Komorebi.LSM.predictiveCompletion_coordinate_realization` — `KomorebiLSM/PredictiveCompletion.lean:175` (theorem).

## P9. Coarsest joint finite closure — complete

Finite state space with actual equivalence-relation partitions, known row-stochastic action kernels and positive observation likelihoods. The mandatory initial quotient is nontrivial for semantic minimality. The construction first splits by likelihood vectors, then by aggregate transition probabilities into current blocks. Strict refinements increase quotient cardinality, giving stabilization within card(states)-card(initial likelihood-split quotient) rounds; equality persists. Actual quotient kernels and positive likelihoods are constructed. Their prediction equation holds on all real vectors and their Bayesian equation on probability priors. Semantic JointlyClosed means existence of such stochastic quotient data, not an assumed structural condition. Its equivalence to lumpability plus likelihood constancy uses P12 and yields the unique coarsest admissible refinement. The exact real/setoid construction is noncomputable and does not implement a finite-precision partition learner or identify unknown dynamics.

Frozen statement/proof SHA-256: `c6a8a40a8385333b261319cd103dcfc51844f8d96d05f274335b2cb80da8a072`.

- `Komorebi.LSM.FinitePartitions.strict_refinement_count` — `KomorebiLSM/FinitePartitions.lean:48` (theorem).

- `Komorebi.LSM.FinitePartitions.refinement_stabilizes` — `KomorebiLSM/JointRefinement.lean:110` (theorem).

- `Komorebi.LSM.FinitePartitions.refinementIter_stays_fixed` — `KomorebiLSM/JointRefinement.lean:101` (theorem).

- `Komorebi.LSM.FinitePartitions.stableRefinement_fixed` — `KomorebiLSM/JointRefinement.lean:136` (theorem).

- `Komorebi.LSM.FinitePartitions.jointRefinement_termination` — `KomorebiLSM/JointRefinement.lean:201` (theorem).

- `Komorebi.LSM.FinitePartitions.jointRefinement_coarsest` — `KomorebiLSM/JointRefinement.lean:194` (theorem).

- `Komorebi.LSM.FinitePartitions.quotientKernel_stochastic` — `KomorebiLSM/FiniteStochastic.lean:82` (theorem).

- `Komorebi.LSM.FinitePartitions.quotient_prediction_commutes` — `KomorebiLSM/FiniteStochastic.lean:90` (theorem).

- `Komorebi.LSM.FinitePartitions.quotientLikelihood_pos` — `KomorebiLSM/FiniteStochastic.lean:109` (theorem).

- `Komorebi.LSM.FinitePartitions.quotient_bayes_commutes` — `KomorebiLSM/FiniteStochastic.lean:115` (theorem).

- `Komorebi.LSM.FinitePartitions.joint_closed_iff` — `KomorebiLSM/FiniteStochastic.lean:142` (theorem).

- `Komorebi.LSM.FinitePartitions.jointRefinement_closed` — `KomorebiLSM/FiniteStochastic.lean:164` (theorem).

- `Komorebi.LSM.FinitePartitions.jointlyClosed_refines_completion` — `KomorebiLSM/FiniteStochastic.lean:176` (theorem).

- `Komorebi.LSM.FinitePartitions.coarsest_jointly_closed` — `KomorebiLSM/FiniteStochastic.lean:184` (theorem).

## P10. Exact projected memory and a conditional tail bound — complete

Exact recurrence elimination, lag reindexing, actual projected blocks, continuous-map bridge, same-history geometric truncation bound and initial-term bound. Nonnegative radius/rho and rho<1 are explicit for the bound. H<=t for full-minus-truncated history; the omitted Ico tail also handles an empty interval. No recursively predicted rollout stability is inferred.

Frozen statement/proof SHA-256: `4d93f4e4f95dabfe78bce656ef19ad65414c9e6269e03f216d4fcd481b4c40f3`.

- `Komorebi.LSM.unresolved_solution` — `KomorebiLSM/Memory.lean:18` (theorem).

- `Komorebi.LSM.exact_memory_lags` — `KomorebiLSM/Memory.lean:52` (theorem).

- `Komorebi.LSM.projected_memory` — `KomorebiLSM/Memory.lean:87` (theorem).

- `Komorebi.LSM.continuous_exact_memory_lags` — `KomorebiLSM/MemoryBounds.lean:20` (theorem).

- `Komorebi.LSM.memory_truncation_difference_bound` — `KomorebiLSM/MemoryBounds.lean:93` (theorem).

- `Komorebi.LSM.unresolved_initial_bound` — `KomorebiLSM/MemoryBounds.lean:103` (theorem).

## P11. Ideal statistical benefit of refinement — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `936ce7f988de860f598cb929510b6d59045b248d68aa4e396eaf2e6f683779b7`.

## P12. Bayesian closure and its exact defect — complete

Finite real probability vectors and a surjective map onto the actual coarse blocks. With at least two coarse blocks and strictly positive fine and declared coarse likelihoods, commutation for every normalized nonnegative prior is equivalent to a common positive likelihood scale. Necessity is proved using two-point priors and a cross-block bridge, not assumed as fiber constancy. The one-block exception is proved separately. The effective-likelihood and matrix-defect identities include zero-prior-mass blocks. The fixed-prior algebra assumes nonnegative prior entries and nonzero fine/coarse evidences, so in particular includes nonnegative likelihoods with positive evidences. Totalized real division at zero is not interpreted as a valid posterior. Matrix null direction for a common likelihood scale is also proved.

Frozen statement/proof SHA-256: `c0b41e8b1a327a50e70dda06a8483bcb157a4fc12665e8e9164073be5a2557bd`.

- `Komorebi.LSM.FiniteBayes.cross_ratio_of_commutes` — `KomorebiLSM/BayesianClosure.lean:14` (theorem).

- `Komorebi.LSM.FiniteBayes.bayesian_coarsening_iff` — `KomorebiLSM/BayesianClosure.lean:46` (theorem).

- `Komorebi.LSM.FiniteBayes.likelihood_constant_on_fibers` — `KomorebiLSM/BayesianClosure.lean:61` (theorem).

- `Komorebi.LSM.FiniteBayes.one_block_commutes` — `KomorebiLSM/BayesianClosure.lean:74` (theorem).

- `Komorebi.LSM.FiniteBayes.zero_mass_weight` — `KomorebiLSM/BayesianDefect.lean:16` (theorem).

- `Komorebi.LSM.FiniteBayes.effectiveLikelihood_product` — `KomorebiLSM/BayesianDefect.lean:33` (theorem).

- `Komorebi.LSM.FiniteBayes.effectiveLikelihood_evidence` — `KomorebiLSM/BayesianDefect.lean:41` (theorem).

- `Komorebi.LSM.FiniteBayes.aggregate_posterior_effective` — `KomorebiLSM/BayesianDefect.lean:46` (theorem).

- `Komorebi.LSM.FiniteBayes.bayesian_coarsening_defect` — `KomorebiLSM/BayesianDefect.lean:66` (theorem).

- `Komorebi.LSM.FiniteBayes.bayesian_coarsening_matrix_defect` — `KomorebiLSM/BayesianDefect.lean:89` (theorem).

- `Komorebi.LSM.FiniteBayes.informationLossMatrix_scale_null` — `KomorebiLSM/BayesianDefect.lean:101` (theorem).

## P13. Strong fixed-horizon refinement limit — complete

Strong convergence is proved for actual continuous linear maps with a uniform operator bound. The compression estimate and fixed-power induction are derived. Actual orthogonal subspace projections provide the contractivity premise, for real or complex inner-product spaces. Each horizon is fixed; neither operator-norm convergence nor uniform-in-time accuracy is asserted. The fitted-operator extension retains its independent uniform-bound and strong-error assumptions.

Frozen statement/proof SHA-256: `a8f19c97198414131a107a5702fe8c3e390f40c632518c60b9637bf03862e8d1`.

- `Komorebi.LSM.Stability.compression_error_bound` — `KomorebiLSM/StrongRefinement.lean:52` (theorem).

- `Komorebi.LSM.Stability.compression_uniform_bound` — `KomorebiLSM/StrongRefinement.lean:65` (theorem).

- `Komorebi.LSM.Stability.strong_fixed_powers` — `KomorebiLSM/StrongRefinement.lean:40` (theorem).

- `Komorebi.LSM.Stability.contractive_refinement_fixed_horizon` — `KomorebiLSM/StrongRefinement.lean:89` (theorem).

- `Komorebi.LSM.Stability.strong_fixed_horizon_refinement` — `KomorebiLSM/StrongRefinement.lean:114` (theorem).

- `Komorebi.LSM.Stability.estimated_refinement_fixed_horizon` — `KomorebiLSM/StrongRefinement.lean:99` (theorem).

## P14. Exact causal delay closure — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `e5e317a533371570c9d5d0c8df9c9d869ae355d788f8a18bbbd93242cae6f167`.

## P15. Data-span identification and its boundary — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `0e59a84ad41ee6be9e89295387c9b426fee59055611a42b9566c5d4f3de26f2d`.

## P16. Fixed-space identification bound — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `5ab61ceac0f982f3815931ce25d1bc4cdd9fb90f931274948e2c82e2bf52fab2`.

## P17. Finite-prefix indistinguishability — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `0240b5672fa832c4b97073ef327de42f511ef9b2ae8207e8ad88868248d687dd`.

## P18. Compositional defect propagation — complete

The theorem permits genuinely time-indexed normed state spaces and representations. It defines local residuals from the true transition and approximate step, derives the one-step error, and proves the manuscript suffix-product/sum bound. Lipschitz constants are nonnegative; both true and predicted inputs must lie in the declared domain. Output decoding, constant contraction and exact closure-versus-fit decomposition are separate theorems. An arbitrary changed policy is not automatically covered.

Frozen statement/proof SHA-256: `9e58e6a27781bdd9a0e3e07eb1e210c3f6e02080aa66398d572e96ad250c8d25`.

- `Komorebi.LSM.Stability.errorEnvelope` — `KomorebiLSM/DefectPropagation.lean:14` (def).

- `Komorebi.LSM.Stability.recurrence_product_sum` — `KomorebiLSM/DefectPropagation.lean:37` (theorem).

- `Komorebi.LSM.Stability.local_error_step` — `KomorebiLSM/DefectPropagation.lean:48` (theorem).

- `Komorebi.LSM.Stability.compositional_defect_propagation` — `KomorebiLSM/DefectPropagation.lean:60` (theorem).

- `Komorebi.LSM.Stability.decoder_error_bound` — `KomorebiLSM/DefectPropagation.lean:81` (theorem).

- `Komorebi.LSM.Stability.constant_gain_bound` — `KomorebiLSM/DefectPropagation.lean:87` (theorem).

- `Komorebi.LSM.Stability.linear_defect_split` — `KomorebiLSM/DefectPropagation.lean:103` (theorem).

## P19. Uniform prediction bound for a stable finite-memory truncation — complete

The predictor uses its own recursively generated history, with integer time indices and an explicit initialization window. A strict norm-sum gain below one yields the actual supremum error bound. Coefficient, geometric memory-tail and initialization-forcing budgets are derived and inserted into the recursive theorem. Zero prehistory handles H=0 and t<H without natural-number subtraction artifacts. Retaining the exact forcing removes its contribution. The condition is sufficient, not necessary; failure of this certificate is not proof of instability.

Frozen statement/proof SHA-256: `601722b65bbbb5b64245d34684a13d749bb71b7b9ccf5760151ff4820b40610e`.

- `Komorebi.LSM.Stability.finiteMemory` — `KomorebiLSM/MemoryStability.lean:14` (def).

- `Komorebi.LSM.Stability.finiteMemory_error_bound` — `KomorebiLSM/MemoryStability.lean:31` (theorem).

- `Komorebi.LSM.Stability.invariant_error_radius` — `KomorebiLSM/MemoryStability.lean:52` (theorem).

- `Komorebi.LSM.Stability.finite_memory_prediction_bound` — `KomorebiLSM/MemoryStability.lean:62` (theorem).

- `Komorebi.LSM.Stability.finite_memory_uniform_prediction_bound` — `KomorebiLSM/MemoryStability.lean:98` (theorem).

- `Komorebi.LSM.Stability.initialized_memory_split` — `KomorebiLSM/MemoryApproximation.lean:28` (theorem).

- `Komorebi.LSM.Stability.memory_defect_identity` — `KomorebiLSM/MemoryApproximation.lean:37` (theorem).

- `Komorebi.LSM.Stability.integer_memory_tail_bound` — `KomorebiLSM/MemoryApproximation.lean:58` (theorem).

- `Komorebi.LSM.Stability.memory_approximation_defect_bound` — `KomorebiLSM/MemoryApproximation.lean:77` (theorem).

- `Komorebi.LSM.Stability.discarded_initialized_forcing_bound` — `KomorebiLSM/MemoryApproximation.lean:116` (theorem).

- `Komorebi.LSM.Stability.retained_initialized_forcing_bound` — `KomorebiLSM/MemoryApproximation.lean:128` (theorem).

- `Komorebi.LSM.Stability.certified_memory_truncation` — `KomorebiLSM/MemoryApproximation.lean:132` (theorem).

## P20. Packet-interaction truncation bound — complete

Continuous multilinear maps retain ordered interaction tuples and their multiplicities. Restricted product-of-packet-range norm bounds yield the exact omitted sum and its amplitude majorant. Telescoping yields the retained Lipschitz bound on the declared ball. Contractivity is explicitly derived for actual orthogonal subspace projectors. The finite-dimensional real Hilbert sector is included in a stronger normed-space algebraic theorem. A separate bound is required for an unexpanded nonpolynomial law and for keeping trajectories inside the domain.

Frozen statement/proof SHA-256: `e1230254db019c84be4c8d33c3a20d93fec47b5e0af6031d60878c2cee61285a`.

- `Komorebi.LSM.PacketApproximation.HasPacketBound` — `KomorebiLSM/PacketApproximation.lean:17` (def).

- `Komorebi.LSM.PacketApproximation.full_ordered_expansion` — `KomorebiLSM/PacketApproximation.lean:81` (theorem).

- `Komorebi.LSM.PacketApproximation.omitted_interaction_identity` — `KomorebiLSM/PacketApproximation.lean:94` (theorem).

- `Komorebi.LSM.PacketApproximation.packet_interaction_truncation_bound` — `KomorebiLSM/PacketApproximation.lean:109` (theorem).

- `Komorebi.LSM.PacketApproximation.packet_term_lipschitz` — `KomorebiLSM/PacketApproximation.lean:47` (theorem).

- `Komorebi.LSM.PacketApproximation.retained_polynomial_lipschitz_bound` — `KomorebiLSM/PacketApproximation.lean:127` (theorem).

- `Komorebi.LSM.PacketApproximation.orthogonal_packet_lipschitz_bound` — `KomorebiLSM/ReconciliationHilbert.lean:54` (theorem).

- `Komorebi.LSM.PacketApproximation.additional_model_remainder` — `KomorebiLSM/PacketApproximation.lean:152` (theorem).

## P21. Coherent reconciliation and coordinate-stable transport — complete

Linear atlases act on the actual analysis-range subtype. A genuine normed additive group and normed space are constructed by pulling back synthesis; exact transports are isometries and every Lipschitz constant is equivalent to its object-space counterpart. Repaired maps are consistent and intertwine. Weighted variance and unique minimization are proved for the actual squared Frobenius objective, with a constructed orthonormal matrix coordinate equivalence in finite-dimensional real Hilbert space. The target-error inequality uses actual continuous-operator norms and nonnegative weights summing to one. Agreement is not correctness. The adjacent learned singular-value/pseudoinverse discussion is not claimed as a separate checked theorem.

Frozen statement/proof SHA-256: `74cf07336519dbb8b7dd71b0b744e59faa2fa43caf7b3bf82292b31995f2c13e`.

- `Komorebi.LSM.Reconciliation.LinearAtlas.repaired_consistent` — `KomorebiLSM/AtlasReconciliation.lean:57` (theorem).

- `Komorebi.LSM.Reconciliation.LinearAtlas.repaired_intertwines` — `KomorebiLSM/AtlasReconciliation.lean:60` (theorem).

- `Komorebi.LSM.Reconciliation.reconciledOperator` — `KomorebiLSM/AtlasReconciliation.lean:134` (def).

- `Komorebi.LSM.Reconciliation.coherent_reconciled_family` — `KomorebiLSM/AtlasReconciliation.lean:138` (theorem).

- `Komorebi.LSM.Reconciliation.weighted_variance_identity` — `KomorebiLSM/WeightedReconciliation.lean:40` (theorem).

- `Komorebi.LSM.Reconciliation.weighted_unique_minimizer` — `KomorebiLSM/WeightedReconciliation.lean:65` (theorem).

- `Komorebi.LSM.Reconciliation.frobenius_variance_identity` — `KomorebiLSM/WeightedReconciliation.lean:128` (theorem).

- `Komorebi.LSM.Reconciliation.operator_unique_frobenius_minimizer` — `KomorebiLSM/AtlasReconciliation.lean:164` (theorem).

- `Komorebi.LSM.Reconciliation.orthonormalOperatorCoordinates` — `KomorebiLSM/ReconciliationHilbert.lean:16` (def).

- `Komorebi.LSM.Reconciliation.hilbert_operator_unique_minimizer` — `KomorebiLSM/ReconciliationHilbert.lean:21` (theorem).

- `Komorebi.LSM.Reconciliation.reconciled_target_error` — `KomorebiLSM/ReconciliationHilbert.lean:32` (theorem).

- `Komorebi.LSM.Reconciliation.LinearAtlas.coeffNormed` — `KomorebiLSM/AtlasReconciliation.lean:77` (def).

- `Komorebi.LSM.Reconciliation.LinearAtlas.coeffNormedSpace` — `KomorebiLSM/AtlasReconciliation.lean:80` (def).

- `Komorebi.LSM.Reconciliation.LinearAtlas.pullback_norm` — `KomorebiLSM/AtlasReconciliation.lean:86` (theorem).

- `Komorebi.LSM.Reconciliation.LinearAtlas.transport_isometry` — `KomorebiLSM/AtlasReconciliation.lean:90` (theorem).

- `Komorebi.LSM.Reconciliation.LinearAtlas.represented_lipschitz_iff` — `KomorebiLSM/AtlasReconciliation.lean:103` (theorem).

## P22. The upward-lift obstruction — complete

Existence/uniqueness between actual images, the linear kernel criterion, and the half-distance worst-case norm lower bound. An onto hypothesis in the linear-map construction means that its codomain is the true coarse state space.

Frozen statement/proof SHA-256: `fda19269fbadebb375c3941d4f45a4fea94d96d2695495c44078d3fae0412807`.

- `Komorebi.LSM.factor_on_images_iff` — `KomorebiLSM/PredictiveClosure.lean:70` (theorem).

- `Komorebi.LSM.linear_fiber_iff_kernel` — `KomorebiLSM/LinearRefinement.lean:16` (theorem).

- `Komorebi.LSM.linear_factor_iff_kernel` — `KomorebiLSM/LinearRefinement.lean:26` (theorem).

- `Komorebi.LSM.refinement_worst_case_lower` — `KomorebiLSM/Normed.lean:62` (theorem).

## P23. Exact accounting for an enumerated grammar — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `5b357abff54aecb91d67342572ab41e6524b8af4f91f8fec6a997e13696a08e2`.

## P24. Prior-preserving program refinement — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `a9c9910c50a69b27adc5d9873a73bb9049d7a70d270fad479e7554cec5ab2329`.

## P25. Observationally grounded finite linear realization — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `8e2c14beb97b522e0d03aca51ecb82a5498889056bf7bf8cbe5a60ab6ef32b71`.

## P26. Finite instrument closure — complete

Known instrument on a finite nonempty hidden state type with finitely many outcomes. Actual nonnegative matrices obey exact per-action column-mass conservation. The P8 iteration from the nonzero mass row stabilizes within card(hidden)-1 steps and is proved equal to the span of all chronological word tests. A finite basis is extended/reindexed to place mass literally in its first coordinate. Its observation map has independent rows, is surjective onto the full coordinate space, has precisely the completed row space, and supplies unique reduced transitions. Word probabilities agree for every initial vector; probability and posterior meaning are restricted to realizableBeliefs and positive evidence. Minimality is against every linear summary with linear readouts of all words on every prior. All constructions using arbitrary real bases are noncomputable. This is not observable-data learning, minimum dimension for one fixed initialization, or a general cone-search theorem.

Frozen statement/proof SHA-256: `187b5bfffbd69d68a364ad531a38d892a92d66b6a85fc90003cfaff81ba97286`.

- `Komorebi.LSM.FiniteInstruments.Instrument.instrument_mass` — `KomorebiLSM/FiniteInstrument.lean:140` (theorem).

- `Komorebi.LSM.FiniteInstruments.Instrument.word_probability` — `KomorebiLSM/FiniteInstrument.lean:184` (theorem).

- `Komorebi.LSM.FiniteInstruments.Instrument.observationTreeMass_eq` — `KomorebiLSM/FiniteInstrument.lean:194` (theorem).

- `Komorebi.LSM.FiniteInstruments.instrumentCompletion_eq_wordSpan` — `KomorebiLSM/InstrumentCompletion.lean:68` (theorem).

- `Komorebi.LSM.FiniteInstruments.finite_instrument_stopping_bound` — `KomorebiLSM/InstrumentCompletion.lean:113` (theorem).

- `Komorebi.LSM.invariantSequence_stays` — `KomorebiLSM/InvariantCompletion.lean:68` (theorem).

- `Komorebi.LSM.FiniteInstruments.exists_basis_first` — `KomorebiLSM/InstrumentCoordinates.lean:16` (theorem).

- `Komorebi.LSM.FiniteInstruments.finite_instrument_coordinates` — `KomorebiLSM/InstrumentCoordinates.lean:109` (theorem).

- `Komorebi.LSM.FiniteInstruments.closed_operator_unique` — `KomorebiLSM/InstrumentCoordinates.lean:75` (theorem).

- `Komorebi.LSM.FiniteInstruments.finite_instrument_closure` — `KomorebiLSM/InstrumentRealization.lean:87` (theorem).

- `Komorebi.LSM.FiniteInstruments.completion_le_word_reading_summary` — `KomorebiLSM/InstrumentCompletion.lean:102` (theorem).

- `Komorebi.LSM.FiniteInstruments.reduced_likelihood` — `KomorebiLSM/InstrumentRealization.lean:26` (theorem).

- `Komorebi.LSM.FiniteInstruments.reduced_posterior` — `KomorebiLSM/InstrumentRealization.lean:34` (theorem).

- `Komorebi.LSM.FiniteInstruments.reduced_likelihood_prior` — `KomorebiLSM/InstrumentRealization.lean:52` (theorem).

- `Komorebi.LSM.FiniteInstruments.reduced_posterior_realizable` — `KomorebiLSM/InstrumentRealization.lean:58` (theorem).

- `Komorebi.LSM.FiniteInstruments.reduced_word_probability` — `KomorebiLSM/InstrumentRealization.lean:67` (theorem).

- `Komorebi.LSM.FiniteInstruments.reduced_mass_identity` — `KomorebiLSM/InstrumentRealization.lean:75` (theorem).

## P27. Minimal finite behavior realization — complete

The behavior space is the actual real linear span of history/test columns on finite chronological words. Branch operators are constructed by restriction of test shifts, rather than postulated well-defined coordinate maps. Rank means finite dimension of this full column space, not a sampled matrix rank. Every finite linear realization has at least that dimension. Reachable and observable realizations are explicitly isomorphic, intertwining the initial vector, all operators and mass; the intertwiner is unique. Conditional predictions use the true word/history ratio on positive histories. Nonnegativity and causal normalization are separate supplied word-law assumptions. Infinite-record probability measures and the auxiliary supremum-of-finite-submatrix characterization are not additional claims of this mapping. No model is learned from a finite noisy sample here.

Frozen statement/proof SHA-256: `f5ea2649d85052e89d555963ba921413fd53bf9cb20c28b5fe1fa34b0983c914`.

- `Komorebi.LSM.Behavior.space` — `KomorebiLSM/BehaviorSpace.lean:16` (def).

- `Komorebi.LSM.Behavior.branch` — `KomorebiLSM/BehaviorSpace.lean:47` (def).

- `Komorebi.LSM.Behavior.branch_history` — `KomorebiLSM/BehaviorSpace.lean:53` (theorem).

- `Komorebi.LSM.Behavior.word_probability` — `KomorebiLSM/BehaviorSpace.lean:77` (theorem).

- `Komorebi.LSM.Behavior.test_evaluation` — `KomorebiLSM/BehaviorSpace.lean:83` (theorem).

- `Komorebi.LSM.Behavior.conditional_test` — `KomorebiLSM/BehaviorSpace.lean:92` (theorem).

- `Komorebi.LSM.Behavior.conditional_mass` — `KomorebiLSM/BehaviorSpace.lean:98` (theorem).

- `Komorebi.LSM.Behavior.conditional_equivalence` — `KomorebiLSM/BehaviorSpace.lean:102` (theorem).

- `Komorebi.LSM.Behavior.Realization.toBehavior_surjective` — `KomorebiLSM/BehaviorSpace.lean:171` (theorem).

- `Komorebi.LSM.Behavior.Realization.behavior_dimension_le` — `KomorebiLSM/BehaviorSpace.lean:191` (theorem).

- `Komorebi.LSM.Behavior.Realization.behavior_finite` — `KomorebiLSM/BehaviorMinimality.lean:35` (theorem).

- `Komorebi.LSM.Behavior.canonical_reachable` — `KomorebiLSM/BehaviorMinimality.lean:15` (theorem).

- `Komorebi.LSM.Behavior.canonical_observable` — `KomorebiLSM/BehaviorMinimality.lean:22` (theorem).

- `Komorebi.LSM.Behavior.Realization.minimal_dimension` — `KomorebiLSM/BehaviorMinimality.lean:97` (theorem).

- `Komorebi.LSM.Behavior.Realization.minimal_realizations_similar` — `KomorebiLSM/BehaviorMinimality.lean:103` (theorem).

- `Komorebi.LSM.Behavior.Realization.intertwiner_unique` — `KomorebiLSM/BehaviorMinimality.lean:72` (theorem).

- `Komorebi.LSM.Behavior.CausalLaw.canonical_conditional_probability` — `KomorebiLSM/BehaviorProbability.lean:67` (theorem).

## P28. Observable table reconstruction — complete

Finite core coordinates are actual selected test evaluations. An invertible square population matrix gives surjectivity and a lower rank bound; an explicit global finite behavior-rank upper bound supplies injectivity and full coverage. The formula G_s H^{-1} is an actual matrix expression using the correct inverse side. It yields the full chronological state, mass and probability for every word, a reachable observable model and minimal dimension against every finite linear realization. A distinguished selected empty test is the literal mass coordinate (index zero in Fin r). Normalized updates require positive evidence for probabilistic interpretation. Finding the core, deriving an unknown global rank bound and statistical estimation of table entries are not claimed. Noncomputable inverse/space constructions do not amount to an executed numerical data learner.

Frozen statement/proof SHA-256: `01167ef48df9e89abde083660149bcef9e8c2917e2f0dd4a041bd308385e52f6`.

- `Komorebi.LSM.Behavior.core` — `KomorebiLSM/ObservableCore.lean:20` (def).

- `Komorebi.LSM.Behavior.shiftedCore` — `KomorebiLSM/ObservableCore.lean:23` (def).

- `Komorebi.LSM.Behavior.evaluate_surjective` — `KomorebiLSM/ObservableCore.lean:53` (theorem).

- `Komorebi.LSM.Behavior.core_rank_exact` — `KomorebiLSM/ObservableCore.lean:62` (theorem).

- `Komorebi.LSM.Behavior.evaluate_bijective` — `KomorebiLSM/ObservableCore.lean:70` (theorem).

- `Komorebi.LSM.Behavior.synthesize_surjective` — `KomorebiLSM/ObservableCore.lean:80` (theorem).

- `Komorebi.LSM.Behavior.coreEquiv` — `KomorebiLSM/ObservableCore.lean:91` (def).

- `Komorebi.LSM.Behavior.reconstructed` — `KomorebiLSM/ObservableCore.lean:97` (def).

- `Komorebi.LSM.Behavior.reconstructed_intertwines` — `KomorebiLSM/ObservableCore.lean:101` (theorem).

- `Komorebi.LSM.Behavior.reconstructed_unique` — `KomorebiLSM/ObservableCore.lean:117` (theorem).

- `Komorebi.LSM.Behavior.reconstructed_state` — `KomorebiLSM/ObservableCore.lean:131` (theorem).

- `Komorebi.LSM.Behavior.reconstructed_probability` — `KomorebiLSM/ObservableCore.lean:153` (theorem).

- `Komorebi.LSM.Behavior.reconstructed_conditional_update` — `KomorebiLSM/ObservableCore.lean:163` (theorem).

- `Komorebi.LSM.Behavior.reconstructed_likelihood_pos` — `KomorebiLSM/ObservableRealization.lean:107` (theorem).

- `Komorebi.LSM.Behavior.tableModel` — `KomorebiLSM/ObservableRealization.lean:11` (def).

- `Komorebi.LSM.Behavior.tableModel_minimal` — `KomorebiLSM/ObservableRealization.lean:21` (theorem).

- `Komorebi.LSM.Behavior.observable_table_reconstruction` — `KomorebiLSM/ObservableRealization.lean:118` (theorem).

## P29. Canonical probability cone — complete

The actual canonical behavior space is the submodule span of history/test functions from P27. Causal consistency and nonnegative behavior are supplied as CausalLaw. The all-test cone is defined by every finite test, not by finitely sampled trajectories. Cone closure under addition and nonnegative scaling, convexity, pointedness, generation by history columns, branch invariance, strict positive mass, the per-action mass identity, normalized posterior closure, and test-coordinate bounds are proved. Closedness and compact normalized-base results use the actual inherited Hausdorff function-space topology and an explicit finite-dimensional behavior-space assumption. Compactness follows through a proved closed embedding into the compact all-test unit cube; boundedness of the desired base is not assumed. The selected empty test is the literal mass-one coordinate. No finite inequality description or learned cone algorithm is claimed for the general canonical space.

Frozen statement/proof SHA-256: `6e2cade2ebf2d2164b0756852c1bdde75fe0d1993a8c7317307614502630c291`.

- `Komorebi.LSM.TestDomains.allTests_closed` — `KomorebiLSM/TestTopology.lean:15` (theorem).

- `Komorebi.LSM.TestDomains.testLevel_closed` — `KomorebiLSM/TestTopology.lean:23` (theorem).

- `Komorebi.LSM.TestDomains.base_closed` — `KomorebiLSM/TestTopology.lean:31` (theorem).

- `Komorebi.LSM.TestDomains.observe_closedEmbedding` — `KomorebiLSM/TestTopology.lean:36` (theorem).

- `Komorebi.LSM.TestDomains.base_compact` — `KomorebiLSM/TestTopology.lean:47` (theorem).

- `Komorebi.LSM.Behavior.probabilityCone` — `KomorebiLSM/CanonicalCone.lean:13` (def).

- `Komorebi.LSM.Behavior.probabilityBase` — `KomorebiLSM/CanonicalCone.lean:16` (def).

- `Komorebi.LSM.Behavior.probabilityCone_eq_tests` — `KomorebiLSM/CanonicalCone.lean:19` (theorem).

- `Komorebi.LSM.Behavior.probabilityBase_eq_tests` — `KomorebiLSM/CanonicalCone.lean:25` (theorem).

- `Komorebi.LSM.Behavior.probability_observe_injective` — `KomorebiLSM/CanonicalCone.lean:30` (theorem).

- `Komorebi.LSM.Behavior.probabilityCone_convex` — `KomorebiLSM/CanonicalCone.lean:38` (theorem).

- `Komorebi.LSM.Behavior.probabilityCone_pointed` — `KomorebiLSM/CanonicalCone.lean:42` (theorem).

- `Komorebi.LSM.Behavior.probabilityCone_closed` — `KomorebiLSM/CanonicalCone.lean:47` (theorem).

- `Komorebi.LSM.Behavior.probabilityCone_invariant` — `KomorebiLSM/CanonicalCone.lean:52` (theorem).

- `Komorebi.LSM.Behavior.probabilityCone_smul` — `KomorebiLSM/CanonicalCone.lean:56` (theorem).

- `Komorebi.LSM.Behavior.probabilityCone_add` — `KomorebiLSM/CanonicalCone.lean:61` (theorem).

- `Komorebi.LSM.Behavior.history_mem_probabilityCone` — `KomorebiLSM/CanonicalCone.lean:67` (theorem).

- `Komorebi.LSM.Behavior.probabilityCone_spans` — `KomorebiLSM/CanonicalCone.lean:71` (theorem).

- `Komorebi.LSM.Behavior.probabilityCone_strict_mass` — `KomorebiLSM/CanonicalCone.lean:79` (theorem).

- `Komorebi.LSM.Behavior.probabilityBase_test_bounds` — `KomorebiLSM/CanonicalCone.lean:85` (theorem).

- `Komorebi.LSM.Behavior.probabilityBase_compact` — `KomorebiLSM/CanonicalCone.lean:92` (theorem).

- `Komorebi.LSM.Behavior.probabilityBase_convex` — `KomorebiLSM/CanonicalCone.lean:98` (theorem).

- `Komorebi.LSM.Behavior.initial_mem_probabilityBase` — `KomorebiLSM/CanonicalCone.lean:102` (theorem).

- `Komorebi.LSM.Behavior.probabilityBase_posterior` — `KomorebiLSM/CanonicalCone.lean:106` (theorem).

- `Komorebi.LSM.Behavior.probabilityBase_core_bounds` — `KomorebiLSM/CanonicalCone.lean:113` (theorem).

- `Komorebi.LSM.Behavior.canonical_probability_cone` — `KomorebiLSM/CanonicalCone.lean:121` (theorem).

## P30. Positive packet decomposition and its boundary — complete

The mixture theorem works over real modules, a cone closed under nonnegative scaling, a strictly positive mass functional on nonzero cone elements, and complete linear packet maps preserving that cone. Weight nonnegativity, their unit sum, normalized component membership and mass, vanishing zero-weight components and the positive-weight finite mixture identity are proved separately. The orthant result uses actual finite real matrices: preservation of all nonnegative vectors is equivalent to entrywise nonnegativity; completeness forces zero off-diagonals; idempotence forces diagonal entries 0 or 1; every coordinate has exactly one selected packet. Reconstruction or orthogonality alone does not imply positivity. This theorem does not supply a learned cone or formalize the compactness theorem of P29.

Frozen statement/proof SHA-256: `c194fa41de56114ad1c7daa9ac348ac1281f798384752100e0474f59cb8ebf5a`.

- `Komorebi.LSM.PositivePackets.StrictMass` — `KomorebiLSM/PositivePackets.lean:14` (def).

- `Komorebi.LSM.PositivePackets.mass_nonnegative` — `KomorebiLSM/PositivePackets.lean:17` (theorem).

- `Komorebi.LSM.PositivePackets.mass_zero_iff` — `KomorebiLSM/PositivePackets.lean:23` (theorem).

- `Komorebi.LSM.PositivePackets.packet_weights_sum` — `KomorebiLSM/PositivePackets.lean:31` (theorem).

- `Komorebi.LSM.PositivePackets.normalized_packet` — `KomorebiLSM/PositivePackets.lean:41` (theorem).

- `Komorebi.LSM.PositivePackets.positive_packet_mixture` — `KomorebiLSM/PositivePackets.lean:50` (theorem).

- `Komorebi.LSM.PositivePackets.orthant_preserving_iff` — `KomorebiLSM/PositivePackets.lean:93` (theorem).

- `Komorebi.LSM.PositivePackets.off_diagonal_zero` — `KomorebiLSM/PositivePackets.lean:109` (theorem).

- `Komorebi.LSM.PositivePackets.matrix_eq_diagonal` — `KomorebiLSM/PositivePackets.lean:121` (theorem).

- `Komorebi.LSM.PositivePackets.diagonal_boolean` — `KomorebiLSM/PositivePackets.lean:131` (theorem).

- `Komorebi.LSM.PositivePackets.unique_selected_packet` — `KomorebiLSM/PositivePackets.lean:145` (theorem).

- `Komorebi.LSM.PositivePackets.positive_idempotents_are_coordinate_selections` — `KomorebiLSM/PositivePackets.lean:173` (theorem).

## P31. Missing-intervention nonidentifiability — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `7965f7973adcfb95a08c2666958f0f757615b3471ed5f199d0da18208f76efaf`.

## P32. Finite-table rank separation and subspace stability — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `062726b8b6d1f04db91faae632eec1d9a0de55eccf12835b3c6591317a5223a7`.

## P33. Noisy core-block realization — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `1c3ae63305b5161e872165fb56b7aa0d281e67dab900566dec2ef0e5bcf595e5`.

## P34. Normalization-aware filtering stability — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `5e426f13fc4b2e8860cebf15a4d97110d1db38875587f5abcf4b7402343b21fb`.

## P35. Reset-experiment probability certificate — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `01a8f88a029cf053dcf73c123d853235b084758b937c4170988c72a061a41d80`.

## P36. Exact normalized closure defect — complete

The vector identity is on real coordinate functions with an actual linear summary and mass-preservation law; the fine and proposed branch evidences are strictly positive. The separate likelihood identity holds without division. The oblique map is an actual rank-one correction of the identity. The converse requires a nonzero entrywise-nonnegative fine branch and agreement of likelihoods AND normalized posteriors on every strictly positive prior. Explicit uniform and perturbed-uniform priors prove that this interior family spans the fine space. No equality of unnormalized operators is assumed in that converse. A one-state instrument counterexample proves that posterior agreement alone is insufficient. The idempotent-projector specialization gives the omitted-to-retained block. The statements do not certify a fitted probability domain or control statistical error.

Frozen statement/proof SHA-256: `976769b1769f848a767529224ac5fb2d7e4d3715d7f32562ffb8c2823a3997fe`.

- `Komorebi.LSM.FiniteInstruments.oblique` — `KomorebiLSM/NormalizedDefect.lean:15` (def).

- `Komorebi.LSM.FiniteInstruments.oblique_null` — `KomorebiLSM/NormalizedDefect.lean:21` (theorem).

- `Komorebi.LSM.FiniteInstruments.oblique_mass_zero` — `KomorebiLSM/NormalizedDefect.lean:25` (theorem).

- `Komorebi.LSM.FiniteInstruments.oblique_idempotent` — `KomorebiLSM/NormalizedDefect.lean:29` (theorem).

- `Komorebi.LSM.FiniteInstruments.likelihood_defect` — `KomorebiLSM/NormalizedDefect.lean:52` (theorem).

- `Komorebi.LSM.FiniteInstruments.normalized_closure_defect` — `KomorebiLSM/NormalizedDefect.lean:74` (theorem).

- `Komorebi.LSM.FiniteInstruments.nonnegative_branch_mass_pos` — `KomorebiLSM/PositivePriors.lean:60` (theorem).

- `Komorebi.LSM.FiniteInstruments.linearMap_eq_of_strict_priors` — `KomorebiLSM/PositivePriors.lean:52` (theorem).

- `Komorebi.LSM.FiniteInstruments.closure_of_likelihood_and_posterior` — `KomorebiLSM/NormalizedDefect.lean:95` (theorem).

- `Komorebi.LSM.FiniteInstruments.closureDefect_projected` — `KomorebiLSM/NormalizedDefect.lean:120` (theorem).

- `Komorebi.LSM.Block4Examples.posterior_alone_does_not_imply_closure` — `KomorebiLSM/Block4Examples.lean:316` (theorem).

- `Komorebi.LSM.Block4Examples.example_satisfies_general_defect` — `KomorebiLSM/Block4Examples.lean:269` (theorem).

## P37. Conditional observation-based stochastic completion — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `ad11b707cf1434589b9687806428ff44d7f0a2a2dbd7f6cdd9f166cbe44f6754`.

## P38. Test-cone hierarchy and a finite stopping certificate — complete

The finite-level cones are actual inequalities for all words of length at most h. Their successor/preimage identity, antitonicity, intersection, largest invariant-set property and exact adjacent-level stopping implication are proved. A noncomputable finite set of linear halfspaces is constructed at every level for finite symbol types, establishing the polyhedral description rather than assuming it. An observability row-span hypothesis is connected to injectivity of all-test evaluation. With the explicit per-action mass law, injectivity yields pointedness and strictly positive mass; membership of reachable vectors and their full span yields generation. Finite stabilization is sufficient, not asserted for every family. A one-step acceptance test is not treated as invariance. The cone may be improper without the stated observability/reachability conditions.

Frozen statement/proof SHA-256: `758558a711f4538ea4aecce64aa36bc59507a845e14ecce6dab81c34123d9efd`.

- `Komorebi.LSM.TestDomains.observe` — `KomorebiLSM/TestCones.lean:12` (def).

- `Komorebi.LSM.TestDomains.observe_apply` — `KomorebiLSM/TestCones.lean:15` (theorem).

- `Komorebi.LSM.TestDomains.testLevel` — `KomorebiLSM/TestCones.lean:18` (def).

- `Komorebi.LSM.TestDomains.allTests` — `KomorebiLSM/TestCones.lean:21` (def).

- `Komorebi.LSM.TestDomains.base` — `KomorebiLSM/TestCones.lean:24` (def).

- `Komorebi.LSM.TestDomains.allTests_zero` — `KomorebiLSM/TestCones.lean:27` (theorem).

- `Komorebi.LSM.TestDomains.allTests_add` — `KomorebiLSM/TestCones.lean:30` (theorem).

- `Komorebi.LSM.TestDomains.allTests_smul` — `KomorebiLSM/TestCones.lean:36` (theorem).

- `Komorebi.LSM.TestDomains.allTests_convex` — `KomorebiLSM/TestCones.lean:42` (theorem).

- `Komorebi.LSM.TestDomains.base_convex` — `KomorebiLSM/TestCones.lean:47` (theorem).

- `Komorebi.LSM.TestDomains.allTests_invariant` — `KomorebiLSM/TestCones.lean:53` (theorem).

- `Komorebi.LSM.TestDomains.allTests_word` — `KomorebiLSM/TestCones.lean:58` (theorem).

- `Komorebi.LSM.TestDomains.allTests_mass_nonneg` — `KomorebiLSM/TestCones.lean:64` (theorem).

- `Komorebi.LSM.TestDomains.testLevel_zero` — `KomorebiLSM/TestCones.lean:67` (theorem).

- `Komorebi.LSM.TestDomains.testLevel_succ` — `KomorebiLSM/TestCones.lean:78` (theorem).

- `Komorebi.LSM.TestDomains.testLevel_antitone` — `KomorebiLSM/TestCones.lean:94` (theorem).

- `Komorebi.LSM.TestDomains.allTests_eq_inter` — `KomorebiLSM/TestCones.lean:99` (theorem).

- `Komorebi.LSM.TestDomains.allTests_greatest` — `KomorebiLSM/TestCones.lean:108` (theorem).

- `Komorebi.LSM.TestDomains.testLevel_stopping` — `KomorebiLSM/TestCones.lean:119` (theorem).

- `Komorebi.LSM.TestDomains.allTests_pointed` — `KomorebiLSM/TestCones.lean:132` (theorem).

- `Komorebi.LSM.TestDomains.allTests_spans` — `KomorebiLSM/TestCones.lean:143` (theorem).

- `Komorebi.LSM.TestDomains.test_sum_next` — `KomorebiLSM/TestCones.lean:160` (theorem).

- `Komorebi.LSM.TestDomains.test_next_le` — `KomorebiLSM/TestCones.lean:166` (theorem).

- `Komorebi.LSM.TestDomains.test_extension_le` — `KomorebiLSM/TestCones.lean:171` (theorem).

- `Komorebi.LSM.TestDomains.test_le_mass` — `KomorebiLSM/TestCones.lean:180` (theorem).

- `Komorebi.LSM.TestDomains.allTests_strict_mass` — `KomorebiLSM/TestCones.lean:185` (theorem).

- `Komorebi.LSM.TestDomains.base_test_bounds` — `KomorebiLSM/TestCones.lean:197` (theorem).

- `Komorebi.LSM.TestDomains.base_posterior` — `KomorebiLSM/TestCones.lean:204` (theorem).

- `Komorebi.LSM.TestDomains.finite_test_halfspaces` — `KomorebiLSM/FiniteTestRows.lean:12` (theorem).

- `Komorebi.LSM.TestDomains.finite_stopping_certificate` — `KomorebiLSM/FiniteTestRows.lean:42` (theorem).

- `Komorebi.LSM.TestDomains.observe_injective_of_row_span` — `KomorebiLSM/FiniteTestRows.lean:50` (theorem).

## P39. Finite positive-lift certificate — complete

The cone is the actual image of nonnegative finite coefficient vectors under V. Normalization is lambda composed with V equals the coefficient-sum functional; surjectivity is the full-row-rank condition when generation is asserted. Cone closedness, convexity, pointedness, strict mass and generation are derived, including for redundant generators. The normalized base is proved equal to the image of the finite probability simplex and to the actual convex hull of the generators, and is compact. Invariance is equivalent to existence of an entrywise nonnegative matrix A with B V = V A, with the necessity witness constructed from the generator images by classical choice. Lifted mass conservation, the actual hidden instrument, intertwining for every chronological word and word probabilities follow from the finite witness and a nonnegative normalized initial coefficient vector. No unique lift is claimed for redundant V. The adjacent Farkas dual-certificate discussion is not claimed as an additional formal theorem.

Frozen statement/proof SHA-256: `b6602e059d0daad1af0b571c63b6500e193a9db81ef2fa9f414b8a04073787e4`.

- `Komorebi.LSM.PositiveLift.hull` — `KomorebiLSM/PositiveLift.lean:12` (def).

- `Komorebi.LSM.PositiveLift.generator` — `KomorebiLSM/PositiveLift.lean:15` (def).

- `Komorebi.LSM.PositiveLift.normalizedHull` — `KomorebiLSM/PositiveLift.lean:17` (def).

- `Komorebi.LSM.PositiveLift.normalized_mass` — `KomorebiLSM/PositiveLift.lean:21` (theorem).

- `Komorebi.LSM.PositiveLift.mass_generator` — `KomorebiLSM/PositiveLift.lean:26` (theorem).

- `Komorebi.LSM.PositiveLift.generator_mem` — `KomorebiLSM/PositiveLift.lean:30` (theorem).

- `Komorebi.LSM.PositiveLift.hull_zero` — `KomorebiLSM/PositiveLift.lean:34` (theorem).

- `Komorebi.LSM.PositiveLift.hull_add` — `KomorebiLSM/PositiveLift.lean:38` (theorem).

- `Komorebi.LSM.PositiveLift.hull_smul` — `KomorebiLSM/PositiveLift.lean:45` (theorem).

- `Komorebi.LSM.PositiveLift.hull_convex` — `KomorebiLSM/PositiveLift.lean:51` (theorem).

- `Komorebi.LSM.PositiveLift.hull_mass_nonneg` — `KomorebiLSM/PositiveLift.lean:56` (theorem).

- `Komorebi.LSM.PositiveLift.hull_mass_zero` — `KomorebiLSM/PositiveLift.lean:63` (theorem).

- `Komorebi.LSM.PositiveLift.hull_strict_mass` — `KomorebiLSM/PositiveLift.lean:73` (theorem).

- `Komorebi.LSM.PositiveLift.hull_pointed` — `KomorebiLSM/PositiveLift.lean:81` (theorem).

- `Komorebi.LSM.PositiveLift.synthesis_sum` — `KomorebiLSM/PositiveLift.lean:89` (theorem).

- `Komorebi.LSM.PositiveLift.hull_spans` — `KomorebiLSM/PositiveLift.lean:94` (theorem).

- `Komorebi.LSM.PositiveLift.normalizedHull_eq_prior_image` — `KomorebiLSM/PositiveLift.lean:104` (theorem).

- `Komorebi.LSM.PositiveLift.invariant_iff_generators` — `KomorebiLSM/PositiveLift.lean:114` (theorem).

- `Komorebi.LSM.PositiveLift.positive_lift_iff` — `KomorebiLSM/PositiveLift.lean:133` (theorem).

- `Komorebi.LSM.PositiveLift.lifted_mass` — `KomorebiLSM/PositiveLift.lean:168` (theorem).

- `Komorebi.LSM.PositiveLift.liftedInstrument` — `KomorebiLSM/PositiveLift.lean:184` (def).

- `Komorebi.LSM.PositiveLift.lifted_word` — `KomorebiLSM/PositiveLift.lean:190` (theorem).

- `Komorebi.LSM.PositiveLift.lifted_word_probability` — `KomorebiLSM/PositiveLift.lean:196` (theorem).

- `Komorebi.LSM.PositiveLift.finite_positive_lift_certificate` — `KomorebiLSM/PositiveLift.lean:202` (theorem).

- `Komorebi.LSM.PositiveLift.prior_box` — `KomorebiLSM/PositiveLiftTopology.lean:18` (theorem).

- `Komorebi.LSM.PositiveLift.priors_compact` — `KomorebiLSM/PositiveLiftTopology.lean:26` (theorem).

- `Komorebi.LSM.PositiveLift.normalizedHull_compact` — `KomorebiLSM/PositiveLiftTopology.lean:38` (theorem).

- `Komorebi.LSM.PositiveLift.normalizedHull_convex` — `KomorebiLSM/PositiveLiftTopology.lean:44` (theorem).

- `Komorebi.LSM.PositiveLift.hull_closed` — `KomorebiLSM/PositiveLiftTopology.lean:51` (theorem).

- `Komorebi.LSM.PositiveLift.normalizedHull_eq_convexHull` — `KomorebiLSM/PositiveLiftTopology.lean:96` (theorem).

## P40. Robust finite-domain certificate — complete

The uncertainty set is the actual convex hull of complete operator families with shared convex coefficients across all branches. Nonnegative vertex lifts and exact mass conservation imply every family in that hull preserves the fixed generator cone and mass. Explicit mixed lifts are constructed. History-dependent selection of a family is handled through an actual adaptive word recursion and finite observation-tree mass recursion under any deterministic history-based action policy. Cone membership, nonnegative word likelihood, the unit upper bound and tree normalization are proved for arbitrary finite horizons. A separate theorem uses actual continuous linear operators, their operator norms and a complete facet description of the same cone to prove the stated norm-ball margin implies perturbed invariance and existence of a positive lift. The normed statement specializes to Euclidean coordinates. Exact mass constraints remain separate; independently mixing branches is not inferred to conserve mass. No statistical coverage of the uncertainty hull is asserted.

Frozen statement/proof SHA-256: `d2c4bca591ad7fe07772548627d638f731d73021685e2aee0dec6950115b2406`.

- `Komorebi.LSM.RobustDomains.ValidFamily` — `KomorebiLSM/RobustFiniteDomains.lean:11` (def).

- `Komorebi.LSM.RobustDomains.validFamily_convex` — `KomorebiLSM/RobustFiniteDomains.lean:15` (theorem).

- `Komorebi.LSM.RobustDomains.robust_convex_hull` — `KomorebiLSM/RobustFiniteDomains.lean:27` (theorem).

- `Komorebi.LSM.RobustDomains.robust_positive_lift` — `KomorebiLSM/RobustFiniteDomains.lean:36` (theorem).

- `Komorebi.LSM.RobustDomains.mixed_lift` — `KomorebiLSM/RobustFiniteDomains.lean:49` (theorem).

- `Komorebi.LSM.RobustDomains.mixed_entries_nonnegative` — `KomorebiLSM/RobustFiniteDomains.lean:61` (theorem).

- `Komorebi.LSM.RobustDomains.adaptiveWord` — `KomorebiLSM/RobustFiniteDomains.lean:69` (def).

- `Komorebi.LSM.RobustDomains.adaptiveWord_in_cone` — `KomorebiLSM/RobustFiniteDomains.lean:74` (theorem).

- `Komorebi.LSM.RobustDomains.adaptiveWord_nonnegative` — `KomorebiLSM/RobustFiniteDomains.lean:82` (theorem).

- `Komorebi.LSM.RobustDomains.adaptiveWord_mass_le` — `KomorebiLSM/RobustFiniteDomains.lean:88` (theorem).

- `Komorebi.LSM.RobustDomains.adaptiveTreeMass` — `KomorebiLSM/RobustFiniteDomains.lean:100` (def).

- `Komorebi.LSM.RobustDomains.adaptiveTreeMass_eq` — `KomorebiLSM/RobustFiniteDomains.lean:105` (theorem).

- `Komorebi.LSM.RobustDomains.facet_error_bound` — `KomorebiLSM/FacetRobustness.lean:12` (theorem).

- `Komorebi.LSM.RobustDomains.facet_margin_robust` — `KomorebiLSM/FacetRobustness.lean:26` (theorem).

- `Komorebi.LSM.RobustDomains.facet_norm_ball_invariant` — `KomorebiLSM/FacetRobustness.lean:32` (theorem).

- `Komorebi.LSM.RobustDomains.facet_norm_ball_lift` — `KomorebiLSM/FacetRobustness.lean:44` (theorem).

## P41. Certified correction and its error budget — complete

A FeasiblePoint records the actual finite nonnegative-lift, intertwining, per-action mass and initial-prior constraints. Internal family validity, normalized initial membership and every finite-word probability are derived from those constraints and normalized generators, not included as assumed conclusions. An actual true member of a confidence set with a fixed-domain witness constructs a feasible point in that set. The two-center bound norm(corrected-truth) <= 2 epsilon is proved for an arbitrary seminormed additive group, hence applies both to continuous linear operators and to initial states in their specified norms. No optimizer, empirical confidence set, or implication from one feasible point to coverage/validity of every point is supplied. Fixed-domain witness construction is classical and noncomputable. The adjacent explicit mixing-repair formula is outside this numbered proposition's mapping.

Frozen statement/proof SHA-256: `058e3939e5d1aada065576d5514f9676772fe30be58c4e1bb85182019e581cde`.

- `Komorebi.LSM.CertifiedCorrection.FeasiblePoint` — `KomorebiLSM/CertifiedCorrection.lean:13` (structure).

- `Komorebi.LSM.CertifiedCorrection.FeasiblePoint.valid_family` — `KomorebiLSM/CertifiedCorrection.lean:28` (theorem).

- `Komorebi.LSM.CertifiedCorrection.FeasiblePoint.initial_mem` — `KomorebiLSM/CertifiedCorrection.lean:33` (theorem).

- `Komorebi.LSM.CertifiedCorrection.FeasiblePoint.all_word_probabilities` — `KomorebiLSM/CertifiedCorrection.lean:37` (theorem).

- `Komorebi.LSM.CertifiedCorrection.feasible_of_certified_member` — `KomorebiLSM/CertifiedCorrection.lean:46` (theorem).

- `Komorebi.LSM.CertifiedCorrection.two_center_error` — `KomorebiLSM/CertifiedCorrection.lean:58` (theorem).

## P42. Instrument contraction before normalization — complete

The base norm is the actual infimum over decompositions x=u-v with u,v in the declared closed, generating cone. Nonnegative mass, existence of decompositions, the infimum bounds, triangle inequality, negation invariance and absolute scalar homogeneity are proved. In finite-dimensional real normed spaces, compactness of the normalized base and a bound by the ambient norm are derived from cone closedness and strict mass; nondegeneracy supplies an actual AddGroupNorm, not an assumed norm. Instrument means cone preservation and exact total mass, not assumed contraction. Summed contraction is proved by the positive-decomposition infimum. For a normalized base equal to a nonempty finite convex hull, the discrepancy supremum is attained at a generator. For two valid instruments it is at most two. The finite positive-lift domains of the previous block instantiate this construction. Invertible synthesis gives the inverse-coordinate l1 formula; redundant synthesis gives only an upper bound for any chosen signed coefficients. The adjacent convex-hull unit-ball identity and general LP minimum-attainment assertion are not separately mapped as additional results. These are noncomputable exact real constructions, not a numerical norm minimizer.

Frozen statement/proof SHA-256: `9613286a6e6b301f504ccfbf8d72d0cc221b4ac30a7e13cccf54ff0f88a43f5f`.

- `Komorebi.LSM.BaseNorm.ProbabilityCone` — `KomorebiLSM/BaseNorm.lean:16` (structure).

- `Komorebi.LSM.BaseNorm.ProbabilityCone.value` — `KomorebiLSM/BaseNorm.lean:68` (def).

- `Komorebi.LSM.BaseNorm.ProbabilityCone.exists_decomposition` — `KomorebiLSM/BaseNorm.lean:48` (theorem).

- `Komorebi.LSM.BaseNorm.ProbabilityCone.value_on_cone` — `KomorebiLSM/BaseNorm.lean:101` (theorem).

- `Komorebi.LSM.BaseNorm.ProbabilityCone.abs_mass_le` — `KomorebiLSM/BaseNorm.lean:95` (theorem).

- `Komorebi.LSM.BaseNorm.ProbabilityCone.base_compact` — `KomorebiLSM/BaseNormTopology.lean:49` (theorem).

- `Komorebi.LSM.BaseNorm.ProbabilityCone.base_norm_laws` — `KomorebiLSM/BaseNormTopology.lean:90` (theorem).

- `Komorebi.LSM.BaseNorm.ProbabilityCone.seminorm` — `KomorebiLSM/BaseNormTopology.lean:98` (def).

- `Komorebi.LSM.BaseNorm.ProbabilityCone.groupNorm` — `KomorebiLSM/BaseNormTopology.lean:106` (def).

- `Komorebi.LSM.BaseNorm.ProbabilityCone.instrument_contraction` — `KomorebiLSM/InstrumentContraction.lean:17` (theorem).

- `Komorebi.LSM.BaseNorm.ProbabilityCone.discrepancy_max_generator` — `KomorebiLSM/InstrumentContraction.lean:66` (theorem).

- `Komorebi.LSM.BaseNorm.ProbabilityCone.instrumentError_le_two` — `KomorebiLSM/InstrumentContraction.lean:98` (theorem).

- `Komorebi.LSM.BaseNorm.finiteCone` — `KomorebiLSM/BaseNormModels.lean:14` (def).

- `Komorebi.LSM.BaseNorm.value_invertible_synthesis` — `KomorebiLSM/BaseNormModels.lean:81` (theorem).

## P43. Observation-tree total-variation bound — complete

The record space, chronological history update, unnormalized record states, record probabilities and total mass are constructed explicitly for each finite horizon. The summed base-norm error is proved by induction, not assumed as a recurrence conclusion. The actual finite total variation is half the sum of absolute probability differences. Arbitrary shared history-dependent branch families, and shared deterministic or randomized history-dependent action policies over finite alphabets, are covered. Complete per-action instruments are multiplied by the same policy probabilities in the two compared models. Joint action/observation laws are proved normalized; observation-only laws are their actual aggregation and inherit the bound. The P42 all-state discrepancy supremum supplies the pointwise budget. The bound retains the initial-state discrepancy and sum of per-time budgets, with min(1, ...) clipping. No positive lower branch likelihood or action propensity is assumed. The norm, cone, mass row, observation alphabet and policy are common. No comparison of separately optimized or different policies, infinite-horizon accuracy, continuous observations or learned statistical coverage is claimed.

Frozen statement/proof SHA-256: `1230487bbd42abce674d8fbb4f92e51e4db8faab953a80341efbf226e3d5b4b5`.

- `Komorebi.LSM.ObservationTree.Record` — `KomorebiLSM/ObservationTree.lean:13` (def).

- `Komorebi.LSM.ObservationTree.recordState` — `KomorebiLSM/ObservationTree.lean:56` (def).

- `Komorebi.LSM.ObservationTree.record_prior` — `KomorebiLSM/ObservationTree.lean:84` (theorem).

- `Komorebi.LSM.ObservationTree.record_state_error` — `KomorebiLSM/ObservationTree.lean:105` (theorem).

- `Komorebi.LSM.ObservationTree.observation_tree_tv_bound` — `KomorebiLSM/ObservationTree.lean:146` (theorem).

- `Komorebi.LSM.ObservationTree.policy_instrument` — `KomorebiLSM/PolicyComparison.lean:16` (theorem).

- `Komorebi.LSM.ObservationTree.shared_randomized_policy_tv_bound` — `KomorebiLSM/PolicyComparison.lean:55` (theorem).

- `Komorebi.LSM.ObservationTree.shared_policy_observation_tv_bound` — `KomorebiLSM/PolicyComparison.lean:76` (theorem).

- `Komorebi.LSM.ObservationTree.shared_policy_instrumentError_bounds` — `KomorebiLSM/PolicyComparison.lean:91` (theorem).

- `Komorebi.LSM.ObservationTree.deterministicPolicy_prior` — `KomorebiLSM/PolicyComparison.lean:117` (theorem).

- `Komorebi.LSM.FiniteTV.distance_aggregate_le` — `KomorebiLSM/FiniteTV.lean:156` (theorem).

## P44. Sharp event-probability dependence of conditioning — complete

Finite distributions are actual nonnegative normalized real vectors. Event restriction, event mass and normalized conditional distribution are defined by finite sums. The exact restriction/complement budget and event-mass difference bound are proved. For strictly positive event masses in both laws, conditioning has total variation at most min(1, delta/true_event_mass). If delta is strictly below the true event mass, positivity in the comparison law is derived, not assumed. Aggregating conditional records also obeys the bound. The factor is sharp for every 0<r<=1 and 0<=d<=r, using explicit three-state priors with common event mass r, unconditional distance d and conditional distance d/r. A concrete impossible-event expression is not treated as a prior. No bound independent of event mass or general measure-theoretic conditioning is claimed.

Frozen statement/proof SHA-256: `5126c411701c18f6d49bce85a591cfd6332b5cee9beda682c5c2d69c8f40ae93`.

- `Komorebi.LSM.FiniteTV.conditional` — `KomorebiLSM/FiniteTV.lean:63` (def).

- `Komorebi.LSM.FiniteTV.restriction_budget` — `KomorebiLSM/FiniteTV.lean:110` (theorem).

- `Komorebi.LSM.FiniteTV.event_difference_le_distance` — `KomorebiLSM/FiniteTV.lean:122` (theorem).

- `Komorebi.LSM.FiniteTV.normalized_l1_bound` — `KomorebiLSM/Conditioning.lean:12` (theorem).

- `Komorebi.LSM.FiniteTV.comparison_event_positive` — `KomorebiLSM/Conditioning.lean:29` (theorem).

- `Komorebi.LSM.FiniteTV.conditioning_tv_bound` — `KomorebiLSM/Conditioning.lean:37` (theorem).

- `Komorebi.LSM.FiniteTV.conditioning_tv_bound_of_margin` — `KomorebiLSM/Conditioning.lean:55` (theorem).

- `Komorebi.LSM.FiniteTV.conditional_readout_bound` — `KomorebiLSM/Conditioning.lean:64` (theorem).

- `Komorebi.LSM.FiniteTV.sharp_conditioning` — `KomorebiLSM/SharpConditioning.lean:60` (theorem).

- `Komorebi.LSM.FiniteTV.sharp_conditional_distance` — `KomorebiLSM/SharpConditioning.lean:51` (theorem).

## P45. Rational finite-certificate search — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `f734c5aafdad96d95c219d435fc85a770d9c4438fc12db7e7d6a3cfa6210a28f`.

## P46. A rational rank-three model with no polyhedral probability-domain certificate — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `d53e8c13817296dab51d773257f0aae9c1678f219bfec274c8354ae8823b5370`.

## P47. Polyhedral approximation of the rotation model — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `f2c388fb949f3237ae43c724cd794e931b1d44ced28d84a5c377d151a916950a`.

## P48. Sequential confidence accounting for certified proposals — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `f16aabb5d998aef5ec2c189cc8cd6d174b95b175b925399933006e3f548570f2`.

## P49. Conditional learning with an all-horizon probability certificate — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `0b14f32e01ce62bab8054528981bf6ea84b4c31549e9d2fd4e333979c70c911a`.

## P50. Matrix-embedding probability certificate — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `bbc28e0df502a01e25624a089884536f6889a99dc84a0cf68e943edce7bfe1a8`.

## P51. Exact rational matrix witness for the rotation model — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `530bc59cd2a6a58904e7fc39627f944195a963e84eea8a5ce79941b4b4e98335`.

## P52. Continuous-observation instrument semantics — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `cb2e01fbed2cbb12ad2996b6513fe05171f5e6691906b52897398f6c3ce474bd`.

## P53. Polynomial Gram certificate for interval observations — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `6230138c01ffc9fd5cb356d943114e3f8bb9364d92e5f7f8b7f180c4b2a456ef`.

## P54. Conditional finite-moment identification — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `407f620fca943d3a6700dc6c8bf1b806db138388c7ebfd5a4e4c066c528cd723`.

## P55. A valid continuous counterexample to finite-moment identification — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `bb5d6788daf2a26bd9c291f67b6e8ac701a5f70a2a438aa6e9e53cfa5089e735`.

## P56. Exact bin coarsening and its posterior — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `69cb151f0a0d446eacfebdebea155d59d66eff445b56a5c19bdef05e92571303`.

## P57. Exact covariance correction for an averaged congruence — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `378882c33f903ebb4b01addfca970761ca5462290a71c7fc2ecd5bef4ff76699`.

## P58. Positive cell-average approximation — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `68534642fabd1f39ab0d97816b6da176f887f5f1c34b697398c3cd3b5cef1e74`.

## P59. Continuous-record total-variation bound — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `c825c2167f27397f4d6ba9ab30934d1f67ed95d94182c16089907f71150ebaa7`.

## P60. Exact recognition of a fixed certified template — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `ec96ab9b3c5a9301ca64a15f71276c805e42bb16ad87a4490148823d52d41513`.

## P61. Conditional continuous realization with a finite domain certificate — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `e881b8924f8eef1982a553272f269d059688d010d59702646af4001f98671f0e`.

## P62. Oriented quadratic probability certificate — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `b01290ddf413f6a716d28aaceb2aec24ed99ed2c8e2e25d8a6a6d15bf42b2b39`.

## P63. Conditional operator-only ellipsoid discovery — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `2f2f44eaa305f5c77ee428e79c468ca6965cb7132c15377089a56adfda5eafee`.

## P64. Valid positive polynomial approximation — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `f56b5431fcf43c3282e37092318181042ea297cc81eae10308f185d712eb61de`.

## P65. Certified coefficient error and approximation bias — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `180a67265ad2383b336068b092f4ba7150f03485ecf56ed06668a189db1961fb`.

## P66. Time-uniform predictable-residual certificate — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `a226cd3f063813d8b15b7be8043a0f1ec955e72e2c11a035cc2611de9e2aaadf`.

## P67. Covered adaptive-action evidence — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `e0335b90979eae4ff2012365c74a10b8bbc35b635816b5486697887487c2b5a5`.

## P68. Sequential evidence gives a lower error certificate — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `a29843467d26a0e261abcea51b4d3269fd0062ec0e0490960271c4370bfca24a`.

## P69. Observation-law error without a shared state space — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `fa81620d074234747cdd19079f56cb4a901aa40ae038827e6e7b5f937e9625b1`.

## P70. Separate structural acceptance, approximation control and sequential rejection — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `58d0605bd0ee96f5b3734546a73954f9c22d73fb68e89fd29c944939639b6083`.

## P71. Robust oriented margin — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `3537031a1132bc49a8b6bece4c92120293281c728b9190fcc7d959a073381a22`.

## P72. Boundary fragility under mass preserving perturbations — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `633bd3af2e9d960bf5aa36df9a24473cff84370e4e5e923227b6ff967adc5dc2`.

## P73. Interior repair with an explicit error budget — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `c12af82ef53cd595ce2616e4a6b06642437e2f8b9b9edea40f173bfaed557806`.

## P74. A posteriori proposal error — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `2aaf4d9ded559ccee57dc238772f867b089bdcbe1378c529dd48ee556088503a`.

## P75. Rational semicircle and Bernstein certificate — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `550ef051f5503b575f7f537f7220fa10a9a1c6e70d845cfe8522cb81ef1dee66`.

## P76. Coefficient boxes and convex uncertainty — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `1fc372ccf6617691509c05c376bf415a8161479119246e974f903ab28df6cc87`.

## P77. Conditional search for strict rational curved certificates — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `ffa40c40b8f21f17a14b5ea84e52a5526f59c49ed17d829cc16b9f34b628257c`.

## P78. Data-selected geometry with honest coverage — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `d68e66bd49b03cd446da824a63e6bd5e089657c84ee86a5c4a510ad77dc09d9b`.

## P79. Certified repair with a retained comparison budget — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `eab6b091d9f93e84c124e5157d19519de70f5e1cfbfe19b7dd6b31510df43345`.

## P80. Convex repair bracketing — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `d25e9dbec98faf98f68cad2346fc304f3cb4cd6d74d6ed94a376b7a3b7d6a5c7`.

## P81. Time-uniform regression confidence — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `dfdf7759ff515806122f126744c08b66364b490d53f578af8e08311731f6ff42`.

## P82. Sequential observable-moment operator sets — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `b8945507c3a01bea18d673e38cec42c9b4f78af92c183dd96c1e4fe404de2d4e`.

## P83. Structured curved-domain certificate — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `eb12c55a9603d10a5da6d472d50930ce119a2b42fcf904e5732e5e2c8623a329`.

## P84. Exact rational outer confidence intervals — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `745279864b56e86e265a8f4bd07c7d79a284132065b21f878a99444c827ad8ed`.

## P85. Parameter-to-law error without a state-estimation term — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `e42a75f2032d8d7e1fa45ef01265b0f1a53f96ec7d2b05975f585b22e06ce43a`.

## P86. Uniform marginal and rolling-window stability — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `c850bf7c9ebd9b5bbbb6d229426318a9e806ce8229eeacc65a5e8f1a8bf4f80b`.

## P87. Observable structured learning with a covered domain — not_formalized

No Lean result for this proposition is included in this release.

Frozen statement/proof SHA-256: `02c397029b27cc1e1635903711b9e2f970ed86bac5dfcdc652bd0f9fedf41b85`.
