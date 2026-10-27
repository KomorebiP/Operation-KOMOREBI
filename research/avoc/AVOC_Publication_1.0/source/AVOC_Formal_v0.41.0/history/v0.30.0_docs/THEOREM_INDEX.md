# AVOC v0.30.0 — declaration inventory

1548 inherited + 64 new = 1612 named theorem/lemma declarations.
Counts include helpers and examples, not independent discoveries.


## `AVOC/AffineCodec.lean`

- `Komorebi.AVOC.Affine.Codec.load_source` — line 90
- `Komorebi.AVOC.Affine.Codec.load_semantics` — line 93

## `AVOC/AffineExamples.lean`

- `Komorebi.AVOC.Affine.Examples.pipeline_coefficients` — line 19
- `Komorebi.AVOC.Affine.Examples.pipeline_all_inputs` — line 21
- `Komorebi.AVOC.Affine.Examples.pipeline_three_probes` — line 25
- `Komorebi.AVOC.Affine.Examples.pipeline_costs` — line 27
- `Komorebi.AVOC.Affine.Examples.pipeline_three_calls` — line 30
- `Komorebi.AVOC.Affine.Examples.bottleneck_costs` — line 36
- `Komorebi.AVOC.Affine.Examples.bottleneck_not_selected` — line 38
- `Komorebi.AVOC.Affine.Examples.bottleneck_never_worth` — line 43
- `Komorebi.AVOC.Affine.Examples.basis_without_zero_insufficient` — line 49
- `Komorebi.AVOC.Affine.Examples.affine_domain_is_essential` — line 56
- `Komorebi.AVOC.Affine.Examples.zero_input_is_offset` — line 61
- `Komorebi.AVOC.Affine.Examples.zero_output_equivalent` — line 65

## `AVOC/AffineFactorChoice.lean`

- `Komorebi.AVOC.Affine.Factorization.cheaper_left` — line 13
- `Komorebi.AVOC.Affine.Factorization.cheaper_right` — line 18
- `Komorebi.AVOC.Affine.Factorization.cheaper_member` — line 23
- `Komorebi.AVOC.Affine.Factorization.cheaper_correct` — line 26
- `Komorebi.AVOC.Affine.Factorization.choose_correct` — line 38
- `Komorebi.AVOC.Affine.Factorization.choose_le_original` — line 46
- `Komorebi.AVOC.Affine.Factorization.choose_le_dense` — line 50
- `Komorebi.AVOC.Affine.Factorization.choose_le_factor` — line 54
- `Komorebi.AVOC.Affine.Factorization.choose_le_any_two_stage` — line 58
- `Komorebi.AVOC.Affine.Factorization.choose_menu_member` — line 66
- `Komorebi.AVOC.Affine.Factorization.amortization_iff` — line 90
- `Komorebi.AVOC.Affine.Factorization.campaign_never_refunds` — line 101
- `Komorebi.AVOC.Affine.Factorization.no_savings_no_positive_net` — line 106
- `Komorebi.AVOC.Affine.Factorization.admission_iff` — line 117
- `Komorebi.AVOC.Affine.Factorization.admitted_budget_and_semantics` — line 131
- `Komorebi.AVOC.Affine.Factorization.insufficient_credit` — line 138

## `AVOC/AffineFactorCodec.lean`

- `Komorebi.AVOC.Affine.FactorCodec.decoded_certificate_sound` — line 36

## `AVOC/AffineFactorExamples.lean`

- `Komorebi.AVOC.Affine.FactorExamples.rankOne_check` — line 16
- `Komorebi.AVOC.Affine.FactorExamples.rankOne_valid` — line 18
- `Komorebi.AVOC.Affine.FactorExamples.rankOne_rank` — line 20
- `Komorebi.AVOC.Affine.FactorExamples.rankOne_minimum_width` — line 22
- `Komorebi.AVOC.Affine.FactorExamples.rankOne_execution_costs` — line 29
- `Komorebi.AVOC.Affine.FactorExamples.rankOne_checker_charge` — line 33
- `Komorebi.AVOC.Affine.FactorExamples.rankOne_amortization` — line 35
- `Komorebi.AVOC.Affine.FactorExamples.redundant_is_exact` — line 52
- `Komorebi.AVOC.Affine.FactorExamples.redundant_lower_rejected` — line 56
- `Komorebi.AVOC.Affine.FactorExamples.wrong_bias_rejected` — line 62
- `Komorebi.AVOC.Affine.FactorExamples.identity_check` — line 65
- `Komorebi.AVOC.Affine.FactorExamples.identity_keeps_zero_cost` — line 70
- `Komorebi.AVOC.Affine.FactorExamples.full_rank_factor_can_lose` — line 73
- `Komorebi.AVOC.Affine.FactorExamples.constant_check` — line 78
- `Komorebi.AVOC.Affine.FactorExamples.constant_zero_width` — line 80
- `Komorebi.AVOC.Affine.FactorExamples.constant_costs` — line 83

## `AVOC/AffineFactorization.lean`

- `Komorebi.AVOC.Affine.Factorization.plan_cost` — line 23
- `Komorebi.AVOC.Affine.Factorization.plan_coefficients` — line 26
- `Komorebi.AVOC.Affine.Factorization.check_iff` — line 38
- `Komorebi.AVOC.Affine.Factorization.valid_execution` — line 43
- `Komorebi.AVOC.Affine.Factorization.lower_witness_rank` — line 47
- `Komorebi.AVOC.Affine.Factorization.any_factor_rank_upper` — line 54
- `Komorebi.AVOC.Affine.Factorization.valid_rank_exact` — line 58
- `Komorebi.AVOC.Affine.Factorization.width_minimal` — line 66
- `Komorebi.AVOC.Affine.Factorization.factorCost_mono` — line 74
- `Komorebi.AVOC.Affine.Factorization.factorCost_strict` — line 81
- `Komorebi.AVOC.Affine.Factorization.two_stage_cost_minimal` — line 90
- `Komorebi.AVOC.Affine.Factorization.checked_optimal` — line 96
- `Komorebi.AVOC.Affine.Factorization.validation_sound` — line 117
- `Komorebi.AVOC.Affine.Factorization.validation_complete` — line 120
- `Komorebi.AVOC.Affine.Factorization.altered_semantics_rejected` — line 124
- `Komorebi.AVOC.Affine.Factorization.false_lower_witness_rejected` — line 130

## `AVOC/AffineFusion.lean`

- `Komorebi.AVOC.Affine.coefficients_correct` — line 31
- `Komorebi.AVOC.Affine.fuse_correct` — line 34
- `Komorebi.AVOC.Affine.fused_execution_cost` — line 37
- `Komorebi.AVOC.Affine.chooseNoSlower_correct` — line 43
- `Komorebi.AVOC.Affine.chooseNoSlower_cost` — line 49
- `Komorebi.AVOC.Affine.worthwhile_certificate` — line 68
- `Komorebi.AVOC.Affine.bottleneck_fusion_cost_increases` — line 75
- `Komorebi.AVOC.Affine.beneficial_fusion_costs` — line 79
- `Komorebi.AVOC.Affine.beneficial_fusion_break_even` — line 82
- `Komorebi.AVOC.Affine.beneficial_fusion_strict_gain` — line 86
- `Komorebi.AVOC.Affine.zero_lower_valid` — line 91
- `Komorebi.AVOC.Affine.identity_global_minimum` — line 101

## `AVOC/AffineReuse.lean`

- `Komorebi.AVOC.Affine.Reuse.retarget_width` — line 22
- `Komorebi.AVOC.Affine.Reuse.retarget_first` — line 25
- `Komorebi.AVOC.Affine.Reuse.retarget_linear` — line 28
- `Komorebi.AVOC.Affine.Reuse.retarget_offset` — line 32
- `Komorebi.AVOC.Affine.Reuse.retarget_valid` — line 39
- `Komorebi.AVOC.Affine.Reuse.retarget_overwrite` — line 50
- `Komorebi.AVOC.Affine.Reuse.retarget_plan_cost` — line 53
- `Komorebi.AVOC.Affine.Reuse.importFor_iff` — line 65
- `Komorebi.AVOC.Affine.Reuse.import_invalid_rejected` — line 80
- `Komorebi.AVOC.Affine.Reuse.import_wrong_linear_rejected` — line 86
- `Komorebi.AVOC.Affine.Reuse.imported_valid` — line 90
- `Komorebi.AVOC.Affine.Reuse.imported_width` — line 93
- `Komorebi.AVOC.Affine.Reuse.reused_choice_correct` — line 103
- `Komorebi.AVOC.Affine.Reuse.reused_minimal_width` — line 109
- `Komorebi.AVOC.Affine.Reuse.checked_width_unique` — line 116
- `Komorebi.AVOC.Affine.Reuse.cheaper_cost` — line 122
- `Komorebi.AVOC.Affine.Reuse.choose_cost_exact` — line 129
- `Komorebi.AVOC.Affine.Reuse.same_signature_search_cannot_lower_factor_cost` — line 136

## `AVOC/AffineReuseCodec.lean`

- `Komorebi.AVOC.Affine.ReuseCodec.import_budget` — line 30
- `Komorebi.AVOC.Affine.ReuseCodec.imported_sound` — line 39
- `Komorebi.AVOC.Affine.ReuseCodec.imported_identity` — line 47
- `Komorebi.AVOC.Affine.ReuseCodec.imported_budget_conservation` — line 56
- `Komorebi.AVOC.Affine.ReuseCodec.unfunded_skips_import` — line 65
- `Komorebi.AVOC.Affine.ReuseCodec.decoded_import_sound` — line 71
- `Komorebi.AVOC.Affine.ReuseCodec.coldMinimum_lower` — line 86
- `Komorebi.AVOC.Affine.ReuseCodec.warmMinimum_lower` — line 97
- `Komorebi.AVOC.Affine.ReuseCodec.baseline_floor_le_choice` — line 103
- `Komorebi.AVOC.Affine.ReuseCodec.cold_preflight_skip_sound` — line 115
- `Komorebi.AVOC.Affine.ReuseCodec.warm_preflight_skip_sound` — line 127

## `AVOC/AffineReuseExamples.lean`

- `Komorebi.AVOC.Affine.ReuseExamples.unchanged_factors_fail_new_bias` — line 12
- `Komorebi.AVOC.Affine.ReuseExamples.retargeted_factors_accept` — line 15
- `Komorebi.AVOC.Affine.ReuseExamples.shifted_import_exists` — line 18
- `Komorebi.AVOC.Affine.ReuseExamples.shifted_first_valid` — line 27
- `Komorebi.AVOC.Affine.ReuseExamples.shifted_first_retarget` — line 29
- `Komorebi.AVOC.Affine.ReuseExamples.wrong_linear_cannot_reuse` — line 35
- `Komorebi.AVOC.Affine.ReuseExamples.rank_one_preflight_tariffs` — line 41
- `Komorebi.AVOC.Affine.ReuseExamples.cheap_cold_skip` — line 45
- `Komorebi.AVOC.Affine.ReuseExamples.same_calls_warm_admissible` — line 47
- `Komorebi.AVOC.Affine.ReuseExamples.preflight_does_not_guarantee_profit` — line 50
- `Komorebi.AVOC.Affine.ReuseExamples.rank_one_cold_lifecycle` — line 54
- `Komorebi.AVOC.Affine.ReuseExamples.rank_one_warm_lifecycle` — line 57
- `Komorebi.AVOC.Affine.ReuseExamples.reuse_is_not_free` — line 60
- `Komorebi.AVOC.Affine.ReuseExamples.identical_linear_does_not_imply_identical_bias` — line 62

## `AVOC/AffineSearchGuard.lean`

- `Komorebi.AVOC.Affine.SearchGuard.zero_width_linear` — line 14
- `Komorebi.AVOC.Affine.SearchGuard.widthFloor_le_factor` — line 19
- `Komorebi.AVOC.Affine.SearchGuard.widthFloor_le_checked` — line 31
- `Komorebi.AVOC.Affine.SearchGuard.menuFloor_le_original` — line 40
- `Komorebi.AVOC.Affine.SearchGuard.menuFloor_le_dense` — line 44
- `Komorebi.AVOC.Affine.SearchGuard.menuFloor_le_factor` — line 48
- `Komorebi.AVOC.Affine.SearchGuard.menuFloor_mono` — line 51
- `Komorebi.AVOC.Affine.SearchGuard.chosen_cost_ge_floor` — line 56
- `Komorebi.AVOC.Affine.SearchGuard.opportunity_bound` — line 65
- `Komorebi.AVOC.Affine.SearchGuard.no_positive_net_of_floor` — line 71
- `Komorebi.AVOC.Affine.SearchGuard.no_positive_net_of_setup_lower_bound` — line 82
- `Komorebi.AVOC.Affine.SearchGuard.worthExploring_iff` — line 93
- `Komorebi.AVOC.Affine.SearchGuard.skipped_search_no_positive_net` — line 97
- `Komorebi.AVOC.Affine.SearchGuard.affine_skip_sound` — line 109
- `Komorebi.AVOC.Affine.SearchGuard.emissionCharge_mono` — line 123
- `Komorebi.AVOC.Affine.SearchGuard.checkingCharge_mono` — line 128
- `Komorebi.AVOC.Affine.SearchGuard.coldFloor_lower` — line 135
- `Komorebi.AVOC.Affine.SearchGuard.reuseCharge_mono` — line 144
- `Komorebi.AVOC.Affine.SearchGuard.reuseCharge_no_free_validation` — line 151
- `Komorebi.AVOC.Affine.SearchGuard.reuse_lifecycle_break_even` — line 161
- `Komorebi.AVOC.Affine.SearchGuard.zero_cost_incumbent_no_positive_search_net` — line 171

## `AVOC/AffineSignature.lean`

- `Komorebi.AVOC.Affine.Signature.ext` — line 14
- `Komorebi.AVOC.Affine.eval_zero` — line 30
- `Komorebi.AVOC.Affine.eval_identity` — line 33
- `Komorebi.AVOC.Affine.eval_compose` — line 36
- `Komorebi.AVOC.Affine.eval_add` — line 40
- `Komorebi.AVOC.Affine.eval_basis` — line 47
- `Komorebi.AVOC.Affine.eq_of_zero_basis` — line 53
- `Komorebi.AVOC.Affine.eq_iff_zero_basis` — line 62
- `Komorebi.AVOC.Affine.eq_iff_eval` — line 68
- `Komorebi.AVOC.Affine.mismatch_witness` — line 74
- `Komorebi.AVOC.Affine.compose_identity` — line 80
- `Komorebi.AVOC.Affine.identity_compose` — line 83
- `Komorebi.AVOC.Affine.compose_assoc` — line 86
- `Komorebi.AVOC.Affine.check_iff` — line 94
- `Komorebi.AVOC.Affine.checkProbes_iff` — line 104
- `Komorebi.AVOC.Affine.probe_count` — line 108

## `AVOC/ApproximateBayesian.lean`

- `Komorebi.AVOC.beliefL1Distance_nonneg` — line 19
- `Komorebi.AVOC.abs_sum_sub_sum_le_sum_abs_sub` — line 28
- `Komorebi.AVOC.normalized_l1_le_two_over_mass` — line 37
- `Komorebi.AVOC.bayes_numerator_l1_le` — line 109
- `Komorebi.AVOC.conditionByWeight_l1_stability_likelihood` — line 129
- `Komorebi.AVOC.bayes_numerator_l1_le_of_prior_error` — line 166
- `Komorebi.AVOC.conditionByWeight_l1_stability_prior` — line 193
- `Komorebi.AVOC.conditionByWeight_l1_stability_combined` — line 227

## `AVOC/ApproximateBayesianCompression.lean`

- `Komorebi.AVOC.beliefL1_pushforward_contract` — line 10
- `Komorebi.AVOC.condition_pushforward_approximately_commutes` — line 22

## `AVOC/ApproximateComposition.lean`

- `Komorebi.AVOC.pushforwardRow_comp` — line 8
- `Komorebi.AVOC.l1_pushforward_contract` — line 22
- `Komorebi.AVOC.l1_pushforward_triangle` — line 49
- `Komorebi.AVOC.approximate_abstraction_comp` — line 69
- `Komorebi.AVOC.approximate_composite_horizon_bound` — line 108

## `AVOC/ApproximateExamples.lean`

- `Komorebi.AVOC.approxBudget_one` — line 7
- `Komorebi.AVOC.approxBudget_two` — line 12
- `Komorebi.AVOC.approxBudget_reward_only` — line 18
- `Komorebi.AVOC.approxBudget_transition_only` — line 24
- `Komorebi.AVOC.approxBudget_zero` — line 30
- `Komorebi.AVOC.tight_l1_distance` — line 43
- `Komorebi.AVOC.tight_weighted_sum_difference` — line 49

## `AVOC/ApproximateStochastic.lean`

- `Komorebi.AVOC.l1RowDistance_nonneg` — line 24
- `Komorebi.AVOC.l1RowDistance_self` — line 30
- `Komorebi.AVOC.l1RowDistance_symm` — line 35
- `Komorebi.AVOC.l1RowDistance_triangle` — line 43
- `Komorebi.AVOC.sum_pushforward_mul` — line 55
- `Komorebi.AVOC.expectedContinuation_abs_le` — line 73
- `Komorebi.AVOC.weighted_sum_difference_le_l1` — line 98
- `Komorebi.AVOC.abstract_horizon_value_abs_le` — line 149
- `Komorebi.AVOC.projected_expectation_error_le` — line 181
- `Komorebi.AVOC.linked_expectation_error_le` — line 203
- `Komorebi.AVOC.approxBudget_nonneg` — line 241
- `Komorebi.AVOC.sum_range_cast_eq_triangular` — line 252
- `Komorebi.AVOC.approxBudget_closed_form` — line 264
- `Komorebi.AVOC.stochastic_qValue_error_le` — line 275
- `Komorebi.AVOC.stochastic_value_error_of_q_error` — line 319
- `Komorebi.AVOC.approximate_stochastic_horizon_value_bound` — line 362
- `Komorebi.AVOC.approximate_stochastic_horizon_value_bound_closed` — line 386
- `Komorebi.AVOC.approximate_value_sufficient_of_budget` — line 400
- `Komorebi.AVOC.abstract_optimal_action_raw_regret_le` — line 417

