# Result-level formalization map

Source: Reviewed Core 0.2. Companion 0.15.0. Every admission refers to complete current-source gates. Supporting declarations are not additional source results.

## 1.1 — A record determines a target exactly on its fibres

Status: **KERNEL_CHECKED_BLOCK01**.

Source label `r:factor`, printed page 1, source lines [98, 106].

- `Komorebi.MachineTheory.decoder_exists_iff`
- `Komorebi.MachineTheory.no_decoder_of_collision`

## 1.2 — Evidence-initialized behavioral state

Status: **KERNEL_CHECKED_BLOCK01**.

Source label `r:behavior`, printed page 2, source lines [146, 157].

- `Komorebi.MachineTheory.evidence_initialized_predictor_iff`
- `Komorebi.MachineTheory.Predictor.record_sufficient`
- `Komorebi.MachineTheory.Predictor.minimal_initialized_card`
- `Komorebi.MachineTheory.canonical_initialized_card`

## 2.1 — Exact accounting of the discarded excursion

Status: **KERNEL_CHECKED_BLOCK01**.

Source label `r:packet`, printed page 4, source lines [183, 192].

- `Komorebi.MachineTheory.split_encoding_comp`
- `Komorebi.MachineTheory.hidden_return_identity`
- `Komorebi.MachineTheory.compressed_comp_iff_no_return`
- `Komorebi.MachineTheory.split_projector_idempotent`
- `Komorebi.MachineTheory.compression_projector_idempotent`

## 2.3 — Forward transport of a reusable method

Status: **KERNEL_CHECKED_BLOCK01**.

Source label `r:transport`, printed page 5, source lines [204, 218].

- `Komorebi.MachineTheory.forward_transport`
- `Komorebi.MachineTheory.forward_output`
- `Komorebi.MachineTheory.invariant_forward_transport`
- `Komorebi.MachineTheory.invariant_forward_output`

## 2.4 — A common observable quotient

Status: **NOT_FORMALIZED_IN_THIS_BLOCK**.

Source label `r:common`, printed page 5, source lines [233, 250].



## 2.5 — When complete packets are genuine probability components

Status: **NOT_FORMALIZED_IN_THIS_BLOCK**.

Source label `r:positive-packets`, printed page 6, source lines [267, 279].



## 3.1 — Minimal exact memory for a correction contract

Status: **KERNEL_CHECKED_BLOCK01**.

Source label `r:memory`, printed page 8, source lines [314, 325].

- `Komorebi.MachineTheory.EvidenceAlgebra.signature_congruence`
- `Komorebi.MachineTheory.EvidenceAlgebra.memory_readout_continuation`
- `Komorebi.MachineTheory.EvidenceAlgebra.memory_universal_property`
- `Komorebi.MachineTheory.EvidenceAlgebra.memory_minimal_card`
- `Komorebi.MachineTheory.EvidenceAlgebra.signature_empty`

## 3.2 — The size of partition correction memory

Status: **NOT_FORMALIZED_IN_THIS_BLOCK**.

Source label `r:occupancy`, printed page 9, source lines [335, 340].



## 3.4 — When a report preserves every Bayesian correction

Status: **KERNEL_CHECKED_BLOCK02**.

Source label `r:bayes`, printed page 9, source lines [364, 385].

- `Komorebi.MachineTheory.Bayes.ReportingModel.all_iff_full_support_prior`
- `Komorebi.MachineTheory.Bayes.ReportingModel.all_iff_exists_full_support`
- `Komorebi.MachineTheory.Bayes.ReportingModel.all_iff_reconstruction`
- `Komorebi.MachineTheory.Bayes.ReportingModel.reconstructs_of_full_support`
- `Komorebi.MachineTheory.Bayes.ReportingModel.preservesAll_of_reconstructs`

## 3.5 — Least refinement closed under prediction and correction

Status: **KERNEL_CHECKED_BLOCK02**.

Source label `r:joint-refinement`, printed page 11, source lines [405, 422].

