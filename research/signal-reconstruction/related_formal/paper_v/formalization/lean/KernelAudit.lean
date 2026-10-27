import KomorebiPaperV

/- Checked-target audit harness. Author: Komorebi P. -/


#print axioms KomorebiPaperV.Binary.cutSum_eq_root
#print axioms KomorebiPaperV.Binary.value_le_cost
#print axioms KomorebiPaperV.Binary.best_cost
#print axioms KomorebiPaperV.Binary.best_is_global_minimum
#print axioms KomorebiPaperV.Binary.root_le_envelope
#print axioms KomorebiPaperV.Binary.cut_perturbation
#print axioms KomorebiPaperV.CRT.residue_pair_iff
#print axioms KomorebiPaperV.CRT.residue_mask_factorization
#print axioms KomorebiPaperV.CRT.dyadic_odd_coprime
#print axioms KomorebiPaperV.CRT.dyadic_odd_packet_factorization
#print axioms KomorebiPaperV.CompletePrunings.terminal_exists
#print axioms KomorebiPaperV.CompletePrunings.node_on_terminal
#print axioms KomorebiPaperV.CompletePrunings.selected_stop_iff
#print axioms KomorebiPaperV.CompletePrunings.selected_split_root_false
#print axioms KomorebiPaperV.CompletePrunings.selected_split_down_iff
#print axioms KomorebiPaperV.CompletePrunings.cut_complete
#print axioms KomorebiPaperV.CompletePrunings.ancestor_onPath
#print axioms KomorebiPaperV.CompletePrunings.path_nodes_comparable
#print axioms KomorebiPaperV.CompletePrunings.complete_iff_covering_antichain
#print axioms KomorebiPaperV.CompletePrunings.complete_root_unique
#print axioms KomorebiPaperV.CompletePrunings.complete_child
#print axioms KomorebiPaperV.CompletePrunings.complete_has_cut
#print axioms KomorebiPaperV.CompletePrunings.cut_ext
#print axioms KomorebiPaperV.CompletePrunings.complete_pruning_finite
#print axioms KomorebiPaperV.CompletePrunings.complete_pruning_minimum
#print axioms KomorebiPaperV.CyclicSeries.coeff_cyclicProjector
#print axioms KomorebiPaperV.CyclicSeries.cyclicProjector_idempotent
#print axioms KomorebiPaperV.CyclicSeries.cyclicProjector_orthogonal
#print axioms KomorebiPaperV.CyclicSeries.cyclicProjector_eq_zero_of_residue_ne
#print axioms KomorebiPaperV.CyclicSeries.cyclicProjector_eq_of_mod_eq
#print axioms KomorebiPaperV.CyclicSeries.cyclicProjector_add
#print axioms KomorebiPaperV.CyclicSeries.cyclicProjector_sum
#print axioms KomorebiPaperV.CyclicSeries.sum_cyclicProjector
#print axioms KomorebiPaperV.CyclicSeries.cyclicProjector_product_packet
#print axioms KomorebiPaperV.CyclicSeries.cyclicProjector_product_other
#print axioms KomorebiPaperV.CyclicSeries.cyclic_product_law
#print axioms KomorebiPaperV.CyclicSeries.pure_finite_product
#print axioms KomorebiPaperV.CyclicSeries.project_finite_product
#print axioms KomorebiPaperV.CyclicSeries.sum_fin_projector
#print axioms KomorebiPaperV.CyclicSeries.cyclic_power_law
#print axioms KomorebiPaperV.FIRTransfer.tapEquiv_symm
#print axioms KomorebiPaperV.FIRTransfer.tapIndex_equiv
#print axioms KomorebiPaperV.FIRTransfer.transfer_address
#print axioms KomorebiPaperV.FIRTransfer.fir_reindex
#print axioms KomorebiPaperV.FIRTransfer.sum_pair_fiber
#print axioms KomorebiPaperV.FIRTransfer.fir_polyphase_transfer
#print axioms KomorebiPaperV.FilterBank.act_apply
#print axioms KomorebiPaperV.FilterBank.act_is_fir
#print axioms KomorebiPaperV.FilterBank.act_impulse
#print axioms KomorebiPaperV.FilterBank.act_single
#print axioms KomorebiPaperV.FilterBank.evalZ_apply
#print axioms KomorebiPaperV.FilterBank.filter_transform
#print axioms KomorebiPaperV.FilterBank.bank_mul
#print axioms KomorebiPaperV.FilterBank.bank_impulse
#print axioms KomorebiPaperV.FilterBank.bank_faithful
#print axioms KomorebiPaperV.FilterBank.gain_delay_action
#print axioms KomorebiPaperV.FilterBank.perfect_reconstruction_iff
#print axioms KomorebiPaperV.FilterBank.bank_transform
#print axioms KomorebiPaperV.FilterBank.original_sample_delay
#print axioms KomorebiPaperV.FiniteAdaptive.cutSum_eq_root
#print axioms KomorebiPaperV.FiniteAdaptive.cutSum_eq_identity
#print axioms KomorebiPaperV.FiniteAdaptive.pathHits_one
#print axioms KomorebiPaperV.FiniteAdaptive.arbitrary_objective_minimum
#print axioms KomorebiPaperV.FiniteAdaptive.strict_minimum_positive_gap
#print axioms KomorebiPaperV.FiniteAdaptive.value_le_cost
#print axioms KomorebiPaperV.FiniteAdaptive.best_cost
#print axioms KomorebiPaperV.FiniteAdaptive.best_is_global_minimum
#print axioms KomorebiPaperV.FiniteAdaptive.best_preserves_synthesis
#print axioms KomorebiPaperV.FiniteAdaptive.stop_on_tie
#print axioms KomorebiPaperV.FiniteAdaptive.root_le_envelope
#print axioms KomorebiPaperV.FiniteAdaptive.cost_le_envelope
#print axioms KomorebiPaperV.FiniteAdaptive.envelope_attained
#print axioms KomorebiPaperV.FiniteAdaptive.cut_perturbation
#print axioms KomorebiPaperV.FiniteAdaptive.value_perturbation
#print axioms KomorebiPaperV.FiniteAdaptive.best_unchanged_of_gap
#print axioms KomorebiPaperV.FiniteAdaptive.one_comparison_per_internal_node
#print axioms KomorebiPaperV.FiniteAdaptive.selector_probability
#print axioms KomorebiPaperV.finite_minimum
#print axioms KomorebiPaperV.positive_gap
#print axioms KomorebiPaperV.gap_stability
#print axioms KomorebiPaperV.singleton_minimum
#print axioms KomorebiPaperV.singleton_selection_unchanged
#print axioms KomorebiPaperV.FiniteTransforms.unpair_pair
#print axioms KomorebiPaperV.FiniteTransforms.pair_unpair
#print axioms KomorebiPaperV.FiniteTransforms.flat_synthesis_analysis
#print axioms KomorebiPaperV.FiniteTransforms.flat_analysis_synthesis
#print axioms KomorebiPaperV.FiniteTransforms.unlift_lift_flat
#print axioms KomorebiPaperV.FiniteTransforms.lift_unlift_flat
#print axioms KomorebiPaperV.FiniteTransforms.haar_involution
#print axioms KomorebiPaperV.FiniteTransforms.haar_pair_energy
#print axioms KomorebiPaperV.FiniteTransforms.haar_finite_energy
#print axioms KomorebiPaperV.FiniteTransforms.haar_flat_involution
#print axioms KomorebiPaperV.FiniteTransforms.matrix_eq_of_all_vectors
#print axioms KomorebiPaperV.FiniteTransforms.perfect_reconstruction_matrix_iff
#print axioms KomorebiPaperV.HaarChannels.norm_sq_tsum
#print axioms KomorebiPaperV.HaarChannels.channel_energy
#print axioms KomorebiPaperV.HaarChannels.even_apply
#print axioms KomorebiPaperV.HaarChannels.odd_apply
#print axioms KomorebiPaperV.HaarChannels.interleaved_energy
#print axioms KomorebiPaperV.HaarChannels.haar_energy
#print axioms KomorebiPaperV.HaarChannels.haar_low_samples
#print axioms KomorebiPaperV.HaarChannels.haar_high_samples
#print axioms KomorebiPaperV.HaarHilbert.inverse_low
#print axioms KomorebiPaperV.HaarHilbert.inverse_high
#print axioms KomorebiPaperV.HaarHilbert.energy
#print axioms KomorebiPaperV.HaarHilbert.low_apply
#print axioms KomorebiPaperV.HaarHilbert.high_apply
#print axioms KomorebiPaperV.HilbertPackets.projection_apply
#print axioms KomorebiPaperV.HilbertPackets.projection_norm_le
#print axioms KomorebiPaperV.HilbertPackets.projector_apply
#print axioms KomorebiPaperV.HilbertPackets.projector_idempotent
#print axioms KomorebiPaperV.HilbertPackets.projector_annihilate
#print axioms KomorebiPaperV.HilbertPackets.projector_complete
#print axioms KomorebiPaperV.HilbertPackets.projector_refinement
#print axioms KomorebiPaperV.HilbertPackets.reindex_norm
#print axioms KomorebiPaperV.HilbertPackets.polyphase_apply
#print axioms KomorebiPaperV.HilbertPackets.polyphase_synthesis_analysis
#print axioms KomorebiPaperV.HilbertPackets.polyphase_analysis_synthesis
#print axioms KomorebiPaperV.HilbertPackets.polyphase_energy
#print axioms KomorebiPaperV.HilbertPackets.impulse_expansion
#print axioms KomorebiPaperV.HilbertPackets.projector_symmetric
#print axioms KomorebiPaperV.HilbertPackets.projector_orthogonal
#print axioms KomorebiPaperV.HilbertPackets.impulse_basis_apply
#print axioms KomorebiPaperV.HilbertPackets.impulse_dense_span
#print axioms KomorebiPaperV.HilbertPackets.shift_apply
#print axioms KomorebiPaperV.HilbertPackets.reindex_single
#print axioms KomorebiPaperV.HilbertPackets.shift_impulse
#print axioms KomorebiPaperV.HilbertPackets.residue_projector_refinement
#print axioms KomorebiPaperV.HilbertPackets.shift_generated_dense_span
#print axioms KomorebiPaperV.HilbertPackets.finite_impulse_expansion
#print axioms KomorebiPaperV.IntegerPolyphase.phase_val
#print axioms KomorebiPaperV.IntegerPolyphase.address_phase_quotient
#print axioms KomorebiPaperV.IntegerPolyphase.address_divmod
#print axioms KomorebiPaperV.IntegerPolyphase.phase_address
#print axioms KomorebiPaperV.IntegerPolyphase.quotient_address
#print axioms KomorebiPaperV.IntegerPolyphase.synthesis_analysis
#print axioms KomorebiPaperV.IntegerPolyphase.analysis_synthesis
#print axioms KomorebiPaperV.IntegerPolyphase.channel_delay
#print axioms KomorebiPaperV.IntegerPolyphase.sample_delay
#print axioms KomorebiPaperV.IntegerPolyphase.emod_coarsen
#print axioms KomorebiPaperV.IntegerPolyphase.residue_refinement
#print axioms KomorebiPaperV.known_edge_error
#print axioms KomorebiPaperV.estimated_edge_error
#print axioms KomorebiPaperV.several_known_edges_error
#print axioms KomorebiPaperV.known_edge_norm
#print axioms KomorebiPaperV.several_known_edges_norm
#print axioms KomorebiPaperV.estimated_edge_norm_bound
#print axioms KomorebiPaperV.lifting_synthesis_analysis
#print axioms KomorebiPaperV.lifting_analysis_synthesis
#print axioms KomorebiPaperV.lifting_determinant
#print axioms KomorebiPaperV.lifting_coordinates_roundtrip
#print axioms KomorebiPaperV.MaskPerturbation.jump_measurable
#print axioms KomorebiPaperV.MaskPerturbation.symmetric_difference_norm
#print axioms KomorebiPaperV.MaskPerturbation.indicator_difference_norm
#print axioms KomorebiPaperV.MaskPerturbation.jump_sub_same_set
#print axioms KomorebiPaperV.MaskPerturbation.jump_error_decomposition
#print axioms KomorebiPaperV.MaskPerturbation.finite_p_perturbation
#print axioms KomorebiPaperV.MaskPerturbation.pointwise_sup_bound
#print axioms KomorebiPaperV.MaskPerturbation.infinity_perturbation
#print axioms KomorebiPaperV.MaskPerturbation.full_signal_perturbation
#print axioms KomorebiPaperV.packet_idempotent
#print axioms KomorebiPaperV.packet_annihilate
#print axioms KomorebiPaperV.packet_complete
#print axioms KomorebiPaperV.packet_refinement
#print axioms KomorebiPaperV.address_synthesize_analyze
#print axioms KomorebiPaperV.address_analyze_synthesize
#print axioms KomorebiPaperV.residuePacket_idempotent
#print axioms KomorebiPaperV.residuePacket_complete
#print axioms KomorebiPaperV.PruningAlgorithm.solve_correct
#print axioms KomorebiPaperV.PruningAlgorithm.solve_comparisons
#print axioms KomorebiPaperV.PruningAlgorithm.solve_visits
#print axioms KomorebiPaperV.PruningAlgorithm.solve_additions
#print axioms KomorebiPaperV.PruningAlgorithm.internal_le_nodes
#print axioms KomorebiPaperV.PruningAlgorithm.solve_linear_work
#print axioms KomorebiPaperV.PruningAlgorithm.computed_antichain_optimal
#print axioms KomorebiPaperV.PruningAlgorithm.antichain_probability
#print axioms KomorebiPaperV.PruningSums.node_sum_branch
#print axioms KomorebiPaperV.PruningSums.mem_selectedNodes
#print axioms KomorebiPaperV.PruningSums.cutSum_eq_nodeSum
#print axioms KomorebiPaperV.PruningSums.pruning_nodeSum
#print axioms KomorebiPaperV.PruningSums.antichain_synthesis
#print axioms KomorebiPaperV.PruningSums.packet_projector_synthesis
#print axioms KomorebiPaperV.PruningSums.selected_global_minimum
#print axioms KomorebiPaperV.PruningSums.antichain_perturbation
#print axioms KomorebiPaperV.PruningSums.antichain_envelope_attained
#print axioms KomorebiPaperV.PruningSums.antichain_selector_stable
#print axioms KomorebiPaperV.PruningSums.objective_minimum
#print axioms KomorebiPaperV.PruningSums.objective_positive_gap
#print axioms KomorebiPaperV.PruningSums.objective_stability
#print axioms KomorebiPaperV.PruningSums.singleton_selector
#print axioms KomorebiPaperV.PruningSums.objective_gap_attained
#print axioms KomorebiPaperV.SmithAction.action_mul
#print axioms KomorebiPaperV.SmithAction.action_one
#print axioms KomorebiPaperV.SmithAction.action_scale
#print axioms KomorebiPaperV.SmithAction.action_nonzero
#print axioms KomorebiPaperV.SmithAction.half_turn
#print axioms KomorebiPaperV.SmithAction.half_turn_zero
#print axioms KomorebiPaperV.SmithAction.half_turn_infinity
#print axioms KomorebiPaperV.SmithAction.homogeneous_chart
#print axioms KomorebiPaperV.SmithAction.chart_composition
#print axioms KomorebiPaperV.SmithAction.finite_half_turn
#print axioms KomorebiPaperV.SmithCyclic.omega_ne_zero
#print axioms KomorebiPaperV.SmithCyclic.omega_pow
#print axioms KomorebiPaperV.SmithCyclic.omega_two
#print axioms KomorebiPaperV.SmithCyclic.action_respects_scaling
#print axioms KomorebiPaperV.SmithCyclic.projective_mul
#print axioms KomorebiPaperV.SmithCyclic.projective_one
#print axioms KomorebiPaperV.SmithCyclic.cyclic_zero
#print axioms KomorebiPaperV.SmithCyclic.cyclic_composition
#print axioms KomorebiPaperV.SmithCyclic.cayley_conjugacy
#print axioms KomorebiPaperV.SmithCyclic.cyclic_chart
#print axioms KomorebiPaperV.SmithCyclic.two_phase_swap
#print axioms KomorebiPaperV.SmithCyclic.two_phase_impedance_admittance
#print axioms KomorebiPaperV.WaveletPackets.low_norm_bound
#print axioms KomorebiPaperV.WaveletPackets.high_norm_bound
#print axioms KomorebiPaperV.WaveletPackets.child_energy
#print axioms KomorebiPaperV.WaveletPackets.packet_energy
#print axioms KomorebiPaperV.WaveletPackets.energy_implies_adjoint_identity
#print axioms KomorebiPaperV.WaveletPackets.packet_operator_reconstruction
#print axioms KomorebiPaperV.WaveletPackets.packet_reconstruction
#print axioms KomorebiPaperV.ZTransform.transform_unique
#print axioms KomorebiPaperV.ZTransform.delay_transform
#print axioms KomorebiPaperV.ZTransform.finite_transfer_transform
#print axioms KomorebiPaperV.ZTransform.fir_channel_transform
#print axioms KomorebiPaperV.ZTransform.fir_matrix_transform