## `AVOC/ArchiveExamples.lean`

- `Komorebi.AVOC.retrospectiveTrueArchive_likelihood` — line 20
- `Komorebi.AVOC.retrospectiveFalseArchive_likelihood` — line 25
- `Komorebi.AVOC.retrospectiveTrueArchive_mass` — line 30
- `Komorebi.AVOC.retrospectiveFalseArchive_mass` — line 36
- `Komorebi.AVOC.retrospectiveTrueArchive_positive` — line 42
- `Komorebi.AVOC.retrospectiveFalseArchive_positive` — line 47
- `Komorebi.AVOC.replay_retrospectiveTrueArchive` — line 54
- `Komorebi.AVOC.replay_retrospectiveFalseArchive` — line 67
- `Komorebi.AVOC.retrospectiveArchiveFineReplay_ne` — line 80
- `Komorebi.AVOC.retrospectiveArchiveCoarseReplay_eq` — line 90
- `Komorebi.AVOC.retrospectiveTrueArchive_recovers_refined_true` — line 100
- `Komorebi.AVOC.retrospectiveFalseArchive_recovers_refined_true` — line 108
- `Komorebi.AVOC.retrospective_archive_preserves_lost_distinction` — line 118

## `AVOC/ArchiveReplay.lean`

- `Komorebi.AVOC.archiveLikelihood_nonneg` — line 22
- `Komorebi.AVOC.archiveLikelihood_nil` — line 34
- `Komorebi.AVOC.archiveLikelihood_append` — line 39
- `Komorebi.AVOC.archiveEvidenceMass_nil` — line 55
- `Komorebi.AVOC.replayArchive_nil` — line 71
- `Komorebi.AVOC.archiveEvidenceMass_append_factor` — line 82
- `Komorebi.AVOC.archiveEvidenceMass_append_pos` — line 101
- `Komorebi.AVOC.replayArchive_append` — line 113
- `Komorebi.AVOC.conditionByWeight_congr_belief` — line 173
- `Komorebi.AVOC.conditionByWeight_congr_likelihood` — line 186
- `Komorebi.AVOC.replayAtResolution_comp` — line 209
- `Komorebi.AVOC.replay_resolution_is_pushforward` — line 223

## `AVOC/ArtifactBinding.lean`

- `Komorebi.AVOC.Binding.validate_iff` — line 52
- `Komorebi.AVOC.Binding.validated_identity` — line 61
- `Komorebi.AVOC.Binding.validated_receipt` — line 64
- `Komorebi.AVOC.Binding.validated_proof` — line 67
- `Komorebi.AVOC.Binding.validated_sound` — line 72
- `Komorebi.AVOC.Binding.validated_artifact_valid` — line 76
- `Komorebi.AVOC.Binding.stale_identity_rejected` — line 82
- `Komorebi.AVOC.Binding.substituted_ticket_rejected` — line 85
- `Komorebi.AVOC.Binding.failed_proof_rejected` — line 88
- `Komorebi.AVOC.Binding.generation_mismatch_rejected` — line 92
- `Komorebi.AVOC.Binding.proof_bytes_mismatch_rejected` — line 96
- `Komorebi.AVOC.Binding.target_mismatch_rejected` — line 101
- `Komorebi.AVOC.Binding.environment_mismatch_rejected` — line 105
- `Komorebi.AVOC.Binding.dependency_mismatch_rejected` — line 109
- `Komorebi.AVOC.Binding.register_pending` — line 130
- `Komorebi.AVOC.Binding.register_wellFormed` — line 133
- `Komorebi.AVOC.Binding.admission_iff` — line 139
- `Komorebi.AVOC.Binding.admission_consumes` — line 149
- `Komorebi.AVOC.Binding.admission_sound` — line 154
- `Komorebi.AVOC.Binding.no_pending_no_admission` — line 158
- `Komorebi.AVOC.Binding.successful_receipt_not_replayable` — line 161
- `Komorebi.AVOC.Binding.old_pending_rejected_after_register` — line 165
- `Komorebi.AVOC.Binding.consume_preserves_generation` — line 173
- `Komorebi.AVOC.Binding.rejected_admission_unchanged` — line 179
- `Komorebi.AVOC.Binding.consume_preserves_wellFormed` — line 188

## `AVOC/ArtifactExamples.lean`

- `Komorebi.AVOC.ArtifactExamples.conjunction_swap_checked` — line 24
- `Komorebi.AVOC.ArtifactExamples.conjunction_swap_all_propositions` — line 26
- `Komorebi.AVOC.ArtifactExamples.disjunction_swap_checked` — line 32
- `Komorebi.AVOC.ArtifactExamples.modus_ponens_checked` — line 39
- `Komorebi.AVOC.ArtifactExamples.false_elimination_checked` — line 43
- `Komorebi.AVOC.ArtifactExamples.missing_premise_rejected` — line 46
- `Komorebi.AVOC.ArtifactExamples.wrong_application_rejected` — line 48
- `Komorebi.AVOC.ArtifactExamples.valid_snapshot_admitted` — line 52
- `Komorebi.AVOC.ArtifactExamples.replay_rejected` — line 55
- `Komorebi.AVOC.ArtifactExamples.candidate_substitution_rejected` — line 58
- `Komorebi.AVOC.ArtifactExamples.changed_environment_rejected` — line 62
- `Komorebi.AVOC.ArtifactExamples.changed_dependency_rejected` — line 66
- `Komorebi.AVOC.ArtifactExamples.old_generation_rejected` — line 70
- `Komorebi.AVOC.ArtifactExamples.false_approval_rejected` — line 73

## `AVOC/ArtifactWorkflow.lean`

- `Komorebi.AVOC.ArtifactWorkflow.stop_allowed` — line 143
- `Komorebi.AVOC.ArtifactWorkflow.allowed_fee` — line 147
- `Komorebi.AVOC.ArtifactWorkflow.halted_only_stop` — line 154
- `Komorebi.AVOC.ArtifactWorkflow.currentReceipt_bound` — line 161
- `Komorebi.AVOC.ArtifactWorkflow.report_true_bound` — line 177
- `Komorebi.AVOC.ArtifactWorkflow.register_safe` — line 195
- `Komorebi.AVOC.ArtifactWorkflow.verify_safe` — line 207
- `Komorebi.AVOC.ArtifactWorkflow.admitStep_of_pass` — line 217
- `Komorebi.AVOC.ArtifactWorkflow.admit_safe` — line 228
- `Komorebi.AVOC.ArtifactWorkflow.step_safe` — line 244
- `Komorebi.AVOC.ArtifactWorkflow.rejection_retains_candidate` — line 257
- `Komorebi.AVOC.ArtifactWorkflow.verify_never_admits` — line 264
- `Komorebi.AVOC.ArtifactWorkflow.register_never_admits` — line 268
- `Komorebi.AVOC.ArtifactWorkflow.admit_consumes` — line 271
- `Komorebi.AVOC.ArtifactWorkflow.admission_has_exact_ticket` — line 280
- `Komorebi.AVOC.ArtifactWorkflow.replay_admission_not_allowed` — line 288

## `AVOC/ArtifactWorkflowControl.lean`

- `Komorebi.AVOC.ArtifactWorkflow.admit_budget_spent` — line 10
- `Komorebi.AVOC.ArtifactWorkflow.step_budget_spent` — line 23
- `Komorebi.AVOC.ArtifactWorkflow.step_budgetSafe` — line 33
- `Komorebi.AVOC.ArtifactWorkflow.mem_actionPool` — line 50
- `Komorebi.AVOC.ArtifactWorkflow.mem_actions` — line 73
- `Komorebi.AVOC.ArtifactWorkflow.controller_preserves` — line 79
- `Komorebi.AVOC.ArtifactWorkflow.artifact_safe_optimal_plan` — line 85
- `Komorebi.AVOC.ArtifactWorkflow.artifact_approximate_policy` — line 98
- `Komorebi.AVOC.ArtifactWorkflow.verification_expectation_raw_expansion` — line 124
- `Komorebi.AVOC.ArtifactWorkflow.verify_posterior_is_report_posterior` — line 132
- `Komorebi.AVOC.ArtifactWorkflow.halted_value_zero` — line 137
- `Komorebi.AVOC.ArtifactWorkflow.stop_q_zero` — line 151
- `Komorebi.AVOC.ArtifactWorkflow.stop_optimal` — line 160

## `AVOC/ArtifactWorkflowExamples.lean`

- `Komorebi.AVOC.ArtifactWorkflowExamples.channel_is_coarse` — line 33
- `Komorebi.AVOC.ArtifactWorkflowExamples.coarse_probability` — line 39
- `Komorebi.AVOC.ArtifactWorkflowExamples.coarse_success_posterior` — line 42
- `Komorebi.AVOC.ArtifactWorkflowExamples.coarse_rejection_posterior` — line 49
- `Komorebi.AVOC.ArtifactWorkflowExamples.raw_rejection_posterior` — line 56
- `Komorebi.AVOC.ArtifactWorkflowExamples.rejecting_is_not_ignoring` — line 65
- `Komorebi.AVOC.ArtifactWorkflowExamples.coarse_is_not_chosen_raw_posterior` — line 70
- `Komorebi.AVOC.ArtifactWorkflowExamples.initial_safe` — line 105
- `Komorebi.AVOC.ArtifactWorkflowExamples.register_allowed` — line 121
- `Komorebi.AVOC.ArtifactWorkflowExamples.verify_allowed` — line 130
- `Komorebi.AVOC.ArtifactWorkflowExamples.actual_filter` — line 134
- `Komorebi.AVOC.ArtifactWorkflowExamples.registered_channel` — line 137
- `Komorebi.AVOC.ArtifactWorkflowExamples.passed_belief` — line 142
- `Komorebi.AVOC.ArtifactWorkflowExamples.rejected_belief` — line 147
- `Komorebi.AVOC.ArtifactWorkflowExamples.checked_receipt` — line 152
- `Komorebi.AVOC.ArtifactWorkflowExamples.verified_not_admitted` — line 154
- `Komorebi.AVOC.ArtifactWorkflowExamples.rejection_retains_exact_ticket` — line 156
- `Komorebi.AVOC.ArtifactWorkflowExamples.rejection_charged` — line 158
- `Komorebi.AVOC.ArtifactWorkflowExamples.admit_precondition` — line 160
- `Komorebi.AVOC.ArtifactWorkflowExamples.admit_allowed` — line 163
- `Komorebi.AVOC.ArtifactWorkflowExamples.final_completion` — line 166
- `Komorebi.AVOC.ArtifactWorkflowExamples.final_budget` — line 168
- `Komorebi.AVOC.ArtifactWorkflowExamples.final_safe` — line 170
- `Komorebi.AVOC.ArtifactWorkflowExamples.consumed_not_replayable` — line 175
- `Komorebi.AVOC.ArtifactWorkflowExamples.no_receipt_one_step` — line 179
- `Komorebi.AVOC.ArtifactWorkflowExamples.rejected_one_step_value` — line 196
- `Komorebi.AVOC.ArtifactWorkflowExamples.passed_admission_reward` — line 199
- `Komorebi.AVOC.ArtifactWorkflowExamples.passed_one_step_value` — line 203
- `Komorebi.AVOC.ArtifactWorkflowExamples.verification_two_step_q` — line 219
- `Komorebi.AVOC.ArtifactWorkflowExamples.register_two_step_q` — line 233
- `Komorebi.AVOC.ArtifactWorkflowExamples.registered_two_step_value` — line 244
- `Komorebi.AVOC.ArtifactWorkflowExamples.initial_three_step_q` — line 260
- `Komorebi.AVOC.ArtifactWorkflowExamples.initial_three_step_value` — line 271
- `Komorebi.AVOC.ArtifactWorkflowExamples.initial_source_safe` — line 295

## `AVOC/ArtifactWorkflowGuarantee.lean`

- `Komorebi.AVOC.ArtifactWorkflow.admit_belief` — line 10
- `Komorebi.AVOC.ArtifactWorkflow.step_belief` — line 23
- `Komorebi.AVOC.ArtifactWorkflow.positive_success_has_receipt` — line 35
- `Komorebi.AVOC.ArtifactWorkflow.new_completion_requires_admit` — line 61
- `Komorebi.AVOC.ArtifactWorkflow.execute_spent` — line 88
- `Komorebi.AVOC.ArtifactWorkflow.legal_trace_safe` — line 98
- `Komorebi.AVOC.ArtifactWorkflow.legal_trace_cost_bound` — line 107
- `Komorebi.AVOC.ArtifactWorkflow.artifact_bayesian_model_policy` — line 118

## `AVOC/ArtifactWorkflowSource.lean`

- `Komorebi.AVOC.ArtifactWorkflow.successful_parse_is_sourceParsed` — line 12
- `Komorebi.AVOC.ArtifactWorkflow.register_pending_parsed` — line 35
- `Komorebi.AVOC.ArtifactWorkflow.step_pending_parsed` — line 43
- `Komorebi.AVOC.ArtifactWorkflow.step_source_safe` — line 58
- `Komorebi.AVOC.ArtifactWorkflow.admission_retains_parsed_source` — line 65
- `Komorebi.AVOC.ArtifactWorkflow.controller_source_preserves` — line 80
- `Komorebi.AVOC.ArtifactWorkflow.source_bound_safe_optimal_plan` — line 87
- `Komorebi.AVOC.ArtifactWorkflow.source_bound_approximate_policy_safe` — line 99

## `AVOC/AtomicCommitModel.lean`

- `Komorebi.AVOC.AtomicCommitModel.prepare_contract` — line 28
- `Komorebi.AVOC.AtomicCommitModel.prepare_does_not_commit` — line 43
- `Komorebi.AVOC.AtomicCommitModel.publish_contract` — line 49
- `Komorebi.AVOC.AtomicCommitModel.published_result_matches_state` — line 62
- `Komorebi.AVOC.AtomicCommitModel.duplicate_publish_rejected` — line 69
- `Komorebi.AVOC.AtomicCommitModel.stale_intent_after_publish_rejected` — line 76
- `Komorebi.AVOC.AtomicCommitModel.no_op_commit_still_advances` — line 85
- `Komorebi.AVOC.AtomicCommitModel.reconcile_physical_unchanged` — line 102
- `Komorebi.AVOC.AtomicCommitModel.reconcile_safe` — line 113
- `Komorebi.AVOC.AtomicCommitModel.reconcile_idempotent` — line 125

## `AVOC/AttemptAccounting.lean`

- `Komorebi.AVOC.Attempts.initial_safe` — line 74
- `Komorebi.AVOC.Attempts.reserve_contract` — line 77
- `Komorebi.AVOC.Attempts.renew_contract` — line 87
- `Komorebi.AVOC.Attempts.publish_contract` — line 97
- `Komorebi.AVOC.Attempts.settle_contract` — line 106
- `Komorebi.AVOC.Attempts.abandon_contract` — line 115
- `Komorebi.AVOC.Attempts.reserve_safe` — line 124
- `Komorebi.AVOC.Attempts.renew_safe` — line 136
- `Komorebi.AVOC.Attempts.publish_safe` — line 148
- `Komorebi.AVOC.Attempts.settle_safe` — line 153
- `Komorebi.AVOC.Attempts.abandon_safe` — line 160
- `Komorebi.AVOC.Attempts.renew_preserves_confirmed` — line 166
- `Komorebi.AVOC.Attempts.renew_charge_and_count` — line 171
- `Komorebi.AVOC.Attempts.renew_fresh_generation` — line 177
- `Komorebi.AVOC.Attempts.stale_publication_rejected` — line 184
- `Komorebi.AVOC.Attempts.renewed_old_attempt_rejected` — line 188
- `Komorebi.AVOC.Attempts.published_retry_rejected` — line 198
- `Komorebi.AVOC.Attempts.published_abandonment_rejected` — line 202
- `Komorebi.AVOC.Attempts.charge_not_refunded_on_abandon` — line 206
- `Komorebi.AVOC.Attempts.terminal_reservation_rejected` — line 212
- `Komorebi.AVOC.Attempts.exhausted_count_rejects_zero_fee` — line 216
- `Komorebi.AVOC.Attempts.exhausted_credit_rejects_retry` — line 221
- `Komorebi.AVOC.Attempts.settle_once` — line 226
- `Komorebi.AVOC.Attempts.settle_no_new_charge` — line 231
- `Komorebi.AVOC.Attempts.step_safe` — line 267
- `Komorebi.AVOC.Attempts.step_accounting` — line 276
- `Komorebi.AVOC.Attempts.run_safe` — line 294
- `Komorebi.AVOC.Attempts.run_accounting` — line 304
- `Komorebi.AVOC.Attempts.complete_trace_bounds` — line 321

## `AVOC/AttemptCodec.lean`

- `Komorebi.AVOC.Attempts.checkSafe_iff` — line 17
- `Komorebi.AVOC.Attempts.checkedStep_sound` — line 23

## `AVOC/AttemptExamples.lean`

- `Komorebi.AVOC.AttemptExamples.fresh_attempt` — line 12
- `Komorebi.AVOC.AttemptExamples.retry_charged_twice` — line 14
- `Komorebi.AVOC.AttemptExamples.old_attempt_cannot_publish` — line 16
- `Komorebi.AVOC.AttemptExamples.new_attempt_can_publish` — line 18
- `Komorebi.AVOC.AttemptExamples.successful_retry_only_one_logical_fee` — line 20
- `Komorebi.AVOC.AttemptExamples.failed_cost_retained` — line 22
- `Komorebi.AVOC.AttemptExamples.no_refund_on_terminal_cancel` — line 24
- `Komorebi.AVOC.AttemptExamples.count_cap_stops_free_retries` — line 27
- `Komorebi.AVOC.AttemptExamples.budget_cap_stops_retry` — line 30

## `AVOC/AttemptRecovery.lean`