- `Komorebi.MachineTheory.BayesianLumping.likelihood_constant_on_fibres`
- `Komorebi.MachineTheory.BayesianLumping.fixed_positive_coarse_iff`
- `Komorebi.MachineTheory.Refinement.step_rel_iff`
- `Komorebi.MachineTheory.Refinement.bounded_stabilization`
- `Komorebi.MachineTheory.Refinement.stopIndex_bound`
- `Komorebi.MachineTheory.Refinement.stable_iff_prediction`
- `Komorebi.MachineTheory.Refinement.admissible_iff`
- `Komorebi.MachineTheory.Refinement.least_prediction_correction_refinement`

## 3.6 — One quotient for reports, posteriors, and feedback

Status: **KERNEL_CHECKED_BLOCK01**.

Source label `r:instrument`, printed page 12, source lines [445, 466].

- `Komorebi.MachineTheory.Instrument.quotient_exists_iff`
- `Komorebi.MachineTheory.Instrument.quotient_unique`
- `Komorebi.MachineTheory.Instrument.instrument_iff_reports_and_posteriors`
- `Komorebi.MachineTheory.Instrument.quotient_feedback_law`
- `Komorebi.MachineTheory.Instrument.totalHistoryMass_eq`
- `Komorebi.MachineTheory.Instrument.positive_history_posterior_dist`
- `Komorebi.MachineTheory.Instrument.stopped_feedback`
- `Komorebi.MachineTheory.Instrument.stoppedAndSurvivingMass_eq`

## 3.8 — A whole-history bound with an explicit conditioning cost

Status: **KERNEL_CHECKED_BLOCK04**.

Source label `r:history-bound`, printed page 13, source lines [483, 503].

- `Komorebi.MachineTheory.ApproximateHistory.whole_history_bound`
- `Komorebi.MachineTheory.ApproximateHistory.observed_history_bound`
- `Komorebi.MachineTheory.ApproximateHistory.conditional_final_bound`
- `Komorebi.MachineTheory.ApproximateHistory.history_event_positive`
- `Komorebi.MachineTheory.Variation.condition_bound`

## 4.1 — A decision bound for one actual approximation chain

Status: **KERNEL_CHECKED_BLOCK05**.

Source label `r:risk`, printed page 15, source lines [533, 550].

- `Komorebi.MachineTheory.ResponseDecision.decision_error_global`
- `Komorebi.MachineTheory.ResponseDecision.metric_minimizers_exist`
- `Komorebi.MachineTheory.ResponseDecision.regret_to_minimum`
- `Komorebi.MachineTheory.ResponseDecision.unique_minimizer_transfer`
- `Komorebi.MachineTheory.ResponseDecision.risk_threshold`

## 4.2 — A common artifact for fixed recipients

Status: **KERNEL_CHECKED_BLOCK06**.

Source label `r:recipient`, printed page 16, source lines [565, 574].

- `Komorebi.MachineTheory.Recipient.encoder_exists_iff`
- `Komorebi.MachineTheory.Recipient.cardinality_budget_iff`
- `Komorebi.MachineTheory.Recipient.minimum_image_eq_cover`
- `Komorebi.MachineTheory.Recipient.minimum_common_artifact`
- `Komorebi.MachineTheory.RecipientExecution.Audience.common_artifact_iff`

## 5.1 — Exact joint feasibility for explicit controllers

Status: **KERNEL_CHECKED_BLOCK07**.

Source label `r:inquiry`, printed page 17, source lines [611, 618].

- `Komorebi.MachineTheory.HardInquiry.Model.exact_frontier`
- `Komorebi.MachineTheory.HardInquiry.Model.joint_budget_iff`
- `Komorebi.MachineTheory.HardInquiry.Model.solve_witness`
- `Komorebi.MachineTheory.HardInquiry.Model.backup_dominates`
- `Komorebi.MachineTheory.HardInquiry.Model.compute_eq_solve`
- `Komorebi.MachineTheory.HardInquiry.Model.execution_sound`
- `Komorebi.MachineTheory.HardInquiry.Model.worst_coordinate_attained`
- `Komorebi.MachineTheory.HardInquiry.Model.profile_records`
- `Komorebi.MachineTheory.HardInquiry.AudienceBridge.recipient_inquiry`
- `Komorebi.MachineTheory.HardExamples.four_frontier_all`
- `Komorebi.MachineTheory.HardExamples.four_no_mixed_budget`
- `Komorebi.MachineTheory.HardControls.sensor_recipient_execution`