open Lean Meta Elab Command

run_cmd do
  let env ← getEnv
  let targets : Array Name := #[
    `KomorebiPaperV.Binary.cutSum_eq_root,
    `KomorebiPaperV.Binary.value_le_cost,
    `KomorebiPaperV.Binary.best_cost,
    `KomorebiPaperV.Binary.best_is_global_minimum,
    `KomorebiPaperV.Binary.root_le_envelope,
    `KomorebiPaperV.Binary.cut_perturbation,
    `KomorebiPaperV.CRT.residue_pair_iff,
    `KomorebiPaperV.CRT.residue_mask_factorization,
    `KomorebiPaperV.CRT.dyadic_odd_coprime,
    `KomorebiPaperV.CRT.dyadic_odd_packet_factorization,
    `KomorebiPaperV.CompletePrunings.terminal_exists,
    `KomorebiPaperV.CompletePrunings.node_on_terminal,
    `KomorebiPaperV.CompletePrunings.selected_stop_iff,
    `KomorebiPaperV.CompletePrunings.selected_split_root_false,
    `KomorebiPaperV.CompletePrunings.selected_split_down_iff,
    `KomorebiPaperV.CompletePrunings.cut_complete,
    `KomorebiPaperV.CompletePrunings.ancestor_onPath,
    `KomorebiPaperV.CompletePrunings.path_nodes_comparable,
    `KomorebiPaperV.CompletePrunings.complete_iff_covering_antichain,
    `KomorebiPaperV.CompletePrunings.complete_root_unique,
    `KomorebiPaperV.CompletePrunings.complete_child,
    `KomorebiPaperV.CompletePrunings.complete_has_cut,
    `KomorebiPaperV.CompletePrunings.cut_ext,
    `KomorebiPaperV.CompletePrunings.complete_pruning_finite,
    `KomorebiPaperV.CompletePrunings.complete_pruning_minimum,
    `KomorebiPaperV.CyclicSeries.coeff_cyclicProjector,
    `KomorebiPaperV.CyclicSeries.cyclicProjector_idempotent,
    `KomorebiPaperV.CyclicSeries.cyclicProjector_orthogonal,
    `KomorebiPaperV.CyclicSeries.cyclicProjector_eq_zero_of_residue_ne,
    `KomorebiPaperV.CyclicSeries.cyclicProjector_eq_of_mod_eq,
    `KomorebiPaperV.CyclicSeries.cyclicProjector_add,
    `KomorebiPaperV.CyclicSeries.cyclicProjector_sum,
    `KomorebiPaperV.CyclicSeries.sum_cyclicProjector,
    `KomorebiPaperV.CyclicSeries.cyclicProjector_product_packet,
    `KomorebiPaperV.CyclicSeries.cyclicProjector_product_other,
    `KomorebiPaperV.CyclicSeries.cyclic_product_law,
    `KomorebiPaperV.CyclicSeries.pure_finite_product,
    `KomorebiPaperV.CyclicSeries.project_finite_product,
    `KomorebiPaperV.CyclicSeries.sum_fin_projector,
    `KomorebiPaperV.CyclicSeries.cyclic_power_law,
    `KomorebiPaperV.FIRTransfer.tapEquiv_symm,
    `KomorebiPaperV.FIRTransfer.tapIndex_equiv,
    `KomorebiPaperV.FIRTransfer.transfer_address,
    `KomorebiPaperV.FIRTransfer.fir_reindex,
    `KomorebiPaperV.FIRTransfer.sum_pair_fiber,
    `KomorebiPaperV.FIRTransfer.fir_polyphase_transfer,
    `KomorebiPaperV.FilterBank.act_apply,
    `KomorebiPaperV.FilterBank.act_is_fir,
    `KomorebiPaperV.FilterBank.act_impulse,
    `KomorebiPaperV.FilterBank.act_single,
    `KomorebiPaperV.FilterBank.evalZ_apply,
    `KomorebiPaperV.FilterBank.filter_transform,
    `KomorebiPaperV.FilterBank.bank_mul,
    `KomorebiPaperV.FilterBank.bank_impulse,
    `KomorebiPaperV.FilterBank.bank_faithful,
    `KomorebiPaperV.FilterBank.gain_delay_action,
    `KomorebiPaperV.FilterBank.perfect_reconstruction_iff,
    `KomorebiPaperV.FilterBank.bank_transform,
    `KomorebiPaperV.FilterBank.original_sample_delay,
    `KomorebiPaperV.FiniteAdaptive.cutSum_eq_root,
    `KomorebiPaperV.FiniteAdaptive.cutSum_eq_identity,
    `KomorebiPaperV.FiniteAdaptive.pathHits_one,
    `KomorebiPaperV.FiniteAdaptive.arbitrary_objective_minimum,
    `KomorebiPaperV.FiniteAdaptive.strict_minimum_positive_gap,
    `KomorebiPaperV.FiniteAdaptive.value_le_cost,
    `KomorebiPaperV.FiniteAdaptive.best_cost,
    `KomorebiPaperV.FiniteAdaptive.best_is_global_minimum,
    `KomorebiPaperV.FiniteAdaptive.best_preserves_synthesis,
    `KomorebiPaperV.FiniteAdaptive.stop_on_tie,
    `KomorebiPaperV.FiniteAdaptive.root_le_envelope,
    `KomorebiPaperV.FiniteAdaptive.cost_le_envelope,
    `KomorebiPaperV.FiniteAdaptive.envelope_attained,
    `KomorebiPaperV.FiniteAdaptive.cut_perturbation,
    `KomorebiPaperV.FiniteAdaptive.value_perturbation,
    `KomorebiPaperV.FiniteAdaptive.best_unchanged_of_gap,
    `KomorebiPaperV.FiniteAdaptive.one_comparison_per_internal_node,
    `KomorebiPaperV.FiniteAdaptive.selector_probability,
    `KomorebiPaperV.finite_minimum,
    `KomorebiPaperV.positive_gap,
    `KomorebiPaperV.gap_stability,
    `KomorebiPaperV.singleton_minimum,
    `KomorebiPaperV.singleton_selection_unchanged,
    `KomorebiPaperV.FiniteTransforms.unpair_pair,
    `KomorebiPaperV.FiniteTransforms.pair_unpair,
    `KomorebiPaperV.FiniteTransforms.flat_synthesis_analysis,
    `KomorebiPaperV.FiniteTransforms.flat_analysis_synthesis,
    `KomorebiPaperV.FiniteTransforms.unlift_lift_flat,
    `KomorebiPaperV.FiniteTransforms.lift_unlift_flat,
    `KomorebiPaperV.FiniteTransforms.haar_involution,
    `KomorebiPaperV.FiniteTransforms.haar_pair_energy,
    `KomorebiPaperV.FiniteTransforms.haar_finite_energy,
    `KomorebiPaperV.FiniteTransforms.haar_flat_involution,
    `KomorebiPaperV.FiniteTransforms.matrix_eq_of_all_vectors,
    `KomorebiPaperV.FiniteTransforms.perfect_reconstruction_matrix_iff,
    `KomorebiPaperV.HaarChannels.norm_sq_tsum,
    `KomorebiPaperV.HaarChannels.channel_energy,
    `KomorebiPaperV.HaarChannels.even_apply,
    `KomorebiPaperV.HaarChannels.odd_apply,
    `KomorebiPaperV.HaarChannels.interleaved_energy,
    `KomorebiPaperV.HaarChannels.haar_energy,
    `KomorebiPaperV.HaarChannels.haar_low_samples,
    `KomorebiPaperV.HaarChannels.haar_high_samples,
    `KomorebiPaperV.HaarHilbert.inverse_low,
    `KomorebiPaperV.HaarHilbert.inverse_high,
    `KomorebiPaperV.HaarHilbert.energy,
    `KomorebiPaperV.HaarHilbert.low_apply,
    `KomorebiPaperV.HaarHilbert.high_apply,
    `KomorebiPaperV.HilbertPackets.projection_apply,
    `KomorebiPaperV.HilbertPackets.projection_norm_le,
    `KomorebiPaperV.HilbertPackets.projector_apply,
    `KomorebiPaperV.HilbertPackets.projector_idempotent,
    `KomorebiPaperV.HilbertPackets.projector_annihilate,
    `KomorebiPaperV.HilbertPackets.projector_complete,
    `KomorebiPaperV.HilbertPackets.projector_refinement,
    `KomorebiPaperV.HilbertPackets.reindex_norm,
    `KomorebiPaperV.HilbertPackets.polyphase_apply,
    `KomorebiPaperV.HilbertPackets.polyphase_synthesis_analysis,
    `KomorebiPaperV.HilbertPackets.polyphase_analysis_synthesis,
    `KomorebiPaperV.HilbertPackets.polyphase_energy,
    `KomorebiPaperV.HilbertPackets.impulse_expansion,
    `KomorebiPaperV.HilbertPackets.projector_symmetric,
    `KomorebiPaperV.HilbertPackets.projector_orthogonal,
    `KomorebiPaperV.HilbertPackets.impulse_basis_apply,
    `KomorebiPaperV.HilbertPackets.impulse_dense_span,
    `KomorebiPaperV.HilbertPackets.shift_apply,
    `KomorebiPaperV.HilbertPackets.reindex_single,
    `KomorebiPaperV.HilbertPackets.shift_impulse,
    `KomorebiPaperV.HilbertPackets.residue_projector_refinement,
    `KomorebiPaperV.HilbertPackets.shift_generated_dense_span,
    `KomorebiPaperV.HilbertPackets.finite_impulse_expansion,
    `KomorebiPaperV.IntegerPolyphase.phase_val,
    `KomorebiPaperV.IntegerPolyphase.address_phase_quotient,
    `KomorebiPaperV.IntegerPolyphase.address_divmod,
    `KomorebiPaperV.IntegerPolyphase.phase_address,
    `KomorebiPaperV.IntegerPolyphase.quotient_address,
    `KomorebiPaperV.IntegerPolyphase.synthesis_analysis,
    `KomorebiPaperV.IntegerPolyphase.analysis_synthesis,
    `KomorebiPaperV.IntegerPolyphase.channel_delay,
    `KomorebiPaperV.IntegerPolyphase.sample_delay,
    `KomorebiPaperV.IntegerPolyphase.emod_coarsen,
    `KomorebiPaperV.IntegerPolyphase.residue_refinement,
    `KomorebiPaperV.known_edge_error,
    `KomorebiPaperV.estimated_edge_error,
    `KomorebiPaperV.several_known_edges_error,
    `KomorebiPaperV.known_edge_norm,
    `KomorebiPaperV.several_known_edges_norm,
    `KomorebiPaperV.estimated_edge_norm_bound,
    `KomorebiPaperV.lifting_synthesis_analysis,
    `KomorebiPaperV.lifting_analysis_synthesis,
    `KomorebiPaperV.lifting_determinant,
    `KomorebiPaperV.lifting_coordinates_roundtrip,
    `KomorebiPaperV.MaskPerturbation.jump_measurable,
    `KomorebiPaperV.MaskPerturbation.symmetric_difference_norm,
    `KomorebiPaperV.MaskPerturbation.indicator_difference_norm,
    `KomorebiPaperV.MaskPerturbation.jump_sub_same_set,
    `KomorebiPaperV.MaskPerturbation.jump_error_decomposition,
    `KomorebiPaperV.MaskPerturbation.finite_p_perturbation,
    `KomorebiPaperV.MaskPerturbation.pointwise_sup_bound,
    `KomorebiPaperV.MaskPerturbation.infinity_perturbation,
    `KomorebiPaperV.MaskPerturbation.full_signal_perturbation,
    `KomorebiPaperV.packet_idempotent,
    `KomorebiPaperV.packet_annihilate,
    `KomorebiPaperV.packet_complete,
    `KomorebiPaperV.packet_refinement,
    `KomorebiPaperV.address_synthesize_analyze,
    `KomorebiPaperV.address_analyze_synthesize,
    `KomorebiPaperV.residuePacket_idempotent,
    `KomorebiPaperV.residuePacket_complete,
    `KomorebiPaperV.PruningAlgorithm.solve_correct,
    `KomorebiPaperV.PruningAlgorithm.solve_comparisons,
    `KomorebiPaperV.PruningAlgorithm.solve_visits,
    `KomorebiPaperV.PruningAlgorithm.solve_additions,
    `KomorebiPaperV.PruningAlgorithm.internal_le_nodes,
    `KomorebiPaperV.PruningAlgorithm.solve_linear_work,
    `KomorebiPaperV.PruningAlgorithm.computed_antichain_optimal,
    `KomorebiPaperV.PruningAlgorithm.antichain_probability,
    `KomorebiPaperV.PruningSums.node_sum_branch,
    `KomorebiPaperV.PruningSums.mem_selectedNodes,
    `KomorebiPaperV.PruningSums.cutSum_eq_nodeSum,
    `KomorebiPaperV.PruningSums.pruning_nodeSum,
    `KomorebiPaperV.PruningSums.antichain_synthesis,
    `KomorebiPaperV.PruningSums.packet_projector_synthesis,
    `KomorebiPaperV.PruningSums.selected_global_minimum,
    `KomorebiPaperV.PruningSums.antichain_perturbation,
    `KomorebiPaperV.PruningSums.antichain_envelope_attained,
    `KomorebiPaperV.PruningSums.antichain_selector_stable,
    `KomorebiPaperV.PruningSums.objective_minimum,
    `KomorebiPaperV.PruningSums.objective_positive_gap,
    `KomorebiPaperV.PruningSums.objective_stability,
    `KomorebiPaperV.PruningSums.singleton_selector,
    `KomorebiPaperV.PruningSums.objective_gap_attained,
    `KomorebiPaperV.SmithAction.action_mul,
    `KomorebiPaperV.SmithAction.action_one,
    `KomorebiPaperV.SmithAction.action_scale,
    `KomorebiPaperV.SmithAction.action_nonzero,
    `KomorebiPaperV.SmithAction.half_turn,
    `KomorebiPaperV.SmithAction.half_turn_zero,
    `KomorebiPaperV.SmithAction.half_turn_infinity,
    `KomorebiPaperV.SmithAction.homogeneous_chart,
    `KomorebiPaperV.SmithAction.chart_composition,
    `KomorebiPaperV.SmithAction.finite_half_turn,
    `KomorebiPaperV.SmithCyclic.omega_ne_zero,
    `KomorebiPaperV.SmithCyclic.omega_pow,
    `KomorebiPaperV.SmithCyclic.omega_two,
    `KomorebiPaperV.SmithCyclic.action_respects_scaling,
    `KomorebiPaperV.SmithCyclic.projective_mul,
    `KomorebiPaperV.SmithCyclic.projective_one,
    `KomorebiPaperV.SmithCyclic.cyclic_zero,
    `KomorebiPaperV.SmithCyclic.cyclic_composition,
    `KomorebiPaperV.SmithCyclic.cayley_conjugacy,
    `KomorebiPaperV.SmithCyclic.cyclic_chart,
    `KomorebiPaperV.SmithCyclic.two_phase_swap,
    `KomorebiPaperV.SmithCyclic.two_phase_impedance_admittance,
    `KomorebiPaperV.WaveletPackets.low_norm_bound,
    `KomorebiPaperV.WaveletPackets.high_norm_bound,
    `KomorebiPaperV.WaveletPackets.child_energy,
    `KomorebiPaperV.WaveletPackets.packet_energy,
    `KomorebiPaperV.WaveletPackets.energy_implies_adjoint_identity,
    `KomorebiPaperV.WaveletPackets.packet_operator_reconstruction,
    `KomorebiPaperV.WaveletPackets.packet_reconstruction,
    `KomorebiPaperV.ZTransform.transform_unique,
    `KomorebiPaperV.ZTransform.delay_transform,
    `KomorebiPaperV.ZTransform.finite_transfer_transform,
    `KomorebiPaperV.ZTransform.fir_channel_transform,
    `KomorebiPaperV.ZTransform.fir_matrix_transform
  ]
  for target in targets do
    match env.find? target with
    | some (.thmInfo _) => pure ()
    | _ => throwError "missing or non-theorem candidate target: {target}"
  let mut audited : Nat := 0
  for (name, info) in env.checked.get.constants.toList do
    if Name.isPrefixOf `KomorebiPaperV name then
      audited := audited + 1
      if info.isUnsafe then
        throwError "unsafe candidate declaration: {name}"
      match info with
      | .axiomInfo _ => throwError "candidate axiom declaration: {name}"
      | .opaqueInfo _ => throwError "candidate opaque declaration: {name}"
      | _ => pure ()
      let axioms ← Lean.collectAxioms name
      for axiomName in axioms do
        unless axiomName == ``propext || axiomName == ``Classical.choice ||
            axiomName == ``Quot.sound do
          throwError "unexpected axiom {axiomName} in {name}"
  logInfo m!"PAPER_V_CANDIDATE_TARGET_AUDIT_PASS: {targets.size} theorem targets; {audited} namespace declarations"