- `Komorebi.AVOC.AttemptRecovery.retry_contract` — line 34
- `Komorebi.AVOC.AttemptRecovery.retry_safe` — line 47
- `Komorebi.AVOC.AttemptRecovery.retry_no_bayesian_or_proof_update` — line 54
- `Komorebi.AVOC.AttemptRecovery.cancel_contract` — line 63
- `Komorebi.AVOC.AttemptRecovery.cancel_safe_and_no_refund` — line 75
- `Komorebi.AVOC.AttemptRecovery.confirm_contract` — line 97
- `Komorebi.AVOC.AttemptRecovery.confirm_safe` — line 117
- `Komorebi.AVOC.AttemptRecovery.confirm_no_double_attempt_charge` — line 126
- `Komorebi.AVOC.AttemptRecovery.confirmed_spend_le_attempt_envelope` — line 131
- `Komorebi.AVOC.AttemptRecovery.confirmed_admission_retains_source` — line 138

## `AVOC/Bayesian.lean`

- `Komorebi.AVOC.RationalBelief.ext` — line 17
- `Komorebi.AVOC.predictiveProb_nonneg` — line 39
- `Komorebi.AVOC.predictiveProb_sum_one` — line 50
- `Komorebi.AVOC.bayesUpdate_mul_predictive` — line 92
- `Komorebi.AVOC.predictive_mul_posteriorExpectedUtility` — line 112
- `Komorebi.AVOC.bayesNumerator_eq_zero_of_predictive_eq_zero` — line 142
- `Komorebi.AVOC.bayesUpdateTotal_eq_of_pos` — line 166
- `Komorebi.AVOC.predictiveProb_eq_zero_of_not_pos` — line 176
- `Komorebi.AVOC.signalActionScore_eq_zero_of_predictive_eq_zero` — line 186
- `Komorebi.AVOC.bayesianPolicyValue_eq_stochasticDecisionValue` — line 215

## `AVOC/BayesianCompression.lean`

- `Komorebi.AVOC.evidenceMass_pushforward` — line 10
- `Komorebi.AVOC.condition_pushforward_commutes` — line 21
- `Komorebi.AVOC.predictiveProb_pushforward` — line 56
- `Komorebi.AVOC.bayesUpdate_pushforward_commutes` — line 78
- `Komorebi.AVOC.likelihood_factors_iff_fiber_constant` — line 118
- `Komorebi.AVOC.likelihood_collision_obstructs_factorization` — line 138

## `AVOC/BayesianControl.lean`

- `Komorebi.AVOC.bayesianHorizonValue_succ_eq_max` — line 51
- `Komorebi.AVOC.bayesian_bellman_action_exists` — line 62
- `Komorebi.AVOC.bayesianHorizonValue_eq_qValue_of_optimal` — line 73
- `Komorebi.AVOC.bayesian_finite_horizon_optimal_action_exists` — line 91
- `Komorebi.AVOC.bayesianExpectedContinuation_mono` — line 102
- `Komorebi.AVOC.bayesianExpectedContinuation_const` — line 119
- `Komorebi.AVOC.posterior_martingale_coordinate` — line 132
- `Komorebi.AVOC.bayesian_law_of_total_expectation` — line 156
- `Komorebi.AVOC.bestBayesianDecisionValue_eq_bestStochasticDecisionValue` — line 198
- `Komorebi.AVOC.best_bayesian_policy_exists` — line 209
- `Komorebi.AVOC.bayesian_blackwell_monotonicity` — line 225
- `Komorebi.AVOC.bayesianValueOfInformation_nonneg` — line 254
- `Komorebi.AVOC.bayesianValueOfInformation_mono_under_garbling` — line 264

## `AVOC/BayesianEvidence.lean`

- `Komorebi.AVOC.evidenceMass_nonneg` — line 15
- `Komorebi.AVOC.conditionByWeight_mul_evidence` — line 42
- `Komorebi.AVOC.bayesUpdate_eq_conditionByWeight` — line 54
- `Komorebi.AVOC.evidenceMass_condition_compose` — line 68
- `Komorebi.AVOC.conditionByWeight_compose` — line 95
- `Komorebi.AVOC.conditionByWeight_commute` — line 142

## `AVOC/BayesianExamples.lean`

- `Komorebi.AVOC.uniformBool_perfect_true_predictive` — line 16
- `Komorebi.AVOC.uniformBool_perfect_true_positive` — line 23
- `Komorebi.AVOC.perfectBoolPosterior_true` — line 29
- `Komorebi.AVOC.perfectBoolPosterior_false` — line 41
- `Komorebi.AVOC.boolLikelihoodOne_nonneg` — line 61
- `Komorebi.AVOC.boolLikelihoodTwo_nonneg` — line 65
- `Komorebi.AVOC.boolLikelihoodOne_mass` — line 69
- `Komorebi.AVOC.boolLikelihoodOne_positive` — line 75
- `Komorebi.AVOC.boolLikelihoodTwo_mass` — line 80
- `Komorebi.AVOC.boolLikelihoodTwo_positive` — line 86
- `Komorebi.AVOC.boolLikelihoodProduct_mass` — line 91
- `Komorebi.AVOC.boolLikelihoodTwo_after_one_positive` — line 98
- `Komorebi.AVOC.boolLikelihoodProductReverse_mass` — line 110
- `Komorebi.AVOC.boolLikelihoodOne_after_two_positive` — line 117
- `Komorebi.AVOC.boolEvidence_order_invariant` — line 130

## `AVOC/BayesianGuardedBridge.lean`

- `Komorebi.AVOC.Guarded.bayesian_link_expectation_error` — line 28
- `Komorebi.AVOC.Guarded.codec_average_of_uniform_error` — line 86
- `Komorebi.AVOC.Guarded.BayesianModelCertificate.toModelCertificate` — line 131
- `Komorebi.AVOC.Guarded.bayesian_primitive_q_error` — line 146
- `Komorebi.AVOC.Guarded.bayesian_primitive_value_error` — line 157

## `AVOC/BayesianInstability.lean`

- `Komorebi.AVOC.rareLikelihoodFalse_nonneg` — line 16
- `Komorebi.AVOC.rareLikelihoodTrue_nonneg` — line 21
- `Komorebi.AVOC.rareLikelihoodFalse_mass` — line 26
- `Komorebi.AVOC.rareLikelihoodTrue_mass` — line 33
- `Komorebi.AVOC.rareLikelihoodFalse_mass_pos` — line 40
- `Komorebi.AVOC.rareLikelihoodTrue_mass_pos` — line 45
- `Komorebi.AVOC.rareLikelihood_pointwise_close` — line 51
- `Komorebi.AVOC.rareFalse_posterior_false` — line 57
- `Komorebi.AVOC.rareFalse_posterior_true` — line 75
- `Komorebi.AVOC.rareTrue_posterior_true` — line 92
- `Komorebi.AVOC.rareTrue_posterior_false` — line 110
- `Komorebi.AVOC.rare_evidence_maximal_posterior_flip` — line 128
- `Komorebi.AVOC.no_uniform_likelihood_lipschitz` — line 145

## `AVOC/BayesianObservationTransport.lean`

- `Komorebi.AVOC.jointObservationL1_nonneg` — line 15
- `Komorebi.AVOC.total_posterior_scaled` — line 20
- `Komorebi.AVOC.mass_weighted_belief_l1` — line 33
- `Komorebi.AVOC.predictive_l1_le_joint` — line 53
- `Komorebi.AVOC.expected_posterior_l1_le_two_joint` — line 63
- `Komorebi.AVOC.joint_l1_le_prior_add_channel` — line 79
- `Komorebi.AVOC.observation_expectation_transport` — line 114
- `Komorebi.AVOC.bayesian_continuation_error` — line 137
- `Komorebi.AVOC.bayesian_continuation_error_of_primitive_bounds` — line 167
- `Komorebi.AVOC.predictive_l1_of_primitive_bounds` — line 182
- `Komorebi.AVOC.expected_posterior_l1_of_primitive_bounds` — line 192

## `AVOC/BayesianTransportExamples.lean`

- `Komorebi.AVOC.BayesianTransportExamples.rare_joint_error` — line 18
- `Komorebi.AVOC.BayesianTransportExamples.rare_predictive_mass` — line 22
- `Komorebi.AVOC.BayesianTransportExamples.rare_branch_posterior_error` — line 25
- `Komorebi.AVOC.BayesianTransportExamples.common_predictive_mass` — line 31
- `Komorebi.AVOC.BayesianTransportExamples.common_branch_posterior_error` — line 34
- `Komorebi.AVOC.BayesianTransportExamples.rare_average_posterior_error` — line 40
- `Komorebi.AVOC.BayesianTransportExamples.rare_average_bound_is_not_pointwise` — line 49

## `AVOC/BeliefValueTables.lean`

- `Komorebi.AVOC.beliefRowValue_bound` — line 11
- `Komorebi.AVOC.beliefRowValue_lipschitz` — line 23
- `Komorebi.AVOC.beliefRowValue_le_table` — line 43
- `Komorebi.AVOC.beliefTableValue_attained` — line 50
- `Komorebi.AVOC.beliefTableValue_bound` — line 58
- `Komorebi.AVOC.beliefTableValue_lipschitz` — line 65

## `AVOC/BindingCodec.lean`

- `Komorebi.AVOC.Binding.source_artifact_consistent` — line 36
- `Komorebi.AVOC.Binding.source_artifact_checked_sound` — line 50
- `Komorebi.AVOC.Binding.accepted_bound_json_has_evidence` — line 94

## `AVOC/Blackwell.lean`

- `Komorebi.AVOC.deterministic_policy_lift_value_eq` — line 23
- `Komorebi.AVOC.deterministicDecisionValue_le_best` — line 57
- `Komorebi.AVOC.best_deterministic_policy_exists` — line 78
- `Komorebi.AVOC.deterministic_blackwell_monotonicity` — line 104
- `Komorebi.AVOC.deterministic_blackwell_cost_dominance` — line 126

## `AVOC/BooleanCostClosure.lean`

- `Komorebi.AVOC.BoolClosure.get_ofFun` — line 38
- `Komorebi.AVOC.BoolClosure.get_neg` — line 42
- `Komorebi.AVOC.BoolClosure.get_bin` — line 46
- `Komorebi.AVOC.BoolClosure.sig_ext` — line 51
- `Komorebi.AVOC.BoolClosure.sem_get` — line 78
- `Komorebi.AVOC.BoolClosure.sem_eq_iff` — line 95
- `Komorebi.AVOC.BoolClosure.mem_bools` — line 112
- `Komorebi.AVOC.BoolClosure.signatures_complete` — line 114
- `Komorebi.AVOC.BoolClosure.signatures_length` — line 127
- `Komorebi.AVOC.BoolClosure.bool_cost_bit_bound` — line 134
- `Komorebi.AVOC.BoolClosure.signature_index_bound` — line 136
- `Komorebi.AVOC.BoolClosure.witness_check_sound` — line 175
- `Komorebi.AVOC.BoolClosure.lower_check_sound` — line 182
- `Komorebi.AVOC.BoolClosure.check_bank_parts` — line 213
- `Komorebi.AVOC.BoolClosure.query_equivalent` — line 230
- `Komorebi.AVOC.BoolClosure.query_globally_minimum` — line 234
- `Komorebi.AVOC.BoolClosure.query_no_larger` — line 240
- `Komorebi.AVOC.BoolClosure.query_cost_fixed` — line 243
- `Komorebi.AVOC.BoolClosure.query_idempotent_cost` — line 249
- `Komorebi.AVOC.BoolClosure.larger_equivalent_cannot_be_witness` — line 256

## `AVOC/BooleanProgram.lean`

- `Komorebi.AVOC.Synthesis.runCount_value` — line 59
- `Komorebi.AVOC.Synthesis.runCount_visits` — line 62
- `Komorebi.AVOC.Synthesis.nodes_positive` — line 65
- `Komorebi.AVOC.Synthesis.input_complete` — line 71
- `Komorebi.AVOC.Synthesis.inputs_length` — line 75
- `Komorebi.AVOC.Synthesis.check_sound` — line 82
- `Komorebi.AVOC.Synthesis.check_complete` — line 87
- `Komorebi.AVOC.Synthesis.check_iff` — line 92
- `Komorebi.AVOC.Synthesis.equivalent_refl` — line 95
- `Komorebi.AVOC.Synthesis.equivalent_trans` — line 97
- `Komorebi.AVOC.Synthesis.check_self` — line 100
- `Komorebi.AVOC.Synthesis.non_equivalent_rejected` — line 103
- `Komorebi.AVOC.Synthesis.pairs_length` — line 116
- `Komorebi.AVOC.Synthesis.mem_pairs` — line 122
- `Komorebi.AVOC.Synthesis.expand_length` — line 147
- `Komorebi.AVOC.Synthesis.programs_length` — line 152
- `Komorebi.AVOC.Synthesis.pair_nodes_bound` — line 157
- `Komorebi.AVOC.Synthesis.expand_nodes_bound` — line 166
- `Komorebi.AVOC.Synthesis.programs_nodes_bound` — line 180
- `Komorebi.AVOC.Synthesis.programs_step_contains` — line 191
- `Komorebi.AVOC.Synthesis.programs_mono` — line 196
- `Komorebi.AVOC.Synthesis.grammar_complete` — line 204
- `Komorebi.AVOC.Synthesis.bounded_grammar_complete` — line 227

## `AVOC/BoundedRecommendation.lean`

- `Komorebi.AVOC.ExecutablePlanner.selectedDepth_le` — line 31
- `Komorebi.AVOC.ExecutablePlanner.recommend_depth` — line 36
- `Komorebi.AVOC.ExecutablePlanner.recommend_action` — line 41
- `Komorebi.AVOC.ExecutablePlanner.recommend_credit` — line 49
- `Komorebi.AVOC.ExecutablePlanner.recommend_score_exact` — line 63
- `Komorebi.AVOC.ExecutablePlanner.recommend_allowed` — line 71
- `Komorebi.AVOC.ExecutablePlanner.recommend_gap` — line 78
- `Komorebi.AVOC.ExecutablePlanner.recommendation_policy_regret` — line 92

## `AVOC/BoundedSynthesis.lean`

- `Komorebi.AVOC.Synthesis.prefer_sound` — line 15
- `Komorebi.AVOC.Synthesis.prefer_no_larger` — line 24
- `Komorebi.AVOC.Synthesis.prefer_le_candidate` — line 32
- `Komorebi.AVOC.Synthesis.prefer_member` — line 39
- `Komorebi.AVOC.Synthesis.select_sound` — line 43
- `Komorebi.AVOC.Synthesis.select_no_larger` — line 49
- `Komorebi.AVOC.Synthesis.select_minimum` — line 55
- `Komorebi.AVOC.Synthesis.select_member` — line 66
- `Komorebi.AVOC.Synthesis.testCharge_positive` — line 82
- `Komorebi.AVOC.Synthesis.testCharge_covers` — line 85
- `Komorebi.AVOC.Synthesis.examined_mem_generated` — line 107
- `Komorebi.AVOC.Synthesis.examined_count` — line 114
- `Komorebi.AVOC.Synthesis.search_budget` — line 122
- `Komorebi.AVOC.Synthesis.insufficient_generation_no_search` — line 133
- `Komorebi.AVOC.Synthesis.synthesis_sound` — line 139
- `Komorebi.AVOC.Synthesis.synthesis_work_nondegrading` — line 143
- `Komorebi.AVOC.Synthesis.synthesis_minimum_on_examined` — line 146
- `Komorebi.AVOC.Synthesis.changed_candidate_was_generated` — line 150
- `Komorebi.AVOC.Synthesis.certified_synthesis` — line 156
- `Komorebi.AVOC.Synthesis.examined_full` — line 165
- `Komorebi.AVOC.Synthesis.synthesis_optimal_bounded_grammar` — line 178
- `Komorebi.AVOC.Synthesis.search_candidate` — line 200
- `Komorebi.AVOC.Synthesis.search_safe` — line 203
- `Komorebi.AVOC.Synthesis.search_tested_bounded` — line 208

## `AVOC/CertificateCodec.lean`

- `Komorebi.AVOC.Certificate.accepted_json_has_sound_sequent` — line 54

## `AVOC/CertificateLogic.lean`

- `Komorebi.AVOC.Certificate.satisfies_cons` — line 78
- `Komorebi.AVOC.Certificate.infer_sound` — line 86
- `Komorebi.AVOC.Certificate.check_sound` — line 158
- `Komorebi.AVOC.Certificate.no_closed_false_proof` — line 163
- `Komorebi.AVOC.Certificate.identity_checked` — line 171
- `Komorebi.AVOC.Certificate.premise_checked` — line 175
- `Komorebi.AVOC.Certificate.truth_checked` — line 178
- `Komorebi.AVOC.Certificate.check_target_unique` — line 180
- `Komorebi.AVOC.Certificate.checked_chain_sound` — line 195
- `Komorebi.AVOC.Certificate.closed_chain_sound` — line 204

## `AVOC/CertificateResearch.lean`

- `Komorebi.AVOC.BoundResearch.bound_receipt_local_rule` — line 18
- `Komorebi.AVOC.BoundResearch.boundGate_sound` — line 35
- `Komorebi.AVOC.BoundResearch.passing_filter_bound` — line 67
- `Komorebi.AVOC.BoundResearch.empty_slot_blocks` — line 84
- `Komorebi.AVOC.BoundResearch.bound_verification_budgetSafe` — line 98
- `Komorebi.AVOC.BoundResearch.bound_verification_consumes` — line 105
- `Komorebi.AVOC.BoundResearch.new_bound_completion_has_exact_artifact` — line 110
- `Komorebi.AVOC.BoundResearch.rejected_bound_completion_unchanged` — line 127
- `Komorebi.AVOC.BoundResearch.replay_cannot_admit_new` — line 134

## `AVOC/CommitRecovery.lean`