## 5.3 — A candidate attaining both lower bounds is optimal

Status: **KERNEL_CHECKED_BLOCK08**.

Source label `r:lowerbound`, printed page 18, source lines [635, 642].

- `Komorebi.MachineTheory.BinaryDiagnosis.binary_lower_bounds`
- `Komorebi.MachineTheory.BinaryDiagnosis.records_exact`
- `Komorebi.MachineTheory.BinaryDiagnosis.actual_run_lower_bound`
- `Komorebi.MachineTheory.BinaryDiagnosis.checked_candidate_closes_frontier`
- `Komorebi.MachineTheory.BinaryDiagnosis.admitted_frontier`
- `Komorebi.MachineTheory.BinaryDiagnosis.admitted_budget`

## 5.4 — The same compressed belief supports the same inquiry

Status: **KERNEL_CHECKED_BLOCK03**.

Source label `r:belief-planning`, printed page 20, source lines [664, 675].

- `Komorebi.MachineTheory.Planning.optimal_value_characterization`
- `Komorebi.MachineTheory.Planning.ExactMap.value_eq`
- `Komorebi.MachineTheory.Planning.ExactMap.firstValue_eq`
- `Komorebi.MachineTheory.Planning.ExactMap.optimalFirst_iff`
- `Komorebi.MachineTheory.Planning.ExactMap.feasible_iff`
- `Komorebi.MachineTheory.Planning.ExactMap.evaluate_eq`
- `Komorebi.MachineTheory.Planning.ExactMap.common_minimizing_tree`
- `Komorebi.MachineTheory.BeliefPlanning.compressed_belief_planning`
- `Komorebi.MachineTheory.BeliefPlanning.common_optimal_inquiry`
- `Komorebi.MachineTheory.BeliefPlanning.constructed_quotient_planning`
- `Komorebi.MachineTheory.Planning.ExactMap.optimalStop_iff`

## 5.6 — Uniform model error controls a changed policy

Status: **KERNEL_CHECKED_BLOCK04**.

Source label `r:policy-error`, printed page 22, source lines [712, 730].

- `Komorebi.MachineTheory.ApproximateDecision.same_policy_error`
- `Komorebi.MachineTheory.ApproximateDecision.uniform_policy_regret`
- `Komorebi.MachineTheory.ApproximateDecision.minimizing_policies_exist`
- `Komorebi.MachineTheory.ApproximateDecision.history_policy_error`
- `Komorebi.MachineTheory.ApproximateDecision.history_selected_policy_regret`

## 6.1 — What finite counterexamples establish

Status: **KERNEL_CHECKED_BLOCK09**.

Source label `r:cegis`, printed page 23, source lines [742, 747].

- `Komorebi.MachineTheory.Synthesis.counterexample_guided_synthesis`
- `Komorebi.MachineTheory.Synthesis.accepted_first`
- `Komorebi.MachineTheory.Synthesis.exhaustion_iff`
- `Komorebi.MachineTheory.Synthesis.truthful_call_bound`
- `Komorebi.MachineTheory.Synthesis.truthful_outcome`
- `Komorebi.MachineTheory.Synthesis.no_unbounded_truthful_calls`
- `Komorebi.MachineTheory.Synthesis.resume_bounded`
- `Komorebi.MachineTheory.Synthesis.bounded_completion_sound`

## 6.2 — Ordered semantic compression preserves the teacher trace

Status: **KERNEL_CHECKED_BLOCK09**.

Source label `r:ordered`, printed page 23, source lines [759, 766].

- `Komorebi.MachineTheory.Synthesis.ordered_compression`
- `Komorebi.MachineTheory.Synthesis.representative_search_complete`
- `Komorebi.MachineTheory.Synthesis.teacher_work_preserved`
- `Komorebi.MachineTheory.Synthesis.prepare_value`

## 6.4 — A sound prefix exclusion

Status: **KERNEL_CHECKED_BLOCK10**.

Source label `r:prefix`, printed page 24, source lines [781, 788].