- `Komorebi.AVOC.CommitRecovery.initial_safe` — line 63
- `Komorebi.AVOC.CommitRecovery.unfinished_rejected` — line 68
- `Komorebi.AVOC.CommitRecovery.acknowledge_contract` — line 75
- `Komorebi.AVOC.CommitRecovery.acknowledge_safe` — line 103
- `Komorebi.AVOC.CommitRecovery.acknowledge_result_identity` — line 112
- `Komorebi.AVOC.CommitRecovery.acknowledge_idempotent` — line 126
- `Komorebi.AVOC.CommitRecovery.acknowledge_count` — line 133
- `Komorebi.AVOC.CommitRecovery.changed_poststate_rejected` — line 141
- `Komorebi.AVOC.CommitRecovery.wrong_sequence_rejected` — line 146
- `Komorebi.AVOC.CommitRecovery.wrong_prestate_rejected` — line 152
- `Komorebi.AVOC.CommitRecovery.fresh_acknowledgement_cost` — line 159
- `Komorebi.AVOC.CommitRecovery.recovered_safe` — line 170
- `Komorebi.AVOC.CommitRecovery.replay_safe` — line 183
- `Komorebi.AVOC.CommitRecovery.replay_initial_safe` — line 195
- `Komorebi.AVOC.CommitRecovery.replay_no_overspend` — line 199
- `Komorebi.AVOC.CommitRecovery.recovered_admission_valid` — line 204
- `Komorebi.AVOC.CommitRecovery.recovered_false_admission_impossible` — line 210

## `AVOC/Composition.lean`

- `Komorebi.AVOC.local_decomposition_cost_bound` — line 8
- `Komorebi.AVOC.local_search_cost_bound` — line 18
- `Komorebi.AVOC.local_reuse_nonincreasing` — line 30

## `AVOC/Context.lean`

- `Komorebi.AVOC.sufficientForQueries_antitone` — line 16
- `Komorebi.AVOC.sufficientForQueries_insert_iff` — line 27
- `Komorebi.AVOC.mem_sufficientContexts_iff` — line 54
- `Komorebi.AVOC.finite_minimum_cost_sufficient_context_exists` — line 67
- `Komorebi.AVOC.sufficientContexts_antitone_queries` — line 98
- `Komorebi.AVOC.minimumCostSufficientContext_exists` — line 127
- `Komorebi.AVOC.minimum_context_cost_monotone_queries` — line 141

## `AVOC/Control.lean`

- `Komorebi.AVOC.score_mono_of_dominance` — line 49
- `Komorebi.AVOC.finite_epistemic_scheduler_exists` — line 74
- `Komorebi.AVOC.constrained_scheduler_exists` — line 96
- `Komorebi.AVOC.stop_optimal_of_nonpositive` — line 133
- `Komorebi.AVOC.answer_better_iff_threshold` — line 147
- `Komorebi.AVOC.weakLinkUtility_positive_iff` — line 174
- `Komorebi.AVOC.weakLinkUtilityWithRisk_antitone_in_falseAdmission` — line 189
- `Komorebi.AVOC.queue_grows_when_generation_exceeds_absorption` — line 206
- `Komorebi.AVOC.queue_nonincreasing_when_absorbed` — line 215

## `AVOC/ControlSufficiency.lean`

- `Komorebi.AVOC.controlSufficient_id` — line 20
- `Komorebi.AVOC.reward_eq_of_refines_controlSufficient` — line 32
- `Komorebi.AVOC.controlSufficient_iff_rewardStable_and_transitionClosed` — line 66
- `Komorebi.AVOC.controlSufficient_of_refines_and_transitionClosed` — line 84
- `Komorebi.AVOC.reward_mismatch_obstructs_controlSufficiency` — line 100
- `Komorebi.AVOC.transition_mismatch_obstructs_controlSufficiency` — line 111
- `Komorebi.AVOC.bellmanOptimalAt_exists` — line 127
- `Komorebi.AVOC.qValue_le_horizonValue_succ` — line 135
- `Komorebi.AVOC.horizonValue_eq_of_controlSufficient` — line 145
- `Komorebi.AVOC.qValue_eq_of_controlSufficient` — line 168
- `Komorebi.AVOC.bellmanOptimalAt_iff_of_controlSufficient` — line 179
- `Komorebi.AVOC.bellmanChoice_optimal` — line 207
- `Komorebi.AVOC.quotient_factored_optimal_policy_exists` — line 217
- `Komorebi.AVOC.controlSection_spec` — line 249
- `Komorebi.AVOC.quotientControlSystem_reward_eq` — line 267
- `Komorebi.AVOC.quotientControlSystem_transition_eq` — line 277
- `Komorebi.AVOC.quotientControlSystem_qValue_eq` — line 289
- `Komorebi.AVOC.quotientControlSystem_horizonValue_eq` — line 306
- `Komorebi.AVOC.quotient_optimal_action_lifts` — line 340
- `Komorebi.AVOC.quotient_bellmanOptimalAt_iff` — line 368

## `AVOC/ControlSufficiencyExamples.lean`

- `Komorebi.AVOC.refinementCounter_fine_refines_coarse` — line 21
- `Komorebi.AVOC.refinementCounter_coarse_controlSufficient` — line 29
- `Komorebi.AVOC.refinementCounter_fine_not_controlSufficient` — line 36
- `Komorebi.AVOC.controlSufficiency_not_monotone_under_refinement` — line 47

## `AVOC/Core.lean`

- `Komorebi.AVOC.refines_refl` — line 28
- `Komorebi.AVOC.refines_trans` — line 32
- `Komorebi.AVOC.encodingEquiv_refl` — line 41
- `Komorebi.AVOC.encodingEquiv_symm` — line 45
- `Komorebi.AVOC.encodingEquiv_trans` — line 49
- `Komorebi.AVOC.target_is_sufficient` — line 55
- `Komorebi.AVOC.sufficient_of_refines` — line 61
- `Komorebi.AVOC.target_is_coarsest_sufficient` — line 70
- `Komorebi.AVOC.sufficient_preserves_target_distinctions` — line 75
- `Komorebi.AVOC.collision_obstructs_sufficiency` — line 87
- `Komorebi.AVOC.sufficient_implies_fiber_refinement` — line 96
- `Komorebi.AVOC.fiber_refinement_implies_sufficient` — line 106
- `Komorebi.AVOC.sufficient_iff_fiber_refinement` — line 124
- `Komorebi.AVOC.refines_iff_fiber_inclusion` — line 139
- `Komorebi.AVOC.reachableCard_mono_of_refines` — line 155
- `Komorebi.AVOC.taskMinimal_iff_encodingEquiv` — line 184
- `Komorebi.AVOC.target_is_taskMinimal` — line 191
- `Komorebi.AVOC.joint_sufficient_implies_each` — line 203
- `Komorebi.AVOC.each_sufficient_implies_joint` — line 217
- `Komorebi.AVOC.sufficient_joint_iff_each` — line 232
- `Komorebi.AVOC.joint_target_is_coarsest_sufficient` — line 242
- `Komorebi.AVOC.verified_yield_ceiling` — line 251
- `Komorebi.AVOC.counterexample_pruning_nonexpansive` — line 259
- `Komorebi.AVOC.counterexample_pruning_strict` — line 267

## `AVOC/CostCertificateExamples.lean`

- `Komorebi.AVOC.CostCertificateExamples.zero_is_lower` — line 16
- `Komorebi.AVOC.CostCertificateExamples.zero_has_no_realizer` — line 19
- `Komorebi.AVOC.CostCertificateExamples.valid_witness_can_be_nonminimal` — line 29
- `Komorebi.AVOC.CostCertificateExamples.witness_cost_two_not_lower` — line 35
- `Komorebi.AVOC.CostCertificateExamples.empty_bank_rejected` — line 41
- `Komorebi.AVOC.CostCertificateExamples.unfunded_empty_bank_no_charge` — line 43
- `Komorebi.AVOC.CostCertificateExamples.funded_empty_bank_charged` — line 45
- `Komorebi.AVOC.CostCertificateExamples.false_same_semantics` — line 48

## `AVOC/DurableUpgrade.lean`

- `Komorebi.AVOC.DurableUpgrade.charged_safe` — line 116
- `Komorebi.AVOC.DurableUpgrade.initial_safe` — line 122
- `Komorebi.AVOC.DurableUpgrade.begin_safe` — line 126
- `Komorebi.AVOC.DurableUpgrade.finish_safe` — line 152
- `Komorebi.AVOC.DurableUpgrade.abandon_safe` — line 171
- `Komorebi.AVOC.DurableUpgrade.apply_safe` — line 185
- `Komorebi.AVOC.DurableUpgrade.begin_keeps_active` — line 194
- `Komorebi.AVOC.DurableUpgrade.abandon_keeps_current` — line 211
- `Komorebi.AVOC.DurableUpgrade.finish_evaluation_unchanged` — line 225
- `Komorebi.AVOC.DurableUpgrade.begin_accounting` — line 247
- `Komorebi.AVOC.DurableUpgrade.finish_accounting` — line 265
- `Komorebi.AVOC.DurableUpgrade.abandon_accounting` — line 288
- `Komorebi.AVOC.DurableUpgrade.apply_accounting` — line 303
- `Komorebi.AVOC.DurableUpgrade.duplicate_closed_begin` — line 313
- `Komorebi.AVOC.DurableUpgrade.duplicate_pending_begin` — line 318
- `Komorebi.AVOC.DurableUpgrade.finished_key_noop` — line 322
- `Komorebi.AVOC.DurableUpgrade.changed_key_request_rejected` — line 326
- `Komorebi.AVOC.DurableUpgrade.stale_complete_parent_rejected` — line 331
- `Komorebi.AVOC.DurableUpgrade.replay_safe` — line 343
- `Komorebi.AVOC.DurableUpgrade.replay_from_initial_safe` — line 355
- `Komorebi.AVOC.DurableUpgrade.replay_contract_and_budget` — line 360
- `Komorebi.AVOC.DurableUpgrade.replay_net_bound` — line 368

## `AVOC/DurableUpgradeExamples.lean`

- `Komorebi.AVOC.DurableUpgradeExamples.reserve_is_paid_not_promoted` — line 21
- `Komorebi.AVOC.DurableUpgradeExamples.bad_trial_completed` — line 25
- `Komorebi.AVOC.DurableUpgradeExamples.full_campaign_replays` — line 28
- `Komorebi.AVOC.DurableUpgradeExamples.persisted_net_gain` — line 30
- `Komorebi.AVOC.DurableUpgradeExamples.duplicate_promotion_has_no_debit` — line 33
- `Komorebi.AVOC.DurableUpgradeExamples.exact_request_replay_is_free` — line 36
- `Komorebi.AVOC.DurableUpgradeExamples.interrupted_evaluation_abandonment_retains_charge` — line 39
- `Komorebi.AVOC.DurableUpgradeExamples.omitted_failed_trial_is_rejected` — line 44
- `Komorebi.AVOC.DurableUpgradeExamples.unchanged_version_does_not_erase_cost` — line 48
- `Komorebi.AVOC.DurableUpgradeExamples.forged_active_checkpoint_rejected` — line 53
- `Komorebi.AVOC.DurableUpgradeExamples.abandoned_result_cannot_promote` — line 56

## `AVOC/DurableUpgradeLaws.lean`

- `Komorebi.AVOC.DurableUpgrade.findClosed_append_new` — line 9
- `Komorebi.AVOC.DurableUpgrade.reserve_exact` — line 15
- `Komorebi.AVOC.DurableUpgrade.finish_reserved_exact` — line 24
- `Komorebi.AVOC.DurableUpgrade.begin_idempotent` — line 33
- `Komorebi.AVOC.DurableUpgrade.finish_idempotent` — line 54
- `Komorebi.AVOC.DurableUpgrade.abandon_idempotent` — line 75
- `Komorebi.AVOC.DurableUpgrade.finish_does_not_lower_utility` — line 94
- `Komorebi.AVOC.DurableUpgrade.apply_does_not_lower_utility` — line 113
- `Komorebi.AVOC.DurableUpgrade.paid_trace_exact_accounting` — line 129
- `Komorebi.AVOC.DurableUpgrade.replay_has_paid_trace` — line 140
- `Komorebi.AVOC.DurableUpgrade.paid_trace_no_overspend` — line 153
- `Komorebi.AVOC.DurableUpgrade.replay_utility_nondecreasing` — line 166
- `Komorebi.AVOC.DurableUpgrade.restored_is_actual` — line 187
- `Komorebi.AVOC.DurableUpgrade.restored_certificate` — line 197
- `Komorebi.AVOC.DurableUpgrade.restored_idempotent` — line 208

## `AVOC/DurableUpgradeRuntime.lean`

- `Komorebi.AVOC.DurableUpgradeRuntime.certified_active_contract` — line 24
- `Komorebi.AVOC.DurableUpgradeRuntime.certified_spending_bound` — line 27
- `Komorebi.AVOC.DurableUpgradeRuntime.certified_active_decision` — line 31
- `Komorebi.AVOC.DurableUpgradeRuntime.certified_endpoint_net` — line 36

## `AVOC/Dynamic.lean`

- `Komorebi.AVOC.horizonValue_succ_eq_max` — line 31
- `Komorebi.AVOC.bellman_action_exists` — line 41
- `Komorebi.AVOC.horizonValue_eq_qValue_of_optimal` — line 49
- `Komorebi.AVOC.finite_horizon_optimal_action_exists` — line 65

## `AVOC/EpistemicState.lean`

- `Komorebi.AVOC.propose_status_eq` — line 24
- `Komorebi.AVOC.candidates_subset_propose` — line 31
- `Komorebi.AVOC.proposeMany_status_eq` — line 47
- `Komorebi.AVOC.proposeMany_preserves_threshold` — line 58
- `Komorebi.AVOC.proposal_only_cannot_upgrade_to_threshold` — line 68

## `AVOC/ExactRateDistortion.lean`

- `Komorebi.AVOC.valueApproximation_implies_fiberDiameter` — line 33
- `Komorebi.AVOC.mem_valueFiberValues_self` — line 55
- `Komorebi.AVOC.midpointValueDecoder_accurate` — line 76
- `Komorebi.AVOC.exists_valueApproximation_iff_fiberDiameter` — line 120
- `Komorebi.AVOC.exists_exact_value_decoder_iff_fiber_constant` — line 135
- `Komorebi.AVOC.valueCenterCover_of_valueApproximation` — line 165
- `Komorebi.AVOC.decoder_center_card_le_code_card` — line 176
- `Komorebi.AVOC.finite_code_gives_center_cover_card_bound` — line 183
- `Komorebi.AVOC.chosenCoverCenter_mem` — line 201
- `Komorebi.AVOC.chosenCoverCenter_accurate` — line 209
- `Komorebi.AVOC.center_cover_gives_finite_code` — line 219
- `Komorebi.AVOC.center_code_card_eq` — line 234
- `Komorebi.AVOC.finite_code_center_cover_cardinality_duality` — line 242
- `Komorebi.AVOC.raw_value_image_is_centerCover` — line 269
- `Komorebi.AVOC.exists_valueCenterCover_card` — line 279
- `Komorebi.AVOC.exactValueCodeNumber_spec` — line 297
- `Komorebi.AVOC.exactValueCodeNumber_le_cover_card` — line 306
- `Komorebi.AVOC.exactValueCodeNumber_le_finite_code_card` — line 317
- `Komorebi.AVOC.exactValueCodeNumber_attained_by_context` — line 330
- `Komorebi.AVOC.exact_finite_scalar_rate_distortion_optimality` — line 344
- `Komorebi.AVOC.valueCenterCover_mono_tolerance` — line 368
- `Komorebi.AVOC.exactValueCodeNumber_antitone_tolerance` — line 379
- `Komorebi.AVOC.exactValueCodeNumber_le_distinct_value_card` — line 393
- `Komorebi.AVOC.raw_values_subset_zero_centerCover` — line 401
- `Komorebi.AVOC.exactValueCodeNumber_zero_eq_distinct_value_card` — line 416
- `Komorebi.AVOC.exactValueCodeNumber_le_one_of_center` — line 429
- `Komorebi.AVOC.valueCenterCover_nonempty` — line 447
- `Komorebi.AVOC.exactValueCodeNumber_pos` — line 457
- `Komorebi.AVOC.exactValueCodeNumber_eq_one_of_center` — line 467
- `Komorebi.AVOC.separated_card_le_exactValueCodeNumber` — line 484

## `AVOC/ExactRateDistortionExamples.lean`

- `Komorebi.AVOC.threeLevel_exact_code_number` — line 10
- `Komorebi.AVOC.threeLevel_greedy_count` — line 23
- `Komorebi.AVOC.twoCluster_two_center_cover` — line 35
- `Komorebi.AVOC.twoCluster_pair_separated` — line 46
- `Komorebi.AVOC.twoCluster_exact_code_number` — line 54
- `Komorebi.AVOC.twoCluster_greedy_count` — line 72
- `Komorebi.AVOC.oneCluster_exact_code_number` — line 84

## `AVOC/ExecutablePlanner.lean`

- `Komorebi.AVOC.ExecutablePlanner.evaluate_zero` — line 61
- `Komorebi.AVOC.ExecutablePlanner.actionEval_action` — line 64
- `Komorebi.AVOC.ExecutablePlanner.actionEval_score` — line 67
- `Komorebi.AVOC.ExecutablePlanner.actionEval_work` — line 73
- `Komorebi.AVOC.ExecutablePlanner.best_none_iff` — line 79
- `Komorebi.AVOC.ExecutablePlanner.best_spec` — line 86
- `Komorebi.AVOC.ExecutablePlanner.observation_sum` — line 126
- `Komorebi.AVOC.ExecutablePlanner.actionEval_exact` — line 131
- `Komorebi.AVOC.ExecutablePlanner.backupEval_correct` — line 138
- `Komorebi.AVOC.ExecutablePlanner.evaluate_exact` — line 166
- `Komorebi.AVOC.ExecutablePlanner.evaluate_choice_optimal` — line 173

## `AVOC/FilteredObservation.lean`

- `Komorebi.AVOC.Filtered.report_expectation` — line 17
- `Komorebi.AVOC.Filtered.predictive_report` — line 24
- `Komorebi.AVOC.Filtered.predictive_report_expectation` — line 35
- `Komorebi.AVOC.Filtered.posterior_report_scaled` — line 46
- `Komorebi.AVOC.Filtered.posterior_report_mixture` — line 54
- `Komorebi.AVOC.Filtered.rejection_likelihood` — line 66
- `Komorebi.AVOC.Filtered.silent_predictive` — line 75
- `Komorebi.AVOC.Filtered.silent_posterior` — line 80

## `AVOC/FiniteEvents.lean`

- `Komorebi.AVOC.eventProb_nonneg` — line 14
- `Komorebi.AVOC.eventProb_univ` — line 24
- `Komorebi.AVOC.eventProb_mono` — line 31
- `Komorebi.AVOC.eventProb_union_of_disjoint` — line 42
- `Komorebi.AVOC.eventProb_union_le_add` — line 51
- `Komorebi.AVOC.eventProb_inter_le_left` — line 61
- `Komorebi.AVOC.eventProb_inter_le_right` — line 68
- `Komorebi.AVOC.eventProb_le_one` — line 75

## `AVOC/GreedyRateDistortion.lean`

- `Komorebi.AVOC.pointCenterCover_self` — line 14
- `Komorebi.AVOC.exists_pointCenterCover_card` — line 26
- `Komorebi.AVOC.pointCoverNumber_spec` — line 39
- `Komorebi.AVOC.pointCoverNumber_le_cover_card` — line 47
- `Komorebi.AVOC.greedy_center_covers_nonresidual` — line 63
- `Komorebi.AVOC.center_covering_min_excludes_residual` — line 75
- `Komorebi.AVOC.erase_min_center_covers_residual` — line 89
- `Komorebi.AVOC.insert_greedy_center_covers` — line 106
- `Komorebi.AVOC.one_add_residual_coverNumber_le` — line 122
- `Komorebi.AVOC.coverNumber_le_one_add_residual` — line 137
- `Komorebi.AVOC.pointCoverNumber_greedy_recurrence` — line 152
- `Komorebi.AVOC.valueCenterCover_iff_pointCenterCover_image` — line 166
- `Komorebi.AVOC.exactValueCodeNumber_eq_pointCoverNumber` — line 180
- `Komorebi.AVOC.greedyResidual_ssubset` — line 204
- `Komorebi.AVOC.greedyResidual_card_lt` — line 218
- `Komorebi.AVOC.pointCoverNumber_empty` — line 224
- `Komorebi.AVOC.greedyPointCoverCount_eq_pointCoverNumber` — line 245
- `Komorebi.AVOC.greedy_computes_exactValueCodeNumber` — line 261

## `AVOC/GuardedControl.lean`

- `Komorebi.AVOC.Guarded.expectation_mono` — line 22
- `Komorebi.AVOC.Guarded.expectation_const` — line 29
- `Komorebi.AVOC.Guarded.value_zero` — line 46
- `Komorebi.AVOC.Guarded.value_succ` — line 48
- `Komorebi.AVOC.Guarded.optimal_action_exists` — line 53
- `Komorebi.AVOC.Guarded.q_le_value` — line 58
- `Komorebi.AVOC.Guarded.value_eq_q_of_optimal` — line 63
- `Komorebi.AVOC.Guarded.optimalAction_mem` — line 79
- `Komorebi.AVOC.Guarded.optimalAction_max` — line 83
- `Komorebi.AVOC.Guarded.optimalAction_realizes` — line 87
- `Komorebi.AVOC.Guarded.qValue_zero_eq_reward` — line 91
- `Komorebi.AVOC.Guarded.planValue_le_value` — line 112
- `Komorebi.AVOC.Guarded.optimalPlan_legal` — line 136
- `Komorebi.AVOC.Guarded.optimalPlan_value` — line 142
- `Komorebi.AVOC.Guarded.legal_plan_safe` — line 165
- `Komorebi.AVOC.Guarded.safe_optimal_plan_exists` — line 177
- `Komorebi.AVOC.Guarded.mixture_q_le_value` — line 192

## `AVOC/GuardedModelError.lean`

- `Komorebi.AVOC.Guarded.tableQ_le_backup` — line 16
- `Komorebi.AVOC.Guarded.backup_attained` — line 20
- `Komorebi.AVOC.Guarded.backup_optimal_value` — line 30
- `Komorebi.AVOC.Guarded.expectation_uniform_error` — line 34
- `Komorebi.AVOC.Guarded.value_backup_error_of_q_error` — line 51
- `Komorebi.AVOC.Guarded.modelValueBudget_zero` — line 77
- `Komorebi.AVOC.Guarded.modelValueBudget_succ` — line 80
- `Komorebi.AVOC.Guarded.model_q_error_step` — line 98
- `Komorebi.AVOC.Guarded.model_value_error` — line 123
- `Komorebi.AVOC.Guarded.model_q_error` — line 139
- `Komorebi.AVOC.Guarded.model_decoded_policy_regret` — line 149

## `AVOC/GuardedPolicyRegret.lean`

- `Komorebi.AVOC.Guarded.regretBudget_zero` — line 9
- `Komorebi.AVOC.Guarded.regretBudget_succ` — line 12
- `Komorebi.AVOC.Guarded.plan_regret_le` — line 25
- `Komorebi.AVOC.Guarded.policyPlan_legal` — line 65
- `Komorebi.AVOC.Guarded.decoded_action_gap` — line 74
- `Komorebi.AVOC.Guarded.decoded_policy_nearGreedy` — line 86
- `Komorebi.AVOC.Guarded.decoded_policy_regret` — line 102
- `Komorebi.AVOC.Guarded.admissible_approximate_policy_safe` — line 119
- `Komorebi.AVOC.Guarded.constant_policy_budget` — line 125

## `AVOC/HistoryArchive.lean`

- `Komorebi.AVOC.archiveOfHistory_root` — line 26
- `Komorebi.AVOC.archiveOfHistory_snoc` — line 33
- `Komorebi.AVOC.positiveResearchHistory_root` — line 54
- `Komorebi.AVOC.archiveLikelihood_single_historyFactor` — line 63
- `Komorebi.AVOC.evidenceMass_single_historyFactor` — line 74
- `Komorebi.AVOC.positive_history_has_exact_archive_replay` — line 89
- `Komorebi.AVOC.positive_history_replay_at_resolution` — line 176

## `AVOC/HistoryExamples.lean`

- `Komorebi.AVOC.unitBelief_unique` — line 8
- `Komorebi.AVOC.transcriptTrue_ne_transcriptFalse` — line 44
- `Komorebi.AVOC.transcript_compiled_states_equal` — line 50
- `Komorebi.AVOC.transcript_future_values_equal` — line 59

## `AVOC/HistoryState.lean`

- `Komorebi.AVOC.CertifiedResearchState.ext` — line 24
- `Komorebi.AVOC.compileHistory_root` — line 63
- `Komorebi.AVOC.compileHistory_snoc` — line 71
- `Komorebi.AVOC.historyQValue_eq_certifiedQValue_of_prev` — line 143
- `Komorebi.AVOC.historyHorizonValue_eq_certifiedHorizonValue` — line 165
- `Komorebi.AVOC.equal_compiled_history_implies_equal_value` — line 214
- `Komorebi.AVOC.historyQValue_eq_certifiedQValue` — line 227
- `Komorebi.AVOC.history_optimal_iff_compiled_optimal` — line 240

## `AVOC/HorizonBehavior.lean`

- `Komorebi.AVOC.horizonEquivalent_refl` — line 22
- `Komorebi.AVOC.horizonEquivalent_symm` — line 34
- `Komorebi.AVOC.horizonEquivalent_trans` — line 49
- `Komorebi.AVOC.horizonEquivalent_of_succ` — line 77
- `Komorebi.AVOC.horizonEquivalent_preserves_value` — line 93
- `Komorebi.AVOC.horizonControlSufficient_of_succ` — line 129
- `Komorebi.AVOC.horizonControlSufficient_preserves_value` — line 138
- `Komorebi.AVOC.stateControlSufficient_implies_all_horizons` — line 147
- `Komorebi.AVOC.horizonQuotient_is_sufficient` — line 173
- `Komorebi.AVOC.horizonForget_comp_quotientMap` — line 192
- `Komorebi.AVOC.horizonQuotient_refines_previous` — line 202
- `Komorebi.AVOC.horizonQuotient_is_coarsest` — line 214
- `Komorebi.AVOC.horizonQuotient_minimal_characterization` — line 233

## `AVOC/HorizonContext.lean`

- `Komorebi.AVOC.mem_horizonSufficientContexts_iff` — line 18
- `Komorebi.AVOC.horizonSufficientContexts_antitone` — line 30
- `Komorebi.AVOC.minimumCostHorizonContext_exists` — line 56
- `Komorebi.AVOC.minimum_horizon_context_cost_monotone` — line 83

## `AVOC/HorizonDecisionRateDistortion.lean`

- `Komorebi.AVOC.exactHorizonDecisionCodeNumber_le_finite_code_card` — line 40
- `Komorebi.AVOC.exactHorizonDecisionCodeNumber_attained` — line 52
- `Komorebi.AVOC.exactHorizonDecisionCodeNumber_zero_eq_distinct_signature_card` — line 67
- `Komorebi.AVOC.decoded_bellman_optimal_raw_regret_bound` — line 86
- `Komorebi.AVOC.bellman_margin_preserves_decoded_unique_optimum` — line 102
- `Komorebi.AVOC.exact_horizon_decision_signature_optimality_iff` — line 119

## `AVOC/HorizonExamples.lean`

- `Komorebi.AVOC.delayedDistinction_equiv_horizon_one` — line 14
- `Komorebi.AVOC.delayedDistinction_not_equiv_horizon_two` — line 20
- `Komorebi.AVOC.delayedDistinction_strict_horizon_refinement` — line 26

## `AVOC/Investment.lean`

- `Komorebi.AVOC.myopic_prefers_immediate_answer` — line 18
- `Komorebi.AVOC.artifact_investment_positive_over_two_steps` — line 26
- `Komorebi.AVOC.myopic_vs_artifact_investment_reversal` — line 35
- `Komorebi.AVOC.buildTwoStepValue_positive_iff` — line 44

## `AVOC/LiveExecution.lean`

- `Komorebi.AVOC.LiveExecution.move_core` — line 58
- `Komorebi.AVOC.LiveExecution.fault_rejected` — line 63
- `Komorebi.AVOC.LiveExecution.accepted_step_contract` — line 68
- `Komorebi.AVOC.LiveExecution.accepted_step_source_safe` — line 93
- `Komorebi.AVOC.LiveExecution.accepted_step_matches_external` — line 102
- `Komorebi.AVOC.LiveExecution.accepted_step_cost` — line 109
- `Komorebi.AVOC.LiveExecution.replay_source_safe` — line 117
- `Komorebi.AVOC.LiveExecution.replay_initial_source_safe` — line 130
- `Komorebi.AVOC.LiveExecution.replay_no_overspend` — line 135
- `Komorebi.AVOC.LiveExecution.replay_certifies` — line 140
- `Komorebi.AVOC.LiveExecution.replay_append` — line 145
- `Komorebi.AVOC.LiveExecution.fault_suffix_aborts` — line 155
- `Komorebi.AVOC.LiveExecution.replay_then_recommend_allowed` — line 160
- `Komorebi.AVOC.LiveExecution.replay_then_policy_source_safe` — line 165
- `Komorebi.AVOC.LiveExecution.matched_continuation_regret` — line 176
- `Komorebi.AVOC.LiveExecution.acknowledged_admission_has_ticket` — line 190
- `Komorebi.AVOC.LiveExecution.accepted_step_archive_safe` — line 206
- `Komorebi.AVOC.LiveExecution.replay_archive_safe` — line 222
- `Komorebi.AVOC.LiveExecution.replay_initial_archive_safe` — line 235

## `AVOC/LiveExecutionCodec.lean`

- `Komorebi.AVOC.LiveExecution.decoded_replay_safe` — line 64
- `Komorebi.AVOC.LiveExecution.agrees_iff` — line 71
- `Komorebi.AVOC.LiveExecution.changed_pending_rejected` — line 74
- `Komorebi.AVOC.LiveExecution.changed_checked_receipt_rejected` — line 80
- `Komorebi.AVOC.LiveExecution.changed_admission_rejected` — line 86
- `Komorebi.AVOC.LiveExecution.changed_generation_rejected` — line 92
- `Komorebi.AVOC.LiveExecution.decodeReplay_contract` — line 98
- `Komorebi.AVOC.LiveExecution.resume_contract` — line 125
- `Komorebi.AVOC.LiveExecution.resumed_certificate` — line 140
- `Komorebi.AVOC.LiveExecution.actual_admission_has_valid_source` — line 146
- `Komorebi.AVOC.LiveExecution.false_root_cannot_be_confirmed` — line 154

## `AVOC/ModelBridgeExamples.lean`

- `Komorebi.AVOC.ModelBridgeExamples.silent_predictive` — line 15
- `Komorebi.AVOC.ModelBridgeExamples.silent_posterior` — line 19
- `Komorebi.AVOC.ModelBridgeExamples.learned_table_q` — line 54
- `Komorebi.AVOC.ModelBridgeExamples.learned_backup` — line 58
- `Komorebi.AVOC.ModelBridgeExamples.coarse_residual` — line 70
- `Komorebi.AVOC.ModelBridgeExamples.example_transport_zero` — line 102
- `Komorebi.AVOC.ModelBridgeExamples.example_transport_eq_zero` — line 106
- `Komorebi.AVOC.ModelBridgeExamples.example_derived_q_bound` — line 111
- `Komorebi.AVOC.ModelBridgeExamples.raw_value_exact` — line 117
- `Komorebi.AVOC.ModelBridgeExamples.learned_choice_value` — line 132
- `Komorebi.AVOC.ModelBridgeExamples.example_actual_regret` — line 141
- `Komorebi.AVOC.ModelBridgeExamples.example_model_policy_bound` — line 147
- `Komorebi.AVOC.ModelBridgeExamples.example_not_zero_regret` — line 163
- `Komorebi.AVOC.ModelBridgeExamples.residual_cannot_be_ignored` — line 167

## `AVOC/OpenWorld.lean`

- `Komorebi.AVOC.pushforwardBelief_prob` — line 26
- `Komorebi.AVOC.refinement_mass_conservation` — line 34
- `Komorebi.AVOC.pushforwardBelief_comp` — line 44
- `Komorebi.AVOC.diracBelief_self` — line 66
- `Komorebi.AVOC.diracBelief_other` — line 71
- `Komorebi.AVOC.pushforward_dirac` — line 77
- `Komorebi.AVOC.no_universal_belief_recovery_of_collision` — line 91
- `Komorebi.AVOC.sufficient_for_all_bool_queries_implies_injective` — line 114
- `Komorebi.AVOC.injective_implies_sufficient_for_all_bool_queries` — line 128
- `Komorebi.AVOC.sufficient_for_all_bool_queries_iff_injective` — line 138

## `AVOC/ParallelSchedule.lean`

- `Komorebi.AVOC.Scheduling.before_ideal` — line 21
- `Komorebi.AVOC.Scheduling.slot_subset_frontier` — line 31
- `Komorebi.AVOC.Scheduling.slot_card_le_width` — line 44
- `Komorebi.AVOC.Scheduling.active_workers_le_frontier` — line 51
- `Komorebi.AVOC.Scheduling.active_workers_le_width` — line 63
- `Komorebi.AVOC.Scheduling.chain_slot_injective` — line 76
- `Komorebi.AVOC.Scheduling.chain_card_le_rounds` — line 87
- `Komorebi.AVOC.Scheduling.work_capacity_bound` — line 99

## `AVOC/Pareto.lean`

- `Komorebi.AVOC.weaklyDominates_refl` — line 28
- `Komorebi.AVOC.weaklyDominates_trans` — line 32
- `Komorebi.AVOC.score_mono_of_weaklyDominates` — line 41
- `Komorebi.AVOC.score_strict_of_strictlyDominates` — line 55
- `Komorebi.AVOC.positive_score_optimizer_is_paretoMaximal` — line 110
- `Komorebi.AVOC.finite_pareto_frontier_nonempty` — line 129
- `Komorebi.AVOC.weakDominance_preserves_feasibility` — line 141
- `Komorebi.AVOC.strictly_dominated_feasible_action_not_optimal` — line 151

## `AVOC/PlannerExamples.lean`

- `Komorebi.AVOC.PlannerExamples.realization` — line 10
- `Komorebi.AVOC.PlannerExamples.executable_three_step_value` — line 15
- `Komorebi.AVOC.PlannerExamples.branching` — line 19
- `Komorebi.AVOC.PlannerExamples.depth_three_reservation` — line 22
- `Komorebi.AVOC.PlannerExamples.depth_three_within_credit` — line 24
- `Komorebi.AVOC.PlannerExamples.insufficient_credit_rejects` — line 27
- `Komorebi.AVOC.PlannerExamples.affordable_depth_two` — line 31
- `Komorebi.AVOC.PlannerExamples.affordable_depth_three` — line 33
- `Komorebi.AVOC.PlannerExamples.zero_credit_no_search` — line 35
- `Komorebi.AVOC.PlannerExamples.myopic_value_zero` — line 38
- `Komorebi.AVOC.PlannerExamples.executable_demo_safe` — line 43

## `AVOC/PlannerGuarantee.lean`

- `Komorebi.AVOC.ExecutablePlanner.choose_allowed` — line 12
- `Komorebi.AVOC.ExecutablePlanner.value_magnitude` — line 23
- `Komorebi.AVOC.ExecutablePlanner.horizon_value_error` — line 45
- `Komorebi.AVOC.ExecutablePlanner.horizon_q_error` — line 64
- `Komorebi.AVOC.ExecutablePlanner.truncated_action_gap` — line 72
- `Komorebi.AVOC.ExecutablePlanner.feasible_action_gap_bound` — line 89
- `Komorebi.AVOC.ExecutablePlanner.choose_gap` — line 105
- `Komorebi.AVOC.ExecutablePlanner.lookahead_policy_regret` — line 123
- `Komorebi.AVOC.ExecutablePlanner.charged_regret` — line 147

## `AVOC/PlannerRuntime.lean`