- `Komorebi.MachineTheory.PrefixScan.integer_completion_iff`
- `Komorebi.MachineTheory.OrderedCompiler.prefix_exclusion`
- `Komorebi.MachineTheory.OrderedCompiler.source_prefix_certificate`
- `Komorebi.MachineTheory.OrderedCompiler.admitted_search_sound_complete`
- `Komorebi.MachineTheory.OrderedCompiler.admitted_failure_iff_empty_frontier`

## 7.1 — Selective reuse with complete dependencies

Status: **KERNEL_CHECKED_BLOCK11**.

Source label `r:dependencies`, printed page 26, source lines [809, 814].

- `Komorebi.MachineTheory.Dependency.System.selective_reuse`
- `Komorebi.MachineTheory.Dependency.System.restoration`
- `Komorebi.MachineTheory.Dependency.System.admitted_reuse_and_restoration`
- `Komorebi.MachineTheory.Dependency.closure_iff_reach`

## 7.3 — Which gains survive every admitted price?

Status: **KERNEL_CHECKED_BLOCK12**.

Source label `r:prices`, printed page 27, source lines [835, 840].

- `Komorebi.MachineTheory.ResourcePrices.all_nonnegative_prices_iff`
- `Komorebi.MachineTheory.ResourcePrices.finite_price_minimum`
- `Komorebi.MachineTheory.ResourcePrices.listed_hull_minimizer`
- `Komorebi.MachineTheory.ResourcePrices.saving_net`
- `Komorebi.MachineTheory.PriceExamples.priced_scan`
- `Komorebi.MachineTheory.PriceExamples.robust_reuse_threshold`
- `Komorebi.MachineTheory.PriceRevision.restored_negative_real_saving`

## 7.4 — A conditional error budget for a lineage

Status: **KERNEL_CHECKED_BLOCK13**.

Source label `r:lineage`, printed page 28, source lines [848, 858].

- `Komorebi.MachineTheory.Lineage.conditional_marginal_bound`
- `Komorebi.MachineTheory.Lineage.finite_lineage_bound`
- `Komorebi.MachineTheory.Lineage.lineage_bound`
- `Komorebi.MachineTheory.Lineage.lineage_ennreal_bound`
- `Komorebi.MachineTheory.Lineage.selected_lineage_bound`
- `Komorebi.MachineTheory.Lineage.stopped_selected_lineage_bound`
- `Komorebi.MachineTheory.Lineage.divergent_real_total_not_union_bound`

## 8.1 — Target-relative joint reconstruction

Status: **KERNEL_CHECKED_BLOCK14**.

Source label `r:reconstruction`, printed page 29, source lines [873, 878].

- `Komorebi.MachineTheory.JointReconstruction.finite_joint_reconstruction`
- `Komorebi.MachineTheory.JointReconstruction.exists_decoder_iff_ker_le`
- `Komorebi.MachineTheory.JointReconstruction.exists_decoder_extending_imageDecoder`
- `Komorebi.MachineTheory.JointReconstruction.full_state_iff_injective`
- `Komorebi.MachineTheory.JointReconstruction.ker_stackRecords`
- `Komorebi.MachineTheory.JointReconstruction.stacked_decoder_iff`

## 8.2 — A quotient that preserves legal operations

Status: **KERNEL_CHECKED_BLOCK15**.

Source label `r:governance`, printed page 29, source lines [888, 898].

- `Komorebi.MachineTheory.LegalQuotient.finite_source_legal_quotient`
- `Komorebi.MachineTheory.LegalQuotient.exists_quotient_iff`
- `Komorebi.MachineTheory.LegalQuotient.representativeQuotient_factors`
- `Komorebi.MachineTheory.LegalQuotient.quotient_unique`
- `Komorebi.MachineTheory.LegalQuotient.ofEnabled_reconstruct`
- `Komorebi.MachineTheory.LegalQuotient.finite_legal_quotient_sequences`
- `Komorebi.MachineTheory.LegalQuotient.Factors.execute_map`
- `Komorebi.MachineTheory.LegalQuotient.Factors.labels_eq`
- `Komorebi.MachineTheory.LegalQuotient.Factors.lift_execution`

## 8.3 — Safe continuation that retains an ending strategy

Status: **NOT_FORMALIZED_IN_THIS_BLOCK**.

Source label `r:ending`, printed page 30, source lines [918, 927].