- `Komorebi.AVOC.PlannerRuntime.runtime_realizes` — line 65
- `Komorebi.AVOC.PlannerRuntime.runtime_branch_bound` — line 71
- `Komorebi.AVOC.PlannerRuntime.runtime_catalogue_parsed` — line 76
- `Komorebi.AVOC.PlannerRuntime.runtime_initial_safe` — line 79
- `Komorebi.AVOC.PlannerRuntime.runtime_fee_bound` — line 95
- `Komorebi.AVOC.PlannerRuntime.runtime_reward_bound` — line 100
- `Komorebi.AVOC.PlannerRuntime.runtime_recommend_allowed` — line 136
- `Komorebi.AVOC.PlannerRuntime.runtime_recommend_credit` — line 142
- `Komorebi.AVOC.PlannerRuntime.runtime_recommend_gap` — line 149
- `Komorebi.AVOC.PlannerRuntime.runtime_policy_source_safe` — line 159
- `Komorebi.AVOC.PlannerRuntime.runtime_policy_regret` — line 170

## `AVOC/PlannerWork.lean`

- `Komorebi.AVOC.ExecutablePlanner.sum_map_bound` — line 16
- `Komorebi.AVOC.ExecutablePlanner.backupEval_work` — line 26
- `Komorebi.AVOC.ExecutablePlanner.action_work_bound` — line 31
- `Komorebi.AVOC.ExecutablePlanner.evaluate_work_le` — line 43
- `Komorebi.AVOC.ExecutablePlanner.affordableDepth_sound` — line 65
- `Komorebi.AVOC.ExecutablePlanner.affordableDepth_maximal` — line 83
- `Komorebi.AVOC.ExecutablePlanner.runReserved_success` — line 110
- `Komorebi.AVOC.ExecutablePlanner.runReserved_reject` — line 119
- `Komorebi.AVOC.ExecutablePlanner.planning_trace_budget` — line 126

## `AVOC/ProjectedStochasticSufficiency.lean`

- `Komorebi.AVOC.projectedTransitionEquivalent_refl` — line 24
- `Komorebi.AVOC.projectedTransitionEquivalent_symm` — line 32
- `Komorebi.AVOC.projectedTransitionEquivalent_trans` — line 41
- `Komorebi.AVOC.projectedSuff_of_strongSuff` — line 66
- `Komorebi.AVOC.expectedContinuation_eq_of_projectedSuff` — line 82
- `Komorebi.AVOC.stochasticHorizonValue_eq_of_projectedSuff` — line 96
- `Komorebi.AVOC.stochasticQValue_eq_of_projectedSuff` — line 130
- `Komorebi.AVOC.stochasticBellmanOptimalAt_iff_of_projectedSuff` — line 147
- `Komorebi.AVOC.fiberIndicator_fiberConstant` — line 176
- `Komorebi.AVOC.projectedTransitionEquivalent_implies_fiber_mass_eq` — line 186
- `Komorebi.AVOC.fiber_weighted_sum_eq_mass_mul` — line 210
- `Komorebi.AVOC.fiber_mass_eq_implies_projectedTransitionEquivalent` — line 230
- `Komorebi.AVOC.projectedTransitionEquivalent_iff_fiberMassEqual` — line 264

## `AVOC/ProofScheduling.lean`

- `Komorebi.AVOC.Scheduling.ideal_empty` — line 25
- `Komorebi.AVOC.Scheduling.ideal_union` — line 29
- `Komorebi.AVOC.Scheduling.ideal_insert` — line 36
- `Komorebi.AVOC.Scheduling.ready_iff_ideal_insert` — line 46
- `Komorebi.AVOC.Scheduling.ready_incomparable` — line 60
- `Komorebi.AVOC.Scheduling.ready_persists` — line 65
- `Komorebi.AVOC.Scheduling.mem_frontier` — line 78
- `Komorebi.AVOC.Scheduling.frontier_antichain` — line 84
- `Komorebi.AVOC.Scheduling.frontier_disjoint` — line 89
- `Komorebi.AVOC.Scheduling.antichain_subset` — line 95
- `Komorebi.AVOC.Scheduling.frontier_batch_ideal` — line 100
- `Komorebi.AVOC.Scheduling.batch_iff` — line 112
- `Komorebi.AVOC.Scheduling.batch_card_add` — line 133
- `Komorebi.AVOC.Scheduling.antichain_card_le_width` — line 146
- `Komorebi.AVOC.Scheduling.frontier_card_le_width` — line 155
- `Komorebi.AVOC.Scheduling.batch_card_le_frontier` — line 160
- `Komorebi.AVOC.Scheduling.batch_card_le_width` — line 164
- `Komorebi.AVOC.Scheduling.legal_nil` — line 173
- `Komorebi.AVOC.Scheduling.legal_cons` — line 175
- `Komorebi.AVOC.Scheduling.legal_final_ideal` — line 178
- `Komorebi.AVOC.Scheduling.legal_fresh` — line 186
- `Komorebi.AVOC.Scheduling.legal_nodup` — line 197
- `Komorebi.AVOC.Scheduling.legal_topological` — line 207

## `AVOC/QRateDistortion.lean`

- `Komorebi.AVOC.qSignatureApproximation_implies_fiberDiameter` — line 35
- `Komorebi.AVOC.mem_qFiberValues_self` — line 64
- `Komorebi.AVOC.midpointQDecoder_accurate` — line 84
- `Komorebi.AVOC.exists_qSignatureApproximation_iff_fiberDiameter` — line 125
- `Komorebi.AVOC.exists_exact_q_decoder_iff_fiber_constant` — line 139
- `Komorebi.AVOC.q_coordinate_gap_forces_distinction` — line 157
- `Komorebi.AVOC.qSignatureApproximation_injectiveOn_separated` — line 177
- `Komorebi.AVOC.q_separated_card_le_code_card` — line 191
- `Komorebi.AVOC.abstract_q_optimal_raw_regret_bound` — line 225
- `Komorebi.AVOC.abstract_q_optimal_regret_vs_raw_optimum` — line 241
- `Komorebi.AVOC.q_margin_preserves_unique_optimum` — line 256
- `Komorebi.AVOC.exact_q_signature_optimality_iff` — line 271

## `AVOC/QRateDistortionExamples.lean`

- `Komorebi.AVOC.crossedValue_exact_code_number_one` — line 14
- `Komorebi.AVOC.crossedQ_false_false_optimal` — line 21
- `Komorebi.AVOC.crossedQ_true_true_optimal` — line 27
- `Komorebi.AVOC.crossedQ_signatures_ne` — line 33
- `Komorebi.AVOC.crossedQ_exact_code_number_two` — line 40
- `Komorebi.AVOC.q_context_strictly_richer_than_scalar_value_context` — line 50
- `Komorebi.AVOC.crossedQ_no_exact_unit_context` — line 57
- `Komorebi.AVOC.crossedQ_half_tolerance_one_code` — line 68

## `AVOC/QRateDistortionFinite.lean`

- `Komorebi.AVOC.qCenterCover_of_qSignatureApproximation` — line 17
- `Komorebi.AVOC.q_decoder_center_card_le_code_card` — line 31
- `Komorebi.AVOC.finite_q_code_gives_center_cover_card_bound` — line 39
- `Komorebi.AVOC.chosenQCoverCenter_mem` — line 59
- `Komorebi.AVOC.chosenQCoverCenter_accurate` — line 67
- `Komorebi.AVOC.q_center_cover_gives_finite_code` — line 75
- `Komorebi.AVOC.q_center_code_card_eq` — line 90
- `Komorebi.AVOC.finite_q_code_center_cover_cardinality_duality` — line 96
- `Komorebi.AVOC.raw_q_image_is_centerCover` — line 119
- `Komorebi.AVOC.exists_qCenterCover_card` — line 130
- `Komorebi.AVOC.exactQCodeNumber_spec` — line 148
- `Komorebi.AVOC.exactQCodeNumber_le_cover_card` — line 157
- `Komorebi.AVOC.exactQCodeNumber_le_finite_code_card` — line 168
- `Komorebi.AVOC.exactQCodeNumber_attained_by_context` — line 180
- `Komorebi.AVOC.exact_finite_q_rate_distortion_optimality` — line 193
- `Komorebi.AVOC.qCenterCover_mono_tolerance` — line 217
- `Komorebi.AVOC.exactQCodeNumber_antitone_tolerance` — line 227
- `Komorebi.AVOC.raw_q_signatures_subset_zero_centerCover` — line 240
- `Komorebi.AVOC.exactQCodeNumber_zero_eq_distinct_signature_card` — line 257
- `Komorebi.AVOC.q_separated_card_le_exactQCodeNumber` — line 271

## `AVOC/QValueBridge.lean`

- `Komorebi.AVOC.qSignatureMax_action_exists` — line 16
- `Komorebi.AVOC.q_le_qSignatureMax` — line 29
- `Komorebi.AVOC.qSignatureApproximation_implies_maxValueApproximation` — line 38
- `Komorebi.AVOC.exactValueCodeNumber_le_exactQCodeNumber` — line 59
- `Komorebi.AVOC.exact_scalar_context_never_richer_than_q_context` — line 77

## `AVOC/RateDistortionExamples.lean`

- `Komorebi.AVOC.threeLevel_pairwise_separated` — line 14
- `Komorebi.AVOC.threeLevel_requires_three_codes` — line 21

## `AVOC/RateDistortionLower.lean`

- `Komorebi.AVOC.value_gap_forces_distinction` — line 19
- `Komorebi.AVOC.valueApproximation_injectiveOn_separated` — line 52
- `Komorebi.AVOC.separated_card_le_code_card` — line 67
- `Komorebi.AVOC.horizon_value_gap_forces_context_distinction` — line 92
- `Komorebi.AVOC.exact_value_representation_separates_unequal` — line 106
- `Komorebi.AVOC.approximate_abstraction_large_gap_forces_distinction` — line 125
- `Komorebi.AVOC.approximate_abstraction_separated_card_lower_bound` — line 146

## `AVOC/RecoveryCodec.lean`

- `Komorebi.AVOC.CommitRecovery.decodeCheckpoint_safe` — line 28
- `Komorebi.AVOC.CommitRecovery.resumeCheckpoint_contract` — line 46
- `Komorebi.AVOC.CommitRecovery.recoverDecoded_contract` — line 66
- `Komorebi.AVOC.CommitRecovery.recoverDecoded_no_overspend` — line 78

## `AVOC/RecoveryExamples.lean`

- `Komorebi.AVOC.RecoveryExamples.preparation_example` — line 14
- `Komorebi.AVOC.RecoveryExamples.atomic_publish_example` — line 18
- `Komorebi.AVOC.RecoveryExamples.identical_view_different_commit_count` — line 22
- `Komorebi.AVOC.RecoveryExamples.no_view_only_commit_count_decoder` — line 27
- `Komorebi.AVOC.RecoveryExamples.repeat_publication_example` — line 36
- `Komorebi.AVOC.RecoveryExamples.unfinished_does_not_become_report` — line 41

## `AVOC/RecursiveSynthesis.lean`

- `Komorebi.AVOC.SemanticSynthesis.covers_refl` — line 11
- `Komorebi.AVOC.SemanticSynthesis.covers_trans` — line 14
- `Komorebi.AVOC.SemanticSynthesis.compact_covers_all` — line 21
- `Komorebi.AVOC.SemanticSynthesis.equivalent_neg` — line 24
- `Komorebi.AVOC.SemanticSynthesis.equivalent_conjunction` — line 27
- `Komorebi.AVOC.SemanticSynthesis.equivalent_disjunction` — line 31
- `Komorebi.AVOC.SemanticSynthesis.equivalent_exclusive` — line 35
- `Komorebi.AVOC.SemanticSynthesis.pairs_covers` — line 39
- `Komorebi.AVOC.SemanticSynthesis.expand_covers` — line 54
- `Komorebi.AVOC.SemanticSynthesis.pairs_mono` — line 77
- `Komorebi.AVOC.SemanticSynthesis.expand_mono` — line 83
- `Komorebi.AVOC.SemanticSynthesis.representative_in_frozen` — line 100
- `Komorebi.AVOC.SemanticSynthesis.recursive_coverage` — line 108
- `Komorebi.AVOC.SemanticSynthesis.retained_knowledge_not_lost` — line 113
- `Komorebi.AVOC.SemanticSynthesis.answer_sound` — line 122
- `Komorebi.AVOC.SemanticSynthesis.answer_no_larger` — line 125
- `Komorebi.AVOC.SemanticSynthesis.answer_bounded_optimal` — line 128
- `Komorebi.AVOC.SemanticSynthesis.same_optimum_as_frozen` — line 135
- `Komorebi.AVOC.SemanticSynthesis.compact_preserves_query_optimum` — line 148

## `AVOC/Refinement.lean`

- `Komorebi.AVOC.mem_collisionPairs_iff` — line 20
- `Komorebi.AVOC.sufficient_collisionPairs_empty` — line 29
- `Komorebi.AVOC.collisionPairs_empty_implies_sufficient` — line 42
- `Komorebi.AVOC.sufficient_iff_collisionPairs_empty` — line 57
- `Komorebi.AVOC.collisionPairs_subset_of_refines` — line 65
- `Komorebi.AVOC.collisionPairs_ssubset_of_refines_and_separates` — line 84
- `Komorebi.AVOC.collisionCard_strictly_decreases` — line 105
- `Komorebi.AVOC.strict_nat_descent_length_bound` — line 120
- `Komorebi.AVOC.collision_guided_refinement_length_bound` — line 142

## `AVOC/RepresentationLattice.lean`

- `Komorebi.AVOC.join_refines_left` — line 14
- `Komorebi.AVOC.join_refines_right` — line 21
- `Komorebi.AVOC.refines_join_of_refines_both` — line 29
- `Komorebi.AVOC.refines_join_iff` — line 41
- `Komorebi.AVOC.join_sufficient_of_left` — line 54
- `Komorebi.AVOC.join_sufficient_of_right` — line 63
- `Komorebi.AVOC.join_preserves_two_tasks` — line 72

## `AVOC/ResearchController.lean`

- `Komorebi.AVOC.Research.accepted_local_rule` — line 50
- `Komorebi.AVOC.Research.mem_actions` — line 76
- `Komorebi.AVOC.Research.stop_allowed` — line 86
- `Komorebi.AVOC.Research.actions_nonempty` — line 89
- `Komorebi.AVOC.Research.allowed_fee_le` — line 93
- `Komorebi.AVOC.Research.attempt_completed_unchanged` — line 118
- `Komorebi.AVOC.Research.attempt_queues` — line 122
- `Komorebi.AVOC.Research.rejected_completed_unchanged` — line 126
- `Komorebi.AVOC.Research.passing_receipt_admits` — line 130
- `Komorebi.AVOC.Research.new_completion_requires_verification` — line 136
- `Komorebi.AVOC.Research.step_safe` — line 156
- `Komorebi.AVOC.Research.step_budget_accounting` — line 190
- `Komorebi.AVOC.Research.step_budget_le` — line 196
- `Komorebi.AVOC.Research.step_spent_increment` — line 200
- `Komorebi.AVOC.Research.step_budgetSafe` — line 207
- `Komorebi.AVOC.Research.controller_preserves` — line 240
- `Komorebi.AVOC.Research.controller_budget_preserves` — line 245
- `Komorebi.AVOC.Research.certified_budget_optimal_plan_exists` — line 253

## `AVOC/ResearchControllerExamples.lean`

- `Komorebi.AVOC.Research.Examples.one_ready` — line 35
- `Komorebi.AVOC.Research.Examples.initial_safe` — line 41
- `Komorebi.AVOC.Research.Examples.initial_attempt_allowed` — line 46
- `Komorebi.AVOC.Research.Examples.initial_verify_forbidden` — line 49
- `Komorebi.AVOC.Research.Examples.predictive_some` — line 53
- `Komorebi.AVOC.Research.Examples.predictive_none` — line 59
- `Komorebi.AVOC.Research.Examples.initial_some_positive` — line 65
- `Komorebi.AVOC.Research.Examples.afterSignal_belief_true` — line 71
- `Komorebi.AVOC.Research.Examples.posterior_one_is_not_admission` — line 82
- `Komorebi.AVOC.Research.Examples.afterSignal_verify_allowed` — line 86
- `Komorebi.AVOC.Research.Examples.successful_verification_completes` — line 91
- `Komorebi.AVOC.Research.Examples.failed_verification_does_not_complete` — line 96
- `Komorebi.AVOC.Research.Examples.successful_spend_exact` — line 101
- `Komorebi.AVOC.Research.Examples.exhausted_attempt_forbidden` — line 105
- `Komorebi.AVOC.Research.Examples.adaptivePlan_legal` — line 119
- `Komorebi.AVOC.Research.Examples.reward_verify_formula` — line 128
- `Komorebi.AVOC.Research.Examples.reward_afterSignal_verify` — line 134
- `Komorebi.AVOC.Research.Examples.adaptivePlan_value` — line 138
- `Komorebi.AVOC.Research.Examples.two_step_value_positive` — line 163
- `Komorebi.AVOC.Research.Examples.adaptivePlan_safe` — line 168
- `Komorebi.AVOC.Research.Examples.one_step_value_zero` — line 175
- `Komorebi.AVOC.Research.Examples.afterNoSignal_belief_true` — line 191
- `Komorebi.AVOC.Research.Examples.repeated_attempt_forbidden` — line 207
- `Komorebi.AVOC.Research.Examples.afterSignal_one_step_value` — line 214
- `Komorebi.AVOC.Research.Examples.afterNoSignal_one_step_value` — line 234
- `Komorebi.AVOC.Research.Examples.initial_attempt_two_step_q` — line 248
- `Komorebi.AVOC.Research.Examples.two_step_value_exact` — line 263
- `Komorebi.AVOC.Research.Examples.false_root_rule_impossible` — line 283
- `Komorebi.AVOC.Research.Examples.false_root_gate_cannot_pass` — line 291

## `AVOC/ResearchModelGuarantee.lean`

- `Komorebi.AVOC.Research.certified_bayesian_model_policy` — line 12

## `AVOC/ResearchPolicy.lean`

- `Komorebi.AVOC.Research.allowed_when_halted` — line 10
- `Komorebi.AVOC.Research.new_admission_has_rule` — line 14
- `Komorebi.AVOC.Research.new_admission_is_true` — line 22
- `Komorebi.AVOC.Research.halted_value_zero` — line 29
- `Komorebi.AVOC.Research.stop_q_zero` — line 45
- `Komorebi.AVOC.Research.controller_value_nonneg` — line 54
- `Komorebi.AVOC.Research.stop_optimal_of_nonpositive_q` — line 66
- `Komorebi.AVOC.Research.legal_trace_preserves` — line 88
- `Komorebi.AVOC.Research.legal_trace_certifies` — line 98
- `Komorebi.AVOC.Research.legal_trace_no_overspend` — line 104
- `Komorebi.AVOC.Research.execute_spent` — line 112
- `Komorebi.AVOC.Research.legal_trace_fee_bound` — line 122
- `Komorebi.AVOC.Research.certified_approximate_policy` — line 132

## `AVOC/Retrospective.lean`

- `Komorebi.AVOC.forgetProposals_known` — line 22
- `Komorebi.AVOC.forgetProposals_proposed` — line 25
- `Komorebi.AVOC.forgetProposals_residual` — line 28
- `Komorebi.AVOC.proposal_is_refinement` — line 33
- `Komorebi.AVOC.retrospectiveLikelihoodTrue_nonneg` — line 48
- `Komorebi.AVOC.retrospectiveLikelihoodFalse_nonneg` — line 52
- `Komorebi.AVOC.retrospectiveLikelihoodTrue_mass` — line 56
- `Komorebi.AVOC.retrospectiveLikelihoodFalse_mass` — line 62
- `Komorebi.AVOC.retrospectiveLikelihoodTrue_positive` — line 68
- `Komorebi.AVOC.retrospectiveLikelihoodFalse_positive` — line 73
- `Komorebi.AVOC.retrospectivePosteriorTrue_true` — line 79
- `Komorebi.AVOC.retrospectivePosteriorFalse_true` — line 91
- `Komorebi.AVOC.retrospectiveFinePosteriors_ne` — line 103
- `Komorebi.AVOC.pushforward_constantUnit` — line 115
- `Komorebi.AVOC.retrospectiveCoarsePosteriors_eq` — line 126
- `Komorebi.AVOC.no_retrospective_decoder_for_evidence_split` — line 137

## `AVOC/RetryBayesian.lean`

- `Komorebi.AVOC.RetryBayesian.mean_nonneg` — line 22
- `Komorebi.AVOC.RetryBayesian.mean_le_one` — line 25
- `Komorebi.AVOC.RetryBayesian.fault_mass` — line 32
- `Komorebi.AVOC.RetryBayesian.afterFault_formula` — line 44
- `Komorebi.AVOC.RetryBayesian.impossible_fault_fallback` — line 51
- `Komorebi.AVOC.RetryBayesian.second_moment_ge_mean_square` — line 56
- `Komorebi.AVOC.RetryBayesian.mean_afterFault_le` — line 74
- `Komorebi.AVOC.RetryBayesian.immediate_nonincreasing` — line 113
- `Komorebi.AVOC.RetryBayesian.no_revival` — line 120
- `Komorebi.AVOC.RetryBayesian.exact_retry_threshold` — line 126
- `Komorebi.AVOC.RetryBayesian.recommend_is_optimal_choice` — line 135
- `Komorebi.AVOC.RetryBayesian.insufficient_credit_abandons` — line 139
- `Komorebi.AVOC.RetryBayesian.no_slots_abandons` — line 144
- `Komorebi.AVOC.RetryBayesian.fee_exceeds_expected_gain_zero` — line 148
- `Komorebi.AVOC.RetryBayesian.enabled_consumes_slot` — line 155
- `Komorebi.AVOC.RetryBayesian.enabled_charges_fee` — line 161

## `AVOC/RetryControl.lean`

- `Komorebi.AVOC.Retry.retryValue_zero` — line 66
- `Komorebi.AVOC.Retry.retryValue_nonneg` — line 68
- `Komorebi.AVOC.Retry.disabled_value` — line 73
- `Komorebi.AVOC.Retry.terminal_value` — line 76
- `Komorebi.AVOC.Retry.abandon_q` — line 88
- `Komorebi.AVOC.Retry.retry_q` — line 95
- `Komorebi.AVOC.Retry.guarded_value_eq` — line 102
- `Komorebi.AVOC.Retry.selector_allowed` — line 134
- `Komorebi.AVOC.Retry.selector_realizes` — line 144
- `Komorebi.AVOC.Retry.selectedPlan_legal` — line 166
- `Komorebi.AVOC.Retry.selectedPlan_value` — line 170
- `Komorebi.AVOC.Retry.all_legal_plans_le_selected` — line 182
- `Komorebi.AVOC.Retry.no_revival_value_zero` — line 192
- `Komorebi.AVOC.Retry.profitable_trial` — line 203
- `Komorebi.AVOC.Retry.choose_threshold` — line 209

## `AVOC/RetryDecisionCodec.lean`

- `Komorebi.AVOC.RetryDecisionCodec.runtime_choice_correct` — line 63
- `Komorebi.AVOC.RetryDecisionCodec.runtime_value_optimal` — line 71
- `Komorebi.AVOC.RetryDecisionCodec.observeFault_ledger_unchanged` — line 98

## `AVOC/RetryEvaluation.lean`

- `Komorebi.AVOC.Retry.evaluate_value` — line 21
- `Komorebi.AVOC.Retry.evaluate_choice` — line 31
- `Komorebi.AVOC.Retry.evaluate_work_bound` — line 45
- `Komorebi.AVOC.Retry.evaluate_guarded_exact` — line 57
- `Komorebi.AVOC.Retry.evaluate_choice_is_threshold` — line 63

## `AVOC/RetryExamples.lean`

- `Komorebi.AVOC.RetryExamples.initial_resolve_probability` — line 22
- `Komorebi.AVOC.RetryExamples.posterior_fast_after_fault` — line 25
- `Komorebi.AVOC.RetryExamples.posterior_slow_after_fault` — line 29
- `Komorebi.AVOC.RetryExamples.fault_resolve_probability` — line 33
- `Komorebi.AVOC.RetryExamples.initially_retry` — line 39
- `Komorebi.AVOC.RetryExamples.after_fault_abandon` — line 42
- `Komorebi.AVOC.RetryExamples.fault_future_value_zero` — line 45
- `Komorebi.AVOC.RetryExamples.persistent_all_positive_horizons` — line 51
- `Komorebi.AVOC.RetryExamples.iid_fault_does_not_change_prior` — line 68
- `Komorebi.AVOC.RetryExamples.iid_three_attempt_value` — line 74
- `Komorebi.AVOC.RetryExamples.same_first_probability_different_value` — line 78
- `Komorebi.AVOC.RetryExamples.improving_one_step_bad` — line 96
- `Komorebi.AVOC.RetryExamples.improving_two_steps_worthwhile` — line 98
- `Komorebi.AVOC.RetryExamples.improving_not_no_revival` — line 101
- `Komorebi.AVOC.RetryExamples.improving_retry_despite_negative_immediate` — line 106
- `Komorebi.AVOC.RetryExamples.example_ledger_safe` — line 113
- `Komorebi.AVOC.RetryExamples.example_retry_charges_fresh` — line 116
- `Komorebi.AVOC.RetryExamples.example_after_fault_abandons_without_refund` — line 122

## `AVOC/RetryLedger.lean`

- `Komorebi.AVOC.RetryLedger.enabled_iff_room` — line 14
- `Komorebi.AVOC.RetryLedger.authorize_safe` — line 32
- `Komorebi.AVOC.RetryLedger.retry_recommendation_affordable` — line 42
- `Komorebi.AVOC.RetryLedger.recommended_retry_exists` — line 51
- `Komorebi.AVOC.RetryLedger.applyAdvice_preserves_science` — line 81

## `AVOC/ScheduleCompletion.lean`

- `Komorebi.AVOC.Scheduling.legal_of_topological` — line 10
- `Komorebi.AVOC.Scheduling.legal_iff_structural` — line 40
- `Komorebi.AVOC.Scheduling.complete_legal_iff_linearExtension` — line 55
- `Komorebi.AVOC.Scheduling.legal_of_all_ready` — line 67
- `Komorebi.AVOC.Scheduling.frontier_batch_serializable` — line 80
- `Komorebi.AVOC.Scheduling.legal_append_iff` — line 90
- `Komorebi.AVOC.Scheduling.frontier_nonempty` — line 99
- `Komorebi.AVOC.Scheduling.remaining_strictly_decreases` — line 118
- `Komorebi.AVOC.Scheduling.exists_legal_completion` — line 129
- `Komorebi.AVOC.Scheduling.exists_linearExtension` — line 150
- `Komorebi.AVOC.Scheduling.completed_card_add` — line 154
- `Komorebi.AVOC.Scheduling.legal_completion_length` — line 162

## `AVOC/SchedulingCertificates.lean`

- `Komorebi.AVOC.Scheduling.ready_with_rule_proves` — line 16
- `Komorebi.AVOC.Scheduling.certified_insert` — line 23
- `Komorebi.AVOC.Scheduling.checked_step_preserves` — line 30
- `Komorebi.AVOC.Scheduling.checked_batch_preserves` — line 36
- `Komorebi.AVOC.Scheduling.legal_rules_certify` — line 46
- `Komorebi.AVOC.Scheduling.certified_completion` — line 56
- `Komorebi.AVOC.Scheduling.ready_does_not_imply_truth` — line 67

## `AVOC/SchedulingExamples.lean`

- `Komorebi.AVOC.Scheduling.Examples.root_ideal` — line 14
- `Komorebi.AVOC.Scheduling.Examples.diamond_frontier` — line 18
- `Komorebi.AVOC.Scheduling.Examples.diamond_forward` — line 25
- `Komorebi.AVOC.Scheduling.Examples.diamond_swapped` — line 29
- `Komorebi.AVOC.Scheduling.Examples.diamond_bad_order` — line 33
- `Komorebi.AVOC.Scheduling.Examples.antichain_not_enough` — line 37
- `Komorebi.AVOC.Scheduling.Examples.diamond_width` — line 42
- `Komorebi.AVOC.Scheduling.Examples.three_chain_requires_three_rounds` — line 60
- `Komorebi.AVOC.Scheduling.Examples.diamond_frontier_has_two_tasks` — line 69

## `AVOC/SemanticCostCertificate.lean`

- `Komorebi.AVOC.CostCertificate.lower_bound` — line 34
- `Komorebi.AVOC.CostCertificate.witness_global_minimum` — line 56
- `Komorebi.AVOC.CostCertificate.cost_is_attained_minimum` — line 63
- `Komorebi.AVOC.CostCertificate.exact_cost_unique` — line 71
- `Komorebi.AVOC.CostCertificate.lower_upper_sandwich` — line 82
- `Komorebi.AVOC.CostCertificate.no_further_node_saving` — line 88

## `AVOC/SemanticIndex.lean`

- `Komorebi.AVOC.SemanticSynthesis.signature_eq_iff` — line 10
- `Komorebi.AVOC.SemanticSynthesis.dominates_refl` — line 29
- `Komorebi.AVOC.SemanticSynthesis.dominates_trans` — line 31
- `Komorebi.AVOC.SemanticSynthesis.equal_bits_equivalent` — line 34
- `Komorebi.AVOC.SemanticSynthesis.pick_origin` — line 40
- `Komorebi.AVOC.SemanticSynthesis.pick_dominates_left` — line 44
- `Komorebi.AVOC.SemanticSynthesis.pick_dominates_right` — line 51
- `Komorebi.AVOC.SemanticSynthesis.insert_origin` — line 62
- `Komorebi.AVOC.SemanticSynthesis.insert_covers_new` — line 81
- `Komorebi.AVOC.SemanticSynthesis.insert_covers_old` — line 91
- `Komorebi.AVOC.SemanticSynthesis.insert_length` — line 107
- `Komorebi.AVOC.SemanticSynthesis.collect_covers_old` — line 119
- `Komorebi.AVOC.SemanticSynthesis.collect_covers_new` — line 128
- `Komorebi.AVOC.SemanticSynthesis.collect_origin` — line 140
- `Komorebi.AVOC.SemanticSynthesis.collect_length` — line 151
- `Komorebi.AVOC.SemanticSynthesis.compact_origin` — line 164
- `Komorebi.AVOC.SemanticSynthesis.compact_covers` — line 169
- `Komorebi.AVOC.SemanticSynthesis.compact_codes_origin` — line 175
- `Komorebi.AVOC.SemanticSynthesis.compact_length` — line 181
- `Komorebi.AVOC.SemanticSynthesis.pick_bits` — line 187
- `Komorebi.AVOC.SemanticSynthesis.insert_unique` — line 193
- `Komorebi.AVOC.SemanticSynthesis.collect_unique` — line 212
- `Komorebi.AVOC.SemanticSynthesis.compact_unique` — line 218
- `Komorebi.AVOC.SemanticSynthesis.bitVectors_complete` — line 225
- `Komorebi.AVOC.SemanticSynthesis.bitVectors_length` — line 231
- `Komorebi.AVOC.SemanticSynthesis.unique_entries_at_most_256` — line 236
- `Komorebi.AVOC.SemanticSynthesis.compact_at_most_256` — line 247

## `AVOC/SemanticLibrary.lean`

- `Komorebi.AVOC.SemanticLibrary.closure_obligation_count` — line 10
- `Komorebi.AVOC.SemanticLibrary.import_conservation` — line 29
- `Komorebi.AVOC.SemanticLibrary.import_budget` — line 36
- `Komorebi.AVOC.SemanticLibrary.unfunded_import` — line 41
- `Komorebi.AVOC.SemanticLibrary.funded_invalid_still_charged` — line 48
- `Komorebi.AVOC.SemanticLibrary.accepted_rows_exact` — line 55
- `Komorebi.AVOC.SemanticLibrary.accepted_import_valid` — line 64
- `Komorebi.AVOC.SemanticLibrary.accepted_import_global` — line 75
- `Komorebi.AVOC.SemanticLibrary.query_conservation` — line 94
- `Komorebi.AVOC.SemanticLibrary.paid_query_certified` — line 99
- `Komorebi.AVOC.SemanticLibrary.import_query_accounting` — line 108
- `Komorebi.AVOC.SemanticLibrary.maximum_future_saving` — line 118
- `Komorebi.AVOC.SemanticLibrary.stop_if_cost_covers_all_saving` — line 125
- `Komorebi.AVOC.SemanticLibrary.globally_minimum_no_positive_saving` — line 131
- `Komorebi.AVOC.SemanticLibrary.many_conservation` — line 151
- `Komorebi.AVOC.SemanticLibrary.many_sound` — line 168
- `Komorebi.AVOC.SemanticLibrary.many_charges_exact` — line 175
- `Komorebi.AVOC.SemanticLibrary.import_many_accounting` — line 182

## `AVOC/SemanticLibraryCodec.lean`

- `Komorebi.AVOC.LibraryCodec.load_accepted_source` — line 74
- `Komorebi.AVOC.LibraryCodec.loaded_query_global` — line 86

## `AVOC/SemanticPromotion.lean`

- `Komorebi.AVOC.SemanticSynthesis.bank_submission_semantics` — line 20
- `Komorebi.AVOC.SemanticSynthesis.bank_submission_replay` — line 25
- `Komorebi.AVOC.SemanticSynthesis.bank_submission_total_cost` — line 34

## `AVOC/SemanticSearchBudget.lean`

- `Komorebi.AVOC.SemanticSynthesis.paid_no_overspend` — line 103
- `Komorebi.AVOC.SemanticSynthesis.unfunded_layer_not_run` — line 107
- `Komorebi.AVOC.SemanticSynthesis.unfunded_seed_no_search` — line 111
- `Komorebi.AVOC.SemanticSynthesis.bank_capacity` — line 115
- `Komorebi.AVOC.SemanticSynthesis.bank_query_sound` — line 118
- `Komorebi.AVOC.SemanticSynthesis.bank_query_bounded_optimal` — line 121
- `Komorebi.AVOC.SemanticSynthesis.bank_query_same_frozen` — line 126
- `Komorebi.AVOC.SemanticSynthesis.paid_certified_result` — line 138

## `AVOC/SemanticSynthesisExamples.lean`

- `Komorebi.AVOC.SemanticSynthesis.same_size_not_same_semantics` — line 10
- `Komorebi.AVOC.SemanticSynthesis.one_sample_not_a_signature` — line 16
- `Komorebi.AVOC.SemanticSynthesis.compact_keeps_smaller_equivalent` — line 23
- `Komorebi.AVOC.SemanticSynthesis.arbitrary_equivalent_representative_can_be_worse` — line 26
- `Komorebi.AVOC.SemanticSynthesis.first_layer_has_seventeen` — line 32
- `Komorebi.AVOC.SemanticSynthesis.feedback_second_layer_count` — line 34
- `Komorebi.AVOC.SemanticSynthesis.frozen_second_layer_count` — line 39
- `Komorebi.AVOC.SemanticSynthesis.feedback_emits_strictly_fewer_at_second_layer` — line 43
- `Komorebi.AVOC.SemanticSynthesis.zero_credit_does_not_search` — line 48

## `AVOC/SemanticSynthesisWork.lean`

- `Komorebi.AVOC.SemanticSynthesis.insertMeasured_refines` — line 14
- `Komorebi.AVOC.SemanticSynthesis.insertMeasured_probes` — line 21
- `Komorebi.AVOC.SemanticSynthesis.collectMeasured_refines` — line 34
- `Komorebi.AVOC.SemanticSynthesis.collectMeasured_probes` — line 40
- `Komorebi.AVOC.SemanticSynthesis.work_charge_add` — line 68
- `Komorebi.AVOC.SemanticSynthesis.indexed_refines` — line 80
- `Komorebi.AVOC.SemanticSynthesis.indexed_unique` — line 83
- `Komorebi.AVOC.SemanticSynthesis.indexed_coverage` — line 87
- `Komorebi.AVOC.SemanticSynthesis.indexed_probe_bound` — line 91
- `Komorebi.AVOC.SemanticSynthesis.sum_nodes_le` — line 94
- `Komorebi.AVOC.SemanticSynthesis.indexed_charge_bound` — line 107
- `Komorebi.AVOC.SemanticSynthesis.learnedBuild_refines` — line 134
- `Komorebi.AVOC.SemanticSynthesis.learnedBuild_capacity` — line 139
- `Komorebi.AVOC.SemanticSynthesis.learnedBuild_optimum` — line 143
- `Komorebi.AVOC.SemanticSynthesis.frozenBuild_raw` — line 162
- `Komorebi.AVOC.SemanticSynthesis.frozenBuild_indexed` — line 167
- `Komorebi.AVOC.SemanticSynthesis.equal_executed_optima` — line 172

## `AVOC/Specification.lean`

- `Komorebi.AVOC.taskSufficient_iff_exists_downstream_recovery` — line 16
- `Komorebi.AVOC.specification_collision_obstructs_every_downstream` — line 27
- `Komorebi.AVOC.insufficient_specification_has_no_exact_downstream` — line 42
- `Komorebi.AVOC.sound_gate_plus_semantic_fidelity` — line 60
- `Komorebi.AVOC.semantic_collision_obstructs_fidelity` — line 72
- `Komorebi.AVOC.no_sound_gate_can_supply_missing_semantic_fidelity` — line 88
- `Komorebi.AVOC.specification_collision_obstructs_verifier_ensemble` — line 107
- `Komorebi.AVOC.exact_ensemble_recovery_implies_specification_sufficient` — line 122

## `AVOC/State.lean`

- `Komorebi.AVOC.researchDebt_nonincreasing_of_subset` — line 17
- `Komorebi.AVOC.resolving_positive_claim_strictly_lowers_debt` — line 31
- `Komorebi.AVOC.ClaimStatus.atLeast_trans` — line 66

## `AVOC/StateDependentControl.lean`

- `Komorebi.AVOC.stateHorizonValue_succ_eq_max` — line 32
- `Komorebi.AVOC.state_bellman_action_exists` — line 41
- `Komorebi.AVOC.stateHorizonValue_eq_qValue_of_optimal` — line 50
- `Komorebi.AVOC.stateQValue_le_horizonValue_succ` — line 66
- `Komorebi.AVOC.stateControlSufficient_id` — line 87
- `Komorebi.AVOC.action_mismatch_obstructs_stateControlSufficiency` — line 96
- `Komorebi.AVOC.stateHorizonValue_eq_of_stateControlSufficient` — line 108
- `Komorebi.AVOC.stateBellmanOptimalAt_iff_of_stateControlSufficient` — line 145
- `Komorebi.AVOC.quotientStateControlSystem_actions_eq` — line 187
- `Komorebi.AVOC.quotientStateControlSystem_reward_eq` — line 197
- `Komorebi.AVOC.quotientStateControlSystem_transition_eq` — line 212
- `Komorebi.AVOC.quotientStateControlSystem_horizonValue_eq` — line 229

## `AVOC/Stochastic.lean`

- `Komorebi.AVOC.stochasticHorizonValue_succ_eq_max` — line 47
- `Komorebi.AVOC.stochastic_bellman_action_exists` — line 56
- `Komorebi.AVOC.stochasticHorizonValue_eq_qValue_of_optimal` — line 65
- `Komorebi.AVOC.stochastic_finite_horizon_optimal_action_exists` — line 81
- `Komorebi.AVOC.expectedContinuation_mono` — line 91
- `Komorebi.AVOC.expectedContinuation_const` — line 103

## `AVOC/StochasticBlackwell.lean`

- `Komorebi.AVOC.RationalChannel.ext` — line 17
- `Komorebi.AVOC.signalActionScore_compose` — line 77
- `Komorebi.AVOC.signalwise_max_policy_exists` — line 108
- `Komorebi.AVOC.garbled_policy_score_le_fine_policy` — line 130
- `Komorebi.AVOC.stochasticDecisionValue_compose_eq_garbled_scores` — line 161
- `Komorebi.AVOC.stochastic_blackwell_policy_dominance` — line 178
- `Komorebi.AVOC.stochasticDecisionValue_le_best` — line 213
- `Komorebi.AVOC.best_stochastic_policy_exists` — line 234
- `Komorebi.AVOC.stochastic_blackwell_monotonicity` — line 259
- `Komorebi.AVOC.stochastic_blackwell_cost_dominance` — line 276
- `Komorebi.AVOC.compose_identityChannel` — line 304
- `Komorebi.AVOC.composeChannel_assoc` — line 314
- `Komorebi.AVOC.blackwellRefines_refl` — line 342
- `Komorebi.AVOC.blackwellRefines_trans` — line 348
- `Komorebi.AVOC.bestValue_mono_blackwell` — line 360
- `Komorebi.AVOC.compose_forget_prob_eq_uninformative` — line 388
- `Komorebi.AVOC.compose_forget_eq_uninformative` — line 398
- `Komorebi.AVOC.blackwellRefines_uninformative` — line 408
- `Komorebi.AVOC.information_never_hurts_without_cost` — line 416
- `Komorebi.AVOC.valueOfInformation_nonneg` — line 442
- `Komorebi.AVOC.valueOfInformation_mono_under_garbling` — line 454
- `Komorebi.AVOC.netValueOfInformation_positive_iff` — line 478
- `Komorebi.AVOC.stop_dominates_acquisition_when_cost_exceeds_voi` — line 492

## `AVOC/StochasticExamples.lean`

- `Komorebi.AVOC.noInformation_not_refines_perfectBool` — line 8
- `Komorebi.AVOC.perfectBool_refines_noInformation` — line 18
- `Komorebi.AVOC.blackwellRefinement_not_symmetric_example` — line 23

## `AVOC/StochasticQuotient.lean`

- `Komorebi.AVOC.stochasticRepresentative_spec` — line 16
- `Komorebi.AVOC.quotientStochastic_reward_eq` — line 58
- `Komorebi.AVOC.fiberConstant_eq_representative` — line 73
- `Komorebi.AVOC.grouped_expectation_eq_raw` — line 84
- `Komorebi.AVOC.quotient_expectedContinuation_eq_raw` — line 112
- `Komorebi.AVOC.quotientStochasticControlSystem_horizonValue_eq` — line 151
- `Komorebi.AVOC.quotientStochasticControlSystem_qValue_eq` — line 198
- `Komorebi.AVOC.quotient_stochasticBellmanOptimalAt_iff` — line 219

## `AVOC/StochasticSufficiency.lean`

- `Komorebi.AVOC.expectedContinuation_eq_of_strongSuff` — line 22
- `Komorebi.AVOC.stochasticQValue_eq_of_strongSuff` — line 38
- `Komorebi.AVOC.stochasticHorizonValue_eq_of_strongSuff` — line 57
- `Komorebi.AVOC.stochasticBellmanOptimalAt_iff_of_strongSuff` — line 94

## `AVOC/SynthesisExamples.lean`

- `Komorebi.AVOC.SynthesisExamples.pair_equivalent` — line 13
- `Komorebi.AVOC.SynthesisExamples.guard_equivalent` — line 17
- `Komorebi.AVOC.SynthesisExamples.pair_strictly_smaller` — line 21
- `Komorebi.AVOC.SynthesisExamples.guard_strictly_smaller` — line 23
- `Komorebi.AVOC.SynthesisExamples.layer_cardinality` — line 25
- `Komorebi.AVOC.SynthesisExamples.protected_function_not_constant` — line 27
- `Komorebi.AVOC.SynthesisExamples.pair_generated_replacement` — line 31
- `Komorebi.AVOC.SynthesisExamples.zero_credit_retains_reference` — line 33
- `Komorebi.AVOC.SynthesisExamples.zero_credit_no_search_charge` — line 36
- `Komorebi.AVOC.SynthesisExamples.pair_search_charge` — line 39
- `Komorebi.AVOC.SynthesisExamples.generated_pair_every_input` — line 42
- `Komorebi.AVOC.SynthesisExamples.pair_campaign_promotes` — line 49
- `Komorebi.AVOC.SynthesisExamples.pair_campaign_net` — line 54
- `Komorebi.AVOC.SynthesisExamples.better_program_unprofitable_search` — line 59

## `AVOC/SynthesisPromotion.lean`

- `Komorebi.AVOC.Synthesis.submission_contract` — line 55
- `Komorebi.AVOC.Synthesis.submission_budget` — line 59
- `Komorebi.AVOC.Synthesis.submission_replays` — line 64
- `Komorebi.AVOC.Synthesis.campaign_total_budget` — line 91
- `Komorebi.AVOC.Synthesis.campaign_active_sound` — line 101
- `Komorebi.AVOC.Synthesis.campaign_net_bound` — line 104
- `Komorebi.AVOC.Synthesis.restored_generated_sound` — line 130

## `AVOC/SynthesisRetry.lean`

- `Komorebi.AVOC.SynthesisRetry.reference_is_retry_threshold` — line 12
- `Komorebi.AVOC.SynthesisRetry.generated_retry_decision` — line 24
- `Komorebi.AVOC.SynthesisRetry.promoted_generated_retry_decision` — line 31
- `Komorebi.AVOC.SynthesisRetry.generated_guard_work_bound` — line 38

## `AVOC/SynthesisRuntime.lean`

- `Komorebi.AVOC.SynthesisRuntime.rendered_campaign_sound` — line 187
- `Komorebi.AVOC.SynthesisRuntime.rendered_campaign_budget` — line 191

## `AVOC/TypedAffineProgram.lean`

- `Komorebi.AVOC.Affine.normalize_correct` — line 31
- `Komorebi.AVOC.Affine.normalized_iff_equivalent` — line 43
- `Komorebi.AVOC.Affine.checkProgram_iff` — line 51
- `Komorebi.AVOC.Affine.finite_probe_complete` — line 56
- `Komorebi.AVOC.Affine.seq_congr` — line 65
- `Komorebi.AVOC.Affine.plus_congr` — line 73
- `Komorebi.AVOC.Affine.context_congr` — line 94
- `Komorebi.AVOC.Affine.context_cost_mono` — line 111
- `Komorebi.AVOC.Affine.lower_bound` — line 131
- `Komorebi.AVOC.Affine.attained_global_minimum` — line 144

## `AVOC/UpgradeRuntime.lean`

- `Komorebi.AVOC.UpgradeRuntime.executed_campaign_preserves_contract` — line 20
- `Komorebi.AVOC.UpgradeRuntime.executed_campaign_credit_bound` — line 23
- `Komorebi.AVOC.UpgradeRuntime.executed_campaign_net_bound` — line 27
- `Komorebi.AVOC.UpgradeRuntime.active_component_correct` — line 34

## `AVOC/UpgradeSpecialization.lean`

- `Komorebi.AVOC.UpgradeCatalogue.dynamic_contract` — line 35
- `Komorebi.AVOC.UpgradeCatalogue.threshold_contract` — line 39
- `Komorebi.AVOC.UpgradeCatalogue.check_sound` — line 45
- `Komorebi.AVOC.UpgradeCatalogue.evaluate_visits_positive` — line 51
- `Komorebi.AVOC.UpgradeCatalogue.threshold_work_nondegrading` — line 59
- `Komorebi.AVOC.UpgradeCatalogue.threshold_observational_equivalence` — line 63
- `Komorebi.AVOC.UpgradeCatalogue.example_no_revival` — line 79
- `Komorebi.AVOC.UpgradeCatalogue.uncertified_version_fails` — line 84
- `Komorebi.AVOC.UpgradeCatalogue.example_dynamic_visits` — line 97
- `Komorebi.AVOC.UpgradeCatalogue.dynamic_work` — line 105
- `Komorebi.AVOC.UpgradeCatalogue.threshold_work` — line 110
- `Komorebi.AVOC.UpgradeCatalogue.alwaysRetry_work` — line 112
- `Komorebi.AVOC.UpgradeCatalogue.initial_safe` — line 147
- `Komorebi.AVOC.UpgradeCatalogue.rejected_bad_candidate` — line 150
- `Komorebi.AVOC.UpgradeCatalogue.bad_trial_cost_retained` — line 155
- `Komorebi.AVOC.UpgradeCatalogue.approved_good_candidate` — line 159
- `Komorebi.AVOC.UpgradeCatalogue.after_upgrade_net_gain` — line 165
- `Komorebi.AVOC.UpgradeCatalogue.after_upgrade_safe` — line 170
- `Komorebi.AVOC.UpgradeCatalogue.expensive_search_reachable` — line 179
- `Komorebi.AVOC.UpgradeCatalogue.expensive_search_safe` — line 183
- `Komorebi.AVOC.UpgradeCatalogue.improved_version_unprofitable_campaign` — line 186

## `AVOC/Verification.lean`

- `Komorebi.AVOC.sound_gate_acceptance` — line 13
- `Komorebi.AVOC.sound_gate_false_filter_empty` — line 22
- `Komorebi.AVOC.sound_gate_false_admission_count_zero` — line 35

## `AVOC/VerifiedUpgrade.lean`

- `Komorebi.AVOC.Upgrade.initial_safe` — line 100
- `Komorebi.AVOC.Upgrade.eligible_gain` — line 103
- `Komorebi.AVOC.Upgrade.eligible_strict_improvement` — line 112
- `Komorebi.AVOC.Upgrade.promoted_iff` — line 119
- `Komorebi.AVOC.Upgrade.promotion_bound_to_request` — line 123
- `Komorebi.AVOC.Upgrade.rejection_keeps_active` — line 130
- `Komorebi.AVOC.Upgrade.funded_trial_is_charged` — line 136
- `Komorebi.AVOC.Upgrade.unfunded_unchanged` — line 141
- `Komorebi.AVOC.Upgrade.step_initial_unchanged` — line 145
- `Komorebi.AVOC.Upgrade.step_accounting` — line 149
- `Komorebi.AVOC.Upgrade.step_safe` — line 154
- `Komorebi.AVOC.Upgrade.step_utility_nondecreasing` — line 172
- `Komorebi.AVOC.Upgrade.promoted_proposal_stale` — line 184
- `Komorebi.AVOC.Upgrade.run_safe` — line 206
- `Komorebi.AVOC.Upgrade.run_initial` — line 212
- `Komorebi.AVOC.Upgrade.run_evaluation_accounting` — line 218
- `Komorebi.AVOC.Upgrade.run_switch_accounting` — line 227
- `Komorebi.AVOC.Upgrade.campaign_net_lower_bound` — line 240
- `Komorebi.AVOC.Upgrade.campaign_profitable_of_paid_search` — line 246
- `Komorebi.AVOC.Upgrade.no_overspend` — line 252
- `Komorebi.AVOC.Upgrade.certified_upgrade_campaign` — line 260
- `Komorebi.AVOC.Upgrade.adaptive_campaign_safe` — line 278
- `Komorebi.AVOC.Upgrade.adaptive_utility_nondecreasing` — line 285
- `Komorebi.AVOC.Upgrade.adaptive_campaign_net_bound` — line 295
- `Komorebi.AVOC.Upgrade.changed_objective_never_promotes` — line 301
- `Komorebi.AVOC.Upgrade.changed_core_never_promotes` — line 307
- `Komorebi.AVOC.Upgrade.rejected_check_never_promotes` — line 313

## `AVOC/VerifierEnsemble.lean`

- `Komorebi.AVOC.mem_jointFailureEvent` — line 17
- `Komorebi.AVOC.jointFailureEvent_subset` — line 27
- `Komorebi.AVOC.jointFailure_prob_le_marginal` — line 38
- `Komorebi.AVOC.jointFailure_prob_eq_product` — line 56
- `Komorebi.AVOC.wrong_probability_le_specification_plus_joint_failure` — line 74
- `Komorebi.AVOC.wrong_probability_le_specification_plus_product` — line 93
- `Komorebi.AVOC.wrong_probability_le_specification_plus_power` — line 109
- `Komorebi.AVOC.shared_specification_error_is_lower_bound` — line 138
- `Komorebi.AVOC.verifier_ensemble_error_sandwich` — line 150
- `Komorebi.AVOC.exact_specification_verification_error_decomposition` — line 169
- `Komorebi.AVOC.exact_error_decomposition_with_factorized_verifiers` — line 185
- `Komorebi.AVOC.cannot_beat_shared_specification_floor` — line 208
- `Komorebi.AVOC.constant_rate_verifier_ensemble_sandwich` — line 218
- `Komorebi.AVOC.exact_constant_rate_error_decomposition` — line 238

## `AVOC/VerifierExamples.lean`

- `Komorebi.AVOC.erased_bool_specification_cannot_recover_identity` — line 10
- `Komorebi.AVOC.erased_bool_specification_cannot_be_repaired_by_ensemble` — line 21
- `Komorebi.AVOC.perfectlyCorrelatedFailure_marginal` — line 37
- `Komorebi.AVOC.perfectlyCorrelatedFailure_joint_event` — line 43
- `Komorebi.AVOC.perfectlyCorrelatedFailure_joint_prob` — line 50
- `Komorebi.AVOC.perfectlyCorrelatedFailure_product_marginals` — line 56
- `Komorebi.AVOC.perfectlyCorrelatedFailure_not_factorized` — line 64
- `Komorebi.AVOC.coordinateFailure_marginal` — line 86
- `Komorebi.AVOC.coordinateFailure_joint_event` — line 91
- `Komorebi.AVOC.coordinateFailure_joint_prob` — line 99
- `Komorebi.AVOC.coordinateFailure_factorizes` — line 106

## `AVOC/WorkflowPlanner.lean`

- `Komorebi.AVOC.WorkflowPlanner.update_eq` — line 17
- `Komorebi.AVOC.WorkflowPlanner.readyCheck_correct` — line 24
- `Komorebi.AVOC.WorkflowPlanner.precheck_correct` — line 44
- `Komorebi.AVOC.WorkflowPlanner.allowedCheck_correct` — line 59
- `Komorebi.AVOC.WorkflowPlanner.pool_complete` — line 69
- `Komorebi.AVOC.WorkflowPlanner.step_eq` — line 92
- `Komorebi.AVOC.WorkflowPlanner.pool_length` — line 107
- `Komorebi.AVOC.WorkflowPlanner.model_branch_bound` — line 114
- `Komorebi.AVOC.WorkflowPlanner.model_realizes` — line 125
- `Komorebi.AVOC.WorkflowPlanner.executable_policy_source_safe` — line 141
- `Komorebi.AVOC.WorkflowPlanner.executable_policy_regret` — line 155
